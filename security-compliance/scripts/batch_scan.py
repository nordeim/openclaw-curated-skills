#!/usr/bin/env python3
"""
Batch Security Scanner - Scans all skills and generates consolidated report
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

RESULTS_DIR = Path(__file__).parent.parent / "security_scan_results"
TRUSTSKILL_CLI = Path(__file__).parent.parent / "src" / "cli.py"
SKILLS_ROOT = Path(__file__).parent.parent.parent

print_lock = threading.Lock()


def safe_print(msg):
    with print_lock:
        print(msg, flush=True)


def scan_skill(skill_path: str) -> dict:
    skill_name = Path(skill_path).name
    try:
        result = subprocess.run(
            [
                "python",
                str(TRUSTSKILL_CLI),
                skill_path,
                "--mode",
                "deep",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(TRUSTSKILL_CLI.parent.parent),
        )

        if result.returncode not in (0, 1):
            return {
                "skill_name": skill_name,
                "skill_path": skill_path,
                "error": f"Scanner exited with code {result.returncode}",
                "stderr": result.stderr[:500] if result.stderr else None,
            }

        data = json.loads(result.stdout)
        data["skill_name"] = skill_name
        data["skill_path"] = skill_path
        return data

    except subprocess.TimeoutExpired:
        return {
            "skill_name": skill_name,
            "skill_path": skill_path,
            "error": "Scan timeout (60s)",
        }
    except json.JSONDecodeError as e:
        return {
            "skill_name": skill_name,
            "skill_path": skill_path,
            "error": f"JSON parse error: {str(e)}",
        }
    except Exception as e:
        return {"skill_name": skill_name, "skill_path": skill_path, "error": str(e)}


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    skills_file = Path("/tmp/skill_paths.txt")
    if not skills_file.exists():
        print("ERROR: /tmp/skill_paths.txt not found. Run the find command first.")
        sys.exit(1)

    with open(skills_file) as f:
        skill_paths = [line.strip() for line in f if line.strip()]

    total = len(skill_paths)
    print(f"{'=' * 60}")
    print(f"BATCH SECURITY SCAN - {total} skills")
    print(f"Mode: deep | Output: JSON")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"{'=' * 60}\n")

    all_results = []
    completed = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_path = {
            executor.submit(scan_skill, path): path for path in skill_paths
        }

        for future in as_completed(future_to_path):
            result = future.result()
            all_results.append(result)
            completed += 1

            skill_name = result.get("skill_name", "unknown")
            if "error" in result:
                safe_print(f"[{completed}/{total}] ❌ {skill_name}: {result['error']}")
            else:
                high = result.get("risk_summary", {}).get("HIGH", 0)
                med = result.get("risk_summary", {}).get("MEDIUM", 0)
                low = result.get("risk_summary", {}).get("LOW", 0)
                status = "🔴" if high > 0 else "🟡" if med > 0 else "✅"
                safe_print(
                    f"[{completed}/{total}] {status} {skill_name}: H={high} M={med} L={low}"
                )

            result_file = RESULTS_DIR / f"{result.get('skill_name', 'unknown')}.json"
            with open(result_file, "w") as f:
                json.dump(result, f, indent=2, default=str)

    consolidated = {
        "scan_metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_skills": total,
            "scan_mode": "deep",
            "scanner_version": "3.0.0",
        },
        "summary": {
            "total_scanned": len(all_results),
            "errors": sum(1 for r in all_results if "error" in r),
            "high_risk": sum(
                1 for r in all_results if r.get("risk_summary", {}).get("HIGH", 0) > 0
            ),
            "medium_risk": sum(
                1 for r in all_results if r.get("risk_summary", {}).get("MEDIUM", 0) > 0
            ),
            "clean": sum(
                1
                for r in all_results
                if not r.get("error")
                and r.get("risk_summary", {}).get("HIGH", 0) == 0
                and r.get("risk_summary", {}).get("MEDIUM", 0) == 0
            ),
        },
        "risk_totals": {
            "HIGH": sum(
                r.get("risk_summary", {}).get("HIGH", 0)
                for r in all_results
                if not r.get("error")
            ),
            "MEDIUM": sum(
                r.get("risk_summary", {}).get("MEDIUM", 0)
                for r in all_results
                if not r.get("error")
            ),
            "LOW": sum(
                r.get("risk_summary", {}).get("LOW", 0)
                for r in all_results
                if not r.get("error")
            ),
            "INFO": sum(
                r.get("risk_summary", {}).get("INFO", 0)
                for r in all_results
                if not r.get("error")
            ),
        },
        "high_risk_skills": [],
        "medium_risk_skills": [],
        "findings_by_category": {},
        "all_results": all_results,
    }

    for r in all_results:
        if r.get("error"):
            continue
        skill_name = r.get("skill_name", "unknown")
        if r.get("risk_summary", {}).get("HIGH", 0) > 0:
            consolidated["high_risk_skills"].append(
                {
                    "name": skill_name,
                    "path": r.get("skill_path"),
                    "high_count": r["risk_summary"]["HIGH"],
                    "findings": r.get("findings", []),
                }
            )
        elif r.get("risk_summary", {}).get("MEDIUM", 0) > 0:
            consolidated["medium_risk_skills"].append(
                {
                    "name": skill_name,
                    "path": r.get("skill_path"),
                    "medium_count": r["risk_summary"]["MEDIUM"],
                    "findings": r.get("findings", []),
                }
            )

        for finding in r.get("findings", []):
            category = finding.get("category", "unknown")
            if category not in consolidated["findings_by_category"]:
                consolidated["findings_by_category"][category] = []
            consolidated["findings_by_category"][category].append(
                {
                    "skill": skill_name,
                    "severity": finding.get("severity"),
                    "description": finding.get("description"),
                    "file": finding.get("file"),
                    "line": finding.get("line"),
                }
            )

    consolidated_file = RESULTS_DIR / "consolidated_report.json"
    with open(consolidated_file, "w") as f:
        json.dump(consolidated, f, indent=2, default=str)

    print(f"\n{'=' * 60}")
    print("SCAN COMPLETE")
    print(f"{'=' * 60}")
    print(f"Total scanned: {consolidated['summary']['total_scanned']}")
    print(f"Errors: {consolidated['summary']['errors']}")
    print(f"High-risk skills: {consolidated['summary']['high_risk']}")
    print(f"Medium-risk skills: {consolidated['summary']['medium_risk']}")
    print(f"Clean skills: {consolidated['summary']['clean']}")
    print(
        f"\nRisk totals: HIGH={consolidated['risk_totals']['HIGH']} MEDIUM={consolidated['risk_totals']['MEDIUM']} LOW={consolidated['risk_totals']['LOW']} INFO={consolidated['risk_totals']['INFO']}"
    )
    print(f"\nResults saved to: {RESULTS_DIR}")
    print(f"Consolidated report: {consolidated_file}")

    return consolidated


if __name__ == "__main__":
    main()
