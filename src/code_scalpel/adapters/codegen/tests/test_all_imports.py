"""
Comprehensive Import Tests for All Codegen Adapters

[20260216_TEST] Validates that all adapter modules can be imported successfully
"""

import pytest


class TestAllAdapterImports:
    """Test suite to validate all adapter imports"""

    def test_import_codegen_codebase_analysis(self):
        """Test import of codegen_codebase_analysis adapter"""
        from code_scalpel.adapters.codegen import codegen_codebase_analysis
        assert codegen_codebase_analysis is not None

    def test_import_codegen_tools(self):
        """Test import of codegen_tools adapter"""
        from code_scalpel.adapters.codegen import codegen_tools
        assert codegen_tools is not None

    def test_import_codegen_mcp(self):
        """Test import of codegen_mcp adapter"""
        from code_scalpel.adapters.codegen import codegen_mcp
        assert codegen_mcp is not None

    def test_import_codegen_graph(self):
        """Test import of codegen_graph adapter"""
        from code_scalpel.adapters.codegen import codegen_graph
        assert codegen_graph is not None

    def test_import_codegen_index(self):
        """Test import of codegen_index adapter"""
        from code_scalpel.adapters.codegen import codegen_index
        assert codegen_index is not None

    def test_import_codegen_lsp(self):
        """Test import of codegen_lsp adapter"""
        from code_scalpel.adapters.codegen import codegen_lsp
        assert codegen_lsp is not None

    def test_import_codegen_codebase(self):
        """Test import of codegen_codebase adapter"""
        from code_scalpel.adapters.codegen import codegen_codebase
        assert codegen_codebase is not None

    def test_import_codegen_parser(self):
        """Test import of codegen_parser adapter"""
        from code_scalpel.adapters.codegen import codegen_parser
        assert codegen_parser is not None

    def test_import_codegen_symbols(self):
        """Test import of codegen_symbols adapter"""
        from code_scalpel.adapters.codegen import codegen_symbols
        assert codegen_symbols is not None

    def test_import_codegen_transactions(self):
        """Test import of codegen_transactions adapter"""
        from code_scalpel.adapters.codegen import codegen_transactions
        assert codegen_transactions is not None

    def test_import_codegen_ai(self):
        """Test import of codegen_ai adapter"""
        from code_scalpel.adapters.codegen import codegen_ai
        assert codegen_ai is not None

    def test_import_codegen_config(self):
        """Test import of codegen_config adapter"""
        from code_scalpel.adapters.codegen import codegen_config
        assert codegen_config is not None

    def test_import_codegen_document_functions(self):
        """Test import of codegen_document_functions adapter"""
        from code_scalpel.adapters.codegen import codegen_document_functions
        assert codegen_document_functions is not None

    def test_import_codegen_progress(self):
        """Test import of codegen_progress adapter"""
        from code_scalpel.adapters.codegen import codegen_progress
        assert codegen_progress is not None

    def test_import_codegen_multigraph(self):
        """Test import of codegen_multigraph adapter"""
        from code_scalpel.adapters.codegen import codegen_multigraph
        assert codegen_multigraph is not None

    def test_import_main_init(self):
        """Test import of main __init__.py"""
        from code_scalpel.adapters import codegen
        assert codegen is not None

    def test_main_init_has_exports(self):
        """Test that main __init__.py has __all__ defined"""
        from code_scalpel.adapters import codegen
        assert hasattr(codegen, '__all__')
        assert len(codegen.__all__) > 0

    def test_all_adapters_accessible_from_main_init(self):
        """Test that all adapters are accessible from main __init__.py"""
        from code_scalpel.adapters import codegen

        # Check that key functions are accessible
        assert hasattr(codegen, 'get_codebase_summary')
        assert hasattr(codegen, 'Codebase')
        assert hasattr(codegen, 'commit')
        assert hasattr(codegen, 'query_codebase')

    def test_no_import_errors_on_module_load(self):
        """Test that loading all adapters doesn't raise ImportError"""
        try:
            from code_scalpel.adapters.codegen import (
                codegen_codebase_analysis,
                codegen_tools,
                codegen_mcp,
                codegen_graph,
                codegen_index,
                codegen_lsp,
                codegen_codebase,
                codegen_parser,
                codegen_symbols,
                codegen_transactions,
                codegen_ai,
                codegen_config,
                codegen_document_functions,
                codegen_progress,
                codegen_multigraph,
            )
        except ImportError as e:
            pytest.fail(f"Import error occurred: {e}")

    def test_adapter_modules_are_not_none(self):
        """Test that all adapter modules are not None after import"""
        from code_scalpel.adapters.codegen import (
            codegen_codebase_analysis,
            codegen_tools,
            codegen_mcp,
            codegen_graph,
            codegen_index,
            codegen_lsp,
            codegen_codebase,
            codegen_parser,
        )

        modules = [
            codegen_codebase_analysis,
            codegen_tools,
            codegen_mcp,
            codegen_graph,
            codegen_index,
            codegen_lsp,
            codegen_codebase,
            codegen_parser,
        ]

        for module in modules:
            assert module is not None, f"Module {module.__name__} is None"

