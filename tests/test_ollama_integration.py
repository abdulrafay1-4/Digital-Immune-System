"""Live Ollama tests. Skipped unless a local server has the model pulled."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import pytest

from agents.classifier import LLMClassifier
from agents.llm_cache import DEFAULT_MODEL, CachedLLM, OllamaClient
from agents.orchestrator import TickBatch
from agents.rules_classifier import ThreatType
from shared.schemas import ContextVector, Provenance, TrustUpdate

RUN = dict(run_id="ollama-it", seed=7, config_hash="cafebabecafebabe")
VALID_THREATS = {t.value for t in ThreatType}


def model_available() -> bool:
    """Is a local Ollama not just listening, but able to answer?"""
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as r:
            tags = json.loads(r.read().decode())
        if not any(m.get("name", "").startswith(DEFAULT_MODEL) for m in tags.get("models", [])):
            return False
        probe = json.dumps(
            {"model": DEFAULT_MODEL, "prompt": "ok", "stream": False, "options": {"num_predict": 1}}
        ).encode()
        request = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=probe,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=60) as r:
            json.loads(r.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return False
    return True


pytestmark = pytest.mark.skipif(
    not model_available(),
    reason=f"needs a local Ollama that can actually serve {DEFAULT_MODEL}",
)


def victim_batch(sim_time: float = 10.0) -> TickBatch:
    def node(node_id: str, trust: float, identity: float) -> TrustUpdate:
        return TrustUpdate(
            sim_time=sim_time,
            node_id=node_id,
            node_trust=trust,
            observation=trust,
            context=ContextVector(identity=identity, behavioral=0.9, device=0.9, network=0.9),
            provenance=Provenance.MEDIUM,
            agent_id=f"mon-{node_id}",
            **RUN,
        )

    return TickBatch(
        sim_time=sim_time,
        updates=[node("node-0", 0.25, 0.12), node("node-1", 0.93, 0.95)],
        **RUN,
    )


def make_classifier(sim_cost: float = 1.5) -> LLMClassifier:
    return LLMClassifier(CachedLLM(OllamaClient(timeout=90.0), sim_cost=sim_cost))


def test_real_model_returns_a_usable_classification() -> None:
    clf = make_classifier()
    result = clf.classify(victim_batch())

    assert result.used_llm is True, f"fell back instead: {result.rationale}"
    assert result.threat_type in VALID_THREATS
    assert 0.0 <= result.severity <= 1.0
    assert result.sim_time == pytest.approx(11.5), "must be charged sim-time cost"


def test_real_model_is_deterministic_at_temperature_zero() -> None:
    """The determinism claim, verified against the actual model rather than assumed."""
    prompts_equal = []
    verdicts = []
    for _ in range(2):
        clf = make_classifier()
        batch = victim_batch()
        prompts_equal.append(clf.build_prompt(batch))
        verdicts.append(clf.classify(batch))

    assert prompts_equal[0] == prompts_equal[1]
    assert verdicts[0].threat_type == verdicts[1].threat_type
    assert verdicts[0].severity == pytest.approx(verdicts[1].severity)


def test_cache_prevents_a_second_real_call() -> None:
    clf = make_classifier()
    batch = victim_batch()

    first = clf.classify(batch)
    second = clf.classify(batch)

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert clf.llm.misses == 1
    assert clf.llm.hits == 1


def test_healthy_batch_is_not_reported_as_a_threat() -> None:
    """Sanity check against a model that flags everything."""
    clf = make_classifier()
    healthy = TickBatch(
        sim_time=0.0,
        updates=[
            TrustUpdate(
                sim_time=0.0,
                node_id=f"node-{i}",
                node_trust=0.95,
                observation=0.95,
                context=ContextVector(identity=0.95, behavioral=0.95, device=0.95, network=0.95),
                provenance=Provenance.MEDIUM,
                agent_id=f"mon-node-{i}",
                **RUN,
            )
            for i in range(3)
        ],
        **RUN,
    )
    result = clf.classify(healthy)

    assert result.threat_type in VALID_THREATS
    assert result.severity < 0.5, f"flagged healthy nodes: {result.rationale}"
