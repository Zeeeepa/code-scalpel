"""ParserFactory - Language-aware parser instantiation.

[20251221_FEATURE] Factory pattern for multi-language code parsing.

============================================================================
TODO ITEMS: code_parsers/factory.py
============================================================================
COMMUNITY TIER - Core Factory Features (P0-P2)
============================================================================

[P0_CRITICAL] Auto-register parsers from language subdirectories:
    - Scan language_parsers/ directories on import
    - Dynamically register all IParser implementations
    - Support hot-reloading of parser modules
    - Add parser version compatibility checking
    - Test count: 20 tests (auto-registration, discovery, compatibility)

[P1_HIGH] Implement lazy loading for parsers:
    - Defer parser imports until first use
    - Reduce startup time for large parser collections
    - Add parser preloading hints for common languages
    - Support eager loading mode for performance
    - Test count: 15 tests (lazy loading, startup time, preloading)

[P1_HIGH] Enhanced language detection:
    - Support shebang-based language detection (#!/usr/bin/python)
    - Add magic comment detection (# -*- coding: utf-8 -*-,  // @ts-check)
    - Integrate with .editorconfig for per-project settings
    - Add content-based language detection fallback
    - Support compound extensions (.spec.ts, .test.js)
    - Test count: 25 tests (detection accuracy, edge cases)

[P2_MEDIUM] Parser capability introspection:
    - Add get_capabilities(language) returning parser features
    - Support querying: supports_incremental, supports_types, etc.
    - Add parser feature matrix display
    - Implement capability-based parser selection
    - Test count: 15 tests (introspection, capability queries)

[P2_MEDIUM] Error handling and diagnostics:
    - Add detailed error messages for unsupported languages
    - Suggest installing missing parser dependencies
    - Add parser health check endpoint
    - Implement parser fallback chains
    - Test count: 20 tests (error handling, fallbacks, diagnostics)

============================================================================
PRO TIER - Advanced Factory Features (P1-P3)
============================================================================

[P1_HIGH] Parser backend selection:
    - Add get_parser(language, backend="tree-sitter") for explicit backend
    - Support multiple backends per language (AST, tree-sitter, regex)
    - Implement smart backend selection based on use case
    - Add backend performance profiling
    - Test count: 25 tests (backend selection, performance)

[P1_HIGH] Parser configuration management:
    - Support parser configuration objects (strict mode, feature flags)
    - Add per-project parser configuration files
    - Implement configuration inheritance (global → project → file)
    - Add configuration validation and schema
    - Test count: 20 tests (config loading, validation, inheritance)

[P2_MEDIUM] Parser benchmarking and optimization:
    - Add parser benchmarking to select fastest available parser
    - Implement adaptive parser selection based on file size
    - Add parser performance metrics collection
    - Support parser warm-up for frequently used languages
    - Test count: 25 tests (benchmarking, optimization, metrics)

[P2_MEDIUM] Multi-strategy parsing:
    - Support running multiple parsers in parallel
    - Aggregate results from multiple parser strategies
    - Add consensus-based error detection
    - Implement parser result merging
    - Test count: 30 tests (multi-strategy, aggregation, consensus)

[P3_LOW] Parser plugin system:
    - Add register_plugin(name, parser_class, languages) API
    - Support third-party parser registration
    - Implement plugin dependency resolution
    - Add plugin marketplace metadata
    - Test count: 20 tests (plugins, registration, dependencies)

============================================================================
ENTERPRISE TIER - Enterprise Factory Features (P2-P4)
============================================================================

[P2_MEDIUM] Multi-tenant parser isolation:
    - Support tenant-specific parser configurations
    - Add parser resource quotas per tenant
    - Implement tenant-specific parser versions
    - Add cross-tenant parser usage analytics
    - Test count: 25 tests (multi-tenancy, isolation, quotas)

[P2_MEDIUM] Distributed parser coordination:
    - Add parser discovery in distributed systems
    - Support remote parser invocation
    - Implement parser load balancing
    - Add parser failover and redundancy
    - Test count: 30 tests (distribution, coordination, failover)

[P3_LOW] Enterprise governance:
    - Add parser usage audit logging
    - Implement parser access control (RBAC)
    - Support compliance-mandated parser configurations
    - Add parser governance dashboards
    - Test count: 20 tests (governance, audit, compliance)

[P3_LOW] Advanced caching strategies:
    - Implement distributed parser result caching
    - Add cache invalidation strategies
    - Support cache warming for common patterns
    - Add cache compression and encryption
    - Test count: 25 tests (caching, invalidation, encryption)

[P4_LOW] ML-driven parser optimization:
    - Add ML model for optimal parser selection
    - Implement predictive parser preloading
    - Support adaptive parser configuration
    - Add anomaly detection for parser failures
    - Test count: 30 tests (ML integration, optimization)

============================================================================
TOTAL TEST ESTIMATE: 370 tests (115 COMMUNITY + 120 PRO + 135 ENTERPRISE)
============================================================================
"""

from typing import Dict, Optional, Type

from .interface import IParser, Language
from .python_parser import PythonParser


class ParserFactory:
    """Factory for creating language-specific parsers.

    [20251221_FEATURE] Unified parser instantiation across all languages.
    """

    _parsers: Dict[Language, Type[IParser]] = {
        Language.PYTHON: PythonParser,
    }

    # Extended extension mapping for comprehensive language detection
    _extension_map: Dict[str, Language] = {
        # Python
        "py": Language.PYTHON,
        "pyw": Language.PYTHON,
        "pyi": Language.PYTHON,
        # JavaScript
        "js": Language.JAVASCRIPT,
        "mjs": Language.JAVASCRIPT,
        "cjs": Language.JAVASCRIPT,
        "jsx": Language.JAVASCRIPT,
        # TypeScript
        "ts": Language.TYPESCRIPT,
        "mts": Language.TYPESCRIPT,
        "cts": Language.TYPESCRIPT,
        "tsx": Language.TYPESCRIPT,
        # Java
        "java": Language.JAVA,
        # C/C++
        "c": Language.CPP,
        "cpp": Language.CPP,
        "cc": Language.CPP,
        "cxx": Language.CPP,
        "h": Language.CPP,
        "hpp": Language.CPP,
        "hxx": Language.CPP,
    }

    @classmethod
    def get_parser(cls, language: Language, backend: Optional[str] = None) -> IParser:
        """Get a parser instance for the specified language.

        Args:
            language: Target programming language
            backend: Optional parser backend (e.g., "tree-sitter", "ast", "regex")

        Returns:
            Parser instance for the language

        Raises:
            ValueError: If no parser is registered for the language
        """
        parser_cls = cls._parsers.get(language)
        if not parser_cls:
            raise ValueError(f"No parser registered for language: {language}")
        return parser_cls()

    @classmethod
    def register_parser(cls, language: Language, parser_cls: Type[IParser]) -> None:
        """Register a new parser for a language.

        Args:
            language: Target programming language
            parser_cls: Parser class implementing IParser
        """
        cls._parsers[language] = parser_cls

    @classmethod
    def is_registered(cls, language: Language) -> bool:
        """Check if a parser is registered for the language."""
        return language in cls._parsers

    @classmethod
    def list_registered(cls) -> list[Language]:
        """List all registered languages."""
        return list(cls._parsers.keys())

    @classmethod
    def detect_language(cls, filename: str) -> Language:
        """Detect language from filename extension.

        Args:
            filename: File path or name with extension

        Returns:
            Detected Language enum value, or Language.UNKNOWN
        """
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        return cls._extension_map.get(ext, Language.UNKNOWN)

    @classmethod
    def from_file(cls, filepath: str, backend: Optional[str] = None) -> IParser:
        """Create parser by detecting language from file path.

        [20251221_FEATURE] Convenience method for file-based parsing.

        Args:
            filepath: Path to source file
            backend: Optional parser backend preference

        Returns:
            Appropriate parser for the file's language

        Raises:
            ValueError: If language cannot be detected or no parser available
        """
        language = cls.detect_language(filepath)
        if language == Language.UNKNOWN:
            raise ValueError(f"Cannot detect language for file: {filepath}")
        return cls.get_parser(language, backend)


# Auto-register additional parsers when their modules are available
def _register_available_parsers() -> None:
    """Register parsers that are available in the installation.

    [20251221_FEATURE] Uses IParser adapters for unified interface.
    """
    # JavaScript parser via adapter
    try:
        from .adapters.javascript_adapter import JavaScriptParserAdapter

        ParserFactory.register_parser(Language.JAVASCRIPT, JavaScriptParserAdapter)
    except ImportError:
        pass

    # TypeScript parser via adapter
    try:
        from .adapters.javascript_adapter import TypeScriptParserAdapter

        ParserFactory.register_parser(Language.TYPESCRIPT, TypeScriptParserAdapter)
    except ImportError:
        pass

    # Java parser via adapter
    try:
        from .adapters.java_adapter import JavaParserAdapter

        ParserFactory.register_parser(Language.JAVA, JavaParserAdapter)
    except ImportError:
        pass


# Run auto-registration on module load
_register_available_parsers()
