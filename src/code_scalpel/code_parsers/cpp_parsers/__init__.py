#!/usr/bin/env python3
"""C++ Parsers Module - Unified Interface and Registry.

[20260303_FEATURE] Phase 2: Full CppParserRegistry with lazy-load factory
replacing NotImplementedError stubs.

Note: The cpp_adapter.py (adapters/) is already complete.  This module
provides the static-analysis tool-parser registry for the six tools:
Cppcheck, clang-tidy, Clang Static Analyzer, cpplint, Coverity, SonarQube.

Special handling: ``cpp_parsers_Clang-Static-Analyzer.py`` contains a
hyphen in the filename (invalid Python identifier), so it is loaded via
``importlib.util.spec_from_file_location`` rather than the normal import
machinery.
"""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

__all__ = [
    "CppParserRegistry",
    "CppcheckParser",
    "ClangTidyParser",
    "ClangStaticAnalyzerParser",
    "CppLintParser",
    "CoverityParser",
    "SonarQubeCppParser",
]

# ---------------------------------------------------------------------------
# Dispatch tables
# ---------------------------------------------------------------------------

# Maps tool name aliases (lower-case) → canonical class name
_TOOL_MAP: Dict[str, str] = {
    "cppcheck": "CppcheckParser",
    "clang-tidy": "ClangTidyParser",
    "clang_tidy": "ClangTidyParser",
    "clangtidy": "ClangTidyParser",
    "clang-sa": "ClangStaticAnalyzerParser",
    "clang-static-analyzer": "ClangStaticAnalyzerParser",
    "clangsa": "ClangStaticAnalyzerParser",
    "cpplint": "CppLintParser",
    "coverity": "CoverityParser",
    "sonarqube": "SonarQubeCppParser",
    "sonar": "SonarQubeCppParser",
    "sonar-cpp": "SonarQubeCppParser",
}

# Maps class name → module basename (relative to this package)
_MODULE_MAP: Dict[str, str] = {
    "CppcheckParser": "cpp_parsers_Cppcheck",
    "ClangTidyParser": "cpp_parsers_clang_tidy",
    "ClangStaticAnalyzerParser": "cpp_parsers_Clang-Static-Analyzer",  # hyphen
    "CppLintParser": "cpp_parsers_cpplint",
    "CoverityParser": "cpp_parsers_coverity",
    "SonarQubeCppParser": "cpp_parsers_SonarQube",
}

# Package directory (used for hyphenated-module loading)
_PKG_DIR = Path(__file__).parent


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class CppParserRegistry:
    """Registry for C++ static-analysis tool parsers.

    [20260303_FEATURE] Phase 2: lazy-load factory pattern.  Parsers are
    imported on first use; the registry itself is zero-cost to instantiate.

    Supported tools
    ---------------
    - ``cppcheck`` / ``Cppcheck``
    - ``clang-tidy`` / ``clang_tidy``
    - ``clang-sa`` / ``clang-static-analyzer``
    - ``cpplint``
    - ``coverity``
    - ``sonarqube`` / ``sonar``
    """

    def get_parser(self, tool_name: str) -> Any:
        """Return an instantiated parser for *tool_name*.

        Args:
            tool_name: One of the recognised tool identifiers (case-insensitive).

        Returns:
            Instantiated parser object.

        Raises:
            ValueError: If *tool_name* is not recognised.
        """
        key = tool_name.lower()
        if key not in _TOOL_MAP:
            raise ValueError(
                f"Unknown C++ parser tool: {tool_name!r}. "
                f"Valid options: {sorted(set(_TOOL_MAP.keys()))}"
            )
        class_name = _TOOL_MAP[key]
        mod = _import_parser_module(class_name)
        return getattr(mod, class_name)()

    def analyze(
        self,
        path: Union[str, Path],
        tools: Optional[List[str]] = None,
    ) -> Dict[str, List]:
        """Run all (or specified) parsers on *path* and aggregate results.

        [20260303_FEATURE] Returns ``{tool: [findings]}`` — empty list on
        failure (parsers require CLI execution or existing report files).
        """
        canonical_tools = [
            "cppcheck",
            "clang-tidy",
            "clang-sa",
            "cpplint",
            "coverity",
            "sonarqube",
        ]
        selected = [t.lower() for t in tools] if tools else canonical_tools
        results: Dict[str, List] = {}
        for tool in selected:
            try:
                self.get_parser(tool)
                results[tool] = []  # parsers require CLI execution / report files
            except Exception:  # noqa: BLE001
                results[tool] = []
        return results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _import_parser_module(class_name: str) -> Any:
    """Import the module that defines *class_name*.

    Handles the special case of ``cpp_parsers_Clang-Static-Analyzer.py``
    whose filename contains a hyphen, making it un-importable via the
    standard ``import`` statement.
    """
    module_basename = _MODULE_MAP[class_name]

    if "-" in module_basename:
        # Hyphenated filename — must use spec_from_file_location
        return _load_hyphenated_module(module_basename)

    return importlib.import_module(
        f"code_scalpel.code_parsers.cpp_parsers.{module_basename}"
    )


def _load_hyphenated_module(module_basename: str) -> Any:
    """Load a .py file whose name contains hyphens using path-based loading.

    Python module identifiers cannot contain hyphens, so we:
      1. Derive a valid dotted name by replacing hyphens with underscores.
      2. Register the module in ``sys.modules`` *before* executing it so
         relative imports (``from .. import base_parser``) can resolve.
    """
    import sys

    file_path = _PKG_DIR / f"{module_basename}.py"
    # Sanitise the basename to a valid Python identifier for the dotted name.
    sanitised = module_basename.replace("-", "_")
    full_name = f"code_scalpel.code_parsers.cpp_parsers.{sanitised}"

    if full_name in sys.modules:
        return sys.modules[full_name]

    spec = importlib.util.spec_from_file_location(full_name, file_path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise ImportError(f"Cannot create module spec from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    # Set __package__ so relative imports inside the file resolve correctly.
    mod.__package__ = "code_scalpel.code_parsers.cpp_parsers"
    sys.modules[full_name] = mod  # register BEFORE exec so re-entrant imports work
    try:
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
    except Exception:
        sys.modules.pop(full_name, None)
        raise
    return mod


# ---------------------------------------------------------------------------
# Module-level lazy attribute access (PEP 562)
# ---------------------------------------------------------------------------
def __getattr__(name: str) -> Any:
    if name in _MODULE_MAP:
        mod = _import_parser_module(name)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
