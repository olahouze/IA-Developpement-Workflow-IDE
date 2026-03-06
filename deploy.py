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
BUNDLE_DIR = SCRIPT_DIR / "bundle"

DEPLOY_ITEMS = [
    (ENGINE_DIR / "src" / "ai_workflow", "src/ai_workflow"),
    (SCRIPT_DIR / "pyproject.toml", "pyproject.toml"),
    (SCRIPT_DIR / "README.md", "README.md"),
    (ENGINE_DIR / "tests", "tests"),
]

# Fichiers Copilot déployés séparément (fusion non-destructive avec .github/ existant)
COPILOT_ITEMS = [
    (BUNDLE_DIR / ".github" / "agents", ".github/agents"),
    (BUNDLE_DIR / ".github" / "prompts", ".github/prompts"),
    (BUNDLE_DIR / ".github" / "copilot-instructions.md", ".github/copilot-instructions.md"),
]

AIDE_MARKER_START = "<!-- AIDE:START -->"
AIDE_MARKER_END = "<!-- AIDE:END -->"
AIDE_PREFIX = "AIDE-"

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


# ── Déploiement Copilot (fusion non-destructive) ───────────────────────────


def deploy_copilot_files(dest: Path, *, dry_run: bool = False) -> list[str]:
    """Déploie les fichiers Copilot avec fusion non-destructive du .github/ existant."""
    copied: list[str] = []

    for source, rel_dest in COPILOT_ITEMS:
        if not source.exists():
            warn(f"Source Copilot introuvable, skip : {source}")
            continue

        target = dest / rel_dest

        # Cas spécial : copilot-instructions.md — fusion avec marqueurs
        if source.name == "copilot-instructions.md":
            if dry_run:
                info("[dry-run] Fusionnerait copilot-instructions.md")
            else:
                _merge_copilot_instructions(source, target)
            copied.append(str(rel_dest))
            continue

        # Dossiers agents/ et prompts/ : ajouter les fichiers AIDE-* sans écraser les existants
        if source.is_dir():
            aide_files = list(source.glob(f"{AIDE_PREFIX}*"))
            if dry_run:
                info(f"[dry-run] Copierait {len(aide_files)} fichiers {AIDE_PREFIX}* → {target}")
                copied.append(str(rel_dest))
                continue

            target.mkdir(parents=True, exist_ok=True)
            for src_file in aide_files:
                shutil.copy2(src_file, target / src_file.name)
            success(f"Copié : {len(aide_files)} fichiers {AIDE_PREFIX}* → {rel_dest}")
            copied.append(str(rel_dest))

    return copied


def _merge_copilot_instructions(source: Path, target: Path) -> None:
    """Fusionne copilot-instructions.md avec marqueurs AIDE:START/END."""
    aide_content = source.read_text(encoding="utf-8")

    if target.exists():
        existing = target.read_text(encoding="utf-8")

        if AIDE_MARKER_START in existing and AIDE_MARKER_END in existing:
            start_idx = existing.index(AIDE_MARKER_START)
            end_idx = existing.index(AIDE_MARKER_END) + len(AIDE_MARKER_END)
            merged = existing[:start_idx] + aide_content.strip() + existing[end_idx:]
            target.write_text(merged, encoding="utf-8")
            success("Fusionné : copilot-instructions.md (section AIDE mise à jour)")
        else:
            merged = existing.rstrip() + "\n\n" + aide_content
            target.write_text(merged, encoding="utf-8")
            success("Fusionné : copilot-instructions.md (section AIDE ajoutée)")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(aide_content, encoding="utf-8")
        success("Créé : copilot-instructions.md")


# ── Configuration cible ─────────────────────────────────────────────────────


def configure_target(
    dest: Path,
    *,
    project_name: str,
    user_name: str,
    lang: str,
    dry_run: bool = False,
) -> None:
    """Remplace les placeholders @@...@@ et crée la structure .ai-workflow/."""
    replacements = {
        "@@PROJECT_NAME@@": project_name,
        "@@USER_NAME@@": user_name,
        "@@LANG@@": lang,
    }

    # Remplacer les placeholders dans les fichiers .github/ AIDE
    github_dir = dest / ".github"
    if github_dir.exists():
        md_files = list(github_dir.rglob(f"{AIDE_PREFIX}*.md"))
        ci = github_dir / "copilot-instructions.md"
        if ci.exists():
            md_files.append(ci)

        replaced_count = 0
        for md_file in md_files:
            content = md_file.read_text(encoding="utf-8")
            original = content
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            if content != original:
                if dry_run:
                    info(f"[dry-run] Remplacerait placeholders dans {md_file.name}")
                else:
                    md_file.write_text(content, encoding="utf-8")
                replaced_count += 1

        if replaced_count and not dry_run:
            success(f"Placeholders remplacés dans {replaced_count} fichier(s)")

    # Créer la structure .ai-workflow/
    ai_dir = dest / ".ai-workflow"
    subdirs = ["skills", "instructions", "reports", "us", "docs"]
    if dry_run:
        info("[dry-run] Créerait .ai-workflow/ avec sous-dossiers")
    else:
        for subdir in subdirs:
            (ai_dir / subdir).mkdir(parents=True, exist_ok=True)
        success("Créé : .ai-workflow/ (skills, instructions, reports, us, docs)")


# ── Déploiement local ───────────────────────────────────────────────────────

def deploy_local(
    target_path: Path,
    *,
    dry_run: bool = False,
    project_name: str = "",
    user_name: str = "",
    lang: str = "French",
) -> None:
    """Déploie les fichiers vers un dossier local."""
    info(f"Cible locale : {_c(Colors.CYAN, str(target_path))}")

    if not dry_run:
        target_path.mkdir(parents=True, exist_ok=True)

    # 1. Copier les fichiers engine
    copied = copy_deploy_items(target_path, dry_run=dry_run)

    # 2. Déployer les fichiers Copilot (fusion non-destructive)
    copilot_copied = deploy_copilot_files(target_path, dry_run=dry_run)
    copied.extend(copilot_copied)

    # 3. Configurer la cible (placeholders + .ai-workflow/)
    configure_target(
        target_path,
        project_name=project_name or target_path.name,
        user_name=user_name or getpass.getuser(),
        lang=lang,
        dry_run=dry_run,
    )

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
    _print_post_deploy_help(target_path)


# ── Déploiement Git ─────────────────────────────────────────────────────────

def deploy_git(
    url: str,
    *,
    branch: str,
    dry_run: bool = False,
    default_branch: str = "main",
    project_name: str = "",
    user_name: str = "",
    lang: str = "French",
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
        deploy_copilot_files(repo_dir, dry_run=False)

        # 6b. Configurer la cible
        configure_target(
            repo_dir,
            project_name=project_name or repo_dir.name,
            user_name=user_name or getpass.getuser(),
            lang=lang,
            dry_run=False,
        )

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
        _print_post_deploy_help()

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Messages post-déploiement ───────────────────────────────────────────────


def _print_post_deploy_help(target_path: Path | None = None) -> None:
    """Affiche les commandes AIDE disponibles après déploiement."""
    print()
    info(_c(Colors.BOLD, "Commandes Copilot disponibles :"))
    info(f"  Agents   : tapez {_c(Colors.CYAN, '@AIDE-')} dans le chat pour voir les 17 agents")
    info(f"  Workflows: tapez {_c(Colors.CYAN, '/AIDE-')} pour voir les workflows")
    print()
    info("Commandes principales :")
    info(f"  {_c(Colors.CYAN, '/AIDE-workflow-init')}      — Initialiser le workspace .ai-workflow/")
    info(f"  {_c(Colors.CYAN, '/AIDE-workflow-vierge')}    — Nouveau projet (14 étapes)")
    info(f"  {_c(Colors.CYAN, '/AIDE-workflow-existant')}  — Enrichir un projet existant (10 étapes)")
    info(f"  {_c(Colors.CYAN, '/AIDE-workflow-feature')}   — Ajouter une feature (7 étapes)")
    info(f"  {_c(Colors.CYAN, '/AIDE-workflow-status')}    — Voir l'état courant")
    if target_path:
        print()
        info("Pour démarrer :")
        info(f"  cd {target_path}")
        info("  Ouvrir dans VS Code, puis /AIDE-workflow-init")


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
        "--project-name",
        default="",
        help="Nom du projet cible (défaut: nom du dossier cible)",
    )
    parser.add_argument(
        "--user-name",
        default="",
        help="Nom d'utilisateur (défaut: utilisateur système)",
    )
    parser.add_argument(
        "--lang",
        default="French",
        help="Langue de communication (défaut: French)",
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
        deploy_git(
            target,
            branch=args.branch,
            dry_run=args.dry_run,
            project_name=args.project_name,
            user_name=args.user_name,
            lang=args.lang,
        )
    else:
        deploy_local(
            Path(target).resolve(),
            dry_run=args.dry_run,
            project_name=args.project_name,
            user_name=args.user_name,
            lang=args.lang,
        )


if __name__ == "__main__":
    main()
