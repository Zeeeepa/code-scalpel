from typing import Dict, Type
from .base_parser import BaseParser
from .python_parser import PythonParser


# [20251221_DEPRECATION] DEPRECATED - Use code_scalpel.code_parser.ParserFactory
# This is a legacy factory with minimal language support (Python only).
# The new factory in code_parser/ provides:
# - 8+ language support (Java, JavaScript, TypeScript, C++, C#, Go, Kotlin, PHP, Ruby, Swift)
# - Language enum for type safety
# - Language auto-detection from file extension
# - 40+ parser implementations across all languages
class ParserFactory:
    """
    Factory for creating language-specific parsers.
    """

    _parsers: Dict[str, Type[BaseParser]] = {
        "python": PythonParser,
        "py": PythonParser,
    }

    @classmethod
    def get_parser(cls, language: str) -> BaseParser:
        """
        Get a parser instance for the specified language.

        Args:
            language: Language identifier (e.g., 'python', 'js')

        Returns:
            Instance of a BaseParser subclass

        Raises:
            ValueError: If language is not supported
        """
        normalized_lang = language.lower()
        parser_cls = cls._parsers.get(normalized_lang)

        if not parser_cls:
            raise ValueError(f"Unsupported language: {language}")

        return parser_cls()

    @classmethod
    def register_parser(cls, language: str, parser_cls: Type[BaseParser]):
        """Register a new parser."""
        cls._parsers[language.lower()] = parser_cls
