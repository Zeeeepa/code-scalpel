"""Analyze MCP tool registrations."""

from __future__ import annotations

import asyncio
from importlib import import_module
from typing import Any

from code_scalpel.mcp.helpers.analyze_helpers import _analyze_code_sync

# Avoid static import resolution issues in some type checkers
mcp = import_module("code_scalpel.mcp.protocol").mcp


@mcp.tool()
async def analyze_code(code: str, language: str = "auto", file_path: str | None = None) -> Any:
    """
    Analyze source code structure.

    Use this tool to understand the high-level architecture (classes, functions, imports)
    of a file before attempting to edit it. This helps prevent hallucinating non-existent
    methods or classes.
    """
    return await asyncio.to_thread(_analyze_code_sync, code, language, file_path)


__all__ = ["analyze_code"]
