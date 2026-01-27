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
    """Get the capabilities available for the current license tier.

    This tool returns a complete list of all 22 Code Scalpel tools and their
    availability/limits at the specified tier or current tier.

    **Usage by Agents:**
    Agents can call this tool to discover:
    - Which tools are available at the current tier
    - The limits applied to each tool (max_files, max_depth, etc.)
    - Whether specific features are enabled

    **Tier Behavior:**
    - Community: All tools available with basic limits
    - Pro: 19 tools available with expanded limits
    - Enterprise: 10 tools available with no limits

    Args:
        tier: Optional tier to query (defaults to current tier from license)
              Must be one of: "community", "pro", "enterprise"
              If not specified, uses the tier from the current license.

    Returns:
        ToolResponseEnvelope containing:
        {
            "tier": "pro",
            "tool_count": 22,
            "available_count": 19,
            "capabilities": {
                "analyze_code": {
                    "tool_id": "analyze_code",
                    "tier": "pro",
                    "available": true,
                    "limits": {
                        "max_file_size_mb": 10,
                        "languages": ["python", "javascript", "typescript", "java"]
                    }
                },
                ...
            }
        }

    Example:
        ```
        # Get capabilities for current tier (from license)
        result = await get_capabilities()

        # Get capabilities for a specific tier (testing/downgrade only)
        result = await get_capabilities(tier="community")
        ```
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
