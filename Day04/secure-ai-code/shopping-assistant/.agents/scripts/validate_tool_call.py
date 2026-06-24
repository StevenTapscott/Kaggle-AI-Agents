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

import sys
import json

def main():
    try:
        context = json.load(sys.stdin)
        command = context.get("tool_args", {}).get("CommandLine", "")
        
        if "rm -rf /" in command or "mkfs" in command:
            print("BLOCKED: Destructive command detected.", file=sys.stderr)
            sys.exit(1)
            
        print("APPROVED: Command validation passed.")
        sys.exit(0)
    except Exception as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
