"""M9 hard gate: every planned action must resolve a signed capability token."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from m9_capability_binder.binder import resolve_capability
from shared.schemas import CapabilityToken, Provenance, ResponsePlan

LEVEL_CAPABILITY: dict[int, str] = {
    0: "monitor_enhance",
    1: "monitor_enhance",
    2: "reauth",
    3: "restrict",
    4: "isolate",
}


@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    capability: str
    token: CapabilityToken | None = None
    deny_reason: str | None = None
    raw: dict[str, Any] | None = None


def level_to_capability(level: int) -> str:
    if level not in LEVEL_CAPABILITY:
        raise ValueError(f"level must be 0..4, got {level}")
    return LEVEL_CAPABILITY[level]


def gate_response_plan(
    plan: ResponsePlan,
    *,
    input_provenance: Provenance | str,
    ttl: float = 60.0,
    prefer_native: bool = True,
) -> GateDecision:
    """Resolve a ResponsePlan through M9 before any execution."""
    capability = level_to_capability(plan.proposed_level)
    prov = (
        input_provenance.value
        if isinstance(input_provenance, Provenance)
        else str(input_provenance)
    )
    result = resolve_capability(
        capability,
        plan.node_id,
        prov,
        plan.sim_time,
        ttl,
        prefer_native=prefer_native,
    )
    if not result.get("ok"):
        return GateDecision(
            allowed=False,
            capability=capability,
            deny_reason=str(result.get("deny_reason", "unknown")),
            raw=dict(result),
        )

    ceiling = Provenance(result["provenance_ceiling"])
    token = CapabilityToken(
        sim_time=plan.sim_time,
        run_id=plan.run_id,
        seed=plan.seed,
        config_hash=plan.config_hash,
        token_id=result["token_id"],
        capability=result["capability"],
        subject_id=result["subject_id"],
        signature=result["signature"],
        expires_at_sim=float(result["expires_at_sim"]),
        provenance_ceiling=ceiling,
    )
    return GateDecision(allowed=True, capability=capability, token=token, raw=dict(result))
