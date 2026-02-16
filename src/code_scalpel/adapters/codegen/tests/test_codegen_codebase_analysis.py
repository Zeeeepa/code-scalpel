"""
Tests for Codegen Codebase Analysis Adapter

[20260216_TEST] Comprehensive test coverage for codebase analysis adapter
"""

import pytest
from unittest.mock import Mock, patch


class TestCodegenCodebaseAnalysis:
    """Test suite for codegen_codebase_analysis adapter"""

    def test_import_adapter(self):
        """Test that the adapter module can be imported"""
        from code_scalpel.adapters.codegen import codegen_codebase_analysis
        assert codegen_codebase_analysis is not None

    def test_get_codebase_summary_exists(self):
        """Test that get_codebase_summary function exists"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_codebase_summary,
        )
        assert callable(get_codebase_summary)

    def test_get_file_summary_exists(self):
        """Test that get_file_summary function exists"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_file_summary,
        )
        assert callable(get_file_summary)

    def test_get_class_summary_exists(self):
        """Test that get_class_summary function exists"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_class_summary,
        )
        assert callable(get_class_summary)

    def test_get_function_summary_exists(self):
        """Test that get_function_summary function exists"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_function_summary,
        )
        assert callable(get_function_summary)

    def test_get_symbol_summary_exists(self):
        """Test that get_symbol_summary function exists"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_symbol_summary,
        )
        assert callable(get_symbol_summary)

    @patch("code_scalpel.adapters.codegen.codegen_codebase_analysis._get_codebase_summary")
    def test_get_codebase_summary_passthrough(self, mock_get_codebase_summary):
        """Test that get_codebase_summary passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_codebase_summary,
        )

        mock_get_codebase_summary.return_value = {"summary": "test"}
        result = get_codebase_summary("test_arg", key="value")

        mock_get_codebase_summary.assert_called_once_with("test_arg", key="value")
        assert result == {"summary": "test"}

    @patch("code_scalpel.adapters.codegen.codegen_codebase_analysis._get_file_summary")
    def test_get_file_summary_passthrough(self, mock_get_file_summary):
        """Test that get_file_summary passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_file_summary,
        )

        mock_get_file_summary.return_value = {"file": "summary"}
        result = get_file_summary("file.py")

        mock_get_file_summary.assert_called_once_with("file.py")
        assert result == {"file": "summary"}

    @patch("code_scalpel.adapters.codegen.codegen_codebase_analysis._get_class_summary")
    def test_get_class_summary_passthrough(self, mock_get_class_summary):
        """Test that get_class_summary passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_class_summary,
        )

        mock_get_class_summary.return_value = {"class": "summary"}
        result = get_class_summary("MyClass")

        mock_get_class_summary.assert_called_once_with("MyClass")
        assert result == {"class": "summary"}

    @patch("code_scalpel.adapters.codegen.codegen_codebase_analysis._get_function_summary")
    def test_get_function_summary_passthrough(self, mock_get_function_summary):
        """Test that get_function_summary passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_function_summary,
        )

        mock_get_function_summary.return_value = {"function": "summary"}
        result = get_function_summary("my_function")

        mock_get_function_summary.assert_called_once_with("my_function")
        assert result == {"function": "summary"}

    @patch("code_scalpel.adapters.codegen.codegen_codebase_analysis._get_symbol_summary")
    def test_get_symbol_summary_passthrough(self, mock_get_symbol_summary):
        """Test that get_symbol_summary passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_symbol_summary,
        )

        mock_get_symbol_summary.return_value = {"symbol": "summary"}
        result = get_symbol_summary("my_symbol")

        mock_get_symbol_summary.assert_called_once_with("my_symbol")
        assert result == {"symbol": "summary"}

    def test_all_functions_have_docstrings(self):
        """Test that all exported functions have docstrings"""
        from code_scalpel.adapters.codegen.codegen_codebase_analysis import (
            get_codebase_summary,
            get_file_summary,
            get_class_summary,
            get_function_summary,
            get_symbol_summary,
        )

        functions = [
            get_codebase_summary,
            get_file_summary,
            get_class_summary,
            get_function_summary,
            get_symbol_summary,
        ]

        for func in functions:
            assert func.__doc__ is not None, f"{func.__name__} missing docstring"
            assert "Community tier" in func.__doc__, f"{func.__name__} missing tier annotation"

