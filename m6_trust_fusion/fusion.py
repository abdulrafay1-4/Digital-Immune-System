"""Global trust fusion: pure math and a thin engine. LLMs never compute GT."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from m1_monitoring.core.observation import observation_from_context
from m6_trust_fusion.master_score import MasterScoreWeights, master_score
from m6_trust_fusion.reputation import (
    ReputationParams,
    ReputationTracker,
    interaction_success,
)
from shared.bus import Bus
from shared.integrity import DEV_KEY, canonical, sign
from shared.schemas import (
    CorrelationResult,
    GlobalTrustUpdate,
    ResponsePlan,
    TrustUpdate,
)

GT_TOPIC = "trust.global"


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def gt_payload(
    *,
    run_id: str,
    seed: int,
    config_hash: str,
    sim_time: float,
    node_id: str,
    gt: float,
    ts: float,
    cti_i: float,
    rep: float,
    drift_flag: float,
) -> bytes:
    """What a GT signature covers."""
    return canonical(run_id, seed, config_hash, sim_time, node_id, gt, ts, cti_i, rep, drift_flag)


@dataclass(frozen=True)
class FusionParams:
    alpha: float = 0.40
    beta: float = 0.35
    gamma: float = 0.25
    drift_coeff: float = 0.3
    implicate_below_ts: float = 0.40
    confirm_below_ts: float = 0.50
    trust_lambda: float = 0.7
    trust_lambda_up: float | None = None
    ts_min: float = 0.05
    obs_weights: tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25)
    step_check: bool = True

    def __post_init__(self) -> None:
        total = self.alpha + self.beta + self.gamma
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"alpha+beta+gamma must sum to 1, got {total}")
        if not 0.0 <= self.implicate_below_ts <= 1.0:
            raise ValueError(f"implicate_below_ts must be in [0, 1], got {self.implicate_below_ts}")
        if not 0.0 <= self.confirm_below_ts <= 1.0:
            raise ValueError(f"confirm_below_ts must be in [0, 1], got {self.confirm_below_ts}")
        if not 0.0 <= self.trust_lambda <= 1.0:
            raise ValueError(f"trust_lambda must be in [0, 1], got {self.trust_lambda}")
        if self.trust_lambda_up is not None and not 0.0 <= self.trust_lambda_up <= 1.0:
            raise ValueError(f"trust_lambda_up must be in [0, 1], got {self.trust_lambda_up}")


def cti_for_node(
    node_id: str,
    correlation: CorrelationResult | None,
    *,
    node_ts: float | None = None,
    implicate_below_ts: float = 0.40,
) -> float:
    """Per-node CTI_i: the campaign score if implicated, else 0."""
    if correlation is None:
        return 0.0
    implicated = node_id in correlation.implicated_node_ids
    if not implicated and node_ts is not None and node_ts < implicate_below_ts:
        implicated = True
    if not implicated:
        return 0.0

    if node_ts is not None and _in_l0_band(node_ts):
        return 0.0

    own = clamp01(correlation.node_ti.get(node_id, 0.0))
    base = max(clamp01(correlation.cti), own) + clamp01(correlation.campaign_corroboration)

    return clamp01(base + clamp01(correlation.recall_boost))


def _in_l0_band(ts: float) -> bool:
    """Would this trust, read on the GT scale, put a device at L0?"""
    from m4_response_engine.levels import level_for_gt

    return level_for_gt(ts) == 0


def fuse_gt(
    *,
    ts: float,
    cti_i: float,
    rep: float,
    params: FusionParams | None = None,
    drift_flag: float = 0.0,
) -> tuple[float, float]:
    """GT = α·TS + β·(1−CTI_i) + γ·REP, then optional drift penalty."""
    p = params or FusionParams()
    cti_trust = clamp01(1.0 - cti_i)
    gt = p.alpha * ts + p.beta * cti_trust + p.gamma * rep
    drift = clamp01(drift_flag)
    gt = gt * (1.0 - p.drift_coeff * drift)
    return clamp01(gt), cti_trust


@dataclass
class _NodeLag:
    """Last published (t−1) inputs used on the next fuse."""

    ts: float = 1.0
    cti_i: float = 0.0
    rep: float = 1.0


@dataclass
class TrustFusionEngine:
    """Consumes TrustUpdates + CorrelationResult; publishes GlobalTrustUpdate."""

    bus: Bus
    run_id: str
    seed: int
    config_hash: str
    params: FusionParams = field(default_factory=FusionParams)
    reputation: ReputationTracker = field(
        default_factory=lambda: ReputationTracker(ReputationParams())
    )
    master_weights: MasterScoreWeights = field(default_factory=MasterScoreWeights)
    signing_key: bytes = DEV_KEY
    _lag: dict[str, _NodeLag] = field(default_factory=dict)
    _latest_corr: CorrelationResult | None = None
    _drift: dict[str, float] = field(default_factory=dict)
    _last_seen: dict[str, float] = field(default_factory=dict)
    _decayed_at: dict[str, float] = field(default_factory=dict)
    trust_rise_capped: int = 0

    def _cti_for(self, node_id: str, node_ts: float) -> float:
        return cti_for_node(
            node_id,
            self._latest_corr,
            node_ts=node_ts,
            implicate_below_ts=self.params.implicate_below_ts,
        )

    def observe_correlation(self, result: CorrelationResult) -> None:
        """Store correlation for next tick's CTI_i (t−1 semantics after first observe)."""
        self._latest_corr = result

    def set_drift(self, node_id: str, drift_flag: float) -> None:
        self._drift[node_id] = clamp01(drift_flag)

    def observe_silence(
        self, node_id: str, *, sim_time: float, beta: float = 0.01
    ) -> GlobalTrustUpdate | None:
        """Re-fuse a node that did not report this tick, with decayed trust."""
        import math

        lag = self._lag.get(node_id)
        if lag is None:
            return None

        since = self._decayed_at.get(node_id, self._last_seen.get(node_id, sim_time))
        dt = max(0.0, sim_time - since)
        decayed = (
            max(self.params.ts_min, clamp01(lag.ts * math.exp(-beta * dt))) if dt > 0 else lag.ts
        )
        self._decayed_at[node_id] = sim_time
        rep = self.reputation.get(node_id)
        gt, cti_trust = fuse_gt(
            ts=decayed,
            cti_i=lag.cti_i,
            rep=rep,
            params=self.params,
            drift_flag=self._drift.get(node_id, 0.0),
        )
        msg = GlobalTrustUpdate(
            signature=sign(
                gt_payload(
                    run_id=self.run_id,
                    seed=self.seed,
                    config_hash=self.config_hash,
                    sim_time=sim_time,
                    node_id=node_id,
                    gt=gt,
                    ts=decayed,
                    cti_i=lag.cti_i,
                    rep=rep,
                    drift_flag=self._drift.get(node_id, 0.0),
                ),
                self.signing_key,
            ),
            sim_time=sim_time,
            run_id=self.run_id,
            seed=self.seed,
            config_hash=self.config_hash,
            node_id=node_id,
            gt=gt,
            ts=decayed,
            cti_i=lag.cti_i,
            cti_trust=cti_trust,
            rep=rep,
            master_score=master_score(
                ts=decayed, cti_i=lag.cti_i, gt=gt, weights=self.master_weights
            ),
            drift_flag=self._drift.get(node_id, 0.0),
            threat_confirmed=lag.cti_i > 0.0 and decayed < self.params.confirm_below_ts,
        )
        self._lag[node_id] = _NodeLag(ts=decayed, cti_i=lag.cti_i, rep=rep)
        self.bus.publish(GT_TOPIC, msg)
        return msg

    def current_ts(self, node_id: str) -> float | None:
        """The trust fusion will fuse from next tick, or `None` if never seen."""
        lag = self._lag.get(node_id)
        return None if lag is None else lag.ts

    def current_trust(self) -> dict[str, float]:
        """
        `current_ts` for every device at once: one read where a remote instance
        (`m6_trust_fusion.remote`) would otherwise answer one device at a time.
        """
        return {node_id: lag.ts for node_id, lag in self._lag.items()}

    def implicates_on_own_trust(self, node_id: str) -> bool:
        """Would the fail-safe implicate this device even if correlation omitted it?"""
        trust = self.current_ts(node_id)
        return trust is not None and trust < self.params.implicate_below_ts

    def apply_recalibration(self, node_id: str, next_ts: float) -> None:
        """Move this node's lagged trust toward M7's recalibration target."""
        lag = self._lag.get(node_id)
        if lag is None:
            return
        self._lag[node_id] = _NodeLag(ts=clamp01(next_ts), cti_i=lag.cti_i, rep=lag.rep)

    def observe_response(self, node_id: str, level: int) -> float:
        """Record one completed response as an interaction."""
        success = interaction_success(level) or self._held_only_by_reputation(node_id, level)
        return self.reputation.record(node_id, success=success)

    def _held_only_by_reputation(self, node_id: str, level: int) -> bool:
        """Is this L1 caused by nothing except past reputation?"""
        if level != 1:
            return False
        from m4_response_engine.levels import level_for_gt

        lag = self._lag.get(node_id)
        return (
            lag is not None
            and lag.cti_i == 0.0
            and self._drift.get(node_id, 0.0) == 0.0
            and level_for_gt(lag.ts) == 0
        )

    def observe_responses(self, plans: Iterable[ResponsePlan]) -> dict[str, float]:
        """Record a whole tick's plans, in a stable node order."""
        return {
            p.node_id: self.observe_response(p.node_id, p.proposed_level)
            for p in sorted(plans, key=lambda p: p.node_id)
        }

    def observe_trust(self, update: TrustUpdate) -> GlobalTrustUpdate:
        """
        Fuse one node's GT from lagged inputs, then refresh lag from this update + current
        correlation (becomes t−1 for the next call).
        """
        node_id = update.node_id
        lag = self._lag.get(node_id)
        cold_start = lag is None
        if lag is None:
            cti_now = self._cti_for(node_id, update.node_trust)
            lag = _NodeLag(
                ts=update.node_trust,
                cti_i=cti_now,
                rep=self.reputation.get(node_id),
            )

        rep = self.reputation.get(node_id)

        drift = self._drift.get(node_id, 0.0)
        gt, cti_trust = fuse_gt(
            ts=lag.ts,
            cti_i=lag.cti_i,
            rep=rep,
            params=self.params,
            drift_flag=drift,
        )
        ms = master_score(
            ts=lag.ts,
            cti_i=lag.cti_i,
            gt=gt,
            weights=self.master_weights,
        )
        threat_confirmed = lag.cti_i > 0.0 and lag.ts < self.params.confirm_below_ts

        msg = GlobalTrustUpdate(
            signature=sign(
                gt_payload(
                    run_id=self.run_id,
                    seed=self.seed,
                    config_hash=self.config_hash,
                    sim_time=update.sim_time,
                    node_id=node_id,
                    gt=gt,
                    ts=lag.ts,
                    cti_i=lag.cti_i,
                    rep=rep,
                    drift_flag=drift,
                ),
                self.signing_key,
            ),
            sim_time=update.sim_time,
            run_id=self.run_id,
            seed=self.seed,
            config_hash=self.config_hash,
            node_id=node_id,
            gt=gt,
            ts=lag.ts,
            cti_i=lag.cti_i,
            cti_trust=cti_trust,
            rep=rep,
            master_score=ms,
            drift_flag=drift,
            threat_confirmed=threat_confirmed,
        )
        self.bus.publish(GT_TOPIC, msg)

        self._last_seen[node_id] = update.sim_time
        self._decayed_at.pop(node_id, None)

        w_identity, w_behavioral, w_device, w_network = self.params.obs_weights
        observed = observation_from_context(
            update.context,
            w_identity=w_identity,
            w_behavioral=w_behavioral,
            w_device=w_device,
            w_network=w_network,
        )
        lam = self.params.trust_lambda
        if self.params.trust_lambda_up is not None and observed > lag.ts:
            lam = self.params.trust_lambda_up
        ceiling = lam * lag.ts + (1.0 - lam) * observed + 1e-9
        if cold_start or not self.params.step_check:
            accepted = update.node_trust
        else:
            accepted = min(update.node_trust, ceiling)
        if accepted < update.node_trust:
            self.trust_rise_capped += 1

        self._lag[node_id] = _NodeLag(
            ts=accepted,
            cti_i=self._cti_for(node_id, accepted),
            rep=self.reputation.get(node_id),
        )
        return msg

    def fuse_batch(
        self,
        updates: list[TrustUpdate],
        correlation: CorrelationResult | None = None,
    ) -> list[GlobalTrustUpdate]:
        if correlation is not None:
            self.observe_correlation(correlation)
        return [self.observe_trust(u) for u in updates]
