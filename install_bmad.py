#!/usr/bin/env python3
"""
BMad Method Installer — Contournement proxy corporate
=====================================================
Ce script installe bmad-method v6 lorsque le registre npm est bloqué
par un proxy d'entreprise (ex: EDF-BlocageListeNoire).

Stratégie :
  1. Clone le repo GitHub bmad-code-org/BMAD-METHOD
  2. Installe les dépendances Node.js via un miroir npm alternatif
  3. Exécute l'installateur CLI depuis les sources locales
  4. Corrige les variables non résolues dans les configs générées
  5. Nettoie le dossier temporaire

Usage :
  python install_bmad.py
  python install_bmad.py --tools claude-code --lang English
  python install_bmad.py --modules bmm,bmb --tools cursor --dry-run
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ── Configuration par défaut ────────────────────────────────────────────────

BMAD_REPO = "https://github.com/bmad-code-org/BMAD-METHOD.git"
BMAD_BRANCH = "main"
BMAD_VERSION = "6.0.4"  # tag de référence, None = latest main

# Miroirs npm alternatifs, testés dans l'ordre
NPM_MIRRORS = [
    "https://registry.npmmirror.com",       # Miroir chinois (rapide, fiable)
    "https://registry.npm.taobao.org",      # Ancien miroir Taobao
    "https://r.cnpmjs.org",                 # cnpm
    "https://registry.npmjs.org",           # Officiel (en dernier, peut être bloqué)
]

TEMP_DIR_NAME = "_bmad-method-src"
OUTPUT_FOLDER_DEFAULT = "_bmad-output"


# ── Utilitaires ─────────────────────────────────────────────────────────────

class Colors:
    """Couleurs ANSI pour le terminal."""
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
    """Applique une couleur si le terminal la supporte."""
    if Colors.supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


def info(msg: str) -> None:
    print(f"  {_c(Colors.BLUE, '●')} {msg}")


def success(msg: str) -> None:
    print(f"  {_c(Colors.GREEN, '✓')} {msg}")


def warn(msg: str) -> None:
    print(f"  {_c(Colors.YELLOW, '⚠')} {msg}")


def error(msg: str) -> None:
    print(f"  {_c(Colors.RED, '✗')} {msg}")


def fatal(msg: str) -> None:
    error(msg)
    sys.exit(1)


def banner() -> None:
    print()
    print(_c(Colors.CYAN + Colors.BOLD, "  ╔══════════════════════════════════════════════╗"))
    print(_c(Colors.CYAN + Colors.BOLD, "  ║  BMad Method — Install (proxy bypass)        ║"))
    print(_c(Colors.CYAN + Colors.BOLD, "  ╚══════════════════════════════════════════════╝"))
    print()


def _resolve_cmd(cmd: list[str]) -> list[str]:
    """Résout le nom de la commande en chemin complet sur Windows (.cmd, .bat, etc.)."""
    if platform.system() == "Windows" and cmd:
        resolved = shutil.which(cmd[0])
        if resolved:
            return [resolved] + cmd[1:]
    return cmd


def run(
    cmd: list[str],
    *,
    cwd: str | Path | None = None,
    check: bool = True,
    capture: bool = False,
    timeout: int = 300,
) -> subprocess.CompletedProcess:
    """Exécute une commande avec logging."""
    cmd = _resolve_cmd(cmd)
    display = " ".join(cmd[:5]) + (" ..." if len(cmd) > 5 else "")
    info(f"Exécution : {_c(Colors.CYAN, display)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            check=check,
            capture_output=capture,
            text=True,
            timeout=timeout,
        )
        return result
    except subprocess.CalledProcessError as e:
        if capture and e.stderr:
            error(f"stderr: {e.stderr.strip()[:500]}")
        raise
    except FileNotFoundError:
        fatal(f"Commande introuvable : {cmd[0]}. Vérifiez que {cmd[0]} est dans le PATH.")
    except subprocess.TimeoutExpired:
        fatal(f"Timeout après {timeout}s pour : {display}")


def check_prerequisites() -> None:
    """Vérifie que git et node sont disponibles."""
    for tool, min_version, version_flag in [
        ("git", None, "--version"),
        ("node", "20", "--version"),
        ("npm", None, "--version"),
    ]:
        result = run([tool, version_flag], check=False, capture=True)
        if result.returncode != 0:
            fatal(f"{tool} n'est pas installé ou pas dans le PATH.")
        version_str = result.stdout.strip()
        info(f"{tool} détecté : {version_str}")

        if min_version and tool == "node":
            match = re.search(r"v?(\d+)", version_str)
            if match and int(match.group(1)) < int(min_version):
                fatal(f"Node.js >= v{min_version} requis (trouvé: {version_str})")


def detect_npm_blocked() -> bool:
    """Teste si le registre npm officiel est bloqué."""
    info("Test de connectivité npm registry...")
    result = run(
        ["npm", "view", "commander", "version", "--registry", "https://registry.npmjs.org"],
        check=False,
        capture=True,
        timeout=30,
    )
    if result.returncode != 0:
        stderr = result.stderr or ""
        if "403" in stderr or "BlocageListeNoire" in stderr or "BLOCKED" in stderr.upper():
            warn("Registre npm officiel BLOQUÉ par le proxy corporate.")
            return True
        if "ETIMEDOUT" in stderr or "ECONNREFUSED" in stderr:
            warn("Registre npm officiel inaccessible (timeout/refusé).")
            return True
    else:
        success("Registre npm officiel accessible.")
    return False


def find_working_mirror() -> str | None:
    """Teste les miroirs npm et retourne le premier fonctionnel."""
    info("Recherche d'un miroir npm fonctionnel...")
    for mirror in NPM_MIRRORS:
        result = run(
            ["npm", "view", "commander", "version", "--registry", mirror],
            check=False,
            capture=True,
            timeout=20,
        )
        if result.returncode == 0:
            success(f"Miroir fonctionnel trouvé : {mirror}")
            return mirror
        warn(f"Miroir indisponible : {mirror}")
    return None


# ── Étapes d'installation ───────────────────────────────────────────────────

def step_clone(project_dir: Path, tag: str | None = None) -> Path:
    """Clone le repo BMAD-METHOD dans un dossier temporaire."""
    src_dir = project_dir / TEMP_DIR_NAME
    if src_dir.exists():
        info(f"Nettoyage de l'ancien clone : {src_dir}")
        shutil.rmtree(src_dir, ignore_errors=True)

    clone_cmd = ["git", "clone", "--depth", "1"]
    if tag:
        clone_cmd += ["--branch", f"v{tag}"]
    clone_cmd += [BMAD_REPO, str(src_dir)]

    run(clone_cmd, timeout=120)

    if not (src_dir / "package.json").exists():
        fatal(f"Clone échoué : package.json introuvable dans {src_dir}")

    # Lire la version clonée
    pkg = json.loads((src_dir / "package.json").read_text(encoding="utf-8"))
    success(f"Repo BMAD-METHOD cloné (v{pkg.get('version', '?')})")
    return src_dir


def step_install_deps(src_dir: Path, mirror: str) -> None:
    """Installe les dépendances Node.js via le miroir npm."""
    pkg_path = src_dir / "package.json"
    pkg_backup = src_dir / "package.json.bak"

    # Lire les dépendances de production
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    prod_deps = pkg.get("dependencies", {})

    if not prod_deps:
        fatal("Aucune dépendance de production trouvée dans package.json")

    info(f"{len(prod_deps)} dépendances de production à installer")

    # Sauvegarder l'original et créer un package.json minimal
    # (évite que npm essaie de résoudre les devDependencies bloquées)
    shutil.copy2(pkg_path, pkg_backup)

    minimal_pkg = {
        "name": "bmad-method-local-install",
        "version": pkg.get("version", "0.0.0"),
        "private": True,
        "dependencies": prod_deps,
    }
    pkg_path.write_text(json.dumps(minimal_pkg, indent=2), encoding="utf-8")

    # Supprimer node_modules existant
    node_modules = src_dir / "node_modules"
    if node_modules.exists():
        shutil.rmtree(node_modules, ignore_errors=True)

    # Installer via le miroir
    try:
        run(
            [
                "npm", "install",
                "--omit=dev",
                "--no-package-lock",
                "--legacy-peer-deps",
                "--registry", mirror,
            ],
            cwd=src_dir,
            timeout=300,
        )
    except subprocess.CalledProcessError:
        # Tentative de fallback : installer depuis les tarballs GitHub
        warn("npm install échoué, tentative via tarballs GitHub...")
        step_install_deps_from_github(src_dir, prod_deps)

    # Restaurer l'original
    shutil.copy2(pkg_backup, pkg_path)
    pkg_backup.unlink(missing_ok=True)

    # Vérifier que commander est installé (dépendance clé du CLI)
    if not (src_dir / "node_modules" / "commander").exists():
        fatal("Installation des dépendances échouée : 'commander' absent de node_modules")

    success("Dépendances installées avec succès")


def step_install_deps_from_github(src_dir: Path, deps: dict) -> None:
    """Fallback : installe chaque dépendance depuis son tarball GitHub."""
    # Mapping npm package → GitHub tarball URL
    github_packages = {
        "commander": "https://github.com/tj/commander.js/archive/refs/tags/v{v}.tar.gz",
        "chalk": "https://github.com/chalk/chalk/archive/refs/tags/v{v}.tar.gz",
        "fs-extra": "https://github.com/jprichardson/node-fs-extra/archive/refs/tags/{v}.tar.gz",
        "glob": "https://github.com/isaacs/node-glob/archive/refs/tags/v{v}.tar.gz",
        "ignore": "https://github.com/kaelzhang/node-ignore/archive/refs/tags/{v}.tar.gz",
        "js-yaml": "https://github.com/nodeca/js-yaml/archive/refs/tags/{v}.tar.gz",
        "picocolors": "https://github.com/alexeyraspopov/picocolors/archive/refs/tags/v{v}.tar.gz",
        "semver": "https://github.com/npm/node-semver/archive/refs/tags/v{v}.tar.gz",
        "xml2js": "https://github.com/Leonidas-from-XIV/node-xml2js/archive/refs/tags/{v}.tar.gz",
        "yaml": "https://github.com/eemeli/yaml/archive/refs/tags/v{v}.tar.gz",
    }

    for pkg_name, version_spec in deps.items():
        # Extraire la version numérique du spec (^1.0.0 → 1.0.0)
        version = re.sub(r"[^0-9.]", "", version_spec).strip(".")
        clean_name = pkg_name.split("/")[-1]  # @scope/name → name

        if clean_name in github_packages:
            url = github_packages[clean_name].format(v=version)
            info(f"Installation de {pkg_name}@{version} depuis GitHub...")
            result = run(
                ["npm", "install", url, "--no-package-lock", "--no-save"],
                cwd=src_dir,
                check=False,
                capture=True,
                timeout=60,
            )
            if result.returncode != 0:
                warn(f"Échec pour {pkg_name} via GitHub tarball")
        else:
            warn(f"Pas de mapping GitHub pour {pkg_name}, ignoré")


def step_run_installer(
    src_dir: Path,
    project_dir: Path,
    *,
    modules: str,
    tools: str,
    comm_lang: str,
    doc_lang: str,
    user_name: str,
    output_folder: str,
) -> None:
    """Exécute l'installateur bmad-method CLI."""
    cli_path = src_dir / "tools" / "cli" / "bmad-cli.js"
    if not cli_path.exists():
        fatal(f"CLI introuvable : {cli_path}")

    cmd = [
        "node", str(cli_path), "install",
        "--directory", str(project_dir),
        "--modules", modules,
        "--tools", tools,
        "--communication-language", comm_lang,
        "--document-output-language", doc_lang,
        "--user-name", user_name,
        "--output-folder", output_folder,
        "--yes",
    ]

    run(cmd, cwd=src_dir, timeout=120)
    success("Installateur bmad-method exécuté avec succès")


def step_fix_configs(project_dir: Path, user_name: str, output_folder: str) -> None:
    """Corrige les variables non résolues dans les fichiers de configuration."""
    fixes_applied = 0

    # Patterns à remplacer
    replacements = {
        "{{user_name}}": user_name,
        "{{output_folder}}": output_folder,
        "{output_folder}": output_folder,
    }

    # Fichiers à vérifier
    config_files = [
        project_dir / ".github" / "copilot-instructions.md",
        project_dir / "_bmad" / "core" / "config.yaml",
        project_dir / "_bmad" / "bmm" / "config.yaml",
    ]

    for config_file in config_files:
        if not config_file.exists():
            continue

        content = config_file.read_text(encoding="utf-8")
        original = content

        for pattern, replacement in replacements.items():
            content = content.replace(pattern, replacement)

        if content != original:
            config_file.write_text(content, encoding="utf-8")
            fixes_applied += 1
            info(f"Variables corrigées dans : {config_file.relative_to(project_dir)}")

    # Renommer le dossier {output_folder} si créé littéralement
    bad_folder = project_dir / "{output_folder}"
    good_folder = project_dir / output_folder
    if bad_folder.exists() and bad_folder.name == "{output_folder}":
        if good_folder.exists():
            # Fusionner le contenu
            for item in bad_folder.iterdir():
                target = good_folder / item.name
                if item.is_dir() and not target.exists():
                    shutil.copytree(item, target)
                elif item.is_file() and not target.exists():
                    shutil.copy2(item, target)
            shutil.rmtree(bad_folder, ignore_errors=True)
        else:
            bad_folder.rename(good_folder)
        fixes_applied += 1
        info(f"Dossier renommé : {{output_folder}} → {output_folder}")

    # Ajouter user_name et output_folder dans bmm/config.yaml si absents
    bmm_config = project_dir / "_bmad" / "bmm" / "config.yaml"
    if bmm_config.exists():
        content = bmm_config.read_text(encoding="utf-8")
        additions = []
        if "user_name:" not in content:
            additions.append(f"user_name: {user_name}")
        if "output_folder:" not in content:
            additions.append(f"output_folder: {output_folder}")
        if additions:
            # Insérer après la ligne project_name ou user_skill_level
            lines = content.splitlines(keepends=True)
            insert_idx = None
            for i, line in enumerate(lines):
                if line.startswith("project_name:") or line.startswith("user_skill_level:"):
                    insert_idx = i + 1
            if insert_idx is not None:
                for j, addition in enumerate(additions):
                    lines.insert(insert_idx + j, addition + "\n")
                bmm_config.write_text("".join(lines), encoding="utf-8")
                fixes_applied += 1

    if fixes_applied:
        success(f"{fixes_applied} correction(s) appliquée(s)")
    else:
        success("Aucune correction nécessaire")


def step_cleanup(project_dir: Path) -> None:
    """Supprime le dossier temporaire de sources."""
    src_dir = project_dir / TEMP_DIR_NAME
    if src_dir.exists():
        info("Nettoyage du dossier temporaire...")
        shutil.rmtree(src_dir, ignore_errors=True)
        success("Dossier temporaire supprimé")


def step_verify(project_dir: Path) -> None:
    """Vérifie que l'installation est complète."""
    checks = [
        ("_bmad/core/config.yaml", "Configuration core"),
        ("_bmad/bmm/config.yaml", "Configuration BMM"),
        ("_bmad/_config/agent-manifest.csv", "Manifeste agents"),
        ("_bmad/_config/workflow-manifest.csv", "Manifeste workflows"),
    ]

    all_ok = True
    for rel_path, label in checks:
        path = project_dir / rel_path
        if path.exists():
            success(f"{label} : OK")
        else:
            error(f"{label} : MANQUANT ({rel_path})")
            all_ok = False

    # Compter les agents et prompts selon l'IDE
    for agents_dir in [".github/agents", ".claude/commands", ".cursor/commands"]:
        path = project_dir / agents_dir
        if path.exists():
            count = len(list(path.glob("*.md")))
            success(f"{agents_dir} : {count} fichier(s)")
            break

    prompts_dir = project_dir / ".github" / "prompts"
    if prompts_dir.exists():
        count = len(list(prompts_dir.glob("*.md")))
        success(f".github/prompts : {count} fichier(s)")

    if all_ok:
        print()
        success(_c(Colors.GREEN + Colors.BOLD, "Installation BMad Method terminée avec succès !"))
    else:
        print()
        warn("Installation partielle — certains fichiers sont manquants.")


# ── Main ────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Installe BMad Method en contournant les blocages proxy npm.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python install_bmad.py
  python install_bmad.py --tools claude-code --lang English
  python install_bmad.py --modules bmm,bmb --tools cursor
  python install_bmad.py --mirror https://registry.npmmirror.com
  python install_bmad.py --dry-run
        """,
    )
    parser.add_argument(
        "--directory", "-d",
        type=Path,
        default=Path.cwd(),
        help="Répertoire cible du projet (défaut: répertoire courant)",
    )
    parser.add_argument(
        "--modules", "-m",
        default="bmm",
        help="Modules à installer, séparés par des virgules (défaut: bmm)",
    )
    parser.add_argument(
        "--tools", "-t",
        default="github-copilot",
        help="IDE/outil à configurer : github-copilot, claude-code, cursor, windsurf, none (défaut: github-copilot)",
    )
    parser.add_argument(
        "--lang",
        default="French",
        help="Langue de communication et des documents (défaut: French)",
    )
    parser.add_argument(
        "--user-name",
        default=None,
        help="Nom utilisateur pour les agents (défaut: utilisateur système)",
    )
    parser.add_argument(
        "--output-folder",
        default=OUTPUT_FOLDER_DEFAULT,
        help=f"Dossier de sortie (défaut: {OUTPUT_FOLDER_DEFAULT})",
    )
    parser.add_argument(
        "--mirror",
        default=None,
        help="URL du miroir npm à utiliser (détection auto si non spécifié)",
    )
    parser.add_argument(
        "--version",
        default=BMAD_VERSION,
        dest="bmad_version",
        help=f"Version de BMAD-METHOD à installer (défaut: {BMAD_VERSION})",
    )
    parser.add_argument(
        "--keep-source",
        action="store_true",
        help="Conserve le dossier source cloné après installation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les étapes sans les exécuter",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    banner()

    project_dir = args.directory.resolve()
    user_name = args.user_name or getpass.getuser()

    info(f"Projet cible      : {project_dir}")
    info(f"Modules            : {args.modules}")
    info(f"Outil/IDE          : {args.tools}")
    info(f"Langue             : {args.lang}")
    info(f"Utilisateur        : {user_name}")
    info(f"Dossier de sortie  : {args.output_folder}")
    print()

    if args.dry_run:
        warn("Mode dry-run — aucune action effectuée.")
        print()
        info("Étapes qui seraient exécutées :")
        info("  1. Vérifier les prérequis (git, node >= 20, npm)")
        info("  2. Tester la connectivité npm")
        info("  3. Trouver un miroir npm fonctionnel")
        info(f"  4. Cloner {BMAD_REPO}")
        info("  5. Installer les dépendances via le miroir")
        info("  6. Exécuter l'installateur bmad-method CLI")
        info("  7. Corriger les variables non résolues")
        info("  8. Nettoyer le dossier temporaire")
        info("  9. Vérifier l'installation")
        return

    # ── Étape 1 : Prérequis ──
    print(_c(Colors.BOLD, "  [1/7] Vérification des prérequis"))
    check_prerequisites()
    print()

    # ── Étape 2 : Connectivité & miroir ──
    print(_c(Colors.BOLD, "  [2/7] Résolution du registre npm"))
    mirror = args.mirror
    if not mirror:
        blocked = detect_npm_blocked()
        if blocked:
            mirror = find_working_mirror()
            if not mirror:
                fatal(
                    "Aucun miroir npm fonctionnel trouvé.\n"
                    "  Essayez de spécifier un miroir manuellement : --mirror <URL>\n"
                    "  Ou vérifiez votre connexion réseau / configuration proxy."
                )
        else:
            mirror = "https://registry.npmjs.org"
    info(f"Registre npm utilisé : {mirror}")
    print()

    # ── Étape 3 : Clone ──
    print(_c(Colors.BOLD, "  [3/7] Clonage du repo BMAD-METHOD"))
    src_dir = step_clone(project_dir, tag=args.bmad_version)
    print()

    try:
        # ── Étape 4 : Dépendances ──
        print(_c(Colors.BOLD, "  [4/7] Installation des dépendances Node.js"))
        step_install_deps(src_dir, mirror)
        print()

        # ── Étape 5 : Installation ──
        print(_c(Colors.BOLD, "  [5/7] Exécution de l'installateur BMad"))
        step_run_installer(
            src_dir,
            project_dir,
            modules=args.modules,
            tools=args.tools,
            comm_lang=args.lang,
            doc_lang=args.lang,
            user_name=user_name,
            output_folder=args.output_folder,
        )
        print()

        # ── Étape 6 : Corrections ──
        print(_c(Colors.BOLD, "  [6/7] Correction des configurations"))
        step_fix_configs(project_dir, user_name, args.output_folder)
        print()

    finally:
        # ── Étape 7 : Nettoyage ──
        if not args.keep_source:
            print(_c(Colors.BOLD, "  [7/7] Nettoyage"))
            step_cleanup(project_dir)
        else:
            info(f"Sources conservées dans : {src_dir}")
        print()

    # ── Vérification finale ──
    print(_c(Colors.BOLD, "  Vérification de l'installation"))
    step_verify(project_dir)

    print()
    info("Pour commencer : tapez /bmad-help dans Copilot Chat")
    print()


if __name__ == "__main__":
    main()
