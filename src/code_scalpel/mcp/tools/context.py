"""Context and discovery MCP tool registrations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Context

from code_scalpel.mcp.helpers.context_helpers import (
    crawl_project as _crawl_project,
    get_file_context as _get_file_context,
    get_symbol_references as _get_symbol_references,
)
from code_scalpel.mcp.protocol import mcp


@mcp.tool()
async def crawl_project(
    root_path: str | None = None,
    exclude_dirs: list[str] | None = None,
    complexity_threshold: int = 10,
    include_report: bool = True,
    pattern: str | None = None,
    pattern_type: str = "regex",
    include_related: list[str] | None = None,
    ctx: Context | None = None,
) -> Any:
    """Crawl a project directory and analyze Python files."""
    return await _crawl_project(
        root_path=root_path,
        exclude_dirs=exclude_dirs,
        complexity_threshold=complexity_threshold,
        include_report=include_report,
        pattern=pattern,
        pattern_type=pattern_type,
        include_related=include_related,
        ctx=ctx,
    )


@mcp.tool()
async def get_file_context(file_path: str) -> Any:
    """Get a file overview without reading full content."""
    return await _get_file_context(file_path)


@mcp.tool()
async def get_symbol_references(
    symbol_name: str,
    project_root: str | None = None,
    scope_prefix: str | None = None,
    include_tests: bool = True,
    ctx: Context | None = None,
) -> Any:
    """Find all references to a symbol across the project."""
    return await _get_symbol_references(
        symbol_name,
        project_root=project_root,
        scope_prefix=scope_prefix,
        include_tests=include_tests,
        ctx=ctx,
    )


__all__ = ["crawl_project", "get_file_context", "get_symbol_references"]
