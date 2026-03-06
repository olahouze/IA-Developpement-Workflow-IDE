"""Gestionnaire de skills (immutables + surcharges)."""

from __future__ import annotations

from pathlib import Path

from ai_workflow.managers.file_manager import FileManager
from ai_workflow.models.profile import ProjectProfile


class SkillManager:
    """Gère les skills immutables et les surcharges du profil projet."""

    def __init__(self, file_manager: FileManager, profile: ProjectProfile):
        self.file_manager = file_manager
        self.profile = profile

    def list_skills(self) -> list[Path]:
        """Liste tous les fichiers skills disponibles."""
        return self.file_manager.list_files("skills", "*.md")

    def get_skill(self, skill_name: str) -> str | None:
        """Lit le contenu d'un skill par son nom (sans extension)."""
        path = self.file_manager.skills_dir / f"{skill_name}.md"
        if path.is_file():
            return path.read_text(encoding="utf-8")
        return None

    def get_effective_skill(self, skill_name: str) -> str | None:
        """Retourne le skill avec surcharge appliquée si elle existe."""
        base = self.get_skill(skill_name)
        override = self.profile.skill_overrides.get(skill_name)
        if override:
            return override
        return base

    def get_all_skills(self) -> dict[str, str]:
        """Retourne tous les skills avec surcharges appliquées."""
        skills: dict[str, str] = {}
        for path in self.list_skills():
            name = path.stem
            content = self.get_effective_skill(name)
            if content:
                skills[name] = content
        return skills

    def is_immutable(self, skill_name: str) -> bool:
        """Vérifie si un skill est marqué comme immutable."""
        content = self.get_skill(skill_name)
        if content and "immutable: true" in content.lower().split("\n")[0:5]:
            return True
        # Vérification dans le frontmatter
        if content:
            for line in content.splitlines()[:10]:
                if line.strip().lower() in ("immutable: true", "immutable: yes"):
                    return True
        return False

    def write_skill(self, skill_name: str, content: str, force: bool = False) -> bool:
        """Écrit un skill. Refuse si immutable (sauf force=True).

        Returns:
            True si écrit, False si refusé (immutable).
        """
        if not force and self.is_immutable(skill_name):
            return False
        self.file_manager.write_md(f"skills/{skill_name}.md", content)
        return True

    def write_instruction(self, instruction_name: str, content: str) -> Path:
        """Écrit un fichier d'instructions."""
        return self.file_manager.write_md(f"instructions/{instruction_name}.md", content)
