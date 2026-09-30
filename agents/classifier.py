"""LLM threat classifier: the one place a language model is allowed to reason."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from agents.llm_cache import CachedLLM, LLMError
from agents.orchestrator import TickBatch
from agents.rules_classifier import DIMENSIONS, RulesClassifier, RulesParams, ThreatType
from shared.schemas import Classification

MAX_LISTED_NODES = 10

PROMPT_TEMPLATE = """You are a security threat classifier in a zero-trust monitoring system.

You are given aggregate statistics for one time step. Trust runs 0.0 (fully
compromised) to 1.0 (fully trusted). Context dimensions run 0.0 (severely
degraded) to 1.0 (healthy).

Time step: {sim_time}
Nodes reporting: {n_total}
Nodes below the trust threshold ({threshold}): {n_affected}
Lowest trust observed: {min_trust:.3f}
Mean trust across all nodes: {mean_trust:.3f}

Mean context dimensions for affected nodes:
  identity:   {identity:.3f}
  behavioral: {behavioral:.3f}
  device:     {device:.3f}
  network:    {network:.3f}

Affected node ids: {affected_ids}

Classify using exactly one of these threat_type values:
  none, credential_abuse, anomalous_behavior, device_compromise,
  network_anomaly, unknown

Respond with ONLY a JSON object:
{{"threat_type": "<one of the above>", "severity": <number 0.0-1.0>,
  "reasoning": "<one sentence>"}}"""


class LLMVerdict(BaseModel):
    """Schema the model's JSON must satisfy."""

    model_config = ConfigDict(extra="ignore")

    threat_type: ThreatType
    severity: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""


class LLMClassifier:
    def __init__(
        self,
        llm: CachedLLM,
        *,
        fallback: RulesClassifier | None = None,
        params: RulesParams | None = None,
    ) -> None:
        self.llm = llm
        self.params = params or RulesParams()
        self.fallback = fallback or RulesClassifier(self.params)
        self.fallback_count = 0
        self.llm_count = 0

    def classify(self, batch: TickBatch) -> Classification:
        if not batch.updates:
            raise ValueError("cannot classify an empty batch")

        prompt = self.build_prompt(batch)
        try:
            response = self.llm.complete(prompt)
            verdict = LLMVerdict.model_validate(response.as_json())
        except (LLMError, ValidationError, ValueError):
            self.fallback_count += 1
            result = self.fallback.classify(batch)
            return result.model_copy(
                update={
                    "sim_time": batch.sim_time + self.llm.sim_cost,
                    "rationale": f"[llm-fallback] {result.rationale}",
                }
            )

        self.llm_count += 1
        return Classification(
            sim_time=batch.sim_time + response.sim_cost,
            run_id=batch.run_id,
            seed=batch.seed,
            config_hash=batch.config_hash,
            threat_type=verdict.threat_type.value,
            severity=verdict.severity,
            rationale=verdict.reasoning,
            used_llm=True,
            cache_hit=response.cache_hit,
        )

    def build_prompt(self, batch: TickBatch) -> str:
        """Give the model summary numbers, never raw telemetry."""
        par = self.params
        affected = [u for u in batch.updates if u.node_trust < par.affected_below]
        source = affected or batch.updates

        means = {
            dim: sum(getattr(u.context, dim) for u in source) / len(source) for dim in DIMENSIONS
        }
        listed = sorted(u.node_id for u in affected)[:MAX_LISTED_NODES]
        hidden = len(affected) - MAX_LISTED_NODES
        suffix = f" (+{hidden} more)" if hidden > 0 else ""

        return PROMPT_TEMPLATE.format(
            sim_time=batch.sim_time,
            n_total=len(batch.updates),
            n_affected=len(affected),
            threshold=f"{par.affected_below:.2f}",
            min_trust=batch.min_node_trust,
            mean_trust=batch.mean_node_trust,
            affected_ids=", ".join(listed) + suffix if listed else "none",
            **means,
        )
