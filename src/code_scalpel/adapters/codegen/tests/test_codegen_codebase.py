"""
Tests for Codegen Codebase Adapter

[20260216_TEST] Comprehensive test coverage for codebase adapter
"""

import pytest
from unittest.mock import Mock, patch


class TestCodegenCodebase:
    """Test suite for codegen_codebase adapter"""

    def test_import_adapter(self):
        """Test that the adapter module can be imported"""
        from code_scalpel.adapters.codegen import codegen_codebase
        assert codegen_codebase is not None

    def test_codebase_class_exists(self):
        """Test that Codebase class exists"""
        from code_scalpel.adapters.codegen.codegen_codebase import Codebase
        assert Codebase is not None

    def test_codebase_is_class(self):
        """Test that Codebase is a class"""
        from code_scalpel.adapters.codegen.codegen_codebase import Codebase
        assert isinstance(Codebase, type)

    @patch("code_scalpel.adapters.codegen.codegen_codebase._Codebase")
    def test_codebase_passthrough(self, mock_codebase_class):
        """Test that Codebase class is a passthrough to Codegen SDK"""
        from code_scalpel.adapters.codegen.codegen_codebase import Codebase

        # Verify that Codebase is the same as _Codebase
        assert Codebase is mock_codebase_class

    def test_codebase_has_from_repo_method(self):
        """Test that Codebase has from_repo class method"""
        from code_scalpel.adapters.codegen.codegen_codebase import Codebase

        assert hasattr(Codebase, 'from_repo'), "Codebase missing from_repo method"

    def test_codebase_has_from_string_method(self):
        """Test that Codebase has from_string class method"""
        from code_scalpel.adapters.codegen.codegen_codebase import Codebase

        assert hasattr(Codebase, 'from_string'), "Codebase missing from_string method"

    def test_codebase_has_from_files_method(self):
        """Test that Codebase has from_files class method"""
        from code_scalpel.adapters.codegen.codegen_codebase import Codebase

        assert hasattr(Codebase, 'from_files'), "Codebase missing from_files method"

