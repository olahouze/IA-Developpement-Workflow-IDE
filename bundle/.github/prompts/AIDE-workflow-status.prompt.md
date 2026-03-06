---
description: 'Afficher l''état courant du workflow AIDE (étape, US, itération)'
tools: ['read', 'search']
---

# AIDE — Status du Workflow

Affiche l'état courant du workflow en cours.

## Instructions

### 1. Lire l'état

Lire le fichier `.ai-workflow/state.json` à la racine du projet.

Si le fichier n'existe pas, indiquer que le workflow n'a pas été initialisé et suggérer d'exécuter `/AIDE-workflow-init`.

### 2. Afficher le résumé

Afficher les informations suivantes :

```
╔══════════════════════════════════════════╗
║  AIDE — Status du Workflow               ║
╚══════════════════════════════════════════╝

Workflow      : <workflow_name>
État courant  : <current_state>
Complété      : <is_complete>

États terminés : <completed_states> (<count>/<total>)

Batch courant : <current_batch_index + 1> / <total_batches>
US courante   : <current_us_id>
Itération     : <current_iteration> / 4

Résultats agents :
  - <agent_name> : <status>
  ...
```

### 3. Afficher les US si disponibles

Si des batches existent dans l'état, lister les US avec leur statut :

| US | Nom | Statut | Itération |
|---|---|---|---|
| US-001 | ... | PASSED / IN_PROGRESS / PENDING / FAILED / ESCALATED | N |

### 4. Suggérer la prochaine action

En fonction de l'état courant, indiquer quel agent ou commande exécuter ensuite.
