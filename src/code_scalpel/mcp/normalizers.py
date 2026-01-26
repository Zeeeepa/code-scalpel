"""Input normalization decorator and utilities.

This module implements the @normalize_input decorator that:
1. Accepts either code or file_path (but not both)
2. Reads files if needed, validates existence
3. Auto-detects language and creates SourceContext
4. Passes unified context to tool function
5. Applies tier-based limits before expensive operations

This removes boilerplate from individual tool functions.
"""

from __future__ import annotations

import asyncio
import functools
import logging
import os
from typing import Any, Callable, Optional, TypeVar, cast

from code_scalpel.mcp.models.context import Language, SourceContext
from code_scalpel.mcp.protocol import _get_current_tier
from code_scalpel.mcp.routers import LanguageRouter
from code_scalpel.licensing.features import get_tool_capabilities

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class InputNormalizationError(ValueError):
    """Raised when input normalization fails."""

    pass


def validate_file_exists(file_path: str) -> str:
    """Validate that a file exists and is readable.

    Args:
        file_path: Path to file (absolute or relative).

    Returns:
        Absolute path to file.

    Raises:
        InputNormalizationError: If file doesn't exist or isn't readable.
    """
    abs_path = os.path.abspath(file_path)

    if not os.path.exists(abs_path):
        raise InputNormalizationError(f"File not found: {file_path}")

    if not os.path.isfile(abs_path):
        raise InputNormalizationError(f"Path is not a file: {file_path}")

    if not os.access(abs_path, os.R_OK):
        raise InputNormalizationError(f"File is not readable: {file_path}")

    return abs_path


def read_file_content(file_path: str, encoding: str = "utf-8") -> str:
    """Read file content with proper error handling.

    Args:
        file_path: Path to file.
        encoding: File encoding (default: utf-8).

    Returns:
        File content as string.

    Raises:
        InputNormalizationError: If file cannot be read.
    """
    abs_path = validate_file_exists(file_path)

    try:
        with open(abs_path, "r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError as e:
        raise InputNormalizationError(
            f"File encoding error in {file_path}: {e}. Try a different encoding."
        ) from e
    except IOError as e:
        raise InputNormalizationError(f"Cannot read file {file_path}: {e}") from e


def check_file_size_limit(file_path: str, max_bytes: int) -> None:
    """Check if file size exceeds limit.

    Args:
        file_path: Path to file.
        max_bytes: Maximum file size in bytes.

    Raises:
        InputNormalizationError: If file exceeds limit.
    """
    abs_path = validate_file_exists(file_path)
    file_size = os.path.getsize(abs_path)
    if file_size > max_bytes:
        size_mb = file_size / (1024 * 1024)
        max_mb = max_bytes / (1024 * 1024)
        raise InputNormalizationError(
            f"File size {size_mb:.1f}MB exceeds limit of {max_mb:.1f}MB"
        )


def normalize_input(
    tool_id: str,
    language_param: str = "language",
) -> Callable[[F], F]:
    """Decorator that normalizes tool inputs into a SourceContext.

    Usage:
        @normalize_input(tool_id="analyze_code")
        async def my_tool(source_context: SourceContext, ...other params):
            # source_context is guaranteed to be valid and complete
            pass

    The decorator handles:
    1. Checking that either code OR file_path is provided (not both, not neither)
    2. Reading file content if file_path is provided
    3. Checking tier-based size limits
    4. Auto-detecting or validating language
    5. Creating and caching the AST
    6. Creating a SourceContext object
    7. Passing it as the first argument to the wrapped function

    Args:
        tool_id: MCP tool ID (for capability lookup).
        language_param: Name of the language parameter in the wrapped function
                       (default: "language").

    Returns:
        Decorator function.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(
            *args,
            code: Optional[str] = None,
            file_path: Optional[str] = None,
            language: Optional[str] = None,
            **kwargs,
        ) -> Any:
            """Async wrapper for normalize_input."""
            # Validate inputs: exactly one of code or file_path must be provided
            if (code is None and file_path is None) or (
                code is not None and file_path is not None
            ):
                raise InputNormalizationError(
                    "Must provide exactly one of: 'code' or 'file_path' (not both, not neither)"
                )

            # Get tier for capability limits
            tier = _get_current_tier()
            capabilities = get_tool_capabilities(tool_id, tier)

            # Determine content and file_path
            if file_path is not None:
                # Check size limit
                max_size_mb = capabilities.get("limits", {}).get("max_file_size_mb", 10)
                max_bytes = max_size_mb * 1024 * 1024
                check_file_size_limit(file_path, max_bytes)

                # Read file
                content = read_file_content(file_path)
                abs_path = os.path.abspath(file_path)
                actual_file_path = abs_path
                is_memory = False
            else:
                # Use provided code (in-memory)
                # Due to validation above, code is guaranteed to be str here
                content = cast(str, code)
                actual_file_path = None
                is_memory = True

            # Detect/validate language
            lang_param = language or "auto"
            lang_enum: Language = Language.UNKNOWN

            if lang_param != "auto":
                # Try to use specified language
                try:
                    lang_enum = Language(lang_param.lower())
                except ValueError:
                    logger.warning(f"Unknown language '{lang_param}', will auto-detect")
                    lang_param = "auto"

            if lang_param == "auto":
                # Auto-detect
                detection = LanguageRouter.detect(
                    content,
                    file_path=actual_file_path,
                    language_override=None,
                )
                logger.debug(f"Language detection: {detection}")
                lang_enum = detection.language

            # Create SourceContext with new field names
            source_context = SourceContext(
                content=content,
                file_path=actual_file_path,
                is_memory=is_memory,
                language=lang_enum,
            )

            # Call wrapped function with SourceContext as first positional arg
            return await func(source_context, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(
            *args,
            code: Optional[str] = None,
            file_path: Optional[str] = None,
            language: Optional[str] = None,
            **kwargs,
        ) -> Any:
            """Sync wrapper for normalize_input (for non-async functions)."""
            # Validate inputs: exactly one of code or file_path must be provided
            if (code is None and file_path is None) or (
                code is not None and file_path is not None
            ):
                raise InputNormalizationError(
                    "Must provide exactly one of: 'code' or 'file_path' (not both, not neither)"
                )

            # Get tier for capability limits
            tier = _get_current_tier()
            capabilities = get_tool_capabilities(tool_id, tier)

            # Determine content and file_path
            if file_path is not None:
                # Check size limit
                max_size_mb = capabilities.get("limits", {}).get("max_file_size_mb", 10)
                max_bytes = max_size_mb * 1024 * 1024
                check_file_size_limit(file_path, max_bytes)

                # Read file
                content = read_file_content(file_path)
                abs_path = os.path.abspath(file_path)
                actual_file_path = abs_path
                is_memory = False
            else:
                # Use provided code (in-memory)
                # Due to validation above, code is guaranteed to be str here
                content = cast(str, code)
                actual_file_path = None
                is_memory = True

            # Detect/validate language
            lang_param = language or "auto"
            lang_enum: Language = Language.UNKNOWN

            if lang_param != "auto":
                # Try to use specified language
                try:
                    lang_enum = Language(lang_param.lower())
                except ValueError:
                    logger.warning(f"Unknown language '{lang_param}', will auto-detect")
                    lang_param = "auto"

            if lang_param == "auto":
                # Auto-detect
                detection = LanguageRouter.detect(
                    content,
                    file_path=actual_file_path,
                    language_override=None,
                )
                logger.debug(f"Language detection: {detection}")
                lang_enum = detection.language

            # Create SourceContext with new field names
            source_context = SourceContext(
                content=content,
                file_path=actual_file_path,
                is_memory=is_memory,
                language=lang_enum,
            )

            # Call wrapped function with SourceContext as first positional arg
            return func(source_context, *args, **kwargs)

        # Determine if the wrapped function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator


__all__ = [
    "InputNormalizationError",
    "normalize_input",
    "validate_file_exists",
    "read_file_content",
    "check_file_size_limit",
]
