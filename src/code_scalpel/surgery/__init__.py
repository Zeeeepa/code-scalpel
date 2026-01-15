"""
Surgery Module - Surgical code extraction and patching for LLM-driven operations.

[20251224_REFACTOR] Created as part of Project Reorganization Issue #2.
Consolidated surgical code tools from top-level modules.

This module provides:
- SurgicalExtractor: Precision code extraction for token-efficient LLM interactions
- SurgicalPatcher: Safe code modification for LLM-driven refactoring
- UnifiedExtractor: Universal extraction across all languages
- UnifiedPatcher: Cross-language patching with language detection

Migration Guide:
    # Old imports (deprecated in v3.3.0):
    from code_scalpel.surgical_extractor import SurgicalExtractor
    from code_scalpel.surgical_patcher import SurgicalPatcher
    from code_scalpel.unified_extractor import UnifiedExtractor

    # New imports (recommended):
    from code_scalpel.surgery import SurgicalExtractor, SurgicalPatcher, UnifiedExtractor
    # Or:
    from code_scalpel.surgery.surgical_extractor import SurgicalExtractor
    from code_scalpel.surgery.surgical_patcher import SurgicalPatcher
    from code_scalpel.surgery.unified_extractor import UnifiedExtractor

# TODO [P0_CRITICAL] Complete module integration: Ensure Extractor and Patcher work seamlessly together, add workflow: extract → modify → patch → verify, Test count: 30 tests (integration, workflow)
# TODO [P1_HIGH] Add convenience functions: extract_and_patch() for common operations, diff_preview() for showing changes before apply, undo_patch() for rollback support, Test count: 20 tests (convenience functions)
# TODO [P2_MEDIUM] Add batch operations: extract_batch() for multiple symbols, patch_batch() for multiple changes, Atomic batch with rollback, Test count: 25 tests (batch operations)
# TODO [P1_HIGH] Cross-file operations: move_symbol() between files, copy_symbol() to new file, Update imports automatically, Test count: 35 tests (cross-file)
# TODO [P2_MEDIUM] Refactoring operations: rename_symbol() with callers update, inline_function(), extract_method(), Test count: 40 tests (refactoring)
# TODO [P3_LOW] Git integration: Auto-commit after patch, Patch history tracking, Branch-aware operations, Test count: 20 tests (git)
# TODO [P2_MEDIUM] Multi-language surgery: Unified API for Python, JS/TS, Java, Cross-language symbol tracking, Mixed-language projects, Test count: 50 tests (multi-lang)
# TODO [P3_LOW] IDE integration: VS Code extension commands, LSP integration, Live preview, Test count: 25 tests (IDE)
# TODO [P4_LOW] Enterprise features: Collaborative locking, Audit trail, Policy enforcement, Test count: 15 tests (enterprise)
"""

# [20251224_REFACTOR] Import from submodules
from .surgical_extractor import (
    ContextualExtraction,
    CrossFileResolution,
    CrossFileSymbol,
    ExtractionResult,
    SurgicalExtractor,
)
from .surgical_patcher import (
    PatchLanguage,
    PatchResult,
    PolyglotPatcher,
    SurgicalPatcher,
    UnifiedPatcher,
)
from .unified_extractor import (
    FileSummary,
    ImportInfo,
    Language,
    SignatureInfo,
    SymbolInfo,
    UnifiedExtractionResult,
    UnifiedExtractor,
)

__all__ = [
    # Surgical Extractor
    "SurgicalExtractor",
    "ExtractionResult",
    "ContextualExtraction",
    "CrossFileSymbol",
    "CrossFileResolution",
    # Surgical Patcher
    "SurgicalPatcher",
    "PatchResult",
    "PatchLanguage",
    "UnifiedPatcher",
    "PolyglotPatcher",
    # Unified Extractor
    "UnifiedExtractor",
    "UnifiedExtractionResult",
    "Language",
    "SymbolInfo",
    "ImportInfo",
    "FileSummary",
    "SignatureInfo",
]

__version__ = "1.0.0"
