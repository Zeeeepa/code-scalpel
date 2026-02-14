"""
Tests for File Operation Tools
"""

import pytest
import tempfile
from pathlib import Path

from code_scalpel.core.codegen_bridge import Tier
from code_scalpel.session.codebase_manager import SessionContext
from code_scalpel.tools.file_operations import (
    ViewFileTool,
    CreateFileTool,
    EditFileTool,
    DeleteFileTool,
    RenameFileTool,
    ReplacementEditTool,
    GlobalReplacementEditTool
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


class TestViewFileTool:
    """Test ViewFileTool"""
    
    def test_view_existing_file(self, mock_session, temp_workspace):
        """Test viewing an existing file"""
        # Create a test file
        test_file = temp_workspace / "test.txt"
        test_file.write_text("Hello, World!")
        
        tool = ViewFileTool()
        result = tool._execute_impl(mock_session, file_path="test.txt")
        
        assert result.success
        assert result.data["content"] == "Hello, World!"
        assert result.data["size"] == 13
        assert result.data["lines"] == 1
    
    def test_view_nonexistent_file(self, mock_session):
        """Test viewing a nonexistent file"""
        tool = ViewFileTool()
        result = tool._execute_impl(mock_session, file_path="nonexistent.txt")
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    def test_tier_is_community(self):
        """Test that tool is Community tier"""
        tool = ViewFileTool()
        assert tool.tier == Tier.COMMUNITY


class TestCreateFileTool:
    """Test CreateFileTool"""
    
    def test_create_new_file(self, mock_session, temp_workspace):
        """Test creating a new file"""
        tool = CreateFileTool()
        result = tool._execute_impl(
            mock_session,
            file_path="new_file.txt",
            content="New content"
        )
        
        assert result.success
        assert result.data["created"]
        
        # Verify file was created
        created_file = temp_workspace / "new_file.txt"
        assert created_file.exists()
        assert created_file.read_text() == "New content"
    
    def test_create_file_with_directories(self, mock_session, temp_workspace):
        """Test creating a file in nested directories"""
        tool = CreateFileTool()
        result = tool._execute_impl(
            mock_session,
            file_path="subdir/nested/file.txt",
            content="Nested content"
        )
        
        assert result.success
        
        # Verify file and directories were created
        created_file = temp_workspace / "subdir" / "nested" / "file.txt"
        assert created_file.exists()
        assert created_file.read_text() == "Nested content"
    
    def test_create_existing_file_fails(self, mock_session, temp_workspace):
        """Test that creating an existing file fails"""
        # Create file first
        test_file = temp_workspace / "existing.txt"
        test_file.write_text("Original")
        
        tool = CreateFileTool()
        result = tool._execute_impl(
            mock_session,
            file_path="existing.txt",
            content="New"
        )
        
        assert not result.success
        assert "already exists" in result.error.lower()


class TestEditFileTool:
    """Test EditFileTool"""
    
    def test_edit_existing_file(self, mock_session, temp_workspace):
        """Test editing an existing file"""
        # Create file
        test_file = temp_workspace / "edit_me.txt"
        test_file.write_text("Original content")
        
        tool = EditFileTool()
        result = tool._execute_impl(
            mock_session,
            file_path="edit_me.txt",
            content="Modified content"
        )
        
        assert result.success
        assert result.data["modified"]
        assert test_file.read_text() == "Modified content"
    
    def test_edit_nonexistent_file_fails(self, mock_session):
        """Test that editing nonexistent file fails"""
        tool = EditFileTool()
        result = tool._execute_impl(
            mock_session,
            file_path="nonexistent.txt",
            content="Content"
        )
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    def test_requires_transaction(self):
        """Test that tool requires transaction"""
        tool = EditFileTool()
        assert tool.requires_transaction


class TestDeleteFileTool:
    """Test DeleteFileTool"""
    
    def test_delete_existing_file(self, mock_session, temp_workspace):
        """Test deleting an existing file"""
        # Create file
        test_file = temp_workspace / "delete_me.txt"
        test_file.write_text("To be deleted")
        
        tool = DeleteFileTool()
        result = tool._execute_impl(mock_session, file_path="delete_me.txt")
        
        assert result.success
        assert result.data["deleted"]
        assert not test_file.exists()
    
    def test_delete_nonexistent_file_fails(self, mock_session):
        """Test that deleting nonexistent file fails"""
        tool = DeleteFileTool()
        result = tool._execute_impl(mock_session, file_path="nonexistent.txt")
        
        assert not result.success
        assert "not found" in result.error.lower()


class TestRenameFileTool:
    """Test RenameFileTool"""
    
    def test_rename_file(self, mock_session, temp_workspace):
        """Test renaming a file"""
        # Create file
        old_file = temp_workspace / "old_name.txt"
        old_file.write_text("Content")
        
        tool = RenameFileTool()
        result = tool._execute_impl(
            mock_session,
            old_path="old_name.txt",
            new_path="new_name.txt"
        )
        
        assert result.success
        assert result.data["renamed"]
        assert not old_file.exists()
        
        new_file = temp_workspace / "new_name.txt"
        assert new_file.exists()
        assert new_file.read_text() == "Content"
    
    def test_rename_to_subdirectory(self, mock_session, temp_workspace):
        """Test renaming file to subdirectory"""
        # Create file
        old_file = temp_workspace / "file.txt"
        old_file.write_text("Content")
        
        tool = RenameFileTool()
        result = tool._execute_impl(
            mock_session,
            old_path="file.txt",
            new_path="subdir/file.txt"
        )
        
        assert result.success
        
        new_file = temp_workspace / "subdir" / "file.txt"
        assert new_file.exists()
    
    def test_rename_nonexistent_file_fails(self, mock_session):
        """Test that renaming nonexistent file fails"""
        tool = RenameFileTool()
        result = tool._execute_impl(
            mock_session,
            old_path="nonexistent.txt",
            new_path="new.txt"
        )
        
        assert not result.success


class TestReplacementEditTool:
    """Test ReplacementEditTool"""
    
    def test_replace_text(self, mock_session, temp_workspace):
        """Test replacing text in a file"""
        # Create file
        test_file = temp_workspace / "replace.txt"
        test_file.write_text("Hello World! Hello again!")
        
        tool = ReplacementEditTool()
        result = tool._execute_impl(
            mock_session,
            file_path="replace.txt",
            old_text="Hello",
            new_text="Hi"
        )
        
        assert result.success
        assert result.data["replacements"] == 2
        assert test_file.read_text() == "Hi World! Hi again!"
    
    def test_replace_text_not_found(self, mock_session, temp_workspace):
        """Test replacing text that doesn't exist"""
        test_file = temp_workspace / "replace.txt"
        test_file.write_text("Hello World!")
        
        tool = ReplacementEditTool()
        result = tool._execute_impl(
            mock_session,
            file_path="replace.txt",
            old_text="Goodbye",
            new_text="Hi"
        )
        
        assert not result.success
        assert "not found" in result.error.lower()


class TestGlobalReplacementEditTool:
    """Test GlobalReplacementEditTool"""
    
    def test_global_replace(self, mock_session, temp_workspace):
        """Test global replacement across multiple files"""
        # Create multiple files
        (temp_workspace / "file1.py").write_text("def old_func(): pass")
        (temp_workspace / "file2.py").write_text("old_func()")
        (temp_workspace / "file3.txt").write_text("old_func()")
        
        tool = GlobalReplacementEditTool()
        result = tool._execute_impl(
            mock_session,
            pattern="**/*.py",
            old_text="old_func",
            new_text="new_func"
        )
        
        assert result.success
        assert result.data["files_modified"] == 2
        assert result.data["total_replacements"] == 2
        
        # Verify replacements
        assert "new_func" in (temp_workspace / "file1.py").read_text()
        assert "new_func" in (temp_workspace / "file2.py").read_text()
        assert "old_func" in (temp_workspace / "file3.txt").read_text()  # Not replaced
    
    def test_global_replace_no_matches(self, mock_session, temp_workspace):
        """Test global replacement with no matches"""
        (temp_workspace / "file.py").write_text("content")
        
        tool = GlobalReplacementEditTool()
        result = tool._execute_impl(
            mock_session,
            pattern="**/*.py",
            old_text="nonexistent",
            new_text="new"
        )
        
        assert result.success
        assert result.data["files_modified"] == 0
    
    def test_tier_unified_from_enterprise(self):
        """Test that tool is unified from Enterprise to Community"""
        tool = GlobalReplacementEditTool()
        assert tool.tier == Tier.COMMUNITY
        assert tool.requires_transaction


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

