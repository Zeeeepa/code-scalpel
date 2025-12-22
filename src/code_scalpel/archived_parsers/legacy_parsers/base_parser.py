from abc import ABC, abstractmethod
from typing import Any, List


# [20251221_DEPRECATION] DEPRECATED - Use code_scalpel.code_parser.BaseParser
# This is a legacy minimal base class kept for backward compatibility.
# The new BaseParser in code_parser/ provides more features:
# - ParseResult dataclass with errors, warnings, metrics
# - PreprocessorConfig for code normalization
# - Language enum for type safety
class BaseParser(ABC):
    """
    Abstract base class for language-specific parsers.
    """

    @abstractmethod
    def parse(self, code: str) -> Any:
        """
        Parse source code into an AST.

        Args:
            code: Source code string

        Returns:
            AST object (type depends on language)
        """
        pass

    @abstractmethod
    def get_functions(self, ast_tree: Any) -> List[str]:
        """Get list of function names from AST."""
        pass

    @abstractmethod
    def get_classes(self, ast_tree: Any) -> List[str]:
        """Get list of class names from AST."""
        pass

    @abstractmethod
    def get_imports(self, ast_tree: Any) -> List[str]:
        """Get list of imported modules."""
        pass
