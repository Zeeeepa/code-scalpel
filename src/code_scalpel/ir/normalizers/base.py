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

    TODO ITEMS:

    COMMUNITY TIER (Basic AST/CST Normalization):
    1. TODO: Implement basic statement normalization (assignments, calls, returns)
    2. TODO: Support function and class definition parsing
    3. TODO: Handle control flow statements (if/else, loops, try/catch)
    4. TODO: Normalize binary/unary operations and comparisons
    5. TODO: Support variable declarations and parameter lists
    6. TODO: Create SourceLocation tracking for all nodes
    7. TODO: Implement error reporting with line/column information
    8. TODO: Add basic expression parsing (literals, names, subscripts)
    9. TODO: Support list/dict/set literals
    10. TODO: Create comprehensive test suite for basic normalization

    PRO TIER (Advanced Language Features):
    11. TODO: Add metadata schema for type annotations and generics
    12. TODO: Preserve access modifiers (public/private/protected)
    13. TODO: Extract and normalize documentation/docstrings
    14. TODO: Support decorator metadata across all languages
    15. TODO: Implement IR validation framework with schema checking
    16. TODO: Add consistency checks across polyglot projects
    17. TODO: Support generic type parameters and constraints
    18. TODO: Normalize async/await and generator functions
    19. TODO: Add language-specific semantic metadata
    20. TODO: Create advanced error recovery with suggestions

    ENTERPRISE TIER (Polyglot & Advanced Analysis):
    21. TODO: Implement IR validation with warning on type mismatches
    22. TODO: Add caching interface for normalized subtrees
    23. TODO: Implement memoization of common patterns
    24. TODO: Support cross-language type resolution
    25. TODO: Add distributed normalization for large projects
    26. TODO: Implement ML-based pattern recognition for optimization
    27. TODO: Support encrypted metadata preservation
    28. TODO: Add AI-driven semantic enrichment
    29. TODO: Implement quantum-safe hash signatures for IR
    30. TODO: Create multi-language consistency analyzer
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
