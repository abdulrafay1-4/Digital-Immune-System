"""M3 threat correlation: reliability-weighted CTI fusion."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from agents.orchestrator import TickBatch
from m1_monitoring.core.observation import observation_from_context
from shared.schemas import CorrelationResult, TrustUpdate

CORRELATION_TOPIC = "correlation.result"
ACTOR_ID = "correlation_agent"


class CorrelationParams(BaseModel):
    """Coefficients."""

    model_config = ConfigDict(extra="forbid")

    k: float = Field(default=2.0, ge=0.0)

    r_init: float = Field(default=0.9, ge=0.0, le=1.0)
    r_lambda: float = Field(default=0.8, ge=0.0, le=1.0)
    r_min: float = Field(default=0.05, ge=0.0, le=1.0)

    integrity_tolerance: float = Field(default=1e-9, ge=0.0)

    campaign_ti_threshold: float = Field(default=0.4, ge=0.0, le=1.0)
    campaign_min_nodes: int = Field(default=2, ge=2)
    cohort_margin: float | None = Field(default=None, ge=0.0, le=1.0)
    cohort_min_nodes: int = Field(default=3, ge=2)
    cohort_baseline_cap: float | None = Field(default=None, ge=0.0, le=1.0)

    w_identity: float = 0.25
    w_behavioral: float = 0.25
    w_device: float = 0.25
    w_network: float = 0.25

    def obs_weights(self) -> dict[str, float]:
        return {
            "w_identity": self.w_identity,
            "w_behavioral": self.w_behavioral,
            "w_device": self.w_device,
            "w_network": self.w_network,
        }


class ThreatIndicator(BaseModel):
    """One reporter's summarised intel for one node, for one tick."""

    model_config = ConfigDict(extra="forbid")

    node_id: str
    reporter_agent_id: str
    ti_score: float = Field(ge=0.0, le=1.0)
    integrity_ok: bool


def indicators_from(batch: TickBatch, params: CorrelationParams) -> list[ThreatIndicator]:
    """Derive threat indicators from a sealed batch."""
    weights = params.obs_weights()
    out: list[ThreatIndicator] = []
    for update in batch.updates:
        out.append(
            ThreatIndicator(
                node_id=update.node_id,
                reporter_agent_id=update.agent_id,
                ti_score=_clamp01(1.0 - update.node_trust),
                integrity_ok=_report_is_self_consistent(update, weights, params),
            )
        )
    return out


def _report_is_self_consistent(
    update: TrustUpdate, weights: dict[str, float], params: CorrelationParams
) -> bool:
    """Does the reported observation reproduce from the reported context?"""
    try:
        expected = observation_from_context(update.context, **weights)
    except ValueError:
        return False
    return abs(expected - update.observation) <= params.integrity_tolerance


class AgentReliabilityTracker:
    """Per-reporter reliability `R_a`, updated from report integrity."""

    def __init__(self, params: CorrelationParams | None = None) -> None:
        self.params = params or CorrelationParams()
        self._r: dict[str, float] = {}

    def get(self, agent_id: str) -> float:
        return self._r.get(agent_id, self.params.r_init)

    def observe(self, indicators: Iterable[ThreatIndicator]) -> None:
        """EWMA the integrity outcome into each reporter's reliability."""
        par = self.params
        for ind in indicators:
            current = self.get(ind.reporter_agent_id)
            signal = 1.0 if ind.integrity_ok else 0.0
            updated = par.r_lambda * current + (1.0 - par.r_lambda) * signal
            self._r[ind.reporter_agent_id] = _clamp(updated, par.r_min, 1.0)

    def observe_outcome(self, agent_id: str, confirmed: bool) -> None:
        """Consensus corroboration, deliberately not implemented."""
        raise NotImplementedError(
            "consensus corroboration is not implemented; "
            "reliability is driven by report integrity only"
        )

    def snapshot(self) -> dict[str, float]:
        return dict(self._r)


def _breadth_band(n: int) -> str:
    if n <= 1:
        return "single"
    if n <= 3:
        return "few"
    if n <= 10:
        return "several"
    return "many"


def _depth_band(mean: float) -> str:
    """How far one dimension has fallen, in five steps."""
    if mean >= 0.80:
        return "clear"
    if mean >= 0.60:
        return "slight"
    if mean >= 0.40:
        return "moderate"
    if mean >= 0.20:
        return "heavy"
    return "severe"


CORROBORATION_PER_PEER = 0.10
MAX_CORROBORATION = 0.30


def campaign_corroboration(n_implicated: int) -> float:
    """What being one of `n_implicated` devices is worth, beyond one's own state."""
    if n_implicated <= 1:
        return 0.0
    return min(MAX_CORROBORATION, CORROBORATION_PER_PEER * (n_implicated - 1))


def _severity_band(cti: float) -> str:
    return "low" if cti < 0.34 else "moderate" if cti < 0.67 else "high"


def campaign_pattern(
    batch: TickBatch,
    indicators: Sequence[ThreatIndicator],
    implicated: Sequence[str],
    cti: float,
) -> str:
    """Deterministic signature of a campaign's *shape*, for immune memory."""
    if not implicated:
        return ""

    targeted = set(implicated)
    parts: list[str] = []
    for dim in ("identity", "behavioral", "device", "network"):
        values = [getattr(u.context, dim) for u in batch.updates if u.node_id in targeted]
        mean = sum(values) / len(values) if values else 1.0
        parts.append(f"{dim}:{_depth_band(mean)}")

    return (
        f"{' '.join(parts)} breadth {_breadth_band(len(implicated))} severity {_severity_band(cti)}"
    )


@runtime_checkable
class Recall(Protocol):
    """Satisfied by `m5_immune_memory.MemoryQuery`."""

    def recognise(self, pattern_text: str) -> object: ...


class CorrelationAgent:
    """Fuses per-node indicators into one campaign-level CTI score."""

    def __init__(
        self,
        params: CorrelationParams | None = None,
        tracker: AgentReliabilityTracker | None = None,
    ) -> None:
        self.params = params or CorrelationParams()
        self.tracker = tracker or AgentReliabilityTracker(self.params)

    def correlate(
        self,
        batch: TickBatch,
        *,
        quarantined_agent_ids: Sequence[str] | None = None,
        recall: Recall | None = None,
    ) -> CorrelationResult:
        """Compute CTI for one tick."""
        if not batch.updates:
            raise ValueError("cannot correlate an empty batch")

        indicators = indicators_from(batch, self.params)
        quarantined = set(quarantined_agent_ids or ())

        weights = self._weights(indicators, quarantined)
        cti = sum(w * ind.ti_score for w, ind in zip(weights, indicators, strict=True))

        self.tracker.observe(indicators)

        implicated = self._implicated(indicators)
        campaign_id = self._campaign_id(batch, implicated)

        pattern = campaign_pattern(batch, indicators, implicated, cti)
        boost, recalled_id = self._recall(pattern, recall)

        return CorrelationResult(
            sim_time=batch.sim_time,
            run_id=batch.run_id,
            seed=batch.seed,
            config_hash=batch.config_hash,
            node_ids=sorted(ind.node_id for ind in indicators),
            cti=_clamp01(cti),
            implicated_node_ids=implicated,
            campaign_id=campaign_id,
            outlier_agent_ids=sorted(
                ind.reporter_agent_id for ind in indicators if not ind.integrity_ok
            ),
            node_ti={ind.node_id: ind.ti_score for ind in indicators},
            campaign_corroboration=campaign_corroboration(len(implicated)),
            pattern_text=pattern,
            recall_boost=boost,
            recalled_record_id=recalled_id,
        )

    def _implicated(self, indicators: Sequence[ThreatIndicator]) -> list[str]:
        """Absolute threshold, plus a cohort standing out from the fleet baseline."""
        par = self.params
        absolute = {i.node_id for i in indicators if i.ti_score >= par.campaign_ti_threshold}
        if par.cohort_margin is None or len(indicators) < 2 * par.cohort_min_nodes:
            return sorted(absolute)
        scores = sorted(i.ti_score for i in indicators)
        baseline = scores[(len(scores) - 1) // 2]
        if par.cohort_baseline_cap is not None:
            baseline = min(baseline, par.cohort_baseline_cap)
        cohort = {
            i.node_id for i in indicators if i.ti_score >= baseline + par.cohort_margin
        } - absolute
        if len(cohort) < par.cohort_min_nodes:
            return sorted(absolute)
        return sorted(absolute | cohort)

    @staticmethod
    def _recall(pattern: str, recall: Recall | None) -> tuple[float, str | None]:
        """Ask memory, tolerating its absence."""
        if recall is None or not pattern:
            return 0.0, None
        recognition = recall.recognise(pattern)
        if not getattr(recognition, "recognised", False):
            return 0.0, None
        best = getattr(recognition, "best", None)
        return float(recognition.cti_boost), getattr(best, "record_id", None)

    def _weights(self, indicators: Sequence[ThreatIndicator], quarantined: set[str]) -> list[float]:
        """w_i = R_i^k / sum(R_j^k), with quarantined reporters zeroed."""
        k = self.params.k
        raw = [
            0.0
            if ind.reporter_agent_id in quarantined
            else self.tracker.get(ind.reporter_agent_id) ** k
            for ind in indicators
        ]
        total = sum(raw)
        if total <= 0.0:
            return [1.0 / len(indicators)] * len(indicators)
        return [value / total for value in raw]

    def _campaign_id(self, batch: TickBatch, implicated: Sequence[str]) -> str | None:
        if len(implicated) < self.params.campaign_min_nodes:
            return None
        blob = f"{batch.run_id}\x00{batch.sim_time}\x00{','.join(implicated)}".encode()
        return f"campaign-{hashlib.sha256(blob).hexdigest()[:12]}"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _clamp01(value: float) -> float:
    return _clamp(value, 0.0, 1.0)
