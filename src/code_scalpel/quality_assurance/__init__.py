"""
Quality Assurance Module - Error detection, fixing, and code quality tools.

[20251224_REFACTOR] Created as part of Project Reorganization Issue #1.
Consolidated error analysis and fixing tools from top-level modules.

This module provides:
- ErrorScanner: Project-wide error detection and categorization
- ErrorFixer: Automatic code quality fixes
- (Future) Linter integration, formatter tools, coverage analysis

Migration Guide:
    # Old imports (deprecated in v3.3.0):
    from code_scalpel.error_scanner import ErrorScanner
    from code_scalpel.error_fixer import ErrorFixer

    # New imports (recommended):
    from code_scalpel.quality_assurance import ErrorScanner, ErrorFixer
    # Or:
    from code_scalpel.quality_assurance.error_scanner import ErrorScanner
    from code_scalpel.quality_assurance.error_fixer import ErrorFixer

TODO ITEMS: quality_assurance/__init__.py
============================================================================
COMMUNITY TIER - Core Quality Assurance (P0-P2)
============================================================================

# [P0_CRITICAL] Complete module integration:
#     - Ensure ErrorScanner and ErrorFixer work seamlessly together
#     - Add unified configuration for both tools
#     - Test count: 15 tests (integration, configuration)

# [P1_HIGH] Add linter integration:
#     - Integrate Ruff as primary Python linter
#     - Add Black formatting check
#     - Support pylint, flake8 as alternative backends
#     - Test count: 25 tests (linter integration, output parsing)

# [P2_MEDIUM] Add coverage integration:
#     - Integrate pytest-cov for coverage checking
#     - Add coverage threshold enforcement
#     - Generate coverage reports
#     - Test count: 20 tests (coverage tools, reporting)

============================================================================
PRO TIER - Advanced Quality Features (P1-P3)
============================================================================

# [P1_HIGH] Multi-language support:
#     - Add TypeScript/JavaScript linting via ESLint
#     - Add Java linting via Checkstyle
#     - Unified error format across languages
#     - Test count: 30 tests (multi-lang linting)

# [P2_MEDIUM] CI/CD integration:
#     - JUnit XML output for CI systems
#     - CodeClimate JSON output
#     - SARIF output for GitHub code scanning
#     - Test count: 20 tests (output formats)

# [P3_LOW] Performance optimization:
#     - Parallel file scanning
#     - Incremental scanning (changed files only)
#     - Result caching
#     - Test count: 15 tests (performance)

============================================================================
ENTERPRISE TIER - Enterprise Quality Features (P2-P4)
============================================================================

# [P2_MEDIUM] Compliance and governance:
#     - License compliance checking
#     - Security vulnerability scanning
#     - Custom rule enforcement
#     - Test count: 25 tests (compliance)

# [P3_LOW] Advanced reporting:
#     - Trend analysis over time
#     - Error hotspot visualization
#     - Team performance metrics
#     - Test count: 15 tests (reporting)

# [P4_LOW] Distributed scanning:
#     - Support for distributed workers
#     - Scan result aggregation
#     - Load balancing
#     - Test count: 10 tests (distribution)

============================================================================
TOTAL ESTIMATED TESTS: 175 tests
============================================================================
"""

from .error_fixer import ErrorFixer, FixResult, FixResults
# [20251224_REFACTOR] Import from submodules
from .error_scanner import CodeError, ErrorScanner, ErrorSeverity, ScanResults

__all__ = [
    # Error Scanner
    "ErrorScanner",
    "ScanResults",
    "CodeError",
    "ErrorSeverity",
    # Error Fixer
    "ErrorFixer",
    "FixResult",
    "FixResults",
]

__version__ = "1.0.0"
