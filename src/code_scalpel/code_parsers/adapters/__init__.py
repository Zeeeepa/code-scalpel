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
"""

from .javascript_adapter import JavaScriptParserAdapter, TypeScriptParserAdapter
from .java_adapter import JavaParserAdapter  # type: ignore[import-not-found]

__all__ = [
    "JavaScriptParserAdapter",
    "TypeScriptParserAdapter",
    "JavaParserAdapter",
]
