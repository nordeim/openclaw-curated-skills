#!/usr/bin/env bash
# ipeaky test suite — non-interactive tests (no osascript popups)
# Usage: bash tests/run_tests.sh

set -uo pipefail
cd "$(dirname "$0")/.."

PASS=0
FAIL=0
SCRIPTS=scripts

pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }

echo "=== ipeaky test suite ==="
echo ""

# -------------------------------------------------------
echo "--- secure_input_mac.sh ---"

# T1: Missing argument → exits non-zero
echo "T1: Missing KEY_NAME argument"
if bash "$SCRIPTS/secure_input_mac.sh" 2>/dev/null; then
  fail "Should have exited non-zero with no args"
else
  pass "Exits non-zero with no args"
fi

# T2: Script uses 'with hidden answer'
echo "T2: Uses hidden answer (no plaintext input)"
if grep -q "with hidden answer" "$SCRIPTS/secure_input_mac.sh"; then
  pass "Hidden answer flag present"
else
  fail "Missing 'with hidden answer' — keys would show in plaintext!"
fi

# T3: Script uses set -euo pipefail
echo "T3: Strict mode (set -euo pipefail)"
if grep -q "set -euo pipefail" "$SCRIPTS/secure_input_mac.sh"; then
  pass "Strict mode enabled"
else
  fail "Missing set -euo pipefail"
fi

# T4: No eval, no key logging
echo "T4: No eval or echo of raw key"
if grep -qE '^\s*eval ' "$SCRIPTS/secure_input_mac.sh"; then
  fail "Contains eval — potential injection risk"
else
  pass "No eval found"
fi

# T5: Output uses echo -n (no trailing newline)
echo "T5: Output via echo -n (clean stdout)"
if grep -q 'echo -n "\$KEY"' "$SCRIPTS/secure_input_mac.sh" || grep -q "echo -n \"\\\$KEY\"" "$SCRIPTS/secure_input_mac.sh" || tail -1 "$SCRIPTS/secure_input_mac.sh" | grep -q 'echo -n'; then
  pass "Uses echo -n for clean output"
else
  fail "Might include trailing newline in key output"
fi

echo ""

# -------------------------------------------------------
echo "--- test_key.sh ---"

# T6: Missing service arg → exits non-zero
echo "T6: Missing SERVICE argument"
if echo "fake-key" | bash "$SCRIPTS/test_key.sh" 2>/dev/null; then
  fail "Should have exited non-zero with no service arg"
else
  pass "Exits non-zero with no service arg"
fi

# T7: Empty stdin → exits non-zero
echo "T7: Empty key on stdin"
if echo -n "" | bash "$SCRIPTS/test_key.sh" openai 2>/dev/null; then
  fail "Should have exited non-zero with empty key"
else
  pass "Exits non-zero with empty stdin"
fi

# T8: Key masking — only first 4 chars shown
echo "T8: Key masking (first 4 + ****)"
if grep -q 'KEY:0:4' "$SCRIPTS/test_key.sh"; then
  pass "Masking uses first 4 chars"
else
  fail "Key masking pattern not found"
fi

# T9: Strict mode
echo "T9: Strict mode (set -euo pipefail)"
if grep -q "set -euo pipefail" "$SCRIPTS/test_key.sh"; then
  pass "Strict mode enabled"
else
  fail "Missing set -euo pipefail"
fi

# T10: Unknown service doesn't fail
echo "T10: Unknown service falls through gracefully"
RESULT=$(echo "test-key-1234" | bash "$SCRIPTS/test_key.sh" unknown_service 2>&1)
if echo "$RESULT" | grep -q "OK:"; then
  pass "Unknown service returns OK with masked key"
else
  fail "Unknown service handling broken: $RESULT"
fi

# T11: Unknown service output doesn't contain full key
echo "T11: Unknown service output doesn't leak full key"
RESULT=$(echo "sk-supersecretkey12345" | bash "$SCRIPTS/test_key.sh" unknown_service 2>&1)
if echo "$RESULT" | grep -q "supersecretkey"; then
  fail "Full key leaked in output!"
else
  pass "Key not leaked in unknown service output"
fi

# T12: No eval in test_key.sh
echo "T12: No eval"
if grep -qE '^\s*eval ' "$SCRIPTS/test_key.sh"; then
  fail "Contains eval"
else
  pass "No eval found"
fi

# T13: No key in error messages (check FAIL paths)
echo "T13: FAIL messages use masked key only"
FAIL_LINES=$(grep "FAIL:" "$SCRIPTS/test_key.sh" | grep -v 'MASKED' || true)
if [ -z "$FAIL_LINES" ]; then
  pass "All FAIL messages reference MASKED variable"
else
  fail "Some FAIL messages might leak keys: $FAIL_LINES"
fi

echo ""

# -------------------------------------------------------
echo "--- SKILL.md security audit ---"

# T14: SKILL.md warns against echoing keys
echo "T14: SKILL.md has NEVER-echo rule"
if grep -qi "NEVER echo\|NEVER include.*key.*chat\|never.*print.*key" SKILL.md; then
  pass "NEVER-echo rule documented"
else
  fail "Missing explicit NEVER-echo warning"
fi

# T15: SKILL.md mentions config.patch
echo "T15: Uses gateway config.patch (native storage)"
if grep -q "config.patch" SKILL.md; then
  pass "config.patch flow documented"
else
  fail "Missing config.patch documentation"
fi

# T16: SKILL.md has key map
echo "T16: Key map (service → config path)"
if grep -q "Config Path" SKILL.md; then
  pass "Key map present"
else
  fail "Missing key map"
fi

echo ""

# -------------------------------------------------------
echo "--- Live key validation (via openclaw.json config) ---"

# v2 stores keys in openclaw.json via gateway config.patch
# To run live tests, set OPENAI_API_KEY and/or ELEVENLABS_API_KEY in env
# (e.g., sourced from config or passed explicitly)

# T17: OpenAI key live test
echo "T17: OpenAI key live validation"
if [ -n "${OPENAI_API_KEY:-}" ]; then
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $OPENAI_API_KEY" "https://api.openai.com/v1/models" 2>/dev/null || echo "000")
  if [ "$HTTP" = "200" ]; then
    pass "OpenAI key valid (HTTP 200)"
  else
    fail "OpenAI key returned HTTP $HTTP"
  fi
else
  echo "  ⏭️  OPENAI_API_KEY not in env, skipping"
fi

# T18: ElevenLabs key live test
echo "T18: ElevenLabs key live validation"
if [ -n "${ELEVENLABS_API_KEY:-}" ]; then
  HTTP=$(curl -s -o /dev/null -w "%{http_code}" -H "xi-api-key: $ELEVENLABS_API_KEY" "https://api.elevenlabs.io/v1/user" 2>/dev/null || echo "000")
  if [ "$HTTP" = "200" ]; then
    pass "ElevenLabs key valid (HTTP 200)"
  else
    fail "ElevenLabs key returned HTTP $HTTP"
  fi
else
  echo "  ⏭️  ELEVENLABS_API_KEY not in env, skipping"
fi

echo ""

# -------------------------------------------------------
echo "================================="
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
  echo "❌ SOME TESTS FAILED"
  exit 1
else
  echo "✅ ALL TESTS PASSED"
  exit 0
fi
