"""Validation de configuration via Pydantic."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class VerdictConfig(BaseModel):
    max_fail_iterations: int = 4
    blocking_analyzers: list[str] = Field(default_factory=lambda: ["analyseur-secu", "analyseur-perf"])
    non_blocking_analyzers: list[str] = Field(default_factory=lambda: ["analyseur-bp"])


class MagazinierConfig(BaseModel):
    sources: list[str] = Field(default_factory=list)
    temp_dir: str = ".ai-workflow/.tmp-magazinier"


class CartographeConfig(BaseModel):
    rescan_threshold: int = 10


class ProfileConfig(BaseModel):
    max_lines: int = 500
    filename: str = "profil_projet.md"


class AppConfig(BaseModel):
    workflow_dir: str = ".ai-workflow"
    directories: list[str] = Field(
        default_factory=lambda: ["skills", "instructions", "reports", "us", "docs"]
    )
    profile: ProfileConfig = Field(default_factory=ProfileConfig)
    workflows: dict[str, str] = Field(default_factory=dict)
    verdict: VerdictConfig = Field(default_factory=VerdictConfig)
    magazinier: MagazinierConfig = Field(default_factory=MagazinierConfig)
    cartographe: CartographeConfig = Field(default_factory=CartographeConfig)
    state_file: str = "state.json"


def load_config(config_path: Path | None = None) -> AppConfig:
    """Charge la config depuis un YAML ou utilise les defaults."""
    defaults_path = Path(__file__).parent / "defaults.yaml"
    data: dict = {}

    if defaults_path.exists():
        with open(defaults_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    if config_path and config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            override = yaml.safe_load(f) or {}
            data.update(override)

    return AppConfig(**data)
