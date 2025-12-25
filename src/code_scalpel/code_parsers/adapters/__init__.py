"""
Parser Adapters - Bridge existing parsers to IParser interface.

[20251221_FEATURE] Adapters that wrap language-specific parsers to implement
the IParser interface for unified factory usage.

This module provides adapters for:
- JavaScriptParser → IParser
- TypeScriptParser → IParser (via JavaScriptParser)
- TreeSitterJavaParser → IParser

Usage:
    from code_parsers.adapters import JavaScriptParserAdapter, JavaParserAdapter
    from code_parsers import ParserFactory, Language

    # Register adapters
    ParserFactory.register_parser(Language.JAVASCRIPT, JavaScriptParserAdapter)
    ParserFactory.register_parser(Language.JAVA, JavaParserAdapter)

    # Use via factory
    parser = ParserFactory.get_parser(Language.JAVASCRIPT)
    result = parser.parse(code)

============================================================================
TODO ITEMS: code_parsers/adapters/__init__.py
============================================================================
COMMUNITY TIER - Core Adapter Infrastructure (P0-P2)
============================================================================

[P0_CRITICAL] Complete adapter implementation:
    - Create CppParserAdapter (C/C++ support)
    - Create GoParserAdapter (Go support)
    - Create RubyParserAdapter (Ruby support)
    - Create PhpParserAdapter (PHP support)
    - Create SwiftParserAdapter (Swift support)
    - Test count: 50 tests (1 adapter × 10 tests each)

[P1_HIGH] Standardize adapter interface:
    - Add get_capabilities() to all adapters
    - Implement consistent error handling
    - Add parser version tracking
    - Support configuration passing to underlying parsers
    - Test count: 30 tests (interface consistency)

[P1_HIGH] Add adapter auto-registration:
    - Auto-discover adapters in this directory
    - Register with ParserFactory on import
    - Support conditional registration (skip if parser unavailable)
    - Add registration metadata (version, capabilities)
    - Test count: 20 tests (auto-registration, discovery)

[P2_MEDIUM] Improve error handling:
    - Standardize error conversion across adapters
    - Add detailed error context extraction
    - Support error recovery strategies
    - Add error aggregation from multiple sources
    - Test count: 25 tests (error handling, conversion)

[P2_MEDIUM] Add adapter testing utilities:
    - Create common adapter test base class
    - Add adapter conformance tests
    - Implement integration tests for all adapters
    - Add performance benchmarking
    - Test count: 30 tests (utilities, conformance)

============================================================================
PRO TIER - Advanced Adapter Features (P1-P3)
============================================================================

[P1_HIGH] Implement multi-backend support:
    - Allow multiple parsers per language (tree-sitter, native, etc.)
    - Add backend selection strategy
    - Support fallback chains
    - Add performance profiling per backend
    - Test count: 35 tests (multi-backend, fallback)

[P1_HIGH] Add semantic analysis adapters:
    - Wrap type checkers (mypy, Flow, tsc)
    - Add symbol resolution adapters
    - Support cross-file analysis
    - Implement incremental analysis
    - Test count: 40 tests (semantic analysis, resolution)

[P2_MEDIUM] Implement adapter caching:
    - Cache parse results per adapter
    - Add invalidation strategies
    - Support distributed caching
    - Add cache metrics collection
    - Test count: 25 tests (caching, invalidation)

[P2_MEDIUM] Add linter adapters:
    - Create unified linter adapter interface
    - Wrap pylint, eslint, checkstyle, etc.
    - Aggregate results from multiple linters
    - Support linter configuration
    - Test count: 35 tests (linter integration, aggregation)

[P3_LOW] Implement transformation adapters:
    - Add code formatting adapters (Black, Prettier)
    - Support refactoring tool adapters
    - Add code generation adapters
    - Implement AST transformation pipelines
    - Test count: 30 tests (transformation, formatting)

============================================================================
ENTERPRISE TIER - Enterprise Adapter Features (P2-P4)
============================================================================

[P2_MEDIUM] Add distributed adapter coordination:
    - Support remote parser invocation
    - Implement adapter load balancing
    - Add adapter health monitoring
    - Support adapter failover
    - Test count: 35 tests (distribution, coordination)

[P2_MEDIUM] Implement enterprise compliance:
    - Add audit logging to all adapters
    - Support compliance policy enforcement
    - Generate compliance reports
    - Add usage tracking per adapter
    - Test count: 30 tests (compliance, audit)

[P3_LOW] Add multi-tenant adapter isolation:
    - Support tenant-specific adapters
    - Implement resource quotas per tenant
    - Add tenant-specific parser versions
    - Generate tenant usage analytics
    - Test count: 30 tests (multi-tenancy, isolation)

[P3_LOW] Implement adapter telemetry:
    - Add OpenTelemetry integration
    - Track adapter performance metrics
    - Support custom metric exporters
    - Generate adapter health dashboards
    - Test count: 25 tests (telemetry, monitoring)

[P4_LOW] Add ML-driven adapter selection:
    - Use ML to select optimal adapter
    - Predict adapter performance
    - Adaptive adapter configuration
    - Anomaly detection for adapter failures
    - Test count: 30 tests (ML integration, prediction)

============================================================================
TOTAL TEST ESTIMATE: 465 tests (175 COMMUNITY + 165 PRO + 125 ENTERPRISE)
============================================================================
"""

from .javascript_adapter import JavaScriptParserAdapter, TypeScriptParserAdapter
from .java_adapter import JavaParserAdapter  # type: ignore[import-not-found]

# [20251224_FEATURE] Additional language adapter stubs
# Note: These are stubs - implementations are in progress
try:
    from .cpp_adapter import CppParserAdapter
except (ImportError, NotImplementedError):
    CppParserAdapter = None  # type: ignore

try:
    from .csharp_adapter import CSharpParserAdapter
except (ImportError, NotImplementedError):
    CSharpParserAdapter = None  # type: ignore

try:
    from .go_adapter import GoParserAdapter
except (ImportError, NotImplementedError):
    GoParserAdapter = None  # type: ignore

try:
    from .kotlin_adapter import KotlinParserAdapter
except (ImportError, NotImplementedError):
    KotlinParserAdapter = None  # type: ignore

try:
    from .ruby_adapter import RubyParserAdapter
except (ImportError, NotImplementedError):
    RubyParserAdapter = None  # type: ignore

try:
    from .php_adapter import PhpParserAdapter
except (ImportError, NotImplementedError):
    PhpParserAdapter = None  # type: ignore

try:
    from .swift_adapter import SwiftParserAdapter
except (ImportError, NotImplementedError):
    SwiftParserAdapter = None  # type: ignore


__all__ = [
    "JavaScriptParserAdapter",
    "TypeScriptParserAdapter",
    "JavaParserAdapter",
    "CppParserAdapter",
    "CSharpParserAdapter",
    "GoParserAdapter",
    "KotlinParserAdapter",
    "RubyParserAdapter",
    "PhpParserAdapter",
    "SwiftParserAdapter",
]
