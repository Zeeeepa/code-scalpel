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

# TODO [COMMUNITY/P0] Complete adapter implementation: Create CppParserAdapter (C/C++ support)
# TODO [COMMUNITY/P0] Complete adapter implementation: Create GoParserAdapter (Go support)
# TODO [COMMUNITY/P0] Complete adapter implementation: Create RubyParserAdapter (Ruby support)
# TODO [COMMUNITY/P0] Complete adapter implementation: Create PhpParserAdapter (PHP support)
# TODO [COMMUNITY/P0] Complete adapter implementation: Create SwiftParserAdapter (Swift support)
# TODO [COMMUNITY/P1] Standardize adapter interface: Add get_capabilities() to all adapters
# TODO [COMMUNITY/P1] Standardize adapter interface: Implement consistent error handling
# TODO [COMMUNITY/P1] Standardize adapter interface: Add parser version tracking
# TODO [COMMUNITY/P1] Add adapter auto-registration: Auto-discover adapters in this directory
# TODO [COMMUNITY/P1] Add adapter auto-registration: Register with ParserFactory on import
# TODO [COMMUNITY/P2] Improve error handling: Standardize error conversion across adapters
# TODO [COMMUNITY/P2] Add adapter testing utilities: Create common adapter test base class
# TODO [PRO/P1] Implement multi-backend support: Allow multiple parsers per language
# TODO [PRO/P1] Add semantic analysis adapters: Wrap type checkers (mypy, Flow, tsc)
# TODO [PRO/P2] Implement adapter caching: Cache parse results per adapter
# TODO [PRO/P2] Add linter adapters: Create unified linter adapter interface
# TODO [PRO/P3] Implement transformation adapters: Add code formatting adapters (Black, Prettier)
# TODO [ENTERPRISE/P2] Add distributed adapter coordination: Support remote parser invocation
# TODO [ENTERPRISE/P2] Implement enterprise compliance: Add audit logging to all adapters
# TODO [ENTERPRISE/P3] Add multi-tenant adapter isolation: Support tenant-specific adapters
# TODO [ENTERPRISE/P3] Implement adapter telemetry: Add OpenTelemetry integration
# TODO [ENTERPRISE/P4] Add ML-driven adapter selection: Use ML to select optimal adapter

from .java_adapter import JavaParserAdapter  # type: ignore[import-not-found]
from .javascript_adapter import JavaScriptParserAdapter, TypeScriptParserAdapter

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
