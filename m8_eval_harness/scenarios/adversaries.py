"""Adversaries for scenarios s4 to s6: attacks on the immune system, not the fleet."""

from __future__ import annotations

from dataclasses import dataclass, field

from agents.orchestrator import TRUST_TOPIC
from m10_persona_drift.nhi import issue_identity
from m11_memory_hardening import MemoryCandidate, attest
from shared.schemas import ContextVector, Provenance, TrustUpdate


@dataclass
class CompromisedAgent:
    """S4. A monitoring agent under attacker control."""

    name: str = "compromised-agent"
    victim_ids: tuple[str, ...] = ()
    own_node: str = "node-0"
    start_sim: float = 5.0

    forged_for_others: int = 0
    lies_about_own: int = 0

    def before_tick(self, run: object, sim_time: float) -> None:
        if sim_time < self.start_sim:
            return
        bus = run.as_agent(f"mon-{self.own_node}")  # type: ignore[attr-defined]

        for victim in self.victim_ids:
            bus.publish(
                TRUST_TOPIC,
                _update(
                    node_id=victim,
                    agent_id=f"mon-{self.own_node}",
                    level=0.01,
                    sim_time=sim_time,
                    run=run,
                ),
            )
            self.forged_for_others += 1

        bus.publish(
            TRUST_TOPIC,
            _update(
                node_id=self.own_node,
                agent_id=f"mon-{self.own_node}",
                level=0.97,
                sim_time=sim_time,
                run=run,
            ),
        )
        self.lies_about_own += 1

    def after_tick(self, run: object, sim_time: float, outcome: object) -> None:
        return None


@dataclass
class MemoryPoisoner:
    """S5. An attacker trying to write a false record into immune memory."""

    name: str = "memory-poisoner"
    write_path: object | None = None
    registry: dict | None = None
    start_sim: float = 5.0
    every: float = 5.0

    attempts: int = 0
    accepted: int = 0
    by_strategy: dict[str, int] = field(default_factory=dict)

    def before_tick(self, run: object, sim_time: float) -> None:
        if self.write_path is None or sim_time < self.start_sim:
            return
        if (sim_time - self.start_sim) % self.every != 0:
            return

        strategy = ["unattested", "forged", "sub_quorum", "true_facts_false_label"][
            self.attempts % 4
        ]
        candidate = MemoryCandidate(
            record_id=f"poison-{self.attempts}",
            pattern_text="identity:severe behavioral:severe device:clear network:clear"
            " breadth few severity high",
            threat_type="none" if strategy == "true_facts_false_label" else "credential_abuse",
            node_ids=("node-0",),
            window_start_sim=max(0.0, sim_time - 4.0),
            window_end_sim=sim_time,
            run_id=run.run_id,  # type: ignore[attr-defined]
            seed=run.seed,  # type: ignore[attr-defined]
            config_hash=run.config_hash,  # type: ignore[attr-defined]
            proposer_id="memory-curator",
        )

        attestations = []
        if strategy == "forged":
            rogue = issue_identity("rogue", seed=b"rogue".ljust(32, b"\0"))
            attestations = [attest(candidate, rogue, sim_time=sim_time)]
        elif strategy in ("sub_quorum", "true_facts_false_label"):
            names = sorted(self.registry or {})[:2]
            attestations = [attest(candidate, self.registry[n], sim_time=sim_time) for n in names]

        result = self.write_path.submit(  # type: ignore[attr-defined]
            candidate, attestations, now_sim=sim_time
        )
        self.attempts += 1
        self.by_strategy[strategy] = self.by_strategy.get(strategy, 0) + 1
        if result.admitted:
            self.accepted += 1

    def after_tick(self, run: object, sim_time: float, outcome: object) -> None:
        return None


@dataclass
class HealingWeaponiser:
    """S6. Turning the system's own response into the outage."""

    name: str = "healing-weaponiser"
    target: str = "node-1"
    start_sim: float = 4.0
    push_ticks: int = 4
    rest_ticks: int = 4

    cycles: int = 0
    pushes: int = 0

    def before_tick(self, run: object, sim_time: float) -> None:
        if sim_time < self.start_sim:
            return
        phase = int(sim_time - self.start_sim) % (self.push_ticks + self.rest_ticks)
        if phase >= self.push_ticks:
            return
        if phase == 0:
            self.cycles += 1
        self.pushes += 1
        run.as_agent(f"mon-{self.target}").publish(  # type: ignore[attr-defined]
            TRUST_TOPIC,
            _update(
                node_id=self.target,
                agent_id=f"mon-{self.target}",
                level=0.02,
                sim_time=sim_time,
                run=run,
            ),
        )

    def after_tick(self, run: object, sim_time: float, outcome: object) -> None:
        return None


def _update(
    *, node_id: str, agent_id: str, level: float, sim_time: float, run: object
) -> TrustUpdate:
    """A self-consistent forged report."""
    return TrustUpdate(
        sim_time=sim_time,
        run_id=run.run_id,  # type: ignore[attr-defined]
        seed=run.seed,  # type: ignore[attr-defined]
        config_hash=run.config_hash,  # type: ignore[attr-defined]
        node_id=node_id,
        node_trust=level,
        observation=level,
        context=ContextVector(identity=level, behavioral=level, device=level, network=level),
        provenance=Provenance.HIGH,
        agent_id=agent_id,
    )


@dataclass
class LyingCorrelation:
    """A compromised correlation agent, lying in either direction."""

    name: str = "lying-correlation"
    start_sim: float = 10.0
    mode: str = "inflate"
    installed: bool = False
    lies: int = 0

    def before_tick(self, run: object, sim_time: float) -> None:
        if self.installed:
            return
        correlator = run.pipeline.correlator  # type: ignore[attr-defined]
        honest = correlator.correlate
        outer = self

        def lying(batch, **kwargs):  # type: ignore[no-untyped-def]
            result = honest(batch, **kwargs)
            if batch.sim_time < outer.start_sim:
                return result
            outer.lies += 1
            if outer.mode == "suppress":
                return result.model_copy(
                    update={
                        "implicated_node_ids": [],
                        "cti": 0.0,
                        "campaign_corroboration": 0.0,
                        "campaign_id": None,
                        "node_ti": {n: 0.0 for n in result.node_ti},
                    }
                )
            return result.model_copy(
                update={
                    "implicated_node_ids": sorted(result.node_ids),
                    "cti": 0.9,
                    "campaign_corroboration": 0.30,
                }
            )

        correlator.correlate = lying
        self.installed = True

    def after_tick(self, run: object, sim_time: float, outcome: object) -> None:
        return None


@dataclass
class SybilPadding:
    """Sybil registration."""

    name: str = "sybil-padding"
    count: int = 200
    start_sim: float = 5.0
    level: float = 0.97
    published: int = 0

    def before_tick(self, run: object, sim_time: float) -> None:
        if sim_time < self.start_sim or sim_time != int(sim_time):
            return
        for i in range(self.count):
            run.bus.publish(  # type: ignore[attr-defined]
                TRUST_TOPIC,
                _update(
                    node_id=f"sybil-{i}",
                    agent_id=f"mon-sybil-{i}",
                    level=self.level,
                    sim_time=sim_time,
                    run=run,
                ),
            )
            self.published += 1

    def after_tick(self, run: object, sim_time: float, outcome: object) -> None:
        return None


@dataclass
class FutureDating:
    """Watermark poisoning."""

    name: str = "future-dating"
    node_id: str = "node-0"
    offset: float = 0.5
    sent: int = 0

    def before_tick(self, run: object, sim_time: float) -> None:
        if sim_time != int(sim_time):
            return
        run.bus.publish(  # type: ignore[attr-defined]
            TRUST_TOPIC,
            _update(
                node_id=self.node_id,
                agent_id=f"mon-{self.node_id}",
                level=0.9,
                sim_time=sim_time + self.offset,
                run=run,
            ),
        )
        self.sent += 1

    def after_tick(self, run: object, sim_time: float, outcome: object) -> None:
        return None
