"""Graph MCP tool registrations.

[20260121_REFACTOR] Wrap outputs in ToolResponseEnvelope for MCP contract
consistency (tier metadata, duration, standardized errors).
"""

from __future__ import annotations

import asyncio
from typing import Any

from code_scalpel.mcp.contract import ToolResponseEnvelope, envelop_tool_function

from mcp.server.fastmcp import Context

from code_scalpel.licensing.features import get_tool_capabilities, has_capability
from code_scalpel.mcp.helpers.graph_helpers import (
    _cross_file_security_scan_sync,
    _get_call_graph_sync,
    _get_cross_file_dependencies_sync,
    _get_graph_neighborhood_sync,
    _get_project_map_sync,
)
from code_scalpel.mcp.protocol import mcp
from code_scalpel import __version__ as _pkg_version
from code_scalpel.mcp.protocol import _get_current_tier as _tier_getter


def _get_current_tier() -> str:
    """Get current tier using JWT validation (late import to avoid circular dependency)."""
    from code_scalpel.mcp.server import _get_current_tier as get_tier

    return get_tier()


async def _get_call_graph_tool(
    project_root: str | None = None,
    entry_point: str | None = None,
    depth: int = 10,
    include_circular_import_check: bool = True,
    paths_from: str | None = None,
    paths_to: str | None = None,
    focus_functions: list[str] | None = None,
    ctx: Context | None = None,
) -> Any:
    """
    Build a call graph showing function relationships in the project.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.

    **Tier Capabilities:**
    - Community: Max depth 3, max nodes 50
    - Pro: Max depth 50, max nodes 500
    - Enterprise: Unlimited depth and nodes

    **Advanced Features:**
    - **Path Queries:** Use paths_from and paths_to to find all call paths between functions
    - **Focus Mode:** Use focus_functions to extract a subgraph centered on specific functions
    - **Call Context:** Each edge includes context (in_loop, in_try_block, in_conditional)
    - **Confidence Scoring:** Each edge includes confidence (1.0=static, 0.8=type_hint, 0.5=inferred)
    - **Source URIs:** Each node includes source_uri for IDE click-through (file:///path#L42)

    Args:
        project_root: Project root directory (default: server's project root)
        entry_point: Starting function name (e.g., "main" or "app.py:main")
                    If None, includes all functions
        depth: Maximum depth to traverse from entry point (default: 10)
        include_circular_import_check: Check for circular imports (default: True)
        paths_from: Source function for path query (e.g., "routes.py:handle_request")
        paths_to: Sink function for path query (e.g., "db.py:execute_query")
        focus_functions: List of functions to focus the subgraph on

    Returns:
        CallGraphResultModel with nodes, edges, Mermaid diagram, paths, and any circular imports
    """
    # [20251220_FEATURE] v3.0.5 - Progress reporting
    if ctx:
        await ctx.report_progress(0, 100, "Building call graph...")

    # [20251225_FEATURE] Capability-driven tier behavior (no upgrade hints)
    tier = _get_current_tier()
    caps = get_tool_capabilities("get_call_graph", tier) or {}
    limits = caps.get("limits", {}) or {}
    cap_set = set(caps.get("capabilities", []) or [])

    max_depth = limits.get("max_depth")
    max_nodes = limits.get("max_nodes")

    # [20260120_FIX] Ensure limits are integers (TOML values should be int, but ensure type safety)
    if max_depth is not None:
        max_depth = int(max_depth)
    if max_nodes is not None:
        max_nodes = int(max_nodes)

    actual_depth = depth
    if max_depth is not None and depth > max_depth:
        actual_depth = max_depth

    # [20260121_BUGFIX] Enable tier-driven advanced resolution and enterprise metrics
    advanced_resolution = "advanced_call_graph" in cap_set
    include_enterprise_metrics = bool(
        {"hot_path_identification", "dead_code_detection", "custom_graph_analysis"}
        & cap_set
    )

    # [20260120_FEATURE] Call sync function with tier/capabilities for metadata transparency
    result = await asyncio.to_thread(
        _get_call_graph_sync,
        project_root,
        entry_point,
        actual_depth,
        include_circular_import_check,
        max_nodes,
        advanced_resolution,
        include_enterprise_metrics,
        paths_from,
        paths_to,
        focus_functions,
        tier,
        caps,
    )

    # [20260120_FEATURE] Metadata already populated by sync function with tier/caps
    if ctx:
        node_count = len(result.nodes) if result.nodes else 0
        edge_count = len(result.edges) if result.edges else 0
        await ctx.report_progress(
            100,
            100,
            f"Call graph complete: {node_count} functions, {edge_count} calls",
        )

    return result


get_call_graph = mcp.tool()(
    envelop_tool_function(
        _get_call_graph_tool,
        tool_id="get_call_graph",
        tool_version=_pkg_version,
        tier_getter=_tier_getter,
    )
)


async def _get_graph_neighborhood_tool(
    center_node_id: str,
    k: int = 2,
    max_nodes: int = 100,
    direction: str = "both",
    min_confidence: float = 0.0,
    project_root: str | None = None,
    query: str | None = None,
) -> Any:
    """
    Extract k-hop neighborhood subgraph around a center node.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.

    **Tier Capabilities:**
    - Community: Max k=1, max nodes=20
    - Pro: Max k=5, max nodes=100
    - Enterprise: Unlimited k and nodes

    Args:
        center_node_id: ID of the center node (format: language::module::type::name)
        k: Maximum hops from center (default: 2)
        max_nodes: Maximum nodes to include (default: 100)
        direction: "outgoing", "incoming", or "both" (default: "both")
        min_confidence: Minimum edge confidence to follow (default: 0.0)
        project_root: Project root directory (default: server's project root)
        query: Graph query language (Enterprise tier only)

    Returns:
        GraphNeighborhoodResult with subgraph, truncation info, and Mermaid diagram
    """
    return await asyncio.to_thread(
        _get_graph_neighborhood_sync,
        center_node_id,
        k,
        max_nodes,
        direction,
        min_confidence,
        project_root,
        query,
    )


get_graph_neighborhood = mcp.tool()(
    envelop_tool_function(
        _get_graph_neighborhood_tool,
        tool_id="get_graph_neighborhood",
        tool_version=_pkg_version,
        tier_getter=_tier_getter,
    )
)


async def _get_project_map_tool(
    project_root: str | None = None,
    include_complexity: bool = True,
    complexity_threshold: int = 10,
    include_circular_check: bool = True,
    detect_service_boundaries: bool = False,
    min_isolation_score: float = 0.6,
    ctx: Context | None = None,
) -> Any:
    """
    Generate a comprehensive map of the project structure.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.

    **Tier Capabilities:**
    - Community: Up to 100 files, 50 modules, basic detail level
    - Pro: Up to 1000 files, 200 modules, detailed level
    - Enterprise: Unlimited files, 1000 modules, comprehensive detail level

    Args:
        project_root: Project root directory (default: server's project root)
        include_complexity: Calculate cyclomatic complexity (default: True)
        complexity_threshold: Threshold for flagging hotspots (default: 10)
        include_circular_check: Check for circular imports (default: True)

    Returns:
        ProjectMapResult with comprehensive project overview
    """
    # [20251220_FEATURE] v3.0.5 - Progress reporting
    if ctx:
        await ctx.report_progress(0, 100, "Scanning project structure...")

    tier = _get_current_tier()
    caps = get_tool_capabilities("get_project_map", tier) or {}
    limits = caps.get("limits", {}) or {}

    result = await asyncio.to_thread(
        _get_project_map_sync,
        project_root,
        include_complexity,
        complexity_threshold,
        include_circular_check,
        tier=tier,
        capabilities=caps,
        max_files_limit=limits.get("max_files"),
        max_modules_limit=limits.get("max_modules"),
    )

    # Enterprise feature: suggest service boundaries (not a standalone MCP tool).
    if detect_service_boundaries:
        if not has_capability("extract_code", "service_boundaries", tier):
            try:
                result = result.model_copy(
                    update={
                        "service_boundaries_success": False,
                        "service_boundaries_error": "Service boundary detection requires ENTERPRISE tier",
                    }
                )
            except Exception:
                pass
        else:
            try:
                from code_scalpel.surgery.surgical_extractor import (
                    detect_service_boundaries as _detect_boundaries,
                )

                boundaries = await asyncio.to_thread(
                    _detect_boundaries,
                    project_root=project_root,
                    min_isolation_score=min_isolation_score,
                )

                if getattr(boundaries, "success", False):
                    payload: dict[str, Any] = {
                        "service_boundaries_success": True,
                        "suggested_services": [
                            {
                                "service_name": s.service_name,
                                "included_files": s.included_files,
                                "external_dependencies": s.external_dependencies,
                                "internal_dependencies": s.internal_dependencies,
                                "isolation_level": s.isolation_level,
                                "rationale": s.rationale,
                            }
                            for s in boundaries.suggested_services
                        ],
                        "service_dependency_graph": boundaries.dependency_graph,
                        "service_total_files_analyzed": boundaries.total_files_analyzed,
                        "service_boundaries_explanation": boundaries.explanation,
                    }
                else:
                    payload = {
                        "service_boundaries_success": False,
                        "service_boundaries_error": getattr(boundaries, "error", None)
                        or "Service boundary detection failed",
                    }

                result = result.model_copy(update=payload)
            except Exception as e:
                try:
                    result = result.model_copy(
                        update={
                            "service_boundaries_success": False,
                            "service_boundaries_error": f"Service boundary detection failed: {e}",
                        }
                    )
                except Exception:
                    pass

    if ctx:
        msg = f"Analyzed {result.total_files} files, {result.total_lines} lines"
        await ctx.report_progress(100, 100, msg)

    return result


get_project_map = mcp.tool()(
    envelop_tool_function(
        _get_project_map_tool,
        tool_id="get_project_map",
        tool_version=_pkg_version,
        tier_getter=_tier_getter,
    )
)


async def _get_cross_file_dependencies_tool(
    target_file: str,
    target_symbol: str,
    project_root: str | None = None,
    max_depth: int = 3,
    include_code: bool = True,
    include_diagram: bool = True,
    confidence_decay_factor: float = 0.9,
    max_files: int | None = None,
    timeout_seconds: float | None = None,
) -> Any:
    """
    Analyze and extract cross-file dependencies for a symbol.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.

    **Tier Capabilities:**
    - Community: Max depth=1, max files=50
    - Pro: Max depth=5, max files=500
    - Enterprise: Unlimited depth and files

    Args:
        target_file: Path to file containing the target symbol (relative to project root)
        target_symbol: Name of the function or class to analyze
        project_root: Project root directory (default: server's project root)
        max_depth: Maximum depth of dependency resolution (default: 3)
        include_code: Include full source code in result (default: True)
        include_diagram: Include Mermaid diagram of imports (default: True)
        confidence_decay_factor: Decay factor per depth level (default: 0.9).
                                 Lower values = faster decay. Range: 0.0-1.0

    Returns:
        CrossFileDependenciesResult with extracted symbols, dependency graph, combined code,
        and confidence scores for each symbol
    """
    # [20251226_FEATURE] Tier-aware limits and capabilities
    tier = _get_current_tier()
    caps = get_tool_capabilities("get_cross_file_dependencies", tier) or {}
    limits = caps.get("limits", {}) or {}

    max_depth_limit = limits.get("max_depth")
    effective_max_depth = max_depth
    if max_depth_limit is not None and max_depth > max_depth_limit:
        effective_max_depth = int(max_depth_limit)

    max_files_limit = limits.get("max_files")
    if max_files is not None:
        max_files_limit = max_files

    result = await asyncio.to_thread(
        _get_cross_file_dependencies_sync,
        target_file,
        target_symbol,
        project_root,
        effective_max_depth,
        include_code,
        include_diagram,
        confidence_decay_factor,
        tier,
        caps,
        max_files_limit,
        timeout_seconds,
    )

    # [20260120_BUGFIX] Ensure raw envelope callers see an explicit success flag.
    if isinstance(result, ToolResponseEnvelope):
        data = result.data
        if isinstance(data, dict) and "success" not in data:
            data["success"] = result.error is None
            result.data = data
    elif isinstance(result, dict) and "success" not in result:
        result["success"] = True

    return result


get_cross_file_dependencies = mcp.tool()(
    envelop_tool_function(
        _get_cross_file_dependencies_tool,
        tool_id="get_cross_file_dependencies",
        tool_version=_pkg_version,
        tier_getter=_tier_getter,
    )
)


async def _cross_file_security_scan_tool(
    project_root: str | None = None,
    entry_points: list[str] | None = None,
    max_depth: int = 5,
    include_diagram: bool = True,
    timeout_seconds: float | None = 120.0,
    max_modules: int | None = 500,
    confidence_threshold: float = 0.7,
    ctx: Context | None = None,
) -> Any:
    """
    Perform cross-file security analysis tracking taint flow across module boundaries.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.

    **Tier Capabilities:**
    - Community: Max modules 10, max depth 3
    - Pro: Max modules 100, max depth 10
    - Enterprise: Unlimited modules and depth

    Args:
        project_root: Project root directory (default: server's project root)
        entry_points: Optional list of entry point functions to start from
                     (e.g., ["app.py:main", "routes.py:index"])
                     If None, analyzes all detected entry points
        max_depth: Maximum call depth to trace (default: 5)
        include_diagram: Include Mermaid diagram of taint flows (default: True)
        timeout_seconds: Maximum time in seconds for analysis (default: 120)
                        Set to None for no timeout (not recommended for large projects)
        max_modules: Maximum number of modules to analyze (default: 500)
                    Set to None for no limit (not recommended for large projects)

    Returns:
        CrossFileSecurityResult with vulnerabilities, taint flows, and risk assessment
    """
    # [20251215_FEATURE] v2.0.0 - Progress token support
    # [20251220_FEATURE] v3.0.5 - Enhanced progress messages
    if ctx:
        await ctx.report_progress(
            progress=0, total=100, message="Starting cross-file security scan..."
        )

    tier = _get_current_tier()
    caps = get_tool_capabilities("cross_file_security_scan", tier)

    result = await asyncio.to_thread(
        _cross_file_security_scan_sync,
        project_root,
        entry_points,
        max_depth,
        include_diagram,
        timeout_seconds,
        max_modules,
        tier,
        caps,
        confidence_threshold,
    )

    # Report completion with summary
    if ctx:
        vuln_count = result.vulnerability_count
        await ctx.report_progress(
            progress=100,
            total=100,
            message=f"Scan complete: {vuln_count} cross-file vulnerabilities found",
        )

    return result


cross_file_security_scan = mcp.tool()(
    envelop_tool_function(
        _cross_file_security_scan_tool,
        tool_id="cross_file_security_scan",
        tool_version=_pkg_version,
        tier_getter=_tier_getter,
    )
)


__all__ = [
    "get_call_graph",
    "get_graph_neighborhood",
    "get_project_map",
    "get_cross_file_dependencies",
    "cross_file_security_scan",
]
