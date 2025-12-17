"""
Autonomy module for Code Scalpel v3.0.0.

This module provides self-correction capabilities for AI agents,
including error-to-diff conversion and speculative execution.

[20251217_FEATURE] v3.0.0 Autonomy - Error-to-Diff Engine
"""

from code_scalpel.autonomy.error_to_diff import (
    ErrorType,
    FixHint,
    ErrorAnalysis,
    ErrorToDiffEngine,
    ParsedError,
)

__all__ = [
    "ErrorType",
    "FixHint",
    "ErrorAnalysis",
    "ErrorToDiffEngine",
    "ParsedError",
]
