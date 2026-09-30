"""Inter-module Pydantic contracts. No raw dicts across module boundaries."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:@+/\-]{0,127}$"
Identifier = Annotated[str, StringConstraints(pattern=IDENTIFIER_PATTERN)]
LONG_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:@+/\-]{0,255}$"
LongIdentifier = Annotated[str, StringConstraints(pattern=LONG_IDENTIFIER_PATTERN)]
Label = Annotated[str, StringConstraints(max_length=64)]
FreeText = Annotated[str, StringConstraints(max_length=4096)]


class Provenance(str, Enum):
    """Closed enum: crosses into Rust as an exhaustively matched type."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNTRUSTED = "UNTRUSTED"


class MessageBase(BaseModel):
    """Every emitted record carries sim_time + run identity."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    sim_time: float = Field(ge=0.0)
    run_id: Identifier
    seed: int
    config_hash: Identifier


class ContextVector(BaseModel):
    """Four-dimensional context."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    identity: float = Field(ge=0.0, le=1.0)
    behavioral: float = Field(ge=0.0, le=1.0)
    device: float = Field(ge=0.0, le=1.0)
    network: float = Field(ge=0.0, le=1.0)


class TrustUpdate(MessageBase):
    """M1 publishes node trust."""

    node_id: Identifier
    node_trust: float = Field(ge=0.0, le=1.0)
    observation: float = Field(ge=0.0, le=1.0)
    context: ContextVector
    provenance: Provenance
    agent_id: Identifier
    attestation: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{128}$")] | None = None


class ThreatIntel(MessageBase):
    node_id: Identifier
    ti_score: float = Field(ge=0.0, le=1.0)
    reporter_agent_id: Identifier
    campaign_id: Identifier | None = None
    notes: FreeText = ""


class AgentReliability(MessageBase):
    """Reporter reliability, kept separate from node_trust."""

    agent_id: Identifier
    agent_reliability: float = Field(ge=0.0, le=1.0)


class CorrelationResult(MessageBase):
    """M3 output. `cti` is global campaign breadth; per-node CTI_i is derived in M6."""

    node_ids: list[Identifier]
    cti: float = Field(ge=0.0, le=1.0)
    implicated_node_ids: list[Identifier] = Field(default_factory=list)
    campaign_id: Identifier | None = None
    outlier_agent_ids: list[Identifier] = Field(default_factory=list)
    pattern_text: FreeText = ""
    recall_boost: float = Field(default=0.0, ge=0.0, le=1.0)
    recalled_record_id: LongIdentifier | None = None
    node_ti: dict[Identifier, float] = Field(default_factory=dict)
    campaign_corroboration: float = Field(default=0.0, ge=0.0, le=1.0)


class GlobalTrustUpdate(MessageBase):
    """M6 publishes per-node GT."""

    node_id: Identifier
    gt: float = Field(ge=0.0, le=1.0)
    ts: float = Field(ge=0.0, le=1.0)
    cti_i: float = Field(ge=0.0, le=1.0)
    cti_trust: float = Field(ge=0.0, le=1.0)
    rep: float = Field(ge=0.0, le=1.0)
    master_score: float = Field(ge=0.0, le=1.0)
    drift_flag: float = Field(ge=0.0, le=1.0, default=0.0)
    threat_confirmed: bool = False
    signature: str = ""


class Classification(MessageBase):
    threat_type: Label
    severity: float = Field(ge=0.0, le=1.0)
    rationale: FreeText = ""
    used_llm: bool = False
    cache_hit: bool = False
    rules_threat_type: Label | None = None
    rules_severity: float | None = Field(default=None, ge=0.0, le=1.0)
    classifiers_agree: bool | None = None


class ResponsePlan(MessageBase):
    node_id: Identifier
    proposed_level: int = Field(ge=0, le=4)
    rationale: FreeText = ""


class CapabilityToken(MessageBase):
    token_id: LongIdentifier
    capability: Identifier
    subject_id: Identifier
    signature: str
    expires_at_sim: float
    provenance_ceiling: Provenance


MemoryStatus = Literal["pending", "confirmed", "benign"]


class MemoryRecord(MessageBase):
    """One admitted immune-memory record, shared by the write and read paths."""

    record_id: LongIdentifier
    pattern_text: FreeText
    threat_type: Label
    node_ids: list[Identifier] = Field(default_factory=list)
    window_start_sim: float = 0.0
    window_end_sim: float = 0.0
    proposer_id: Annotated[str, StringConstraints(max_length=128)] = ""
    embedding_dim: int = 384
    quorum_certificate: str | None = None
    similarity_hint: float | None = None
    status: MemoryStatus = "pending"
    adjudicated_by: Annotated[str, StringConstraints(max_length=128)] | None = None
    adjudication_sim: float | None = None
    adjudication_signature: str | None = None


class HealingEvent(MessageBase):
    node_id: Identifier
    phase: Annotated[str, StringConstraints(max_length=32)]
    target_ts: float | None = None
    success: bool = True


class AuditRecord(MessageBase):
    event_type: Identifier
    actor_id: Identifier
    payload: dict[str, Any] = Field(default_factory=dict)


class SkeletonEvent(MessageBase):
    """Walking-skeleton null-node event (constant publish)."""

    node_id: Identifier
    value: float


class SealedBatch(MessageBase):
    """One tick as the orchestrator sealed it: the attesters' evidence."""

    updates: list[TrustUpdate]
    over_budget_agents: list[Identifier] = Field(default_factory=list)
    part: int = Field(default=0, ge=0)
    parts: int = Field(default=1, ge=1, le=512)


class AttestationRequest(MessageBase):
    """A memory candidate put to every attester."""

    request_id: Identifier
    record_id: Identifier
    pattern_text: FreeText
    threat_type: Label
    node_ids: list[Identifier]
    window_start_sim: float
    window_end_sim: float
    proposer_id: Identifier


class SignedAttestation(MessageBase):
    """One attester's Ed25519 signature over a candidate's record hash."""

    request_id: Identifier
    record_hash: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    attester_id: Identifier
    signature: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{128}$")]


FusionPart = Annotated[str, StringConstraints(max_length=12_000)]


class FusionCall(MessageBase):
    seq: int = Field(ge=1)
    method: Identifier
    part: int = Field(ge=0)
    parts: int = Field(ge=1, le=64)
    body: FusionPart


class FusionReply(MessageBase):
    seq: int = Field(ge=1)
    ok: bool
    part: int = Field(ge=0)
    parts: int = Field(ge=1, le=64)
    body: FusionPart


class OperatorQuestion(MessageBase):
    """An isolation the control plane will not carry out without a person."""

    node_id: Identifier
    level: int = Field(ge=0, le=4)
    rationale: FreeText = ""
    open: bool = True


class OperatorDecision(MessageBase):
    """A person's answer, signed with the console's Ed25519 key (`sim_time` = the question's)."""

    node_id: Identifier
    approved: bool
    reason: FreeText
    decided_by: Identifier
    signature: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{128}$")]


class AdjudicationQuestion(MessageBase):
    """A remembered incident waiting for a person to say what it meant."""

    record_id: LongIdentifier
    threat_type: Label
    node_ids: list[Identifier] = Field(default_factory=list)
    window_start_sim: float = 0.0
    window_end_sim: float = 0.0
    pattern_text: FreeText = ""
    status: MemoryStatus = "pending"
    decided_by: Identifier | None = None
    open: bool = True


class AdjudicationVerdict(MessageBase):
    """
    A person's verdict on one remembered incident, signed with the console's Ed25519 key (`sim_time`
    = the question's).
    """

    record_id: LongIdentifier
    status: Literal["confirmed", "benign"]
    decided_by: Identifier
    signature: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{128}$")]


class DeviceMeasurement(MessageBase):
    """
    One device's measurement and its own Ed25519 signature over it, from the device's sensor to its
    monitor (the container deployment, attested).
    """

    node_id: Identifier
    context: ContextVector
    provenance: Provenance
    attestation: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{128}$")]
