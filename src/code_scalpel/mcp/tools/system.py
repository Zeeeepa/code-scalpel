"""System and capability tools for Code Scalpel MCP server.

[20260127_FEATURE] Add get_capabilities() tool to expose tier-aware capabilities.
"""

from __future__ import annotations

import time
from mcp.server.fastmcp import Context

from code_scalpel.mcp.protocol import mcp, _get_current_tier
from code_scalpel.mcp.contract import ToolResponseEnvelope, ToolError, make_envelope
from code_scalpel.capabilities import (
    get_all_capabilities,
    get_tool_names,
    get_tier_names,
)
from code_scalpel import __version__ as _pkg_version


@mcp.tool()
async def get_capabilities(
    tier: str | None = None,
    ctx: Context | None = None,
) -> ToolResponseEnvelope:
    """
    Get the capabilities available for the current license tier.

    Returns a complete list of all Code Scalpel tools and their availability/limits at the specified tier or current tier.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Provides information about capabilities available at different tiers.

    **Tier Capabilities:**
    - **Community:** Returns capabilities for community tier (basic limits on all tools)
    - **Pro:** Returns capabilities for pro tier (expanded limits on most tools)
    - **Enterprise:** Returns capabilities for enterprise tier (no limits on core tools)

    **Args:**
    - tier (str, optional): Tier to query (defaults to current tier from license). Must be one of: "community", "pro", "enterprise"

    **Returns:**
    - ToolResponseEnvelope: Standardized MCP response envelope containing:
      - data (dict): Capabilities information with:
        - tier (str): The tier that was queried
        - tool_count (int): Total number of tools
        - available_count (int): Number of tools available at this tier
        - capabilities (dict): Dictionary mapping tool_id -> capability info for each tool:
          - tool_id (str): The tool identifier
          - tier (str): The tier being described
          - available (bool): Whether the tool is available at this tier
          - limits (dict): The limits applied to this tool at this tier
      - tier (str, optional): Applied tier ("community", "pro", "enterprise")
      - error (ToolError, optional): Standardized error if operation failed
      - warnings (list[str]): Non-fatal warnings from MCP boundary
    """
    started = time.perf_counter()
    current_tier = _get_current_tier()

    try:
        # Use provided tier or current tier from license
        if tier is None:
            tier = current_tier
        else:
            tier = tier.lower()
            if tier not in get_tier_names():
                error = ToolError(
                    error=f"Invalid tier: {tier}. Must be one of {get_tier_names()}",
                    error_code="invalid_argument",
                    error_details={"available_tiers": get_tier_names()},
                )
                return make_envelope(
                    data=None,
                    tool_id="get_capabilities",
                    tool_version=_pkg_version,
                    tier=current_tier,
                    duration_ms=int((time.perf_counter() - started) * 1000),
                    error=error,
                )

        # Get capabilities for the tier
        capabilities = get_all_capabilities(tier=tier)

        # Build response
        available_count = sum(1 for c in capabilities.values() if c["available"])

        result = {
            "tier": tier,
            "tool_count": len(capabilities),
            "available_count": available_count,
            "capabilities": capabilities,
        }

        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="get_capabilities",
            tool_version=_pkg_version,
            tier=current_tier,
            duration_ms=duration_ms,
        )

    except Exception as e:
        duration_ms = int((time.perf_counter() - started) * 1000)
        error = ToolError(
            error=f"Failed to get capabilities: {str(e)}",
            error_code="internal_error",
        )
        return make_envelope(
            data=None,
            tool_id="get_capabilities",
            tool_version=_pkg_version,
            tier=current_tier,
            duration_ms=duration_ms,
            error=error,
        )


# Re-export get_tool_names and get_tier_names for introspection
__all__ = ["get_capabilities", "get_tool_names", "get_tier_names"]
