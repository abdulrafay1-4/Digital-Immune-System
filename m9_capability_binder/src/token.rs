//! Signed capability tokens: callers must handle DenyReason (no fall-through-to-allow).

use hmac::{Hmac, Mac};
use sha2::Sha256;

use crate::provenance::ProvenanceLevel;
use crate::registry::Capability;

type HmacSha256 = Hmac<Sha256>;

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum DenyReason {
    UnknownCapability,
    ProvenanceTooLow,
    NonPositiveTtl,
    InvalidTime,
}

impl DenyReason {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::UnknownCapability => "unknown_capability",
            Self::ProvenanceTooLow => "provenance_too_low",
            Self::NonPositiveTtl => "non_positive_ttl",
            Self::InvalidTime => "invalid_time",
        }
    }
}

#[derive(Clone, Debug)]
pub struct SignedToken {
    pub token_id: String,
    pub capability: String,
    pub subject_id: String,
    pub signature: String,
    pub expires_at_sim: f64,
    pub provenance_ceiling: String,
}

/// The signed payload, with expiry fixed to six decimals so Rust and Python sign identical bytes.
pub fn payload(
    token_id: &str,
    capability: &str,
    subject_id: &str,
    expires_at_sim: f64,
    ceiling: &str,
) -> String {
    format!("{token_id}|{capability}|{subject_id}|{expires_at_sim:.6}|{ceiling}")
}

pub fn sign_token(
    secret: &[u8],
    token_id: &str,
    capability: Capability,
    subject_id: &str,
    expires_at_sim: f64,
    ceiling: ProvenanceLevel,
) -> SignedToken {
    let ceiling_s = ceiling.as_str();
    let body = payload(
        token_id,
        capability.as_str(),
        subject_id,
        expires_at_sim,
        ceiling_s,
    );
    let mut mac = HmacSha256::new_from_slice(secret).expect("HMAC key");
    mac.update(body.as_bytes());
    let sig = hex::encode(mac.finalize().into_bytes());
    SignedToken {
        token_id: token_id.to_string(),
        capability: capability.as_str().to_string(),
        subject_id: subject_id.to_string(),
        signature: sig,
        expires_at_sim,
        provenance_ceiling: ceiling_s.to_string(),
    }
}

pub fn verify_signature(secret: &[u8], token: &SignedToken) -> bool {
    let body = payload(
        &token.token_id,
        &token.capability,
        &token.subject_id,
        token.expires_at_sim,
        &token.provenance_ceiling,
    );
    let mut mac = match HmacSha256::new_from_slice(secret) {
        Ok(m) => m,
        Err(_) => return false,
    };
    mac.update(body.as_bytes());
    match hex::decode(&token.signature) {
        Ok(bytes) => mac.verify_slice(&bytes).is_ok(),
        Err(_) => false,
    }
}
