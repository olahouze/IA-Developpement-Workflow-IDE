"""Tests du ContextBuilder."""

from __future__ import annotations

from ai_workflow.managers.context_builder import ContextBuilder
from ai_workflow.models.agent import AgentDefinition


class TestContextBuilder:
    def test_build_basic(self, context_builder: ContextBuilder, sample_agent: AgentDefinition):
        ctx = context_builder.build(sample_agent)
        assert ctx.agent is sample_agent
        assert ctx.iteration == 1
        assert ctx.us_definition == ""
        assert isinstance(ctx.profile_content, str)

    def test_build_with_us(
        self, context_builder: ContextBuilder, sample_agent: AgentDefinition, file_manager
    ):
        # Créer une définition d'US
        file_manager.write_md("us/US-001/definition.md", "# US-001\n\nDéfinition test")
        ctx = context_builder.build(sample_agent, us_id="US-001")
        assert "US-001" in ctx.us_definition

    def test_build_with_previous_reports(
        self, context_builder: ContextBuilder, sample_agent: AgentDefinition, file_manager
    ):
        file_manager.write_us_report("US-001", "developpeur", 1, "# Rapport Dev iter1")
        ctx = context_builder.build(sample_agent, us_id="US-001")
        assert len(ctx.previous_reports) == 1
        assert "Rapport Dev" in ctx.previous_reports[0]

    def test_build_includes_skills(
        self, context_builder: ContextBuilder, sample_agent: AgentDefinition, skill_manager
    ):
        skill_manager.write_skill("test-skill", "# Test Skill Content")
        ctx = context_builder.build(sample_agent)
        assert "test-skill" in ctx.skills

    def test_build_includes_memory(
        self, context_builder: ContextBuilder, sample_agent: AgentDefinition, memory_manager
    ):
        memory_manager.add_discovery("cartographe", "global", "Uses FastAPI")
        ctx = context_builder.build(sample_agent)
        assert len(ctx.memory_entries) == 1
        assert "Uses FastAPI" in ctx.memory_entries[0]
