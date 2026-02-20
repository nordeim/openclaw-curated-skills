#!/usr/bin/env bash
# wreckit-ralph — automated mutation testing
# Usage: ./mutation-test.sh [project-path] [test-command]
# Generates mutations, runs tests, reports kill rate
# Exit 0 = results produced, check JSON for pass/fail

set -euo pipefail
PROJECT="${1:-.}"
TEST_CMD="${2:-}"
cd "$PROJECT"

# Auto-detect test command
if [ -z "$TEST_CMD" ]; then
  if [ -f "package.json" ]; then
    if grep -q '"vitest"' package.json 2>/dev/null; then TEST_CMD="npx vitest run"
    elif grep -q '"jest"' package.json 2>/dev/null; then TEST_CMD="npx jest"
    elif grep -q 'node --test' package.json 2>/dev/null; then TEST_CMD="npm test"
    fi
  elif [ -f "Cargo.toml" ]; then TEST_CMD="cargo test"
  elif [ -f "go.mod" ]; then TEST_CMD="go test ./..."
  elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then TEST_CMD="pytest"
  fi
fi

if [ -z "$TEST_CMD" ]; then
  echo '{"error":"Could not detect test command. Pass as second argument."}'
  exit 1
fi

echo "Test command: $TEST_CMD" >&2
echo "Verifying baseline tests pass..." >&2
if ! eval "$TEST_CMD" >/dev/null 2>&1; then
  echo '{"error":"Baseline tests fail. Fix tests before mutation testing."}'
  exit 1
fi
echo "Baseline OK" >&2

# Find source files
if [ -f "tsconfig.json" ] || ([ -f "package.json" ] && ! [ -f "Cargo.toml" ]); then
  LANG="ts"
  SRC_FILES=$(find . -name '*.ts' -not -name '*.test.*' -not -name '*.spec.*' \
    -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' \
    -not -name '*.d.ts' -not -path '*/tests/*' -not -path '*/__tests__/*' 2>/dev/null || true)
elif [ -f "Cargo.toml" ]; then
  LANG="rs"; SRC_FILES=$(find . -name '*.rs' -not -path '*/target/*' -not -path '*/.git/*' 2>/dev/null || true)
elif [ -f "go.mod" ]; then
  LANG="go"; SRC_FILES=$(find . -name '*.go' -not -name '*_test.go' -not -path '*/.git/*' 2>/dev/null || true)
elif [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  LANG="py"; SRC_FILES=$(find . -name '*.py' -not -name 'test_*' -not -name '*_test.py' -not -path '*/.git/*' -not -path '*/venv/*' 2>/dev/null || true)
else
  LANG="sh"; SRC_FILES=$(find . -name '*.sh' -not -path '*/.git/*' 2>/dev/null || true)
fi

FILE_COUNT=$(echo "$SRC_FILES" | grep -c '.' 2>/dev/null || echo 0)
echo "Found $FILE_COUNT source files ($LANG)" >&2

# Use temp files for counters (avoids subshell issues)
RESULTS_FILE=$(mktemp)
KILLED=0
SURVIVED=0
TOTAL=0
MAX_MUTATIONS=20

mutate_line() {
  local line="$1"
  if echo "$line" | grep -q '==='; then echo "$line" | sed 's/===/!==/'
  elif echo "$line" | grep -q '!=='; then echo "$line" | sed 's/!==/===/'
  elif echo "$line" | grep -q '>='; then echo "$line" | sed 's/>=/</'
  elif echo "$line" | grep -q '<='; then echo "$line" | sed 's/<=/>/g'
  elif echo "$line" | grep -q '&&'; then echo "$line" | sed 's/&&/||/'
  elif echo "$line" | grep -qF '||'; then echo "$line" | sed 's/||/\&\&/'
  elif echo "$line" | grep -q ' true'; then echo "$line" | sed 's/ true/ false/'
  elif echo "$line" | grep -q ' false'; then echo "$line" | sed 's/ false/ true/'
  elif echo "$line" | grep -q 'return '; then echo "$line" | sed 's/return /return undefined; \/\/ /'
  else echo "$line"
  fi
}

for file in $SRC_FILES; do
  [ "$TOTAL" -ge "$MAX_MUTATIONS" ] && break
  LINE_COUNT=$(wc -l < "$file" | tr -d ' ')
  [ "$LINE_COUNT" -lt 5 ] && continue

  CANDIDATES=$(grep -nE '(===|!==|>=|<=|&&|\|\|| true| false|return )' "$file" 2>/dev/null | head -5 || true)
  [ -z "$CANDIDATES" ] && continue

  cp "$file" "/tmp/wreckit-backup-$$"

  while IFS= read -r candidate; do
    [ "$TOTAL" -ge "$MAX_MUTATIONS" ] && break
    LINENUM=$(echo "$candidate" | cut -d: -f1)
    ORIGINAL=$(sed -n "${LINENUM}p" "$file")
    MUTATED=$(mutate_line "$ORIGINAL")
    [ "$ORIGINAL" = "$MUTATED" ] && continue

    # Apply mutation via awk
    awk -v ln="$LINENUM" -v rep="$MUTATED" 'NR==ln{print rep;next}{print}' "$file" > "/tmp/wreckit-mutated-$$"
    cp "/tmp/wreckit-mutated-$$" "$file"
    TOTAL=$((TOTAL + 1))

    if eval "$TEST_CMD" >/dev/null 2>&1; then
      SURVIVED=$((SURVIVED + 1))
      echo "  SURVIVED: ${file}:${LINENUM}" >> "$RESULTS_FILE"
    else
      KILLED=$((KILLED + 1))
      echo "  KILLED:   ${file}:${LINENUM}" >> "$RESULTS_FILE"
    fi

    cp "/tmp/wreckit-backup-$$" "$file"
  done <<< "$CANDIDATES"

  cp "/tmp/wreckit-backup-$$" "$file"
  rm -f "/tmp/wreckit-backup-$$" "/tmp/wreckit-mutated-$$"
done

if [ "$TOTAL" -eq 0 ]; then
  rm -f "$RESULTS_FILE"
  echo '{"error":"No mutatable lines found in source files."}'
  exit 1
fi

KILL_RATE=$(echo "scale=1; $KILLED * 100 / $TOTAL" | bc 2>/dev/null || echo "0")

echo ""
echo "=== MUTATION TEST RESULTS ==="
cat "$RESULTS_FILE"
echo ""
echo "Total: $TOTAL | Killed: $KILLED | Survived: $SURVIVED"
echo "Kill rate: ${KILL_RATE}%"

cat <<EOF

{"total":$TOTAL,"killed":$KILLED,"survived":$SURVIVED,"killRate":$KILL_RATE,"language":"$LANG"}
EOF

rm -f "$RESULTS_FILE"
