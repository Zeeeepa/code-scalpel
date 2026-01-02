#!/usr/bin/env python3
"""
Deployer Configuration Example

This script demonstrates how MCP server deployers can customize tier limits
without rebuilding the Python package.

[20251225_CONFIG] v3.3.0 - TOML-based configuration system
"""

import os
import sys
from pathlib import Path

# Add src to path for running directly
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from code_scalpel.licensing import (
    get_tool_capabilities,
    reload_config,
)


def show_current_limits():
    """Display current tier limits for key tools."""
    print("=" * 70)
    print("CURRENT TIER LIMITS")
    print("=" * 70)

    tools = ["extract_code", "security_scan", "crawl_project", "symbolic_execute"]
    tiers = ["community", "pro", "enterprise"]

    for tool in tools:
        print(f"\n{tool}:")
        print("-" * 70)
        for tier in tiers:
            caps = get_tool_capabilities(tool, tier)
            limits = caps.get("limits", {})
            print(f"  {tier.upper():12} {limits}")


def show_config_location():
    """Show where config is being loaded from."""
    print("\n" + "=" * 70)
    print("CONFIGURATION")
    print("=" * 70)

    env_file = os.environ.get("CODE_SCALPEL_LIMITS_FILE")
    if env_file:
        print(f"Environment: CODE_SCALPEL_LIMITS_FILE={env_file}")
    else:
        print("Environment: CODE_SCALPEL_LIMITS_FILE not set")

    # Show search locations
    candidates = [
        Path.cwd() / ".code-scalpel" / "limits.local.toml",
        Path.cwd() / ".code-scalpel" / "limits.toml",
        Path.home() / ".code-scalpel" / "limits.toml",
        Path("/etc/code-scalpel/limits.toml"),
    ]

    print("\nSearch locations (in priority order):")
    for i, path in enumerate(candidates, 1):
        exists = "✓" if path.exists() else "✗"
        print(f"  {i}. {exists} {path}")


def customize_example():
    """Show example of customizing limits."""
    print("\n" + "=" * 70)
    print("HOW TO CUSTOMIZE")
    print("=" * 70)

    print(
        """
1. Create or edit .code-scalpel/limits.toml:

   [pro.extract_code]
   max_depth = 5              # Increase from default 2
   max_extraction_size_mb = 20

   [community.security_scan]
   max_findings = 100         # Increase from default 50

2. For local development, create .code-scalpel/limits.local.toml:
   (This file is gitignored and takes precedence)

   [pro.extract_code]
   max_depth = 999           # Effectively unlimited for testing

3. Or set environment variable:

   export CODE_SCALPEL_LIMITS_FILE=/path/to/custom.toml

4. Changes take effect immediately - no rebuild or restart needed!

5. To verify your changes:

   python examples/deployer_config_example.py
"""
    )


def reload_example():
    """Show how to reload config at runtime."""
    print("\n" + "=" * 70)
    print("RUNTIME RELOAD")
    print("=" * 70)

    print("\nBefore reload:")
    caps = get_tool_capabilities("extract_code", "pro")
    print(f"  Pro max_depth: {caps['limits']['max_depth']}")

    print("\nReloading config from disk...")
    reload_config()

    print("\nAfter reload:")
    caps = get_tool_capabilities("extract_code", "pro")
    print(f"  Pro max_depth: {caps['limits']['max_depth']}")

    print(
        "\n(If you edited limits.toml between these calls, you'd see different values)"
    )


def main():
    """Run all examples."""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║         Code Scalpel - Deployer Configuration Example            ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")

    show_config_location()
    show_current_limits()
    customize_example()
    reload_example()

    print("\n" + "=" * 70)
    print("For more information, see:")
    print("  - docs/guides/developer_tier_controls.md")
    print("  - .code-scalpel/limits.toml (the actual config)")
    print("  - .code-scalpel/limits.local.toml.example (local overrides)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
