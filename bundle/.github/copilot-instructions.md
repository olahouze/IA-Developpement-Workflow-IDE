<!-- AIDE:START -->
# AIDE — AI Development Engine

> **AIDE** orchestre 17 agents IA spécialisés pour développer un projet de bout en bout :
> conception → architecture → planification → développement → tests → analyse → intégration → documentation.

## Configuration

- **Projet** : @@PROJECT_NAME@@
- **Utilisateur** : @@USER_NAME@@
- **Langue** : @@LANG@@

## Runtime

- **Répertoire de travail** : `.ai-workflow/` (créé par `/AIDE-workflow-init`)
- **Agents** : `src/ai_workflow/agents/definitions/` (définitions YAML + instructions Jinja2)
- **Workflows** : `src/ai_workflow/workflows/` (3 fichiers YAML)
- **État** : `.ai-workflow/state.json` (persistance entre sessions)
- **Rapports** : `.ai-workflow/reports/` (globaux) et `.ai-workflow/us/<US_ID>/` (par user story)
- **Profil projet** : `.ai-workflow/profil_projet.md` (mémoire évolutive)
- **Skills** : `.ai-workflow/skills/` (fichiers .md réutilisables)

## Agents disponibles (17)

| Agent | Rôle | Phase | Bloquant |
|---|---|---|---|
| `@AIDE-brainstormer` | Facilitateur créatif — clarifie la vision, produit un brief structuré | Conception | — |
| `@AIDE-arch-produit` | Architecture produit haut niveau — composants, interactions | Conception | — |
| `@AIDE-arch-metier` | Architecture métier — domaine, règles business, modèle conceptuel | Conception | — |
| `@AIDE-arch-gui` | Architecture GUI — interfaces, composants UI, navigation | Conception | Optionnel |
| `@AIDE-arch-technique` | Architecture technique — stack, patterns, structure projet | Conception | — |
| `@AIDE-cartographe` | Scanne le repo existant, construit le profil projet | Approvisionnement | — |
| `@AIDE-orchestrateur` | Décompose en US, analyse dépendances, crée des batches parallèles | Orchestration | — |
| `@AIDE-magazinier` | Enrichit le projet avec skills/instructions depuis des sources externes | Approvisionnement | — |
| `@AIDE-developpeur` | Implémente le code de l'US. Relit tout le contexte à chaque itération | Construction | — |
| `@AIDE-testeur` | Écrit et maintient les tests. Code analysé comme celui du Dev | Construction | — |
| `@AIDE-analyseur-secu` | Analyse sécurité (OWASP Top 10). Verdict PASS/FAIL **bloquant** | Analyse | Bloquant |
| `@AIDE-analyseur-perf` | Analyse performance (complexité, I/O, mémoire). Verdict **bloquant** | Analyse | Bloquant |
| `@AIDE-analyseur-bp` | Analyse bonnes pratiques (DRY, SOLID). Verdict **non-bloquant** seul | Analyse | Non-bloquant |
| `@AIDE-integrateur` | Cohérence inter-US (read-only). Classifie MINEUR/MAJEUR | Intégration | — |
| `@AIDE-fixeur-integration` | Corrige les incohérences. MINEUR → corrige ; MAJEUR → renvoie aux builders | Intégration | — |
| `@AIDE-documentaliste` | Documentation technique et utilisateur GLOBALE | Finalisation | — |
| `@AIDE-agent-memoire` | Gardien de la mémoire collective. Tourne après chaque agent | Transversal | — |

## Workflows disponibles (3)

| Workflow | Commande | Description | États |
|---|---|---|---|
| Projet vierge | `/AIDE-workflow-vierge` | Workflow complet — de la conception à la livraison | 14 états |
| Projet existant | `/AIDE-workflow-existant` | Enrichir un projet existant — scan repo puis développement | 10 états |
| Feature | `/AIDE-workflow-feature` | Ajouter une feature à un projet existant | 7 états |

## Commandes utilitaires

| Commande | Description |
|---|---|
| `/AIDE-workflow-init` | Initialiser le répertoire `.ai-workflow/` et choisir le type de workflow |
| `/AIDE-workflow-status` | Afficher l'état courant du workflow (étape, US, itération) |

## Conventions

### Cycle de développement par US (batch_builders)

Pour chaque User Story dans un batch :
1. `@AIDE-developpeur` implémente le code
2. `@AIDE-testeur` écrit les tests
3. Les 3 analyseurs s'exécutent en parallèle : `@AIDE-analyseur-secu`, `@AIDE-analyseur-perf`, `@AIDE-analyseur-bp`
4. **Verdict** :
   - Tous PASS → US validée, passer à la suivante
   - FAIL bloquant (sécu ou perf) → retour au développeur (retry, max 4 itérations)
   - Seul FAIL non-bloquant (bp) → US validée quand même
   - ≥ 4 itérations en échec → ESCALADE (intervention manuelle requise)

### Mémoire

- Chaque agent produit une section "Découvertes pour mémoire" dans son rapport
- `@AIDE-agent-memoire` collecte et déduplique ces découvertes dans le profil projet
- Le développeur fait foi pour la mémoire intra-US (ses découvertes priment)
- Le profil projet ne dépasse pas 500 lignes (élagage automatique)

### Rapports

- Les rapports globaux sont dans `.ai-workflow/reports/<agent>_report.md`
- Les rapports par US sont dans `.ai-workflow/us/<US_ID>/<agent>_report_iter<N>.md`
- Chaque rapport suit le template de sortie défini par l'agent

## Slash Commands

Tapez `/AIDE-` dans Copilot Chat pour voir tous les workflows et utilitaires disponibles.
Les agents sont disponibles via `@AIDE-` dans le menu agents.
<!-- AIDE:END -->
