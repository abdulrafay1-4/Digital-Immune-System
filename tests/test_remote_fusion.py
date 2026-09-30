"""Trust fusion instances in their own processes, over the broker (a fake one here)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from m6_trust_fusion.fusion import TrustFusionEngine
from m6_trust_fusion.remote import (
    FusionReplicaService,
    RemoteFusion,
    call_topic,
    replica_user,
    reply_topic,
)
from m6_trust_fusion.replicated import ReplicatedFusion, _Discard
from m8_eval_harness.baselines import by_id
from m8_eval_harness.baselines.base import Baseline, _assemble, _fusion
from m8_eval_harness.baselines.compromised_core import _CompromisedFusion
from m8_eval_harness.evaluation import evaluate
from m8_eval_harness.params import FROZEN
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios import by_id as scenario
from shared.redis_bus import RedisBus
from shared.schemas import FusionCall, FusionReply
from tests.test_redis_bus import _Broker, _Client

NAMES = ("a", "b", "c")


def _remote(liar: str | None = None, silent: str | None = None) -> Baseline:
    """The full system with its three fusion instances behind a broker."""

    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        broker = _Broker()
        services = []
        for name in NAMES:
            engine: Any = _fusion(
                _Discard(),
                run_id,
                seed,
                config_hash,
                params,
                cls=_CompromisedFusion if name == liar else TrustFusionEngine,
            )
            engine.mode = "suppress"
            link = RedisBus(_Client(broker), publisher=replica_user(name))
            services.append(FusionReplicaService(engine, link, name))
        core = RedisBus(_Client(broker), publisher="control")

        def poll() -> None:
            for service in services:
                if service.name != silent:
                    service.step(timeout=0)
            core.pump(timeout=0)

        proxies = [
            RemoteFusion(
                core, n, params.fusion_params(), run_id, seed, config_hash, poll=poll, max_polls=3
            )
            for n in NAMES
        ]
        fusion = ReplicatedFusion(proxies, bus=bus)
        pipeline = _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            fusion=fusion,  # type: ignore[arg-type]
            approval=approval,
        )
        pipeline.engine.fusion_params = fusion.params
        return pipeline

    return Baseline("full_remote_fusion", "Full system, fusion in three processes", None, "", build)


def _decisions(result) -> list:
    return [
        (
            o.sim_time,
            [(u.node_id, u.gt, u.ts, u.cti_i, u.rep, u.drift_flag) for u in o.gt_updates],
            [(p.node_id, p.proposed_level) for p in o.plans],
            o.reputations,
        )
        for o in result.pipeline.outcomes
    ]


def test_remote_instances_decide_exactly_as_one_local_engine() -> None:
    local = run_scenario(scenario("s3"), by_id("full"))
    remote = run_scenario(scenario("s3"), _remote())
    assert _decisions(remote) == _decisions(local)
    assert remote.pipeline.fusion.disagreements == 0


def test_a_lying_instance_in_its_own_process_is_outvoted() -> None:
    result = run_scenario(scenario("s1"), _remote(liar="a"))
    assert evaluate(result)["device_tpr"] == 1.0
    assert result.pipeline.fusion.disagreements > 0


def test_a_silent_instance_is_dropped_and_the_loop_goes_on() -> None:
    local = run_scenario(scenario("s1"), by_id("full"))
    result = run_scenario(scenario("s1"), _remote(silent="c"))
    proxies = result.pipeline.fusion.replicas
    assert [p.down for p in proxies] == [False, False, True] and proxies[2].unanswered == 1
    assert [
        (o.sim_time, [(p.node_id, p.proposed_level) for p in o.plans])
        for o in result.pipeline.outcomes
    ] == [
        (o.sim_time, [(p.node_id, p.proposed_level) for p in o.plans])
        for o in local.pipeline.outcomes
    ]


def test_a_private_or_dunder_name_cannot_even_be_sent() -> None:
    with pytest.raises(ValidationError):
        FusionCall(
            sim_time=0, run_id="r", seed=1, config_hash="h", seq=1, method="__class__",
            part=0, parts=1, body="{}",
        )  # fmt: skip


@pytest.mark.parametrize("method", ["signing_key", "params", "observe_trust", "reputation"])
def test_an_instance_serves_only_fusions_own_calls(method: str) -> None:
    broker = _Broker()
    engine = _fusion(_Discard(), "r", 1, "h")
    service = FusionReplicaService(
        engine, RedisBus(_Client(broker), publisher=replica_user("a")), "a"
    )
    core = RedisBus(_Client(broker), publisher="control")
    replies: list[FusionReply] = []
    core.discover = False
    core.subscribe(reply_topic("a"), replies.append)
    core.follow(reply_topic("a"), replica_user("a"))
    core.publish(
        call_topic("a"),
        FusionCall(
            sim_time=0, run_id="r", seed=1, config_hash="h", seq=1, method=method, part=0, parts=1,
            body=json.dumps({"args": [], "kwargs": {}}),
        ),
    )  # fmt: skip
    service.step(timeout=0)
    core.pump(timeout=0)
    assert [r.ok for r in replies] == [False] and service.refused == 1 and service.served == 0


def test_the_broker_lets_an_instance_read_its_calls_and_write_its_answers_only() -> None:
    from deploy.wire import acl_file, broker_users

    acl = acl_file({u: "pw" for u in broker_users()}).decode().splitlines()
    (line,) = [x for x in acl if x.startswith("user fusion-a ")]
    assert "~dis:fusion.reply-a:fusion-a" in line and "%R~dis:fusion.call-a:control" in line
    assert "+scan" not in line and "~dis:*" not in line


def test_a_full_part_fits_in_one_frame_however_it_escapes() -> None:
    """A part is escaped twice on the wire and must still fit in one broker frame."""
    from m6_trust_fusion.remote import CHUNK
    from shared.redis_bus import MAX_FRAME_BYTES, encode

    worst = '"\\' * (CHUNK // 2)
    call = FusionCall(
        sim_time=1.0,
        run_id="r" * 40,
        seed=1,
        config_hash="h" * 64,
        seq=10**6,
        method="fuse_batch",
        part=63,
        parts=64,
        body=worst,
    )
    envelope = 400
    assert len(encode(call)) + envelope <= MAX_FRAME_BYTES
