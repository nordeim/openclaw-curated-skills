#!/usr/bin/env python3
"""Regression tests for guard_and_run adapter."""

import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "guard_and_run.py"


def run(*args: str, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    command = [sys.executable, str(SCRIPT), *args]
    proc = subprocess.run(
        command,
        env=env,
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


# Sanity: benign text should pass and execute command.
code, out, err = run(
    "--app",
    "website",
    "--action",
    "post",
    "--text",
    "Hello colleague, we have a stable release update.",
    "--",
    "python3",
    "-c",
    "print('ok')",
)
assert code == 0, (code, out, err)
assert out.strip() == "ok", (out, err)

# REVIEW should still run by default but emit a warning to stderr.
code, out, err = run(
    "--app",
    "website",
    "--action",
    "post",
    "--text",
    "John is a scammer and this is a guaranteed 100% win",
    "--",
    "python3",
    "-c",
    "print('review-ok')",
)
assert code == 0, (code, out, err)
assert out.strip() == "review-ok", (out, err)
assert "Guardrail REVIEW" in err, err

# Strict REVIEW should block.
code, out, err = run(
    "--strict",
    "--app",
    "website",
    "--action",
    "post",
    "--text",
    "John is a scammer and this is a guaranteed 100% win",
    "--",
    "python3",
    "-c",
    "print('should-not-run')",
)
assert code == 2, (code, out, err)
assert "Blocked by enterprise legal guardrails" in err, err
assert "should-not-run" not in out and "should-not-run" not in err, (out, err)

# Block threshold override can enforce a hard block.
code, out, err = run(
    "--app",
    "website",
    "--action",
    "post",
    "--text",
    "John is a scammer and this is a guaranteed 100% win",
    "--review-threshold",
    "2",
    "--block-threshold",
    "4",
    "--",
    "python3",
    "-c",
    "print('should-not-run2')",
)
assert code == 2, (code, out, err)
assert "Blocked by enterprise legal guardrails" in err, err

print("ok")
