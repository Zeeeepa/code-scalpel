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
    - Add schema versioning for backwards compatibility

TODO ITEMS:

COMMUNITY TIER (Core MCP Integration):
1. TODO: Implement basic MCP server with stdio transport
2. TODO: Expose core analysis tools (analyze_code, extract_code) as MCP tools
3. TODO: Create MCP request/response envelope with tier metadata
4. TODO: Implement error handling with machine-parseable error codes
5. TODO: Add tool discovery and capability advertisement
6. TODO: Create comprehensive MCP logging framework
7. TODO: Implement request tracing and correlation IDs
8. TODO: Add basic rate limiting for community tier
9. TODO: Create MCP server unit tests and integration tests
10. TODO: Document MCP protocol compliance and tool specifications

PRO TIER (Enhanced MCP Features):
11. TODO: Add HTTP transport with TLS support
12. TODO: Implement per-client quota tracking (requests/hour)
13. TODO: Add tier-based feature gating at MCP boundary
14. TODO: Implement custom MCP prompt templates export
15. TODO: Add analytics queries for usage patterns
16. TODO: Support batch tool invocations
17. TODO: Implement response streaming for large outputs
18. TODO: Add performance monitoring and SLA tracking
19. TODO: Create advanced logging with structured analytics
20. TODO: Implement request filtering and query optimization

ENTERPRISE TIER (Distributed & Scale):
21. TODO: Implement distributed MCP with load balancing
22. TODO: Add multi-protocol support (gRPC, WebSocket)
23. TODO: Implement federated MCP across multiple servers
24. TODO: Add OpenTelemetry distributed tracing
25. TODO: Support custom authentication/authorization plugins
26. TODO: Implement MCP caching layer with invalidation
27. TODO: Add audit logging for compliance (SOC2, HIPAA)
28. TODO: Implement health checks and failover
29. TODO: Add blockchain-based request signature verification
30. TODO: Create AI-powered MCP request optimization engine"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# [20251228_BUGFIX] Avoid stdlib `logging` shadowing when server is run as a script.
from .mcp_logging import ToolInvocation  # noqa: E402
from .mcp_logging import (MCPAnalytics, get_analytics, log_tool_error,
                          log_tool_invocation, log_tool_success, mcp_logger)

if TYPE_CHECKING:
    # Make `mcp` visible to type checkers without eagerly importing at runtime.
    from .server import mcp as mcp
else:
    mcp: Any


def _load_server():
    # Import lazily to avoid runpy warnings when executing the module as a script
    # (python -m code_scalpel.mcp.server).
    from . import server as _server

    return _server


def get_mcp():
    """Return the FastMCP server instance (lazy import)."""

    return _load_server().mcp


def run_server(*args, **kwargs):
    """Run the MCP server (lazy import)."""

    return _load_server().run_server(*args, **kwargs)


def __getattr__(name: str):
    # Backwards compatibility: older code imported `mcp` from this package.
    if name == "mcp":
        return get_mcp()
    raise AttributeError(name)


__all__ = [
    "get_mcp",
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
