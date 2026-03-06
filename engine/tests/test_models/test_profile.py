"""Tests du modèle profil projet."""

from ai_workflow.models.profile import MemoryEntry, ProjectProfile


class TestMemoryEntry:
    def test_creation(self):
        entry = MemoryEntry(
            source_agent="cartographe",
            source_us="US-001",
            content="Le projet utilise FastAPI",
        )
        assert entry.iteration == 1


class TestProjectProfile:
    def test_defaults(self):
        p = ProjectProfile()
        assert p.project_name == ""
        assert p.memory_entries == []
        assert p.iterations_since_full_scan == 0

    def test_add_memory(self):
        p = ProjectProfile()
        entry = MemoryEntry(
            source_agent="cartographe",
            source_us="global",
            content="Python 3.11",
        )
        result = p.add_memory(entry)
        assert result is True
        assert len(p.memory_entries) == 1

    def test_add_memory_duplicate(self):
        p = ProjectProfile()
        entry1 = MemoryEntry(source_agent="a", source_us="US-1", content="Fact X")
        entry2 = MemoryEntry(source_agent="b", source_us="US-2", content="Fact X")
        p.add_memory(entry1)
        p.add_memory(entry2)
        # Duplicate content from different US is detected and returns True
        assert len(p.memory_entries) == 1

    def test_line_count(self):
        p = ProjectProfile(
            security_constraints=["SC1", "SC2"],
            enterprise_constraints=["EC1"],
            conventions={"style": "PEP8"},
            memory_entries=[
                MemoryEntry(source_agent="a", source_us="b", content="fact"),
            ],
        )
        assert p.line_count() > 10
