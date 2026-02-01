"""Unit tests for Oracle resilience middleware.

Tests the @with_oracle_resilience decorator and all recovery strategies.
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any

import pytest

from code_scalpel.mcp.contract import ToolError, ToolResponseEnvelope
from code_scalpel.mcp.oracle_middleware import (
    PathStrategy,
    SymbolStrategy,
    SafetyStrategy,
    NodeIdFormatStrategy,
    MethodNameFormatStrategy,
    CompositeStrategy,
    with_oracle_resilience,
)
from code_scalpel.mcp.validators.core import ValidationError


class TestSymbolStrategy:
    """Test SymbolStrategy recovery for missing symbols."""

    def test_suggest_empty_context(self):
        """Should return empty list if symbol_name is missing."""
        result = SymbolStrategy.suggest(ValidationError("Symbol not found"), {})
        assert result == []

    def test_suggest_missing_file_and_code(self):
        """Should return empty list if both file and code are missing."""
        result = SymbolStrategy.suggest(
            ValidationError("Symbol not found"), {"symbol_name": "foo"}
        )
        assert result == []

    def test_suggest_with_in_memory_code(self):
        """Should generate suggestions for in-memory code."""
        code = """
def process_data(x):
    return x * 2

def process_item(y):
    return y + 1

def process_file(z):
    return str(z)
"""
        context = {
            "code": code,
            "symbol_name": "process_dta",  # Typo
        }

        result = SymbolStrategy.suggest(
            ValidationError("Symbol 'process_dta' not found."), context
        )

        # Should get suggestions for similar symbols
        assert len(result) > 0
        assert any("process_data" in str(r.get("symbol", "")) for r in result)

    def test_suggest_with_file_code(self, tmp_path: Path):
        """Should generate suggestions from file content."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def calculate_sum(a, b):
    return a + b

def calculate_product(x, y):
    return x * y

def calculate_diff(p, q):
    return p - q
""")

        context = {
            "file_path": str(test_file),
            "symbol_name": "calculate_sum_total",  # Typo
        }

        result = SymbolStrategy.suggest(
            ValidationError("Symbol 'calculate_sum_total' not found."), context
        )

        # Should get suggestions
        assert len(result) > 0
        assert all("symbol" in r for r in result)
        assert all("score" in r for r in result)
        assert all("reason" in r for r in result)


class TestPathStrategy:
    """Test PathStrategy recovery for missing files."""

    def test_suggest_empty_context(self):
        """Should return empty list if file_path is missing."""
        result = PathStrategy.suggest(FileNotFoundError("File not found"), {})
        assert result == []

    def test_suggest_missing_parent_dir(self):
        """Should return empty list if parent directory doesn't exist."""
        result = PathStrategy.suggest(
            FileNotFoundError("File not found"),
            {"file_path": "/nonexistent/dir/file.py"},
        )
        assert result == []

    def test_suggest_similar_file(self, tmp_path: Path):
        """Should find similar files in directory."""
        # Create test files
        (tmp_path / "auth.py").write_text("# auth")
        (tmp_path / "utils.py").write_text("# utils")
        (tmp_path / "helpers.py").write_text("# helpers")

        context = {"file_path": str(tmp_path / "auth_utils.py")}  # Doesn't exist

        result = PathStrategy.suggest(
            FileNotFoundError(f"File not found: {tmp_path / 'auth_utils.py'}"), context
        )

        # Should suggest similar filenames
        assert len(result) > 0
        assert all("path" in r for r in result)
        assert all("score" in r for r in result)
        assert all(0 <= r["score"] <= 1 for r in result)

    def test_suggest_typo_filename(self, tmp_path: Path):
        """Should suggest correct file for typo."""
        (tmp_path / "authentication.py").write_text("# auth code")

        context = {"file_path": str(tmp_path / "autentication.py")}  # Typo: missing 'h'

        result = PathStrategy.suggest(
            FileNotFoundError(f"File not found: {tmp_path / 'autentication.py'}"),
            context,
        )

        # Should find 'authentication.py' as suggestion
        assert len(result) > 0
        assert any("authentication.py" in r.get("path", "") for r in result)
        # Top suggestion should be similar
        assert result[0]["score"] > 0.7


class TestOracleResilienceDecorator:
    """Test the @with_oracle_resilience decorator."""

    def test_non_async_function_raises_error(self):
        """Decorator should reject non-async functions."""
        with pytest.raises(TypeError, match="async"):

            @with_oracle_resilience(tool_id="test_tool")
            def sync_func():  # type: ignore
                pass

    def test_validation_error_triggers_oracle(self):
        """ValidationError should trigger oracle suggestions."""

        @with_oracle_resilience(tool_id="test_tool", strategy=SymbolStrategy)
        async def failing_tool(code: str, target_name: str) -> ToolResponseEnvelope:
            raise ValidationError(f"Symbol '{target_name}' not found.")

        result = asyncio.run(
            failing_tool(code="def process_data(): pass", target_name="process_dta")
        )

        # Should return ToolResponseEnvelope with correction_needed
        assert isinstance(result, ToolResponseEnvelope)
        assert result.error is not None
        assert result.error.error_code == "correction_needed"
        assert result.data is None

    def test_file_not_found_triggers_oracle(self, tmp_path: Path):
        """FileNotFoundError should trigger oracle suggestions."""

        @with_oracle_resilience(tool_id="test_tool", strategy=PathStrategy)
        async def failing_tool(file_path: str) -> ToolResponseEnvelope:
            with open(file_path) as f:  # Will raise FileNotFoundError
                return f.read()

        # Create similar file so oracle can suggest it
        (tmp_path / "existing.py").write_text("# code")

        result = asyncio.run(
            failing_tool(file_path=str(tmp_path / "exissting.py"))  # Typo
        )

        # Should return ToolResponseEnvelope with correction_needed
        assert isinstance(result, ToolResponseEnvelope)
        assert result.error is not None
        assert result.error.error_code == "correction_needed"

    def test_other_exceptions_pass_through(self):
        """Non-recoverable exceptions should pass through."""

        @with_oracle_resilience(tool_id="test_tool")
        async def failing_tool() -> ToolResponseEnvelope:
            raise RuntimeError("Some other error")

        with pytest.raises(RuntimeError, match="Some other error"):
            asyncio.run(failing_tool())

    def test_successful_tool_execution(self):
        """Successful execution should return normal result."""
        from code_scalpel.mcp.contract import make_envelope

        @with_oracle_resilience(tool_id="test_tool")
        async def working_tool() -> ToolResponseEnvelope:
            return make_envelope(
                data={"result": "success"},
                tool_id="test_tool",
                tool_version="1.0.0",
                tier="community",
            )

        result = asyncio.run(working_tool())

        # Should return success envelope
        assert result.error is None
        assert result.data == {"result": "success"}

    def test_error_details_structure(self):
        """error_details should contain suggestions in correct format."""

        @with_oracle_resilience(tool_id="test_tool", strategy=SymbolStrategy)
        async def failing_tool(code: str, target_name: str) -> ToolResponseEnvelope:
            raise ValidationError(f"Symbol '{target_name}' not found.")

        result = asyncio.run(
            failing_tool(
                code="def process_data(): pass\ndef process_item(): pass",
                target_name="process_dta",
            )
        )

        # Check error_details structure
        assert result.error is not None
        assert result.error.error_details is not None
        assert "suggestions" in result.error.error_details
        assert "hint" in result.error.error_details

        # Check suggestions format
        suggestions = result.error.error_details["suggestions"]
        if suggestions:
            assert all("symbol" in s or "path" in s for s in suggestions)
            assert all("score" in s for s in suggestions)
            assert all("reason" in s for s in suggestions)

    def test_suggestion_ranking(self):
        """Suggestions should be ranked by score."""

        @with_oracle_resilience(tool_id="test_tool", strategy=SymbolStrategy)
        async def failing_tool(code: str, target_name: str) -> ToolResponseEnvelope:
            raise ValidationError(f"Symbol '{target_name}' not found.")

        result = asyncio.run(
            failing_tool(
                code="""
def process_data(): pass
def process_item(): pass
def process_file(): pass
def foo(): pass
""",
                target_name="process_dta",
            )
        )

        # Suggestions should be ranked by score
        suggestions = result.error.error_details["suggestions"]
        if len(suggestions) > 1:
            scores = [s.get("score", 0) for s in suggestions]
            assert scores == sorted(scores, reverse=True)

    def test_envelope_metadata(self):
        """ToolResponseEnvelope should contain proper error and data structure."""

        @with_oracle_resilience(tool_id="extract_code", strategy=SymbolStrategy)
        async def sample_tool(code: str, target_name: str) -> ToolResponseEnvelope:
            raise ValidationError(f"Symbol '{target_name}' not found.")

        result = asyncio.run(sample_tool(code="def foo(): pass", target_name="bar"))

        # Check that result is a valid envelope
        assert isinstance(result, ToolResponseEnvelope)
        # Check error structure
        assert result.error is not None
        assert result.error.error_code == "correction_needed"
        # Data should be None when oracle intercepts an error
        assert result.data is None
        # Duration should be recorded (or None if filtered by response config)
        assert result.duration_ms is None or result.duration_ms >= 0


class TestNodeIdFormatStrategy:
    """Test NodeIdFormatStrategy for graph node ID validation."""

    def test_valid_node_id_format(self):
        """Valid node IDs should return empty list."""
        valid_ids = [
            "python::app.main::function::process_data",
            "python::models.user::class::User",
            "javascript::routes::method::handleRequest",
        ]

        for node_id in valid_ids:
            result = NodeIdFormatStrategy.suggest(
                ValidationError("Invalid format"), {"center_node_id": node_id}
            )
            assert result == [], f"Valid ID '{node_id}' should return empty list"

    def test_missing_components(self):
        """Node IDs with missing components should get suggestions."""
        result = NodeIdFormatStrategy.suggest(
            ValidationError("Invalid format"),
            {"center_node_id": "python::app.main::function"},  # Missing name
        )

        assert len(result) > 0
        assert "format_error" in str(result)

    def test_invalid_type(self):
        """Invalid type should get suggestion."""
        result = NodeIdFormatStrategy.suggest(
            ValidationError("Invalid format"),
            {"center_node_id": "python::app.main::invalid::process_data"},
        )

        assert len(result) > 0
        assert any("function" in str(r.get("example", "")) for r in result)

    def test_extra_components(self):
        """Too many components should get suggestion."""
        result = NodeIdFormatStrategy.suggest(
            ValidationError("Invalid format"),
            {"center_node_id": "python::app::main::function::process::data"},  # 6 parts
        )

        assert len(result) > 0
        assert result[0]["score"] < 0.5


class TestMethodNameFormatStrategy:
    """Test MethodNameFormatStrategy for method name validation."""

    def test_valid_method_name_format(self):
        """Valid method names should return empty list."""
        # Not a method extraction, should return empty
        result = MethodNameFormatStrategy.suggest(
            ValidationError("Invalid"),
            {"symbol_name": "validate_email", "target_type": "function"},
        )
        assert result == []

    def test_missing_dot_in_method(self):
        """Method without dot should get suggestion."""
        result = MethodNameFormatStrategy.suggest(
            ValidationError("Invalid"),
            {"symbol_name": "validate_email", "target_type": "method"},
        )

        assert len(result) > 0
        assert "ClassName.method_name" in str(result[0])

    def test_valid_class_method_format(self):
        """Valid Class.method format should return empty list."""
        result = MethodNameFormatStrategy.suggest(
            ValidationError("Invalid"),
            {"symbol_name": "User.validate_email", "target_type": "method"},
        )
        assert result == []

    def test_too_many_dots(self):
        """Too many dots in method name should get suggestion."""
        result = MethodNameFormatStrategy.suggest(
            ValidationError("Invalid"),
            {"symbol_name": "User.Profile.validate_email", "target_type": "method"},
        )

        assert len(result) > 0
        assert "one dot" in str(result[0])

    def test_missing_class_or_method(self):
        """Missing class or method name should get suggestion."""
        result = MethodNameFormatStrategy.suggest(
            ValidationError("Invalid"),
            {"symbol_name": ".validate_email", "target_type": "method"},
        )

        assert len(result) > 0

        result = MethodNameFormatStrategy.suggest(
            ValidationError("Invalid"),
            {"symbol_name": "User.", "target_type": "method"},
        )

        assert len(result) > 0


class TestCompositeStrategy:
    """Test CompositeStrategy for chaining multiple recovery strategies."""

    def test_composite_with_symbol_and_safety_strategy(self):
        """CompositeStrategy should combine suggestions from multiple strategies."""
        code = """
def process_data(x):
    return x * 2

def process_item(y):
    return y + 1
"""

        context = {
            "code": code,
            "symbol_name": "process_dta",  # Typo
            "new_name": "process_data",  # Collision with existing
        }

        composite = CompositeStrategy([SymbolStrategy, SafetyStrategy])
        result = composite.suggest(ValidationError("Symbol not found"), context)

        # Should get suggestions from both strategies
        # SymbolStrategy suggests 'process_data'
        # SafetyStrategy warns about collision
        assert isinstance(result, list)

    def test_composite_strategy_deduplication(self):
        """CompositeStrategy should deduplicate suggestions."""
        composite = CompositeStrategy([SymbolStrategy])

        # Create fake suggestions with duplicates
        suggestions = [
            {"symbol": "foo", "score": 0.9},
            {"symbol": "foo", "score": 0.85},  # Duplicate with lower score
            {"symbol": "bar", "score": 0.8},
        ]

        # Use the deduplication method directly
        deduped = composite._rank_and_dedupe(suggestions)

        # Should keep only one "foo" (the highest score one)
        foo_items = [s for s in deduped if s.get("symbol") == "foo"]
        assert len(foo_items) == 1
        assert foo_items[0]["score"] == 0.9

    def test_composite_strategy_ranking(self):
        """CompositeStrategy should rank suggestions by score."""
        suggestions = [
            {"symbol": "foo", "score": 0.7},
            {"symbol": "bar", "score": 0.95},
            {"symbol": "baz", "score": 0.8},
        ]

        composite = CompositeStrategy([SymbolStrategy])
        ranked = composite._rank_and_dedupe(suggestions)

        # Should be ranked descending by score
        scores = [s.get("score", 0) for s in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_composite_strategy_top_3_limit(self):
        """CompositeStrategy should return at most 3 suggestions."""
        suggestions = [
            {"symbol": f"var_{i}", "score": 1.0 - (i * 0.1)} for i in range(10)
        ]

        composite = CompositeStrategy([SymbolStrategy])
        result = composite._rank_and_dedupe(suggestions)

        assert len(result) <= 3


class TestIntegrationWithContext:
    """Integration tests with actual context."""

    def test_symbol_strategy_with_realistic_code(self):
        """Test SymbolStrategy with realistic Python code."""
        code = """
import os
from pathlib import Path

class FileManager:
    def __init__(self, base_path):
        self.base_path = base_path

    def list_files(self, directory):
        return os.listdir(directory)

    def read_file(self, file_path):
        with open(file_path) as f:
            return f.read()

    def write_file(self, file_path, content):
        with open(file_path, 'w') as f:
            f.write(content)

def process_files(directory):
    manager = FileManager(directory)
    return manager.list_files(directory)
"""
        # Test with typo "write_file" -> "write_fil"
        context = {"code": code, "symbol_name": "write_fil"}

        result = SymbolStrategy.suggest(
            ValidationError("Symbol 'write_fil' not found."), context
        )

        # Should suggest similar methods
        assert len(result) > 0
        assert any("write_file" in str(r.get("symbol", "")) for r in result)

    def test_path_strategy_in_project_structure(self, tmp_path: Path):
        """Test PathStrategy with realistic directory structure."""
        # Create project structure
        src = tmp_path / "src"
        src.mkdir()
        (src / "main.py").write_text("# main")
        (src / "utils.py").write_text("# utils")
        (src / "config.py").write_text("# config")

        tests = tmp_path / "tests"
        tests.mkdir()
        (tests / "test_main.py").write_text("# tests")

        # Test finding similar file in wrong directory
        context = {"file_path": str(src / "utils_helper.py")}
        result = PathStrategy.suggest(
            FileNotFoundError(f"File not found: {src / 'utils_helper.py'}"), context
        )

        # Should suggest utils.py
        assert len(result) > 0
        assert any("utils.py" in r.get("path", "") for r in result)


class TestGetFileContextOracle:
    """Test get_file_context tool with oracle resilience."""

    def test_get_file_context_with_missing_file(self, tmp_path: Path):
        """Test that oracle provides suggestions for missing files in get_file_context."""
        # Create a file so oracle can suggest it
        (tmp_path / "utils.py").write_text("def helper(): pass")

        # Test with typo - oracle should suggest utils.py
        context = {"file_path": str(tmp_path / "utils_typo.py")}
        result = PathStrategy.suggest(
            FileNotFoundError(f"File not found: {tmp_path / 'utils_typo.py'}"), context
        )

        # Should get suggestion for similar file
        assert len(result) > 0
        assert any("utils.py" in r.get("path", "") for r in result)
        assert result[0]["score"] > 0.6


class TestCrawlProjectOracle:
    """Test crawl_project tool with oracle resilience."""

    def test_crawl_project_with_missing_root(self, tmp_path: Path):
        """Test that oracle provides suggestions for missing project roots."""
        # Create a valid project root
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# main")

        # Test with typo in directory name
        context = {"file_path": str(tmp_path / "scr")}  # Typo: scr instead of src
        result = PathStrategy.suggest(
            FileNotFoundError(f"Directory not found: {tmp_path / 'scr'}"), context
        )

        # Note: PathStrategy suggests files, not directories, so this might return empty
        # But the oracle decorator will still handle the FileNotFoundError gracefully
        # The important thing is that the decorator is applied and catches the error
        assert isinstance(result, list)


class TestCrossFileSecurityScanOracle:
    """Test cross_file_security_scan tool with oracle resilience."""

    def test_cross_file_security_scan_with_missing_project(self, tmp_path: Path):
        """Test that oracle handles missing project roots in cross_file_security_scan."""
        # Create a project structure
        (tmp_path / "app").mkdir()
        (tmp_path / "app" / "main.py").write_text("# main")

        # Test with typo in project root
        context = {"file_path": str(tmp_path / "aap")}  # Typo
        result = PathStrategy.suggest(
            FileNotFoundError(f"Project root not found: {tmp_path / 'aap'}"), context
        )

        # Oracle should handle this gracefully
        assert isinstance(result, list)


class TestRenameSymbolCollisionDetection:
    """Test rename_symbol with collision detection."""

    def test_rename_symbol_detects_collision(self):
        """RenameSymbolStrategy should detect when new_name already exists."""
        code = """
def process_data(x):
    return x * 2

def process_item(y):
    return y + 1

def calculate_total(items):
    return sum(items)
"""

        # Try to rename calculate_total to process_item (collision with existing function)
        context = {
            "code": code,
            "symbol_name": "calculate_total",  # Symbol to rename
            "target_name": "calculate_total",
            "new_name": "process_item",  # This already exists
        }

        from code_scalpel.mcp.oracle_middleware import RenameSymbolStrategy

        result = RenameSymbolStrategy.suggest(
            ValidationError("Collision detected"), context
        )

        # Should detect the collision
        assert len(result) > 0
        assert any("already exists" in str(r).lower() for r in result)

    def test_rename_symbol_allows_unique_name(self):
        """RenameSymbolStrategy should not flag unique new names."""
        code = """
def process_data(x):
    return x * 2
"""

        context = {
            "code": code,
            "symbol_name": "process_data",
            "target_name": "process_data",
            "new_name": "transform_data",  # Unique name
        }

        from code_scalpel.mcp.oracle_middleware import RenameSymbolStrategy

        result = RenameSymbolStrategy.suggest(
            ValidationError("Check collision"), context
        )

        # Should not detect collision for unique name
        # Result might be empty or contain symbol suggestions, but no collision hint
        assert not any("collision" in str(r).lower() for r in result)

    def test_rename_symbol_with_typo_and_collision(self):
        """RenameSymbolStrategy should handle both typo and collision detection."""
        code = """
def process_data(x):
    return x * 2

def process_item(y):
    return y + 1

def calcualte_total(items):  # Typo in source
    return sum(items)
"""

        # Try to rename with typo in target_name AND collision in new_name
        context = {
            "code": code,
            "symbol_name": "calucalte_total",  # Typo
            "target_name": "calucalte_total",
            "new_name": "process_item",  # Collision
        }

        from code_scalpel.mcp.oracle_middleware import RenameSymbolStrategy

        result = RenameSymbolStrategy.suggest(
            ValidationError("Multiple issues"), context
        )

        # Should return suggestions (either for typo or collision detection)
        # The composite strategy should provide helpful suggestions
        assert isinstance(result, list)


class TestGraphNodeIdPreValidation:
    """Test pre-validation in get_graph_neighborhood."""

    def test_invalid_node_id_format_raises_error(self):
        """Invalid node ID format should raise ValidationError."""
        # This test verifies that the pre-validation logic works
        # In real use, this would be caught by NodeIdFormatStrategy

        result = NodeIdFormatStrategy.suggest(
            ValidationError("Invalid format"), {"center_node_id": "invalid_format"}
        )

        assert len(result) > 0
        assert any("format" in str(r).lower() for r in result)

    def test_valid_node_id_format_passes(self):
        """Valid node ID format should pass pre-validation."""
        result = NodeIdFormatStrategy.suggest(
            ValidationError("Should be valid"),
            {"center_node_id": "python::app.routes::function::handle_request"},
        )

        # Valid format should return empty suggestions
        assert result == []

    def test_node_id_missing_components(self):
        """Node ID with missing components should be flagged."""
        result = NodeIdFormatStrategy.suggest(
            ValidationError("Invalid"),
            {"center_node_id": "python::app.routes::function"},  # Missing name
        )

        assert len(result) > 0
        # Check that the suggestion includes info about expected format
        all_hints = "".join(
            str(r.get("hint", "")) + str(r.get("example", "")) for r in result
        )
        assert (
            "parts" in all_hints.lower()
            or "expected" in all_hints.lower()
            or "format" in all_hints.lower()
        )


class TestPolicyToolsOracle:
    """Test policy tools with oracle resilience."""

    def test_validate_paths_oracle(self, tmp_path: Path):
        """PathStrategy should suggest correct files for typos in path list."""
        (tmp_path / "config.yaml").write_text("# config")
        result = PathStrategy.suggest(
            FileNotFoundError(f"Path not found: {tmp_path / 'config_typo.yaml'}"),
            {"file_path": str(tmp_path / "config_typo.yaml")},
        )
        assert len(result) > 0
        assert any("config.yaml" in r.get("path", "") for r in result)

    def test_code_policy_check_oracle(self, tmp_path: Path):
        """Policy tool should use PathStrategy for file validation."""
        (tmp_path / "policy.txt").write_text("# policy")
        result = PathStrategy.suggest(
            FileNotFoundError(str(tmp_path / "polciy.txt")),
            {"file_path": str(tmp_path / "polciy.txt")},
        )
        assert len(result) > 0


class TestSecurityToolsOracle:
    """Test security tools with oracle resilience."""

    def test_type_evaporation_scan_oracle(self, tmp_path: Path):
        """Security tool should suggest files for frontend/backend path typos."""
        (tmp_path / "frontend.ts").write_text("// frontend")
        result = PathStrategy.suggest(
            FileNotFoundError(str(tmp_path / "frontned.ts")),
            {"file_path": str(tmp_path / "frontned.ts")},
        )
        assert len(result) > 0

    def test_scan_dependencies_oracle(self, tmp_path: Path):
        """Dependency scanner should use PathStrategy for path validation."""
        (tmp_path / "src").mkdir()
        result = PathStrategy.suggest(
            FileNotFoundError(str(tmp_path / "scr")),
            {"file_path": str(tmp_path / "scr")},
        )
        assert isinstance(result, list)

    def test_security_scan_oracle(self, tmp_path: Path):
        """Security scanner should suggest files for path typos."""
        (tmp_path / "app.py").write_text("# app")
        result = PathStrategy.suggest(
            FileNotFoundError(str(tmp_path / "ap.py")),
            {"file_path": str(tmp_path / "ap.py")},
        )
        assert len(result) > 0


class TestGenerateTestsStrategy:
    """Test GenerateTestsStrategy for combined file and function validation."""

    def test_generate_tests_with_file_typo(self, tmp_path: Path):
        """GenerateTestsStrategy should suggest files for path typos."""
        from code_scalpel.mcp.oracle_middleware import GenerateTestsStrategy

        (tmp_path / "app.py").write_text("def process_data(): pass")
        context = {"file_path": str(tmp_path / "aap.py")}
        result = GenerateTestsStrategy.suggest(
            FileNotFoundError(str(tmp_path / "aap.py")), context
        )
        assert len(result) > 0

    def test_composite_deduplication_edge_case(self):
        """CompositeStrategy should handle empty suggestion lists."""
        from code_scalpel.mcp.oracle_middleware import CompositeStrategy

        empty_list = []
        result = CompositeStrategy._rank_and_dedupe(empty_list)
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
