#!/usr/bin/env bash
# ipeaky - Native macOS secure key input
# Usage: ./secure_input_mac.sh <KEY_NAME>
# Pops a native macOS dialog with hidden input, outputs the key to stdout.
# The caller (agent) captures stdout and stores via gateway config.patch.

set -euo pipefail

KEY_NAME="${1:?Usage: secure_input_mac.sh <KEY_NAME>}"

# Native macOS hidden-input dialog → outputs key to stdout
KEY=$(osascript -e "set theKey to text returned of (display dialog \"Paste your ${KEY_NAME}:\" default answer \"\" with hidden answer with title \"ipeaky\" with icon caution)" -e "return theKey" 2>/dev/null)

if [ -z "$KEY" ]; then
  echo "ERROR: No key provided" >&2
  exit 1
fi

echo -n "$KEY"
