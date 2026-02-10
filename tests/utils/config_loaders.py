"""Config file loaders for testing.

Helpers to load and parse limits.toml, features.py, and response_config.json
for testing consistency across configuration files.

Usage:
    from tests.utils.config_loaders import (
        load_limits_toml, load_features_py, load_response_config
    )

    limits = load_limits_toml()
    features = load_features_py()
    response_config = load_response_config()
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

# tomllib is available in Python 3.11+, use tomli for earlier versions
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        import tomllib  # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LIMITS_TOML_PATH = (
    PROJECT_ROOT / "src" / "code_scalpel" / "capabilities" / "limits.toml"
)
FEATURES_PY_PATH = PROJECT_ROOT / "src" / "code_scalpel" / "licensing" / "features.py"
RESPONSE_CONFIG_PATH = PROJECT_ROOT / ".code-scalpel" / "response_config.json"


def load_limits_toml() -> Dict[str, Any]:
    """Load and parse limits.toml configuration.

    Returns:
        Dictionary with structure like:
        {
            "global": {"default_timeout_seconds": 120},
            "community": {
                "analyze_code": {"max_file_size_mb": 1},
                ...
            },
            "pro": {...},
            "enterprise": {...}
        }
    """
    if not LIMITS_TOML_PATH.exists():
        raise FileNotFoundError(f"limits.toml not found at {LIMITS_TOML_PATH}")

    with open(LIMITS_TOML_PATH, "rb") as f:
        return tomllib.load(f)


def load_response_config() -> Dict[str, Any]:
    """Load and parse response_config.json.

    Returns:
        Dictionary with response field filtering configuration.
    """
    if not RESPONSE_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"response_config.json not found at {RESPONSE_CONFIG_PATH}"
        )

    with open(RESPONSE_CONFIG_PATH, "r") as f:
        return json.load(f)


def get_all_tool_names() -> list[str]:
    """Extract all tool names from limits.toml.

    Returns:
        Sorted list of all 22 tool names.
    """
    limits = load_limits_toml()
    tools = set()

    # Tools appear under community/pro/enterprise sections
    for tier in ["community", "pro", "enterprise"]:
        if tier in limits:
            tools.update(limits[tier].keys())

    return sorted(tools)


def get_tier_limit(tool: str, tier: str, limit_key: str) -> Any:
    """Get a specific limit value for a tool at a tier.

    Args:
        tool: Tool name (e.g., "extract_code")
        tier: Tier name ("community", "pro", "enterprise")
        limit_key: Limit key (e.g., "max_depth", "max_files")

    Returns:
        The limit value, or None if omitted or -1 (indicating unlimited).
    """
    limits = load_limits_toml()

    if tier not in limits or tool not in limits[tier]:
        return None

    value = limits[tier][tool].get(limit_key)
    # Convert -1 sentinel to None (unlimited), matching features.py convention
    if isinstance(value, int) and value == -1:
        return None
    return value


def _convert_sentinel(value: Any) -> Any:
    """Convert -1 sentinel to None (unlimited), matching features.py convention."""
    if isinstance(value, int) and value == -1:
        return None
    return value


def get_all_tier_limits(tool: str) -> Dict[str, Dict[str, Any]]:
    """Get all limits for a tool across all tiers.

    Applies -1 -> None sentinel conversion on all numeric values.

    Returns:
        Dictionary with structure:
        {
            "community": {"max_depth": 3, ...},
            "pro": {"max_depth": 50, ...},
            "enterprise": {...}
        }
    """
    limits = load_limits_toml()
    result = {}

    for tier in ["community", "pro", "enterprise"]:
        if tier in limits and tool in limits[tier]:
            result[tier] = {
                k: _convert_sentinel(v) for k, v in limits[tier][tool].items()
            }
        else:
            result[tier] = {}

    return result


def verify_limits_toml_consistency() -> list[str]:
    """Verify internal consistency of limits.toml.

    Returns:
        List of consistency issues found (empty if all consistent).
    """
    limits = load_limits_toml()
    issues = []
    tools = get_all_tool_names()

    # Verify each tool has entries for at least one tier
    for tool in tools:
        has_any_tier = any(
            tool in limits.get(tier, {}) for tier in ["community", "pro", "enterprise"]
        )
        if not has_any_tier:
            issues.append(f"Tool '{tool}' has no tier definitions")

    # Verify tier hierarchy: Enterprise >= Pro >= Community
    # (limits should decrease as you go down tiers)
    numeric_limits = [
        ("max_depth", "depth"),
        ("max_files", "files"),
        ("max_nodes", "nodes"),
        ("max_modules", "modules"),
        ("max_references", "references"),
        ("max_context_lines", "context lines"),
    ]

    for tool in tools:
        tool_limits = get_all_tier_limits(tool)
        for limit_key, limit_name in numeric_limits:
            community_val = tool_limits.get("community", {}).get(limit_key)
            pro_val = tool_limits.get("pro", {}).get(limit_key)
            enterprise_val = tool_limits.get("enterprise", {}).get(limit_key)

            # Check that None (unlimited) only appears in pro/enterprise
            if community_val is None and pro_val is not None:
                # Community has no limit but Pro does - check if intentional
                pass

            # Check numeric progression
            if all(v is not None for v in [community_val, pro_val, enterprise_val]):
                if not (community_val <= pro_val <= enterprise_val):
                    issues.append(
                        f"Tool '{tool}' limit '{limit_key}': "
                        f"community={community_val}, pro={pro_val}, "
                        f"enterprise={enterprise_val} - not monotonic"
                    )

    return issues
