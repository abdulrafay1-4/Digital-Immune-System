"""The memory server over a real network transport: streamable HTTP and bearer tokens."""

from __future__ import annotations

import socket
import threading
import time
from collections.abc import Iterator

import pytest

from agents.context_broker import CORRELATION_CLIENT, CURATOR_CLIENT, InProcBroker
from agents.mcp_broker import (
    CORE_CLIENT,
    MCP_AVAILABLE,
    McpBroker,
    ProvisionedTokens,
    build_server,
    issue_token,
)
from m5_immune_memory import IncidentSummary
from m8_eval_harness.baselines.base import _memory
from m10_persona_drift.nhi import issue_signing_identity
from m11_memory_hardening.quorum import attest
from shared.schemas import Provenance

pytestmark = pytest.mark.skipif(not MCP_AVAILABLE, reason="the mcp extra is not installed")

CAMPAIGN = "three controllers sliding together on device and network dimensions"
KEY = b"k" * 32
CLIENTS = (CORRELATION_CLIENT, CURATOR_CLIENT, CORE_CLIENT)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture(scope="module")
def memory() -> Iterator[dict]:
    """A memory server on a local port, holding one confirmed record."""
    import uvicorn

    identities = {c: issue_signing_identity(c) for c in CLIENTS}
    port = _free_port()
    url = f"http://127.0.0.1:{port}/mcp"
    tokens = ProvisionedTokens(key=KEY, now=lambda: 100.0)
    built: dict = {"url": url, "identities": identities, "tokens": tokens}
    ready = threading.Event()

    def run() -> None:
        query, writer, attesters = _memory("mcp-network")
        writer.initial_status = "confirmed"
        writer.propose_and_submit(
            IncidentSummary(
                record_id="rec-1",
                node_ids=("n-1",),
                peak_level=3,
                threat_type="device_compromise",
                pattern_text=CAMPAIGN,
                window_start_sim=1.0,
                window_end_sim=5.0,
                run_id="mcp-network",
                seed=1,
                config_hash="h",
            ),
            {n: a.identity for n, a in attesters.items()},
            now_sim=5.0,
        )
        broker = InProcBroker(query=query, write_path=writer, run_id="mcp-network", seed=1)
        server = build_server(
            broker, {c: i.public() for c, i in identities.items()}, tokens=tokens, resource_url=url
        )
        app = server.streamable_http_app(host="127.0.0.1")
        uv = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
        built.update(broker=broker, attesters=attesters, writer=writer, uvicorn=uv)
        ready.set()
        uv.run()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    ready.wait(timeout=10)
    deadline = time.monotonic() + 10
    while not built["uvicorn"].started and time.monotonic() < deadline:
        time.sleep(0.02)
    yield built
    built["uvicorn"].should_exit = True
    thread.join(timeout=5)


def _client(memory: dict, *, token: str | None = "valid", **kw) -> McpBroker:
    if token == "valid":
        token = issue_token("control", KEY, audience=memory["url"], expires_at=1000)
    kw.setdefault("identities", memory["identities"])
    return McpBroker(url=memory["url"], token=token, **kw)


def test_a_remote_client_recalls_after_the_core_sets_the_tick(memory: dict) -> None:
    client = _client(memory).at(6.0, Provenance.HIGH, fleet_size=3)
    assert memory["broker"].now == 6.0, "the core's signed tick reached the server"
    best = client.recognise(CAMPAIGN).best
    assert best.record_id == "rec-1" and best.threat_type == "device_compromise"


@pytest.mark.parametrize(
    "token",
    [
        None,
        issue_token("control", KEY, audience="http://elsewhere/mcp", expires_at=1000),
        issue_token("control", b"x" * 32, audience="http://127.0.0.1/mcp", expires_at=1000),
        "not-a-token",
    ],
    ids=["no token", "another server's token", "forged token", "garbage"],
)
def test_a_request_without_a_token_for_this_server_never_reaches_a_tool(
    memory: dict, token: str | None
) -> None:
    requests_before = memory["broker"].requests
    with pytest.raises(Exception):  # noqa: B017
        _client(memory, token=token)
    assert memory["broker"].requests == requests_before


def test_an_expired_token_is_refused(memory: dict) -> None:
    expired = issue_token("control", KEY, audience=memory["url"], expires_at=50)
    with pytest.raises(Exception):  # noqa: B017
        _client(memory, token=expired)
    assert memory["tokens"].refused["expired_token"] >= 1


def test_only_the_core_moves_the_tick(memory: dict) -> None:
    client = _client(memory).at(7.0, Provenance.HIGH, fleet_size=3)
    reader = dict(memory["identities"])
    del reader[CORE_CLIENT]
    impostor = _client(memory, identities=reader)
    impostor.identities[CORE_CLIENT] = issue_signing_identity(CORE_CLIENT)
    impostor.at(99.0)
    assert memory["broker"].now == 7.0, "an unregistered core key moved nothing"
    client.at(3.0)
    assert memory["broker"].now == 7.0, "the tick never goes backwards"


def test_the_servers_quorum_decides_a_write_made_over_the_wire(memory: dict) -> None:
    client = _client(memory).at(8.0, Provenance.HIGH, fleet_size=3)
    candidate = memory["writer"].curator.propose(
        IncidentSummary(
            record_id="rec-2",
            node_ids=("n-2",),
            peak_level=3,
            threat_type="network_intrusion",
            pattern_text="a different campaign shape",
            window_start_sim=6.0,
            window_end_sim=8.0,
            run_id="mcp-network",
            seed=1,
            config_hash="h",
        )
    )
    signers = [a.identity for _, a in sorted(memory["attesters"].items())]
    two = [attest(candidate, s, sim_time=8.0) for s in signers[:2]]
    refused = client.submit(candidate, two, now_sim=8.0)
    assert not refused.admitted and refused.reason.startswith("quorum_not_met")
    three = [attest(candidate, s, sim_time=8.0) for s in signers[:3]]
    assert client.submit(candidate, three, now_sim=8.0).admitted
