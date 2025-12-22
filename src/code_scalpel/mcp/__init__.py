"""
Code Scalpel MCP Server - Model Context Protocol integration.

This module provides a fully MCP-compliant server that exposes Code Scalpel's
analysis capabilities through the official MCP protocol.

Supports:
- stdio transport (preferred for local integration)
- Streamable HTTP transport (for network deployment)

[20251216_FEATURE] v2.2.0 - Structured MCP Logging
- Tool invocation tracking with timing
- Success/failure metrics
- Analytics queries for usage patterns
[20251220_TODO] Add MCP prompt templates export:
    - Export prompt templates as resources (code_review_prompt, security_audit_prompt, etc.)
    - Implement prompt registry with versioning
    - Support custom prompt injection from client

[20251220_TODO] Add sampling/rate limiting:
    - Implement request rate limiting by client ID
    - Add quota tracking (requests per hour/day)
    - Support tiered rate limits (free/pro/enterprise)

[20251220_TODO] Add request/response validation schemas:
    - Validate all MCP request payloads against JSON Schema
    - Implement strict type checking for response models
    - Add schema versioning for backwards compatibility"""

from .server import mcp, run_server

# [20251216_FEATURE] v2.2.0 - Structured logging
from .logging import (
    MCPAnalytics,
    ToolInvocation,
    log_tool_invocation,
    log_tool_success,
    log_tool_error,
    get_analytics,
    mcp_logger,
)

__all__ = [
    "mcp",
    "run_server",
    # [20251216_FEATURE] v2.2.0 - Logging exports
    "MCPAnalytics",
    "ToolInvocation",
    "log_tool_invocation",
    "log_tool_success",
    "log_tool_error",
    "get_analytics",
    "mcp_logger",
]
