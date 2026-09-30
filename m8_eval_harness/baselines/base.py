"""
Baselines: every arm the evaluation compares. Contribution ablations, the proposal's baselines,
reimplemented published methods, and a factorial arm.
"""

from __future__ import annotations

import functools
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import numpy as np

from agents.correlation import CorrelationAgent
from agents.pipeline import ClosedLoopPipeline
from m1_monitoring.core.observation import observation_from_context
from m4_response_engine.engine import ResponseEngine
from m4_response_engine.hysteresis import HysteresisParams, LevelHysteresis
from m4_response_engine.levels import ResponseLevel
from m6_trust_fusion import TrustFusionEngine
from m6_trust_fusion.fusion import GT_TOPIC, clamp01, gt_payload
from m6_trust_fusion.reputation import ReputationTracker
from m8_eval_harness.params import FROZEN, SystemParams
from shared.integrity import sign
from shared.schemas import GlobalTrustUpdate, TrustUpdate

DETECTOR_TRAINING_SEED = 9900


@dataclass(frozen=True)
class Baseline:
    baseline_id: str
    name: str
    isolates: str | None
    mechanism: str
    build: Callable[..., ClosedLoopPipeline]
    family: str = "contribution"

    def pipeline(self, **kwargs: object) -> ClosedLoopPipeline:
        return self.build(**kwargs)


class _BinaryResponseEngine(ResponseEngine):
    """Allow or block."""

    def decide(self, gt_update) -> ResponseLevel:  # type: ignore[override]
        graduated = super().decide(gt_update)
        return ResponseLevel.NONE if graduated is ResponseLevel.NONE else ResponseLevel.ISOLATE

    def effective_level(self, node_id: str) -> ResponseLevel:  # type: ignore[override]
        graduated = super().effective_level(node_id)
        return ResponseLevel.NONE if graduated is ResponseLevel.NONE else ResponseLevel.ISOLATE


def _fusion(
    bus: Any,
    run_id: str,
    seed: int,
    config_hash: str,
    params: SystemParams = FROZEN,
    cls: type[TrustFusionEngine] = TrustFusionEngine,
    fusion_overrides: dict[str, Any] | None = None,
    **fields: Any,
) -> TrustFusionEngine:
    return cls(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params.fusion_params(**(fusion_overrides or {})),
        reputation=ReputationTracker(params.reputation_params()),
        **fields,
    )


def _memory(
    run_id: str,
    quorum_k: int | None = None,
    params: SystemParams = FROZEN,
    correlator_cls: type[CorrelationAgent] = CorrelationAgent,
):
    """A live immune memory: the store, a read path, a write path and its attesters."""
    import hashlib

    from agents.attester import IndependentAttester
    from m5_immune_memory import HashingEmbedder, MemoryQuery, MemoryStore, WritePath
    from m10_persona_drift.nhi import issue_signing_identity
    from m11_memory_hardening import QuorumGate
    from m11_memory_hardening.quorum import DEFAULT_K, QuorumParams

    names = ("verifier", "correlation", "fusion", "orchestrator", "monitoring")
    attesters = {
        n: IndependentAttester(
            identity=issue_signing_identity(
                n, seed=hashlib.sha256(f"{run_id}:attester:{n}".encode()).digest()
            ),
            correlator=correlator_cls(params.correlation_params()),
        )
        for n in names
    }
    registry = {n: a.public() for n, a in attesters.items()}
    embedder = HashingEmbedder()
    store = MemoryStore(dim=embedder.dim)
    query = MemoryQuery(
        store=store, registry=registry, embedder=embedder, quorum_k=quorum_k or DEFAULT_K
    )
    writer = WritePath(
        store=store,
        gate=QuorumGate(registry=registry, params=QuorumParams(k=quorum_k or DEFAULT_K)),
        embedder=embedder,
    )
    return query, writer, attesters


def _healer():
    from m7_self_healing import SelfHealingEngine

    return SelfHealingEngine()


def _engine(params: SystemParams, cls: type[ResponseEngine] = ResponseEngine, n: int | None = None):
    hysteresis = HysteresisParams(n=n) if n is not None else params.hysteresis_params()
    return cls(require_signature=True, hysteresis=LevelHysteresis(params=hysteresis))


def _assemble(
    *,
    bus: Any,
    run_id: str,
    seed: int,
    config_hash: str,
    params: SystemParams,
    fusion: TrustFusionEngine | None = None,
    correlator: CorrelationAgent | None = None,
    engine: ResponseEngine | None = None,
    memory: bool = True,
    healing: bool = True,
    approval: Any | None = None,
    classifier: Any | None = None,
    recall: Any | None = None,
    healer: Any | None = None,
    brake: bool = True,
    quorum_k: int | None = None,
) -> ClosedLoopPipeline:
    from agents.verifier import VerifierAgent

    chosen = correlator if correlator is not None else CorrelationAgent(params.correlation_params())
    kw: dict[str, Any] = {
        "fusion": fusion if fusion is not None else _fusion(bus, run_id, seed, config_hash, params),
        "correlator": chosen,
        "verifier": VerifierAgent(correlator=CorrelationAgent(params.correlation_params())),
        "bound_correlator": type(chosen)(params.correlation_params()),
        "engine": engine if engine is not None else _engine(params),
        "approval": approval,
        **params.pipeline_policy(),
    }
    if not brake:
        kw["max_auto_restrict_fraction"] = None
    if type(kw["fusion"]) is TrustFusionEngine:
        kw["engine"].fusion_params = kw["fusion"].params
    if classifier is not None:
        kw["classifier"] = classifier
    if memory:
        query, writer, attesters = _memory(run_id, quorum_k, params, type(chosen))
        kw.update(
            recall=recall if recall is not None else query, curator=writer, attesters=attesters
        )
    if healing:
        kw["healer"] = healer if healer is not None else _healer()
    return ClosedLoopPipeline(**kw)


def _observation(update: TrustUpdate, fusion: TrustFusionEngine) -> float:
    w_identity, w_behavioral, w_device, w_network = fusion.params.obs_weights
    return observation_from_context(
        update.context,
        w_identity=w_identity,
        w_behavioral=w_behavioral,
        w_device=w_device,
        w_network=w_network,
    )


def _signed_gt(fusion: TrustFusionEngine, node_id: str, sim_time: float, *, gt: float, ts: float):
    """A signed GT for an arm that decides without trust fusion."""
    gt, ts = clamp01(gt), clamp01(ts)
    rep = fusion.reputation.get(node_id)
    payload = gt_payload(
        run_id=fusion.run_id,
        seed=fusion.seed,
        config_hash=fusion.config_hash,
        sim_time=sim_time,
        node_id=node_id,
        gt=gt,
        ts=ts,
        cti_i=0.0,
        rep=rep,
        drift_flag=0.0,
    )
    message = GlobalTrustUpdate(
        signature=sign(payload, fusion.signing_key),
        sim_time=sim_time,
        run_id=fusion.run_id,
        seed=fusion.seed,
        config_hash=fusion.config_hash,
        node_id=node_id,
        gt=gt,
        ts=ts,
        cti_i=0.0,
        cti_trust=1.0,
        rep=rep,
        master_score=gt,
        drift_flag=0.0,
        threat_confirmed=gt < 0.5,
    )
    fusion.bus.publish(GT_TOPIC, message)
    return message


class _StaticTrustFusion(TrustFusionEngine):
    """Fusion that never lets accumulated trust move."""

    def observe_trust(self, update):  # type: ignore[override]
        frozen = update.model_copy(
            update={
                "node_trust": 1.0,
                "observation": 1.0,
                "context": update.context.model_copy(
                    update={"identity": 1.0, "behavioral": 1.0, "device": 1.0, "network": 1.0}
                ),
            }
        )
        return super().observe_trust(frozen)


class _IsolatedCorrelation(CorrelationAgent):
    """Every device judged alone."""

    def correlate(self, batch, **kwargs):  # type: ignore[override]
        result = super().correlate(batch, **kwargs)
        return result.model_copy(
            update={
                "cti": 0.0,
                "implicated_node_ids": [],
                "campaign_corroboration": 0.0,
                "campaign_id": None,
                "recall_boost": 0.0,
                "recalled_record_id": None,
            }
        )


@dataclass
class _PolicyFusion(TrustFusionEngine):
    """Binary Zero Trust: a policy decision on each report, with nothing carried over."""

    policy_threshold: float = 0.5

    def observe_trust(self, update):  # type: ignore[override]
        observed = _observation(update, self)
        gt = 1.0 if observed >= self.policy_threshold else 0.0
        return _signed_gt(self, update.node_id, update.sim_time, gt=gt, ts=observed)

    def observe_silence(self, node_id, *, sim_time, beta=0.01):  # type: ignore[override]
        return None


@dataclass
class _BetaTrustFusion(TrustFusionEngine):
    """The Beta Reputation System in place of M1's EWMA trust."""

    forgetting: float = 0.9
    _evidence: dict[str, tuple[float, float]] = field(default_factory=dict, repr=False)

    def observe_trust(self, update):  # type: ignore[override]
        observed = _observation(update, self)
        positive, negative = self._evidence.get(update.node_id, (0.0, 0.0))
        positive = self.forgetting * positive + observed
        negative = self.forgetting * negative + (1.0 - observed)
        self._evidence[update.node_id] = (positive, negative)
        expectation = (positive + 1.0) / (positive + negative + 2.0)
        return super().observe_trust(update.model_copy(update={"node_trust": clamp01(expectation)}))


@dataclass
class _AnomalyDetectorFusion(TrustFusionEngine):
    """An unsupervised per-device detector as the decision signal."""

    detector: Any = None

    def fuse_batch(self, updates, correlation=None):  # type: ignore[override]
        if correlation is not None:
            self.observe_correlation(correlation)
        if not updates:
            return []
        matrix = np.asarray(
            [
                [u.context.identity, u.context.behavioral, u.context.device, u.context.network]
                for u in updates
            ]
        )
        outlier = self.detector.predict(matrix) == -1
        return [
            _signed_gt(
                self, u.node_id, u.sim_time, gt=0.0 if flag else 1.0, ts=_observation(u, self)
            )
            for u, flag in zip(updates, outlier, strict=True)
        ]

    def observe_silence(self, node_id, *, sim_time, beta=0.01):  # type: ignore[override]
        return None


@functools.lru_cache(maxsize=4)
def _trained_detector(contamination: float):
    from sklearn.ensemble import IsolationForest

    from m1_monitoring.sensors.synthetic import SyntheticTelemetry

    sensor = SyntheticTelemetry(DETECTOR_TRAINING_SEED)
    rows = []
    for i in range(200):
        for t in range(25):
            context, _ = sensor.read(float(t), f"node-{i}")
            rows.append([context.identity, context.behavioral, context.device, context.network])
    return IsolationForest(n_estimators=200, contamination=contamination, random_state=0).fit(
        np.asarray(rows)
    )


@functools.lru_cache(maxsize=2)
def _shared_llm(model: str):
    """One prompt cache per model per process, shared across runs."""
    from agents.llm_cache import CachedLLM, OllamaClient

    return CachedLLM(OllamaClient(model=model))


def _full(
    *,
    bus,
    run_id,
    seed,
    config_hash,
    params=FROZEN,
    approval=None,
    recall=None,
    healer=None,
    classifier=None,
    engine=None,
    **_,
):
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        approval=approval,
        recall=recall,
        healer=healer,
        classifier=classifier,
        engine=engine,
    )


def _replicated_fusion(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    """The full system with trust fusion run three times, the majority update acting."""
    from m6_trust_fusion.replicated import ReplicatedFusion

    fusion = ReplicatedFusion(
        [_fusion(bus, run_id, seed, config_hash, params) for _ in range(3)], bus=bus
    )
    pipeline = _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        fusion=fusion,  # type: ignore[arg-type]
        approval=approval,
    )
    pipeline.engine.fusion_params = fusion.params
    return pipeline


def _static_trust(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        approval=approval,
        fusion=_fusion(bus, run_id, seed, config_hash, params, cls=_StaticTrustFusion),
    )


def _no_sharing(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        approval=approval,
        correlator=_IsolatedCorrelation(params.correlation_params()),
    )


def _no_memory(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        approval=approval,
        memory=False,
    )


def _binary_response(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        approval=approval,
        engine=_engine(params, _BinaryResponseEngine),
    )


def _no_recovery(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        approval=approval,
        healing=False,
    )


def _static_no_sharing(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        approval=approval,
        fusion=_fusion(bus, run_id, seed, config_hash, params, cls=_StaticTrustFusion),
        correlator=_IsolatedCorrelation(params.correlation_params()),
    )


def _mediated(transport: str):
    """The full system with immune memory behind the mediated-access broker."""

    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        from agents.context_broker import InProcBroker

        pipeline = _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
        )
        broker = InProcBroker(
            query=pipeline.recall,
            write_path=pipeline.curator,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
        )
        if transport == "mcp":
            from agents.mcp_broker import McpBroker

            pipeline.broker = McpBroker(inner=broker)
        else:
            pipeline.broker = broker
        return pipeline

    return build


def _trust_only(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    """Staged baseline B: continuous trust alone drives the response."""
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        approval=approval,
        correlator=_IsolatedCorrelation(params.correlation_params()),
        memory=False,
        healing=False,
    )


def _trust_ti(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    """Staged baseline C: continuous trust plus shared threat intelligence."""
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        approval=approval,
        memory=False,
        healing=False,
    )


def _equal_weighting(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    """Security-plane ablation C: every reporter counts the same."""
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=replace(params, cti_k=0.0),
        approval=approval,
    )


def _no_quorum(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    """Security-plane ablation F: one attester admits a memory write."""
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=params,
        approval=approval,
        quorum_k=1,
    )


def _no_weighting_no_quorum(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
    """Security-plane ablation G: the security plane's two collective defences, both off."""
    return _assemble(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=config_hash,
        params=replace(params, cti_k=0.0),
        approval=approval,
        quorum_k=1,
    )


def binary_zero_trust(threshold: float = 0.5, *, brake: bool = False) -> Baseline:
    """The proposal's Binary Zero Trust, at a policy threshold."""

    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        return _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            fusion=_fusion(
                bus,
                run_id,
                seed,
                config_hash,
                params,
                cls=_PolicyFusion,
                policy_threshold=threshold,
            ),
            correlator=_IsolatedCorrelation(params.correlation_params()),
            engine=_engine(params, _BinaryResponseEngine, n=1),
            memory=False,
            healing=False,
            brake=brake,
        )

    suffix = "" if threshold == 0.5 else f"@{threshold:g}"
    suffix += "+brake" if brake else ""
    return Baseline(
        baseline_id=f"binary_zt{suffix}",
        name=f"Binary Zero Trust (policy threshold {threshold:g})"
        + (" with our restriction brake" if brake else ""),
        isolates=None,
        mechanism="per-report policy check on the current observation; allow or block; "
        "no trust history, fleet view, memory, graduation or recovery",
        build=build,
        family="fyp",
    )


def beta_reputation(forgetting: float = 0.9) -> Baseline:
    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        return _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            fusion=_fusion(
                bus,
                run_id,
                seed,
                config_hash,
                params,
                cls=_BetaTrustFusion,
                fusion_overrides={"step_check": False},
                forgetting=forgetting,
            ),
        )

    suffix = "" if forgetting == 0.9 else f"@{forgetting:g}"
    return Baseline(
        baseline_id=f"beta_reputation{suffix}",
        name=f"Beta Reputation System trust (forgetting {forgetting:g})",
        isolates=None,
        mechanism="Josang & Ismail (2002) beta expectation replaces M1's EWMA; rest unchanged",
        build=build,
        family="external",
    )


def isolation_forest(contamination: float = 0.01) -> Baseline:
    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        return _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            fusion=_fusion(
                bus,
                run_id,
                seed,
                config_hash,
                params,
                cls=_AnomalyDetectorFusion,
                detector=_trained_detector(contamination),
            ),
            correlator=_IsolatedCorrelation(params.correlation_params()),
            engine=_engine(params, _BinaryResponseEngine, n=1),
            memory=False,
            healing=False,
            brake=False,
        )

    suffix = "" if contamination == 0.01 else f"@{contamination:g}"
    return Baseline(
        baseline_id=f"isolation_forest{suffix}",
        name=f"Isolation Forest per-device detector (contamination {contamination:g})",
        isolates=None,
        mechanism="Liu, Ting & Zhou (2008) on healthy calibration telemetry; block outliers",
        build=build,
        family="external",
    )


_STOP_LEVELS: tuple[ResponseLevel, ...] = (
    ResponseLevel.NONE,
    ResponseLevel.REAUTH,
    ResponseLevel.RESTRICT,
    ResponseLevel.ISOLATE,
)

STOPPING_POLICY_PATH = Path(__file__).resolve().parents[2] / "configs" / "stopping_response.json"


_PRIOR = 1e-6


def _logit(p: float) -> float:
    import math

    p = min(max(p, 1e-300), 1.0 - 1e-16)
    return math.log(p) - math.log1p(-p)


def _expit(x: float) -> float:
    import math

    return 1.0 / (1.0 + math.exp(-x)) if x >= 0 else math.exp(x) / (1.0 + math.exp(x))


@dataclass(frozen=True)
class StoppingPolicy:
    """A fitted multiple-stopping policy: observation likelihoods and thresholds."""

    thresholds: tuple[float, ...]
    f_healthy: tuple[float, ...]
    f_intruded: tuple[float, ...]
    intrusion_rate: float
    release: bool = False

    def __post_init__(self) -> None:
        if len(self.f_healthy) != len(self.f_intruded):
            raise ValueError("the two likelihoods must use the same bins")
        if sorted(self.thresholds, reverse=True) != list(self.thresholds):
            raise ValueError(f"thresholds must be nested, got {self.thresholds}")

    @classmethod
    def load(cls, path: Path | None = None, *, release: bool = False) -> StoppingPolicy:
        import json

        path = path or (
            STOPPING_POLICY_PATH.with_name("stopping_response_release.json")
            if release
            else STOPPING_POLICY_PATH
        )
        if not path.exists():
            raise FileNotFoundError(
                f"{path} is missing: fit it first with `python -m m8_eval_harness.stopping_fit`"
            )
        raw = json.loads(path.read_text())
        return cls(
            thresholds=tuple(raw["thresholds"]),
            f_healthy=tuple(raw["f_healthy"]),
            f_intruded=tuple(raw["f_intruded"]),
            intrusion_rate=float(raw["intrusion_rate"]),
            release=release,
        )

    def likelihood(self, observation: float) -> tuple[float, float]:
        """(P(o | intruded), P(o | healthy)) for one observation."""
        bins = len(self.f_healthy)
        index = min(bins - 1, max(0, int(clamp01(observation) * bins)))
        return self.f_intruded[index], self.f_healthy[index]

    def update_logit(self, logit: float, observation: float) -> float:
        """One step of the belief recursion, in log-odds."""
        import math

        rate = self.intrusion_rate
        b, not_b = _expit(logit), _expit(-logit)
        predicted = math.log(b + not_b * rate) - (math.log(not_b) + math.log1p(-rate))
        f_intruded, f_healthy = self.likelihood(observation)
        return predicted + math.log(max(f_intruded, 1e-300)) - math.log(max(f_healthy, 1e-300))

    def update(self, belief: float, observation: float) -> float:
        """The same recursion in probability space, for inspection and tests."""
        return _expit(self.update_logit(_logit(belief), observation))

    def stops_after(self, belief: float, stops_used: int) -> int:
        """Stops used after this tick, one step per tick, given a probability."""
        return self.stops_after_logit(_logit(belief), stops_used)

    def stops_after_logit(self, logit: float, stops_used: int) -> int:
        """Stops used after this tick, one step per tick."""
        remaining = len(self.thresholds) - stops_used
        if remaining > 0 and logit >= _logit(self.thresholds[remaining - 1]):
            return stops_used + 1
        if self.release and stops_used > 0 and logit < _logit(self.thresholds[remaining]):
            return stops_used - 1
        return stops_used


class _StoppingResponseEngine(ResponseEngine):
    """Their stopping rule in place of ours, on the same evidence (C4 only)."""

    def __init__(self, *args: Any, policy: StoppingPolicy, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.policy = policy
        self._logit: dict[str, float] = {}
        self._stops: dict[str, int] = {}

    def decide(self, gt_update) -> ResponseLevel:  # type: ignore[override]
        if self.require_signature and not self.gt_is_authentic(gt_update):
            raise ValueError(f"unsigned or altered GlobalTrustUpdate for {gt_update.node_id}")
        node = gt_update.node_id
        logit = self.policy.update_logit(self._logit.get(node, _logit(_PRIOR)), gt_update.ts)
        self._logit[node] = logit
        self._stops[node] = self.policy.stops_after_logit(logit, self._stops.get(node, 0))
        self._last_gt[node] = gt_update
        return _STOP_LEVELS[self._stops[node]]

    def effective_level(self, node_id: str) -> ResponseLevel:  # type: ignore[override]
        return _STOP_LEVELS[self._stops.get(node_id, 0)]


def stopping_response(policy: StoppingPolicy | None = None, *, release: bool = False) -> Baseline:
    """C4 comparator: their response rule, our evidence."""

    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        fitted = policy or StoppingPolicy.load(release=release)
        return _full(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            engine=_StoppingResponseEngine(
                require_signature=True,
                hysteresis=LevelHysteresis(params=params.hysteresis_params()),
                policy=fitted,
            ),
        )

    released = "_release" if release else ""
    return Baseline(
        baseline_id=f"stopping_response{released}",
        name="Graduated response replaced by optimal multiple stopping"
        + (", levels released when the belief falls" if release else ""),
        isolates="C4 graduated response",
        mechanism=(
            "Hammar & Stadler (2022) multi-threshold stopping on fused trust, in place of "
            "the level rule and hysteresis"
            + ("; our release extension" if release else "; stops irreversible, as published")
        ),
        build=build,
        family="external",
    )


def full_with_llm(model: str = "llama3.2:3b") -> Baseline:
    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        from agents.classifier import LLMClassifier
        from agents.dual_classifier import DualClassifier

        classifier = DualClassifier(primary=LLMClassifier(_shared_llm(model)))
        return _full(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            classifier=classifier,
        )

    return Baseline(
        baseline_id="full_llm",
        name=f"Full system, LLM classifier ({model})",
        isolates=None,
        mechanism="the full system with the local model as the classifier's primary",
        build=build,
        family="fyp",
    )


FULL = Baseline(
    "full", "Full system", None, "every contribution enabled; rules classifier primary", _full
)
FULL_REPLICATED_FUSION = Baseline(
    "full_replicated_fusion",
    "Full system, fusion replicated",
    None,
    "trust fusion run three times with its own state each; the median GT acts",
    _replicated_fusion,
)
STATIC_TRUST = Baseline(
    "static_trust",
    "Static trust",
    "C1 continuous trust",
    "trust pinned at its initial value; weights untouched",
    _static_trust,
)
NO_SHARING = Baseline(
    "no_sharing",
    "No sharing",
    "C2 collaborative threat intelligence",
    "no fleet view: every device judged on its own evidence",
    _no_sharing,
)
NO_MEMORY = Baseline(
    "no_memory",
    "No memory",
    "C3 immune memory",
    "recall disabled: every recurrence is a first encounter",
    _no_memory,
)
BINARY_RESPONSE = Baseline(
    "binary_response",
    "Binary response",
    "C4 graduated response",
    "allow or isolate, with no level between",
    _binary_response,
)
NO_RECOVERY = Baseline(
    "no_recovery",
    "No recovery",
    "C5 self-healing",
    "healing disabled: trust is never earned back",
    _no_recovery,
)
STATIC_NO_SHARING = Baseline(
    "static_no_sharing",
    "Static trust and no sharing",
    None,
    "the C1 x C2 factorial cell: neither contribution",
    _static_no_sharing,
    family="factorial",
)

MEDIATED = Baseline(
    "full_mediated",
    "Full system, mediated memory",
    None,
    "immune memory behind the in-process broker: authenticate, ceiling, M9, filter, audit",
    _mediated("inproc"),
    family="mediated",
)
MEDIATED_MCP = Baseline(
    "full_mcp",
    "Full system, memory over MCP",
    None,
    "the same policy with the Model Context Protocol as the transport",
    _mediated("mcp"),
    family="mediated",
)
TRUST_ONLY = Baseline(
    "trust_only",
    "Continuous trust only",
    None,
    "research baseline B: trust drives the response; no sharing, memory or healing",
    _trust_only,
    family="research",
)
TRUST_TI = Baseline(
    "trust_ti",
    "Trust and threat intelligence",
    None,
    "research baseline C: trust plus the fleet view; no memory or healing",
    _trust_ti,
    family="research",
)
EQUAL_WEIGHTING = Baseline(
    "equal_weighting",
    "Equal weighting",
    "reliability-weighted fusion (research ablation C)",
    "k = 0: every reporter's intel counts the same, however unreliable",
    _equal_weighting,
    family="ablation",
)
NO_QUORUM = Baseline(
    "no_quorum",
    "No quorum",
    "quorum-gated memory (research ablation F)",
    "k = 1: a single attester admits a memory write",
    _no_quorum,
    family="ablation",
)
NO_WEIGHTING_NO_QUORUM = Baseline(
    "no_weighting_no_quorum",
    "No weighting, no quorum",
    "the security plane's collective defences (research ablation G)",
    "equal weighting and single-attester writes together",
    _no_weighting_no_quorum,
    family="ablation",
)

BINARY_ZT = binary_zero_trust()
BETA_REPUTATION = beta_reputation()
ISOLATION_FOREST = isolation_forest()
FULL_LLM = full_with_llm()
STOPPING_RESPONSE = stopping_response()
STOPPING_RESPONSE_RELEASE = stopping_response(release=True)
MEMORYLESS = NO_MEMORY
RULES_ONLY = FULL

BASELINES: tuple[Baseline, ...] = (
    FULL,
    STATIC_TRUST,
    NO_SHARING,
    NO_MEMORY,
    BINARY_RESPONSE,
    NO_RECOVERY,
)


@dataclass
class _CusumTrustFusion(TrustFusionEngine):
    """Page's CUSUM (Biometrika 1954) in place of M1's EWMA trust (a C1 comparator)."""

    cusum_k: float = 0.05
    cusum_h: float = 0.4
    cusum_mu0: float = 0.92
    _s: dict[str, float] = field(default_factory=dict, repr=False)

    def observe_trust(self, update):  # type: ignore[override]
        observed = _observation(update, self)
        s = max(0.0, self._s.get(update.node_id, 0.0) + (self.cusum_mu0 - observed) - self.cusum_k)
        self._s[update.node_id] = s
        trust = clamp01(1.0 - s / self.cusum_h)
        return super().observe_trust(update.model_copy(update={"node_trust": trust}))


def cusum(k: float = 0.05, h: float = 0.4) -> Baseline:
    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        return _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            fusion=_fusion(
                bus,
                run_id,
                seed,
                config_hash,
                params,
                cls=_CusumTrustFusion,
                fusion_overrides={"step_check": False},
                cusum_k=k,
                cusum_h=h,
            ),
        )

    return Baseline(
        baseline_id=f"cusum@{k:g}:{h:g}",
        name=f"DIS with CUSUM trust (k {k:g}, h {h:g})",
        isolates=None,
        mechanism="Page (1954) one-sided CUSUM replaces M1's EWMA; rest unchanged",
        build=build,
        family="external",
    )


@functools.lru_cache(maxsize=1)
def _healthy_observation_mean() -> float:
    """Page's in-control mean, measured on the healthy training fleet (seed 9900)."""
    from m1_monitoring.sensors.synthetic import SyntheticTelemetry

    w_identity, w_behavioral, w_device, w_network = FROZEN.obs_weights
    sensor = SyntheticTelemetry(DETECTOR_TRAINING_SEED)
    return float(
        np.mean(
            [
                observation_from_context(
                    sensor.read(float(t), f"node-{i}")[0],
                    w_identity=w_identity,
                    w_behavioral=w_behavioral,
                    w_device=w_device,
                    w_network=w_network,
                )
                for i in range(200)
                for t in range(25)
            ]
        )
    )


@dataclass
class _PageCusumFusion(TrustFusionEngine):
    """Page's CUSUM (Biometrika 1954) on its own, as the whole decision."""

    cusum_k: float = 0.05
    cusum_h: float = 0.4
    cusum_mu0: float = 0.0
    _s: dict[str, float] = field(default_factory=dict, repr=False)

    def observe_trust(self, update):  # type: ignore[override]
        x = _observation(update, self)
        s = max(0.0, self._s.get(update.node_id, 0.0) + (self.cusum_mu0 - self.cusum_k) - x)
        action = s >= self.cusum_h
        self._s[update.node_id] = 0.0 if action else s
        return _signed_gt(self, update.node_id, update.sim_time, gt=0.0 if action else 1.0, ts=x)

    def observe_silence(self, node_id, *, sim_time, beta=0.01):  # type: ignore[override]
        return None


def page_cusum(k: float = 0.05, h: float = 0.4) -> Baseline:
    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        return _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            fusion=_fusion(
                bus,
                run_id,
                seed,
                config_hash,
                params,
                cls=_PageCusumFusion,
                cusum_k=k,
                cusum_h=h,
                cusum_mu0=_healthy_observation_mean(),
            ),
            correlator=_IsolatedCorrelation(params.correlation_params()),
            engine=_engine(params, _BinaryResponseEngine, n=1),
            memory=False,
            healing=False,
            brake=False,
        )

    return Baseline(
        baseline_id=f"page_cusum@{k:g}:{h:g}",
        name=f"Page's CUSUM on its own (k {k:g}, h {h:g})",
        isolates=None,
        mechanism="Page (1954) one-sided CUSUM on each report; block at S >= h, restart at "
        "zero; nothing else of the DIS",
        build=build,
        family="external",
    )


class _DirichletReliabilityTracker:
    """Jøsang and Haller's Dirichlet reputation (ARES 2007) for reporter reliability."""

    LEVELS = 5
    BOUNDS = (0.02, 0.05, 0.1, 0.2)

    def __init__(self, lam: float = 0.9, c: float = 2.0) -> None:
        self.lam, self.c = lam, c
        self._r: dict[str, list[float]] = {}

    def _level(self, deviation: float) -> int:
        for index, bound in enumerate(self.BOUNDS):
            if deviation <= bound:
                return self.LEVELS - 1 - index
        return 0

    def observe(self, indicators) -> None:  # type: ignore[no-untyped-def]
        """The correlator's per-tick hook."""

    def observe_deviation(self, agent_id: str, deviation: float) -> None:
        evidence = [self.lam * r for r in self._r.get(agent_id, [0.0] * self.LEVELS)]
        evidence[self._level(deviation)] += 1.0
        self._r[agent_id] = evidence

    def get(self, agent_id: str) -> float:
        evidence = self._r.get(agent_id, [0.0] * self.LEVELS)
        total = self.c + sum(evidence)
        base = 1.0 / self.LEVELS
        return sum(
            (i / (self.LEVELS - 1)) * (r + self.c * base) / total for i, r in enumerate(evidence)
        )

    def snapshot(self) -> dict[str, float]:
        return {a: self.get(a) for a in self._r}


class _DirichletCorrelation(CorrelationAgent):
    """Reporter weights from the Dirichlet score instead of `R^k` (C2 only)."""

    def __init__(self, params=None, lam: float = 0.9) -> None:  # type: ignore[no-untyped-def]
        super().__init__(params)
        self.params = self.params.model_copy(update={"k": 1.0})
        self.lam = lam
        self.tracker = _DirichletReliabilityTracker(lam=lam)  # type: ignore[assignment]

    def correlate(self, batch, **kwargs):  # type: ignore[override]
        weights = (
            self.params.w_identity,
            self.params.w_behavioral,
            self.params.w_device,
            self.params.w_network,
        )
        for u in batch.updates:
            recomputed = observation_from_context(
                u.context,
                w_identity=weights[0],
                w_behavioral=weights[1],
                w_device=weights[2],
                w_network=weights[3],
            )
            self.tracker.observe_deviation(u.agent_id, abs(u.observation - recomputed))
        return super().correlate(batch, **kwargs)


def dirichlet_reliability(lam: float = 0.9) -> Baseline:
    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        return _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            correlator=_DirichletCorrelation(params.correlation_params(), lam=lam),
        )

    suffix = "" if lam == 0.9 else f"@{lam:g}"
    return Baseline(
        baseline_id=f"dirichlet_reliability{suffix}",
        name=f"Dirichlet reporter reliability (longevity {lam:g})",
        isolates=None,
        mechanism="Josang & Haller (2007) Dirichlet reputation weights reporters; rest unchanged",
        build=build,
        family="external",
    )


@dataclass
class _PenaltyHealer:
    """Isolate, then restore after a fixed penalty (Fotohi et al."""

    penalty_ticks: int = 10
    tau_h: float = 0.5
    floor: float = 0.05
    _held: dict[str, int] = field(default_factory=dict, repr=False)

    def observe(self, node_id, *, gt, health, sim_time, approval_granted=False):  # type: ignore[no-untyped-def]
        remaining = self._held.get(node_id)
        if remaining is not None:
            if remaining <= 1:
                del self._held[node_id]
            else:
                self._held[node_id] = remaining - 1
        elif gt < self.tau_h:
            self._held[node_id] = self.penalty_ticks
        return None

    def target_for(self, node_id: str) -> float | None:
        return self.floor if node_id in self._held else None

    def next_ts(self, node_id: str, current_ts: float) -> float:
        return self.floor if node_id in self._held else current_ts

    def state(self, node_id: str):  # type: ignore[no-untyped-def]
        from m7_self_healing import NodeHealingState

        return NodeHealingState()


def penalty_healing(penalty_ticks: float = 10) -> Baseline:
    from m7_self_healing.engine import HealingParams

    ticks = int(penalty_ticks)

    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        return _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            healer=_PenaltyHealer(penalty_ticks=ticks, tau_h=HealingParams().tau_h),
        )

    return Baseline(
        baseline_id=f"penalty_healing@{ticks}",
        name=f"Isolate-then-restore after a {ticks}-tick penalty",
        isolates=None,
        mechanism="Fotohi et al. (2020) fixed-penalty restore replaces M7's ramp; rest unchanged",
        build=build,
        family="external",
    )


@dataclass
class _DdcaFusion(TrustFusionEngine):
    """The deterministic Dendritic Cell Algorithm (Greensmith & Aickelin 2008)."""

    theta: float = 0.8
    migration: float = 2.0
    cells: int = 10
    window: int = 10
    _csm: dict[str, list[float]] = field(default_factory=dict, repr=False)
    _k: dict[str, list[float]] = field(default_factory=dict, repr=False)
    _presented: dict[str, deque] = field(default_factory=dict, repr=False)

    def fuse_batch(self, updates, correlation=None):  # type: ignore[override]
        if correlation is not None:
            self.observe_correlation(correlation)
        out = []
        for u in updates:
            o = _observation(u, self)
            danger = max(0.0, (self.theta - o) / self.theta)
            safe = max(0.0, (o - self.theta) / (1.0 - self.theta))
            csm = self._csm.setdefault(u.node_id, [0.0] * self.cells)
            k = self._k.setdefault(u.node_id, [0.0] * self.cells)
            shown = self._presented.setdefault(u.node_id, deque(maxlen=self.window))
            for i in range(self.cells):
                csm[i] += safe + danger
                k[i] += danger - 2.0 * safe
                if csm[i] >= self.migration * (i + 1) / self.cells:
                    shown.append(k[i])
                    csm[i], k[i] = 0.0, 0.0
            anomalous = bool(shown) and sum(shown) / len(shown) > 0.0
            out.append(_signed_gt(self, u.node_id, u.sim_time, gt=0.0 if anomalous else 1.0, ts=o))
        return out

    def observe_silence(self, node_id, *, sim_time, beta=0.01):  # type: ignore[override]
        return None


def ddca(theta: float = 0.8, migration: float = 2.0) -> Baseline:
    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        return _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            fusion=_fusion(
                bus,
                run_id,
                seed,
                config_hash,
                params,
                cls=_DdcaFusion,
                theta=theta,
                migration=migration,
            ),
            correlator=_IsolatedCorrelation(params.correlation_params()),
            engine=_engine(params, _BinaryResponseEngine, n=1),
            memory=False,
            healing=False,
            brake=False,
        )

    return Baseline(
        baseline_id=f"ddca@{theta:g}:{migration:g}",
        name=f"Deterministic DCA (theta {theta:g}, migration {migration:g})",
        isolates=None,
        mechanism="Greensmith & Aickelin (2008) dDCA per device as the decision signal",
        build=build,
        family="external",
    )


@dataclass
class _PersistentAnomalyFusion(_AnomalyDetectorFusion):
    """The Isolation Forest arm with persistence: act on k flags in the last m ticks."""

    persist_k: int = 3
    persist_m: int = 5
    _flags: dict[str, deque] = field(default_factory=dict, repr=False)

    def fuse_batch(self, updates, correlation=None):  # type: ignore[override]
        raw = super().fuse_batch(updates, correlation)
        out = []
        for u, gt_update in zip(updates, raw, strict=True):
            flags = self._flags.setdefault(u.node_id, deque(maxlen=self.persist_m))
            flags.append(gt_update.gt == 0.0)
            persistent = sum(flags) >= self.persist_k
            out.append(
                _signed_gt(
                    self, u.node_id, u.sim_time, gt=0.0 if persistent else 1.0, ts=gt_update.ts
                )
            )
        return out


def isolation_forest_persistent(contamination: float = 0.01) -> Baseline:
    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        return _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            fusion=_fusion(
                bus,
                run_id,
                seed,
                config_hash,
                params,
                cls=_PersistentAnomalyFusion,
                detector=_trained_detector(contamination),
            ),
            correlator=_IsolatedCorrelation(params.correlation_params()),
            engine=_engine(params, _BinaryResponseEngine, n=1),
            memory=False,
            healing=False,
            brake=False,
        )

    return Baseline(
        baseline_id=f"isolation_forest_persistent@{contamination:g}",
        name=f"Isolation Forest, 3-of-5 persistence (contamination {contamination:g})",
        isolates=None,
        mechanism="Isolation Forest per device, acting on 3 flags in 5 ticks",
        build=build,
        family="external",
    )


EXTERNAL_BASELINES: tuple[Baseline, ...] = (
    BINARY_ZT,
    BETA_REPUTATION,
    ISOLATION_FOREST,
    STOPPING_RESPONSE,
    STOPPING_RESPONSE_RELEASE,
)
ABLATION_BASELINES: tuple[Baseline, ...] = (EQUAL_WEIGHTING, NO_QUORUM, NO_WEIGHTING_NO_QUORUM)
RESEARCH_BASELINES: tuple[Baseline, ...] = (TRUST_ONLY, TRUST_TI)
MEDIATED_BASELINES: tuple[Baseline, ...] = (MEDIATED, MEDIATED_MCP)


def _tolerance_arm(
    baseline_id: str, name: str, mechanism: str, fields: Callable[[], dict[str, Any]]
) -> Baseline:
    """TOLERANCE's node controller, or one of its paper's baselines, as the whole decision."""
    from m8_eval_harness.baselines.tolerance import _ToleranceFusion

    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        return _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            approval=approval,
            fusion=_fusion(
                bus, run_id, seed, config_hash, params, cls=_ToleranceFusion, **fields()
            ),
            correlator=_IsolatedCorrelation(params.correlation_params()),
            engine=_engine(params, _BinaryResponseEngine, n=1),
            memory=False,
            healing=False,
            brake=False,
        )

    return Baseline(baseline_id, name, None, mechanism, build, family="external")


def _tolerance_fields() -> dict[str, Any]:
    from m8_eval_harness.baselines.tolerance import fitted_model

    model, alpha = fitted_model()
    return {"model": model, "alpha": alpha}


TOLERANCE = _tolerance_arm(
    "tolerance",
    "TOLERANCE node controller (Hammar & Stadler 2024)",
    "belief over healthy/compromised from observations; recover (block) when the belief "
    "reaches the CEM threshold; a silent node is evicted; fitted on calibration",
    fields=_tolerance_fields,
)
TOLERANCE_NO_RECOVERY = _tolerance_arm(
    "tolerance_no_recovery",
    "NO-RECOVERY (TOLERANCE's baseline)",
    "never recovers",
    fields=lambda: {"never": True, "evict_silent": False},
)


def tolerance_site(site: str) -> Baseline:
    """
    TOLERANCE with its model measured on one real dataset's calibration half (`tolerance_fit
    --site`).
    """
    from m8_eval_harness.baselines.tolerance import fitted_model, site_config

    def fields() -> dict[str, Any]:
        model, alpha = fitted_model(site_config(site))
        return {"model": model, "alpha": alpha}

    return _tolerance_arm(
        f"tolerance@{site}",
        f"TOLERANCE node controller, model measured on {site}'s calibration half",
        "as `tolerance`, with Z and p_A measured on this dataset's calibration half",
        fields=fields,
    )


def tolerance_periodic(delta_r: float = 15) -> Baseline:
    """PERIODIC (TOLERANCE's baseline): recover every Delta_R steps, whatever is seen."""
    steps = int(delta_r)
    return _tolerance_arm(
        f"tolerance_periodic@{steps}",
        f"PERIODIC every {steps} steps (TOLERANCE's baseline)",
        "recovers every node every Delta_R steps",
        fields=lambda: {"periodic": steps, "evict_silent": False},
    )


ALL_BASELINES: tuple[Baseline, ...] = (
    *BASELINES,
    FULL_REPLICATED_FUSION,
    STATIC_NO_SHARING,
    *RESEARCH_BASELINES,
    *MEDIATED_BASELINES,
    *ABLATION_BASELINES,
    *EXTERNAL_BASELINES,
    FULL_LLM,
    TOLERANCE,
    TOLERANCE_NO_RECOVERY,
)

_FACTORIES: dict[str, Callable[..., Baseline]] = {
    "binary_zt": binary_zero_trust,
    "beta_reputation": beta_reputation,
    "isolation_forest": isolation_forest,
    "isolation_forest_persistent": isolation_forest_persistent,
    "cusum": cusum,
    "page_cusum": page_cusum,
    "dirichlet_reliability": dirichlet_reliability,
    "penalty_healing": penalty_healing,
    "ddca": ddca,
    "tolerance_periodic": tolerance_periodic,
}


def by_id(baseline_id: str) -> Baseline:
    for baseline in ALL_BASELINES:
        if baseline.baseline_id == baseline_id:
            return baseline
    stem, braked, _ = baseline_id.partition("+brake")
    name, _, argument = stem.partition("@")
    if name == "tolerance" and argument and not braked:
        return tolerance_site(argument)
    if name in _FACTORIES:
        kwargs = {"brake": True} if braked else {}
        try:
            values = [float(a) for a in argument.split(":")] if argument else []
            built = _FACTORIES[name](*values, **kwargs)
        except (TypeError, ValueError):
            built = None
        if built is not None and built.baseline_id == baseline_id:
            return built
    from m8_eval_harness.baselines.compromised_core import COMPROMISED_CORE_BASELINES

    for baseline in COMPROMISED_CORE_BASELINES:
        if baseline.baseline_id == baseline_id:
            return baseline
    raise KeyError(f"unknown baseline: {baseline_id}")
