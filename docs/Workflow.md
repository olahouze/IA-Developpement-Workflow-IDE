# AIDE — Workflows & Orchestration

Guide des workflows AIDE : 3 workflows principaux et 2 commandes utilitaires, accessibles via `/AIDE-*` dans Copilot Chat.

---

## Commandes Disponibles

| Commande | Type | Description |
|---|---|---|
| `/AIDE-workflow-init` | Utilitaire | Crée `.ai-workflow/` et choisit le type de workflow |
| `/AIDE-workflow-vierge` | Workflow | Nouveau projet complet (14 états) |
| `/AIDE-workflow-existant` | Workflow | Enrichir un projet existant (10 états) |
| `/AIDE-workflow-feature` | Workflow | Ajouter une feature (7 états) |
| `/AIDE-workflow-status` | Utilitaire | Afficher l'état courant du workflow |

---

## Initialisation : `/AIDE-workflow-init`

Point de départ obligatoire. Crée la structure de travail :

```
.ai-workflow/
├── skills/          # Skills .md réutilisables (instructions domaine)
├── instructions/    # Instructions spécifiques au projet
├── reports/         # Rapports globaux des agents
├── us/              # Dossiers par User Story (US-001/, US-002/...)
├── docs/            # Documentation générée
├── state.json       # État du workflow (étape, batch, itération)
└── profil_projet.md # Profil projet (mémoire évolutive, ≤500 lignes)
```

Après création, ajoute `.ai-workflow/` au `.gitignore`.

---

## Workflow Projet Vierge — `/AIDE-workflow-vierge`

Workflow complet pour un **nouveau projet**, de la conception à la livraison.

### 14 États

```
[1] brainstorming
 │  @AIDE-brainstormer → brief structuré
 ▼
[2] architecture_produit
 │  @AIDE-arch-produit → composants, interactions
 ▼
[3] architecture_metier
 │  @AIDE-arch-metier → domaine, règles business
 ▼
[4] architecture_gui (optionnel)
 │  @AIDE-arch-gui → interfaces, navigation
 ▼
[5] architecture_technique
 │  @AIDE-arch-technique → stack, patterns, structure
 ▼
[6] cartographie
 │  @AIDE-cartographe → profil_projet.md
 ▼
[7] approvisionnement
 │  @AIDE-magazinier → skills, instructions
 ▼
[8] orchestration
 │  @AIDE-orchestrateur → US, batches, dépendances
 ▼
[9] batch_builders (boucle)
 │  Pour chaque batch :
 │    Pour chaque US :
 │      @AIDE-developpeur → code
 │      @AIDE-testeur → tests
 │      @AIDE-analyseur-secu ┐
 │      @AIDE-analyseur-perf ├→ en parallèle
 │      @AIDE-analyseur-bp   ┘
 │      → Verdict (PASS/FAIL/RETRY)
 │      @AIDE-agent-memoire → collecte découvertes
 ▼
[10] integration
 │  @AIDE-integrateur → cohérence inter-US (MINEUR/MAJEUR)
 ▼
[11] fix_integration
 │  @AIDE-fixeur-integration → corrections
 ▼
[12] documentation
 │  @AIDE-documentaliste → docs globales
 ▼
[13] memoire_finale
 │  @AIDE-agent-memoire → synthèse finale
 ▼
[14] termine
```

---

## Workflow Projet Existant — `/AIDE-workflow-existant`

Workflow pour **enrichir un projet existant** : scan repo → brainstorming léger → développement.

### 10 États

```
[1] cartographie
 │  @AIDE-cartographe → scan repo, profil_projet.md
 ▼
[2] brainstorming_leger
 │  @AIDE-brainstormer → clarifier les objectifs d'enrichissement
 ▼
[3] architecture_technique
 │  @AIDE-arch-technique → raffinement technique
 ▼
[4] orchestration
 │  @AIDE-orchestrateur → US, batches
 ▼
[5] batch_builders (boucle)
 │  Même boucle que le workflow vierge
 ▼
[6] integration
 │  @AIDE-integrateur
 ▼
[7] fix_integration
 │  @AIDE-fixeur-integration
 ▼
[8] documentation
 │  @AIDE-documentaliste
 ▼
[9] memoire_finale
 │  @AIDE-agent-memoire
 ▼
[10] termine
```

---

## Workflow Feature — `/AIDE-workflow-feature`

Workflow **léger** pour ajouter une feature. Pas de phase d'architecture ni d'intégration complète.

### 7 États

```
[1] cartographie
 │  @AIDE-cartographe → scan rapide du contexte
 ▼
[2] orchestration
 │  @AIDE-orchestrateur → 1 batch (la feature)
 ▼
[3] batch_builders (boucle)
 │  Dev → Test → Analyse → Verdict
 ▼
[4] documentation
 │  @AIDE-documentaliste → docs de la feature
 ▼
[5] memoire_finale
 │  @AIDE-agent-memoire
 ▼
[6] termine
```

---

## Cycle de Développement par US (batch_builders)

C'est le cœur de l'exécution. Commun à tous les workflows.

### Séquence

```
Pour chaque User Story dans le batch courant :

  ┌────────────────────────────────────────┐
  │ 1. @AIDE-developpeur                   │
  │    Implémente le code de l'US          │
  │    → developpeur_report_iter<N>.md     │
  └───────────────┬────────────────────────┘
                  ▼
  ┌────────────────────────────────────────┐
  │ 2. @AIDE-testeur                       │
  │    Écrit/maintient les tests           │
  │    → testeur_report_iter<N>.md         │
  └───────────────┬────────────────────────┘
                  ▼
  ┌─────────────────┬──────────────────┬──────────────────┐
  │ 3a. @AIDE-      │ 3b. @AIDE-       │ 3c. @AIDE-       │
  │ analyseur-secu  │ analyseur-perf   │ analyseur-bp     │
  │ (bloquant)      │ (bloquant)       │ (non-bloquant)   │
  └────────┬────────┴────────┬─────────┴────────┬─────────┘
           └─────────────────┴──────────────────┘
                             ▼
  ┌────────────────────────────────────────┐
  │ 4. VERDICT                              │
  │                                         │
  │  Tous PASS        → US validée ✓       │
  │  FAIL bloquant    → retry (max 4)      │
  │  Seul FAIL BP     → US validée ✓       │
  │  ≥ 4 itérations   → ESCALADE ⚠        │
  └───────────────┬────────────────────────┘
                  ▼
  ┌────────────────────────────────────────┐
  │ 5. @AIDE-agent-memoire                 │
  │    Collecte découvertes → profil       │
  └────────────────────────────────────────┘
```

### Logique de Verdict

| Résultat sécu | Résultat perf | Résultat BP | Verdict |
|---|---|---|---|
| PASS | PASS | PASS | **US validée** |
| PASS | PASS | FAIL | **US validée** (BP non-bloquant) |
| FAIL | PASS | * | **Retry** → retour au développeur |
| PASS | FAIL | * | **Retry** → retour au développeur |
| FAIL | FAIL | * | **Retry** → retour au développeur |
| * (itération ≥ 4) | * | * | **ESCALADE** (intervention manuelle) |

### Rapports générés

```
.ai-workflow/us/US-001/
├── definition.md                      # Créé par @AIDE-orchestrateur
├── developpeur_report_iter1.md        # Itération 1 du développeur
├── testeur_report_iter1.md            # Itération 1 du testeur
├── analyseur-secu_report_iter1.md     # Analyse sécurité
├── analyseur-perf_report_iter1.md     # Analyse performance
├── analyseur-bp_report_iter1.md       # Analyse bonnes pratiques
├── developpeur_report_iter2.md        # Itération 2 (si retry)
└── ...
```

---

## Mémoire et Profil Projet

### profil_projet.md

Fichier central de mémoire (`.ai-workflow/profil_projet.md`), limité à **500 lignes** :
- Conventions du projet (langage, framework, patterns)
- Découvertes des agents (problèmes rencontrés, solutions choisies)
- Stack technique, dépendances
- Règles métier identifiées

### Flux mémoire

1. Chaque agent produit une section **"Découvertes pour mémoire"** dans son rapport
2. `@AIDE-agent-memoire` collecte ces découvertes
3. Déduplique, catégorise, intègre dans `profil_projet.md`
4. Si > 500 lignes : élagage des entrées les plus anciennes/moins pertinentes

### Priorité mémoire

- Le développeur fait foi pour la mémoire intra-US (ses découvertes priment)
- Les analyseurs priment pour les contraintes techniques (sécu, perf)

---

## Deux Modes d'Exécution

### Mode Copilot Natif (recommandé pour démarrer)

L'utilisateur pilote le workflow manuellement dans Copilot Chat :
1. `/AIDE-workflow-init` → crée la structure
2. `/AIDE-workflow-vierge` → le prompt guide étape par étape
3. À chaque étape, l'agent approprié est invoqué
4. L'utilisateur valide et passe à l'étape suivante
5. L'état est sauvé dans `state.json`

**Avantage** : Contrôle total, feedback humain à chaque étape.

### Mode Engine Python (orchestration automatisée)

Le moteur Python gère le workflow de bout en bout :
```bash
ai-workflow run --workflow vierge
```

**Avantages** :
- Machine à états automatique (library `transitions`)
- Fork/join pour parallélisation des analyseurs
- Verdict automatique avec retry
- Injection de contexte Jinja2

Voir [Architecture.md](Architecture.md) pour les détails techniques.

