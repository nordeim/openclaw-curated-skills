#!/usr/bin/env python3
"""Apt maintenance helper for the OpenClaw host (sys-updater).

Modes:
- run_6am: sudo apt-get update; sudo unattended-upgrade; sudo apt-get -s upgrade; snapshot upgradable pkgs.
- report_9am: render a human report from last run state.

Conservative by design:
- No full-upgrade/dist-upgrade
- No autoremove
- Non-security upgrades are NOT applied automatically (planned list is informational)
"""

from __future__ import annotations

import argparse
import fcntl
import json
import logging
import logging.handlers
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

# === Constants ===
DEFAULT_TIMEOUT = 600  # 10 minutes for long-running commands like unattended-upgrade
APT_HISTORY_HOURS = 24  # Only consider upgrades from last N hours

# === Directories ===
BASE_DIR = Path(os.getenv("SYS_UPDATER_BASE_DIR", "/home/moltuser/clawd/sys-updater"))
STATE_DIR = Path(os.getenv("SYS_UPDATER_STATE_DIR", BASE_DIR / "state" / "apt"))
LOG_DIR = Path(os.getenv("SYS_UPDATER_LOG_DIR", BASE_DIR / "state" / "logs"))
LOCK_FILE = STATE_DIR / ".run_6am.lock"

LAST_RUN_PATH = STATE_DIR / "last_run.json"
TRACK_PATH = STATE_DIR / "tracked.json"

# === Logging setup: daily rotation, keep 10 days ===
LOG_FILE = LOG_DIR / "apt_maint.log"

# Global state
_dry_run = False
_verbose = False


def _ensure_directories() -> None:
    """Create required directories and verify write permissions."""
    for d in (STATE_DIR, LOG_DIR):
        d.mkdir(parents=True, exist_ok=True)
        # Verify write permission
        test_file = d / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except PermissionError:
            raise PermissionError(f"No write permission for directory: {d}")


def _setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure file logging with daily rotation (10 days retention).

    Args:
        verbose: If True, also log to console (stderr).
    """
    logger = logging.getLogger("sys_updater")

    # Clear existing handlers to allow reconfiguration
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    # File handler: daily rotation, 10 days
    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=10,
        encoding="utf-8",
        utc=True,
    )
    file_handler.suffix = "%Y-%m-%d"
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (if verbose)
    if verbose:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


# Initialize with file-only logging; reconfigure if --verbose
_ensure_directories()
log = _setup_logging(verbose=False)


def sh(
    cmd: list[str],
    *,
    check: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
) -> subprocess.CompletedProcess[str]:
    """Run a shell command with timeout.

    Args:
        cmd: Command and arguments.
        check: Raise on non-zero exit code.
        timeout: Timeout in seconds (default 600s = 10min).

    Returns:
        CompletedProcess with stdout/stderr captured.

    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout.
        subprocess.CalledProcessError: If check=True and command fails.
    """
    global _dry_run
    if _dry_run and cmd[0] == "sudo":
        log.info("[DRY-RUN] Would execute: %s", " ".join(cmd))
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
    return subprocess.run(cmd, text=True, capture_output=True, check=check, timeout=timeout)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def sudo_cmd(args: list[str]) -> list[str]:
    return ["sudo", "-n", *args]


@dataclass
class RunResult:
    ranAt: str
    aptUpdateOk: bool
    unattendedOk: bool
    simulatedOk: bool
    updatedPackages: list[str]
    # plannedApplied is reserved for future (when we actually apply planned non-security upgrades)
    plannedApplied: list[str]
    securityNote: str | None
    upgradable: list[str]
    simulateSummary: str


def parse_apt_upgrade_simulation(output: str) -> str:
    m = re.search(r"\d+ upgraded, \d+ newly installed, \d+ to remove and \d+ not upgraded\.", output)
    if m:
        return m.group(0)
    lines = output.strip().splitlines()
    return lines[-1] if lines else ""


def list_upgradable() -> list[str]:
    """List upgradable packages using apt directly (no bash wrapper)."""
    # Use apt list directly, suppressing the warning about CLI stability
    env = os.environ.copy()
    env["LANG"] = "C.UTF-8"
    cp = subprocess.run(
        ["apt", "list", "--upgradable"],
        text=True,
        capture_output=True,
        check=True,
        env=env,
        timeout=60,
    )
    pkgs: list[str] = []
    for line in cp.stdout.splitlines():
        if not line or line.startswith("Listing"):
            continue
        # Format: "package/repo version [upgradable from: old_version]"
        name = line.split("/")[0].strip()
        if name:
            pkgs.append(name)
    return sorted(set(pkgs))


def parse_recent_upgrades_from_history(hours: int = APT_HISTORY_HOURS) -> list[str]:
    """Parse apt history.log for packages upgraded in the last N hours.

    Args:
        hours: Only consider upgrades from the last N hours.

    Returns:
        List of package names that were upgraded recently.
    """
    p = Path("/var/log/apt/history.log")
    if not p.exists():
        return []
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except PermissionError:
        return []

    cutoff = now_utc() - timedelta(hours=hours)
    upgraded: list[str] = []

    # Parse history.log blocks
    # Format:
    # Start-Date: 2024-01-15  06:00:05
    # Commandline: ...
    # Upgrade: pkg1:arch (old -> new), pkg2:arch (old -> new)
    # End-Date: ...

    current_date: datetime | None = None
    for line in text.splitlines():
        if line.startswith("Start-Date:"):
            # Parse: "Start-Date: 2024-01-15  06:00:05"
            date_str = line.replace("Start-Date:", "").strip()
            try:
                # Handle double spaces in date format
                date_str = re.sub(r"\s+", " ", date_str)
                current_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                current_date = current_date.replace(tzinfo=timezone.utc)
            except ValueError:
                current_date = None
        elif line.startswith("Upgrade:") and current_date and current_date >= cutoff:
            # Parse: "Upgrade: pkg1:arch (1.0 -> 2.0), pkg2:arch (1.0 -> 2.0)"
            items = line.replace("Upgrade:", "").split(",")
            for it in items:
                # Extract package name before the colon (arch separator)
                name = it.strip().split(":")[0].split()[0]
                if name:
                    upgraded.append(name)

    return sorted(set(upgraded))


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Failed to load %s: %s; using default", path, e)
        return default


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class LockFile:
    """Context manager for exclusive file locking (prevents parallel runs)."""

    def __init__(self, path: Path):
        self.path = path
        self.fd: int | None = None

    def __enter__(self) -> "LockFile":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fd = os.open(str(self.path), os.O_CREAT | os.O_RDWR)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(self.fd)
            raise RuntimeError(f"Another instance is running (lock: {self.path})")
        # Write PID for debugging
        os.ftruncate(self.fd, 0)
        os.write(self.fd, f"{os.getpid()}\n".encode())
        return self

    def __exit__(self, *args: Any) -> None:
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
            try:
                self.path.unlink()
            except OSError:
                pass


def extract_last_line(text: str | None) -> str | None:
    """Safely extract the last non-empty line from text."""
    if not text:
        return None
    lines = text.strip().splitlines()
    return lines[-1] if lines else None


def run_6am() -> RunResult:
    ran_at = now_iso()
    log.info("=== run_6am START ===")
    log.info("State files: last_run=%s, tracked=%s", LAST_RUN_PATH, TRACK_PATH)

    apt_update_ok = True
    try:
        log.info("Running: sudo apt-get update")
        sh(sudo_cmd(["apt-get", "update"]), check=True, timeout=300)
        log.info("apt-get update: OK")
    except subprocess.TimeoutExpired:
        apt_update_ok = False
        log.error("apt-get update: TIMEOUT (300s)")
    except Exception as e:
        apt_update_ok = False
        log.error("apt-get update: FAILED (%s)", e)

    unattended_ok = True
    security_note: str | None = None
    try:
        log.info("Running: sudo unattended-upgrade -d")
        cp = sh(sudo_cmd(["unattended-upgrade", "-d"]), check=False, timeout=DEFAULT_TIMEOUT)
        unattended_ok = cp.returncode == 0
        security_note = extract_last_line(cp.stdout)
        log.info("unattended-upgrade: %s (rc=%d)", "OK" if unattended_ok else "FAIL", cp.returncode)
    except subprocess.TimeoutExpired:
        unattended_ok = False
        log.error("unattended-upgrade: TIMEOUT (%ds)", DEFAULT_TIMEOUT)
    except Exception as e:
        unattended_ok = False
        log.error("unattended-upgrade: FAILED (%s)", e)

    simulated_ok = True
    sim_summary = ""
    try:
        log.info("Running: sudo apt-get -s upgrade (simulation)")
        cp = sh(sudo_cmd(["apt-get", "-s", "upgrade"]), check=False, timeout=120)
        simulated_ok = cp.returncode == 0
        sim_summary = parse_apt_upgrade_simulation((cp.stdout or "") + "\n" + (cp.stderr or ""))
        log.info("apt-get -s upgrade: %s; summary=%s", "OK" if simulated_ok else "FAIL", sim_summary)
    except subprocess.TimeoutExpired:
        simulated_ok = False
        log.error("apt-get -s upgrade: TIMEOUT (120s)")
    except Exception as e:
        simulated_ok = False
        log.error("apt-get -s upgrade: FAILED (%s)", e)

    upgradable: list[str] = []
    try:
        upgradable = list_upgradable()
        log.info("Upgradable packages found: %d", len(upgradable))
    except subprocess.TimeoutExpired:
        log.error("list_upgradable: TIMEOUT")
    except Exception as e:
        log.error("list_upgradable: FAILED (%s)", e)

    updated_pkgs = parse_recent_upgrades_from_history(hours=APT_HISTORY_HOURS)
    log.info("Recently updated packages (last %dh): %d", APT_HISTORY_HOURS, len(updated_pkgs))

    result = RunResult(
        ranAt=ran_at,
        aptUpdateOk=apt_update_ok,
        unattendedOk=unattended_ok,
        simulatedOk=simulated_ok,
        updatedPackages=updated_pkgs,
        plannedApplied=[],
        securityNote=security_note,
        upgradable=upgradable,
        simulateSummary=sim_summary,
    )
    save_json(LAST_RUN_PATH, result.__dict__)
    log.info("Saved last_run.json")

    # Load and update tracked packages
    tracked = load_json(TRACK_PATH, {"createdAt": ran_at, "items": {}})
    items: dict[str, Any] = tracked.get("items") or {}

    # Track new packages
    new_tracked = 0
    for pkg in upgradable:
        if pkg not in items:
            new_tracked += 1
            items[pkg] = {
                "firstSeenAt": ran_at,
                "reviewedAt": None,
                "planned": False,
                "blocked": False,
                "note": None,
            }

    # Cleanup: remove packages no longer upgradable (unless blocked/planned)
    upgradable_set = set(upgradable)
    removed = 0
    to_remove = []
    for pkg, meta in items.items():
        if pkg not in upgradable_set:
            # Keep if blocked or planned (user made a decision)
            if not meta.get("blocked") and not meta.get("planned"):
                to_remove.append(pkg)
    for pkg in to_remove:
        del items[pkg]
        removed += 1

    if removed > 0:
        log.info("Cleanup: removed %d packages no longer upgradable", removed)

    tracked["items"] = items
    save_json(TRACK_PATH, tracked)
    log.info("Updated tracked.json: %d new, %d removed, %d total", new_tracked, removed, len(items))

    # Log summary of planned/blocked decisions
    planned_count = sum(1 for m in items.values() if m.get("planned") and not m.get("blocked"))
    blocked_count = sum(1 for m in items.values() if m.get("blocked"))
    log.info("Tracking summary: planned=%d, blocked=%d", planned_count, blocked_count)

    # Run pkg_maint.py for npm/brew checks
    try:
        log.info("Running: pkg_maint.py for npm/brew checks")
        pkg_maint_path = Path(__file__).parent / "pkg_maint.py"
        if pkg_maint_path.exists():
            cp = subprocess.run(
                ["python3", str(pkg_maint_path)],
                capture_output=True, text=True, timeout=120
            )
            if cp.returncode == 0:
                log.info("pkg_maint.py: OK")
            else:
                log.warning("pkg_maint.py: rc=%d, err=%s", cp.returncode, cp.stderr[:200])
        else:
            log.warning("pkg_maint.py not found at %s", pkg_maint_path)
    except Exception as e:
        log.error("pkg_maint.py failed: %s", e)

    log.info("=== run_6am END (success) ===")
    return result


def render_report(now_msk_label: str = "09:00 MSK") -> str:
    log.info("=== report_9am START ===")
    log.info("Reading state files: last_run=%s, tracked=%s", LAST_RUN_PATH, TRACK_PATH)
    last = load_json(LAST_RUN_PATH, None)
    tracked = load_json(TRACK_PATH, {"items": {}})

    if not last:
        log.warning("No last_run.json found")
        log.info("=== report_9am END ===")
        return "🕘 Отчёт (09:00 MSK)\n\n⚠️ Нет данных: задача 06:00 ещё не запускалась или не смогла сохранить состояние."

    updated = last.get("updatedPackages") or []
    applied_planned = last.get("plannedApplied") or []
    sim = last.get("simulateSummary") or ""

    items: dict[str, Any] = (tracked.get("items") or {})

    tracked_pkgs = sorted([p for p, meta in items.items() if not meta.get("reviewedAt") and not meta.get("blocked")])
    planned_pkgs = sorted([p for p, meta in items.items() if meta.get("planned") and not meta.get("blocked")])
    blocked_pkgs = sorted([p for p, meta in items.items() if meta.get("blocked")])

    def fmt_list(pkgs: list[str], max_n: int = 25) -> str:
        if not pkgs:
            return "—"
        if len(pkgs) <= max_n:
            return ", ".join(pkgs)
        return ", ".join(pkgs[:max_n]) + f" …(+{len(pkgs)-max_n})"

    lines: list[str] = []

    lines.append(f"🕘 Отчёт ({now_msk_label})")
    lines.append("")

    lines.append("⚙️ Сегодня в 06:00:")
    lines.append(f"- apt update: {'OK' if last.get('aptUpdateOk') else 'FAIL'}")
    lines.append(f"- security updates (unattended-upgrade): {'OK' if last.get('unattendedOk') else 'FAIL'}")
    lines.append(f"- симуляция upgrade: {'OK' if last.get('simulatedOk') else 'FAIL'}; {sim}")
    lines.append(f"- обновилось (любые apt апдейты): {fmt_list(updated)}")
    lines.append("")

    lines.append("✅ Сегодня применено (из запланированного):")
    lines.append(f"- apt (non-security planned): {fmt_list(applied_planned)}")
    lines.append("")

    lines.append("🔎 Отслеживаем (не-security):")
    lines.append(f"- кандидаты: {fmt_list(tracked_pkgs)}")
    if blocked_pkgs:
        lines.append(f"- ⚠️ заблокировано из-за багов/рисков: {fmt_list(blocked_pkgs)}")
    lines.append("")

    lines.append("📅 Запланировано на завтра 06:00:")
    lines.append("- security updates + симуляция (всегда)")
    lines.append(f"- apt (non-security planned): {fmt_list(planned_pkgs)}")

    # Add npm/brew sections
    npm_tracked = load_json(STATE_DIR / "npm_tracked.json", {"items": {}})
    brew_tracked = load_json(STATE_DIR / "brew_tracked.json", {"items": {}})
    
    npm_items = npm_tracked.get("items", {})
    brew_items = brew_tracked.get("items", {})
    
    npm_outdated = [k for k, v in npm_items.items() if not v.get("blocked")]
    brew_outdated = [k for k, v in brew_items.items() if not v.get("blocked")]
    npm_blocked = [k for k, v in npm_items.items() if v.get("blocked")]
    brew_blocked = [k for k, v in brew_items.items() if v.get("blocked")]
    
    if npm_items or brew_items:
        lines.append("")
        lines.append("📦 Другие пакетные менеджеры:")
        
        if npm_items:
            lines.append(f"- npm global outdated: {fmt_list(npm_outdated, max_n=5)}")
            if npm_blocked:
                lines.append(f"  ⚠️ npm blocked: {fmt_list(npm_blocked, max_n=3)}")
        
        if brew_items:
            lines.append(f"- brew outdated: {fmt_list(brew_outdated, max_n=5)}")
            if brew_blocked:
                lines.append(f"  ⚠️ brew blocked: {fmt_list(brew_blocked, max_n=3)}")
    
    # Add skills section
    rc, stdout, stderr = subprocess.run(
        ["clawhub", "list"], capture_output=True, text=True, timeout=30
    ).returncode, "", ""
    if rc == 0:
        lines.append("")
        lines.append("🧩 OpenClaw Skills:")
        lines.append("- Автообновление при каждом запуске (без карантина)")
        result = subprocess.run(
            ["clawhub", "list"], capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout:
            skill_count = len([l for l in result.stdout.strip().split('\n') if l.strip()])
            lines.append(f"- Установлено: {skill_count} скиллов")

    log.info("Report generated: updated=%d, tracked=%d, planned=%d, blocked=%d",
             len(updated), len(tracked_pkgs), len(planned_pkgs), len(blocked_pkgs))
    log.info("=== report_9am END ===")
    return "\n".join(lines)


def main() -> int:
    global _dry_run, _verbose, log

    ap = argparse.ArgumentParser(
        description="Apt maintenance helper for sys-updater.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 apt_maint.py run_6am           # Run daily maintenance
  python3 apt_maint.py run_6am --dry-run # Simulate without executing sudo commands
  python3 apt_maint.py report_9am        # Generate Telegram report
  python3 apt_maint.py report_9am -v     # Generate report with verbose logging
""",
    )
    ap.add_argument("mode", choices=["run_6am", "report_9am"], help="Operation mode")
    ap.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Don't execute sudo commands, just log what would happen",
    )
    ap.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Also log to console (stderr)",
    )
    args = ap.parse_args()

    _dry_run = args.dry_run
    _verbose = args.verbose

    # Reconfigure logging if verbose requested
    if _verbose:
        log = _setup_logging(verbose=True)

    if _dry_run:
        log.info("DRY-RUN mode enabled: sudo commands will be skipped")

    exit_code = 0
    try:
        if args.mode == "run_6am":
            with LockFile(LOCK_FILE):
                run_6am()
        elif args.mode == "report_9am":
            print(render_report())
        else:
            log.error("Unknown mode: %s", args.mode)
            exit_code = 2
    except RuntimeError as e:
        # LockFile error (another instance running)
        log.error("%s", e)
        print(f"Error: {e}", file=sys.stderr)
        exit_code = 1
    except Exception as e:
        log.exception("Unhandled exception in mode=%s: %s", args.mode, e)
        exit_code = 1

    if exit_code != 0:
        log.error("Exiting with code %d", exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
