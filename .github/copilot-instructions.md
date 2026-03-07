<!-- BMAD:START -->
# BMAD Method — Project Instructions

## Project Configuration

- **Project**: IA-Developpement-Workflow-IDE
- **User**: B68682
- **Communication Language**: French
- **Document Output Language**: French
- **User Skill Level**: intermediate
- **Output Folder**: _bmad-output
- **Planning Artifacts**: {project-root}/_bmad-output/planning-artifacts
- **Implementation Artifacts**: {project-root}/_bmad-output/implementation-artifacts
- **Project Knowledge**: {project-root}/docs

## BMAD Runtime Structure

- **Agent definitions**: `_bmad/bmm/agents/` (BMM module) and `_bmad/core/agents/` (core)
- **Workflow definitions**: `_bmad/bmm/workflows/` (organized by phase)
- **Core tasks**: `_bmad/core/tasks/` (help, editorial review, indexing, sharding, adversarial review)
- **Core workflows**: `_bmad/core/workflows/` (brainstorming, party-mode, advanced-elicitation)
- **Workflow engine**: `_bmad/core/tasks/workflow.xml` (executes YAML-based workflows)
- **Module configuration**: `_bmad/bmm/config.yaml`
- **Core configuration**: `_bmad/core/config.yaml`
- **Agent manifest**: `_bmad/_config/agent-manifest.csv`
- **Workflow manifest**: `_bmad/_config/workflow-manifest.csv`
- **Help manifest**: `_bmad/_config/bmad-help.csv`
- **Agent memory**: `_bmad/_memory/`

## Key Conventions

- Always load `_bmad/bmm/config.yaml` before any agent activation or workflow execution
- Store all config fields as session variables: `{user_name}`, `{communication_language}`, `{output_folder}`, `{planning_artifacts}`, `{implementation_artifacts}`, `{project_knowledge}`
- MD-based workflows execute directly — load and follow the `.md` file
- YAML-based workflows require the workflow engine — load `workflow.xml` first, then pass the `.yaml` config
- Follow step-based workflow execution: load steps JIT, never multiple at once
- Save outputs after EACH step when using the workflow engine
- The `{project-root}` variable resolves to the workspace root at runtime

## Available Agents

| Agent | Persona | Title | Capabilities |
|---|---|---|---|
| bmad-master | BMad Master | BMad Master Executor, Knowledge Custodian, and Workflow Orchestrator | runtime resource management, workflow orchestration, task execution, knowledge custodian |
| analyst | Mary | Business Analyst | market research, competitive analysis, requirements elicitation, domain expertise |
| architect | Winston | Architect | distributed systems, cloud infrastructure, API design, scalable patterns |
| dev | Amelia | Developer Agent | story execution, test-driven development, code implementation |
| pm | John | Product Manager | PRD creation, requirements discovery, stakeholder alignment, user interviews |
| qa | Quinn | QA Engineer | test automation, API testing, E2E testing, coverage analysis |
| quick-flow-solo-dev | Barry | Quick Flow Solo Dev | rapid spec creation, lean implementation, minimum ceremony |
| sm | Bob | Scrum Master | sprint planning, story preparation, agile ceremonies, backlog management |
| tech-writer | Paige | Technical Writer | documentation, Mermaid diagrams, standards compliance, concept explanation |
| ux-designer | Sally | UX Designer | user research, interaction design, UI patterns, experience strategy |

## Slash Commands

Type `/bmad-` in Copilot Chat to see all available BMAD workflows and agent activators. Agents are also available in the agents dropdown.
<!-- BMAD:END -->

<!-- AIDE:START -->
# AIDE (AI Development Engine) — Product Instructions

> Ce dépôt développe AIDE. Les sections BMAD ci-dessus sont pour le **développement interne**.
> Les sections AIDE ci-dessous décrivent le **produit déployable** vers les projets cibles.

## Structure du Produit

- **Bundle** : `bundle/.github/` — 17 agents (`AIDE-*.agent.md`) + 5 workflows (`AIDE-*.prompt.md`) + `copilot-instructions.md`
- **Engine** : `engine/src/ai_workflow/` — Moteur Python (machine à états, runners, fork/join)
- **Déploiement** : `deploy.py` — Déploie bundle + engine vers un projet local ou Git distant
- **Template** : `bundle/.ai-workflow/` — Structure de workspace déployée sur la cible

## Agents AIDE (17)

| Agent | Phase | Rôle |
|---|---|---|
| AIDE-brainstormer | Conception | Clarifier la vision et les objectifs |
| AIDE-arch-produit | Conception | Architecture produit haut niveau |
| AIDE-arch-metier | Conception | Domaine métier, règles business |
| AIDE-arch-gui | Conception | Interfaces utilisateur, navigation |
| AIDE-arch-technique | Conception | Stack technique, patterns, structure |
| AIDE-cartographe | Approvisionnement | Scan repo, profil_projet.md |
| AIDE-magazinier | Approvisionnement | Skills, instructions réutilisables |
| AIDE-orchestrateur | Orchestration | US, batches, dépendances |
| AIDE-developpeur | Construction | Implémentation du code |
| AIDE-testeur | Construction | Tests unitaires et fonctionnels |
| AIDE-analyseur-secu | Analyse | Sécurité (bloquant) |
| AIDE-analyseur-perf | Analyse | Performance (bloquant) |
| AIDE-analyseur-bp | Analyse | Bonnes pratiques (non-bloquant) |
| AIDE-integrateur | Intégration | Cohérence inter-US |
| AIDE-fixeur-integration | Intégration | Corrections post-intégration |
| AIDE-documentaliste | Finalisation | Documentation globale |
| AIDE-agent-memoire | Transversal | Mémoire projet, profil_projet.md |

## Workflows AIDE (5)

| Commande | Description |
|---|---|
| `/AIDE-workflow-init` | Initialiser `.ai-workflow/` |
| `/AIDE-workflow-vierge` | Nouveau projet complet (14 états) |
| `/AIDE-workflow-existant` | Enrichir un projet existant (10 états) |
| `/AIDE-workflow-feature` | Ajouter une feature (7 états) |
| `/AIDE-workflow-status` | Afficher l'état courant |

## Coexistence BMAD / AIDE

- `/bmad-*` et `@bmad-*` = **développement interne** de ce dépôt (méthode BMAD)
- `/AIDE-*` et `@AIDE-*` = **produit** déployé vers les projets cibles
- L'engine (`engine/`) et le bundle (`bundle/`) n'ont **aucune dépendance** vers BMAD
- Voir `docs/BMAD-AIDE-Coexistence.md` pour les détails
<!-- AIDE:END -->
