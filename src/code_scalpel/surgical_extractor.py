"""
SurgicalExtractor - DEPRECATED: Moved to code_scalpel.surgery.surgical_extractor.

# [20251224_DEPRECATE] This module has been moved to surgery/surgical_extractor.py
# as part of Issue #2 in PROJECT_REORG_REFACTOR.md Phase 1.
# This file provides backward-compatibility aliases.
# Import from code_scalpel.surgery.surgical_extractor instead.

Migration:
    # Old (deprecated):
    from code_scalpel.surgical_extractor import SurgicalExtractor

    # New (recommended):
    from code_scalpel.surgery import SurgicalExtractor
"""

import warnings

warnings.warn(
    "code_scalpel.surgical_extractor is deprecated. "
    "Import from code_scalpel.surgery instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from new location for backward compatibility
from code_scalpel.surgery.surgical_extractor import (
    SurgicalExtractor,
    ExtractionResult,
    ContextualExtraction,
    CrossFileSymbol,
    CrossFileResolution,
    # Convenience functions
    extract_function,
    extract_class,
    extract_method,
    extract_with_context,
)

__all__ = [
    "SurgicalExtractor",
    "ExtractionResult",
    "ContextualExtraction",
    "CrossFileSymbol",
    "CrossFileResolution",
    "extract_function",
    "extract_class",
    "extract_method",
    "extract_with_context",
]
