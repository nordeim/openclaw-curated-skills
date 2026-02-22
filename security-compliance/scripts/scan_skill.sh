#!/bin/bash
# Orange TrustSkill v2.0 - Backward Compatibility Entry Script
# This script maintains compatibility with v1.x invocation methods.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/../src/cli.py" "$@"
