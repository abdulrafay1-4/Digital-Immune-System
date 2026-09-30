"""The trusted components, compromised one at a time."""

from __future__ import annotations

from typing import Any

from agents.pipeline import ClosedLoopPipeline
from m6_trust_fusion.fusion import TrustFusionEngine, fuse_gt, gt_payload
from m8_eval_harness.params import FROZEN
from shared.integrity import sign
from shared.schemas import ContextVector, GlobalTrustUpdate, TrustUpdate

VICTIMS = 3


def _number(node_id: str) -> int:
    tail = node_id.rsplit("-", 1)[-1]
    return int(tail) if tail.isdigit() else -1


def _victims(node_ids: Any) -> set[str]:
    return set(sorted(node_ids, key=_number)[-VICTIMS:])


class _CompromisedFusion(TrustFusionEngine):
    """Trust fusion under the attacker's control."""

    mode: str = "suppress_naive"

    def fuse_batch(self, updates: Any, correlation: Any) -> list[GlobalTrustUpdate]:
        fused = super().fuse_batch(updates, correlation)
        self.__dict__.setdefault("_seen", set()).update(u.node_id for u in fused)
        return [self._forge(u) for u in fused]

    def observe_silence(self, node_id: str, **kw: Any) -> GlobalTrustUpdate | None:
        update = super().observe_silence(node_id, **kw)
        return None if update is None else self._forge(update)

    def _forge(self, u: GlobalTrustUpdate) -> GlobalTrustUpdate:
        seen = self.__dict__.setdefault("_seen", set())
        suppress = self.mode.startswith("suppress")
        if not suppress and u.node_id not in _victims(seen):
            return u
        naive = self.mode.endswith("naive")
        if suppress:
            inputs = dict(ts=u.ts, cti_i=u.cti_i, rep=u.rep, drift_flag=u.drift_flag)
            if not naive:
                inputs = dict(ts=1.0, cti_i=0.0, rep=1.0, drift_flag=0.0)
            gt = 1.0
        else:
            inputs = dict(ts=u.ts, cti_i=u.cti_i, rep=u.rep, drift_flag=u.drift_flag)
            if not naive:
                inputs = dict(ts=0.05, cti_i=1.0, rep=0.05, drift_flag=1.0)
            gt = 0.05
        if not naive:
            gt, _ = fuse_gt(**inputs, params=self.params)
        payload = gt_payload(
            run_id=u.run_id,
            seed=u.seed,
            config_hash=u.config_hash,
            sim_time=u.sim_time,
            node_id=u.node_id,
            gt=gt,
            ts=inputs["ts"],
            cti_i=inputs["cti_i"],
            rep=inputs["rep"],
            drift_flag=inputs["drift_flag"],
        )
        return u.model_copy(
            update={
                "gt": gt,
                "ts": inputs["ts"],
                "cti_i": inputs["cti_i"],
                "rep": inputs["rep"],
                "drift_flag": inputs["drift_flag"],
                "signature": sign(payload, self.signing_key),
            }
        )


class _CompromisedOrchestrator(ClosedLoopPipeline):
    """The core, fed by an orchestrator under the attacker's control."""

    def run(self, batch: Any) -> Any:
        return super().run(self._tamper(batch))

    def _tamper(self, batch: Any) -> Any:
        mode = self.__dict__.get("orchestrator_mode", "frame")
        good: dict[str, TrustUpdate] = self.__dict__.setdefault("_last_good", {})
        out = []
        if mode == "frame":
            victims = _victims(u.node_id for u in batch.updates)
            for u in batch.updates:
                out.append(_forged_low(u) if u.node_id in victims else u)
        else:
            for u in batch.updates:
                if u.node_trust >= 0.9:
                    good[u.node_id] = u
                    out.append(u)
                elif u.node_id in good:
                    out.append(good[u.node_id].model_copy(update={"sim_time": u.sim_time}))
                else:
                    out.append(u)
        return batch.model_copy(update={"updates": out})


def _forged_low(u: TrustUpdate) -> TrustUpdate:
    """A report the device never made."""
    low = 0.1
    return u.model_copy(
        update={
            "node_trust": low,
            "observation": low,
            "context": ContextVector(identity=low, behavioral=low, device=low, network=low),
        }
    )


def compromised_fusion(
    mode: str,
    *,
    engine_check: bool = True,
    replicated: bool = False,
    instances: int = 3,
    liars: int = 1,
):
    from m8_eval_harness.baselines.base import _assemble, _fusion

    def build(*, bus, run_id, seed, config_hash, params=FROZEN, approval=None, **_):
        def liar() -> Any:
            instance = _fusion(bus, run_id, seed, config_hash, params, cls=_CompromisedFusion)
            instance.mode = mode
            return instance

        fusion: Any = liar()
        if replicated:
            from m6_trust_fusion.replicated import ReplicatedFusion

            honest = [
                _fusion(bus, run_id, seed, config_hash, params) for _ in range(instances - liars)
            ]
            fusion = ReplicatedFusion(
                [fusion, *(liar() for _ in range(liars - 1)), *honest], bus=bus
            )
        pipeline = _assemble(
            bus=bus,
            run_id=run_id,
            seed=seed,
            config_hash=config_hash,
            params=params,
            fusion=fusion,
            approval=approval,
        )
        pipeline.engine.fusion_params = fusion.params if engine_check else None
        return pipeline

    return build


def compromised_orchestrator(mode: str):
    from m8_eval_harness.baselines.base import _full

    def build(**kw: Any) -> ClosedLoopPipeline:
        pipeline = _full(**kw)
        pipeline.__class__ = _CompromisedOrchestrator
        pipeline.orchestrator_mode = mode
        return pipeline

    return build


def _arms() -> tuple[Any, ...]:
    from m8_eval_harness.baselines.base import Baseline

    arms = []
    for mode in ("suppress", "frame"):
        arms.append(
            Baseline(
                f"core_fusion_{mode}_replicated",
                f"Compromised fusion ({mode}), one of three replicas",
                "trusted core",
                "a majority of three fusion instances acts",
                compromised_fusion(mode, replicated=True),
            )
        )
        for instances in (3, 5):
            arms.append(
                Baseline(
                    f"core_fusion_{mode}_replicated_2of{instances}",
                    f"Compromised fusion ({mode}), two of {instances} replicas colluding",
                    "trusted core",
                    "more liars than three instances tolerate, and five",
                    compromised_fusion(mode, replicated=True, instances=instances, liars=2),
                )
            )
    for mode in ("suppress_naive", "suppress", "frame_naive", "frame"):
        for check in (True, False):
            suffix = "" if check else "_unchecked"
            arms.append(
                Baseline(
                    f"core_fusion_{mode}{suffix}",
                    f"Compromised fusion ({mode.replace('_', ', ')})"
                    + ("" if check else ", engine does not recompute GT"),
                    "trusted core",
                    "trust fusion under the attacker's control",
                    compromised_fusion(mode, engine_check=check),
                )
            )
    for mode in ("frame", "hide"):
        arms.append(
            Baseline(
                f"core_orchestrator_{mode}",
                f"Compromised orchestrator ({mode})",
                "trusted core",
                "the tick sealer under the attacker's control",
                compromised_orchestrator(mode),
            )
        )
    return tuple(arms)


COMPROMISED_CORE_BASELINES = _arms()
