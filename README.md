# AI Workflow Engine — IDE Développement d'Agents IA

> Moteur d'orchestration et d'exécution de workflows avec agents IA spécialisés, inspiré par la méthode BMAD (Business Modelling & Agency Design).

## 🚀 Démarrage Rapide

### Installation

```bash
# Cloner le projet
git clone https://gitlab.example.com/olahouze/IA-Developpement-Workflow-IDE.git
cd IA-Developpement-Workflow-IDE

# Installer les dépendances
uv sync

# Initialiser un projet
ai-workflow init --name mon-projet-exemple
```

### Utilisation basique

```bash
# Lister les agents disponibles
ai-workflow agents

# Voir l'état d'un workflow
ai-workflow status

# Exécuter un workflow
ai-workflow run --workflow brainstorming
```

## 📁 Structure du Projet

```
IA-Developpement-Workflow-IDE/
├── src/ai_workflow/                    # Code source principal
│   ├── cli.py                         # Interface ligne de commande (Typer)
│   ├── config/
│   │   ├── defaults.yaml              # Configuration par défaut
│   │   └── schema.py                  # Pydantic models de configuration
│   ├── models/                        # Modèles de données
│   │   ├── agent.py                  # Définition d'un agent
│   │   ├── workflow.py                # Définition d'un workflow
│   │   ├── verdict.py                 # Verdict d'exécution
│   │   └── profile.py                 # Profils utilisateur
│   ├── managers/                      # Gestionnaires métier
│   │   ├── file_manager.py            # Gestion des fichiers
│   │   ├── memory_manager.py          # Gestion de la mémoire
│   │   ├── skill_manager.py           # Gestion des compétences
│   │   └── context_builder.py         # Construction du contexte
│   ├── engine/                        # Moteur d'exécution
│   │   ├── workflow_engine.py         # Orchestration des workflows
│   │   ├── agent_runner.py            # Exécution des agents
│   │   ├── fork_join.py               # Pattern fork/join pour parallélisation
│   │   └── verdict.py                 # Logique de verdict
│   ├── agents/                        # 17 agents spécialisés
│   │   ├── registry.py               # Registre centralisé des agents
│   │   └── [agent-name]/             # Dossier par agent
│   │       ├── config.yaml           # Configuration de l'agent
│   │       ├── system_prompt.md      # Prompt système
│   │       └── tools.yaml            # Outils disponibles
│   ├── workflows/                     # Définitions de workflows
│   │   ├── brainstorming.yaml        # Workflow brainstorming
│   │   ├── party-mode.yaml           # Workflow collaboratif
│   │   └── advanced-elicitation.yaml # Workflow avancé
│   ├── templates/                     # Templates Jinja2
│   │   ├── agent_prompt.j2           # Template prompt agent
│   │   ├── workflow_summary.j2       # Résumé workflow
│   │   └── memory_snapshot.j2        # Snapshot mémoire
│   └── __init__.py                   # Package initialization
├── bundle/                             # Assets de déploiement
│   ├── pyproject.toml                # Config for distributed projects
│   └── README.md                     # docs utilisateur déployées
├── docs/                              # Documentation
│   ├── Architecture.md                # Architecture détaillée
│   ├── Workflow.md                    # Explication des workflows
│   ├── Agents.md                      # Catalog des 17 agents
│   └── DeploymentGuide.md            # Guide de déploiement
├── tests/                             # Suites de tests (pytest)
│   ├── conftest.py                   # Fixtures pytest
│   ├── test_models/                  # Tests modèles
│   ├── test_managers/                # Tests managers
│   ├── test_engine/                  # Tests moteur
│   ├── test_agents/                  # Tests agents
│   ├── test_workflows/               # Tests workflows
│   └── test_cli.py                   # Tests CLI
├── deploy.py                          # Script de déploiement vers Git/dossier
├── pyproject.toml                     # Config projet (uv + pytest + ruff)
└── README.md                          # Ce fichier
```

## 🏗️ Architecture

Le moteur fonctionne selon une architecture modulaire en 4 couches :

### 1. **Modèles de Données** (`models/`)
- `Agent` : Représentation d'un agent IA spécialisé
- `Workflow` : Orchestration d'agents en séquence/parallèle
- `Verdict` : Résultat d'exécution (success/partial/error)
- `Profile` : Profil utilisateur et préférences

### 2. **Managers** (`managers/`)
Gestionnaires métier pour les ressources partagées :
- **FileManager** : I/O fichiers, cache, artifacts
- **MemoryManager** : Mémoire persistante (contexte, historique)
- **SkillManager** : Compétences et outils disponibles pour les agents
- **ContextBuilder** : Construit le contexte d'exécution (variables, secrets)

### 3. **Moteur d'Exécution** (`engine/`)
- **WorkflowEngine** : Orchestre les workflows (état, transitions, erreurs)
- **AgentRunner** : Exécute un agent unique avec un contexte
- **ForkJoin** : Pattern parallélisation (plusieurs agents en parallèle, attendre sync)
- **Verdict** : Évalue succès/échec/partiel d'une exécution

### 4. **Agents Spécialisés** (`agents/`)
17 agents avec rôles distincts : brainstormer, analyst, architect, developer, PM, QA, tech-writer, UX designer, scrum master, etc.

## 🤖 Agents Disponibles (15 au total)

| Agent | Rôle | Accès |
|---|---|---|
| **BMAD Master** | Orchestration | [docs/agents/bmad-master.md](docs/agents/bmad-master.md) |
| **Analyst** (Mary) | Business Analysis | [docs/agents/analyst.md](docs/agents/analyst.md) |
| **Researcher** | Deep exploration | [docs/agents/researcher.md](docs/agents/researcher.md) |
| **Product Manager** (John) | PRD & strategy | [docs/agents/product-manager.md](docs/agents/product-manager.md) |
| **UX Designer** (Sally) | Design & research | [docs/agents/ux-designer.md](docs/agents/ux-designer.md) |
| **Architect** (Winston) | System design | [docs/agents/architect.md](docs/agents/architect.md) |
| **Developer** (Amelia) | Implementation | [docs/agents/developer.md](docs/agents/developer.md) |
| **QA Engineer** (Quinn) | Testing | [docs/agents/qa.md](docs/agents/qa.md) |
| **Security Expert** | Compliance & audit | [docs/agents/security.md](docs/agents/security.md) |
| **Tech Writer** (Paige) | Documentation | [docs/agents/tech-writer.md](docs/agents/tech-writer.md) |
| **Testing Specialist** | Test strategy | [docs/agents/testing-specialist.md](docs/agents/testing-specialist.md) |
| **Code Reviewer** | Code quality | [docs/agents/code-reviewer.md](docs/agents/code-reviewer.md) |
| **DevOps Engineer** | Infrastructure & CI/CD | [docs/agents/devops.md](docs/agents/devops.md) |
| **Scrum Master** (Bob) | Agile ceremonies | [docs/agents/scrum-master.md](docs/agents/scrum-master.md) |
| **Quick Flow Solo Dev** (Barry) | MVP rapid | [docs/agents/quick-flow-solo-dev.md](docs/agents/quick-flow-solo-dev.md) |

👉 **[Catalog complet](docs/Agents.md) avec workflows et bonnes pratiques.**

## 🔄 Workflows Disponibles

### 1. **Brainstorming** (`workflows/brainstorming.yaml`)
Séquence : Analyst → Architect → Developer
- Analyzer analyse les requirements
- Architect designs la solution
- Developer propose l'implémentation

### 2. **Party Mode** (`workflows/party-mode.yaml`)
Collaboration parallèle d'experts :
- PM, UX Designer, Architect, Developer exécutés **en parallèle**
- Sync final sur les decisions
- Pattern: fork/join

### 3. **Advanced Elicitation** (`workflows/advanced-elicitation.yaml`)
Approche profonde de découverte :
- Analyst → Researcher → PM → UX Designer (séquence + feedback loops)
- Itération sur les insights

👉 **Voir [docs/Workflow.md](docs/Workflow.md) pour les détails d'exécution.**

## 🚀 Déploiement

Le projet inclut un script de déploiement à la racine : **`deploy.py`**

### Déployer dans un dossier local
```bash
python deploy.py ./mon-projet-cible
```
Copie `src/ai_workflow/`, `pyproject.toml`, `README.md`, `tests/` vers la cible.

### Déployer dans un repo Git (GitLab/GitHub)
```bash
python deploy.py https://gitlab.example.com/org/repo.git \
  --branch feat/ai-workflow-engine
```
- Clone le repo
- Crée une branche personnalisée
- Push les fichiers
- (Demande un token GitLab si auth échoue)

Options :
- `--branch` : Nom de branche (défaut: `feat/ai-workflow-engine`)
- `--dry-run` : Affiche sans exécuter

## 📚 Documentation Complète

- **[Architecture.md](docs/Architecture.md)** — Détails techniques, patterns, décisions
- **[Workflow.md](docs/Workflow.md)** — Exécution des workflows, état, transitions
- **[Agents.md](docs/Agents.md)** — Catalog de chaque agent, prompts, skillets
- **[DeploymentGuide.md](docs/DeploymentGuide.md)** — Guide déploiement avancé

## 🧪 Tests

```bash
# Lancer tous les tests (138 tests, 81% coverage)
uv run pytest -v

# Coverage détaillé
uv run pytest --cov=src/ai_workflow --cov-report=html

# Tests spécifiques
uv run pytest tests/test_engine/test_workflow_engine.py -v
```

## 🔧 Configuration

### Fichier `pyproject.toml`

```toml
[project]
name = "ai-workflow-engine"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
ai-workflow = "ai_workflow.cli:app"  # CLI entry point
```

### Dépendances principales

- **typer** + **rich** : Interface CLI interactive
- **transitions** : State machine (workflows)
- **pydantic** : Validation models
- **jinja2** : Rendering templates
- **pyyaml** : Configuration YAML
- **pytest** : Framework tests
- **ruff** : Linting/formatting

## 🎯 Intégration Continue

Tout code pushé doit :
1. ✅ Passer `ruff check` (linting)
2. ✅ Passer `pytest` (138 tests)
3. ✅ Maintenir ≥81% coverage

```bash
# Pre-commit local
uv run ruff check src/ tests/
uv run pytest
```

## 📝 Contribution

Pour contribuer :
1. Créer une branche `feat/` ou `fix/`
2. Ajouter tests pour les changements
3. Lancer `uv run ruff check --fix` avant commit
4. Pousser vers GitLab

## 📦 Bundle & Distribution

Le dossier `bundle/` contient les artifacts de production :
- `pyproject.toml` : Config déployée (sans dev deps)
- `README.md` : Docs utilisateur simplifiées

Utilisé par `deploy.py` pour distribuer le moteur vers des projets cibles.

## 📊 Statistiques du Projet

- **Lines of Code** : ~3500 (source) + ~2000 (tests)
- **Test Coverage** : 81%
- **Agents** : 17 spécialisés
- **Workflows** : 3 orchestrations
- **Python** : ≥3.11
- **Package Manager** : uv
- **Linter** : ruff
- **Framework CLI** : Typer

## 🤝 Support & Contact

Pour questions ou bugs :
- 🜔 **GitLab Issues** : [Create issue](https://gitlab.example.com/olahouze/IA-Developpement-Workflow-IDE/-/issues)
- 📧 **Contact** : B68682@placide-cloud.fr

---

**Version 0.1.0** — Basé sur BMAD Method (Business Modelling & Agency Design)