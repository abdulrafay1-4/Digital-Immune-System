"""LLM caching, sim-time charging, and transport-level failure handling."""

from __future__ import annotations

import json

import pytest

from agents.llm_cache import (
    CachedLLM,
    FakeLLM,
    LLMError,
    LLMResponse,
    OllamaClient,
    prompt_hash,
)


def json_response(**fields: object) -> str:
    return json.dumps(fields)


def test_identical_prompt_is_served_from_cache() -> None:
    client = FakeLLM(json_response(threat_type="none", severity=0.0))
    llm = CachedLLM(client)

    first = llm.complete("same prompt")
    second = llm.complete("same prompt")

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert first.text == second.text
    assert len(client.calls) == 1, "cache must prevent the second model call"
    assert (llm.hits, llm.misses) == (1, 1)


def test_different_prompts_are_separate_entries() -> None:
    client = FakeLLM(["a", "b"])
    llm = CachedLLM(client)

    assert llm.complete("one").text == "a"
    assert llm.complete("two").text == "b"
    assert llm.misses == 2
    assert llm.hits == 0


def test_cache_key_includes_the_model() -> None:
    """Switching models must not serve a stale hit from the previous one."""
    assert prompt_hash("p", "llama3.2:3b") != prompt_hash("p", "phi3:mini")
    assert prompt_hash("p", "m") == prompt_hash("p", "m")


def test_clear_empties_the_cache() -> None:
    client = FakeLLM("x")
    llm = CachedLLM(client)

    llm.complete("p")
    llm.clear()
    llm.complete("p")

    assert len(client.calls) == 2


def test_a_real_call_is_charged_sim_time() -> None:
    llm = CachedLLM(FakeLLM("x"), sim_cost=1.5)
    response = llm.complete("p")

    assert response.sim_cost == pytest.approx(1.5)
    assert llm.total_sim_cost == pytest.approx(1.5)


def test_cache_hits_are_free_by_default() -> None:
    """
    A hit did not call the model, so charging it would inflate latency during sweeps where almost
    everything is cached.
    """
    llm = CachedLLM(FakeLLM("x"), sim_cost=1.5)

    llm.complete("p")
    hit = llm.complete("p")

    assert hit.sim_cost == 0.0
    assert llm.total_sim_cost == pytest.approx(1.5)


def test_cache_hits_can_be_charged_when_modelling_a_real_deployment() -> None:
    llm = CachedLLM(FakeLLM("x"), sim_cost=2.0, charge_on_cache_hit=True)

    llm.complete("p")
    llm.complete("p")

    assert llm.total_sim_cost == pytest.approx(4.0)


def test_negative_sim_cost_is_rejected() -> None:
    with pytest.raises(ValueError, match="sim_cost must be >= 0"):
        CachedLLM(FakeLLM("x"), sim_cost=-1.0)


def test_zero_sim_cost_is_allowed() -> None:
    """Needed for the no-LLM ablation, where nothing should be charged."""
    llm = CachedLLM(FakeLLM("x"), sim_cost=0.0)
    assert llm.complete("p").sim_cost == 0.0


@pytest.mark.parametrize(
    "text",
    [
        "not json at all",
        "",
        "{unclosed",
        '{"a": 1,}',
        "```json\n{}\n```",
    ],
)
def test_unparseable_output_raises_llm_error(text: str) -> None:
    llm = CachedLLM(FakeLLM(text))
    with pytest.raises(LLMError, match="valid JSON"):
        llm.complete("p").as_json()


@pytest.mark.parametrize("text", ["[1, 2, 3]", '"a string"', "42", "true", "null"])
def test_valid_json_that_is_not_an_object_is_rejected(text: str) -> None:
    """json.loads succeeds on these, so only a type check catches them."""
    llm = CachedLLM(FakeLLM(text))
    with pytest.raises(LLMError, match="expected a JSON object"):
        llm.complete("p").as_json()


def test_well_formed_object_parses() -> None:
    llm = CachedLLM(FakeLLM(json_response(threat_type="none", severity=0.25)))
    parsed = llm.complete("p").as_json()

    assert parsed == {"threat_type": "none", "severity": 0.25}


def test_exhausted_fake_client_raises_rather_than_looping() -> None:
    client = FakeLLM([])
    with pytest.raises(LLMError, match="no scripted responses"):
        client.complete("p")


def test_response_rejects_negative_cost() -> None:
    with pytest.raises(ValueError):
        LLMResponse(text="{}", prompt_hash="abc", model="m", cache_hit=False, sim_cost=-0.5)


def test_unreachable_ollama_raises_a_typed_error() -> None:
    """
    A dead server must surface as LLMError so the classifier can fall back, not as a raw URLError
    that escapes the pipeline.
    """
    client = OllamaClient(endpoint="http://127.0.0.1:9/api/generate", timeout=1.0)
    with pytest.raises(LLMError, match="cannot reach Ollama"):
        client.complete("p")
