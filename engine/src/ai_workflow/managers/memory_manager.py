"""Gestionnaire de mémoire et profil projet."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ai_workflow.config.schema import AppConfig
from ai_workflow.models.profile import MemoryEntry, ProjectProfile


class MemoryManager:
    """Gère le profil projet et la mémoire évolutive."""

    def __init__(self, project_root: Path, config: AppConfig):
        self.project_root = project_root
        self.config = config
        self.workflow_dir = project_root / config.workflow_dir
        self.profile_path = self.workflow_dir / config.profile.filename
        self._profile: ProjectProfile | None = None
        self._template_dir = Path(__file__).parent.parent / "templates"

    @property
    def profile(self) -> ProjectProfile:
        if self._profile is None:
            self._profile = self._load_or_create_profile()
        return self._profile

    def _load_or_create_profile(self) -> ProjectProfile:
        """Charge le profil depuis le MD ou en crée un vide."""
        if self.profile_path.is_file():
            return self._parse_profile_md(self.profile_path.read_text(encoding="utf-8"))
        return ProjectProfile()

    def _parse_profile_md(self, content: str) -> ProjectProfile:
        """Parse un profil projet depuis son contenu Markdown."""
        profile = ProjectProfile()

        # Parse sections basiques
        name_match = re.search(r"^## Identité\s*\n.*?Nom\s*:\s*(.+)", content, re.MULTILINE)
        if name_match:
            profile.project_name = name_match.group(1).strip()

        type_match = re.search(r"Type\s*:\s*(.+)", content)
        if type_match:
            profile.project_type = type_match.group(1).strip()

        lang_match = re.search(r"Langage\s*:\s*(.+)", content)
        if lang_match:
            profile.language = lang_match.group(1).strip()

        # Parse mémoire évolutive
        memory_section = re.search(
            r"## Mémoire Évolutive\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
        )
        if memory_section:
            entries = re.findall(
                r"- \[(.+?)\]\[(.+?)\] (.+)", memory_section.group(1)
            )
            for agent, us, entry_content in entries:
                profile.memory_entries.append(
                    MemoryEntry(source_agent=agent, source_us=us, content=entry_content)
                )

        # Parse contraintes
        for section_name, target_list in [
            ("Contraintes Cyber", profile.security_constraints),
            ("Contraintes Entreprise", profile.enterprise_constraints),
        ]:
            section = re.search(
                rf"## {section_name}\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
            )
            if section:
                for line in section.group(1).strip().splitlines():
                    line = line.strip()
                    if line.startswith("- "):
                        target_list.append(line[2:])

        # Parse iterations_since_full_scan
        scan_match = re.search(r"iterations_since_full_scan\s*:\s*(\d+)", content)
        if scan_match:
            profile.iterations_since_full_scan = int(scan_match.group(1))

        return profile

    def save_profile(self) -> Path:
        """Sauvegarde le profil projet en Markdown via template Jinja2."""
        content = self.render_profile()
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        self.profile_path.write_text(content, encoding="utf-8")
        return self.profile_path

    def render_profile(self) -> str:
        """Rend le profil en Markdown via Jinja2."""
        if self._template_dir.is_dir():
            env = Environment(loader=FileSystemLoader(str(self._template_dir)), autoescape=False)
            try:
                template = env.get_template("profil_projet.md.j2")
                return template.render(profile=self.profile)
            except Exception:
                pass
        return self._render_profile_inline()

    def _render_profile_inline(self) -> str:
        """Fallback : rend le profil sans template Jinja2."""
        p = self.profile
        lines = [
            f"# Profil Projet : {p.project_name}",
            "",
            "## Identité",
            f"- Nom : {p.project_name}",
            f"- Type : {p.project_type}",
            f"- Description : {p.description}",
            f"- Langage : {p.language}",
            f"- Framework : {p.framework}",
            "",
            "## Contraintes Cyber",
        ]
        for c in p.security_constraints:
            lines.append(f"- {c}")
        lines += ["", "## Contraintes Entreprise"]
        for c in p.enterprise_constraints:
            lines.append(f"- {c}")
        lines += ["", "## Conventions"]
        for k, v in p.conventions.items():
            lines.append(f"- **{k}** : {v}")
        lines += ["", "## Surcharge Skills"]
        for k, v in p.skill_overrides.items():
            lines.append(f"- **{k}** : {v}")
        lines += [
            "",
            "## Contexte Auto-Détecté",
            f"- iterations_since_full_scan : {p.iterations_since_full_scan}",
            f"- last_full_scan_iteration : {p.last_full_scan_iteration}",
        ]
        for pat in p.detected_patterns:
            lines.append(f"- {pat}")
        lines += ["", "## Mémoire Évolutive"]
        for entry in p.memory_entries:
            lines.append(f"- [{entry.source_agent}][{entry.source_us}] {entry.content}")
        lines.append("")
        return "\n".join(lines)

    def add_discovery(self, agent_name: str, us_id: str, content: str, iteration: int = 1) -> bool:
        """Ajoute une découverte à la mémoire évolutive.

        Returns:
            True si ajoutée, False si contradiction ou limite atteinte.
        """
        entry = MemoryEntry(
            source_agent=agent_name,
            source_us=us_id,
            content=content,
            iteration=iteration,
        )
        result = self.profile.add_memory(entry)
        if result and self.profile.line_count() > self.config.profile.max_lines:
            self._compact_memory()
        return result

    def _compact_memory(self) -> None:
        """Réduit la mémoire si le profil dépasse la limite de lignes."""
        entries = self.profile.memory_entries
        if len(entries) > 20:
            # Garde les 20 plus récentes
            self.profile.memory_entries = entries[-20:]

    def extract_discoveries(self, report_content: str) -> list[str]:
        """Extrait les découvertes pour mémoire depuis un rapport d'agent."""
        discoveries = []
        section = re.search(
            r"## Découvertes pour mémoire\s*\n(.*?)(?=\n## |\Z)",
            report_content,
            re.DOTALL,
        )
        if section:
            for line in section.group(1).strip().splitlines():
                line = line.strip()
                if line.startswith("- "):
                    discoveries.append(line[2:])
                elif line and not line.startswith("#"):
                    discoveries.append(line)
        return discoveries

    def increment_scan_counter(self) -> None:
        """Incrémente le compteur d'itérations depuis le dernier scan complet."""
        self.profile.iterations_since_full_scan += 1

    def reset_scan_counter(self, iteration: int) -> None:
        """Réinitialise le compteur après un scan complet."""
        self.profile.iterations_since_full_scan = 0
        self.profile.last_full_scan_iteration = iteration
