# AI Workflow Engine

Framework Python d'orchestration d'agents IA pour workflows de développement structurés.

## Installation

```bash
uv sync
```

## Utilisation

```bash
# Initialiser un projet
ai-workflow init --name mon-projet --type vierge

# Lancer le workflow
ai-workflow run

# Voir l'état courant
ai-workflow status

# Lister les agents
ai-workflow agents
```

## Workflows disponibles

| Type | Description |
|------|-------------|
| `vierge` | Projet from scratch — brainstorming, architecture, implémentation complète |
| `existant` | Projet existant — cartographie, adaptation, amélioration |
| `feature` | Ajout de feature — orchestration directe, pas de brainstorming |

## Structure .ai-workflow/

```
.ai-workflow/
  profil_projet.md      ← Profil projet évolutif
  state.json            ← État du workflow (reprise automatique)
  skills/               ← Skills immutables + surcharges
  instructions/         ← Instructions agents
  reports/              ← Rapports agents globaux
  us/                   ← User Stories (1 dossier par US)
  docs/                 ← Documentation générée
```

## 17 Agents disponibles

| Phase | Agents |
|-------|--------|
| Conception | Brainstormer, Arch-Produit, Arch-Métier, Arch-GUI, Arch-Technique |
| Orchestration | Orchestrateur |
| Approvisionnement | Cartographe, Magazinier |
| Construction | Développeur, Testeur |
| Analyse | Analyseur-Perf, Analyseur-Sécu, Analyseur-BP |
| Intégration | Intégrateur, Fixeur-Intégration |
| Finalisation | Documentaliste |
| Transversal | Agent-Mémoire |
