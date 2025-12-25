"""
BACKWARD COMPATIBILITY STUB - DO NOT EDIT.

[20251225_DEPRECATE] This module has moved to code_scalpel.governance.governance_config

All exports are re-exported from the new location for backward compatibility.
Please update your imports to use:
    from code_scalpel.governance import GovernanceConfig, GovernanceConfigLoader
"""

import warnings

# [20251225_DEPRECATE] Issue deprecation warning
warnings.warn(
    "Importing from 'code_scalpel.config.governance_config' is deprecated. "
    "Please use 'from code_scalpel.governance import GovernanceConfig' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from code_scalpel.governance.governance_config import *  # noqa: F401, F403
