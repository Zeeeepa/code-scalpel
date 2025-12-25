"""
BACKWARD COMPATIBILITY STUB - DO NOT EDIT.

[20251225_DEPRECATE] This module has moved to code_scalpel.security.analyzers.cross_file_taint

All exports are re-exported from the new location for backward compatibility.
Please update your imports to use:
    from code_scalpel.security.analyzers import CrossFileTaintTracker
"""

import warnings

# [20251225_DEPRECATE] Issue deprecation warning
warnings.warn(
    "Importing from 'code_scalpel.symbolic_execution_tools.cross_file_taint' is deprecated. "
    "Please use 'from code_scalpel.security.analyzers import CrossFileTaintTracker' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from code_scalpel.security.analyzers.cross_file_taint import *  # noqa: F401, F403
