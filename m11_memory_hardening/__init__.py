"""M11 memory hardening: quorum-gated writes and outlier-based down-weighting."""

from m11_memory_hardening.outlier import (
    AgentVerdict,
    OutlierParams,
    OutlierReport,
    assess,
    median_absolute_deviation,
    robust_z,
)
from m11_memory_hardening.quorum import (
    DEFAULT_K,
    Attestation,
    MemoryCandidate,
    QuorumDecision,
    QuorumGate,
    QuorumParams,
    RejectReason,
    attest,
    verify_certificate,
)

__all__ = [
    "DEFAULT_K",
    "AgentVerdict",
    "OutlierParams",
    "OutlierReport",
    "assess",
    "median_absolute_deviation",
    "robust_z",
    "Attestation",
    "MemoryCandidate",
    "QuorumDecision",
    "QuorumGate",
    "QuorumParams",
    "RejectReason",
    "attest",
    "verify_certificate",
]
