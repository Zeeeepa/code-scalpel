"""Tests for symbol_extractor module."""

from __future__ import annotations

import pytest
from pathlib import Path

from code_scalpel.oracle.symbol_extractor import SymbolExtractor


class TestSymbolExtractor:
    """Test symbol extraction from Python code."""

    def test_extract_from_source_functions(self):
        """Test extracting functions from source code."""
        source = """
def hello() -> str:
    '''Say hello.'''
    return "hello"

def add(a: int, b: int) -> int:
    '''Add two numbers.'''
    return a + b
"""
        extractor = SymbolExtractor()
        table = extractor.extract_from_source(source, "test.py", "python")

        assert len(table.functions) == 2
        assert table.functions[0].name == "hello"
        assert table.functions[0].returns == "str"
        assert table.functions[1].name == "add"
        assert len(table.functions[1].params) == 2

    def test_extract_from_source_classes(self):
        """Test extracting classes from source code."""
        source = """
class User:
    '''User class.'''
    def __init__(self, name: str):
        self.name = name
    
    def greet(self) -> str:
        return f"Hello {self.name}"

class Admin(User):
    pass
"""
        extractor = SymbolExtractor()
        table = extractor.extract_from_source(source, "test.py", "python")

        assert len(table.classes) == 2
        assert table.classes[0].name == "User"
        assert len(table.classes[0].methods) == 2
        assert table.classes[1].name == "Admin"
        assert table.classes[1].bases == ["User"]

    def test_extract_from_source_imports(self):
        """Test extracting imports from source code."""
        source = """
import os
from typing import Optional, List
from pathlib import Path
"""
        extractor = SymbolExtractor()
        table = extractor.extract_from_source(source, "test.py", "python")

        assert len(table.imports) == 3
        assert table.imports[0].module == "os"
        assert table.imports[1].module == "typing"
        assert set(table.imports[1].symbols) == {"Optional", "List"}

    def test_extract_from_file(self, sample_auth_file: Path):
        """Test extracting from an actual file."""
        extractor = SymbolExtractor()
        table = extractor.extract_from_file(str(sample_auth_file))

        assert table.file_path == str(sample_auth_file)
        assert table.language == "python"
        assert any(c.name == "User" for c in table.classes)
        assert any(f.name == "validate_email" for f in table.functions)

    def test_extract_with_decorators(self):
        """Test extracting functions with decorators."""
        source = """
@property
def name(self) -> str:
    return self._name

@staticmethod
def version() -> str:
    return "1.0"
"""
        extractor = SymbolExtractor()
        table = extractor.extract_from_source(source, "test.py", "python")

        assert len(table.functions) == 2
        assert "property" in table.functions[0].decorators
        assert "staticmethod" in table.functions[1].decorators

    def test_extract_nonexistent_file(self):
        """Test error handling for missing files."""
        extractor = SymbolExtractor()
        with pytest.raises(FileNotFoundError):
            extractor.extract_from_file("/nonexistent/file.py")

    def test_extract_syntax_error(self):
        """Test error handling for syntax errors."""
        source = "def broken( : pass"
        extractor = SymbolExtractor()
        with pytest.raises(SyntaxError):
            extractor.extract_from_source(source, "test.py", "python")

    def test_unsupported_language(self):
        """Test error handling for unsupported languages."""
        extractor = SymbolExtractor()
        with pytest.raises(NotImplementedError):
            extractor.extract_from_source("code", "test.js", "javascript")

    def test_get_symbol_by_name(self):
        """Test looking up symbols by name."""
        source = """
def hello():
    pass

class User:
    pass
"""
        extractor = SymbolExtractor()
        table = extractor.extract_from_source(source, "test.py", "python")

        func = extractor.get_symbol_by_name(table, "hello")
        assert func is not None
        assert func.name == "hello"

        cls = extractor.get_symbol_by_name(table, "User")
        assert cls is not None
        assert cls.name == "User"

        missing = extractor.get_symbol_by_name(table, "NotFound")
        assert missing is None
