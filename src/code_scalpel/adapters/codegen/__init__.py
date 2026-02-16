"""
Codegen Adapters

This module provides clean adapters to Codegen SDK functionality.
All imports are from the official Codegen SDK - no reimplementation.
"""

from .codegen_codebase_analysis import (
    get_codebase_summary,
    get_file_summary,
    get_class_summary,
    get_function_summary,
    get_symbol_summary
)

from .codegen_codebase import Codebase
from .codegen_parser import Parser

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
]

