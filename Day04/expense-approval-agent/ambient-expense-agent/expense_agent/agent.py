# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json
import os
import re
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.agents.context import Context
from google.adk.apps import App
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.events.request_input import RequestInput
from google.adk.models import Gemini
from google.adk.workflow import Workflow
from google.genai import types

from expense_agent.config import MODEL_NAME, THRESHOLD

# Default to Vertex AI unless explicitly configured otherwise via environment
if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true":
    import google.auth

    try:
        _, project_id = google.auth.default()
        if not os.environ.get("GOOGLE_CLOUD_PROJECT") and project_id:
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    except Exception:
        pass

    if not os.environ.get("GOOGLE_CLOUD_LOCATION"):
        os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
else:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


# --- Schemas & Models ---


class ExpenseReport(BaseModel):
    amount: float = Field(
        default=0.0, description="The amount of the expense in dollars."
    )
    submitter: str = Field(
        default="Unknown", description="The person who submitted the expense."
    )
    category: str = Field(default="General", description="The category of the expense.")
    description: str = Field(
        default="No description", description="Description of the expense."
    )
    date: str = Field(default="", description="The date of the expense.")


class RiskReview(BaseModel):
    risk_score: int = Field(description="Risk score from 1 (low) to 10 (high).")
    risk_factors: list[str] = Field(
        description="List of identified risk factors or anomalies."
    )
    alert_triggered: bool = Field(
        description="True if risk score is high (>= 7) or specific anomalies are found."
    )
    explanation: str = Field(description="Detailed explanation of the risk review.")


class ApprovalResult(BaseModel):
    approved: bool = Field(description="Whether the expense was approved.")
    reason: str = Field(description="Reason for approval or rejection.")
    amount: float = Field(description="The finalized expense amount.")
    submitter: str = Field(description="The submitter of the expense.")


# --- Node Implementations ---


def redact_ssn(text: str) -> str:
    """Redacts SSN format (xxx-xx-xxxx or 9 digits) from a text."""
    if not isinstance(text, str):
        return text
    # Match standard SSN with dashes, or 9 consecutive digits
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED SSN]', text)
    text = re.sub(r'\b\d{9}\b', '[REDACTED SSN]', text)
    return text


def parse_expense_report(node_input: types.Content | str | dict) -> ExpenseReport:
    """Extracts and parses expense report details from a potentially encoded input.

    Supports base64-encoded strings (as in real Pub/Sub messages), raw JSON strings,
    and dictionary inputs.
    """
    raw_dict = {}

    if isinstance(node_input, dict):
        raw_dict = node_input
    elif isinstance(node_input, str):
        try:
            raw_dict = json.loads(node_input)
        except Exception:
            pass
    elif hasattr(node_input, "parts") and node_input.parts:
        text_parts = [p.text for p in node_input.parts if p.text]
        raw_str = "".join(text_parts)
        try:
            raw_dict = json.loads(raw_str)
        except Exception:
            pass

    # Pub/Sub payload check: the details may sit under a "data" key
    data_content = raw_dict.get("data")
    expense_data = {}

    if data_content is not None:
        if isinstance(data_content, str):
            # Try base64 decoding first
            try:
                decoded = base64.b64decode(data_content).decode("utf-8")
                expense_data = json.loads(decoded)
            except Exception:
                # Fallback to parsing raw string as JSON
                try:
                    expense_data = json.loads(data_content)
                except Exception:
                    pass
        elif isinstance(data_content, dict):
            expense_data = data_content
    else:
        # If no "data" wrapper key, treat the raw input dict as the expense details
        expense_data = raw_dict

    # Extract fields with fallback values
    amount = expense_data.get("amount")
    try:
        amount = float(amount) if amount is not None else 0.0
    except (ValueError, TypeError):
        amount = 0.0

    raw_description = expense_data.get("description", "No description")
    redacted_description = redact_ssn(raw_description)

    return ExpenseReport(
        amount=amount,
        submitter=expense_data.get("submitter", "Unknown"),
        category=expense_data.get("category", "General"),
        description=redacted_description,
        date=expense_data.get("date", ""),
    )


def evaluate_rules(node_input: ExpenseReport) -> Event:
    """Applies routing rules based on the expense amount and security checks."""
    # Store the parsed expense in the session state for downstream nodes
    state_delta = {"expense": node_input.model_dump()}

    # Check for prompt injection keywords
    injection_keywords = ["bypass", "ignore", "override", "instruction", "system prompt", "auto-approve"]
    desc_lower = (node_input.description or "").lower()
    has_injection = any(kw in desc_lower for kw in injection_keywords)

    if has_injection:
        return Event(
            output=node_input,
            actions=EventActions(route="escalate", state_delta=state_delta),
        )

    if node_input.amount < THRESHOLD:
        return Event(
            output=node_input,
            actions=EventActions(route="auto_approve", state_delta=state_delta),
        )
    else:
        return Event(
            output=node_input,
            actions=EventActions(route="manual_review", state_delta=state_delta),
        )


def auto_approve(node_input: ExpenseReport) -> Event:
    """Auto-approves expenses that are below the dollar threshold."""
    result = ApprovalResult(
        approved=True,
        reason=f"Auto-approved: Amount ${node_input.amount:.2f} is under the threshold of ${THRESHOLD:.2f}.",
        amount=node_input.amount,
        submitter=node_input.submitter,
    )

    content_text = f"Expense of ${result.amount:.2f} by {result.submitter} has been AUTO-APPROVED. Reason: {result.reason}"

    return Event(
        output=result,
        content=types.Content(
            role="model", parts=[types.Part.from_text(text=content_text)]
        ),
        actions=EventActions(state_delta={"approval_result": result.model_dump()}),
    )


# --- LLM Risk Analysis Agent Node ---

risk_reviewer = LlmAgent(
    name="risk_reviewer",
    model=Gemini(
        model=MODEL_NAME,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are a risk analysis agent. Review the provided expense report for risk factors, policy violations, or suspicious activity.
Identify specific risk factors, assign a risk score between 1 and 10, and indicate if an alert should be triggered.

Expense Details:
Submitter: {expense[submitter]}
Amount: ${expense[amount]}
Category: {expense[category]}
Description: {expense[description]}
Date: {expense[date]}
""",
    output_schema=RiskReview,
    output_key="risk_review",
)


# --- Human-in-the-Loop Node ---


async def human_approval(ctx: Context, node_input: RiskReview):
    """Pauses the workflow for human approval and records the decision."""
    expense_dict = ctx.state.get("expense", {})
    amount = expense_dict.get("amount", 0.0)
    submitter = expense_dict.get("submitter", "Unknown")

    if not ctx.resume_inputs or "approve_decision" not in ctx.resume_inputs:
        msg = (
            f"=== EXPENSE APPROVAL REQUESTED ===\n"
            f"Submitter: {submitter}\n"
            f"Amount: ${amount:.2f}\n"
            f"Category: {expense_dict.get('category')}\n"
            f"Description: {expense_dict.get('description')}\n"
            f"Date: {expense_dict.get('date')}\n\n"
            f"--- LLM Risk Review ---\n"
            f"Risk Score: {node_input.risk_score}/10\n"
            f"Alert Triggered: {node_input.alert_triggered}\n"
            f"Risk Factors: {', '.join(node_input.risk_factors)}\n"
            f"Explanation: {node_input.explanation}\n\n"
            f"Please approve or reject this expense report (enter 'approve' or 'reject'):"
        )
        yield RequestInput(
            interrupt_id="approve_decision",
            message=msg,
        )
        return

    # User resumed and provided a choice
    decision = ctx.resume_inputs["approve_decision"].strip().lower()
    approved = decision in ["approve", "yes", "y", "ok"]

    result = ApprovalResult(
        approved=approved,
        reason=f"Reviewed by human. Decision: {'APPROVED' if approved else 'REJECTED'}. Risk Score: {node_input.risk_score}/10.",
        amount=amount,
        submitter=submitter,
    )

    content_text = f"Expense of ${result.amount:.2f} by {result.submitter} has been {'APPROVED' if approved else 'REJECTED'} by human review. Reason: {result.reason}"

    yield Event(
        output=result,
        content=types.Content(
            role="model", parts=[types.Part.from_text(text=content_text)]
        ),
        actions=EventActions(state_delta={"approval_result": result.model_dump()}),
    )


def escalate_injection(node_input: ExpenseReport) -> RiskReview:
    """Bypasses model for prompt injection, directly escalating to human review."""
    return RiskReview(
        risk_score=10,
        risk_factors=["Prompt Injection Attempt"],
        alert_triggered=True,
        explanation="Escalated: Suspected prompt injection attempt detected."
    )


# --- Workflow Graph Definition ---

root_agent = Workflow(
    name="expense_approval_workflow",
    edges=[
        ("START", parse_expense_report),
        (parse_expense_report, evaluate_rules),
        # Conditional paths using a RoutingMap (dict)
        (
            evaluate_rules,
            {
                "auto_approve": auto_approve,
                "manual_review": risk_reviewer,
                "escalate": escalate_injection,
            },
        ),
        (escalate_injection, human_approval),
        (risk_reviewer, human_approval),
    ],
)


# --- App Container ---

app = App(
    root_agent=root_agent,
    name="expense_agent",
)
