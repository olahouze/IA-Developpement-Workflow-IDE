"""Tests du registre des agents."""

from __future__ import annotations

from ai_workflow.agents.registry import AgentRegistry
from ai_workflow.models.agent import AgentPhase


class TestAgentRegistry:
    def test_load_all_17_agents(self):
        registry = AgentRegistry()
        agents = registry.get_all()
        assert len(agents) == 17

    def test_list_names(self):
        registry = AgentRegistry()
        names = registry.list_names()
        assert "brainstormer" in names
        assert "developpeur" in names
        assert "testeur" in names
        assert "documentaliste" in names
        assert len(names) == 17

    def test_get_known_agent(self):
        registry = AgentRegistry()
        agent = registry.get("brainstormer")
        assert agent is not None
        assert agent.display_name == "Brainstormer"
        assert agent.phase == AgentPhase.CONCEPTION

    def test_get_unknown_agent(self):
        registry = AgentRegistry()
        assert registry.get("nonexistent") is None

    def test_get_by_phase(self):
        registry = AgentRegistry()
        conception = registry.get_by_phase(AgentPhase.CONCEPTION)
        assert len(conception) >= 1
        assert all(a.phase == AgentPhase.CONCEPTION for a in conception)

    def test_all_agents_have_required_fields(self):
        registry = AgentRegistry()
        for name, agent in registry.get_all().items():
            assert agent.name, f"{name}: name manquant"
            assert agent.display_name, f"{name}: display_name manquant"
            assert agent.role, f"{name}: role manquant"
            assert isinstance(agent.phase, AgentPhase), f"{name}: phase invalide"
            assert len(agent.permissions) > 0, f"{name}: permissions manquantes"

    def test_all_agents_have_instructions(self):
        registry = AgentRegistry()
        for name, agent in registry.get_all().items():
            assert agent.instructions_path is not None, f"{name}: instructions_path manquant"
            assert agent.instructions_path.is_file(), f"{name}: instructions.md introuvable"

    def test_all_agents_have_output_template(self):
        registry = AgentRegistry()
        for name, agent in registry.get_all().items():
            assert agent.output_template_path is not None, f"{name}: output_template_path manquant"
            assert agent.output_template_path.is_file(), f"{name}: output_template.md introuvable"

    def test_expected_agents_present(self):
        registry = AgentRegistry()
        expected = [
            "brainstormer", "arch-produit", "arch-metier", "arch-gui",
            "arch-technique", "cartographe", "orchestrateur", "magazinier",
            "developpeur", "testeur", "analyseur-perf", "analyseur-secu",
            "analyseur-bp", "agent-memoire", "integrateur", "fixeur-integration",
            "documentaliste",
        ]
        names = registry.list_names()
        for expected_name in expected:
            assert expected_name in names, f"Agent manquant : {expected_name}"

    def test_lazy_loading(self):
        """Vérifie que les agents ne sont chargés qu'au premier accès."""
        registry = AgentRegistry()
        assert registry._loaded is False
        registry.list_names()
        assert registry._loaded is True
