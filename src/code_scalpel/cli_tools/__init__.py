"""CLI package for Code Scalpel.

This package contains CLI-specific modules:
- tool_bridge: Bridge between CLI and MCP tools
- formatters: Output formatting utilities (future)

[20260205_FEATURE] Created as part of Phase 1 CLI tool access implementation.
"""

from code_scalpel.cli_tools.tool_bridge import invoke_tool

__all__ = ["invoke_tool"]
