"""Exécution fork/join pour parallélisme d'agents."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from ai_workflow.models.agent import AgentResult


def fork_join(
    tasks: dict[str, Callable[[], AgentResult]],
    max_workers: int | None = None,
) -> dict[str, AgentResult]:
    """Exécute plusieurs agents en parallèle et attend tous les résultats.

    Args:
        tasks: Dict {agent_name: callable} où chaque callable retourne un AgentResult.
        max_workers: Nombre max de threads (None = auto).

    Returns:
        Dict {agent_name: AgentResult} pour chaque agent.
    """
    results: dict[str, AgentResult] = {}

    if not tasks:
        return results

    # Cas trivial : un seul agent, pas besoin de thread
    if len(tasks) == 1:
        name, func = next(iter(tasks.items()))
        try:
            results[name] = func()
        except Exception as e:
            results[name] = AgentResult(
                agent_name=name,
                status="error",
                error=str(e),
            )
        return results

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_name = {
            executor.submit(func): name for name, func in tasks.items()
        }
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = AgentResult(
                    agent_name=name,
                    status="error",
                    error=str(e),
                )

    return results
