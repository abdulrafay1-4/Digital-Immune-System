"""Run identity, stamped into every message and into results/<run_id>/."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RunManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    seed: int
    config_hash: str
    config: dict[str, Any] = Field(default_factory=dict)
    git_commit: str | None = None
    notes: str = ""

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")


def config_hash(config: dict[str, Any]) -> str:
    """Stable hash of config for reproducibility stamps."""
    blob = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def load_yaml_config(path: Path) -> dict[str, Any]:
    import yaml

    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"config root must be a mapping: {path}")
    return data


def new_manifest(
    run_id: str,
    seed: int,
    config: dict[str, Any],
    *,
    git_commit: str | None = None,
    notes: str = "",
) -> RunManifest:
    return RunManifest(
        run_id=run_id,
        seed=seed,
        config_hash=config_hash(config),
        config=config,
        git_commit=git_commit,
        notes=notes,
    )
