# Architecture — AI Workflow Engine

## Vue d'ensemble

L'AI Workflow Engine est un moteur d'orchestration modulaire conçu pour exécuter de workflows complexes coordonnant plusieurs agents IA spécialisés.

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface (Typer)                  │
│              init | run | status | agents                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Context Builder & Configuration                │
│           (FileManager, MemoryManager, SkillManager)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│         Workflow Engine (State Machine via transitions)     │
│         ├─ WorkflowState (PENDING → RUNNING → COMPLETE)    │
│         ├─ Orchestration (séquence | parallèle)            │
│         └─ Error Handling & Verdicts                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
   ┌───▼──┐      ┌────▼─────┐    ┌───▼──┐
   │Agent │      │Fork/Join │    │Verdict
   │Runner│      │Executor  │    │Logic│
   └──────┘      └──────────┘    └─────┘
       │               │               │
       └───────────────┼───────────────┘
                       │
          ┌────────────▼──────────────┐
          │   17 Agents spécialisés   │
          │  (brainstormer, analyst,  │
          │   architect, developer...)│
          └───────────────────────────┘
```

## Couches Architecturales

### 1️⃣ Couche API / Interface Utilisateur

**Fichier** : `src/ai_workflow/cli.py`

Utilise **Typer** pour une CLI riche et interactive.

```python
# Commandes disponibles:
ai-workflow init --name mon-projet      # Initialiser un projet
ai-workflow run --workflow brainstorming # Exécuter un workflow
ai-workflow status                       # Voir l'état d'un workflow
ai-workflow agents                       # Lister les agents disponibles
```

**Responsabilité** :
- Parser les arguments CLI
- Valider les entrées utilisateur
- Charger la configuration de projet
- Deleguer l'exécution au WorkflowEngine
- Afficher les résultats en format rich (table, tree, etc.)

---

### 2️⃣ Couche Configuration & Contexte

**Fichiers** : `src/ai_workflow/config/`, `src/ai_workflow/managers/`

#### ConfigSchema (`config/schema.py`)

Modèles Pydantic pour validation :

```python
class ProjectConfig(BaseModel):
    name: str
    version: str
    workflows: list[str]
    agents: list[str]

class WorkflowConfig(BaseModel):
    name: str
    description: str
    agents: list[str]
    orchestration: str  # "sequential" ou "parallel"
```

#### FileManager (`managers/file_manager.py`)

Gestion I/O fichiers et artefacts :

```python
class FileManager:
    def load_config(path: Path) -> dict
    def save_artifact(key: str, data: Any) -> Path
    def load_memory(key: str) -> Any
    def list_projects() -> list[str]
```

#### MemoryManager (`managers/memory_manager.py`)

Préservation du contexte entre exécutions :

```python
class MemoryManager:
    def store(key: str, value: Any) -> None
    def retrieve(key: str) -> Any
    def clear() -> None
    def export_snapshot() -> dict
```

#### SkillManager (`managers/skill_manager.py`)

Registre des compétences/outils disponibles pour les agents :

```python
class SkillManager:
    def register_skill(name: str, fn: Callable) -> None
    def get_skill(name: str) -> Callable
    def list_available_skills() -> list[str]
```

#### ContextBuilder (`managers/context_builder.py`)

Construit le contexte d'exécution avec variables, secrets, données :

```python
class ContextBuilder:
    def build_agent_context(agent: Agent, workflow_state: dict) -> dict
    def inject_memory() -> None
    def resolve_variables(template: str) -> str
```

---

### 3️⃣ Couche Modèles de Données

**Fichier** : `src/ai_workflow/models/`

Définitions Pydantic des entités principales :

#### Agent (`models/agent.py`)

```python
class Agent(BaseModel):
    name: str
    role: str
    expertise: list[str]
    description: str
    system_prompt: str
    tools: list[str]

class AgentVerdictType(StrEnum):
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
```

#### Workflow (`models/workflow.py`)

```python
class Workflow(BaseModel):
    name: str
    description: str
    steps: list[WorkflowStep]
    orchestration_type: str  # "sequential" ou "parallel"

class WorkflowStep(BaseModel):
    agent_name: str
    inputs: dict
    depends_on: list[str] = []
```

#### Verdict (`models/verdict.py`)

```python
class ExecutionVerdict(BaseModel):
    status: AgentVerdictType
    output: Any
    error_message: str | None = None
    duration_seconds: float
    timestamp: datetime
```

#### Profile (`models/profile.py`)

```python
class UserProfile(StrEnum):
    EXPERT = "expert"
    INTERMEDIATE = "intermediate"
    BEGINNER = "beginner"

class ExecutionProfile(BaseModel):
    user_level: UserProfile
    max_iterations: int
    timeout_seconds: int
    parallel_agents: int
```

---

### 4️⃣ Couche Moteur d'Exécution

**Fichier** : `src/ai_workflow/engine/`

#### WorkflowEngine (`engine/workflow_engine.py`)

Orchestre l'exécution du workflow complet :

```python
class WorkflowEngine:
    def __init__(self, config: ProjectConfig):
        self.workflow_state = WorkflowState.PENDING
        self.machine = Machine(transitions=self.transitions_map)
        self.verdicts: list[ExecutionVerdict] = []
    
    async def execute_workflow(name: str) -> ExecutionVerdict:
        """Exécute un workflow complet"""
        self.workflow_state = WorkflowState.RUNNING
        # Orchestration séquentielle ou parallèle
        # État machine transitions
        # Gestion des erreurs
        self.workflow_state = WorkflowState.COMPLETE
```

**État Machine** (transitions library) :

```
PENDING → RUNNING → COMPLETE
   ↑        ↓
   └─── ERROR (si échec)
```

#### AgentRunner (`engine/agent_runner.py`)

Exécute un agent unique :

```python
class AgentRunner:
    def run_agent(agent: Agent, context: dict) -> ExecutionVerdict:
        """Exécute l'agent avec le contexte donné"""
        # 1. Injecter contexte dans prompt
        # 2. Appeler l'agent (LLM + outils)
        # 3. Capturer output
        # 4. Retourner verdict
```

#### ForkJoin (`engine/fork_join.py`)

Pattern parallélisation pour workflows parallèles :

```python
class ForkJoinExecutor:
    def execute_parallel(agents: list[Agent], context: dict):
        """Exécute plusieurs agents en parallèle, attend sync"""
        with ThreadPoolExecutor(max_workers=N) as executor:
            futures = [executor.submit(run_agent, a, ctx) for a in agents]
            verdicts = [f.result() for f in futures]  # Attend toutes les tâches
        
        # Sync & fusion des résultats
        return merge_verdicts(verdicts)
```

#### Verdict (`engine/verdict.py`)

Logique d'évaluation des résultats :

```python
class VerdictLogic:
    @staticmethod
    def evaluate_all_verdicts(verdicts: list[ExecutionVerdict]) -> ExecutionVerdict:
        """Si tous SUCCESS → SUCCESS, sinon PARTIAL ou ERROR"""
        
    @staticmethod
    def merge_outputs(verdicts: list[ExecutionVerdict]) -> dict:
        """Fusionne les outputs de tous les agents"""
```

---

### 5️⃣ Couche Agents Spécialisés

**Fichier** : `src/ai_workflow/agents/`

Chaque agent est structuré en dossier :

```
agents/
├── registry.py              # Registre centralisé
├── brainstormer/
│   ├── config.yaml
│   ├── system_prompt.md
│   └── tools.yaml
├── analyst/
│   ├── config.yaml
│   ├── system_prompt.md
│   └── tools.yaml
├── architect/
│   ├── config.yaml
│   ├── system_prompt.md
│   └── tools.yaml
...
```

#### Agent Registry (`agents/registry.py`)

Chargement centralisé de tous les agents au démarrage :

```python
class AgentRegistry:
    @staticmethod
    def load_agents() -> dict[str, Agent]:
        """Charge tous les agents depuis agents/*/config.yaml"""
        return {
            "brainstormer": Agent(...),
            "analyst": Agent(...),
            "architect": Agent(...),
            ...
        }
```

#### Configuration Agent (`agents/[name]/config.yaml`)

```yaml
name: analyst
role: Business Analyst
expertise:
  - market research
  - competitive analysis
  - requirements elicitation
description: "Découvre et analyse les requirements"

# Prompt injecté dans le contexte d'exécution
system_prompt_file: system_prompt.md

# Outils disponibles pour cet agent
tools:
  - search_market
  - analyze_competitors
  - interview_stakeholders
```

---

### 6️⃣ Couche Workflows

**Fichier** : `src/ai_workflow/workflows/`

Fichiers YAML définissant les orchestrations :

```yaml
# workflows/brainstorming.yaml
name: brainstorming
description: "Séquence de brainstorming : analyst → architect → dev"
orchestration_type: sequential

steps:
  - agent: analyst
    name: "Analyser les requirements"
    inputs:
      requirements: "{{ user_input }}"
  
  - agent: architect
    name: "Designer la solution"
    inputs:
      analysis: "{{ steps[0].output }}"  # Dépendance
  
  - agent: developer
    name: "Proposer l'implémentation"
    inputs:
      design: "{{ steps[1].output }}"
```

```yaml
# workflows/party-mode.yaml
name: party-mode
description: "Collaboration parallèle : PM, UX, Architect, Dev"
orchestration_type: parallel

steps:
  - agent: product_manager
    inputs:
      context: "{{ project_context }}"
  
  - agent: ux_designer
    inputs:
      context: "{{ project_context }}"
  
  - agent: architect
    inputs:
      context: "{{ project_context }}"
  
  - agent: developer
    inputs:
      context: "{{ project_context }}"
```

---

### 7️⃣ Couche Templates

**Fichier** : `src/ai_workflow/templates/`

Templates Jinja2 pour rendering dynamique :

#### Agent Prompt (`templates/agent_prompt.j2`)

```jinja2
You are {{ agent.name }}, a {{ agent.role }}.
Your expertise: {{ agent.expertise | join(', ') }}

Context:
{{ context | to_yaml }}

Task:
{{ task_description }}

Available tools: {{ tools | join(', ') }}

Instructions:
{{ agent.system_prompt }}
```

#### Workflow Summary (`templates/workflow_summary.j2`)

```jinja2
# Workflow: {{ workflow.name }}

{% for step in steps %}
## Step {{ loop.index }}: {{ step.agent }} — {{ step.name }}
- Status: {{ step.verdict.status }}
- Duration: {{ step.verdict.duration_seconds }}s
- Output:
{{ step.verdict.output | indent(2) }}
{% endfor %}

**Overall**: {{ overall_verdict.status }}
```

---

## Patterns & Décisions d'Architecture

### 1. State Machine avec `transitions`

**Pourquoi** : Gestion explicite des états workflow (PENDING → RUNNING → COMPLETE).

**Trade-off** : `transitions.Machine(model=self)` override `self.state` → renommé en `self.workflow_state` pour éviter conflit.

```python
class WorkflowEngine:
    def __init__(self):
        self.workflow_state = WorkflowState.PENDING  # NOT self.state
        self.machine = Machine(
            states=self.states,
            transitions=self.transitions,
            initial=WorkflowState.PENDING
        )
```

### 2. Fork/Join Pattern

**Séquence** : Agents exécutés un par un (dépendances entre steps)

```python
for step in workflow.steps:
    verdict = agent_runner.execute(step.agent, context)
    context.update(verdict.output)
```

**Parallèle** : Agents indépendants exécutés simultanément

```python
futures = [executor.submit(agent_runner.execute, agent, ctx) for agent in agents]
verdicts = [f.result() for f in futures]  # Await all
```

### 3. Injection de Contexte via Templates Jinja2

Permet la réutilisabilité des prompts agents sans hard-code :

```python
prompt = render_template("agent_prompt.j2", {
    "agent": agent,
    "context": workflow_context,
    "task_description": step.task,
    "tools": skill_manager.list_available()
})
```

### 4. Verdict comme Pattern Principal

Chaque exécution produit un `ExecutionVerdict` :
- `status`: SUCCESS | PARTIAL | ERROR
- `output`: Résultat de l'agent
- `error_message`: Si applicable
- `duration_seconds`: Timing

Permet métriques, retry logic, et merging de résultats parallèles.

### 5. Configuration Centralisée via Pydantic

Validation stricte de tous les inputs :
- Agent definitions
- Workflow definitions
- Project configuration
- User profiles

```python
agent = Agent.model_validate(yaml.safe_load("agents/analyst/config.yaml"))
```

---

## Flux d'Exécution Complet

```
┌─ CLI: ai-workflow run --workflow brainstorming
│
├─ Load ProjectConfig from .ai-workflow/config.yaml
│
├─ Initialize:
│  ├─ FileManager (artifacts, memory)
│  ├─ MemoryManager (contexte)
│  ├─ SkillManager (tools)
│  ├─ ContextBuilder (variables)
│  └─ AgentRegistry (load all 17 agents)
│
├─ Create WorkflowEngine with ProjectConfig
│
├─ Load Workflow YAML (brainstorming.yaml)
│
├─ Execute Workflow:
│  ├─ foreach step in workflow.steps:
│  │  ├─ Get Agent from registry
│  │  ├─ Build context with ContextBuilder
│  │  ├─ Render prompt template with Jinja2
│  │  ├─ Run AgentRunner with context
│  │  ├─ Get ExecutionVerdict
│  │  ├─ Store output in context (for next step)
│  │  └─ Store verdict in verdicts[]
│  │
│  └─ (If parallel) Fork/Join all agents, merge verdicts
│
├─ Evaluate final verdict (all SUCCESS → SUCCESS)
│
├─ Store artifacts & memory snapshot
│
├─ Render summary with workflow_summary.j2
│
└─ Return verdict to CLI, display with rich
```

---

## Conventions & Best Practices

### Nommage

- **Agents** : lowercase avec hyphènes (e.g., `product-manager`, `tech-writer`)
- **Workflows** : lowercase avec hyphènes (e.g., `brainstorming`, `party-mode`)
- **Files** : snake_case Python, kebab-case YAML (e.g., `agent_runner.py`, `brainstorming.yaml`)

### Configuration YAML

```yaml
# ✅ Good
steps:
  - agent: analyst
    name: "Clear description"
    inputs:
      requirement: "{{ user_input }}"

# ❌ Bad
steps:
  - agent_name: analyst  # Inconsistent naming
    description: Find issues  # Vague
    input: "{% raw %}{{ x }}{% endraw %}"  # Raw Jinja without field context
```

### Error Handling

```python
# ✅ Return partial verdict on error
try:
    output = agent_runner.run(agent, context)
except Exception as e:
    return ExecutionVerdict(
        status=AgentVerdictType.ERROR,
        output=None,
        error_message=str(e),
        duration_seconds=duration
    )

# ❌ Suppress errors silently
except:
    pass  # Lost context!
```

### Testing

Toute nouvelle couche doit avoir des tests :

```
tests/
├── test_models/
│   ├── test_agent.py
│   ├── test_workflow.py
│   └── test_verdict.py
├── test_managers/
│   └── test_file_manager.py
├── test_engine/
│   ├── test_workflow_engine.py
│   ├── test_agent_runner.py
│   └── test_fork_join.py
└── test_agents/
    └── test_registry.py
```

---

## Dépendances Clés

| Package | Rôle | Version |
|---------|------|---------|
| **typer** | CLI framework | ^0.9 |
| **transitions** | State machine | ^0.8 |
| **pydantic** | Data validation | ^2.0 |
| **jinja2** | Template rendering | ^3.0 |
| **pyyaml** | Config parsing | ^6.0 |
| **pytest** | Testing | ^7.0 |
| **rich** | Terminal UI | ^13.0 |

---

## Évolutions Futures

1. **Async Execution** : Utiliser `asyncio` pour AgentRunner
2. **Agent Learning** : Stocker les verdicts pour improve les prompts
3. **Multi-LLM** : Support OpenAI, Anthropic, local models
4. **Streaming** : Render agent responses en streaming
5. **Observability** : Logs structurés, traces distribués
