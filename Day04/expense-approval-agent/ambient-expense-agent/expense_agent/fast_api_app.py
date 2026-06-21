# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FastAPI entry point for the ambient expense agent backend.

This file configures the ADK web server with Pub/Sub trigger endpoints
enabled, allowing the agent to process expense reports autonomously.
"""

import json
import logging
import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from starlette.requests import Request

# Configure standard Python logging for console logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# The ADK needs the project root as agents_dir so it discovers
# expense_agent/ as an agent package (contains agent.py + __init__.py).
AGENTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configure ADK web server with Pub/Sub trigger source and disable cloud telemetry
app = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    web=False,
    trigger_sources=["pubsub"],
    otel_to_cloud=False,
)


@app.middleware("http")
async def normalize_pubsub_subscription(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Normalize ``projects/.../subscriptions/NAME`` to just ``NAME``.

    Pub/Sub push deliveries include the fully-qualified subscription
    resource path. The ADK trigger handler uses this value as the
    session ``user_id``. Normalizing to the short name keeps session
    records clean and consistent with the subscription name.
    """
    if request.url.path.endswith("/trigger/pubsub") and request.method == "POST":
        body = await request.body()
        try:
            data = json.loads(body)
            sub = data.get("subscription", "")
            if "/" in sub:
                short_sub = sub.rsplit("/", 1)[-1]
                logger.info(f"Normalizing subscription from '{sub}' to '{short_sub}'")
                data["subscription"] = short_sub
                request._body = json.dumps(data).encode()
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error normalising subscription: {e}")
    return await call_next(request)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting ambient expense agent FastAPI app on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
    )
