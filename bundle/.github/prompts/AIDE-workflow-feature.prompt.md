---
description: 'Workflow Feature — 7 états, ajouter une feature à un projet existant'
tools: ['read', 'editFiles', 'search', 'terminalLastCommand']
---

# AIDE — Workflow Feature

> Workflow **léger** pour ajouter une feature à un projet existant : scan → planification → développement → documentation.
> **7 états**, pas de phase d'architecture ni d'intégration complète.

## Prérequis

Le répertoire `.ai-workflow/` doit exister. Sinon, exécuter d'abord `/AIDE-workflow-init`.

## Séquence des étapes

### Étape 1 — Cartographe

Activer `@AIDE-cartographe` pour scanner le repo et mettre à jour le profil projet.
- **Mode** : Incrémental si profil existant, complet sinon
- **Sortie** : `.ai-workflow/reports/cartographe_report.md` + `.ai-workflow/profil_projet.md`

### Étape 2 — Fork : Orchestrateur ∥ Magazinier

Exécuter en parallèle :
1. `@AIDE-orchestrateur` — décompose la feature en US, crée des batches
2. `@AIDE-magazinier` — enrichit avec des skills (mode maintenance)

- **Sortie Orchestrateur** : `.ai-workflow/reports/orchestrateur_report.md` + dossiers `.ai-workflow/us/<US_ID>/`
- **Sortie Magazinier** : `.ai-workflow/reports/magazinier_report.md`

### Étape 3 — Batches Builders (boucle)

Pour chaque **batch** et chaque **US** :
1. `@AIDE-developpeur` → implémente
2. `@AIDE-testeur` → teste
3. `@AIDE-analyseur-secu` + `@AIDE-analyseur-perf` + `@AIDE-analyseur-bp` → analysent
4. **Verdict** : PASS → suivant | FAIL bloquant → retry (max 4) | ESCALADE si ≥ 4

Après chaque agent : `@AIDE-agent-memoire` collecte les découvertes.

### Étape 4 — Documentaliste

Activer `@AIDE-documentaliste` pour mettre à jour la documentation globale.
- **Sortie** : `.ai-workflow/docs/`

### Terminé

Le workflow est complet.

## État

Mettre à jour `.ai-workflow/state.json` après chaque étape :
```json
{
  "workflow_name": "feature",
  "current_state": "<état_courant>",
  "completed_states": ["init", "cartographe", "..."],
  "is_complete": false
}
```

## Mode d'exécution

Ce workflow fonctionne en **mode Copilot natif** : chaque étape est pilotée manuellement dans Copilot Chat.
Pour l'orchestration automatisée avec machine à états, utilisez : `ai-workflow run --workflow feature`
