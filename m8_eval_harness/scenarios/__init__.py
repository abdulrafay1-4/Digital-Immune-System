"""Evaluation scenarios. The calibration set stays disjoint from every evaluation scenario."""

from m8_eval_harness.scenarios.adversaries import (
    CompromisedAgent,
    HealingWeaponiser,
    MemoryPoisoner,
)
from m8_eval_harness.scenarios.base import DIMENSIONS, Adversary, Anomaly, Scenario
from m8_eval_harness.scenarios.catalogue import (
    ADAPTIVE,
    CALIBRATION,
    RESILIENCE,
    SCENARIOS,
    by_id,
)

__all__ = [
    "ADAPTIVE",
    "CALIBRATION",
    "DIMENSIONS",
    "RESILIENCE",
    "SCENARIOS",
    "Adversary",
    "Anomaly",
    "CompromisedAgent",
    "HealingWeaponiser",
    "MemoryPoisoner",
    "Scenario",
    "by_id",
]
