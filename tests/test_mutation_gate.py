"""
[20251217_TEST] Tests for Mutation Test Gate (v3.0.0 Autonomy).

Tests P0 Acceptance Criteria:
- Mutation Gate: Detects hollow fixes (tests pass after revert) (P0)
- Mutation Gate: Generates additional mutations (P0)
- Mutation Gate: Calculates mutation score (P0)
- Mutation Gate: Gates on minimum score threshold (P0)

Tests P1 Acceptance Criteria:
- Mutation Gate: Identifies weak tests (P1)
- Mutation Gate: Provides actionable recommendations (P1)
"""

import pytest
from unittest.mock import Mock

from code_scalpel.autonomy import (
    MutationTestGate,
    MutationGateResult,
    MutationType,
    SandboxExecutor,
    SandboxResult,
    ExecutionTestResult,
)


def create_failing_result():
    """Helper to create a failing sandbox result."""
    return SandboxResult(
        success=False, all_passed=False, stdout="", stderr="",
        execution_time_ms=100, tests=[]
    )


def create_passing_result():
    """Helper to create a passing sandbox result."""
    return SandboxResult(
        success=True, all_passed=True, stdout="", stderr="",
        execution_time_ms=100, tests=[]
    )


class TestMutationGateHollowFixDetection:
    """Test hollow fix detection (P0)."""
    
    def test_detects_hollow_fix_tests_pass_after_revert(self):
        """P0: Mutation gate detects hollow fixes when tests pass after reverting."""
        # Setup - both original and fixed code pass tests (hollow fix!)
        sandbox = Mock(spec=SandboxExecutor)
        sandbox.run_tests.return_value = SandboxResult(
            success=True,
            all_passed=True,  # Tests pass even with reverted code
            stdout="All tests passed",
            stderr="",
            execution_time_ms=100,
            tests=[
                ExecutionTestResult(name="test_feature", passed=True, duration_ms=50),
            ]
        )
        
        # Execute
        gate = MutationTestGate(sandbox=sandbox)
        result = gate.validate_fix(
            original_code="def func(): pass  # Hollow",
            fixed_code="def func(): return 42",
            test_files=["tests/test_feature.py"],
            language="python"
        )
        
        # Assert
        assert not result.passed
        assert result.hollow_fix_detected
        assert result.mutations_tested == 1
        assert result.mutations_caught == 0
        assert result.mutations_survived == 1
        assert "HOLLOW FIX DETECTED" in result.recommendations[0]
    
    def test_passes_when_revert_causes_tests_to_fail(self):
        """P0: Mutation gate passes when reverting fix causes tests to fail."""
        # Setup - fixed code passes, original code fails (genuine fix!)
        sandbox = Mock(spec=SandboxExecutor)
        
        # Provide enough responses for revert + potential additional mutations
        responses = [
            # First call: fixed_code passes
            SandboxResult(
                success=True, all_passed=True, stdout="All tests passed", stderr="",
                execution_time_ms=100,
                tests=[ExecutionTestResult(name="test_feature", passed=True, duration_ms=50)]
            ),
            # Second call: original_code fails (revert)
            SandboxResult(
                success=False, all_passed=False, stdout="", stderr="Test failed",
                execution_time_ms=100,
                tests=[ExecutionTestResult(name="test_feature", passed=False, duration_ms=50)]
            ),
        ]
        # Add up to 5 more responses for additional mutations (all caught)
        for _ in range(5):
            responses.append(SandboxResult(
                success=False, all_passed=False, stdout="", stderr="",
                execution_time_ms=100, tests=[]
            ))
        
        sandbox.run_tests.side_effect = responses
        
        # Execute
        gate = MutationTestGate(sandbox=sandbox, min_mutation_score=1.0)
        result = gate.validate_fix(
            original_code="def func(): return 0  # Bug",
            fixed_code="def func(): return 42  # Fixed",
            test_files=["tests/test_feature.py"],
            language="python"
        )
        
        # Assert
        assert result.passed  # Passed because revert was caught
        assert not result.hollow_fix_detected
        assert result.mutations_tested == 1
        assert result.mutations_caught == 1
        assert result.mutations_survived == 0
    
    def test_fails_when_fixed_code_does_not_pass_tests(self):
        """P0: Mutation gate fails sanity check if fixed code doesn't pass."""
        # Setup - fixed code doesn't pass
        sandbox = Mock(spec=SandboxExecutor)
        sandbox.run_tests.return_value = SandboxResult(
            success=False,
            all_passed=False,
            stdout="",
            stderr="Test failed",
            execution_time_ms=100,
            tests=[ExecutionTestResult(name="test_feature", passed=False, duration_ms=50)]
        )
        
        # Execute
        gate = MutationTestGate(sandbox=sandbox)
        result = gate.validate_fix(
            original_code="def func(): return 0",
            fixed_code="def func(): return invalid",
            test_files=["tests/test_feature.py"],
            language="python"
        )
        
        # Assert
        assert not result.passed
        assert not result.hollow_fix_detected
        assert result.mutations_tested == 0
        assert "not ready for mutation testing" in result.recommendations[0]


class TestMutationGeneration:
    """Test mutation generation (P0)."""
    
    def test_generates_negate_condition_mutations(self):
        """P0: Mutation gate generates condition negation mutations."""
        # Setup
        sandbox = Mock(spec=SandboxExecutor)
        # Provide enough responses: fixed pass + revert + 5 additional mutations
        responses = [create_passing_result(), create_failing_result()]
        responses.extend([create_failing_result() for _ in range(5)])
        sandbox.run_tests.side_effect = responses
        
        code_with_condition = """
def check_positive(x):
    if x > 0:
        return True
    return False
"""
        
        # Execute
        gate = MutationTestGate(sandbox=sandbox)
        result = gate.validate_fix(
            original_code="def check_positive(x): return False",
            fixed_code=code_with_condition,
            test_files=["tests/test_check.py"],
            language="python"
        )
        
        # Assert - should have tested revert + at least one mutation
        assert result.mutations_tested >= 2
        assert result.passed  # All mutations caught
    
    def test_generates_null_return_mutations(self):
        """P0: Mutation gate generates null return mutations."""
        # Setup
        sandbox = Mock(spec=SandboxExecutor)
        responses = [create_passing_result(), create_failing_result()]
        responses.extend([create_failing_result() for _ in range(5)])
        sandbox.run_tests.side_effect = responses
        
        code_with_return = """
def calculate(x):
    result = x * 2
    return result
"""
        
        # Execute
        gate = MutationTestGate(sandbox=sandbox)
        result = gate.validate_fix(
            original_code="def calculate(x): return 0",
            fixed_code=code_with_return,
            test_files=["tests/test_calc.py"],
            language="python"
        )
        
        # Assert
        assert result.mutations_tested >= 2
        assert result.passed
    
    def test_handles_unparseable_code(self):
        """P0: Mutation gate handles syntax errors in code gracefully."""
        # Setup
        sandbox = Mock(spec=SandboxExecutor)
        responses = [create_passing_result(), create_failing_result()]
        responses.extend([create_failing_result() for _ in range(5)])
        sandbox.run_tests.side_effect = responses
        
        # Execute with invalid syntax
        gate = MutationTestGate(sandbox=sandbox)
        result = gate.validate_fix(
            original_code="def func(): invalid syntax here",
            fixed_code="def func(): return 42",
            test_files=["tests/test_func.py"],
            language="python"
        )
        
        # Assert - should still work with just the revert test
        assert result.mutations_tested == 1  # Only revert test
        assert result.passed


class TestMutationScore:
    """Test mutation score calculation (P0)."""
    
    def test_calculates_mutation_score_correctly(self):
        """P0: Mutation gate calculates mutation score correctly."""
        # Setup - 3 mutations caught, 1 survives
        sandbox = Mock(spec=SandboxExecutor)
        responses = [
            create_passing_result(),  # Fixed passes
            create_failing_result(),  # Revert caught
            create_failing_result(),  # Mutation 1 caught
            create_failing_result(),  # Mutation 2 caught
            create_passing_result(),  # Mutation 3 survives
        ]
        responses.extend([create_failing_result() for _ in range(5)])  # Extra buffer
        sandbox.run_tests.side_effect = responses
        
        code = """
def multi_function(x):
    if x > 0:
        return x * 2
    if x < 0:
        return x * 3
    return 0
"""
        
        # Execute
        gate = MutationTestGate(sandbox=sandbox, min_mutation_score=0.75)
        result = gate.validate_fix(
            original_code="def multi_function(x): return 0",
            fixed_code=code,
            test_files=["tests/test_multi.py"],
            language="python"
        )
        
        # Assert - 3/4 = 0.75, meets threshold
        assert result.mutations_caught == 3
        assert result.mutations_survived == 1
        assert result.passed  # 75% meets 0.75 threshold
    
    def test_gates_on_minimum_score_threshold(self):
        """P0: Mutation gate fails when score below threshold."""
        # Setup - only 1 of 3 mutations caught (33%)
        sandbox = Mock(spec=SandboxExecutor)
        responses = [
            create_passing_result(),  # Fixed passes
            create_failing_result(),  # Revert caught
            create_passing_result(),  # Mutation 1 survives
            create_passing_result(),  # Mutation 2 survives
        ]
        responses.extend([create_passing_result() for _ in range(5)])  # More mutations survive
        sandbox.run_tests.side_effect = responses
        
        code = """
def weak_tests(x):
    if x > 0:
        return x * 2
    if x < 0:
        return x * 3
    return 0
"""
        
        # Execute with 80% threshold
        gate = MutationTestGate(sandbox=sandbox, min_mutation_score=0.8)
        result = gate.validate_fix(
            original_code="def weak_tests(x): return 0",
            fixed_code=code,
            test_files=["tests/test_weak.py"],
            language="python"
        )
        
        # Assert - 33% below 80% threshold
        assert result.mutations_caught == 1
        assert result.mutations_survived == 2
        assert not result.passed  # Failed gate
    
    def test_passes_with_perfect_score(self):
        """P0: Mutation gate passes with 100% mutation score."""
        # Setup - all mutations caught
        sandbox = Mock(spec=SandboxExecutor)
        responses = [create_passing_result()]  # Fixed passes
        responses.extend([create_failing_result() for _ in range(10)])  # All mutations caught
        sandbox.run_tests.side_effect = responses
        
        code = "def func(x):\n    if x > 0:\n        return x\n    return 0"
        
        # Execute
        gate = MutationTestGate(sandbox=sandbox, min_mutation_score=1.0)
        result = gate.validate_fix(
            original_code="def func(x): return 0",
            fixed_code=code,
            test_files=["tests/test_func.py"],
            language="python"
        )
        
        # Assert
        assert result.mutations_caught == result.mutations_tested
        assert result.mutations_survived == 0
        assert result.passed


class TestWeakTestIdentification:
    """Test weak test identification (P1)."""
    
    def test_identifies_weak_tests(self):
        """P1: Mutation gate identifies tests that don't catch mutations."""
        # Setup
        sandbox = Mock(spec=SandboxExecutor)
        responses = [
            # Fixed passes
            SandboxResult(
                success=True, all_passed=True, stdout="", stderr="",
                execution_time_ms=100,
                tests=[
                    ExecutionTestResult(name="test_basic", passed=True, duration_ms=50),
                    ExecutionTestResult(name="test_edge", passed=True, duration_ms=50),
                ]
            ),
            # Revert fails - test_basic catches it
            SandboxResult(
                success=False, all_passed=False, stdout="", stderr="",
                execution_time_ms=100,
                tests=[
                    ExecutionTestResult(name="test_basic", passed=False, duration_ms=50),
                    ExecutionTestResult(name="test_edge", passed=True, duration_ms=50),  # Weak!
                ]
            ),
            # Mutation 1 survives - test_edge doesn't catch
            SandboxResult(
                success=True, all_passed=True, stdout="", stderr="",
                execution_time_ms=100,
                tests=[
                    ExecutionTestResult(name="test_basic", passed=True, duration_ms=50),
                    ExecutionTestResult(name="test_edge", passed=True, duration_ms=50),  # Weak!
                ]
            ),
        ]
        responses.extend([create_failing_result() for _ in range(5)])  # Buffer
        sandbox.run_tests.side_effect = responses
        
        code = "def func(x):\n    if x > 0:\n        return x\n    return 0"
        
        # Execute
        gate = MutationTestGate(sandbox=sandbox, min_mutation_score=0.5)
        result = gate.validate_fix(
            original_code="def func(x): return 0",
            fixed_code=code,
            test_files=["tests/test_func.py"],
            language="python"
        )
        
        # Assert
        assert "test_edge" in result.weak_tests
        assert "test_basic" not in result.weak_tests
    
    def test_provides_actionable_recommendations(self):
        """P1: Mutation gate provides actionable recommendations."""
        # Setup - some mutations survive
        sandbox = Mock(spec=SandboxExecutor)
        responses = [
            # Fixed passes
            SandboxResult(success=True, all_passed=True, stdout="", stderr="",
                         execution_time_ms=100, tests=[]),
            # Revert caught
            SandboxResult(success=False, all_passed=False, stdout="", stderr="",
                         execution_time_ms=100, tests=[]),
            # Mutation survives
            SandboxResult(success=True, all_passed=True, stdout="", stderr="",
                         execution_time_ms=100,
                         tests=[ExecutionTestResult(name="test_weak", passed=True, duration_ms=50)]),
        ]
        responses.extend([create_passing_result() for _ in range(5)])  # More mutations survive
        sandbox.run_tests.side_effect = responses
        
        code = "def func(x):\n    if x > 0:\n        return x\n    return 0"
        
        # Execute
        gate = MutationTestGate(sandbox=sandbox, min_mutation_score=1.0)
        result = gate.validate_fix(
            original_code="def func(x): return 0",
            fixed_code=code,
            test_files=["tests/test_func.py"],
            language="python"
        )
        
        # Assert
        assert not result.passed  # Failed because mutation survived
        assert len(result.recommendations) > 0
        assert "survived" in result.recommendations[0].lower()
        assert "test_weak" in str(result.weak_tests)


class TestMutationGateIntegration:
    """Test mutation gate with realistic scenarios."""
    
    def test_real_world_scenario_genuine_fix(self):
        """Integration: Real-world scenario with genuine fix."""
        # Setup - simulates a real bug fix
        sandbox = Mock(spec=SandboxExecutor)
        
        # All mutations should be caught by tests
        responses = [
            # Fixed code passes all tests
            SandboxResult(
                success=True, all_passed=True, stdout="4 passed", stderr="",
                execution_time_ms=200,
                tests=[
                    ExecutionTestResult(name="test_positive", passed=True, duration_ms=50),
                    ExecutionTestResult(name="test_negative", passed=True, duration_ms=50),
                    ExecutionTestResult(name="test_zero", passed=True, duration_ms=50),
                    ExecutionTestResult(name="test_edge", passed=True, duration_ms=50),
                ]
            ),
            # Revert causes failures
            SandboxResult(
                success=False, all_passed=False, stdout="", stderr="2 failed",
                execution_time_ms=150,
                tests=[
                    ExecutionTestResult(name="test_positive", passed=False, duration_ms=50),
                    ExecutionTestResult(name="test_negative", passed=False, duration_ms=50),
                    ExecutionTestResult(name="test_zero", passed=True, duration_ms=25),
                    ExecutionTestResult(name="test_edge", passed=True, duration_ms=25),
                ]
            ),
            # Negated condition causes failure
            SandboxResult(
                success=False, all_passed=False, stdout="", stderr="1 failed",
                execution_time_ms=150,
                tests=[
                    ExecutionTestResult(name="test_positive", passed=False, duration_ms=50),
                    ExecutionTestResult(name="test_negative", passed=True, duration_ms=50),
                    ExecutionTestResult(name="test_zero", passed=True, duration_ms=25),
                    ExecutionTestResult(name="test_edge", passed=True, duration_ms=25),
                ]
            ),
        ]
        responses.extend([create_failing_result() for _ in range(5)])  # Additional mutations caught
        sandbox.run_tests.side_effect = responses
        
        original_buggy = """
def calculate_tax(amount, rate):
    # Bug: returning 0 instead of calculation
    return 0
"""
        
        fixed_correct = """
def calculate_tax(amount, rate):
    if amount < 0 or rate < 0:
        raise ValueError("Amount and rate must be non-negative")
    return amount * rate
"""
        
        # Execute
        gate = MutationTestGate(sandbox=sandbox, min_mutation_score=0.8)
        result = gate.validate_fix(
            original_code=original_buggy,
            fixed_code=fixed_correct,
            test_files=["tests/test_calculate_tax.py"],
            language="python"
        )
        
        # Assert
        assert result.passed
        assert not result.hollow_fix_detected
        assert result.mutations_tested >= 2
        assert result.mutations_caught >= 2
