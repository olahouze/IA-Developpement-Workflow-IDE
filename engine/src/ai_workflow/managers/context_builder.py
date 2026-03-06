"""Construit le contexte complet pour l'exécution d'un agent."""

from __future__ import annotations

from ai_workflow.managers.file_manager import FileManager
from ai_workflow.managers.memory_manager import MemoryManager
from ai_workflow.managers.skill_manager import SkillManager
from ai_workflow.models.agent import AgentContext, AgentDefinition


class ContextBuilder:
    """Assemble le contexte complet qu'un agent reçoit pour s'exécuter."""

    def __init__(
        self,
        file_manager: FileManager,
        memory_manager: MemoryManager,
        skill_manager: SkillManager,
    ):
        self.file_manager = file_manager
        self.memory_manager = memory_manager
        self.skill_manager = skill_manager

    def build(
        self,
        agent: AgentDefinition,
        us_id: str | None = None,
        iteration: int = 1,
    ) -> AgentContext:
        """Construit le contexte complet pour un agent."""
        # Profil projet
        profile_content = self.memory_manager.render_profile()

        # Skills applicables
        skills = self.skill_manager.get_all_skills()

        # Mémoire évolutive
        memory_entries = [
            e.content for e in self.memory_manager.profile.memory_entries
        ]

        # Rapports précédents pour cette US
        previous_reports: list[str] = []
        us_definition = ""
        if us_id:
            # Charger la définition de l'US
            us_def_content = self.file_manager.read_md(f"us/{us_id}/definition.md")
            if us_def_content:
                us_definition = us_def_content

            # Charger tous les rapports précédents de cette US
            report_files = self.file_manager.list_us_reports(us_id)
            for report_path in report_files:
                previous_reports.append(report_path.read_text(encoding="utf-8"))

        return AgentContext(
            agent=agent,
            profile_content=profile_content,
            skills=skills,
            memory_entries=memory_entries,
            previous_reports=previous_reports,
            us_definition=us_definition,
            iteration=iteration,
        )
