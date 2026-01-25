"""
Code Scalpel Agent Extensions - Autonomous code analysis and modification.

This package provides AI agent frameworks and autonomous code repair capabilities
for use with Code Scalpel's MCP tools.

Key Modules:
- agents: AI agent framework (CodeReviewAgent, SecurityAgent, OptimizationAgent, etc.)
- autonomy: Autonomous error-to-fix engine with safety guarantees
- integrations: Framework integrations (AutoGen, CrewAI, LangGraph, LangChain)

Installation:
    pip install code-scalpel[agents]

Usage:
    from codescalpel_agents.agents import CodeReviewAgent
    from codescalpel_agents.autonomy import ErrorToDiffEngine, FixLoop
"""

__version__ = "1.0.2"

# Import public API
from .agents import (
    AgentContext,
    BaseCodeAnalysisAgent,
    CodeReviewAgent,
    OptimizationAgent,
    SecurityAgent,
)

from .autonomy import (
    AuditEntry,
    AutonomyAuditTrail,
    ErrorAnalysis,
    ErrorToDiffEngine,
    ErrorType,
    ExecutionTestResult,
    FileChange,
    FixAttempt,
    FixHint,
    FixLoop,
    FixLoopResult,
    Mutation,
    MutationGateResult,
    MutationResult,
    MutationTestGate,
    MutationType,
    ParsedError,
    SandboxExecutorImpl,
    SandboxResultImpl,
)

__all__ = [
    # Version
    "__version__",
    # Agent framework
    "BaseCodeAnalysisAgent",
    "AgentContext",
    "CodeReviewAgent",
    "OptimizationAgent",
    "SecurityAgent",
    # Autonomy / Error-to-Diff Engine
    "ErrorToDiffEngine",
    "ErrorAnalysis",
    "ErrorType",
    "FixHint",
    "FixLoop",
    "FixLoopResult",
    "FixAttempt",
    "ParsedError",
    "MutationTestGate",
    "MutationGateResult",
    "MutationResult",
    "Mutation",
    "MutationType",
    "SandboxExecutorImpl",
    "SandboxResultImpl",
    "ExecutionTestResult",
    "FileChange",
    "AutonomyAuditTrail",
    "AuditEntry",
]
