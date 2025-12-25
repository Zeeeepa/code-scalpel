"""
BACKWARD COMPATIBILITY STUB - DO NOT EDIT.

[20251225_DEPRECATE] This module has moved to code_scalpel.integrations.protocol_analyzers.grpc

All exports are re-exported from the new location for backward compatibility.
Please update your imports to use:
    from code_scalpel.integrations.protocol_analyzers.grpc import GrpcContractAnalyzer
"""

import warnings

# [20251225_DEPRECATE] Issue deprecation warning
warnings.warn(
    "Importing from 'code_scalpel.symbolic_execution_tools.grpc_contract_analyzer' is deprecated. "
    "Please use 'from code_scalpel.integrations.protocol_analyzers.grpc import GrpcContractAnalyzer' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from code_scalpel.integrations.protocol_analyzers.grpc.contract_analyzer import *  # noqa: F401, F403
