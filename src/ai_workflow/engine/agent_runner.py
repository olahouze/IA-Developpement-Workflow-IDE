"""Agent Runner — charge et exécute un agent avec son contexte."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ai_workflow.managers.context_builder import ContextBuilder
from ai_workflow.managers.file_manager import FileManager
from ai_workflow.managers.memory_manager import MemoryManager
from ai_workflow.models.agent import AgentContext, AgentDefinition, AgentResult


class AgentRunner:
    """Charge une définition agent, résout le contexte, rend le template, exécute."""

    def __init__(
        self,
        file_manager: FileManager,
        memory_manager: MemoryManager,
        context_builder: ContextBuilder,
        definitions_dir: Path | None = None,
    ):
        self.file_manager = file_manager
        self.memory_manager = memory_manager
        self.context_builder = context_builder
        self.definitions_dir = definitions_dir or (
            Path(__file__).parent.parent / "agents" / "definitions"
        )

    def run(
        self,
        agent: AgentDefinition,
        us_id: str | None = None,
        iteration: int = 1,
    ) -> AgentResult:
        """Exécute un agent complet : contexte → render → output.

        Args:
            agent: Définition de l'agent à exécuter.
            us_id: ID de l'US courante (si applicable).
            iteration: Numéro d'itération courante.

        Returns:
            AgentResult avec le contenu généré et les découvertes pour mémoire.
        """
        # 1. Construire le contexte
        context = self.context_builder.build(agent, us_id=us_id, iteration=iteration)

        # 2. Rendre les instructions via Jinja2
        instructions = self._render_instructions(agent, context)

        # 3. Rendre le template de sortie
        output_content = self._render_output(agent, context, instructions)

        # 4. Sauvegarder le rapport
        output_path = self._save_output(agent, context, output_content, us_id, iteration)

        # 5. Extraire les découvertes pour mémoire
        discoveries = self.memory_manager.extract_discoveries(output_content)

        # 6. Traiter les découvertes via l'Agent Mémoire
        for discovery in discoveries:
            self.memory_manager.add_discovery(
                agent_name=agent.name,
                us_id=us_id or "global",
                content=discovery,
                iteration=iteration,
            )

        return AgentResult(
            agent_name=agent.name,
            output_path=output_path,
            output_content=output_content,
            status="success",
            discoveries_for_memory=discoveries,
        )

    def _render_instructions(self, agent: AgentDefinition, context: AgentContext) -> str:
        """Rend les instructions de l'agent via Jinja2."""
        agent_dir = self.definitions_dir / agent.name
        instructions_path = agent_dir / "instructions.md"

        if not instructions_path.is_file():
            return f"# Instructions pour {agent.display_name}\n\nAucune instruction spécifique."

        env = Environment(
            loader=FileSystemLoader(str(agent_dir)),
            autoescape=False,
        )
        template = env.get_template("instructions.md")
        return template.render(
            agent=agent,
            context=context,
            profile=context.profile_content,
            skills=context.skills,
            memory=context.memory_entries,
            previous_reports=context.previous_reports,
            us_definition=context.us_definition,
            iteration=context.iteration,
        )

    def _render_output(
        self, agent: AgentDefinition, context: AgentContext, instructions: str
    ) -> str:
        """Rend le template de sortie de l'agent."""
        agent_dir = self.definitions_dir / agent.name
        output_template_path = agent_dir / "output_template.md"

        if not output_template_path.is_file():
            return self._default_output(agent, context, instructions)

        env = Environment(
            loader=FileSystemLoader(str(agent_dir)),
            autoescape=False,
        )
        template = env.get_template("output_template.md")
        return template.render(
            agent=agent,
            context=context,
            instructions=instructions,
            iteration=context.iteration,
        )

    def _default_output(
        self, agent: AgentDefinition, context: AgentContext, instructions: str
    ) -> str:
        """Génère un output par défaut si pas de template."""
        return (
            f"# Rapport — {agent.display_name}\n\n"
            f"**Agent:** {agent.name}\n"
            f"**Phase:** {agent.phase.value}\n"
            f"**Itération:** {context.iteration}\n\n"
            f"## Instructions exécutées\n\n{instructions}\n\n"
            "## Découvertes pour mémoire\n\n"
            "- (aucune découverte)\n"
        )

    def _save_output(
        self,
        agent: AgentDefinition,
        context: AgentContext,
        content: str,
        us_id: str | None,
        iteration: int,
    ) -> Path | None:
        """Sauvegarde le rapport de l'agent."""
        if us_id:
            return self.file_manager.write_us_report(us_id, agent.name, iteration, content)

        # Rapport global (pas lié à une US)
        return self.file_manager.write_md(
            f"reports/{agent.name}_report_iter{iteration}.md", content
        )
