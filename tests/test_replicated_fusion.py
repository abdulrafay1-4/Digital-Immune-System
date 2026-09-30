"""Trust fusion run three times, and the majority acts."""

from __future__ import annotations

import pytest

from m6_trust_fusion.replicated import NoMajority, ReplicatedFusion
from m8_eval_harness.baselines import by_id
from m8_eval_harness.evaluation import evaluate
from m8_eval_harness.scenario_runner import run_scenario
from m8_eval_harness.scenarios import by_id as scenario


def _run(arm: str, sid: str = "s1", **kw):
    result = run_scenario(scenario(sid), by_id(arm), **kw)
    return result, evaluate(result)


def _decisions(result) -> list:
    return [
        (
            o.sim_time,
            [(u.node_id, u.gt, u.ts, u.cti_i, u.rep, u.drift_flag) for u in o.gt_updates],
            [(p.node_id, p.proposed_level) for p in o.plans],
            [e.executed for e in o.executions],
            o.reputations,
        )
        for o in result.pipeline.outcomes
    ]


@pytest.mark.parametrize("sid", ["s1", "s3"])
def test_honest_replicas_decide_exactly_what_one_instance_decides(sid: str) -> None:
    single, _ = _run("full", sid)
    replicated, _ = _run("full_replicated_fusion", sid)
    assert _decisions(replicated) == _decisions(single)
    assert replicated.pipeline.fusion.disagreements == 0
    assert replicated.pipeline.engine.gt_inconsistent == 0


def test_a_consistent_suppressing_replica_is_outvoted() -> None:
    _, alone = _run("core_fusion_suppress")
    assert alone["device_tpr"] == 0.0, "one instance: the consistent lie hides the attack"
    result, ev = _run("core_fusion_suppress_replicated")
    assert ev["device_tpr"] == 1.0
    assert result.pipeline.fusion.disagreements > 0, "the lie is still visible as an alarm"


def test_a_consistent_framing_replica_restricts_no_one() -> None:
    _, alone = _run("core_fusion_frame")
    assert alone["false_restriction_rate"] > 0.0
    result, ev = _run("core_fusion_frame_replicated")
    assert ev["false_restriction_rate"] == 0.0
    assert result.pipeline.fusion.disagreements > 0


class _Update:
    def __init__(self, node_id: str, gt: float) -> None:
        self.node_id, self.gt = node_id, gt
        self.ts = self.cti_i = self.cti_trust = self.rep = self.master_score = gt
        self.drift_flag, self.threat_confirmed = 0.0, False


class _Replica:
    def __init__(self, gt: float) -> None:
        self.gt, self.bus = gt, None

    def fuse_batch(self, updates, correlation):
        return [_Update(u, self.gt) for u in updates]


class _Bus:
    def __init__(self) -> None:
        self.published: list = []

    def publish(self, topic, message) -> None:
        self.published.append(message)


@pytest.mark.parametrize("liar", [0.0, 1.0])
def test_the_majority_is_the_honest_value_whichever_way_one_instance_lies(liar: float) -> None:
    bus = _Bus()
    fusion = ReplicatedFusion([_Replica(liar), _Replica(0.6), _Replica(0.6)], bus=bus)
    (chosen,) = fusion.fuse_batch(["n-1"], None)
    assert chosen.gt == 0.6 and bus.published == [chosen]
    assert fusion.disagreements == 1


def test_without_a_majority_fusion_refuses_rather_than_guesses() -> None:
    """
    Two instances disagreeing, the third silent: the tick fails and responses are held (the
    orchestrator's fail-static path).
    """

    class _Silent(_Replica):
        def fuse_batch(self, updates, correlation):
            return []

    bus = _Bus()
    fusion = ReplicatedFusion([_Replica(1.0), _Replica(0.6), _Silent(0.0)], bus=bus)
    with pytest.raises(NoMajority):
        fusion.fuse_batch(["n-1"], None)
    assert bus.published == []


@pytest.mark.parametrize("n", [2, 4])
def test_an_even_or_too_small_number_of_instances_is_refused(n: int) -> None:
    with pytest.raises(ValueError):
        ReplicatedFusion([_Replica(0.5) for _ in range(n)], bus=_Bus())


@pytest.mark.parametrize("mode", ["suppress", "frame"])
def test_five_instances_outvote_two_colluding_liars_and_three_do_not(mode: str) -> None:
    metric = "device_tpr" if mode == "suppress" else "false_restriction_rate"
    honest = 1.0 if mode == "suppress" else 0.0
    _, five = _run(f"core_fusion_{mode}_replicated_2of5")
    assert five[metric] == honest
    _, three = _run(f"core_fusion_{mode}_replicated_2of3")
    assert three[metric] != honest, "two of three is a majority: the stated limit"
