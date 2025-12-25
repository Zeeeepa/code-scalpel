"""
BACKWARD COMPATIBILITY STUB - DO NOT EDIT.

[20251225_DEPRECATE] This module has moved to code_scalpel.integrations.protocol_analyzers.schema

All exports are re-exported from the new location for backward compatibility.
Please update your imports to use:
    from code_scalpel.integrations.protocol_analyzers.schema import SchemaDriftDetector
"""

import warnings

# [20251225_DEPRECATE] Issue deprecation warning
warnings.warn(
    "Importing from 'code_scalpel.symbolic_execution_tools.schema_drift_detector' is deprecated. "
    "Please use 'from code_scalpel.integrations.protocol_analyzers.schema import SchemaDriftDetector' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from code_scalpel.integrations.protocol_analyzers.schema.drift_detector import *  # noqa: F401, F403
