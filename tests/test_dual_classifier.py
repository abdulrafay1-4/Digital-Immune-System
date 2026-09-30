"""Dual classification: the defence against a classifier steering the operator."""

from __future__ import annotations

from agents.dual_classifier import DualClassifier
from agents.orchestrator import TickBatch
from agents.rules_classifier import RulesClassifier
from shared.schemas import Classification, ContextVector, Provenance, TrustUpdate


def _batch(level: float = 0.10, n_bad: int = 3, n_total: int = 6) -> TickBatch:
    return TickBatch(
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
                node_trust=level if i < n_bad else 0.95,
                observation=level if i < n_bad else 0.95,
                context=ContextVector(
                    identity=level if i < n_bad else 0.95,
                    behavioral=level if i < n_bad else 0.95,
                    device=level if i < n_bad else 0.95,
                    network=level if i < n_bad else 0.95,
                ),
                provenance=Provenance.HIGH,
                agent_id=f"mon-{i}",
            )
            for i in range(n_total)
        ],
    )


class _Liar:
    """A compromised classifier: a real campaign, reported as nothing."""

    def classify(self, batch: TickBatch) -> Classification:
        return Classification(
            sim_time=batch.sim_time,
            run_id=batch.run_id,
            seed=batch.seed,
            config_hash=batch.config_hash,
            threat_type="none",
            severity=0.05,
            rationale="all clear",
            used_llm=True,
        )


def test_the_rules_verdict_is_always_carried_alongside() -> None:
    result = DualClassifier().classify(_batch())
    assert result.rules_threat_type is not None
    assert result.rules_severity is not None
    assert result.classifiers_agree is True


def test_a_lying_classifier_cannot_hide_behind_its_own_label() -> None:
    """The operator sees both, so the disagreement is the signal."""
    dual = DualClassifier(primary=_Liar())
    result = dual.classify(_batch())

    assert result.threat_type == "none", "the model's verdict is still reported"
    assert result.rules_threat_type != "none", "and contradicted in the same record"
    assert result.classifiers_agree is False


def test_divergence_rate_is_the_behavioural_baseline() -> None:
    """A sustained rise is what a hijacked classifier looks like to M10."""
    honest = DualClassifier()
    for _ in range(5):
        honest.classify(_batch())
    assert honest.divergence_rate == 0.0
    assert honest.agreement_rate == 1.0

    hijacked = DualClassifier(primary=_Liar())
    for _ in range(5):
        hijacked.classify(_batch())
    assert hijacked.divergence_rate == 1.0


def test_divergence_is_zero_with_nothing_observed() -> None:
    assert DualClassifier().divergence_rate == 0.0


def test_with_no_model_both_halves_agree_by_construction() -> None:
    """Safe to install everywhere: the rules-only configuration costs nothing."""
    dual = DualClassifier(primary=RulesClassifier())
    for _ in range(3):
        assert dual.classify(_batch()).classifiers_agree is True
    assert dual.divergence_rate == 0.0


def test_a_quiet_fleet_agrees_too() -> None:
    result = DualClassifier().classify(_batch(n_bad=0))
    assert result.classifiers_agree is True


def test_the_primary_verdict_is_not_overwritten() -> None:
    """Annotated, not replaced: the ablation must be able to separate them."""
    result = DualClassifier(primary=_Liar()).classify(_batch())
    assert result.severity == 0.05
    assert result.used_llm is True
    assert result.rationale == "all clear"
