"""Generate simple test specs from docs/roadmap/*.md.

This extracts Tool Name, Primary Module, and Tier Availability and writes
one JSON spec per roadmap file to test-harness/specs/.
"""

import json
from pathlib import Path
import re
import datetime

ROOT = Path(__file__).resolve().parents[1]
ROADMAP = ROOT / "docs" / "roadmap"
OUT = ROOT / "test-harness" / "specs"
OUT.mkdir(parents=True, exist_ok=True)


def extract_fields(text: str) -> dict:
    fields = {}
    # Tool Name
    m = re.search(r"\*\*Tool Name:\*\*\s*`(?P<name>[^`]+)`", text)
    if m:
        fields["name"] = m.group("name").strip()
    else:
        # fallback to header
        m2 = re.search(r"#\s*(?P<h>[^\n]+) Tool Roadmap", text)
        if m2:
            fields["name"] = m2.group("h").strip()

    # Primary Module
    m = re.search(r"\*\*Primary Module:\*\*\s*`(?P<module>[^`]+)`", text)
    if m:
        fields["primary_module"] = m.group("module").strip()

    # Tier Availability
    m = re.search(r"\*\*Tier Availability:\*\*\s*(?P<t>[^\n]+)", text)
    if m:
        fields["tier_availability"] = m.group("t").strip()

    # Simple description first paragraph after Overview
    m = re.search(r"## Overview\n\n(?P<ov>.+?)\n\n", text, re.S)
    if m:
        fields["overview"] = " ".join(m.group("ov").splitlines()).strip()

    return fields


def main():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    specs = []
    for md in sorted(ROADMAP.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        data = extract_fields(text)
        if "name" not in data:
            # fallback to filename
            data["name"] = md.stem
        spec = {
            "tool": data.get("name"),
            "primary_module": data.get("primary_module"),
            "tier_availability": data.get("tier_availability"),
            "overview": data.get("overview"),
            "generated_at": now,
            "tests": {
                "happy_path": {"note": "Auto-generated; fill in params as needed"},
                "edge_cases": [],
                "invalid_inputs": [],
            },
        }
        outp = OUT / f"{md.stem}.json"
        outp.write_text(json.dumps(spec, indent=2), encoding="utf-8")
        specs.append(spec)

    print(f"Generated {len(specs)} specs to {OUT}")


if __name__ == "__main__":
    main()
