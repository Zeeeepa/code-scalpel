"""
Tests for Symbol Operation Tools
"""

import pytest
import tempfile
from pathlib import Path

from code_scalpel.core.codegen_bridge import Tier
from code_scalpel.session.codebase_manager import SessionContext
from code_scalpel.tools.symbol_operations import (
    FindSymbolTool,
    GetSymbolReferencesTool,
    RevealSymbolTool,
    MoveSymbolTool
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
def sample_python_files(temp_workspace):
    """Create sample Python files for testing"""
    # File 1: Contains function definition
    file1 = temp_workspace / "module1.py"
    file1.write_text("""
def my_function():
    '''A sample function'''
    return 42

class MyClass:
    def method(self):
        return my_function()
""")
    
    # File 2: Uses the function
    file2 = temp_workspace / "module2.py"
    file2.write_text("""
from module1 import my_function

def another_function():
    result = my_function()
    return result * 2
""")
    
    return file1, file2


class TestFindSymbolTool:
    """Test FindSymbolTool"""
    
    def test_find_function(self, mock_session, sample_python_files):
        """Test finding a function definition"""
        tool = FindSymbolTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="my_function"
        )
        
        assert result.success
        assert result.data["matches"] == 1
        assert result.data["results"][0]["type"] == "function"
        assert "module1.py" in result.data["results"][0]["file"]
    
    def test_find_class(self, mock_session, sample_python_files):
        """Test finding a class definition"""
        tool = FindSymbolTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="MyClass"
        )
        
        assert result.success
        assert result.data["matches"] == 1
        assert result.data["results"][0]["type"] == "class"
    
    def test_find_nonexistent_symbol(self, mock_session, sample_python_files):
        """Test finding a symbol that doesn't exist"""
        tool = FindSymbolTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="nonexistent_symbol"
        )
        
        assert result.success
        assert result.data["matches"] == 0
    
    def test_tier_is_community(self):
        """Test that tool is Community tier"""
        tool = FindSymbolTool()
        assert tool.tier == Tier.COMMUNITY


class TestGetSymbolReferencesTool:
    """Test GetSymbolReferencesTool"""
    
    def test_get_references(self, mock_session, sample_python_files):
        """Test getting all references to a symbol"""
        tool = GetSymbolReferencesTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="my_function"
        )
        
        assert result.success
        assert result.data["total_references"] >= 3  # definition + 2 usages
        
        # Check usage types
        usage_types = [ref["usage_type"] for ref in result.data["references"]]
        assert "definition" in usage_types
        assert "call" in usage_types or "reference" in usage_types
    
    def test_classify_usage_types(self, mock_session, sample_python_files):
        """Test that usage types are classified correctly"""
        tool = GetSymbolReferencesTool()
        
        # Test different usage patterns
        assert tool._classify_usage("def my_function():", "my_function") == "definition"
        assert tool._classify_usage("from module import my_function", "my_function") == "import"
        assert tool._classify_usage("result = my_function()", "my_function") == "call"
        assert tool._classify_usage("x = my_function", "my_function") == "reference"
    
    def test_tier_unified_from_pro(self):
        """Test that tool is unified from Pro to Community"""
        tool = GetSymbolReferencesTool()
        assert tool.tier == Tier.COMMUNITY


class TestRevealSymbolTool:
    """Test RevealSymbolTool"""
    
    def test_reveal_function(self, mock_session, sample_python_files):
        """Test revealing a function with context"""
        tool = RevealSymbolTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="my_function",
            context_lines=2
        )
        
        assert result.success
        assert result.data["symbol_name"] == "my_function"
        assert "module1.py" in result.data["file"]
        assert "def my_function" in result.data["definition"]
        assert result.data["context"] is not None
    
    def test_reveal_with_context(self, mock_session, sample_python_files):
        """Test that context includes surrounding lines"""
        tool = RevealSymbolTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="my_function",
            context_lines=5
        )
        
        assert result.success
        context = result.data["context"]
        assert "def my_function" in context
        assert "return 42" in context
    
    def test_reveal_nonexistent_symbol(self, mock_session, sample_python_files):
        """Test revealing a symbol that doesn't exist"""
        tool = RevealSymbolTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="nonexistent_symbol"
        )
        
        assert not result.success
        assert "not found" in result.error.lower()


class TestMoveSymbolTool:
    """Test MoveSymbolTool"""
    
    def test_move_function(self, mock_session, temp_workspace):
        """Test moving a function to another file"""
        # Create source file
        source = temp_workspace / "source.py"
        source.write_text("""
def function_to_move():
    return 42

def other_function():
    return 100
""")
        
        tool = MoveSymbolTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="function_to_move",
            source_file="source.py",
            target_file="target.py"
        )
        
        assert result.success
        assert result.data["moved"]
        
        # Verify function was removed from source
        source_content = source.read_text()
        assert "function_to_move" not in source_content
        assert "other_function" in source_content
        
        # Verify function was added to target
        target = temp_workspace / "target.py"
        assert target.exists()
        target_content = target.read_text()
        assert "function_to_move" in target_content
    
    def test_move_to_existing_file(self, mock_session, temp_workspace):
        """Test moving a function to an existing file"""
        # Create source file
        source = temp_workspace / "source.py"
        source.write_text("""
def function_to_move():
    return 42
""")
        
        # Create target file
        target = temp_workspace / "target.py"
        target.write_text("""
def existing_function():
    return 100
""")
        
        tool = MoveSymbolTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="function_to_move",
            source_file="source.py",
            target_file="target.py"
        )
        
        assert result.success
        
        # Verify both functions in target
        target_content = target.read_text()
        assert "existing_function" in target_content
        assert "function_to_move" in target_content
    
    def test_move_nonexistent_symbol(self, mock_session, temp_workspace):
        """Test moving a symbol that doesn't exist"""
        source = temp_workspace / "source.py"
        source.write_text("def some_function(): pass")
        
        tool = MoveSymbolTool()
        result = tool._execute_impl(
            mock_session,
            symbol_name="nonexistent",
            source_file="source.py",
            target_file="target.py"
        )
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    def test_tier_unified_from_enterprise(self):
        """Test that tool is unified from Enterprise to Community"""
        tool = MoveSymbolTool()
        assert tool.tier == Tier.COMMUNITY
        assert tool.requires_transaction


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

