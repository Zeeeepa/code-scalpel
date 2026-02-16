"""
Codegen Adapters

This module provides clean adapters to Codegen SDK functionality.
All imports are from the official Codegen SDK - no reimplementation.

All functionality is unified to Community tier - no Pro/Enterprise gates.
"""

# Analysis functions
from .codegen_codebase_analysis import (
    get_codebase_summary,
    get_file_summary,
    get_class_summary,
    get_function_summary,
    get_symbol_summary
)

# Core classes
from .codegen_codebase import Codebase
from .codegen_parser import Parser

# Tools
from .codegen_tools import (
    commit,
    create_file,
    create_pr,
    create_pr_comment,
    create_pr_review_comment,
    delete_file,
    edit_file,
    move_symbol,
    perform_reflection,
    rename_file,
    replacement_edit,
    replacement_edit_global,
    reveal_symbol,
    run_codemod,
    search,
    search_files_by_name,
    semantic_edit,
    semantic_search,
    view_file,
    view_pr
)

# MCP functionality
from .codegen_mcp import (
    query_codebase,
    split_files_by_function,
    reveal_symbol_tool,
    search_codebase_tool,
    get_docs,
    get_setup_instructions,
    get_service_config,
    ask_codegen_sdk,
    generate_codemod,
    improve_codemod
)

# Graph analysis
from .codegen_graph import (
    create_codebase_graph,
    visualize_codebase
)

# Indexing and LangChain tools
from .codegen_index import (
    CodeIndex,
    FileIndex,
    SymbolIndex,
    create_langchain_tools,
    ViewFileTool,
    ListDirectoryTool,
    RipGrepTool,
    EditFileTool,
    CreateFileTool,
    DeleteFileTool,
    RenameFileTool,
    MoveSymbolTool,
    RevealSymbolTool,
    SemanticEditTool,
    ReplacementEditTool,
    GlobalReplacementEditTool,
    ReflectionTool,
    SearchFilesByNameTool,
)

# LSP modules
from . import codegen_lsp as lsp

# SWE-bench modules
from . import codegen_swebench as swebench

# Document functions example
from .codegen_document_functions import (
    hop_through_imports,
    get_extended_context,
    document_functions
)

__all__ = [
    # Analysis
    'get_codebase_summary',
    'get_file_summary',
    'get_class_summary',
    'get_function_summary',
    'get_symbol_summary',
    
    # Core
    'Codebase',
    'Parser',
    
    # Tools
    'commit',
    'create_file',
    'create_pr',
    'create_pr_comment',
    'create_pr_review_comment',
    'delete_file',
    'edit_file',
    'move_symbol',
    'perform_reflection',
    'rename_file',
    'replacement_edit',
    'replacement_edit_global',
    'reveal_symbol',
    'run_codemod',
    'search',
    'search_files_by_name',
    'semantic_edit',
    'semantic_search',
    'view_file',
    'view_pr',
    
    # MCP
    'query_codebase',
    'split_files_by_function',
    'reveal_symbol_tool',
    'search_codebase_tool',
    'get_docs',
    'get_setup_instructions',
    'get_service_config',
    'ask_codegen_sdk',
    'generate_codemod',
    'improve_codemod',
    
    # Graph
    'create_codebase_graph',
    'visualize_codebase',
    
    # Index
    'CodeIndex',
    'FileIndex',
    'SymbolIndex',
    'create_langchain_tools',
    
    # LangChain Tools
    'ViewFileTool',
    'ListDirectoryTool',
    'RipGrepTool',
    'EditFileTool',
    'CreateFileTool',
    'DeleteFileTool',
    'RenameFileTool',
    'MoveSymbolTool',
    'RevealSymbolTool',
    'SemanticEditTool',
    'ReplacementEditTool',
    'GlobalReplacementEditTool',
    'ReflectionTool',
    'SearchFilesByNameTool',
    
    # LSP
    'lsp',
    
    # SWE-bench
    'swebench',
    
    # Document Functions
    'hop_through_imports',
    'get_extended_context',
    'document_functions',
]
