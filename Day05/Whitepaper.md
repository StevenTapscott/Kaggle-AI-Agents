# Day 05 – Agent Skills White Notes

## Google Generative AI Intensive Course

Source: *Agent Skills Whitepaper (May 2026)* :contentReference[oaicite:0]{index=0}

---

# Core Idea

Agent Skills are becoming the missing procedural memory layer for AI agents.

Models already have:

```text
Semantic Memory
= Facts

Episodic Memory
= Past interactions
```

What they historically lacked:

```text
Procedural Memory
= How to perform tasks
```

Agent Skills solve this problem by packaging repeatable workflows into reusable, portable units. :contentReference[oaicite:1]{index=1}

---

# One-Line Definition

An Agent Skill is:

```text
A portable folder that teaches
an agent how to perform a task.
```

Minimum requirement:

```text
SKILL.md
```

Everything else is optional.

---

# Why Agent Skills Matter

The whitepaper identifies four major problems Skills solve:

## 1. Context Rot

Large system prompts become bloated.

```text
More Instructions
=
Worse Performance
```

Skills load only when needed.

Result:

```text
Smaller Context
Better Performance
```

---

## 2. Procedural Memory

Models know facts but often forget processes.

Example:

```text
How to onboard a new employee
How to process a refund
How to create compliance reports
```

Skills preserve these workflows.

---

## 3. Multi-Agent Overload

Old solution:

```text
100 workflows
=
100 agents
```

New solution:

```text
1 Agent
+
100 Skills
```

Much easier to maintain.

---

## 4. Portability

Skills are lightweight.

```text
Folder
+
Markdown
```

Any compliant agent can use them.

No vendor lock-in. :contentReference[oaicite:2]{index=2}

---

# Mental Model

Think of a Skill as:

```text
A specialist profession
that an agent can learn on demand.
```

Examples:

```text
HR onboarding
Invoice processing
BigQuery ingestion
Customer refunds
Database management
```

---

# Skill Architecture

Canonical structure:

```text
skill_name/
│
├── SKILL.md          (Required)
├── scripts/          (Optional)
├── references/       (Optional)
├── assets/           (Optional)
```

Only:

```text
SKILL.md
```

is mandatory. :contentReference[oaicite:3]{index=3}

---

# Progressive Disclosure

This is the most important concept.

Skills load in three stages.

---

## Level 1 – Metadata

Always loaded.

Contains:

```text
Name
Description
```

Tiny token footprint.

---

## Level 2 – Skill Body

Loaded only if activated.

```text
SKILL.md instructions
```

---

## Level 3 – Resources

Loaded only when needed.

```text
references/
assets/
scripts/
```

Result:

```text
100 Skills Installed
≠
100 Skills Loaded
```

Only the active skill consumes context. :contentReference[oaicite:4]{index=4}

---

# Skill Anatomy

Example:

```text
cafe-preparation/
```

Contains:

### SKILL.md

Instructions.

### scripts/

Python/Bash automation.

### references/

Knowledge files.

### assets/

Templates and schemas.

Example:

```text
shopping_list_template.md
prep_sheet_template.md
```

---

# Path A – Human Written Skills

Most common approach.

Take existing knowledge:

```text
Runbooks
SOPs
Policies
Documentation
```

Convert into:

```text
SKILL.md
```

No coding required. :contentReference[oaicite:5]{index=5}

---

# Path B – Agent Generated Skills

A successful workflow becomes reusable.

Process:

```text
Agent performs task
↓
Task succeeds
↓
Workflow extracted
↓
Skill drafted
↓
Human reviews
```

This is called:

```text
Skill Crystallization
```

The workflow becomes permanent procedural memory. :contentReference[oaicite:6]{index=6}

---

# The Most Important Field

Inside YAML:

```yaml
---
name: cafe-preparation
description: |
  Calculates daily ingredient needs.
  Use when estimating daily quantities.
  Do NOT use for scheduling.
---
```

The description acts as:

```text
Routing Logic
```

The model uses it to decide:

```text
Trigger?
or
Ignore?
```

The description is the most important part of a skill. :contentReference[oaicite:7]{index=7}

---

# Naming Rules

Directory:

```text
snake_case
```

Example:

```text
bigquery_ingestion
```

Skill Name:

```text
kebab-case
```

Example:

```text
pdf-processing
```

Prefer:

```text
gerunds
```

Examples:

```text
managing-databases
processing-pdfs
```

Avoid:

```text
utils
tools
helper
```

---

# What Goes Where?

## SKILL.md

Instructions.

---

## scripts/

Deterministic logic.

Examples:

```text
Calculations
Formatting
Parsing
Conversions
```

---

## references/

Domain knowledge.

Examples:

```text
Policies
Rules
Definitions
```

---

## assets/

Templates.

Examples:

```text
Markdown templates
Schemas
Output formats
```

Rule:

```text
If SKILL.md gets long,
move content to references/.
```

---

# Installing Skills

Three deployment models.

---

## 1. File Drop

Coding agents.

```text
.agents/skills/
```

Drop folder.

Restart.

Done.

---

## 2. UI Install

Enterprise platforms.

Upload skill through:

```text
Marketplace
Registry
Portal
```

---

## 3. Programmatic

Frameworks such as ADK.

```python
SkillToolset()
```

Skills loaded directly in code. :contentReference[oaicite:8]{index=8}

---

# Skills vs MCP

Common interview question.

---

## MCP

Provides:

```text
Reach
```

Access to:

```text
BigQuery
Drive
Salesforce
APIs
```

---

## Skills

Provide:

```text
Know-How
```

Teach:

```text
How to use tools
How to solve tasks
How to execute workflows
```

Relationship:

```text
Skills + MCP
```

not

```text
Skills OR MCP
```

They complement each other. :contentReference[oaicite:9]{index=9}

---

# Skills vs AGENTS.md

## AGENTS.md

Always loaded.

Contains:

```text
Project conventions
Build commands
Standards
```

---

## Skills

Loaded on demand.

Contains:

```text
Specialized workflows
```

Best practice:

```text
Use both.
```

:contentReference[oaicite:10]{index=10}

---

# Why Skills Exploded

Before Skills:

```text
Router Agent
 ├─ HR Agent
 ├─ PDF Agent
 ├─ Invoice Agent
 └─ Compliance Agent
```

Problems:

- Deployment complexity
- CI/CD complexity
- Routing complexity

---

After Skills:

```text
Single Agent
+
Skill Library
```

Simpler architecture.

Much lower operational burden. :contentReference[oaicite:11]{index=11}

---

# When Multi-Agent Still Wins

Skills do NOT replace multi-agent systems.

Use multi-agent when you need:

```text
Parallel execution
Different security boundaries
Different models
Agent-to-agent communication
Hierarchical decomposition
```

Otherwise:

```text
Single Agent + Skills
```

is often enough. :contentReference[oaicite:12]{index=12}

---

# Skill Evaluation

A skill without tests is:

```text
Hope
```

not capability. :contentReference[oaicite:13]{index=13}

---

# Four Failure Modes

## 1. Trigger Failure

Wrong skill fires.

Or correct skill doesn't fire.

---

## 2. Execution Failure

Correct skill.

Wrong result.

---

## 3. Token Budget Failure

Skill too large.

Creates context rot.

---

## 4. Regression

New skill breaks existing skills.

---

# Evaluation Toolkit

Five testing layers:

| Method | Purpose |
|----------|----------|
| Unit Tests | Every change |
| Golden Dataset | Expected outputs |
| LLM Judge | Quality scoring |
| Red Team | Adversarial testing |
| Canary Deployments | Production testing |

:contentReference[oaicite:14]{index=14}

---

# Trigger Accuracy

Target:

```text
90%+
```

Description must support:

- Positive triggers
- Negative triggers
- Clear scope
- Rephrase robustness

The description determines routing success.

---

# Evaluation Driven Development (EDD)

Traditional:

```text
Write Skill
Then Test
```

EDD:

```text
Write Tests
Then Skill
```

Start with:

```json
Input
Expected Tools
Expected Output
```

before writing SKILL.md. :contentReference[oaicite:15]{index=15}

---

# Token Economics

Big Prompt:

```text
50 workflows
=
15,000+ tokens
```

Skills:

```text
50 descriptions
+
1 active skill
≈ 6,000 tokens
```

Massive reduction.

Anthropic example:

```text
150,000
↓
2,000
```

98% reduction. :contentReference[oaicite:16]{index=16}

---

# Meta-Skills

Skills that improve skills.

Four categories:

## Authoring

Generate SKILL.md.

---

## Trace Harvesting

Convert successful runs into skills.

---

## Improvement

Repair weak skills.

---

## Library Evolution

Create new skills automatically.

:contentReference[oaicite:17]{index=17}

---

# Rule For Meta-Skills

Never trust autonomous improvement without evaluation.

Always:

```text
Draft
→ Review
→ Test
→ Promote
```

Human oversight remains mandatory. :contentReference[oaicite:18]{index=18}

---

# Skill Composition

Real systems need many skills.

Three major approaches:

---

## Linear Pipeline

```text
A → B → C
```

Simple.

---

## DAG Orchestration

```text
Graph-based execution
```

Reliable.

Scalable.

---

## Capability Profiles

Dynamic bundles:

```text
Skills
Tools
Prompts
Models
```

Loaded as needed. :contentReference[oaicite:19]{index=19}

---

# Context Debt

Bad approach:

```text
ALWAYS DO THIS
ALWAYS DO THAT
ALWAYS NEVER...
```

inside prompts.

Result:

```text
Context Debt
```

Models eventually ignore instructions.

Better:

```text
Move logic into code.
Move workflows into skills.
```

:contentReference[oaicite:20]{index=20}

---

# Choosing Skills

Three trust levels.

## First-Party Skills

Highest trust.

Examples:

- Google
- Anthropic
- Stripe
- Microsoft

---

## Organization Skills

Internal company skills.

---

## Community Skills

Audit carefully.

Pin versions.

Review code. :contentReference[oaicite:21]{index=21}

---

# Key Interview Terms

### Agent Skill

Portable procedural memory unit.

### Progressive Disclosure

Load instructions only when needed.

### Trigger Accuracy

Probability correct skill activates.

### Context Rot

Performance degradation from large prompts.

### Meta-Skill

Skill that creates or improves skills.

### Capability Profile

Runtime bundle of skills and tools.

### Context Debt

Prompt bloat caused by excessive instructions.

### Evaluation-Driven Development (EDD)

Tests written before the skill.

---

# One-Line Mental Model

```text
MCP gives agents access.

Skills teach agents expertise.
```

---

# Final Takeaway

Agent Skills are emerging as the procedural memory layer for AI agents. Rather than building increasingly complex multi-agent systems or gigantic system prompts, organizations can package expertise into lightweight, portable, testable Skill libraries that load on demand.

The result is:

```text
Smaller Context
Better Performance
Reusable Knowledge
Portable Expertise
Simpler Architectures
```

and a shift from:

```text
Prompt Engineering
```

toward:

```text
Procedural Engineering
```

for enterprise-scale agent systems. :contentReference[oaicite:22]{index=22}
