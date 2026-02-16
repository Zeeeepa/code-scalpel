"""
Symbol Operation Tools

Implements symbol-level operations with tier unification (all Community tier).
Uses graph-sitter for AST parsing and symbol resolution.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from code_scalpel.core.codegen_bridge import Tier
from code_scalpel.adapters.codegen_tool_adapter import (
    CodegenToolAdapter,
    ToolResult
)
from code_scalpel.session.codebase_manager import SessionContext

logger = logging.getLogger(__name__)


class FindSymbolTool(CodegenToolAdapter):
    """
    Find symbol definitions in the codebase.
    
    Tier: Community
    Transaction: No
    """
    
    def __init__(self):
        super().__init__(
            name="find_symbol",
            tier=Tier.COMMUNITY,
            requires_transaction=False,
            description="Find symbol definitions in the codebase"
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
            
            # Search for symbol in files matching pattern
            for file_path in session.workspace_path.glob(file_pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text()
                        
                        # Simple pattern matching for now
                        # In production, would use graph-sitter AST parsing
                        lines = content.split('\n')
                        for line_num, line in enumerate(lines, 1):
                            # Look for function/class definitions
                            if f"def {symbol_name}" in line or f"class {symbol_name}" in line:
                                results.append({
                                    "file": str(file_path.relative_to(session.workspace_path)),
                                    "line": line_num,
                                    "context": line.strip(),
                                    "type": "function" if "def" in line else "class"
                                })
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {e}")
                        continue
            
            return ToolResult(
                success=True,
                data={
                    "symbol_name": symbol_name,
                    "matches": len(results),
                    "results": results
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to find symbol: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol_name": {
                    "type": "string",
                    "description": "Name of the symbol to find"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern for files to search (default: **/*.py)"
                }
            },
            "required": ["symbol_name"]
        }


class GetSymbolReferencesTool(CodegenToolAdapter):
    """
    Get all references to a symbol.
    
    Tier: Community (unified from Pro)
    Transaction: No
    """
    
    def __init__(self):
        super().__init__(
            name="get_symbol_references",
            tier=Tier.COMMUNITY,
            requires_transaction=False,
            description="Get all references to a symbol"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "symbol_name" not in kwargs:
            return "Missing required parameter: symbol_name"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        symbol_name = kwargs["symbol_name"]
        file_pattern = kwargs.get("file_pattern", "**/*.py")
        
        try:
            references = []
            
            # Search for symbol usage in files
            for file_path in session.workspace_path.glob(file_pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text()
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            # Look for symbol usage (simple pattern matching)
                            if symbol_name in line:
                                references.append({
                                    "file": str(file_path.relative_to(session.workspace_path)),
                                    "line": line_num,
                                    "context": line.strip(),
                                    "usage_type": self._classify_usage(line, symbol_name)
                                })
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {e}")
                        continue
            
            return ToolResult(
                success=True,
                data={
                    "symbol_name": symbol_name,
                    "total_references": len(references),
                    "references": references
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to get symbol references: {str(e)}"
            )
    
    def _classify_usage(self, line: str, symbol: str) -> str:
        """Classify how the symbol is used in the line"""
        if f"def {symbol}" in line or f"class {symbol}" in line:
            return "definition"
        elif f"import {symbol}" in line or f"from {symbol}" in line:
            return "import"
        elif f"{symbol}(" in line:
            return "call"
        else:
            return "reference"
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol_name": {
                    "type": "string",
                    "description": "Name of the symbol to find references for"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern for files to search (default: **/*.py)"
                }
            },
            "required": ["symbol_name"]
        }


class RevealSymbolTool(CodegenToolAdapter):
    """
    Reveal symbol definition with context.
    
    Tier: Community
    Transaction: No
    """
    
    def __init__(self):
        super().__init__(
            name="reveal_symbol",
            tier=Tier.COMMUNITY,
            requires_transaction=False,
            description="Reveal symbol definition with surrounding context"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "symbol_name" not in kwargs:
            return "Missing required parameter: symbol_name"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        symbol_name = kwargs["symbol_name"]
        file_pattern = kwargs.get("file_pattern", "**/*.py")
        context_lines = kwargs.get("context_lines", 5)
        
        try:
            # Find the symbol first
            for file_path in session.workspace_path.glob(file_pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text()
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            if f"def {symbol_name}" in line or f"class {symbol_name}" in line:
                                # Found the definition, get context
                                start = max(0, line_num - context_lines - 1)
                                end = min(len(lines), line_num + context_lines)
                                
                                context = '\n'.join(lines[start:end])
                                
                                return ToolResult(
                                    success=True,
                                    data={
                                        "symbol_name": symbol_name,
                                        "file": str(file_path.relative_to(session.workspace_path)),
                                        "line": line_num,
                                        "definition": line.strip(),
                                        "context": context,
                                        "context_start_line": start + 1,
                                        "context_end_line": end
                                    }
                                )
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {e}")
                        continue
            
            # Symbol not found
            return ToolResult(
                success=False,
                error=f"Symbol '{symbol_name}' not found in codebase"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to reveal symbol: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol_name": {
                    "type": "string",
                    "description": "Name of the symbol to reveal"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern for files to search (default: **/*.py)"
                },
                "context_lines": {
                    "type": "integer",
                    "description": "Number of context lines before/after (default: 5)"
                }
            },
            "required": ["symbol_name"]
        }


class MoveSymbolTool(CodegenToolAdapter):
    """
    Move a symbol to a different file.
    
    Tier: Community (unified from Enterprise)
    Transaction: Mandatory
    """
    
    def __init__(self):
        super().__init__(
            name="move_symbol",
            tier=Tier.COMMUNITY,
            requires_transaction=True,
            description="Move a symbol to a different file"
        )
    
    def _validate_parameters(self, **kwargs) -> Optional[str]:
        if "symbol_name" not in kwargs:
            return "Missing required parameter: symbol_name"
        if "source_file" not in kwargs:
            return "Missing required parameter: source_file"
        if "target_file" not in kwargs:
            return "Missing required parameter: target_file"
        return None
    
    def _execute_impl(self, session: SessionContext, **kwargs) -> ToolResult:
        symbol_name = kwargs["symbol_name"]
        source_file = Path(kwargs["source_file"])
        target_file = Path(kwargs["target_file"])
        
        try:
            source_path = session.workspace_path / source_file
            target_path = session.workspace_path / target_file
            
            if not source_path.exists():
                return ToolResult(
                    success=False,
                    error=f"Source file not found: {source_file}"
                )
            
            # Read source file
            source_content = source_path.read_text()
            source_lines = source_content.split('\n')
            
            # Find the symbol definition
            symbol_start = None
            symbol_end = None
            indent_level = None
            
            for i, line in enumerate(source_lines):
                if f"def {symbol_name}" in line or f"class {symbol_name}" in line:
                    symbol_start = i
                    indent_level = len(line) - len(line.lstrip())
                    
                    # Find the end of the symbol (next definition at same or lower indent)
                    for j in range(i + 1, len(source_lines)):
                        next_line = source_lines[j]
                        if next_line.strip() and not next_line.strip().startswith('#'):
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= indent_level:
                                symbol_end = j
                                break
                    
                    if symbol_end is None:
                        symbol_end = len(source_lines)
                    
                    break
            
            if symbol_start is None:
                return ToolResult(
                    success=False,
                    error=f"Symbol '{symbol_name}' not found in {source_file}"
                )
            
            # Extract symbol code
            symbol_code = '\n'.join(source_lines[symbol_start:symbol_end])
            
            # Remove from source
            new_source_lines = source_lines[:symbol_start] + source_lines[symbol_end:]
            source_path.write_text('\n'.join(new_source_lines))
            
            # Add to target
            if target_path.exists():
                target_content = target_path.read_text()
                target_path.write_text(target_content + '\n\n' + symbol_code)
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(symbol_code)
            
            return ToolResult(
                success=True,
                data={
                    "symbol_name": symbol_name,
                    "source_file": str(source_file),
                    "target_file": str(target_file),
                    "lines_moved": symbol_end - symbol_start,
                    "moved": True
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to move symbol: {str(e)}"
            )
    
    def _get_parameter_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol_name": {
                    "type": "string",
                    "description": "Name of the symbol to move"
                },
                "source_file": {
                    "type": "string",
                    "description": "Source file containing the symbol"
                },
                "target_file": {
                    "type": "string",
                    "description": "Target file to move the symbol to"
                }
            },
            "required": ["symbol_name", "source_file", "target_file"]
        }

