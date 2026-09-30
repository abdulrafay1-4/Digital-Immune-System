"""The container twin's comparison, overlay and attacker placement (no Docker needed)."""

from deploy import wire
from m8_eval_harness.container_twin import _overlay, compare
from m8_eval_harness.scenarios.catalogue import by_id


def test_compare_counts_every_device_tick_and_names_the_differences() -> None:
    sim = {0: {"node-0": 0, "node-1": 2}, 1: {"node-0": 3}}
    box = {0: {"node-0": 0, "node-1": 2}, 1: {"node-0": 2}, 2: {"node-0": 0}}
    result = compare(sim, box)
    assert result["device_ticks"] == 3
    assert result["identical"] == 2
    assert result["first_differences"] == [(1, "node-0", 3, 2)]
    assert result["ticks_only_in_containers"] == [2]


def test_overlay_adds_a_container_per_device_and_stolen_keys_only_for_the_poisoner() -> None:
    env = {"DIS_SEED": "101", "DIS_SCENARIO": "s5", "HOME": "/x"}
    poisoner = _overlay(by_id("s5"), env)
    assert sorted(poisoner["volumes"]) == sorted(f"node-{i}-secrets" for i in range(3, 30))
    assert poisoner["services"]["node-29"]["environment"]["NODE_ID"] == "node-29"
    assert "HOME" not in poisoner["services"]["node-29"]["environment"]
    assert len(poisoner["services"]["control"]["volumes"]) == 2
    assert _overlay(by_id("s1"), env)["services"]["control"]["volumes"] == []


def test_each_attacker_runs_where_its_stolen_key_is() -> None:
    assert wire._adversary(by_id("s4"), "node-0") is not None
    assert wire._adversary(by_id("s4"), "control") is None
    assert wire._adversary(by_id("s6"), "node-1") is not None
    assert wire._adversary(by_id("a5"), "control") is not None
    assert wire._adversary(by_id("s5"), "control") is not None
    assert wire._adversary(by_id("s1"), "control") is None
