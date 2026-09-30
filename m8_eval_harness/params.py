"""System coefficients chosen by calibration, in one place."""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SystemParams:
    trust_lambda: float = 0.7
    trust_lambda_up: float | None = None
    cohort_margin: float | None = None
    cohort_min_nodes: int = 3
    rep_lam_up: float = 0.95
    rep_lam_down: float = 0.6
    hysteresis_n: int = 3
    drift_coeff: float = 0.3
    alpha: float = 0.40
    beta: float = 0.35
    gamma: float = 0.25
    cti_k: float = 2.0
    campaign_ti_threshold: float = 0.4
    cohort_baseline_cap: float | None = None
    max_auto_restrict_fraction: float | None = None
    min_auto_restrict: int = 5
    intermittent_window: int = 20
    intermittent_alpha: float = 1e-4
    intermittent_loss_floor: float = 0.01
    obs_weights: tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25)

    def fusion_params(self, **overrides: Any):
        from m6_trust_fusion.fusion import FusionParams

        return FusionParams(
            alpha=self.alpha,
            beta=self.beta,
            gamma=self.gamma,
            trust_lambda=self.trust_lambda,
            trust_lambda_up=self.trust_lambda_up,
            obs_weights=tuple(self.obs_weights),
            **{"drift_coeff": self.drift_coeff, **overrides},
        )

    def correlation_params(self):
        from agents.correlation import CorrelationParams

        return CorrelationParams(
            k=self.cti_k,
            campaign_ti_threshold=self.campaign_ti_threshold,
            cohort_margin=self.cohort_margin,
            cohort_min_nodes=self.cohort_min_nodes,
            cohort_baseline_cap=self.cohort_baseline_cap,
            **dict(
                zip(
                    ("w_identity", "w_behavioral", "w_device", "w_network"),
                    self.obs_weights,
                    strict=True,
                )
            ),
        )

    def pipeline_policy(self) -> dict[str, Any]:
        return {
            "max_auto_restrict_fraction": self.max_auto_restrict_fraction,
            "min_auto_restrict": self.min_auto_restrict,
            "intermittent_window": self.intermittent_window,
            "intermittent_alpha": self.intermittent_alpha,
            "intermittent_loss_floor": self.intermittent_loss_floor,
        }

    def reputation_params(self):
        from m6_trust_fusion.reputation import ReputationParams

        return ReputationParams(lam_up=self.rep_lam_up, lam_down=self.rep_lam_down)

    def hysteresis_params(self):
        from m4_response_engine.hysteresis import HysteresisParams

        return HysteresisParams(n=self.hysteresis_n)

    def apply_to_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """A copy of `config` carrying these coefficients, so its hash changes with them."""
        out = copy.deepcopy(config)
        trust = out.setdefault("trust", {})
        trust.update(
            zip(
                ("w_identity", "w_behavioral", "w_device", "w_network"),
                self.obs_weights,
                strict=True,
            )
        )
        trust["lambda"] = self.trust_lambda
        trust["lambda_up"] = (
            self.trust_lambda_up if self.trust_lambda_up is not None else self.trust_lambda
        )
        out.setdefault("reputation", {}).update(
            {"lam_up": self.rep_lam_up, "lam_down": self.rep_lam_down}
        )
        out.setdefault("response", {}).update(
            {
                "hysteresis_n": self.hysteresis_n,
                "max_auto_restrict_fraction": self.max_auto_restrict_fraction,
                "min_auto_restrict": self.min_auto_restrict,
            }
        )
        out.setdefault("silence", {}).update(
            {
                "intermittent_window": self.intermittent_window,
                "intermittent_alpha": self.intermittent_alpha,
                "intermittent_loss_floor": self.intermittent_loss_floor,
            }
        )
        out.setdefault("fusion", {}).update(
            {"alpha": self.alpha, "beta": self.beta, "gamma": self.gamma}
        )
        out.setdefault("cti", {})["k"] = self.cti_k
        out.setdefault("correlation", {}).update(
            {
                "campaign_ti_threshold": self.campaign_ti_threshold,
                "cohort_margin": self.cohort_margin,
                "cohort_min_nodes": self.cohort_min_nodes,
                "cohort_baseline_cap": self.cohort_baseline_cap,
            }
        )
        return out

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


FROZEN = SystemParams(
    cohort_margin=0.15,
    rep_lam_up=0.85,
    cohort_baseline_cap=0.11,
    max_auto_restrict_fraction=0.10,
)
