"""Tests du FileManager."""

from __future__ import annotations

from pathlib import Path

from ai_workflow.config.schema import AppConfig
from ai_workflow.managers.file_manager import FileManager


class TestFileManagerInit:
    def test_init_structure_creates_dirs(self, file_manager: FileManager, tmp_project: Path):
        dirs = file_manager.init_structure()
        assert len(dirs) == 5
        for d in dirs:
            assert d.is_dir()

    def test_exists_true(self, file_manager: FileManager):
        assert file_manager.exists() is True

    def test_exists_false(self, tmp_path: Path, config: AppConfig):
        fm = FileManager(tmp_path / "nonexistent", config)
        assert fm.exists() is False


class TestFileManagerReadWrite:
    def test_write_and_read_md(self, file_manager: FileManager):
        content = "# Test\n\nHello World"
        path = file_manager.write_md("reports/test.md", content)
        assert path.is_file()
        assert file_manager.read_md("reports/test.md") == content

    def test_read_md_nonexistent(self, file_manager: FileManager):
        assert file_manager.read_md("reports/nonexistent.md") is None

    def test_write_creates_subdirs(self, file_manager: FileManager):
        file_manager.write_md("deep/nested/dir/file.md", "content")
        assert file_manager.read_md("deep/nested/dir/file.md") == "content"


class TestFileManagerListFiles:
    def test_list_files_empty(self, file_manager: FileManager):
        files = file_manager.list_files("reports")
        assert files == []

    def test_list_files_with_content(self, file_manager: FileManager):
        file_manager.write_md("reports/a.md", "A")
        file_manager.write_md("reports/b.md", "B")
        file_manager.write_md("reports/c.txt", "C")
        md_files = file_manager.list_files("reports", "*.md")
        assert len(md_files) == 2

    def test_list_files_nonexistent_dir(self, file_manager: FileManager):
        assert file_manager.list_files("nonexistent") == []


class TestFileManagerState:
    def test_save_and_load_state(self, file_manager: FileManager):
        state = {"workflow_name": "vierge", "current_state": "init", "is_complete": False}
        file_manager.save_state(state)
        loaded = file_manager.load_state()
        assert loaded == state

    def test_load_state_nonexistent(self, file_manager: FileManager):
        assert file_manager.load_state() is None


class TestFileManagerUS:
    def test_get_us_dir_creates(self, file_manager: FileManager):
        path = file_manager.get_us_dir("US-001")
        assert path.is_dir()
        assert path.name == "US-001"

    def test_write_us_report(self, file_manager: FileManager):
        path = file_manager.write_us_report("US-001", "developpeur", 1, "# Rapport Dev")
        assert path.is_file()
        assert path.name == "developpeur_report_iter1.md"
        assert path.read_text(encoding="utf-8") == "# Rapport Dev"

    def test_list_us_reports(self, file_manager: FileManager):
        file_manager.write_us_report("US-001", "developpeur", 1, "Dev 1")
        file_manager.write_us_report("US-001", "testeur", 1, "Test 1")
        file_manager.write_us_report("US-001", "developpeur", 2, "Dev 2")

        all_reports = file_manager.list_us_reports("US-001")
        assert len(all_reports) == 3

        dev_reports = file_manager.list_us_reports("US-001", agent_name="developpeur")
        assert len(dev_reports) == 2

    def test_list_us_reports_nonexistent(self, file_manager: FileManager):
        assert file_manager.list_us_reports("US-NOPE") == []
