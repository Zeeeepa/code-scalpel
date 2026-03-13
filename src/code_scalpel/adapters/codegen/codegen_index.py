"""
Codegen Index Adapter

Direct imports from Codegen SDK index extension - no reimplementation.
Provides code indexing functionality with tier unification.

Also includes LangChain tool wrappers that require Codebase instance.
"""

from codegen.extensions.index.code_index import CodeIndex as _CodeIndex
from codegen.extensions.index.file_index import FileIndex as _FileIndex
from codegen.extensions.index.symbol_index import SymbolIndex as _SymbolIndex

# LangChain tools - these require a Codebase instance for instantiation
from codegen.extensions.langchain.tools import (
    ViewFileTool as _ViewFileTool,
    ListDirectoryTool as _ListDirectoryTool,
    RipGrepTool as _RipGrepTool,
    EditFileTool as _EditFileTool,
    CreateFileTool as _CreateFileTool,
    DeleteFileTool as _DeleteFileTool,
    RenameFileTool as _RenameFileTool,
    MoveSymbolTool as _MoveSymbolTool,
    RevealSymbolTool as _RevealSymbolTool,
    SemanticEditTool as _SemanticEditTool,
    ReplacementEditTool as _ReplacementEditTool,
    GlobalReplacementEditTool as _GlobalReplacementEditTool,
    ReflectionTool as _ReflectionTool,
    SearchFilesByNameTool as _SearchFilesByNameTool,
)

# Re-export index classes with tier unification
# All indexing functionality is now Community tier accessible


class CodeIndex(_CodeIndex):
    """
    Code index - Community tier (unified from Pro)
    Direct passthrough to Codegen SDK
    
    Abstract base class for code indexing.
    """
    pass


class FileIndex(_FileIndex):
    """
    File index - Community tier (unified from Pro)
    Direct passthrough to Codegen SDK
    
    Indexes files in the codebase for fast lookup.
    """
    pass


class SymbolIndex(_SymbolIndex):
    """
    Symbol index - Community tier (unified from Enterprise)
    Direct passthrough to Codegen SDK
    
    Indexes symbols (functions, classes, variables) for fast lookup.
    """
    pass


# LangChain tool factory functions
# These create tool instances that require a Codebase


def create_langchain_tools(codebase):
    """
    Create all LangChain tools for a given codebase - Community tier
    
    Args:
        codebase: Codegen Codebase instance
        
    Returns:
        List of LangChain tool instances
    """
    return [
        _ViewFileTool(codebase),
        _ListDirectoryTool(codebase),
        _RipGrepTool(codebase),
        _EditFileTool(codebase),
        _CreateFileTool(codebase),
        _DeleteFileTool(codebase),
        _RenameFileTool(codebase),
        _MoveSymbolTool(codebase),
        _RevealSymbolTool(codebase),
        _SemanticEditTool(codebase),
        _ReplacementEditTool(codebase),
        _GlobalReplacementEditTool(codebase),
        _ReflectionTool(codebase),
        _SearchFilesByNameTool(codebase),
    ]


# Individual tool classes for direct access
ViewFileTool = _ViewFileTool
ListDirectoryTool = _ListDirectoryTool
RipGrepTool = _RipGrepTool
EditFileTool = _EditFileTool
CreateFileTool = _CreateFileTool
DeleteFileTool = _DeleteFileTool
RenameFileTool = _RenameFileTool
MoveSymbolTool = _MoveSymbolTool
RevealSymbolTool = _RevealSymbolTool
SemanticEditTool = _SemanticEditTool
ReplacementEditTool = _ReplacementEditTool
GlobalReplacementEditTool = _GlobalReplacementEditTool
ReflectionTool = _ReflectionTool
SearchFilesByNameTool = _SearchFilesByNameTool

