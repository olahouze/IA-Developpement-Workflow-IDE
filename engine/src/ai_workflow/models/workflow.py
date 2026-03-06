"""Modèles de données pour les workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class WorkflowType(StrEnum):
    VIERGE = "vierge"
    EXISTANT = "existant"
    FEATURE = "feature"


class USStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    ESCALATED = "escalated"
    SKIPPED = "skipped"


@dataclass
class UserStory:
    """Une User Story avec ses métadonnées."""

    id: str
    name: str
    description: str
    files_impacted: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    batch: str = ""
    status: USStatus = USStatus.PENDING
    current_iteration: int = 0
    max_iterations: int = 4


@dataclass
class Batch:
    """Un batch d'US exécutables en parallèle (sans conflit fichiers)."""

    id: str
    stories: list[UserStory] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(us.status == USStatus.PASSED for us in self.stories)


@dataclass
class TransitionDef:
    """Définition d'une transition dans la state machine."""

    trigger: str
    source: str
    dest: str
    conditions: list[str] = field(default_factory=list)


@dataclass
class ForkDef:
    """Définition d'un fork/join parallèle."""

    fork_state: str
    agents: list[str]
    join_state: str


@dataclass
class WorkflowDefinition:
    """Définition complète d'un workflow chargée depuis YAML."""

    name: str
    type: WorkflowType
    description: str = ""
    states: list[str] = field(default_factory=list)
    initial_state: str = "init"
    transitions: list[TransitionDef] = field(default_factory=list)
    forks: list[ForkDef] = field(default_factory=list)
    agent_mapping: dict[str, str] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """État courant d'un workflow en exécution."""

    workflow_name: str
    current_state: str = "init"
    completed_states: list[str] = field(default_factory=list)
    batches: list[Batch] = field(default_factory=list)
    current_batch_index: int = 0
    current_us_id: str | None = None
    current_iteration: int = 0
    agent_results: dict[str, list[dict]] = field(default_factory=dict)
    is_complete: bool = False

    def to_dict(self) -> dict:
        """Sérialise l'état pour persistance JSON."""
        return {
            "workflow_name": self.workflow_name,
            "current_state": self.current_state,
            "completed_states": self.completed_states,
            "current_batch_index": self.current_batch_index,
            "current_us_id": self.current_us_id,
            "current_iteration": self.current_iteration,
            "is_complete": self.is_complete,
            "batches": [
                {
                    "id": b.id,
                    "stories": [
                        {
                            "id": us.id,
                            "name": us.name,
                            "status": us.status.value,
                            "current_iteration": us.current_iteration,
                        }
                        for us in b.stories
                    ],
                }
                for b in self.batches
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> WorkflowState:
        """Désérialise l'état depuis JSON."""
        batches = []
        for bd in data.get("batches", []):
            stories = [
                UserStory(
                    id=sd["id"],
                    name=sd["name"],
                    description="",
                    status=USStatus(sd["status"]),
                    current_iteration=sd["current_iteration"],
                )
                for sd in bd.get("stories", [])
            ]
            batches.append(Batch(id=bd["id"], stories=stories))

        return cls(
            workflow_name=data["workflow_name"],
            current_state=data.get("current_state", "init"),
            completed_states=data.get("completed_states", []),
            batches=batches,
            current_batch_index=data.get("current_batch_index", 0),
            current_us_id=data.get("current_us_id"),
            current_iteration=data.get("current_iteration", 0),
            is_complete=data.get("is_complete", False),
        )
