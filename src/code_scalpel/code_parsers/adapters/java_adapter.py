"""
Java Parser Adapter - IParser interface for Java parser.

[20251221_FEATURE] Bridges TreeSitterJavaParser to the IParser interface.
============================================================================
============================================================================
COMMUNITY TIER - Core Java Adapter (P0-P2)
============================================================================

[P0_CRITICAL] Enhance Java-specific extraction:
    - Extract annotations with full metadata
    - Parse generic type parameters
    - Extract lambda expressions
    - Support method references
    - Extract nested classes and inner classes
    - Test count: 30 tests (extraction completeness)

[P1_HIGH] Improve error handling:
    - Better syntax error messages with context
    - Support partial parsing on errors
    - Add error recovery strategies
    - Provide fix suggestions
    - Test count: 20 tests (error handling)

[P1_HIGH] Add Java version detection:
    - Detect Java version from syntax (8, 11, 17, 21)
    - Support version-specific features
    - Add compatibility warnings
    - Handle preview features
    - Test count: 25 tests (version detection)

[P2_MEDIUM] Enhance metrics calculation:
    - Add package-level metrics
    - Calculate inheritance depth
    - Track coupling metrics
    - Add cohesion metrics (LCOM)
    - Test count: 25 tests (metrics accuracy)

[P2_MEDIUM] Add import analysis:
    - Extract all imports with types
    - Detect unused imports
    - Find wildcard imports
    - Build import dependency graph
    - Test count: 20 tests (import analysis)

============================================================================
PRO TIER - Advanced Java Adapter (P1-P3)
============================================================================

[P1_HIGH] Integrate static analysis:
    - Add SpotBugs integration
    - Support PMD checks
    - Integrate Checkstyle
    - Add SonarQube analysis
    - Test count: 35 tests (static analysis integration)

[P1_HIGH] Add semantic analysis:
    - Resolve type information
    - Track inheritance chains
    - Analyze method overrides
    - Detect polymorphism patterns
    - Test count: 40 tests (semantic analysis)

[P2_MEDIUM] Implement code transformation:
    - Support refactoring operations
    - Add code formatting (Google Java Format)
    - Generate modified AST
    - Support code generation
    - Test count: 30 tests (transformation)

[P2_MEDIUM] Add framework detection:
    - Detect Spring framework usage
    - Identify JPA/Hibernate patterns
    - Find JAX-RS endpoints
    - Detect JUnit tests
    - Test count: 30 tests (framework detection)

[P3_LOW] Support bytecode analysis:
    - Parse compiled .class files
    - Extract bytecode metrics
    - Analyze JVM optimizations
    - Support decompilation
    - Test count: 35 tests (bytecode analysis)

============================================================================
ENTERPRISE TIER - Enterprise Java Adapter (P2-P4)
============================================================================

[P2_MEDIUM] Add security analysis:
    - Integrate FindSecBugs
    - Detect OWASP vulnerabilities
    - Find hardcoded secrets
    - Analyze authentication/authorization
    - Test count: 40 tests (security scanning)

[P2_MEDIUM] Implement incremental parsing:
    - Parse only changed classes
    - Cache parsed results
    - Support streaming for large files
    - Add efficient AST diffing
    - Test count: 30 tests (incremental parsing)

[P3_LOW] Add enterprise compliance:
    - Check code against enterprise standards
    - Enforce mandatory documentation
    - Validate license headers
    - Generate compliance reports
    - Test count: 25 tests (compliance)

[P3_LOW] Implement performance profiling:
    - Profile parsing time
    - Track memory usage
    - Identify bottlenecks
    - Add optimization hints
    - Test count: 20 tests (profiling)

[P4_LOW] Add ML-driven analysis:
    - Predict code quality
    - Suggest refactorings via ML
    - Detect code clones
    - Find potential bugs via anomaly detection
    - Test count: 30 tests (ML integration)

============================================================================
TOTAL TEST ESTIMATE: 435 tests (140 COMMUNITY + 165 PRO + 130 ENTERPRISE)
============================================================================"""

from typing import Any, Dict, List, Optional

from ..interface import IParser, Language, ParseResult

# Try to import the Java parser
try:
    from ..java_parsers import TreeSitterJavaParser

    JAVA_PARSER_AVAILABLE = True
except ImportError:
    JAVA_PARSER_AVAILABLE = False
    TreeSitterJavaParser = None  # type: ignore


class JavaParserAdapter(IParser):
    """
    Adapter that wraps TreeSitterJavaParser to implement IParser interface.

    [20251221_FEATURE] Enables Java parsing through unified factory.

    Example:
        >>> adapter = JavaParserAdapter()
        >>> result = adapter.parse("public class Hello { public void greet() {} }")
        >>> print(result.language)
        Language.JAVA
    """

    def __init__(self):
        """Initialize the Java parser adapter."""
        if not JAVA_PARSER_AVAILABLE or TreeSitterJavaParser is None:
            raise ImportError(
                "TreeSitterJavaParser not available. Install tree-sitter-java: "
                "pip install tree-sitter tree-sitter-java"
            )
        self._parser = TreeSitterJavaParser()
        self._last_result: Optional[Any] = None

    def parse(self, code: str) -> ParseResult:
        """
        Parse Java code into an AST.

        Args:
            code: Java source code

        Returns:
            ParseResult with AST, errors, warnings, and metrics
        """
        try:
            # Use the underlying parser's parse method
            java_result = self._parser.parse(code)
            self._last_result = java_result

            # Convert to IParser ParseResult format
            return ParseResult(
                ast=java_result,  # Store the full JavaParseResult
                errors=self._convert_errors(java_result),
                warnings=self._extract_warnings(java_result),
                metrics=self._extract_metrics(java_result),
                language=Language.JAVA,
            )
        except Exception as e:
            return ParseResult(
                ast=None,
                errors=[{"message": str(e), "line": 0, "column": 0}],
                warnings=[],
                metrics={},
                language=Language.JAVA,
            )

    def get_functions(self, ast_tree: Any) -> List[str]:
        """
        Get list of method names from the AST.

        In Java, standalone functions don't exist - all are methods.
        This returns all method names across all classes.

        Args:
            ast_tree: Parsed AST (JavaParseResult or None to use last)

        Returns:
            List of method names (qualified as ClassName.methodName)
        """
        result = ast_tree if ast_tree is not None else self._last_result

        if result is None:
            return []

        methods = []

        # Extract from classes
        for cls in getattr(result, "classes", []):
            class_name = cls.name
            for method in getattr(cls, "methods", []):
                # Include class name for qualification
                methods.append(f"{class_name}.{method.name}")

        # Extract from interfaces
        for iface in getattr(result, "interfaces", []):
            iface_name = iface.name
            for method in getattr(iface, "methods", []):
                methods.append(f"{iface_name}.{method.name}")

        # Extract from enums (enum methods)
        for enum in getattr(result, "enums", []):
            enum_name = enum.name
            for method in getattr(enum, "methods", []):
                methods.append(f"{enum_name}.{method.name}")

        return methods

    def get_classes(self, ast_tree: Any) -> List[str]:
        """
        Get list of class/interface/enum names from the AST.

        Args:
            ast_tree: Parsed AST (JavaParseResult or None to use last)

        Returns:
            List of type names (classes, interfaces, enums)
        """
        result = ast_tree if ast_tree is not None else self._last_result

        if result is None:
            return []

        names = []

        # Classes
        for cls in getattr(result, "classes", []):
            names.append(cls.name)

        # Interfaces
        for iface in getattr(result, "interfaces", []):
            names.append(iface.name)

        # Enums
        for enum in getattr(result, "enums", []):
            names.append(enum.name)

        return names

    def get_methods_for_class(self, class_name: str, ast_tree: Any = None) -> List[str]:
        """
        Get method names for a specific class.

        [20251221_FEATURE] Java-specific helper method.

        Args:
            class_name: Name of the class
            ast_tree: Parsed AST (optional)

        Returns:
            List of method names in that class
        """
        result = ast_tree if ast_tree is not None else self._last_result

        if result is None:
            return []

        for cls in getattr(result, "classes", []):
            if cls.name == class_name:
                return [m.name for m in getattr(cls, "methods", [])]

        return []

    def get_fields_for_class(self, class_name: str, ast_tree: Any = None) -> List[str]:
        """
        Get field names for a specific class.

        [20251221_FEATURE] Java-specific helper method.

        Args:
            class_name: Name of the class
            ast_tree: Parsed AST (optional)

        Returns:
            List of field names in that class
        """
        result = ast_tree if ast_tree is not None else self._last_result

        if result is None:
            return []

        for cls in getattr(result, "classes", []):
            if cls.name == class_name:
                return [f.name for f in getattr(cls, "fields", [])]

        return []

    def _convert_errors(self, result: Any) -> List[Dict[str, Any]]:
        """Convert parser errors to standard format."""
        errors = []

        # Check for syntax errors in the result
        if hasattr(result, "errors") and result.errors:
            for err in result.errors:
                if isinstance(err, dict):
                    errors.append(err)
                elif isinstance(err, str):
                    errors.append({"message": err, "line": 0, "column": 0})
                else:
                    errors.append(
                        {
                            "message": str(err),
                            "line": getattr(err, "line", 0),
                            "column": getattr(err, "column", 0),
                        }
                    )

        return errors

    def _extract_warnings(self, result: Any) -> List[str]:
        """Extract warnings from parse result."""
        warnings = []

        if hasattr(result, "warnings"):
            warnings.extend(result.warnings)

        return warnings

    def _extract_metrics(self, result: Any) -> Dict[str, Any]:
        """Extract metrics from parse result."""
        metrics = {}

        if result is None:
            return metrics

        # Count classes, interfaces, enums
        metrics["class_count"] = len(getattr(result, "classes", []))
        metrics["interface_count"] = len(getattr(result, "interfaces", []))
        metrics["enum_count"] = len(getattr(result, "enums", []))

        # Count total methods
        total_methods = 0
        total_fields = 0
        max_complexity = 0

        for cls in getattr(result, "classes", []):
            methods = getattr(cls, "methods", [])
            total_methods += len(methods)
            total_fields += len(getattr(cls, "fields", []))

            for method in methods:
                complexity = getattr(method, "complexity", 1)
                max_complexity = max(max_complexity, complexity)

        metrics["method_count"] = total_methods
        metrics["field_count"] = total_fields
        metrics["max_complexity"] = max_complexity

        # Package info
        if hasattr(result, "package") and result.package:
            metrics["package"] = result.package

        return metrics
