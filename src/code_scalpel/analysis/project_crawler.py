"""
Project Crawler - Whole-project Python analysis tool.

# [20251224_REFACTOR] Moved from code_scalpel/project_crawler.py to
# code_scalpel/analysis/project_crawler.py as part of Issue #3
# in PROJECT_REORG_REFACTOR.md Phase 1.

Crawls an entire project directory, analyzes all Python files, and generates
comprehensive metrics including:
- Structure analysis (classes, functions, imports)
- Cyclomatic complexity estimation
- Lines of code counts
- Complexity hotspot detection

This module integrates with Code Scalpel's existing AST analysis tools
and can be used standalone or via the MCP server.

Usage:
    from code_scalpel.analysis import ProjectCrawler

    crawler = ProjectCrawler("/path/to/project")
    result = crawler.crawl()
    print(result.summary)

    # Generate markdown report
    report = crawler.generate_report()

TODO: Module Enhancement Roadmap
================================

COMMUNITY (Current & Planned):
- TODO [COMMUNITY]: Implement Halstead complexity metrics (volume, difficulty, effort) (current)
- TODO [COMMUNITY]: Implement maintainability index calculation
- TODO [COMMUNITY]: Add SLOC vs logical LOC distinction
- TODO [COMMUNITY]: Implement comment density analysis
- TODO [COMMUNITY]: Build import dependency graph for the entire project
- TODO [COMMUNITY]: Detect circular import dependencies
- TODO [COMMUNITY]: Identify unused imports across the codebase
- TODO [COMMUNITY]: Flag functions exceeding parameter count thresholds
- TODO [COMMUNITY]: Track technical debt indicators

PRO (Enhanced Features):
- TODO [PRO]: Add support for analyzing JavaScript/TypeScript files
- TODO [PRO]: Add support for analyzing Java files with similar metrics
- TODO [PRO]: Add cognitive complexity scoring (more accurate than cyclomatic)
- TODO [PRO]: Track code churn metrics when git history is available
- TODO [PRO]: Calculate test coverage correlation per module
- TODO [PRO]: Detect code duplication (clone detection)
- TODO [PRO]: Identify dead code (unreachable functions/classes)
- TODO [PRO]: Detect deeply nested code blocks
- TODO [PRO]: Identify god classes and long methods
- TODO [PRO]: Generate dependency visualization (DOT/Mermaid format)
- TODO [PRO]: Calculate coupling metrics between modules
- TODO [PRO]: Add incremental analysis (only changed files)
- TODO [PRO]: Implement caching of analysis results
- TODO [PRO]: Add HTML report generation with interactive charts
- TODO [PRO]: Add CI/CD integration helpers (GitHub Actions, GitLab CI)

ENTERPRISE (Advanced Capabilities):
- TODO [ENTERPRISE]: Add support for analyzing Go files
- TODO [ENTERPRISE]: Add support for analyzing Rust files
- TODO [ENTERPRISE]: Create language-agnostic base visitor for multi-language support
- TODO [ENTERPRISE]: Track external vs internal dependency ratio
- TODO [ENTERPRISE]: Implement parallel file analysis using multiprocessing
- TODO [ENTERPRISE]: Add memory-efficient streaming for large codebases
- TODO [ENTERPRISE]: Support analysis of monorepos with multiple roots
- TODO [ENTERPRISE]: Export metrics to Prometheus/Grafana format
- TODO [ENTERPRISE]: Generate SARIF output for IDE integration
- TODO [ENTERPRISE]: Create VS Code extension integration
- TODO [ENTERPRISE]: Add threshold-based exit codes for CI gates
- TODO [ENTERPRISE]: Train model to predict bug-prone files based on metrics
- TODO [ENTERPRISE]: Implement semantic code similarity detection
- TODO [ENTERPRISE]: Add natural language summaries of complex functions
- TODO [ENTERPRISE]: Generate refactoring suggestions based on patterns
"""

from __future__ import annotations

import ast
import datetime
import os
from fnmatch import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Default directories to exclude from crawling
DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "venv",
        ".venv",
        "env",
        ".env",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        "dist",
        "build",
        "egg-info",
        ".egg-info",
        ".tox",
        ".nox",
        "htmlcov",
        "site-packages",
    }
)

# Default complexity threshold for warnings
DEFAULT_COMPLEXITY_THRESHOLD: int = 10


@dataclass
class FunctionInfo:
    """
    Information about a function or method.

    TODO: Add the following fields for richer analysis:
    - TODO: end_lineno: int - Track function end line for size calculation
    - TODO: docstring: str | None - Extract and store docstring
    - TODO: has_docstring: bool - Quick check for documentation coverage
    - TODO: parameters: list[str] - Track parameter names and count
    - TODO: return_type: str | None - Extract return type annotation
    - TODO: decorators: list[str] - Track applied decorators
    - TODO: is_async: bool - Flag async functions separately
    - TODO: is_generator: bool - Flag generator functions
    - TODO: is_property: bool - Flag property methods
    - TODO: is_staticmethod: bool - Flag static methods
    - TODO: is_classmethod: bool - Flag class methods
    - TODO: cognitive_complexity: int - More accurate complexity metric
    - TODO: nested_depth: int - Maximum nesting level in function
    - TODO: local_variables: int - Count of local variable declarations
    - TODO: calls_made: list[str] - Functions/methods called within
    """

    name: str
    lineno: int
    complexity: int
    is_method: bool = False
    class_name: str | None = None

    # TODO: Add computed properties:
    # - is_complex: bool - Returns True if complexity > threshold
    # - size_lines: int - Number of lines (requires end_lineno)
    # - documentation_ratio: float - Docstring lines vs code lines

    @property
    def qualified_name(self) -> str:
        """Return the fully qualified name."""
        if self.class_name:
            return f"{self.class_name}.{self.name}"
        return self.name


@dataclass
class ClassInfo:
    """
    Information about a class.

    TODO: Add the following fields for richer class analysis:
    - TODO: end_lineno: int - Track class end line
    - TODO: docstring: str | None - Extract class docstring
    - TODO: decorators: list[str] - Track class decorators (@dataclass, etc.)
    - TODO: instance_attributes: list[str] - Attributes set in __init__
    - TODO: class_attributes: list[str] - Class-level attribute definitions
    - TODO: properties: list[str] - @property decorated methods
    - TODO: abstract_methods: list[str] - @abstractmethod decorated methods
    - TODO: is_dataclass: bool - Flag dataclass decorated classes
    - TODO: is_abstract: bool - Flag ABC subclasses
    - TODO: is_protocol: bool - Flag Protocol subclasses
    - TODO: metaclass: str | None - Track metaclass if specified
    - TODO: inner_classes: list[ClassInfo] - Nested class definitions
    - TODO: method_count_by_visibility: dict - public/private/protected counts
    """

    name: str
    lineno: int
    methods: list[FunctionInfo] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)

    # TODO: Add computed properties:
    # - total_complexity: int - Sum of all method complexities
    # - average_method_complexity: float - Mean complexity per method
    # - is_god_class: bool - Too many methods/attributes indicator
    # - inheritance_depth: int - Depth in inheritance hierarchy


@dataclass
class FileAnalysisResult:
    """
    Result of analyzing a single file.

    TODO: Add the following fields for comprehensive file analysis:
    - TODO: file_hash: str - SHA256 hash for change detection
    - TODO: last_modified: datetime - File modification timestamp
    - TODO: encoding: str - Detected file encoding
    - TODO: blank_lines: int - Count of blank lines
    - TODO: comment_lines: int - Count of comment-only lines
    - TODO: docstring_lines: int - Lines within docstrings
    - TODO: logical_lines: int - Actual code statements
    - TODO: global_variables: list[str] - Module-level variable definitions
    - TODO: constants: list[str] - UPPER_CASE module-level names
    - TODO: type_aliases: list[str] - Type alias definitions
    - TODO: __all__: list[str] | None - Exported names if defined
    - TODO: shebang: str | None - Shebang line if present
    - TODO: future_imports: list[str] - __future__ imports used
    - TODO: conditional_imports: list[str] - Imports inside if/try blocks
    - TODO: star_imports: list[str] - from x import * occurrences
    - TODO: relative_imports: list[str] - Relative import statements
    - TODO: syntax_version: str - Minimum Python version required
    """

    path: str
    status: str  # "success" or "error"
    lines_of_code: int = 0
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    complexity_warnings: list[FunctionInfo] = field(default_factory=list)
    error: str | None = None

    # TODO: Add computed properties:
    # - code_to_comment_ratio: float - Code lines / comment lines
    # - documentation_coverage: float - % of functions with docstrings
    # - average_function_length: float - Mean lines per function
    # - max_nesting_depth: int - Deepest nesting in file
    # - import_count_external: int - Third-party imports
    # - import_count_stdlib: int - Standard library imports
    # - import_count_local: int - Project-internal imports

    @property
    def total_functions(self) -> int:
        """Total number of functions including class methods."""
        return len(self.functions) + sum(len(c.methods) for c in self.classes)


@dataclass
class CrawlResult:
    """
    Result of crawling an entire project.

    TODO: Add the following fields for comprehensive project analysis:
    - TODO: duration_seconds: float - Time taken to complete crawl
    - TODO: python_version: str - Python version used for parsing
    - TODO: exclude_patterns: list[str] - Patterns that were excluded
    - TODO: file_count_by_extension: dict[str, int] - All files found by type
    - TODO: largest_files: list[tuple[str, int]] - Top N files by LOC
    - TODO: most_complex_files: list[tuple[str, int]] - Top N by complexity
    - TODO: dependency_graph: dict[str, list[str]] - Import relationships
    - TODO: circular_dependencies: list[list[str]] - Detected cycles
    - TODO: packages_found: list[str] - Directories with __init__.py
    - TODO: test_files: list[str] - Files matching test patterns
    - TODO: config_files: list[str] - setup.py, pyproject.toml, etc.
    """

    root_path: str
    timestamp: str
    files_analyzed: list[FileAnalysisResult] = field(default_factory=list)
    files_with_errors: list[FileAnalysisResult] = field(default_factory=list)

    # TODO: Add methods:
    # - get_files_by_complexity(min_score: int) -> list[FileAnalysisResult]
    # - get_files_by_size(min_loc: int) -> list[FileAnalysisResult]
    # - get_hotspots(top_n: int) -> list[tuple[str, FunctionInfo]]
    # - compare(other: CrawlResult) -> CrawlDiff - Compare two crawl results
    # - filter_by_path(pattern: str) -> CrawlResult - Filter results by path

    @property
    def total_files(self) -> int:
        """Total number of files scanned."""
        return len(self.files_analyzed) + len(self.files_with_errors)

    @property
    def total_lines_of_code(self) -> int:
        """Total lines of code across all files."""
        return sum(f.lines_of_code for f in self.files_analyzed)

    @property
    def total_functions(self) -> int:
        """Total number of functions across all files."""
        return sum(f.total_functions for f in self.files_analyzed)

    @property
    def total_classes(self) -> int:
        """Total number of classes across all files."""
        return sum(len(f.classes) for f in self.files_analyzed)

    @property
    def all_complexity_warnings(self) -> list[tuple[str, FunctionInfo]]:
        """All complexity warnings with file paths."""
        warnings = []
        for file_result in self.files_analyzed:
            for func in file_result.complexity_warnings:
                warnings.append((file_result.path, func))
        return warnings

    @property
    def summary(self) -> dict[str, Any]:
        """Summary statistics."""
        return {
            "root_path": self.root_path,
            "timestamp": self.timestamp,
            "total_files": self.total_files,
            "successful_files": len(self.files_analyzed),
            "failed_files": len(self.files_with_errors),
            "total_lines_of_code": self.total_lines_of_code,
            "total_functions": self.total_functions,
            "total_classes": self.total_classes,
            "complexity_warnings": len(self.all_complexity_warnings),
        }


class CodeAnalyzerVisitor(ast.NodeVisitor):
    """
    AST visitor that extracts code metrics.

    TODO: Visitor Enhancement Roadmap:
    - TODO: Track current nesting depth for nested function detection
    - TODO: Collect decorator information from function/class nodes
    - TODO: Extract docstrings using ast.get_docstring()
    - TODO: Detect type annotations on parameters and return values
    - TODO: Track global/nonlocal statements for scope analysis
    - TODO: Identify comprehension patterns (list, dict, set, generator)
    - TODO: Count exception handling patterns (try/except/finally)
    - TODO: Detect context managers (with statements)
    - TODO: Track assertion statements for test-like code detection
    - TODO: Identify magic methods (__init__, __str__, etc.)
    - TODO: Detect protocol/ABC usage patterns
    - TODO: Track lambda expressions and their complexity
    - TODO: Identify f-string usage vs .format() vs % formatting
    """

    def __init__(self, complexity_threshold: int = DEFAULT_COMPLEXITY_THRESHOLD):
        self.complexity_threshold = complexity_threshold
        self.functions: list[FunctionInfo] = []
        self.classes: list[ClassInfo] = []
        self.imports: list[str] = []
        self.complexity_warnings: list[FunctionInfo] = []
        self._current_class: ClassInfo | None = None
        # TODO: Add tracking for:
        # self._nesting_depth: int = 0
        # self._max_nesting_depth: int = 0
        # self.global_variables: list[str] = []
        # self.constants: list[str] = []
        # self.decorators_used: set[str] = set()
        # self.type_annotations_count: int = 0

    def visit_Import(self, node: ast.Import) -> None:
        """Handle import statements."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle from ... import statements."""
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Handle class definitions."""
        bases: list[str] = [
            base_name
            for base in node.bases
            if (base_name := self._get_base_name(base)) is not None
        ]
        class_info = ClassInfo(
            name=node.name,
            lineno=node.lineno,
            bases=bases,
        )
        self.classes.append(class_info)

        # Visit class body with context
        old_class = self._current_class
        self._current_class = class_info
        self.generic_visit(node)
        self._current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Handle function definitions."""
        self._process_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Handle async function definitions."""
        self._process_function(node)

    def _process_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Process a function or async function definition."""
        complexity = self._calculate_complexity(node)

        func_info = FunctionInfo(
            name=node.name,
            lineno=node.lineno,
            complexity=complexity,
            is_method=self._current_class is not None,
            class_name=self._current_class.name if self._current_class else None,
        )

        if self._current_class:
            self._current_class.methods.append(func_info)
        else:
            self.functions.append(func_info)

        if complexity > self.complexity_threshold:
            self.complexity_warnings.append(func_info)

        self.generic_visit(node)

    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity.

        Complexity = 1 + number of decision points (if, for, while, try, etc.)

        TODO: Complexity Calculation Improvements:
        - TODO: Implement cognitive complexity (Sonar-style) as alternative metric
        - TODO: Add weighted complexity based on nesting depth
        - TODO: Handle match/case statements (Python 3.10+)
        - TODO: Consider ternary expressions (a if b else c)
        - TODO: Weight recursive calls higher
        - TODO: Track complexity per branch for detailed analysis
        - TODO: Add support for async for/async with statements
        - TODO: Consider walrus operator (:=) in conditions
        - TODO: Implement essential complexity (after structured simplification)
        - TODO: Add McCabe strict mode vs relaxed mode option
        """
        score = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                score += 1
            elif isinstance(child, ast.Try):
                score += 1
            elif isinstance(child, ast.ExceptHandler):
                score += 1
            elif isinstance(child, ast.BoolOp):
                # and/or add decision points
                score += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                # List/dict/set comprehensions with if clauses
                score += len(child.ifs)
            # TODO: Add these cases:
            # elif isinstance(child, ast.Match):  # Python 3.10+
            #     score += len(child.cases)
            # elif isinstance(child, ast.IfExp):  # Ternary expressions
            #     score += 1
            # elif isinstance(child, ast.Assert):
            #     score += 1  # Optional: count assertions
        return score

    @staticmethod
    def _get_base_name(node: ast.expr) -> str | None:
        """Extract base class name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None


class ProjectCrawler:
    """
    Crawls a project directory and analyzes all Python files.

    Example:
        crawler = ProjectCrawler("/path/to/project")
        result = crawler.crawl()
        print(f"Analyzed {result.total_files} files")
        print(f"Total LOC: {result.total_lines_of_code}")

    TODO: ProjectCrawler Enhancement Roadmap:
    =========================================

    Configuration & Flexibility:
    - TODO: Add .crawlerignore file support (like .gitignore)
    - TODO: Support glob patterns for include/exclude (not just dir names)
    - TODO: Add file size limits to skip extremely large files
    - TODO: Support configuration via pyproject.toml [tool.code-scalpel.crawler]
    - TODO: Add preset configurations (strict, relaxed, ci-mode)

    Performance & Scalability:
    - TODO: Implement multiprocessing.Pool for parallel file analysis
    - TODO: Add async/await support with aiofiles for I/O bound operations
    - TODO: Implement incremental crawling with file hash caching
    - TODO: Add progress callback for UI integration
    - TODO: Support streaming results for memory efficiency
    - TODO: Add timeout per-file to handle pathological cases

    Analysis Features:
    - TODO: Integrate with git to get file history/blame info
    - TODO: Add support for analyzing Jupyter notebooks (.ipynb)
    - TODO: Detect and parse type stub files (.pyi)
    - TODO: Support analyzing Cython files (.pyx)
    - TODO: Add configurable complexity algorithms (cyclomatic, cognitive, etc.)

    Output & Integration:
    - TODO: Add JSON Schema for output validation
    - TODO: Generate SonarQube compatible metrics
    - TODO: Output CodeClimate compatible format
    - TODO: Add SQLite export for querying large results
    - TODO: Generate treemap visualization data
    - TODO: Add diff mode to compare two crawl results
    """

    def __init__(
        self,
        root_path: str | Path,
        exclude_dirs: frozenset[str] | None = None,
        complexity_threshold: int = DEFAULT_COMPLEXITY_THRESHOLD,
        max_files: int | None = None,
        max_depth: int | None = None,
        respect_gitignore: bool = False,
    ):
        """
        Initialize the project crawler.

        Args:
            root_path: Root directory to crawl
            exclude_dirs: Directory names to exclude (uses defaults if None)
            complexity_threshold: Complexity score that triggers a warning
        """
        self.root_path = Path(root_path).resolve()
        self.exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
        self.complexity_threshold = complexity_threshold
        self.max_files = max_files
        self.max_depth = max_depth
        self.respect_gitignore = respect_gitignore
        self._gitignore_patterns: list[str] = []

        if not self.root_path.exists():
            raise ValueError(f"Path does not exist: {self.root_path}")
        if not self.root_path.is_dir():
            raise ValueError(f"Path is not a directory: {self.root_path}")

        # [20251225_FEATURE] Minimal .gitignore support for tiered crawling.
        if self.respect_gitignore:
            gitignore_file = self.root_path / ".gitignore"
            if gitignore_file.exists() and gitignore_file.is_file():
                for raw in gitignore_file.read_text(
                    encoding="utf-8", errors="ignore"
                ).splitlines():
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("!"):
                        # Negation patterns are intentionally ignored in this minimal implementation.
                        continue
                    self._gitignore_patterns.append(line)

    def _is_gitignored(self, rel_path: Path, *, is_dir: bool) -> bool:
        if not self._gitignore_patterns:
            return False
        rel_posix = rel_path.as_posix().lstrip("./")
        for pattern in self._gitignore_patterns:
            pat = pattern
            if pat.endswith("/"):
                if not is_dir:
                    continue
                pat = pat[:-1]
            if "/" in pat:
                if fnmatch(rel_posix, pat):
                    return True
            else:
                if fnmatch(rel_path.name, pat):
                    return True
        return False

    def crawl(self) -> CrawlResult:
        """
        Crawl the project and analyze all Python files.

        Returns:
            CrawlResult with analysis data for all files
        """
        result = CrawlResult(
            root_path=str(self.root_path),
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        analyzed_python_files = 0
        reached_limit = False
        for root, dirs, files in os.walk(self.root_path):
            rel_dir = Path(root).resolve().relative_to(self.root_path)
            depth = len(rel_dir.parts)
            if self.max_depth is not None and depth >= self.max_depth:
                dirs[:] = []
            else:
                filtered_dirs: list[str] = []
                for d in dirs:
                    if d in self.exclude_dirs:
                        continue
                    rel_child = rel_dir / d
                    if self._is_gitignored(rel_child, is_dir=True):
                        continue
                    filtered_dirs.append(d)
                dirs[:] = filtered_dirs

            for filename in files:
                rel_file = rel_dir / filename
                if self._is_gitignored(rel_file, is_dir=False):
                    continue

                if filename.endswith(".py"):
                    if self.max_files is not None and analyzed_python_files >= self.max_files:
                        reached_limit = True
                        dirs[:] = []
                        break
                    analyzed_python_files += 1
                    file_path = os.path.join(root, filename)
                    file_result = self._analyze_file(file_path)

                    if file_result.status == "success":
                        result.files_analyzed.append(file_result)
                    else:
                        result.files_with_errors.append(file_result)

            if reached_limit:
                break

        return result

    def _analyze_file(self, file_path: str) -> FileAnalysisResult:
        """
        Analyze a single Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            FileAnalysisResult with metrics
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            tree = ast.parse(code, filename=file_path)
            visitor = CodeAnalyzerVisitor(self.complexity_threshold)
            visitor.visit(tree)

            return FileAnalysisResult(
                path=file_path,
                status="success",
                lines_of_code=len(code.splitlines()),
                functions=visitor.functions,
                classes=visitor.classes,
                imports=visitor.imports,
                complexity_warnings=visitor.complexity_warnings,
            )

        except SyntaxError as e:
            return FileAnalysisResult(
                path=file_path,
                status="error",
                error=f"Syntax error at line {e.lineno}: {e.msg}",
            )
        except Exception as e:
            return FileAnalysisResult(
                path=file_path,
                status="error",
                error=str(e),
            )

    def generate_report(
        self, result: CrawlResult | None = None, output_path: str | None = None
    ) -> str:
        """
        Generate a Markdown report of the crawl results.

        Args:
            result: CrawlResult to report on (crawls if None)
            output_path: Optional path to write the report

        Returns:
            Markdown report string

        TODO: Report Generation Enhancements:
        - TODO: Add HTML report with interactive charts (Chart.js/D3.js)
        - TODO: Generate PDF report using weasyprint or reportlab
        - TODO: Add treemap visualization of code structure
        - TODO: Include mini sparkline graphs for trends (if historical data)
        - TODO: Add collapsible sections for large reports
        - TODO: Generate per-package/module breakdown sections
        - TODO: Add code snippets for complexity hotspots
        - TODO: Include actionable recommendations section
        - TODO: Add comparison table if baseline provided
        - TODO: Generate badges (shields.io compatible) for README
        - TODO: Support custom Jinja2 templates for report formatting
        - TODO: Add executive summary with key findings
        - TODO: Include trend indicators (↑↓→) when comparing
        """
        if result is None:
            result = self.crawl()

        md_lines = [
            "# Project Python Analysis Report",
            "",
            f"**Target:** `{result.root_path}`",
            f"**Date:** {result.timestamp}",
            "",
            "## Executive Summary",
            "",
            f"- **Total Files Scanned:** {result.total_files}",
            f"- **Successful Analyses:** {len(result.files_analyzed)}",
            f"- **Failed Analyses:** {len(result.files_with_errors)}",
            f"- **Total Lines of Code:** {result.total_lines_of_code:,}",
            f"- **Total Functions:** {result.total_functions}",
            f"- **Total Classes:** {result.total_classes}",
            f"- **Complexity Hotspots:** {len(result.all_complexity_warnings)}",
            "",
            "---",
            "",
        ]

        # Complexity warnings section
        md_lines.append(f"## Complexity Warnings (Score > {self.complexity_threshold})")
        md_lines.append("")

        warnings = result.all_complexity_warnings
        if not warnings:
            md_lines.append("No overly complex functions detected.")
        else:
            md_lines.append("| File | Function | Complexity | Line |")
            md_lines.append("|------|----------|------------|------|")
            for file_path, func in sorted(
                warnings, key=lambda x: x[1].complexity, reverse=True
            ):
                rel_path = os.path.relpath(file_path, result.root_path)
                md_lines.append(
                    f"| `{rel_path}` | `{func.qualified_name}` | **{func.complexity}** | {func.lineno} |"
                )
        md_lines.append("")

        # File statistics section
        md_lines.append("## File Statistics")
        md_lines.append("")
        md_lines.append("| File | LOC | Classes | Functions | Imports |")
        md_lines.append("|------|-----|---------|-----------|---------|")

        for file_result in sorted(
            result.files_analyzed, key=lambda x: x.lines_of_code, reverse=True
        ):
            rel_path = os.path.relpath(file_result.path, result.root_path)
            md_lines.append(
                f"| `{rel_path}` | {file_result.lines_of_code} | "
                f"{len(file_result.classes)} | {file_result.total_functions} | "
                f"{len(file_result.imports)} |"
            )
        md_lines.append("")

        # Error section
        if result.files_with_errors:
            md_lines.append("## Analysis Errors")
            md_lines.append("")
            md_lines.append("| File | Error |")
            md_lines.append("|------|-------|")
            for file_result in result.files_with_errors:
                rel_path = os.path.relpath(file_result.path, result.root_path)
                error_msg = file_result.error or "Unknown error"
                md_lines.append(f"| `{rel_path}` | {error_msg} |")
            md_lines.append("")

        report = "\n".join(md_lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)

        return report

    def to_dict(self, result: CrawlResult | None = None) -> dict[str, Any]:
        """
        Convert crawl results to a dictionary for JSON serialization.

        Args:
            result: CrawlResult to convert (crawls if None)

        Returns:
            Dictionary representation of the results
        """
        if result is None:
            result = self.crawl()

        def file_result_to_dict(fr: FileAnalysisResult) -> dict[str, Any]:
            return {
                "path": os.path.relpath(fr.path, result.root_path),
                "status": fr.status,
                "lines_of_code": fr.lines_of_code,
                "functions": [
                    {
                        "name": f.qualified_name,
                        "lineno": f.lineno,
                        "complexity": f.complexity,
                    }
                    for f in fr.functions
                ],
                "classes": [
                    {
                        "name": c.name,
                        "lineno": c.lineno,
                        "methods": [
                            {
                                "name": m.name,
                                "lineno": m.lineno,
                                "complexity": m.complexity,
                            }
                            for m in c.methods
                        ],
                        "bases": c.bases,
                    }
                    for c in fr.classes
                ],
                "imports": fr.imports,
                "complexity_warnings": [
                    {
                        "name": f.qualified_name,
                        "lineno": f.lineno,
                        "complexity": f.complexity,
                    }
                    for f in fr.complexity_warnings
                ],
                "error": fr.error,
            }

        return {
            "root_path": result.root_path,
            "timestamp": result.timestamp,
            "summary": result.summary,
            "files": [file_result_to_dict(f) for f in result.files_analyzed],
            "errors": [file_result_to_dict(f) for f in result.files_with_errors],
        }


def crawl_project(
    root_path: str,
    exclude_dirs: list[str] | None = None,
    complexity_threshold: int = DEFAULT_COMPLEXITY_THRESHOLD,
) -> dict[str, Any]:
    """
    Convenience function to crawl a project and return results as a dictionary.

    Args:
        root_path: Path to the project root
        exclude_dirs: Optional list of directory names to exclude
        complexity_threshold: Complexity score that triggers a warning

    Returns:
        Dictionary with crawl results
    """
    exclude_set = frozenset(exclude_dirs) if exclude_dirs else None
    crawler = ProjectCrawler(
        root_path,
        exclude_dirs=exclude_set,
        complexity_threshold=complexity_threshold,
    )
    result = crawler.crawl()
    return crawler.to_dict(result)
