"""
Assertion helpers for tier-aware testing.

Provides helpers to assert:
- Tool availability
- Capability presence
- Limit values
- Tier detection
"""

from __future__ import annotations

from pathlib import Path

from code_scalpel.capabilities.resolver import (
    get_all_capabilities,
    get_tool_capabilities,
)
from code_scalpel.licensing.features import TOOL_CAPABILITIES
from code_scalpel.mcp.server import _get_current_tier


def assert_tool_available(tool_id: str, tier: str = "community") -> None:
    """Assert that a tool is available in the specified tier.

    Args:
        tool_id: The tool ID to check
        tier: The tier to check (defaults to 'community')

    Raises:
        AssertionError: If tool is not available in tier
    """
    capabilities = get_all_capabilities(tier)
    cap = capabilities.get(tool_id, {})
    if not cap.get("available", False):
        locked_tools = {
            tid for tid, c in capabilities.items() if not c.get("available", False)
        }
        raise AssertionError(
            f"Tool '{tool_id}' is not available in {tier} tier. "
            f"Locked tools: {sorted(locked_tools)}"
        )


def assert_tool_unavailable(tool_id: str, tier: str = "community") -> None:
    """Assert that a tool is locked/unavailable in the specified tier.

    Args:
        tool_id: The tool ID to check
        tier: The tier to check

    Raises:
        AssertionError: If tool is available
    """
    capabilities = get_all_capabilities(tier)
    cap = capabilities.get(tool_id, {})
    if cap.get("available", False):
        raise AssertionError(
            f"Tool '{tool_id}' is available in {tier} tier, "
            f"but expected it to be locked"
        )


def assert_capability_present(
    tool_id: str, capability: str, tier: str = "community"
) -> None:
    """Assert that a capability is present for a tool in a tier.

    Args:
        tool_id: The tool ID
        capability: The capability name
        tier: The tier to check

    Raises:
        AssertionError: If capability is not present
    """
    if tool_id not in TOOL_CAPABILITIES:
        raise AssertionError(f"Unknown tool: {tool_id}")

    tool_cap = TOOL_CAPABILITIES[tool_id]
    # The structure has tier names as direct keys, not nested under 'tiers'
    tier_cap = tool_cap.get(tier, {})
    capabilities_str = tier_cap.get("capabilities", "")

    # Capabilities are stored as a string representation of a set
    # We need to parse them
    if isinstance(capabilities_str, str):
        # Parse the string representation of set
        try:
            # Use ast.literal_eval to safely parse the string
            import ast

            capabilities = ast.literal_eval(capabilities_str)
            if not isinstance(capabilities, set):
                capabilities = set(capabilities_str.split())
        except (ValueError, SyntaxError):
            capabilities = set()
    else:
        capabilities = set(capabilities_str) if capabilities_str else set()

    if capability not in capabilities:
        raise AssertionError(
            f"Capability '{capability}' not present for tool '{tool_id}' "
            f"in {tier} tier. Available: {sorted(capabilities)}"
        )


def assert_limit_value(
    tool_id: str, limit_name: str, expected_value: int | float, tier: str = "community"
) -> None:
    """Assert that a limit has a specific value.

    Args:
        tool_id: The tool ID
        limit_name: The limit name (e.g., 'max_lines')
        expected_value: The expected limit value
        tier: The tier to check

    Raises:
        AssertionError: If limit doesn't match
    """
    cap = get_tool_capabilities(tool_id, tier)
    limits = cap.get("limits", {})
    actual_value = limits.get(limit_name)

    if actual_value != expected_value:
        raise AssertionError(
            f"Limit '{limit_name}' for tool '{tool_id}' in {tier} tier "
            f"is {actual_value}, expected {expected_value}"
        )


def assert_limits_present(
    tool_id: str, expected_limits: set[str], tier: str = "community"
) -> None:
    """Assert that expected limits are defined for a tool.

    Args:
        tool_id: The tool ID
        expected_limits: Set of limit names that should be present
        tier: The tier to check

    Raises:
        AssertionError: If any expected limit is missing
    """
    cap = get_tool_capabilities(tool_id, tier)
    limits = cap.get("limits", {})
    limit_keys = set(limits.keys())

    missing = expected_limits - limit_keys
    if missing:
        raise AssertionError(
            f"Tool '{tool_id}' in {tier} tier missing limits: {sorted(missing)}"
        )


def assert_all_capabilities(
    tool_id: str,
    expected_capabilities: set[str],
    tier: str = "community",
) -> None:
    """Assert that all expected capabilities are present.

    Args:
        tool_id: The tool ID
        expected_capabilities: Set of capability names
        tier: The tier to check

    Raises:
        AssertionError: If any expected capability is missing
    """
    if tool_id not in TOOL_CAPABILITIES:
        raise AssertionError(f"Unknown tool: {tool_id}")

    tool_cap = TOOL_CAPABILITIES[tool_id]
    tiers = tool_cap.get("tiers", {})
    tier_cap = tiers.get(tier, {})
    actual_capabilities = set(tier_cap.get("capabilities", []))

    missing = expected_capabilities - actual_capabilities
    if missing:
        raise AssertionError(
            f"Tool '{tool_id}' in {tier} tier missing capabilities: "
            f"{sorted(missing)}. Available: {sorted(actual_capabilities)}"
        )


def assert_tier_detected(license_path: str | Path | None, expected_tier: str) -> None:
    """Assert that a license is detected as the expected tier.

    Args:
        license_path: Path to license file (or None for community)
        expected_tier: The expected tier

    Raises:
        AssertionError: If detected tier doesn't match
    """
    import os
    from code_scalpel.licensing import config_loader, jwt_validator

    # Save original state
    original_path = os.environ.get("CODE_SCALPEL_LICENSE_PATH")

    try:
        # Clear caches and set license
        jwt_validator._LICENSE_VALIDATION_CACHE = None
        config_loader.clear_cache()

        if license_path is None:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
        else:
            os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(license_path)

        # Detect tier
        detected_tier = _get_current_tier()

        if detected_tier != expected_tier:
            raise AssertionError(
                f"Tier detected as '{detected_tier}', expected '{expected_tier}'"
            )
    finally:
        # Restore original state
        if original_path is None:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
        else:
            os.environ["CODE_SCALPEL_LICENSE_PATH"] = original_path

        # Clear caches again
        jwt_validator._LICENSE_VALIDATION_CACHE = None
        config_loader.clear_cache()


def assert_tool_count(tier: str, expected_count: int, message: str = "") -> None:
    """Assert that a tier has a specific number of available tools.

    Args:
        tier: The tier to check
        expected_count: Expected number of available tools
        message: Optional assertion message

    Raises:
        AssertionError: If tool count doesn't match
    """
    capabilities = get_all_capabilities(tier)
    available_tools = {
        tool_id for tool_id, cap in capabilities.items() if cap.get("available", False)
    }
    actual_count = len(available_tools)

    if actual_count != expected_count:
        error_msg = (
            f"{tier} tier has {actual_count} available tools, expected {expected_count}"
        )
        if message:
            error_msg = f"{message}: {error_msg}"
        raise AssertionError(error_msg)
