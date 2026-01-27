"""Analyze MCP tool registrations.

[20260121_REFACTOR] Ensure all MCP tool responses use ToolResponseEnvelope
for contract compliance (tier metadata, duration, standardized errors).

[20260126_v1_1] Integrate Phase 6 Kernel (SourceContext, Validators, ResponseEnvelope)
to enable self-correction with validation suggestions for analyze_code.
Hybrid architecture: new tool uses kernel, legacy tools unchanged.
"""

from __future__ import annotations

import asyncio
import os
import time
from importlib import import_module

from code_scalpel.mcp.helpers.analyze_helpers import _analyze_code_sync
from code_scalpel.mcp.contract import ToolResponseEnvelope, ToolError, make_envelope
from code_scalpel import __version__ as _pkg_version
from code_scalpel.mcp.protocol import _get_current_tier
from code_scalpel.mcp.v1_1_kernel_adapter import get_adapter

# Avoid static import resolution issues in some type checkers
mcp = import_module("code_scalpel.mcp.protocol").mcp


@mcp.tool()
async def analyze_code(
    code: str | None = None, language: str = "auto", file_path: str | None = None
) -> ToolResponseEnvelope:
    """
    Analyze source code structure with AST parsing and metrics.

    Provide either 'code' (string) or 'file_path' (to read from file). Language is auto-detected
    if set to 'auto' (default). Use this tool to understand high-level architecture (classes,
    functions, imports) before attempting to edit, preventing hallucinated methods or classes.

    **Tier Behavior:**
    - Community: Basic AST parsing, functions/classes, complexity metrics, imports
    - Pro: + Cognitive complexity, code smells, Halstead metrics, duplicate detection
    - Enterprise: + Custom rules, compliance checks, org patterns, technical debt

    **Tier Capabilities:**
    The following features/limits vary by tier:
    - Community: Basic metrics only, max file size 10MB
    - Pro: Advanced metrics and smells, max file size 50MB
    - Enterprise: All features, unlimited file size, compliance checks

    **Args:**
        code (str, optional): Source code to analyze. Either code or file_path required.
        language (str): Programming language for analysis. Default: 'auto' (auto-detect).
                       Supported: python, javascript, typescript, java
        file_path (str, optional): Path to file to analyze. Either code or file_path required.
                                   If provided, file_size limits apply per tier.

    **Returns:**
        ToolResponseEnvelope:
        - success: True if analysis completed
        - data: Analysis results including functions, classes, complexity, imports
        - error: Error message if analysis failed (invalid code, file not found, etc.)

    **Example:**
        ```python
        result = await analyze_code(code="def hello(): pass", language="python")
        if result.success:
            print(result.data['functions'])
        ```

    [20260126_v1_1] Now with self-correction suggestions via kernel validation.
    """
    started = time.perf_counter()
    try:
        # [20260126_v1_1] Integrate Phase 6 Kernel for validation and self-correction
        adapter = get_adapter()

        # 1. Validate input: either code or file_path must be provided
        if code is None and file_path is None:
            raise ValueError("Either 'code' or 'file_path' must be provided")

        # If code is not provided, read from file_path
        if code is None and file_path is not None:
            # Get tier for limits
            tier = _get_current_tier()
            from code_scalpel.mcp.helpers.analyze_helpers import get_tool_capabilities

            capabilities = get_tool_capabilities("analyze_code", tier)
            limit_mb = capabilities.get("limits", {}).get("max_file_size_mb")

            # Check file exists
            if not os.path.isfile(file_path):
                raise ValueError(f"File not found: {file_path}")

            # Check file size before reading
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if limit_mb is not None and file_size_mb > limit_mb:
                raise ValueError(
                    f"File size {file_size_mb:.2f} MB exceeds limit of {limit_mb} MB for {tier} tier"
                )

            # Read the file
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

        # [20260126_v1_1] Create SourceContext and validate input
        try:
            ctx = adapter.create_source_context(
                code=code, file_path=file_path, language=language
            )
            is_valid, error_obj, suggestions = adapter.validate_input(ctx)

            if not is_valid and error_obj:
                # Return error response with self-correction suggestions
                duration_ms = int((time.perf_counter() - started) * 1000)
                tier = _get_current_tier()
                # Enhance error with suggestions
                error_obj.error_details = error_obj.error_details or {}
                error_obj.error_details["suggestions"] = suggestions
                return make_envelope(
                    data=None,
                    tool_id="analyze_code",
                    tool_version=_pkg_version,
                    tier=tier,
                    duration_ms=duration_ms,
                    error=error_obj,
                )
        except ValueError:
            # Validation setup error
            pass  # Continue with legacy code path

        # [20260126_v1_1] Core analysis (unchanged)
        result = await asyncio.to_thread(
            _analyze_code_sync, code or "", language, file_path
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        return make_envelope(
            data=result,
            tool_id="analyze_code",
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
            tool_id="analyze_code",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


__all__ = ["analyze_code"]
