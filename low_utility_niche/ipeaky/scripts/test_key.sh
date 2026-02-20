#!/usr/bin/env bash
# ipeaky - Test an API key by calling the provider's API
# Usage: echo "KEY_VALUE" | ./test_key.sh <SERVICE>
# Reads key from stdin. Never prints the full key.

set -euo pipefail

SERVICE="${1:?Usage: echo KEY | test_key.sh <SERVICE>}"
KEY=$(cat)

if [ -z "$KEY" ]; then
  echo "ERROR: No key provided on stdin"
  exit 1
fi

MASKED="${KEY:0:4}****"

case "$SERVICE" in
  OPENAI_API_KEY|openai)
    RESP=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $KEY" "https://api.openai.com/v1/models" 2>/dev/null)
    CODE=$(echo "$RESP" | tail -1)
    if [ "$CODE" = "200" ]; then
      echo "OK: OpenAI key ($MASKED) is valid."
    else
      echo "FAIL: OpenAI key ($MASKED) returned HTTP $CODE."
      exit 1
    fi
    ;;
  ELEVENLABS_API_KEY|elevenlabs)
    RESP=$(curl -s -w "\n%{http_code}" -H "xi-api-key: $KEY" "https://api.elevenlabs.io/v1/user" 2>/dev/null)
    CODE=$(echo "$RESP" | tail -1)
    if [ "$CODE" = "200" ]; then
      echo "OK: ElevenLabs key ($MASKED) is valid."
    else
      echo "FAIL: ElevenLabs key ($MASKED) returned HTTP $CODE."
      exit 1
    fi
    ;;
  ANTHROPIC_API_KEY|anthropic)
    RESP=$(curl -s -w "\n%{http_code}" -H "x-api-key: $KEY" -H "anthropic-version: 2023-06-01" -H "Content-Type: application/json" \
      "https://api.anthropic.com/v1/messages" \
      -d '{"model":"claude-3-haiku-20240307","max_tokens":1,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null)
    CODE=$(echo "$RESP" | tail -1)
    if [ "$CODE" = "200" ]; then
      echo "OK: Anthropic key ($MASKED) is valid."
    else
      echo "FAIL: Anthropic key ($MASKED) returned HTTP $CODE."
      exit 1
    fi
    ;;
  BRAVE_API_KEY|brave)
    RESP=$(curl -s -w "\n%{http_code}" -H "X-Subscription-Token: $KEY" "https://api.search.brave.com/res/v1/web/search?q=test&count=1" 2>/dev/null)
    CODE=$(echo "$RESP" | tail -1)
    if [ "$CODE" = "200" ]; then
      echo "OK: Brave Search key ($MASKED) is valid."
    else
      echo "FAIL: Brave Search key ($MASKED) returned HTTP $CODE."
      exit 1
    fi
    ;;
  GEMINI_API_KEY|gemini)
    RESP=$(curl -s -w "\n%{http_code}" "https://generativelanguage.googleapis.com/v1/models?key=$KEY" 2>/dev/null)
    CODE=$(echo "$RESP" | tail -1)
    if [ "$CODE" = "200" ]; then
      echo "OK: Gemini key ($MASKED) is valid."
    else
      echo "FAIL: Gemini key ($MASKED) returned HTTP $CODE."
      exit 1
    fi
    ;;
  *)
    echo "OK: Key ($MASKED) stored. No built-in test for '$SERVICE'."
    ;;
esac
