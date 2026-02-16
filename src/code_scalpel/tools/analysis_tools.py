"""
Analysis Tools

Implements code analysis tools with tier unification (all Community tier).
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


class GetCodebaseSummaryTool(CodegenToolAdapter):
    """
    Get a summary of the entire codebase.
    
    Tier: Community
    Transaction: No
    """
    
    def __init__(self):
        super().__init__(
            name="get_codebase_summary",
            tier=Tier.COMMUNITY,
            requires_transaction=False,
            description="Get a summary of the entire codebase"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        return None  # No required parameters
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        file_pattern = kwargs.get("file_pattern", "**/*.py")
        
        try:
            files = []
            total_lines = 0
            total_size = 0
            
            for file_path in session.workspace_path.glob(file_pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text()
                        lines = len(content.split('\n'))
                        size = len(content)
                        
                        files.append({
                            "path": str(file_path.relative_to(session.workspace_path)),
                            "lines": lines,
                            "size": size
                        })
                        
                        total_lines += lines
                        total_size += size
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {e}")
                        continue
            
            return ToolResult(
                success=True,
                data={
                    "total_files": len(files),
                    "total_lines": total_lines,
                    "total_size": total_size,
                    "files": files
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to get codebase summary: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern for files (default: **/*.py)"
                }
            }
        }


class GetFunctionSummaryTool(CodegenToolAdapter):
    """
    Get a summary of a specific function.
    
    Tier: Community
    Transaction: No
    """
    
    def __init__(self):
        super().__init__(
            name="get_function_summary",
            tier=Tier.COMMUNITY,
            requires_transaction=False,
            description="Get a summary of a specific function"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "function_name" not in kwargs:
            return "Missing required parameter: function_name"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        function_name = kwargs["function_name"]
        file_pattern = kwargs.get("file_pattern", "**/*.py")
        
        try:
            # Find the function
            for file_path in session.workspace_path.glob(file_pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines):
                            if f"def {function_name}" in line:
                                # Extract function body
                                func_lines = [line]
                                indent = len(line) - len(line.lstrip())
                                
                                for j in range(i + 1, len(lines)):
                                    next_line = lines[j]
                                    if next_line.strip() and not next_line.strip().startswith('#'):
                                        next_indent = len(next_line) - len(next_line.lstrip())
                                        if next_indent <= indent:
                                            break
                                    func_lines.append(next_line)
                                
                                func_body = '\n'.join(func_lines)
                                
                                # Extract docstring if present
                                docstring = None
                                if '"""' in func_body or "'''" in func_body:
                                    doc_start = func_body.find('"""') or func_body.find("'''")
                                    if doc_start != -1:
                                        doc_end = func_body.find('"""', doc_start + 3) or func_body.find("'''", doc_start + 3)
                                        if doc_end != -1:
                                            docstring = func_body[doc_start:doc_end + 3].strip()
                                
                                return ToolResult(
                                    success=True,
                                    data={
                                        "function_name": function_name,
                                        "file": str(file_path.relative_to(session.workspace_path)),
                                        "line": i + 1,
                                        "lines_count": len(func_lines),
                                        "docstring": docstring,
                                        "signature": line.strip()
                                    }
                                )
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {e}")
                        continue
            
            return ToolResult(
                success=False,
                error=f"Function '{function_name}' not found"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to get function summary: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "function_name": {
                    "type": "string",
                    "description": "Name of the function"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern for files (default: **/*.py)"
                }
            },
            "required": ["function_name"]
        }


class GetClassSummaryTool(CodegenToolAdapter):
    """
    Get a summary of a specific class.
    
    Tier: Community
    Transaction: No
    """
    
    def __init__(self):
        super().__init__(
            name="get_class_summary",
            tier=Tier.COMMUNITY,
            requires_transaction=False,
            description="Get a summary of a specific class"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "class_name" not in kwargs:
            return "Missing required parameter: class_name"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        class_name = kwargs["class_name"]
        file_pattern = kwargs.get("file_pattern", "**/*.py")
        
        try:
            # Find the class
            for file_path in session.workspace_path.glob(file_pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines):
                            if f"class {class_name}" in line:
                                # Extract class body and count methods
                                methods = []
                                indent = len(line) - len(line.lstrip())
                                
                                for j in range(i + 1, len(lines)):
                                    next_line = lines[j]
                                    if next_line.strip().startswith('def '):
                                        method_name = next_line.strip().split('(')[0].replace('def ', '')
                                        methods.append(method_name)
                                    elif next_line.strip() and not next_line.strip().startswith('#'):
                                        next_indent = len(next_line) - len(next_line.lstrip())
                                        if next_indent <= indent and next_line.strip():
                                            break
                                
                                # Extract docstring
                                docstring = None
                                if i + 1 < len(lines):
                                    next_lines = '\n'.join(lines[i+1:i+10])
                                    if '"""' in next_lines or "'''" in next_lines:
                                        doc_start = next_lines.find('"""') or next_lines.find("'''")
                                        if doc_start != -1:
                                            doc_end = next_lines.find('"""', doc_start + 3) or next_lines.find("'''", doc_start + 3)
                                            if doc_end != -1:
                                                docstring = next_lines[doc_start:doc_end + 3].strip()
                                
                                return ToolResult(
                                    success=True,
                                    data={
                                        "class_name": class_name,
                                        "file": str(file_path.relative_to(session.workspace_path)),
                                        "line": i + 1,
                                        "methods": methods,
                                        "method_count": len(methods),
                                        "docstring": docstring,
                                        "signature": line.strip()
                                    }
                                )
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {e}")
                        continue
            
            return ToolResult(
                success=False,
                error=f"Class '{class_name}' not found"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to get class summary: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "class_name": {
                    "type": "string",
                    "description": "Name of the class"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern for files (default: **/*.py)"
                }
            },
            "required": ["class_name"]
        }


class GetSymbolSummaryTool(CodegenToolAdapter):
    """
    Get a summary of any symbol (function, class, variable).
    
    Tier: Community (unified from Pro)
    Transaction: No
    """
    
    def __init__(self):
        super().__init__(
            name="get_symbol_summary",
            tier=Tier.COMMUNITY,
            requires_transaction=False,
            description="Get a summary of any symbol"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "symbol_name" not in kwargs:
            return "Missing required parameter: symbol_name"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        symbol_name = kwargs["symbol_name"]
        file_pattern = kwargs.get("file_pattern", "**/*.py")
        
        try:
            results = []
            
            # Search for symbol
            for file_path in session.workspace_path.glob(file_pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines):
                            # Check for various symbol types
                            symbol_type = None
                            if f"def {symbol_name}" in line:
                                symbol_type = "function"
                            elif f"class {symbol_name}" in line:
                                symbol_type = "class"
                            elif f"{symbol_name} =" in line:
                                symbol_type = "variable"
                            
                            if symbol_type:
                                results.append({
                                    "file": str(file_path.relative_to(session.workspace_path)),
                                    "line": i + 1,
                                    "type": symbol_type,
                                    "context": line.strip()
                                })
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {e}")
                        continue
            
            if not results:
                return ToolResult(
                    success=False,
                    error=f"Symbol '{symbol_name}' not found"
                )
            
            return ToolResult(
                success=True,
                data={
                    "symbol_name": symbol_name,
                    "occurrences": len(results),
                    "results": results
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to get symbol summary: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol_name": {
                    "type": "string",
                    "description": "Name of the symbol"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern for files (default: **/*.py)"
                }
            },
            "required": ["symbol_name"]
        }

