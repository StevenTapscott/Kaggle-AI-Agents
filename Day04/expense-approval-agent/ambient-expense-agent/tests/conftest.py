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

import os
from unittest.mock import MagicMock
import google.auth
from google.cloud.aiplatform.utils import resource_manager_utils
import google.cloud.logging

# Mock google.auth.default to return a dummy credential and project
google.auth.default = MagicMock(return_value=(MagicMock(), "dummy-project-id"))

# Mock resource_manager_utils.get_project_id to prevent outbound network calls during tests
resource_manager_utils.get_project_id = MagicMock(side_effect=lambda project: project)

# Mock google.cloud.logging.Client to prevent outbound logging calls
mock_client = MagicMock()
google.cloud.logging.Client = MagicMock(return_value=mock_client)

# Set dummy Google Cloud project environment variables for tests
os.environ["GOOGLE_CLOUD_PROJECT"] = "dummy-project-id"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
