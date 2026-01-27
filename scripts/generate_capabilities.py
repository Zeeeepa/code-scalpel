#!/usr/bin/env python3
"""
Generate golden capability JSON files from limits.toml

[20260127_FEATURE] Generates capabilities/free.json, pro.json, enterprise.json
from the resolver.

Usage:
    python3 scripts/generate_capabilities.py

This creates the golden files used for regression testing.
"""

import json
from datetime import datetime
from pathlib import Path

# Import from the capabilities module
from code_scalpel.capabilities import (
    get_all_capabilities,
    get_json_schema,
)


def generate_capability_files():
    """Generate golden capability JSON files for all tiers."""

    # Use canonical tier names (free instead of community for golden file)
    tier_mapping = {
        "community": "free",
        "pro": "pro",
        "enterprise": "enterprise",
    }

    output_dir = Path(__file__).parent.parent / "capabilities"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating golden capability files in {output_dir}...")

    # Generate for each tier
    for tier_name in ["community", "pro", "enterprise"]:
        caps = get_all_capabilities(tier=tier_name)
        filename = tier_mapping[tier_name]

        # Build capability envelope
        envelope = {
            "tier": tier_name,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "tool_count": len(caps),
            "available_count": sum(1 for c in caps.values() if c["available"]),
            "capabilities": caps,
        }

        # Write JSON file
        output_file = output_dir / f"{filename}.json"
        with open(output_file, "w") as f:
            json.dump(envelope, f, indent=2)

        print(
            f"✓ {output_file} ({len(caps)} tools, {envelope['available_count']} available)"
        )

    # Generate schema file
    schema_file = output_dir / "schema.json"
    with open(schema_file, "w") as f:
        json.dump(get_json_schema(), f, indent=2)
    print(f"✓ {schema_file}")

    print("\nDone!")


if __name__ == "__main__":
    generate_capability_files()
