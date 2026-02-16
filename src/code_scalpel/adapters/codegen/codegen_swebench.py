"""
Codegen SWE-bench Adapter

Direct imports from Codegen SDK SWE-bench extension - no reimplementation.
Provides SWE-bench integration functionality with tier unification.
"""

# Import all SWE-bench modules
from codegen.extensions.swebench import (
    enums as _enums,
    harness as _harness,
    report as _report,
    subsets as _subsets,
    success_rates as _success_rates,
    tests as _tests,
    utils as _utils,
)

# Re-export with tier unification
# All SWE-bench functionality is now Community tier accessible

# Module re-exports
enums = _enums
harness = _harness
report = _report
subsets = _subsets
success_rates = _success_rates
tests = _tests
utils = _utils

__all__ = [
    'enums',
    'harness',
    'report',
    'subsets',
    'success_rates',
    'tests',
    'utils',
]

