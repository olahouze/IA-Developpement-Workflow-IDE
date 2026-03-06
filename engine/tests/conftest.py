"""Fixtures partagées pour les tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_workflow.config.schema import AppConfig, load_config
from ai_workflow.managers.context_builder import ContextBuilder
from ai_workflow.managers.file_manager import FileManager
from ai_workflow.managers.memory_manager import MemoryManager
from ai_workflow.managers.skill_manager import SkillManager
from ai_workflow.models.agent import AgentDefinition, AgentPhase, FilePermission
from ai_workflow.models.profile import ProjectProfile


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Crée un répertoire projet temporaire."""
    return tmp_path / "test-project"


@pytest.fixture
def config() -> AppConfig:
    """Config par défaut."""
    return load_config()


@pytest.fixture
def file_manager(tmp_project: Path, config: AppConfig) -> FileManager:
    """FileManager initialisé avec structure créée."""
    tmp_project.mkdir(parents=True, exist_ok=True)
    fm = FileManager(tmp_project, config)
    fm.init_structure()
    return fm


@pytest.fixture
def memory_manager(tmp_project: Path, config: AppConfig, file_manager: FileManager) -> MemoryManager:
    """MemoryManager prêt à l'emploi."""
    return MemoryManager(tmp_project, config)


@pytest.fixture
def profile() -> ProjectProfile:
    """Profil projet de test."""
    return ProjectProfile(
        project_name="test-project",
        project_type="api",
        description="Un projet de test",
        language="Python",
        framework="FastAPI",
    )


@pytest.fixture
def skill_manager(file_manager: FileManager, profile: ProjectProfile) -> SkillManager:
    """SkillManager prêt à l'emploi."""
    return SkillManager(file_manager, profile)


@pytest.fixture
def context_builder(
    file_manager: FileManager,
    memory_manager: MemoryManager,
    skill_manager: SkillManager,
) -> ContextBuilder:
    """ContextBuilder prêt à l'emploi."""
    return ContextBuilder(file_manager, memory_manager, skill_manager)


@pytest.fixture
def sample_agent() -> AgentDefinition:
    """Définition d'agent de test."""
    return AgentDefinition(
        name="test-agent",
        display_name="Agent de Test",
        role="Teste les fonctionnalités",
        phase=AgentPhase.CONSTRUCTION,
        permissions=[FilePermission.READ_MD, FilePermission.CREATE_MD],
        optional=False,
        interactive=False,
        dependencies=[],
    )


@pytest.fixture
def brainstormer_agent() -> AgentDefinition:
    """Définition du brainstormer."""
    return AgentDefinition(
        name="brainstormer",
        display_name="Brainstormer",
        role="Animation de brainstorming structuré",
        phase=AgentPhase.CONCEPTION,
        permissions=[FilePermission.READ_MD, FilePermission.CREATE_MD],
        optional=False,
        interactive=True,
        dependencies=[],
    )
