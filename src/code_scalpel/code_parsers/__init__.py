# __init__.py
"""
Code Parser Module - Multi-language code parsing and analysis.

This module provides a unified interface for parsing code in various languages
using different analysis tools.

[20251224_REFACTOR] polyglot/ module absorbed into code_parsers/:
    - polyglot/extractor.py → code_parsers/extractor.py
    - polyglot/typescript/* → code_parsers/typescript_parsers/
    - polyglot/alias_resolver.py → code_parsers/typescript_parsers/alias_resolver.py
    - polyglot/tsx_analyzer.py → code_parsers/typescript_parsers/tsx_analyzer.py
    - polyglot/contract_breach_detector.py → security/contract_breach_detector.py

    The polyglot/ module now re-exports from here with deprecation warnings.

[20251221_DEPRECATION] Old parsers/ module is DEPRECATED and should be removed:
    - parsers/ is a legacy minimal implementation with only Python support
    - code_parser/ is the current production-grade implementation
    - parsers/ is no longer used in production (only in legacy tests)

"""

from .base_parser import BaseParser, Language, ParseResult, PreprocessorConfig

# [20251224_FEATURE] Import from polyglot extractor (migrated from polyglot/)
from .extractor import (
    EXTENSION_MAP,
)
from .extractor import (
    Language as PolyglotLanguage,  # Alias to avoid conflict with base_parser.Language
)
from .extractor import (
    PolyglotExtractionResult,
    PolyglotExtractor,
    detect_language,
    extract_from_code,
    extract_from_file,
)
from .factory import ParserFactory
from .interface import IParser
from .python_parser import PythonParser

# Import parsers from python_parsers submodule
# These use lazy imports to avoid loading all dependencies at startup
from .python_parsers import (  # These will be available when their modules are complete; BanditParser,; Flake8Parser,; MypyParser,; PylintParser,; PydocstyleParser,; PycodestyleParser,; ProspectorParser,
    PythonASTParser,
    RuffParser,
)

# [20251224_FEATURE] TypeScript parser exports (migrated from polyglot/typescript/)
from .typescript_parsers import (
    AliasResolver,
    DecoratorAnalyzer,
    TypeNarrowing,
    TypeScriptAnalyzer,
    TypeScriptParser,
)

__all__ = [
    # Base classes
    "BaseParser",
    "Language",
    "ParseResult",
    "PreprocessorConfig",
    "IParser",
    "ParserFactory",
    "PythonParser",
    # Python parsers
    "PythonASTParser",
    "RuffParser",
    # Polyglot extractor (migrated from polyglot/)
    "PolyglotExtractor",
    "PolyglotExtractionResult",
    "detect_language",
    "extract_from_file",
    "extract_from_code",
    "EXTENSION_MAP",
    "PolyglotLanguage",
    # TypeScript parsers (migrated from polyglot/typescript/)
    "TypeScriptParser",
    "TypeScriptAnalyzer",
    "TypeNarrowing",
    "DecoratorAnalyzer",
    "AliasResolver",
]

# ============================================================================
# ============================================================================
# COMMUNITY TIER - Core Parser Infrastructure (P0-P2)
# ============================================================================

# [P0_CRITICAL] Remove deprecated parsers/ module:
#     - Audit all imports from parsers/ to ensure they use code_parser/
#     - Update remaining test files (test_base_parser.py, test_parser_factory.py)
#     - Delete src/code_scalpel/parsers/ directory entirely
#     - Verify no external dependencies on parsers/ package
#     - Test count: 25 tests (migration validation, import checks, backward compat)

# [P1_HIGH] Consolidate parser factory and interfaces:
#     - Merge BaseParser and IParser interfaces (currently both exist)
#     - Standardize on single factory pattern (currently in factory.py)
#     - Move Language enum to top-level exports
#     - Add backwards compatibility alias if needed for external users
#     - Create unified ParseResult format across all parsers
#     - Test count: 20 tests (interface consistency, factory methods)

# [P1_HIGH] Complete multi-language parser implementation:
#     - Implement missing language parsers (PHP, Ruby, Swift stubs are empty)
#     - Add comprehensive test coverage for all 8+ language families
#     - Implement unified error reporting across all languages
#     - Add language feature detection (ES6+, Python 3.9+, Java 17+, etc.)
#     - Support syntax variants (JSX, TSX, Kotlin Script, etc.)
#     - Test count: 30 tests (parser functionality, language detection)

# [P2_MEDIUM] Add module exports and initialization:
#     - Export all language-specific parsers from __init__.py
#     - Add lazy loading for parsers to reduce startup time
#     - Create parser capability registry (supports_incremental, etc.)
#     - Add get_available_parsers() function
#     - Support parser plugin registration
#     - Test count: 15 tests (exports, lazy loading, registry)

# [P2_MEDIUM] Improve error handling and diagnostics:
#     - Standardize error codes across all parsers
#     - Add detailed error messages with fix suggestions
#     - Implement error recovery for partial parsing
#     - Add parser diagnostics endpoint
#     - Test count: 20 tests (error handling, diagnostics)

# ============================================================================
# PRO TIER - Advanced Parser Features (P1-P3)
# ============================================================================

# [P1_HIGH] Add tool-aware parsing configuration:
#     - Allow specifying which tools/linters to use per language
#     - Implement tool version detection and compatibility checking
#     - Add tool output caching keyed by (tool, version, code_hash)
#     - Support tool-specific configuration files (eslintrc, mypy.ini, etc.)
#     - Add tool result normalization across different linters
#     - Test count: 25 tests (tool integration, config loading, caching)

# [P1_HIGH] Implement incremental parsing:
#     - Add support for parsing only changed sections
#     - Implement AST diffing for efficient updates
#     - Cache parsed results with invalidation strategy
#     - Support streaming parsing for large files
#     - Test count: 25 tests (incremental updates, caching, performance)

# [P2_MEDIUM] Add semantic analysis integration:
#     - Integrate with type checkers (mypy, Flow, TypeScript)
#     - Add symbol resolution across modules
#     - Implement import path resolution
#     - Support workspace-wide semantic analysis
#     - Test count: 30 tests (semantic analysis, cross-module)

# [P2_MEDIUM] Implement parser middleware system:
#     - Add pre-parsing hooks (normalization, macro expansion)
#     - Add post-parsing hooks (validation, transformation)
#     - Support custom parser plugins
#     - Add parser pipeline configuration
#     - Test count: 20 tests (middleware, hooks, plugins)

# [P3_LOW] Add code generation from parsed AST:
#     - Implement AST-to-source generation
#     - Support code formatting options
#     - Add source map generation
#     - Support partial code generation
#     - Test count: 25 tests (generation, formatting, source maps)

# ============================================================================
# ENTERPRISE TIER - Distributed & Enterprise Features (P2-P4)
# ============================================================================

# [P2_MEDIUM] Implement distributed parsing:
#     - Add work queue for parallel parsing
#     - Support distributed parser workers
#     - Implement result aggregation across workers
#     - Add progress tracking for large codebases
#     - Test count: 30 tests (distribution, workers, aggregation)

# [P2_MEDIUM] Add enterprise compliance features:
#     - Implement parsing policy enforcement
#     - Add audit logging for all parsing operations
#     - Support parsing quota management
#     - Add compliance reporting (HIPAA, SOC2, GDPR)
#     - Test count: 25 tests (compliance, audit, quotas)

# [P3_LOW] Implement parser telemetry and monitoring:
#     - Add parsing metrics collection (time, memory, file count)
#     - Implement OpenTelemetry integration
#     - Add performance profiling hooks
#     - Support custom metrics exporters
#     - Test count: 20 tests (telemetry, monitoring, profiling)

# [P3_LOW] Add multi-tenant parser isolation:
#     - Implement tenant-specific parser configurations
#     - Add resource isolation per tenant
#     - Support tenant-specific tool versions
#     - Add cross-tenant usage analytics
#     - Test count: 25 tests (multi-tenancy, isolation, analytics)

# [P4_LOW] Implement ML-based parsing optimization:
#     - Add ML model for language detection confidence
#     - Implement parsing strategy selection via ML
#     - Add anomaly detection for malformed code
#     - Support adaptive parser configuration
#     - Test count: 30 tests (ML integration, optimization)

# ============================================================================
# TOTAL TEST ESTIMATE: 420 tests (140 COMMUNITY + 145 PRO + 135 ENTERPRISE)
# ============================================================================
