"""
Base Normalizer - Abstract interface for language-specific normalizers.

A normalizer converts a language's native AST/CST into Unified IR.
All normalizers must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Union

from ..nodes import IRModule, IRNode


class BaseNormalizer(ABC):
    """
    Abstract base class for language-specific normalizers.

    A normalizer:
    1. Parses source code using the language's native parser
    2. Converts the native AST/CST to Unified IR
    3. Sets source_language on all nodes for semantic dispatch

    Example:
        >>> normalizer = PythonNormalizer()
        >>> ir = normalizer.normalize("x = 1 + 2")
        >>> ir.source_language
        'python'

    # TODO COMMUNITY TIER: Implement basic statement normalization (assignments, calls, returns)
    # TODO COMMUNITY TIER: Support function and class definition parsing
    # TODO COMMUNITY TIER: Handle control flow statements (if/else, loops, try/catch)
    # TODO COMMUNITY TIER: Normalize binary/unary operations and comparisons
    # TODO COMMUNITY TIER: Support variable declarations and parameter lists
    # TODO COMMUNITY TIER: Create SourceLocation tracking for all nodes
    # TODO COMMUNITY TIER: Implement error reporting with line/column information
    # TODO COMMUNITY TIER: Add basic expression parsing (literals, names, subscripts)
    # TODO COMMUNITY TIER: Support list/dict/set literals
    # TODO COMMUNITY TIER: Create comprehensive test suite for basic normalization

    # TODO PRO TIER: Add metadata schema for type annotations and generics
    # TODO PRO TIER: Preserve access modifiers (public/private/protected)
    # TODO PRO TIER: Extract and normalize documentation/docstrings
    # TODO PRO TIER: Support decorator metadata across all languages
    # TODO PRO TIER: Implement IR validation framework with schema checking
    # TODO PRO TIER: Add consistency checks across polyglot projects
    # TODO PRO TIER: Support generic type parameters and constraints
    # TODO PRO TIER: Normalize async/await and generator functions
    # TODO PRO TIER: Add language-specific semantic metadata
    # TODO PRO TIER: Create advanced error recovery with suggestions

    # TODO ENTERPRISE TIER: Implement IR validation with warning on type mismatches
    # TODO ENTERPRISE TIER: Add caching interface for normalized subtrees
    # TODO ENTERPRISE TIER: Implement memoization of common patterns
    # TODO ENTERPRISE TIER: Support cross-language type resolution
    # TODO ENTERPRISE TIER: Add distributed normalization for large projects
    # TODO ENTERPRISE TIER: Implement ML-based pattern recognition for optimization
    # TODO ENTERPRISE TIER: Support encrypted metadata preservation
    # TODO ENTERPRISE TIER: Add AI-driven semantic enrichment
    # TODO ENTERPRISE TIER: Implement quantum-safe hash signatures for IR
    # TODO ENTERPRISE TIER: Create multi-language consistency analyzer
    """

    @property
    @abstractmethod
    def language(self) -> str:
        """
        Return the language name.

        This value is set on all IR nodes' source_language field.

        Returns:
            Language identifier (e.g., "python", "javascript")
        """
        pass

    @abstractmethod
    def normalize(self, source: str, filename: str = "<string>") -> IRModule:
        """
        Parse source code and normalize to Unified IR.

        Args:
            source: Source code string
            filename: Optional filename for error messages

        Returns:
            IRModule representing the normalized program

        Raises:
            SyntaxError: If source cannot be parsed
        """
        pass

    @abstractmethod
    def normalize_node(self, node: Any) -> Union[IRNode, List[IRNode], None]:
        """
        Normalize a single native AST/CST node to IR.

        This method dispatches based on node type to specific handlers.

        Args:
            node: Native AST/CST node from the language parser

        Returns:
            IRNode: Single normalized node
            List[IRNode]: Multiple nodes (e.g., multiple statements)
            None: Node should be skipped (comments, whitespace)

        Raises:
            NotImplementedError: If node type is not supported
        """
        pass

    def _set_language(self, node: IRNode) -> IRNode:
        """
        Set source_language on a node.

        Helper method for subclasses.
        """
        node.source_language = self.language
        return node
