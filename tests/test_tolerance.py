"""
TOLERANCE's node controller, re-built from the paper: the model's arithmetic, the simulator against
hand-derived costs, and eviction of a node that sends nothing.
"""

import numpy as np

from m8_eval_harness.baselines.base import _fusion
from m8_eval_harness.baselines.tolerance import NodeModel, _ToleranceFusion, observation
from m8_eval_harness.params import FROZEN
from shared.bus import InProcBus
from shared.schemas import ContextVector, Provenance, TrustUpdate

MODEL = NodeModel(
    p_a=0.1,
    p_c1=1e-5,
    p_c2=1e-3,
    p_u=0.02,
    z_h=(0.5, 0.3, 0.1, 0.05, 0.02, 0.01, 0.01, 0.005, 0.003, 0.002),
    z_c=(0.002, 0.003, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.31),
)


def test_the_belief_is_appendix_a_e_over_the_live_states() -> None:
    b, o = 0.3, 7
    to_h = 0.7 * 0.9 * (1 - 1e-5) + 0.3 * (1 - 1e-3) * 0.02
    to_c = 0.7 * (1 - 1e-5) * 0.1 + 0.3 * (1 - 1e-3) * 0.98
    expected = 0.2 * to_c / (0.005 * to_h + 0.2 * to_c)
    assert abs(MODEL.belief(b, False, o) - expected) < 1e-12


def test_the_simulated_cost_matches_hand_derived_limits() -> None:
    rng = np.random.default_rng(0)
    assert abs(MODEL.average_cost(0.0, rng, episodes=200) - 1.0) < 1e-9
    never = MODEL.average_cost(1.01, np.random.default_rng(1), episodes=400, horizon=800)
    assert abs(never - 2.0 * 0.1 / 0.12) < 0.08


def test_observations_use_the_papers_ten_values() -> None:
    assert [observation(x) for x in (1.0, 0.95, 0.5, 0.0)] == [0, 0, 5, 9]


def _report(node: str, t: float, level: float) -> TrustUpdate:
    return TrustUpdate(
        sim_time=t,
        run_id="r",
        seed=1,
        config_hash="h",
        node_id=node,
        node_trust=level,
        observation=level,
        context=ContextVector(identity=level, behavioral=level, device=level, network=level),
        provenance=Provenance.HIGH,
        agent_id=f"mon-{node}",
    )


def test_a_node_that_sends_nothing_is_evicted_and_returns_as_a_new_node() -> None:
    fusion = _fusion(InProcBus(), "r", 1, "h", FROZEN, cls=_ToleranceFusion, model=MODEL, alpha=0.9)
    first = fusion.fuse_batch([_report("n-0", 0.0, 0.97), _report("n-1", 0.0, 0.97)])
    assert [u.gt for u in first] == [1.0, 1.0]
    silent = fusion.fuse_batch([_report("n-0", 1.0, 0.97)])
    assert {u.node_id: u.gt for u in silent} == {"n-0": 1.0, "n-1": 0.0}
    back = fusion.fuse_batch([_report("n-0", 2.0, 0.97), _report("n-1", 2.0, 0.97)])
    assert [u.gt for u in back] == [1.0, 1.0]
