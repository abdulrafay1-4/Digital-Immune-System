"""The closed loop: one sealed batch in, a complete tick of the system out."""

from __future__ import annotations

import math
import statistics
from collections import Counter, deque
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

from agents.approval import ApprovalDecision, ApprovalGate
from agents.correlation import CorrelationAgent
from agents.dual_classifier import DualClassifier
from agents.orchestrator import Pipeline, TickBatch
from agents.planner import ResponsePlanner
from agents.verifier import VerifierAgent, VerifierReport
from m4_response_engine.engine import ExecutionResult, ResponseEngine
from m6_trust_fusion.fusion import TrustFusionEngine
from m11_memory_hardening.outlier import OutlierParams, assess
from shared.provenance import rank
from shared.schemas import (
    AuditRecord,
    Classification,
    CorrelationResult,
    GlobalTrustUpdate,
    HealingEvent,
    Provenance,
    ResponsePlan,
)

RECALL_PROVENANCE = Provenance.MEDIUM


@dataclass
class TickOutcome:
    """Everything one tick produced."""

    sim_time: float
    correlation: CorrelationResult
    classification: Classification
    gt_updates: list[GlobalTrustUpdate]
    plans: list[ResponsePlan]
    report: VerifierReport
    approvals: list[ApprovalDecision] = field(default_factory=list)
    executions: list[ExecutionResult] = field(default_factory=list)
    healing: list[HealingEvent] = field(default_factory=list)
    reputations: dict[str, float] = field(default_factory=dict)

    @property
    def executed(self) -> list[ResponsePlan]:
        return [
            plan
            for plan, result in zip(self.plans, self.executions, strict=True)
            if result.executed
        ]

    @property
    def audit(self) -> list[AuditRecord]:
        return [r.audit for r in self.executions if r.audit is not None]


@dataclass
class ClosedLoopPipeline(Pipeline):
    """Drives every module for one tick."""

    fusion: TrustFusionEngine
    correlator: CorrelationAgent = field(default_factory=CorrelationAgent)
    classifier: Any = field(default_factory=DualClassifier)
    planner: ResponsePlanner = field(default_factory=ResponsePlanner)
    verifier: VerifierAgent = field(
        default_factory=lambda: VerifierAgent(correlator=CorrelationAgent())
    )
    engine: ResponseEngine = field(default_factory=lambda: ResponseEngine(require_signature=True))
    healer: Any | None = None
    recall: Any | None = None
    approval: ApprovalGate | None = None
    quarantined_agent_ids: tuple[str, ...] = ()
    silence_ticks: int = 3
    silence_beta: float = 0.01
    curator: Any | None = None
    attesters: Any | None = None
    input_provenance: Provenance = Provenance.HIGH

    max_retained_outcomes: int = 4096
    max_retained_decisions: int = 50_000
    outcomes: list[TickOutcome] = field(default_factory=list)
    _roster: set[str] = field(default_factory=set, repr=False)
    _missed: dict[str, int] = field(default_factory=dict, repr=False)
    _peak_level: dict[str, int] = field(default_factory=dict, repr=False)
    _peak_pattern: dict[str, str] = field(default_factory=dict, repr=False)
    degraded: dict[str, int] = field(default_factory=dict)
    _silence_drifted: set[str] = field(default_factory=set, repr=False)
    _ramp: dict[str, float] = field(default_factory=dict, repr=False)
    _heal_granted: set[str] = field(default_factory=set, repr=False)
    adjudicator: Any | None = None
    max_auto_restrict_fraction: float | None = None
    min_auto_restrict: int = 5
    restrictions_withheld: int = 0
    intermittent_window: int = 20
    intermittent_alpha: float = 1e-4
    intermittent_loss_floor: float = 0.01
    _signatures: dict[str, tuple[str, ...]] = field(default_factory=dict, repr=False)
    _presence: dict[str, deque] = field(default_factory=dict, repr=False)
    correlation_overstated: int = 0
    correlation_understated: int = 0
    bound_correlator: Any | None = None
    _bound_correlator: Any = field(default=None, repr=False)
    _recall_memo: dict[str, object] = field(default_factory=dict, repr=False)
    _recall_touched_prev: set[str] = field(default_factory=set, repr=False)
    outlier_params: OutlierParams | None = None
    agents_quarantined: set[str] = field(default_factory=set)
    _quarantined_now: frozenset[str] = field(default_factory=frozenset, repr=False)
    persona_violations: int = 0
    broker: Any | None = None
    memory_writes_denied: int = 0
    device_keys: Any | None = None
    reports_unattested_in_core: int = 0
    observers: tuple[Any, ...] = ()
    observer_keys: dict[str, Any] = field(default_factory=dict)
    observer_tolerance: float = 0.15
    observed_contradictions: int = 0
    observed_unverified: int = 0
    _awaiting_adjudication: list[tuple[float, Any]] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if self._bound_correlator is None:
            self._bound_correlator = (
                self.bound_correlator
                if self.bound_correlator is not None
                else CorrelationAgent(self.correlator.params.model_copy(deep=True))
            )

    def run(self, batch: TickBatch) -> TickOutcome:
        if self.device_keys is not None:
            batch = self._attested_only(batch)
        contradicted: set[str] = set()
        if self.observers:
            batch, contradicted = self._observed(batch)
        try:
            self._adjudicate_due(batch.sim_time)
        except Exception:  # noqa: BLE001
            self._degrade("adjudication")
        silent = self._track_silence(batch)
        for update in batch.updates:
            if update.node_id in self._silence_drifted:
                self.fusion.set_drift(update.node_id, 0.0)
                self._silence_drifted.discard(update.node_id)
        misses = {
            u.node_id: self._short_gap_misses(u.node_id)
            for u in batch.updates
            if len(self._presence.get(u.node_id, ())) >= self.intermittent_window
        }
        if misses:
            fleet_rate = statistics.median_low(misses.values()) / self.intermittent_window
            bar = _binomial_upper_count(
                self.intermittent_window,
                max(fleet_rate, self.intermittent_loss_floor),
                self.intermittent_alpha,
            )
            for node_id, count in misses.items():
                if count > bar:
                    self.fusion.set_drift(node_id, 1.0)
                    self._silence_drifted.add(node_id)
        flooding = set(batch.over_budget_agents)
        for update in batch.updates:
            if update.agent_id in flooding:
                self.fusion.set_drift(update.node_id, 1.0)
                self._silence_drifted.add(update.node_id)
                self.persona_violations += 1
        for node_id in contradicted:
            self.fusion.set_drift(node_id, 1.0)
            self._silence_drifted.add(node_id)

        if self.broker is not None:
            worst = min([self.input_provenance, *(u.provenance for u in batch.updates)], key=rank)
            fleet = max(len(self._roster), len(batch.updates))
            self.broker.at(batch.sim_time, worst, fleet)
        self._recall_memo = {}
        published = self.correlator.correlate(
            batch,
            quarantined_agent_ids=self._quarantine(),
            recall=self._recall_view(),
        )
        correlation = self._bounded(batch, published)
        self._reassess_quarantine()
        classification = self.classifier.classify(batch)

        gt_updates = self.fusion.fuse_batch(list(batch.updates), correlation)

        for node_id in silent:
            missed = self._missed.get(node_id, 0)
            self.fusion.set_drift(node_id, min(1.0, missed / max(1, self.silence_ticks * 4)))
            self._silence_drifted.add(node_id)
            update = self.fusion.observe_silence(
                node_id, sim_time=batch.sim_time, beta=self.silence_beta
            )
            if update is not None:
                gt_updates.append(update)

        levels = {u.node_id: self.engine.decide(u) for u in gt_updates}
        plans = self.planner.plan_batch(gt_updates, classification=classification, levels=levels)

        approvals = self._approve(plans, correlation)
        approval_by_node = {d.node_id: d for d in approvals}
        report = self.verifier.audit(
            plans=plans,
            gt_updates=gt_updates,
            correlation=published,
            classification=classification,
            approvals=approval_by_node,
            batch=batch,
        )

        provenance = self._provenance_by_node(batch, correlation)
        restrict_allowed = self._restriction_budget(plans, gt_updates, silent, batch)
        executions = [
            self.engine.execute(
                plan,
                verification=report,
                input_provenance=provenance[plan.node_id],
                approval=approval_by_node.get(plan.node_id),
                restrict_allowed=restrict_allowed.get(plan.node_id, True),
            )
            for plan in plans
        ]

        reputations = self.fusion.observe_responses(plans)
        try:
            healing = self._heal(batch, gt_updates)
        except Exception:  # noqa: BLE001
            self._degrade("healing")
            healing = []
        try:
            self._remember(batch, correlation, classification, levels)
        except Exception:  # noqa: BLE001
            self._degrade("memory_write")

        outcome = TickOutcome(
            sim_time=batch.sim_time,
            correlation=correlation,
            classification=classification,
            gt_updates=gt_updates,
            plans=plans,
            report=report,
            approvals=approvals,
            executions=executions,
            healing=healing,
            reputations=reputations,
        )
        self.outcomes.append(outcome)
        if 0 < self.max_retained_outcomes < len(self.outcomes):
            del self.outcomes[0]
        if self.max_retained_decisions > 0:
            retained = sum(len(o.plans) for o in self.outcomes)
            while len(self.outcomes) > 1 and retained > self.max_retained_decisions:
                retained -= len(self.outcomes.pop(0).plans)
        return outcome

    def _bounded(self, batch: TickBatch, published: CorrelationResult) -> CorrelationResult:
        """What acts is the pipeline's own recomputation; the published result is audited."""
        own = self._bound_correlator.correlate(
            batch, quarantined_agent_ids=self._quarantine(), recall=self._recall_view()
        )
        overstated = (
            published.cti > own.cti
            or published.campaign_corroboration > own.campaign_corroboration
            or published.recall_boost > own.recall_boost
            or bool(set(published.implicated_node_ids) - set(own.implicated_node_ids))
            or any(published.node_ti.get(n, 0.0) > ti for n, ti in own.node_ti.items())
        )
        understated = (
            published.cti < own.cti
            or published.campaign_corroboration < own.campaign_corroboration
            or bool(set(own.implicated_node_ids) - set(published.implicated_node_ids))
            or any(published.node_ti.get(n, 0.0) < ti for n, ti in own.node_ti.items())
        )
        self.correlation_overstated += int(overstated)
        self.correlation_understated += int(understated)
        return own

    def _quarantine(self) -> tuple[str, ...]:
        """Configured quarantine plus what M11 decided last tick."""
        return tuple(sorted(set(self.quarantined_agent_ids) | self._quarantined_now))

    def _reassess_quarantine(self) -> None:
        """M11 on this tick's reliabilities; takes effect on the next tick (t-1 rule)."""
        report = assess(self._bound_correlator.tracker.snapshot(), self.outlier_params)
        self._quarantined_now = report.quarantined
        self.agents_quarantined |= report.quarantined

    def _observed(self, batch: TickBatch) -> tuple[TickBatch, set[str]]:
        """
        The batch with each observed dimension as its observer measured it, and the devices whose
        own signed reading an observer contradicts.
        """
        from shared.attestation import observation_payload

        updates, contradicted, changed = [], set(), False
        for update in batch.updates:
            readings = {}
            for observer in self.observers:
                seen = observer.observe(update.node_id, update.sim_time)
                if seen is None:
                    continue
                key = self.observer_keys.get(observer.dimension)
                payload = observation_payload(
                    observer.dimension, update.node_id, update.sim_time, seen[0]
                )
                if key is None or not key.verify(payload, seen[1]):
                    self.observed_unverified += 1
                    continue
                readings[observer.dimension] = seen[0]
            claimed = {d: getattr(update.context, d) for d in readings}
            if any(abs(claimed[d] - v) > self.observer_tolerance for d, v in readings.items()):
                self.observed_contradictions += 1
                contradicted.add(update.node_id)
            if readings == claimed:
                updates.append(update)
                continue
            context = update.context.model_copy(update=readings)
            updates.append(update.model_copy(update={"context": context}))
            changed = True
        return (batch.model_copy(update={"updates": updates}) if changed else batch), contradicted

    def _attested_only(self, batch: TickBatch) -> TickBatch:
        """The batch without reports whose context this tick's device did not sign."""
        from shared.attestation import attestation_payload

        kept = []
        for update in batch.updates:
            key = self.device_keys.get(update.node_id)
            genuine = (
                key is not None
                and update.attestation is not None
                and update.sim_time == batch.sim_time
                and key.verify(
                    attestation_payload(update.node_id, update.sim_time, update.context),
                    update.attestation,
                )
            )
            if genuine:
                kept.append(update)
            else:
                self.reports_unattested_in_core += 1
        if len(kept) == len(batch.updates):
            return batch
        return batch.model_copy(update={"updates": kept})

    def _recall_view(self) -> Any:
        return None if self.recall is None else SimpleNamespace(recognise=self._recognise)

    def _recognise(self, pattern_text: str) -> object:
        """Ask immune memory, tolerating it being broken."""
        if pattern_text in self._recall_memo:
            return self._recall_memo[pattern_text]
        try:
            source = self.broker if self.broker is not None else self.recall
            answer = source.recognise(pattern_text)  # type: ignore[union-attr]
        except Exception:  # noqa: BLE001
            self._degrade("recall")
            answer = None
        self._recall_memo[pattern_text] = answer
        return answer

    def _adjudicate_due(self, now: float) -> None:
        """Hand stored incidents to the adjudicator once their review is due."""
        if self.adjudicator is None or self.curator is None or not self._awaiting_adjudication:
            return
        due = [(t, r) for t, r in self._awaiting_adjudication if t <= now]
        if not due:
            return
        self._awaiting_adjudication = [(t, r) for t, r in self._awaiting_adjudication if t > now]
        for _, record in due:
            status = self.adjudicator.adjudicate(record)
            if status in ("confirmed", "benign"):
                self.curator.store.adjudicate(
                    record.record_id, status, actor=self.adjudicator.actor_id, sim_time=now
                )

    def _short_gap_misses(self, node_id: str) -> int:
        """Ticks in the window lost to gaps too short for silence escalation."""
        long_gap = 2 * self.silence_ticks
        missed, run, seen_report = 0, 0, False
        for present in self._presence.get(node_id, ()):
            if present:
                if seen_report and 0 < run < long_gap:
                    missed += run
                run, seen_report = 0, True
            else:
                run += 1
        return missed

    def _restriction_budget(
        self,
        plans: list[ResponsePlan],
        gt_updates: list[GlobalTrustUpdate],
        silent: list[str],
        batch: TickBatch,
    ) -> dict[str, bool]:
        """Which devices may be restricted automatically this tick."""
        if self.max_auto_restrict_fraction is None:
            return {}
        dark = set(silent)
        gt_by_node = {u.node_id: u.gt for u in gt_updates}
        contexts = {u.node_id: u.context for u in batch.updates}
        eligible = [
            (gt_by_node.get(p.node_id, 1.0), p.node_id)
            for p in plans
            if p.proposed_level >= 3 and p.node_id not in dark
        ]
        for _, node_id in eligible:
            current = _degraded_dimensions(contexts.get(node_id))
            if current:
                self._signatures[node_id] = current
        signature = {node_id: self._signatures.get(node_id, ()) for _, node_id in eligible}
        group_size = Counter(signature.values())
        candidates = [
            (gt, node_id)
            for _, gt, node_id in sorted(
                (group_size[signature[node_id]], gt, node_id) for gt, node_id in eligible
            )
        ]
        budget = max(
            self.min_auto_restrict,
            math.ceil(self.max_auto_restrict_fraction * max(1, len(self._roster))),
        )
        if len(candidates) <= budget:
            if self.approval is not None:
                self.approval.clear_mass_restriction()
            return {}
        if self.approval is not None:
            try:
                decision = self.approval.review_mass_restriction(
                    count=len(candidates),
                    budget=budget,
                    sim_time=batch.sim_time,
                    run_id=batch.run_id,
                    seed=batch.seed,
                    config_hash=batch.config_hash,
                )
            except Exception:  # noqa: BLE001
                self._degrade("approval")
                decision = None
            if (
                decision is not None
                and decision.approved
                and decision.decided_at_sim <= batch.sim_time
            ):
                return {}
        withheld = candidates[budget:]
        self.restrictions_withheld += len(withheld)
        return {node_id: False for _, node_id in withheld}

    def _degrade(self, stage: str) -> None:
        self.degraded[stage] = self.degraded.get(stage, 0) + 1

    def _track_silence(self, batch: TickBatch) -> list[str]:
        """Known nodes absent for `silence_ticks` consecutive ticks, sorted."""
        reported = {u.node_id for u in batch.updates}
        self._roster |= reported
        for node_id in self._roster:
            window = self._presence.setdefault(node_id, deque(maxlen=self.intermittent_window))
            window.append(node_id in reported)
        silent: list[str] = []
        for node_id in self._roster:
            if node_id in reported:
                self._missed[node_id] = 0
                continue
            self._missed[node_id] = self._missed.get(node_id, 0) + 1
            if self._missed[node_id] >= self.silence_ticks:
                silent.append(node_id)
        return sorted(silent)

    def _provenance_by_node(
        self, batch: TickBatch, correlation: CorrelationResult
    ) -> dict[str, Provenance]:
        """Effective provenance per device: the worst thing behind the decision."""
        recalled = correlation.recall_boost > 0.0
        memory_floor = RECALL_PROVENANCE if recalled else None
        implicated = set(correlation.implicated_node_ids) | {
            u.node_id for u in batch.updates if self.fusion.implicates_on_own_trust(u.node_id)
        }
        touched_now = implicated if memory_floor is not None else set()
        floored = touched_now | self._recall_touched_prev
        self._recall_touched_prev = set(touched_now)

        out: dict[str, Provenance] = {}
        for node_id in self._roster:
            out[node_id] = self.input_provenance
        for update in batch.updates:
            candidates = [self.input_provenance, update.provenance]
            if update.node_id in floored:
                candidates.append(RECALL_PROVENANCE)
            out[update.node_id] = min(candidates, key=rank)
        return out

    def _approve(
        self, plans: list[ResponsePlan], correlation: CorrelationResult
    ) -> list[ApprovalDecision]:
        """Every plan is reviewed; the gate decides which actually escalate."""
        if self.approval is None:
            return []
        decisions = []
        for plan in plans:
            try:
                decisions.append(
                    self.approval.review_plan(plan, campaign_id=correlation.campaign_id)
                )
            except Exception:  # noqa: BLE001
                self._degrade("approval")
        return decisions

    def _heal(self, batch: TickBatch, gt_updates: list[GlobalTrustUpdate]) -> list[HealingEvent]:
        """Feed this tick's GT to M7, with device posture as the health signal."""
        if self.healer is None:
            return []
        health = {u.node_id: u.context.device for u in batch.updates}
        events = []
        for update in gt_updates:
            event = self.healer.observe(
                update.node_id,
                gt=update.gt,
                health=health.get(update.node_id, 1.0),
                sim_time=batch.sim_time,
                approval_granted=update.node_id in self._heal_granted,
            )
            self._heal_granted.discard(update.node_id)
            if event is not None:
                events.append(event)

            target = self.healer.target_for(update.node_id)
            evidence = self.fusion.current_ts(update.node_id)
            if target is None or evidence is None:
                self._ramp.pop(update.node_id, None)
                continue
            ramp = self.healer.next_ts(update.node_id, self._ramp.get(update.node_id, evidence))
            self._ramp[update.node_id] = ramp
            self.fusion.apply_recalibration(update.node_id, min(evidence, ramp))
        return events

    def grant_heal(self, node_id: str) -> None:
        """Release a device parked in NEEDS_APPROVAL."""
        self._heal_granted.add(node_id)

    def _remember(self, batch, correlation, classification, levels) -> None:
        """Turn a resolved incident into a memory candidate."""
        if self.curator is None or self.attesters is None:
            return
        for node_id, level in levels.items():
            was_under_response = self._peak_level.get(node_id, 0)
            if int(level) > was_under_response:
                self._peak_level[node_id] = int(level)
                if correlation.pattern_text:
                    self._peak_pattern[node_id] = correlation.pattern_text
            if int(level) >= 2 or was_under_response < 2:
                continue
            if not self._peak_pattern.get(node_id):
                self._peak_level[node_id] = 0
                continue

            from m5_immune_memory import IncidentSummary

            if self.broker is not None and not getattr(self.curator, "authorises", False):
                from agents.context_broker import CURATOR_CLIENT

                permitted = self.broker.authorise_write(
                    caller_id=CURATOR_CLIENT, sim_time=batch.sim_time
                )
                if not permitted.allowed:
                    self.memory_writes_denied += 1
                    self._peak_level[node_id] = 0
                    self._peak_pattern.pop(node_id, None)
                    continue

            result = self.curator.propose_and_submit(
                IncidentSummary(
                    record_id=f"{batch.run_id}-{node_id}-{batch.sim_time:.6f}",
                    node_ids=(node_id,),
                    peak_level=was_under_response,
                    threat_type=classification.rules_threat_type or classification.threat_type,
                    pattern_text=self._peak_pattern.get(node_id, ""),
                    window_start_sim=max(0.0, batch.sim_time - 10.0),
                    window_end_sim=batch.sim_time,
                    run_id=batch.run_id,
                    seed=batch.seed,
                    config_hash=batch.config_hash,
                ),
                self.attesters,
                now_sim=batch.sim_time,
            )
            if self.adjudicator is not None and result.admitted and result.record is not None:
                due = batch.sim_time + float(getattr(self.adjudicator, "delay_sim", 0.0))
                self._awaiting_adjudication.append((due, result.record))
                if (ask := getattr(self.adjudicator, "ask", None)) is not None:
                    ask(result.record, sim_time=batch.sim_time)
            self._peak_level[node_id] = 0
            self._peak_pattern.pop(node_id, None)


DEGRADED_DIMENSION = 0.75


def _degraded_dimensions(context: Any) -> tuple[str, ...]:
    """Which dimensions a device has lost: how correlated incidents are grouped."""
    if context is None:
        return ()
    return tuple(
        d
        for d in ("identity", "behavioral", "device", "network")
        if getattr(context, d) < DEGRADED_DIMENSION
    )


def _binomial_upper_count(n: int, p: float, alpha: float) -> int:
    """The largest miss count a loss rate `p` still produces with probability above `alpha`."""
    import math

    tail = 0.0
    for k in range(n, -1, -1):
        tail += math.comb(n, k) * p**k * (1 - p) ** (n - k)
        if tail > alpha:
            return k
    return 0
