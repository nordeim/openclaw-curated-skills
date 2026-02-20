---
name: uv-priority
description: Prioritize uv over pip for all Python package management and execution commands in Claude Code.
license: MIT
metadata: {"openclaw":{"always":true,"emoji":"⚡","homepage":"https://github.com/marcoracer/uv-priority","os":["darwin","linux","windows"],"tags":["python","uv","pip","package-management"],"requires":{"anyBins":["uv"]}}}
---

# UV Priority

Always prioritize `uv` over `pip` for any Python command in Claude Code.

## When to Use

Use when:
- Any task involving Python (scripts, libs, projects, dbt)
- Installing dependencies
- Creating/maintaining virtual environments
- Running Python commands
- Running tests

Do not use when:
- Tasks without Python

## Command Substitutions

Always use uv instead of pip:
- `uv pip install` → `uv add`
- `python -m venv` → `uv venv`
- `pip install -r requirements.txt` → `uv pip install -r requirements.txt` or migrate to `pyproject.toml`
- `python script.py` → `uv run script.py`
- `pytest` → `uv run pytest`
- `dbt run` → `uv run dbt run`
- `python -m pytest` → `uv run pytest`
- `pip list` → `uv pip list`
- `pip freeze` → `uv pip freeze`

## Priority

`uv` is ALWAYS the first option for any Python package management or execution.

## Fallback

If `uv` is not available on the system:
1. Suggest installing `uv` first: `curl -LsSf https://astral.sh/uv/install.sh | sh` (Linux/macOS) or `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` (Windows)
2. If installation is not possible, suggest using `pip` as fallback
3. Ask for user confirmation before proceeding with `pip`

## Flexibility

This is a flexible skill - adapt to context and use good judgment. The priority is `uv`, but use appropriate alternatives when genuinely necessary (e.g., system constraints, specific CI environments where `uv` cannot be installed).

## Notes

- Models often already use `uv`; this skill reinforces `uv` as the priority
- No instructions about `pyproject.toml` structure included
- Assume project already has `pyproject.toml` configured or `uv` will manage it
- Mention pytest should be run with `uv run pytest` when applicable
