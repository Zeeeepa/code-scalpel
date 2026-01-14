from __future__ import annotations

import ast
import os
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

# [20251213_FEATURE] v1.5.0 - Enhanced call graph with line numbers and Mermaid support


@dataclass
class CallContext:
    """Context information about where a call is made.

    Server-side serialization expects this to exist for v3.3.0 pre-release
    get_call_graph outputs; builders may leave it as defaults.
    """

    in_loop: bool = False
    in_try_block: bool = False
    in_conditional: bool = False
    condition_summary: Optional[str] = None
    in_async: bool = False
    in_except_handler: bool = False


@dataclass
class CallNode:
    """A node in the call graph with location information."""

    name: str
    file: str
    line: int
    end_line: Optional[int] = None
    is_entry_point: bool = False
    # [20260111_BUGFIX] v3.3.0 - MCP server expects source_uri for serialization
    source_uri: Optional[str] = None


@dataclass
class CallEdge:
    """An edge in the call graph representing a call relationship."""

    caller: str
    callee: str
    confidence: float = 1.0
    inference_source: str = "static"
    call_line: Optional[int] = None
    context: Optional[CallContext] = None


@dataclass
class CallGraphResult:
    """Result of call graph analysis."""

    nodes: List[CallNode] = field(default_factory=list)
    edges: List[CallEdge] = field(default_factory=list)
    entry_point: Optional[str] = None
    depth_limit: Optional[int] = None
    mermaid: str = ""
    # [20251225_FEATURE] Tier-friendly metadata for truncation and summaries
    total_nodes: int = 0
    total_edges: int = 0
    nodes_truncated: bool = False
    edges_truncated: bool = False


class CallGraphBuilder:
    """
    Builds a static call graph for a Python project.

    ====================================================================
    TIER 1: COMMUNITY (Free - High Priority)
    ====================================================================
            TODO [COMMUNITY][FEATURE]: Basic call graph building
        TODO [COMMUNITY]: Parse Python files and extract function definitions
        TODO [COMMUNITY]: Track function calls within each function
        TODO [COMMUNITY]: Build adjacency list representation
        TODO [COMMUNITY]: Handle basic import resolution
        TODO [COMMUNITY]: Add 25+ tests for core functionality
            TODO [COMMUNITY][FEATURE]: Entry point detection
        TODO [COMMUNITY]: Detect main() functions
        TODO [COMMUNITY]: Detect CLI decorators (click.command, etc.)
        TODO [COMMUNITY]: Identify __name__ == "__main__" blocks
        TODO [COMMUNITY]: Mark entry points in graph
        TODO [COMMUNITY]: Add 15+ tests for entry point detection
            TODO [COMMUNITY][FEATURE]: Basic visualization
        TODO [COMMUNITY]: Generate simple text representation
        TODO [COMMUNITY]: Output to stdout
        TODO [COMMUNITY]: Show call relationships
        TODO [COMMUNITY]: Add 10+ tests for visualization
            TODO [COMMUNITY][FEATURE]: Circular import detection
        TODO [COMMUNITY]: Find import cycles in project
        TODO [COMMUNITY]: Report cycle paths
        TODO [COMMUNITY]: Handle complex import graphs
        TODO [COMMUNITY]: Add 20+ tests for cycle detection
            TODO [COMMUNITY][TEST]: Adversarial tests
        TODO [COMMUNITY]: Empty files, single function projects
        TODO [COMMUNITY]: Deeply nested calls, recursive functions
        TODO [COMMUNITY]: Large projects, complex imports
    ====================================================================
    TIER 2: PRO (Commercial - Medium Priority)
    ====================================================================
            TODO [PRO][FEATURE]: Dynamic call detection      Purpose: Track reflection and dynamic imports
      Steps:
        1. Detect getattr() calls
        2. Track __getattribute__ overrides
        3. Detect importlib.import_module() patterns
        4. Detect __import__() usage
        5. Mark as potential calls with confidence
        6. Add 30+ tests for dynamic detection

            TODO [PRO][FEATURE]: Call frequency and confidence scoring      Purpose: Quantify call reliability
      Steps:
        1. Count call occurrences per pair
        2. Track conditional calls (if/try blocks)
        3. Score probability of execution
        4. Report confidence levels
        5. Add 25+ tests for scoring

            TODO [PRO][FEATURE]: Support async/await call graph      Purpose: Handle modern async patterns
      Steps:
        1. Detect AsyncFunctionDef definitions
        2. Track await expressions
        3. Handle async context managers
        4. Detect asyncio.create_task() patterns
        5. Build async call graph
        6. Add 25+ tests for async support

            TODO [PRO][FEATURE]: Framework-specific call patterns      Purpose: Understand framework conventions
      Steps:
        1. Django URL routing (url() patterns)
        2. FastAPI route decorators (app.get, app.post)
        3. Flask route registration
        4. Middleware chains
        5. Callback registration patterns
        6. Add 30+ tests for framework patterns

            TODO [PRO][ENHANCEMENT]: Mermaid diagram generation      Purpose: Better visualization capabilities
      Steps:
        1. Generate Mermaid syntax
        2. Support multiple diagram styles
        3. Color-code node types
        4. Add legend and statistics
        5. Export to HTML
        6. Add 15+ tests for diagram generation

            TODO [PRO][FEATURE]: Cross-file call tracking      Purpose: Understand module boundaries
      Steps:
        1. Track calls across files
        2. Mark external module calls
        3. Resolve imported function calls
        4. Detect library calls
        5. Add 25+ tests for cross-file

    ====================================================================
    TIER 3: ENTERPRISE (Commercial - Lower Priority)
    ====================================================================
            TODO [ENTERPRISE][FEATURE]: Advanced dynamic resolution      Purpose: Sophisticated call inference
      Steps:
        1. Use type hints for call inference
        2. Support Protocol/ABC matching
        3. Dataflow-based resolution
        4. Symbol table analysis
        5. Add 35+ tests for resolution

            TODO [ENTERPRISE][FEATURE]: Machine learning call prediction      Purpose: Predict likely calls in dynamic code
      Steps:
        1. Train on known call patterns
        2. Predict probable calls
        3. Confidence scoring
        4. Learn from user feedback
        5. Add 30+ tests for ML prediction

            TODO [ENTERPRISE][FEATURE]: Distributed call graph analysis      Purpose: Analyze large monorepos efficiently
      Steps:
        1. Parallel file parsing
        2. Incremental updates
        3. Caching between runs
        4. Distributed computation
        5. Add 25+ tests for distribution

            TODO [ENTERPRISE][ENHANCEMENT]: IDE integration      Purpose: Real-time call graph in editor
      Steps:
        1. LSP integration
        2. Real-time updates
        3. Quick peek implementation
        4. Go to definition
        5. Add 20+ tests for IDE features

            TODO [ENTERPRISE][FEATURE]: Advanced visualization      Purpose: Interactive call graph exploration
      Steps:
        1. Web-based visualization
        2. Force-directed layout
        3. Zoom and pan
        4. Filter by node type
        5. Search and highlighting
        6. Add 25+ tests for UI

            TODO [ENTERPRISE][FEATURE]: Performance analysis      Purpose: Identify bottleneck functions
      Steps:
        1. Integrate with profiling data
        2. Show call counts from traces
        3. Identify hot paths
        4. Suggest optimizations
        5. Add 20+ tests for performance
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.definitions: Dict[str, Set[str]] = (
            {}
        )  # file_path -> set of defined functions/classes
        self.calls: Dict[str, List[str]] = (
            {}
        )  # "file:function" -> list of called function names
        self.imports: Dict[str, Dict[str, str]] = (
            {}
        )  # file_path -> { alias -> full_name }

        # [20251231_FEATURE] v1.0 - JS/TS support for get_call_graph
        # Raw JS/TS import metadata: file -> local_name -> (module_spec, imported_name)
        self._js_imports_raw: Dict[str, Dict[str, tuple[str, str]]] = {}
        # Export index: file -> exported symbol names
        self._js_exports: Dict[str, Set[str]] = {}

    def build(self, advanced_resolution: bool = False) -> Dict[str, List[str]]:
        """Build the call graph.

        Returns an adjacency list: {"module:caller": ["module:callee", ...]}

        ====================================================================
        TIER 1: COMMUNITY (Free - High Priority)
        ====================================================================
                TODO [COMMUNITY][FEATURE]: Two-pass graph construction
        TODO [COMMUNITY]: First pass: collect definitions and imports
        TODO [COMMUNITY]: Second pass: analyze calls and resolve them
        TODO [COMMUNITY]: Error handling for malformed code
        TODO [COMMUNITY]: Add 15+ tests for build process        """
        # 1. First pass: Collect definitions and imports
        for file_path in self._iter_source_files():
            rel_path = str(file_path.relative_to(self.root_path))
            suffix = file_path.suffix.lower()

            if suffix == ".py":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                    tree = ast.parse(code)
                    self._analyze_definitions(tree, rel_path)
                except Exception:
                    continue
            elif suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
                self._analyze_definitions_js_ts(file_path, rel_path)

        # 2. Second pass: Analyze calls and resolve them
        graph: Dict[str, List[str]] = {}
        for file_path in self._iter_source_files():
            rel_path = str(file_path.relative_to(self.root_path))
            suffix = file_path.suffix.lower()

            if suffix == ".py":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                    tree = ast.parse(code)
                    file_calls = self._analyze_calls(
                        tree,
                        rel_path,
                        advanced_resolution=advanced_resolution,
                    )
                    graph.update(file_calls)
                except Exception:
                    continue
            elif suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
                file_calls = self._analyze_calls_js_ts(
                    file_path,
                    rel_path,
                    advanced_resolution=advanced_resolution,
                )
                graph.update(file_calls)

        return graph

    def _iter_source_files(self):
        """Iterate over supported source files (.py/.js/.ts) in project."""
        skip_dirs = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            "dist",
            "build",
        }
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
            for file in files:
                lower = file.lower()
                if lower.endswith(
                    (
                        ".py",
                        ".js",
                        ".jsx",
                        ".ts",
                        ".tsx",
                        ".mjs",
                        ".cjs",
                    )
                ):
                    yield Path(root) / file

    def _analyze_definitions_js_ts(self, file_path: Path, rel_path: str) -> None:
        """Extract JS/TS definitions and import/export metadata.

        Prefers tree-sitter (when available) and falls back to the Esprima-based
        parser shipped with Code Scalpel.
        """
        # ------------------------------------------------------------------
        # Tree-sitter path (preferred)
        # ------------------------------------------------------------------
        try:
            from code_scalpel.code_parsers.javascript_parsers.javascript_parsers_treesitter import (
                TREE_SITTER_AVAILABLE,
                TreeSitterJSParser,
            )
        except Exception:
            TREE_SITTER_AVAILABLE = False
            TreeSitterJSParser = None  # type: ignore[assignment]

        if TREE_SITTER_AVAILABLE and TreeSitterJSParser is not None:
            try:
                parser = TreeSitterJSParser()
                result = parser.parse_file(str(file_path))
            except Exception:
                result = None

            if result is not None:
                # Definitions
                self.definitions[rel_path] = set()
                for sym in result.symbols:
                    if sym.kind == "function":
                        self.definitions[rel_path].add(sym.name)
                    elif sym.kind == "class":
                        self.definitions[rel_path].add(sym.name)
                    elif sym.kind == "method" and sym.parent_name:
                        self.definitions[rel_path].add(f"{sym.parent_name}.{sym.name}")

                # Imports (raw)
                self._js_imports_raw.setdefault(rel_path, {})
                for imp in result.imports:
                    module = imp.module
                    # import foo from './x'
                    if imp.default_import:
                        self._js_imports_raw[rel_path][imp.default_import] = (
                            module,
                            "<default>",
                        )
                    # import * as ns from './x'
                    if imp.namespace_import:
                        self._js_imports_raw[rel_path][imp.namespace_import] = (
                            module,
                            "*",
                        )
                    # import { a as b } from './x'
                    for name, alias in imp.named_imports:
                        local = alias or name
                        self._js_imports_raw[rel_path][local] = (module, name)

                # Exports index (best-effort)
                self._js_exports.setdefault(rel_path, set())
                for ex in result.exports:
                    if ex.name:
                        self._js_exports[rel_path].add(ex.name)
                    if ex.kind == "default":
                        self._js_exports[rel_path].add("<default>")
                return

        # ------------------------------------------------------------------
        # Esprima fallback (portable)
        # ------------------------------------------------------------------
        try:
            import esprima  # type: ignore[import-untyped]
            import esprima.nodes  # type: ignore[import-untyped]
        except Exception:
            return

        try:
            code = file_path.read_text(encoding="utf-8")
        except Exception:
            return

        try:
            # Prefer module parsing so `import`/`export` works.
            ast_js = esprima.parseModule(code, loc=True, tolerant=True)
        except Exception:
            try:
                ast_js = esprima.parseScript(code, loc=True, tolerant=True)
            except Exception:
                return

        def _children(n):
            if isinstance(n, list):
                for item in n:
                    if isinstance(item, esprima.nodes.Node):
                        yield item
                return
            if not isinstance(n, esprima.nodes.Node):
                return

            # [20260102_REFACTOR] Avoid shadowing the imported esprima field helper
            for node_field in n.__dict__.values():
                if isinstance(node_field, esprima.nodes.Node):
                    yield node_field
                elif isinstance(node_field, list):
                    for item in node_field:
                        if isinstance(item, esprima.nodes.Node):
                            yield item

        # Definitions
        self.definitions[rel_path] = set()
        stack: list[esprima.nodes.Node] = [ast_js]
        while stack:
            cur = stack.pop()
            if isinstance(cur, esprima.nodes.FunctionDeclaration):
                func_id = getattr(cur, "id", None)
                name = getattr(func_id, "name", None)
                if name:
                    self.definitions[rel_path].add(name)
            for ch in _children(cur):
                stack.append(ch)

        # Imports (raw)
        self._js_imports_raw.setdefault(rel_path, {})
        stack: list[esprima.nodes.Node] = [ast_js]
        while stack:
            cur = stack.pop()
            if isinstance(cur, esprima.nodes.ImportDeclaration):
                module_val = getattr(getattr(cur, "source", None), "value", None)
                module = str(module_val) if module_val is not None else ""
                for spec in getattr(cur, "specifiers", []) or []:
                    if isinstance(spec, esprima.nodes.ImportDefaultSpecifier):
                        local = getattr(getattr(spec, "local", None), "name", None)
                        if local:
                            self._js_imports_raw[rel_path][local] = (
                                module,
                                "<default>",
                            )
                    elif isinstance(spec, esprima.nodes.ImportNamespaceSpecifier):
                        local = getattr(getattr(spec, "local", None), "name", None)
                        if local:
                            self._js_imports_raw[rel_path][local] = (module, "*")
                    elif isinstance(spec, esprima.nodes.ImportSpecifier):
                        imported = getattr(
                            getattr(spec, "imported", None), "name", None
                        )
                        local = (
                            getattr(getattr(spec, "local", None), "name", None)
                            or imported
                        )
                        if imported and local:
                            self._js_imports_raw[rel_path][local] = (
                                module,
                                str(imported),
                            )

            for ch in _children(cur):
                stack.append(ch)

        # Exports index (best-effort)
        self._js_exports.setdefault(rel_path, set())
        stack: list[esprima.nodes.Node] = [ast_js]
        while stack:
            cur = stack.pop()
            if isinstance(cur, esprima.nodes.ExportDefaultDeclaration):
                self._js_exports[rel_path].add("<default>")
                decl = getattr(cur, "declaration", None)
                name = getattr(getattr(decl, "id", None), "name", None)
                if name:
                    self._js_exports[rel_path].add(name)
            elif isinstance(cur, esprima.nodes.ExportNamedDeclaration):
                decl = getattr(cur, "declaration", None)
                exported_name = getattr(getattr(decl, "id", None), "name", None)
                if exported_name:
                    self._js_exports[rel_path].add(exported_name)
                for spec in getattr(cur, "specifiers", []) or []:
                    exported = getattr(getattr(spec, "exported", None), "name", None)
                    if exported:
                        self._js_exports[rel_path].add(exported)

            for ch in _children(cur):
                stack.append(ch)

    def _resolve_js_module_path(self, from_file: str, module_spec: str) -> str | None:
        """Resolve a relative JS/TS module specifier to a project-relative file path."""
        if not module_spec or not module_spec.startswith("."):
            return None

        base_dir = (self.root_path / from_file).parent
        # Handle './x', './x.js', './x.ts', './x/index.js', etc.
        candidate_bases = [module_spec]
        if not any(
            module_spec.endswith(ext)
            for ext in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")
        ):
            candidate_bases.extend(
                [
                    module_spec + ext
                    for ext in (".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs")
                ]
            )

        candidates: list[Path] = []
        for base in candidate_bases:
            candidates.append((base_dir / base).resolve())
        # index.* fallback
        if module_spec and not module_spec.endswith(
            (".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs")
        ):
            for ext in (".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs"):
                candidates.append((base_dir / module_spec / f"index{ext}").resolve())

        for p in candidates:
            try:
                if p.exists() and p.is_file() and self.root_path in p.parents:
                    return str(p.relative_to(self.root_path))
            except Exception:
                continue
        return None

    def _analyze_calls_js_ts(
        self,
        file_path: Path,
        rel_path: str,
        advanced_resolution: bool = False,
    ) -> Dict[str, List[str]]:
        """Build per-file call graph for JS/TS.

        Prefers tree-sitter (when available) and falls back to Esprima.
        """
        # ------------------------------------------------------------------
        # Tree-sitter path (preferred)
        # ------------------------------------------------------------------
        try:
            from code_scalpel.code_parsers.javascript_parsers.javascript_parsers_treesitter import (
                TREE_SITTER_AVAILABLE,
                TreeSitterJSParser,
            )
        except Exception:
            TREE_SITTER_AVAILABLE = False
            TreeSitterJSParser = None  # type: ignore[assignment]

        if TREE_SITTER_AVAILABLE and TreeSitterJSParser is not None:
            try:
                parser = TreeSitterJSParser()
                result = parser.parse_file(str(file_path))
                root = result.root_node
            except Exception:
                result = None
                root = None
        else:
            result = None
            root = None

        def _resolve_callee(raw_callee: str, caller_parent: str | None) -> str:
            # Resolve this.method() to Class.method when inside a class method.
            if advanced_resolution and caller_parent and raw_callee.startswith("this."):
                return f"{rel_path}:{caller_parent}.{raw_callee.split('.', 1)[1]}"

            # Local direct definition in same file
            if raw_callee in self.definitions.get(rel_path, set()):
                return f"{rel_path}:{raw_callee}"

            if advanced_resolution:
                # Resolve namespace imports: ns.foo()
                if "." in raw_callee:
                    base, member = raw_callee.split(".", 1)
                    imp = self._js_imports_raw.get(rel_path, {}).get(base)
                    if imp and imp[1] == "*":
                        mod = self._resolve_js_module_path(rel_path, imp[0])
                        if mod and member in self._js_exports.get(mod, set()):
                            return f"{mod}:{member}"

                # Resolve imported identifiers
                imp = self._js_imports_raw.get(rel_path, {}).get(raw_callee)
                if imp:
                    module_spec, imported_name = imp
                    mod = self._resolve_js_module_path(rel_path, module_spec)
                    if mod:
                        if imported_name == "<default>":
                            return f"{mod}:<default>"
                        if imported_name in self._js_exports.get(mod, set()):
                            return f"{mod}:{imported_name}"
                        # Best-effort even if exports index is incomplete
                        return f"{mod}:{imported_name}"

            return raw_callee

        if result is not None and root is not None:
            # Build a list of callable symbol ranges for caller attribution
            callable_ranges: list[tuple[int, int, str, str | None]] = []
            for sym in result.symbols:
                if sym.kind == "function":
                    end_line = sym.end_line or sym.line
                    callable_ranges.append((sym.line, end_line, sym.name, None))
                elif sym.kind == "method" and sym.parent_name:
                    end_line = sym.end_line or sym.line
                    callable_ranges.append(
                        (sym.line, end_line, sym.name, sym.parent_name)
                    )

            def _caller_for_line(line: int) -> tuple[str, str | None] | None:
                # Choose the smallest enclosing range (most specific)
                best: tuple[int, int, str, str | None] | None = None
                for start, end, name, parent in callable_ranges:
                    if start <= line <= end:
                        if best is None or (end - start) < (best[1] - best[0]):
                            best = (start, end, name, parent)
                if best is None:
                    return None
                return (best[2], best[3])

            def _callee_from_call(node) -> str | None:
                # call_expression: function field
                fn = node.child_by_field("function")
                if not fn:
                    return None
                # Identifier call
                if fn.type == "identifier":
                    return str(fn.text)
                # member_expression: obj.prop
                if fn.type == "member_expression":
                    obj = fn.child_by_field("object")
                    prop = fn.child_by_field("property")
                    if obj and prop:
                        return f"{str(obj.text)}.{str(prop.text)}"
                    return str(fn.text)
                return str(fn.text)

                # Walk tree to find call expressions
                file_graph: Dict[str, List[str]] = {}

                def visit(node) -> None:
                    if node.type in {"call_expression", "new_expression"}:
                        line = getattr(node, "start_line", None)
                        if isinstance(line, int):
                            caller = _caller_for_line(line)
                            if caller:
                                caller_name, caller_parent = caller
                                caller_key = (
                                    f"{rel_path}:{caller_parent}.{caller_name}"
                                    if caller_parent
                                    else f"{rel_path}:{caller_name}"
                                )
                                raw = _callee_from_call(node)
                                if raw:
                                    file_graph.setdefault(caller_key, []).append(
                                        _resolve_callee(raw, caller_parent)
                                    )

                    for child in getattr(node, "named_children", []) or []:
                        visit(child)

                visit(root)
                return file_graph

        # ------------------------------------------------------------------
        # Esprima fallback
        # ------------------------------------------------------------------
        try:
            import esprima  # type: ignore[import-untyped]
            import esprima.nodes  # type: ignore[import-untyped]
        except Exception:
            return {}

        try:
            code = file_path.read_text(encoding="utf-8")
        except Exception:
            return {}

        try:
            ast_js = esprima.parseModule(code, loc=True, tolerant=True)
        except Exception:
            try:
                ast_js = esprima.parseScript(code, loc=True, tolerant=True)
            except Exception:
                return {}

        def _children(n):
            if isinstance(n, list):
                for item in n:
                    if isinstance(item, esprima.nodes.Node):
                        yield item
                return
            if not isinstance(n, esprima.nodes.Node):
                return

            # [20260102_REFACTOR] Avoid shadowing the imported esprima field helper
            for node_field in n.__dict__.values():
                if isinstance(node_field, esprima.nodes.Node):
                    yield node_field
                elif isinstance(node_field, list):
                    for item in node_field:
                        if isinstance(item, esprima.nodes.Node):
                            yield item

        def _callee_name(call_node) -> str | None:
            callee = getattr(call_node, "callee", None)
            if isinstance(callee, esprima.nodes.Identifier):
                return callee.name
            if isinstance(callee, (esprima.nodes.StaticMemberExpression, esprima.nodes.ComputedMemberExpression)):
                obj = getattr(callee, "object", None)
                prop = getattr(callee, "property", None)
                if isinstance(obj, esprima.nodes.Identifier) and isinstance(
                    prop, esprima.nodes.Identifier
                ):
                    return f"{obj.name}.{prop.name}"
            return None

        file_graph: Dict[str, List[str]] = {}

        # Walk while tracking current function context.
        stack: list[tuple[object, str]] = [(ast_js, "<global>")]
        while stack:
            cur, current_fn = stack.pop()
            if isinstance(cur, esprima.nodes.FunctionDeclaration):
                name = getattr(getattr(cur, "id", None), "name", None) or "<anonymous>"
                # Traverse into the function body with new context.
                for ch in _children(cur):
                    stack.append((ch, name))
                continue

            if isinstance(
                cur, (esprima.nodes.CallExpression, esprima.nodes.NewExpression)
            ):
                raw = _callee_name(cur)
                if raw and current_fn not in {"<global>", "<anonymous>", "<arrow>"}:
                    caller_key = f"{rel_path}:{current_fn}"
                    file_graph.setdefault(caller_key, []).append(
                        _resolve_callee(raw, None)
                    )

            for ch in _children(cur):
                stack.append((ch, current_fn))

        return file_graph

    def _iter_python_files(self):
        """
        Iterate over all Python files in the project, skipping hidden/ignored dirs.

        Yields:
            Path: Absolute path to each Python file

        ====================================================================
        TIER 1: COMMUNITY (Free - High Priority)
        ====================================================================
                TODO [COMMUNITY][FEATURE]: Recursively walk directory tree
        TODO [COMMUNITY]: Use os.walk() for directory traversal
        TODO [COMMUNITY]: Start from project root
        TODO [COMMUNITY]: Yield files in consistent order
        TODO [COMMUNITY]: Add 10+ tests for directory walking
                TODO [COMMUNITY][FEATURE]: Filter Python files by extension
        TODO [COMMUNITY]: Check for .py file extension
        TODO [COMMUNITY]: Skip non-Python files
        TODO [COMMUNITY]: Handle special cases (__init__.py, setup.py)
        TODO [COMMUNITY]: Add 8+ tests for file filtering
                TODO [COMMUNITY][FEATURE]: Skip ignored directories
        TODO [COMMUNITY]: Skip .git, .venv, venv, __pycache__
        TODO [COMMUNITY]: Skip node_modules, dist, build
        TODO [COMMUNITY]: Skip hidden directories (.*)
        TODO [COMMUNITY]: Add 10+ tests for directory skipping
        ====================================================================
        TIER 2: PRO (Commercial - Medium Priority)
        ====================================================================
                TODO [PRO][FEATURE]: Respect .gitignore patterns
        TODO [PRO]: Parse .gitignore file
        TODO [PRO]: Apply glob patterns
        TODO [PRO]: Support negation patterns
        TODO [PRO]: Add 12+ tests for gitignore
                TODO [PRO][FEATURE]: Handle symbolic links
        TODO [PRO]: Detect symlinks to avoid loops
        TODO [PRO]: Option to follow symlinks
        TODO [PRO]: Track visited inodes
        TODO [PRO]: Add 10+ tests for symlinks
                TODO [PRO][FEATURE]: Performance optimization
        TODO [PRO]: Cache directory structure
        TODO [PRO]: Lazy evaluation of files
        TODO [PRO]: Parallel file discovery
        TODO [PRO]: Add 10+ tests for performance        """
        skip_dirs = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            "dist",
            "build",
        }
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
            for file in files:
                if file.endswith(".py"):
                    yield Path(root) / file

    def _analyze_definitions(self, tree: ast.AST, rel_path: str):
        """
        Extract function/class definitions and imports.

        Args:
            tree: AST of the file
            rel_path: Relative path of the file

        ====================================================================
        TIER 1: COMMUNITY (Free - High Priority)
        ====================================================================
                TODO [COMMUNITY][FEATURE]: Extract function definitions
        TODO [COMMUNITY]: Walk AST for FunctionDef and AsyncFunctionDef nodes
        TODO [COMMUNITY]: Store function names in definitions set
        TODO [COMMUNITY]: Handle nested functions
        TODO [COMMUNITY]: Add 10+ tests for function extraction
                TODO [COMMUNITY][FEATURE]: Extract class definitions
        TODO [COMMUNITY]: Walk AST for ClassDef nodes
        TODO [COMMUNITY]: Store class names in definitions set
        TODO [COMMUNITY]: Extract methods from classes
        TODO [COMMUNITY]: Add 10+ tests for class extraction
                TODO [COMMUNITY][FEATURE]: Collect import statements
        TODO [COMMUNITY]: Extract import and from...import statements
        TODO [COMMUNITY]: Map aliases to full module names
        TODO [COMMUNITY]: Handle wildcard imports (from x import *)
        TODO [COMMUNITY]: Add 15+ tests for import collection
        ====================================================================
        TIER 2: PRO (Commercial - Medium Priority)
        ====================================================================
                TODO [PRO][FEATURE]: Track relative imports
        TODO [PRO]: Resolve relative import dots (.., ...)
        TODO [PRO]: Convert relative to absolute paths
        TODO [PRO]: Handle package context
        TODO [PRO]: Add 10+ tests for relative imports
                TODO [PRO][FEATURE]: Extract decorator information
        TODO [PRO]: Track decorators on functions and classes
        TODO [PRO]: Store decorator metadata
        TODO [PRO]: Identify special decorators
        TODO [PRO]: Add 10+ tests for decorators
                TODO [PRO][FEATURE]: Type hint analysis
        TODO [PRO]: Extract type annotations
        TODO [PRO]: Store parameter types
        TODO [PRO]: Track return types
        TODO [PRO]: Add 10+ tests for type hints        """
        self.definitions[rel_path] = set()
        self.imports[rel_path] = {}

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.definitions[rel_path].add(node.name)
            elif isinstance(node, ast.ClassDef):
                self.definitions[rel_path].add(node.name)
                # Also add methods
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        self.definitions[rel_path].add(f"{node.name}.{item.name}")

            # Collect imports for resolution
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    asname = alias.asname or name
                    self.imports[rel_path][asname] = name
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    name = alias.name
                    asname = alias.asname or name
                    full_name = f"{module}.{name}" if module else name
                    self.imports[rel_path][asname] = full_name

    def _analyze_calls(
        self,
        tree: ast.AST,
        rel_path: str,
        advanced_resolution: bool = False,
    ) -> Dict[str, List[str]]:
        """
        Extract calls from functions and resolve them.

        Args:
            tree: AST of the file
            rel_path: Relative path of the file

        Returns:
            Dictionary mapping function keys to list of called function names

        ====================================================================
        TIER 1: COMMUNITY (Free - High Priority)
        ====================================================================
                TODO [COMMUNITY][FEATURE]: Extract function calls by name
        TODO [COMMUNITY]: Walk AST for Call nodes
        TODO [COMMUNITY]: Extract function names from ast.Name calls
        TODO [COMMUNITY]: Track current function scope
        TODO [COMMUNITY]: Store calls per function
        TODO [COMMUNITY]: Add 15+ tests for call extraction
                TODO [COMMUNITY][FEATURE]: Handle attribute method calls
        TODO [COMMUNITY]: Extract calls like obj.method()
        TODO [COMMUNITY]: Parse attribute chains
        TODO [COMMUNITY]: Simplify attribute names
        TODO [COMMUNITY]: Add 12+ tests for method calls
                TODO [COMMUNITY][FEATURE]: Resolve local calls
        TODO [COMMUNITY]: Map called names to definitions
        TODO [COMMUNITY]: Handle local vs imported functions
        TODO [COMMUNITY]: Create qualified function names
        TODO [COMMUNITY]: Add 12+ tests for resolution
        ====================================================================
        TIER 2: PRO (Commercial - Medium Priority)
        ====================================================================
                TODO [PRO][FEATURE]: Track call line numbers
        TODO [PRO]: Store AST node line information
        TODO [PRO]: Create call edges with location data
        TODO [PRO]: Support call statistics
        TODO [PRO]: Add 10+ tests for line tracking
                TODO [PRO][FEATURE]: Detect dynamic calls
        TODO [PRO]: Find getattr() calls
        TODO [PRO]: Detect __call__ invocations
        TODO [PRO]: Handle indirect calls
        TODO [PRO]: Add 15+ tests for dynamic detection
                TODO [PRO][FEATURE]: Cross-file call resolution
        TODO [PRO]: Resolve imported function calls
        TODO [PRO]: Handle relative imports
        TODO [PRO]: Build cross-file call graphs
        TODO [PRO]: Add 15+ tests for cross-file        """
        file_graph = {}

        class CallVisitor(ast.NodeVisitor):
            def __init__(self, builder, current_file):
                self.builder = builder
                self.current_file = current_file
                self.current_scope: str | None = None
                self.calls: list[str] = []

                # [20251225_FEATURE] Pro+ scoped method resolution (best-effort)
                self._advanced_resolution = advanced_resolution
                self._current_class: str | None = None
                self._var_types: Dict[str, str] = {}

            def visit_ClassDef(self, node: ast.ClassDef) -> None:
                if not self._advanced_resolution:
                    self.generic_visit(node)
                    return

                old_class = self._current_class
                self._current_class = node.name
                self.generic_visit(node)
                self._current_class = old_class

            def visit_FunctionDef(
                self, node: ast.FunctionDef | ast.AsyncFunctionDef
            ) -> None:
                old_scope = self.current_scope

                if self._advanced_resolution and self._current_class:
                    self.current_scope = f"{self._current_class}.{node.name}"
                else:
                    self.current_scope = node.name

                self.calls = []
                self._var_types = {}
                self.generic_visit(node)

                # Store calls for this function
                key = f"{self.current_file}:{self.current_scope}"
                file_graph[key] = self.calls

                self.current_scope = old_scope

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
                self.visit_FunctionDef(node)

            def visit_Call(self, node: ast.Call) -> None:
                if self.current_scope:
                    callee = self._get_callee_name(node)
                    if callee:
                        resolved = self._resolve_callee(callee)
                        self.calls.append(resolved)
                self.generic_visit(node)

            def visit_Assign(self, node: ast.Assign) -> None:
                if not (self._advanced_resolution and self.current_scope):
                    self.generic_visit(node)
                    return

                # Track simple type assignments: x = ClassName()
                class_name: str | None = None
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        class_name = node.value.func.id
                    elif isinstance(node.value.func, ast.Attribute):
                        # module.ClassName() -> take last segment
                        class_name = node.value.func.attr

                if class_name:
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self._var_types[target.id] = class_name

                self.generic_visit(node)

            def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
                if not (self._advanced_resolution and self.current_scope):
                    self.generic_visit(node)
                    return

                # Track simple annotations: x: ClassName = ...
                if isinstance(node.target, ast.Name):
                    ann = node.annotation
                    if isinstance(ann, ast.Name):
                        self._var_types[node.target.id] = ann.id
                    elif isinstance(ann, ast.Attribute):
                        self._var_types[node.target.id] = ann.attr

                self.generic_visit(node)

            def _get_callee_name(self, node: ast.Call) -> str | None:
                if isinstance(node.func, ast.Name):
                    return node.func.id
                if isinstance(node.func, ast.Attribute):
                    value = self._get_attribute_value(node.func.value)
                    if not value:
                        return None

                    if self._advanced_resolution:
                        # Resolve self.method() -> ClassName.method()
                        if value == "self" and self._current_class:
                            return f"{self._current_class}.{node.func.attr}"
                        # Resolve instance.method() using simple type tracking
                        if value in self._var_types:
                            return f"{self._var_types[value]}.{node.func.attr}"

                    return f"{value}.{node.func.attr}"

                return None

            def _get_attribute_value(self, node):
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    val = self._get_attribute_value(node.value)
                    return f"{val}.{node.attr}" if val else None
                return None

            def _resolve_callee(self, callee):
                # 1. Check local imports
                imports = self.builder.imports.get(self.current_file, {})

                # Case: alias.method() where alias is imported
                parts = callee.split(".")
                if parts[0] in imports:
                    # e.g. "utils.hash" where "import my_utils as utils" -> "my_utils.hash"
                    # or "hash" where "from utils import hash" -> "utils.hash"
                    resolved_base = imports[parts[0]]
                    if len(parts) > 1:
                        return f"{resolved_base}.{'.'.join(parts[1:])}"
                    return resolved_base

                # 2. Check if it's a local definition in the same file
                if callee in self.builder.definitions.get(self.current_file, set()):
                    return f"{self.current_file}:{callee}"

                # 3. Fallback: return as is (likely external lib or built-in)
                return callee

        visitor = CallVisitor(self, rel_path)
        visitor.visit(tree)
        return file_graph

    # [20251213_FEATURE] v1.5.0 - Enhanced call graph methods

    def build_with_details(
        self,
        entry_point: Optional[str] = None,
        depth: int = 10,
        max_nodes: Optional[int] = None,
        advanced_resolution: bool = False,
    ) -> CallGraphResult:
        """
        Build call graph with detailed node and edge information.

        Args:
            entry_point: Starting function (e.g., "main" or "src/app.py:main")
                        If None, includes all functions
            depth: Maximum depth to traverse from entry point (default: 10)

        Returns:
            CallGraphResult with nodes, edges, and Mermaid diagram

        ====================================================================
        TIER 2: PRO (Commercial - Medium Priority)
        ====================================================================
                TODO [PRO][FEATURE]: Collect node information with line numbers
        TODO [PRO]: Parse files and extract function locations
        TODO [PRO]: Track line numbers and end lines
        TODO [PRO]: Build node metadata
        TODO [PRO]: Add 15+ tests for node collection
                TODO [PRO][FEATURE]: Filter to reachable nodes
        TODO [PRO]: BFS/DFS from entry point
        TODO [PRO]: Apply depth limit
        TODO [PRO]: Mark reachable subset
        TODO [PRO]: Handle cycles gracefully
        TODO [PRO]: Add 15+ tests for reachability
                TODO [PRO][FEATURE]: Build edges list
        TODO [PRO]: Create edge objects
        TODO [PRO]: Track call line numbers
        TODO [PRO]: Filter by reachability
        TODO [PRO]: Add 12+ tests for edge building
                TODO [PRO][FEATURE]: Generate Mermaid diagram
        TODO [PRO]: Create Mermaid syntax
        TODO [PRO]: Apply node styling
        TODO [PRO]: Show call relationships
        TODO [PRO]: Export format
        TODO [PRO]: Add 15+ tests for Mermaid        """
        # [20251225_FEATURE] Pro+ may enable improved method/polymorphism resolution
        base_graph = self.build(advanced_resolution=advanced_resolution)

        # Collect node information with line numbers
        node_info: Dict[str, CallNode] = {}

        # Python nodes
        for file_path in self._iter_source_files():
            rel_path = str(file_path.relative_to(self.root_path))
            suffix = file_path.suffix.lower()
            if suffix != ".py":
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                tree = ast.parse(code)

                if advanced_resolution:
                    for top in getattr(tree, "body", []):
                        if isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            key = f"{rel_path}:{top.name}"
                            node_info[key] = CallNode(
                                name=top.name,
                                file=rel_path,
                                line=top.lineno,
                                end_line=getattr(top, "end_lineno", None),
                                is_entry_point=self._is_entry_point(top, tree),
                            )
                        elif isinstance(top, ast.ClassDef):
                            for item in top.body:
                                if isinstance(
                                    item, (ast.FunctionDef, ast.AsyncFunctionDef)
                                ):
                                    qualified = f"{top.name}.{item.name}"
                                    key = f"{rel_path}:{qualified}"
                                    node_info[key] = CallNode(
                                        name=qualified,
                                        file=rel_path,
                                        line=item.lineno,
                                        end_line=getattr(item, "end_lineno", None),
                                        is_entry_point=False,
                                    )
                else:
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            key = f"{rel_path}:{node.name}"
                            node_info[key] = CallNode(
                                name=node.name,
                                file=rel_path,
                                line=node.lineno,
                                end_line=getattr(node, "end_lineno", None),
                                is_entry_point=self._is_entry_point(node, tree),
                            )
            except Exception:
                continue

        # JS/TS nodes
        tree_sitter_available = False
        TreeSitterJSParser = None  # type: ignore[assignment]
        try:
            from code_scalpel.code_parsers.javascript_parsers.javascript_parsers_treesitter import (
                TREE_SITTER_AVAILABLE,
            )
            from code_scalpel.code_parsers.javascript_parsers.javascript_parsers_treesitter import (
                TreeSitterJSParser as _TSParser,
            )

            tree_sitter_available = bool(TREE_SITTER_AVAILABLE)
            TreeSitterJSParser = _TSParser
        except Exception:
            tree_sitter_available = False

        def _add_js_nodes_esprima(file_path: Path, rel_path: str) -> None:
            try:
                import esprima  # type: ignore[import-untyped]
                import esprima.nodes  # type: ignore[import-untyped]
            except Exception:
                return

            try:
                code = file_path.read_text(encoding="utf-8")
            except Exception:
                return

            try:
                ast_js = esprima.parseModule(code, loc=True, tolerant=True)
            except Exception:
                try:
                    ast_js = esprima.parseScript(code, loc=True, tolerant=True)
                except Exception:
                    return

            def _children(n):
                if isinstance(n, list):
                    for item in n:
                        if isinstance(item, esprima.nodes.Node):
                            yield item
                    return
                if not isinstance(n, esprima.nodes.Node):
                    return
                # [20260102_REFACTOR] Avoid shadowing the imported esprima field helper
                for node_field in n.__dict__.values():
                    if isinstance(node_field, esprima.nodes.Node):
                        yield node_field
                    elif isinstance(node_field, list):
                        for item in node_field:
                            if isinstance(item, esprima.nodes.Node):
                                yield item

            def _callee_ident(call_node) -> str | None:
                callee = getattr(call_node, "callee", None)
                if isinstance(callee, esprima.nodes.Identifier):
                    return callee.name
                return None

            # Determine top-level called identifiers.
            top_level_called: Set[str] = set()
            call_stack: list[tuple[esprima.nodes.Node, str]] = [(ast_js, "<global>")]
            while call_stack:
                cur, current_fn = call_stack.pop()
                if isinstance(cur, esprima.nodes.FunctionDeclaration):
                    name = (
                        getattr(getattr(cur, "id", None), "name", None) or "<anonymous>"
                    )
                    for ch in _children(cur):
                        call_stack.append((ch, name))
                    continue

                if current_fn == "<global>" and isinstance(
                    cur, esprima.nodes.CallExpression
                ):
                    ident = _callee_ident(cur)
                    if ident:
                        top_level_called.add(ident)

                for ch in _children(cur):
                    call_stack.append((ch, current_fn))

            # Extract function declarations.
            func_stack: list[esprima.nodes.Node] = [ast_js]
            while func_stack:
                cur = func_stack.pop()
                if isinstance(cur, esprima.nodes.FunctionDeclaration):
                    name = getattr(getattr(cur, "id", None), "name", None)
                    if name:
                        loc = getattr(cur, "loc", None)
                        start = getattr(loc, "start", None) if loc else None
                        end = getattr(loc, "end", None) if loc else None
                        line = getattr(start, "line", 0) if start else 0
                        end_line = getattr(end, "line", None) if end else None
                        key = f"{rel_path}:{name}"
                        is_entry = name == "main" or name in top_level_called
                        node_info[key] = CallNode(
                            name=name,
                            file=rel_path,
                            line=line,
                            end_line=end_line,
                            is_entry_point=is_entry,
                        )
                for ch in _children(cur):
                    func_stack.append(ch)

        if tree_sitter_available and TreeSitterJSParser is not None:
            js_parser = TreeSitterJSParser()
            for file_path in self._iter_source_files():
                rel_path = str(file_path.relative_to(self.root_path))
                suffix = file_path.suffix.lower()
                if suffix not in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
                    continue
                try:
                    parsed = js_parser.parse_file(str(file_path))
                except Exception:
                    # tree-sitter may be "available" but lack language bindings at runtime.
                    _add_js_nodes_esprima(file_path, rel_path)
                    continue

                # Best-effort JS entry-point detection: functions invoked as direct root statements.
                top_level_called: Set[str] = set()
                try:
                    for child in getattr(parsed.root_node, "named_children", []) or []:
                        if child.type != "expression_statement":
                            continue
                        expr = child.child_by_field("expression")
                        if expr and expr.type == "call_expression":
                            fn = expr.child_by_field("function")
                            if fn and fn.type == "identifier":
                                top_level_called.add(str(fn.text))
                except Exception:
                    pass

                for sym in parsed.symbols:
                    if sym.kind == "function":
                        key = f"{rel_path}:{sym.name}"
                        is_entry = sym.name == "main" or sym.name in top_level_called
                        node_info[key] = CallNode(
                            name=sym.name,
                            file=rel_path,
                            line=sym.line,
                            end_line=sym.end_line,
                            is_entry_point=is_entry,
                        )
                    elif (
                        sym.kind == "method" and sym.parent_name and advanced_resolution
                    ):
                        qualified = f"{sym.parent_name}.{sym.name}"
                        key = f"{rel_path}:{qualified}"
                        node_info[key] = CallNode(
                            name=qualified,
                            file=rel_path,
                            line=sym.line,
                            end_line=sym.end_line,
                            is_entry_point=False,
                        )
        else:
            for file_path in self._iter_source_files():
                rel_path = str(file_path.relative_to(self.root_path))
                suffix = file_path.suffix.lower()
                if suffix not in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
                    continue
                _add_js_nodes_esprima(file_path, rel_path)

        # If entry_point is specified, filter to reachable nodes
        if entry_point:
            reachable = self._get_reachable_nodes(base_graph, entry_point, depth)
        else:
            # "Includes all functions" should include leaf nodes too (nodes with no outgoing edges).
            reachable = set(node_info.keys()) | set(base_graph.keys())

        reachable_list = sorted(reachable)
        total_nodes = len(reachable_list)
        nodes_truncated = False
        if max_nodes is not None and total_nodes > max_nodes:
            reachable_list = reachable_list[:max_nodes]
            nodes_truncated = True

        included = set(reachable_list)

        nodes: List[CallNode] = []
        seen_nodes = set()
        for key in reachable_list:
            if key in node_info:
                nodes.append(node_info[key])
                seen_nodes.add(key)
            else:
                # External or built-in function
                nodes.append(
                    CallNode(
                        name=key.split(":")[-1] if ":" in key else key,
                        file="<external>" if ":" not in key else key.split(":")[0],
                        line=0,
                    )
                )
                seen_nodes.add(key)

        # Build edges list
        edges_full: List[CallEdge] = []
        edges: List[CallEdge] = []
        for caller, callees in base_graph.items():
            if caller not in reachable:
                continue
            for callee in callees:
                edges_full.append(CallEdge(caller=caller, callee=callee))

                # If nodes were truncated, drop edges to truncated nodes.
                if nodes_truncated:
                    if caller not in included:
                        continue
                    if callee in reachable and callee not in included:
                        continue

                edges.append(CallEdge(caller=caller, callee=callee))

        total_edges = len(edges_full)
        edges_truncated = len(edges) != total_edges

        # Generate Mermaid diagram
        mermaid = self._generate_mermaid(nodes, edges, entry_point)

        return CallGraphResult(
            nodes=nodes,
            edges=edges,
            entry_point=entry_point,
            depth_limit=depth,
            mermaid=mermaid,
            total_nodes=total_nodes,
            total_edges=total_edges,
            nodes_truncated=nodes_truncated,
            edges_truncated=edges_truncated,
        )

    def _is_entry_point(
        self, func_node: ast.FunctionDef | ast.AsyncFunctionDef, tree: ast.AST
    ) -> bool:
        """
        Detect if a function is likely an entry point.

        Entry point heuristics:
        - Function named "main"
        - Function decorated with CLI decorators (click.command, etc.)
        - Function called in if __name__ == "__main__" block

        ====================================================================
        TIER 1: COMMUNITY (Free - High Priority)
        ====================================================================
                TODO [COMMUNITY][FEATURE]: Detect 'main' function by name
        TODO [COMMUNITY]: Check if node.name == 'main'
        TODO [COMMUNITY]: Add 5+ tests for main detection
                TODO [COMMUNITY][FEATURE]: Check for common decorator patterns
        TODO [COMMUNITY]: Detect @click.command()
        TODO [COMMUNITY]: Detect @app.route()
        TODO [COMMUNITY]: Detect @cli.command()
        TODO [COMMUNITY]: Add 10+ tests for decorator detection
        ====================================================================
        TIER 2: PRO (Commercial - Medium Priority)
        ====================================================================
                TODO [PRO][FEATURE]: Detect framework-specific entry patterns
        TODO [PRO]: FastAPI: @app.on_event("startup")
        TODO [PRO]: Django: management command detection
        TODO [PRO]: Flask: @app.before_request, @app.after_request
        TODO [PRO]: Add 15+ tests for framework patterns
                TODO [PRO][FEATURE]: Confidence scoring for entry points
        TODO [PRO]: High confidence: main() or __name__ == '__main__'
        TODO [PRO]: Medium confidence: common decorators
        TODO [PRO]: Low confidence: CLI-like decorators
        TODO [PRO]: Add 10+ tests for confidence calculation        """
        if func_node.name == "main":
            return True

        # Detect calls in if __name__ == "__main__" blocks
        try:
            for node in ast.walk(tree):
                if not isinstance(node, ast.If):
                    continue

                test = node.test
                if not isinstance(test, ast.Compare):
                    continue

                if not (
                    isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"
                    and len(test.ops) == 1
                    and isinstance(test.ops[0], ast.Eq)
                    and len(test.comparators) == 1
                ):
                    continue

                comp = test.comparators[0]
                value = None
                if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
                    value = comp.value
                elif isinstance(comp, ast.Str):
                    value = comp.s

                if value != "__main__":
                    continue

                for stmt in node.body:
                    for inner in ast.walk(stmt):
                        if isinstance(inner, ast.Call) and isinstance(
                            inner.func, ast.Name
                        ):
                            if inner.func.id == func_node.name:
                                return True
        except Exception:
            pass

        # Check for CLI decorators
        for decorator in getattr(func_node, "decorator_list", []):
            dec_name = ""
            if isinstance(decorator, ast.Name):
                dec_name = decorator.id
            elif isinstance(decorator, ast.Attribute):
                dec_name = decorator.attr
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    dec_name = decorator.func.attr
                elif isinstance(decorator.func, ast.Name):
                    dec_name = decorator.func.id

            if dec_name in ("command", "main", "cli", "app", "route", "get", "post"):
                return True

        return False

    def _get_reachable_nodes(
        self,
        graph: Dict[str, List[str]],
        entry_point: str,
        max_depth: int,
    ) -> Set[str]:
        """
        Get all nodes reachable from entry point within depth limit using BFS.
        Handles recursive calls gracefully.

        Args:
            graph: Call graph mapping caller to callees
            entry_point: Starting function key (e.g., "file.py:main")
            max_depth: Maximum depth to traverse

        Returns:
            Set of reachable node keys

        ====================================================================
        TIER 2: PRO (Commercial - Medium Priority)
        ====================================================================
                TODO [PRO][FEATURE]: BFS traversal with depth limiting
        TODO [PRO]: Initialize queue with entry point and depth 0
        TODO [PRO]: Process nodes in breadth-first order
        TODO [PRO]: Stop when depth exceeds max_depth
        TODO [PRO]: Handle missing entry points gracefully
        TODO [PRO]: Add 15+ tests for BFS traversal
                TODO [PRO][FEATURE]: Cycle detection in reachability
        TODO [PRO]: Track visited nodes to prevent infinite loops
        TODO [PRO]: Store path information for cycle reporting
        TODO [PRO]: Add 12+ tests for cycle handling
        ====================================================================
        TIER 3: ENTERPRISE (Commercial - Lower Priority)
        ====================================================================
                TODO [ENTERPRISE][FEATURE]: Advanced depth analysis
        TODO [ENTERPRISE]: Calculate depth for each reachable node
        TODO [ENTERPRISE]: Identify deepest call paths
        TODO [ENTERPRISE]: Compute call levels and stratification
        TODO [ENTERPRISE]: Add 10+ tests for depth analysis        """
        # Normalize entry point (might be just "main" or "file:main")
        if ":" not in entry_point:
            # Find the full key
            for key in graph.keys():
                if key.endswith(f":{entry_point}"):
                    entry_point = key
                    break

        reachable = set()
        queue = deque([(entry_point, 0)])

        while queue:
            node, depth = queue.popleft()

            if node in reachable:
                continue  # Already visited (handles cycles)

            reachable.add(node)

            if depth >= max_depth:
                continue  # Don't explore further

            # Add callees to queue
            for callee in graph.get(node, []):
                if callee not in reachable:
                    queue.append((callee, depth + 1))

        return reachable

    def _generate_mermaid(
        self,
        nodes: List[CallNode],
        edges: List[CallEdge],
        entry_point: Optional[str],
    ) -> str:
        """
        Generate Mermaid flowchart diagram from call graph.

        Args:
            nodes: List of call nodes to visualize
            edges: List of call edges to visualize
            entry_point: Optional entry point to highlight

        Returns:
            Mermaid diagram syntax

        ====================================================================
        TIER 2: PRO (Commercial - Medium Priority)
        ====================================================================
                TODO [PRO][FEATURE]: Basic Mermaid diagram generation
        TODO [PRO]: Create graph TD structure
        TODO [PRO]: Map nodes to node IDs
        TODO [PRO]: Add node labels with line numbers
        TODO [PRO]: Create edges between nodes
        TODO [PRO]: Add 15+ tests for diagram generation
                TODO [PRO][FEATURE]: Node styling based on type
        TODO [PRO]: Stadium shape for entry points
        TODO [PRO]: Round shape for external functions
        TODO [PRO]: Rectangle for internal functions
        TODO [PRO]: Color coding for call frequency
        TODO [PRO]: Add 10+ tests for styling
        ====================================================================
        TIER 3: ENTERPRISE (Commercial - Lower Priority)
        ====================================================================
                TODO [ENTERPRISE][FEATURE]: Advanced diagram customization
        TODO [ENTERPRISE]: Parameter sizing based on call count
        TODO [ENTERPRISE]: Color gradients for importance
        TODO [ENTERPRISE]: Subgraph clustering for modules
        TODO [ENTERPRISE]: Interactive highlighting
        TODO [ENTERPRISE]: Add 15+ tests for customization
                TODO [ENTERPRISE][FEATURE]: Export to multiple formats
        TODO [ENTERPRISE]: SVG export
        TODO [ENTERPRISE]: PNG rasterization
        TODO [ENTERPRISE]: HTML interactive viewer
        TODO [ENTERPRISE]: GraphML format for other tools
        TODO [ENTERPRISE]: Add 12+ tests for export formats        """
        lines = ["graph TD"]

        # Create node ID mapping (Mermaid doesn't like special chars)
        node_ids: Dict[str, str] = {}
        for i, node in enumerate(nodes):
            full_name = (
                f"{node.file}:{node.name}" if node.file != "<external>" else node.name
            )
            node_id = f"N{i}"
            node_ids[full_name] = node_id
            # Also map short names for external refs
            node_ids[node.name] = node_ids.get(node.name, node_id)

        # Add nodes with labels
        for i, node in enumerate(nodes):
            node_id = f"N{i}"
            label = node.name
            if node.line > 0:
                label = f"{node.name}:L{node.line}"

            # Style entry points differently
            if node.is_entry_point or (
                entry_point and entry_point.endswith(f":{node.name}")
            ):
                lines.append(f'    {node_id}[["{label}"]]')  # Stadium shape for entry
            elif node.file == "<external>":
                lines.append(f"    {node_id}({label})")  # Round for external
            else:
                lines.append(f'    {node_id}["{label}"]')  # Rectangle for internal

        # Add edges
        for edge in edges:
            caller_id = node_ids.get(edge.caller) or node_ids.get(
                edge.caller.split(":")[-1]
            )
            callee_id = node_ids.get(edge.callee) or node_ids.get(
                edge.callee.split(":")[-1]
            )

            if caller_id and callee_id:
                lines.append(f"    {caller_id} --> {callee_id}")

        return "\n".join(lines)

    def detect_circular_imports(self) -> List[List[str]]:
        """
        Detect circular import cycles in the project.

        [20251213_FEATURE] P1 - Circular dependency detection

        Returns:
            List of cycles, where each cycle is a list of module paths
            e.g., [["a.py", "b.py", "a.py"], ["c.py", "d.py", "e.py", "c.py"]]

        ====================================================================
        TIER 1: COMMUNITY (Free - High Priority)
        ====================================================================
                TODO [COMMUNITY][FEATURE]: Build import graph from AST
        TODO [COMMUNITY]: Iterate over all Python files
        TODO [COMMUNITY]: Extract import statements (import, from...import)
        TODO [COMMUNITY]: Build module adjacency list
        TODO [COMMUNITY]: Handle relative imports correctly
        TODO [COMMUNITY]: Add 15+ tests for graph building
                TODO [COMMUNITY][FEATURE]: Cycle detection using DFS
        TODO [COMMUNITY]: Implement 3-color DFS (WHITE, GRAY, BLACK)
        TODO [COMMUNITY]: Detect cycles when finding GRAY node
        TODO [COMMUNITY]: Extract cycle path from stack
        TODO [COMMUNITY]: Handle missing/external modules
        TODO [COMMUNITY]: Add 15+ tests for DFS algorithm
        ====================================================================
        TIER 2: PRO (Commercial - Medium Priority)
        ====================================================================
                TODO [PRO][FEATURE]: Detailed cycle information
        TODO [PRO]: Track cycle depth and impact
        TODO [PRO]: Identify common paths in cycles
        TODO [PRO]: Suggest import order fixes
        TODO [PRO]: Calculate cycle metrics
        TODO [PRO]: Add 12+ tests for cycle analysis
                TODO [PRO][FEATURE]: Dynamic import resolution
        TODO [PRO]: Handle importlib usage
        TODO [PRO]: Detect runtime imports
        TODO [PRO]: Support conditional imports
        TODO [PRO]: Track circular import avoidance
        TODO [PRO]: Add 10+ tests for dynamic imports
        ====================================================================
        TIER 3: ENTERPRISE (Commercial - Lower Priority)
        ====================================================================
                TODO [ENTERPRISE][FEATURE]: Visualization of circular imports
        TODO [ENTERPRISE]: Generate dependency diagrams
        TODO [ENTERPRISE]: Highlight cycle paths
        TODO [ENTERPRISE]: Show import count per module
        TODO [ENTERPRISE]: Interactive cycle explorer
        TODO [ENTERPRISE]: Add 12+ tests for visualization
                TODO [ENTERPRISE][FEATURE]: Automated refactoring suggestions
        TODO [ENTERPRISE]: Suggest module reorganization
        TODO [ENTERPRISE]: Identify mediator modules
        TODO [ENTERPRISE]: Propose breaking points
        TODO [ENTERPRISE]: Generate refactoring plan
        TODO [ENTERPRISE]: Add 15+ tests for suggestions        """
        # Build import graph: module -> modules it imports
        import_graph: Dict[str, Set[str]] = {}

        for file_path in self._iter_source_files():
            rel_path = str(file_path.relative_to(self.root_path))
            suffix = file_path.suffix.lower()
            try:
                if suffix == ".py":
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                    tree = ast.parse(code)

                    imports = set()
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                # Convert module name to potential file path
                                mod_path = alias.name.replace(".", "/") + ".py"
                                imports.add(mod_path)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                mod_path = node.module.replace(".", "/") + ".py"
                                imports.add(mod_path)

                    import_graph[rel_path] = imports

                elif suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
                    # Best-effort JS/TS cycle detection via relative imports
                    try:
                        from code_scalpel.code_parsers.javascript_parsers.javascript_parsers_treesitter import (
                            TREE_SITTER_AVAILABLE,
                            TreeSitterJSParser,
                        )
                    except Exception:
                        continue

                    if not TREE_SITTER_AVAILABLE:
                        continue

                    parser = TreeSitterJSParser()
                    result = parser.parse_file(str(file_path))
                    imports = set()
                    for imp in result.imports:
                        mod = self._resolve_js_module_path(rel_path, imp.module)
                        if mod:
                            imports.add(mod)
                    import_graph[rel_path] = imports
            except Exception:
                continue

        # Find cycles using DFS with coloring
        cycles = []
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in import_graph}
        path = []

        def dfs(node: str):
            if color[node] == GRAY:
                # Found a cycle - extract it
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if color[node] == BLACK:
                return

            color[node] = GRAY
            path.append(node)

            for neighbor in import_graph.get(node, set()):
                if neighbor in import_graph:  # Only follow internal imports
                    dfs(neighbor)

            path.pop()
            color[node] = BLACK

        for node in import_graph:
            if color[node] == WHITE:
                dfs(node)

        return cycles
