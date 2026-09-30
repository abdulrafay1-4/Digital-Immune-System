"""LLM access for the reasoning plane: deterministic, cached, and sim-time charged."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_ENDPOINT = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"

DEFAULT_SIM_COST = 1.5


class LLMError(RuntimeError):
    """Transport or protocol failure talking to the model."""


class LLMResponse(BaseModel):
    """One completion, plus everything the audit trail needs about it."""

    model_config = ConfigDict(extra="forbid")

    text: str
    prompt_hash: str
    model: str
    cache_hit: bool
    sim_cost: float = Field(ge=0.0)

    def as_json(self) -> dict[str, Any]:
        """Parse the completion as a JSON object."""
        try:
            parsed = json.loads(self.text)
        except json.JSONDecodeError as exc:
            raise LLMError(f"model did not return valid JSON: {exc}") from exc
        if not isinstance(parsed, dict):
            raise LLMError(f"expected a JSON object, got {type(parsed).__name__}")
        return parsed


def prompt_hash(prompt: str, model: str) -> str:
    """Cache key. Includes the model so switching models cannot serve a stale hit."""
    blob = f"{model}\x00{prompt}".encode()
    return hashlib.sha256(blob).hexdigest()[:16]


class LLMClient(Protocol):
    """Minimal transport contract."""

    model: str

    def complete(self, prompt: str) -> str: ...


class FakeLLM:
    """Scripted client for tests and for the LLM-free ablation baseline."""

    def __init__(self, responses: list[str] | str, model: str = "fake") -> None:
        self._responses = [responses] if isinstance(responses, str) else list(responses)
        self._index = 0
        self.model = model
        self.calls: list[str] = []

    def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        if not self._responses:
            raise LLMError("FakeLLM has no scripted responses left")
        idx = min(self._index, len(self._responses) - 1)
        self._index += 1
        return self._responses[idx]


class OllamaClient:
    """Local Ollama over HTTP."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        endpoint: str = DEFAULT_ENDPOINT,
        seed: int = 0,
        timeout: float = 60.0,
    ) -> None:
        self.model = model
        self.endpoint = endpoint
        self.seed = seed
        self.timeout = timeout

    def complete(self, prompt: str) -> str:
        import urllib.error
        import urllib.request

        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {"temperature": 0, "seed": self.seed},
            }
        ).encode()

        request = urllib.request.Request(
            self.endpoint, data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode())
        except urllib.error.URLError as exc:
            raise LLMError(f"cannot reach Ollama at {self.endpoint}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise LLMError(f"Ollama returned non-JSON envelope: {exc}") from exc

        text = body.get("response")
        if not isinstance(text, str):
            raise LLMError(f"Ollama envelope has no 'response' string: {body!r}")
        return text


class CachedLLM:
    """Wraps a client with a prompt-hash cache and a sim-time charge."""

    def __init__(
        self,
        client: LLMClient,
        *,
        sim_cost: float = DEFAULT_SIM_COST,
        charge_on_cache_hit: bool = False,
    ) -> None:
        """
        `charge_on_cache_hit` defaults to False: a cache hit did not really call the model, so
        charging it would inflate latency during sweeps.
        """
        if sim_cost < 0:
            raise ValueError("sim_cost must be >= 0")
        self.client = client
        self.sim_cost = float(sim_cost)
        self.charge_on_cache_hit = charge_on_cache_hit
        self._cache: dict[str, str] = {}
        self.hits = 0
        self.misses = 0
        self.total_sim_cost = 0.0

    def complete(self, prompt: str) -> LLMResponse:
        key = prompt_hash(prompt, self.client.model)
        cached = key in self._cache

        if cached:
            self.hits += 1
            text = self._cache[key]
        else:
            self.misses += 1
            text = self.client.complete(prompt)
            self._cache[key] = text

        cost = self.sim_cost if (not cached or self.charge_on_cache_hit) else 0.0
        self.total_sim_cost += cost

        return LLMResponse(
            text=text,
            prompt_hash=key,
            model=self.client.model,
            cache_hit=cached,
            sim_cost=cost,
        )

    @property
    def calls(self) -> int:
        return self.hits + self.misses

    def clear(self) -> None:
        self._cache.clear()
