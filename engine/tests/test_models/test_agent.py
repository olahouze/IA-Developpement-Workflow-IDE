"""Tests des modèles agent."""

from ai_workflow.models.agent import AgentDefinition, AgentPhase, FilePermission


class TestAgentPhase:
    def test_all_phases_exist(self):
        expected = {
            "conception", "orchestration", "approvisionnement",
            "construction", "analyse", "integration",
            "finalisation", "transversal",
        }
        assert {p.value for p in AgentPhase} == expected

    def test_str_enum(self):
        assert str(AgentPhase.CONCEPTION) == "conception"
        assert AgentPhase.CONCEPTION.value == "conception"


class TestFilePermission:
    def test_all_permissions_exist(self):
        expected = {"read_md", "create_md", "add_config", "update_config", "modify_code"}
        assert {p.value for p in FilePermission} == expected


class TestAgentDefinition:
    def test_create_minimal(self):
        agent = AgentDefinition(
            name="test",
            display_name="Test Agent",
            role="Testing",
            phase=AgentPhase.CONSTRUCTION,
            permissions=[FilePermission.READ_MD],
        )
        assert agent.name == "test"
        assert agent.optional is False
        assert agent.interactive is False
        assert agent.dependencies == []

    def test_create_full(self):
        agent = AgentDefinition(
            name="dev",
            display_name="Développeur",
            role="Implémente le code",
            phase=AgentPhase.CONSTRUCTION,
            permissions=[FilePermission.READ_MD, FilePermission.MODIFY_CODE],
            optional=False,
            interactive=False,
            dependencies=["brainstormer", "arch-technique"],
        )
        assert len(agent.permissions) == 2
        assert len(agent.dependencies) == 2
        assert agent.instructions_path is None
        assert agent.output_template_path is None
