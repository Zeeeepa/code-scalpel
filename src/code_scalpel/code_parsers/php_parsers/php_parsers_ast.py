#!/usr/bin/env python3
"""PHP AST / structure parser — uses PHPNormalizer for pure-Python extraction.

[20260304_FEATURE] Phase 2: full implementation using internal PHPNormalizer
(no external CLI required).

This parser wraps Code Scalpel's own PHPNormalizer to extract class and
function structure from PHP source files, providing the same interface
that PHP-Parser (the PHP library) would via CLI.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PHPClass:
    """Represents a PHP class definition."""

    name: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    namespace: Optional[str] = None
    methods: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    parent_class: Optional[str] = None
    interfaces: List[str] = field(default_factory=list)
    is_abstract: bool = False
    is_final: bool = False


@dataclass
class PHPFunction:
    """Represents a PHP function definition."""

    name: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    namespace: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None


class PHPParserAST:
    """PHP structure analyser using internal PHPNormalizer.

    [20260304_FEATURE] Full implementation — no external CLI needed.
    Falls back gracefully if tree-sitter-php is not installed.
    """

    def __init__(self) -> None:
        """Initialise PHPParserAST."""
        self.classes: List[PHPClass] = []
        self.functions: List[PHPFunction] = []
        self.language = "php"
        self._normalizer = None  # lazy load

    def _get_normalizer(self):
        """Lazily load PHPNormalizer; returns None if unavailable."""
        if self._normalizer is not None:
            return self._normalizer
        try:
            from code_scalpel.ir.normalizers.php_normalizer import PHPNormalizer

            self._normalizer = PHPNormalizer()
        except ImportError:
            self._normalizer = None
        return self._normalizer

    # ------------------------------------------------------------------
    # File-level interface
    # ------------------------------------------------------------------

    def parse_file(self, php_file: Path) -> Dict[str, Any]:
        """Parse a PHP file and return structure summary.

        [20260304_FEATURE] Reads file and delegates to extract_classes/functions.

        Args:
            php_file: Path to PHP file.
        Returns:
            Dict with ``classes``, ``functions``, ``file`` keys.
        """
        try:
            source = Path(php_file).read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return {"error": str(exc), "classes": [], "functions": []}
        classes = self.extract_classes(source, file_path=str(php_file))
        functions = self.extract_functions(source, file_path=str(php_file))
        self.classes = classes
        self.functions = functions
        return {
            "file": str(php_file),
            "classes": [
                {
                    "name": c.name,
                    "methods": c.methods,
                    "line": c.line_number,
                }
                for c in classes
            ],
            "functions": [
                {"name": f.name, "parameters": f.parameters, "line": f.line_number}
                for f in functions
            ],
        }

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def extract_classes(
        self, php_code: str, file_path: Optional[str] = None
    ) -> List[PHPClass]:
        """Extract class definitions from PHP source.

        [20260304_FEATURE] Uses PHPNormalizer to walk IR.

        Args:
            php_code: PHP source code.
            file_path: Optional file path for attribution.
        Returns:
            List of PHPClass objects.
        """
        normalizer = self._get_normalizer()
        if normalizer is None:
            return []
        try:
            module = normalizer.normalize(php_code)
        except Exception:  # noqa: BLE001
            return []

        from code_scalpel.ir.nodes import IRClassDef, IRFunctionDef

        classes: List[PHPClass] = []
        for node in module.body:
            if isinstance(node, IRClassDef):
                methods = [b.name for b in node.body if isinstance(b, IRFunctionDef)]
                loc = node.loc
                classes.append(
                    PHPClass(
                        name=node.name,
                        file_path=file_path,
                        line_number=loc.line if loc else None,
                        methods=methods,
                    )
                )
        return classes

    def extract_functions(
        self, php_code: str, file_path: Optional[str] = None
    ) -> List[PHPFunction]:
        """Extract top-level function definitions from PHP source.

        Args:
            php_code: PHP source code.
            file_path: Optional file path for attribution.
        Returns:
            List of PHPFunction objects.
        """
        normalizer = self._get_normalizer()
        if normalizer is None:
            return []
        try:
            module = normalizer.normalize(php_code)
        except Exception:  # noqa: BLE001
            return []

        from code_scalpel.ir.nodes import IRFunctionDef, IRParameter

        funcs: List[PHPFunction] = []
        for node in module.body:
            if isinstance(node, IRFunctionDef):
                params = [
                    p.name for p in node.params if isinstance(p, IRParameter) and p.name
                ]
                loc = node.loc
                funcs.append(
                    PHPFunction(
                        name=node.name,
                        file_path=file_path,
                        line_number=loc.line if loc else None,
                        parameters=params,
                    )
                )
        return funcs

    def build_call_graph(self, php_code: str) -> Dict[str, List[str]]:
        """Build a simple call graph mapping function names to called functions.

        [20260304_FEATURE] Walks IRCall nodes inside each function body.

        Args:
            php_code: PHP source code.
        Returns:
            Dict mapping caller name to list of callee names.
        """
        normalizer = self._get_normalizer()
        if normalizer is None:
            return {}
        try:
            module = normalizer.normalize(php_code)
        except Exception:  # noqa: BLE001
            return {}

        from code_scalpel.ir.nodes import IRCall, IRFunctionDef, IRName

        graph: Dict[str, List[str]] = {}

        def _collect_calls(stmts: list) -> List[str]:
            calls: List[str] = []
            for stmt in stmts:
                if isinstance(stmt, IRCall):
                    if isinstance(stmt.func, IRName):
                        calls.append(stmt.func.id)
                    for child in stmt.args or []:
                        calls.extend(_collect_calls([child]))
                for attr in ("body", "elif_clauses", "orelse", "values"):
                    sub = getattr(stmt, attr, None)
                    if isinstance(sub, list):
                        calls.extend(_collect_calls(sub))
            return calls

        for node in module.body:
            if isinstance(node, IRFunctionDef):
                graph[node.name] = _collect_calls(node.body)

        return graph

    def analyze_structure(self, php_code: str) -> Dict[str, Any]:
        """Return a structure summary dict for the given PHP code.

        Args:
            php_code: PHP source code.
        Returns:
            Summary dict with class/function counts and names.
        """
        classes = self.extract_classes(php_code)
        functions = self.extract_functions(php_code)
        return {
            "class_count": len(classes),
            "function_count": len(functions),
            "classes": [c.name for c in classes],
            "functions": [f.name for f in functions],
        }

    def generate_report(
        self,
        classes: Optional[List[PHPClass]] = None,
        functions: Optional[List[PHPFunction]] = None,
        fmt: str = "json",
    ) -> str:
        """Return JSON or text structure report."""
        cls_list = classes if classes is not None else self.classes
        fn_list = functions if functions is not None else self.functions
        if fmt == "json":
            return json.dumps(
                {
                    "tool": "php-ast",
                    "class_count": len(cls_list),
                    "function_count": len(fn_list),
                    "classes": [
                        {
                            "name": c.name,
                            "line": c.line_number,
                            "methods": c.methods,
                        }
                        for c in cls_list
                    ],
                    "functions": [
                        {
                            "name": f.name,
                            "line": f.line_number,
                            "parameters": f.parameters,
                        }
                        for f in fn_list
                    ],
                },
                indent=2,
            )
        lines = [f"Classes ({len(cls_list)}):"] + [
            f"  {c.name} [{', '.join(c.methods)}]" for c in cls_list
        ]
        lines += [f"Functions ({len(fn_list)}):"] + [
            f"  {f.name}({', '.join(f.parameters)})" for f in fn_list
        ]
        return "\n".join(lines)
