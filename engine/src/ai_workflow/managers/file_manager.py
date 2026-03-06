"""Gestionnaire de fichiers pour .ai-workflow/."""

from __future__ import annotations

import json
from pathlib import Path

from ai_workflow.config.schema import AppConfig


class FileManager:
    """Gère la lecture/écriture dans le répertoire .ai-workflow/."""

    def __init__(self, project_root: Path, config: AppConfig):
        self.project_root = project_root
        self.config = config
        self.workflow_dir = project_root / config.workflow_dir

    @property
    def skills_dir(self) -> Path:
        return self.workflow_dir / "skills"

    @property
    def instructions_dir(self) -> Path:
        return self.workflow_dir / "instructions"

    @property
    def reports_dir(self) -> Path:
        return self.workflow_dir / "reports"

    @property
    def us_dir(self) -> Path:
        return self.workflow_dir / "us"

    @property
    def docs_dir(self) -> Path:
        return self.workflow_dir / "docs"

    @property
    def state_path(self) -> Path:
        return self.workflow_dir / self.config.state_file

    @property
    def profile_path(self) -> Path:
        return self.workflow_dir / self.config.profile.filename

    def init_structure(self) -> list[Path]:
        """Crée la structure .ai-workflow/ complète. Retourne les dossiers créés."""
        created = []
        for subdir in self.config.directories:
            path = self.workflow_dir / subdir
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)
        return created

    def exists(self) -> bool:
        """Vérifie si .ai-workflow/ existe."""
        return self.workflow_dir.is_dir()

    def write_md(self, relative_path: str, content: str) -> Path:
        """Écrit un fichier Markdown dans .ai-workflow/."""
        path = self.workflow_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def read_md(self, relative_path: str) -> str | None:
        """Lit un fichier Markdown depuis .ai-workflow/."""
        path = self.workflow_dir / relative_path
        if path.is_file():
            return path.read_text(encoding="utf-8")
        return None

    def list_files(self, relative_dir: str, pattern: str = "*.md") -> list[Path]:
        """Liste les fichiers dans un sous-dossier de .ai-workflow/."""
        path = self.workflow_dir / relative_dir
        if not path.is_dir():
            return []
        return sorted(path.glob(pattern))

    def save_state(self, state: dict) -> Path:
        """Sauvegarde l'état du workflow en JSON."""
        self.workflow_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        return self.state_path

    def load_state(self) -> dict | None:
        """Charge l'état du workflow depuis JSON."""
        if self.state_path.is_file():
            with open(self.state_path, encoding="utf-8") as f:
                return json.load(f)
        return None

    def get_us_dir(self, us_id: str) -> Path:
        """Retourne le dossier d'une US (le crée si nécessaire)."""
        path = self.us_dir / us_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_us_report(self, us_id: str, agent_name: str, iteration: int, content: str) -> Path:
        """Écrit un rapport d'agent pour une US avec suffixe _iterN."""
        us_path = self.get_us_dir(us_id)
        filename = f"{agent_name}_report_iter{iteration}.md"
        report_path = us_path / filename
        report_path.write_text(content, encoding="utf-8")
        return report_path

    def list_us_reports(self, us_id: str, agent_name: str | None = None) -> list[Path]:
        """Liste les rapports d'une US, optionnellement filtrés par agent."""
        us_path = self.us_dir / us_id
        if not us_path.is_dir():
            return []
        if agent_name:
            return sorted(us_path.glob(f"{agent_name}_report_iter*.md"))
        return sorted(us_path.glob("*_report_iter*.md"))
