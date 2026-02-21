"""Tests for ProjectScanner - Library graph building.

[20260126_PHASE1] Tests for pure library scanner with no MCP/tier knowledge.
"""

import tempfile
from pathlib import Path

import pytest

from code_scalpel.lib_scalpel import ProjectScanner
from code_scalpel.lib_scalpel.graph_engine import UniversalGraph


class TestProjectScanner:
    """Test cases for ProjectScanner."""

    def test_scan_simple_directory(self):
        """Test scanning a simple Python directory structure."""
        # Create a temporary directory with sample files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a simple Python file
            py_file = tmpdir_path / "test_module.py"
            py_file.write_text(
                """
def hello():
    pass

class MyClass:
    def method(self):
        pass
"""
            )

            # Scan with low limits
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
            )
            graph = scanner.scan()

            # Verify graph was built
            assert isinstance(graph, UniversalGraph)
            assert len(graph.nodes) > 0
            assert len(graph.edges) > 0
            assert scanner.scanned_files == 1

    def test_scan_respects_max_files_limit(self):
        """Test that scanner respects max_files limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create 5 Python files
            for i in range(5):
                py_file = tmpdir_path / f"test_{i}.py"
                py_file.write_text(f"# Test file {i}\ndef func_{i}(): pass")

            # Scan with max_files=3
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=3,
                max_depth=2,
            )
            _ = scanner.scan()

            # Verify only 3 files were scanned
            assert scanner.scanned_files == 3

    def test_scan_respects_max_depth_limit(self):
        """Test that scanner respects max_depth limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create nested directory structure
            deep_dir = tmpdir_path / "a" / "b" / "c" / "d"
            deep_dir.mkdir(parents=True)

            # Put files at different depths
            (tmpdir_path / "level_0.py").write_text("# level 0")
            (tmpdir_path / "a" / "level_1.py").write_text("# level 1")
            (tmpdir_path / "a" / "b" / "level_2.py").write_text("# level 2")
            (deep_dir / "level_4.py").write_text("# level 4")

            # Scan with max_depth=2
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
            )
            _ = scanner.scan()

            # Should scan level 0, 1, 2 but not level 4
            # (depth 0=root, 1=a, 2=b, 3=c, 4=d)
            assert scanner.scanned_files <= 3

    def test_scan_excludes_default_directories(self):
        """Test that scanner excludes default directories like __pycache__."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create normal and excluded directories
            (tmpdir_path / "normal.py").write_text("# normal")
            pycache = tmpdir_path / "__pycache__"
            pycache.mkdir()
            (pycache / "excluded.py").write_text("# should not be scanned")

            # Scan
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
            )
            _ = scanner.scan()

            # Should only find normal.py
            assert scanner.scanned_files == 1

    def test_scan_handles_syntax_errors(self):
        """Test that scanner handles files with syntax errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a valid and invalid Python file
            (tmpdir_path / "valid.py").write_text("def valid(): pass")
            (tmpdir_path / "invalid.py").write_text("def invalid( broken syntax")

            # Scan
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
            )
            _ = scanner.scan()

            # Should have scanned both, but one has an error
            assert scanner.scanned_files == 2
            assert len(scanner.errors) == 1

    def test_scan_nonexistent_directory_raises(self):
        """Test that scanning nonexistent directory raises ValueError."""
        scanner = ProjectScanner(
            root_dir="/nonexistent/directory",
            max_files=10,
            max_depth=2,
        )

        with pytest.raises(ValueError, match="Root directory does not exist"):
            scanner.scan()

    def test_graph_contains_file_nodes(self):
        """Test that graph contains file nodes with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a Python file
            test_file = tmpdir_path / "test.py"
            test_file.write_text("# Test\ndef foo(): pass")

            # Scan
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
            )
            graph = scanner.scan()

            # Find file node
            file_nodes = [n for n in graph.nodes if n.id.node_type.value == "module"]
            assert len(file_nodes) > 0
            assert file_nodes[0].metadata["size"] > 0

    def test_graph_contains_class_nodes(self):
        """Test that graph contains class nodes from analyzed files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a file with a class
            test_file = tmpdir_path / "test.py"
            test_file.write_text(
                """
class MyClass:
    def method(self):
        pass
"""
            )

            # Scan
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
            )
            graph = scanner.scan()

            # Find class node
            class_nodes = [n for n in graph.nodes if n.id.node_type.value == "class"]
            assert len(class_nodes) > 0
            assert "MyClass" in str(class_nodes[0].id)

    def test_graph_contains_edges(self):
        """Test that graph contains edges between nodes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a file with a class
            test_file = tmpdir_path / "test.py"
            test_file.write_text(
                """
class MyClass:
    def method(self):
        pass
"""
            )

            # Scan
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=10,
                max_depth=2,
            )
            graph = scanner.scan()

            # Check that we have edges
            assert len(graph.edges) > 0

            # At minimum, should have edges from file to class and class to method
            edge_types = set(e.edge_type for e in graph.edges)
            assert len(edge_types) > 0

    def test_graph_metadata_set_correctly(self):
        """Test that graph metadata is set with scan information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create a file
            (tmpdir_path / "test.py").write_text("# test")

            # Scan with specific limits
            scanner = ProjectScanner(
                root_dir=tmpdir_path,
                max_files=100,
                max_depth=5,
            )
            graph = scanner.scan()

            # Verify metadata
            assert graph.metadata["scanned_files"] == 1
            assert graph.metadata["max_files_limit"] == 100
            assert graph.metadata["max_depth_limit"] == 5
            assert graph.metadata["errors"] == 0


class TestProjectScannerIntegration:
    """Integration tests with real code_scalpel modules."""

    def test_scan_lib_scalpel_directory(self):
        """Test scanning the lib_scalpel directory itself."""
        scanner = ProjectScanner(
            root_dir="src/code_scalpel/lib_scalpel",
            max_files=10,
            max_depth=2,
        )
        graph = scanner.scan()

        # Verify scan worked
        assert scanner.scanned_files == 10
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0

        # Verify we got various node types
        node_types = set(n.id.node_type.value for n in graph.nodes)
        assert "module" in node_types or "class" in node_types
