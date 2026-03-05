"""
Codegen Codebase Analysis Adapter

Direct imports from Codegen SDK - no reimplementation.
Provides codebase analysis functionality with tier unification.
"""

from codegen.sdk.codebase.codebase_analysis import (
    get_codebase_summary as _get_codebase_summary,
    get_file_summary as _get_file_summary,
    get_class_summary as _get_class_summary,
    get_function_summary as _get_function_summary,
    get_symbol_summary as _get_symbol_summary
)

# Re-export with tier unification applied
# All functions are now Community tier accessible

def get_codebase_summary(*args, **kwargs):
    """
    Get codebase summary - Community tier
    Direct passthrough to Codegen SDK
    """
    return _get_codebase_summary(*args, **kwargs)


def get_file_summary(*args, **kwargs):
    """
    Get file summary - Community tier
    Direct passthrough to Codegen SDK
    """
    return _get_file_summary(*args, **kwargs)


def get_class_summary(*args, **kwargs):
    """
    Get class summary - Community tier
    Direct passthrough to Codegen SDK
    """
    return _get_class_summary(*args, **kwargs)


def get_function_summary(*args, **kwargs):
    """
    Get function summary - Community tier
    Direct passthrough to Codegen SDK
    """
    return _get_function_summary(*args, **kwargs)


def get_symbol_summary(*args, **kwargs):
    """
    Get symbol summary - Community tier (unified from Pro)
    Direct passthrough to Codegen SDK
    """
    return _get_symbol_summary(*args, **kwargs)

