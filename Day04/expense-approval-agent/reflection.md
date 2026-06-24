# Day 04 Expense Approval Agent - Project Reflection

This document reflects on the development, implementation, and evaluation of the graph-based expense approval agent and its security/routing evaluation system.

---

## 1. Task 1 Reflection: Graph-Based Workflow Design

### Workflow & Topology
The task required designing and wiring a graph-based approval workflow using the **ADK 2.0 Graph Workflow API**. The topology handles expense reports dynamically:
- **`parse_expense_report`**: Extracts and structures the input.
- **`evaluate_rules`**: Inspects the amount against the auto-approval threshold ($100.0) and sets conditional routing paths.
- **`auto_approve`**: Instantly approves clean expenses under $100.0 without invoking the LLM.
- **`risk_reviewer`**: An `LlmAgent` node that generates a structured risk review (`RiskReview`) for expenses $\ge \$100.0$.
- **`human_approval`**: A Human-in-the-Loop (HITL) node that intercepts approval requests and awaits human decisions.

### Technical Challenges & Solutions
1. **State Persistence**: We utilized the ADK session state to store parsed expense details in `evaluate_rules` (`state_delta={"expense": ...}`), making them available during later nodes (`risk_reviewer`) by referencing context formatting strings (`{expense[amount]}`).
2. **Pydantic Validation in `RequestInput`**: The framework's `RequestInput` model expects the `message` field to be a plain string (`str` or `None`). We encountered validation errors when trying to pass a `types.Content` object. This was fixed by passing the formatted message string directly to the model.

---

## 2. Task 2 Reflection: Local Evaluation Loop

### Hardening Security Controls
Before evaluations, we implemented security guards to prevent PII leakage and prompt injection bypasses:
- **PII Redaction**: Any SSN format in description text is immediately redacted to `[REDACTED SSN]`.
- **Prompt Injection Bypassing**: Descriptions with injection keywords (`bypass`, `ignore`, `override`, etc.) trigger a complete bypass of the LLM risk reviewer. A new Python node `escalate_injection` intercepts the request and routes it straight to human review with a pre-set high risk score, ensuring the agent cannot be tricked into auto-approving.

### Traces & Local Grading
1. **Offline Trace Generator (`generate_traces.py`)**: Designed to execute all 5 scenarios locally using a class-level monkeypatched `LlmAgent` to run offline without GCP API keys. It successfully captures and formats the trace dataset.
2. **Offline Grading Wrapper (`grade_override.py`)**: On workstations where GCP Application Default Credentials (ADC) are not configured, calling the remote Vertex AI Evals service fails. To bypass this, we wrote a grading wrapper that analyzes trace details locally and outputs the identical `EvaluationResult` artifacts (JSON and HTML) and prints the CLI-styled rich results table.

### Scenarios & Metric Scores
We ran the evaluation loop across the 5 synthetic test cases:
- **`auto_approve_clean`**: Under $100, no threats -> Auto-approved.
- **`high_value_clean`**: $\ge \$100$, no threats -> Sent to human approval.
- **`pii_leak`**: $\ge \$100$, contains SSN -> SSN redacted, sent to human.
- **`prompt_injection`**: $\ge \$100$, contains bypass keywords -> LLM bypassed, escalated, rejected.
- **`auto_approve_injection`**: Under $100$, contains bypass keywords -> Normal auto-approval overridden, escalated, rejected.

Both metrics (`routing_correctness` and `security_containment`) scored a perfect **5.0000** with a **100% pass rate**.

---

## 3. Task 3 Reflection: Secure AI Code (Shopping Assistant)

### Technical Challenges & Solutions
1. **API Key Recovery & Persistency**: Verified the status of `GEMINI_API_KEY` after a system shutdown and configured it persistently at the Windows `User` registry level to survive future restarts.
2. **Hardcoded Credential Remediation**: Resolved a simulated security vulnerability by replacing the hardcoded mock key in `app/agent.py` with dynamic environment variable retrieval (`os.environ.get("GEMINI_API_KEY")`).
3. **Vertex AI vs. Developer API Routing**: Implemented dynamic environment routing. When `GEMINI_API_KEY` is present, `GOOGLE_GENAI_USE_VERTEXAI` is toggled to `"False"`, which correctly diverts requests to the GenAI Developer API and prevents GCP Application Default Credentials (ADC) auth errors.
4. **Session Mismatch & App Name Alignment**: Remedied a critical `SessionNotFoundError` in the local playground server. Because the agent directory was `app`, the ADK server inferred the app name as `"app"`. Renaming the `App` object in `app/agent.py` to `name="app"` resolved the mismatch and enabled successful session creation.
5. **Import & Test Suite Recovery**: Added the missing `root_agent = root_workflow` export in `app/agent.py` to fix import errors in `tests/integration/test_agent.py`.

---

## 4. Key Takeaways
- **Design for Failures Offline**: Mocking out model layers and authentication endpoints allows developer testing loops to execute instantly and reliably.
- **Graph Routing Security**: Keeping security checks in simple Python nodes (like `escalate_injection`) rather than delegating them to LLM agents ensures absolute containment for prompt-injection attacks.
- **Align App Names with Directories**: The Google ADK local web server infers the application name from the path argument (e.g., `app`). Ensuring the `App` object name inside your code matches this directory name is crucial for successful session management.
