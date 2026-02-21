"""Test suite for Oracle MCP tool.

Tests write_perfect_code tool registration and behavior.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from code_scalpel.mcp.tools.oracle import (
    write_perfect_code,
    _write_perfect_code_sync,
    _write_perfect_code_impl,
)
from code_scalpel.mcp.contract import ToolResponseEnvelope


class TestWritePerfectCodeSync:
    """Test synchronous implementation of write_perfect_code."""

    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a temporary Python file in an isolated tmp_path directory.

        [20260219_BUGFIX] Use tmp_path to ensure the OraclePipeline only scans
        a small isolated directory, not /tmp or the full workspace.
        """
        content = '''"""Sample module."""

def hello(name: str) -> str:
    """Greet someone."""
    return f"Hello {name}"

class Greeter:
    """A greeter class."""
    
    def greet(self, name: str) -> str:
        """Greet a person."""
        return hello(name)
'''
        sample = tmp_path / "sample.py"
        sample.write_text(content, encoding="utf-8")
        return str(sample)

    def test_sync_implementation_valid_file(self, sample_file):
        """Test sync implementation with valid file."""
        sample_dir = str(Path(sample_file).parent)
        # [20260219_BUGFIX] Mock get_project_root to isolated tmp_path dir; use community
        # tier (max_files=50) so the 1-file scan completes instantly.
        with patch(
            "code_scalpel.mcp.protocol._get_current_tier", return_value="community"
        ):
            with patch(
                "code_scalpel.mcp.server.get_project_root", return_value=sample_dir
            ):
                markdown = _write_perfect_code_sync(
                    file_path=sample_file,
                    instruction="Add error handling",
                )

                assert isinstance(markdown, str)
                assert len(markdown) > 0
                assert "Code Generation Constraints" in markdown
                assert sample_file in markdown

    def test_sync_implementation_missing_file(self):
        """Test sync implementation with missing file."""
        with pytest.raises(FileNotFoundError):
            _write_perfect_code_sync(
                file_path="/nonexistent/file.py",
                instruction="Add error handling",
            )

    def test_sync_implementation_empty_file_path(self, sample_file):
        """Test sync implementation with empty file path."""
        with pytest.raises(ValueError, match="file_path is required"):
            _write_perfect_code_sync(
                file_path="",
                instruction="Add error handling",
            )

    def test_sync_implementation_empty_instruction(self, sample_file):
        """Test sync implementation with empty instruction."""
        with pytest.raises(ValueError, match="instruction is required"):
            _write_perfect_code_sync(
                file_path=sample_file,
                instruction="",
            )

    def test_sync_implementation_invalid_python(self, tmp_path):
        """Test sync implementation with invalid Python syntax."""
        # [20260219_BUGFIX] Use tmp_path for isolated scan root; mock get_project_root
        # to prevent the graph engine from scanning the workspace.
        content = "def broken("
        file_path = str(tmp_path / "broken.py")
        Path(file_path).write_text(content, encoding="utf-8")

        with patch(
            "code_scalpel.mcp.protocol._get_current_tier", return_value="community"
        ):
            with patch(
                "code_scalpel.mcp.server.get_project_root", return_value=str(tmp_path)
            ):
                with pytest.raises(SyntaxError):
                    _write_perfect_code_sync(
                        file_path=file_path,
                        instruction="Fix syntax",
                    )

    def test_sync_implementation_respects_tier(self, sample_file):
        """Test that sync implementation respects tier for limits."""
        sample_dir = str(Path(sample_file).parent)
        # [20260219_BUGFIX] Mock get_project_root to isolated tmp_path dir.
        with patch(
            "code_scalpel.mcp.protocol._get_current_tier", return_value="community"
        ):
            with patch(
                "code_scalpel.mcp.server.get_project_root", return_value=sample_dir
            ):
                markdown = _write_perfect_code_sync(
                    file_path=sample_file,
                    instruction="Add validation",
                )

                # Pro tier should have reasonable context
                assert len(markdown) > 100


class TestWritePerfectCodeAsync:
    """Test async implementation of write_perfect_code."""

    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a temporary Python file in an isolated tmp_path directory.

        [20260219_BUGFIX] Use tmp_path to ensure the OraclePipeline only scans
        a small isolated directory, not /tmp or the full workspace.
        """
        content = '''"""Sample module."""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
'''
        sample = tmp_path / "sample.py"
        sample.write_text(content, encoding="utf-8")
        return str(sample)

    @pytest.mark.asyncio
    async def test_async_implementation_valid_file(self, sample_file):
        """Test async implementation with valid file."""
        sample_dir = str(Path(sample_file).parent)
        # [20260219_BUGFIX] Mock get_project_root to isolated tmp_path dir.
        with patch(
            "code_scalpel.mcp.protocol._get_current_tier", return_value="community"
        ):
            with patch(
                "code_scalpel.mcp.server.get_project_root", return_value=sample_dir
            ):
                markdown = await _write_perfect_code_impl(
                    file_path=sample_file,
                    instruction="Add logging",
                )

                assert isinstance(markdown, str)
                assert len(markdown) > 0
                assert "Code Generation Constraints" in markdown

    @pytest.mark.asyncio
    async def test_async_implementation_propagates_file_not_found(self):
        """Test async implementation propagates FileNotFoundError."""
        with patch("code_scalpel.mcp.protocol._get_current_tier", return_value="pro"):
            with pytest.raises(FileNotFoundError):
                await _write_perfect_code_impl(
                    file_path="/nonexistent/file.py",
                    instruction="Test",
                )

    @pytest.mark.asyncio
    async def test_async_implementation_propagates_value_error(self, sample_file):
        """Test async implementation propagates ValueError."""
        with patch("code_scalpel.mcp.protocol._get_current_tier", return_value="pro"):
            with pytest.raises(ValueError):
                await _write_perfect_code_impl(
                    file_path=sample_file,
                    instruction="",  # Empty instruction
                )


class TestWritePerfectCodeMCPTool:
    """Test MCP tool registration and interface."""

    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a temporary Python file in an isolated tmp_path directory.

        [20260219_BUGFIX] Use tmp_path for consistency (these tests mock
        _write_perfect_code_impl so no real scan occurs, but using tmp_path
        ensures cleanup and isolation).
        """
        content = '''"""Sample module."""

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
'''
        sample = tmp_path / "sample.py"
        sample.write_text(content, encoding="utf-8")
        return str(sample)

    @pytest.mark.asyncio
    async def test_tool_success_response(self, sample_file):
        """Test tool returns valid response on success."""
        with patch(
            "code_scalpel.mcp.tools.oracle._get_current_tier", return_value="pro"
        ):
            with patch(
                "code_scalpel.mcp.tools.oracle._write_perfect_code_impl"
            ) as mock_impl:
                mock_impl.return_value = "# Constraint Spec\nTest content"

                response = await write_perfect_code(
                    file_path=sample_file,
                    instruction="Add validation",
                )

                assert isinstance(response, ToolResponseEnvelope)
                assert response.data == "# Constraint Spec\nTest content"
                assert response.error is None
                assert response.tool_id == "write_perfect_code"
                assert response.tier == "pro"
                assert response.duration_ms is not None
                assert response.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_tool_includes_version(self, sample_file):
        """Test tool includes package version in response."""
        with patch("code_scalpel.mcp.protocol._get_current_tier", return_value="pro"):
            with patch(
                "code_scalpel.mcp.tools.oracle._write_perfect_code_impl"
            ) as mock_impl:
                mock_impl.return_value = "# Spec"

                response = await write_perfect_code(
                    file_path=sample_file,
                    instruction="Test",
                )

                assert response.tool_version is not None
                assert isinstance(response.tool_version, str)

    @pytest.mark.asyncio
    async def test_tool_includes_tier(self, sample_file):
        """Test tool includes current tier in response."""
        for tier in ["community", "pro", "enterprise"]:
            with patch(
                "code_scalpel.mcp.tools.oracle._get_current_tier", return_value=tier
            ):
                with patch(
                    "code_scalpel.mcp.tools.oracle._write_perfect_code_impl"
                ) as mock_impl:
                    mock_impl.return_value = "# Spec"

                    response = await write_perfect_code(
                        file_path="src/test.py",
                        instruction="Test",
                    )

                    assert response.tier == tier


class TestWritePerfectCodeIntegration:
    """Integration tests for write_perfect_code tool."""

    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a temporary Python file in an isolated tmp_path directory.

        [20260219_BUGFIX] Use tmp_path to ensure the OraclePipeline only scans
        a small isolated directory, not /tmp or the full workspace.
        """
        content = '''"""Authentication module."""

import json
from typing import Optional

def validate_token(token: str) -> bool:
    """Validate JWT token."""
    try:
        payload = json.loads(token)
        return payload.get("exp") is not None
    except Exception:
        return False

class TokenManager:
    """Manage authentication tokens."""
    
    def __init__(self):
        """Initialize token manager."""
        self.tokens = {}
    
    def store_token(self, user_id: str, token: str) -> None:
        """Store user token."""
        self.tokens[user_id] = token
    
    def get_token(self, user_id: str) -> Optional[str]:
        """Retrieve user token."""
        return self.tokens.get(user_id)
'''
        sample = tmp_path / "auth.py"
        sample.write_text(content, encoding="utf-8")
        return str(sample)

    def test_sync_with_real_file_content(self, sample_file):
        """Test sync implementation with real file content."""
        sample_dir = str(Path(sample_file).parent)
        # [20260219_BUGFIX] Mock get_project_root to isolated tmp_path dir.
        with patch(
            "code_scalpel.mcp.protocol._get_current_tier", return_value="community"
        ):
            with patch(
                "code_scalpel.mcp.server.get_project_root", return_value=sample_dir
            ):
                markdown = _write_perfect_code_sync(
                    file_path=sample_file,
                    instruction="Add token refresh functionality",
                )

                # Should include symbols from the file
                assert "validate_token" in markdown
                assert "TokenManager" in markdown
                assert "store_token" in markdown
                # Should include instruction
                assert "token refresh" in markdown.lower()

    @pytest.mark.asyncio
    async def test_async_integration_with_mcp_tool(self, sample_file):
        """Test async implementation integrates with MCP tool."""
        sample_dir = str(Path(sample_file).parent)
        # [20260219_BUGFIX] Mock get_project_root to isolated tmp_path dir.
        with patch(
            "code_scalpel.mcp.protocol._get_current_tier", return_value="community"
        ):
            with patch(
                "code_scalpel.mcp.server.get_project_root", return_value=sample_dir
            ):
                response = await write_perfect_code(
                    file_path=sample_file,
                    instruction="Add expiration checking",
                )

                assert isinstance(response, ToolResponseEnvelope)
                assert response.error is None
                assert response.data is not None
                assert "Code Generation Constraints" in response.data
                assert sample_file in response.data
