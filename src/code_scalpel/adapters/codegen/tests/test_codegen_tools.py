"""
Tests for Codegen Tools Adapter

[20260216_TEST] Comprehensive test coverage for tools adapter
"""

import pytest
from unittest.mock import Mock, patch


class TestCodegenTools:
    """Test suite for codegen_tools adapter"""

    def test_import_adapter(self):
        """Test that the adapter module can be imported"""
        from code_scalpel.adapters.codegen import codegen_tools
        assert codegen_tools is not None

    def test_all_tools_exist(self):
        """Test that all tool functions exist"""
        from code_scalpel.adapters.codegen.codegen_tools import (
            commit,
            create_file,
            create_pr,
            create_pr_comment,
            create_pr_review_comment,
            delete_file,
            edit_file,
            move_symbol,
            perform_reflection,
            rename_file,
            replacement_edit,
            replacement_edit_global,
            reveal_symbol,
            run_codemod,
            search,
            search_files_by_name,
            semantic_edit,
            semantic_search,
            view_file,
            view_pr,
        )

        tools = [
            commit,
            create_file,
            create_pr,
            create_pr_comment,
            create_pr_review_comment,
            delete_file,
            edit_file,
            move_symbol,
            perform_reflection,
            rename_file,
            replacement_edit,
            replacement_edit_global,
            reveal_symbol,
            run_codemod,
            search,
            search_files_by_name,
            semantic_edit,
            semantic_search,
            view_file,
            view_pr,
        ]

        for tool in tools:
            assert callable(tool), f"{tool.__name__} is not callable"

    @patch("code_scalpel.adapters.codegen.codegen_tools._commit")
    def test_commit_passthrough(self, mock_commit):
        """Test that commit passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_tools import commit

        mock_commit.return_value = {"status": "success"}
        result = commit("test message")

        mock_commit.assert_called_once_with("test message")
        assert result == {"status": "success"}

    @patch("code_scalpel.adapters.codegen.codegen_tools._create_file")
    def test_create_file_passthrough(self, mock_create_file):
        """Test that create_file passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_tools import create_file

        mock_create_file.return_value = {"file": "created"}
        result = create_file("test.py", "content")

        mock_create_file.assert_called_once_with("test.py", "content")
        assert result == {"file": "created"}

    @patch("code_scalpel.adapters.codegen.codegen_tools._search")
    def test_search_passthrough(self, mock_search):
        """Test that search passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_tools import search

        mock_search.return_value = {"results": []}
        result = search("query", path="/src")

        mock_search.assert_called_once_with("query", path="/src")
        assert result == {"results": []}

    @patch("code_scalpel.adapters.codegen.codegen_tools._view_file")
    def test_view_file_passthrough(self, mock_view_file):
        """Test that view_file passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_tools import view_file

        mock_view_file.return_value = {"content": "file content"}
        result = view_file("test.py")

        mock_view_file.assert_called_once_with("test.py")
        assert result == {"content": "file content"}

    @patch("code_scalpel.adapters.codegen.codegen_tools._semantic_edit")
    def test_semantic_edit_passthrough(self, mock_semantic_edit):
        """Test that semantic_edit passes through to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_tools import semantic_edit

        mock_semantic_edit.return_value = {"edited": True}
        result = semantic_edit("file.py", "edit instruction")

        mock_semantic_edit.assert_called_once_with("file.py", "edit instruction")
        assert result == {"edited": True}

    def test_all_tools_have_docstrings(self):
        """Test that all exported tools have docstrings"""
        from code_scalpel.adapters.codegen.codegen_tools import (
            commit,
            create_file,
            create_pr,
            delete_file,
            edit_file,
            move_symbol,
            search,
            view_file,
        )

        tools = [commit, create_file, create_pr, delete_file, edit_file, move_symbol, search, view_file]

        for tool in tools:
            assert tool.__doc__ is not None, f"{tool.__name__} missing docstring"
            assert "Community tier" in tool.__doc__, f"{tool.__name__} missing tier annotation"

    @patch("code_scalpel.adapters.codegen.codegen_tools._move_symbol")
    def test_move_symbol_with_kwargs(self, mock_move_symbol):
        """Test that move_symbol handles keyword arguments correctly"""
        from code_scalpel.adapters.codegen.codegen_tools import move_symbol

        mock_move_symbol.return_value = {"moved": True}
        result = move_symbol(
            source="src.py",
            target="dest.py",
            symbol="MyClass",
            strategy="copy"
        )

        mock_move_symbol.assert_called_once_with(
            source="src.py",
            target="dest.py",
            symbol="MyClass",
            strategy="copy"
        )
        assert result == {"moved": True}

