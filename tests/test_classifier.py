"""Deterministic classifier, LLM classifier, and every way the model can misbehave."""

from __future__ import annotations

import json

import pytest

from agents.classifier import MAX_LISTED_NODES, LLMClassifier
from agents.llm_cache import CachedLLM, FakeLLM
from agents.orchestrator import TickBatch
from agents.rules_classifier import RulesClassifier, RulesParams, ThreatType
from shared.schemas import ContextVector, Provenance, TrustUpdate

RUN = dict(run_id="test", seed=7, config_hash="cafebabecafebabe")

HEALTHY = dict(identity=0.95, behavioral=0.95, device=0.95, network=0.95)


def node(node_id: str, trust: float, **dims: float) -> TrustUpdate:
    ctx = {**HEALTHY, **dims}
    return TrustUpdate(
        sim_time=0.0,
        node_id=node_id,
        node_trust=trust,
        observation=trust,
        context=ContextVector(**ctx),
        provenance=Provenance.MEDIUM,
        agent_id=f"mon-{node_id}",
        **RUN,
    )


def batch(*updates: TrustUpdate, sim_time: float = 0.0) -> TickBatch:
    return TickBatch(sim_time=sim_time, updates=list(updates), **RUN)


def llm_json(**fields: object) -> str:
    return json.dumps(fields)


def test_all_healthy_is_classified_as_none() -> None:
    result = RulesClassifier().classify(batch(node("a", 0.9), node("b", 0.92)))

    assert result.threat_type == ThreatType.NONE.value
    assert result.severity == 0.0
    assert result.used_llm is False
    assert "[none]" in result.rationale


@pytest.mark.parametrize(
    ("degraded_dim", "expected"),
    [
        ("identity", ThreatType.CREDENTIAL_ABUSE),
        ("behavioral", ThreatType.ANOMALOUS_BEHAVIOR),
        ("device", ThreatType.DEVICE_COMPROMISE),
        ("network", ThreatType.NETWORK_ANOMALY),
    ],
)
def test_worst_context_dimension_selects_the_threat_family(
    degraded_dim: str, expected: ThreatType
) -> None:
    victim = node("a", 0.3, **{degraded_dim: 0.1})
    result = RulesClassifier().classify(batch(victim, node("b", 0.9)))

    assert result.threat_type == expected.value
    assert degraded_dim in result.rationale


def test_one_affected_node_is_single_scope() -> None:
    result = RulesClassifier().classify(batch(node("a", 0.3), node("b", 0.9)))
    assert result.rationale.startswith("[single_node]")


def test_two_affected_nodes_read_as_coordinated() -> None:
    result = RulesClassifier().classify(batch(node("a", 0.3), node("b", 0.35)))
    assert result.rationale.startswith("[coordinated]")


def test_severity_combines_depth_and_breadth() -> None:
    result = RulesClassifier().classify(batch(node("a", 0.3), node("b", 0.9)))
    assert result.severity == pytest.approx(0.64)


def test_deeper_compromise_scores_higher() -> None:
    shallow = RulesClassifier().classify(batch(node("a", 0.55), node("b", 0.9)))
    deep = RulesClassifier().classify(batch(node("a", 0.05), node("b", 0.9)))
    assert deep.severity > shallow.severity


def test_wider_spread_scores_higher() -> None:
    narrow = RulesClassifier().classify(
        batch(node("a", 0.3), node("b", 0.9), node("c", 0.9), node("d", 0.9))
    )
    wide = RulesClassifier().classify(
        batch(node("a", 0.3), node("b", 0.3), node("c", 0.3), node("d", 0.3))
    )
    assert wide.severity > narrow.severity


def test_severity_stays_within_range_at_extremes() -> None:
    worst = RulesClassifier().classify(batch(node("a", 0.0, identity=0.0)))
    assert 0.0 <= worst.severity <= 1.0


def test_threshold_is_configurable() -> None:
    strict = RulesClassifier(RulesParams(affected_below=0.95))
    lenient = RulesClassifier(RulesParams(affected_below=0.5))
    b = batch(node("a", 0.7), node("b", 0.9))

    assert strict.classify(b).threat_type != ThreatType.NONE.value
    assert lenient.classify(b).threat_type == ThreatType.NONE.value


def test_classification_is_deterministic() -> None:
    b = batch(node("a", 0.3, network=0.1), node("b", 0.9))
    first = RulesClassifier().classify(b)
    second = RulesClassifier().classify(b)
    assert first.model_dump() == second.model_dump()


def test_tie_between_dimensions_resolves_stably() -> None:
    """Equally degraded dimensions must not flip between runs."""
    b = batch(node("a", 0.3, identity=0.2, behavioral=0.2, device=0.2, network=0.2))
    verdicts = {RulesClassifier().classify(b).threat_type for _ in range(20)}
    assert len(verdicts) == 1


def test_empty_batch_is_rejected() -> None:
    with pytest.raises(ValueError, match="empty batch"):
        RulesClassifier().classify(batch())


def test_run_identity_is_carried_through() -> None:
    result = RulesClassifier().classify(batch(node("a", 0.3), sim_time=12.0))
    assert result.sim_time == 12.0
    assert result.run_id == RUN["run_id"]
    assert result.config_hash == RUN["config_hash"]


@pytest.mark.parametrize("bad", [-0.1, 1.1])
def test_rules_params_reject_out_of_range_thresholds(bad: float) -> None:
    with pytest.raises(ValueError):
        RulesParams(affected_below=bad)


def test_rules_params_reject_a_coordinated_threshold_below_two() -> None:
    with pytest.raises(ValueError):
        RulesParams(coordinated_min_nodes=1)


def make_llm_classifier(responses: list[str] | str, sim_cost: float = 1.5) -> LLMClassifier:
    return LLMClassifier(CachedLLM(FakeLLM(responses), sim_cost=sim_cost))


def test_valid_model_output_is_used() -> None:
    clf = make_llm_classifier(
        llm_json(threat_type="credential_abuse", severity=0.8, reasoning="mfa failures")
    )
    result = clf.classify(batch(node("a", 0.3)))

    assert result.threat_type == "credential_abuse"
    assert result.severity == pytest.approx(0.8)
    assert result.rationale == "mfa failures"
    assert result.used_llm is True
    assert clf.fallback_count == 0


def test_classification_is_stamped_when_the_model_finished() -> None:
    """sim_time = requested + sim_cost."""
    clf = make_llm_classifier(llm_json(threat_type="none", severity=0.0), sim_cost=1.5)
    result = clf.classify(batch(node("a", 0.3), sim_time=10.0))

    assert result.sim_time == pytest.approx(11.5)


def test_cached_verdict_is_free_and_flagged() -> None:
    clf = make_llm_classifier(llm_json(threat_type="none", severity=0.0), sim_cost=1.5)
    b = batch(node("a", 0.3), sim_time=10.0)

    first = clf.classify(b)
    second = clf.classify(b)

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert second.sim_time == pytest.approx(10.0), "a cache hit costs no sim time"


@pytest.mark.parametrize(
    ("label", "text"),
    [
        ("not json", "the threat is credential abuse"),
        ("empty", ""),
        ("markdown fence", '```json\n{"threat_type":"none"}\n```'),
        ("json array", '["credential_abuse", 0.8]'),
        ("json scalar", '"credential_abuse"'),
        ("missing threat_type", json.dumps({"severity": 0.5})),
        ("missing severity", json.dumps({"threat_type": "none"})),
        ("unknown label", json.dumps({"threat_type": "alien_invasion", "severity": 0.5})),
        ("severity above range", json.dumps({"threat_type": "none", "severity": 1.5})),
        ("severity below range", json.dumps({"threat_type": "none", "severity": -0.2})),
        ("severity as text", json.dumps({"threat_type": "none", "severity": "high"})),
        ("severity null", json.dumps({"threat_type": "none", "severity": None})),
        ("threat_type null", json.dumps({"threat_type": None, "severity": 0.5})),
    ],
)
def test_bad_model_output_falls_back_instead_of_crashing(label: str, text: str) -> None:
    clf = make_llm_classifier(text)
    result = clf.classify(batch(node("a", 0.3, identity=0.1), node("b", 0.9)))

    assert clf.fallback_count == 1, f"{label} should have triggered a fallback"
    assert result.used_llm is False
    assert result.rationale.startswith("[llm-fallback]")
    assert result.threat_type == ThreatType.CREDENTIAL_ABUSE.value


def test_transport_failure_falls_back() -> None:
    clf = LLMClassifier(CachedLLM(FakeLLM([])))
    result = clf.classify(batch(node("a", 0.3)))

    assert clf.fallback_count == 1
    assert result.used_llm is False


def test_fallback_still_charges_sim_time() -> None:
    """
    A call that timed out consumed model time in a real deployment; not charging it would flatter
    detection latency.
    """
    clf = make_llm_classifier("garbage", sim_cost=2.0)
    result = clf.classify(batch(node("a", 0.3), sim_time=5.0))

    assert result.sim_time == pytest.approx(7.0)


def test_extra_keys_in_model_output_are_ignored() -> None:
    clf = make_llm_classifier(
        json.dumps({"threat_type": "none", "severity": 0.1, "confidence": 0.9, "junk": [1, 2]})
    )
    result = clf.classify(batch(node("a", 0.9)))

    assert result.used_llm is True
    assert clf.fallback_count == 0


def test_severity_at_exact_bounds_is_accepted() -> None:
    for value in (0.0, 1.0):
        clf = make_llm_classifier(json.dumps({"threat_type": "none", "severity": value}))
        assert clf.classify(batch(node("a", 0.9))).severity == pytest.approx(value)


def test_empty_batch_is_rejected_before_calling_the_model() -> None:
    client = FakeLLM("{}")
    clf = LLMClassifier(CachedLLM(client))

    with pytest.raises(ValueError, match="empty batch"):
        clf.classify(batch())

    assert client.calls == [], "must not spend a model call on an invalid batch"


def test_prompt_is_stable_for_a_given_batch() -> None:
    """The cache key depends on this."""
    clf = make_llm_classifier("{}")
    b = batch(node("a", 0.3), node("b", 0.9))
    assert clf.build_prompt(b) == clf.build_prompt(b)


def test_prompt_summarises_rather_than_dumping_telemetry() -> None:
    clf = make_llm_classifier("{}")
    prompt = clf.build_prompt(batch(node("a", 0.3), node("b", 0.9)))

    assert "provenance" not in prompt.lower()
    assert "config_hash" not in prompt
    assert "Nodes reporting: 2" in prompt
    assert "Nodes below the trust threshold" in prompt


def test_long_node_lists_are_truncated() -> None:
    clf = make_llm_classifier("{}")
    victims = [node(f"node-{i:02d}", 0.2) for i in range(25)]
    prompt = clf.build_prompt(batch(*victims))

    assert "+15 more" in prompt
    assert prompt.count("node-") <= MAX_LISTED_NODES + 1


def test_prompt_reports_healthy_dimensions_when_nothing_is_affected() -> None:
    clf = make_llm_classifier("{}")
    prompt = clf.build_prompt(batch(node("a", 0.95), node("b", 0.95)))

    assert "Nodes below the trust threshold (0.60): 0" in prompt
    assert "none" in prompt
