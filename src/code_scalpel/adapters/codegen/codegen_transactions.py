"""
Codegen Transactions Adapter

Direct imports from Codegen SDK transaction system - no reimplementation.
Provides ACID guarantees for multi-file refactoring operations.

Features:
- Transaction management with rollback
- Validation before commit
- Diff generation
- Symbol resolution tracking
"""

from codegen.sdk.codebase.transaction_manager import TransactionManager as _TransactionManager
from codegen.sdk.codebase.transactions import Transaction as _Transaction
from codegen.sdk.codebase.validation import (
    validate_codebase as _validate_codebase,
    ValidationError as _ValidationError
)
from codegen.sdk.codebase.diff_lite import (
    generate_diff as _generate_diff,
    DiffResult as _DiffResult
)
from codegen.sdk.codebase.resolution_stack import ResolutionStack as _ResolutionStack

# Re-export with tier unification
# All transaction functionality is now Community tier accessible

# Transaction Manager
TransactionManager = _TransactionManager
"""
Transaction manager class - Community tier (unified from Enterprise)

Manages ACID transactions for codebase operations with:
- Checkpoint creation
- Rollback on failure
- Commit validation
- Nested transactions

Example:
    with codebase.transaction():
        func.rename("new_name")
        func.move_to_file("new_file.py")
        # Auto-rollback on error
"""

# Transaction
Transaction = _Transaction
"""
Transaction class - Community tier (unified from Enterprise)

Represents a single transaction with:
- Operation tracking
- State management
- Commit/rollback logic
"""

# Validation
def validate_codebase(*args, **kwargs):
    """
    Validate codebase integrity - Community tier (unified from Enterprise)
    
    Checks for:
    - Syntax errors
    - Import errors
    - Type errors
    - Circular dependencies
    
    Returns:
        ValidationResult with errors and warnings
    """
    return _validate_codebase(*args, **kwargs)


ValidationError = _ValidationError
"""
Validation error class - Community tier

Represents validation failures with:
- Error location
- Error message
- Suggested fixes
"""

# Diff Generation
def generate_diff(*args, **kwargs):
    """
    Generate diff for changes - Community tier
    
    Creates unified diff showing:
    - Added lines
    - Removed lines
    - Modified lines
    - File changes
    
    Returns:
        DiffResult with formatted diff
    """
    return _generate_diff(*args, **kwargs)


DiffResult = _DiffResult
"""
Diff result class - Community tier

Contains diff information with:
- Unified diff format
- File-level changes
- Line-level changes
- Statistics
"""

# Resolution Stack
ResolutionStack = _ResolutionStack
"""
Resolution stack class - Community tier (unified from Pro)

Tracks symbol resolution during operations with:
- Resolution history
- Circular reference detection
- Resolution caching
"""

__all__ = [
    # Transaction Management
    'TransactionManager',
    'Transaction',
    
    # Validation
    'validate_codebase',
    'ValidationError',
    
    # Diff
    'generate_diff',
    'DiffResult',
    
    # Resolution
    'ResolutionStack',
]

