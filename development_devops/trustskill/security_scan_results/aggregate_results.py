#!/usr/bin/env python3
"""Aggregate security scan results from all skills."""

import json
import os
from collections import defaultdict
from datetime import datetime

RESULTS_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_TO_AGGREGATE = [
    "aliyun-oss-upload",
    "asdasd",
    "banshee-s-last-cry",
    "barkpush",
    "bring-shopping-list",
    "bring",
    "case-record-socialwork",
    "cma-email",
    "d4-world-boss",
    "data-viz",
    "deepdub-tts",
    "enzoldhazam",
    "grazy",
    "host-ping-detect",
    "imap-email",
    "imap-smtp-email",
    "instagram-reels",
    "intodns",
    "katok",
    "localsend",
    "mfa-word",
    "notectl",
    "pandic-office",
    "political-struggle",
    "pptx-pdf-font-fix",
    "printer",
    "probar",
    "sarvam",
    "say-xiaoai",
    "searxng-local",
    "searxng-metasearch",
    "searxng-self-hosted",
    "signal-cli",
    "sparkle-vpn",
    "tamil-whatsapp",
    "tt",
    "variflight-aviation",
    "webpage-screenshot",
    "wechat-article-search",
    "whats",
    "whispers-from-the-star-cn",
    "win-mouse-native",
    "winamp",
    "x-trends",
    "xuezh",
    "yoebao-bazi",
    "yoebao-yao",
    "youtube-shorts",
    "zotero-sholar",
]


def load_result(skill_name):
    filepath = os.path.join(RESULTS_DIR, f"{skill_name}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return None


def aggregate_results():
    aggregated = {
        "scan_metadata": {
            "generated_at": datetime.now().isoformat(),
            "skills_scanned": 0,
            "total_files_scanned": 0,
            "total_findings": 0,
        },
        "severity_summary": {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "INFO": 0,
        },
        "category_breakdown": defaultdict(lambda: {"count": 0, "skills": []}),
        "skills_by_risk": {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "safe": [],
        },
        "detailed_findings": {"CRITICAL": [], "HIGH": [], "MEDIUM": []},
        "skill_summaries": [],
    }

    for skill_name in SKILLS_TO_AGGREGATE:
        result = load_result(skill_name)
        if not result:
            continue

        aggregated["scan_metadata"]["skills_scanned"] += 1
        aggregated["scan_metadata"]["total_files_scanned"] += result.get(
            "files_scanned", 0
        )

        risk_summary = result.get("risk_summary", {})
        total_findings = sum(risk_summary.values())
        aggregated["scan_metadata"]["total_findings"] += total_findings

        for severity, count in risk_summary.items():
            aggregated["severity_summary"][severity] += count

        assessment = result.get("security_assessment", "")
        skill_summary = {
            "skill": skill_name,
            "files_scanned": result.get("files_scanned", 0),
            "risk_summary": risk_summary,
            "assessment": assessment,
            "scan_time": result.get("scan_time", 0),
        }
        aggregated["skill_summaries"].append(skill_summary)

        if "CRITICAL" in assessment:
            aggregated["skills_by_risk"]["critical"].append(skill_name)
        elif risk_summary.get("HIGH", 0) > 0:
            aggregated["skills_by_risk"]["high"].append(skill_name)
        elif risk_summary.get("MEDIUM", 0) > 0:
            aggregated["skills_by_risk"]["medium"].append(skill_name)
        elif risk_summary.get("LOW", 0) > 0:
            aggregated["skills_by_risk"]["low"].append(skill_name)
        else:
            aggregated["skills_by_risk"]["safe"].append(skill_name)

        for finding in result.get("findings", []):
            level = finding.get("level", "INFO")
            category = finding.get("category", "unknown")

            cat_data = aggregated["category_breakdown"][category]
            cat_data["count"] += 1
            if skill_name not in cat_data["skills"]:
                cat_data["skills"].append(skill_name)

            if level in ["CRITICAL", "HIGH", "MEDIUM"]:
                aggregated["detailed_findings"][level].append(
                    {
                        "skill": skill_name,
                        "category": category,
                        "description": finding.get("description", ""),
                        "file": finding.get("file", ""),
                        "line": finding.get("line", 0),
                        "confidence": finding.get("confidence", 0),
                    }
                )

    aggregated["category_breakdown"] = dict(aggregated["category_breakdown"])
    return aggregated


def generate_markdown_report(aggregated):
    lines = [
        "# Security Scan Report - Deep Analysis",
        "",
        f"**Generated:** {aggregated['scan_metadata']['generated_at']}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Skills Scanned | {aggregated['scan_metadata']['skills_scanned']} |",
        f"| Total Files Analyzed | {aggregated['scan_metadata']['total_files_scanned']} |",
        f"| Total Findings | {aggregated['scan_metadata']['total_findings']} |",
        "",
        "### Severity Distribution",
        "",
        f"| Severity | Count |",
        f"|----------|-------|",
    ]

    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        count = aggregated["severity_summary"].get(sev, 0)
        icon = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🟢",
            "INFO": "ℹ️",
        }.get(sev, "")
        lines.append(f"| {icon} {sev} | {count} |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Skills by Risk Level",
            "",
            f"### 🔴 Critical Risk ({len(aggregated['skills_by_risk']['critical'])} skills)",
            "",
        ]
    )

    for skill in sorted(aggregated["skills_by_risk"]["critical"]):
        lines.append(f"- `{skill}`")

    lines.extend(
        [
            "",
            f"### 🟠 High Risk ({len(aggregated['skills_by_risk']['high'])} skills)",
            "",
        ]
    )

    for skill in sorted(aggregated["skills_by_risk"]["high"]):
        lines.append(f"- `{skill}`")

    lines.extend(
        [
            "",
            f"### 🟡 Medium Risk ({len(aggregated['skills_by_risk']['medium'])} skills)",
            "",
        ]
    )

    for skill in sorted(aggregated["skills_by_risk"]["medium"]):
        lines.append(f"- `{skill}`")

    lines.extend(
        [
            "",
            f"### 🟢 Low Risk ({len(aggregated['skills_by_risk']['low'])} skills)",
            "",
        ]
    )

    for skill in sorted(aggregated["skills_by_risk"]["low"]):
        lines.append(f"- `{skill}`")

    lines.extend(
        [
            "",
            f"### ✅ Safe ({len(aggregated['skills_by_risk']['safe'])} skills)",
            "",
        ]
    )

    for skill in sorted(aggregated["skills_by_risk"]["safe"]):
        lines.append(f"- `{skill}`")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Category Breakdown",
            "",
            "| Category | Count | Affected Skills |",
            "|----------|-------|-----------------|",
        ]
    )

    sorted_categories = sorted(
        aggregated["category_breakdown"].items(),
        key=lambda x: x[1]["count"],
        reverse=True,
    )
    for category, data in sorted_categories:
        skills_str = ", ".join(data["skills"][:3])
        if len(data["skills"]) > 3:
            skills_str += f" (+{len(data['skills']) - 3} more)"
        lines.append(f"| {category} | {data['count']} | {skills_str} |")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Detailed High-Priority Findings",
            "",
        ]
    )

    if aggregated["detailed_findings"]["HIGH"]:
        lines.append("### 🔴 HIGH Severity Issues")
        lines.append("")
        for finding in aggregated["detailed_findings"]["HIGH"][:50]:
            lines.append(
                f"- **{finding['skill']}** `{finding['file']}:{finding['line']}`"
            )
            lines.append(f"  - Category: `{finding['category']}`")
            lines.append(f"  - Description: {finding['description']}")
            lines.append(f"  - Confidence: {finding['confidence']:.2%}")
            lines.append("")

    if aggregated["detailed_findings"]["MEDIUM"]:
        lines.append("### 🟡 MEDIUM Severity Issues (Top 20)")
        lines.append("")
        for finding in aggregated["detailed_findings"]["MEDIUM"][:20]:
            lines.append(
                f"- **{finding['skill']}** `{finding['file']}:{finding['line']}`"
            )
            lines.append(
                f"  - Category: `{finding['category']}` - {finding['description']}"
            )
            lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Recommendations",
            "",
            "1. **Immediate Action Required**: Review skills with HIGH severity findings",
            "2. **Medium Priority**: Investigate MEDIUM severity issues in context",
            "3. **False Positive Review**: Many `hardcoded_secret` findings in `package-lock.json` are likely integrity hashes (safe)",
            "4. **Environment Access**: `dotenv` usage is typically safe for configuration management",
            "",
            "---",
            "",
            "*Report generated by TrustSkill v3.0*",
        ]
    )

    return "\n".join(lines)


if __name__ == "__main__":
    aggregated = aggregate_results()

    with open(os.path.join(RESULTS_DIR, "AGGREGATED_REPORT.json"), "w") as f:
        json.dump(aggregated, f, indent=2)

    markdown = generate_markdown_report(aggregated)
    with open(os.path.join(RESULTS_DIR, "AGGREGATED_REPORT.md"), "w") as f:
        f.write(markdown)

    print(f"✓ Processed {aggregated['scan_metadata']['skills_scanned']} skills")
    print(f"✓ Total findings: {aggregated['scan_metadata']['total_findings']}")
    print(
        f"✓ HIGH: {aggregated['severity_summary']['HIGH']}, MEDIUM: {aggregated['severity_summary']['MEDIUM']}, LOW: {aggregated['severity_summary']['LOW']}"
    )
    print(f"✓ Reports saved to AGGREGATED_REPORT.json and AGGREGATED_REPORT.md")
