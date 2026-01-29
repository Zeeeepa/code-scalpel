"""Symbolic and testing MCP tool registrations.

[20260121_REFACTOR] Wrap outputs in ToolResponseEnvelope for MCP contract.
"""

from __future__ import annotations

import asyncio
import inspect
import sys
import time
from importlib import import_module

import code_scalpel.licensing.features as feature_caps
from code_scalpel.mcp.helpers import symbolic_helpers as sym_helpers
from code_scalpel.mcp.models.core import TestGenerationResult
from code_scalpel.licensing import tier_detector

# [20260121_BUGFIX] Move contract imports before variable assignments to satisfy E402
from code_scalpel.mcp.contract import ToolResponseEnvelope, ToolError, make_envelope
from code_scalpel import __version__ as _pkg_version
from code_scalpel.mcp.protocol import _get_current_tier

_ORIG_SYM_GENERATE_TESTS = sym_helpers._generate_tests_sync
_ORIG_SYM_SYMBOLIC = sym_helpers._symbolic_execute_sync

# [20260121_TEST] Expose helper aliases for test monkeypatching
_generate_tests_sync = sym_helpers._generate_tests_sync
_symbolic_execute_sync = sym_helpers._symbolic_execute_sync

mcp = import_module("code_scalpel.mcp.protocol").mcp


@mcp.tool()
async def symbolic_execute(
    code: str,
    max_paths: int | None = None,
    max_depth: int | None = None,
) -> ToolResponseEnvelope:
    """
    Perform symbolic execution on Python code.
    Analyzes Python code symbolically to explore execution paths, discover constraints, and identify potential issues without concrete execution.

    **Tier Behavior:**
    - Community: Basic symbolic execution (max_paths=50, max_depth=10, basic types)
    - Pro: Advanced symbolic execution (max_paths=unlimited, max_depth=100, concolic execution)
    - Enterprise: Unlimited symbolic execution (max_paths=unlimited, max_depth=unlimited, distributed execution, memory modeling)

    **Tier Capabilities:**
    - **Community:** Basic symbolic execution (max_paths=50, max_depth=10, constraint_types=["int", "bool", "string", "float"])
    - **Pro:** Advanced symbolic execution (max_paths=unlimited, max_depth=100, constraint_types=["int", "bool", "string", "float", "list", "dict"], concolic execution)
    - **Enterprise:** Unlimited symbolic execution (max_paths=unlimited, max_depth=unlimited, constraint_types="all", distributed execution, memory modeling)

    **Args:**
    - code (str): Python code to symbolically execute
    - max_paths (int, optional): Maximum number of execution paths to explore (subject to tier limits)
    - max_depth (int, optional): Maximum loop unrolling depth (subject to tier limits)

    **Returns:**
    - ToolResponseEnvelope: Standardized MCP response envelope containing:
      - data (SymbolicResult): Symbolic execution results with:
        - success (bool): Whether analysis succeeded
        - paths_explored (int): Number of execution paths explored
        - paths (list[ExecutionPath]): Discovered execution paths with conditions and constraints
        - symbolic_variables (list[str]): Variables treated symbolically
        - constraints (list[str]): Discovered constraints
        - total_paths (int, optional): Total paths discovered before limiting
        - truncated (bool): Whether paths were limited by configuration
        - truncation_warning (str, optional): Warning when results are limited
        - path_prioritization (dict, optional): Path prioritization metadata (Pro/Enterprise)
        - concolic_results (dict, optional): Concolic execution results (Pro/Enterprise)
        - state_space_analysis (dict, optional): State space reduction analysis (Enterprise)
        - memory_model (dict, optional): Memory modeling results (Enterprise)
        - error (str, optional): Error message if analysis failed
      - tier (str, optional): Applied tier ("community", "pro", "enterprise")
      - error (ToolError, optional): Standardized error if operation failed
      - warnings (list[str]): Non-fatal warnings from MCP boundary
    """
    started = time.perf_counter()
    try:
        tier = tier_detector.get_current_tier()
        caps = feature_caps.get_tool_capabilities("symbolic_execute", tier)
        limits = caps.get("limits", {}) if isinstance(caps, dict) else {}

        configured_max_paths = limits.get("max_paths")
        configured_max_depth = limits.get("max_depth")
        constraint_types = limits.get("constraint_types")

        effective_max_paths: int | None
        if max_paths is None:
            effective_max_paths = None if configured_max_paths is None else int(configured_max_paths)
        else:
            effective_max_paths = int(max_paths)
            if configured_max_paths is not None:
                effective_max_paths = min(effective_max_paths, int(configured_max_paths))

        effective_max_depth: int | None
        if max_depth is None:
            effective_max_depth = None if configured_max_depth is None else int(configured_max_depth)
        else:
            effective_max_depth = int(max_depth)
            if configured_max_depth is not None:
                effective_max_depth = min(effective_max_depth, int(configured_max_depth))

        # [20260121_BUGFIX] Resolve helper at runtime; prefer sym_helpers to honor monkeypatches
        helper = sym_helpers._symbolic_execute_sync

        result = await asyncio.to_thread(
            helper,
            code,
            effective_max_paths,
            effective_max_depth,
            constraint_types,
            tier=tier,
            capabilities=caps,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="symbolic_execute",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(error=str(exc), error_code="internal_error")
        return make_envelope(
            data=None,
            tool_id="symbolic_execute",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


@mcp.tool()
async def generate_unit_tests(
    code: str | None = None,
    file_path: str | None = None,
    function_name: str | None = None,
    framework: str = "pytest",
    data_driven: bool = False,
    crash_log: str | None = None,
) -> ToolResponseEnvelope:
    """Generate unit tests from code using symbolic execution.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.

    **Tier Capabilities:**
    - Community: Max 5 test cases, pytest framework only
    - Pro: Max 20 test cases, pytest/unittest frameworks, data-driven tests
    - Enterprise: Unlimited test cases, all frameworks, data-driven tests, bug reproduction

    **Input Methods (choose one):**
    - `code`: Direct Python code string to analyze
    - `file_path`: Path to Python file containing the code
    - `function_name`: Name of function to generate tests for (requires file_path)

    **Args:**
        code: Python code string to generate tests for
        file_path: Path to Python file to analyze
        function_name: Specific function name to target (optional)
        framework: Test framework ("pytest", "unittest", etc.)
        data_driven: Generate parameterized data-driven tests (Pro+)
        crash_log: Crash log for bug reproduction tests (Enterprise only)

    **Returns:**
        ToolResponseEnvelope with generated test cases and tier metadata
    """
    started = time.perf_counter()
    try:
        # [20260120_BUGFIX] Consistent tier detection pattern
        tier = tier_detector.get_current_tier()
        caps = feature_caps.get_tool_capabilities("generate_unit_tests", tier)
        limits = caps.get("limits", {})
        cap_set = caps.get("capabilities", set())

        max_test_cases = limits.get("max_test_cases")
        allowed_frameworks = limits.get("test_frameworks")
        # [20251231_BUGFIX] Fixed capabilities check - it's a set, not dict
        data_driven_supported = "data_driven_tests" in cap_set
        bug_reproduction_supported = "bug_reproduction" in cap_set

        # [20251229_FEATURE] v3.3.0 - Pro tier enforcement for data-driven tests
        if data_driven and not data_driven_supported:
            result = TestGenerationResult(
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
            duration_ms = int((time.perf_counter() - started) * 1000)
            return make_envelope(
                data=result,
                tool_id="generate_unit_tests",
                tool_version=_pkg_version,
                tier=tier,
                duration_ms=duration_ms,
            )

        # [20251229_FEATURE] v3.3.0 - Enterprise tier enforcement for bug reproduction
        if crash_log and not bug_reproduction_supported:
            result = TestGenerationResult(
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
            duration_ms = int((time.perf_counter() - started) * 1000)
            return make_envelope(
                data=result,
                tool_id="generate_unit_tests",
                tool_version=_pkg_version,
                tier=tier,
                duration_ms=duration_ms,
            )

        if isinstance(allowed_frameworks, list) and framework not in allowed_frameworks:
            result = TestGenerationResult(
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
            duration_ms = int((time.perf_counter() - started) * 1000)
            return make_envelope(
                data=result,
                tool_id="generate_unit_tests",
                tool_version=_pkg_version,
                tier=tier,
                duration_ms=duration_ms,
            )

        # [20260121_BUGFIX] Resolve helper at runtime so tests can monkeypatch either
        # sym_helpers._generate_tests_sync or server._generate_tests_sync.
        helper = sym_helpers._generate_tests_sync
        if sym_helpers._generate_tests_sync is not _ORIG_SYM_GENERATE_TESTS:
            helper = sym_helpers._generate_tests_sync
        else:
            server_mod = sys.modules.get("code_scalpel.mcp.server")
            if server_mod is None:
                try:
                    server_mod = sym_helpers._get_server()
                except Exception:
                    server_mod = None

            if server_mod and hasattr(server_mod, "_generate_tests_sync"):
                candidate = getattr(server_mod, "_generate_tests_sync")
                try:
                    sig = inspect.signature(candidate)
                    if len(sig.parameters) >= 7:
                        helper = candidate
                except Exception:
                    # If signature cannot be inspected, fall back to sym_helpers
                    helper = sym_helpers._generate_tests_sync

        result = await asyncio.to_thread(
            helper,
            code,
            file_path,
            function_name,
            framework,
            max_test_cases,
            data_driven,
            crash_log,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="generate_unit_tests",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(error=str(exc), error_code="internal_error")
        return make_envelope(
            data=None,
            tool_id="generate_unit_tests",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


@mcp.tool()
async def simulate_refactor(
    original_code: str,
    new_code: str | None = None,
    patch: str | None = None,
    strict_mode: bool = False,
) -> ToolResponseEnvelope:
    """Simulate applying a code change and check for safety issues.

    **Description:**
    Verifies code changes are safe before applying them by detecting security issues and structural changes that could break functionality.

    **Tier Behavior:**
    - Community: Basic refactor simulation (max 1MB file size, basic analysis depth)
    - Pro: Advanced simulation with type checking (max 10MB file size, advanced analysis depth)
    - Enterprise: Deep simulation with compliance validation (max 100MB file size, deep analysis depth)

    **Tier Capabilities:**
    - Community: basic_simulation, structural_diff (max_file_size_mb=1, analysis_depth="basic")
    - Pro: Community capabilities + advanced_simulation, behavior_preservation, type_checking, build_check (max_file_size_mb=10, analysis_depth="advanced")
    - Enterprise: Pro capabilities + regression_prediction, impact_analysis, custom_rules, compliance_validation (max_file_size_mb=100, analysis_depth="deep")

    **Args:**
        original_code: Original code before changes
        new_code: Complete new code after changes (alternative to patch)
        patch: Patch/diff describing the changes (alternative to new_code)
        strict_mode: Enable strict validation checks

    **Returns:**
        ToolResponseEnvelope:
        - success: True if simulation succeeded
        - data: RefactorSimulationResult with detailed safety analysis:
            - success: Whether simulation succeeded
            - is_safe: Whether the refactor is safe to apply
            - status: Status (safe, unsafe, warning, or error)
            - reason: Reason if not safe
            - security_issues: List of security issues found with type, severity, line, description, CWE
            - structural_changes: Dictionary of functions/classes added/removed/modified
            - warnings: List of non-critical warnings
            - error: Error message if simulation failed
        - error: Error message if operation failed
    """
    started = time.perf_counter()
    try:
        # [20251225_FEATURE] Tier-based behavior via capability matrix (no upgrade hints).
        tier = tier_detector.get_current_tier()
        caps = feature_caps.get_tool_capabilities("simulate_refactor", tier)
        limits = caps.get("limits", {})
        tool_caps = caps.get("capabilities", set())

        max_file_size_mb = limits.get("max_file_size_mb")
        analysis_depth = limits.get("analysis_depth", "basic")
        compliance_validation = "compliance_validation" in tool_caps

        result = await asyncio.to_thread(
            sym_helpers._simulate_refactor_sync,
            original_code,
            new_code,
            patch,
            strict_mode,
            max_file_size_mb=max_file_size_mb,
            analysis_depth=analysis_depth,
            compliance_validation=compliance_validation,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="simulate_refactor",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(error=str(exc), error_code="internal_error")
        return make_envelope(
            data=None,
            tool_id="simulate_refactor",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


__all__ = ["symbolic_execute", "generate_unit_tests", "simulate_refactor"]
