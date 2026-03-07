# BMAD & AIDE — Coexistence

Ce document explique la relation entre **BMAD** (méthode de développement) et **AIDE** (produit déployable).

---

## Résumé

| Aspect | BMAD | AIDE |
|---|---|---|
| **Nature** | Méthode de développement interne | Produit livré aux utilisateurs |
| **Emplacement** | `_bmad/`, `.github/agents/bmad-*`, `.github/prompts/bmad-*` | `bundle/`, `engine/` |
| **Préfixe** | `bmad-*` | `AIDE-*` |
| **Déployé ?** | Non — interne au dépôt source | Oui — déployé sur les projets cibles |
| **Dépendance** | Aucune dépendance vers AIDE | Aucune dépendance vers BMAD |

---

## BMAD — Méthode Interne

**BMAD** (BMad Method) est le framework de développement utilisé pour **construire** AIDE.

### Contenu

```
_bmad/                          # Runtime BMAD
├── _config/                    # Manifests, configuration
├── _memory/                    # Mémoire agents BMAD
├── bmm/                        # Module métier BMAD
│   ├── agents/                 # Définitions agents BMAD
│   ├── workflows/              # Workflows BMAD (par phase)
│   └── config.yaml             # Configuration module
└── core/                       # Noyau BMAD
    ├── agents/
    ├── tasks/
    └── workflows/

.github/agents/bmad-*.agent.md  # 10 agents de dev BMAD
.github/prompts/bmad-*.prompt.md # Prompts BMAD
install_bmad.py                  # Installateur BMAD
```

### Agents BMAD (développement)

| Agent | Rôle | Usage |
|---|---|---|
| `bmad-master` | Orchestrateur BMAD | Gestion des workflows BMAD |
| `analyst` (Mary) | Analyste business | Recherche marché, requirements |
| `architect` (Winston) | Architecte | Infrastructure, API design |
| `dev` (Amelia) | Développeur | Implémentation TDD |
| `pm` (John) | Product Manager | PRD, stakeholder alignment |
| `qa` (Quinn) | QA Engineer | Tests, couverture |
| `sm` (Bob) | Scrum Master | Sprints, backlog |
| `tech-writer` (Paige) | Rédacteur technique | Documentation |
| `ux-designer` (Sally) | UX Designer | Interfaces, UX |
| `quick-flow-solo-dev` (Barry) | Dev rapide | Implémentation lean |

### Quand utiliser BMAD

- Pour développer/modifier le code source d'AIDE
- Pour planifier les sprints de développement AIDE
- Pour les cérémonies agile internes
- Commandes : `/bmad-*`, `@bmad-*`

---

## AIDE — Produit Déployable

**AIDE** (AI Development Engine) est le produit livré aux utilisateurs.

### Contenu

```
bundle/                          # Fichiers déployables (Copilot natif)
├── .github/
│   ├── agents/AIDE-*.agent.md   # 17 agents AIDE
│   ├── prompts/AIDE-*.prompt.md # 5 workflows AIDE
│   └── copilot-instructions.md  # Instructions projet (avec marqueurs)

engine/                          # Moteur Python (orchestration automatisée)
├── src/ai_workflow/             # Code source
└── tests/                       # Tests unitaires
```

### Agents AIDE (produit)

17 agents spécialisés par phase :
- **Conception** : brainstormer, arch-produit, arch-metier, arch-gui, arch-technique
- **Approvisionnement** : cartographe, magazinier
- **Orchestration** : orchestrateur
- **Construction** : developpeur, testeur
- **Analyse** : analyseur-secu, analyseur-perf, analyseur-bp
- **Intégration** : integrateur, fixeur-integration
- **Finalisation** : documentaliste, agent-memoire

### Quand utiliser AIDE

- Pour développer un projet cible (l'utilisateur final)
- Déployé via `python deploy.py`
- Commandes : `/AIDE-*`, `@AIDE-*`

---

## Indépendance Technique

### Engine (zéro référence BMAD)

```
engine/src/ai_workflow/  →  Aucun import, aucune référence à BMAD
engine/tests/            →  Aucune dépendance BMAD
pyproject.toml           →  Nom: "ai-workflow-engine" (pas "bmad")
```

### Bundle (zéro référence BMAD)

```
bundle/.github/agents/      →  17 fichiers, tous préfixés AIDE-
bundle/.github/prompts/     →  5 fichiers, tous préfixés AIDE-
bundle/.github/copilot-instructions.md →  Marqueurs AIDE:START/END
```

### Vérification

```bash
# Doit retourner 0 résultats
grep -ri "bmad" bundle/
grep -ri "bmad" engine/src/
```

---

## Règles de Coexistence

1. **Ne jamais déployer BMAD** : `_bmad/`, `install_bmad.py`, `.github/agents/bmad-*` ne sont pas copiés vers les projets cibles
2. **Ne jamais référencer BMAD dans AIDE** : les fichiers du bundle et de l'engine ne doivent contenir aucune mention de BMAD
3. **Développement interne avec BMAD** : les contributeurs d'AIDE utilisent BMAD dans ce dépôt pour s'organiser
4. **Nommage clair** : préfixe `bmad-` = interne, préfixe `AIDE-` = produit
5. **`.github/copilot-instructions.md` du dépôt source** : contient les deux sections (BMAD pour le dev, AIDE pour référence)

---

## Diagramme

```
┌─────────────────────────────────────────────┐
│  Dépôt Source (IA-Developpement-Workflow-IDE)│
│                                              │
│  ┌──────────────┐    ┌────────────────────┐ │
│  │ BMAD          │    │ AIDE               │ │
│  │ (_bmad/)      │    │ (bundle/ + engine/)│ │
│  │ .github/bmad-*│    │ .github/AIDE-*     │ │
│  │               │    │                    │ │
│  │ ← interne     │    │ → déployable       │ │
│  └──────────────┘    └─────────┬──────────┘ │
│                                │             │
└────────────────────────────────┼─────────────┘
                                 │ deploy.py
                                 ▼
                    ┌────────────────────────┐
                    │  Projet Cible           │
                    │  .github/AIDE-*         │
                    │  src/ai_workflow/       │
                    │  .ai-workflow/          │
                    │                         │
                    │  Aucune trace de BMAD   │
                    └────────────────────────┘
```
