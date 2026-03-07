# AIDE — Catalog des 17 Agents Spécialisés

Index centralisé des 17 agents AIDE disponibles pour le développement de projets. Chaque agent est déployé sous forme de fichier `.agent.md` auto-suffisant, utilisable dans GitHub Copilot via `@AIDE-<nom>`.

## Vue d'ensemble

Les agents sont organisés par **phase de développement** :

| Phase | Agents | Rôle |
|-------|--------|------|
| **Conception** | `@AIDE-brainstormer`, `@AIDE-arch-produit`, `@AIDE-arch-metier`, `@AIDE-arch-gui`, `@AIDE-arch-technique` | Vision, architecture produit/métier/GUI/technique |
| **Approvisionnement** | `@AIDE-cartographe`, `@AIDE-magazinier` | Scan repo, enrichissement en skills |
| **Orchestration** | `@AIDE-orchestrateur` | Décomposition en US, batches parallèles |
| **Construction** | `@AIDE-developpeur`, `@AIDE-testeur` | Code + tests |
| **Analyse** | `@AIDE-analyseur-secu`, `@AIDE-analyseur-perf`, `@AIDE-analyseur-bp` | Sécurité, performance, bonnes pratiques |
| **Intégration** | `@AIDE-integrateur`, `@AIDE-fixeur-integration` | Cohérence inter-US, corrections |
| **Finalisation** | `@AIDE-documentaliste` | Documentation globale |
| **Transversal** | `@AIDE-agent-memoire` | Mémoire collective |

---

## Agents Détaillés

### Conception (5 agents)

- **`@AIDE-brainstormer`** — Facilitateur créatif. Clarifie la vision, produit un brief structuré. Point de départ recommandé pour tout nouveau projet.

- **`@AIDE-arch-produit`** — Architecture produit haut niveau. Définit les composants majeurs, leurs interactions et les frontières du système.

- **`@AIDE-arch-metier`** — Architecture métier. Modélise le domaine, les règles business, le modèle conceptuel (entités, relations).

- **`@AIDE-arch-gui`** — Architecture GUI (optionnel). Conçoit les interfaces, composants UI, navigation. Utile pour les projets avec frontend.

- **`@AIDE-arch-technique`** — Architecture technique. Choisit la stack, les patterns, la structure de fichiers du projet.

### Approvisionnement (2 agents)

- **`@AIDE-cartographe`** — Scanne le repo existant, identifie les conventions en place, et construit le `profil_projet.md` (mémoire du projet, ≤500 lignes).

- **`@AIDE-magazinier`** — Enrichit le projet avec des skills et instructions depuis des sources externes (fichiers `.md` dans `.ai-workflow/skills/`).

### Orchestration (1 agent)

- **`@AIDE-orchestrateur`** — Décompose le projet en User Stories (US), analyse les dépendances, crée des batches de US parallélisables. Produit le plan d'exécution.

### Construction (2 agents)

- **`@AIDE-developpeur`** — Implémente le code de l'US. Relit tout le contexte à chaque itération (profil, skills, rapports précédents). Produit un rapport `developpeur_report_iter<N>.md`.

- **`@AIDE-testeur`** — Écrit et maintient les tests. Analyse le code produit par le développeur. Produit un rapport `testeur_report_iter<N>.md`.

### Analyse (3 agents)

Ces trois agents s'exécutent **en parallèle** après le développement et le test.

- **`@AIDE-analyseur-secu`** — Analyse sécurité (OWASP Top 10). Verdict PASS/FAIL **bloquant**. Un FAIL empêche la validation de l'US.

- **`@AIDE-analyseur-perf`** — Analyse performance (complexité algorithmique, I/O, mémoire). Verdict PASS/FAIL **bloquant**.

- **`@AIDE-analyseur-bp`** — Analyse bonnes pratiques (DRY, SOLID, conventions). Verdict **non-bloquant** seul : un FAIL BP ne bloque pas si les autres analyses passent.

### Intégration (2 agents)

- **`@AIDE-integrateur`** — Vérifie la cohérence inter-US en mode read-only. Classifie les problèmes en MINEUR ou MAJEUR.

- **`@AIDE-fixeur-integration`** — Corrige les incohérences. MINEUR → corrige directement ; MAJEUR → renvoie aux agents de construction.

### Finalisation (1 agent)

- **`@AIDE-documentaliste`** — Produit la documentation technique et utilisateur globale du projet. Synthétise les rapports de tous les agents.

### Transversal (1 agent)

- **`@AIDE-agent-memoire`** — Gardien de la mémoire collective. Tourne après chaque agent pour collecter les découvertes et les intégrer au `profil_projet.md`. Déduplique et élague automatiquement.

---

## Organiser les Agents par Workflow

### `/AIDE-workflow-vierge` — Nouveau projet (14 étapes)

```
@AIDE-brainstormer
  → @AIDE-arch-produit
  → @AIDE-arch-metier
  → @AIDE-arch-gui (optionnel)
  → @AIDE-arch-technique
    → @AIDE-cartographe
    → @AIDE-magazinier
      → @AIDE-orchestrateur
        → Pour chaque batch d'US :
            @AIDE-developpeur → @AIDE-testeur → Analyseurs (×3) → Verdict
          → @AIDE-integrateur → @AIDE-fixeur-integration
            → @AIDE-documentaliste
```

### `/AIDE-workflow-existant` — Projet existant (10 étapes)

```
@AIDE-cartographe (scan repo)
  → @AIDE-brainstormer (brainstorming léger)
    → @AIDE-arch-technique (raffinement)
      → @AIDE-orchestrateur
        → Boucle batch_builders (Dev → Test → Analyse → Verdict)
          → @AIDE-integrateur → @AIDE-fixeur-integration
            → @AIDE-documentaliste
```

### `/AIDE-workflow-feature` — Ajout de feature (7 étapes)

```
@AIDE-cartographe (scan rapide)
  → @AIDE-orchestrateur (1 batch)
    → @AIDE-developpeur → @AIDE-testeur → Analyseurs → Verdict
      → @AIDE-documentaliste
```

---

## Sélectionner par Cas d'Usage

| Cas | Agents recommandés |
|-----|-----|
| **MVP Rapide** | `@AIDE-brainstormer` → `@AIDE-arch-technique` → `@AIDE-developpeur` → `@AIDE-testeur` |
| **Projet Enterprise** | Workflow complet (17 agents) |
| **Audit Sécurité** | `@AIDE-cartographe` → `@AIDE-analyseur-secu` → `@AIDE-analyseur-perf` |
| **Bug Fix** | `@AIDE-cartographe` → `@AIDE-developpeur` → `@AIDE-testeur` → `@AIDE-analyseur-secu` |
| **Documentation** | `@AIDE-cartographe` → `@AIDE-documentaliste` |
| **Découverte** | `@AIDE-brainstormer` → `@AIDE-arch-produit` → `@AIDE-arch-metier` |

---

## Bonnes Pratiques

### Chaîner logiquement

Respecter l'ordre des phases : Conception → Approvisionnement → Orchestration → Construction → Analyse → Intégration → Finalisation.

### Toujours scanner avant de coder

Sur un projet existant, commencer par `@AIDE-cartographe` pour construire le profil projet. Les agents suivants utilisent ce profil.

### Utiliser la mémoire

`@AIDE-agent-memoire` doit tourner après chaque agent pour capturer les découvertes. Le profil projet s'enrichit à chaque passage.

### Ne pas ignorer les verdicts bloquants

Un FAIL de `@AIDE-analyseur-secu` ou `@AIDE-analyseur-perf` doit être résolu avant de valider l'US. Le retry automatique relance `@AIDE-developpeur` avec les remarques des analyseurs.

