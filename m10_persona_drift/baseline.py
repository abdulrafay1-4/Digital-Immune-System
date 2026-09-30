"""Fixed persona baseline: invariants, not learned behaviour."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PersonaBaseline:
    """Fixed invariants for an agent."""

    agent_id: str
    message_rate: float = 1.0
    allowed_capabilities: frozenset[str] = field(
        default_factory=lambda: frozenset({"monitor_enhance", "reauth", "restrict", "isolate"})
    )
    capability_mix: dict[str, float] = field(
        default_factory=lambda: {
            "monitor_enhance": 0.5,
            "reauth": 0.2,
            "restrict": 0.2,
            "isolate": 0.1,
        }
    )
    required_schema_keys: frozenset[str] = field(
        default_factory=lambda: frozenset({"sim_time", "run_id", "seed", "config_hash"})
    )
