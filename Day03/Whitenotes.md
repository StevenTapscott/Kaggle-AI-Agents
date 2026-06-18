# Day 03 – Agent Skills White Notes

## Google Generative AI Intensive Course

---

# Core Idea

Agent Skills are a mechanism for giving AI agents **on-demand specialist expertise** without permanently increasing their context window.

Instead of placing all instructions, procedures, examples, and domain knowledge into one giant system prompt, knowledge is packaged into reusable Skills that are loaded only when required.

This solves one of the largest problems in agent engineering:

**Context Rot**

---

# What is Context Rot?

Context Rot occurs when an agent receives excessive instructions, documents, examples, tool outputs, and conversation history.

### Effects

- Reduced accuracy
- Lower instruction adherence
- Increased hallucinations
- Poor reasoning performance
- Higher token costs

The whitepaper argues:

> Too many instructions often produce worse results.

Skills combat this problem through selective loading.

---

# What is an Agent Skill?

An Agent Skill is a structured folder that contains procedural knowledge.

Minimum requirement:

```text
SKILL.md
```

Optional components:

```text
skill_name/
│
├── SKILL.md
├── scripts/
├── references/
├── assets/
```

A Skill transforms a general-purpose agent into a specialist only when needed.

---

# Why Skills Matter

The paper identifies four major problems Skills solve.

## 1. Context Rot

Load knowledge only when needed.

---

## 2. Procedural Memory

LLMs already have:

- Semantic memory (facts)
- Episodic memory (events)

Skills provide:

- Procedural memory

The agent learns:

```text
How to perform a task
```

rather than simply remembering information.

---

## 3. Multi-Agent Complexity

Traditional solution:

```text
Router Agent
│
├── Finance Agent
├── HR Agent
├── Legal Agent
└── Support Agent
```

Alternative:

```text
One Agent
+
Many Skills
```

This reduces:

- Maintenance
- Deployments
- Orchestration complexity

---

## 4. Portability

A Skill is essentially:

```text
Folder + Markdown
```

Any agent with filesystem access can use it.

---

# Skill Anatomy

Example:

```text
cafe-preparation/
│
├── SKILL.md
├── scripts/
│   ├── calc_quantities.py
│   └── convert_to_ingredients.py
│
├── references/
│   ├── recipes.md
│   └── minimums.md
│
└── assets/
    ├── prep_sheet.md
    └── shopping_template.md
```

---

# Progressive Disclosure

The most important architectural concept.

Skills load in three layers.

## Layer 1 – Metadata

Always loaded.

```text
Name
Description
```

---

## Layer 2 – Skill Body

Loaded only when triggered.

```text
SKILL.md instructions
Workflow
Rules
```

---

## Layer 3 – Supporting Resources

Loaded only if needed.

```text
References
Assets
Scripts
```

Scripts execute outside the context window.

---

# Benefits of Progressive Disclosure

Without Skills:

```text
50 workflows
=
15,000+ tokens
every request
```

With Skills:

```text
Metadata
+
One active Skill
```

Approximately:

```text
6,000 tokens
```

instead of:

```text
15,000+ tokens
```

The paper cites examples where active context dropped by over 98%.

---

# The SKILL.md File

The heart of every Skill.

Example:

```yaml
---
name: cafe-preparation
description: |
  Calculates ingredient needs and
  generates preparation sheets.

  Use when estimating quantities,
  ingredient conversions or
  shopping lists.

  Do NOT use for scheduling
  or accounting.
---
```

---

# The Description Field

The description acts as:

```text
Routing Logic
```

The model reads descriptions to decide:

```text
Should this Skill load?
```

A good description includes:

- What it does
- When to use it
- When NOT to use it

---

# Building Skills

## Path A – Human Expertise

Convert existing knowledge into Skills.

Examples:

- SOPs
- Runbooks
- Onboarding guides
- Compliance documents

---

## Path B – Agent Generated

Agent completes a task.

The workflow proves useful.

Agent proposes a Skill.

Human reviews and approves.

This creates:

```text
Meta-Skills
```

Skills that create Skills.

---

# Skills vs MCP

## MCP

Provides access.

Examples:

- BigQuery
- Salesforce
- Google Drive
- Internal APIs

MCP answers:

```text
What can I reach?
```

---

## Skills

Provide expertise.

Skills answer:

```text
How should I perform this task?
```

---

# Skills vs AGENTS.md

## AGENTS.md

Always loaded.

Contains:

- Project conventions
- Stack information
- Build instructions

---

## Skills

Loaded on demand.

Contain:

- Task-specific expertise

Best practice:

```text
AGENTS.md
+
Skills
```

Together.

---

# Why Skills Became Popular

Before Skills:

```text
Many specialized agents
```

Problems:

- Complex routing
- Multiple deployments
- Difficult maintenance

Skills introduced:

```text
One agent
Many specialist capabilities
```

---

# Evaluation of Skills

A Skill without testing is unreliable.

Research cited in the paper found:

```text
19%
```

of Skills actually reduced performance.

---

# Four Failure Modes

## Trigger Failure

Correct Skill never loads.

OR

Wrong Skill loads.

---

## Execution Failure

Skill activates but produces poor output.

---

## Token Budget Failure

Skill consumes excessive context.

---

## Regression Failure

New Skill breaks existing Skills.

---

# Evaluation Toolkit

## 1. Unit Tests

Run during CI/CD.

## 2. Golden Dataset

Curated examples.

Expected:

- Inputs
- Outputs
- Tool calls

## 3. LLM-as-Judge

Peer model evaluates results.

## 4. Red Team Testing

Boundary conditions.

Failure probing.

## 5. Canary Testing

Small-scale production deployment.

Monitor before full rollout.

---

# Trigger Quality

Target:

```text
90%+
```

trigger accuracy.

Test:

### Positive Cases

Skill should activate.

### Negative Cases

Skill should not activate.

---

# Evaluation Driven Development (EDD)

Instead of:

```text
Write Skill
Then Test
```

Use:

```text
Write Tests
Then Skill
```

Example:

```json
{
  "input": "...",
  "expected_skill": "...",
  "expected_tool_calls": [],
  "expected_output": "..."
}
```

---

# Token Budget Reality

Large context windows do not solve the problem.

Research shows:

Performance declines long before context limits are reached.

Even:

```text
1,000,000 token windows
```

still experience context rot.

---

# Skill Authority Levels

## Read Only

Can view information.

Cannot modify systems.

---

## Draft Only

Produces content.

Requires human approval.

---

## Action Allowed

Can perform real actions.

Requires extensive testing.

Examples:

- Refunds
- Messages
- Reservations

---

# Skills in Production

Google Agents CLI demonstrates Skills across:

- Scaffolding
- Development
- Evaluation
- Deployment
- Publishing
- Monitoring

The whitepaper argues:

> The expertise lives in the Skill, not the runtime.

---

# Why Skills Are the Unit of Improvement

Traditional improvement:

- Better model
- Fine tuning
- Larger prompts

Skill-based improvement:

```text
New Skill
```

Benefits:

- Faster
- Safer
- Version controlled
- Easier ownership

---

# Meta-Skills

Skills that:

- Create Skills
- Improve Skills
- Evaluate Skills
- Expand Skill libraries

Examples:

- Skill creators
- Skill optimizers
- Self-learning Skill systems

---

# Risks of Meta-Skills

Agents optimizing themselves require:

- Strong evaluations
- Human review
- Regression testing

Otherwise:

The Skill library may degrade while metrics appear to improve.

---

# Composing Skills

Complex workflows require orchestration.

Recommended architecture:

```text
DAG
(Directed Acyclic Graph)
```

Benefits:

- Better routing
- Isolated state
- Reduced context growth
- Easier debugging

---

# Capability Profiles

A Capability Profile defines:

- Active Skills
- Tools
- Guardrails
- Model parameters

Instead of loading everything, profiles switch capabilities as needed.

---

# Context Debt

Equivalent to technical debt.

Occurs when authors continually add:

```text
ALWAYS DO THIS
NEVER DO THAT
```

to prompts.

Result:

- Bloated context
- Reduced effectiveness

Best practice:

```text
Move logic into code
```

rather than instructions.

---

# Skill Design Principles

## One Skill = One Job

If description needs "and", it may be two Skills.

## Descriptions Matter Most

Descriptions drive routing.

## Treat Skills Like Code

- Version control
- Testing
- Reviews
- Ownership

## Domain Experts Own Domain Skills

Not AI teams.

## Keep Skills Portable

Avoid platform lock-in.

---

# Skill Smells

Warning signs:

- Over 5,000 words
- Too many responsibilities
- No test cases
- Endless edge-case sections
- Generic descriptions

---

# One-Line Mental Model

```text
System Prompt = Instinct
AGENTS.md = Project Handbook
MCP = Hands
RAG = Library
Skill = Experienced colleague's runbook
```

---

# Exam Cheat Sheet

## Context Rot

Performance degradation caused by excessive context, instructions, and noise.

---

## Progressive Disclosure

Three-stage loading strategy:

1. Metadata
2. SKILL.md
3. References / Assets / Scripts

Loaded only when needed.

---

## Procedural Memory

Knowledge of:

```text
How to perform tasks
```

rather than simply remembering facts.

---

## Four Skill Failure Modes

1. Trigger Failure
2. Execution Failure
3. Token Budget Failure
4. Regression Failure

---

## Three Skill Authority Levels

1. Read Only
2. Draft Only
3. Action Allowed

---

## Five Evaluation Methods

1. Unit Tests
2. Golden Dataset
3. LLM-as-Judge
4. Red Team Testing
5. Canary Testing

---

# Final Takeaway

Agent Skills provide a scalable method for giving agents specialist expertise while avoiding context rot.

Instead of:

```text
One giant prompt
```

Modern agent systems use:

```text
General Agent
+
Portable Skills
+
Progressive Disclosure
```

This allows a single agent to flex into hundreds of specialist roles while maintaining performance, portability, and maintainability.

Source: Agent Skills Whitepaper (May 2026). :contentReference[oaicite:0]{index=0}
