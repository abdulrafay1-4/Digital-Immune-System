"""The named security experiments: the quorum cliff and the compromised-agent sweep."""

from __future__ import annotations

from m8_eval_harness.security_experiments import (
    compromised_agent_experiment,
    overhead_experiment,
    quorum_experiment,
)


def test_no_malicious_write_is_admitted_below_k() -> None:
    """The formal claim, as an experiment: below k of n, nothing malicious lands."""
    rows = quorum_experiment(trials=25, k=3)
    below = [r for r in rows if r["compromised_attesters"] < 3]
    at_or_above = [r for r in rows if r["compromised_attesters"] >= 3]

    assert below and all(r["malicious_accepted"] == 0 for r in below)
    assert all(r["malicious_acceptance_rate"] == 1.0 for r in at_or_above)


def test_the_quorum_costs_availability_once_too_few_honest_attesters_remain() -> None:
    rows = quorum_experiment(trials=10, k=3)
    by_compromised = {r["compromised_attesters"]: r for r in rows}
    assert by_compromised[0]["valid_acceptance_rate"] == 1.0
    assert by_compromised[3]["valid_acceptance_rate"] == 0.0, "only two honest attesters left"


def test_lying_monitors_are_quarantined_and_the_fleet_still_detects() -> None:
    rows = compromised_agent_experiment(
        fractions=(0.0, 0.2), n_nodes=40, ticks=25, seeds=(7900,), arms=("full",)
    )
    clean, compromised = rows
    assert clean["agents_quarantined"] == 0
    assert compromised["agents_quarantined"] == compromised["compromised_monitors"] > 0
    assert compromised["device_tpr"] == 1.0, "the lie does not hide the device"
    assert compromised["false_restriction_rate"] == 0.0, "and it frames nobody"


def test_overhead_reports_a_cost_for_each_mechanism() -> None:
    rows = overhead_experiment(scenario_id="s1", seeds=(20000,))
    arms = {r["arm"]: r for r in rows}
    assert all(r["tick_ms_p50"] > 0 for r in rows), "every mechanism reports a cost"
    assert arms["full_mcp"]["memory_read_ms_p50"] > arms["full"]["memory_read_ms_p50"], (
        "mediation over a protocol costs more than a method call"
    )
