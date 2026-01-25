"""
CrewAI Integration - Compatibility shim.

This module has been moved to the code-scalpel[agents] package (codescalpel_agents.integrations).
This shim provides backward compatibility for imports from code_scalpel.integrations.crewai.

Installation:
    pip install code-scalpel[agents]

New import path:
    from codescalpel_agents.integrations.crewai import CrewAIScalpel

Deprecated import path (redirected):
    from code_scalpel.integrations.crewai import CrewAIScalpel
"""

import warnings

try:
    from codescalpel_agents.integrations.crewai import CrewAIScalpel

    warnings.warn(
        "Importing from code_scalpel.integrations.crewai is deprecated. "
        "Use 'from codescalpel_agents.integrations.crewai import ...' instead. "
        "Install with: pip install code-scalpel[agents]",
        DeprecationWarning,
        stacklevel=2,
    )

    __all__ = ["CrewAIScalpel"]

except ImportError as e:
    raise ImportError(
        "CrewAI integration requires the agents package. Install with: pip install code-scalpel[agents]"
    ) from e
