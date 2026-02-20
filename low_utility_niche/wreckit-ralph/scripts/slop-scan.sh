#!/usr/bin/env bash
# wreckit-ralph — scan for AI slop (placeholders, phantoms, template artifacts)
# Usage: ./slop-scan.sh [project-path]
# Exit 0 = clean, Exit 1 = slop found

set -euo pipefail
PROJECT="${1:-.}"
cd "$PROJECT"
FINDINGS=0

echo "=== AI Slop Scan ==="

# Placeholders
echo ""
echo "--- Placeholders ---"
PLACEHOLDERS=$(grep -rn "TODO\|FIXME\|implement this\|HACK\|XXX" \
  --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' \
  --include='*.py' --include='*.rs' --include='*.go' --include='*.sh' \
  --include='*.swift' \
  . 2>/dev/null | grep -v node_modules | grep -v '.git/' | grep -v 'dist/' || true)

if [ -n "$PLACEHOLDERS" ]; then
  echo "$PLACEHOLDERS"
  COUNT=$(echo "$PLACEHOLDERS" | wc -l | tr -d ' ')
  echo "Found $COUNT placeholder(s)"
  FINDINGS=$((FINDINGS + COUNT))
else
  echo "None found"
fi

# Template artifacts
echo ""
echo "--- Template Artifacts ---"
TEMPLATES=$(grep -rn "example\.com\|YOUR_API_KEY\|lorem ipsum\|changeme\|placeholder\|sample_value" \
  --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' \
  --include='*.py' --include='*.rs' --include='*.go' --include='*.sh' \
  --include='*.swift' --include='*.json' \
  . 2>/dev/null | grep -v node_modules | grep -v '.git/' | grep -v 'dist/' | grep -v 'package-lock' || true)

if [ -n "$TEMPLATES" ]; then
  echo "$TEMPLATES"
  COUNT=$(echo "$TEMPLATES" | wc -l | tr -d ' ')
  echo "Found $COUNT template artifact(s)"
  FINDINGS=$((FINDINGS + COUNT))
else
  echo "None found"
fi

# Dead/empty functions
echo ""
echo "--- Empty Function Bodies ---"
EMPTY=$(grep -rn -A1 "function.*{" \
  --include='*.ts' --include='*.js' \
  . 2>/dev/null | grep -v node_modules | grep -v '.git/' | grep "^.*-.*}$" || true)

if [ -n "$EMPTY" ]; then
  echo "$EMPTY"
  COUNT=$(echo "$EMPTY" | wc -l | tr -d ' ')
  FINDINGS=$((FINDINGS + COUNT))
else
  echo "None found"
fi

echo ""
echo "=== Total slop findings: $FINDINGS ==="

if [ "$FINDINGS" -gt 0 ]; then
  exit 1
else
  exit 0
fi
