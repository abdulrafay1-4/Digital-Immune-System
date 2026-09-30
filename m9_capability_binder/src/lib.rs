//! M9 deterministic capability binder: resolves and redeems signed capability tokens.
//! Capabilities are matched exhaustively: a missing variant is a compile error, never an allow.

mod provenance;
mod registry;
mod token;

use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Mutex, OnceLock};

use pyo3::prelude::*;
use pyo3::types::PyDict;

use provenance::ProvenanceLevel;
use registry::Capability;
use token::{sign_token, verify_signature, DenyReason, SignedToken};

/// Development fallback only. Production callers pass a derived key.
const DEFAULT_SECRET: &[u8] = b"dis-m9-dev-secret-change-me";

/// Makes every token unique even for the same subject, capability and tick.
static NONCE: AtomicU64 = AtomicU64::new(1);

const EVICT_FLOOR: usize = 4096;

struct Spent {
    tokens: HashMap<String, f64>,
    evict_at: usize,
}

impl Spent {
    fn new() -> Self {
        Self {
            tokens: HashMap::new(),
            evict_at: EVICT_FLOOR,
        }
    }

    /// Forget tokens the expiry check refuses anyway, in sweeps whose threshold grows.
    fn maybe_evict(&mut self, now: f64) {
        if self.tokens.len() < self.evict_at {
            return;
        }
        self.tokens.retain(|_, expires| now <= *expires);
        self.evict_at = std::cmp::max(EVICT_FLOOR, self.tokens.len() * 2);
    }
}

fn spent() -> &'static Mutex<Spent> {
    static SPENT: OnceLock<Mutex<Spent>> = OnceLock::new();
    SPENT.get_or_init(|| Mutex::new(Spent::new()))
}

fn resolve_inner(
    capability: &str,
    subject_id: &str,
    input_provenance: &str,
    sim_time: f64,
    ttl: f64,
    secret: &[u8],
) -> Result<SignedToken, DenyReason> {
    if !sim_time.is_finite() || !ttl.is_finite() {
        return Err(DenyReason::InvalidTime);
    }
    let cap = Capability::from_str(capability).map_err(|_| DenyReason::UnknownCapability)?;
    let prov =
        ProvenanceLevel::parse(input_provenance).map_err(|_| DenyReason::UnknownCapability)?;
    let required = cap.required_provenance();
    if !prov.meets(required) {
        return Err(DenyReason::ProvenanceTooLow);
    }
    if ttl <= 0.0 {
        return Err(DenyReason::NonPositiveTtl);
    }
    let expires = sim_time + ttl;
    let nonce = NONCE.fetch_add(1, Ordering::Relaxed);
    let token_id = format!("{subject_id}:{}:{sim_time}:{nonce}", cap.as_str());
    Ok(sign_token(
        secret, &token_id, cap, subject_id, expires, required,
    ))
}

/// Resolve a capability request; returns a dict whose `ok` must be checked.
#[pyfunction]
#[pyo3(signature = (capability, subject_id, input_provenance, sim_time, ttl=60.0, secret=None))]
fn resolve_capability(
    py: Python<'_>,
    capability: &str,
    subject_id: &str,
    input_provenance: &str,
    sim_time: f64,
    ttl: f64,
    secret: Option<&[u8]>,
) -> PyResult<Py<PyDict>> {
    let out = PyDict::new_bound(py);
    let key = secret.unwrap_or(DEFAULT_SECRET);
    match resolve_inner(capability, subject_id, input_provenance, sim_time, ttl, key) {
        Ok(tok) => {
            out.set_item("ok", true)?;
            out.set_item("token_id", tok.token_id)?;
            out.set_item("capability", tok.capability)?;
            out.set_item("subject_id", tok.subject_id)?;
            out.set_item("signature", tok.signature)?;
            out.set_item("expires_at_sim", tok.expires_at_sim)?;
            out.set_item("provenance_ceiling", tok.provenance_ceiling)?;
        }
        Err(reason) => {
            out.set_item("ok", false)?;
            out.set_item("deny_reason", reason.as_str())?;
        }
    }
    Ok(out.unbind())
}

#[pyfunction]
#[pyo3(signature = (token_id, capability, subject_id, signature, expires_at_sim, provenance_ceiling, sim_time, secret=None))]
#[allow(clippy::too_many_arguments)]
fn verify_token(
    token_id: &str,
    capability: &str,
    subject_id: &str,
    signature: &str,
    expires_at_sim: f64,
    provenance_ceiling: &str,
    sim_time: f64,
    secret: Option<&[u8]>,
) -> bool {
    if !sim_time.is_finite() || !expires_at_sim.is_finite() || sim_time > expires_at_sim {
        return false;
    }
    let tok = SignedToken {
        token_id: token_id.to_string(),
        capability: capability.to_string(),
        subject_id: subject_id.to_string(),
        signature: signature.to_string(),
        expires_at_sim,
        provenance_ceiling: provenance_ceiling.to_string(),
    };
    verify_signature(secret.unwrap_or(DEFAULT_SECRET), &tok)
}

/// Spend a token exactly once. Returns None when spent, or the reason it was refused.
#[pyfunction]
#[pyo3(signature = (token_id, capability, subject_id, signature, expires_at_sim, provenance_ceiling, now_sim, secret=None))]
#[allow(clippy::too_many_arguments)]
fn redeem_token(
    token_id: &str,
    capability: &str,
    subject_id: &str,
    signature: &str,
    expires_at_sim: f64,
    provenance_ceiling: &str,
    now_sim: f64,
    secret: Option<&[u8]>,
) -> Option<String> {
    if !now_sim.is_finite() || !expires_at_sim.is_finite() {
        return Some("malformed_token".to_string());
    }
    if now_sim > expires_at_sim {
        return Some("token_expired".to_string());
    }
    let tok = SignedToken {
        token_id: token_id.to_string(),
        capability: capability.to_string(),
        subject_id: subject_id.to_string(),
        signature: signature.to_string(),
        expires_at_sim,
        provenance_ceiling: provenance_ceiling.to_string(),
    };
    if !verify_signature(secret.unwrap_or(DEFAULT_SECRET), &tok) {
        return Some("bad_signature".to_string());
    }
    let mut set = spent()
        .lock()
        .unwrap_or_else(|poisoned| poisoned.into_inner());
    set.maybe_evict(now_sim);
    if set.tokens.contains_key(token_id) {
        return Some("token_replayed".to_string());
    }
    set.tokens.insert(token_id.to_string(), expires_at_sim);
    None
}

#[pyfunction]
fn reset_spent_tokens() {
    let mut set = spent()
        .lock()
        .unwrap_or_else(|poisoned| poisoned.into_inner());
    *set = Spent::new();
}

#[pyfunction]
fn spent_token_count() -> usize {
    spent()
        .lock()
        .unwrap_or_else(|poisoned| poisoned.into_inner())
        .tokens
        .len()
}

#[pymodule]
fn dis_m9(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(resolve_capability, m)?)?;
    m.add_function(wrap_pyfunction!(verify_token, m)?)?;
    m.add_function(wrap_pyfunction!(redeem_token, m)?)?;
    m.add_function(wrap_pyfunction!(reset_spent_tokens, m)?)?;
    m.add_function(wrap_pyfunction!(spent_token_count, m)?)?;
    m.add_class::<ProvenanceLevel>()?;
    Ok(())
}
