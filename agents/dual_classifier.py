"""Dual classification: the model and the rules classifier, on every batch."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from agents.orchestrator import TickBatch
from agents.rules_classifier import RulesClassifier
from shared.schemas import Classification


class Classifier(Protocol):
    def classify(self, batch: TickBatch) -> Classification: ...


@dataclass
class DualClassifier:
    """Runs both, returns the primary's verdict annotated with the rules verdict."""

    primary: Classifier = field(default_factory=RulesClassifier)
    rules: RulesClassifier = field(default_factory=RulesClassifier)

    window: int = 1024
    observations: list[tuple[str, str]] = field(default_factory=list)

    primary_failures: int = 0

    def classify(self, batch: TickBatch) -> Classification:
        reference = self.rules.classify(batch)
        try:
            verdict = self.primary.classify(batch)
        except Exception:  # noqa: BLE001
            self.primary_failures += 1
            verdict = reference.model_copy(update={"used_llm": False})
        agree = verdict.threat_type == reference.threat_type
        self.observations.append((verdict.threat_type, reference.threat_type))
        if len(self.observations) > self.window:
            del self.observations[0]

        return verdict.model_copy(
            update={
                "rules_threat_type": reference.threat_type,
                "rules_severity": reference.severity,
                "classifiers_agree": agree,
            }
        )

    @property
    def availability(self) -> float:
        """Fraction of batches the primary answered."""
        if not self.observations:
            return 1.0
        return 1.0 - self.primary_failures / len(self.observations)

    @property
    def divergence_rate(self) -> float:
        """Fraction of batches where the two disagreed."""
        if not self.observations:
            return 0.0
        disagreements = sum(1 for a, b in self.observations if a != b)
        return disagreements / len(self.observations)

    @property
    def agreement_rate(self) -> float:
        return 1.0 - self.divergence_rate
