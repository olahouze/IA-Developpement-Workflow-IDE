---
description: 'Initialiser le répertoire .ai-workflow/ et choisir le type de workflow'
tools: ['read', 'editFiles', 'search']
---

# AIDE — Initialisation du Workflow

Initialise le répertoire de travail `.ai-workflow/` pour le projet courant.

## Instructions

### 1. Créer la structure `.ai-workflow/`

Créer les sous-dossiers suivants à la racine du projet :

```
.ai-workflow/
├── skills/          ← Fichiers .md réutilisables (skills, conventions)
├── instructions/    ← Instructions spécifiques au projet
├── reports/         ← Rapports globaux des agents
├── us/              ← Dossiers par User Story (US-001/, US-002/...)
└── docs/            ← Documentation générée
```

### 2. Demander le type de workflow

Demander à l'utilisateur quel workflow il souhaite utiliser :

| Type | Description | Commande |
|---|---|---|
| **vierge** | Nouveau projet de zéro — conception complète (14 étapes) | `/AIDE-workflow-vierge` |
| **existant** | Enrichir un projet existant — scan repo + développement (10 étapes) | `/AIDE-workflow-existant` |
| **feature** | Ajouter une feature — léger et rapide (7 étapes) | `/AIDE-workflow-feature` |

### 3. Créer le fichier d'état initial

Créer `.ai-workflow/state.json` :

```json
{
  "workflow_name": "<type choisi>",
  "current_state": "init",
  "completed_states": [],
  "batches": [],
  "current_batch_index": 0,
  "current_us_id": null,
  "current_iteration": 1,
  "agent_results": {},
  "is_complete": false
}
```

### 4. Ajouter `.ai-workflow/` au `.gitignore`

Si un `.gitignore` existe, ajouter `.ai-workflow/` s'il n'y est pas déjà.

### 5. Indiquer la suite

Afficher un message indiquant que l'initialisation est terminée et quelle commande `/AIDE-workflow-*` lancer pour démarrer le workflow choisi.
