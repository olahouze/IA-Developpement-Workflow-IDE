# Agents — Catalog des 15 Agents Spécialisés

Index centralisé des agents IA disponibles dans l'AI Workflow Engine. Chaque agent a un fichier détaillé avec profil, prompts, tools et exemples.

## 📊 Vue d'ensemble

Les agents sont organisés par domaine :

| Catégorie | Agents | Rôle |
|-----------|--------|------|
| **🎭 Orchestration** | [BMAD Master](agents/bmad-master.md) | Contrôle & coordination |
| **🔍 Discovery** | [Analyst](agents/analyst.md), [Researcher](agents/researcher.md), [Product Manager](agents/product-manager.md), [UX Designer](agents/ux-designer.md) | Découverte & spécification |
| **🏗️ Architecture** | [Architect](agents/architect.md), [Security Expert](agents/security.md) | Design & compliance |
| **💻 Development** | [Developer](agents/developer.md), [Quick Flow Solo Dev](agents/quick-flow-solo-dev.md) | Implémentation |
| **✅ Quality & DevOps** | [QA Engineer](agents/qa.md), [Testing Specialist](agents/testing-specialist.md), [Code Reviewer](agents/code-reviewer.md), [DevOps Engineer](agents/devops.md) | Tests & déploiement |
| **📚 Support** | [Tech Writer](agents/tech-writer.md), [Scrum Master](agents/scrum-master.md) | Documentation & processus |



---

## 🔗 Agents Détaillés

Pour chaque agent, cliquez sur le lien pour accéder à la documentation complète avec système prompt, tools et exemples.

### 🎭 Orchestration & Coordination

- **[1. BMAD Master](agents/bmad-master.md)** — Orchestrateur principal, gestion ressources

### 🔍 Discovery & Research (4 agents)

- **[2. Analyst](agents/analyst.md)** (Mary) — Business Analysis, market research, requirements
- **[3. Researcher](agents/researcher.md)** — Deep exploration, market sizing, insights  
- **[4. Product Manager](agents/product-manager.md)** (John) — PRD creation, stakeholder alignment
- **[5. UX Designer](agents/ux-designer.md)** (Sally) — User research, wireframing, accessibility

### 🏗️ Architecture & Security (2 agents)

- **[6. Architect](agents/architect.md)** (Winston) — System design, scalability, tech decisions
- **[7. Security Expert](agents/security.md)** — Threat modeling, compliance, vulnerability assessment

### 💻 Development & Implementation (2 agents)

- **[8. Developer](agents/developer.md)** (Amelia) — Code implementation, TDD, full-stack
- **[9. Quick Flow Solo Dev](agents/quick-flow-solo-dev.md)** (Barry) — MVP rapid, lean implementation

### ✅ Quality & Deployment (4 agents)

- **[10. QA Engineer](agents/qa.md)** (Quinn) — Test automation, E2E, coverage
- **[11. Testing Specialist](agents/testing-specialist.md)** — Test strategy, baselines, metrics
- **[12. Code Reviewer](agents/code-reviewer.md)** — Code quality, design patterns, standards
- **[13. DevOps Engineer](agents/devops.md)** — Infrastructure, CI/CD, monitoring, reliability

### 📚 Support & Process (2 agents)

- **[14. Tech Writer](agents/tech-writer.md)** (Paige) — Documentation, diagrams, API docs
- **[15. Scrum Master](agents/scrum-master.md)** (Bob) — Sprint planning, ceremonies, velocity

---

## 🎯 Organiser les Agents par Workflow

### Brainstorming (séquence : 3 agents)
1. [Analyst](agents/analyst.md) — Analyser requirements
2. [Architect](agents/architect.md) — Designer solution
3. [Developer](agents/developer.md) — Implémenter

### Party Mode (parallèle : 4 agents)
- [Product Manager](agents/product-manager.md) — Perspective produit
- [UX Designer](agents/ux-designer.md) — Perspective design
- [Architect](agents/architect.md) — Perspective architecture
- [Developer](agents/developer.md) — Perspective implémentation

### Advanced Elicitation (itératif : 4 agents)
1. [Analyst](agents/analyst.md) — Analyse initiale
2. [Researcher](agents/researcher.md) — Deep research (itérations)
3. [Product Manager](agents/product-manager.md) — PRD création
4. [UX Designer](agents/ux-designer.md) — Design refinement

### Full Project Cycle (complet : 8+ agents)
1. [Analyst](agents/analyst.md) — Validation
2. [Product Manager](agents/product-manager.md) — Specification
3. [Architect](agents/architect.md) — Design
4. [Developer](agents/developer.md) — Building
5. [QA Engineer](agents/qa.md) — Testing
6. [Security Expert](agents/security.md) — Security audit
7. [DevOps Engineer](agents/devops.md) — Deployment
8. [Tech Writer](agents/tech-writer.md) — Documentation

---

## 📊 Sélectionner par Cas d'Usage

| Cas | Agents |
|-----|--------|
| **MVP Rapide** | [Quick Flow Solo Dev](agents/quick-flow-solo-dev.md), [Developer](agents/developer.md) |
| **Système Enterprise** | [Analyst](agents/analyst.md), [Architect](agents/architect.md), [Security Expert](agents/security.md), [DevOps Engineer](agents/devops.md), [QA Engineer](agents/qa.md) |
| **Startup Discovery** | [Analyst](agents/analyst.md), [Product Manager](agents/product-manager.md), [UX Designer](agents/ux-designer.md) |
| **Scale to 1M Users** | [Researcher](agents/researcher.md), [Architect](agents/architect.md), [DevOps Engineer](agents/devops.md) |
| **Compliance/Regulatory** | [Security Expert](agents/security.md), [Tech Writer](agents/tech-writer.md) |

---

## 💡 Bonnes Pratiques

### ✅ Chaîner logiquement

```yaml
steps:
  - agent: analyst        # Comprendre
  - agent: architect      # Designer
  - agent: developer      # Implémenter
  - agent: qa             # Tester
  - agent: devops         # Déployer
```

### ✅ Passer le contexte

```yaml
steps:
  - agent: analyst
    inputs:
      requirements: "{{ user_input }}"
  
  - agent: architect
    inputs:
      analysis: "{{ steps[0].output }}"  # Output du step précédent
```

### ❌ Erreurs à éviter

- Un seul agent fait tout → Utiliser agents spécialisés
- Coder sans requirements → Commencer par [Analyst](agents/analyst.md)
- Ignorer sécurité → Inclure [Security Expert](agents/security.md)
- Pas de tests → Ajouter [Testing Specialist](agents/testing-specialist.md)
- Déployer sans infra → Impliquer [DevOps Engineer](agents/devops.md)

