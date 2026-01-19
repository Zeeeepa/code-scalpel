"""Security MCP tool registrations."""

from __future__ import annotations

import asyncio
from importlib import import_module
from typing import Optional

from mcp.server.fastmcp import Context
from code_scalpel.licensing.features import get_tool_capabilities
from code_scalpel.mcp.models.core import UnifiedSinkResult
from code_scalpel.mcp.models.security import (
    DependencyScanResult,
    SecurityResult,
    TypeEvaporationResultModel,
)
from code_scalpel.mcp.helpers.security_helpers import (
    _unified_sink_detect_sync,
    _type_evaporation_scan_sync,
    _scan_dependencies_sync,
    _security_scan_sync,
)
from code_scalpel.mcp.protocol import _get_current_tier

# Avoid static import resolution issues in some type checkers
mcp = import_module("code_scalpel.mcp.protocol").mcp


@mcp.tool()
async def unified_sink_detect(
    code: str, language: str, confidence_threshold: float = 0.7
) -> UnifiedSinkResult:
    """Unified polyglot sink detection with confidence thresholds."""
    tier = _get_current_tier()
    capabilities = get_tool_capabilities("unified_sink_detect", tier)
    return await asyncio.to_thread(
        _unified_sink_detect_sync,
        code,
        language,
        confidence_threshold,
        tier,
        capabilities,
    )


@mcp.tool()
async def type_evaporation_scan(
    frontend_code: str,
    backend_code: str,
    frontend_file: str = "frontend.ts",
    backend_file: str = "backend.py",
) -> TypeEvaporationResultModel:
    """Detect Type System Evaporation vulnerabilities across frontend/backend code."""
    tier = _get_current_tier()
    caps = get_tool_capabilities("type_evaporation_scan", tier) or {}
    cap_set = set(caps.get("capabilities", []))
    limits = caps.get("limits", {}) or {}
    frontend_only = bool(limits.get("frontend_only", False))
    raw_max_files = limits.get("max_files")
    try:
        max_files = int(raw_max_files) if raw_max_files is not None else None
    except (TypeError, ValueError):
        max_files = None

    enable_pro = bool(
        {
            "implicit_any_tracing",
            "network_boundary_analysis",
            "library_boundary_analysis",
        }
        & cap_set
    )
    enable_enterprise = bool(
        {
            "runtime_validation_generation",
            "zod_schema_generation",
            "api_contract_validation",
        }
        & cap_set
    )

    return await asyncio.to_thread(
        _type_evaporation_scan_sync,
        frontend_code,
        backend_code,
        frontend_file,
        backend_file,
        enable_pro,
        enable_enterprise,
        frontend_only,
        max_files,
    )


@mcp.tool()
async def scan_dependencies(
    path: str | None = None,
    project_root: str | None = None,
    scan_vulnerabilities: bool = True,
    include_dev: bool = True,
    timeout: float = 30.0,
    ctx: Context | None = None,
) -> DependencyScanResult:
    """Scan project dependencies for known vulnerabilities."""
    # Import PROJECT_ROOT from server to avoid circular import issues
    server = import_module("code_scalpel.mcp.server")
    resolved_path = path or project_root or str(server.PROJECT_ROOT)
    tier = _get_current_tier()
    caps = get_tool_capabilities("scan_dependencies", tier)

    if ctx:
        await ctx.report_progress(0, 100, f"Scanning dependencies in {resolved_path}...")

    result = await asyncio.to_thread(
        _scan_dependencies_sync,
        project_root=resolved_path,
        scan_vulnerabilities=scan_vulnerabilities,
        include_dev=include_dev,
        timeout=timeout,
        tier=tier,
        capabilities=caps,
        ctx=ctx,
    )

    if ctx:
        vuln_count = result.total_vulnerabilities
        await ctx.report_progress(100, 100, f"Scan complete: {vuln_count} vulnerabilities found")

    return result


@mcp.tool()
async def security_scan(
    code: Optional[str] = None,
    file_path: Optional[str] = None,
    confidence_threshold: float = 0.7,
) -> SecurityResult:
    """Scan code for security vulnerabilities using taint analysis."""
    tier = _get_current_tier()
    caps = get_tool_capabilities("security_scan", tier)
    return await asyncio.to_thread(
        _security_scan_sync, code, file_path, tier, caps, confidence_threshold
    )


__all__ = [
    "security_scan",
    "scan_dependencies",
    "type_evaporation_scan",
    "unified_sink_detect",
]
