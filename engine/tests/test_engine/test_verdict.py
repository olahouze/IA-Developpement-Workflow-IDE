"""Tests verdict engine."""

from __future__ import annotations

from ai_workflow.config.schema import AppConfig
from ai_workflow.engine.verdict import build_verdict, get_next_action, should_escalate
from ai_workflow.models.agent import AgentResult
from ai_workflow.models.verdict import AnalysisReport, CompositeVerdict, VerdictStatus


class TestBuildVerdict:
    def test_all_pass(self, config: AppConfig):
        results = {
            "analyseur-secu": AgentResult(agent_name="analyseur-secu", verdict="PASS"),
            "analyseur-perf": AgentResult(agent_name="analyseur-perf", verdict="PASS"),
            "analyseur-bp": AgentResult(agent_name="analyseur-bp", verdict="PASS"),
        }
        verdict = build_verdict(results, config)
        assert verdict.all_passed is True

    def test_blocking_fail(self, config: AppConfig):
        results = {
            "analyseur-secu": AgentResult(agent_name="analyseur-secu", verdict="FAIL"),
            "analyseur-perf": AgentResult(agent_name="analyseur-perf", verdict="PASS"),
        }
        verdict = build_verdict(results, config)
        assert verdict.has_blocking_failure is True

    def test_non_blocking_fail_only(self, config: AppConfig):
        results = {
            "analyseur-bp": AgentResult(agent_name="analyseur-bp", verdict="FAIL"),
        }
        verdict = build_verdict(results, config)
        assert verdict.has_blocking_failure is False

    def test_error_treated_as_fail(self, config: AppConfig):
        results = {
            "analyseur-secu": AgentResult(agent_name="analyseur-secu", status="error", error="crash"),
        }
        verdict = build_verdict(results, config)
        assert verdict.has_blocking_failure is True


class TestShouldEscalate:
    def test_below_threshold(self):
        assert should_escalate(2, 4) is False

    def test_at_threshold(self):
        assert should_escalate(4, 4) is True

    def test_above_threshold(self):
        assert should_escalate(5, 4) is True


class TestGetNextAction:
    def test_all_pass_continue(self):
        v = CompositeVerdict(reports=[
            AnalysisReport(analyzer_name="s", verdict=VerdictStatus.PASS),
        ])
        assert get_next_action(v, 1, 4) == "continue"

    def test_non_blocking_only_continue(self):
        v = CompositeVerdict(reports=[
            AnalysisReport(analyzer_name="bp", verdict=VerdictStatus.FAIL, is_blocking=False),
        ])
        assert get_next_action(v, 1, 4) == "continue"

    def test_blocking_fail_retry(self):
        v = CompositeVerdict(reports=[
            AnalysisReport(analyzer_name="secu", verdict=VerdictStatus.FAIL, is_blocking=True),
        ])
        assert get_next_action(v, 1, 4) == "retry"

    def test_blocking_fail_escalate_at_max(self):
        v = CompositeVerdict(reports=[
            AnalysisReport(analyzer_name="secu", verdict=VerdictStatus.FAIL, is_blocking=True),
        ])
        assert get_next_action(v, 4, 4) == "escalate"
