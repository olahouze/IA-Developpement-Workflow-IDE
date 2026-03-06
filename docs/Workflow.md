# Workflows — Exécution & Orchestration

Guide complet d'exécution et de composition des workflows dans l'AI Workflow Engine.

---

## Concepts Fondamentaux

### Workflow vs Orchestration

**Workflow** : Définition statique (YAML) d'une séquence de steps coordonnant des agents.

```yaml
name: brainstorming
steps:
  - agent: analyst
  - agent: architect
  - agent: developer
```

**Orchestration** : Exécution dynamique du workflow au runtime avec gestion d'état, erreurs, parallélisme.

```python
engine = WorkflowEngine(config)
verdict = engine.execute_workflow("brainstorming")
```

---

## Workflows Disponibles

### 1. **Brainstorming** (Séquence linéaire)

**Fichier** : `src/ai_workflow/workflows/brainstorming.yaml`

**Objectif** : Progression structurée d'analyse → design → implémentation.

**Orchestration** : **SÉQUENTIELLE** (chaîne)

```
INPUT
  ↓
[1] Analyst (analyse requirements)
  ↓
[2] Architect (design solution)
  ↓
[3] Developer (propose implementation)
  ↓
OUTPUT (verdict final)
```

**Dépendances** : Chaque step consomme l'output du précédent.

```yaml
name: brainstorming
description: "Brainstorming séquence : analyst → architect → developer"
orchestration_type: sequential

steps:
  - agent: analyst
    name: "Analyser les requirements"
    description: "Identifie les gaps, risques, assumptions"
    inputs:
      requirements: "{{ user_input }}"
  
  - agent: architect
    name: "Designer la solution"
    description: "Propose architecture & design patterns"
    inputs:
      analysis: "{{ steps[0].output }}"  # Dépend du step 0
      project_context: "{{ context.project }}"
  
  - agent: developer
    name: "Proposer l'implémentation"
    description: "Code stubs, stack recommendations"
    inputs:
      design: "{{ steps[1].output }}"  # Dépend du step 1
      constraints: "{{ context.constraints }}"

# Configuration d'exécution
config:
  timeout_seconds: 300
  max_retries: 2
  parallel_agents: 1  # Séquence = max 1 agent à la fois
```

**Exemplo d'exécution** :

```bash
ai-workflow run --workflow brainstorming --input "Build a REST API for todo app"
```

**Résultat** :

```
✓ Step 1: analyst
  - Identifie 5 requirements clés
  - Signale 2 risques de scalabilité
  
✓ Step 2: architect
  - Propose PostgreSQL + FastAPI + Docker
  - Diagramme d'architecture

✓ Step 3: developer
  - Code skeleton (project structure)
  - Dependencies (requirements.txt)

VERDICT: SUCCESS (all steps completed)
DURATION: 45 seconds
```

---

### 2. **Party Mode** (Parallèle collaboratif)

**Fichier** : `src/ai_workflow/workflows/party-mode.yaml`

**Objectif** : Collaboration simultanée d'experts indépendants, puis fusion des insights.

**Orchestration** : **PARALLÈLE** (fork/join)

```
INPUT (context partagé)
  ↓
┌──────────────────────────────────┐
│      Fork — Exécution parallèle   │
├──────────────────────────────────┤
│ [1] Product Manager              │
│ [2] UX Designer                  │
│ [3] Architect                    │
│ [4] Developer                    │
└──────────────────────────────────┘
       (tous en même temps)
  ↓
┌──────────────────────────────────┐
│    Join — Synchronisation         │
│  Fusion des outputs              │
└──────────────────────────────────┘
  ↓
OUTPUT (verdict fusionné)
```

**Avantages** :
- ⚡ Exécution 4x plus rapide (si 4 agents)
- 🤝 Perspectives multiples simultanément
- 🔀 Moins de dépendances en chaîne

```yaml
name: party-mode
description: "Collaboration parallèle : PM, UX, Architect, Developer"
orchestration_type: parallel

steps:
  - agent: product_manager
    name: "Définir les requirements"
    inputs:
      business_context: "{{ context.business }}"
      target_users: "{{ context.users }}"
  
  - agent: ux_designer
    name: "Designer le UX"
    inputs:
      business_context: "{{ context.business }}"
      user_research: "{{ context.user_research }}"
  
  - agent: architect
    name: "Designer l'architecture"
    inputs:
      requirements: "{{ context.requirements }}"
      constraints: "{{ context.technical_constraints }}"
  
  - agent: developer
    name: "Proposer l'implémentation"
    inputs:
      requirements: "{{ context.requirements }}"
      architecture: "{{ context.architecture }}"

# Configuration
config:
  timeout_seconds: 300
  max_workers: 4  # Parallélisation : 4 agents max
```

**Execution example** :

```bash
ai-workflow run --workflow party-mode --context '{"business": "Fintech", "users": "Millennials"}'
```

**Résultat** :

```
🔀 Fork: Lancement parallèle de 4 agents...

✓ PM completed in 15s
  - 3 user personas
  - 5 key requirements

✓ UX completed in 18s
  - Wireframes (5 screens)
  - Interaction patterns

✓ Architect completed in 12s
  - Tech stack: Node.js + React + PostgreSQL
  - Cloud: AWS ECS + RDS

✓ Developer completed in 20s
  - Code structure (src/, tests/, etc.)
  - Docker + CI/CD setup

📊 Join: Fusion des résultats
  - Alignement PM ↔ UX ↔ Architect
  - Conflits résolus par consensus

VERDICT: SUCCESS (all agents aligned)
DURATION: 20 seconds (vs 65s en séquence)
EFFICIENCY: 3.25x speedup
```

---

### 3. **Advanced Elicitation** (Itératif & profond)

**Fichier** : `src/ai_workflow/workflows/advanced-elicitation.yaml`

**Objectif** : Découverte approfondie avec feedback loops et itération.

**Orchestration** : **PIPELINE ITÉRATIF**

```
INPUT (user challenges)
  ↓
[1] Analyst (v1)
  ├─ analyse initiale
  └─ génère questions
  ↓
[2] Researcher (research)
  ├─ explorationplus profonde
  └─ fournit insights
  ↓
[3] Product Manager (v2)
  ├─ priorise basé sur insights
  └─ crée PRD draft
  ↓
[4] UX Designer (v2, optionnel)
  ├─ affine wireframes
  └─ valide avec insights
  ↓
FEEDBACK LOOP (si insights insuffisants)
  └─ Retour à [2] pour approfondir
  ↓
OUTPUT (PRD + insights complets)
```

**Itération** : Si les doutes persistent, re-run le researcher.

```yaml
name: advanced-elicitation
description: "Découverte itérative : analyst → researcher → PM → UX"
orchestration_type: sequential_with_feedback

steps:
  - agent: analyst
    name: "Analyze Initial State"
    iteration: 1
    inputs:
      challenges: "{{ user_input }}"
      discovery_depth: "shallow"
  
  - agent: researcher
    name: "Deep Research"
    iterations: "{{ feedback_iterations }}"  # Peut répéter
    inputs:
      analyst_questions: "{{ steps[0].output.questions }}"
      focus_areas: "{{ context.focus_areas }}"
  
  - agent: product_manager
    name: "Create PRD v2"
    inputs:
      analyst_insights: "{{ steps[0].output }}"
      research_findings: "{{ steps[1].output }}"
      market_context: "{{ context.market }}"
  
  - agent: ux_designer
    name: "Refine UX"
    optional: true
    inputs:
      prd: "{{ steps[2].output }}"
      research_findings: "{{ steps[1].output }}"

# Configuration
config:
  max_iterations: 3  # Max feedback loops
  feedback_threshold: 0.7  # Si confidence < 70%, iterate
  timeout_seconds: 600
```

**Execution** :

```bash
ai-workflow run --workflow advanced-elicitation --user-input "Build platform for remote teams"
```

**Résultat avec itération** :

```
🔄 Iteration 1

✓ Analyst
  - 4 major pain points identified
  - Confidence: 0.65 (< 0.7 threshold)
  - Questions for researcher

⚠️ Researcher feedback needed

✓ Researcher (iteration 1)
  - Market size: $50B
  - Competitor analysis: 8 players
  - User research: 15 interviews
  - New confidence: 0.78

✓ PM
  - PRD v1 created
  - Key features prioritized

🔄 Iteration 2 (feedback loop triggered)

✓ Researcher (iteration 2)
  - Deeper analysis on pricing models
  - User willingness to pay
  - New confidence: 0.85

✓ PM
  - PRD v2 updated
  - Pricing strategy added

🔄 Loop terminée (confidence > 0.7)

✓ UX Designer (final refinement)
  - Wireframes aligned with PRD v2
  - Prototypes: 3 screens

VERDICT: SUCCESS (elicitation complete)
ITERATIONS: 2 feedback loops
FINAL_CONFIDENCE: 0.85
DURATION: 180 seconds
```

---

## Exécution Détaillée

### Flux d'Exécution Principal

```python
# src/ai_workflow/engine/workflow_engine.py

class WorkflowEngine:
    async def execute_workflow(self, workflow_name: str) -> ExecutionVerdict:
        """
        Exécute un workflow complet avec gestion d'état.
        """
        # 1. Load workflow definition
        workflow = self.config.load_workflow(workflow_name)
        
        # 2. Initialize state machine
        self.workflow_state = WorkflowState.PENDING
        
        # 3. Start execution
        self.workflow_state = WorkflowState.RUNNING
        
        # 4. Orchestrate steps
        if workflow.orchestration_type == "sequential":
            verdicts = self._execute_sequential(workflow)
        elif workflow.orchestration_type == "parallel":
            verdicts = self._execute_parallel(workflow)
        elif workflow.orchestration_type == "sequential_with_feedback":
            verdicts = self._execute_with_feedback(workflow)
        
        # 5. Evaluate final verdict
        final_verdict = self._merge_verdicts(verdicts)
        
        # 6. Store artifacts
        self._store_results(workflow_name, verdicts)
        
        # 7. Transition to complete
        self.workflow_state = WorkflowState.COMPLETE
        
        return final_verdict
```

### Orchestration Séquentielle

```python
def _execute_sequential(self, workflow: Workflow) -> list[ExecutionVerdict]:
    """
    Exécute les steps en chaîne (step i+1 attend step i).
    """
    context = self.context_builder.build_initial_context(workflow)
    verdicts = []
    
    for i, step in enumerate(workflow.steps):
        agent = self.agent_registry.get(step.agent_name)
        
        # Build context with previous outputs
        step_context = self.context_builder.build_step_context(
            workflow_context=context,
            previous_verdicts=verdicts,
            current_step=step
        )
        
        # Execute agent
        verdict = self.agent_runner.run_agent(agent, step_context)
        verdicts.append(verdict)
        
        # Update context for next step
        context[f"step_{i}_output"] = verdict.output
        
        # Early exit on critical error
        if verdict.status == AgentVerdictType.ERROR:
            return verdicts
    
    return verdicts
```

### Orchestration Parallèle (Fork/Join)

```python
def _execute_parallel(self, workflow: Workflow) -> list[ExecutionVerdict]:
    """
    Exécute tous les steps en parallèle.
    """
    context = self.context_builder.build_initial_context(workflow)
    
    # Fork: Préparer les tâches
    tasks = []
    for step in workflow.steps:
        agent = self.agent_registry.get(step.agent_name)
        step_context = self.context_builder.build_step_context(
            workflow_context=context,
            current_step=step
        )
        tasks.append((agent, step_context))
    
    # Fork: Lancer toutes les tâches en parallèle
    with ThreadPoolExecutor(max_workers=self.config.max_parallel_workers) as executor:
        futures = [
            executor.submit(self.agent_runner.run_agent, agent, ctx)
            for agent, ctx in tasks
        ]
        
        # Join: Attendre toutes les tâches
        verdicts = []
        for future in futures:
            try:
                verdict = future.result(timeout=self.config.timeout_seconds)
                verdicts.append(verdict)
            except TimeoutError:
                verdicts.append(ExecutionVerdict(
                    status=AgentVerdictType.ERROR,
                    error_message="Agent timeout"
                ))
    
    return verdicts
```

### Orchestration avec Feedback Loops

```python
def _execute_with_feedback(self, workflow: Workflow) -> list[ExecutionVerdict]:
    """
    Exécute avec itération jusqu'à confidence suffisante.
    """
    all_verdicts = []
    iteration = 0
    
    while iteration < workflow.config.max_iterations:
        iteration += 1
        print(f"🔄 Iteration {iteration}")
        
        # Exécute les steps de cette iteration
        iteration_verdicts = self._execute_sequential(workflow)
        all_verdicts.extend(iteration_verdicts)
        
        # Évaluer confidence
        confidence = self._calculate_confidence(iteration_verdicts)
        
        # Si suffisant, arrêter
        if confidence >= workflow.config.feedback_threshold:
            print(f"✓ Confidence {confidence:.2f} reached, stopping iterations")
            break
        
        print(f"⚠️ Confidence {confidence:.2f} < {workflow.config.feedback_threshold}, iterating...")
    
    return all_verdicts
```

### Fusion des Verdicts (Parallel)

```python
@staticmethod
def _merge_verdicts(verdicts: list[ExecutionVerdict]) -> ExecutionVerdict:
    """
    Fusionne les verdicts parallèles.
    - Si TOUS = SUCCESS → SUCCESS
    - Si QUELQUES = ERROR → PARTIAL
    - Si TOUS = ERROR → ERROR
    """
    statuses = [v.status for v in verdicts]
    success_count = statuses.count(AgentVerdictType.SUCCESS)
    error_count = statuses.count(AgentVerdictType.ERROR)
    
    if error_count == 0:
        final_status = AgentVerdictType.SUCCESS
    elif success_count > 0:
        final_status = AgentVerdictType.PARTIAL
    else:
        final_status = AgentVerdictType.ERROR
    
    # Fusionner les outputs
    merged_output = {}
    for i, v in enumerate(verdicts):
        if v.output:
            merged_output[f"agent_{i}"] = v.output
    
    return ExecutionVerdict(
        status=final_status,
        output=merged_output,
        error_message=None if final_status == SUCCESS else "Some agents failed",
        duration_seconds=sum(v.duration_seconds for v in verdicts)
    )
```

---

## Gestion des Erreurs

### Stratégies de Recovery

#### 1. Retry Automatique

```python
class AgentRunner:
    def run_agent(self, agent: Agent, context: dict, max_retries: int = 2):
        for attempt in range(1, max_retries + 1):
            try:
                return self._execute(agent, context)
            except Exception as e:
                if attempt < max_retries:
                    print(f"⚠️ Attempt {attempt} failed, retrying...")
                    time.sleep(2 ** attempt)  # exponential backoff
                else:
                    return ExecutionVerdict(
                        status=AgentVerdictType.ERROR,
                        error_message=f"Failed after {max_retries} attempts: {e}"
                    )
```

#### 2. Fallback Agent

```yaml
# workflows/brainstorming.yaml
steps:
  - agent: analyst
    name: "Analyze Requirements"
    fallback_agent: quick_analyzer  # Si analyst échoue
    inputs:
      requirements: "{{ user_input }}"
```

#### 3. Partial Success

Continuer l'exécution même si un step échoue (dépend du config).

```yaml
config:
  continue_on_error: true  # true = PARTIAL, false = arrête
  critical_steps: ["architect"]  # Ces steps doivent réussir
```

---

## Contexte & Variables

### Template Variables

Disponibles dans les inputs YAML via `{{ }}` :

```yaml
steps:
  - agent: analyst
    inputs:
      user_input: "{{ user_input }}"               # Cli arg
      previous_output: "{{ steps[0].output }}"     # Previous step
      project_name: "{{ context.project.name }}"   # Config
      timestamp: "{{ now() }}"                     # Function
```

### Context Layers

```
1. Initial Context (from CLI)
   ↓
2. Project Config (.ai-workflow/config.yaml)
   ↓
3. Workflow Config (workflows/brainstorming.yaml)
   ↓
4. Step Inputs (inputs: section in step)
   ↓
5. Memory (stored from previous runs)
   ↓
FINAL CONTEXT → Agent Execution
```

---

## Monitoring & Observabilité

### Status Command

```bash
ai-workflow status --workflow brainstorming
```

**Affiche** :

```
Workflow: brainstorming
State: RUNNING

Steps:
  [✓] Step 0: analyst (15s, SUCCESS)
     Output: 5 requirements identified
  
  [⏳] Step 1: architect (8s / 30s timeout)
     Status: RUNNING
  
  [⏬] Step 2: developer
     Status: PENDING

Duration: 23s / 300s timeout
Progress: 33% (1/3 completed)
```

### Artifacts Sauvegardés

Chaque exécution crée des artifacts dans `.ai-workflow/artifacts/` :

```
.ai-workflow/artifacts/
├── brainstorming_2025-03-06T10:30:00.json
│  ├── workflow_config
│  ├── steps[]
│  │  ├── agent: analyst
│  │  ├── verdict: SUCCESS
│  │  ├── output: { requirements: [...] }
│  │  └── duration: 15.2
│  ├── final_verdict: SUCCESS
│  └── total_duration: 45.8
│
└── party-mode_2025-03-06T10:45:00.json
   └── ...
```

### Memory Persistent

Entrée/sortie de chaque agent sauvegardée pour réutilisation :

```python
memory_manager.store(
    key=f"{workflow_name}::{agent_name}::{step_index}",
    value=verdict.output
)
```

Permet de restaurer ou analyser les résultats ultérieurement.

---

## Bonnes Pratiques

### 1. Nommage Clair

```yaml
# ✅ Good
steps:
  - agent: analyst
    name: "Analyze Requirements & Identify Risks"
    description: "Interview stakeholders and document findings"

# ❌ Bad
steps:
  - agent: analyst
    name: "analyze"  # Trop vague
```

### 2. Inputs Explicites

```yaml
# ✅ Good
inputs:
  requirements: "{{ user_input }}"
  context: "{{ context.project }}"
  previous_analysis: "{{ steps[0].output }}"

# ❌ Bad
inputs:
  x: "{{ user_input }}"  # Quelle variable?
  data: "{{ all_context }}"  # Trop large
```

### 3. Timeouts Réalistes

```yaml
# ✅ Good
config:
  timeout_seconds: 120  # 2 minutes par agent
  max_parallel_workers: 4

# ❌ Bad
config:
  timeout_seconds: 10  # Trop court pour agent complexe
```

### 4. Error Handling Explicite

```yaml
config:
  continue_on_error: false  # Défaut: arrêter sur erreur
  critical_steps: ["architect", "developer"]
  retry_count: 2
  retry_backoff: exponential
```

---

## Cas d'Usage

### Use Case 1: Spécification Rapide

**Workflow** : `brainstorming` (séquentiel, ~1 min)

```bash
ai-workflow run --workflow brainstorming \
  --input "Build a TODO app backend"
```

Résultat : Analysis → Design → Code skeleton

### Use Case 2: Approche Multi-Stakeholder

**Workflow** : `party-mode` (parallèle, ~30s)

```bash
ai-workflow run --workflow party-mode \
  --context '{"business": "E-commerce", "users": "Businesses"}'
```

Résultat : PM view + UX view + Architecture + Dev plan

### Use Case 3: Découverte Profonde

**Workflow** : `advanced-elicitation` (itératif, ~5 min)

```bash
ai-workflow run --workflow advanced-elicitation \
  --user-input "Scale platform to 1M users" \
  --depth deep
```

Résultat : PRD complet avec insights de marché & recherche utilisateur

