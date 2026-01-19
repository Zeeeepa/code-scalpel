"""
REST API Server - Legacy HTTP API for Code Scalpel.

NOTE: This is NOT an MCP-compliant server. It uses a custom REST API.
For true MCP protocol support, use: code_scalpel.mcp.server

======================================================================
COMMUNITY TIER - Core REST API Infrastructure
======================================================================
1. Add FastAPI application initialization
2. Add API endpoint definition
3. Add request validation
4. Add response formatting
5. Add error handling
6. Add CORS support
7. Add request logging
8. Add health check endpoint
9. Add status endpoint
10. Add metrics endpoint
11. Add OpenAPI documentation
12. Add Swagger UI integration
13. Add ReDoc documentation
14. Add request/response serialization
15. Add JSON schema validation
16. Add path parameters
17. Add query parameters
18. Add request body handling
19. Add file upload support
20. Add file download support
21. Add pagination support
22. Add sorting support
23. Add filtering support
24. Add search support
25. Add API versioning

PRO TIER - Advanced API Features
======================================================================
26. Add authentication (JWT)
27. Add OAuth2 integration
28. Add API key authentication
29. Add rate limiting middleware
30. Add request throttling
31. Add response compression
32. Add caching headers
33. Add ETags support
34. Add conditional requests
35. Add streaming responses
36. Add async endpoints
37. Add background tasks
38. Add webhook support
39. Add event streaming
40. Add GraphQL support
41. Add batch endpoints
42. Add async task status
43. Add long-running operations
44. Add job queue integration
45. Add database transactions
46. Add multi-database support
47. Add data validation rules
48. Add custom validators
49. Add middleware pipeline
50. Add request tracing

ENTERPRISE TIER - Enterprise API Features
======================================================================
51. Add multi-tenancy support
52. Add tenant isolation
53. Add cross-tenant authorization
54. Add enterprise authentication (SAML/SSO)
55. Add RBAC enforcement
56. Add audit logging
57. Add compliance reporting
58. Add encryption at rest
59. Add encryption in transit (TLS)
60. Add API gateway integration
61. Add service mesh integration
62. Add load balancing
63. Add auto-scaling
64. Add circuit breaker pattern
65. Add bulkhead isolation
66. Add retry policies
67. Add timeout management
68. Add resource quotas
69. Add cost allocation
70. Add billing integration
71. Add SLA management
72. Add disaster recovery
73. Add multi-region deployment
74. Add high availability
75. Add executive dashboards

This module provides a Flask-based REST API that exposes Code Scalpel's
analysis capabilities via HTTP endpoints for agent queries.

Endpoints:
- GET  /health   - Health check
- GET  /tools    - List available tools
- POST /analyze  - Analyze code structure
- POST /security - Security vulnerability scan
- POST /symbolic - Symbolic execution
- POST /refactor - Code refactoring suggestions
"""

import time
from dataclasses import dataclass
from typing import Optional, Union

from flask import Flask, Response, jsonify, request

# Version updated to match package
__version__ = "1.0.0"


@dataclass
class MCPServerConfig:
    """Configuration for the REST API server."""

    # SECURITY: Default to localhost only. Use --host 0.0.0.0 explicitly for network access.
    host: str = "127.0.0.1"
    port: int = 8080
    debug: bool = False
    cache_enabled: bool = True
    max_code_size: int = 100000  # Maximum code size in characters


def create_app(config: Optional[MCPServerConfig] = None) -> Flask:
    """
    Create and configure the Flask MCP server application.

    Args:
        config: Optional server configuration.

    Returns:
        Configured Flask application.
    """
    if config is None:
        config = MCPServerConfig()

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = config.max_code_size

    # Lazy import to avoid circular dependencies
    # [20251220_BUGFIX] Fixed import path for CrewAIScalpel
    try:
        from code_scalpel.integrations.crewai import CrewAIScalpel
    except ImportError:
        try:
            from .crewai import CrewAIScalpel
        except ImportError as e:
            raise ImportError(
                "Could not import CrewAIScalpel. Ensure code_scalpel is properly installed."
            ) from e
    scalpel = CrewAIScalpel(cache_enabled=config.cache_enabled)

    @app.route("/health", methods=["GET"])
    def health_check() -> Response:
        """Health check endpoint."""
        return jsonify({"status": "healthy", "service": "code-scalpel-mcp", "version": __version__})

    @app.route("/analyze", methods=["POST"])
    def analyze_code() -> Union[Response, tuple[Response, int]]:
        """
        Analyze Python code and return analysis results.

        Request body:
            {
                "code": "string",  # Python code to analyze
                "options": {       # Optional analysis options
                    "include_security": true,
                    "include_style": true
                }
            }

        Response:
            {
                "success": bool,
                "analysis": {...},
                "issues": [...],
                "suggestions": [...],
                "processing_time_ms": float,
                "error": "string" (optional)
            }
        """
        start_time = time.time()

        # Parse request body
        data = request.get_json()
        if not data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Request body is required",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        code = data.get("code")
        if not code:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Code field is required",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        if not isinstance(code, str):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Code must be a string",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        if len(code) > config.max_code_size:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Code exceeds maximum size of {config.max_code_size} characters",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        try:
            # Perform analysis
            result = scalpel.analyze(code)

            response = {
                "success": result.success,
                "analysis": result.analysis,
                "issues": result.issues,
                "suggestions": result.suggestions,
                "processing_time_ms": _elapsed_ms(start_time),
            }

            if result.error:
                response["error"] = result.error

            return jsonify(response)

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Internal error: {str(e)}",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                500,
            )

    @app.route("/refactor", methods=["POST"])
    def refactor_code() -> Union[Response, tuple[Response, int]]:
        """
        Refactor Python code based on analysis.

        Request body:
            {
                "code": "string",           # Python code to refactor
                "task": "string" (optional) # Refactoring task description
            }

        Response:
            {
                "success": bool,
                "original_code": "string",
                "refactored_code": "string" (optional),
                "analysis": {...},
                "suggestions": [...],
                "processing_time_ms": float,
                "error": "string" (optional)
            }
        """
        start_time = time.time()

        data = request.get_json()
        if not data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Request body is required",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        code = data.get("code")
        if not code:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Code field is required",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        if not isinstance(code, str):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Code must be a string",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        task = data.get("task", "improve code quality")

        try:
            result = scalpel.refactor(code, task)

            response = {
                "success": result.success,
                "original_code": result.original_code,
                "refactored_code": result.refactored_code,
                "analysis": result.analysis,
                "suggestions": result.suggestions,
                "processing_time_ms": _elapsed_ms(start_time),
            }

            if result.error:
                response["error"] = result.error

            return jsonify(response)

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Internal error: {str(e)}",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                500,
            )

    @app.route("/security", methods=["POST"])
    def security_scan() -> Union[Response, tuple[Response, int]]:
        """
        Perform security-focused analysis on Python code.

        Request body:
            {
                "code": "string"  # Python code to analyze
            }

        Response:
            {
                "success": bool,
                "issues": [...],
                "risk_level": "string",
                "recommendations": [...],
                "processing_time_ms": float,
                "error": "string" (optional)
            }
        """
        start_time = time.time()

        data = request.get_json()
        if not data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Request body is required",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        code = data.get("code")
        if not code:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Code field is required",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        if not isinstance(code, str):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Code must be a string",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        try:
            result = scalpel.analyze_security(code)
            result["processing_time_ms"] = _elapsed_ms(start_time)
            return jsonify(result)

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Internal error: {str(e)}",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                500,
            )

    @app.route("/symbolic", methods=["POST"])
    def symbolic_analysis() -> Union[Response, tuple[Response, int]]:
        """
        Perform symbolic execution analysis on Python code.

        v0.3.0+: Uses Z3-powered symbolic execution to enumerate paths.

        Request body:
            {
                "code": "string"  # Python code to analyze
            }

        Response:
            {
                "success": bool,
                "total_paths": int,
                "feasible_paths": int,
                "paths": [...],
                "processing_time_ms": float,
                "error": "string" (optional)
            }
        """
        start_time = time.time()

        data = request.get_json()
        if not data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Request body is required",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        code = data.get("code")
        if not code:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Code field is required",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        if not isinstance(code, str):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Code must be a string",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                400,
            )

        try:
            result = scalpel.analyze_symbolic(code)
            result["processing_time_ms"] = _elapsed_ms(start_time)
            return jsonify(result)

        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Internal error: {str(e)}",
                        "processing_time_ms": _elapsed_ms(start_time),
                    }
                ),
                500,
            )

    @app.route("/tools", methods=["GET"])
    def list_tools() -> Response:
        """
        List all available MCP tools/endpoints.

        This endpoint helps agents discover what capabilities are available.
        """
        return jsonify(
            {
                "service": "code-scalpel-mcp",
                "version": __version__,
                "tools": [
                    {
                        "name": "analyze",
                        "endpoint": "/analyze",
                        "method": "POST",
                        "description": "Analyze Python code for style and security issues",
                    },
                    {
                        "name": "security",
                        "endpoint": "/security",
                        "method": "POST",
                        "description": "Taint-based security scan (SQLi, XSS, Command Injection, Path Traversal)",
                    },
                    {
                        "name": "symbolic",
                        "endpoint": "/symbolic",
                        "method": "POST",
                        "description": "Symbolic execution to enumerate paths and generate test inputs",
                    },
                    {
                        "name": "refactor",
                        "endpoint": "/refactor",
                        "method": "POST",
                        "description": "Refactor Python code based on analysis",
                    },
                ],
            }
        )

    return app


def _elapsed_ms(start_time: float) -> float:
    """Calculate elapsed time in milliseconds."""
    return (time.time() - start_time) * 1000


def run_server(host: str = "127.0.0.1", port: int = 8080, debug: bool = False) -> None:
    """
    Run the MCP server.

    Args:
        host: Host to bind to.
        port: Port to bind to.
        debug: Whether to run in debug mode. WARNING: Debug mode should
               never be enabled in production as it can allow arbitrary
               code execution.
    """
    import os
    import warnings

    # Warn if debug mode is enabled in production
    if debug and os.environ.get("FLASK_ENV") == "production":
        warnings.warn(
            "Debug mode should not be enabled in production. "
            "Set FLASK_ENV to 'development' or disable debug mode.",
            RuntimeWarning,
            stacklevel=2,
        )
        debug = False  # Force disable debug in production

    config = MCPServerConfig(host=host, port=port, debug=debug)
    app = create_app(config)
    app.run(host=host, port=port, debug=debug)


# Allow running directly as a script or module
if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Code Scalpel MCP Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to (default: 8080)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode (development only)")

    args = parser.parse_args()

    # Only enable debug mode in development
    is_development = os.environ.get("FLASK_ENV", "development") == "development"
    run_server(host=args.host, port=args.port, debug=args.debug and is_development)
