"""Registre centralisé des 17 agents."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_workflow.models.agent import AgentDefinition, AgentPhase, FilePermission


class AgentRegistry:
    """Registre des agents chargés depuis leurs definition.yaml."""

    def __init__(self, definitions_dir: Path | None = None):
        self._definitions_dir = definitions_dir or (
            Path(__file__).parent / "definitions"
        )
        self._agents: dict[str, AgentDefinition] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._load_all()
            self._loaded = True

    def _load_all(self) -> None:
        """Charge toutes les définitions d'agents depuis le dossier definitions/."""
        if not self._definitions_dir.is_dir():
            return

        for agent_dir in sorted(self._definitions_dir.iterdir()):
            if not agent_dir.is_dir():
                continue
            def_path = agent_dir / "definition.yaml"
            if def_path.is_file():
                agent = self._load_definition(def_path)
                if agent:
                    self._agents[agent.name] = agent

    def _load_definition(self, path: Path) -> AgentDefinition | None:
        """Charge une définition d'agent depuis un fichier YAML."""
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            return None

        permissions = [FilePermission(p) for p in data.get("permissions", ["read_md"])]

        return AgentDefinition(
            name=data["name"],
            display_name=data.get("display_name", data["name"]),
            role=data.get("role", ""),
            phase=AgentPhase(data.get("phase", "conception")),
            permissions=permissions,
            optional=data.get("optional", False),
            interactive=data.get("interactive", False),
            instructions_path=path.parent / "instructions.md",
            output_template_path=path.parent / "output_template.md",
            dependencies=data.get("dependencies", []),
        )

    def get(self, name: str) -> AgentDefinition | None:
        """Retourne la définition d'un agent par son nom."""
        self._ensure_loaded()
        return self._agents.get(name)

    def get_all(self) -> dict[str, AgentDefinition]:
        """Retourne toutes les définitions d'agents."""
        self._ensure_loaded()
        return dict(self._agents)

    def get_by_phase(self, phase: AgentPhase) -> list[AgentDefinition]:
        """Retourne les agents d'une phase donnée."""
        self._ensure_loaded()
        return [a for a in self._agents.values() if a.phase == phase]

    def list_names(self) -> list[str]:
        """Liste les noms de tous les agents enregistrés."""
        self._ensure_loaded()
        return sorted(self._agents.keys())
