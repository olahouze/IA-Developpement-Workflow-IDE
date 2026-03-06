"""Logique de verdict composite (PASS/FAIL) pour les analyseurs."""

from __future__ import annotations

from ai_workflow.config.schema import AppConfig
from ai_workflow.models.agent import AgentResult
from ai_workflow.models.verdict import AnalysisReport, CompositeVerdict, VerdictStatus


def build_verdict(
    results: dict[str, AgentResult],
    config: AppConfig,
) -> CompositeVerdict:
    """Construit un verdict composite à partir des résultats des analyseurs.

    Règles:
    - Sécu ou Perf FAIL = bloquant → retour Dev
    - BP seul FAIL = non-bloquant → continue
    """
    reports = []
    for agent_name, result in results.items():
        is_blocking = agent_name in config.verdict.blocking_analyzers
        verdict = VerdictStatus.PASS
        if result.verdict and result.verdict.upper() == "FAIL":
            verdict = VerdictStatus.FAIL
        elif result.status == "error":
            verdict = VerdictStatus.FAIL

        reports.append(
            AnalysisReport(
                analyzer_name=agent_name,
                verdict=verdict,
                findings=result.discoveries_for_memory,
                is_blocking=is_blocking,
            )
        )

    return CompositeVerdict(reports=reports)


def should_escalate(us_iteration: int, max_iterations: int) -> bool:
    """Vérifie si on doit escalader vers l'humain."""
    return us_iteration >= max_iterations


def get_next_action(verdict: CompositeVerdict, iteration: int, max_iterations: int) -> str:
    """Détermine l'action suivante basée sur le verdict.

    Returns:
        "continue" — US passe, aller à la suivante
        "retry" — retour Dev pour nouvelle itération
        "escalate" — ≥4 itérations, demander à l'humain
    """
    if verdict.all_passed or verdict.only_non_blocking_failures:
        return "continue"

    if should_escalate(iteration, max_iterations):
        return "escalate"

    return "retry"
