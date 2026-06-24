# AI Agents Intensive with Google

## Project Overview

This repository documents my participation in the **5-Day AI Agents Intensive Course with Google**, hosted through Kaggle.

The course explores the evolution of software development from traditional syntax-based coding toward **agentic engineering**, **vibe coding**, and **AI-assisted development workflows**.

Across the five days, I documented key concepts, whitepaper notes, codelabs, practical setup work, and reflections covering AI agents, interoperability, agent skills, security, evaluation, and production-grade development practices.

**Status:** Complete

---

## Objectives

- Understand AI agents and agentic workflows
- Explore vibe coding and agentic engineering
- Learn how AI agents interact with tools, data, users, and other agents
- Understand Model Context Protocol (MCP), A2A, A2UI, AP2, and UCP
- Explore Agent Skills as portable procedural memory
- Understand security, evaluation, observability, and guardrails for AI agents
- Learn how spec-driven development supports production-grade AI-assisted software delivery
- Build portfolio-ready AI engineering documentation

---

## Technologies & Platforms

### AI & Development

- Google AI Studio
- Google Antigravity
- Antigravity CLI
- Gemini Models
- AI Agents
- Agents CLI
- Agent Development Kit (ADK)

### Cloud & Deployment

- Google Cloud Run
- Google Cloud tooling

### Standards & Protocols

- Model Context Protocol (MCP)
- Agent-to-Agent Protocol (A2A)
- Agent-to-User Interface (A2UI)
- Agent Payments Protocol (AP2)
- Universal Commerce Protocol (UCP)

### Development Practices

- Spec-Driven Development (SDD)
- Behavior-Driven Development (BDD)
- Agent Skills
- Agent Evaluation
- Zero-Trust Development
- Human-in-the-Loop controls
- Sandboxing
- Observability

### Version Control

- Git
- GitHub

---

## Course Progress

| Day | Topic | Status |
|---|---|---|
| Day 1 | Introduction to Agents & Vibe Coding | Complete |
| Day 2 | Agent Tools & Interoperability | Complete |
| Day 3 | Agent Skills | Complete |
| Day 4 | Vibe Coding Agent Security and Evaluation | Complete |
| Day 5 | Spec-Driven Production Grade Development | Complete |

---

## Repository Structure

```text
Kaggle-AI-Agents/
│
├── README.md
│
├── Day01/
│   ├── Whitepaper-Notes.md
│   ├── Key-Concepts.md
│   ├── Reflection.md
│   └── Screenshots/
│
├── Day02/
│   ├── Whitepaper-Notes.md
│   ├── Key-Concepts.md
│   ├── Reflection.md
│   ├── Antigravity-CLI-Lab/
│   └── MCP-Server-Lab/
│
├── Day03/
│   ├── Whitepaper-Notes.md
│   ├── Key-Concepts.md
│   ├── Reflection.md
│   ├── Skills-Lab/
│   └── Agents-CLI-ADK-Lab/
│
├── Day04/
│   ├── Whitepaper-Notes.md
│   ├── Key-Concepts.md
│   └── Reflection.md
│
└── Day05/
    ├── Whitepaper-Notes.md
    ├── Key-Concepts.md
    └── Reflection.md
```

---

# Day 1 – Introduction to Agents & Vibe Coding

## Topics Covered

- AI Agents
- Vibe Coding
- Agentic Engineering
- Context Engineering
- AI-driven SDLC
- Factory Model
- Harness Engineering
- Developer roles as Conductors and Orchestrators

## Key Learning Outcomes

Day 1 introduced the shift from writing syntax to expressing intent. The key distinction was between casual vibe coding and disciplined agentic engineering.

The main takeaway was that AI does not remove engineering discipline. Instead, it increases the importance of:

- Clear requirements
- Context engineering
- Tests and evaluations
- Architecture
- Guardrails
- Human judgment

---

# Day 2 – Agent Tools & Interoperability

## Topics Covered

- Model Context Protocol (MCP)
- Agent-to-Agent Communication (A2A)
- Agent-to-User Interface (A2UI)
- Agent Payments Protocol (AP2)
- Universal Commerce Protocol (UCP)
- Antigravity CLI
- Google Developer Knowledge MCP Server

## Key Learning Outcomes

Day 2 focused on interoperability standards for agent ecosystems.

The most important concept was that agents become more powerful when they can connect to tools, services, users, and other agents through standardised protocols rather than custom integrations.

Key takeaway:

```text
MCP = Agent to Tools
A2A = Agent to Agent
A2UI = Agent to Interface
AP2 = Agent to Payments
UCP = Agent to Commerce
```

---

# Day 3 – Agent Skills

## Topics Covered

- Agent Skills
- SKILL.md
- Context Rot
- Progressive Disclosure
- Procedural Memory
- Meta-Skills
- Skill Evaluation
- Agents CLI and ADK

## Key Learning Outcomes

Day 3 introduced Agent Skills as portable procedural memory for AI agents.

Instead of loading every instruction into one large system prompt, skills allow agents to load specialist knowledge only when needed.

Key takeaway:

```text
Agent Skills = Specialist expertise on demand
```

This reduces context bloat, improves maintainability, and allows one general-purpose agent to flex into many specialist roles.

---

# Day 4 – Vibe Coding Agent Security and Evaluation

## Topics Covered

- Agent Security
- Agent Evaluation
- Effective Trust
- 7-Pillar Agent Security Architecture
- Sandboxing
- Supply Chain Defence
- Zero Ambient Authority
- Human-in-the-Loop
- Vibe Diff
- Agent Observability
- Intent Drift
- Evaluation Dimensions

## Key Learning Outcomes

Day 4 focused on securing and evaluating non-deterministic AI agents.

The key distinction was:

```text
Security = Did the agent stay within safe boundaries?
Evaluation = Was the agent output actually worth shipping?
```

The whitepaper reinforced that production AI agents require more than working outputs. They need controlled execution, identity management, sandboxing, observability, evaluation pipelines, and continuous trust monitoring.

---

# Day 5 – Spec-Driven Production Grade Development

## Topics Covered

- Spec-Driven Development (SDD)
- Behavior-Driven Development (BDD)
- Gherkin Scenarios
- Production-grade AI-assisted development
- MCP Server implementation
- AI-generated code reviews
- Zero-Trust Development
- Sandboxing
- Guardrails
- Human-in-the-Loop controls
- Policy Servers
- Prompt Sanitization
- Context Hygiene

## Key Learning Outcomes

Day 5 focused on moving from vibe-coded prototypes to production-grade software development.

The central lesson was:

```text
Vibe Coding is not Vibe in Production
```

Production development with AI agents requires clear specifications, reviewed designs, structured tests, controlled tool access, security guardrails, and human oversight.

A strong specification becomes the source of truth for both humans and agents.

---

## Key Concepts Learned

### Agentic Engineering

A disciplined approach to AI-assisted development where agents operate within constraints, tests, evaluations, and human review.

### Context Engineering

The practice of giving an AI agent the right instructions, knowledge, examples, tools, memory, and guardrails at the right time.

### Harness Engineering

The surrounding system that turns a model into an agent, including tools, orchestration, guardrails, sandboxing, observability, and deployment.

### Model Context Protocol

A standard protocol that connects agents to tools and external systems.

### Agent Skills

Portable task-specific workflows that allow agents to load specialist expertise on demand.

### Progressive Disclosure

A context management pattern where only the necessary instructions and resources are loaded when required.

### Spec-Driven Development

A production approach where specifications, scenarios, and architecture guide AI-generated implementation.

### Zero-Trust Agent Development

A security approach where agents are not trusted by default and must operate within scoped permissions, sandboxed environments, and policy controls.

---

## Skills Demonstrated

- AI Agent Concepts
- Agentic Engineering
- Vibe Coding
- Context Engineering
- Model Context Protocol
- Agent Skills
- Antigravity CLI
- Google AI Studio
- Cloud Run Deployment Concepts
- Agent Security
- Agent Evaluation
- Spec-Driven Development
- Technical Documentation
- GitHub Portfolio Documentation
- AI Workflow Analysis

---

## Applications to Data Analytics and Business Intelligence

The course concepts are directly relevant to future analytics and business systems projects, including:

- AI-assisted data analysis
- SQL query agents
- Power BI reporting assistants
- Dataverse-connected agents
- Automated report generation
- Data quality monitoring
- Business process automation
- AI-powered documentation workflows
- Agentic business intelligence systems

These ideas align with future portfolio projects involving Power BI, SQL, Power Apps, Power Automate, Dataverse, Azure, and AI agents.

---

## Final Reflection

The most important learning from this course is that AI-assisted development is not just about generating code faster.

The real value comes from designing the system around the agent:

```text
Specifications
Context
Tools
Skills
Security
Evaluation
Guardrails
Observability
Human judgment
```

As implementation becomes increasingly automated, the most valuable skills shift toward problem definition, architecture, evaluation, security, and orchestration.

This course provided a strong foundation for understanding how modern AI agents can be used responsibly in software development, analytics, automation, and enterprise systems.

---

## Author

**Steven Tapscott**

GitHub: [StevenTapscott](https://github.com/StevenTapscott)
---

## Current Status

This repository is actively being updated as I progress through the 5-Day AI Agents Intensive Course.
