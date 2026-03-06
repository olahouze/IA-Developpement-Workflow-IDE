"""Tests de chargement des workflows YAML."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ai_workflow.models.workflow import WorkflowType

WORKFLOWS_DIR = Path(__file__).parent.parent.parent / "src" / "ai_workflow" / "workflows"


class TestWorkflowYAMLFiles:
    @pytest.fixture(params=["workflow_projet_vierge.yaml", "workflow_projet_existant.yaml", "workflow_feature.yaml"])
    def workflow_data(self, request) -> dict:
        path = WORKFLOWS_DIR / request.param
        assert path.is_file(), f"Fichier absent : {path}"
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_has_required_keys(self, workflow_data: dict):
        assert "name" in workflow_data
        assert "type" in workflow_data
        assert "states" in workflow_data
        assert "transitions" in workflow_data

    def test_type_is_valid(self, workflow_data: dict):
        WorkflowType(workflow_data["type"])

    def test_states_not_empty(self, workflow_data: dict):
        assert len(workflow_data["states"]) > 0

    def test_transitions_reference_existing_states(self, workflow_data: dict):
        states = set(workflow_data["states"])
        for t in workflow_data["transitions"]:
            assert t["source"] in states, f"source '{t['source']}' not in states"
            assert t["dest"] in states, f"dest '{t['dest']}' not in states"

    def test_initial_state_in_states(self, workflow_data: dict):
        initial = workflow_data.get("initial_state", "init")
        assert initial in workflow_data["states"]

    def test_agent_mapping_states_exist(self, workflow_data: dict):
        states = set(workflow_data["states"])
        for state in workflow_data.get("agent_mapping", {}):
            assert state in states, f"agent_mapping state '{state}' not in states"

    def test_forks_reference_existing_states(self, workflow_data: dict):
        states = set(workflow_data["states"])
        for fork in workflow_data.get("forks", []):
            assert fork["fork_state"] in states
            assert fork["join_state"] in states


class TestWorkflowVierge:
    def test_has_brainstorm(self):
        path = WORKFLOWS_DIR / "workflow_projet_vierge.yaml"
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        agents = list(data.get("agent_mapping", {}).values())
        forks_agents = []
        for fork in data.get("forks", []):
            forks_agents.extend(fork.get("agents", []))
        all_agents = agents + forks_agents
        assert "brainstormer" in all_agents


class TestWorkflowFeature:
    def test_no_brainstorm(self):
        path = WORKFLOWS_DIR / "workflow_feature.yaml"
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        agents = list(data.get("agent_mapping", {}).values())
        forks_agents = []
        for fork in data.get("forks", []):
            forks_agents.extend(fork.get("agents", []))
        all_agents = agents + forks_agents
        assert "brainstormer" not in all_agents
