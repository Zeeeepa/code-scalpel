"""
Type Safety - Type-related security analysis.

[20251225_FEATURE] Created as part of Project Reorganization Issue #9.

This module contains type safety analysis tools:
- type_evaporation_detector.py: TypeScript type boundary vulnerabilities
"""

from .type_evaporation_detector import \
    analyze_type_evaporation_cross_file  # [20251225_BUGFIX] Export function
from .type_evaporation_detector import (TypeEvaporationDetector,
                                        TypeEvaporationVulnerability)

__all__ = [
    "TypeEvaporationDetector",
    "TypeEvaporationVulnerability",
    "analyze_type_evaporation_cross_file",
]
