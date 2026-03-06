"""Modèles de données pour les agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class AgentPhase(StrEnum):
    CONCEPTION = "conception"
    ORCHESTRATION = "orchestration"
    APPROVISIONNEMENT = "approvisionnement"
    CONSTRUCTION = "construction"
    ANALYSE = "analyse"
    INTEGRATION = "integration"
    FINALISATION = "finalisation"
    TRANSVERSAL = "transversal"


class FilePermission(StrEnum):
    READ_MD = "read_md"
    CREATE_MD = "create_md"
    ADD_CONFIG = "add_config"
    UPDATE_CONFIG = "update_config"
    MODIFY_CODE = "modify_code"


@dataclass
class AgentDefinition:
    """Définition statique d'un agent chargée depuis definition.yaml."""

    name: str
    display_name: str
    role: str
    phase: AgentPhase
    permissions: list[FilePermission]
    optional: bool = False
    interactive: bool = False
    instructions_path: Path | None = None
    output_template_path: Path | None = None
    dependencies: list[str] = field(default_factory=list)


@dataclass
class AgentContext:
    """Contexte complet fourni à un agent pour son exécution."""

    agent: AgentDefinition
    profile_content: str = ""
    skills: dict[str, str] = field(default_factory=dict)
    memory_entries: list[str] = field(default_factory=list)
    previous_reports: list[str] = field(default_factory=list)
    us_definition: str = ""
    iteration: int = 1


@dataclass
class AgentResult:
    """Résultat de l'exécution d'un agent."""

    agent_name: str
    output_path: Path | None = None
    output_content: str = ""
    status: str = "success"
    discoveries_for_memory: list[str] = field(default_factory=list)
    verdict: str | None = None  # PASS / FAIL (analyseurs uniquement)
    error: str | None = None
