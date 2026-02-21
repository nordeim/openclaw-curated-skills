# Troubleshooting

Use `--json` when possible to get structured errors.

## Quick checks

- Node.js 18+ installed
- `python3` available (required for `prepare.py` transcript text output)
- Runtime mode check:
  - default runtime install mode → `npx` available
  - strict local mode (`YOUTUBE2MD_NO_RUNTIME_INSTALL=1`) → `youtube2md` available on PATH
  - explicit command mode (`YOUTUBE2MD_BIN=...`) → command/path is executable
- URL is a valid YouTube link
- `OPENAI_API_KEY` set for full mode
- Runner uses fixed package target: `youtube2md@1.0.1`

## Common failures and fixes

### 1) `npx` not found (runtime install mode)

Fix:
- Install Node.js 18+
- Verify with `npx --version`
- Or switch to strict local mode:
  - `YOUTUBE2MD_NO_RUNTIME_INSTALL=1` and ensure `youtube2md` exists on PATH

### 2) `python3` not found (extract mode text prep)

Symptom:
- Extract JSON is created but `.txt` transcript is missing

Fix:
- Install Python 3
- Verify with `python3 --version`
- Re-run extract mode so `prepare.py` can generate `.txt`

### 3) Full mode without API key

Symptom:
- OpenAI auth error / missing key

Fix:
- Default runner behavior auto-falls back to extract mode when key is missing.
- To force hard-fail behavior instead, set:
  - `YOUTUBE2MD_ALLOW_EXTRACT_FALLBACK=0`
- If you want full summary output, set `OPENAI_API_KEY` and rerun full mode.

### 4) Transcript unavailable

Symptom:
- Captions not available and fallback also fails

Fix:
- Retry later / try another video
- For Whisper fallback paths, ensure `OPENAI_API_KEY` is set

### 5) OpenAI rate limit

Fix:
- Retry after backoff
- Optionally use a different model (`--model`)

### 6) Output file missing / write failure

Fix:
- Provide explicit writable path:
  - Full: `scripts/run_youtube2md.sh <url> full ./summaries/custom.md`
  - Extract: `scripts/run_youtube2md.sh <url> extract ./summaries/custom.json`

### 7) Package trust / version policy

Symptom:
- Security policy blocks runtime installs or unreviewed npm execution

Fix:
- Keep fixed package target (`youtube2md@1.0.1`) unless a reviewed version bump is intentionally applied in the script.
- For stricter controls, disable runtime install (`YOUTUBE2MD_NO_RUNTIME_INSTALL=1`) or set trusted binary path (`YOUTUBE2MD_BIN`).
- See `references/security.md` for installation-time risk decisions.

## Structured error codes (`--json`)

- `E_TRANSCRIPT_UNAVAILABLE`
- `E_OPENAI_AUTH`
- `E_OPENAI_RATE_LIMIT`
- `E_WHISPER_FAILED`
- `E_NETWORK`
- `E_WRITE_FAILED`

## Recovery response pattern

1. State what failed in one line.
2. Give one concrete retry/fix command.
3. Ask whether to retry automatically.
