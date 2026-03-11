"""C++ Parser Adapter - IParser interface wrapping CppNormalizer.

[20260303_FEATURE] Full implementation using CppNormalizer (tree-sitter-cpp).
Replaces the NotImplementedError stub with a real implementation.
"""

from typing import Any, List

from ..interface import IParser, Language, ParseResult


class CppParserAdapter(IParser):
    """
    Adapter wrapping CppNormalizer to implement the IParser interface.

    [20260303_FEATURE] Thin wrapper over CppNormalizer that translates
    between the IParser contract and the IR normalizer output.
    """

    def __init__(self) -> None:
        """Initialize the C++ parser adapter."""
        from code_scalpel.ir.normalizers.cpp_normalizer import CppNormalizer

        self._normalizer = CppNormalizer()

    def parse(self, code: str) -> ParseResult:
        """Parse C++ source code and return a ParseResult with the IR module."""
        ir_module = self._normalizer.normalize(code)
        return ParseResult(
            ast=ir_module,
            errors=[],
            warnings=[],
            metrics={},
            language=Language.CPP,
        )

    def get_functions(self, ast_tree: Any) -> List[str]:
        """Return names of all top-level functions and methods."""
        from code_scalpel.ir.nodes import IRFunctionDef

        return [
            n.name
            for n in getattr(ast_tree, "body", [])
            if isinstance(n, IRFunctionDef)
        ]

    def get_classes(self, ast_tree: Any) -> List[str]:
        """Return names of all struct and class type declarations."""
        from code_scalpel.ir.nodes import IRClassDef

        return [
            n.name for n in getattr(ast_tree, "body", []) if isinstance(n, IRClassDef)
        ]
