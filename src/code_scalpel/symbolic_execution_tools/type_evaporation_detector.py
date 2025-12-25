"""
BACKWARD COMPATIBILITY STUB - DO NOT EDIT.

[20251225_DEPRECATE] This module has moved to code_scalpel.security.type_safety.type_evaporation_detector

All exports are re-exported from the new location for backward compatibility.
Please update your imports to use:
    from code_scalpel.security.type_safety import TypeEvaporationDetector, TypeEvaporationVulnerability
"""

import warnings

# [20251225_DEPRECATE] Issue deprecation warning
warnings.warn(
    "Importing from 'code_scalpel.symbolic_execution_tools.type_evaporation_detector' is deprecated. "
    "Please use 'from code_scalpel.security.type_safety import TypeEvaporationDetector' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from code_scalpel.security.type_safety.type_evaporation_detector import *  # noqa: F401, F403
