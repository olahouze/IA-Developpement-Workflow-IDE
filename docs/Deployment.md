# AIDE — Guide de Déploiement

Comment déployer AIDE (agents + workflows + engine) sur un projet cible.

---

## Prérequis

- Python 3.11+
- Git (pour le déploiement distant)
- VS Code avec GitHub Copilot Chat (pour le mode Copilot natif)

---

## Commande de Déploiement

```bash
python deploy.py <cible> [options]
```

### Arguments

| Argument | Description |
|---|---|
| `<cible>` | Chemin local ou URL Git du projet cible |
| `--branch`, `-b` | Branche Git à créer (défaut: `feat/ai-workflow-engine`) |
| `--project-name` | Nom du projet cible (défaut: nom du dossier) |
| `--user-name` | Nom d'utilisateur (défaut: utilisateur système) |
| `--lang` | Langue de communication (défaut: `French`) |
| `--copilot-only` | Déploie uniquement les fichiers Copilot (agents, prompts, instructions) |
| `--dry-run` | Affiche les actions sans les exécuter |

---

## Modes de Déploiement

### 1. Déploiement Local

```bash
# Basique
python deploy.py ./mon-projet

# Avec configuration
python deploy.py /chemin/vers/projet --project-name "Mon Projet" --user-name "Jean" --lang "French"

# Copilot uniquement (pas d'engine Python)
python deploy.py ./mon-projet --copilot-only

# Prévisualisation
python deploy.py ./mon-projet --dry-run
```

### 2. Déploiement Git Distant

```bash
# GitLab
python deploy.py https://gitlab.example.com/org/repo.git

# GitHub
python deploy.py https://github.com/org/repo.git

# Branche personnalisée
python deploy.py https://gitlab.example.com/org/repo.git --branch feat/aide

# Avec token (demandé interactivement si l'accès échoue)
python deploy.py https://gitlab.example.com/org/repo.git
```

Le déploiement Git :
1. Clone le repo (shallow clone)
2. Crée la branche spécifiée
3. Copie les fichiers
4. Commit + Push
5. Affiche le lien pour créer une Merge Request

---

## Ce Qui Est Déployé

### Mode Complet (défaut)

| Source | Destination | Description |
|---|---|---|
| `engine/src/ai_workflow/` | `src/ai_workflow/` | Moteur Python (state machine, runners) |
| `pyproject.toml` | `pyproject.toml` | Dépendances Python |
| `README.md` | `README.md` | Documentation |
| `engine/tests/` | `tests/` | Tests unitaires |
| `bundle/.github/agents/AIDE-*.agent.md` | `.github/agents/` | 17 agents Copilot |
| `bundle/.github/prompts/AIDE-*.prompt.md` | `.github/prompts/` | 5 workflows Copilot |
| `bundle/.github/copilot-instructions.md` | `.github/copilot-instructions.md` | Instructions Copilot (fusionnées) |

### Mode `--copilot-only`

| Source | Destination | Description |
|---|---|---|
| `bundle/.github/agents/AIDE-*.agent.md` | `.github/agents/` | 17 agents Copilot |
| `bundle/.github/prompts/AIDE-*.prompt.md` | `.github/prompts/` | 5 workflows Copilot |
| `bundle/.github/copilot-instructions.md` | `.github/copilot-instructions.md` | Instructions Copilot (fusionnées) |

---

## Structure Créée sur la Cible

Après déploiement, le projet cible contient :

```
projet-cible/
├── .github/
│   ├── agents/
│   │   ├── AIDE-brainstormer.agent.md
│   │   ├── AIDE-arch-produit.agent.md
│   │   ├── AIDE-arch-metier.agent.md
│   │   ├── AIDE-arch-gui.agent.md
│   │   ├── AIDE-arch-technique.agent.md
│   │   ├── AIDE-cartographe.agent.md
│   │   ├── AIDE-magazinier.agent.md
│   │   ├── AIDE-orchestrateur.agent.md
│   │   ├── AIDE-developpeur.agent.md
│   │   ├── AIDE-testeur.agent.md
│   │   ├── AIDE-analyseur-secu.agent.md
│   │   ├── AIDE-analyseur-perf.agent.md
│   │   ├── AIDE-analyseur-bp.agent.md
│   │   ├── AIDE-integrateur.agent.md
│   │   ├── AIDE-fixeur-integration.agent.md
│   │   ├── AIDE-documentaliste.agent.md
│   │   └── AIDE-agent-memoire.agent.md
│   ├── prompts/
│   │   ├── AIDE-workflow-init.prompt.md
│   │   ├── AIDE-workflow-vierge.prompt.md
│   │   ├── AIDE-workflow-existant.prompt.md
│   │   ├── AIDE-workflow-feature.prompt.md
│   │   └── AIDE-workflow-status.prompt.md
│   └── copilot-instructions.md
├── .ai-workflow/           ← créé par configure_target()
│   ├── skills/
│   ├── instructions/
│   ├── reports/
│   ├── us/
│   └── docs/
├── src/ai_workflow/        ← seulement en mode complet
├── tests/                  ← seulement en mode complet
├── pyproject.toml          ← seulement en mode complet
└── .gitignore
```

---

## Fusion Non-Destructive

Le fichier `copilot-instructions.md` est **fusionné** et non écrasé :

### Cas 1 — Pas de fichier existant
Le contenu AIDE est créé tel quel.

### Cas 2 — Fichier existant sans section AIDE
Le contenu AIDE est **ajouté à la fin** du fichier existant.

### Cas 3 — Fichier existant avec section AIDE
Le contenu entre `<!-- AIDE:START -->` et `<!-- AIDE:END -->` est **remplacé**. Le reste du fichier est préservé.

Cela permet de re-déployer sans perdre les instructions custom du projet.

---

## Placeholders

Les fichiers déployés contiennent des placeholders remplacés automatiquement :

| Placeholder | Remplacé par | Source |
|---|---|---|
| `@@PROJECT_NAME@@` | Nom du projet | `--project-name` ou nom du dossier |
| `@@USER_NAME@@` | Nom utilisateur | `--user-name` ou utilisateur système |
| `@@LANG@@` | Langue | `--lang` (défaut: French) |
| `@@VERSION@@` | Version AIDE | Lue depuis `pyproject.toml` |

---

## Injection de Version

La version est extraite automatiquement depuis `pyproject.toml` :
- Injectée dans le message de commit Git
- Remplace le placeholder `@@VERSION@@` dans les fichiers déployés
- Visible dans `copilot-instructions.md` sur le projet cible

---

## Post-Déploiement

Après déploiement, dans VS Code sur le projet cible :

1. **Vérifier** : taper `@AIDE-` dans Copilot Chat → les 17 agents apparaissent
2. **Vérifier** : taper `/AIDE-` → les 5 workflows apparaissent
3. **Démarrer** : `/AIDE-workflow-init` pour créer la structure `.ai-workflow/`
4. **Choisir** : un workflow adapté (`vierge`, `existant`, ou `feature`)

### Si mode complet (engine Python)

```bash
cd projet-cible
pip install -e .
ai-workflow run --workflow vierge
```

---

## Redéploiement

Le script est conçu pour être **idempotent** :
- Les agents `AIDE-*` sont copiés à chaque fois (mise à jour)
- Le `copilot-instructions.md` est fusionné (pas écrasé)
- Le `.ai-workflow/` est créé seulement si absent
- Les fichiers engine sont écrasés (dernière version)

Pour mettre à jour AIDE sur un projet déjà déployé :
```bash
python deploy.py ./projet-cible  # Re-déploiement sûr
```
