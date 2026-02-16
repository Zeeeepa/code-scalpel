"""
Codegen MCP Adapter

Direct imports from Codegen SDK MCP extensions - no reimplementation.
All MCP functionality with tier unification applied.
"""

from codegen.extensions.mcp.codebase_agent import (
    query_codebase as _query_codebase
)

from codegen.extensions.mcp.codebase_mods import (
    split_files_by_function as _split_files_by_function
)

from codegen.extensions.mcp.codebase_tools import (
    reveal_symbol_tool as _reveal_symbol_tool,
    search_codebase_tool as _search_codebase_tool
)

from codegen.cli.mcp.server import (
    get_docs as _get_docs,
    get_setup_instructions as _get_setup_instructions,
    get_service_config as _get_service_config,
    ask_codegen_sdk as _ask_codegen_sdk,
    generate_codemod as _generate_codemod,
    improve_codemod as _improve_codemod
)

# Re-export with tier unification
# All MCP functionality is now Community tier accessible

def query_codebase(*args, **kwargs):
    """Query codebase - Community tier"""
    return _query_codebase(*args, **kwargs)


def split_files_by_function(*args, **kwargs):
    """Split files by function - Community tier"""
    return _split_files_by_function(*args, **kwargs)


def reveal_symbol_tool(*args, **kwargs):
    """Reveal symbol tool - Community tier"""
    return _reveal_symbol_tool(*args, **kwargs)


def search_codebase_tool(*args, **kwargs):
    """Search codebase tool - Community tier"""
    return _search_codebase_tool(*args, **kwargs)


def get_docs(*args, **kwargs):
    """Get docs - Community tier"""
    return _get_docs(*args, **kwargs)


def get_setup_instructions(*args, **kwargs):
    """Get setup instructions - Community tier"""
    return _get_setup_instructions(*args, **kwargs)


def get_service_config(*args, **kwargs):
    """Get service config - Community tier"""
    return _get_service_config(*args, **kwargs)


def ask_codegen_sdk(*args, **kwargs):
    """Ask Codegen SDK - Community tier"""
    return _ask_codegen_sdk(*args, **kwargs)


def generate_codemod(*args, **kwargs):
    """Generate codemod - Community tier"""
    return _generate_codemod(*args, **kwargs)


def improve_codemod(*args, **kwargs):
    """Improve codemod - Community tier"""
    return _improve_codemod(*args, **kwargs)

