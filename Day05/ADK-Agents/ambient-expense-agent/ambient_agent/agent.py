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

import json
import re
import os
from pydantic import BaseModel, Field

from google.adk.agents.context import Context
from google.adk.apps import App
from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.events.request_input import RequestInput
from google.adk.models import Gemini
from google.adk.workflow import Workflow, node
from google.genai import types

import google.auth

# Default configuration for GCP/Vertex AI
try:
    _, project_id = google.auth.default()
    if not os.environ.get("GOOGLE_CLOUD_PROJECT") and project_id:
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
except Exception:
    pass

if not os.environ.get("GOOGLE_CLOUD_LOCATION"):
    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


# --- Schemas ---


class ExpenseReport(BaseModel):
    amount: float = Field(
        default=0.0, description="The amount of the expense in dollars."
    )
    submitter: str = Field(
        default="Unknown", description="The person who submitted the expense."
    )
    description: str = Field(
        default="No description", description="Description of the expense."
    )


class ApprovalResult(BaseModel):
    approved: bool = Field(description="Whether the expense was approved.")
    reason: str = Field(description="Reason for approval or rejection.")
    amount: float = Field(description="The finalized expense amount.")
    submitter: str = Field(description="The submitter of the expense.")


# --- Nodes ---


def parse_expense_report(node_input: types.Content | str | dict) -> ExpenseReport:
    """Extracts and parses expense report details from a potentially encoded input."""
    raw_dict = {}

    if isinstance(node_input, dict):
        raw_dict = node_input
    elif isinstance(node_input, str):
        try:
            raw_dict = json.loads(node_input)
        except Exception:
            # Fallback to simple regex matching for raw text
            amount_match = re.search(
                r"(?:amount|price|cost|total)\D*(\d+(?:\.\d+)?)",
                node_input,
                re.IGNORECASE,
            )
            amount = float(amount_match.group(1)) if amount_match else 0.0

            submitter_match = re.search(
                r"(?:submitter|user|name|employee)\D*([a-zA-Z\s]+)",
                node_input,
                re.IGNORECASE,
            )
            submitter = (
                submitter_match.group(1).strip() if submitter_match else "Unknown"
            )

            desc_match = re.search(
                r"(?:description|for|desc)\D*([a-zA-Z0-9\s]+)",
                node_input,
                re.IGNORECASE,
            )
            description = desc_match.group(1).strip() if desc_match else node_input

            return ExpenseReport(
                amount=amount, submitter=submitter, description=description
            )
    elif hasattr(node_input, "parts") and node_input.parts:
        text_parts = [p.text for p in node_input.parts if p.text]
        raw_str = "".join(text_parts)
        try:
            raw_dict = json.loads(raw_str)
        except Exception:
            # Fallback to regex matching on part text
            amount_match = re.search(
                r"(?:amount|price|cost|total)\D*(\d+(?:\.\d+)?)", raw_str, re.IGNORECASE
            )
            amount = float(amount_match.group(1)) if amount_match else 0.0

            submitter_match = re.search(
                r"(?:submitter|user|name|employee)\D*([a-zA-Z\s]+)",
                raw_str,
                re.IGNORECASE,
            )
            submitter = (
                submitter_match.group(1).strip() if submitter_match else "Unknown"
            )

            desc_match = re.search(
                r"(?:description|for|desc)\D*([a-zA-Z0-9\s]+)", raw_str, re.IGNORECASE
            )
            description = desc_match.group(1).strip() if desc_match else raw_str

            return ExpenseReport(
                amount=amount, submitter=submitter, description=description
            )

    amount = raw_dict.get("amount")
    try:
        amount = float(amount) if amount is not None else 0.0
    except (ValueError, TypeError):
        amount = 0.0

    return ExpenseReport(
        amount=amount,
        submitter=raw_dict.get("submitter", "Unknown"),
        description=raw_dict.get("description", "No description"),
    )


def evaluate_rules(node_input: ExpenseReport) -> Event:
    """Branches the workflow routing based on the expense amount."""
    state_delta = {"expense": node_input.model_dump()}

    if node_input.amount < 100.0:
        return Event(
            output=node_input,
            actions=EventActions(route="auto_approve", state_delta=state_delta),
        )
    else:
        return Event(
            output=node_input,
            actions=EventActions(route="review_agent", state_delta=state_delta),
        )


def auto_approve(node_input: ExpenseReport) -> Event:
    """Node that automatically approves expenses under $100."""
    result = ApprovalResult(
        approved=True,
        reason=f"Auto-approved: Amount ${node_input.amount:.2f} is under the $100.00 threshold.",
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


@node(rerun_on_resume=True)
async def review_agent(ctx: Context, node_input: ExpenseReport):
    """Node that triggers a human-in-the-loop pause for expenses of $100 or more."""
    if not ctx.resume_inputs or "approve_decision" not in ctx.resume_inputs:
        msg = (
            f"=== EXPENSE REVIEW REQUIRED ===\n"
            f"Submitter: {node_input.submitter}\n"
            f"Amount: ${node_input.amount:.2f}\n"
            f"Description: {node_input.description}\n\n"
            f"Please approve or reject this expense report (enter 'approve' or 'reject'):"
        )
        yield RequestInput(
            interrupt_id="approve_decision",
            message=msg,
        )
        return

    # Process the decision after resume (handling dict or string inputs)
    decision_val = ctx.resume_inputs["approve_decision"]
    if isinstance(decision_val, dict):
        decision = (
            (decision_val.get("response") or decision_val.get("approve_decision") or "")
            .strip()
            .lower()
        )
    else:
        decision = str(decision_val).strip().lower()

    approved = decision in ["approve", "yes", "y", "ok"]

    result = ApprovalResult(
        approved=approved,
        reason=f"Reviewed by human. Decision: {'APPROVED' if approved else 'REJECTED'}.",
        amount=node_input.amount,
        submitter=node_input.submitter,
    )

    content_text = f"Expense of ${result.amount:.2f} by {result.submitter} has been {'APPROVED' if approved else 'REJECTED'} by human review. Reason: {result.reason}"

    yield Event(
        output=result,
        content=types.Content(
            role="model", parts=[types.Part.from_text(text=content_text)]
        ),
        actions=EventActions(state_delta={"approval_result": result.model_dump()}),
    )


# --- Workflow Definition ---

root_agent = Workflow(
    name="expense_approval_workflow",
    edges=[
        ("START", parse_expense_report),
        (parse_expense_report, evaluate_rules),
        (
            evaluate_rules,
            {
                "auto_approve": auto_approve,
                "review_agent": review_agent,
            },
        ),
    ],
)

# Export for test suite and playground
root_workflow = root_agent

app = App(
    root_agent=root_agent,
    name="app",
)
