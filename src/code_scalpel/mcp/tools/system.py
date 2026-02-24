"""System and capability tools for Code Scalpel MCP server."""

from __future__ import annotations

import time
from mcp.server.fastmcp import Context

from code_scalpel.mcp.protocol import mcp, _get_current_tier
from code_scalpel.mcp.contract import ToolResponseEnvelope, ToolError, make_envelope
from code_scalpel.capabilities import (
    get_all_capabilities,
    get_tool_names,
    get_tier_names,
    get_tool_capabilities,
)
from code_scalpel import __version__ as _pkg_version


@mcp.tool(
    description="List all tools with tier limits. Pass tool_name='...' for full parameter docs and usage details."
)
async def get_capabilities(
    tier: str | None = None,
    tool_name: str | None = None,
    ctx: Context | None = None,
) -> ToolResponseEnvelope:
    """Get the capabilities available for the current license tier.

    Returns a complete list of all Code Scalpel tools and their availability/limits
    at the specified tier or current tier.

    When **tool_name** is provided, returns detailed documentation for that specific
    tool: the full docstring, JSON parameter schema, and per-tier limits for all
    three tiers (community / pro / enterprise).

    **Tier Behavior:**
    - Community: Returns capabilities for community tier (basic limits on all tools)
    - Pro: Returns capabilities for pro tier (expanded limits on most tools)
    - Enterprise: Returns capabilities for enterprise tier (no limits on core tools)

    **Args:**
        tier (str, optional): Tier to query. Default: current tier from license.
            Options: "community", "pro", "enterprise".
        tool_name (str, optional): If provided, return full docs for this specific
            tool instead of listing all tools.
        ctx (Context, optional): MCP context for progress reporting.

    **Returns without tool_name:**
        ToolResponseEnvelope containing:
        - tier (str): The tier that was queried
        - tool_count (int): Total number of tools
        - available_count (int): Number of tools available at this tier
        - capabilities (dict): Maps tool_id to capability info:
          - tool_id (str): The tool identifier
          - tier (str): The tier being described
          - available (bool): Whether tool is available at this tier
          - limits (dict): The limits applied at this tier

    **Returns with tool_name:**
        ToolResponseEnvelope containing:
        - tool_name (str): The tool queried
        - short_description (str): One-line description shown during tool listing
        - full_description (str): Full docstring with parameters and examples
        - parameters (dict): JSON schema for tool input parameters
        - tier_limits (dict): Per-tier availability and limits for community/pro/enterprise
    """
    started = time.perf_counter()
    current_tier = _get_current_tier()

    try:
        # Validate tier if provided
        resolved_tier = tier.lower() if tier else current_tier
        if tier and resolved_tier not in get_tier_names():
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

        # Per-tool detail mode: return full docs for a single tool
        if tool_name is not None:
            tool_obj = mcp._tool_manager.get_tool(tool_name)
            if tool_obj is None:
                error = ToolError(
                    error=(
                        f"Unknown tool: {tool_name!r}. "
                        "Call get_capabilities() without tool_name to list all available tools."
                    ),
                    error_code="not_found",
                    error_details={"available_tools": get_tool_names()},
                )
                return make_envelope(
                    data=None,
                    tool_id="get_capabilities",
                    tool_version=_pkg_version,
                    tier=current_tier,
                    duration_ms=int((time.perf_counter() - started) * 1000),
                    error=error,
                )

            # tool_obj.description = the short advertising string (sent at session init)
            # tool_obj.fn.__doc__  = the full docstring (available on demand)
            short_desc = tool_obj.description
            full_doc = getattr(tool_obj.fn, "__doc__", None) or tool_obj.description

            # Collect per-tier limits across all three tiers
            tier_limits: dict[str, dict] = {}
            for t in get_tier_names():
                try:
                    tier_limits[t] = get_tool_capabilities(tool_name, tier=t)
                except Exception:
                    tier_limits[t] = {"available": False, "limits": {}}

            result = {
                "tool_name": tool_name,
                "short_description": short_desc,
                "full_description": full_doc,
                "parameters": tool_obj.parameters,
                "tier_limits": tier_limits,
            }
            duration_ms = int((time.perf_counter() - started) * 1000)
            return make_envelope(
                data=result,
                tool_id="get_capabilities",
                tool_version=_pkg_version,
                tier=current_tier,
                duration_ms=duration_ms,
            )

        # All-tools listing mode
        capabilities = get_all_capabilities(tier=resolved_tier)
        available_count = sum(1 for c in capabilities.values() if c["available"])

        result = {
            "tier": resolved_tier,
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
