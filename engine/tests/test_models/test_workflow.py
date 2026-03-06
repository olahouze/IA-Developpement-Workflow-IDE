"""Tests des modèles workflow."""

from ai_workflow.models.workflow import (
    Batch,
    ForkDef,
    TransitionDef,
    UserStory,
    USStatus,
    WorkflowDefinition,
    WorkflowState,
    WorkflowType,
)


class TestWorkflowType:
    def test_types(self):
        assert WorkflowType.VIERGE.value == "vierge"
        assert WorkflowType.EXISTANT.value == "existant"
        assert WorkflowType.FEATURE.value == "feature"


class TestUSStatus:
    def test_all_statuses(self):
        expected = {"pending", "in_progress", "passed", "failed", "escalated", "skipped"}
        assert {s.value for s in USStatus} == expected


class TestUserStory:
    def test_default_values(self):
        us = UserStory(id="US-001", name="Test", description="A test story")
        assert us.status == USStatus.PENDING
        assert us.current_iteration == 0
        assert us.max_iterations == 4
        assert us.files_impacted == []
        assert us.dependencies == []


class TestBatch:
    def test_all_passed_empty(self):
        batch = Batch(id="B1")
        assert batch.all_passed is True

    def test_all_passed_true(self):
        batch = Batch(
            id="B1",
            stories=[
                UserStory(id="US-1", name="A", description="", status=USStatus.PASSED),
                UserStory(id="US-2", name="B", description="", status=USStatus.PASSED),
            ],
        )
        assert batch.all_passed is True

    def test_all_passed_false(self):
        batch = Batch(
            id="B1",
            stories=[
                UserStory(id="US-1", name="A", description="", status=USStatus.PASSED),
                UserStory(id="US-2", name="B", description="", status=USStatus.PENDING),
            ],
        )
        assert batch.all_passed is False


class TestTransitionDef:
    def test_defaults(self):
        t = TransitionDef(trigger="next", source="A", dest="B")
        assert t.conditions == []


class TestForkDef:
    def test_basic(self):
        f = ForkDef(fork_state="fork_1", agents=["a", "b"], join_state="join_1")
        assert len(f.agents) == 2


class TestWorkflowDefinition:
    def test_defaults(self):
        wf = WorkflowDefinition(name="test", type=WorkflowType.VIERGE)
        assert wf.states == []
        assert wf.initial_state == "init"
        assert wf.transitions == []
        assert wf.forks == []
        assert wf.agent_mapping == {}


class TestWorkflowState:
    def test_serialization_roundtrip(self):
        state = WorkflowState(
            workflow_name="test",
            current_state="brainstorm",
            completed_states=["init"],
            batches=[
                Batch(
                    id="B1",
                    stories=[
                        UserStory(
                            id="US-1", name="Story 1", description="desc",
                            status=USStatus.PASSED, current_iteration=2,
                        ),
                        UserStory(
                            id="US-2", name="Story 2", description="desc",
                            status=USStatus.PENDING,
                        ),
                    ],
                )
            ],
            current_batch_index=0,
            current_us_id="US-1",
            current_iteration=2,
            is_complete=False,
        )

        data = state.to_dict()
        restored = WorkflowState.from_dict(data)

        assert restored.workflow_name == "test"
        assert restored.current_state == "brainstorm"
        assert restored.completed_states == ["init"]
        assert len(restored.batches) == 1
        assert len(restored.batches[0].stories) == 2
        assert restored.batches[0].stories[0].status == USStatus.PASSED
        assert restored.batches[0].stories[0].current_iteration == 2
        assert restored.batches[0].stories[1].status == USStatus.PENDING
        assert restored.current_us_id == "US-1"
        assert restored.is_complete is False

    def test_empty_state(self):
        state = WorkflowState(workflow_name="empty")
        data = state.to_dict()
        restored = WorkflowState.from_dict(data)
        assert restored.workflow_name == "empty"
        assert restored.batches == []
        assert restored.is_complete is False
