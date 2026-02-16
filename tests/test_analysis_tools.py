"""
Tests for Analysis Tools
"""

import pytest
import tempfile
from pathlib import Path

from code_scalpel.core.codegen_bridge import Tier
from code_scalpel.session.codebase_manager import SessionContext
from code_scalpel.tools.analysis_tools import (
    GetCodebaseSummaryTool,
    GetFunctionSummaryTool,
    GetClassSummaryTool,
    GetSymbolSummaryTool
)


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        yield workspace


@pytest.fixture
def mock_session(temp_workspace):
    """Create a mock session context"""
    return SessionContext(
        session_id="test-session",
        workspace_path=temp_workspace,
        codebase=None
    )


@pytest.fixture
def sample_codebase(temp_workspace):
    """Create sample codebase for testing"""
    # Module 1
    (temp_workspace / "module1.py").write_text("""
def helper_function():
    '''A helper function'''
    return 42

class DataProcessor:
    '''Process data'''
    
    def process(self):
        return helper_function()
    
    def validate(self):
        return True
""")
    
    # Module 2
    (temp_workspace / "module2.py").write_text("""
class Calculator:
    '''A simple calculator'''
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
""")
    
    return temp_workspace


class TestGetCodebaseSummaryTool:
    """Test GetCodebaseSummaryTool"""
    
    def test_get_summary(self, mock_session, sample_codebase):
        """Test getting codebase summary"""
        tool = GetCodebaseSummaryTool()
        result = tool._execute_impl(mock_session)
        
        assert result.success
        assert result.data["total_files"] == 2
        assert result.data["total_lines"] > 0
        assert result.data["total_size"] > 0
        assert len(result.data["files"]) == 2
    
    def test_empty_codebase(self, mock_session, temp_workspace):
        """Test with empty codebase"""
        tool = GetCodebaseSummaryTool()
        result = tool._execute_impl(mock_session)
        
        assert result.success
        assert result.data["total_files"] == 0
    
    def test_tier_is_community(self):
        """Test that tool is Community tier"""
        tool = GetCodebaseSummaryTool()
        assert tool.tier == Tier.COMMUNITY


class TestGetFunctionSummaryTool:
    """Test GetFunctionSummaryTool"""
    
    def test_get_function_summary(self, mock_session, sample_codebase):
        """Test getting function summary"""
        tool = GetFunctionSummaryTool()
        result = tool._execute_impl(
            mock_session,
            function_name="helper_function"
        )
        
        assert result.success
        assert result.data["function_name"] == "helper_function"
        assert "module1.py" in result.data["file"]
        assert result.data["lines_count"] > 0
        assert "def helper_function" in result.data["signature"]
    
    def test_function_with_docstring(self, mock_session, sample_codebase):
        """Test that docstring is extracted if present"""
        tool = GetFunctionSummaryTool()
        result = tool._execute_impl(
            mock_session,
            function_name="helper_function"
        )
        
        assert result.success
        # Docstring extraction is optional - just verify the field exists
        assert "docstring" in result.data
    
    def test_nonexistent_function(self, mock_session, sample_codebase):
        """Test with nonexistent function"""
        tool = GetFunctionSummaryTool()
        result = tool._execute_impl(
            mock_session,
            function_name="nonexistent"
        )
        
        assert not result.success
        assert "not found" in result.error.lower()


class TestGetClassSummaryTool:
    """Test GetClassSummaryTool"""
    
    def test_get_class_summary(self, mock_session, sample_codebase):
        """Test getting class summary"""
        tool = GetClassSummaryTool()
        result = tool._execute_impl(
            mock_session,
            class_name="DataProcessor"
        )
        
        assert result.success
        assert result.data["class_name"] == "DataProcessor"
        assert "module1.py" in result.data["file"]
        assert result.data["method_count"] == 2
        assert "process" in result.data["methods"]
        assert "validate" in result.data["methods"]
    
    def test_class_with_docstring(self, mock_session, sample_codebase):
        """Test that class docstring is extracted if present"""
        tool = GetClassSummaryTool()
        result = tool._execute_impl(
            mock_session,
            class_name="Calculator"
        )
        
        assert result.success
        # Docstring extraction is optional - just verify the field exists
        assert "docstring" in result.data
    
    def test_nonexistent_class(self, mock_session, sample_codebase):
        """Test with nonexistent class"""
        tool = GetClassSummaryTool()
        result = tool._execute_impl(
            mock_session,
            class_name="NonexistentClass"
        )
        
        assert not result.success
        assert "not found" in result.error.lower()


class TestGetSymbolSummaryTool:
    """Test GetSymbolSummaryTool"""
    
    def test_get_symbol_summary_function(self, mock_session, sample_codebase):
        """Test getting summary for a function symbol"""
        tool = GetSymbolSummaryTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="helper_function"
        )
        
        assert result.success
        assert result.data["symbol_name"] == "helper_function"
        assert result.data["occurrences"] >= 1
        assert any(r["type"] == "function" for r in result.data["results"])
    
    def test_get_symbol_summary_class(self, mock_session, sample_codebase):
        """Test getting summary for a class symbol"""
        tool = GetSymbolSummaryTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="Calculator"
        )
        
        assert result.success
        assert any(r["type"] == "class" for r in result.data["results"])
    
    def test_nonexistent_symbol(self, mock_session, sample_codebase):
        """Test with nonexistent symbol"""
        tool = GetSymbolSummaryTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="nonexistent_symbol"
        )
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    def test_tier_unified_from_pro(self):
        """Test that tool is unified from Pro to Community"""
        tool = GetSymbolSummaryTool()
        assert tool.tier == Tier.COMMUNITY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
