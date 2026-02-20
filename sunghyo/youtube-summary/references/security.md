# Security and installation considerations

Review this before installing or enabling the skill.

## 1) Runtime dependencies are mandatory

The runner relies on:

- Node.js 18+
- `python3` (for transcript text preparation via `prepare.py`)
- `npx` **only when using runtime npm execution mode** (default)

If these are missing, conversion or transcript post-processing will fail.

## 2) Runtime package execution risk

By default, the skill executes `youtube2md` through `npx`, which downloads and runs code from npm at execution time.

Current hardening default:

- package target is hard-pinned to `youtube2md@1.0.1`

This reduces churn compared with unpinned or `@latest` targets, but still requires trust in npm supply chain and transitive dependencies.

For stricter environments, prefer one of:

- disable runtime installs (`YOUTUBE2MD_NO_RUNTIME_INSTALL=1`) and use a preinstalled local `youtube2md`
- set explicit trusted binary path (`YOUTUBE2MD_BIN`)
- vendor a reviewed CLI/binary
- use a vetted internal package mirror
- audit and pin approved package versions

## 3) OPENAI_API_KEY data exposure boundary

Providing `OPENAI_API_KEY` enables full summarization mode in youtube2md workflows.

Practical implication:

- transcript text and/or related content may be sent to OpenAI APIs.

If content is sensitive, do not set `OPENAI_API_KEY`; use extract-only mode and summarize locally from prepared transcript text.

## 4) Upstream trust and review

`prepare.py` and local shell script are simple and readable, but the highest trust boundary is still the upstream `youtube2md` npm package and its dependencies.

Before production use in sensitive environments:

- review upstream source and release history
- verify dependency tree and lock strategy
- define an update cadence and re-audit process

## Recommended maintainer actions

1. Keep runtime dependencies explicit in skill docs (`Node.js/python3`, plus `npx` when runtime mode is enabled).
2. Keep package target fixed at `youtube2md@1.0.1` unless there is an explicit reviewed version bump.
3. For sensitive systems, prefer `YOUTUBE2MD_NO_RUNTIME_INSTALL=1` (or `YOUTUBE2MD_BIN`) to avoid runtime npm execution.
4. Document `OPENAI_API_KEY` behavior as an explicit data-sharing choice.
5. Re-audit upstream package versions before bumping pins.
