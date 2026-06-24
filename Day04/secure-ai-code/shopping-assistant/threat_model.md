# STRIDE Threat Modeling Assessment: Shopping Assistant Agent

This document evaluates the security posture of the `shopping-assistant` agent using the STRIDE threat modeling framework.

---

## 1. System Boundaries & Entry Points

- **User Entry Point**: Chat interface where users submit arbitrary text prompts (potential prompt injection vector).
- **Agent Workflow**: `shopping_assistant_workflow` routes the input to the `ShoppingHelper` `LlmAgent` node.
- **Agent Tools**: `redeem_discount(code, user_id)` is exposed as a tool to the LLM agent.
- **State/Data Storage**: `DISCOUNT_STORE` is an in-memory dictionary mapping discount codes (`WELCOME50`, `SUMMER20`) to their redemption status (boolean).

---

## 2. STRIDE Evaluation

### Spoofing (Identity Spoofing)
- **Vulnerability**: The `redeem_discount` tool accepts `user_id` as a raw string parameter. There is no verification/authentication check to ensure the user executing the agent is actually the owner of the `user_id` being passed.
- **Mitigation**: Implement cryptographic session token verification or resolve the `user_id` directly from the authenticated context (rather than allowing the LLM agent or caller to pass it arbitrarily).

### Tampering (Data/State Manipulation)
- **Vulnerability**: The `DISCOUNT_STORE` state update is susceptible to race conditions. If two concurrent threads execute `redeem_discount` with the same code, both could pass the `DISCOUNT_STORE[code]` check before either sets it to `True`, leading to a double-redemption (TOCTOU race condition).
- **Mitigation**: Use a database with pessimistic locking (e.g. `SELECT FOR UPDATE`) or a thread-safe mutex lock for in-memory operations.

### Repudiation
- **Vulnerability**: Redemptions and validation failures are returned as strings to the console/chat but are not logged to a secure, write-only persistent audit trail. This makes it impossible to prove who redeemed which code or trace malicious activities.
- **Mitigation**: Integrate secure, structured logging (e.g. Cloud Logging or a secure audit database) to record all redemption attempts and results.

### Information Disclosure
- **Vulnerability**: Stack traces and internal validation error messages could be returned directly to the user if exceptions occur within the tool logic or ADK container.
- **Mitigation**: Handle exceptions gracefully inside tools and return user-friendly, generic error messages rather than raw stack traces.

### Denial of Service
- **Vulnerability**: There are no rate-limiting controls on the `redeem_discount` tool. A user could flood the agent with requests, exhausting the model quota or compute resources.
- **Mitigation**: Implement rate limiting at the application API layer.

### Elevation of Privilege
- **Vulnerability**: Any unauthenticated client can claim to be a registered user simply by providing a valid user ID (e.g., `user_123`), bypassing the guest account block (`guest_` check).
- **Mitigation**: Enforce that the user context is populated via an authenticated session token, and do not allow the LLM agent or client to supply the `user_id` parameter directly.
