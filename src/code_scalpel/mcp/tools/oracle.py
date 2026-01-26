"""Oracle MCP tool registrations.

[20260126_FEATURE] write_perfect_code tool for deterministic code generation.

Generates constraint specifications that bind LLMs to the reality of the codebase,
preventing hallucinations and enabling first-try correct code.
"""

from __future__ import annotations

import asyncio
import logging
import time
from importlib import import_module
from pathlib import Path

from code_scalpel.mcp.contract import ToolResponseEnvelope, ToolError, make_envelope
from code_scalpel import __version__ as _pkg_version
from code_scalpel.mcp.protocol import _get_current_tier
from code_scalpel.oracle.oracle_pipeline import OraclePipeline

logger = logging.getLogger(__name__)

# Avoid static import resolution issues in some type checkers
mcp = import_module("code_scalpel.mcp.protocol").mcp


async def _write_perfect_code_impl(
    file_path: str,
    instruction: str,
) -> str:
    """Implementation of write_perfect_code (async wrapper).

    Args:
        file_path: Path to target file
        instruction: Implementation instruction

    Returns:
        Markdown constraint specification
    """
    return await asyncio.to_thread(
        _write_perfect_code_sync,
        file_path,
        instruction,
    )


def _write_perfect_code_sync(
    file_path: str,
    instruction: str,
) -> str:
    """Synchronous implementation of write_perfect_code.

    Args:
        file_path: Path to target file
        instruction: Implementation instruction

    Returns:
        Markdown constraint specification

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If instruction is empty
    """
    # Validate inputs
    if not file_path:
        raise ValueError("file_path is required")
    if not instruction:
        raise ValueError("instruction is required")

    # Check file exists
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Get current tier for limits
    tier = _get_current_tier()

    # Get project root
    from code_scalpel.mcp.server import get_project_root

    repo_root = get_project_root()

    # Generate specification using OraclePipeline
    try:
        pipeline = OraclePipeline(repo_root, tier)
        spec = pipeline.generate_constraint_spec(
            file_path=file_path,
            instruction=instruction,
            governance_config=None,  # TODO: Load from .code-scalpel/governance.yaml
        )

        return spec

    except (FileNotFoundError, SyntaxError):
        raise
    except Exception as e:
        logger.error(f"Error generating constraint spec for {file_path}: {e}")
        raise


@mcp.tool()
async def write_perfect_code(
    file_path: str,
    instruction: str,
) -> ToolResponseEnvelope:
    """
    Generate constraint specification for AI-assisted code generation.

    Provides a Markdown specification containing:
    - Strict symbol table (function/class signatures)
    - Graph constraints (dependencies, callers)
    - Architectural rules (layer boundaries)
    - Code context (relevant snippet)
    - Implementation notes (best practices)

    The LLM uses this spec to generate code that compiles and integrates correctly.

    Args:
        file_path: Path to target file (e.g., "src/auth.py")
        instruction: What needs to be implemented (e.g., "Add JWT validation")

    Returns:
        Markdown constraint specification in response envelope
    """
    started = time.perf_counter()
    try:
        result = await _write_perfect_code_impl(file_path, instruction)
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        return make_envelope(
            data=result,
            tool_id="write_perfect_code",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
        )
    except FileNotFoundError as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(
            error=str(exc),
            error_code="not_found",
        )
        return make_envelope(
            data=None,
            tool_id="write_perfect_code",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )
    except ValueError as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(
            error=str(exc),
            error_code="invalid_argument",
        )
        return make_envelope(
            data=None,
            tool_id="write_perfect_code",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )
    except SyntaxError as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(
            error=str(exc),
            error_code="invalid_argument",
        )
        return make_envelope(
            data=None,
            tool_id="write_perfect_code",
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
            tool_id="write_perfect_code",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


__all__ = ["write_perfect_code"]
