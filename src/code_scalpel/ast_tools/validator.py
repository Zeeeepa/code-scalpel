import ast
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(Enum):
    """Severity levels for validation issues."""

    INFO = 1
    WARNING = 2
    ERROR = 3


@dataclass
class ValidationIssue:
    """Represents a validation issue."""

    message: str
    severity: Severity
    line: Optional[int] = None
    column: Optional[int] = None
    code: Optional[str] = None


class ASTValidator:
    """
    Advanced AST validator with configurable rules and detailed reporting.

    ====================================================================
    TIER 1: COMMUNITY (Free - High Priority)
    ====================================================================
    [20251224_TIER1_TODO] FEATURE: Validate nesting depth limits
      - Track nesting depth during traversal
      - Check against max_nesting_depth config
      - Report violations with line numbers
      - Add 15+ tests for nesting validation

    [20251224_TIER1_TODO] FEATURE: Validate code style basics
      - Check naming conventions
      - Validate line lengths
      - Check indentation consistency
      - Add 15+ tests for style validation

    [20251224_TIER1_TODO] FEATURE: Validate docstring presence
      - Check function docstrings
      - Check class docstrings
      - Verify docstring format
      - Add 12+ tests for docstring validation

    [20251224_TIER1_TODO] FEATURE: Validate function size limits
      - Count statements in functions
      - Check against max_function_length
      - Report oversized functions
      - Add 12+ tests for size validation

    ====================================================================
    TIER 2: PRO (Commercial - Medium Priority)
    ====================================================================
    [20251224_TIER2_TODO] FEATURE: Validate cognitive complexity
      - Calculate complexity score
      - Check against thresholds
      - Identify complex paths
      - Add 15+ tests for complexity

    [20251224_TIER2_TODO] FEATURE: Validate function parameters
      - Check parameter count against limits
      - Detect unused parameters
      - Validate parameter types
      - Add 12+ tests for parameters

    [20251224_TIER2_TODO] FEATURE: Validate class sizes
      - Count attributes and methods
      - Check against max_class_length
      - Identify God Classes
      - Add 12+ tests for class validation

    [20251224_TIER2_TODO] FEATURE: Custom rule registration
      - Register validation plugins
      - Apply custom rules
      - Support rule configuration
      - Add 15+ tests for custom rules

    [20251224_TIER2_TODO] FEATURE: Auto-fix suggestions
      - Suggest code formatting fixes
      - Recommend variable renames
      - Propose simplifications
      - Add 15+ tests for suggestions

    ====================================================================
    TIER 3: ENTERPRISE (Commercial - Lower Priority)
    ====================================================================
    [20251224_TIER3_TODO] FEATURE: Style guide enforcement
      - Load Black/Ruff configurations
      - Apply style checks
      - Enforce naming patterns
      - Add 15+ tests for style guides

    [20251224_TIER3_TODO] FEATURE: Language-specific validation
      - Python-specific rules
      - JavaScript/TypeScript rules
      - Java-specific rules
      - Add 15+ tests for languages

    [20251224_TIER3_TODO] FEATURE: Security validation
      - Detect security patterns
      - Check for injection risks
      - Validate credential handling
      - Add 15+ tests for security

    [20251224_TIER3_TODO] FEATURE: ML-based anomaly detection
      - Learn code patterns
      - Detect deviations
      - Suggest corrections
      - Add 12+ tests for anomalies
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = {
            "max_line_length": 80,
            "max_function_length": 50,
            "max_class_length": 200,
            "max_nesting_depth": 4,
            "max_arguments": 5,
            "min_variable_length": 2,
            "max_variable_length": 30,
            "max_cognitive_complexity": 15,
            **(config or {}),
        }
        self.issues: list[ValidationIssue] = []

    def validate(self, tree: ast.AST, code: str) -> list[ValidationIssue]:
        """Perform all validations on the AST."""
        self.issues = []

        # Structure validations
        self._validate_nesting(tree)
        self._validate_complexity(tree)
        self._validate_sizes(tree)

        # Naming validations
        self._validate_naming_conventions(tree)

        # Code style validations
        self._validate_line_lengths(code)
        self._validate_docstrings(tree)

        # Security validations
        self._validate_security(tree)

        return sorted(self.issues, key=lambda x: (x.severity.value, x.line or 0))

    def _validate_nesting(self, tree: ast.AST) -> None:
        """Validate nesting depth of code blocks."""

        class NestingValidator(ast.NodeVisitor):
            def __init__(self, max_depth: int):
                self.max_depth = max_depth
                self.current_depth = 0
                self.issues = []

            def visit(self, node: ast.AST) -> None:
                if isinstance(node, (ast.For, ast.While, ast.If, ast.With)):
                    self.current_depth += 1
                    if self.current_depth > self.max_depth:
                        self.issues.append(
                            ValidationIssue(
                                f"Nesting depth exceeds maximum ({self.max_depth})",
                                Severity.WARNING,
                                getattr(node, "lineno", None),
                            )
                        )
                    super().generic_visit(node)
                    self.current_depth -= 1
                else:
                    super().generic_visit(node)

        validator = NestingValidator(self.config["max_nesting_depth"])
        validator.visit(tree)
        self.issues.extend(validator.issues)

    def _validate_complexity(self, tree: ast.AST) -> None:
        """Validate cognitive complexity of functions."""

        class ComplexityValidator(ast.NodeVisitor):
            def __init__(self, max_complexity: int):
                self.max_complexity = max_complexity
                self.issues = []

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                complexity = self._calculate_cognitive_complexity(node)
                if complexity > self.max_complexity:
                    self.issues.append(
                        ValidationIssue(
                            f"Function '{node.name}' has too high cognitive "
                            f"complexity ({complexity})",
                            Severity.WARNING,
                            node.lineno,
                        )
                    )
                self.generic_visit(node)

            def _calculate_cognitive_complexity(self, node: ast.AST) -> int:
                complexity = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                return complexity

        validator = ComplexityValidator(self.config["max_cognitive_complexity"])
        validator.visit(tree)
        self.issues.extend(validator.issues)

    def _validate_naming_conventions(self, tree: ast.AST) -> None:
        """Validate naming conventions."""

        class NamingValidator(ast.NodeVisitor):
            def __init__(self):
                self.issues = []

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                if not node.name[0].isupper():
                    self.issues.append(
                        ValidationIssue(
                            f"Class name '{node.name}' should use CapWords convention",
                            Severity.WARNING,
                            node.lineno,
                        )
                    )
                self.generic_visit(node)

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                if not node.name.islower() and "_" not in node.name:
                    self.issues.append(
                        ValidationIssue(
                            f"Function name '{node.name}' should use "
                            "lowercase_with_underscores convention",
                            Severity.WARNING,
                            node.lineno,
                        )
                    )
                self.generic_visit(node)

            def visit_Name(self, node: ast.Name) -> None:
                if isinstance(node.ctx, ast.Store):
                    if not re.match(r"^[a-z_][a-z0-9_]*$", node.id):
                        self.issues.append(
                            ValidationIssue(
                                f"Variable name '{node.id}' should use "
                                "lowercase_with_underscores convention",
                                Severity.INFO,
                                getattr(node, "lineno", None),
                            )
                        )

        validator = NamingValidator()
        validator.visit(tree)
        self.issues.extend(validator.issues)

    def _validate_sizes(self, tree: ast.AST) -> None:
        """Validate function and class sizes."""

        class SizeValidator(ast.NodeVisitor):
            def __init__(self, max_function_length: int, max_class_length: int):
                self.max_function_length = max_function_length
                self.max_class_length = max_class_length
                self.issues = []

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                length = len(node.body)
                if length > self.max_function_length:
                    self.issues.append(
                        ValidationIssue(
                            f"Function '{node.name}' is too long ({length} lines)",
                            Severity.WARNING,
                            node.lineno,
                        )
                    )
                self.generic_visit(node)

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                length = sum(len(getattr(item, "body", [])) for item in node.body)
                if length > self.max_class_length:
                    self.issues.append(
                        ValidationIssue(
                            f"Class '{node.name}' is too long ({length} lines)",
                            Severity.WARNING,
                            node.lineno,
                        )
                    )
                self.generic_visit(node)

        validator = SizeValidator(
            self.config["max_function_length"], self.config["max_class_length"]
        )
        validator.visit(tree)
        self.issues.extend(validator.issues)

    def _validate_line_lengths(self, code: str) -> None:
        """Validate line lengths."""
        for i, line in enumerate(code.split("\n"), start=1):
            if len(line) > self.config["max_line_length"]:
                self.issues.append(
                    ValidationIssue(
                        f"Line {i} exceeds maximum length ({self.config['max_line_length']} characters)",
                        Severity.WARNING,
                        i,
                    )
                )

    def _validate_docstrings(self, tree: ast.AST) -> None:
        """Validate presence of docstrings in functions and classes."""

        class DocstringValidator(ast.NodeVisitor):
            def __init__(self):
                self.issues = []

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                if not ast.get_docstring(node):
                    self.issues.append(
                        ValidationIssue(
                            f"Class '{node.name}' is missing a docstring",
                            Severity.INFO,
                            node.lineno,
                        )
                    )
                self.generic_visit(node)

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
                if not ast.get_docstring(node):
                    self.issues.append(
                        ValidationIssue(
                            f"Function '{node.name}' is missing a docstring",
                            Severity.INFO,
                            node.lineno,
                        )
                    )
                self.generic_visit(node)

        validator = DocstringValidator()
        validator.visit(tree)
        self.issues.extend(validator.issues)

    def _validate_security(self, tree: ast.AST) -> None:
        """Validate security issues."""

        class SecurityValidator(ast.NodeVisitor):
            def __init__(self):
                self.issues = []

            def visit_Call(self, node: ast.Call) -> None:
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in {"execute", "executemany"}:
                        # Check if string formatting or concatenation is used
                        if any(
                            isinstance(arg, (ast.BinOp, ast.JoinedStr))
                            for arg in node.args
                        ):
                            self.issues.append(
                                ValidationIssue(
                                    "Possible SQL injection vulnerability",
                                    Severity.ERROR,
                                    node.lineno,
                                )
                            )
                self.generic_visit(node)

        validator = SecurityValidator()
        validator.visit(tree)
        self.issues.extend(validator.issues)
