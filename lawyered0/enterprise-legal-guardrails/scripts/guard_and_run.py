#!/usr/bin/env python3
"""Run enterprise guardrails on draft text, then execute a command.

This is a generic adapter for outbound/public-facing workflows that do not yet
have native enterprise guardrail wiring.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


CHECKER_SCRIPT = Path(__file__).resolve().parent / "check_enterprise_guardrails.py"


def _get_env_bool(*names: str, default: bool = False) -> bool:
    raw = _get_env(*names)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_env(*names: str) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value is not None:
            return value
    return None


def _read_text(text: str | None, text_file: str | None) -> str:
    if text is not None:
        return text.strip()
    if text_file is not None:
        return Path(text_file).read_text(encoding="utf-8").strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise ValueError("No text to validate. Use --text, --text-file, or stdin.")


def run_guardrails(
    *,
    text: str,
    action: str,
    app: str,
    scope: str | None,
    apps: list[str] | None,
    policies: list[str] | None,
    review_threshold: int | None,
    block_threshold: int | None,
    strict: bool,
) -> dict:
    if not CHECKER_SCRIPT.exists():
        raise RuntimeError(f"Guardrail script not found: {CHECKER_SCRIPT}")

    args = [
        sys.executable,
        str(CHECKER_SCRIPT),
        "--action",
        action,
        "--text",
        text,
        "--json",
    ]

    if app:
        args.extend(["--app", app])
    if scope:
        args.extend(["--scope", scope])
    if apps:
        args.extend(["--apps", *apps])
    if policies:
        args.extend(["--policies", *policies])
    if review_threshold is not None:
        args.extend(["--review-threshold", str(review_threshold)])
    if block_threshold is not None:
        args.extend(["--block-threshold", str(block_threshold)])

    proc = subprocess.run(args, check=False, text=True, capture_output=True)
    stdout = (proc.stdout or "").strip()
    if not stdout:
        err = (proc.stderr or "").strip()
        raise RuntimeError(f"Guardrail check returned no output. {err}".strip())

    try:
        report = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Guardrail checker output was invalid JSON: {exc}")

    status = report.get("status")
    if proc.returncode not in {0, 1, 2}:
        err = (proc.stderr or "").strip()
        raise RuntimeError(
            f"Guardrail check failed before execution (exit={proc.returncode}). {status=} {err}".strip()
        )
    if status not in {"PASS", "WATCH", "REVIEW", "BLOCK"}:
        raise RuntimeError(f"Guardrail checker returned unexpected status: {status}")

    status = report.get("status")
    if status == "BLOCK" or (strict and status == "REVIEW"):
        print(
            f"Blocked by enterprise legal guardrails ({status}) for {action} on {app or 'unknown'} "
            f"before command execution. Score: {report.get('score', 'n/a')}, "
            f"Findings: {report.get('findings_count', 'n/a')}",
            file=sys.stderr,
        )
        raise SystemExit(2)

    if status == "REVIEW":
        suggestion = (report.get("suggestions") or ["Consider rewriting before execution."])[0]
        print(f"Guardrail REVIEW for {action} on {app or 'unknown'}: {suggestion}", file=sys.stderr)

    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run enterprise legal guardrails on draft outbound content, "
            "then execute a command only when allowed."
        )
    )
    parser.add_argument("--app", default="", help="App context for app-level scoping/filtering.")
    parser.add_argument(
        "--action",
        default="generic",
        choices=["post", "comment", "message", "trade", "market-analysis", "generic"],
        help="Action profile to use for policy selection.",
    )
    parser.add_argument("--text", help="Draft content to validate.")
    parser.add_argument("--text-file", help="Read draft content from a file.")
    parser.add_argument(
        "--scope",
        choices=["all", "include", "exclude"],
        default=os.environ.get(
            "ENTERPRISE_LEGAL_GUARDRAILS_OUTBOUND_SCOPE",
            os.environ.get(
                "ELG_OUTBOUND_SCOPE",
                os.environ.get(
                    "BABYLON_GUARDRAILS_SCOPE",
                    os.environ.get("BABYLON_GUARDRAILS_OUTBOUND_SCOPE", "all"),
                ),
            ),
        ),
        help="Scope mode for app filtering: all|include|exclude.",
    )
    parser.add_argument("--apps", nargs="*", help="App list used with --scope include|exclude.")
    parser.add_argument("--policies", nargs="+", help="Explicit policy families to enforce.")
    parser.add_argument("--review-threshold", type=int, help="Override review threshold.")
    parser.add_argument("--block-threshold", type=int, help="Override block threshold.")
    parser.add_argument(
        "--strict",
        action="store_true",
        default=_get_env_bool(
            "ENTERPRISE_LEGAL_GUARDRAILS_STRICT",
            "ELG_STRICT",
            "BABYLON_GUARDRAILS_STRICT",
            default=False,
        ),
        help="Treat REVIEW as BLOCK for this run.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to run after '--', for example: -- python3 script.py ...",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.command:
        print("Missing command. Use -- <command...>", file=sys.stderr)
        return 2

    if args.command[0] != "--":
        print("Guardrail gate requires delimiter -- before command.", file=sys.stderr)
        return 2

    command = args.command[1:]
    if not command:
        print("Missing command after --.", file=sys.stderr)
        return 2

    try:
        text = _read_text(args.text, args.text_file)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        run_guardrails(
            text=text,
            action=args.action,
            app=args.app,
            scope=args.scope,
            apps=args.apps,
            policies=args.policies,
            review_threshold=args.review_threshold,
            block_threshold=args.block_threshold,
            strict=args.strict,
        )
    except RuntimeError as exc:
        print(f"Guardrail error: {exc}", file=sys.stderr)
        return 1

    proc = subprocess.run(command)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
