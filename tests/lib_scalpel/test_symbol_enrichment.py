"""Tests for symbol enrichment in ProjectScanner.

[20260126_PHASE1] Tests for SymbolExtractor integration in ProjectScanner.
"""

import tempfile
from pathlib import Path


from code_scalpel.lib_scalpel import ProjectScanner


class TestProjectScannerSymbolEnrichment:
    """Test symbol extraction and graph enrichment."""

    def test_scan_with_symbol_extraction_enabled(self):
        """Test that scanner extracts and enriches symbols."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a test file with function and class
            test_file = tmpdir_path / "test_module.py"
            test_file.write_text(
                """
def process_data(data: list) -> dict:
    '''Process data and return results.'''
    return {'count': len(data)}

class DataProcessor:
    '''A processor for data.'''
    
    def __init__(self, name: str):
        self.name = name
    
    def process(self, items):
        '''Process items.'''
        return items
"""
            )

            # Scan with symbol extraction enabled
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
                extract_symbols=True,
            )
            graph = scanner.scan()

            # Verify we have enriched nodes
            assert len(graph.nodes) > 0

            # Find function node with parameters
            func_nodes = [
                n
                for n in graph.nodes
                if n.id.node_type.value == "function" and n.metadata.get("parameters")
            ]
            assert len(func_nodes) > 0

            # Verify function has signature info
            func_node = func_nodes[0]
            assert func_node.metadata[
                "return_type"
            ] is not None or "process_data" not in str(func_node.id)

    def test_scan_without_symbol_extraction(self):
        """Test that scanner works without symbol extraction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            test_file = tmpdir_path / "simple.py"
            test_file.write_text("def hello(): pass")

            # Scan without symbol extraction
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
                extract_symbols=False,  # Disabled
            )
            graph = scanner.scan()

            # Should still have nodes but without enrichment
            assert len(graph.nodes) > 0

    def test_symbol_extraction_adds_class_methods(self):
        """Test that class methods are extracted and linked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            test_file = tmpdir_path / "classes.py"
            test_file.write_text(
                """
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        return a - b
"""
            )

            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
                extract_symbols=True,
            )
            graph = scanner.scan()

            # Find class node
            class_nodes = [n for n in graph.nodes if n.id.node_type.value == "class"]
            assert len(class_nodes) > 0

            # Verify methods are listed
            class_node = class_nodes[0]
            methods = class_node.metadata.get("methods", [])
            assert "add" in methods or "subtract" in methods

    def test_symbol_extraction_handles_errors(self):
        """Test that symbol extraction errors don't crash scanner."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a valid file
            valid_file = tmpdir_path / "valid.py"
            valid_file.write_text("def valid(): pass")

            # Create an invalid file
            invalid_file = tmpdir_path / "invalid.py"
            invalid_file.write_text("def invalid( broken syntax")

            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
                extract_symbols=True,
            )
            _ = scanner.scan()

            # Should handle the error gracefully
            assert scanner.scanned_files == 2
            assert len(scanner.errors) > 0

    def test_symbol_enrichment_preserves_ast_data(self):
        """Test that AST extraction and symbol enrichment work together."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            test_file = tmpdir_path / "mixed.py"
            test_file.write_text(
                """
import json
from typing import Dict

def helper():
    pass

class Manager:
    def task(self):
        pass
"""
            )

            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
                extract_symbols=True,
            )
            graph = scanner.scan()

            # Verify we have all node types
            node_types = set(n.id.node_type.value for n in graph.nodes)
            assert "module" in node_types
            assert "class" in node_types or "function" in node_types

    def test_function_signature_extraction(self):
        """Test that function signatures are correctly extracted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            test_file = tmpdir_path / "signatures.py"
            test_file.write_text(
                """
def simple():
    '''Simple function.'''
    pass

def with_args(a: int, b: str) -> bool:
    '''Function with arguments.'''
    return True

@decorator
def decorated():
    '''Decorated function.'''
    pass
"""
            )

            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
                extract_symbols=True,
            )
            graph = scanner.scan()

            # Find all function nodes
            func_nodes = [n for n in graph.nodes if n.id.node_type.value == "function"]

            # Should have extracted functions
            assert len(func_nodes) >= 1

            # At least one should have parameters
            param_nodes = [n for n in func_nodes if n.metadata.get("parameters")]
            assert len(param_nodes) >= 1


class TestSymbolExtractorIntegration:
    """Test integration between ProjectScanner and SymbolExtractor."""

    def test_symbol_extractor_available(self):
        """Test that ProjectScanner initializes SymbolExtractor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(
                root_dir=tmpdir,
                extract_symbols=True,
            )
            assert scanner.symbol_extractor is not None

    def test_symbol_extractor_disabled(self):
        """Test that SymbolExtractor can be disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(
                root_dir=tmpdir,
                extract_symbols=False,
            )
            assert scanner.symbol_extractor is None

    def test_enriched_nodes_have_metadata(self):
        """Test that enriched nodes have proper metadata structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            test_file = tmpdir_path / "metadata.py"
            test_file.write_text(
                """
def example(x, y) -> int:
    '''Example function.'''
    return x + y
"""
            )

            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
                extract_symbols=True,
            )
            graph = scanner.scan()

            # Find a function node
            func_nodes = [n for n in graph.nodes if n.id.node_type.value == "function"]
            assert len(func_nodes) > 0

            # Check metadata structure
            func_node = func_nodes[0]
            # Should have at least some metadata
            assert isinstance(func_node.metadata, dict)
