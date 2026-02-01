"""Symbol extractor for generating strict symbol tables.

[20260126_FEATURE] Extract function/class signatures from Python ASTs.

Enables Oracle to build "Strict Symbol Tables" that prevent LLM hallucinations
of non-existent functions, classes, and their signatures.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Optional

from code_scalpel.lib_scalpel.models import (
    ClassSignature,
    FunctionSignature,
    ImportStatement,
    SymbolTable,
)


class SymbolExtractor:
    """Extracts function/class signatures from Python ASTs."""

    def __init__(self):
        """Initialize the extractor."""
        self.current_file = ""
        self.current_language = "python"

    def extract_from_file(self, file_path: str) -> SymbolTable:
        """Extract all symbols from a Python file.

        Args:
            file_path: Path to Python file

        Returns:
            SymbolTable with extracted symbols

        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file has syntax errors
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.suffix not in {".py"}:
            raise ValueError(f"Unsupported file type: {path.suffix}")

        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        return self.extract_from_source(source, file_path, "python")

    def extract_from_source(
        self,
        source: str,
        file_path: str = "<string>",
        language: str = "python",
    ) -> SymbolTable:
        """Extract symbols from source code.

        Args:
            source: Source code as string
            file_path: File path (for context)
            language: Programming language ("python", "typescript", etc.)

        Returns:
            SymbolTable with extracted symbols
        """
        if language != "python":
            raise NotImplementedError(f"Language support coming soon: {language}")

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {file_path}: {e}")

        self.current_file = file_path
        self.current_language = language

        symbol_table = SymbolTable(
            file_path=file_path,
            language=language,
        )

        # Extract top-level symbols
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Only include top-level functions
                if self._is_toplevel(node, tree):
                    symbol_table.functions.append(self._extract_function(node))

            elif isinstance(node, ast.ClassDef):
                # Only include top-level classes
                if self._is_toplevel(node, tree):
                    symbol_table.classes.append(self._extract_class(node))

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                # Extract imports
                if self._is_toplevel(node, tree):
                    symbol_table.imports.extend(self._extract_imports(node))

        return symbol_table

    def _is_toplevel(self, node: ast.stmt, tree: ast.Module) -> bool:
        """Check if a node is top-level in the module.

        Args:
            node: AST node to check
            tree: Module AST

        Returns:
            True if node is top-level
        """
        return node in tree.body

    def _extract_function(self, node: ast.FunctionDef) -> FunctionSignature:
        """Extract function signature from AST node.

        Args:
            node: FunctionDef node

        Returns:
            FunctionSignature
        """
        # Extract parameters
        params = []
        for arg in node.args.args:
            param_info = {"name": arg.arg}
            if arg.annotation:
                param_info["type"] = ast.unparse(arg.annotation)
            params.append(param_info)

        # Extract return type
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        # Extract decorators
        decorators = [ast.unparse(d) for d in node.decorator_list]

        # Extract docstring
        docstring = ast.get_docstring(node)

        # Build signature string
        params_str = ", ".join(
            [
                f"{p['name']}: {p.get('type', '')}" if p.get("type") else p["name"]
                for p in params
            ]
        )
        return_str = f" -> {return_type}" if return_type else ""
        signature = f"def {node.name}({params_str}){return_str}"

        return FunctionSignature(
            name=node.name,
            signature=signature,
            params=params,
            returns=return_type,
            decorators=decorators,
            line=node.lineno,
            docstring=docstring,
        )

    def _extract_class(self, node: ast.ClassDef) -> ClassSignature:
        """Extract class signature from AST node.

        Args:
            node: ClassDef node

        Returns:
            ClassSignature
        """
        # Extract base classes
        bases = [ast.unparse(b) for b in node.bases]

        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(self._extract_function(item))

        # Extract properties (simple heuristic: attributes with type annotations)
        properties = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                properties.append(item.target.id)

        # Extract docstring
        docstring = ast.get_docstring(node)

        return ClassSignature(
            name=node.name,
            bases=bases,
            methods=methods,
            properties=properties,
            line=node.lineno,
            docstring=docstring,
        )

    def _extract_imports(self, node: ast.stmt) -> List[ImportStatement]:
        """Extract import statements.

        Args:
            node: Import or ImportFrom node

        Returns:
            List of ImportStatements
        """
        imports = []

        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    ImportStatement(
                        module=alias.name,
                        symbols=[],
                        alias=alias.asname,
                        line=node.lineno,
                    )
                )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            symbols = []
            for alias in node.names:
                symbols.append(alias.name)

            imports.append(
                ImportStatement(
                    module=module,
                    symbols=symbols,
                    line=node.lineno,
                )
            )

        return imports

    def get_symbol_by_name(
        self,
        symbol_table: SymbolTable,
        name: str,
    ) -> Optional[FunctionSignature | ClassSignature]:
        """Look up a symbol by name in a symbol table.

        Args:
            symbol_table: SymbolTable to search
            name: Symbol name

        Returns:
            FunctionSignature, ClassSignature, or None
        """
        for func in symbol_table.functions:
            if func.name == name:
                return func

        for cls in symbol_table.classes:
            if cls.name == name:
                return cls

        return None
