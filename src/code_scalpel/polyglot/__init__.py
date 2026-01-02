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

COMMUNITY TIER (Core Functionality):
1. TODO: Improve language detection accuracy for ambiguous file extensions
2. TODO: Add support for Go programming language extraction
3. TODO: Add support for Rust programming language extraction
4. TODO: Implement caching for repeated language detection operations
5. TODO: Add comprehensive error handling for malformed source code
6. TODO: Document polyglot extraction API with examples for each language
7. TODO: Implement fallback detection using file content heuristics
8. TODO: Add validation for language enum values
9. TODO: Create comprehensive test suite for all supported languages
10. TODO: Performance optimize language detection for large codebases

PRO TIER (Enhanced Features):
11. TODO: Add C++ language support for polyglot extraction
12. TODO: Implement Rust-specific extraction patterns
13. TODO: Add Go-specific extraction patterns
14. TODO: Integrate taint tracking across language boundaries
15. TODO: Add cross-language type inference system
16. TODO: Implement semantic analysis for language bridges
17. TODO: Add cross-language import resolution
18. TODO: Create language-specific security pattern libraries
19. TODO: Add support for custom DSLs and configuration languages
20. TODO: Implement language feature capability detection
21. TODO: Add cross-language refactoring utilities

ENTERPRISE TIER (Advanced Capabilities):
22. TODO: Build ML-based language detection using AST features
23. TODO: Implement distributed extraction for large multi-language projects
24. TODO: Add support for proprietary/custom programming languages
25. TODO: Create language interoperability analysis system
26. TODO: Add bytecode decompilation for compiled languages
27. TODO: Implement quantum-safe code extraction patterns
28. TODO: Add advanced concurrency pattern detection across languages
29. TODO: Create enterprise audit trails for language migrations
30. TODO: Implement federated extraction for multi-organization codebases
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

# [20251224_REFACTOR] Import from new locations for backward compatibility
from code_scalpel.code_parsers.extractor import (EXTENSION_MAP, Language,
                                                 PolyglotExtractionResult,
                                                 PolyglotExtractor,
                                                 detect_language,
                                                 extract_from_code,
                                                 extract_from_file)

__all__ = [
    "Language",
    "PolyglotExtractor",
    "PolyglotExtractionResult",
    "detect_language",
    "extract_from_file",
    "extract_from_code",
    "EXTENSION_MAP",
]
