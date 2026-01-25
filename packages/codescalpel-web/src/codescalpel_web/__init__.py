"""
Code Scalpel Web Integrations - REST API and framework adapters.

This package provides web server integrations for Code Scalpel, including
a Flask REST API server for remote access to Code Scalpel's analysis tools.

Installation:
    pip install code-scalpel[web]

Usage:
    from codescalpel_web.server import create_app, run_server

    app = create_app()
    run_server(app, port=8080)
"""

__version__ = "1.0.2"

try:
    from .server import MCPServerConfig, create_app, run_server
except ImportError:
    create_app = None
    run_server = None
    MCPServerConfig = None

__all__ = [
    "__version__",
    "create_app",
    "run_server",
    "MCPServerConfig",
]
