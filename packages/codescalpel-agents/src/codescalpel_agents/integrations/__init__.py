"""Agent framework integrations for Code Scalpel.

This module provides integrations with popular AI agent frameworks:
- AutoGen: Microsoft AutoGen multi-agent conversations (via AutogenScalpel)
- CrewAI: CrewAI agent orchestration framework (via CrewAIScalpel)
"""

try:
    from .autogen import AutogenScalpel
except ImportError:
    AutogenScalpel = None

try:
    from .crewai import CrewAIScalpel
except ImportError:
    CrewAIScalpel = None

__all__ = [
    "AutogenScalpel",
    "CrewAIScalpel",
]
