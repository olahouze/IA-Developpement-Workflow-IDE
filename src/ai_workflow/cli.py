"""CLI principale — ai-workflow (init, run, status, agents)."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_workflow.config.schema import load_config
from ai_workflow.engine.workflow_engine import WorkflowEngine
from ai_workflow.managers.file_manager import FileManager
from ai_workflow.managers.memory_manager import MemoryManager
from ai_workflow.models.workflow import WorkflowType

app = typer.App = typer.Typer(
    name="ai-workflow",
    help="Framework d'orchestration d'agents IA pour workflows de développement structurés.",
    no_args_is_help=True,
)
console = Console()


def _get_project_root() -> Path:
    return Path.cwd()


def _get_config(project_root: Path):
    config_path = project_root / ".ai-workflow" / "config.yaml"
    return load_config(config_path if config_path.exists() else None)


@app.command()
def init(
    workflow_type: str = typer.Option(
        "vierge",
        "--type", "-t",
        help="Type de workflow : vierge, existant, feature",
    ),
    project_name: str = typer.Option(
        "",
        "--name", "-n",
        help="Nom du projet (défaut : nom du dossier courant)",
    ),
) -> None:
    """Initialise la structure .ai-workflow/ dans le projet courant."""
    project_root = _get_project_root()
    config = _get_config(project_root)
    fm = FileManager(project_root, config)

    if fm.exists():
        console.print("[yellow]⚠ .ai-workflow/ existe déjà.[/yellow]")
        overwrite = typer.confirm("Réinitialiser ?", default=False)
        if not overwrite:
            raise typer.Abort()

    # Créer la structure
    dirs = fm.init_structure()
    console.print(f"[green]✓ Structure créée ({len(dirs)} dossiers)[/green]")
    for d in dirs:
        console.print(f"  {d.relative_to(project_root)}")

    # Créer le profil projet initial
    mm = MemoryManager(project_root, config)
    name = project_name or project_root.name
    mm.profile.project_name = name
    mm.save_profile()
    console.print(f"[green]✓ Profil projet créé : {name}[/green]")

    # Sauvegarder le type de workflow choisi
    state = {
        "workflow_name": workflow_type,
        "current_state": "init",
        "completed_states": [],
        "batches": [],
        "current_batch_index": 0,
        "current_us_id": None,
        "current_iteration": 0,
        "is_complete": False,
    }
    fm.save_state(state)
    console.print(f"[green]✓ Workflow '{workflow_type}' configuré[/green]")


@app.command()
def run(
    workflow_type: str = typer.Option(
        "",
        "--type", "-t",
        help="Type de workflow (détecté automatiquement si déjà initialisé)",
    ),
) -> None:
    """Lance ou reprend l'exécution du workflow."""
    project_root = _get_project_root()
    config = _get_config(project_root)
    fm = FileManager(project_root, config)

    if not fm.exists():
        console.print("[red]✗ Projet non initialisé. Lancez 'ai-workflow init' d'abord.[/red]")
        raise typer.Exit(1)

    # Déterminer le type de workflow
    saved_state = fm.load_state()
    if saved_state and not workflow_type:
        workflow_type = saved_state.get("workflow_name", "vierge")
    elif not workflow_type:
        workflow_type = "vierge"

    try:
        wf_type = WorkflowType(workflow_type)
    except ValueError:
        console.print(f"[red]✗ Type de workflow inconnu : {workflow_type}[/red]")
        raise typer.Exit(1)

    engine = WorkflowEngine(project_root, config)
    engine.load_workflow(wf_type)
    engine.resume_or_start()
    engine.run()


@app.command()
def status() -> None:
    """Affiche l'état du workflow en cours."""
    project_root = _get_project_root()
    config = _get_config(project_root)
    fm = FileManager(project_root, config)

    if not fm.exists():
        console.print("[red]✗ Projet non initialisé.[/red]")
        raise typer.Exit(1)

    saved = fm.load_state()
    if not saved:
        console.print("[yellow]Aucun workflow en cours.[/yellow]")
        return

    table = Table(title="État du Workflow")
    table.add_column("Propriété", style="cyan")
    table.add_column("Valeur", style="white")

    table.add_row("Workflow", saved.get("workflow_name", "?"))
    table.add_row("État courant", saved.get("current_state", "?"))
    table.add_row("Terminé", "✓" if saved.get("is_complete") else "✗")

    completed = saved.get("completed_states", [])
    table.add_row("États complétés", str(len(completed)))

    batches = saved.get("batches", [])
    if batches:
        total_us = sum(len(b.get("stories", [])) for b in batches)
        passed = sum(
            1
            for b in batches
            for s in b.get("stories", [])
            if s.get("status") == "passed"
        )
        table.add_row("US total", str(total_us))
        table.add_row("US validées", str(passed))

    console.print(table)

    # Afficher les états complétés
    if completed:
        console.print("\n[dim]États complétés :[/dim]")
        for state_name in completed:
            console.print(f"  [green]✓[/green] {state_name}")


@app.command()
def agents() -> None:
    """Liste les 17 agents disponibles."""
    from ai_workflow.agents.registry import AgentRegistry

    registry = AgentRegistry()
    all_agents = registry.get_all()

    table = Table(title="Agents Disponibles")
    table.add_column("#", style="dim")
    table.add_column("Nom", style="cyan")
    table.add_column("Rôle", style="white", max_width=60)
    table.add_column("Phase", style="yellow")
    table.add_column("Droits", style="green")
    table.add_column("Opt.", style="dim")

    for i, (name, agent) in enumerate(sorted(all_agents.items()), 1):
        perms = ", ".join(p.value for p in agent.permissions)
        opt = "✓" if agent.optional else ""
        table.add_row(
            str(i),
            agent.display_name,
            agent.role[:60],
            agent.phase.value,
            perms,
            opt,
        )

    console.print(table)


if __name__ == "__main__":
    app()
