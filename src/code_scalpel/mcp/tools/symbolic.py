"""Symbolic and testing MCP tool registrations."""

from __future__ import annotations

import asyncio
import inspect
from importlib import import_module
from typing import Any

from code_scalpel.licensing.features import get_tool_capabilities
from code_scalpel.mcp.helpers.symbolic_helpers import (
    _generate_tests_sync,
    _simulate_refactor_sync,
    _symbolic_execute_sync,
)
from code_scalpel.mcp.models.core import TestGenerationResult
from code_scalpel.licensing import tier_detector

mcp = import_module("code_scalpel.mcp.protocol").mcp


@mcp.tool()
async def symbolic_execute(
    code: str,
    max_paths: int | None = None,
    max_depth: int | None = None,
) -> Any:
    """Perform symbolic execution on Python code.

    [20251226_FEATURE] Tier-aware limits are loaded from limits.toml via get_tool_capabilities.
    """

    tier = tier_detector.get_current_tier()
    caps = get_tool_capabilities("symbolic_execute", tier)
    limits = caps.get("limits", {}) if isinstance(caps, dict) else {}

    configured_max_paths = limits.get("max_paths")
    configured_max_depth = limits.get("max_depth")
    constraint_types = limits.get("constraint_types")

    effective_max_paths: int | None
    if max_paths is None:
        effective_max_paths = (
            None if configured_max_paths is None else int(configured_max_paths)
        )
    else:
        effective_max_paths = int(max_paths)
        if configured_max_paths is not None:
            effective_max_paths = min(effective_max_paths, int(configured_max_paths))

    effective_max_depth: int | None
    if max_depth is None:
        effective_max_depth = (
            None if configured_max_depth is None else int(configured_max_depth)
        )
    else:
        effective_max_depth = int(max_depth)
        if configured_max_depth is not None:
            effective_max_depth = min(effective_max_depth, int(configured_max_depth))

    return await asyncio.to_thread(
        _symbolic_execute_sync,
        code,
        effective_max_paths,
        effective_max_depth,
        constraint_types,
        tier,
        caps,
    )


@mcp.tool()
async def generate_unit_tests(
    code: str | None = None,
    file_path: str | None = None,
    function_name: str | None = None,
    framework: str = "pytest",
    data_driven: bool = False,
    crash_log: str | None = None,
) -> Any:
    """Generate unit tests from code using symbolic execution."""
    # [20260120_BUGFIX] Allow test monkeypatch of server._get_current_tier for tier overrides
    try:
        server_module = import_module("code_scalpel.mcp.server")
        tier_override = getattr(server_module, "_get_current_tier", None)
        tier = (
            tier_override()
            if callable(tier_override)
            else tier_detector.get_current_tier()
        )
    except Exception:
        tier = tier_detector.get_current_tier()
    caps = get_tool_capabilities("generate_unit_tests", tier)
    limits = caps.get("limits", {})
    cap_set = caps.get("capabilities", set())

    max_test_cases = limits.get("max_test_cases")
    allowed_frameworks = limits.get("test_frameworks")
    # [20251231_BUGFIX] Fixed capabilities check - it's a set, not dict
    data_driven_supported = "data_driven_tests" in cap_set
    bug_reproduction_supported = "bug_reproduction" in cap_set

    # [20251229_FEATURE] v3.3.0 - Pro tier enforcement for data-driven tests
    if data_driven and not data_driven_supported:
        return TestGenerationResult(
            success=False,
            function_name=function_name or "unknown",
            test_count=0,
            total_test_cases=0,
            error="Data-driven test generation requires Pro tier or higher.",
            tier_applied=tier,
            framework_used=framework,
            max_test_cases_limit=max_test_cases,
            data_driven_enabled=False,
            bug_reproduction_enabled=False,
        )

    # [20251229_FEATURE] v3.3.0 - Enterprise tier enforcement for bug reproduction
    if crash_log and not bug_reproduction_supported:
        return TestGenerationResult(
            success=False,
            function_name=function_name or "unknown",
            test_count=0,
            total_test_cases=0,
            error="Bug reproduction test generation requires Enterprise tier.",
            tier_applied=tier,
            framework_used=framework,
            max_test_cases_limit=max_test_cases,
            data_driven_enabled=data_driven,
            bug_reproduction_enabled=False,
        )

    if isinstance(allowed_frameworks, list) and framework not in allowed_frameworks:
        return TestGenerationResult(
            success=False,
            function_name=function_name or "unknown",
            test_count=0,
            total_test_cases=0,
            error=f"Unsupported framework: {framework}",
            tier_applied=tier,
            framework_used=framework,
            max_test_cases_limit=max_test_cases,
            data_driven_enabled=data_driven,
            bug_reproduction_enabled=crash_log is not None,
        )

    # [20260120_BUGFIX] Allow tests to monkeypatch sync impl via server._generate_tests_sync
    try:
        server_module = import_module("code_scalpel.mcp.server")
        sync_impl_candidate = getattr(server_module, "_generate_tests_sync", None)
    except Exception:
        sync_impl_candidate = None

    # [20260120_BUGFIX] Only use monkeypatched sync impl if it supports extended args
    def _is_compatible(func: Any) -> bool:
        try:
            sig = inspect.signature(func)
        except (TypeError, ValueError):
            return False

        params = sig.parameters.values()
        positional_params = [
            p for p in params if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        has_var_positional = any(p.kind == p.VAR_POSITIONAL for p in params)
        has_var_keyword = any(p.kind == p.VAR_KEYWORD for p in params)

        # Need to accept at least 7 positional args or be variadic.
        return has_var_positional or has_var_keyword or len(positional_params) >= 7

    sync_impl = (
        sync_impl_candidate
        if callable(sync_impl_candidate) and _is_compatible(sync_impl_candidate)
        else _generate_tests_sync
    )

    result = await asyncio.to_thread(
        sync_impl,
        code,
        file_path,
        function_name,
        framework,
        max_test_cases,
        data_driven,
        crash_log,
    )

    # Add output metadata for transparency
    result.tier_applied = tier
    result.framework_used = framework
    result.max_test_cases_limit = max_test_cases
    result.data_driven_enabled = data_driven
    result.bug_reproduction_enabled = crash_log is not None

    return result


@mcp.tool()
async def simulate_refactor(
    original_code: str,
    new_code: str | None = None,
    patch: str | None = None,
    strict_mode: bool = False,
) -> Any:
    """Simulate applying a code change and check for safety issues."""
    # [20251225_FEATURE] Tier-based behavior via capability matrix (no upgrade hints).
    tier = tier_detector.get_current_tier()
    caps = get_tool_capabilities("simulate_refactor", tier)
    limits = caps.get("limits", {})
    tool_caps = caps.get("capabilities", set())

    max_file_size_mb = limits.get("max_file_size_mb")
    analysis_depth = limits.get("analysis_depth", "basic")
    compliance_validation = "compliance_validation" in tool_caps

    return await asyncio.to_thread(
        _simulate_refactor_sync,
        original_code,
        new_code,
        patch,
        strict_mode,
        max_file_size_mb=max_file_size_mb,
        analysis_depth=analysis_depth,
        compliance_validation=compliance_validation,
    )


__all__ = ["symbolic_execute", "generate_unit_tests", "simulate_refactor"]
