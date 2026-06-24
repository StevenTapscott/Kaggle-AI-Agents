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

from __future__ import annotations
from typing import Any, Dict
import os
import google.auth
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.workflow import Workflow
from google.adk.models import Gemini
from pydantic import BaseModel, Field

# Ensure project_id is fetched
try:
    _, project_id = google.auth.default()
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
except Exception:
    pass

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
if os.environ.get("GEMINI_API_KEY"):
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
else:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Fixed vulnerability: Read API key from environment variable
api_key = os.environ.get("GEMINI_API_KEY")
model = Gemini(model="gemini-3.1-flash-lite", api_key=api_key)

# In-memory discount redemption store (simulating database state)
DISCOUNT_STORE: Dict[str, bool] = {"WELCOME50": False, "SUMMER20": False}

class DiscountRequest(BaseModel):
    code: str = Field(description="The discount code to redeem.")
    user_id: str = Field(description="The ID of the user requesting redemption.")

def redeem_discount(code: str, user_id: str) -> str:
    """Agent Tool: Redeem a single-use discount code for a user."""
    if code not in DISCOUNT_STORE:
        return "Error: Invalid discount code."
    if DISCOUNT_STORE[code]:
        return "Error: Discount code has already been redeemed."
    if not user_id or user_id.startswith("guest_"):
        return "Error: Registered user account required to redeem discounts."
        
    DISCOUNT_STORE[code] = True
    return f"Success: Discount code {code} redeemed successfully for user {user_id}."

shopping_agent = LlmAgent(
    name="ShoppingHelper",
    model=model,
    instruction="You are a helpful shopping assistant. Use your tools to redeem discount codes for users.",
    tools=[redeem_discount]
)

root_workflow = Workflow(
    name="shopping_assistant_workflow",
    edges=[('START', shopping_agent)]
)

root_agent = root_workflow

app = App(
    name="app",
    root_agent=root_workflow
)
