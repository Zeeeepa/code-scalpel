"""
[20251221_DEPRECATION] DEPRECATED MODULE - Use code_parser/ instead.

This module (parsers/) is a legacy minimal implementation kept only for
backward compatibility with old tests. It is NOT used in production.

MIGRATION GUIDE:
    OLD: from code_scalpel.parsers import BaseParser, PythonParser
    NEW: from code_scalpel.code_parser import BaseParser, PythonParser

The new code_parser/ module provides:
    - 8+ programming languages (vs. Python only in this old module)
    - 40+ parser implementations covering multiple tools per language
    - Structured error reporting and metrics
    - Type-safe Language enum and ParseResult dataclass
    - Factory pattern with language auto-detection

    - Update imports in tests to use code_scalpel.code_parser
    - Delete src/code_scalpel/parsers/ directory
    - Verify no external code depends on this module
"""

from .base_parser import BaseParser
from .factory import ParserFactory
from .python_parser import PythonParser

__all__ = ["BaseParser", "PythonParser", "ParserFactory"]
