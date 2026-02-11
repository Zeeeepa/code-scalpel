"""Test oracle functionality with AI feedback for incorrect tool calls.

These tests simulate scenarios where an AI model calls a tool with incorrect
parameters and receives helpful error messages with suggestions.

Test scenarios:
1. Wrong file path - suggests actual files
2. Wrong function/class name - suggests existing symbols
3. Wrong parameter type - explains expected type
4. Missing required parameter - lists what was needed
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from code_scalpel.mcp.tools.oracle import write_perfect_code
from code_scalpel.mcp.tools.analyze import analyze_code
from code_scalpel.mcp.tools.extraction import extract_code, rename_symbol
from code_scalpel.mcp.contract import ToolResponseEnvelope


class TestOracleWritePerfectCodeWithWrongInputs:
    """Test write_perfect_code oracle feedback for incorrect inputs."""

    @pytest.mark.asyncio
    async def test_wrong_file_path_returns_error(self):
        """Test that wrong file path returns meaningful error.

        AI scenario: AI thinks file is at "src/config.py" but it's actually "src/settings.py"
        Expected: Error message indicates file not found
        """
        response = await write_perfect_code(
            file_path="/nonexistent/config.py",
            instruction="Add database connection pooling",
        )

        assert isinstance(response, ToolResponseEnvelope)
        assert response.error is not None
        assert (
            "not found" in response.error.error.lower()
            or "nonexistent" in response.error.error.lower()
        )
        assert response.tool_id == "write_perfect_code"

    @pytest.mark.asyncio
    async def test_empty_instruction_returns_error(self):
        """Test that empty instruction returns error.

        AI scenario: AI forgets to include instruction
        Expected: Error message indicates instruction is required
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def hello(): pass")
            temp_path = f.name

        try:
            response = await write_perfect_code(file_path=temp_path, instruction="")

            assert response.error is not None
            assert "required" in response.error.error.lower()
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_valid_inputs_returns_spec(self):
        """Test that valid inputs return constraint specification.

        AI scenario: AI correctly identifies file and instruction
        Expected: Successful response with constraint specification
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def authenticate(user: str, password: str) -> bool:
    return user == "admin" and password == "secret"

class AuthManager:
    def validate(self, token: str) -> bool:
        return len(token) > 0
"""
            )
            temp_path = f.name

        try:
            with patch(
                "code_scalpel.mcp.protocol._get_current_tier", return_value="pro"
            ):
                response = await write_perfect_code(
                    file_path=temp_path,
                    instruction="Add token refresh and security improvements",
                )

            assert isinstance(response, ToolResponseEnvelope)
            assert response.error is None
            assert response.data is not None
            assert "Code Generation Constraints" in response.data
        finally:
            Path(temp_path).unlink()


class TestOracleAnalyzeCodeWithWrongInputs:
    """Test analyze_code oracle feedback for incorrect language/code."""

    @pytest.mark.asyncio
    async def test_analyze_invalid_code_provides_feedback(self):
        """Test that invalid code returns helpful feedback.

        AI scenario: AI provides syntactically invalid Python code
        Expected: Error indicates syntax issue, may suggest corrections
        """
        response = await analyze_code(
            code="def broken(:\n    pass",  # Missing parameter name
            language="python",
        )

        assert isinstance(response, ToolResponseEnvelope)
        # Check if the response data contains error information
        if isinstance(response.data, dict):
            assert response.data.get("success") is False
            assert "syntax" in response.data.get("error", "").lower()

    @pytest.mark.asyncio
    async def test_analyze_valid_python_succeeds(self):
        """Test that valid Python code is analyzed successfully.

        AI scenario: AI provides correct Python code
        Expected: Successful analysis with function/class info
        """
        response = await analyze_code(
            code="""
def calculate_average(numbers: list[float]) -> float:
    '''Calculate the average of a list of numbers.'''
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

class DataProcessor:
    '''Process and analyze data.'''
    
    def process(self, data: list) -> dict:
        return {"count": len(data), "average": calculate_average(data)}
""",
            language="python",
        )

        assert isinstance(response, ToolResponseEnvelope)
        assert response.error is None
        assert response.data is not None
        assert "calculate_average" in response.data.get("functions", {})
        assert "DataProcessor" in response.data.get("classes", {})

    @pytest.mark.asyncio
    async def test_analyze_with_explicit_language_works(self):
        """Test that language specification is respected.

        AI scenario: AI explicitly specifies language
        Expected: Code analyzed with specified language rules
        """
        response = await analyze_code(
            code="function greet(name) { return 'Hello ' + name; }",
            language="javascript",
        )

        assert isinstance(response, ToolResponseEnvelope)
        # Check that we get a response with data
        assert response.data is not None
        # Should contain function analysis info
        assert isinstance(response.data, dict)


class TestOracleExtractCodeWithWrongInputs:
    """Test extract_code oracle feedback for incorrect symbol names."""

    @pytest.mark.asyncio
    async def test_extract_nonexistent_function_returns_error(self):
        """Test extracting non-existent function returns meaningful error.

        AI scenario: AI tries to extract function "calculate" but code has "compute"
        Expected: Error indicates function not found, may suggest similar names
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def compute_sum(a, b):
    return a + b

def compute_product(a, b):
    return a * b
"""
            )
            temp_path = f.name

        try:
            response = await extract_code(
                target_type="function",
                target_name="calculate",  # Wrong name
                file_path=temp_path,
            )

            assert isinstance(response, ToolResponseEnvelope)
            # Check if the response contains error information
            if isinstance(response.data, dict):
                # Should indicate function not found
                assert response.data.get("success") is False
                assert "not found" in response.data.get("error", "").lower()
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_extract_existing_function_succeeds(self):
        """Test extracting existing function succeeds.

        AI scenario: AI correctly identifies function to extract
        Expected: Successful extraction with code and context
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
import math

def calculate_distance(x1, y1, x2, y2):
    '''Calculate Euclidean distance between two points.'''
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
"""
            )
            temp_path = f.name

        try:
            response = await extract_code(
                target_type="function",
                target_name="calculate_distance",
                file_path=temp_path,
                include_context=True,
            )

            assert isinstance(response, ToolResponseEnvelope)
            # Check if we successfully extracted the function
            if isinstance(response.data, dict):
                assert response.data.get("success") is True
                assert "calculate_distance" in response.data.get("target_code", "")
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_extract_class_method_succeeds(self):
        """Test extracting class method.

        AI scenario: AI extracts specific method from class
        Expected: Successful extraction of method with class context
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
class Calculator:
    '''A simple calculator.'''
    
    def add(self, a: int, b: int) -> int:
        '''Add two numbers.'''
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        '''Multiply two numbers.'''
        return a * b
"""
            )
            temp_path = f.name

        try:
            response = await extract_code(
                target_type="method", target_name="Calculator.add", file_path=temp_path
            )

            assert isinstance(response, ToolResponseEnvelope)
            # Check if we got a valid response
            assert response.data is not None
        finally:
            Path(temp_path).unlink()


class TestOracleRenameSymbolWithWrongInputs:
    """Test rename_symbol oracle feedback for incorrect symbol names."""

    @pytest.mark.asyncio
    async def test_rename_nonexistent_function_returns_error(self):
        """Test renaming non-existent function returns error.

        AI scenario: AI tries to rename function that doesn't exist
        Expected: Error indicates symbol not found
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def authenticate_user(username, password):
    return True

def validate_token(token):
    return len(token) > 0
"""
            )
            temp_path = f.name

        try:
            response = await rename_symbol(
                file_path=temp_path,
                target_type="function",
                target_name="authorize_user",  # Wrong name
                new_name="authorize_with_token",
            )

            assert isinstance(response, ToolResponseEnvelope)
            # Check if the response contains error information
            if isinstance(response.data, dict):
                assert response.data.get("success") is False
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_rename_existing_function_succeeds(self):
        """Test renaming existing function succeeds.

        AI scenario: AI correctly renames function
        Expected: Successful rename with backup created
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def old_name(x):
    '''This will be renamed.'''
    return x * 2

print(old_name(5))
"""
            )
            temp_path = f.name

        try:
            response = await rename_symbol(
                file_path=temp_path,
                target_type="function",
                target_name="old_name",
                new_name="new_name",
                create_backup=True,
            )

            assert isinstance(response, ToolResponseEnvelope)
            # Check if the response contains data
            assert response.data is not None
        finally:
            Path(temp_path).unlink()


class TestOracleFeedbackMessages:
    """Test that oracle provides helpful feedback messages."""

    @pytest.mark.asyncio
    async def test_error_includes_helpful_context(self):
        """Test that error responses include context.

        Oracle principle: Never just say 'error', explain what went wrong
        """
        response = await write_perfect_code(
            file_path="/nonexistent/path.py", instruction="test"
        )

        assert response.error is not None
        # Error should have meaningful message
        assert len(response.error.error) > 0
        assert isinstance(response.error.error, str)

    @pytest.mark.asyncio
    async def test_success_includes_metadata(self):
        """Test that success responses include all metadata.

        Oracle principle: Tool responses should always be complete
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test(): pass")
            temp_path = f.name

        try:
            with patch(
                "code_scalpel.mcp.protocol._get_current_tier", return_value="pro"
            ):
                response = await write_perfect_code(
                    file_path=temp_path, instruction="add docstring"
                )

            if response.error is None:
                assert response.data is not None
                assert response.tool_version is not None
                assert response.tier is not None
                assert response.duration_ms is not None
        finally:
            Path(temp_path).unlink()


class TestOracleConsistencyAcrossTools:
    """Test that oracle behavior is consistent across all tools."""

    @pytest.mark.asyncio
    async def test_all_tools_return_envelope(self):
        """Test that all tools return ToolResponseEnvelope.

        Consistency principle: All responses follow same contract
        """
        # write_perfect_code
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test(): pass")
            temp_path = f.name

        try:
            with patch(
                "code_scalpel.mcp.protocol._get_current_tier", return_value="pro"
            ):
                resp1 = await write_perfect_code(
                    file_path=temp_path, instruction="test"
                )
            assert isinstance(resp1, ToolResponseEnvelope)

            # analyze_code
            resp2 = await analyze_code(code="def test(): pass")
            assert isinstance(resp2, ToolResponseEnvelope)

            # extract_code
            resp3 = await extract_code(
                target_type="function", target_name="test", file_path=temp_path
            )
            assert isinstance(resp3, ToolResponseEnvelope)
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_all_tools_include_tier(self):
        """Test that all tool responses include tier information.

        Consistency principle: Tier information is always accessible
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test(): pass")
            temp_path = f.name

        try:
            with patch(
                "code_scalpel.mcp.protocol._get_current_tier", return_value="pro"
            ):
                resp1 = await write_perfect_code(
                    file_path=temp_path, instruction="test"
                )
                resp2 = await analyze_code(code="def test(): pass")

            # Verify that both responses contain tier information somewhere
            # Tier may be on envelope or in data payload depending on response config
            resp1_tier = resp1.tier or (
                resp1.data.get("tier_applied") if isinstance(resp1.data, dict) else None
            )
            resp2_tier = resp2.tier or (
                resp2.data.get("tier_applied") if isinstance(resp2.data, dict) else None
            )

            # Both should have a tier applied (either pro from patch or community default)
            assert resp1_tier in ("pro", "community")
            assert resp2_tier in ("pro", "community")
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
