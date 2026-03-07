# AIDE — AI Development Engine

> **AIDE** (AI Development Engine) orchestre 17 agents IA spécialisés pour développer un projet de bout en bout :
> conception → architecture → planification → développement → tests → analyse → intégration → documentation.

## Démarrage Rapide

### Déployer AIDE sur un projet cible

```bash
# Cloner ce dépôt
git clone https://github.com/olahouze/IA-Developpement-Workflow-IDE.git
cd IA-Developpement-Workflow-IDE
uv sync

# Déployer AIDE dans un projet local
python deploy.py /chemin/vers/mon-projet

# Déployer uniquement les agents Copilot (sans le moteur Python)
python deploy.py /chemin/vers/mon-projet --copilot-only

# Déployer dans un repo Git distant
python deploy.py https://gitlab.example.com/org/repo.git --branch feat/aide
```

### Utiliser AIDE dans le projet cible

Ouvrir le projet cible dans VS Code, puis dans Copilot Chat :

```
/AIDE-workflow-init              → Initialiser le workspace .ai-workflow/
/AIDE-workflow-vierge            → Nouveau projet (14 étapes)
/AIDE-workflow-existant          → Enrichir un projet existant (10 étapes)
/AIDE-workflow-feature           → Ajouter une feature (7 étapes)
/AIDE-workflow-status            → Voir l'état courant
```

Les agents sont disponibles via `@AIDE-` dans le menu agents Copilot :

```
@AIDE-brainstormer               → Facilitateur créatif
@AIDE-developpeur                → Implémente le code
@AIDE-testeur                    → Écrit les tests
@AIDE-analyseur-secu             → Analyse sécurité (OWASP)
...et 13 autres
```

## Structure du Projet

```
IA-Developpement-Workflow-IDE/
├── bundle/                             # Produit AIDE livrable
│   ├── .github/
│   │   ├── agents/                    # 17 fichiers AIDE-*.agent.md
│   │   ├── prompts/                   # 5 fichiers AIDE-workflow-*.prompt.md
│   │   └── copilot-instructions.md    # Instructions Copilot (avec placeholders)
│   └── .ai-workflow/                  # Template structure du workspace
├── engine/                             # Moteur d'exécution Python (optionnel)
│   ├── src/ai_workflow/               # Code source
│   │   ├── cli.py                     # CLI Typer (ai-workflow)
│   │   ├── agents/definitions/        # 17 agents (YAML + Jinja2)
│   │   ├── workflows/                 # 3 workflows (YAML state machines)
│   │   ├── engine/                    # WorkflowEngine, AgentRunner, ForkJoin
│   │   ├── managers/                  # File, Memory, Skill, Context
│   │   ├── models/                    # Agent, Workflow, Verdict, Profile
│   │   └── templates/                 # Templates Jinja2
│   └── tests/                         # 138 tests pytest
├── deploy.py                          # Script de déploiement vers projet cible
├── scripts/generate_bundle.py         # Génération du bundle depuis engine/
├── docs/                              # Documentation
│   ├── Agents.md                      # Catalog des 17 agents AIDE
│   ├── Architecture.md                # Architecture détaillée
│   ├── Workflow.md                    # Workflows AIDE
│   ├── Deployment.md                  # Guide de déploiement
│   └── BMAD-AIDE-Coexistence.md       # Séparation BMAD/AIDE
├── _bmad/                             # Framework BMAD (développement interne)
└── pyproject.toml                     # Configuration projet
```

## Deux Modes d'Exécution

### Mode Copilot Natif (recommandé)

Les fichiers `.agent.md` et `.prompt.md` sont **complètement autonomes**. Aucun runtime Python n'est nécessaire. L'utilisateur interagit via Copilot Chat :
- `/AIDE-workflow-*` lance un workflow pas-à-pas guidé par Copilot
- `@AIDE-*` invoque un agent spécialisé dans la conversation

### Mode Engine Python (orchestration automatisée)

Pour une orchestration avancée avec machine à états, parallélisation fork/join et verdicts automatisés :

```bash
cd mon-projet-cible
uv sync
ai-workflow run --workflow vierge
```

## Agents AIDE (17)

| Agent | Rôle | Phase |
|---|---|---|
| `@AIDE-brainstormer` | Facilitateur créatif — clarifie la vision | Conception |
| `@AIDE-arch-produit` | Architecture produit haut niveau | Conception |
| `@AIDE-arch-metier` | Architecture métier — domaine, règles business | Conception |
| `@AIDE-arch-gui` | Architecture GUI — interfaces, navigation | Conception |
| `@AIDE-arch-technique` | Architecture technique — stack, patterns | Conception |
| `@AIDE-cartographe` | Scanne le repo, construit le profil projet | Approvisionnement |
| `@AIDE-orchestrateur` | Décompose en US, crée des batches parallèles | Orchestration |
| `@AIDE-magazinier` | Enrichit avec skills/instructions externes | Approvisionnement |
| `@AIDE-developpeur` | Implémente le code de l'US | Construction |
| `@AIDE-testeur` | Écrit et maintient les tests | Construction |
| `@AIDE-analyseur-secu` | Analyse sécurité OWASP (verdict **bloquant**) | Analyse |
| `@AIDE-analyseur-perf` | Analyse performance (verdict **bloquant**) | Analyse |
| `@AIDE-analyseur-bp` | Analyse bonnes pratiques (verdict non-bloquant) | Analyse |
| `@AIDE-integrateur` | Cohérence inter-US (read-only) | Intégration |
| `@AIDE-fixeur-integration` | Corrige les incohérences inter-US | Intégration |
| `@AIDE-documentaliste` | Documentation technique et utilisateur globale | Finalisation |
| `@AIDE-agent-memoire` | Gardien de la mémoire collective | Transversal |

## Workflows AIDE (3 + 2 utilitaires)

| Commande | Description | États |
|---|---|---|
| `/AIDE-workflow-vierge` | Projet complet : conception → livraison | 14 |
| `/AIDE-workflow-existant` | Enrichir un projet existant | 10 |
| `/AIDE-workflow-feature` | Ajouter une feature | 7 |
| `/AIDE-workflow-init` | Initialiser `.ai-workflow/` | — |
| `/AIDE-workflow-status` | État courant du workflow | — |

## Cycle de Développement par User Story

```
Pour chaque US dans un batch :
1. @AIDE-developpeur      → implémente le code
2. @AIDE-testeur           → écrit les tests
3. @AIDE-analyseur-secu  ┐
   @AIDE-analyseur-perf  ├→ en parallèle
   @AIDE-analyseur-bp    ┘
4. Verdict :
   - Tous PASS              → US validée
   - FAIL bloquant          → retour dev (max 4 itérations)
   - Seul FAIL BP           → US validée quand même
   - ≥ 4 itérations         → ESCALADE manuelle
5. @AIDE-agent-memoire    → collecte les découvertes
```

## Déploiement

```bash
# Déploiement complet (Copilot + Engine Python)
python deploy.py ./mon-projet

# Copilot uniquement (agents + workflows, sans Python)
python deploy.py ./mon-projet --copilot-only

# Repo Git distant
python deploy.py https://gitlab.example.com/org/repo.git

# Aperçu sans modifier
python deploy.py ./mon-projet --dry-run
```

Options :
- `--copilot-only` : Ne déploie que `.github/` (agents, prompts, instructions)
- `--branch` : Branche Git (défaut: `feat/ai-workflow-engine`)
- `--project-name` : Nom du projet (défaut: nom du dossier)
- `--user-name` : Nom utilisateur (défaut: utilisateur système)
- `--lang` : Langue (défaut: `French`)
- `--dry-run` : Aperçu sans exécution

Voir [docs/Deployment.md](docs/Deployment.md) pour le guide complet.

## Documentation

- [Agents.md](docs/Agents.md) — Catalog des 17 agents AIDE
- [Workflow.md](docs/Workflow.md) — Détails des workflows et du cycle de développement
- [Architecture.md](docs/Architecture.md) — Architecture technique et modes d'exécution
- [Deployment.md](docs/Deployment.md) — Guide de déploiement vers un projet cible
- [BMAD-AIDE-Coexistence.md](docs/BMAD-AIDE-Coexistence.md) — Séparation BMAD/AIDE dans ce dépôt

## Tests

```bash
uv run pytest -v                    # 138 tests
uv run pytest --cov=src/ai_workflow --cov-report=html
```

## Statistiques

| Métrique | Valeur |
|---|---|
| **Version** | 0.1.0 |
| **Agents AIDE** | 17 |
| **Workflows AIDE** | 3 + 2 utilitaires |
| **Tests** | 138 (81% coverage) |
| **Python** | ≥ 3.11 |
| **Mode Copilot** | Autonome (pas de runtime Python requis) |

---

**AIDE v0.1.0** — AI Development Engine