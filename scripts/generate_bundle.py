#!/usr/bin/env python3
"""
generate_bundle.py — Génère les fichiers Copilot du bundle AIDE depuis les définitions engine.

Usage:
  python scripts/generate_bundle.py
  python scripts/generate_bundle.py --dry-run

Lit les définitions d'agents dans engine/src/ai_workflow/agents/definitions/
et les workflows dans engine/src/ai_workflow/workflows/ pour générer :
  - bundle/.github/agents/AIDE-*.agent.md
  - bundle/.github/prompts/AIDE-workflow-*.prompt.md
  - bundle/.github/copilot-instructions.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENGINE_AGENTS_DIR = PROJECT_ROOT / "engine" / "src" / "ai_workflow" / "agents" / "definitions"
ENGINE_WORKFLOWS_DIR = PROJECT_ROOT / "engine" / "src" / "ai_workflow" / "workflows"
BUNDLE_DIR = PROJECT_ROOT / "bundle" / ".github"

PREFIX = "AIDE"

# Mapping phase → description lisible
PHASE_FR = {
    "conception": "Conception",
    "approvisionnement": "Approvisionnement",
    "orchestration": "Orchestration",
    "construction": "Construction",
    "analyse": "Analyse",
    "integration": "Intégration",
    "finalisation": "Finalisation",
    "transversal": "Transversal",
}


def load_agent_definitions() -> list[dict]:
    """Charge toutes les définitions d'agents depuis le moteur."""
    agents = []
    for agent_dir in sorted(ENGINE_AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        def_path = agent_dir / "definition.yaml"
        if not def_path.exists():
            continue

        with open(def_path, encoding="utf-8") as f:
            definition = yaml.safe_load(f)

        instructions = ""
        instr_path = agent_dir / "instructions.md"
        if instr_path.exists():
            instructions = instr_path.read_text(encoding="utf-8")

        output_template = ""
        out_path = agent_dir / "output_template.md"
        if out_path.exists():
            output_template = out_path.read_text(encoding="utf-8")

        agents.append({
            "definition": definition,
            "instructions": instructions,
            "output_template": output_template,
        })
    return agents


def load_workflows() -> list[dict]:
    """Charge les workflows YAML depuis le moteur."""
    workflows = []
    for wf_path in sorted(ENGINE_WORKFLOWS_DIR.glob("workflow_*.yaml")):
        with open(wf_path, encoding="utf-8") as f:
            workflows.append(yaml.safe_load(f))
    return workflows


def generate_agent_md(agent_data: dict) -> str:
    """Génère le contenu .agent.md standalone pour un agent."""
    d = agent_data["definition"]
    name = d["name"]
    display_name = d["display_name"]
    role = d["role"]
    phase = PHASE_FR.get(d.get("phase", ""), d.get("phase", ""))
    optional = d.get("optional", False)
    interactive = d.get("interactive", False)
    deps = d.get("dependencies", [])
    permissions = d.get("permissions", [])

    tools = ["read", "editFiles", "search"]
    if interactive or "modify_code" in permissions:
        tools.append("terminalLastCommand")

    # Clean Jinja2 from instructions (replace with static text)
    instructions = agent_data["instructions"]
    instructions = _clean_jinja(instructions)

    output_template = agent_data["output_template"]
    output_template = _clean_jinja(output_template)

    # Build description
    desc = f"{display_name} — {role}"
    if len(desc) > 120:
        desc = desc[:117] + "..."

    lines = [
        "---",
        f"description: '{_escape_yaml(desc)}'",
        f"tools: {tools}",
        "---",
        "",
        f"# Agent {PREFIX} — {display_name}",
        "",
        f"Tu es le **{display_name}**.",
        "",
        "## Identité",
        "",
        f"- **Nom** : {display_name}",
        f"- **Phase** : {phase}",
    ]

    if optional:
        lines.append(f"- **Optionnel** : Oui")
    if interactive:
        lines.append(f"- **Mode** : Interactif")
    if deps:
        lines.append(f"- **Dépendances** : {', '.join(deps)}")

    perm_labels = {
        "read_md": "Lecture markdown",
        "create_md": "Créer des fichiers markdown",
        "modify_code": "Modifier le code",
        "add_config": "Ajouter des configurations",
        "update_config": "Mettre à jour des configurations",
    }
    perm_str = ", ".join(perm_labels.get(p, p) for p in permissions)
    lines.append(f"- **Permissions** : {perm_str}")

    lines.extend([
        "",
        "## Instructions",
        "",
        instructions.strip(),
        "",
        "## Format de sortie",
        "",
        output_template.strip(),
    ])

    return "\n".join(lines) + "\n"


def _clean_jinja(text: str) -> str:
    """Supprime les blocs Jinja2 et remplace par du texte statique."""
    import re
    # Remove {% ... %} blocks
    text = re.sub(r"\{%.*?%\}", "", text, flags=re.DOTALL)
    # Replace {{ ... }} with placeholder
    text = re.sub(r"\{\{.*?\}\}", "(variable)", text)
    # Clean up empty lines left by Jinja removal
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _escape_yaml(text: str) -> str:
    """Échappe les apostrophes pour YAML single-quoted string."""
    return text.replace("'", "''")


def generate_copilot_instructions(agents: list[dict], workflows: list[dict]) -> str:
    """Génère le copilot-instructions.md depuis les données du moteur."""
    agent_rows = []
    for a in agents:
        d = a["definition"]
        name = d["name"]
        role = d["role"]
        phase = PHASE_FR.get(d.get("phase", ""), d.get("phase", ""))
        optional = "Optionnel" if d.get("optional") else ""

        # Determine blocking status for analyzers
        blocking = ""
        if "analyseur" in name:
            if name == "analyseur-bp":
                blocking = "Non-bloquant"
            else:
                blocking = "Bloquant"
        if optional:
            blocking = optional

        agent_rows.append(f"| `@{PREFIX}-{name}` | {role} | {phase} | {blocking} |")

    wf_rows = []
    for wf in workflows:
        name = wf.get("name", "")
        desc = wf.get("description", "")
        state_count = len(wf.get("states", []))
        wf_rows.append(f"| {name} | `/{PREFIX}-workflow-{wf.get('type', name)}` | {desc} | {state_count} états |")

    return f"""<!-- {PREFIX}:START -->
# {PREFIX} — AI Development Engine

> **{PREFIX}** orchestre 17 agents IA spécialisés pour développer un projet de bout en bout.

## Configuration

- **Projet** : @@PROJECT_NAME@@
- **Utilisateur** : @@USER_NAME@@
- **Langue** : @@LANG@@

## Runtime

- **Répertoire de travail** : `.ai-workflow/`
- **État** : `.ai-workflow/state.json`
- **Rapports** : `.ai-workflow/reports/` et `.ai-workflow/us/<US_ID>/`
- **Profil projet** : `.ai-workflow/profil_projet.md`
- **Skills** : `.ai-workflow/skills/`

## Agents disponibles

| Agent | Rôle | Phase | Bloquant |
|---|---|---|---|
{chr(10).join(agent_rows)}

## Workflows disponibles

| Workflow | Commande | Description | États |
|---|---|---|---|
{chr(10).join(wf_rows)}

## Commandes utilitaires

| Commande | Description |
|---|---|
| `/{PREFIX}-workflow-init` | Initialiser `.ai-workflow/` et choisir le workflow |
| `/{PREFIX}-workflow-status` | Afficher l'état courant |

## Conventions

### Cycle de développement par US

1. `@{PREFIX}-developpeur` implémente
2. `@{PREFIX}-testeur` écrit les tests
3. 3 analyseurs en parallèle (sécu, perf, bp)
4. Verdict : PASS → suivant, FAIL bloquant → retry (max 4), ESCALADE si ≥ 4

### Mémoire

- Section "Découvertes pour mémoire" dans chaque rapport
- `@{PREFIX}-agent-memoire` collecte et déduplique
- Le développeur fait foi intra-US
- Profil projet ≤ 500 lignes

## Slash Commands

Tapez `/{PREFIX}-` pour voir les workflows. Les agents sont disponibles via `@{PREFIX}-`.
<!-- {PREFIX}:END -->
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Génère le bundle AIDE depuis les définitions engine.")
    parser.add_argument("--dry-run", action="store_true", help="Affiche les fichiers sans les écrire")
    args = parser.parse_args()

    if not ENGINE_AGENTS_DIR.exists():
        print(f"Erreur : dossier agents introuvable : {ENGINE_AGENTS_DIR}", file=sys.stderr)
        sys.exit(1)

    agents = load_agent_definitions()
    workflows = load_workflows()

    print(f"Agents trouvés : {len(agents)}")
    print(f"Workflows trouvés : {len(workflows)}")

    # Generate agent .agent.md files
    agents_dir = BUNDLE_DIR / "agents"
    for agent_data in agents:
        name = agent_data["definition"]["name"]
        filename = f"{PREFIX}-{name}.agent.md"
        content = generate_agent_md(agent_data)

        if args.dry_run:
            print(f"  [dry-run] {filename} ({len(content)} chars)")
        else:
            agents_dir.mkdir(parents=True, exist_ok=True)
            (agents_dir / filename).write_text(content, encoding="utf-8")
            print(f"  ✓ {filename}")

    # Generate copilot-instructions.md
    instructions_content = generate_copilot_instructions(agents, workflows)
    instructions_path = BUNDLE_DIR / "copilot-instructions.md"

    if args.dry_run:
        print(f"  [dry-run] copilot-instructions.md ({len(instructions_content)} chars)")
    else:
        BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
        instructions_path.write_text(instructions_content, encoding="utf-8")
        print(f"  ✓ copilot-instructions.md")

    print(f"\nBundle généré : {len(agents)} agents + copilot-instructions.md")
    if not args.dry_run:
        print(f"  → {BUNDLE_DIR}")


if __name__ == "__main__":
    main()
