"""
LangGraph wiring for the reasoning plane: correlate, classify, plan and verify as a graph. It
narrates; the enforcing loop is agents/pipeline.py.
"""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from agents.correlation import CorrelationAgent
from agents.orchestrator import Pipeline, TickBatch
from agents.planner import ResponsePlanner
from agents.rules_classifier import RulesClassifier
from agents.verifier import VerifierAgent, VerifierReport
from shared.schemas import (
    Classification,
    CorrelationResult,
    GlobalTrustUpdate,
    ResponsePlan,
)

try:  # pragma: no cover
    from langgraph.graph import END, START, StateGraph

    LANGGRAPH_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover
    LANGGRAPH_AVAILABLE = False


class Correlator(Protocol):
    """Satisfied by `CorrelationAgent` (M3)."""

    def correlate(self, batch: TickBatch) -> CorrelationResult: ...


class Classifier(Protocol):
    """Satisfied by both `RulesClassifier` and `LLMClassifier`."""

    def classify(self, batch: TickBatch) -> Classification: ...


class Fusion(Protocol):
    """Satisfied by `m6_trust_fusion.TrustFusionEngine`."""

    def fuse_batch(
        self, updates: list[Any], correlation: CorrelationResult | None = None
    ) -> list[GlobalTrustUpdate]: ...


class DISState(BaseModel):
    """State passed between reasoning-plane nodes."""

    model_config = ConfigDict(extra="forbid")

    batch: TickBatch

    cti: float | None = None
    campaign_id: str | None = None
    correlation: CorrelationResult | None = None
    classification: Classification | None = None
    gt_updates: list[GlobalTrustUpdate] = []
    plans: list[ResponsePlan] = []
    proposed_level: int | None = None
    verifier_report: VerifierReport | None = None
    guard_verdict: str | None = None

    trail: list[str] = []

    @property
    def sim_time(self) -> float:
        return self.batch.sim_time

    @property
    def run_id(self) -> str:
        return self.batch.run_id

    @property
    def node_trusts(self) -> dict[str, float]:
        return {u.node_id: u.node_trust for u in self.batch.updates}


def make_correlate(correlator: Correlator | None, recall: Any | None = None) -> Any:
    """Build the correlate node around an injected M3 correlator."""

    def correlate(state: DISState) -> dict[str, Any]:
        trail = [*state.trail, "correlate"]
        if correlator is None:
            return {"trail": trail}
        result = (
            correlator.correlate(state.batch, recall=recall)
            if recall is not None
            else correlator.correlate(state.batch)
        )
        return {
            "trail": trail,
            "cti": result.cti,
            "campaign_id": result.campaign_id,
            "correlation": result,
        }

    return correlate


def make_classify(classifier: Classifier | None) -> Any:
    """Build the classify node around an injected classifier."""

    def classify(state: DISState) -> dict[str, Any]:
        trail = [*state.trail, "classify"]
        if classifier is None:
            return {"trail": trail}
        return {"trail": trail, "classification": classifier.classify(state.batch)}

    return classify


def make_plan(planner: ResponsePlanner | None, fusion: Fusion | None) -> Any:
    """Build the plan node around M6 fusion + the Response Planner."""

    def plan(state: DISState) -> dict[str, Any]:
        trail = [*state.trail, "plan"]
        if planner is None or fusion is None:
            return {"trail": trail}

        gt_updates = fusion.fuse_batch(list(state.batch.updates), state.correlation)
        plans = planner.plan_batch(gt_updates, classification=state.classification)
        worst = max((p.proposed_level for p in plans), default=0)
        return {
            "trail": trail,
            "gt_updates": gt_updates,
            "plans": plans,
            "proposed_level": worst,
        }

    return plan


def make_verify(verifier: VerifierAgent | None) -> Any:
    """Build the verify node around the deterministic Guard."""

    def verify(state: DISState) -> dict[str, Any]:
        trail = [*state.trail, "verify"]
        if verifier is None or not state.plans:
            return {"trail": trail}

        report = verifier.audit(
            plans=state.plans,
            gt_updates=state.gt_updates,
            correlation=state.correlation,
            classification=state.classification,
        )
        return {
            "trail": trail,
            "verifier_report": report,
            "guard_verdict": report.verdict.value,
        }

    return verify


NODE_ORDER: tuple[str, ...] = ("correlate", "classify", "plan", "verify")


def build_graph(
    *,
    correlator: Correlator | None = None,
    classifier: Classifier | None = None,
    planner: ResponsePlanner | None = None,
    fusion: Fusion | None = None,
    verifier: VerifierAgent | None = None,
    recall: Any | None = None,
) -> Any:
    """Compile the reasoning-plane graph."""
    if not LANGGRAPH_AVAILABLE:
        raise RuntimeError(
            "LangGraph is not installed. Install the control-plane extras: "
            'pip install -e ".[agents]"'
        )

    nodes = {
        "correlate": make_correlate(correlator, recall),
        "classify": make_classify(classifier),
        "plan": make_plan(planner, fusion),
        "verify": make_verify(verifier),
    }

    graph = StateGraph(DISState)
    for name in NODE_ORDER:
        graph.add_node(name, nodes[name])

    graph.add_edge(START, NODE_ORDER[0])
    for src, dst in zip(NODE_ORDER, NODE_ORDER[1:], strict=False):
        graph.add_edge(src, dst)
    graph.add_edge(NODE_ORDER[-1], END)

    return graph.compile()


class GraphPipeline(Pipeline):
    """Adapts the compiled graph to the orchestrator's `Pipeline` protocol."""

    max_results = 1024

    def __init__(
        self,
        *,
        correlator: Correlator | None = None,
        classifier: Classifier | None = None,
        planner: ResponsePlanner | None = None,
        fusion: Fusion | None = None,
        verifier: VerifierAgent | None = None,
        compiled: Any | None = None,
    ) -> None:
        self.correlator = correlator if correlator is not None else CorrelationAgent()
        self.classifier = classifier if classifier is not None else RulesClassifier()
        self.fusion = fusion
        self.planner = (
            planner if planner is not None else (ResponsePlanner() if fusion is not None else None)
        )
        self.verifier = (
            verifier if verifier is not None else (VerifierAgent() if fusion is not None else None)
        )
        self._app = (
            compiled
            if compiled is not None
            else build_graph(
                correlator=self.correlator,
                classifier=self.classifier,
                planner=self.planner,
                fusion=self.fusion,
                verifier=self.verifier,
            )
        )
        self.results: list[DISState] = []

    def run(self, batch: TickBatch) -> None:
        raw = self._app.invoke(DISState(batch=batch))
        self.results.append(DISState.model_validate(raw))
        if len(self.results) > self.max_results:
            del self.results[0]

    @property
    def classifications(self) -> list[Classification]:
        return [s.classification for s in self.results if s.classification is not None]
