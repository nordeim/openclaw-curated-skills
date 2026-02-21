#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   run_youtube2md.sh <youtube_url> [mode] [output_path] [language] [model]
#
# mode:
#   full    -> summarize to Markdown (requires OPENAI_API_KEY)
#   extract -> transcript JSON only (--extract-only) + run prepare.py to build .txt
#
# Examples:
#   run_youtube2md.sh "https://youtu.be/VIDEO_ID"
#   run_youtube2md.sh "https://youtu.be/VIDEO_ID" full ./summaries/video.md Korean gpt-5-mini
#   run_youtube2md.sh "https://youtu.be/VIDEO_ID" extract ./summaries/video.json
#
# Optional env flags:
#   YOUTUBE2MD_JSON=1               add --json for machine-readable success/error output
#   YOUTUBE2MD_STDOUT=1             add --stdout (do not write file)
#   YOUTUBE2MD_OUT_DIR              add --out-dir <dir>
#   YOUTUBE2MD_ALLOW_EXTRACT_FALLBACK=1 (default) auto-switch full -> extract when OPENAI_API_KEY is missing
#   YOUTUBE2MD_NO_RUNTIME_INSTALL=0 when set to 1, do not use npx install; require local youtube2md binary
#   YOUTUBE2MD_BIN=<cmd/path>       explicit youtube2md command to run (bypasses npx)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PREPARE_PY="$SKILL_DIR/prepare.py"
YOUTUBE2MD_PACKAGE="youtube2md@1.0.1"
YOUTUBE2MD_NO_RUNTIME_INSTALL="${YOUTUBE2MD_NO_RUNTIME_INSTALL:-0}"
YOUTUBE2MD_BIN="${YOUTUBE2MD_BIN:-}"

run_youtube2md_cli() {
  local -a cli_args=("$@")

  if [[ -n "$YOUTUBE2MD_BIN" ]]; then
    if ! command -v "$YOUTUBE2MD_BIN" >/dev/null 2>&1; then
      echo "ERROR: YOUTUBE2MD_BIN command not found: $YOUTUBE2MD_BIN"
      return 12
    fi
    "$YOUTUBE2MD_BIN" "${cli_args[@]}"
    return $?
  fi

  if [[ "$YOUTUBE2MD_NO_RUNTIME_INSTALL" == "1" ]]; then
    if ! command -v youtube2md >/dev/null 2>&1; then
      echo "ERROR: youtube2md is required on PATH when YOUTUBE2MD_NO_RUNTIME_INSTALL=1"
      return 13
    fi
    youtube2md "${cli_args[@]}"
    return $?
  fi

  npx --yes "$YOUTUBE2MD_PACKAGE" "${cli_args[@]}"
}

extract_video_id() {
  local url="$1"
  local id=""

  id="$(printf '%s' "$url" | sed -nE 's#.*[?&]v=([^&#]+).*#\1#p' | head -n1)"
  if [[ -z "$id" ]]; then
    id="$(printf '%s' "$url" | sed -nE 's#.*youtu\.be/([^?&#/]+).*#\1#p' | head -n1)"
  fi
  if [[ -z "$id" ]]; then
    id="$(printf '%s' "$url" | sed -nE 's#.*/shorts/([^?&#/]+).*#\1#p' | head -n1)"
  fi
  if [[ -z "$id" ]]; then
    id="$(printf '%s' "$url" | sed -nE 's#.*/embed/([^?&#/]+).*#\1#p' | head -n1)"
  fi

  printf '%s' "$id"
}

guess_extract_json_path() {
  local url="$1"
  local video_id
  local out_dir

  video_id="$(extract_video_id "$url")"
  out_dir="${YOUTUBE2MD_OUT_DIR:-./summaries}"

  if [[ -n "$video_id" ]]; then
    printf '%s/%s.json' "$out_dir" "$video_id"
  fi
}

URL="${1:-}"
MODE="${2:-full}"
OUTPUT_PATH="${3:-}"
LANGUAGE="${4:-}"
MODEL="${5:-}"

if [[ -z "$URL" ]]; then
  echo "ERROR: missing YouTube URL"
  echo "Usage: run_youtube2md.sh <youtube_url> [mode] [output_path] [language] [model]"
  exit 2
fi

if [[ -z "$YOUTUBE2MD_BIN" && "$YOUTUBE2MD_NO_RUNTIME_INSTALL" != "1" ]]; then
  if ! command -v npx >/dev/null 2>&1; then
    echo "ERROR: npx is required unless YOUTUBE2MD_NO_RUNTIME_INSTALL=1 or YOUTUBE2MD_BIN is set."
    exit 3
  fi
fi

if [[ "$MODE" != "full" && "$MODE" != "extract" ]]; then
  echo "ERROR: mode must be 'full' or 'extract'"
  exit 5
fi

FALLBACK_FROM_FULL=0

if [[ "$MODE" == "full" && -z "${OPENAI_API_KEY:-}" ]]; then
  if [[ "${YOUTUBE2MD_ALLOW_EXTRACT_FALLBACK:-1}" == "1" ]]; then
    echo "WARN: OPENAI_API_KEY is missing; switching to extract mode"
    MODE="extract"
    FALLBACK_FROM_FULL=1

    if [[ -n "$OUTPUT_PATH" ]]; then
      echo "WARN: ignoring full-mode output path during fallback: $OUTPUT_PATH"
      OUTPUT_PATH=""
    fi
  else
    echo "ERROR: OPENAI_API_KEY is required for full mode"
    exit 6
  fi
fi

ARGS=(--url "$URL")

if [[ "$MODE" == "extract" ]]; then
  ARGS+=(--extract-only)
fi

if [[ -n "$OUTPUT_PATH" ]]; then
  mkdir -p "$(dirname "$OUTPUT_PATH")"
  ARGS+=(--out "$OUTPUT_PATH")
fi

if [[ -n "${YOUTUBE2MD_OUT_DIR:-}" ]]; then
  mkdir -p "$YOUTUBE2MD_OUT_DIR"
  ARGS+=(--out-dir "$YOUTUBE2MD_OUT_DIR")
fi

if [[ -n "$LANGUAGE" && "$MODE" == "full" ]]; then
  ARGS+=(--lang "$LANGUAGE")
fi

if [[ -n "$MODEL" && "$MODE" == "full" ]]; then
  ARGS+=(--model "$MODEL")
fi

if [[ "${YOUTUBE2MD_JSON:-0}" == "1" ]]; then
  ARGS+=(--json)
fi

if [[ "${YOUTUBE2MD_STDOUT:-0}" == "1" ]]; then
  ARGS+=(--stdout)
fi

run_youtube2md_cli "${ARGS[@]}"

EXTRACT_JSON_PATH=""
OUTPUT_TXT_PATH=""

if [[ "$MODE" == "extract" && "${YOUTUBE2MD_STDOUT:-0}" != "1" ]]; then
  if [[ -n "$OUTPUT_PATH" ]]; then
    EXTRACT_JSON_PATH="$OUTPUT_PATH"
  else
    EXTRACT_JSON_PATH="$(guess_extract_json_path "$URL")"
  fi

  if [[ -z "$EXTRACT_JSON_PATH" || ! -f "$EXTRACT_JSON_PATH" ]]; then
    SEARCH_DIR="${YOUTUBE2MD_OUT_DIR:-./summaries}"
    if [[ -d "$SEARCH_DIR" ]]; then
      EXTRACT_JSON_PATH="$(ls -1t "$SEARCH_DIR"/*.json 2>/dev/null | head -n1 || true)"
    fi
  fi

  if [[ -n "$EXTRACT_JSON_PATH" && -f "$EXTRACT_JSON_PATH" ]]; then
    if [[ ! -f "$PREPARE_PY" ]]; then
      echo "WARN: prepare.py not found at $PREPARE_PY (skipping .txt preparation)"
    elif ! command -v python3 >/dev/null 2>&1; then
      echo "WARN: python3 not found (skipping .txt preparation)"
    else
      PREPARE_OUTPUT="$(python3 "$PREPARE_PY" "$EXTRACT_JSON_PATH")"
      echo "$PREPARE_OUTPUT"
      OUTPUT_TXT_PATH="$(printf '%s\n' "$PREPARE_OUTPUT" | tail -n1)"
    fi
  else
    echo "WARN: could not locate extract JSON output (skipping .txt preparation)"
  fi
fi

if [[ "${YOUTUBE2MD_STDOUT:-0}" == "1" ]]; then
  echo "OK: youtube2md completed (stdout mode)"
elif [[ "$MODE" == "extract" ]]; then
  if [[ "$FALLBACK_FROM_FULL" == "1" ]]; then
    echo "INFO: completed in extract mode (full-mode fallback)"
  fi
  echo "OK: transcript extracted"

  if [[ -n "$OUTPUT_PATH" ]]; then
    echo "OUTPUT_JSON: $OUTPUT_PATH"
  elif [[ -n "$EXTRACT_JSON_PATH" ]]; then
    echo "OUTPUT_JSON: $EXTRACT_JSON_PATH"
  else
    echo "OUTPUT_JSON: ./summaries/<video_id>.json"
  fi

  if [[ -n "$OUTPUT_TXT_PATH" ]]; then
    echo "OUTPUT_TXT: $OUTPUT_TXT_PATH"
  fi
else
  if [[ -n "$OUTPUT_PATH" ]]; then
    echo "OK: summary generated"
    echo "OUTPUT_MD: $OUTPUT_PATH"
  else
    echo "OK: summary generated (default output under ./summaries/<video_id>.md)"
  fi
fi
