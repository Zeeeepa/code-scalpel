# TODO Documentation: Add solver configuration guide
# TODO Documentation: Document constraint types supported
# TODO Documentation: Create timeout tuning guide
# TODO Documentation: Add examples for solve/prove operations
# TODO Documentation: Document Z3 type marshaling
# TODO Documentation: Create troubleshooting guide
# TODO Documentation: Add API reference documentation
# TODO Documentation: Document SolverStatus enumeration
# TODO Documentation: Create error handling guide
# TODO Documentation: Add constraint building patterns
# TODO Tutorial: Create basic constraint solving tutorial
# TODO Documentation: Add solve() vs prove() comparison guide
# TODO Documentation: Document model extraction workflow
# TODO Example: Create example for finding counterexamples
# TODO Documentation: Add type marshaling examples
# TODO Testing: Add unit tests for all solver operations
# TODO Testing: Create test suite for different constraint types
# TODO Testing: Add timeout handling tests
# TODO Documentation: Document test coverage
# TODO Optimization: Optimize type marshaling performance
# TODO Implementation: Implement constraint memoization
# TODO Implementation: Add early termination heuristics
# TODO Implementation: Support partial model extraction
# TODO Implementation: Implement solver state snapshots
# TODO Visualization: Add constraint visualization
# TODO Implementation: Implement solver tracing
# TODO Debugging: Add step-by-step solver debugging
# TODO Implementation: Support constraint path tracking
# TODO Implementation: Implement model difference analysis
# TODO Implementation: Implement distributed constraint solving
# TODO Implementation: Add alternative SMT solvers (CVC5, Yices2, MathSAT)
# TODO Implementation: Support heterogeneous solving (multiple solvers)
# TODO Implementation: Implement adaptive solver selection
# TODO Optimization: Add MaxSMT optimization support
# TODO Implementation: Support incremental model building
# TODO Implementation: Implement constraint portfolio solving
# TODO Implementation: Add load balancing for solver instances
# TODO Implementation: Support cluster-aware constraint distribution
# TODO Implementation: Add machine learning for solver tuning
# TODO Implementation: Support custom constraint theories
# TODO Visualization: Implement visualization for constraints
# TODO Implementation: Add probabilistic constraint solving
# TODO Implementation: Support constraint ranking and prioritization
# TODO Implementation: Implement model interpolation
# TODO Implementation: Add constraint learning from failure
# TODO Implementation: Support dynamic constraint updates
# TODO Metrics: Implement solver metrics collection
# TODO Analytics: Add performance analytics dashboard
# TODO Monitoring: Support solver health monitoring
# TODO Tuning: Implement automatic solver tuning
# TODO Alerting: Add alerting for solver anomalies
# TODO Implementation: Support external constraint databases
# TODO Versioning: Implement solver versioning system
# TODO Reporting: Add compliance reporting for constraint solving

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional

import z3
from z3 import BoolRef, ExprRef, Not, Solver, sat, simplify, unsat


class SolverStatus(Enum):
    """Result status from the solver."""

    SAT = auto()  # Satisfiable - model found
    UNSAT = auto()  # Unsatisfiable - no model exists
    UNKNOWN = auto()  # Timeout or undecidable
    VALID = auto()  # For prove(): assertion is always true
    INVALID = auto()  # For prove(): counterexample found


@dataclass
class SolverResult:
    """
    Result from constraint solving.

    Attributes:
        status: SAT, UNSAT, UNKNOWN, VALID, or INVALID
        model: Variable assignments (for SAT) - Python-native types
        counterexample: Counterexample (for INVALID) - Python-native types
        time_ms: Solving time in milliseconds
    """

    status: SolverStatus
    model: Optional[Dict[str, Any]] = None
    counterexample: Optional[Dict[str, Any]] = None
    time_ms: float = 0.0

    def is_sat(self) -> bool:
        """Check if result is satisfiable."""
        return self.status == SolverStatus.SAT

    def is_valid(self) -> bool:
        """Check if result is valid (for prove())."""
        return self.status == SolverStatus.VALID

    def __bool__(self) -> bool:
        """Result is truthy if SAT or VALID."""
        return self.status in (SolverStatus.SAT, SolverStatus.VALID)

    def __repr__(self) -> str:  # pragma: no cover
        if self.status == SolverStatus.SAT:
            return f"SolverResult(SAT, model={self.model})"
        elif self.status == SolverStatus.INVALID:
            return f"SolverResult(INVALID, counterexample={self.counterexample})"
        else:
            return f"SolverResult({self.status.name})"


class ConstraintSolver:
    """
    Z3-based constraint solver with Python-native output.

    Provides two main operations:
    - solve(): Find a model satisfying constraints
    - prove(): Prove an assertion is valid or find counterexample

    All outputs are Python-native types (int, bool, dict) for
    easy JSON serialization.

    Example:
        solver = ConstraintSolver()
        x = Int("x")

        result = solver.solve([x > 10, x < 20], [x])
        if result.is_sat():
            print(result.model)  # {'x': 15} - Python int!
    """

    DEFAULT_TIMEOUT_MS = 2000  # 2 seconds

    def __init__(self, timeout_ms: int = DEFAULT_TIMEOUT_MS):
        """
        Initialize the solver.

        Args:
            timeout_ms: Timeout in milliseconds (default: 2000)
        """
        self.timeout_ms = timeout_ms

    # =========================================================================
    # Main API
    # =========================================================================

    def solve(
        self,
        constraints: List[BoolRef],
        variables: List[ExprRef],
        variable_names: Optional[List[str]] = None,
    ) -> SolverResult:
        """
        Find a model satisfying all constraints.

        Args:
            constraints: List of Z3 boolean constraints
            variables: List of Z3 variables to include in model

        Returns:
            SolverResult with status and model (if SAT)
        """
        solver = Solver()
        solver.set("timeout", self.timeout_ms)

        # Add all constraints
        for c in constraints:
            solver.add(c)

        # Check satisfiability
        check_result = solver.check()

        if check_result == sat:
            # Extract and convert model
            z3_model = solver.model()
            model = self._extract_model(z3_model, variables, variable_names)
            return SolverResult(status=SolverStatus.SAT, model=model)
        elif check_result == unsat:
            return SolverResult(status=SolverStatus.UNSAT, model=None)
        else:
            # unknown - timeout or undecidable
            return SolverResult(status=SolverStatus.UNKNOWN, model=None)

    def prove(self, preconditions: List[BoolRef], assertion: BoolRef) -> SolverResult:
        """
        Prove an assertion is valid under preconditions.

        To prove P → Q (preconditions imply assertion):
        We check if P ∧ ¬Q is unsatisfiable.
        If UNSAT: The assertion is VALID (always true)
        If SAT: The assertion is INVALID (counterexample found)

        Args:
            preconditions: List of assumptions
            assertion: Property to prove

        Returns:
            SolverResult with VALID or INVALID status
        """
        solver = Solver()
        solver.set("timeout", self.timeout_ms)

        # Add preconditions
        for pre in preconditions:
            solver.add(pre)

        # Add negation of assertion
        solver.add(Not(assertion))

        # Check: can we satisfy preconditions AND NOT assertion?
        check_result = solver.check()

        if check_result == unsat:
            # Cannot violate assertion → it's VALID
            return SolverResult(status=SolverStatus.VALID, counterexample=None)
        elif check_result == sat:
            # Found a counterexample
            z3_model = solver.model()
            counterexample = self._model_to_dict(z3_model)
            return SolverResult(
                status=SolverStatus.INVALID, counterexample=counterexample
            )
        else:
            return SolverResult(status=SolverStatus.UNKNOWN, counterexample=None)

    # =========================================================================
    # Type Marshaling - The Critical Part
    # =========================================================================

    def _extract_model(
        self,
        z3_model: z3.ModelRef,
        variables: List[ExprRef],
        variable_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Extract variable values from Z3 model as Python-native types.

        Args:
            z3_model: The Z3 model
            variables: Variables to extract

        Returns:
            Dictionary of variable name → Python value
        """
        result: Dict[str, Any] = {}

        for idx, var in enumerate(variables):
            if variable_names and idx < len(variable_names):
                name = variable_names[idx]
            else:
                name = str(var)

            # Get value from model (with model completion for unconstrained vars)
            z3_value = z3_model.eval(var, model_completion=True)

            # Convert to Python-native type
            python_value = self._z3_to_python(z3_value)
            result[name] = python_value

        return result

    def _model_to_dict(self, z3_model: z3.ModelRef) -> Dict[str, Any]:
        """
        Convert entire Z3 model to Python dictionary.

        Args:
            z3_model: The Z3 model

        Returns:
            Dictionary of all variable assignments
        """
        result: Dict[str, Any] = {}

        for decl in z3_model.decls():
            name = decl.name()
            z3_value = z3_model[decl]
            python_value = self._z3_to_python(z3_value)
            result[name] = python_value

        return result

    def _z3_to_python(self, z3_value: Any) -> Any:
        """
        Convert a Z3 value to Python-native type.

        CRITICAL: This is where we prevent JSON serialization crashes.

        Args:
            z3_value: Z3 expression or value

        Returns:
            Python int, bool, str, or string representation
        """
        # Integer
        if z3.is_int_value(z3_value):
            return z3_value.as_long()

        # Boolean
        if z3.is_bool(z3_value):
            # Handle both concrete True/False and symbolic booleans
            if z3.is_true(z3_value):
                return True
            elif z3.is_false(z3_value):
                return False
            else:
                # Symbolic boolean - shouldn't happen in model
                return bool(z3.is_true(simplify(z3_value)))

        # String (v0.3.0)
        if z3.is_string_value(z3_value):
            return z3_value.as_string()

        # Real (convert to float)
        if z3.is_real(z3_value):
            # Try to get as fraction, then convert to float
            try:
                return float(z3_value.as_decimal(10).rstrip("?"))
            except Exception:
                return float(z3_value.numerator_as_long()) / float(
                    z3_value.denominator_as_long()
                )

        # BitVector
        if z3.is_bv_value(z3_value):
            return z3_value.as_long()

        # Fallback: string representation
        return str(z3_value)


# =============================================================================
# Legacy API Compatibility (from original constraint_solver.py)
# =============================================================================


class SolverType(Enum):
    """Supported constraint solver types."""

    Z3 = "z3"
    CVC4 = "cvc4"
    YICES = "yices"
    MATHSAT = "mathsat"


class ConstraintType(Enum):
    """Types of constraints."""

    ARITHMETIC = "arithmetic"
    BOOLEAN = "boolean"
    BITVECTOR = "bitvector"
    STRING = "string"
    ARRAY = "array"


@dataclass
class SolverConfig:
    """Configuration for the constraint solver."""

    solver_type: SolverType = SolverType.Z3
    timeout: Optional[int] = None
    memory_limit: Optional[int] = None
    use_incremental: bool = True
    simplify_constraints: bool = True
    parallel_solving: bool = False
    track_unsat_core: bool = False
    optimization_level: int = 1


@dataclass
class SolverStatistics:
    """Statistics about constraint solving."""

    num_constraints: int = 0
    num_variables: int = 0
    solving_time: float = 0.0
    memory_used: int = 0
    num_sat_checks: int = 0
    num_unsat_results: int = 0
    num_unknown_results: int = 0


class ConstraintError(Exception):
    """Base class for constraint solver errors."""

    pass


class UnsatisfiableError(ConstraintError):
    """Raised when constraints are unsatisfiable."""

    pass


class SolverTimeoutError(ConstraintError):
    """Raised when solver times out."""

    pass


# Convenience functions
def create_solver(
    timeout_ms: int = ConstraintSolver.DEFAULT_TIMEOUT_MS,
) -> ConstraintSolver:
    """Create a new constraint solver instance."""
    return ConstraintSolver(timeout_ms=timeout_ms)


def solve_constraints(
    constraints: List[BoolRef],
    variables: List[ExprRef],
    timeout_ms: int = ConstraintSolver.DEFAULT_TIMEOUT_MS,
) -> Optional[Dict[str, Any]]:
    """
    Solve a list of constraints.

    Args:
        constraints: List of Z3 boolean constraints
        variables: List of Z3 variables
        timeout_ms: Timeout in milliseconds

    Returns:
        Model if SAT, None if UNSAT
    """
    solver = ConstraintSolver(timeout_ms=timeout_ms)
    result = solver.solve(constraints, variables)
    return result.model if result.is_sat() else None


def is_satisfiable(constraints: List[BoolRef]) -> bool:
    """Check if a list of constraints is satisfiable."""
    solver = ConstraintSolver()
    result = solver.solve(constraints, [])
    return result.is_sat()
