"""Golden run: a fixed seed gives a byte-identical event log."""

from __future__ import annotations

from pathlib import Path

from m8_eval_harness.simulator import run_walking_skeleton

RESULTS = Path(__file__).resolve().parents[1] / "results" / "_golden"


def test_walking_skeleton_is_deterministic() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    _, a = run_walking_skeleton(
        seed=42,
        n_nodes=3,
        ticks=5,
        run_id="golden",
        results_dir=RESULTS / "a",
    )
    _, b = run_walking_skeleton(
        seed=42,
        n_nodes=3,
        ticks=5,
        run_id="golden",
        results_dir=RESULTS / "b",
    )
    assert a == b
    assert len(a) > 0


def test_different_seed_changes_log_identity_fields() -> None:
    _, a = run_walking_skeleton(seed=1, run_id="s1", results_dir=RESULTS / "s1")
    _, b = run_walking_skeleton(seed=2, run_id="s2", results_dir=RESULTS / "s2")
    assert a != b
