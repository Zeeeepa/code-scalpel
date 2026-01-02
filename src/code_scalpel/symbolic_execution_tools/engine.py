"""
Symbolic Analysis Engine - The Heart of code-scalpel's symbolic execution.

This module wires together the core components:
- TypeInferenceEngine: Infers Z3 types from Python AST
- SymbolicState: Tracks variables and path constraints with fork() isolation
- SymbolicInterpreter: Walks AST with smart forking and bounded loops
- ConstraintSolver: Marshals Z3 to Python natives for JSON/CLI consumption

PHASE 1 SCOPE (RFC-001): Integers and Booleans only.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, cast

import z3

from ..ir.nodes import IRFunctionDef, IRModule
from ..ir.normalizers.java_normalizer import JavaNormalizer
from ..ir.normalizers.javascript_normalizer import JavaScriptNormalizer
from ..ir.normalizers.python_normalizer import PythonNormalizer
from .constraint_solver import ConstraintSolver, SolverStatus
from .ir_interpreter import IRSymbolicInterpreter
from .state_manager import SymbolicState
from .type_inference import InferredType, TypeInferenceEngine

logger = logging.getLogger(__name__)


# Note: The symbolic engine has type limitations
# It handles Int/Bool/String but not Float/List/Dict
# Loop unrolling is bounded to prevent explosion

# TODO: Add support for complex data types
#   - List/Array symbolic execution with index tracking
#   - Dictionary/Map symbolic execution with key constraints
#   - Tuple unpacking and multiple assignment
#   - Set operations with symbolic membership

# TODO: Improve path exploration strategies
#   - Implement concolic execution (concrete + symbolic)
#   - Add heuristic-based path prioritization
#   - Implement depth-first vs breadth-first strategies
#   - Add coverage-guided exploration

# TODO: Performance optimizations
#   - Implement path memoization to avoid re-exploring
#   - Add incremental constraint solving
#   - Implement constraint caching and simplification
#   - Parallelize path exploration with worker pools

# TODO: Enhanced loop handling
#   - Implement widening for unbounded loops
#   - Add loop invariant detection
#   - Support dynamic unrolling based on complexity
#   - Detect and warn on infinite loops

# TODO: Engine Enhancement Roadmap
# =================================
#
# COMMUNITY (Current & Planned):
# Documentation & Learning:
# - TODO [COMMUNITY]: Add better error messages for path exploration (current)
# - TODO [COMMUNITY]: Document symbolic state management
# - TODO [COMMUNITY]: Add visualization of explored paths
# - TODO [COMMUNITY]: Create debugging helpers for analysis
# - TODO [COMMUNITY]: Add path explosion detection and reporting
# - TODO [COMMUNITY]: Implement graceful degradation on solver timeout
# - TODO [COMMUNITY]: Create symbolic execution tutorial
# - TODO [COMMUNITY]: Document PathStatus and AnalysisResult
# - TODO [COMMUNITY]: Add troubleshooting guide for path explosion
# - TODO [COMMUNITY]: Create performance tuning guide
# - TODO [COMMUNITY]: Document cache configuration options
# - TODO [COMMUNITY]: Add examples for different code patterns
#
# Testing & Validation:
# - TODO [COMMUNITY]: Add integration tests for path exploration
# - TODO [COMMUNITY]: Create test suite for different Python versions
# - TODO [COMMUNITY]: Add regression tests for engine behavior
# - TODO [COMMUNITY]: Document test execution procedure
# - TODO [COMMUNITY]: Add test coverage reporting
#
# User Experience:
# - TODO [COMMUNITY]: Improve error messages with suggestions
# - TODO [COMMUNITY]: Add progress reporting for long-running analysis
# - TODO [COMMUNITY]: Implement analysis cancellation support
# - TODO [COMMUNITY]: Add memory usage warnings
#
# PRO (Enhanced Features):
# Core Engine Capabilities:
# - TODO [PRO]: Implement concurrent path exploration
# - TODO [PRO]: Add memory-efficient state tracking
# - TODO [PRO]: Support partial path exploration
# - TODO [PRO]: Implement symbolic array indexing
# - TODO [PRO]: Add state merging heuristics
# - TODO [PRO]: Support function summaries for better performance
# - TODO [PRO]: Implement path ranking by feasibility
# - TODO [PRO]: Add integration with external solvers (CVC4, Yices)
# - TODO [PRO]: Implement loop widening algorithms
# - TODO [PRO]: Support recursive function analysis
#
# Analysis Enhancements:
# - TODO [PRO]: Add interprocedural analysis
# - TODO [PRO]: Implement context-sensitive analysis
# - TODO [PRO]: Support module-level analysis
# - TODO [PRO]: Add call graph construction
# - TODO [PRO]: Implement data flow analysis
# - TODO [PRO]: Support def-use chain analysis
# - TODO [PRO]: Add control flow graph construction
#
# Data Type Support:
# - TODO [PRO]: Add symbolic List/Array support
# - TODO [PRO]: Implement symbolic Dict/Map support
# - TODO [PRO]: Support symbolic Set operations
# - TODO [PRO]: Implement symbolic Tuple analysis
# - TODO [PRO]: Add string length tracking
# - TODO [PRO]: Support symbolic slice operations
#
# Performance & Optimization:
# - TODO [PRO]: Implement constraint caching
# - TODO [PRO]: Add path memoization
# - TODO [PRO]: Support incremental re-analysis
# - TODO [PRO]: Implement dead code elimination
# - TODO [PRO]: Add solver result caching
# - TODO [PRO]: Support parallel path exploration
#
# Debugging & Analysis Tools:
# - TODO [PRO]: Add path visualization tools
# - TODO [PRO]: Implement constraint visualization
# - TODO [PRO]: Add execution trace generation
# - TODO [PRO]: Support breakpoint-style debugging
# - TODO [PRO]: Implement variable watch functionality
#
# ENTERPRISE (Advanced Capabilities):
# Distributed & Scalability:
# - TODO [ENTERPRISE]: Implement distributed engine via MCP server
# - TODO [ENTERPRISE]: Add persistent cache for analysis results
# - TODO [ENTERPRISE]: Support multi-language symbolic execution
# - TODO [ENTERPRISE]: Implement custom path exploration strategies
# - TODO [ENTERPRISE]: Add dataflow-aware state management
# - TODO [ENTERPRISE]: Support incremental re-analysis
# - TODO [ENTERPRISE]: Implement parallel constraint solving
# - TODO [ENTERPRISE]: Add human-in-the-loop annotation support
# - TODO [ENTERPRISE]: Support cluster-based distributed analysis
# - TODO [ENTERPRISE]: Implement load balancing for path exploration
#
# Advanced Analysis Capabilities:
# - TODO [ENTERPRISE]: Implement vulnerability prediction
# - TODO [ENTERPRISE]: Add exploit chain detection
# - TODO [ENTERPRISE]: Support zero-day vulnerability detection
# - TODO [ENTERPRISE]: Implement behavior-based anomaly detection
# - TODO [ENTERPRISE]: Add ML-based false positive filtering
# - TODO [ENTERPRISE]: Support supply chain attack detection
# - TODO [ENTERPRISE]: Implement semantic code similarity
# - TODO [ENTERPRISE]: Add automatic remediation suggestions
#
# Integration & Intelligence:
# - TODO [ENTERPRISE]: Add SIEM integration
# - TODO [ENTERPRISE]: Support compliance reporting
# - TODO [ENTERPRISE]: Implement audit trail logging
# - TODO [ENTERPRISE]: Add multi-tenant architecture
# - TODO [ENTERPRISE]: Support policy enforcement
# - TODO [ENTERPRISE]: Implement continuous monitoring
# - TODO [ENTERPRISE]: Add automated triage workflows
# - TODO [ENTERPRISE]: Support vulnerability management integration


class PathStatus(Enum):
    """Status of an explored execution path."""

    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    UNKNOWN = "unknown"


@dataclass
class PathResult:
    """Result of exploring a single execution path."""

    path_id: int
    status: PathStatus
    constraints: List[z3.BoolRef]
    variables: Dict[str, Any]  # Python native values (marshaled from Z3)
    model: Optional[Dict[str, Any]] = None  # Concrete satisfying assignment

    def to_dict(self) -> Dict[str, Any]:
        """Convert to cache-serializable dictionary.

        Z3 constraints are converted to string representations.
        """
        return {
            "path_id": self.path_id,
            "status": self.status.value,
            "constraints": [str(c) for c in self.constraints],
            "variables": self.variables,
            "model": self.model,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PathResult":
        """Reconstruct from cached dictionary.

        Note: constraints are stored as strings (not executable Z3 objects).
        """
        return cls(
            path_id=data["path_id"],
            status=PathStatus(data["status"]),
            constraints=[],  # Z3 objects cannot be reconstructed from strings
            variables=data["variables"],
            model=data.get("model"),
        )


@dataclass
class AnalysisResult:
    """
    Complete result from symbolic analysis.

    This is the primary output format for CLI/MCP consumption.
    All values are Python natives (int, bool) - no raw Z3 objects.
    """

    paths: List[PathResult] = field(default_factory=list)
    all_variables: Dict[str, InferredType] = field(default_factory=dict)
    feasible_count: int = 0
    infeasible_count: int = 0
    total_paths: int = 0
    from_cache: bool = False  # True if result was retrieved from cache

    def get_feasible_paths(self) -> List[PathResult]:
        """Return only feasible paths."""
        return [p for p in self.paths if p.status == PathStatus.FEASIBLE]

    def get_all_models(self) -> List[Dict[str, Any]]:
        """Return concrete models from all feasible paths."""
        return [p.model for p in self.paths if p.model is not None]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to cache-serializable dictionary."""
        return {
            "paths": [p.to_dict() for p in self.paths],
            "all_variables": {
                k: v.value if isinstance(v, InferredType) else str(v)
                for k, v in self.all_variables.items()
            },
            "feasible_count": self.feasible_count,
            "infeasible_count": self.infeasible_count,
            "total_paths": self.total_paths,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        """Reconstruct from cached dictionary."""
        return cls(
            paths=[PathResult.from_dict(p) for p in data.get("paths", [])],
            all_variables={
                k: InferredType(v) if isinstance(v, str) else v
                for k, v in data.get("all_variables", {}).items()
            },
            feasible_count=data.get("feasible_count", 0),
            infeasible_count=data.get("infeasible_count", 0),
            total_paths=data.get("total_paths", 0),
            from_cache=True,
        )


class SymbolicAnalyzer:
    """
    High-level symbolic analysis interface.

    Wires together TypeInferenceEngine, SymbolicInterpreter, and ConstraintSolver
    to provide a clean API for symbolic execution.

    Example:
        >>> analyzer = SymbolicAnalyzer()
        >>> result = analyzer.analyze('''
        ... x = symbolic('x', int)
        ... if x > 10:
        ...     y = x + 5
        ... else:
        ...     y = x - 5
        ... ''')
        >>> print(result.feasible_count)
        2
        >>> print(result.get_all_models())
        [{'x': 11, 'y': 16}, {'x': 0, 'y': -5}]

    Note:
        PHASE 1: Only supports Int and Bool types. Float/String/List will raise errors.
    """

    def __init__(
        self,
        max_loop_iterations: int = 10,
        solver_timeout: int = 2000,
        enable_cache: bool = True,
    ):
        """
        Initialize the symbolic analyzer.

        Args:
            max_loop_iterations: Maximum iterations before terminating loops (default 10)
            solver_timeout: Z3 solver timeout in milliseconds (default 2000)
            enable_cache: Enable result caching for repeated analysis (default True)
        """
        self.max_loop_iterations = max_loop_iterations
        self.solver_timeout = solver_timeout
        self.enable_cache = enable_cache

        # Cache for expensive symbolic analysis
        self._cache = None
        if enable_cache:
            try:
                # [20251223_CONSOLIDATION] Import from unified cache
                from code_scalpel.cache import get_cache

                self._cache = get_cache()
            except ImportError:
                logger.warning("Cache module not available, caching disabled")

        # Core components - initialized fresh for each analysis
        self._type_engine: Optional[TypeInferenceEngine] = None
        self._interpreter: Optional[IRSymbolicInterpreter] = None
        self._solver: Optional[ConstraintSolver] = None

        # Manual symbolic declarations for advanced use
        self._preconditions: List[z3.BoolRef] = []
        self._declared_symbols: Dict[str, z3.ExprRef] = {}

    def _get_cache_config(self, language: str) -> Dict[str, Any]:
        """Generate cache configuration key components."""
        return {
            "language": language,
            "max_loop_iterations": self.max_loop_iterations,
            "solver_timeout": self.solver_timeout,
            # [20251214_FEATURE] Cache-bust when model schema changes (friendly names)
            "model_schema": "friendly_names_v20251214",
        }

    def analyze(self, code: str, language: str = "python") -> AnalysisResult:
        """
        Perform symbolic analysis on source code.

        Results are cached to avoid expensive Z3 solving on repeated analysis.
        Cache key: SHA256(code + tool_version + config)

        Args:
            code: Source code string
            language: Source language ("python", "javascript", or "java")

        Returns:
            AnalysisResult with all explored paths and their models

        Raises:
            SyntaxError: If code cannot be parsed
            NotImplementedError: If code uses unsupported constructs
            ValueError: If language is not supported
        """
        cache_config = self._get_cache_config(language)

        # Check cache first (hashing is cheap, Z3 solving is expensive)
        if self._cache:
            cached = self._cache.get(code, "symbolic", cache_config)
            if cached is not None:
                logger.debug("Cache hit for symbolic analysis")
                # Cache always stores dicts via to_dict()
                return AnalysisResult.from_dict(cached)

        # Cache miss - perform expensive symbolic analysis
        result = self._analyze_uncached(code, language)

        # Store in cache for future runs
        if self._cache:
            try:
                self._cache.set(code, "symbolic", result.to_dict(), cache_config)
                logger.debug("Cached symbolic analysis result")
            except Exception as e:
                logger.warning(f"Failed to cache result: {e}")

        return result

    def _analyze_uncached(self, code: str, language: str) -> AnalysisResult:
        """Perform symbolic analysis without caching (internal method)."""
        # Fresh components for this analysis
        self._type_engine = TypeInferenceEngine()
        self._solver = ConstraintSolver(timeout_ms=self.solver_timeout)
        self._interpreter = IRSymbolicInterpreter(
            max_loop_iterations=self.max_loop_iterations
        )

        # Step 1: Type inference (Python only for now)
        inferred_types = {}
        if language == "python":
            inferred_types = self._type_engine.infer(code)

        # Step 2: Normalize to IR and execute symbolically
        try:
            if language == "python":
                ir_module = PythonNormalizer().normalize(code)
            elif language == "javascript":
                ir_module = JavaScriptNormalizer().normalize(code)
            elif language == "java":
                ir_module = JavaNormalizer().normalize(code)
            else:
                raise ValueError(f"Unsupported language: {language}")
        except SyntaxError as e:
            raise ValueError(f"Invalid {language} syntax: {e}")

        # Step 2.5: Check if top-level contains function definition
        # If so, extract and execute function body with symbolic parameters
        if ir_module.body and isinstance(ir_module.body[0], IRFunctionDef):
            func_def = ir_module.body[0]
            logger.debug(f"Detected function definition: {func_def.name}")

            # Create symbolic parameters for function arguments
            for param in func_def.params:
                param_name = param.name
                # Infer Z3 sort from type annotation
                if param.type_annotation:
                    type_str = param.type_annotation.lower()
                    if "int" in type_str:
                        param_sort = z3.IntSort()
                        sort_name = "Int"
                    elif "float" in type_str or "real" in type_str:
                        param_sort = z3.RealSort()
                        sort_name = "Real"
                    elif "bool" in type_str:
                        param_sort = z3.BoolSort()
                        sort_name = "Bool"
                    elif "str" in type_str:
                        param_sort = z3.StringSort()
                        sort_name = "String"
                    else:
                        # Default to String for unknown types
                        param_sort = z3.StringSort()
                        sort_name = f"String (fallback from {param.type_annotation})"
                else:
                    # Default to String for untyped parameters
                    param_sort = z3.StringSort()
                    sort_name = "String (untyped)"

                logger.debug(f"Creating symbolic parameter: {param_name} ({sort_name})")
                # declare_symbolic expects z3.Sort objects (IntSort(), BoolSort(), etc.)
                # param_sort is already the result of z3.IntSort(), so it's a Sort object
                self._interpreter.declare_symbolic(
                    param_name, cast(z3.Sort, param_sort)
                )

            # Execute the function body instead of module body
            modified_ir = IRModule(
                loc=ir_module.loc,
                source_language=ir_module.source_language,
                body=func_def.body,
                docstring=ir_module.docstring,
            )
            execution_result = self._interpreter.execute(modified_ir)
        else:
            # Normal module-level execution
            execution_result = self._interpreter.execute(ir_module)

        terminal_states = execution_result.states

        # Step 3: Process each path through solver
        result = AnalysisResult(
            all_variables=inferred_types,
            total_paths=len(terminal_states),
        )

        for i, state in enumerate(terminal_states):
            path_result = self._process_path(i, state)
            result.paths.append(path_result)

            if path_result.status == PathStatus.FEASIBLE:
                result.feasible_count += 1
            elif path_result.status == PathStatus.INFEASIBLE:
                result.infeasible_count += 1

        return result

    def _process_path(self, path_id: int, state: SymbolicState) -> PathResult:
        """Process a single execution path through the solver."""
        # Build list of Z3 constraints
        constraints = list(state.constraints)

        # Add any preconditions from manual declarations
        constraints.extend(self._preconditions)

        # Get variables from state
        state_vars = state.variables
        variables_list = list(state_vars.values())
        variable_names = list(state_vars.keys())

        # Check satisfiability (solver is initialized in _analyze_uncached)
        if self._solver is None:
            raise RuntimeError("Solver not initialized - call _analyze_uncached first")
        solver_result = self._solver.solve(constraints, variables_list, variable_names)

        if solver_result.status == SolverStatus.SAT:
            # Extract variable values (already marshaled to Python natives)
            variables = {}
            for name, expr in state_vars.items():
                if solver_result.model and name in solver_result.model:
                    variables[name] = solver_result.model[name]
                elif solver_result.model and str(expr) in solver_result.model:
                    # [20251214_FEATURE] Fall back to expression key if solver named it
                    variables[name] = solver_result.model[str(expr)]
                else:
                    # Variable not in model - might be unconstrained
                    variables[name] = None

            return PathResult(
                path_id=path_id,
                status=PathStatus.FEASIBLE,
                constraints=constraints,
                variables=variables,
                model=solver_result.model,
            )
        elif solver_result.status == SolverStatus.UNSAT:
            return PathResult(
                path_id=path_id,
                status=PathStatus.INFEASIBLE,
                constraints=constraints,
                variables={},
            )
        else:
            # UNKNOWN or TIMEOUT
            return PathResult(
                path_id=path_id,
                status=PathStatus.UNKNOWN,
                constraints=constraints,
                variables={},
            )

    def declare_symbolic(self, name: str, sort: z3.SortRef) -> z3.ExprRef:
        """
        Manually declare a symbolic variable.

        This is for advanced use when you want to constrain inputs
        before calling analyze().

        Args:
            name: Variable name
            sort: Z3 sort (z3.IntSort(), z3.BoolSort(), z3.StringSort())

        Returns:
            Z3 expression reference for the symbolic variable

        Example:
            >>> analyzer = SymbolicAnalyzer()
            >>> x = analyzer.declare_symbolic('x', z3.IntSort())
            >>> analyzer.add_precondition(x > 0)
            >>> result = analyzer.analyze('y = x * 2')
        """
        if sort == z3.IntSort():
            var = z3.Int(name)
        elif sort == z3.BoolSort():
            var = z3.Bool(name)
        elif sort == z3.StringSort():
            var = z3.String(name)
        else:
            raise NotImplementedError(
                f"Only IntSort, BoolSort, and StringSort supported, got {sort}"
            )

        self._declared_symbols[name] = var
        return var

    def add_precondition(self, constraint: z3.BoolRef) -> None:
        """
        Add a precondition constraint.

        All preconditions are added to every path during analysis.

        Args:
            constraint: Z3 boolean constraint
        """
        self._preconditions.append(constraint)

    def find_inputs(self, target_condition: z3.BoolRef) -> Optional[Dict[str, Any]]:
        """
        Find input values that make a target condition true.

        This is the "reverse" query: given a target (e.g., error condition),
        find inputs that trigger it.

        Args:
            target_condition: Z3 boolean expression representing target

        Returns:
            Dictionary of variable names to concrete values, or None if impossible

        Example:
            >>> analyzer = SymbolicAnalyzer()
            >>> x = analyzer.declare_symbolic('x', z3.IntSort())
            >>> result = analyzer.find_inputs(x * x == 16)
            >>> print(result)  # {'x': 4} or {'x': -4}
        """
        if self._solver is None:
            self._solver = ConstraintSolver(timeout_ms=self.solver_timeout)

        constraints = list(self._preconditions) + [target_condition]
        # Extract variables from declared symbols for model extraction
        variables = list(self._declared_symbols.values())
        variable_names = list(self._declared_symbols.keys())
        solver_result = self._solver.solve(constraints, variables, variable_names)

        if solver_result.status == SolverStatus.SAT:
            return solver_result.model
        return None

    def get_solver(self) -> ConstraintSolver:
        """Get the underlying constraint solver for advanced use."""
        if self._solver is None:
            self._solver = ConstraintSolver(timeout_ms=self.solver_timeout)
        return self._solver

    def reset(self) -> None:
        """Reset analyzer state for fresh analysis."""
        self._preconditions.clear()
        self._declared_symbols.clear()
        self._type_engine = None
        self._interpreter = None
        self._solver = None


# Legacy alias for backward compatibility
SymbolicExecutionEngine = SymbolicAnalyzer


def create_analyzer(
    max_loop_iterations: int = 10,
    solver_timeout: int = 2000,
) -> SymbolicAnalyzer:
    """
    Create a new symbolic analyzer.

    Factory function for creating analyzers with custom configuration.

    Args:
        max_loop_iterations: Maximum loop iterations (default 10)
        solver_timeout: Solver timeout in ms (default 2000)

    Returns:
        Configured SymbolicAnalyzer instance
    """
    return SymbolicAnalyzer(
        max_loop_iterations=max_loop_iterations,
        solver_timeout=solver_timeout,
    )
