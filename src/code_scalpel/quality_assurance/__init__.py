# TODO [P0_CRITICAL] Complete module integration: Ensure ErrorScanner and ErrorFixer work seamlessly together, add unified configuration for both tools, test count: 15 tests (integration, configuration)
# TODO [P1_HIGH] Add linter integration: Integrate Ruff as primary Python linter, add Black formatting check, support pylint, flake8 as alternative backends, test count: 25 tests (linter integration, output parsing)
# TODO [P2_MEDIUM] Add coverage integration: Integrate pytest-cov for coverage checking, add coverage threshold enforcement, generate coverage reports, test count: 20 tests (coverage tools, reporting)
# TODO [P1_HIGH] Multi-language support: Add TypeScript/JavaScript linting via ESLint, add Java linting via Checkstyle, unified error format across languages, test count: 30 tests (multi-lang linting)
# TODO [P2_MEDIUM] CI/CD integration: JUnit XML output for CI systems, CodeClimate JSON output, SARIF output for GitHub code scanning, test count: 20 tests (output formats)
# TODO [P3_LOW] Performance optimization: Parallel file scanning, incremental scanning (changed files only), result caching, test count: 15 tests (performance)
# TODO [P2_MEDIUM] Compliance and governance: License compliance checking, security vulnerability scanning, custom rule enforcement, test count: 25 tests (compliance)
# TODO [P3_LOW] Advanced reporting: Trend analysis over time, error hotspot visualization, team performance metrics, test count: 15 tests (reporting)
# TODO [P4_LOW] Distributed scanning: Support for distributed workers, scan result aggregation, load balancing, test count: 10 tests (distribution)

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
