"""Tests CLI via invoke de typer."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from ai_workflow.cli import app

runner = CliRunner()


class TestCLIInit:
    def test_init_creates_structure(self, tmp_path: Path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init", "--name", "test-project"])
        assert result.exit_code == 0
        assert (tmp_path / ".ai-workflow").is_dir()

    def test_init_with_type(self, tmp_path: Path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["init", "--type", "feature", "--name", "feat-test"])
        assert result.exit_code == 0

    def test_init_twice_abort(self, tmp_path: Path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner.invoke(app, ["init", "--name", "p1"])
        # Second init with 'n' to abort
        result = runner.invoke(app, ["init", "--name", "p1"], input="n\n")
        assert result.exit_code != 0 or "Aborted" in (result.output or "")


class TestCLIStatus:
    def test_status_not_initialized(self, tmp_path: Path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 1

    def test_status_after_init(self, tmp_path: Path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runner.invoke(app, ["init", "--name", "test-project"])
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "vierge" in result.output.lower() or "Workflow" in result.output


class TestCLIAgents:
    def test_agents_list(self):
        result = runner.invoke(app, ["agents"])
        assert result.exit_code == 0
        assert "Brainstormer" in result.output
        assert "Développeur" in result.output or "veloppeur" in result.output


class TestCLIRun:
    def test_run_not_initialized(self, tmp_path: Path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["run"])
        assert result.exit_code == 1
