"""
Run the whole system on a simulated fleet: monitoring agents, the orchestrator and the closed-loop
pipeline on one bus.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import simpy

from agents.orchestrator import Orchestrator
from agents.pipeline import ClosedLoopPipeline, TickOutcome
from m6_trust_fusion import TrustFusionEngine
from m8_eval_harness.simulator import DEFAULT_CONFIG, run_trust_sim
from shared.bus import InProcBus
from shared.clock import SimPyClock
from shared.run_manifest import RunManifest, config_hash, load_yaml_config


@dataclass
class ClosedLoopRun:
    """Everything one run produced, ready for the metrics layer."""

    manifest: RunManifest
    outcomes: list[TickOutcome]
    series: dict[str, list[float]]
    events_jsonl: bytes
    pipeline: ClosedLoopPipeline = field(repr=False, default=None)  # type: ignore[assignment]

    @property
    def ticks(self) -> int:
        return len(self.outcomes)

    def worst_level(self, node_id: str) -> int:
        """Highest level ever planned for one device across the run."""
        return max(
            (
                plan.proposed_level
                for out in self.outcomes
                for plan in out.plans
                if plan.node_id == node_id
            ),
            default=0,
        )

    def first_tick_at_or_above(self, node_id: str, level: int) -> float | None:
        """Sim time a device first reached `level`."""
        for out in self.outcomes:
            for plan in out.plans:
                if plan.node_id == node_id and plan.proposed_level >= level:
                    return out.sim_time
        return None

    def healing_phases(self, node_id: str) -> list[str]:
        return [
            event.phase
            for out in self.outcomes
            for event in out.healing
            if event.node_id == node_id
        ]

    @property
    def audit_intact(self) -> bool:
        """False if the hash chain does not reconcile, i.e. the log was touched."""
        return self.pipeline.engine.audit.verify() is None


def run_closed_loop(
    *,
    seed: int = 42,
    n_nodes: int = 50,
    ticks: int = 30,
    run_id: str = "closed-loop",
    anomaly_node: str = "node-0",
    anomaly_window: tuple[float, float, float] = (10.0, 25.0, 0.6),
    pipeline: ClosedLoopPipeline | None = None,
    results_dir: Path | None = None,
    config: dict[str, Any] | None = None,
) -> ClosedLoopRun:
    """Drive the full loop over a seeded fleet."""
    bus = InProcBus()
    cfg = config if config is not None else load_yaml_config(DEFAULT_CONFIG)
    cfg_hash = config_hash(cfg)
    loop = pipeline or ClosedLoopPipeline(
        fusion=TrustFusionEngine(bus=bus, run_id=run_id, seed=seed, config_hash=cfg_hash)
    )
    loop.fusion.run_id, loop.fusion.seed, loop.fusion.config_hash = run_id, seed, cfg_hash

    orchestrator = Orchestrator(
        bus=bus,
        run_id=run_id,
        seed=seed,
        config_hash=cfg_hash,
        pipeline=loop,
        observers=tuple((getattr(loop, "attesters", None) or {}).values()),
    )
    env = simpy.Environment()
    orchestrator.clock = SimPyClock(env)
    orchestrator.attach()

    manifest, series, events = run_trust_sim(
        seed=seed,
        n_nodes=n_nodes,
        ticks=ticks,
        run_id=run_id,
        anomaly_node=anomaly_node,
        anomaly_window=anomaly_window,
        config=cfg,
        results_dir=results_dir,
        bus=bus,
        env=env,
    )
    orchestrator.flush()

    return ClosedLoopRun(
        manifest=manifest,
        outcomes=list(loop.outcomes),
        series=series,
        events_jsonl=events,
        pipeline=loop,
    )
