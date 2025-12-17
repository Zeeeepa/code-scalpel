"""
Autonomy module for Code Scalpel v3.0.0.

This module provides self-correction capabilities for AI agents,
including error-to-diff conversion, speculative execution, and 
integrations with popular AI agent frameworks.

[20251217_FEATURE] v3.0.0 Autonomy - Merged Error-to-Diff and Framework Integrations
"""

from code_scalpel.autonomy.error_to_diff import (
    ErrorType,
    FixHint,
    ErrorAnalysis,
    ErrorToDiffEngine,
    ParsedError,
)

from code_scalpel.autonomy.integrations.langgraph import (
    create_scalpel_fix_graph,
    ScalpelState,
)
from code_scalpel.autonomy.integrations.crewai import create_scalpel_fix_crew
from code_scalpel.autonomy.integrations.autogen import create_scalpel_autogen_agents

__all__ = [
    # Error-to-Diff Engine
    "ErrorType",
    "FixHint",
    "ErrorAnalysis",
    "ErrorToDiffEngine",
    "ParsedError",
    # LangGraph
    "create_scalpel_fix_graph",
    "ScalpelState",
    # CrewAI
    "create_scalpel_fix_crew",
    # AutoGen
    "create_scalpel_autogen_agents",
]
