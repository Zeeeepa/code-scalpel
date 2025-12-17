"""
Autonomy module for Code Scalpel v3.0.0.

This module provides self-correction capabilities for AI agents,
including error-to-diff conversion and speculative execution in sandboxed environments.

[20251217_FEATURE] v3.0.0 Autonomy - Merged Error-to-Diff and Sandbox Execution
"""

from code_scalpel.autonomy.error_to_diff import (
    ErrorType,
    FixHint,
    ErrorAnalysis,
    ErrorToDiffEngine,
    ParsedError,
)

from code_scalpel.autonomy.sandbox import (
    ExecutionTestResult,
    FileChange,
    LintResult,
    SandboxExecutor,
    SandboxResult,
    SandboxTestResult,
    TestResult,
)

__all__ = [
    # Error-to-Diff Engine
    "ErrorType",
    "FixHint",
    "ErrorAnalysis",
    "ErrorToDiffEngine",
    "ParsedError",
    # Sandbox Executor
    "SandboxExecutor",
    "SandboxResult",
    "ExecutionTestResult",
    "SandboxTestResult",
    "TestResult",
    "LintResult",
    "FileChange",
]
