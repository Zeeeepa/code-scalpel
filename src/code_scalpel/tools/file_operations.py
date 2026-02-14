"""
File Operation Tools

Implements core file operations with tier unification (all Community tier).
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

from code_scalpel.core.codegen_bridge import Tier
from code_scalpel.adapters.codegen_tool_adapter import (
    CodegenToolAdapter,
    ToolResult
)
from code_scalpel.session.codebase_manager import SessionContext

logger = logging.getLogger(__name__)


class ViewFileTool(CodegenToolAdapter):
    """
    View file contents.
    
    Tier: Community (unified from all tiers)
    Transaction: No
    """
    
    def __init__(self):
        super().__init__(
            name="view_file",
            tier=Tier.COMMUNITY,
            requires_transaction=False,
            description="View the contents of a file"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "file_path" not in kwargs:
            return "Missing required parameter: file_path"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        file_path = Path(kwargs["file_path"])
        
        try:
            # Read file through codebase
            full_path = session.workspace_path / file_path
            
            if not full_path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {file_path}"
                )
            
            content = full_path.read_text()
            
            return ToolResult(
                success=True,
                data={
                    "file_path": str(file_path),
                    "content": content,
                    "size": len(content),
                    "lines": content.count('\n') + 1
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to read file: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to view"
                }
            },
            "required": ["file_path"]
        }


class CreateFileTool(CodegenToolAdapter):
    """
    Create a new file.
    
    Tier: Community (unified from all tiers)
    Transaction: Optional
    """
    
    def __init__(self):
        super().__init__(
            name="create_file",
            tier=Tier.COMMUNITY,
            requires_transaction=False,
            description="Create a new file with specified content"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "file_path" not in kwargs:
            return "Missing required parameter: file_path"
        if "content" not in kwargs:
            return "Missing required parameter: content"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        file_path = Path(kwargs["file_path"])
        content = kwargs["content"]
        
        try:
            full_path = session.workspace_path / file_path
            
            # Check if file already exists
            if full_path.exists():
                return ToolResult(
                    success=False,
                    error=f"File already exists: {file_path}"
                )
            
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            full_path.write_text(content)
            
            return ToolResult(
                success=True,
                data={
                    "file_path": str(file_path),
                    "size": len(content),
                    "created": True
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to create file: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path where the file should be created"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }


class EditFileTool(CodegenToolAdapter):
    """
    Edit an existing file.
    
    Tier: Community (unified from Pro)
    Transaction: Mandatory
    """
    
    def __init__(self):
        super().__init__(
            name="edit_file",
            tier=Tier.COMMUNITY,
            requires_transaction=True,
            description="Edit an existing file with new content"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "file_path" not in kwargs:
            return "Missing required parameter: file_path"
        if "content" not in kwargs:
            return "Missing required parameter: content"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        file_path = Path(kwargs["file_path"])
        content = kwargs["content"]
        
        try:
            full_path = session.workspace_path / file_path
            
            if not full_path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {file_path}"
                )
            
            # Store original content for rollback
            original_content = full_path.read_text()
            
            # Write new content
            full_path.write_text(content)
            
            return ToolResult(
                success=True,
                data={
                    "file_path": str(file_path),
                    "original_size": len(original_content),
                    "new_size": len(content),
                    "modified": True
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to edit file: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to edit"
                },
                "content": {
                    "type": "string",
                    "description": "New content for the file"
                }
            },
            "required": ["file_path", "content"]
        }


class DeleteFileTool(CodegenToolAdapter):
    """
    Delete a file.
    
    Tier: Community (unified from Pro)
    Transaction: Mandatory
    """
    
    def __init__(self):
        super().__init__(
            name="delete_file",
            tier=Tier.COMMUNITY,
            requires_transaction=True,
            description="Delete a file"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "file_path" not in kwargs:
            return "Missing required parameter: file_path"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        file_path = Path(kwargs["file_path"])
        
        try:
            full_path = session.workspace_path / file_path
            
            if not full_path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {file_path}"
                )
            
            # Delete the file
            full_path.unlink()
            
            return ToolResult(
                success=True,
                data={
                    "file_path": str(file_path),
                    "deleted": True
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to delete file: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to delete"
                }
            },
            "required": ["file_path"]
        }


class RenameFileTool(CodegenToolAdapter):
    """
    Rename a file.
    
    Tier: Community (unified from Pro)
    Transaction: Mandatory
    """
    
    def __init__(self):
        super().__init__(
            name="rename_file",
            tier=Tier.COMMUNITY,
            requires_transaction=True,
            description="Rename a file"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "old_path" not in kwargs:
            return "Missing required parameter: old_path"
        if "new_path" not in kwargs:
            return "Missing required parameter: new_path"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        old_path = Path(kwargs["old_path"])
        new_path = Path(kwargs["new_path"])
        
        try:
            full_old_path = session.workspace_path / old_path
            full_new_path = session.workspace_path / new_path
            
            if not full_old_path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {old_path}"
                )
            
            if full_new_path.exists():
                return ToolResult(
                    success=False,
                    error=f"Target file already exists: {new_path}"
                )
            
            # Create parent directories if needed
            full_new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Rename the file
            full_old_path.rename(full_new_path)
            
            return ToolResult(
                success=True,
                data={
                    "old_path": str(old_path),
                    "new_path": str(new_path),
                    "renamed": True
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to rename file: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "old_path": {
                    "type": "string",
                    "description": "Current path of the file"
                },
                "new_path": {
                    "type": "string",
                    "description": "New path for the file"
                }
            },
            "required": ["old_path", "new_path"]
        }


class ReplacementEditTool(CodegenToolAdapter):
    """
    Replace text in a file.
    
    Tier: Community (unified from Pro)
    Transaction: Optional
    """
    
    def __init__(self):
        super().__init__(
            name="replacement_edit",
            tier=Tier.COMMUNITY,
            requires_transaction=False,
            description="Replace text in a file"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "file_path" not in kwargs:
            return "Missing required parameter: file_path"
        if "old_text" not in kwargs:
            return "Missing required parameter: old_text"
        if "new_text" not in kwargs:
            return "Missing required parameter: new_text"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        file_path = Path(kwargs["file_path"])
        old_text = kwargs["old_text"]
        new_text = kwargs["new_text"]
        
        try:
            full_path = session.workspace_path / file_path
            
            if not full_path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {file_path}"
                )
            
            content = full_path.read_text()
            
            if old_text not in content:
                return ToolResult(
                    success=False,
                    error=f"Text not found in file: {old_text}"
                )
            
            # Replace text
            new_content = content.replace(old_text, new_text)
            full_path.write_text(new_content)
            
            return ToolResult(
                success=True,
                data={
                    "file_path": str(file_path),
                    "replacements": content.count(old_text),
                    "modified": True
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to replace text: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file"
                },
                "old_text": {
                    "type": "string",
                    "description": "Text to replace"
                },
                "new_text": {
                    "type": "string",
                    "description": "Replacement text"
                }
            },
            "required": ["file_path", "old_text", "new_text"]
        }


class GlobalReplacementEditTool(CodegenToolAdapter):
    """
    Replace text across multiple files.
    
    Tier: Community (unified from Enterprise)
    Transaction: Mandatory
    """
    
    def __init__(self):
        super().__init__(
            name="global_replacement_edit",
            tier=Tier.COMMUNITY,
            requires_transaction=True,
            description="Replace text across multiple files"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "pattern" not in kwargs:
            return "Missing required parameter: pattern"
        if "old_text" not in kwargs:
            return "Missing required parameter: old_text"
        if "new_text" not in kwargs:
            return "Missing required parameter: new_text"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        pattern = kwargs["pattern"]  # e.g., "**/*.py"
        old_text = kwargs["old_text"]
        new_text = kwargs["new_text"]
        
        try:
            files_modified = []
            total_replacements = 0
            
            # Find matching files
            for file_path in session.workspace_path.glob(pattern):
                if file_path.is_file():
                    content = file_path.read_text()
                    
                    if old_text in content:
                        new_content = content.replace(old_text, new_text)
                        file_path.write_text(new_content)
                        
                        count = content.count(old_text)
                        files_modified.append({
                            "path": str(file_path.relative_to(session.workspace_path)),
                            "replacements": count
                        })
                        total_replacements += count
            
            return ToolResult(
                success=True,
                data={
                    "pattern": pattern,
                    "files_modified": len(files_modified),
                    "total_replacements": total_replacements,
                    "files": files_modified
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to perform global replacement: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern for files (e.g., '**/*.py')"
                },
                "old_text": {
                    "type": "string",
                    "description": "Text to replace"
                },
                "new_text": {
                    "type": "string",
                    "description": "Replacement text"
                }
            },
            "required": ["pattern", "old_text", "new_text"]
        }

