"""
Autonomy module for Code Scalpel v3.0.0.

This module provides self-correction capabilities for AI agents,
including error-to-diff conversion, audit trail, and speculative execution.

[20251217_FEATURE] v3.0.0 Autonomy - Merged Error-to-Diff and Audit Trail
"""

from code_scalpel.autonomy.error_to_diff import (
    ErrorType,
    FixHint,
    ErrorAnalysis,
    ErrorToDiffEngine,
    ParsedError,
)

from code_scalpel.autonomy.audit import (
    AuditEntry,
    AutonomyAuditTrail,
)

__all__ = [
    # Error-to-Diff Engine
    "ErrorType",
    "FixHint",
    "ErrorAnalysis",
    "ErrorToDiffEngine",
    "ParsedError",
    # Audit Trail
    "AuditEntry",
    "AutonomyAuditTrail",
]
