"""
Capability Resolver - Resolve tool capabilities by tier and license.

[20260127_FEATURE] Centralized capability resolution system for license-aware testing.

This module provides functions to query which capabilities are available at a given
tier by reading from the .code-scalpel/limits.toml configuration file.

USAGE:
    from code_scalpel.capabilities import get_tool_capabilities, get_all_capabilities

    # Get capabilities for a specific tool
    caps = get_tool_capabilities("analyze_code", tier="pro")
    print(caps)  # {'tool_id': 'analyze_code', 'tier': 'pro', 'available': True, 'limits': {...}}

    # Get all capabilities for a tier
    all_caps = get_all_capabilities(tier="enterprise")
    print(len(all_caps))  # 22 tools

DESIGN NOTES:
- limits.toml is the single source of truth
- Caching is essential for performance
- Environment override via CODE_SCALPEL_LIMITS_FILE for CI testing
- Handles missing tool/tier gracefully (available=False)
- No dependencies on licensing or tier detection (stateless resolver)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from threading import Lock

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python 3.10

logger = logging.getLogger(__name__)

# Global cache and lock for thread-safe access
_LIMITS_CACHE: Optional[Dict[str, Any]] = None
_CACHE_LOCK = Lock()

# All 22 tools in Code Scalpel (alphabetical order)
# Note: These are the tools registered in TOOL_CAPABILITIES
# (excludes oracle tools and special system tools)
ALL_TOOLS = [
    "analyze_code",
    "code_policy_check",
    "crawl_project",
    "cross_file_security_scan",
    "extract_code",
    "generate_unit_tests",
    "get_call_graph",
    "get_cross_file_dependencies",
    "get_file_context",
    "get_graph_neighborhood",
    "get_project_map",
    "get_symbol_references",
    "rename_symbol",
    "scan_dependencies",
    "security_scan",
    "simulate_refactor",
    "symbolic_execute",
    "type_evaporation_scan",
    "unified_sink_detect",
    "update_symbol",
    "validate_paths",
    "verify_policy_integrity",
]

# All tier names
TIERS = ["community", "pro", "enterprise"]


def _find_limits_file() -> Path:
    """
    Find the limits.toml file using the priority order.

    Priority:
    1. Environment: CODE_SCALPEL_LIMITS_FILE
    2. Project: .code-scalpel/limits.toml (relative to cwd or up the tree)
    3. User: ~/.code-scalpel/limits.toml
    4. System: /etc/code-scalpel/limits.toml

    Returns the path if found, otherwise raises FileNotFoundError.
    """
    # 1. Environment variable
    if env_path := os.environ.get("CODE_SCALPEL_LIMITS_FILE"):
        path = Path(env_path)
        if path.exists():
            logger.debug(f"Found limits.toml via CODE_SCALPEL_LIMITS_FILE: {path}")
            return path
        else:
            logger.warning(f"CODE_SCALPEL_LIMITS_FILE points to non-existent file: {path}")

    # 2. Project directory (search up tree or use current)
    project_path = Path.cwd() / ".code-scalpel" / "limits.toml"
    if project_path.exists():
        logger.debug(f"Found limits.toml in project: {project_path}")
        return project_path

    # Try from source directory (when module is installed)
    # Walk up from this file's location
    current_file = Path(__file__)
    for parent in current_file.parents:
        project_candidate = parent / ".code-scalpel" / "limits.toml"
        if project_candidate.exists():
            logger.debug(f"Found limits.toml via source tree search: {project_candidate}")
            return project_candidate

    # 3. User home directory
    user_path = Path.home() / ".code-scalpel" / "limits.toml"
    if user_path.exists():
        logger.debug(f"Found limits.toml in user home: {user_path}")
        return user_path

    # 4. System directory
    system_path = Path("/etc/code-scalpel/limits.toml")
    if system_path.exists():
        logger.debug(f"Found limits.toml in system: {system_path}")
        return system_path

    # Not found
    raise FileNotFoundError(
        "Could not find limits.toml in any of the expected locations:\n"
        f"  1. CODE_SCALPEL_LIMITS_FILE env var (currently: {os.environ.get('CODE_SCALPEL_LIMITS_FILE', 'not set')})\n"
        f"  2. .code-scalpel/limits.toml (project)\n"
        f"  3. ~/.code-scalpel/limits.toml (user)\n"
        f"  4. /etc/code-scalpel/limits.toml (system)\n"
        "\nPlease set CODE_SCALPEL_LIMITS_FILE or create .code-scalpel/limits.toml"
    )


def _load_limits_toml() -> Dict[str, Any]:
    """
    Load and parse the limits.toml file.

    Returns a dictionary with the parsed TOML content.
    Raises FileNotFoundError if limits.toml cannot be found.
    Raises tomllib.TOMLDecodeError if limits.toml is malformed.
    """
    limits_file = _find_limits_file()
    logger.debug(f"Loading limits.toml from: {limits_file}")

    try:
        with open(limits_file, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        logger.error(f"Failed to parse limits.toml: {e}")
        raise


def _clear_cache() -> None:
    """Clear the global limits cache."""
    global _LIMITS_CACHE
    with _CACHE_LOCK:
        _LIMITS_CACHE = None


def _get_cached_limits() -> Dict[str, Any]:
    """
    Get the cached limits dictionary, loading if necessary.

    Uses thread-safe caching to avoid re-parsing limits.toml on every call.
    """
    global _LIMITS_CACHE

    if _LIMITS_CACHE is not None:
        return _LIMITS_CACHE

    with _CACHE_LOCK:
        # Double-check after acquiring lock
        if _LIMITS_CACHE is not None:
            return _LIMITS_CACHE

        _LIMITS_CACHE = _load_limits_toml()
        return _LIMITS_CACHE


def get_tool_capabilities(tool_id: str, tier: str = "community") -> Dict[str, Any]:
    """
    Get the capabilities/limits for a specific tool at a specific tier.

    Args:
        tool_id: Tool identifier (e.g., "analyze_code")
        tier: Tier name ("community", "pro", "enterprise")

    Returns:
        Dictionary with structure:
        {
            "tool_id": "analyze_code",
            "tier": "pro",
            "available": True,
            "limits": {
                "max_file_size_mb": 10,
                "languages": ["python", "javascript", ...]
            }
        }

        If tool is not available at the tier, "available" is False and "limits" is empty.

    Example:
        >>> caps = get_tool_capabilities("analyze_code", tier="pro")
        >>> print(caps["available"])  # True
        >>> print(caps["limits"]["max_file_size_mb"])  # 10
    """
    # Normalize inputs
    tool_id_lower = tool_id.lower()
    tier_lower = tier.lower()

    # Validate tier
    if tier_lower not in TIERS:
        logger.warning(f"Invalid tier: {tier_lower}. Valid tiers: {TIERS}")
        tier_lower = "community"

    # Load limits from cache
    limits = _get_cached_limits()

    # Look for limits[tier][tool_id] (nested dict structure)
    tier_limits = limits.get(tier_lower, {})
    tool_limits = tier_limits.get(tool_id_lower, {})

    # Return capability envelope
    return {
        "tool_id": tool_id_lower,
        "tier": tier_lower,
        "available": bool(tool_limits),  # Available if section exists
        "limits": tool_limits if tool_limits else {},
    }


def get_all_capabilities(tier: str = "community") -> Dict[str, Dict[str, Any]]:
    """
    Get all capabilities for all 22 tools at a specific tier.

    Args:
        tier: Tier name ("community", "pro", "enterprise")

    Returns:
        Dictionary mapping tool_id -> capability dict for that tool at the tier.

        {
            "analyze_code": {
                "tool_id": "analyze_code",
                "tier": "pro",
                "available": True,
                "limits": {...}
            },
            "get_file_context": {
                "tool_id": "get_file_context",
                "tier": "pro",
                "available": True,
                "limits": {...}
            },
            ...
        }

    Example:
        >>> all_caps = get_all_capabilities(tier="pro")
        >>> print(len(all_caps))  # 22
        >>> print(all_caps["analyze_code"]["available"])  # True
    """
    return {tool: get_tool_capabilities(tool, tier) for tool in ALL_TOOLS}


def get_tool_names() -> list[str]:
    """Get the list of all 22 tool names."""
    return ALL_TOOLS.copy()


def get_tier_names() -> list[str]:
    """Get the list of all supported tier names."""
    return TIERS.copy()


def validate_tier(tier: str) -> bool:
    """Check if a tier name is valid."""
    return tier.lower() in TIERS


def reload_limits_cache() -> None:
    """
    Force reload of the limits.toml file.

    Useful in tests or when limits.toml is modified at runtime.
    """
    _clear_cache()
    _get_cached_limits()  # Reload
    logger.info("Limits cache reloaded")
