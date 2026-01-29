"""Validation engine for code analysis.

This module implements the "Self-Correction" validation layer that provides
fuzzy matching and intelligent error suggestions before expensive analysis.

Key features:
- Pre-execution validation (fail fast)
- Weighted fuzzy matching for symbol/import names
- Scope tracking for locality-aware suggestions
- Shallow scanning to detect typos early
- Smart error messages with "Did you mean?" suggestions
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass
from typing import Optional

from code_scalpel.mcp.models.context import Language, SourceContext
from code_scalpel.mcp.validators.weighted_scorer import (
    WeightedSymbolMatcher,
)

logger = logging.getLogger(__name__)


@dataclass
class ScopedSymbol:
    """A symbol with scope and export information."""

    name: str
    """Symbol name."""

    scope: str
    """Where symbol lives: 'module', class name, or function name."""

    is_exported: bool
    """True if public API (no leading underscore, etc)."""

    symbol_type: str
    """Type of symbol: 'function', 'class', 'import', 'attribute'."""

    line_number: Optional[int] = None
    """Line number in source (useful for sorting)."""

    def __repr__(self) -> str:
        return (
            f"ScopedSymbol({self.name}, type={self.symbol_type}, " f"scope={self.scope}, exported={self.is_exported})"
        )


class ValidationError(ValueError):
    """Raised when validation detects a semantic error."""

    def __init__(self, message: str, suggestions: list[str] | None = None):
        super().__init__(message)
        self.suggestions = suggestions or []


class ScopeTrackingVisitor(ast.NodeVisitor):
    """Tracks parent scope of functions and classes using a stack.

    This visitor walks the AST and records scope information for symbols,
    enabling locality-aware fuzzy matching.
    """

    def __init__(self):
        """Initialize the visitor."""
        self.symbols: list[ScopedSymbol] = []
        """List of extracted symbols with scope information."""

        self.scope_stack: list[str] = ["module"]
        """Stack of scopes: ['module'] initially, pushes/pops as we traverse."""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit a class definition and track it."""
        is_exported = not node.name.startswith("_")
        current_scope = self.scope_stack[-1]

        # Record the class itself
        self.symbols.append(
            ScopedSymbol(
                name=node.name,
                scope=current_scope,
                is_exported=is_exported,
                symbol_type="class",
                line_number=node.lineno,
            )
        )

        # Enter class scope
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition and track it."""
        is_exported = not node.name.startswith("_")
        current_scope = self.scope_stack[-1]

        # Record the function
        self.symbols.append(
            ScopedSymbol(
                name=node.name,
                scope=current_scope,
                is_exported=is_exported,
                symbol_type="function",
                line_number=node.lineno,
            )
        )

        # Enter function scope (for nested functions)
        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition (treat same as FunctionDef)."""
        # Convert to FunctionDef-like for consistent handling
        is_exported = not node.name.startswith("_")
        current_scope = self.scope_stack[-1]

        self.symbols.append(
            ScopedSymbol(
                name=node.name,
                scope=current_scope,
                is_exported=is_exported,
                symbol_type="function",
                line_number=node.lineno,
            )
        )

        self.scope_stack.append(node.name)
        self.generic_visit(node)
        self.scope_stack.pop()


class SymbolExtractor:
    """Shallow scanner to extract symbols from code without full parsing."""

    @staticmethod
    def extract_python_symbols(content: str) -> dict[str, list[ScopedSymbol]]:
        """Extract symbols from Python code with scope and export information.

        Uses the ScopeTrackingVisitor to track parent scopes (module, class, function).
        Falls back to regex if AST parsing fails.

        Args:
            content: Python source code.

        Returns:
            Dict with keys: imports, functions, classes, attributes
            Values: list[ScopedSymbol] with scope and export info.
        """
        symbols_dict: dict[str, list[ScopedSymbol]] = {
            "imports": [],
            "functions": [],
            "classes": [],
            "attributes": [],
        }

        try:
            tree = ast.parse(content)

            # Use the visitor to track scopes
            visitor = ScopeTrackingVisitor()
            visitor.visit(tree)

            # Separate symbols by type
            for symbol in visitor.symbols:
                if symbol.symbol_type == "function":
                    symbols_dict["functions"].append(symbol)
                elif symbol.symbol_type == "class":
                    symbols_dict["classes"].append(symbol)

            # Extract imports (simple iteration)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_name = alias.name.split(".")[0]
                        symbols_dict["imports"].append(
                            ScopedSymbol(
                                name=import_name,
                                scope="module",
                                is_exported=True,  # Imports are always public
                                symbol_type="import",
                                line_number=node.lineno,
                            )
                        )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split(".")[0]
                        symbols_dict["imports"].append(
                            ScopedSymbol(
                                name=module_name,
                                scope="module",
                                is_exported=True,
                                symbol_type="import",
                                line_number=node.lineno,
                            )
                        )

        except SyntaxError:
            # Fallback to regex-based extraction
            logger.warning("Failed to parse Python AST, falling back to regex")
            symbols_dict["imports"] = [
                ScopedSymbol(
                    name=match,
                    scope="module",
                    is_exported=True,
                    symbol_type="import",
                    line_number=None,
                )
                for match in re.findall(r"^(?:from|import)\s+([\w.]+)", content, re.MULTILINE)
            ]
            symbols_dict["functions"] = [
                ScopedSymbol(
                    name=match,
                    scope="module",
                    is_exported=not match.startswith("_"),
                    symbol_type="function",
                    line_number=None,
                )
                for match in re.findall(r"^def\s+(\w+)", content, re.MULTILINE)
            ]
            symbols_dict["classes"] = [
                ScopedSymbol(
                    name=match,
                    scope="module",
                    is_exported=not match.startswith("_"),
                    symbol_type="class",
                    line_number=None,
                )
                for match in re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
            ]

        return symbols_dict

    @staticmethod
    def extract_javascript_symbols(content: str) -> dict[str, list[ScopedSymbol]]:
        """Extract symbols from JavaScript/TypeScript code using regex.

        Note: JavaScript AST parsing is more complex and requires tree-sitter.
        This uses regex as a fallback, returning ScopedSymbol objects.

        Args:
            content: JavaScript/TypeScript source code.

        Returns:
            Dict with keys: imports, functions, classes, attributes
            Values: list[ScopedSymbol]
        """
        symbols_dict: dict[str, list[ScopedSymbol]] = {
            "imports": [],
            "functions": [],
            "classes": [],
            "attributes": [],
        }

        # Extract imports (ES6 and CommonJS)
        for match in re.findall(r"from\s+['\"]([^'\"]+)['\"]", content):
            symbols_dict["imports"].append(
                ScopedSymbol(
                    name=match,
                    scope="module",
                    is_exported=True,
                    symbol_type="import",
                )
            )
        for match in re.findall(r"require\(['\"]([^'\"]+)['\"]\)", content):
            symbols_dict["imports"].append(
                ScopedSymbol(
                    name=match,
                    scope="module",
                    is_exported=True,
                    symbol_type="import",
                )
            )

        # Extract function declarations
        for match in re.findall(r"function\s+(\w+)", content):
            symbols_dict["functions"].append(
                ScopedSymbol(
                    name=match,
                    scope="module",
                    is_exported=not match.startswith("_"),
                    symbol_type="function",
                )
            )
        for match in re.findall(r"const\s+(\w+)\s*=\s*\(", content):
            symbols_dict["functions"].append(
                ScopedSymbol(
                    name=match,
                    scope="module",
                    is_exported=not match.startswith("_"),
                    symbol_type="function",
                )
            )
        for match in re.findall(r"const\s+(\w+)\s*=\s*async\s*\(", content):
            symbols_dict["functions"].append(
                ScopedSymbol(
                    name=match,
                    scope="module",
                    is_exported=not match.startswith("_"),
                    symbol_type="function",
                )
            )

        # Extract class declarations
        for match in re.findall(r"class\s+(\w+)", content):
            symbols_dict["classes"].append(
                ScopedSymbol(
                    name=match,
                    scope="module",
                    is_exported=not match.startswith("_"),
                    symbol_type="class",
                )
            )

        return symbols_dict

    @staticmethod
    def extract_symbols(content: str, language: Language) -> dict[str, list[ScopedSymbol]]:
        """Extract symbols from code in the given language.

        Args:
            content: Source code.
            language: Programming language.

        Returns:
            Dict with symbol categories mapping to lists of ScopedSymbol objects.
        """
        if language == Language.PYTHON:
            return SymbolExtractor.extract_python_symbols(content)
        elif language in (Language.JAVASCRIPT, Language.TYPESCRIPT):
            return SymbolExtractor.extract_javascript_symbols(content)
        else:
            # For unsupported languages, return empty
            return {
                "imports": [],
                "functions": [],
                "classes": [],
                "attributes": [],
            }


class SemanticValidator:
    """Validates code references against actual symbols using weighted scoring.

    This validator uses the WeightedSymbolMatcher to provide intelligent,
    context-aware suggestions when symbols are not found.
    """

    def __init__(self):
        """Initialize the validator with an empty cache."""
        self.symbol_cache: dict[str, dict[str, list[ScopedSymbol]]] = {}

    def validate_symbol_exists(
        self,
        source_context: SourceContext,
        symbol_name: str,
        symbol_type: str = "any",
        request_context_scope: Optional[str] = None,
    ) -> None:
        """Validate that a symbol exists in the source code.

        Uses weighted scoring to provide "Did you mean?" suggestions
        with locality and export boosts.

        Args:
            source_context: Source code context.
            symbol_name: Symbol to look for (e.g., "process_dta").
            symbol_type: Type of symbol ('function', 'class', 'import', 'any').
            request_context_scope: Scope context for boost (e.g., "UserService" class).

        Raises:
            ValidationError: If symbol not found, with suggestions.

        HARD CONSTRAINT: We return suggestions ONLY.
        The Agent MUST self-correct. This forces learning of the API surface.
        """
        # Extract symbols (cached by content hash)
        cache_key: str = source_context.content_hash or ""
        if not cache_key:
            cache_key = str(id(source_context))

        if cache_key not in self.symbol_cache:
            symbols = SymbolExtractor.extract_symbols(source_context.content, source_context.language)
            self.symbol_cache[cache_key] = symbols
        else:
            symbols = self.symbol_cache[cache_key]

        # Determine search space based on symbol_type
        if symbol_type == "any":
            search_space = (
                symbols.get("functions", [])
                + symbols.get("classes", [])
                + symbols.get("imports", [])
                + symbols.get("attributes", [])
            )
        else:
            search_space = symbols.get(symbol_type + "s", [])

        # Check for exact match
        for candidate in search_space:
            if candidate.name == symbol_name:
                return  # Found it, validation passes

        # Fuzzy match with weighted scoring
        scored_candidates = []
        for candidate in search_space:
            scored = WeightedSymbolMatcher.calculate_match_score(
                target_symbol=symbol_name,
                candidate_symbol=candidate.name,
                candidate_scope=candidate.scope,
                candidate_is_exported=candidate.is_exported,
                request_context_scope=request_context_scope,
            )
            scored_candidates.append(scored)

        # Rank and filter by threshold
        suggestions = WeightedSymbolMatcher.rank_candidates(
            scored_candidates,
            threshold=0.6,
            top_k=3,
        )

        # Build error message with suggestions (NO AUTO-FIXING)
        error_msg = f"Symbol '{symbol_name}' not found in " f"{'file' if source_context.file_path else 'memory'}"

        suggestion_names = []
        if suggestions:
            suggestion_names = [s.name for s in suggestions]
            error_msg += f". Did you mean: {', '.join(suggestion_names)}?"

        # Return ValidationError with suggestions for agent self-correction
        raise ValidationError(error_msg, suggestions=suggestion_names)

    def validate_import_exists(
        self,
        source_context: SourceContext,
        import_name: str,
    ) -> None:
        """Validate that an import exists in the code.

        Args:
            source_context: Source code context.
            import_name: Import module name to look for.

        Raises:
            ValidationError: If import not found with suggestions.
        """
        cache_key: str = source_context.content_hash or ""
        if not cache_key:
            cache_key = str(id(source_context))

        if cache_key not in self.symbol_cache:
            symbols = SymbolExtractor.extract_symbols(source_context.content, source_context.language)
            self.symbol_cache[cache_key] = symbols
        else:
            symbols = self.symbol_cache[cache_key]

        imports = symbols.get("imports", [])

        # Check for exact match (handle dotted imports)
        for imp in imports:
            if imp.name == import_name or import_name.startswith(imp.name + "."):
                return  # Found it

        # Fuzzy match with weighted scoring
        scored_candidates = []
        for imp in imports:
            scored = WeightedSymbolMatcher.calculate_match_score(
                target_symbol=import_name,
                candidate_symbol=imp.name,
                candidate_scope=imp.scope,
                candidate_is_exported=imp.is_exported,
            )
            scored_candidates.append(scored)

        # Rank and filter
        suggestions = WeightedSymbolMatcher.rank_candidates(
            scored_candidates,
            threshold=0.6,
            top_k=3,
        )

        error_msg = f"Import '{import_name}' not found in " f"{'file' if source_context.file_path else 'memory'}"
        suggestion_names = []
        if suggestions:
            suggestion_names = [s.name for s in suggestions]
            error_msg += f". Did you mean: {', '.join(suggestion_names)}?"

        raise ValidationError(error_msg, suggestions=suggestion_names)

    def clear_cache(self) -> None:
        """Clear the symbol cache (useful for testing)."""
        self.symbol_cache.clear()


class StructuralValidator:
    """Validates structural properties of code."""

    @staticmethod
    def validate_python_syntax(source_context: SourceContext) -> None:
        """Ensure Python code is syntactically valid.

        Args:
            source_context: Source code context.

        Raises:
            ValidationError: If syntax is invalid.
        """
        if source_context.language != Language.PYTHON:
            return

        try:
            ast.parse(source_context.content)
        except SyntaxError as e:
            raise ValidationError(f"Python syntax error at line {e.lineno}: {e.msg}") from e

    @staticmethod
    def validate_file_size(source_context: SourceContext, max_bytes: int = 10_000_000) -> None:
        """Ensure source file is within size limits.

        Args:
            source_context: Source code context.
            max_bytes: Maximum file size in bytes (default: 10MB).

        Raises:
            ValidationError: If file exceeds limit.
        """
        if source_context.file_size_bytes > max_bytes:
            size_mb = source_context.file_size_bytes / (1024 * 1024)
            max_mb = max_bytes / (1024 * 1024)
            raise ValidationError(f"File size {size_mb:.1f}MB exceeds limit of {max_mb:.1f}MB")


# Global singleton validators
_symbol_validator = SemanticValidator()


def get_symbol_validator() -> SemanticValidator:
    """Get the global symbol validator instance."""
    return _symbol_validator


__all__ = [
    "ValidationError",
    "SymbolExtractor",
    "SemanticValidator",
    "StructuralValidator",
    "get_symbol_validator",
]
