"""Analyze MCP tool registrations.

[20260121_REFACTOR] Ensure all MCP tool responses use ToolResponseEnvelope
for contract compliance (tier metadata, duration, standardized errors).
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

# Avoid static import resolution issues in some type checkers
mcp = import_module("code_scalpel.mcp.protocol").mcp


@mcp.tool()
async def analyze_code(
    code: str | None = None, language: str = "auto", file_path: str | None = None
) -> ToolResponseEnvelope:
    """
    Analyze source code structure.

    Provide either 'code' (string) or 'file_path' (to read from file).
    Language is auto-detected if set to 'auto' (default).
    Use this tool to understand the high-level architecture (classes, functions, imports)
    of a file before attempting to edit it. This helps prevent hallucinating non-existent
    methods or classes.

    Tier Features:
    - Community: Basic AST parsing, functions/classes, complexity, imports
    - Pro: + Cognitive complexity, code smells, Halstead metrics, duplicate detection
    - Enterprise: + Custom rules, compliance checks, organization patterns, technical debt
    """
    started = time.perf_counter()
    try:
        # Validate input: either code or file_path must be provided
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

        result = await asyncio.to_thread(_analyze_code_sync, code, language, file_path)
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
