# Whitepaper Notes – The New SDLC with Vibe Coding

## Executive Summary

The paper argues that software development is shifting from **writing code (syntax)** to **expressing intent**. AI agents increasingly handle implementation while humans focus on architecture, evaluation, constraints, and judgment. This evolution moves development from simple **vibe coding** toward disciplined **agentic engineering**.

---

# 1. The Shift from Syntax to Intent

Historically developers translated:

```text
Problem
→ Design
→ Code
→ Software
```

The new model becomes:

```text
Intent
→ AI Agent
→ Implementation
→ Verification
→ Software
```

The developer's value increasingly comes from:

- Defining objectives
- Designing systems
- Setting constraints
- Evaluating outcomes
- Making architectural decisions

rather than manually writing code.

---

# 2. Understanding AI Agents

An AI agent operates through a continuous loop:

```text
Perceive
→ Plan
→ Act
→ Observe
→ Iterate
```

## Key Components

| Component | Purpose |
|------------|----------|
| Model | Reasoning engine |
| Tools | APIs, databases, code execution |
| Memory | Retains context |
| Orchestration | Controls workflow |
| Deployment | Production infrastructure |

The agent loop is the foundation of modern AI systems.

---

# 3. Vibe Coding vs Agentic Engineering

The paper presents these as opposite ends of a spectrum.

## Vibe Coding

### Characteristics

- Natural language prompts
- Minimal planning
- Manual verification
- Rapid prototyping
- High risk

### Suitable For

- Experiments
- Personal projects
- Proofs of concept
- Hackathons

---

## Agentic Engineering

### Characteristics

- Structured specifications
- Automated testing
- Evaluation frameworks
- Guardrails
- Human oversight

### Suitable For

- Enterprise software
- Production systems
- Team environments
- Mission-critical applications

### Key Difference

The core difference is not AI usage but **verification and governance**.

---

# 4. Context Engineering is the New Skill

The paper argues that prompt engineering is being replaced by **context engineering**.

Developers must provide:

1. Instructions
2. Knowledge
3. Memory
4. Examples
5. Tools
6. Guardrails

The quality of AI output depends more on context than prompt wording.

---

## Static Context

Always available:

- System instructions
- Rules
- Architecture standards
- Project conventions

---

## Dynamic Context

Loaded when required:

- Documentation
- Tool results
- Skills
- Session history
- Retrieved knowledge

### Key Principle

The goal is to give AI the same information a competent teammate would need.

---

# 5. AI is Reshaping the SDLC

AI compresses traditional development cycles.

## Requirements

AI can:

- Generate user stories
- Build prototypes
- Identify edge cases
- Produce specifications

---

## Architecture

Still largely human-led because architecture requires:

- Business judgment
- Trade-off analysis
- Strategic decision making

---

## Implementation

AI increasingly generates code while humans review and guide.

---

## Testing

Tests become the primary way of communicating intent to AI.

---

## Maintenance

AI helps:

- Understand legacy systems
- Refactor old code
- Modernize applications
- Reduce technical debt

---

# 6. The Factory Model

One of the most important concepts in the paper.

The developer's job becomes:

```text
Build the system
that builds the software
```

Developers design:

- Specifications
- Constraints
- Tests
- Feedback loops
- Evaluation mechanisms

Agents generate code.

Tests verify output.

Humans verify correctness.

---

# 7. Harness Engineering

A model alone is not an agent.

```text
Agent = Model + Harness
```

## The Harness Contains

- Rules
- Tools
- Sandboxes
- Orchestration
- Guardrails
- Observability

### Key Insight

Many AI failures are not model failures.

They are harness failures caused by:

- Poor context
- Missing tools
- Weak constraints
- Insufficient verification

---

# 8. Developers Become Conductors and Orchestrators

## Conductor Mode

Working directly with AI:

- Pair programming
- Reviewing generated code
- Real-time guidance
- Interactive development

---

## Orchestrator Mode

Managing multiple agents:

- Assigning tasks
- Reviewing outputs
- Monitoring workflows
- Delegating implementation

### Future Direction

Developers will spend more time orchestrating than coding.

---

# 9. The 80% Problem

AI can often generate:

```text
80% of a solution very quickly
```

The remaining:

```text
20%
```

typically contains:

- Edge cases
- Business rules
- Error handling
- Integration issues
- Architectural decisions

### Key Lesson

The final 20% still requires significant human expertise.

---

# 10. Economics of AI Development

## Vibe Coding

### Cost Profile

```text
Low CapEx
High OpEx
```

### Risks

- Technical debt
- Poor maintainability
- Security vulnerabilities
- Repeated prompting cycles

---

## Agentic Engineering

### Cost Profile

```text
High CapEx
Low OpEx
```

### Benefits

- Better quality
- Lower maintenance costs
- Improved scalability
- Reduced long-term expenditure

### Key Insight

Context engineering becomes both a technical and financial optimisation strategy.

---

# Key Personal Takeaways

As a Data Analyst and aspiring AI-enabled analytics professional, the most relevant lessons were:

1. AI amplifies existing processes rather than replacing expertise.
2. Context engineering is becoming as important as coding.
3. Verification and evaluation matter more than generation.
4. Human judgment remains essential for architecture and business decisions.
5. Future professionals will increasingly act as orchestrators of AI systems rather than manual implementers.
6. The most valuable skill is moving from building solutions to designing systems that build solutions.

---

# Applications to Data Analytics

Potential future applications include:

- AI-assisted dashboard development
- Automated report generation
- Data quality monitoring
- Business process automation
- Intelligent decision support systems
- Analytics workflow orchestration
- AI-powered business intelligence solutions

---

# Key Quote

> "Generation is solved. Verification, judgment, and direction are the new craft."

---

# One-Sentence Summary

> The future of software development is not about writing more code; it is about designing the context, constraints, evaluations, and systems that enable AI agents to produce reliable software.