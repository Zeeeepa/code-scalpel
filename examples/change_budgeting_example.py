"""
Change Budgeting Example - Blast Radius Control

[20251216_FEATURE] Demonstrates how to use Change Budgeting to limit
the scope of agent modifications and prevent runaway changes.

This example shows:
1. Creating operations with file changes
2. Validating operations against budget constraints
3. Handling budget violations
4. Configuring different budget policies
"""

from code_scalpel.policy import (
    Operation,
    FileChange,
    ChangeBudget,
)


def example_basic_validation():
    """Example 1: Basic budget validation."""
    print("=" * 60)
    print("Example 1: Basic Budget Validation")
    print("=" * 60)

    # Create a budget with default limits
    budget = ChangeBudget(
        {
            "max_files": 5,
            "max_lines_per_file": 100,
            "max_total_lines": 300,
            "max_complexity_increase": 10,
            "allowed_file_patterns": ["*.py", "*.ts", "*.java"],
            "forbidden_paths": [".git/", "node_modules/", "__pycache__/"],
        }
    )

    # Create an operation within budget
    small_operation = Operation(
        changes=[
            FileChange(
                file_path="src/utils.py",
                added_lines=["def helper():", "    return 42"],
                original_code="",
                modified_code="def helper():\n    return 42",
            )
        ],
        description="Add helper function",
    )

    decision = budget.validate_operation(small_operation)

    print(f"Operation: {small_operation.description}")
    print(f"Files affected: {len(small_operation.affected_files)}")
    print(f"Lines changed: {small_operation.total_lines_changed}")
    print(f"Decision: {'✓ ALLOWED' if decision.allowed else '✗ DENIED'}")
    print(f"Reason: {decision.reason}")
    print()


def example_max_files_violation():
    """Example 2: Violating max_files limit."""
    print("=" * 60)
    print("Example 2: Max Files Violation")
    print("=" * 60)

    budget = ChangeBudget({"max_files": 3})

    # Operation affecting 5 files (exceeds limit)
    large_operation = Operation(
        changes=[
            FileChange(file_path=f"src/file{i}.py", added_lines=["x = 1"])
            for i in range(5)
        ],
        description="Modify 5 files",
    )

    decision = budget.validate_operation(large_operation)

    print(f"Operation: {large_operation.description}")
    print(f"Files affected: {len(large_operation.affected_files)}")
    print(f"Budget max_files: {budget.max_files}")
    print(f"Decision: {'✓ ALLOWED' if decision.allowed else '✗ DENIED'}")
    print()
    if not decision.allowed:
        print("Error Message:")
        print(decision.get_error_message())
    print()


def example_complexity_increase():
    """Example 3: Complexity increase validation."""
    print("=" * 60)
    print("Example 3: Complexity Increase Validation")
    print("=" * 60)

    budget = ChangeBudget({"max_complexity_increase": 5})

    # Simple code (complexity = 1)
    original_code = """
def simple():
    return 42
"""

    # Complex code (complexity = 8)
    modified_code = """
def complex():
    if x > 0:  # +1
        if y > 0:  # +1
            for i in range(10):  # +1
                while j < 5:  # +1
                    if z > 0:  # +1
                        if a or b:  # +2 (if + or)
                            return i
    return 0
"""

    operation = Operation(
        changes=[
            FileChange(
                file_path="src/complex.py",
                original_code=original_code,
                modified_code=modified_code,
            )
        ],
        description="Add complex logic",
    )

    decision = budget.validate_operation(operation)

    print(f"Operation: {operation.description}")
    print(f"Budget max_complexity_increase: {budget.max_complexity_increase}")
    print(f"Decision: {'✓ ALLOWED' if decision.allowed else '✗ DENIED'}")
    print()
    if not decision.allowed:
        print("Error Message:")
        print(decision.get_error_message())
    print()


def example_forbidden_paths():
    """Example 4: Forbidden paths blocking."""
    print("=" * 60)
    print("Example 4: Forbidden Paths Blocking")
    print("=" * 60)

    budget = ChangeBudget({"forbidden_paths": [".git/", "node_modules/"]})

    # Attempt to modify .git file (CRITICAL violation)
    dangerous_operation = Operation(
        changes=[FileChange(file_path=".git/config", added_lines=["[core]"])],
        description="Modify git config",
    )

    decision = budget.validate_operation(dangerous_operation)

    print(f"Operation: {dangerous_operation.description}")
    print(f"File: {dangerous_operation.affected_files[0]}")
    print(f"Decision: {'✓ ALLOWED' if decision.allowed else '✗ DENIED'}")
    print(f"Has CRITICAL violations: {decision.has_critical_violations}")
    print()
    if not decision.allowed:
        print("Error Message:")
        print(decision.get_error_message())
    print()


def example_critical_vs_default_budget():
    """Example 5: Critical files budget vs default."""
    print("=" * 60)
    print("Example 5: Critical Files Budget vs Default")
    print("=" * 60)

    # Default budget (permissive)
    default_budget = ChangeBudget(
        {
            "max_files": 5,
            "max_lines_per_file": 100,
            "max_total_lines": 300,
        }
    )

    # Critical files budget (strict)
    critical_budget = ChangeBudget(
        {
            "max_files": 1,
            "max_lines_per_file": 20,
            "max_total_lines": 20,
            "max_complexity_increase": 0,
        }
    )

    # Operation that passes default but fails critical
    operation = Operation(
        changes=[
            FileChange(
                file_path="src/security/auth.py",
                added_lines=[f"line_{i}" for i in range(50)],
            )
        ],
        description="Modify auth module",
    )

    default_decision = default_budget.validate_operation(operation)
    critical_decision = critical_budget.validate_operation(operation)

    print(f"Operation: {operation.description}")
    print(f"Lines changed: {operation.total_lines_changed}")
    print()
    print(
        f"Default Budget Decision: {'✓ ALLOWED' if default_decision.allowed else '✗ DENIED'}"
    )
    print(
        f"Critical Budget Decision: {'✓ ALLOWED' if critical_decision.allowed else '✗ DENIED'}"
    )
    print()
    if not critical_decision.allowed:
        print("Critical Budget Error:")
        print(critical_decision.get_error_message())
    print()


def main():
    """Run all examples."""
    print("\n")
    print("*" * 60)
    print(" Change Budgeting Examples - Blast Radius Control")
    print("*" * 60)
    print()

    example_basic_validation()
    example_max_files_violation()
    example_complexity_increase()
    example_forbidden_paths()
    example_critical_vs_default_budget()

    print("*" * 60)
    print(" All examples completed!")
    print("*" * 60)
    print()


if __name__ == "__main__":
    main()
