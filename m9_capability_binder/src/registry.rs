//! Capability registry: adding a variant without updating match sites is a compile error.

use crate::provenance::ProvenanceLevel;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Capability {
    MonitorEnhance,
    Reauth,
    Restrict,
    Isolate,
    /// Read immune memory through the mediated broker.
    MemoryRead,
    /// Propose a memory write through the broker.
    MemoryWrite,
}

impl Capability {
    pub fn from_str(s: &str) -> Result<Self, String> {
        match s {
            "monitor_enhance" | "MonitorEnhance" => Ok(Self::MonitorEnhance),
            "reauth" | "Reauth" => Ok(Self::Reauth),
            "restrict" | "Restrict" => Ok(Self::Restrict),
            "isolate" | "Isolate" => Ok(Self::Isolate),
            "memory_read" | "MemoryRead" => Ok(Self::MemoryRead),
            "memory_write" | "MemoryWrite" => Ok(Self::MemoryWrite),
            other => Err(format!("unknown capability: {other}")),
        }
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::MonitorEnhance => "monitor_enhance",
            Self::Reauth => "reauth",
            Self::Restrict => "restrict",
            Self::Isolate => "isolate",
            Self::MemoryRead => "memory_read",
            Self::MemoryWrite => "memory_write",
        }
    }

    /// Minimum input provenance required to resolve this capability.
    pub fn required_provenance(self) -> ProvenanceLevel {
        match self {
            Self::MonitorEnhance => ProvenanceLevel::Low,
            Self::Reauth => ProvenanceLevel::Medium,
            Self::Restrict => ProvenanceLevel::Medium,
            Self::Isolate => ProvenanceLevel::High,
            Self::MemoryRead => ProvenanceLevel::Low,
            Self::MemoryWrite => ProvenanceLevel::Medium,
        }
    }
}
