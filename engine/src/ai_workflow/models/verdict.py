"""Modèles de données pour les verdicts d'analyse."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class VerdictStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"


class IssueSeverity(StrEnum):
    MINOR = "MINEUR"
    MAJOR = "MAJEUR"


@dataclass
class AnalysisReport:
    """Rapport d'un analyseur (Perf, Sécu, BP)."""

    analyzer_name: str
    verdict: VerdictStatus
    score: int = 0  # 0-100 gradué pour l'humain
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    is_blocking: bool = True


@dataclass
class CompositeVerdict:
    """Verdict composite des 3 analyseurs."""

    reports: list[AnalysisReport] = field(default_factory=list)
    iteration: int = 1

    @property
    def has_blocking_failure(self) -> bool:
        return any(r.verdict == VerdictStatus.FAIL and r.is_blocking for r in self.reports)

    @property
    def all_passed(self) -> bool:
        return all(r.verdict == VerdictStatus.PASS for r in self.reports)

    @property
    def only_non_blocking_failures(self) -> bool:
        failures = [r for r in self.reports if r.verdict == VerdictStatus.FAIL]
        return len(failures) > 0 and all(not f.is_blocking for f in failures)

    @property
    def overall_status(self) -> str:
        if self.all_passed:
            return "PASS"
        if self.has_blocking_failure:
            return "FAIL_BLOCKING"
        return "FAIL_NON_BLOCKING"


@dataclass
class IntegrationIssue:
    """Problème détecté par l'Intégrateur."""

    description: str
    severity: IssueSeverity
    affected_stories: list[str] = field(default_factory=list)
    suggested_fix: str = ""
