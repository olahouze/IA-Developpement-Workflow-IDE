"""Tests des modèles verdict."""

from ai_workflow.models.verdict import (
    AnalysisReport,
    CompositeVerdict,
    IntegrationIssue,
    IssueSeverity,
    VerdictStatus,
)


class TestVerdictStatus:
    def test_values(self):
        assert VerdictStatus.PASS.value == "PASS"
        assert VerdictStatus.FAIL.value == "FAIL"


class TestAnalysisReport:
    def test_defaults(self):
        report = AnalysisReport(analyzer_name="secu", verdict=VerdictStatus.PASS)
        assert report.score == 0
        assert report.findings == []
        assert report.recommendations == []
        assert report.is_blocking is True


class TestCompositeVerdict:
    def test_all_passed(self):
        v = CompositeVerdict(reports=[
            AnalysisReport(analyzer_name="secu", verdict=VerdictStatus.PASS),
            AnalysisReport(analyzer_name="perf", verdict=VerdictStatus.PASS),
            AnalysisReport(analyzer_name="bp", verdict=VerdictStatus.PASS, is_blocking=False),
        ])
        assert v.all_passed is True
        assert v.has_blocking_failure is False
        assert v.overall_status == "PASS"

    def test_blocking_failure(self):
        v = CompositeVerdict(reports=[
            AnalysisReport(analyzer_name="secu", verdict=VerdictStatus.FAIL, is_blocking=True),
            AnalysisReport(analyzer_name="perf", verdict=VerdictStatus.PASS),
        ])
        assert v.all_passed is False
        assert v.has_blocking_failure is True
        assert v.overall_status == "FAIL_BLOCKING"

    def test_non_blocking_failure_only(self):
        v = CompositeVerdict(reports=[
            AnalysisReport(analyzer_name="secu", verdict=VerdictStatus.PASS, is_blocking=True),
            AnalysisReport(analyzer_name="bp", verdict=VerdictStatus.FAIL, is_blocking=False),
        ])
        assert v.all_passed is False
        assert v.has_blocking_failure is False
        assert v.only_non_blocking_failures is True
        assert v.overall_status == "FAIL_NON_BLOCKING"

    def test_empty(self):
        v = CompositeVerdict()
        assert v.all_passed is True
        assert v.has_blocking_failure is False


class TestIntegrationIssue:
    def test_minor(self):
        issue = IntegrationIssue(
            description="Conflit de nommage",
            severity=IssueSeverity.MINOR,
            affected_stories=["US-1", "US-2"],
        )
        assert issue.severity == IssueSeverity.MINOR
        assert len(issue.affected_stories) == 2
        assert issue.suggested_fix == ""
