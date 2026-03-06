#!/usr/bin/env python3
"""
deploy.py — Déploie AI Workflow Engine vers un dossier local ou un repo Git distant.

Usage:
  python deploy.py /chemin/vers/projet-cible
  python deploy.py https://gitlab.example.com/org/repo.git
  python deploy.py https://gitlab.example.com/org/repo.git --branch feat/ai-workflow
  python deploy.py /chemin --dry-run

Fonctionnement:
  - Path local  → copie directe de src/ai_workflow + bundle/ dans le dossier cible
  - URL Git     → clone le repo, crée une branche, copie les fichiers, commit + push
                  Si l'authentification git échoue, demande un token à l'utilisateur
"""

from __future__ import annotations

import argparse
import getpass
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse, urlunparse

# ── Configuration ───────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
ENGINE_DIR = SCRIPT_DIR / "engine"

DEPLOY_ITEMS = [
    (ENGINE_DIR / "src" / "ai_workflow", "src/ai_workflow"),
    (SCRIPT_DIR / "pyproject.toml", "pyproject.toml"),
    (SCRIPT_DIR / "README.md", "README.md"),
    (ENGINE_DIR / "tests", "tests"),
]

DEFAULT_BRANCH = "feat/ai-workflow-engine"
COMMIT_MESSAGE = "feat: deploy AI Workflow Engine v0.1.0"


# ── Couleurs ────────────────────────────────────────────────────────────────

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

    @staticmethod
    def supports_color() -> bool:
        if os.environ.get("NO_COLOR"):
            return False
        if platform.system() == "Windows":
            return os.environ.get("TERM") or os.environ.get("WT_SESSION")
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(color: str, text: str) -> str:
    return f"{color}{text}{Colors.RESET}" if Colors.supports_color() else text


def info(msg: str) -> None:
    print(f"  {_c(Colors.BLUE, '●')} {msg}")


def success(msg: str) -> None:
    print(f"  {_c(Colors.GREEN, '✓')} {msg}")


def warn(msg: str) -> None:
    print(f"  {_c(Colors.YELLOW, '⚠')} {msg}")


def error(msg: str) -> None:
    print(f"  {_c(Colors.RED, '✗')} {msg}")


def banner() -> None:
    print()
    print(_c(Colors.CYAN + Colors.BOLD, "  ╔══════════════════════════════════════════════╗"))
    print(_c(Colors.CYAN + Colors.BOLD, "  ║  AI Workflow Engine — Deploy                 ║"))
    print(_c(Colors.CYAN + Colors.BOLD, "  ╚══════════════════════════════════════════════╝"))
    print()


# ── Utilitaires Git ─────────────────────────────────────────────────────────

def run_cmd(
    cmd: list[str],
    *,
    cwd: str | Path | None = None,
    check: bool = True,
    capture: bool = False,
    timeout: int = 120,
) -> subprocess.CompletedProcess:
    display = " ".join(cmd[:6]) + (" ..." if len(cmd) > 6 else "")
    info(f"→ {_c(Colors.CYAN, display)}")
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=check,
        capture_output=capture,
        text=True,
        timeout=timeout,
    )


def is_git_url(target: str) -> bool:
    """Détecte si la cible est une URL Git."""
    if target.endswith(".git"):
        return True
    parsed = urlparse(target)
    return parsed.scheme in ("https", "http", "ssh", "git")


def inject_token_in_url(url: str, token: str) -> str:
    """Injecte un token OAuth2 dans une URL HTTPS Git."""
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http"):
        return url
    netloc = f"oauth2:{token}@{parsed.hostname}"
    if parsed.port:
        netloc += f":{parsed.port}"
    return urlunparse(parsed._replace(netloc=netloc))


def test_git_access(url: str) -> bool:
    """Teste si git peut accéder au repo sans authentification supplémentaire."""
    result = run_cmd(
        ["git", "ls-remote", "--exit-code", url],
        check=False,
        capture=True,
        timeout=30,
    )
    return result.returncode == 0


def prompt_git_token(url: str) -> str:
    """Demande un token Git à l'utilisateur."""
    parsed = urlparse(url)
    host = parsed.hostname or "le serveur Git"
    print()
    warn(f"L'accès Git classique a échoué pour {_c(Colors.CYAN, host)}")
    info("Un token d'accès personnel est nécessaire.")
    info("  GitLab : Settings → Access Tokens → Scope: read_repository, write_repository")
    info("  GitHub : Settings → Developer settings → Personal access tokens")
    print()
    token = getpass.getpass(f"  Token pour {host} : ")
    if not token.strip():
        error("Token vide, abandon.")
        sys.exit(1)
    return token.strip()


# ── Copie des fichiers ──────────────────────────────────────────────────────

def copy_deploy_items(dest: Path, *, dry_run: bool = False) -> list[str]:
    """Copie tous les éléments de déploiement vers la destination."""
    copied = []
    for source, rel_dest in DEPLOY_ITEMS:
        target = dest / rel_dest
        if not source.exists():
            warn(f"Source introuvable, skip : {source}")
            continue

        if dry_run:
            label = "dir" if source.is_dir() else "file"
            info(f"[dry-run] Copierait {label} → {target}")
            copied.append(str(rel_dest))
            continue

        if source.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        copied.append(str(rel_dest))
        success(f"Copié : {rel_dest}")

    return copied


# ── Déploiement local ───────────────────────────────────────────────────────

def deploy_local(target_path: Path, *, dry_run: bool = False) -> None:
    """Déploie les fichiers vers un dossier local."""
    info(f"Cible locale : {_c(Colors.CYAN, str(target_path))}")

    if not dry_run:
        target_path.mkdir(parents=True, exist_ok=True)

    copied = copy_deploy_items(target_path, dry_run=dry_run)

    if not dry_run:
        # Créer un .gitignore basique si absent
        gitignore = target_path / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text(
                ".venv/\n__pycache__/\n*.pyc\n.ai-workflow/\n.ruff_cache/\n.pytest_cache/\n.coverage\n",
                encoding="utf-8",
            )
            success("Créé : .gitignore")

    print()
    success(f"Déploiement local terminé — {len(copied)} éléments copiés vers {target_path}")
    info("Pour démarrer :")
    info(f"  cd {target_path}")
    info("  uv sync")
    info("  ai-workflow init --name mon-projet")


# ── Déploiement Git ─────────────────────────────────────────────────────────

def deploy_git(
    url: str,
    *,
    branch: str,
    dry_run: bool = False,
    default_branch: str = "main",
) -> None:
    """Clone le repo, crée une branche, copie les fichiers, commit + push."""
    info(f"Cible Git : {_c(Colors.CYAN, url)}")
    info(f"Branche   : {_c(Colors.CYAN, branch)}")

    # 1. Tester l'accès Git
    clone_url = url
    if not test_git_access(url):
        token = prompt_git_token(url)
        clone_url = inject_token_in_url(url, token)
        if not test_git_access(clone_url):
            error("Échec d'authentification même avec le token fourni.")
            sys.exit(1)
        success("Authentification par token réussie.")

    if dry_run:
        info("[dry-run] Clonerais le repo, créerais la branche, copierais les fichiers, push.")
        copy_deploy_items(Path("/tmp/dry-run-target"), dry_run=True)
        return

    # 2. Clone dans un dossier temporaire
    tmpdir = Path(tempfile.mkdtemp(prefix="ai-workflow-deploy-"))
    try:
        run_cmd(["git", "clone", "--depth=1", clone_url, str(tmpdir / "repo")], timeout=120)
        repo_dir = tmpdir / "repo"

        # 3. Déterminer la branche par défaut du repo
        result = run_cmd(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=repo_dir,
            check=False,
            capture=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            default_branch = result.stdout.strip().split("/")[-1]
        info(f"Branche par défaut du repo : {default_branch}")

        # 4. Fetch complet pour la branche par défaut
        run_cmd(["git", "fetch", "origin", default_branch], cwd=repo_dir, check=False, capture=True)

        # 5. Créer la branche de déploiement
        result = run_cmd(
            ["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
            cwd=repo_dir,
            check=False,
            capture=True,
        )
        if result.returncode == 0:
            warn(f"La branche '{branch}' existe déjà sur le remote.")
            run_cmd(["git", "checkout", "-B", branch, f"origin/{branch}"], cwd=repo_dir)
        else:
            run_cmd(["git", "checkout", "-b", branch], cwd=repo_dir)
        success(f"Sur la branche : {branch}")

        # 6. Copier les fichiers
        copy_deploy_items(repo_dir, dry_run=False)

        # 7. Commit + Push
        run_cmd(["git", "add", "-A"], cwd=repo_dir)

        result = run_cmd(["git", "diff", "--cached", "--quiet"], cwd=repo_dir, check=False, capture=True)
        if result.returncode == 0:
            warn("Aucun changement détecté, rien à commit.")
            return

        run_cmd(["git", "commit", "-m", COMMIT_MESSAGE], cwd=repo_dir)
        run_cmd(["git", "push", "-u", "origin", branch], cwd=repo_dir)

        print()
        success(f"Déploiement Git terminé sur la branche '{branch}'")
        parsed = urlparse(url)
        if parsed.hostname:
            path_clean = parsed.path.rstrip(".git").lstrip("/")
            mr_url = f"https://{parsed.hostname}/{path_clean}/-/merge_requests/new?merge_request[source_branch]={branch}"
            info(f"Créer une Merge Request : {_c(Colors.CYAN, mr_url)}")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── CLI ─────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Déploie AI Workflow Engine vers un dossier local ou un repo Git distant.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python deploy.py ./mon-projet
  python deploy.py /chemin/absolu/vers/projet
  python deploy.py https://gitlab.example.com/org/repo.git
  python deploy.py https://gitlab.example.com/org/repo.git --branch feat/ai-workflow
  python deploy.py ./cible --dry-run
        """,
    )
    parser.add_argument(
        "target",
        help="Chemin local ou URL Git du projet cible",
    )
    parser.add_argument(
        "--branch", "-b",
        default=DEFAULT_BRANCH,
        help=f"Branche Git à créer (défaut: {DEFAULT_BRANCH})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les actions sans les exécuter",
    )
    return parser.parse_args()


def validate_sources() -> None:
    """Vérifie que les sources de déploiement existent."""
    for source, rel_dest in DEPLOY_ITEMS:
        if not source.exists():
            error(f"Source manquante : {source}")
            error("Lancez ce script depuis la racine du projet IA-Developpement-Workflow-IDE.")
            sys.exit(1)


def main() -> None:
    banner()
    args = parse_args()

    if args.dry_run:
        warn("Mode dry-run — aucune modification ne sera effectuée.")
        print()

    validate_sources()

    target = args.target

    if is_git_url(target):
        deploy_git(target, branch=args.branch, dry_run=args.dry_run)
    else:
        deploy_local(Path(target).resolve(), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
