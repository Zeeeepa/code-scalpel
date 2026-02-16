"""
Tests for Codegen MCP Adapter

[20260216_TEST] Comprehensive test coverage for MCP adapter
"""

import pytest
from unittest.mock import Mock, patch


class TestCodegenMCP:
    """Test suite for codegen_mcp adapter"""

    def test_import_adapter(self):
        """Test that the adapter module can be imported"""
        from code_scalpel.adapters.codegen import codegen_mcp
        assert codegen_mcp is not None

    def test_query_codebase_exists(self):
        """Test that query_codebase function exists"""
        from code_scalpel.adapters.codegen.codegen_mcp import query_codebase
        assert callable(query_codebase)

    def test_split_files_by_function_exists(self):
        """Test that split_files_by_function function exists"""
        from code_scalpel.adapters.codegen.codegen_mcp import split_files_by_function
        assert callable(split_files_by_function)

    def test_reveal_symbol_tool_exists(self):
        """Test that reveal_symbol_tool function exists"""
        from code_scalpel.adapters.codegen.codegen_mcp import reveal_symbol_tool
        assert callable(reveal_symbol_tool)

    def test_search_codebase_tool_exists(self):
        """Test that search_codebase_tool function exists"""
        from code_scalpel.adapters.codegen.codegen_mcp import search_codebase_tool
        assert callable(search_codebase_tool)

    def test_get_docs_exists(self):
        """Test that get_docs function exists"""
        from code_scalpel.adapters.codegen.codegen_mcp import get_docs
        assert callable(get_docs)

    def test_get_setup_instructions_exists(self):
        """Test that get_setup_instructions function exists"""
        from code_scalpel.adapters.codegen.codegen_mcp import get_setup_instructions
        assert callable(get_setup_instructions)

    def test_get_service_config_exists(self):
        """Test that get_service_config function exists"""
        from code_scalpel.adapters.codegen.codegen_mcp import get_service_config
        assert callable(get_service_config)

    def test_ask_codegen_sdk_exists(self):
        """Test that ask_codegen_sdk function exists"""
        from code_scalpel.adapters.codegen.codegen_mcp import ask_codegen_sdk
        assert callable(ask_codegen_sdk)

    def test_generate_codemod_exists(self):
        """Test that generate_codemod function exists"""
        from code_scalpel.adapters.codegen.codegen_mcp import generate_codemod
        assert callable(generate_codemod)

    def test_improve_codemod_exists(self):
        """Test that improve_codemod function exists"""
        from code_scalpel.adapters.codegen.codegen_mcp import improve_codemod
        assert callable(improve_codemod)

    @patch("code_scalpel.adapters.codegen.codegen_mcp._query_codebase")
    def test_query_codebase_passthrough(self, mock_query_codebase):
        """Test that query_codebase passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_mcp import query_codebase

        mock_query_codebase.return_value = {"results": []}
        result = query_codebase("test query")

        mock_query_codebase.assert_called_once_with("test query")
        assert result == {"results": []}

    @patch("code_scalpel.adapters.codegen.codegen_mcp._split_files_by_function")
    def test_split_files_by_function_passthrough(self, mock_split):
        """Test that split_files_by_function passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_mcp import split_files_by_function

        mock_split.return_value = {"files": []}
        result = split_files_by_function("file.py")

        mock_split.assert_called_once_with("file.py")
        assert result == {"files": []}

    @patch("code_scalpel.adapters.codegen.codegen_mcp._reveal_symbol_tool")
    def test_reveal_symbol_tool_passthrough(self, mock_reveal):
        """Test that reveal_symbol_tool passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_mcp import reveal_symbol_tool

        mock_reveal.return_value = {"symbol": "info"}
        result = reveal_symbol_tool("MyClass")

        mock_reveal.assert_called_once_with("MyClass")
        assert result == {"symbol": "info"}

    @patch("code_scalpel.adapters.codegen.codegen_mcp._search_codebase_tool")
    def test_search_codebase_tool_passthrough(self, mock_search):
        """Test that search_codebase_tool passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_mcp import search_codebase_tool

        mock_search.return_value = {"results": []}
        result = search_codebase_tool("query")

        mock_search.assert_called_once_with("query")
        assert result == {"results": []}

    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have docstrings"""
        from code_scalpel.adapters.codegen.codegen_mcp import (
            query_codebase,
            split_files_by_function,
            reveal_symbol_tool,
            search_codebase_tool,
            get_docs,
            ask_codegen_sdk,
        )

        functions = [
            query_codebase,
            split_files_by_function,
            reveal_symbol_tool,
            search_codebase_tool,
            get_docs,
            ask_codegen_sdk,
        ]

        for func in functions:
            assert func.__doc__ is not None, f"{func.__name__} missing docstring"
            assert "Community tier" in func.__doc__, f"{func.__name__} missing tier annotation"

