"""
CodeAnalyzer - Stable analysis pipeline for code-scalpel.

# [20251224_REFACTOR] Moved from code_scalpel/code_analyzer.py to
# code_scalpel/analysis/code_analyzer.py as part of Issue #3
# in PROJECT_REORG_REFACTOR.md Phase 1.

This module provides a unified interface for:
- AST analysis and parsing
- PDG (Program Dependence Graph) construction
- Symbolic execution for path analysis
- Dead code detection
- Refactoring via PDG-guided transformations

TODO: CodeAnalyzer Enhancement Roadmap
======================================

COMMUNITY (Current & Planned):
- TODO [COMMUNITY]: Leverage code_parsers.RuffParser for fast linting integration (current)
- TODO [COMMUNITY]: Implement language-agnostic AnalysisResult with unified metrics
- TODO [COMMUNITY]: Add Halstead complexity metrics
- TODO [COMMUNITY]: Implement maintainability index calculation
- TODO [COMMUNITY]: Implement extract_function() refactoring
- TODO [COMMUNITY]: Implement extract_variable() refactoring
- TODO [COMMUNITY]: Implement inline_variable() refactoring
- TODO [COMMUNITY]: Add automatic import management during refactoring

PRO (Enhanced Features):
- TODO [PRO]: Use code_parsers.ParserFactory instead of direct ast.parse()
- TODO [PRO]: Support code_parsers.ParseResult for unified error handling
- TODO [PRO]: Integrate code_parsers language detection for multi-language files
- TODO [PRO]: Use code_parsers.PythonASTParser for enhanced Python parsing
- TODO [PRO]: Add parser_backend parameter to __init__ for parser selection
- TODO [PRO]: Extend analyze() to support JavaScript/TypeScript via code_parsers
- TODO [PRO]: Add Java analysis using code_parsers.java_parsers
- TODO [PRO]: Create language-specific analyzers that inherit from CodeAnalyzer
- TODO [PRO]: Add cross-file dead code detection (unused exports)
- TODO [PRO]: Implement test coverage integration for dead code validation
- TODO [PRO]: Add code churn metrics (requires git integration)
- TODO [PRO]: Calculate test-to-code ratio
- TODO [PRO]: Add dependency depth metrics
- TODO [PRO]: Add rename_symbol() with scope awareness
- TODO [PRO]: Implement persistent analysis cache (SQLite or file-based)
- TODO [PRO]: Add incremental analysis (only re-analyze changed functions)
- TODO [PRO]: Integrate taint analysis from symbolic_execution_tools

ENTERPRISE (Advanced Capabilities):
- TODO [ENTERPRISE]: Support mixed-language projects (JS + Python)
- TODO [ENTERPRISE]: Add dead code detection for TypeScript (unused types/interfaces)
- TODO [ENTERPRISE]: Support conditional dead code (platform-specific, debug-only)
- TODO [ENTERPRISE]: Add confidence scores based on multiple analysis passes
- TODO [ENTERPRISE]: Integrate with PDG for data-flow based dead code detection
- TODO [ENTERPRISE]: Implement cognitive complexity (beyond cyclomatic)
- TODO [ENTERPRISE]: Implement move_to_module() refactoring
- TODO [ENTERPRISE]: Implement parallel analysis for multi-file projects
- TODO [ENTERPRISE]: Add analysis result serialization for external tools
- TODO [ENTERPRISE]: Implement analysis result diffing for change detection
- TODO [ENTERPRISE]: Add SAST rule engine for custom security patterns
- TODO [ENTERPRISE]: Implement dependency vulnerability scanning
- TODO [ENTERPRISE]: Add secrets detection (API keys, passwords)
- TODO [ENTERPRISE]: Generate SARIF output for security findings
- TODO [ENTERPRISE]: Multi-framework analysis support (Django, Flask, FastAPI)
"""

import ast
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional, Union

import astor
import networkx as nx

# Import code_parsers for multi-language support
CODE_PARSERS_AVAILABLE = False
ParserFactory: Any = None
ParserLanguage: Any = None
_detect_language_func: Optional[Callable[..., Any]] = None

try:
    from .code_parsers.factory import \
        ParserFactory as _PF  # type: ignore[import-not-found]
    from .code_parsers.interface import \
        Language as _PL  # type: ignore[import-not-found]
    from .code_parsers.language_detection import \
        detect_language as _dl  # type: ignore[import-not-found]

    ParserFactory = _PF
    ParserLanguage = _PL
    _detect_language_func = _dl
    CODE_PARSERS_AVAILABLE = True
except ImportError:
    pass

# Configure module logger
logger = logging.getLogger(__name__)


class AnalysisLevel(Enum):
    """Level of analysis to perform."""

    BASIC = "basic"  # AST only
    STANDARD = "standard"  # AST + PDG
    FULL = "full"  # AST + PDG + Symbolic Execution


class AnalysisLanguage(Enum):
    """Supported analysis languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    AUTO = "auto"  # Auto-detect from file extension or content


@dataclass
class DeadCodeItem:
    """Represents a detected dead code element."""

    name: str
    code_type: str  # 'function', 'variable', 'class', 'import', 'statement'
    line_start: int
    line_end: int
    reason: str
    confidence: float  # 0.0 to 1.0


@dataclass
class AnalysisMetrics:
    """Metrics from code analysis."""

    lines_of_code: int = 0
    num_functions: int = 0
    num_classes: int = 0
    num_variables: int = 0
    cyclomatic_complexity: int = 0
    analysis_time_seconds: float = 0.0
    language: str = "python"
    parser_backend: str = "ast"  # Which parser was used
    # Additional metrics from code_parsers
    halstead_volume: float = 0.0
    halstead_difficulty: float = 0.0
    cognitive_complexity: int = 0
    maintainability_index: float = 0.0


@dataclass
class RefactorSuggestion:
    """A suggested refactoring operation."""

    refactor_type: str
    description: str
    target_node: str
    priority: int  # 1-5, higher is more important
    estimated_impact: str


@dataclass
class AnalysisResult:
    """Complete result of code analysis."""

    code: str
    ast_tree: Optional[ast.AST] = None
    pdg: Optional[nx.DiGraph] = None
    call_graph: Optional[nx.DiGraph] = None
    dead_code: list[DeadCodeItem] = field(default_factory=list)
    metrics: AnalysisMetrics = field(default_factory=AnalysisMetrics)
    security_issues: list[dict[str, Any]] = field(default_factory=list)
    refactor_suggestions: list[RefactorSuggestion] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    symbolic_paths: list[dict[str, Any]] = field(default_factory=list)
    # Multi-language support
    language: str = "python"
    parser_result: Optional[Any] = None  # Raw ParseResult from code_parsers
    functions: list[str] = field(default_factory=list)  # Extracted function names
    classes: list[str] = field(default_factory=list)  # Extracted class names


class CodeAnalyzer:
    """
    Unified code analysis pipeline with AST, PDG, and symbolic execution.

    This class provides a stable interface for comprehensive code analysis
    including dead code detection and PDG-guided refactoring.

    Example usage:
        analyzer = CodeAnalyzer()
        result = analyzer.analyze(code)
        print(result.dead_code)

        # Apply refactoring
        new_code = analyzer.apply_refactor(code, 'remove_dead_code')
    """

    def __init__(
        self,
        level: AnalysisLevel = AnalysisLevel.STANDARD,
        language: AnalysisLanguage = AnalysisLanguage.AUTO,
        parser_backend: Optional[str] = None,
        cache_enabled: bool = True,
        max_symbolic_depth: int = 50,
        max_loop_iterations: int = 10,
        use_code_parsers: bool = True,
    ):
        """
        Initialize the CodeAnalyzer.

        Args:
            level: Analysis level (BASIC, STANDARD, or FULL)
            language: Target language (AUTO for detection, or specific language)
            parser_backend: Parser backend to use (e.g., "tree-sitter", "ast", "esprima")
            cache_enabled: Whether to cache analysis results
            max_symbolic_depth: Maximum depth for symbolic execution
            max_loop_iterations: Maximum loop iterations for symbolic execution
            use_code_parsers: Whether to use code_parsers module when available
        """
        self.level = level
        self.language = language
        self.parser_backend = parser_backend
        self.cache_enabled = cache_enabled
        self.max_symbolic_depth = max_symbolic_depth
        self.max_loop_iterations = max_loop_iterations
        self.use_code_parsers = use_code_parsers and CODE_PARSERS_AVAILABLE

        # Caches
        self._ast_cache: dict[str, ast.AST] = {}
        self._pdg_cache: dict[str, tuple[nx.DiGraph, nx.DiGraph]] = {}
        self._analysis_cache: dict[str, AnalysisResult] = {}

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for the analyzer."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger("CodeAnalyzer")

    def analyze(
        self,
        code: str,
        level: Optional[AnalysisLevel] = None,
        language: Optional[AnalysisLanguage] = None,
        filepath: Optional[str] = None,
    ) -> AnalysisResult:
        """
        Perform comprehensive code analysis.

        Args:
            code: Source code to analyze (Python, JavaScript, TypeScript, or Java)
            level: Override the default analysis level
            language: Override the default language (None = use instance default)
            filepath: Optional file path for language detection and context

        Returns:
            AnalysisResult containing all analysis data
        """
        start_time = time.time()
        analysis_level = level or self.level
        analysis_language = language or self.language

        # Detect language if AUTO
        detected_lang = self._detect_language(code, filepath, analysis_language)

        # Check cache
        cache_key = f"{hash(code)}_{analysis_level.value}_{detected_lang}"
        if self.cache_enabled and cache_key in self._analysis_cache:
            return self._analysis_cache[cache_key]

        result = AnalysisResult(code=code, language=detected_lang)

        try:
            # Step 1: Parse to AST (using code_parsers if available and appropriate)
            parse_result = self._parse_code(code, detected_lang, filepath)
            result.ast_tree = parse_result.get("ast")
            result.parser_result = parse_result.get("parser_result")
            result.functions = parse_result.get("functions", [])
            result.classes = parse_result.get("classes", [])

            if result.ast_tree is None and not result.parser_result:
                result.errors.append("Failed to parse code to AST")
                if parse_result.get("errors"):
                    result.errors.extend(parse_result["errors"])
                return result

            # Compute basic metrics
            result.metrics = self._compute_metrics(
                result.ast_tree, code, detected_lang, parse_result
            )

            # Step 2: Build PDG (if STANDARD or FULL level) - Python only for now
            if (
                analysis_level in (AnalysisLevel.STANDARD, AnalysisLevel.FULL)
                and detected_lang == "python"
            ):
                result.pdg, result.call_graph = self._build_pdg(code)

            # Step 3: Symbolic Execution (if FULL level) - Python only for now
            if analysis_level == AnalysisLevel.FULL and detected_lang == "python":
                result.symbolic_paths = self._run_symbolic_execution(code)

            # Step 4: Dead code detection (requires Python AST)
            if result.ast_tree is not None:
                result.dead_code = self._detect_dead_code(
                    result.ast_tree, result.pdg, result.call_graph
                )

                # Step 5: Security analysis (requires Python AST)
                result.security_issues = self._analyze_security(result.ast_tree)

                # Step 6: Generate refactoring suggestions
                result.refactor_suggestions = self._generate_refactor_suggestions(
                    result.ast_tree, result.pdg, result.dead_code
                )

        except SyntaxError as e:
            result.errors.append(f"Syntax error: {str(e)}")
        except Exception as e:
            result.errors.append(f"Analysis error: {str(e)}")
            self.logger.error(f"Analysis failed: {str(e)}")

        # Record analysis time
        result.metrics.analysis_time_seconds = time.time() - start_time

        # Cache result
        if self.cache_enabled:
            self._analysis_cache[cache_key] = result

        return result

    def _parse_to_ast(self, code: str) -> Optional[ast.AST]:
        """Parse code to AST with caching."""
        if self.cache_enabled and code in self._ast_cache:
            return self._ast_cache[code]

        try:
            tree = ast.parse(code)
            if self.cache_enabled:
                self._ast_cache[code] = tree
            return tree
        except SyntaxError as e:
            self.logger.error(f"Parse error at line {e.lineno}: {e.msg}")
            return None

    def _detect_language(
        self,
        code: str,
        filepath: Optional[str],
        language: AnalysisLanguage,
    ) -> str:
        """
        Detect the programming language of the code.

        [20251221_FEATURE] Uses code_parsers language detection when available.
        """
        if language != AnalysisLanguage.AUTO:
            return language.value

        # Use code_parsers detection if available
        if self.use_code_parsers and CODE_PARSERS_AVAILABLE and _detect_language_func:
            try:
                detected = _detect_language_func(filepath, code)
                return detected.value
            except Exception:
                pass

        # Fallback: simple extension-based detection
        if filepath:
            ext = Path(filepath).suffix.lower()
            ext_map = {
                ".py": "python",
                ".pyi": "python",
                ".js": "javascript",
                ".mjs": "javascript",
                ".jsx": "javascript",
                ".ts": "typescript",
                ".tsx": "typescript",
                ".java": "java",
            }
            if ext in ext_map:
                return ext_map[ext]

        # Content-based heuristics (basic)
        # Check for Python patterns
        if any(
            pattern in code
            for pattern in [
                "def ",
                "import ",
                "class ",
                "from ",
                "print(",
                "if __name__",
            ]
        ):
            return "python"
        # Check for JavaScript/TypeScript patterns
        if any(
            pattern in code
            for pattern in [
                "function ",
                "const ",
                "let ",
                "var ",
                "=>",
                "module.exports",
            ]
        ):
            return "javascript"
        # Check for Java patterns
        if any(
            pattern in code
            for pattern in [
                "public class ",
                "import java.",
                "private ",
                "public static void main",
            ]
        ):
            return "java"

        # Default to Python for simple expressions like "x = 1"
        return "python"

    def _parse_code(
        self,
        code: str,
        language: str,
        filepath: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Parse code using the appropriate parser for the language.

        [20251221_FEATURE] Uses code_parsers.ParserFactory for multi-language support.

        Returns:
            Dict with keys: ast, parser_result, functions, classes, errors
        """
        result: dict[str, Any] = {
            "ast": None,
            "parser_result": None,
            "functions": [],
            "classes": [],
            "errors": [],
            "parser_backend": "ast",
        }

        # For Python, always try standard ast first
        if language == "python":
            result["ast"] = self._parse_to_ast(code)
            result["parser_backend"] = "ast"

            # Extract functions and classes from Python AST
            if result["ast"]:
                for node in ast.walk(result["ast"]):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        result["functions"].append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        result["classes"].append(node.name)
            return result

        # For other languages, use code_parsers
        if (
            self.use_code_parsers
            and CODE_PARSERS_AVAILABLE
            and ParserFactory
            and ParserLanguage
        ):
            try:
                # Map language string to ParserLanguage enum
                lang_map: dict[str, Any] = {
                    "javascript": getattr(ParserLanguage, "JAVASCRIPT", None),
                    "typescript": getattr(ParserLanguage, "TYPESCRIPT", None),
                    "java": getattr(ParserLanguage, "JAVA", None),
                }

                parser_lang = lang_map.get(language)
                if parser_lang and ParserFactory.is_registered(parser_lang):
                    parser = ParserFactory.get_parser(parser_lang, self.parser_backend)
                    parse_result = parser.parse(code)

                    result["parser_result"] = parse_result
                    result["ast"] = parse_result.ast
                    result["functions"] = parser.get_functions(parse_result.ast)
                    result["classes"] = parser.get_classes(parse_result.ast)
                    result["parser_backend"] = language

                    # Collect errors from parse result
                    if parse_result.errors:
                        for err in parse_result.errors:
                            if isinstance(err, dict):
                                result["errors"].append(err.get("message", str(err)))
                            else:
                                result["errors"].append(str(err))

                    return result
            except Exception as e:
                result["errors"].append(f"Parser error: {str(e)}")
                self.logger.warning(f"code_parsers failed for {language}: {e}")

        # Fallback: return empty result with error
        if not result["ast"] and not result["parser_result"]:
            result["errors"].append(f"No parser available for language: {language}")

        return result

    def analyze_file(
        self,
        filepath: Union[str, Path],
        level: Optional[AnalysisLevel] = None,
    ) -> AnalysisResult:
        """
        Analyze a source file with automatic language detection.

        [20251221_FEATURE] Convenience method for file-based analysis.

        Args:
            filepath: Path to the source file
            level: Analysis level override

        Returns:
            AnalysisResult for the file
        """
        filepath = Path(filepath)

        if not filepath.exists():
            result = AnalysisResult(code="")
            result.errors.append(f"File not found: {filepath}")
            return result

        code = filepath.read_text(encoding="utf-8")
        return self.analyze(
            code,
            level=level,
            language=AnalysisLanguage.AUTO,
            filepath=str(filepath),
        )

    def _build_pdg(self, code: str) -> tuple[nx.DiGraph, nx.DiGraph]:
        """Build Program Dependence Graph and Call Graph."""
        if self.cache_enabled and code in self._pdg_cache:
            return self._pdg_cache[code]

        tree = self._parse_to_ast(code)
        if tree is None:
            return nx.DiGraph(), nx.DiGraph()

        builder = self._PDGBuilder()
        builder.visit(tree)

        result = (builder.graph, builder.call_graph)
        if self.cache_enabled:
            self._pdg_cache[code] = result

        return result

    def _compute_metrics(
        self,
        tree: Optional[ast.AST],
        code: str,
        language: str = "python",
        parse_result: Optional[dict[str, Any]] = None,
    ) -> AnalysisMetrics:
        """
        Compute code metrics from AST.

        [20251221_FEATURE] Extended to support multi-language metrics from code_parsers.
        """
        metrics = AnalysisMetrics()
        metrics.language = language
        metrics.parser_backend = (
            parse_result.get("parser_backend", "ast") if parse_result else "ast"
        )

        # Count lines of code (non-empty, non-comment)
        comment_chars = {
            "python": "#",
            "javascript": "//",
            "typescript": "//",
            "java": "//",
        }
        comment_char = comment_chars.get(language, "#")
        lines = [
            line
            for line in code.split("\n")
            if line.strip() and not line.strip().startswith(comment_char)
        ]
        metrics.lines_of_code = len(lines)

        # Extract metrics from parse_result if available
        if parse_result:
            metrics.num_functions = len(parse_result.get("functions", []))
            metrics.num_classes = len(parse_result.get("classes", []))

            # Get extended metrics from parser_result
            parser_result = parse_result.get("parser_result")
            if parser_result and hasattr(parser_result, "metrics"):
                pr_metrics = parser_result.metrics
                if isinstance(pr_metrics, dict):
                    metrics.halstead_volume = pr_metrics.get("halstead_volume", 0.0)
                    metrics.halstead_difficulty = pr_metrics.get(
                        "halstead_difficulty", 0.0
                    )
                    metrics.cognitive_complexity = pr_metrics.get(
                        "cognitive_complexity", 0
                    )

        # For Python AST, compute metrics directly
        if tree and language == "python":
            # Walk AST to count elements
            func_count = 0
            class_count = 0
            var_count = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_count += 1
                elif isinstance(node, ast.ClassDef):
                    class_count += 1
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    var_count += 1

            # Only override if not already set from parse_result
            if metrics.num_functions == 0:
                metrics.num_functions = func_count
            if metrics.num_classes == 0:
                metrics.num_classes = class_count
            metrics.num_variables = var_count

            # Calculate cyclomatic complexity
            metrics.cyclomatic_complexity = self._calculate_complexity(tree)

            # Calculate maintainability index (simplified)
            # MI = 171 - 5.2*ln(V) - 0.23*CC - 16.2*ln(LOC)
            # Simplified: higher is better, 0-100 scale
            if metrics.lines_of_code > 0:
                import math

                loc = max(metrics.lines_of_code, 1)
                cc = max(metrics.cyclomatic_complexity, 1)
                # Simplified maintainability calculation
                mi = max(
                    0,
                    171
                    - 5.2 * math.log(loc * 10 + 1)
                    - 0.23 * cc
                    - 16.2 * math.log(loc + 1),
                )
                metrics.maintainability_index = min(100, mi)

        return metrics

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of code."""
        complexity = 1

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ExceptHandler, ast.Assert, ast.With)):
                complexity += 1

        return complexity

    def _run_symbolic_execution(self, code: str) -> list[dict[str, Any]]:
        """Run symbolic execution on code."""
        paths = []

        try:
            tree = self._parse_to_ast(code)
            if tree is None:
                return paths

            # Simple path collection - track if/else branches
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    path_info = {
                        "type": "conditional",
                        "line": node.lineno,
                        "condition": ast.unparse(node.test),
                        "has_else": len(node.orelse) > 0,
                    }
                    paths.append(path_info)
                elif isinstance(node, ast.While):
                    path_info = {
                        "type": "loop",
                        "line": node.lineno,
                        "condition": ast.unparse(node.test),
                    }
                    paths.append(path_info)

        except Exception as e:
            self.logger.warning(f"Symbolic execution limited: {str(e)}")

        return paths

    def _detect_dead_code(
        self, tree: ast.AST, pdg: Optional[nx.DiGraph], call_graph: Optional[nx.DiGraph]
    ) -> list[DeadCodeItem]:
        """
        Detect dead code in the AST.

        This identifies:
        - Unused functions
        - Unused variables
        - Unreachable code after return/raise
        - Unused imports
        """
        dead_code = []

        # Collect all definitions and uses
        definitions = self._collect_definitions(tree)
        uses = self._collect_uses(tree)

        # Check for unused functions
        for func_name, func_info in definitions.get("functions", {}).items():
            if func_name not in uses.get("function_calls", set()):
                # Skip if it's a special method or main entry point
                if not func_name.startswith("_") and func_name != "main":
                    dead_code.append(
                        DeadCodeItem(
                            name=func_name,
                            code_type="function",
                            line_start=func_info["line_start"],
                            line_end=func_info["line_end"],
                            reason="Function is defined but never called",
                            confidence=0.9,
                        )
                    )

        # Check for unused variables
        defined_vars = definitions.get("variables", {})
        used_vars = uses.get("variables", set())

        for var_name, var_info in defined_vars.items():
            if var_name not in used_vars:
                # Skip loop variables and private variables
                if not var_name.startswith("_"):
                    dead_code.append(
                        DeadCodeItem(
                            name=var_name,
                            code_type="variable",
                            line_start=var_info["line"],
                            line_end=var_info["line"],
                            reason="Variable is assigned but never used",
                            confidence=0.85,
                        )
                    )

        # Check for unreachable code after return/raise
        dead_code.extend(self._find_unreachable_code(tree))

        # Check for unused imports
        dead_code.extend(self._find_unused_imports(tree, uses))

        # Use PDG for additional analysis if available
        if pdg is not None:
            dead_code.extend(self._detect_dead_code_from_pdg(pdg))

        return dead_code

    def _collect_definitions(self, tree: ast.AST) -> dict[str, Any]:
        """Collect all definitions in the code."""
        definitions = {"functions": {}, "classes": {}, "variables": {}, "imports": {}}

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                definitions["functions"][node.name] = {
                    "line_start": node.lineno,
                    "line_end": node.end_lineno or node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                }
            elif isinstance(node, ast.ClassDef):
                definitions["classes"][node.name] = {
                    "line_start": node.lineno,
                    "line_end": node.end_lineno or node.lineno,
                }
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        definitions["variables"][target.id] = {"line": node.lineno}
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    definitions["imports"][name] = {
                        "line": node.lineno,
                        "module": alias.name,
                    }
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    definitions["imports"][name] = {
                        "line": node.lineno,
                        "module": (
                            f"{node.module}.{alias.name}" if node.module else alias.name
                        ),
                    }

        return definitions

    def _collect_uses(self, tree: ast.AST) -> dict[str, set[str]]:
        """Collect all uses of names in the code."""
        uses = {"function_calls": set(), "variables": set(), "imports": set()}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    uses["function_calls"].add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    uses["function_calls"].add(node.func.attr)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                uses["variables"].add(node.id)
                uses["imports"].add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    uses["imports"].add(node.value.id)

        return uses

    def _find_unreachable_code(self, tree: ast.AST) -> list[DeadCodeItem]:
        """Find code that appears after return/raise statements."""
        dead_code = []

        class UnreachableVisitor(ast.NodeVisitor):
            def __init__(self):
                self.dead_items = []

            def visit_FunctionDef(self, node):
                self._check_body(node.body)
                self.generic_visit(node)

            def visit_AsyncFunctionDef(self, node):
                self._check_body(node.body)
                self.generic_visit(node)

            def _check_body(self, body):
                found_terminal = False
                terminal_line = 0

                for stmt in body:
                    if found_terminal:
                        self.dead_items.append(
                            DeadCodeItem(
                                name=f"statement at line {stmt.lineno}",
                                code_type="statement",
                                line_start=stmt.lineno,
                                line_end=getattr(stmt, "end_lineno", stmt.lineno),
                                reason=f"Unreachable code after line {terminal_line}",
                                confidence=0.95,
                            )
                        )

                    if isinstance(stmt, (ast.Return, ast.Raise)):
                        found_terminal = True
                        terminal_line = stmt.lineno

        visitor = UnreachableVisitor()
        visitor.visit(tree)
        dead_code.extend(visitor.dead_items)

        return dead_code

    def _find_unused_imports(
        self, tree: ast.AST, uses: dict[str, set[str]]
    ) -> list[DeadCodeItem]:
        """Find imports that are never used."""
        dead_code = []
        used_names = uses.get("imports", set())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    if name not in used_names:
                        dead_code.append(
                            DeadCodeItem(
                                name=alias.name,
                                code_type="import",
                                line_start=node.lineno,
                                line_end=node.lineno,
                                reason="Import is never used",
                                confidence=0.9,
                            )
                        )
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    if name not in used_names and alias.name != "*":
                        dead_code.append(
                            DeadCodeItem(
                                name=(
                                    f"{node.module}.{alias.name}"
                                    if node.module
                                    else alias.name
                                ),
                                code_type="import",
                                line_start=node.lineno,
                                line_end=node.lineno,
                                reason="Import is never used",
                                confidence=0.9,
                            )
                        )

        return dead_code

    def _detect_dead_code_from_pdg(self, pdg: nx.DiGraph) -> list[DeadCodeItem]:
        """Use PDG to detect additional dead code patterns."""
        dead_code = []

        # Find nodes with no outgoing data dependencies (potential dead code)
        for node in pdg.nodes():
            node_data = pdg.nodes[node]
            out_edges = list(pdg.out_edges(node, data=True))

            # Check if this is a computation with no uses
            if node_data.get("type") == "assign":
                has_data_dep = any(
                    edge[2].get("type") == "data_dependency" for edge in out_edges
                )
                if not has_data_dep and "lineno" in node_data:
                    dead_code.append(
                        DeadCodeItem(
                            name=node_data.get("target", node),
                            code_type="variable",
                            line_start=node_data["lineno"],
                            line_end=node_data["lineno"],
                            reason="Assignment has no downstream dependencies (PDG analysis)",
                            confidence=0.8,
                        )
                    )

        return dead_code

    def _analyze_security(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Analyze code for security issues."""
        issues = []

        dangerous_functions = {
            "eval": "Code injection via eval()",
            "exec": "Code injection via exec()",
            "compile": "Potential code injection via compile()",
            "__import__": "Dynamic import could be dangerous",
        }

        dangerous_patterns = {
            "os.system": "Command injection risk",
            "subprocess.call": "Command injection risk",
            "subprocess.Popen": "Command injection risk (use list args)",
            "pickle.loads": "Deserialization vulnerability",
            "yaml.load": "YAML deserialization vulnerability",
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check direct function calls
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in dangerous_functions:
                        issues.append(
                            {
                                "type": "dangerous_function",
                                "function": func_name,
                                "line": node.lineno,
                                "severity": "high",
                                "description": dangerous_functions[func_name],
                            }
                        )

                # Check method calls
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        full_name = f"{node.func.value.id}.{node.func.attr}"
                        if full_name in dangerous_patterns:
                            issues.append(
                                {
                                    "type": "dangerous_pattern",
                                    "pattern": full_name,
                                    "line": node.lineno,
                                    "severity": "high",
                                    "description": dangerous_patterns[full_name],
                                }
                            )

        return issues

    def _generate_refactor_suggestions(
        self, tree: ast.AST, pdg: Optional[nx.DiGraph], dead_code: list[DeadCodeItem]
    ) -> list[RefactorSuggestion]:
        """Generate refactoring suggestions based on analysis."""
        suggestions = []

        # Suggest removing dead code
        for item in dead_code:
            if item.confidence >= 0.85:
                suggestions.append(
                    RefactorSuggestion(
                        refactor_type="remove_dead_code",
                        description=f"Remove unused {item.code_type}: {item.name}",
                        target_node=f"line_{item.line_start}",
                        priority=4,
                        estimated_impact="Code cleanup, reduced complexity",
                    )
                )

        # Analyze for long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_length = (node.end_lineno or node.lineno) - node.lineno
                if func_length > 50:
                    suggestions.append(
                        RefactorSuggestion(
                            refactor_type="extract_method",
                            description=f"Function '{node.name}' is {func_length} lines. Consider splitting.",
                            target_node=node.name,
                            priority=3,
                            estimated_impact="Improved readability and maintainability",
                        )
                    )

                # Check for deep nesting
                max_depth = self._max_nesting_depth(node)
                if max_depth > 4:
                    suggestions.append(
                        RefactorSuggestion(
                            refactor_type="reduce_nesting",
                            description=f"Function '{node.name}' has nesting depth {max_depth}. Consider flattening.",
                            target_node=node.name,
                            priority=3,
                            estimated_impact="Improved readability",
                        )
                    )

        return suggestions

    def _max_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth in a node."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._max_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def apply_refactor(
        self, code: str, refactor_type: str, target: Optional[str] = None, **options
    ) -> str:
        """
        Apply a PDG-guided refactoring to the code.

        Args:
            code: Source code to refactor
            refactor_type: Type of refactoring to apply
                - 'remove_dead_code': Remove detected dead code
                - 'remove_unused_imports': Remove unused imports
                - 'rename_variable': Rename a variable (requires target and new_name)
                - 'extract_function': Extract code into new function
            target: Target element for the refactoring
            **options: Additional refactoring options

        Returns:
            Refactored source code
        """
        tree = self._parse_to_ast(code)
        if tree is None:
            return code

        if refactor_type == "remove_dead_code":
            return self._remove_dead_code(code, tree)
        elif refactor_type == "remove_unused_imports":
            return self._remove_unused_imports(code, tree)
        elif refactor_type == "rename_variable":
            new_name = options.get("new_name")
            if target and new_name:
                return self._rename_variable(code, tree, target, new_name)
        elif refactor_type == "inline_constant" and target:
            return self._inline_constant(code, tree, target)

        # No changes made
        return code

    def _remove_dead_code(self, code: str, tree: ast.AST) -> str:
        """Remove dead code from the source."""
        result = self.analyze(code)

        if not result.dead_code:
            return code

        # Sort by line number descending to remove from bottom up
        dead_items = sorted(result.dead_code, key=lambda x: x.line_start, reverse=True)

        lines = code.split("\n")

        for item in dead_items:
            if item.confidence >= 0.85:
                # Remove the lines for this dead code item
                start_idx = item.line_start - 1
                end_idx = item.line_end

                # Don't remove if it would break indentation structure
                if start_idx >= 0 and end_idx <= len(lines):
                    del lines[start_idx:end_idx]

        return "\n".join(lines)

    def _remove_unused_imports(self, code: str, tree: ast.AST) -> str:
        """Remove unused import statements."""
        uses = self._collect_uses(tree)
        used_names = uses.get("imports", set())

        class ImportRemover(ast.NodeTransformer):
            def visit_Import(self, node):
                remaining = []
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    if name in used_names:
                        remaining.append(alias)

                if not remaining:
                    return None
                elif len(remaining) < len(node.names):
                    node.names = remaining
                return node

            def visit_ImportFrom(self, node):
                if node.names[0].name == "*":
                    return node

                remaining = []
                for alias in node.names:
                    name = alias.asname or alias.name
                    if name in used_names:
                        remaining.append(alias)

                if not remaining:
                    return None
                elif len(remaining) < len(node.names):
                    node.names = remaining
                return node

        transformer = ImportRemover()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)

        try:
            return astor.to_source(new_tree)
        except (AttributeError, ValueError, TypeError) as e:
            self.logger.debug(f"Failed to convert AST to source: {e}")
            return code

    def _rename_variable(
        self, code: str, tree: ast.AST, old_name: str, new_name: str
    ) -> str:
        """Rename a variable throughout the code."""

        class VariableRenamer(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id == old_name:
                    node.id = new_name
                return node

            def visit_arg(self, node):
                if node.arg == old_name:
                    node.arg = new_name
                return node

        transformer = VariableRenamer()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)

        try:
            return astor.to_source(new_tree)
        except (AttributeError, ValueError, TypeError) as e:
            self.logger.debug(f"Failed to convert AST to source: {e}")
            return code

    def _inline_constant(self, code: str, tree: ast.AST, target: str) -> str:
        """Inline a constant variable."""
        # Find the constant value
        constant_value = None

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == target:
                        if isinstance(node.value, ast.Constant):
                            constant_value = node.value.value
                            break

        if constant_value is None:
            return code

        class ConstantInliner(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id == target and isinstance(node.ctx, ast.Load):
                    return ast.Constant(value=constant_value)
                return node

        transformer = ConstantInliner()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)

        try:
            return astor.to_source(new_tree)
        except (AttributeError, ValueError, TypeError) as e:
            self.logger.debug(f"Failed to convert AST to source: {e}")
            return code

    def clear_cache(self):
        """Clear all analysis caches."""
        self._ast_cache.clear()
        self._pdg_cache.clear()
        self._analysis_cache.clear()

    def get_dead_code_summary(self, result: AnalysisResult) -> str:
        """Generate a human-readable summary of dead code."""
        if not result.dead_code:
            return "No dead code detected."

        lines = [f"Found {len(result.dead_code)} dead code items:"]

        # Group by type
        by_type: dict[str, list[DeadCodeItem]] = {}
        for item in result.dead_code:
            if item.code_type not in by_type:
                by_type[item.code_type] = []
            by_type[item.code_type].append(item)

        for code_type, items in by_type.items():
            lines.append(f"\n{code_type.title()}s ({len(items)}):")
            for item in items:
                confidence_pct = int(item.confidence * 100)
                lines.append(
                    f"  - {item.name} (line {item.line_start}, {confidence_pct}% confidence)"
                )
                lines.append(f"    Reason: {item.reason}")

        return "\n".join(lines)

    class _PDGBuilder(ast.NodeVisitor):
        """Internal PDG builder for the analyzer."""

        def __init__(self):
            self.graph = nx.DiGraph()
            self.call_graph = nx.DiGraph()
            self.var_defs: dict[str, str] = {}
            self.control_deps: list[str] = []
            self.current_function: Optional[str] = None
            self.node_counter = 0

        def _get_node_id(self, prefix: str) -> str:
            """Generate unique node ID."""
            self.node_counter += 1
            return f"{prefix}_{self.node_counter}"

        def visit_FunctionDef(self, node: ast.FunctionDef):
            node_id = self._get_node_id("func")
            self.graph.add_node(
                node_id,
                type="function",
                name=node.name,
                lineno=node.lineno,
                args=[arg.arg for arg in node.args.args],
            )

            self.call_graph.add_node(node.name)

            prev_function = self.current_function
            self.current_function = node.name

            # Add parameters
            for arg in node.args.args:
                arg_id = self._get_node_id("param")
                self.graph.add_node(
                    arg_id,
                    type="parameter",
                    name=arg.arg,
                    lineno=arg.lineno if hasattr(arg, "lineno") else node.lineno,
                )
                self.graph.add_edge(node_id, arg_id, type="parameter_dependency")
                self.var_defs[arg.arg] = arg_id

            # Process body
            for stmt in node.body:
                self.visit(stmt)

            self.current_function = prev_function

        def visit_Assign(self, node: ast.Assign):
            node_id = self._get_node_id("assign")

            target_names = []
            for target in node.targets:
                if isinstance(target, ast.Name):
                    target_names.append(target.id)

            self.graph.add_node(
                node_id,
                type="assign",
                target=", ".join(target_names),
                lineno=node.lineno,
            )

            # Add data dependencies
            for var in self._extract_variables(node.value):
                if var in self.var_defs:
                    self.graph.add_edge(
                        self.var_defs[var], node_id, type="data_dependency"
                    )

            # Add control dependencies
            for ctrl_node in self.control_deps:
                self.graph.add_edge(ctrl_node, node_id, type="control_dependency")

            # Update definitions
            for name in target_names:
                self.var_defs[name] = node_id

            self.generic_visit(node)

        def visit_If(self, node: ast.If):
            node_id = self._get_node_id("if")

            self.graph.add_node(node_id, type="if", lineno=node.lineno)

            # Add data dependencies for condition
            for var in self._extract_variables(node.test):
                if var in self.var_defs:
                    self.graph.add_edge(
                        self.var_defs[var], node_id, type="data_dependency"
                    )

            # Add control dependencies
            for ctrl_node in self.control_deps:
                self.graph.add_edge(ctrl_node, node_id, type="control_dependency")

            # Process branches with control dependency
            self.control_deps.append(node_id)

            for stmt in node.body:
                self.visit(stmt)

            for stmt in node.orelse:
                self.visit(stmt)

            self.control_deps.pop()

        def visit_For(self, node: ast.For):
            node_id = self._get_node_id("for")

            self.graph.add_node(node_id, type="for", lineno=node.lineno)

            # Handle loop variable
            if isinstance(node.target, ast.Name):
                self.var_defs[node.target.id] = node_id

            # Add data dependencies for iterator
            for var in self._extract_variables(node.iter):
                if var in self.var_defs:
                    self.graph.add_edge(
                        self.var_defs[var], node_id, type="data_dependency"
                    )

            # Process body
            self.control_deps.append(node_id)
            for stmt in node.body:
                self.visit(stmt)
            self.control_deps.pop()

        def visit_While(self, node: ast.While):
            node_id = self._get_node_id("while")

            self.graph.add_node(node_id, type="while", lineno=node.lineno)

            # Add data dependencies for condition
            for var in self._extract_variables(node.test):
                if var in self.var_defs:
                    self.graph.add_edge(
                        self.var_defs[var], node_id, type="data_dependency"
                    )

            # Process body
            self.control_deps.append(node_id)
            for stmt in node.body:
                self.visit(stmt)
            self.control_deps.pop()

        def visit_Call(self, node: ast.Call):
            node_id = self._get_node_id("call")

            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            self.graph.add_node(
                node_id, type="call", function=func_name, lineno=node.lineno
            )

            # Add to call graph
            if self.current_function and func_name:
                self.call_graph.add_edge(self.current_function, func_name)

            # Add data dependencies for arguments
            for arg in node.args:
                for var in self._extract_variables(arg):
                    if var in self.var_defs:
                        self.graph.add_edge(
                            self.var_defs[var], node_id, type="data_dependency"
                        )

            self.generic_visit(node)

        def visit_Return(self, node: ast.Return):
            node_id = self._get_node_id("return")

            self.graph.add_node(node_id, type="return", lineno=node.lineno)

            if node.value:
                for var in self._extract_variables(node.value):
                    if var in self.var_defs:
                        self.graph.add_edge(
                            self.var_defs[var], node_id, type="data_dependency"
                        )

            for ctrl_node in self.control_deps:
                self.graph.add_edge(ctrl_node, node_id, type="control_dependency")

        def _extract_variables(self, node: ast.AST) -> set[str]:
            """Extract variable names from an AST node."""
            variables = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                    variables.add(child.id)
            return variables


# Convenience function for quick analysis
def analyze_code(
    code: str,
    level: AnalysisLevel = AnalysisLevel.STANDARD,
    *,
    language: AnalysisLanguage | str = "python",
) -> AnalysisResult:
    """
    Convenience function to quickly analyze code.

    Args:
        code: Python source code
        level: Analysis level
        language: Language hint (accepted for MCP parity). Only "python"/"auto" are supported.

    Returns:
        AnalysisResult with all analysis data
    """
    # [20251228_BUGFIX] Accept `language=` for parity with MCP API and tests.
    # [20260101_BUGFIX] Proper type handling for language parameter (enum or str)
    from enum import Enum

    lang_value = language.value if isinstance(language, Enum) else str(language)
    if lang_value.lower() not in {"python", "auto"}:
        raise ValueError(
            "This convenience analyze_code() only supports Python. "
            "Use code_scalpel.mcp.server.analyze_code for polyglot analysis."
        )
    analyzer = CodeAnalyzer(level=level)
    return analyzer.analyze(code)
