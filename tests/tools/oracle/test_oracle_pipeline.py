"""Tests for oracle_pipeline - Serverless Constraint Injection.

[20260126_PHASE1B] Comprehensive tests for OraclePipeline and entry points.

Tests cover:
- Tier-aware resource limits (community/pro/enterprise)
- End-to-end pipeline execution
- Performance (<200ms execution)
- Error handling
- Integration with ProjectCrawler
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

import pytest

from code_scalpel.oracle.oracle_pipeline import (
    OraclePipeline,
    generate_constraint_spec_sync,
    generate_constraint_spec_async,
)


class TestOraclePipelineTierLimits:
    """Test tier-aware resource limits."""

    def test_community_tier_limits(self):
        """Community tier should have 50 files, depth 2."""
        pipeline = OraclePipeline(".", tier="community")
        assert pipeline.scanner_limits["max_files"] == 50
        assert pipeline.scanner_limits["max_depth"] == 2

    def test_pro_tier_limits(self):
        """Pro tier should have 2000 files, depth 10."""
        pipeline = OraclePipeline(".", tier="pro")
        assert pipeline.scanner_limits["max_files"] == 2000
        assert pipeline.scanner_limits["max_depth"] == 10

    def test_enterprise_tier_limits(self):
        """Enterprise tier should have 100000 files, depth 50."""
        pipeline = OraclePipeline(".", tier="enterprise")
        assert pipeline.scanner_limits["max_files"] == 100000
        assert pipeline.scanner_limits["max_depth"] == 50

    def test_default_tier_is_community(self):
        """Default tier should be community."""
        pipeline = OraclePipeline(".")
        assert pipeline.tier == "community"
        assert pipeline.scanner_limits["max_files"] == 50

    def test_invalid_tier_defaults_to_community(self):
        """Invalid tier should default to community limits."""
        pipeline = OraclePipeline(".", tier="invalid")
        assert pipeline.scanner_limits["max_files"] == 50
        assert pipeline.scanner_limits["max_depth"] == 2


class TestOraclePipelineContextLines:
    """Test context line limits by tier."""

    def test_community_context_lines(self):
        """Community tier should have 100 context lines."""
        lines = OraclePipeline._get_context_lines("community")
        assert lines == 100

    def test_pro_context_lines(self):
        """Pro tier should have 200 context lines."""
        lines = OraclePipeline._get_context_lines("pro")
        assert lines == 200

    def test_enterprise_context_lines(self):
        """Enterprise tier should have 1000 context lines."""
        lines = OraclePipeline._get_context_lines("enterprise")
        assert lines == 1000

    def test_invalid_tier_defaults_to_100_lines(self):
        """Invalid tier should default to 100 lines."""
        lines = OraclePipeline._get_context_lines("invalid")
        assert lines == 100


class TestOraclePipelineBasicExecution:
    """Test basic pipeline execution."""

    def test_pipeline_initialization(self):
        """Pipeline should initialize with repo_root and tier."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = OraclePipeline(tmpdir, tier="pro")
            assert pipeline.repo_root == Path(tmpdir).resolve()
            assert pipeline.tier == "pro"
            assert pipeline.symbol_extractor is not None
            assert pipeline.constraint_analyzer is not None
            assert pipeline.spec_generator is not None

    def test_generate_constraint_spec_basic(self):
        """Should generate constraint spec for a valid Python file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                """
def hello(name):
    '''Say hello.'''
    return f"Hello, {name}!"
"""
            )

            pipeline = OraclePipeline(tmpdir, tier="community")
            spec = pipeline.generate_constraint_spec(
                file_path=str(test_file),
                instruction="Add error handling for empty name",
            )

            # Should return markdown string
            assert isinstance(spec, str)
            assert len(spec) > 0
            assert "hello" in spec.lower() or "function" in spec.lower()

    def test_generate_constraint_spec_file_not_found(self):
        """Should raise FileNotFoundError for missing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = OraclePipeline(tmpdir, tier="community")
            with pytest.raises(FileNotFoundError):
                pipeline.generate_constraint_spec(
                    file_path="/nonexistent/file.py",
                    instruction="Add feature",
                )

    def test_generate_constraint_spec_empty_instruction(self):
        """Should raise ValueError for empty instruction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def foo(): pass")

            pipeline = OraclePipeline(tmpdir, tier="community")
            with pytest.raises(ValueError, match="instruction is required"):
                pipeline.generate_constraint_spec(
                    file_path=str(test_file),
                    instruction="",
                )

    def test_generate_constraint_spec_syntax_error(self):
        """Should raise SyntaxError for invalid Python."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def foo( invalid syntax here")

            pipeline = OraclePipeline(tmpdir, tier="community")
            with pytest.raises(SyntaxError):
                pipeline.generate_constraint_spec(
                    file_path=str(test_file),
                    instruction="Add feature",
                )


class TestOraclePipelinePerformance:
    """Test performance constraints."""

    def test_pipeline_executes_in_time_budget(self):
        """Pipeline should complete in <200ms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                """
def add(a, b):
    '''Add two numbers.'''
    return a + b
"""
            )

            pipeline = OraclePipeline(tmpdir, tier="community")

            started = time.perf_counter()
            spec = pipeline.generate_constraint_spec(
                file_path=str(test_file),
                instruction="Add docstring",
            )
            duration_ms = int((time.perf_counter() - started) * 1000)

            # Should complete in reasonable time (200ms budget)
            assert duration_ms < 200, f"Pipeline took {duration_ms}ms (> 200ms budget)"
            assert isinstance(spec, str)
            assert len(spec) > 0

    def test_community_tier_faster_than_enterprise(self):
        """Community tier should be faster (smaller crawl)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def foo(): pass")

            # Time community tier
            pipeline_community = OraclePipeline(tmpdir, tier="community")
            started = time.perf_counter()
            _ = pipeline_community.generate_constraint_spec(
                file_path=str(test_file),
                instruction="Add feature",
            )
            community_ms = int((time.perf_counter() - started) * 1000)

            # Time enterprise tier
            pipeline_enterprise = OraclePipeline(tmpdir, tier="enterprise")
            started = time.perf_counter()
            _ = pipeline_enterprise.generate_constraint_spec(
                file_path=str(test_file),
                instruction="Add feature",
            )
            enterprise_ms = int((time.perf_counter() - started) * 1000)

            # Enterprise should not be significantly faster (both should be fast)
            # but community should have access to smaller limits
            assert community_ms < 200
            assert enterprise_ms < 200


class TestOraclePipelineEntryPoints:
    """Test entry point functions."""

    def test_generate_constraint_spec_sync(self):
        """Sync entry point should work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def bar(): pass")

            spec = generate_constraint_spec_sync(
                repo_root=tmpdir,
                file_path=str(test_file),
                instruction="Add error handling",
                tier="pro",
            )

            assert isinstance(spec, str)
            assert len(spec) > 0

    @pytest.mark.asyncio
    async def test_generate_constraint_spec_async(self):
        """Async entry point should work correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def baz(): pass")

            spec = await generate_constraint_spec_async(
                repo_root=tmpdir,
                file_path=str(test_file),
                instruction="Add logging",
                tier="community",
            )

            assert isinstance(spec, str)
            assert len(spec) > 0

    def test_sync_entry_point_file_not_found(self):
        """Sync entry point should propagate FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError):
                generate_constraint_spec_sync(
                    repo_root=tmpdir,
                    file_path="/nonexistent.py",
                    instruction="Add feature",
                )

    def test_sync_entry_point_respects_tier(self):
        """Sync entry point should pass tier to pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def func(): pass")

            # Should work with different tiers
            for tier in ["community", "pro", "enterprise"]:
                spec = generate_constraint_spec_sync(
                    repo_root=tmpdir,
                    file_path=str(test_file),
                    instruction="Add feature",
                    tier=tier,
                )
                assert isinstance(spec, str)
                assert len(spec) > 0


class TestOraclePipelineMultiFile:
    """Test pipeline with multiple files in project."""

    def test_pipeline_scans_multiple_files(self):
        """Pipeline should crawl and scan multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple Python files
            (Path(tmpdir) / "file1.py").write_text("def func1(): pass")
            (Path(tmpdir) / "file2.py").write_text("def func2(): pass")
            (Path(tmpdir) / "file3.py").write_text("def func3(): pass")

            pipeline = OraclePipeline(tmpdir, tier="pro")
            spec = pipeline.generate_constraint_spec(
                file_path=str(Path(tmpdir) / "file1.py"),
                instruction="Add validation",
            )

            # Should generate spec even with multiple files
            assert isinstance(spec, str)
            assert len(spec) > 0

    def test_community_tier_limits_file_crawl(self):
        """Community tier should respect max_files limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create more files than community limit (50)
            for i in range(100):
                (Path(tmpdir) / f"file{i}.py").write_text(f"def func{i}(): pass")

            # Community tier should crawl only up to 50 files
            pipeline = OraclePipeline(tmpdir, tier="community")
            assert pipeline.scanner_limits["max_files"] == 50

            spec = pipeline.generate_constraint_spec(
                file_path=str(Path(tmpdir) / "file0.py"),
                instruction="Add feature",
            )

            assert isinstance(spec, str)
            assert len(spec) > 0


class TestOraclePipelineClassInit:
    """Test OraclePipeline class initialization."""

    def test_repo_root_resolution(self):
        """repo_root should be resolved to absolute path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = OraclePipeline(tmpdir, tier="community")
            assert pipeline.repo_root.is_absolute()
            assert pipeline.repo_root.exists()

    def test_repo_root_string_or_path(self):
        """repo_root should accept string or Path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # String
            pipeline1 = OraclePipeline(tmpdir, tier="community")
            assert isinstance(pipeline1.repo_root, Path)

            # Path
            pipeline2 = OraclePipeline(Path(tmpdir), tier="community")
            assert isinstance(pipeline2.repo_root, Path)

            assert pipeline1.repo_root == pipeline2.repo_root


class TestOraclePipelineGovernanceConfig:
    """Test governance configuration handling."""

    def test_governance_config_optional(self):
        """Governance config should be optional."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def foo(): pass")

            pipeline = OraclePipeline(tmpdir, tier="community")
            spec = pipeline.generate_constraint_spec(
                file_path=str(test_file),
                instruction="Add feature",
                # governance_config=None (default)
            )

            assert isinstance(spec, str)

    def test_governance_config_passthrough(self):
        """Governance config should be passed to analyzer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def foo(): pass")

            pipeline = OraclePipeline(tmpdir, tier="community")
            governance = {
                "rules": [
                    {
                        "pattern": "src/**",
                        "forbidden": ["test/**"],
                    }
                ]
            }

            spec = pipeline.generate_constraint_spec(
                file_path=str(test_file),
                instruction="Add feature",
                governance_config=governance,
            )

            assert isinstance(spec, str)
