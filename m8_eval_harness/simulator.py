"""SimPy drivers: the walking skeleton and the monitoring-agent trust loop."""

from __future__ import annotations

import random
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import simpy
from pydantic import BaseModel

from m1_monitoring.agent import TRUST_TOPIC, MonitoringAgent
from m1_monitoring.core.trust import TrustParams, TrustState
from m1_monitoring.sensors.synthetic import SyntheticTelemetry
from shared.bus import InProcBus
from shared.run_manifest import RunManifest, load_yaml_config, new_manifest
from shared.schemas import ContextVector, SkeletonEvent, TrustUpdate

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "configs" / "default.yaml"


class JsonlSink:
    """Append-only JSONL event log, with deterministic key order via model_dump."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("w", encoding="utf-8", newline="\n")

    def write_model(self, model: BaseModel) -> None:
        self._fh.write(model.model_dump_json() + "\n")

    def close(self) -> None:
        self._fh.close()

    def bytes(self) -> bytes:
        if not self._fh.closed:
            self._fh.flush()
        return self.path.read_bytes()


def run_walking_skeleton(
    *,
    seed: int = 42,
    n_nodes: int = 3,
    ticks: int = 5,
    tick_seconds: float = 1.0,
    run_id: str = "skeleton",
    config: dict[str, Any] | None = None,
    results_dir: Path | None = None,
) -> tuple[RunManifest, bytes]:
    """Walking skeleton: null nodes publish a constant SkeletonEvent to the bus and a JSONL log."""
    cfg = config if config is not None else load_yaml_config(DEFAULT_CONFIG)
    manifest = new_manifest(run_id, seed, cfg, notes="walking-skeleton")
    out_dir = results_dir or (Path("results") / run_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest.write_json(out_dir / "manifest.json")

    bus = InProcBus()
    sink = JsonlSink(out_dir / "events.jsonl")
    bus.subscribe("*", sink.write_model)

    env = simpy.Environment()

    def node_proc(node_id: str) -> Iterator[simpy.Event]:
        for _ in range(ticks):
            evt = SkeletonEvent(
                sim_time=float(env.now),
                run_id=manifest.run_id,
                seed=manifest.seed,
                config_hash=manifest.config_hash,
                node_id=node_id,
                value=1.0,
            )
            bus.publish("skeleton.tick", evt)
            yield env.timeout(tick_seconds)

    for i in range(n_nodes):
        env.process(node_proc(f"node-{i}"))

    env.run()
    sink.close()
    return manifest, sink.bytes()


def trust_settings(cfg: dict[str, Any]) -> tuple[TrustParams, dict[str, float]]:
    """A monitoring agent's parameters from the run config."""
    trust_cfg = cfg.get("trust", {})
    params = TrustParams(
        lam=float(trust_cfg.get("lambda", 0.7)),
        beta=float(trust_cfg.get("beta_decay", 0.01)),
        ts_min=float(trust_cfg.get("ts_min", 0.05)),
        ts_init=float(trust_cfg.get("ts_init", 1.0)),
        lam_up=float(trust_cfg["lambda_up"]) if trust_cfg.get("lambda_up") is not None else None,
    )
    obs_weights = {
        "w_identity": float(trust_cfg.get("w_identity", 0.25)),
        "w_behavioral": float(trust_cfg.get("w_behavioral", 0.25)),
        "w_device": float(trust_cfg.get("w_device", 0.25)),
        "w_network": float(trust_cfg.get("w_network", 0.25)),
    }
    return params, obs_weights


class CompromisedDevice:
    """
    A device under the attacker's control: while its attack runs, its sensor reports what it would
    have measured had there been no attack.
    """

    def __init__(
        self, true: Any, healthy: Any, modes: dict[str, str], observed: tuple[str, ...] = ()
    ) -> None:
        self._true, self._healthy, self._modes = true, healthy, modes
        self._observed = observed

    def read(self, sim_time: float, node_id: str) -> tuple[Any, Any]:
        context, provenance = self._true.read(sim_time, node_id)
        mode = self._modes.get(node_id)
        if mode is None or not self._true.anomaly_active(sim_time, node_id):
            return context, provenance
        forged, _ = self._healthy.read(sim_time, node_id)
        if mode == "unobservable":
            forged = forged.model_copy(update={d: getattr(context, d) for d in self._observed})
        return forged, provenance

    def __getattr__(self, name: str) -> Any:
        return getattr(self._true, name)


def run_trust_sim(
    *,
    seed: int = 42,
    n_nodes: int = 50,
    ticks: int = 30,
    tick_seconds: float = 1.0,
    run_id: str = "trust-phase1",
    anomaly_node: str = "node-0",
    anomaly_window: tuple[float, float, float] = (10.0, 25.0, 0.6),
    anomalies: dict[str, tuple[float, float, float]] | None = None,
    dimension_masks: dict[str, tuple[str, ...]] | None = None,
    config: dict[str, Any] | None = None,
    results_dir: Path | None = None,
    bus: InProcBus | None = None,
    outages: dict[str, tuple[float, float]] | None = None,
    env: simpy.Environment | None = None,
    noise_model: Any | None = None,
    restarts: dict[str, tuple[float, int]] | None = None,
    forged_observation: dict[str, float] | None = None,
    forged_context: dict[str, float] | None = None,
    device_keys: dict[str, Any] | None = None,
    selective_reporting: dict[str, float] | None = None,
    message_loss: float = 0.0,
    dropped: dict[str, tuple[float, float]] | None = None,
    identities: dict[str, Any] | None = None,
    compromised_device: dict[str, str] | None = None,
    observers: tuple[Any, ...] = (),
) -> tuple[RunManifest, dict[str, list[float]], bytes]:
    """N monitored nodes on the virtual clock, by default one anomalous."""
    cfg = config if config is not None else load_yaml_config(DEFAULT_CONFIG)
    params, obs_weights = trust_settings(cfg)

    manifest = new_manifest(run_id, seed, cfg, notes="phase1-trust-sim")
    out_dir = results_dir or (Path("results") / run_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest.write_json(out_dir / "manifest.json")

    bus = bus if bus is not None else InProcBus()
    sink = JsonlSink(out_dir / "events.jsonl")
    from shared.secure_bus import inner_model

    bus.subscribe(TRUST_TOPIC, lambda m: sink.write_model(inner_model(m)))

    resolved = anomalies if anomalies is not None else {anomaly_node: anomaly_window}
    sensor: Any = SyntheticTelemetry(
        seed, anomalies=resolved, dimension_masks=dimension_masks, noise_model=noise_model
    )
    for observer in observers:
        observer.source = sensor
    if compromised_device:
        sensor = CompromisedDevice(
            sensor,
            SyntheticTelemetry(seed, noise_model=noise_model),
            compromised_device,
            observed=tuple(o.dimension for o in observers),
        )
    if device_keys:
        from m1_monitoring.sensors.attested import AttestedTelemetry

        sensor = AttestedTelemetry(sensor, device_keys)
    env = env if env is not None else simpy.Environment()
    down = outages or {}
    restart = restarts or {}
    forged = forged_observation or {}
    patient = forged_context or {}
    selective = selective_reporting or {}
    series: dict[str, list[float]] = {f"node-{i}": [] for i in range(n_nodes)}

    def make_agent(node_id: str) -> MonitoringAgent:
        agent_id = f"mon-{node_id}"
        publish_bus = _publisher_view(bus, identities, agent_id)
        window = (dropped or {}).get(node_id)
        if message_loss > 0.0 or window is not None:
            publish_bus = _LossyLink(publish_bus, node_id, seed, message_loss, window, env)

        class _EnvClock:
            def now(self) -> float:
                return float(env.now)

            def sleep(self, duration: float) -> None:
                raise RuntimeError("use env.timeout")

        return MonitoringAgent(
            node_id=node_id,
            agent_id=agent_id,
            sensor=sensor,
            bus=publish_bus,
            clock=_EnvClock(),
            run_id=manifest.run_id,
            seed=manifest.seed,
            config_hash=manifest.config_hash,
            trust_params=params,
            obs_weights=obs_weights,
        )

    agents = [make_agent(f"node-{i}") for i in range(n_nodes)]

    def node_proc(agent: MonitoringAgent) -> Iterator[simpy.Event]:
        for _ in range(ticks):
            window = down.get(agent.node_id)
            now = float(env.now)
            if window is not None and window[0] <= now < window[1]:
                agent.state = TrustState.initial(params, sim_time=now)
            else:
                upd = scripted_tick(
                    agent,
                    now,
                    sensor,
                    params,
                    selective=selective,
                    restart=restart,
                    patient=patient,
                    forged=forged,
                )
                if upd is not None:
                    series[agent.node_id].append(upd.node_trust)
            yield env.timeout(tick_seconds)

    for agent in agents:
        env.process(node_proc(agent))

    env.run()
    sink.close()
    return manifest, series, sink.bytes()


def scripted_tick(
    agent: MonitoringAgent,
    now: float,
    sensor: Any,
    params: Any,
    *,
    selective: dict[str, float],
    restart: dict[str, tuple[float, int]],
    patient: dict[str, float],
    forged: dict[str, float],
) -> TrustUpdate | None:
    """One monitor's tick as its scenario scripts it; `None` when it withholds the report."""
    node = agent.node_id
    if node in selective and now >= selective[node] and sensor.anomaly_active(now, node):
        return None
    spec = restart.get(node)
    if spec is not None and now >= spec[0] and int(now - spec[0]) % spec[1] == 0:
        agent.state = TrustState.initial(params, sim_time=now)
    if node in patient and now >= patient[node]:
        return _patient_tick(agent)
    if node in forged and now >= forged[node]:
        return _forged_tick(agent)
    return agent.tick()


def _publisher_view(bus: InProcBus, identities: dict[str, Any] | None, agent_id: str) -> Any:
    """The bus one agent publishes on: its own key, and nobody else's."""
    if not identities or agent_id not in identities:
        return bus
    from shared.secure_bus import SignedBus

    return SignedBus(
        inner=bus,
        identity=identities[agent_id],
        topics=frozenset({TRUST_TOPIC}),
    )


class _LossyLink:
    """Frames lost between a monitor and the control plane."""

    def __init__(
        self,
        inner: Any,
        node_id: str,
        seed: int,
        loss: float,
        window: tuple[float, float] | None,
        env: simpy.Environment,
    ) -> None:
        self._inner, self._node, self._seed = inner, node_id, seed
        self._loss, self._window, self._env = loss, window, env

    def publish(self, topic: str, model: Any) -> None:
        now = float(self._env.now)
        if self._window is not None and self._window[0] <= now < self._window[1]:
            return
        if self._loss and random.Random(f"{self._seed}:{self._node}:{now}").random() < self._loss:
            return
        self._inner.publish(topic, model)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


def _forged_tick(agent: MonitoringAgent) -> TrustUpdate:
    """A compromised monitor: its real context, beside a perfect claimed observation."""
    now = agent.clock.now()
    context, provenance = agent.sensor.read(now, agent.node_id)
    update = TrustUpdate(
        sim_time=now,
        run_id=agent.run_id,
        seed=agent.seed,
        config_hash=agent.config_hash,
        node_id=agent.node_id,
        node_trust=agent.state.step(1.0, now),
        observation=1.0,
        context=context,
        provenance=provenance,
        agent_id=agent.agent_id,
        attestation=_relayed(agent, now),
    )
    agent.bus.publish(TRUST_TOPIC, update)
    return update


def _relayed(agent: MonitoringAgent, now: float) -> str | None:
    """The device's signature over its real measurement: all a monitor can relay."""
    attest = getattr(agent.sensor, "attestation", None)
    return attest(now, agent.node_id) if attest is not None else None


def _patient_tick(agent: MonitoringAgent) -> TrustUpdate:
    """The patient liar: forge the context too, and claim only what a step allows."""
    now = agent.clock.now()
    _, provenance = agent.sensor.read(now, agent.node_id)
    perfect = ContextVector(identity=1.0, behavioral=1.0, device=1.0, network=1.0)
    update = TrustUpdate(
        sim_time=now,
        run_id=agent.run_id,
        seed=agent.seed,
        config_hash=agent.config_hash,
        node_id=agent.node_id,
        node_trust=agent.state.step(1.0, now),
        observation=1.0,
        context=perfect,
        provenance=provenance,
        agent_id=agent.agent_id,
        attestation=_relayed(agent, now),
    )
    agent.bus.publish(TRUST_TOPIC, update)
    return update


def latest_ts(series: dict[str, list[float]], node_id: str) -> float:
    return series[node_id][-1]
