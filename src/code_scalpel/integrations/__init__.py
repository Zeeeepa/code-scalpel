# [20260125_REFACTOR] Core integrations module for protocol analysis only.
# Agent and web integrations have been moved to separate packages:
# - codescalpel-agents: AutoGen, CrewAI, LangChain integrations
# - codescalpel-web: Flask REST API server
#
# This module now contains only protocol analyzers (Claude, GraphQL, gRPC, etc.)
# which are part of the core Code Scalpel functionality.

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

__all__ = []


def __getattr__(name: str) -> Any:
    """Lazy attribute loading for deprecated integration packages.

    Agent and web integrations have moved to separate packages.
    Please install and import from:
    - codescalpel-agents for agent framework integrations
    - codescalpel-web for REST API server
    """
    deprecated_agents = {
        "AutogenScalpel",
        "AutogenCodeAnalysisAgent",
        "AnalysisResult",
        "CrewAIScalpel",
        "RefactorResult",
    }
    deprecated_web = {"MCPServerConfig", "create_app", "run_rest_server"}

    if name in deprecated_agents:
        raise ImportError(
            f"'{name}' has been moved to codescalpel-agents package. " f"Install with: pip install codescalpel-agents"
        )

    if name in deprecated_web:
        raise ImportError(
            f"'{name}' has been moved to codescalpel-web package. " f"Install with: pip install codescalpel-web"
        )

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
