"""Kotlin Parser Adapter - IParser interface for Kotlin parser.

[20260303_FEATURE] Full implementation using KotlinNormalizer (tree-sitter-kotlin).
"""

from typing import Any, List

from ..interface import IParser, ParseResult


class KotlinParserAdapter(IParser):
    """Adapter wrapping KotlinNormalizer to implement IParser."""

    def __init__(self) -> None:
        from code_scalpel.ir.normalizers.kotlin_normalizer import KotlinNormalizer

        self._normalizer = KotlinNormalizer()

    def parse(self, code: str) -> ParseResult:
        """Parse Kotlin source code and return a ParseResult with IR module."""
        from ..interface import Language as IParserLanguage

        ir_module = self._normalizer.normalize(code)
        return ParseResult(
            ast=ir_module,
            errors=[],
            warnings=[],
            metrics={},
            language=IParserLanguage.KOTLIN,
        )

    def get_functions(self, ast_tree: Any) -> List[str]:
        """Return names of all top-level functions and extension functions."""
        from code_scalpel.ir.nodes import IRFunctionDef

        return [
            n.name
            for n in getattr(ast_tree, "body", [])
            if isinstance(n, IRFunctionDef)
        ]

    def get_classes(self, ast_tree: Any) -> List[str]:
        """Return names of all class, object, and interface declarations."""
        from code_scalpel.ir.nodes import IRClassDef

        return [
            n.name for n in getattr(ast_tree, "body", []) if isinstance(n, IRClassDef)
        ]
