"""C# Parser Adapter - IParser interface wrapping CSharpNormalizer.

[20260224_FEATURE] Full C# parsing support via tree-sitter-c-sharp.

This adapter wraps CSharpNormalizer so the language-agnostic IParser
interface can be used by the rest of the code_parsers infrastructure.
"""

from typing import Any, List

from ..interface import IParser, ParseResult


class CSharpParserAdapter(IParser):
    """
    Adapter for C# parsing backed by CSharpNormalizer (tree-sitter-c-sharp).

    [20260224_FEATURE] Production-ready C# parser integration.

    Supports:
        - .cs file extension
        - Class, struct, interface, record, enum extraction
        - Method and constructor extraction
        - Namespace transparency
        - Generic type parameters
        - Using directives, field declarations
        - Control-flow: if / while / for / foreach / switch / try
    """

    def __init__(self) -> None:
        """Initialize the C# parser adapter using CSharpNormalizer."""
        from code_scalpel.ir.normalizers.csharp_normalizer import CSharpNormalizer

        self._normalizer = CSharpNormalizer()
        self._cached_module: Any = None
        self._cached_code: str = ""

    def parse(self, code: str) -> ParseResult:
        """Parse C# source code and return a ParseResult wrapping the IR module."""
        from code_scalpel.code_parsers.interface import Language as IFaceLanguage

        ir_module = self._normalizer.normalize(code)
        self._cached_module = ir_module
        self._cached_code = code
        return ParseResult(
            ast=ir_module,
            language=IFaceLanguage.CSHARP,  # [20260225_BUGFIX] was UNKNOWN; enum now has CSHARP
            errors=[],
            warnings=[],
            metrics={},
        )

    def get_functions(self, ast_tree: Any) -> List[str]:
        """Return method/function names from a parsed IR module."""
        from code_scalpel.ir.nodes import IRClassDef, IRFunctionDef, IRModule

        names: List[str] = []
        if not isinstance(ast_tree, IRModule):
            return names

        def _walk(nodes: Any) -> None:
            for node in nodes:
                if isinstance(node, IRFunctionDef):
                    if not node._metadata.get("is_property"):
                        names.append(node.name)
                    # Also recurse into function body for nested functions
                    _walk(node.body)
                elif isinstance(node, IRClassDef):
                    _walk(node.body)

        _walk(ast_tree.body)
        return names

    def get_classes(self, ast_tree: Any) -> List[str]:
        """Return class/struct/interface/record/enum names from a parsed IR module."""
        from code_scalpel.ir.nodes import IRClassDef, IRModule

        names: List[str] = []
        if not isinstance(ast_tree, IRModule):
            return names

        def _walk(nodes: Any) -> None:
            for node in nodes:
                if isinstance(node, IRClassDef):
                    names.append(node.name)
                    _walk(node.body)

        _walk(ast_tree.body)
        return names
