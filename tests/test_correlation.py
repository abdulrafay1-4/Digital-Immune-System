"""M3 reliability-weighted CTI fusion."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from agents.correlation import (
    AgentReliabilityTracker,
    CorrelationAgent,
    CorrelationParams,
    indicators_from,
)
from agents.orchestrator import TickBatch
from shared.schemas import ContextVector, Provenance, TrustUpdate

RUN = dict(run_id="test", seed=7, config_hash="cafebabecafebabe")


def node(
    node_id: str,
    trust: float,
    *,
    agent_id: str | None = None,
    dims: tuple[float, float, float, float] | None = None,
    observation: float | None = None,
) -> TrustUpdate:
    """An honest report by default: observation is the mean of the dimensions."""
    d = dims if dims is not None else (0.9, 0.9, 0.9, 0.9)
    honest_obs = sum(d) / 4
    return TrustUpdate(
        sim_time=0.0,
        node_id=node_id,
        node_trust=trust,
        observation=honest_obs if observation is None else observation,
        context=ContextVector(identity=d[0], behavioral=d[1], device=d[2], network=d[3]),
        provenance=Provenance.MEDIUM,
        agent_id=agent_id or f"mon-{node_id}",
        **RUN,
    )


def batch(*updates: TrustUpdate, sim_time: float = 0.0) -> TickBatch:
    return TickBatch(sim_time=sim_time, updates=list(updates), **RUN)


def test_threat_indicator_is_the_inverse_of_node_trust() -> None:
    inds = indicators_from(batch(node("a", 0.25)), CorrelationParams())
    assert inds[0].ti_score == pytest.approx(0.75)
    assert inds[0].reporter_agent_id == "mon-a"


def test_honest_report_passes_the_integrity_check() -> None:
    inds = indicators_from(batch(node("a", 0.3, dims=(0.1, 0.2, 0.3, 0.4))), CorrelationParams())
    assert inds[0].integrity_ok is True


def test_forged_report_fails_the_integrity_check() -> None:
    """Context says severely degraded, observation claims healthy."""
    forged = node("a", 0.95, dims=(0.1, 0.1, 0.1, 0.1), observation=0.95)
    inds = indicators_from(batch(forged), CorrelationParams())
    assert inds[0].integrity_ok is False


def test_reporting_a_real_attack_does_not_fail_integrity() -> None:
    """The whole point: an honest agent on a compromised node stays credible."""
    victim = node("a", 0.05, dims=(0.02, 0.03, 0.04, 0.05))
    inds = indicators_from(batch(victim), CorrelationParams())
    assert inds[0].ti_score > 0.9
    assert inds[0].integrity_ok is True


def test_equal_reliability_gives_a_plain_average() -> None:
    agent = CorrelationAgent()
    result = agent.correlate(batch(node("a", 0.2), node("b", 0.8)))
    assert result.cti == pytest.approx(0.5)


def test_a_less_reliable_reporter_counts_for_less() -> None:
    params = CorrelationParams(k=2.0)
    tracker = AgentReliabilityTracker(params)
    tracker._r["mon-a"] = 1.0
    tracker._r["mon-b"] = 0.2
    agent = CorrelationAgent(params, tracker)

    result = agent.correlate(batch(node("a", 0.1), node("b", 1.0)))

    assert result.cti == pytest.approx(0.9 * (1.0 / 1.04), abs=1e-6)
    assert result.cti > 0.8


def test_k_sharpens_the_weighting() -> None:
    """
    The reason for correction #2: linear weighting barely differs from uniform, so C2 would look
    like a null result.
    """

    def cti_at(k: float) -> float:
        params = CorrelationParams(k=k)
        tracker = AgentReliabilityTracker(params)
        tracker._r["mon-a"] = 0.9
        tracker._r["mon-b"] = 0.5
        return (
            CorrelationAgent(params, tracker).correlate(batch(node("a", 0.0), node("b", 1.0))).cti
        )

    uniform = cti_at(0.0)
    linear = cti_at(1.0)
    sharp = cti_at(4.0)

    assert uniform == pytest.approx(0.5)
    assert linear > uniform
    assert sharp > linear, "higher k must concentrate weight on reliable reporters"


def test_k_zero_is_uniform_weighting() -> None:
    params = CorrelationParams(k=0.0)
    tracker = AgentReliabilityTracker(params)
    tracker._r["mon-a"] = 1.0
    tracker._r["mon-b"] = 0.05
    result = CorrelationAgent(params, tracker).correlate(batch(node("a", 0.0), node("b", 1.0)))
    assert result.cti == pytest.approx(0.5)


def test_quarantined_reporters_get_zero_weight() -> None:
    agent = CorrelationAgent()
    b = batch(node("a", 0.0), node("b", 1.0))

    normal = agent.correlate(b)
    without_a = CorrelationAgent().correlate(b, quarantined_agent_ids=["mon-a"])

    assert normal.cti == pytest.approx(0.5)
    assert without_a.cti == pytest.approx(0.0), "a's report must be excluded"


def test_quarantining_everyone_falls_back_to_uniform_not_zero() -> None:
    """
    Returning CTI=0 would read as 'no threat' exactly when the reporting population is least
    trustworthy.
    """
    agent = CorrelationAgent()
    result = agent.correlate(
        batch(node("a", 0.0), node("b", 0.0)),
        quarantined_agent_ids=["mon-a", "mon-b"],
    )
    assert result.cti == pytest.approx(1.0)


def test_cti_stays_in_range() -> None:
    agent = CorrelationAgent()
    for trust in (0.0, 0.5, 1.0):
        result = agent.correlate(batch(node("a", trust), node("b", trust)))
        assert 0.0 <= result.cti <= 1.0


def test_unseen_agent_starts_at_the_configured_default() -> None:
    tracker = AgentReliabilityTracker(CorrelationParams(r_init=0.75))
    assert tracker.get("never-seen") == pytest.approx(0.75)


def test_forging_reports_erodes_reliability() -> None:
    agent = CorrelationAgent()
    forged = node("a", 0.95, dims=(0.1, 0.1, 0.1, 0.1), observation=0.95)

    before = agent.tracker.get("mon-a")
    for _ in range(5):
        agent.correlate(batch(forged, node("b", 0.9)))
    after = agent.tracker.get("mon-a")

    assert after < before
    assert agent.tracker.get("mon-b") >= before, "the honest reporter is unaffected"


def test_reliability_never_reaches_zero() -> None:
    """Mirrors TS_min: a quarantined agent must be able to earn trust back."""
    params = CorrelationParams(r_min=0.05)
    agent = CorrelationAgent(params)
    forged = node("a", 0.95, dims=(0.1, 0.1, 0.1, 0.1), observation=0.95)

    for _ in range(200):
        agent.correlate(batch(forged))

    assert agent.tracker.get("mon-a") == pytest.approx(0.05)


def test_reliability_recovers_when_reporting_honestly_again() -> None:
    agent = CorrelationAgent()
    forged = node("a", 0.95, dims=(0.1, 0.1, 0.1, 0.1), observation=0.95)
    for _ in range(10):
        agent.correlate(batch(forged))
    damaged = agent.tracker.get("mon-a")

    for _ in range(10):
        agent.correlate(batch(node("a", 0.9)))

    assert agent.tracker.get("mon-a") > damaged


def test_sustained_honest_reporting_of_an_attack_keeps_reliability_high() -> None:
    """
    Regression guard for the trap in the module docstring: the agent on the only compromised node
    must not be down-weighted for saying so.
    """
    agent = CorrelationAgent()
    for _ in range(20):
        agent.correlate(
            batch(
                node("victim", 0.05, dims=(0.05, 0.05, 0.05, 0.05)),
                node("peer-1", 0.9),
                node("peer-2", 0.9),
            )
        )
    assert agent.tracker.get("mon-victim") == pytest.approx(1.0, abs=0.02)


def test_weights_use_reliability_from_the_previous_tick() -> None:
    """Correction #4: fusion reads t-1 and writes t."""
    agent = CorrelationAgent()
    forged = node("a", 0.0, dims=(0.9, 0.9, 0.9, 0.9), observation=0.0)

    first = agent.correlate(batch(forged, node("b", 1.0)))
    second = agent.correlate(batch(forged, node("b", 1.0)))

    assert first.cti > second.cti


def test_consensus_corroboration_is_not_implemented() -> None:
    tracker = AgentReliabilityTracker()
    with pytest.raises(NotImplementedError, match="report integrity only"):
        tracker.observe_outcome("mon-a", confirmed=True)


def test_two_implicated_nodes_form_a_campaign() -> None:
    result = CorrelationAgent().correlate(batch(node("a", 0.1), node("b", 0.2)))
    assert result.campaign_id is not None
    assert result.node_ids == ["a", "b"]


def test_a_single_implicated_node_is_not_a_campaign() -> None:
    result = CorrelationAgent().correlate(batch(node("a", 0.1), node("b", 0.95)))
    assert result.campaign_id is None


def test_healthy_batch_has_no_campaign() -> None:
    result = CorrelationAgent().correlate(batch(node("a", 0.95), node("b", 0.95)))
    assert result.campaign_id is None
    assert result.cti < 0.1


def test_campaign_id_is_deterministic_and_content_addressed() -> None:
    a = CorrelationAgent().correlate(batch(node("x", 0.1), node("y", 0.1), sim_time=3.0))
    b = CorrelationAgent().correlate(batch(node("x", 0.1), node("y", 0.1), sim_time=3.0))
    other = CorrelationAgent().correlate(batch(node("x", 0.1), node("z", 0.1), sim_time=3.0))

    assert a.campaign_id == b.campaign_id
    assert a.campaign_id != other.campaign_id


def test_empty_batch_is_rejected() -> None:
    with pytest.raises(ValueError, match="empty batch"):
        CorrelationAgent().correlate(batch())


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("k", -1.0),
        ("r_init", 1.5),
        ("r_init", -0.1),
        ("r_lambda", 1.1),
        ("r_min", -0.2),
        ("campaign_ti_threshold", 2.0),
        ("campaign_min_nodes", 1),
        ("integrity_tolerance", -1e-9),
    ],
)
def test_out_of_range_params_are_rejected(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        CorrelationParams(**{field: value})


def test_result_carries_run_identity() -> None:
    result = CorrelationAgent().correlate(batch(node("a", 0.5), sim_time=9.0))
    assert result.sim_time == 9.0
    assert result.run_id == RUN["run_id"]
    assert result.seed == RUN["seed"]


def test_correlation_is_deterministic() -> None:
    def once() -> tuple[float, str | None]:
        agent = CorrelationAgent()
        r = agent.correlate(batch(node("a", 0.2), node("b", 0.3), node("c", 0.9)))
        return r.cti, r.campaign_id

    assert once() == once()


def test_correlate_node_populates_state() -> None:
    pytest.importorskip("langgraph.graph")
    from agents.graph import GraphPipeline

    pipeline = GraphPipeline()
    pipeline.run(batch(node("a", 0.1), node("b", 0.2)))

    state = pipeline.results[0]
    assert state.cti is not None and state.cti > 0.5
    assert state.campaign_id is not None
    assert state.correlation is not None
    assert state.trail[0] == "correlate"


class _Recall:
    """Stands in for m5_immune_memory.MemoryQuery without importing FAISS."""

    def __init__(self, boost: float, record_id: str | None = "rec-1") -> None:
        self.boost, self.record_id = boost, record_id
        self.queries: list[str] = []

    def recognise(self, pattern_text: str):
        self.queries.append(pattern_text)
        best = SimpleNamespace(record_id=self.record_id)
        return SimpleNamespace(recognised=self.boost > 0.0, cti_boost=self.boost, best=best)


def _attacked_batch(n_bad: int = 3, n_total: int = 6) -> TickBatch:
    updates = []
    for i in range(n_total):
        bad = i < n_bad
        ctx = (0.9, 0.9, 0.2, 0.2) if bad else (0.95, 0.95, 0.95, 0.95)
        updates.append(
            TrustUpdate(
                sim_time=1.0,
                run_id="r",
                seed=1,
                config_hash="h",
                node_id=f"n-{i}",
                node_trust=0.2 if bad else 0.95,
                observation=0.2 if bad else 0.95,
                context=ContextVector(
                    identity=ctx[0], behavioral=ctx[1], device=ctx[2], network=ctx[3]
                ),
                provenance=Provenance.HIGH,
                agent_id=f"mon-{i}",
            )
        )
    return TickBatch(sim_time=1.0, run_id="r", seed=1, config_hash="h", updates=updates)


def test_the_pattern_describes_the_attack_shape_not_the_devices() -> None:
    """The same attack on other devices must produce the same signature."""
    a = CorrelationAgent().correlate(_attacked_batch())
    b = CorrelationAgent().correlate(_attacked_batch())
    assert a.pattern_text == b.pattern_text
    assert "device" in a.pattern_text and "network" in a.pattern_text
    assert "n-0" not in a.pattern_text, "node ids would make every recurrence unique"


def test_without_recall_nothing_is_added() -> None:
    """This configuration is the `memoryless` evaluation baseline."""
    result = CorrelationAgent().correlate(_attacked_batch())
    assert result.recall_boost == 0.0
    assert result.recalled_record_id is None


def test_recognition_travels_beside_the_measured_score_not_inside_it() -> None:
    """D1: the boost is applied once, by fusion, per device."""
    batch = _attacked_batch()
    baseline = CorrelationAgent().correlate(batch)
    recalled = CorrelationAgent().correlate(batch, recall=_Recall(0.25))

    assert recalled.cti == baseline.cti, "the measured score does not move"
    assert recalled.recall_boost == 0.25
    assert recalled.recalled_record_id == "rec-1"


def test_recall_is_asked_with_the_pattern_the_deterministic_layer_built() -> None:
    """No caller composes its own query, so none can probe memory."""
    recall = _Recall(0.25)
    result = CorrelationAgent().correlate(_attacked_batch(), recall=recall)
    assert recall.queries == [result.pattern_text]


def test_recall_cannot_push_cti_out_of_range() -> None:
    result = CorrelationAgent().correlate(_attacked_batch(), recall=_Recall(0.9))
    assert 0.0 <= result.cti <= 1.0


def test_recall_adds_and_never_replaces() -> None:
    """A poisoned record can raise the number; it cannot author it."""
    quiet = TickBatch(
        sim_time=1.0,
        run_id="r",
        seed=1,
        config_hash="h",
        updates=[
            TrustUpdate(
                sim_time=1.0,
                run_id="r",
                seed=1,
                config_hash="h",
                node_id=f"n-{i}",
                node_trust=0.98,
                observation=0.98,
                context=ContextVector(identity=0.98, behavioral=0.98, device=0.98, network=0.98),
                provenance=Provenance.HIGH,
                agent_id=f"mon-{i}",
            )
            for i in range(5)
        ],
    )
    result = CorrelationAgent().correlate(quiet, recall=_Recall(0.9))
    assert result.implicated_node_ids == []
    assert result.pattern_text == "", "nothing implicated means nothing to recall on"
    assert result.recall_boost == 0.0
