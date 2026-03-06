"""Tests fork_join."""

from __future__ import annotations

import time

from ai_workflow.engine.fork_join import fork_join
from ai_workflow.models.agent import AgentResult


class TestForkJoin:
    def test_empty_tasks(self):
        results = fork_join({})
        assert results == {}

    def test_single_task(self):
        def task():
            return AgentResult(agent_name="a", status="success")

        results = fork_join({"a": task})
        assert len(results) == 1
        assert results["a"].status == "success"

    def test_multiple_tasks(self):
        def task_a():
            return AgentResult(agent_name="a", status="success")

        def task_b():
            return AgentResult(agent_name="b", status="success")

        results = fork_join({"a": task_a, "b": task_b})
        assert len(results) == 2
        assert results["a"].status == "success"
        assert results["b"].status == "success"

    def test_task_error_handled(self):
        def failing_task():
            raise ValueError("boom")

        results = fork_join({"broken": failing_task})
        assert results["broken"].status == "error"
        assert "boom" in results["broken"].error

    def test_parallel_execution(self):
        """Vérifie que les tasks s'exécutent en parallèle."""
        def slow_task():
            time.sleep(0.1)
            return AgentResult(agent_name="slow", status="success")

        tasks = {f"t{i}": slow_task for i in range(3)}
        start = time.time()
        results = fork_join(tasks, max_workers=3)
        elapsed = time.time() - start

        assert len(results) == 3
        # En parallèle, ~0.1s ; en séquentiel, ~0.3s
        assert elapsed < 0.25

    def test_mixed_success_and_failure(self):
        def ok():
            return AgentResult(agent_name="ok", status="success")

        def ko():
            raise RuntimeError("fail")

        results = fork_join({"ok": ok, "ko": ko})
        assert results["ok"].status == "success"
        assert results["ko"].status == "error"
