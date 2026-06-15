#!/bin/bash
# Wrap deployment script with local mock binaries path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$SCRIPT_DIR/mock_bin:$PATH"
./deploy.sh
