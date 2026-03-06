"""Tests de l'AgentRunner."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_workflow.engine.agent_runner import AgentRunner
from ai_workflow.managers.context_builder import ContextBuilder
from ai_workflow.managers.file_manager import FileManager
from ai_workflow.managers.memory_manager import MemoryManager
from ai_workflow.models.agent import AgentDefinition, AgentPhase, FilePermission


@pytest.fixture
def agent_runner(
    file_manager: FileManager,
    memory_manager: MemoryManager,
    context_builder: ContextBuilder,
) -> AgentRunner:
    return AgentRunner(file_manager, memory_manager, context_builder)


class TestAgentRunner:
    def test_run_global_agent(self, agent_runner: AgentRunner, brainstormer_agent: AgentDefinition):
        result = agent_runner.run(brainstormer_agent)
        assert result.agent_name == "brainstormer"
        assert result.status == "success"
        assert result.output_path is not None
        assert result.output_path.is_file()

    def test_run_with_us(self, agent_runner: AgentRunner, sample_agent: AgentDefinition, file_manager: FileManager):
        file_manager.write_md("us/US-001/definition.md", "# US-001\nTest story")
        result = agent_runner.run(sample_agent, us_id="US-001", iteration=1)
        assert result.status == "success"
        assert result.output_path is not None
        assert "US-001" in str(result.output_path)

    def test_run_generates_output_content(self, agent_runner: AgentRunner, sample_agent: AgentDefinition):
        result = agent_runner.run(sample_agent)
        assert len(result.output_content) > 0
        # Output should contain agent name
        assert "test-agent" in result.output_content.lower() or "Agent de Test" in result.output_content

    def test_run_with_nonexistent_agent_dir(
        self,
        file_manager: FileManager,
        memory_manager: MemoryManager,
        context_builder: ContextBuilder,
    ):
        """Agent sans dossier de définition → utilise output par défaut."""
        runner = AgentRunner(
            file_manager,
            memory_manager,
            context_builder,
            definitions_dir=Path("/tmp/nonexistent_agents"),
        )
        agent = AgentDefinition(
            name="phantom",
            display_name="Phantom Agent",
            role="N/A",
            phase=AgentPhase.CONSTRUCTION,
            permissions=[FilePermission.READ_MD],
        )
        result = runner.run(agent)
        assert result.status == "success"
        assert "Phantom Agent" in result.output_content
