#!/usr/bin/env python3
"""build-index.py — Regenerate skills-index.json and description.md from current structure."""
import json, os, re, glob
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(BASE, "skills-index.json")
DESC = os.path.join(BASE, "description.md")

skill_files = sorted(glob.glob(os.path.join(BASE, "*/*/SKILL.md")))
skills = []
desc_lines = []
categories = {}

for sf in skill_files:
    rel = os.path.relpath(sf, BASE)
    cat_skill = rel.replace("/SKILL.md", "")
    parts = cat_skill.split("/", 1)
    category, skill_name = parts[0], parts[1] if len(parts) > 1 else ""
    
    desc = ""
    try:
        with open(sf, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("description:"):
                    desc = line.split("description:", 1)[1].strip().strip("'\"")
                    break
    except Exception:
        pass
    
    desc = re.sub(r'[\x00-\x1f\x7f\r]', '', desc).replace("\t", " ")
    
    skills.append({"name": skill_name, "category": category, "path": cat_skill, "description": desc[:300]})
    desc_lines.append(f"{cat_skill}/SKILL.md:description: {desc}")
    categories[category] = categories.get(category, 0) + 1

index = {
    "version": "1.0",
    "generated": datetime.now(timezone.utc).isoformat(),
    "categories": len(categories),
    "total_skills": len(skills),
    "category_list": [{"name": k, "count": v} for k, v in sorted(categories.items())],
    "skills": skills
}

with open(INDEX, "w", encoding="utf-8") as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

with open(DESC, "w", encoding="utf-8") as f:
    f.write("\n".join(desc_lines) + "\n")

print(f"✅ Index: {len(skills)} skills in {len(categories)} categories")
print(f"   {INDEX}")
print(f"   {DESC}")
