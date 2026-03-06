"""WorkflowEngine — State machine avec orchestration des agents."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import yaml
from rich.console import Console
from transitions import Machine

from ai_workflow.config.schema import AppConfig
from ai_workflow.engine.agent_runner import AgentRunner
from ai_workflow.engine.fork_join import fork_join
from ai_workflow.engine.verdict import build_verdict, get_next_action
from ai_workflow.managers.context_builder import ContextBuilder
from ai_workflow.managers.file_manager import FileManager
from ai_workflow.managers.memory_manager import MemoryManager
from ai_workflow.managers.skill_manager import SkillManager
from ai_workflow.models.agent import AgentResult
from ai_workflow.models.workflow import (
    ForkDef,
    TransitionDef,
    UserStory,
    USStatus,
    WorkflowDefinition,
    WorkflowState,
    WorkflowType,
)

console = Console()


class WorkflowEngine:
    """Moteur principal : charge un workflow YAML, gère la state machine, orchestre les agents."""

    def __init__(self, project_root: Path, config: AppConfig):
        self.project_root = project_root
        self.config = config
        self.file_manager = FileManager(project_root, config)
        self.memory_manager = MemoryManager(project_root, config)
        self.skill_manager = SkillManager(self.file_manager, self.memory_manager.profile)
        self.context_builder = ContextBuilder(
            self.file_manager, self.memory_manager, self.skill_manager
        )
        self.agent_runner = AgentRunner(
            self.file_manager, self.memory_manager, self.context_builder
        )
        self.workflow_state: WorkflowState | None = None
        self._workflow_def: WorkflowDefinition | None = None
        self._machine: Machine | None = None
        self._agent_registry: dict | None = None

    def load_workflow(self, workflow_type: WorkflowType) -> WorkflowDefinition:
        """Charge une définition de workflow depuis YAML."""
        workflows_dir = Path(__file__).parent.parent / "workflows"
        workflow_file = self.config.workflows.get(workflow_type.value)
        if not workflow_file:
            workflow_file = f"workflow_{workflow_type.value}.yaml"

        workflow_path = workflows_dir / workflow_file
        if not workflow_path.is_file():
            raise FileNotFoundError(f"Workflow non trouvé : {workflow_path}")

        with open(workflow_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        transitions = [
            TransitionDef(**t) for t in data.get("transitions", [])
        ]
        forks = [ForkDef(**f) for f in data.get("forks", [])]

        self._workflow_def = WorkflowDefinition(
            name=data["name"],
            type=WorkflowType(data.get("type", workflow_type.value)),
            description=data.get("description", ""),
            states=data.get("states", []),
            initial_state=data.get("initial_state", "init"),
            transitions=transitions,
            forks=forks,
            agent_mapping=data.get("agent_mapping", {}),
        )
        return self._workflow_def

    def init_state_machine(self) -> None:
        """Initialise la state machine transitions à partir de la définition."""
        if not self._workflow_def:
            raise RuntimeError("Workflow non chargé. Appelez load_workflow() d'abord.")

        wf = self._workflow_def
        self.workflow_state = WorkflowState(workflow_name=wf.name, current_state=wf.initial_state)

        transitions_config = [
            {
                "trigger": t.trigger,
                "source": t.source,
                "dest": t.dest,
                "conditions": t.conditions if t.conditions else [],
            }
            for t in wf.transitions
        ]

        self._machine = Machine(
            states=wf.states,
            transitions=transitions_config,
            initial=wf.initial_state,
            auto_transitions=False,
            send_event=False,
        )

    def resume_or_start(self) -> None:
        """Reprend un workflow existant ou en démarre un nouveau."""
        saved = self.file_manager.load_state()
        if saved:
            self.workflow_state = WorkflowState.from_dict(saved)
            console.print(f"[green]Reprise du workflow à l'état : {self.workflow_state.current_state}[/green]")
        else:
            self.init_state_machine()
            console.print(f"[green]Nouveau workflow démarré : {self._workflow_def.name}[/green]")

    def save(self) -> None:
        """Sauvegarde l'état courant."""
        if self.workflow_state:
            self.file_manager.save_state(self.workflow_state.to_dict())
            self.memory_manager.save_profile()

    def run(self) -> None:
        """Exécute le workflow de bout en bout."""
        if not self._workflow_def or not self.workflow_state:
            raise RuntimeError("Workflow non initialisé.")

        wf = self._workflow_def
        console.print(f"\n[bold blue]═══ Workflow : {wf.name} ═══[/bold blue]\n")

        while not self.workflow_state.is_complete:
            current = self.workflow_state.current_state
            console.print(f"[cyan]→ État : {current}[/cyan]")

            # Vérifier si c'est un fork
            fork = self._find_fork(current)
            if fork:
                self._execute_fork(fork)
                self.workflow_state.completed_states.append(current)
                self._advance_to(fork.join_state)
                self.save()
                continue

            # Vérifier si c'est un état d'agent
            agent_name = wf.agent_mapping.get(current)
            if agent_name:
                self._execute_agent_state(agent_name, current)

            # Vérifier si c'est l'état des batches builders
            if current == "batch_builders":
                self._execute_batches()
                self.workflow_state.completed_states.append(current)
                self.save()
                continue

            # Avancer à l'état suivant
            self.workflow_state.completed_states.append(current)
            next_state = self._find_next_state(current)
            if next_state:
                self._advance_to(next_state)
            else:
                self.workflow_state.is_complete = True

            self.save()

        console.print("\n[bold green]✓ Workflow terminé ![/bold green]\n")
        self.memory_manager.save_profile()

    def _find_fork(self, state: str) -> ForkDef | None:
        """Trouve le fork correspondant à un état."""
        if not self._workflow_def:
            return None
        for fork in self._workflow_def.forks:
            if fork.fork_state == state:
                return fork
        return None

    def _execute_fork(self, fork: ForkDef) -> dict[str, AgentResult]:
        """Exécute un fork/join parallèle."""
        console.print(f"[yellow]  ⑂ Fork : {', '.join(fork.agents)}[/yellow]")

        tasks: dict[str, Callable[[], AgentResult]] = {}
        for agent_name in fork.agents:
            agent_def = self._get_agent_definition(agent_name)
            if agent_def:
                tasks[agent_name] = lambda a=agent_def: self.agent_runner.run(a)

        results = fork_join(tasks)

        for name, result in results.items():
            status = "✓" if result.status == "success" else "✗"
            console.print(f"[yellow]  {status} {name}[/yellow]")

        console.print("[yellow]  ⑃ Join complet[/yellow]")
        return results

    def _execute_agent_state(self, agent_name: str, state: str) -> AgentResult | None:
        """Exécute un agent pour un état donné."""
        agent_def = self._get_agent_definition(agent_name)
        if not agent_def:
            console.print(f"[red]  Agent inconnu : {agent_name}[/red]")
            return None

        console.print(f"[white]  ▸ Exécution : {agent_def.display_name}[/white]")
        result = self.agent_runner.run(
            agent_def,
            us_id=self.workflow_state.current_us_id if self.workflow_state else None,
            iteration=self.workflow_state.current_iteration if self.workflow_state else 1,
        )

        if result.output_path:
            console.print(f"[dim]    → {result.output_path}[/dim]")

        return result

    def _execute_batches(self) -> None:
        """Exécute les batches d'US : Dev → Testeur → [Analyseurs] → verdict."""
        if not self.workflow_state or not self.workflow_state.batches:
            console.print("[dim]  Aucun batch à exécuter[/dim]")
            return

        for batch_idx, batch in enumerate(self.workflow_state.batches):
            console.print(f"\n[bold magenta]  ── Batch {batch.id} ({len(batch.stories)} US) ──[/bold magenta]")

            for us in batch.stories:
                if us.status in (USStatus.PASSED, USStatus.SKIPPED):
                    continue

                self._execute_us(us)

    def _execute_us(self, us: UserStory) -> None:
        """Exécute une US complète avec boucle PASS/FAIL."""
        us.status = USStatus.IN_PROGRESS

        while us.current_iteration < us.max_iterations:
            us.current_iteration += 1
            self.workflow_state.current_us_id = us.id
            self.workflow_state.current_iteration = us.current_iteration

            console.print(
                f"\n[white]    US {us.id} — itération {us.current_iteration}[/white]"
            )

            # Dev
            dev_def = self._get_agent_definition("developpeur")
            if dev_def:
                console.print("    ▸ Développeur")
                self.agent_runner.run(dev_def, us_id=us.id, iteration=us.current_iteration)

            # Testeur
            test_def = self._get_agent_definition("testeur")
            if test_def:
                console.print("    ▸ Testeur")
                self.agent_runner.run(test_def, us_id=us.id, iteration=us.current_iteration)

            # Analyseurs en parallèle
            analyzer_results = self._run_analyzers(us.id, us.current_iteration)

            # Verdict
            verdict = build_verdict(analyzer_results, self.config)
            action = get_next_action(verdict, us.current_iteration, us.max_iterations)

            console.print(f"    Verdict : {verdict.overall_status} → {action}")

            if action == "continue":
                us.status = USStatus.PASSED
                console.print(f"[green]    ✓ US {us.id} validée[/green]")
                break
            elif action == "escalate":
                us.status = USStatus.ESCALATED
                console.print(f"[red]    ⚠ US {us.id} escaladée (≥{us.max_iterations} itérations)[/red]")
                # En mode non-interactif, on skip
                us.status = USStatus.SKIPPED
                break
            # action == "retry" → boucle continue

        if us.status == USStatus.IN_PROGRESS:
            us.status = USStatus.ESCALATED

    def _run_analyzers(self, us_id: str, iteration: int) -> dict[str, AgentResult]:
        """Exécute les 3 analyseurs en parallèle."""
        analyzer_names = (
            self.config.verdict.blocking_analyzers + self.config.verdict.non_blocking_analyzers
        )

        tasks: dict[str, Callable[[], AgentResult]] = {}
        for name in analyzer_names:
            agent_def = self._get_agent_definition(name)
            if agent_def:
                tasks[name] = lambda a=agent_def, u=us_id, i=iteration: self.agent_runner.run(
                    a, us_id=u, iteration=i
                )

        console.print(f"    ⑂ Analyseurs : {', '.join(analyzer_names)}")
        return fork_join(tasks)

    def _get_agent_definition(self, agent_name: str) -> object | None:
        """Charge la définition d'un agent depuis le registre."""
        # Import tardif pour éviter les imports circulaires
        from ai_workflow.agents.registry import AgentRegistry

        if self._agent_registry is None:
            self._agent_registry = AgentRegistry()

        return self._agent_registry.get(agent_name)

    def _find_next_state(self, current: str) -> str | None:
        """Trouve l'état suivant dans la liste séquentielle."""
        if not self._workflow_def:
            return None
        states = self._workflow_def.states
        try:
            idx = states.index(current)
            if idx + 1 < len(states):
                return states[idx + 1]
        except ValueError:
            pass
        return None

    def _advance_to(self, state: str) -> None:
        """Avance la state machine vers un état donné."""
        if self.workflow_state:
            self.workflow_state.current_state = state


def load_workflow_from_file(path: Path) -> dict:
    """Charge un fichier YAML de workflow."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
