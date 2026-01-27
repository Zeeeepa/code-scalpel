"""Extraction and refactor MCP tool registrations.

[20260121_REFACTOR] Wrap outputs in ToolResponseEnvelope to meet MCP
contract expectations (tier metadata and standardized envelope).
"""

from __future__ import annotations

import time

from mcp.server.fastmcp import Context
from code_scalpel.mcp.debug import debug_print
import sys
import traceback

from code_scalpel.mcp.helpers import extraction_helpers as _helpers
from code_scalpel.mcp.models.core import PatchResultModel
from code_scalpel.mcp.protocol import mcp, _get_current_tier
from code_scalpel.mcp.contract import ToolResponseEnvelope, ToolError, make_envelope
from code_scalpel import __version__ as _pkg_version

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
) -> ToolResponseEnvelope:
    """Extract code elements with optional dependency context.

    Extracts a specified code element (function, class, method) along with optional
    context, cross-file dependencies, and refactoring suggestions. Provide either
    'file_path' (recommended) or 'code' for the source. Language is auto-detected if not specified.

    **Tier Behavior:**
    - Community: Basic extraction only, no cross-file deps, depth 0
    - Pro: + Cross-file dependencies, variable promotion, closures, depth 1
    - Enterprise: + Microservice extraction, organization-wide analysis, unlimited depth

    **Tier Capabilities:**
    The following features/limits vary by tier:
    - Community: Basic extraction, max_depth 0, single file only
    - Pro: + Cross-file deps, variable promotion, closure detection, max_depth 1
    - Enterprise: + Microservice refactoring, org-wide scope, unlimited depth

    **Args:**
        target_type (str): Type of element to extract ('function', 'class', 'method')
        target_name (str): Name of the element to extract
        file_path (str, optional): Path to source file. Either file_path or code required.
        code (str, optional): Source code string. Either file_path or code required.
        language (str, optional): Programming language. Default: auto-detect
        include_context (bool): Include surrounding code context. Default: False
        context_depth (int): Depth of context to include. Default: 1
        include_cross_file_deps (bool): Include cross-file dependencies. Pro+ tier only. Default: False
        include_token_estimate (bool): Include token count estimate. Default: True
        variable_promotion (bool): Suggest variables for external dependencies. Pro+ only. Default: False
        closure_detection (bool): Detect closure requirements. Pro+ only. Default: False
        dependency_injection_suggestions (bool): Suggest DI patterns. Pro+ only. Default: False
        as_microservice (bool): Refactor as microservice. Enterprise only. Default: False
        microservice_host (str): Host for microservice. Default: '127.0.0.1'
        microservice_port (int): Port for microservice. Default: 8000
        organization_wide (bool): Organization-wide scope. Enterprise only. Default: False
        workspace_root (str, optional): Workspace root directory
        ctx (Context, optional): MCP context for progress reporting

    **Returns:**
        ToolResponseEnvelope:
        - success: True if extraction completed
        - data: Extracted code with context, dependencies, and suggestions
        - error: Error message if extraction failed (target not found, invalid code, etc.)

    **Example:**
        ```python
        result = await extract_code(
            target_type="function",
            target_name="authenticate",
            file_path="/src/auth.py",
            include_context=True
        )
        if result.success:
            print(result.data['target_code'])
        ```
    """
    started = time.perf_counter()
    try:
        if _extract_code is None:
            # [20260118_BUGFIX] Return error response instead of raising TypeError
            from code_scalpel.mcp.models.core import ContextualExtractionResult

            result = ContextualExtractionResult(
                success=False,
                target_name=target_name,
                target_code="",
                context_code="",
                full_code="",
                error="extract_code helper not loaded",
            )
        else:
            result = await _extract_code(
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
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        return make_envelope(
            data=result,
            tool_id="extract_code",
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
            tool_id="extract_code",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


@mcp.tool()
async def rename_symbol(
    file_path: str,
    target_type: str,
    target_name: str,
    new_name: str,
    create_backup: bool = True,
) -> ToolResponseEnvelope:
    """Rename a function, class, or method in a file.

    Updates a symbol's name throughout the file and optionally across the project,
    maintaining code integrity with automatic backup creation and reference updates.

    **Tier Behavior:**
    - Community: Definition-only rename, same-file reference updates only
    - Pro: + Cross-file reference updates (max 500 files searched, 200 updated)
    - Enterprise: + Unlimited cross-file updates, organization-wide rename capability

    **Tier Capabilities:**
    The following features/limits vary by tier:
    - Community: Same-file only, no cross-file changes
    - Pro: Cross-file updates, max 500 files searched, 200 updates
    - Enterprise: Unlimited cross-file updates, org-wide scope

    **Args:**
        file_path (str): Path to file containing the symbol to rename
        target_type (str): Type of symbol ('function', 'class', 'method')
        target_name (str): Current name of the symbol
        new_name (str): New name for the symbol
        create_backup (bool): Create backup before renaming. Default: True

    **Returns:**
        ToolResponseEnvelope:
        - success: True if rename completed
        - data: Patch result with updated file content and change locations
        - error: Error message if rename failed (symbol not found, invalid name, etc.)

    **Example:**
        ```python
        result = await rename_symbol(
            file_path="/src/auth.py",
            target_type="function",
            target_name="login",
            new_name="authenticate"
        )
        if result.success:
            print(f"Renamed {result.data['occurrences']} occurrences")
        ```
    """
    started = time.perf_counter()
    try:
        if _rename_symbol is None:
            result = PatchResultModel(
                success=False,
                file_path=file_path,
                target_name=target_name,
                target_type=target_type,
                error="rename_symbol helper not loaded",
            )
        else:
            result = await _rename_symbol(
                file_path=file_path,
                target_type=target_type,
                target_name=target_name,
                new_name=new_name,
                create_backup=create_backup,
            )
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        return make_envelope(
            data=result,
            tool_id="rename_symbol",
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
            tool_id="rename_symbol",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
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
) -> ToolResponseEnvelope:
    """Safely replace a function, class, or method in a file.

    **Tier Behavior:**
    - All tiers: Tool is available.
    - Limits and optional enhancements are applied based on tool capabilities.

    **Tier Capabilities:**
    - Community: Syntax validation, automatic backups, up to 10 updates per call
    - Pro: Semantic validation, automatic backups, unlimited updates per call
    - Enterprise: Full validation, automatic backups, unlimited updates per call

    **Validation Levels:**
    - Community: Syntax validation only
    - Pro: Syntax + semantic validation
    - Enterprise: Syntax + semantic + full compliance validation

    Args:
        file_path: Path to the file containing the symbol to update
        target_type: Type of symbol ("function", "class", "method")
        target_name: Name of the symbol to update
        new_code: New code for the symbol (required for "replace" operation)
        operation: Operation type ("replace" is the only supported operation)
        new_name: Optional new name for the symbol (for rename operations)
        create_backup: Whether to create a backup before updating (default: True)

    Returns:
        ToolResponseEnvelope with update result and tier metadata
    """
    started = time.perf_counter()
    try:
        debug_print(
            f"DEBUG:update_symbol: start file_path={file_path!r} target_type={target_type!r} target_name={target_name!r} operation={operation!r}"
        )
        if _update_symbol is None:
            result = PatchResultModel(
                success=False,
                file_path=file_path,
                target_name=target_name,
                target_type=target_type,
                error="update_symbol helper not loaded",
            )
        else:
            try:
                debug_print("DEBUG:update_symbol: calling helper _update_symbol")
                result = await _update_symbol(
                    file_path=file_path,
                    target_type=target_type,
                    target_name=target_name,
                    new_code=new_code,
                    operation=operation,
                    new_name=new_name,
                    create_backup=create_backup,
                )
            except Exception:
                debug_print("ERROR:update_symbol: exception in helper _update_symbol:")
                traceback.print_exc(file=sys.stderr)
                raise
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        debug_print(
            f"DEBUG:update_symbol: helper returned, preparing envelope (duration_ms={duration_ms})"
        )
        try:
            env = make_envelope(
                data=result,
                tool_id="update_symbol",
                tool_version=_pkg_version,
                tier=tier,
                duration_ms=duration_ms,
            )
            debug_print("DEBUG:update_symbol: envelope created successfully")
            return env
        except Exception as exc:
            # Log full traceback and return an error envelope so the MCP
            # transport can still send a valid JSON response back to the client.
            debug_print("ERROR:update_symbol: exception while creating envelope:")
            traceback.print_exc(file=sys.stderr)
            # Use a generic internal_error code when the contract's ErrorCode
            # union does not include a custom serialization error string.
            error_obj = ToolError(error=str(exc), error_code="internal_error")
            return make_envelope(
                data=None,
                tool_id="update_symbol",
                tool_version=_pkg_version,
                tier=tier,
                duration_ms=duration_ms,
                error=error_obj,
            )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(error=str(exc), error_code="internal_error")
        return make_envelope(
            data=None,
            tool_id="update_symbol",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


__all__ = ["extract_code", "rename_symbol", "update_symbol"]
