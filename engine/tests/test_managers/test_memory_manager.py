"""Tests du MemoryManager."""

from __future__ import annotations

from pathlib import Path

from ai_workflow.config.schema import AppConfig
from ai_workflow.managers.memory_manager import MemoryManager


class TestMemoryManagerProfile:
    def test_create_default_profile(self, memory_manager: MemoryManager):
        assert memory_manager.profile.project_name == ""

    def test_save_and_reload(self, tmp_project: Path, config: AppConfig):
        tmp_project.mkdir(parents=True, exist_ok=True)
        mm = MemoryManager(tmp_project, config)
        mm.profile.project_name = "MonProjet"
        mm.profile.language = "Python"
        mm.save_profile()

        # Recharge
        mm2 = MemoryManager(tmp_project, config)
        assert mm2.profile.project_name == "MonProjet"

    def test_render_profile_contains_sections(self, memory_manager: MemoryManager):
        memory_manager.profile.project_name = "Test"
        content = memory_manager.render_profile()
        assert "Test" in content
        assert "Identité" in content or "identité" in content.lower()


class TestMemoryManagerDiscoveries:
    def test_add_discovery(self, memory_manager: MemoryManager):
        result = memory_manager.add_discovery("cartographe", "global", "FastAPI detected")
        assert result is True
        assert len(memory_manager.profile.memory_entries) == 1

    def test_add_discovery_compaction(self, memory_manager: MemoryManager):
        """Compaction after exceeding max_lines."""
        memory_manager.config.profile.max_lines = 20
        for i in range(30):
            memory_manager.add_discovery("agent", f"US-{i}", f"Discovery {i}")
        assert len(memory_manager.profile.memory_entries) <= 20

    def test_extract_discoveries(self, memory_manager: MemoryManager):
        report = """# Rapport
## Résultats
Tout ok.
## Découvertes pour mémoire
- Le projet utilise SQLAlchemy
- La DB est PostgreSQL
## Conclusion
Fin.
"""
        disco = memory_manager.extract_discoveries(report)
        assert len(disco) == 2
        assert "Le projet utilise SQLAlchemy" in disco
        assert "La DB est PostgreSQL" in disco

    def test_extract_discoveries_empty(self, memory_manager: MemoryManager):
        report = "# Rapport\nRAS.\n"
        disco = memory_manager.extract_discoveries(report)
        assert disco == []


class TestMemoryManagerScanCounter:
    def test_increment(self, memory_manager: MemoryManager):
        memory_manager.increment_scan_counter()
        assert memory_manager.profile.iterations_since_full_scan == 1

    def test_reset(self, memory_manager: MemoryManager):
        memory_manager.profile.iterations_since_full_scan = 5
        memory_manager.reset_scan_counter(iteration=10)
        assert memory_manager.profile.iterations_since_full_scan == 0
        assert memory_manager.profile.last_full_scan_iteration == 10
