"""
Code Scalpel Polyglot Module - Multi-language code analysis.

[20251224_DEPRECATION] v3.2.0 - This module is DEPRECATED.
Functionality has been migrated to code_parsers/ for architectural consistency:
    - polyglot/extractor.py → code_parsers/extractor.py
    - polyglot/typescript/* → code_parsers/typescript_parsers/
    - polyglot/alias_resolver.py → code_parsers/typescript_parsers/alias_resolver.py
    - polyglot/tsx_analyzer.py → code_parsers/typescript_parsers/tsx_analyzer.py
    - polyglot/contract_breach_detector.py → security/contract_breach_detector.py

This module provides backward-compatible aliases that will be removed in v3.3.0.

Migration Guide:
    # Old imports (deprecated):
    from code_scalpel.polyglot import PolyglotExtractor, Language
    from code_scalpel.polyglot.extractor import detect_language

    # New imports (recommended):
    from code_scalpel.code_parsers import PolyglotExtractor, Language
    from code_scalpel.code_parsers.extractor import detect_language
    from code_scalpel.code_parsers.typescript_parsers import TypeScriptParser

[20251214_FEATURE] v2.0.0 - Unified interface for Python, JavaScript, TypeScript, and Java.

This module provides:
- PolyglotExtractor: Multi-language code extraction
- Language detection from file extensions
- Unified IR-based analysis

TODO ITEMS:

# TODO COMMUNITY TIER Improve language detection accuracy for ambiguous file extensions
# TODO COMMUNITY TIER Add support for Go programming language extraction
# TODO COMMUNITY TIER Add support for Rust programming language extraction
# TODO COMMUNITY TIER Implement caching for repeated language detection operations
# TODO COMMUNITY TIER Add comprehensive error handling for malformed source code
# TODO COMMUNITY TIER Document polyglot extraction API with examples for each language
# TODO COMMUNITY TIER Implement fallback detection using file content heuristics
# TODO COMMUNITY TIER Add validation for language enum values
# TODO COMMUNITY TIER Create comprehensive test suite for all supported languages
# TODO COMMUNITY TIER Performance optimize language detection for large codebases

# TODO PRO TIER Add C++ language support for polyglot extraction
# TODO PRO TIER Implement Rust-specific extraction patterns
# TODO PRO TIER Add Go-specific extraction patterns
# TODO PRO TIER Integrate taint tracking across language boundaries
# TODO PRO TIER Add cross-language type inference system
# TODO PRO TIER Implement semantic analysis for language bridges
# TODO PRO TIER Add cross-language import resolution
# TODO PRO TIER Create language-specific security pattern libraries
# TODO PRO TIER Add support for custom DSLs and configuration languages
# TODO PRO TIER Implement language feature capability detection
# TODO PRO TIER Add cross-language refactoring utilities

# TODO ENTERPRISE TIER Build ML-based language detection using AST features
# TODO ENTERPRISE TIER Implement distributed extraction for large multi-language projects
# TODO ENTERPRISE TIER Add support for proprietary/custom programming languages
# TODO ENTERPRISE TIER Create language interoperability analysis system
# TODO ENTERPRISE TIER Add bytecode decompilation for compiled languages
# TODO ENTERPRISE TIER Implement quantum-safe code extraction patterns
# TODO ENTERPRISE TIER Add advanced concurrency pattern detection across languages
# TODO ENTERPRISE TIER Create enterprise audit trails for language migrations
# TODO ENTERPRISE TIER Implement federated extraction for multi-organization codebases
"""

import warnings

# [20251224_DEPRECATION] Issue deprecation warning on module import
warnings.warn(
    "The 'code_scalpel.polyglot' module is deprecated and will be removed in v3.3.0. "
    "Use 'code_scalpel.code_parsers' instead. "
    "See migration guide in module docstring.",
    DeprecationWarning,
    stacklevel=2,
)

# [20260102_REFACTOR] Backward-compat shim keeps imports below for legacy users.
# ruff: noqa: E402
# [20251224_REFACTOR] Import from new locations for backward compatibility
from code_scalpel.code_parsers.extractor import (
    EXTENSION_MAP,
    Language,
    PolyglotExtractionResult,
    PolyglotExtractor,
    detect_language,
    extract_from_code,
    extract_from_file,
)

__all__ = [
    "Language",
    "PolyglotExtractor",
    "PolyglotExtractionResult",
    "detect_language",
    "extract_from_file",
    "extract_from_code",
    "EXTENSION_MAP",
]
