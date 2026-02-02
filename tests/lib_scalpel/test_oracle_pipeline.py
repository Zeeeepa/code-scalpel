"""Tests for OraclePipeline - Pure library constraint injection.

[20260126_PHASE1] Tests for library pipeline with config-based limits (no tiers).
"""

import tempfile
from pathlib import Path

import pytest

from code_scalpel.lib_scalpel import OraclePipeline


class TestOraclePipelineBasics:
    """Test basic OraclePipeline functionality."""

    def test_pipeline_initialization(self):
        """Test pipeline initialization with config parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = OraclePipeline(
                repo_root=tmpdir,
                max_files=50,
                max_depth=2,
            )

            assert pipeline.repo_root == Path(tmpdir).resolve()
            assert pipeline.max_files == 50
            assert pipeline.max_depth == 2

    def test_pipeline_initialization_with_defaults(self):
        """Test pipeline uses default limits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = OraclePipeline(repo_root=tmpdir)

            assert pipeline.max_files == 50
            assert pipeline.max_depth == 2

    def test_pipeline_initialization_with_string_path(self):
        """Test pipeline accepts string paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = OraclePipeline(repo_root=str(tmpdir), max_files=100)
            assert isinstance(pipeline.repo_root, Path)

    def test_get_context_lines_formula(self):
        """Test context lines calculation based on max_files."""
        # Base: 100 + (max_files // 10), capped at 1000

        # Small scan
        lines = OraclePipeline._get_context_lines(50)
        assert lines == 100 + (50 // 10)  # 105

        # Medium scan
        lines = OraclePipeline._get_context_lines(2000)
        assert lines == 100 + (2000 // 10)  # 300

        # Large scan (capped)
        lines = OraclePipeline._get_context_lines(100000)
        assert lines == 1000  # Capped at 1000


class TestOraclePipelineEntryPoints:
    """Test module-level entry point functions."""

    def test_generate_constraint_spec_sync_signature(self):
        """Test sync entry point has correct signature."""
        from code_scalpel.lib_scalpel.oracle_pipeline import (
            generate_constraint_spec_sync,
        )
        import inspect

        sig = inspect.signature(generate_constraint_spec_sync)
        params = list(sig.parameters.keys())

        # Should have these parameters (no 'tier' parameter)
        assert "repo_root" in params
        assert "file_path" in params
        assert "instruction" in params
        assert "max_files" in params
        assert "max_depth" in params
        assert "governance_config" in params
        assert "tier" not in params

    def test_generate_constraint_spec_async_signature(self):
        """Test async entry point has correct signature."""
        from code_scalpel.lib_scalpel.oracle_pipeline import (
            generate_constraint_spec_async,
        )
        import inspect

        sig = inspect.signature(generate_constraint_spec_async)
        params = list(sig.parameters.keys())

        # Should have these parameters (no 'tier' parameter)
        assert "repo_root" in params
        assert "file_path" in params
        assert "instruction" in params
        assert "max_files" in params
        assert "max_depth" in params
        assert "governance_config" in params
        assert "tier" not in params


class TestOraclePipelineValidation:
    """Test input validation in OraclePipeline."""

    def test_missing_file_raises_error(self):
        """Test that missing file raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = OraclePipeline(repo_root=tmpdir)

            with pytest.raises(FileNotFoundError):
                pipeline.generate_constraint_spec(
                    file_path="/nonexistent/file.py",
                    instruction="Test",
                )

    def test_missing_file_path_raises_error(self):
        """Test that missing file_path parameter raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = OraclePipeline(repo_root=tmpdir)

            with pytest.raises(ValueError, match="file_path is required"):
                pipeline.generate_constraint_spec(
                    file_path="",
                    instruction="Test",
                )

    def test_missing_instruction_raises_error(self):
        """Test that missing instruction parameter raises ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# test")

            pipeline = OraclePipeline(repo_root=tmpdir)

            with pytest.raises(ValueError, match="instruction is required"):
                pipeline.generate_constraint_spec(
                    file_path=str(test_file),
                    instruction="",
                )


class TestOraclePipelineIntegration:
    """Integration tests for OraclePipeline."""

    def test_pipeline_generates_spec(self):
        """Test that pipeline can generate a spec without errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test Python file
            test_file = Path(tmpdir) / "auth.py"
            test_file.write_text("""
def login(username, password):
    '''Authenticate user.'''
    # TODO: Hash password
    return True

class User:
    def __init__(self, name):
        self.name = name
""")

            # Generate spec with small limits
            pipeline = OraclePipeline(
                repo_root=tmpdir,
                max_files=10,
                max_depth=2,
            )

            spec = pipeline.generate_constraint_spec(
                file_path=str(test_file),
                instruction="Add JWT authentication",
            )

            # Verify we got a spec back
            assert isinstance(spec, str)
            assert len(spec) > 0

    def test_pipeline_respects_max_files_limit(self):
        """Test that pipeline respects max_files configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple Python files
            for i in range(5):
                py_file = Path(tmpdir) / f"module_{i}.py"
                py_file.write_text(f"# Module {i}\ndef func_{i}(): pass")

            # Create target file
            target_file = Path(tmpdir) / "target.py"
            target_file.write_text("def target(): pass")

            # Generate spec with max_files=2
            pipeline = OraclePipeline(
                repo_root=tmpdir,
                max_files=2,
                max_depth=2,
            )

            spec = pipeline.generate_constraint_spec(
                file_path=str(target_file),
                instruction="Implement feature",
            )

            # Should not raise an error
            assert isinstance(spec, str)

    def test_pipeline_handles_syntax_errors(self):
        """Test that pipeline handles files with syntax errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with syntax error
            test_file = Path(tmpdir) / "broken.py"
            test_file.write_text("def broken( syntax error")

            pipeline = OraclePipeline(repo_root=tmpdir)

            # Should raise SyntaxError
            with pytest.raises(SyntaxError):
                pipeline.generate_constraint_spec(
                    file_path=str(test_file),
                    instruction="Fix syntax",
                )
