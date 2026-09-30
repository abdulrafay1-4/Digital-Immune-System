"""Monitoring agent: thin wiring of core, sensor, bus and clock."""

from __future__ import annotations

from m1_monitoring.core.observation import observation_from_context
from m1_monitoring.core.trust import TrustParams, TrustState
from m1_monitoring.sensors.base import TelemetrySource
from shared.bus import Bus
from shared.clock import Clock
from shared.schemas import TrustUpdate

TRUST_TOPIC = "trust.update"


class MonitoringAgent:
    def __init__(
        self,
        *,
        node_id: str,
        agent_id: str,
        sensor: TelemetrySource,
        bus: Bus,
        clock: Clock,
        run_id: str,
        seed: int,
        config_hash: str,
        trust_params: TrustParams | None = None,
        obs_weights: dict[str, float] | None = None,
    ) -> None:
        self.node_id = node_id
        self.agent_id = agent_id
        self.sensor = sensor
        self.bus = bus
        self.clock = clock
        self.run_id = run_id
        self.seed = seed
        self.config_hash = config_hash
        self.params = trust_params or TrustParams()
        self.state = TrustState.initial(self.params, sim_time=clock.now())
        self.obs_weights = obs_weights or {
            "w_identity": 0.25,
            "w_behavioral": 0.25,
            "w_device": 0.25,
            "w_network": 0.25,
        }

    def tick(self) -> TrustUpdate:
        sim_time = self.clock.now()
        ctx, provenance = self.sensor.read(sim_time, self.node_id)
        observation = observation_from_context(ctx, **self.obs_weights)
        ts = self.state.step(observation, sim_time)
        attest = getattr(self.sensor, "attestation", None)
        attestation = attest(sim_time, self.node_id) if attest is not None else None
        update = TrustUpdate(
            sim_time=sim_time,
            run_id=self.run_id,
            seed=self.seed,
            config_hash=self.config_hash,
            node_id=self.node_id,
            node_trust=ts,
            observation=observation,
            context=ctx,
            provenance=provenance,
            agent_id=self.agent_id,
            attestation=attestation,
        )
        self.bus.publish(TRUST_TOPIC, update)
        return update
