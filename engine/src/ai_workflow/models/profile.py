"""Modèles de données pour le profil projet et la mémoire."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MemoryEntry:
    """Une entrée dans la mémoire évolutive du profil projet."""

    source_agent: str
    source_us: str
    content: str
    iteration: int = 1


@dataclass
class ProjectProfile:
    """Profil projet complet avec toutes les sections."""

    # Section Identité
    project_name: str = ""
    project_type: str = ""
    description: str = ""
    language: str = ""
    framework: str = ""

    # Section Contraintes Cyber
    security_constraints: list[str] = field(default_factory=list)

    # Section Contraintes Entreprise
    enterprise_constraints: list[str] = field(default_factory=list)

    # Section Conventions
    conventions: dict[str, str] = field(default_factory=dict)

    # Section Surcharge Skills
    skill_overrides: dict[str, str] = field(default_factory=dict)

    # Section Contexte Auto-Détecté
    detected_patterns: list[str] = field(default_factory=list)
    iterations_since_full_scan: int = 0
    last_full_scan_iteration: int = 0

    # Section Mémoire Évolutive
    memory_entries: list[MemoryEntry] = field(default_factory=list)

    def add_memory(self, entry: MemoryEntry) -> bool:
        """Ajoute une entrée mémoire si elle ne contredit pas les existantes.

        Returns:
            True si ajoutée, False si contradiction détectée.
        """
        for existing in self.memory_entries:
            if existing.source_us != entry.source_us and existing.content == entry.content:
                return True  # Doublon, déjà présent
        self.memory_entries.append(entry)
        return True

    def line_count(self) -> int:
        """Estime le nombre de lignes du profil sérialisé."""
        lines = 10  # En-têtes
        lines += len(self.security_constraints)
        lines += len(self.enterprise_constraints)
        lines += len(self.conventions) * 2
        lines += len(self.skill_overrides) * 2
        lines += len(self.detected_patterns)
        lines += len(self.memory_entries) * 3
        return lines
