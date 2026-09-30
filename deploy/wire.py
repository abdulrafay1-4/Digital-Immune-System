"""The container deployment: one image, nine roles, one broker."""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
import secrets
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from deploy.remote_attesters import attester_user
from m1_monitoring.sensors.remote import sensor_user
from shared.clock import RealClock

SECRETS = Path(os.environ.get("SECRETS_DIR", "/secrets"))
RUN_ID = os.environ.get("DIS_RUN_ID", "wire-demo")
SEED = int(os.environ.get("DIS_SEED", "7"))
NODES = [n for n in os.environ.get("DIS_NODES", "node-0,node-1,node-2").split(",") if n]
TICKS = int(os.environ.get("DIS_TICKS", "40"))
TICK_SECONDS = float(os.environ.get("DIS_TICK_SECONDS", "1.0"))
EPOCH_KEY = f"dis:{RUN_ID}:epoch"
ATTEST = os.environ.get("DIS_ATTEST") == "1"
LEAD_TICKS = int(os.environ.get("DIS_LEAD_TICKS", "8"))
SCENARIO = os.environ.get("DIS_SCENARIO") or None
STOLEN = Path("/stolen")
VICTIM = os.environ.get("VICTIM", "node-2")
MEMORY_URL = os.environ.get("MEMORY_URL", "https://memory:8443/mcp")
MEMORY_PORT = 8443
ATTESTERS = ("verifier", "correlation", "fusion", "orchestrator", "monitoring")
FUSION_REPLICAS = ("a", "b", "c")


REDIS_UID, APP_UID = 999, 10001


def agent_for(node_id: str) -> str:
    return f"mon-{node_id}"


def identity_seed(fleet_secret: bytes, agent_id: str) -> bytes:
    return hmac.new(fleet_secret, b"dis-agent:" + agent_id.encode(), hashlib.sha256).digest()


class BrokerClock:
    """Ticks since the run epoch, on the broker's time."""

    def __init__(self, client: Any, epoch: float, *, whole_ticks: bool = False) -> None:
        self._real = RealClock()
        secs, micros = client.time()
        self._offset = secs + micros / 1e6 - self._real.now()
        self.epoch = epoch
        self.whole_ticks = whole_ticks

    def broker_time(self) -> float:
        return self._real.now() + self._offset

    def ticks(self) -> float:
        return (self.broker_time() - self.epoch) / TICK_SECONDS

    def now(self) -> float:
        return float(math.floor(self.ticks())) if self.whole_ticks else self.ticks()

    def sleep(self, duration: float) -> None:
        self._real.sleep(max(0.0, duration) * TICK_SECONDS)

    def wait_until(self, tick: float) -> None:
        self.sleep(tick - self.ticks())


def _connect(publisher: str) -> Any:
    """A bus as this role's Redis user."""
    from shared.redis_bus import RedisBus
    from shared.secure_bus import TLSConfig

    url = os.environ.get("REDIS_URL", "rediss://redis:6379/0")
    tls = TLSConfig(
        enabled=url.startswith("rediss://"),
        ca_cert=SECRETS / "ca.crt",
        client_cert=SECRETS / "client.crt",
        client_key=SECRETS / "client.key",
    )
    bus = RedisBus.connect(
        url,
        publisher=publisher,
        username=(SECRETS / "redis.user").read_text().strip(),
        password=(SECRETS / "redis.pass").read_text().strip(),
        tls=tls,
    )
    bus.transport = tls.describe()
    return bus


def _wait_for_epoch(bus: Any) -> float:
    real = RealClock()
    while (raw := bus.client.get(EPOCH_KEY)) is None:
        real.sleep(0.2)
    return float(raw)


def _run_identity() -> tuple[dict[str, Any], str]:
    from m8_eval_harness.simulator import DEFAULT_CONFIG
    from shared.run_manifest import config_hash, load_yaml_config

    cfg = load_yaml_config(DEFAULT_CONFIG)
    return cfg, config_hash(cfg)


def _log(**fields: Any) -> None:
    print(json.dumps(fields, default=str), flush=True)


def _scenario() -> Any:
    if SCENARIO is None:
        return None
    from m8_eval_harness.scenarios.catalogue import by_id

    scenario = by_id(SCENARIO)
    if unsupported := [f for f in ("outages", "message_loss", "dropped") if getattr(scenario, f)]:
        raise ValueError(f"{SCENARIO}: not modelled in containers: {unsupported}")
    return scenario


def _adversary(scenario: Any, host: str) -> Any:
    """The scenario's attacker, if it runs here: in the container holding the key it stole."""
    import copy

    adversary = scenario.adversary if scenario is not None else None
    if adversary is None:
        return None
    where = getattr(adversary, "own_node", None) or getattr(adversary, "target", None)
    if where is None and type(adversary).__name__ in ("LyingCorrelation", "MemoryPoisoner"):
        where = "control"
    if where is None:
        raise ValueError(f"no container hosts {type(adversary).__name__}")
    return copy.deepcopy(adversary) if where == host else None


def adversary_counters(adversary: Any) -> dict[str, Any]:
    """What an attacker attempted and what landed (its keys excluded)."""
    fields = vars(adversary).items()
    return {k: v for k, v in fields if isinstance(v, int | dict) and k != "registry"}


def broker_users() -> list[str]:
    """Every login the broker has, one per role instance."""
    return [
        "health",
        "control",
        *map(agent_for, NODES),
        *map(sensor_user, NODES),
        *map(attester_user, ATTESTERS),
        *(f"fusion-{r}" for r in FUSION_REPLICAS),
        "console",
    ]


def acl_file(passwords: dict[str, str]) -> bytes:
    """Least privilege on the broker."""

    def digest(user: str) -> str:
        return "#" + hashlib.sha256(passwords[user].encode()).hexdigest()

    lines = [
        "user default off",
        f"user health on {digest('health')} +ping +hello +auth",
        f"user control on {digest('control')} ~dis:* +@connection +time +get +set +xadd"
        " +xread +scan",
    ]
    for node_id in NODES:
        agent, sensor = agent_for(node_id), sensor_user(node_id)
        lines.append(
            f"user {agent} on {digest(agent)} ~dis:*:{agent} %R~{EPOCH_KEY}"
            f" %R~dis:device.measurement:{sensor} +@connection +time +get +xadd +xread"
        )
        lines.append(
            f"user {sensor} on {digest(sensor)} ~dis:device.measurement:{sensor}"
            f" %R~{EPOCH_KEY} +@connection +time +get +xadd"
        )
    for replica in FUSION_REPLICAS:
        user = f"fusion-{replica}"
        lines.append(
            f"user {user} on {digest(user)} ~dis:fusion.reply-{replica}:{user}"
            f" %R~dis:fusion.call-{replica}:control %R~{EPOCH_KEY}"
            " +@connection +time +get +xadd +xread"
        )
    lines.append(
        f"user console on {digest('console')} %R~dis:*:control ~dis:operator.decision:console"
        " +@connection +time +xread +xadd"
    )
    for user in map(attester_user, ATTESTERS):
        lines.append(
            f"user {user} on {digest(user)} ~dis:attest:{user} %R~dis:sealed:control"
            f" %R~dis:candidates:control %R~{EPOCH_KEY} +@connection +time +get +xadd +xread"
        )
    return ("\n".join(lines) + "\n").encode()


def provision(out: Path) -> int:
    """TLS material and secrets, one directory per role."""
    if (out / "control" / "devices.pub").exists():
        _log(role="provision", status="already provisioned")
        return 0
    import datetime

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

    start = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=5)
    end = start + datetime.timedelta(days=30)

    def name(cn: str) -> x509.Name:
        return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])

    ca_key = ec.generate_private_key(ec.SECP256R1())
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(name("dis-ca"))
        .issuer_name(name("dis-ca"))
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(start)
        .not_valid_after(end)
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    def leaf(cn: str, usage: Any, dns: list[str]) -> tuple[bytes, bytes]:
        key = ec.generate_private_key(ec.SECP256R1())
        builder = (
            x509.CertificateBuilder()
            .subject_name(name(cn))
            .issuer_name(ca_cert.subject)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(start)
            .not_valid_after(end)
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.ExtendedKeyUsage([usage]), critical=False)
        )
        if dns:
            builder = builder.add_extension(
                x509.SubjectAlternativeName([x509.DNSName(d) for d in dns]), critical=False
            )
        cert = builder.sign(ca_key, hashes.SHA256())
        key_pem = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        return cert.public_bytes(serialization.Encoding.PEM), key_pem

    ca_pem = ca_cert.public_bytes(serialization.Encoding.PEM)
    fleet_secret = secrets.token_bytes(32)
    passwords = {user: secrets.token_urlsafe(32) for user in broker_users()}

    def write(role: str, uid: int, files: dict[str, bytes]) -> None:
        directory = out / role
        directory.mkdir(parents=True, exist_ok=True)
        for filename, content in files.items():
            path = directory / filename
            path.write_bytes(content)
            path.chmod(0o600 if filename.endswith((".key", ".pass", ".secret")) else 0o644)
            os.chown(path, uid, uid)

    def client(cn: str, user: str) -> dict[str, bytes]:
        cert, key = leaf(cn, ExtendedKeyUsageOID.CLIENT_AUTH, [])
        return {
            "ca.crt": ca_pem,
            "client.crt": cert,
            "client.key": key,
            "redis.user": user.encode(),
            "redis.pass": passwords[user].encode(),
        }

    server_cert, server_key = leaf("redis", ExtendedKeyUsageOID.SERVER_AUTH, ["redis", "localhost"])
    write(
        "server",
        REDIS_UID,
        {
            "redis.crt": server_cert,
            "redis.key": server_key,
            "users.acl": acl_file(passwords),
            **client("redis-healthcheck", "health"),
        },
    )
    write(
        "control",
        APP_UID,
        {
            **client("control", "control"),
            "fleet.secret": fleet_secret,
            "master.key": secrets.token_hex(32).encode(),
        },
    )
    from m10_persona_drift.nhi import issue_signing_identity

    device_seeds = {node_id: secrets.token_bytes(32) for node_id in NODES}
    for node_id in NODES:
        write(
            f"nodes/{agent_for(node_id)}",
            APP_UID,
            {
                **client(node_id, agent_for(node_id)),
                "identity.key": identity_seed(fleet_secret, agent_for(node_id)),
            },
        )
        write(
            f"sensors/{sensor_user(node_id)}",
            APP_UID,
            {
                **client(sensor_user(node_id), sensor_user(node_id)),
                "device.key": device_seeds[node_id],
            },
        )
    public = {
        n: issue_signing_identity(n, seed=seed).public().public_key.hex()
        for n, seed in device_seeds.items()
    }
    write("control", APP_UID, {"devices.pub": json.dumps(public).encode()})

    from agents.context_broker import CORRELATION_CLIENT, CURATOR_CLIENT
    from agents.mcp_broker import CORE_CLIENT, issue_token

    def publics(seeds: dict[str, bytes]) -> bytes:
        keys = {n: issue_signing_identity(n, seed=s).public() for n, s in seeds.items()}
        return json.dumps({n: k.public_key.hex() for n, k in keys.items()}).encode()

    def hexed(seeds: dict[str, bytes]) -> bytes:
        return json.dumps({n: s.hex() for n, s in seeds.items()}).encode()

    client_seeds = {
        c: secrets.token_bytes(32) for c in (CORRELATION_CLIENT, CURATOR_CLIENT, CORE_CLIENT)
    }
    attester_seeds = {n: secrets.token_bytes(32) for n in ATTESTERS}
    token_key = secrets.token_bytes(32)
    memory_cert, memory_key = leaf(
        "memory", ExtendedKeyUsageOID.SERVER_AUTH, ["memory", "localhost"]
    )
    write(
        "memory",
        APP_UID,
        {
            "ca.crt": ca_pem,
            "memory.crt": memory_cert,
            "memory.key": memory_key,
            "token.secret": token_key,
            "mcp_clients.pub": publics(client_seeds),
            "attesters.pub": publics(attester_seeds),
        },
    )
    token = issue_token("control", token_key, audience=MEMORY_URL, expires_at=int(end.timestamp()))
    write(
        "control",
        APP_UID,
        {"mcp_clients.secret": hexed(client_seeds), "memory_token.secret": token.encode()},
    )
    for attester, seed in attester_seeds.items():
        user = attester_user(attester)
        write(f"attesters/{user}", APP_UID, {**client(user, user), "attester.key": seed})
    write("impersonator", APP_UID, client("impersonator", agent_for(VICTIM)))
    console_seed = secrets.token_bytes(32)
    write("console", APP_UID, {**client("console", "console"), "console.key": console_seed})
    console_pub = issue_signing_identity("console", seed=console_seed).public().public_key.hex()
    write("control", APP_UID, {"console.pub": console_pub.encode()})
    write(
        "memory",
        APP_UID,
        {"console.pub": console_pub.encode(), "adjudication.key": secrets.token_bytes(32)},
    )
    for replica in FUSION_REPLICAS:
        user = f"fusion-{replica}"
        write(f"fusion/{user}", APP_UID, client(user, user))
    _log(role="provision", status="done", roles=sorted(p.name for p in out.iterdir()))
    return 0


def memory() -> int:
    """Immune memory behind MCP: the store and the quorum gate."""
    from agents.context_broker import InProcBroker
    from agents.mcp_broker import OperatorVerdicts, ProvisionedTokens, build_server, serve
    from m5_immune_memory import HashingEmbedder, MemoryQuery, MemoryStore, WritePath
    from m10_persona_drift.nhi import VerifyingIdentity
    from m11_memory_hardening import QuorumGate
    from m11_memory_hardening.quorum import DEFAULT_K, QuorumParams
    from shared.clock import WallClock

    def verifiers(filename: str) -> dict[str, Any]:
        keys = json.loads((SECRETS / filename).read_text())
        return {
            n: VerifyingIdentity(agent_id=n, public_key=bytes.fromhex(h)) for n, h in keys.items()
        }

    attesters = verifiers("attesters.pub")
    status_key = (SECRETS / "adjudication.key").read_bytes()
    console = VerifyingIdentity(
        agent_id="console", public_key=bytes.fromhex((SECRETS / "console.pub").read_text())
    )
    embedder = HashingEmbedder()
    store = MemoryStore(dim=embedder.dim)
    broker = InProcBroker(
        query=MemoryQuery(
            store=store,
            registry=attesters,
            embedder=embedder,
            quorum_k=DEFAULT_K,
            adjudication_key=status_key,
        ),
        write_path=WritePath(
            store=store,
            gate=QuorumGate(registry=attesters, params=QuorumParams(k=DEFAULT_K)),
            embedder=embedder,
        ),
        run_id=RUN_ID,
        seed=SEED,
    )
    tokens = ProvisionedTokens(key=(SECRETS / "token.secret").read_bytes(), now=WallClock().now)
    server = build_server(
        broker,
        verifiers("mcp_clients.pub"),
        tokens=tokens,
        resource_url=MEMORY_URL,
        verdicts=OperatorVerdicts(console=console, key=status_key),
    )
    Path("/tmp/ready").write_text("ready")
    _log(role="memory", status="serving", url=MEMORY_URL, attesters=sorted(attesters))
    serve(
        server,
        host="0.0.0.0",  # noqa: S104
        port=MEMORY_PORT,
        certfile=str(SECRETS / "memory.crt"),
        keyfile=str(SECRETS / "memory.key"),
        ca_certs=str(SECRETS / "ca.crt"),
        allowed_hosts=[f"memory:{MEMORY_PORT}"],
    )
    return 0


def attest() -> int:
    """One memory attester: observe every sealed batch, sign what its evidence shows."""
    from agents.attester import IndependentAttester
    from agents.correlation import CorrelationAgent
    from deploy.remote_attesters import AttesterService
    from m8_eval_harness.params import FROZEN
    from m10_persona_drift.nhi import issue_signing_identity

    name = os.environ["ATTESTER"]
    bus = _connect(attester_user(name))
    service = AttesterService(
        IndependentAttester(
            identity=issue_signing_identity(name, seed=(SECRETS / "attester.key").read_bytes()),
            correlator=CorrelationAgent(FROZEN.correlation_params()),
        ),
        bus,
    )
    clock = BrokerClock(bus.client, _wait_for_epoch(bus))
    while clock.ticks() < TICKS + 3:
        service.step(timeout=0.2)
    _log(
        role="attester",
        attester=name,
        observed_until=service.observed_until,
        signed=service.signed,
        declined=service.declined,
    )
    return 0


def fuse() -> int:
    """One trust-fusion instance: the control plane's calls in, its answers out, no key."""
    from m6_trust_fusion.fusion import TrustFusionEngine
    from m6_trust_fusion.remote import FusionReplicaService, replica_user
    from m6_trust_fusion.replicated import _Discard
    from m8_eval_harness.baselines.base import _fusion
    from m8_eval_harness.baselines.compromised_core import _CompromisedFusion
    from m8_eval_harness.params import FROZEN

    name = os.environ["FUSION_REPLICA"]
    lie = os.environ.get("FUSION_LIE")
    _, cfg_hash = _run_identity()
    cls = _CompromisedFusion if lie else TrustFusionEngine
    engine: Any = _fusion(_Discard(), RUN_ID, SEED, cfg_hash, FROZEN, cls=cls)
    if lie:
        engine.mode = lie
    bus = _connect(replica_user(name))
    service = FusionReplicaService(engine, bus, name)
    Path("/tmp/ready").write_text("ready")
    _log(role="fuse", replica=name, lying=lie or False)
    clock = None
    while clock is None or clock.ticks() < TICKS + 3:
        service.step(timeout=0.2)
        if clock is None and (raw := bus.client.get(EPOCH_KEY)) is not None:
            clock = BrokerClock(bus.client, float(raw))
    _log(role="fuse", replica=name, served=service.served, refused=service.refused)
    return 0


def _memory_client(identities: dict[str, Any], token: str | None) -> Any:
    """The control plane's MCP client, retried while the memory service starts."""
    from agents.mcp_broker import McpBroker

    tls = (str(SECRETS / "ca.crt"), str(SECRETS / "client.crt"), str(SECRETS / "client.key"))
    clock = RealClock()
    for attempt in range(60):
        try:
            return McpBroker(url=MEMORY_URL, token=token, tls=tls, identities=identities)
        except Exception:  # noqa: BLE001
            if token is None or attempt == 59:
                raise
            clock.sleep(1.0)
    raise RuntimeError("unreachable")


def _memory_refuses(token: str | None) -> bool:
    """Does the memory service refuse this credential before any tool runs?"""
    try:
        _memory_client({}, token)
    except Exception:  # noqa: BLE001
        return True
    return False


def control() -> int:
    os.environ["DIS_MASTER_KEY"] = (SECRETS / "master.key").read_text().strip()
    from redis.exceptions import ConnectionError as BrokerDown

    from agents.correlation import CORRELATION_TOPIC
    from agents.orchestrator import Orchestrator
    from agents.planner import PLAN_TOPIC
    from console.stream import AUDIT_TOPIC, CLASSIFICATION_TOPIC
    from m1_monitoring.agent import TRUST_TOPIC
    from m7_self_healing import HEAL_TOPIC
    from m8_eval_harness import baselines
    from m8_eval_harness.params import FROZEN
    from m9_capability_binder.binder import implementation
    from m10_persona_drift.nhi import VerifyingIdentity, issue_identity
    from shared.keys import using_development_key
    from shared.secure_bus import SignedBus

    bus = _connect("control")
    device_keys = (
        {
            n: VerifyingIdentity(agent_id=n, public_key=bytes.fromhex(h))
            for n, h in json.loads((SECRETS / "devices.pub").read_text()).items()
        }
        if ATTEST
        else None
    )
    _, cfg_hash = _run_identity()
    fleet_secret = (SECRETS / "fleet.secret").read_bytes()
    identities = {
        agent_for(n): issue_identity(agent_for(n), seed=identity_seed(fleet_secret, agent_for(n)))
        for n in NODES
    }
    from agents.approval import ApprovalGate
    from deploy.operator import BrokerApproval

    operator = BrokerApproval(
        _connect("control"),
        VerifyingIdentity(
            agent_id="console", public_key=bytes.fromhex((SECRETS / "console.pub").read_text())
        ),
    )
    gate = ApprovalGate(operator)
    operator.gate = gate
    pipeline = baselines.by_id("full").pipeline(
        bus=bus, run_id=RUN_ID, seed=SEED, config_hash=cfg_hash, params=FROZEN, approval=gate
    )
    from m6_trust_fusion.remote import RemoteFusion
    from m6_trust_fusion.replicated import ReplicatedFusion

    fusion_bus = _connect("control")
    local = pipeline.fusion
    pipeline.fusion = ReplicatedFusion(  # type: ignore[assignment]
        [
            RemoteFusion(
                fusion_bus, r, local.params, RUN_ID, SEED, cfg_hash, signing_key=local.signing_key
            )
            for r in FUSION_REPLICAS
        ],
        bus=bus,
    )
    pipeline.engine.fusion_params = local.params
    from agents.mcp_broker import RemoteWritePath
    from deploy.remote_attesters import RemoteAttesters, SealedPublisher
    from m10_persona_drift.nhi import issue_signing_identity

    attest_bus = _connect("control")
    pipeline.attesters = RemoteAttesters(attest_bus, ATTESTERS)
    sealed_publisher = SealedPublisher(attest_bus)
    client_seeds = json.loads((SECRETS / "mcp_clients.secret").read_text())
    memory_client = _memory_client(
        {c: issue_signing_identity(c, seed=bytes.fromhex(h)) for c, h in client_seeds.items()},
        (SECRETS / "memory_token.secret").read_text().strip(),
    )
    pipeline.recall = memory_client
    pipeline.broker = memory_client
    pipeline.curator = RemoteWritePath(client=memory_client)
    pipeline.device_keys = device_keys
    verified = SignedBus(
        inner=bus,
        identity=next(iter(identities.values())),
        registry=identities,
        topics=frozenset({TRUST_TOPIC}),
    )
    secs, micros = bus.client.time()
    epoch = secs + micros / 1e6 + LEAD_TICKS * TICK_SECONDS
    clock = BrokerClock(bus.client, epoch, whole_ticks=True)
    orchestrator = Orchestrator(
        bus=verified,
        run_id=RUN_ID,
        seed=SEED,
        config_hash=cfg_hash,
        pipeline=pipeline,
        node_agent_binding={n: agent_for(n) for n in NODES},
        bind_on_first_sight=False,
        clock=clock,
        max_clock_skew=1.0,
        observers=(sealed_publisher,),
        device_keys=device_keys,
        seal_on_report=False,
    )
    orchestrator.attach()
    scenario = _scenario()
    adversary = _adversary(scenario, "control")
    from deploy.operator import BrokerAdjudicator

    adjudicator = BrokerAdjudicator(_connect("control"), memory_client)
    pipeline.adjudicator = adjudicator
    if adversary is not None and getattr(adversary, "write_path", "n/a") is None:
        adversary.write_path = memory_client
        adversary.registry = {
            d.name: issue_signing_identity(d.name, seed=(d / "attester.key").read_bytes())
            for d in sorted(STOLEN.iterdir())
        }
    attacker = SimpleNamespace(
        run_id=RUN_ID, seed=SEED, config_hash=cfg_hash, pipeline=pipeline, as_agent=lambda _: bus
    )
    attacked_until = -1
    bus.client.set(EPOCH_KEY, repr(epoch))
    Path("/tmp/ready").write_text("ready")
    _log(
        role="control",
        status="epoch set",
        run_id=RUN_ID,
        nodes=NODES,
        ticks=TICKS,
        transport=bus.transport,
        binder=implementation(),
        development_key=using_development_key(),
        device_attestation=ATTEST,
    )

    worst = dict.fromkeys(NODES, 0)
    isolated: set[str] = set()
    reported = 0
    broker_errors = 0

    def publish_new() -> None:
        """Log and publish every outcome sealed since the last call."""
        nonlocal reported, isolated
        for outcome in list(pipeline.outcomes)[reported:]:
            isolated |= {
                p.node_id
                for p, r in zip(outcome.plans, outcome.executions, strict=True)
                if r.executed and r.level is not None and int(r.level) == 4
            }
            bus.publish(CORRELATION_TOPIC, outcome.correlation)
            bus.publish(CLASSIFICATION_TOPIC, outcome.classification)
            bus.publish(AUDIT_TOPIC, _verifier_record(outcome))
            for plan in outcome.plans:
                bus.publish(PLAN_TOPIC, plan)
            for record in outcome.audit:
                bus.publish(AUDIT_TOPIC, record)
            for event in outcome.healing:
                bus.publish(HEAL_TOPIC, event)
            levels = {p.node_id: int(p.proposed_level) for p in outcome.plans}
            for node_id, level in levels.items():
                worst[node_id] = max(worst.get(node_id, 0), level)
            _log(
                tick=outcome.sim_time,
                reports=len(outcome.gt_updates),
                levels=levels,
                recall=outcome.correlation.recall_boost,
                executed=[p.node_id for p in outcome.executed],
                enforced={
                    p.node_id: int(r.level)
                    for p, r in zip(outcome.plans, outcome.executions, strict=True)
                    if r.executed and r.level is not None
                },
            )
        reported = len(pipeline.outcomes)

    while clock.ticks() < TICKS + 1:
        try:
            bus.pump(timeout=0.05)
        except BrokerDown as exc:
            broker_errors += 1
            _log(role="control", broker_error=str(exc))
            clock.sleep(0.2)
        if adversary is not None and attacked_until < (now := math.floor(clock.ticks())) < TICKS:
            attacked_until = now
            adversary.before_tick(attacker, float(now))
        orchestrator.seal_due()
        operator.poll()
        adjudicator.poll(float(math.floor(clock.ticks())))
        publish_new()
    for _ in range(50):
        if not bus.pump(timeout=0.2):
            break
    orchestrator.flush()
    publish_new()

    summary = {
        "ticks_sealed": len(pipeline.outcomes),
        "worst_level": worst,
        "telemetry_refused": verified.rejected_count,
        "refusal_reasons": dict(Counter(reason for _, reason in verified.rejected)),
        "wire_frames_dropped": dict(bus.dropped),
        "late_reports": orchestrator.late_updates,
        "duplicate_reports": orchestrator.duplicate_updates,
        "future_reports": orchestrator.future_updates,
        "unbound_reports": orchestrator.unbound_updates,
        "unattested_reports": orchestrator.unattested_updates,
        "audit_intact": pipeline.engine.audit.verify() is None,
        "messages_published": bus.published,
        "broker_errors": broker_errors,
        "memory_calls_over_mcp": memory_client.calls,
        "memory_writes_over_mcp": dict(pipeline.curator.outcomes),
        "sealed_batches_published": sealed_publisher.published,
        "attestation_waits_timed_out": pipeline.attesters.timed_out,
        "unattested_dropped_by_core": pipeline.reports_unattested_in_core,
        "fusion_disagreements": pipeline.fusion.disagreements,
        "operator_questions": operator.asked,
        "operator_answers_accepted": operator.accepted,
        "operator_answers_refused": dict(operator.refused),
        "isolated": sorted(isolated),
        "fusion_instances_down": [p.name for p in pipeline.fusion.replicas if p.down],
        "degraded": dict(pipeline.degraded),
        "adjudication": {
            "asked": adjudicator.asked,
            "applied": adjudicator.applied,
            "refused": dict(adjudicator.refused),
        },
        "scenario": SCENARIO,
        "adversary": adversary_counters(adversary) if adversary is not None else None,
    }
    from agents.mcp_broker import issue_token

    checks = {
        "every tick sealed": summary["ticks_sealed"] >= TICKS - 1,
        "audit chain intact": summary["audit_intact"],
        "memory reached over MCP": summary["memory_calls_over_mcp"] > 0,
        "memory refuses a request without a token": _memory_refuses(None),
        "control plane holds no attester key": not any(SECRETS.glob("attester*")),
        "every fusion instance answered": not summary["fusion_instances_down"],
        "memory refuses a token provisioning did not issue": _memory_refuses(
            issue_token("control", secrets.token_bytes(32), audience=MEMORY_URL, expires_at=2**31)
        ),
    }
    for node_id in _csv("EXPECT_RESTRICTED"):
        checks[f"{node_id} restricted"] = worst.get(node_id, 0) >= 3
    for node_id in _csv("EXPECT_HEALTHY"):
        checks[f"{node_id} left alone"] = worst.get(node_id, 0) <= 1
    for node_id in _csv("EXPECT_ISOLATED"):
        checks[f"{node_id} isolated on the operator's signed answer"] = (
            node_id in isolated and operator.accepted > 0
        )
    for node_id in _csv("EXPECT_DETECTED"):
        checks[f"{node_id} detected"] = worst.get(node_id, 0) >= 2
    for node_id in _csv("EXPECT_UNDETECTED"):
        checks[f"{node_id} never detected (patient liar reproduced)"] = worst.get(node_id, 0) <= 1
    if expected_binder := os.environ.get("EXPECT_BINDER"):
        checks[f"capability binder is the {expected_binder} build"] = (
            implementation() == expected_binder
        )
    if os.environ.get("EXPECT_ADJUDICATED") == "1":
        checks["a remembered incident recorded on the console's signed verdict"] = (
            adjudicator.applied > 0
        )
    if os.environ.get("EXPECT_FUSION_LIAR") == "1":
        checks["a lying fusion instance outvoted"] = summary["fusion_disagreements"] > 0
    if os.environ.get("EXPECT_UNATTESTED") == "1":
        checks["forged context refused by device attestation"] = summary["unattested_reports"] > 0
    if os.environ.get("EXPECT_REFUSALS") == "1":
        checks["forged telemetry refused"] = summary["telemetry_refused"] > 0
        checks["same-tick replays absorbed"] = summary["duplicate_reports"] > 0
        checks["stale replays refused"] = summary["late_reports"] > 0
        checks["garbage frames dropped"] = sum(summary["wire_frames_dropped"].values()) > 0
    _log(role="control", summary=summary, checks=checks)
    return 0 if all(checks.values()) else 1


def node() -> int:
    from m1_monitoring.agent import TRUST_TOPIC, MonitoringAgent
    from m1_monitoring.sensors.synthetic import SyntheticTelemetry
    from m8_eval_harness.simulator import scripted_tick, trust_settings
    from m10_persona_drift.nhi import issue_identity
    from shared.clock import ManualClock
    from shared.secure_bus import SignedBus

    node_id = os.environ["NODE_ID"]
    agent_id = agent_for(node_id)
    identity = issue_identity(agent_id, seed=(SECRETS / "identity.key").read_bytes())
    bus = _connect(agent_id)
    clock = BrokerClock(bus.client, _wait_for_epoch(bus))
    cfg, cfg_hash = _run_identity()
    params, weights = trust_settings(cfg)
    attack = os.environ.get("ATTACK")
    anomalies = {node_id: tuple(float(x) for x in attack.split(","))} if attack else None
    first = max(0, math.ceil(clock.ticks()))
    tick_clock = ManualClock(first)
    scenario = _scenario()
    sensor: Any = (
        SyntheticTelemetry(
            SEED,
            anomalies=scenario.anomaly_map,
            dimension_masks=scenario.dimension_masks,
            noise_model=scenario.noise,
        )
        if scenario is not None
        else SyntheticTelemetry(SEED, anomalies=anomalies)
    )
    if ATTEST:
        from m1_monitoring.sensors.remote import RemoteSensor

        sensor = RemoteSensor(bus, node_id)
    liar_from = os.environ.get("LIAR_FROM")
    agent = MonitoringAgent(
        node_id=node_id,
        agent_id=agent_id,
        sensor=sensor,
        bus=SignedBus(inner=bus, identity=identity, topics=frozenset({TRUST_TOPIC})),
        clock=tick_clock,
        run_id=RUN_ID,
        seed=SEED,
        config_hash=cfg_hash,
        trust_params=params,
        obs_weights=weights,
    )
    _log(
        role="node",
        node_id=node_id,
        first_tick=first,
        attack=attack,
        attested=ATTEST,
        patient_liar_from=liar_from,
        transport=bus.transport,
        holds_device_key=(SECRETS / "device.key").exists(),
    )
    from m1_monitoring.sensors.remote import MissingMeasurement

    script: dict[str, Any] = {
        "selective": dict(scenario.selective_reporting) if scenario else {},
        "restart": dict(scenario.restarts) if scenario else {},
        "patient": (
            dict(scenario.forged_context)
            if scenario
            else ({node_id: float(liar_from)} if liar_from is not None else {})
        ),
        "forged": dict(scenario.forged_observation) if scenario else {},
    }
    adversary = _adversary(scenario, node_id)
    attacker = SimpleNamespace(
        run_id=RUN_ID,
        seed=SEED,
        config_hash=cfg_hash,
        as_agent=lambda a: agent.bus if a == agent_id else bus,
    )
    for t in range(first, TICKS):
        clock.wait_until(t)
        tick_clock.set(t)
        if adversary is not None:
            adversary.before_tick(attacker, float(t))
        try:
            update = scripted_tick(agent, float(t), agent.sensor, params, **script)
        except MissingMeasurement:
            continue
        if update is not None and t % 10 == 0:
            _log(role="node", node_id=node_id, tick=t, trust=round(update.node_trust, 3))
    if adversary is not None:
        _log(role="node", node_id=node_id, adversary=adversary_counters(adversary))
    return 0


def sense() -> int:
    """One device's sensor: measure each tick, sign with the device's own key, publish."""
    from m1_monitoring.sensors.attested import AttestedTelemetry
    from m1_monitoring.sensors.remote import SensorService
    from m1_monitoring.sensors.synthetic import SyntheticTelemetry
    from m10_persona_drift.nhi import issue_signing_identity

    node_id = os.environ["NODE_ID"]
    attack = os.environ.get("ATTACK")
    anomalies = {node_id: tuple(float(x) for x in attack.split(","))} if attack else None
    device = issue_signing_identity(node_id, seed=(SECRETS / "device.key").read_bytes())
    bus = _connect(sensor_user(node_id))
    _, cfg_hash = _run_identity()
    service = SensorService(
        AttestedTelemetry(SyntheticTelemetry(SEED, anomalies=anomalies), {node_id: device}),
        bus,
        node_id,
        RUN_ID,
        SEED,
        cfg_hash,
    )
    clock = BrokerClock(bus.client, _wait_for_epoch(bus))
    first = max(0, math.ceil(clock.ticks()))
    _log(role="sense", node_id=node_id, first_tick=first, attack=attack)
    for t in range(first, TICKS):
        clock.wait_until(t)
        service.measure(float(t))
    _log(role="sense", node_id=node_id, published=service.published)
    return 0


def impersonate() -> int:
    """Everything an insider with a network certificate but no agent key can try."""
    from redis.exceptions import NoPermissionError as NoPermission

    from m1_monitoring.agent import TRUST_TOPIC
    from m1_monitoring.core.context_vector import make_context
    from m10_persona_drift.nhi import issue_identity
    from shared.provenance import tag_synthetic
    from shared.redis_bus import MAX_FRAME_BYTES, STREAM_MAXLEN, stream_key
    from shared.schemas import TrustUpdate
    from shared.secure_bus import SignedBus, _Envelope, payload_bytes

    victim = VICTIM
    agent_id = agent_for(victim)
    bus = _connect(agent_id)
    bus.discover = False
    bus.follow(TRUST_TOPIC, agent_id)
    clock = BrokerClock(bus.client, _wait_for_epoch(bus))
    _, cfg_hash = _run_identity()
    rogue_identity = issue_identity(agent_id)
    rogue = SignedBus(inner=bus, identity=rogue_identity, topics=frozenset({TRUST_TOPIC}))
    captured: dict[str, _Envelope] = {}

    def capture(m: Any) -> None:
        if not isinstance(m, _Envelope) or m.sender != agent_id or m.signature in captured:
            return
        if rogue_identity.verify(
            payload_bytes(m.topic, m.sender, m.model.model_dump_json()), m.signature
        ):
            return
        captured[m.signature] = m

    bus.subscribe(TRUST_TOPIC, capture)
    tried: Counter[str] = Counter()
    flood = int(os.environ.get("FLOOD_FRAMES_PER_TICK", "0"))
    own_stream = stream_key(TRUST_TOPIC, agent_id)
    heavy = json.dumps(
        {"type": "TrustUpdate", "body": "{" + " " * (MAX_FRAME_BYTES - 100) + "}"}
    ).encode()
    for t in range(max(0, math.ceil(clock.ticks())), TICKS):
        clock.wait_until(t + 0.3)
        bus.pump()
        forged = TrustUpdate(
            sim_time=float(t),
            run_id=RUN_ID,
            seed=SEED,
            config_hash=cfg_hash,
            node_id=victim,
            node_trust=0.05,
            observation=0.05,
            context=make_context(0.05, 0.05, 0.05, 0.05),
            provenance=tag_synthetic(),
            agent_id=agent_id,
        )
        rogue.publish(TRUST_TOPIC, forged)
        tried["wrong_key"] += 1
        bus.publish(TRUST_TOPIC, forged)
        tried["unsigned"] += 1
        bus.client.xadd(own_stream, {"f": b"\x00not a frame"})
        tried["garbage"] += 1
        for start in range(0, flood, 500):
            batch = bus.client.pipeline(transaction=False)
            for _ in range(min(500, flood - start)):
                batch.xadd(own_stream, {"f": heavy}, maxlen=STREAM_MAXLEN)
            batch.execute()
        tried["flood"] += flood
        try:
            bus.client.xadd(stream_key(TRUST_TOPIC, agent_for(NODES[0])), {"f": b"{}"})
        except NoPermission:
            tried["other_stream_refused_by_broker"] += 1
        bus.publish(
            TRUST_TOPIC,
            _Envelope(TRUST_TOPIC, forged, agent_for(NODES[0]), "0" * 64),
        )
        tried["claims_other_sender"] += 1
        genuine_frames = list(captured.values())
        if genuine_frames:
            genuine = genuine_frames[-1]
            tampered = genuine.model.model_copy(update={"node_trust": 0.05, "observation": 0.05})
            bus.publish(
                TRUST_TOPIC, _Envelope(genuine.topic, tampered, genuine.sender, genuine.signature)
            )
            tried["tampered"] += 1
            bus.publish(TRUST_TOPIC, genuine)
            tried["replayed"] += 1
        if len(genuine_frames) > 2:
            bus.publish(TRUST_TOPIC, genuine_frames[-3])
            tried["replayed_stale"] += 1
    tried["memory_without_token_refused"] = int(_memory_refuses(None))
    _log(role="impersonator", victim=victim, attempts=dict(tried), captured=len(captured))
    return 0


def _csv(var: str) -> list[str]:
    return [x for x in os.environ.get(var, "").split(",") if x]


def _verifier_record(outcome: Any) -> Any:
    """The verifier's verdict on a tick, as an audit record the console can read."""
    from console.stream import VERIFIER_EVENT
    from shared.schemas import AuditRecord

    return AuditRecord(
        sim_time=outcome.sim_time,
        run_id=outcome.correlation.run_id,
        seed=outcome.correlation.seed,
        config_hash=outcome.correlation.config_hash,
        event_type=VERIFIER_EVENT,
        actor_id="verifier",
        payload={"verdict": outcome.report.verdict.value, "findings": outcome.report.codes()},
    )


def console() -> int:
    """The operator console on the deployment: it reads the control plane's streams."""
    import threading

    from redis.exceptions import NoPermissionError

    from agents.planner import PLAN_TOPIC
    from console.stream import StreamFleet
    from m10_persona_drift.nhi import issue_signing_identity
    from shared.clock import WallClock
    from shared.redis_bus import stream_key

    bus = _connect("console")
    signer = issue_signing_identity("console", seed=(SECRETS / "console.key").read_bytes())
    fleet = StreamFleet(bus, NODES, run_id=RUN_ID, signer=signer)
    scripted = os.environ.get("CONSOLE_AUTO_DECIDE")
    answered: set[tuple[str, float]] = set()
    judge = _judge(os.environ.get("CONSOLE_AUTO_ADJUDICATE"))
    judged: set[str] = set()
    port = os.environ.get("CONSOLE_PORT")
    if port:
        import uvicorn

        from console.accounts import Accounts
        from console.app import create_app

        data = Path("/tmp/console")
        data.mkdir(exist_ok=True)
        accounts = Accounts(data / "accounts.db", now=WallClock().now)
        password = secrets.token_urlsafe(12)
        accounts.create("auditor", password, "auditor")
        app = create_app(accounts, fleet)
        server = uvicorn.Server(
            uvicorn.Config(app, host="0.0.0.0", port=int(port), log_level="warning")  # noqa: S104
        )
        threading.Thread(target=server.run, name="console-http", daemon=True).start()
        _log(role="console", url=f"http://127.0.0.1:{port}", username="auditor", password=password)

    real = RealClock()
    deadline = real.now() + (TICKS + LEAD_TICKS + 30) * TICK_SECONDS
    while fleet.tick < TICKS - 1 and real.now() < deadline:
        fleet.step()
        for question in list(fleet.pending.values()) if scripted else []:
            if (question.node_id, question.sim_time) not in answered:
                answered.add((question.node_id, question.sim_time))
                fleet.submit(
                    "approve",
                    node_id=question.node_id,
                    approved=scripted == "approve",
                    reason="scripted operator (wire test)",
                    user="scripted",
                ).result()
                _log(role="console", answered=question.node_id, approved=scripted == "approve")
        for review in [q for q in list(fleet.reviews.values()) if q.open] if judge else []:
            if review.record_id not in judged:
                judged.add(review.record_id)
                verdict = judge(review)
                fleet.submit(
                    "adjudicate", record_id=review.record_id, status=verdict, user="scripted"
                ).result()
                _log(role="console", adjudicated=review.record_id, status=verdict)
    for _ in range(10):
        fleet.step()
    try:
        bus.client.xadd(stream_key(PLAN_TOPIC, "control"), {"f": b"{}"})
        write_refused = False
    except NoPermissionError:
        write_refused = True
    checks = {
        "console saw every device": all(r["reporting"] for r in fleet.rows.values()),
        "console followed the run to its end": fleet.tick >= TICKS - 2,
        "console saw the response engine act": fleet.received["AuditRecord"] > 0,
        "broker refuses the console a write to the control plane's streams": write_refused,
    }
    _log(role="console", worst_level=fleet.worst, received=dict(fleet.received), checks=checks)
    if not port:
        return 0 if all(checks.values()) else 1
    while True:
        fleet.step()


def _judge(mode: str | None) -> Any:
    """A stand-in operator for unattended runs: `confirm`, `benign`, or `oracle`."""
    if mode is None:
        return None
    if mode == "oracle":
        from agents.adjudication import OracleAdjudicator

        return OracleAdjudicator(compromised=_scenario().compromised).adjudicate
    status = {"confirm": "confirmed", "benign": "benign"}[mode]
    return lambda _: status


def main(argv: list[str]) -> int:
    role = argv[1] if len(argv) > 1 else ""
    if role == "provision":
        return provision(SECRETS)
    if role == "memory":
        return memory()
    if role == "attest":
        return attest()
    if role == "fuse":
        return fuse()
    if role == "control":
        return control()
    if role == "console":
        return console()
    if role == "node":
        return node()
    if role == "sense":
        return sense()
    if role == "impersonate":
        return impersonate()
    roles = "provision|memory|attest|fuse|control|node|sense|impersonate|console"
    print(f"usage: python -m deploy.wire {{{roles}}}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
