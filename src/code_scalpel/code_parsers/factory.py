"""ParserFactory - Language-aware parser instantiation.

[20251221_FEATURE] Factory pattern for multi-language code parsing.

# TODO [COMMUNITY] Scan language_parsers/ directories on import
# TODO [COMMUNITY] Dynamically register all IParser implementations
# TODO [COMMUNITY] Support hot-reloading of parser modules
# TODO [COMMUNITY] Add parser version compatibility checking
# TODO [COMMUNITY] Defer parser imports until first use
# TODO [COMMUNITY] Reduce startup time for large parser collections
# TODO [COMMUNITY] Add parser preloading hints for common languages
# TODO [COMMUNITY] Support eager loading mode for performance
# TODO [COMMUNITY] Support shebang-based language detection (#!/usr/bin/python)
# TODO [COMMUNITY] Add magic comment detection (# -*- coding: utf-8 -*-, // @ts-check)
# TODO [COMMUNITY] Integrate with .editorconfig for per-project settings
# TODO [COMMUNITY] Add content-based language detection fallback
# TODO [COMMUNITY] Support compound extensions (.spec.ts, .test.js)
# TODO [COMMUNITY] Add get_capabilities(language) returning parser features
# TODO [COMMUNITY] Support querying supports_incremental, supports_types, etc.
# TODO [COMMUNITY] Add parser feature matrix display
# TODO [COMMUNITY] Implement capability-based parser selection
# TODO [COMMUNITY] Add detailed error messages for unsupported languages
# TODO [COMMUNITY] Suggest installing missing parser dependencies
# TODO [COMMUNITY] Add parser health check endpoint
# TODO [COMMUNITY] Implement parser fallback chains
# TODO [PRO] Add get_parser(language, backend="tree-sitter") for explicit backend
# TODO [PRO] Support multiple backends per language (AST, tree-sitter, regex)
# TODO [PRO] Implement smart backend selection based on use case
# TODO [PRO] Add backend performance profiling
# TODO [PRO] Support parser configuration objects (strict mode, feature flags)
# TODO [PRO] Add per-project parser configuration files
# TODO [PRO] Implement configuration inheritance (global → project → file)
# TODO [PRO] Add configuration validation and schema
# TODO [PRO] Add parser benchmarking to select fastest available parser
# TODO [PRO] Implement adaptive parser selection based on file size
# TODO [PRO] Add parser performance metrics collection
# TODO [PRO] Support parser warm-up for frequently used languages
# TODO [PRO] Support running multiple parsers in parallel
# TODO [PRO] Aggregate results from multiple parser strategies
# TODO [PRO] Add consensus-based error detection
# TODO [PRO] Implement parser result merging
# TODO [PRO] Add register_plugin(name, parser_class, languages) API
# TODO [PRO] Support third-party parser registration
# TODO [PRO] Implement plugin dependency resolution
# TODO [PRO] Add plugin marketplace metadata
# TODO [ENTERPRISE] Support tenant-specific parser configurations
# TODO [ENTERPRISE] Add parser resource quotas per tenant
# TODO [ENTERPRISE] Implement tenant-specific parser versions
# TODO [ENTERPRISE] Add cross-tenant parser usage analytics
# TODO [ENTERPRISE] Add parser discovery in distributed systems
# TODO [ENTERPRISE] Support remote parser invocation
# TODO [ENTERPRISE] Implement parser load balancing
# TODO [ENTERPRISE] Add parser failover and redundancy
# TODO [ENTERPRISE] Add parser usage audit logging
# TODO [ENTERPRISE] Implement parser access control (RBAC)
# TODO [ENTERPRISE] Support compliance-mandated parser configurations
# TODO [ENTERPRISE] Add parser governance dashboards
# TODO [ENTERPRISE] Implement distributed parser result caching
# TODO [ENTERPRISE] Add cache invalidation strategies
# TODO [ENTERPRISE] Support cache warming for common patterns
# TODO [ENTERPRISE] Add cache compression and encryption
# TODO [ENTERPRISE] Add ML model for optimal parser selection
# TODO [ENTERPRISE] Implement predictive parser preloading
# TODO [ENTERPRISE] Support adaptive parser configuration
# TODO [ENTERPRISE] Add anomaly detection for parser failures
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
