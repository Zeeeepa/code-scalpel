"""Extraction and refactor MCP tool registrations."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Context

from code_scalpel.mcp.helpers import extraction_helpers as _helpers
from code_scalpel.mcp.models.core import PatchResultModel
from code_scalpel.mcp.protocol import mcp

_extract_code = getattr(_helpers, "extract_code", None) or getattr(
    _helpers, "_extract_code_impl", None
)
_rename_symbol = getattr(_helpers, "rename_symbol", None)
_update_symbol = getattr(_helpers, "update_symbol", None)

if _extract_code is None or _rename_symbol is None or _update_symbol is None:
    raise ImportError("Extraction helpers missing expected tool implementations.")


@mcp.tool()
async def extract_code(
    target_type: str,
    target_name: str,
    file_path: str | None = None,
    code: str | None = None,
    language: str | None = None,
    include_context: bool = False,
    context_depth: int = 1,
    include_cross_file_deps: bool = False,
    include_token_estimate: bool = True,
    variable_promotion: bool = False,
    closure_detection: bool = False,
    dependency_injection_suggestions: bool = False,
    as_microservice: bool = False,
    microservice_host: str = "127.0.0.1",
    microservice_port: int = 8000,
    organization_wide: bool = False,
    workspace_root: str | None = None,
    ctx: Context | None = None,
) -> Any:
    """Extract code elements with optional dependency context."""
    return await _extract_code(
        target_type,
        target_name,
        file_path=file_path,
        code=code,
        language=language,
        include_context=include_context,
        context_depth=context_depth,
        include_cross_file_deps=include_cross_file_deps,
        include_token_estimate=include_token_estimate,
        variable_promotion=variable_promotion,
        closure_detection=closure_detection,
        dependency_injection_suggestions=dependency_injection_suggestions,
        as_microservice=as_microservice,
        microservice_host=microservice_host,
        microservice_port=microservice_port,
        organization_wide=organization_wide,
        workspace_root=workspace_root,
        ctx=ctx,
    )


@mcp.tool()
async def rename_symbol(
    file_path: str,
    target_type: str,
    target_name: str,
    new_name: str,
    create_backup: bool = True,
) -> PatchResultModel:
    """Rename a function, class, or method in a file."""
    if _rename_symbol is None:
        return PatchResultModel(
            success=False,
            file_path=file_path,
            target_name=target_name,
            target_type=target_type,
            error="rename_symbol helper not loaded",
        )
    return await _rename_symbol(
        file_path=file_path,
        target_type=target_type,
        target_name=target_name,
        new_name=new_name,
        create_backup=create_backup,
    )


@mcp.tool()
async def update_symbol(
    file_path: str,
    target_type: str,
    target_name: str,
    new_code: str | None = None,
    operation: str = "replace",
    new_name: str | None = None,
    create_backup: bool = True,
) -> PatchResultModel:
    """Update a function, class, or method in a file."""
    if _update_symbol is None:
        return PatchResultModel(
            success=False,
            file_path=file_path,
            target_name=target_name,
            target_type=target_type,
            error="update_symbol helper not loaded",
        )
    return await _update_symbol(
        file_path=file_path,
        target_type=target_type,
        target_name=target_name,
        new_code=new_code,
        operation=operation,
        new_name=new_name,
        create_backup=create_backup,
    )


__all__ = ["extract_code", "rename_symbol", "update_symbol"]
