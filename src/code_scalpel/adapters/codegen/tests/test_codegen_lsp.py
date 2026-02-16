"""
Tests for Codegen LSP Adapter

[20260216_TEST] Comprehensive test coverage for LSP adapter
"""

import pytest
from unittest.mock import Mock, patch


class TestCodegenLSP:
    """Test suite for codegen_lsp adapter"""

    def test_import_adapter(self):
        """Test that the adapter module can be imported"""
        from code_scalpel.adapters.codegen import codegen_lsp
        assert codegen_lsp is not None

    def test_all_lsp_modules_exist(self):
        """Test that all LSP modules are re-exported"""
        from code_scalpel.adapters.codegen.codegen_lsp import (
            completion,
            definition,
            document_symbol,
            execute,
            io,
            kind,
            lsp,
            progress,
            protocol,
            range,
            server,
            utils,
        )

        modules = [
            completion,
            definition,
            document_symbol,
            execute,
            io,
            kind,
            lsp,
            progress,
            protocol,
            range,
            server,
            utils,
        ]

        for module in modules:
            assert module is not None, f"Module {module} is None"

    def test_all_exports_in_all_list(self):
        """Test that __all__ contains all expected exports"""
        from code_scalpel.adapters.codegen import codegen_lsp

        expected_exports = [
            'completion',
            'definition',
            'document_symbol',
            'execute',
            'io',
            'kind',
            'lsp',
            'progress',
            'protocol',
            'range',
            'server',
            'utils',
        ]

        assert hasattr(codegen_lsp, '__all__')
        assert set(codegen_lsp.__all__) == set(expected_exports)

    def test_server_module_accessible(self):
        """Test that server module is accessible and has expected attributes"""
        from code_scalpel.adapters.codegen.codegen_lsp import server

        # Server module should have start_io method (from the example)
        assert hasattr(server, 'start_io'), "server module missing start_io method"

    def test_protocol_module_accessible(self):
        """Test that protocol module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import protocol

        assert protocol is not None

    def test_document_symbol_module_accessible(self):
        """Test that document_symbol module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import document_symbol

        assert document_symbol is not None

    def test_lsp_module_accessible(self):
        """Test that lsp module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import lsp

        assert lsp is not None

    def test_utils_module_accessible(self):
        """Test that utils module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import utils

        assert utils is not None

    def test_io_module_accessible(self):
        """Test that io module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import io

        assert io is not None

    def test_range_module_accessible(self):
        """Test that range module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import range

        assert range is not None

    def test_kind_module_accessible(self):
        """Test that kind module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import kind

        assert kind is not None

    def test_progress_module_accessible(self):
        """Test that progress module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import progress

        assert progress is not None

    def test_execute_module_accessible(self):
        """Test that execute module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import execute

        assert execute is not None

    def test_completion_module_accessible(self):
        """Test that completion module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import completion

        assert completion is not None

    def test_definition_module_accessible(self):
        """Test that definition module is accessible"""
        from code_scalpel.adapters.codegen.codegen_lsp import definition

        assert definition is not None

