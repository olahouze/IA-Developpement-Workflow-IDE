"""Tests du WorkflowEngine."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_workflow.config.schema import AppConfig
from ai_workflow.engine.workflow_engine import WorkflowEngine
from ai_workflow.managers.file_manager import FileManager
from ai_workflow.models.workflow import WorkflowType


class TestLoadWorkflow:
    def test_load_vierge(self, tmp_project: Path, config: AppConfig):
        tmp_project.mkdir(parents=True, exist_ok=True)
        engine = WorkflowEngine(tmp_project, config)
        wf = engine.load_workflow(WorkflowType.VIERGE)
        assert wf.name == "projet-vierge"
        assert len(wf.states) > 0
        assert wf.initial_state == "init"

    def test_load_existant(self, tmp_project: Path, config: AppConfig):
        tmp_project.mkdir(parents=True, exist_ok=True)
        engine = WorkflowEngine(tmp_project, config)
        wf = engine.load_workflow(WorkflowType.EXISTANT)
        assert "existant" in wf.name.lower() or wf.type == WorkflowType.EXISTANT

    def test_load_feature(self, tmp_project: Path, config: AppConfig):
        tmp_project.mkdir(parents=True, exist_ok=True)
        engine = WorkflowEngine(tmp_project, config)
        wf = engine.load_workflow(WorkflowType.FEATURE)
        assert wf.type == WorkflowType.FEATURE

    def test_load_nonexistent_raises(self, tmp_project: Path):
        tmp_project.mkdir(parents=True, exist_ok=True)
        config = AppConfig(workflows={"vierge": "nonexistent.yaml"})
        engine = WorkflowEngine(tmp_project, config)
        with pytest.raises(FileNotFoundError):
            engine.load_workflow(WorkflowType.VIERGE)


class TestInitStateMachine:
    def test_init_creates_state(self, tmp_project: Path, config: AppConfig):
        tmp_project.mkdir(parents=True, exist_ok=True)
        engine = WorkflowEngine(tmp_project, config)
        engine.load_workflow(WorkflowType.VIERGE)
        engine.init_state_machine()
        assert engine.workflow_state is not None
        assert engine.workflow_state.current_state == "init"
        assert engine.workflow_state.is_complete is False

    def test_init_without_load_raises(self, tmp_project: Path, config: AppConfig):
        tmp_project.mkdir(parents=True, exist_ok=True)
        engine = WorkflowEngine(tmp_project, config)
        with pytest.raises(RuntimeError):
            engine.init_state_machine()


class TestSaveAndResume:
    def test_save_state(self, tmp_project: Path, config: AppConfig):
        tmp_project.mkdir(parents=True, exist_ok=True)
        fm = FileManager(tmp_project, config)
        fm.init_structure()

        engine = WorkflowEngine(tmp_project, config)
        engine.load_workflow(WorkflowType.VIERGE)
        engine.init_state_machine()
        engine.save()

        loaded = fm.load_state()
        assert loaded is not None
        assert loaded["workflow_name"] == "projet-vierge"

    def test_resume_from_saved(self, tmp_project: Path, config: AppConfig):
        tmp_project.mkdir(parents=True, exist_ok=True)
        fm = FileManager(tmp_project, config)
        fm.init_structure()

        # Première exécution : sauvegarder
        engine1 = WorkflowEngine(tmp_project, config)
        engine1.load_workflow(WorkflowType.VIERGE)
        engine1.init_state_machine()
        engine1.workflow_state.current_state = "brainstorm"
        engine1.workflow_state.completed_states = ["init"]
        engine1.save()

        # Deuxième exécution : reprendre
        engine2 = WorkflowEngine(tmp_project, config)
        engine2.load_workflow(WorkflowType.VIERGE)
        engine2.resume_or_start()
        assert engine2.workflow_state.current_state == "brainstorm"
        assert "init" in engine2.workflow_state.completed_states


class TestFindNextState:
    def test_find_next(self, tmp_project: Path, config: AppConfig):
        tmp_project.mkdir(parents=True, exist_ok=True)
        engine = WorkflowEngine(tmp_project, config)
        engine.load_workflow(WorkflowType.VIERGE)
        engine.init_state_machine()

        states = engine._workflow_def.states
        if len(states) >= 2:
            next_state = engine._find_next_state(states[0])
            assert next_state == states[1]

    def test_find_next_last_state(self, tmp_project: Path, config: AppConfig):
        tmp_project.mkdir(parents=True, exist_ok=True)
        engine = WorkflowEngine(tmp_project, config)
        engine.load_workflow(WorkflowType.VIERGE)
        engine.init_state_machine()

        states = engine._workflow_def.states
        last = states[-1]
        assert engine._find_next_state(last) is None
