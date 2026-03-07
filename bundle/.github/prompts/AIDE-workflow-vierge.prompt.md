---
description: 'Workflow Projet Vierge — 14 états, de la conception à la livraison complète'
tools: ['read', 'editFiles', 'search', 'terminalLastCommand']
---

# AIDE — Workflow Projet Vierge

> Workflow complet pour un **nouveau projet** : conception → architecture → planification → développement → tests → analyse → intégration → documentation.
> **14 états** avec forks parallèles et boucle de verdict.

## Prérequis

Le répertoire `.ai-workflow/` doit exister. Sinon, exécuter d'abord `/AIDE-workflow-init`.

## Séquence des étapes

### Étape 1 — Brainstorming (interactif)

Activer `@AIDE-brainstormer` pour clarifier la vision du projet.
- **Entrée** : questions à l'utilisateur
- **Sortie** : `.ai-workflow/reports/brainstormer_report.md`
- Attendre que le rapport soit complet avant de passer à l'étape suivante.

### Étape 2 — Architecture Produit

Activer `@AIDE-arch-produit` pour définir l'architecture haut niveau.
- **Entrée** : rapport du Brainstormer
- **Sortie** : `.ai-workflow/reports/arch-produit_report.md`

### Étape 3 — Architecture Métier

Activer `@AIDE-arch-metier` pour formaliser le domaine et les règles business.
- **Entrée** : rapports du Brainstormer et de l'Architecte Produit
- **Sortie** : `.ai-workflow/reports/arch-metier_report.md`

### Étape 4 — Architecture GUI (optionnel)

Si le projet comporte une GUI, activer `@AIDE-arch-gui`.
Sinon, **passer directement à l'étape 5**.
- **Entrée** : rapports précédents
- **Sortie** : `.ai-workflow/reports/arch-gui_report.md`

### Étape 5 — Architecture Technique

Activer `@AIDE-arch-technique` pour les spécifications techniques détaillées.
- **Entrée** : rapports des architectes précédents
- **Sortie** : `.ai-workflow/reports/arch-technique_report.md`

### Étape 6 — Cartographe

Activer `@AIDE-cartographe` pour scanner le repo et construire le profil projet.
- **Entrée** : état du repo
- **Sortie** : `.ai-workflow/reports/cartographe_report.md` + `.ai-workflow/profil_projet.md`

### Étape 7 — Fork : Orchestrateur ∥ Magazinier

Exécuter **en parallèle** (ou séquentiellement) :
1. `@AIDE-orchestrateur` — décompose en US, crée des batches
2. `@AIDE-magazinier` — enrichit avec des skills/instructions

- **Sortie Orchestrateur** : `.ai-workflow/reports/orchestrateur_report.md` + dossiers `.ai-workflow/us/<US_ID>/`
- **Sortie Magazinier** : `.ai-workflow/reports/magazinier_report.md` + fichiers dans `.ai-workflow/skills/`

### Étape 8 — Batches Builders (boucle)

Pour chaque **batch** créé par l'Orchestrateur, et pour chaque **US** dans le batch :

#### 8a. Développeur

Activer `@AIDE-developpeur` pour implémenter le code de l'US.
- **Sortie** : `.ai-workflow/us/<US_ID>/developpeur_report_iter<N>.md`

#### 8b. Testeur

Activer `@AIDE-testeur` pour écrire les tests.
- **Sortie** : `.ai-workflow/us/<US_ID>/testeur_report_iter<N>.md`

#### 8c. Analyseurs (parallèle)

Exécuter les 3 analyseurs :
1. `@AIDE-analyseur-secu` — sécurité (**bloquant**)
2. `@AIDE-analyseur-perf` — performance (**bloquant**)
3. `@AIDE-analyseur-bp` — bonnes pratiques (**non-bloquant** seul)

#### 8d. Verdict

- **Tous PASS** → US validée, passer à l'US suivante
- **FAIL bloquant** (sécu ou perf) → retour à 8a (retry, itération + 1)
- **Seul FAIL non-bloquant** (bp uniquement) → US validée quand même
- **≥ 4 itérations** → **ESCALADE** : arrêter et signaler à l'utilisateur

#### 8e. Agent Mémoire

Après chaque agent, `@AIDE-agent-memoire` collecte les découvertes.

Répéter pour chaque US de chaque batch (A → B → C → ...).

### Étape 9 — Fork : Intégrateur ∥ Documentaliste

Exécuter en parallèle :
1. `@AIDE-integrateur` — vérifie la cohérence inter-US
2. `@AIDE-documentaliste` — met à jour la documentation globale

- **Sortie Intégrateur** : `.ai-workflow/reports/integrateur_report.md`
- **Sortie Documentaliste** : `.ai-workflow/docs/`

### Étape 10 — Fixeur d'Intégration (conditionnel)

Si l'Intégrateur a détecté des problèmes :
- **MINEURS uniquement** → activer `@AIDE-fixeur-integration` pour corriger → Terminé
- **MAJEURS** → activer `@AIDE-fixeur-integration` → retour à l'Étape 8 (Batches Builders)
- **Aucun problème** → Terminé directement

### Terminé

Le workflow est complet. Tous les rapports sont dans `.ai-workflow/`.

## État

Mettre à jour `.ai-workflow/state.json` après chaque étape :
```json
{
  "workflow_name": "projet-vierge",
  "current_state": "<état_courant>",
  "completed_states": ["init", "brainstorm", "..."],
  "is_complete": false
}
```

## Mode d'exécution

Ce workflow fonctionne en **mode Copilot natif** : chaque étape est pilotée manuellement dans Copilot Chat.
Pour l'orchestration automatisée avec machine à états, utilisez : `ai-workflow run --workflow vierge`
