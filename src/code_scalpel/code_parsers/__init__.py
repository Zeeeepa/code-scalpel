# __init__.py
"""
Code Parser Module - Multi-language code parsing and analysis.

This module provides a unified interface for parsing code in various languages
using different analysis tools.

[20251221_DEPRECATION] Old parsers/ module is DEPRECATED and should be removed:
    - parsers/ is a legacy minimal implementation with only Python support
    - code_parser/ is the current production-grade implementation
    - parsers/ is no longer used in production (only in legacy tests)

    See consolidation plan in TODOs below.
"""
from .base_parser import BaseParser, Language, ParseResult, PreprocessorConfig
from .interface import IParser
from .factory import ParserFactory
from .python_parser import PythonParser

# Import parsers from python_parsers submodule
# These use lazy imports to avoid loading all dependencies at startup
from .python_parsers import (
    PythonASTParser,
    RuffParser,
    # These will be available when their modules are complete
    # BanditParser,
    # Flake8Parser,
    # MypyParser,
    # PylintParser,
    # PydocstyleParser,
    # PycodestyleParser,
    # ProspectorParser,
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
]

# [20251221_TODO] Remove deprecated parsers/ module:
#     - Audit all imports from parsers/ to ensure they use code_parser/
#     - Update remaining test files (test_base_parser.py, test_parser_factory.py)
#     - Delete src/code_scalpel/parsers/ directory entirely
#     - Verify no external dependencies on parsers/ package

# [20251221_TODO] Consolidate parser factory and interfaces:
#     - Merge BaseParser and IParser interfaces (currently both exist)
#     - Standardize on single factory pattern (currently in factory.py)
#     - Move Language enum to top-level exports
#     - Add backwards compatibility alias if needed for external users

# [20251221_TODO] Complete multi-language parser implementation:
#     - Implement missing language parsers (PHP, Ruby, Swift stubs are empty)
#     - Add comprehensive test coverage for all 8+ language families
#     - Implement unified error reporting across all languages
#     - Add language feature detection (ES6+, Python 3.9+, Java 17+, etc.)

# [20251221_TODO] Add tool-aware parsing configuration:
#     - Allow specifying which tools/linters to use per language
#     - Implement tool version detection and compatibility checking
#     - Add tool output caching keyed by (tool, version, code_hash)
#     - Support tool-specific configuration files (eslintrc, mypy.ini, etc.)
