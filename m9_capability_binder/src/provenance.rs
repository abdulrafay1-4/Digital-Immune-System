//! Provenance enum: an exhaustive match is required at every use site.

use pyo3::prelude::*;

#[pyclass(eq, eq_int)]
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ProvenanceLevel {
    Untrusted = 0,
    Low = 1,
    Medium = 2,
    High = 3,
}

impl ProvenanceLevel {
    pub fn parse(s: &str) -> Result<Self, String> {
        match s {
            "UNTRUSTED" | "Untrusted" => Ok(Self::Untrusted),
            "LOW" | "Low" => Ok(Self::Low),
            "MEDIUM" | "Medium" => Ok(Self::Medium),
            "HIGH" | "High" => Ok(Self::High),
            other => Err(format!("unknown provenance: {other}")),
        }
    }

    pub fn rank(self) -> u8 {
        self as u8
    }

    pub fn meets(self, ceiling: ProvenanceLevel) -> bool {
        self.rank() >= ceiling.rank()
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::Untrusted => "UNTRUSTED",
            Self::Low => "LOW",
            Self::Medium => "MEDIUM",
            Self::High => "HIGH",
        }
    }
}

#[pymethods]
impl ProvenanceLevel {
    #[staticmethod]
    fn from_str(s: &str) -> PyResult<Self> {
        Self::parse(s).map_err(pyo3::exceptions::PyValueError::new_err)
    }

    fn __repr__(&self) -> String {
        format!("ProvenanceLevel::{self:?}")
    }
}
