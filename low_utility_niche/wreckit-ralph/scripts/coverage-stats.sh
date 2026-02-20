#!/usr/bin/env bash
# wreckit — extract raw coverage stats from test runners
# Usage: ./coverage-stats.sh [project-path]
# Outputs JSON with coverage numbers

set -euo pipefail
PROJECT="${1:-.}"
cd "$PROJECT"

# Detect stack
STACK=$(bash "$(dirname "$0")/detect-stack.sh" "$PROJECT" 2>/dev/null)
LANG=$(echo "$STACK" | python3 -c "import sys,json; print(json.load(sys.stdin).get('language','unknown'))" 2>/dev/null || echo "unknown")
TEST_RUNNER=$(echo "$STACK" | python3 -c "import sys,json; print(json.load(sys.stdin).get('testRunner','none'))" 2>/dev/null || echo "none")

case "$TEST_RUNNER" in
  vitest)
    npx vitest run --coverage --reporter=json 2>/dev/null | tail -1 || echo '{"error":"vitest coverage failed"}'
    ;;
  jest)
    npx jest --coverage --coverageReporters=json-summary 2>/dev/null
    if [ -f "coverage/coverage-summary.json" ]; then
      cat coverage/coverage-summary.json
    else
      echo '{"error":"jest coverage file not found"}'
    fi
    ;;
  pytest)
    pytest --cov=. --cov-report=json 2>/dev/null
    if [ -f "coverage.json" ]; then
      cat coverage.json
    else
      echo '{"error":"pytest coverage file not found"}'
    fi
    ;;
  cargo)
    # cargo-tarpaulin for Rust coverage
    if command -v cargo-tarpaulin &>/dev/null; then
      cargo tarpaulin --out Json 2>/dev/null || echo '{"error":"tarpaulin failed"}'
    else
      echo '{"error":"cargo-tarpaulin not installed","hint":"cargo install cargo-tarpaulin"}'
    fi
    ;;
  go)
    go test -coverprofile=coverage.out ./... 2>/dev/null
    if [ -f "coverage.out" ]; then
      go tool cover -func=coverage.out | tail -1
      rm -f coverage.out
    else
      echo '{"error":"go coverage failed"}'
    fi
    ;;
  swift)
    swift test --enable-code-coverage 2>/dev/null || echo '{"error":"swift test coverage failed"}'
    ;;
  *)
    echo "{\"error\":\"unknown test runner: $TEST_RUNNER\",\"language\":\"$LANG\"}"
    ;;
esac
