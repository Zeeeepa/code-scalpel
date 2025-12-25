from __future__ import annotations

import ast
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional

import astor

logger = logging.getLogger(__name__)


@dataclass
class FunctionMetrics:
    """Metrics for a function."""

    name: str
    args: list[str]
    kwargs: list[tuple[str, str]]  # (arg_name, default_value)
    return_type: Optional[str]
    complexity: int
    line_count: int
    calls_made: list[str]
    variables_used: set[str]


@dataclass
class ClassMetrics:
    """Metrics for a class."""

    name: str
    bases: list[str]
    methods: list[str]
    attributes: dict[str, Optional[str]]  # attribute_name -> type_hint
    instance_vars: set[str]
    class_vars: set[str]


class ASTAnalyzer:
    """
    Advanced Python code analyzer using Abstract Syntax Trees (ASTs).
    """

    def __init__(self, cache_enabled: bool = True):
        self.ast_cache: dict[str, ast.AST] = {}
        self.cache_enabled = cache_enabled
        self.current_context: list[str] = []  # Track current function/class context
        # ====================================================================
        # TIER 1: COMMUNITY (Free - High Priority)
        # ====================================================================
        # [20251224_TIER1_TODO] FEATURE: Enhanced caching with LRU eviction
        #   Purpose: Improve performance for large codebases
        #   Steps:
        #     1. Implement bounded cache size with LRU eviction
        #     2. Add cache hit/miss statistics
        #     3. Support cache invalidation by file path
        #     4. Add 15+ tests for cache behavior

        # [20251224_TIER1_TODO] FEATURE: Improve function metrics accuracy
        #   Purpose: Provide better code quality insights
        #   Steps:
        #     1. Track decorator information (staticmethod, classmethod, property)
        #     2. Detect generator functions and coroutines
        #     3. Support type hints in complexity calculation
        #     4. Add 20+ tests for decorator and generator detection

        # [20251224_TIER1_TODO] TEST: Adversarial tests for code analysis
        #   - Empty functions, deeply nested code
        #   - Unicode identifiers, edge case naming
        #   - Large classes with minimal functions

        # ====================================================================
        # TIER 2: PRO (Commercial - Medium Priority)
        # ====================================================================
        # [20251224_TIER2_TODO] FEATURE: Type hint inference from code analysis
        #   Purpose: Enable type checking without explicit annotations
        #   Steps:
        #     1. Infer return types from return statements
        #     2. Infer parameter types from usage patterns
        #     3. Support PEP 484 annotations
        #     4. Generate type hints for untyped code
        #     5. Add 30+ tests for type inference accuracy

        # [20251224_TIER2_TODO] FEATURE: Support async function metrics and analysis
        #   Purpose: Analyze modern async/await patterns
        #   Steps:
        #     1. Detect async/await patterns
        #     2. Track coroutine awaits and yields
        #     3. Analyze async context managers
        #     4. Calculate async complexity metrics
        #     5. Add 25+ tests for async detection

        # [20251224_TIER2_TODO] ENHANCEMENT: Data flow analysis for variable usage
        #   Purpose: Track variable lifecycle and detect issues
        #   Steps:
        #     1. Build def-use chains for all variables
        #     2. Detect uninitialized variable uses
        #     3. Identify dead assignments
        #     4. Track variable scope and visibility
        #     5. Add 35+ tests for def-use analysis

        # ====================================================================
        # TIER 3: ENTERPRISE (Commercial - Lower Priority)
        # ====================================================================
        # [20251224_TIER3_TODO] FEATURE: Class inheritance analysis
        #   Purpose: Analyze object-oriented design patterns
        #   Steps:
        #     1. Calculate inheritance depth
        #     2. Detect diamond inheritance patterns
        #     3. Analyze method override patterns
        #     4. Calculate class cohesion metrics
        #     5. Add 25+ tests for inheritance analysis

        # [20251224_TIER3_TODO] FEATURE: Performance optimization analysis
        #   Purpose: Identify inefficient code patterns
        #   Steps:
        #     1. Detect inefficient patterns (list comprehensions vs loops)
        #     2. Identify expensive operations in loops
        #     3. Suggest optimization opportunities
        #     4. Calculate complexity vs performance impact
        #     5. Add 30+ tests for pattern detection

        # [20251224_TIER3_TODO] ENHANCEMENT: Security-focused analysis
        #   Purpose: Extend vulnerability detection
        #   Steps:
        #     1. Add more vulnerability types beyond SQL injection
        #     2. Implement taint tracking for sensitive operations
        #     3. Detect hardcoded secrets and credentials
        #     4. Cross-file vulnerability tracking
        #     5. Add 40+ tests for security patterns

    def parse_to_ast(self, code: str) -> ast.AST:
        """Parse Python code into an AST with caching."""
        if self.cache_enabled and code in self.ast_cache:
            return self.ast_cache[code]

        try:
            tree = ast.parse(code)
            if self.cache_enabled:
                self.ast_cache[code] = tree
            return tree
        except SyntaxError as e:
            logger.error(f"Syntax error while parsing code: {e}")
            raise

    def ast_to_code(self, node: ast.AST) -> str:
        """Convert AST back to source code with formatting."""
        return astor.to_source(node)

    def analyze_function(self, node: ast.FunctionDef) -> FunctionMetrics:
        """Analyze a function definition comprehensively."""
        # Extract arguments
        args = [arg.arg for arg in node.args.args]
        kwargs = [
            (
                node.args.args[len(node.args.args) - len(node.args.defaults) + i].arg,
                astor.to_source(default).strip(),
            )
            for i, default in enumerate(node.args.defaults)
        ]

        # Extract return type
        return_type = astor.to_source(node.returns).strip() if node.returns else None

        # Calculate complexity
        complexity = self._calculate_complexity(node)

        # Count lines
        line_count = self._count_node_lines(node)

        # Analyze function calls
        calls_made = self._extract_function_calls(node)

        # Analyze variables
        variables_used = self._extract_variables(node)

        return FunctionMetrics(
            name=node.name,
            args=args,
            kwargs=kwargs,
            return_type=return_type,
            complexity=complexity,
            line_count=line_count,
            calls_made=calls_made,
            variables_used=variables_used,
        )

    def analyze_class(self, node: ast.ClassDef) -> ClassMetrics:
        """Analyze a class definition comprehensively."""
        # Extract base classes
        bases = [astor.to_source(base).strip() for base in node.bases]

        # Extract methods and attributes
        methods = []
        attributes = {}
        instance_vars = set()
        class_vars = set()

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attributes[item.target.id] = (
                    astor.to_source(item.annotation).strip()
                    if item.annotation
                    else None
                )
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_vars.add(target.id)

        # Find instance variables in __init__
        init_method = next(
            (
                m
                for m in node.body
                if isinstance(m, ast.FunctionDef) and m.name == "__init__"
            ),
            None,
        )
        if init_method:
            instance_vars = self._extract_instance_vars(init_method)

        return ClassMetrics(
            name=node.name,
            bases=bases,
            methods=methods,
            attributes=attributes,
            instance_vars=instance_vars,
            class_vars=class_vars,
        )

    def analyze_code_style(self, tree: ast.AST) -> dict[str, Any]:
        """Analyze code style and potential issues."""
        issues = defaultdict(list)

        # Check function lengths
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if self._count_node_lines(node) > 20:
                    issues["long_functions"].append(
                        f"Function '{node.name}' is too long ({self._count_node_lines(node)} lines)"
                    )

        # Check nesting depth
        self._check_nesting_depth(tree, issues)

        # Check naming conventions
        self._check_naming_conventions(tree, issues)

        return dict(issues)

    def find_security_issues(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Identify potential security issues in the code."""
        issues = []

        # Check for dangerous function calls
        dangerous_functions = {
            "eval",
            "exec",
            "os.system",
            "subprocess.call",
            "subprocess.Popen",
            "pickle.loads",
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name in dangerous_functions:
                    issues.append(
                        {
                            "type": "dangerous_function",
                            "function": func_name,
                            "line": getattr(node, "lineno", None),
                        }
                    )

        # Check for SQL injection vulnerabilities
        self._check_sql_injection(tree, issues)

        return issues

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a code block."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1

        return complexity

    def _count_node_lines(self, node: ast.AST) -> int:
        """Count the number of lines in a node."""
        lineno = getattr(node, "lineno", None)
        end_lineno = getattr(node, "end_lineno", None)
        if lineno and end_lineno:
            return end_lineno - lineno + 1
        return 1

    def _extract_function_calls(self, node: ast.AST) -> list[str]:
        """Extract all function calls within a node."""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(
                        f"{astor.to_source(child.func.value).strip()}.{child.func.attr}"
                    )
        return calls

    def _extract_variables(self, node: ast.AST) -> set[str]:
        """Extract all variables used within a node."""
        variables = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                variables.add(child.id)
        return variables

    def _extract_instance_vars(self, init_method: ast.FunctionDef) -> set[str]:
        """Extract instance variables from __init__ method."""
        instance_vars = set()
        for node in ast.walk(init_method):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "self"
            ):
                instance_vars.add(node.attr)
        return instance_vars

    def _check_nesting_depth(self, tree: ast.AST, issues: defaultdict) -> None:
        """Check for excessive nesting depth."""

        def get_nesting_depth(node, current_depth=0):
            if isinstance(node, (ast.If, ast.For, ast.While)):
                current_depth += 1
                if current_depth > 3:
                    issues["deep_nesting"].append(
                        f"Deep nesting detected at line {node.lineno}"
                    )
            for child in ast.iter_child_nodes(node):
                get_nesting_depth(child, current_depth)

        get_nesting_depth(tree)

    def _check_naming_conventions(self, tree: ast.AST, issues: defaultdict) -> None:
        """Check Python naming conventions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and not node.name[0].isupper():
                issues["naming_conventions"].append(
                    f"Class '{node.name}' should use CapWords convention"
                )
            elif isinstance(node, ast.FunctionDef) and not node.name.islower():
                issues["naming_conventions"].append(
                    f"Function '{node.name}' should use lowercase_with_underscores"
                )

    def _check_sql_injection(self, tree: ast.AST, issues: list[dict[str, Any]]) -> None:
        """Check for potential SQL injection vulnerabilities."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {"execute", "executemany"}:
                    # Check if string formatting or concatenation is used
                    if any(
                        isinstance(arg, (ast.BinOp, ast.JoinedStr)) for arg in node.args
                    ):
                        issues.append(
                            {
                                "type": "sql_injection",
                                "line": node.lineno,
                                "message": "Possible SQL injection vulnerability",
                            }
                        )

    def _get_call_name(self, node: ast.Call) -> str:
        """Get the full name of a function call."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            return f"{astor.to_source(node.func.value).strip()}.{node.func.attr}"
        return ""
