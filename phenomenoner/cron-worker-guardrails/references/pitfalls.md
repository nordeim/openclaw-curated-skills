# Cron exec pitfalls → safer replacements (portable)

## 1) Command substitution breaks quoting

**Bad (fragile):**
- `TODAY=$(date +%Y-%m-%d)`

**Better:**
- Don’t capture in shell; let a script compute the date.
- Or compute in Python and print JSON/text.

## 2) JSON arguments + nested quotes

**Bad (fragile):**
- `bash -lc '... --meta \'{"lane":"A-fast"}\''` (quotes inside quotes inside quotes)

**Better:**
- Avoid JSON args in shell when you can (omit `--meta`, or use a wrapper script).
- If you must: prefer **double quotes** around the JSON and avoid wrapping the whole command in another quoted `bash -lc '...'.`

## 3) `python3 -c '...'` with list literals / single quotes

A common self-own is:
- `python3 -c '... subprocess.check_output(['openclaw','cron','list',...]) ...'`

This breaks because the inner `['openclaw', ...]` terminates the outer single-quoted `-c` string.

**Better:**
- scripts-first (put the logic in `tools/*.py`)
- or wrap the `-c` string in **double quotes** if you need single quotes inside

## 4) Heredocs in generated shell

**Bad (fragile):**
- `python3 - <<"PY" ... PY` (easy to truncate / misquote)

**Better:**
- Put code in `tools/*.py` and run it.

## 5) `pipefail` + `head`

**Bad:**
- `set -o pipefail; big_command | head`

**Better:**
- Avoid `pipefail` if you’re piping into `head`.
- Or write a script that reads only what it needs.

## 6) Exec packing

**Bad:**
- One huge `bash -lc '...many steps...'`.

**Better:**
- Multiple short exec calls, or one deterministic script.
- Best: a single scripts-first wrapper that runs argv-list subprocess calls (no shell), and `chdir` to repo root.

## 7) `~` expansion and non-interactive shells

Some cron environments do not expand `~` the way you expect.

**Better:**
- Use an absolute path.
- Or use `$HOME` (POSIX) / `%USERPROFILE%` (Windows) if you must reference user-home.

## 8) Tooling optionality (uv/poetry/pip)

Not everyone uses the same Python toolchain.

- If you use **uv**, remember: `-m` is a **python** flag, not a `uv run` flag.
  - **Bad:** `uv run -m my_module`
  - **Good:** `uv run -- python -m my_module`

## 9) Output discipline

- Scheduled jobs should be silent by default: `NO_REPLY`.
- If failure: <= 6 bullets, include *what failed* + *next action*.
