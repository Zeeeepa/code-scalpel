"""
REST API Server - Compatibility shim.

This module has been moved to the code-scalpel[web] package (codescalpel_web.server).
This shim provides backward compatibility for imports from code_scalpel.integrations.rest_api_server.

Installation:
    pip install code-scalpel[web]

New import path:
    from codescalpel_web.server import create_app, run_server, MCPServerConfig

Deprecated import path (redirected):
    from code_scalpel.integrations.rest_api_server import create_app, run_server, MCPServerConfig
"""

import warnings

try:
    from codescalpel_web.server import (
        MCPServerConfig,
        _elapsed_ms,
        create_app,
        run_server,
    )

    warnings.warn(
        "Importing from code_scalpel.integrations.rest_api_server is deprecated. "
        "Use 'from codescalpel_web.server import ...' instead. "
        "Install with: pip install code-scalpel[web]",
        DeprecationWarning,
        stacklevel=2,
    )

    __all__ = ["MCPServerConfig", "create_app", "run_server", "_elapsed_ms"]

except ImportError as e:
    raise ImportError(
        "REST API server requires the web package. Install with: pip install code-scalpel[web]"
    ) from e
