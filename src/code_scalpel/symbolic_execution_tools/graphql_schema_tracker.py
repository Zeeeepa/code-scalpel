"""
BACKWARD COMPATIBILITY STUB - DO NOT EDIT.

[20251225_DEPRECATE] This module has moved to code_scalpel.integrations.protocol_analyzers.graphql

All exports are re-exported from the new location for backward compatibility.
Please update your imports to use:
    from code_scalpel.integrations.protocol_analyzers.graphql import GraphQLSchemaTracker
"""

import warnings

# [20251225_DEPRECATE] Issue deprecation warning
warnings.warn(
    "Importing from 'code_scalpel.symbolic_execution_tools.graphql_schema_tracker' is deprecated. "
    "Please use 'from code_scalpel.integrations.protocol_analyzers.graphql import GraphQLSchemaTracker' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from code_scalpel.integrations.protocol_analyzers.graphql.schema_tracker import *  # noqa: F401, F403
