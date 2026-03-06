---
description: 'Workflow Projet Existant — 10 états, scan repo puis développement'
tools: ['read', 'editFiles', 'search', 'terminalLastCommand']
---

# AIDE — Workflow Projet Existant

> Workflow pour **enrichir un projet existant** : scan repo → brainstorming léger → planification → développement → intégration → documentation.
> **10 états** avec forks parallèles et boucle de verdict.

## Prérequis

Le répertoire `.ai-workflow/` doit exister. Sinon, exécuter d'abord `/AIDE-workflow-init`.

## Séquence des étapes

### Étape 1 — Cartographe

Activer `@AIDE-cartographe` pour scanner le repo existant et construire le profil projet.
- **Mode** : Scan complet (initial)
- **Sortie** : `.ai-workflow/reports/cartographe_report.md` + `.ai-workflow/profil_projet.md`

### Étape 2 — Brainstorming (léger)

Activer `@AIDE-brainstormer` pour clarifier les objectifs d'enrichissement.
- **Mode** : Léger/ciblé (le projet existe déjà)
- **Entrée** : profil projet existant + rapport du Cartographe
- **Sortie** : `.ai-workflow/reports/brainstormer_report.md`

### Étape 3 — Fork : Orchestrateur ∥ Magazinier

Exécuter en parallèle :
1. `@AIDE-orchestrateur` — décompose en US, crée des batches
2. `@AIDE-magazinier` — enrichit avec des skills (mode maintenance)

- **Sortie Orchestrateur** : `.ai-workflow/reports/orchestrateur_report.md` + dossiers `.ai-workflow/us/<US_ID>/`
- **Sortie Magazinier** : `.ai-workflow/reports/magazinier_report.md`

### Étape 4 — Batches Builders (boucle)

Identique au workflow Projet Vierge (étape 8) :

Pour chaque **batch** et chaque **US** :
1. `@AIDE-developpeur` → implémente
2. `@AIDE-testeur` → teste
3. `@AIDE-analyseur-secu` + `@AIDE-analyseur-perf` + `@AIDE-analyseur-bp` → analysent
4. **Verdict** : PASS → suivant | FAIL bloquant → retry (max 4) | ESCALADE si ≥ 4

Après chaque agent : `@AIDE-agent-memoire` collecte les découvertes.

### Étape 5 — Fork : Intégrateur ∥ Documentaliste

Exécuter en parallèle :
1. `@AIDE-integrateur` — cohérence inter-US
2. `@AIDE-documentaliste` — documentation globale

### Étape 6 — Fixeur d'Intégration (conditionnel)

- **MINEURS** → `@AIDE-fixeur-integration` corrige → Terminé
- **MAJEURS** → `@AIDE-fixeur-integration` → retour à l'Étape 4
- **Aucun problème** → Terminé

### Terminé

Le workflow est complet.

## État

Mettre à jour `.ai-workflow/state.json` après chaque étape :
```json
{
  "workflow_name": "projet-existant",
  "current_state": "<état_courant>",
  "completed_states": ["init", "cartographe", "..."],
  "is_complete": false
}
```
