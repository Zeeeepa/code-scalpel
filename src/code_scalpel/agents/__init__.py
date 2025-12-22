"""
Code Scalpel Agents - AI Agent Framework for Code Analysis.

This module provides specialized AI agents that demonstrate how to use Code Scalpel's
MCP tools for various code analysis and improvement tasks.

Agents follow the OODA loop (Observe, Orient, Decide, Act) and use MCP tools to:
- Observe: Gather information about codebases
- Orient: Analyze and understand context
- Decide: Determine optimal actions
- Act: Execute changes safely with verification

Available Agents:
- CodeReviewAgent: Comprehensive code quality and security review
- SecurityAgent: Specialized security vulnerability detection and remediation
- OptimizationAgent: Performance analysis and optimization suggestions
- RefactoringAgent: Code restructuring and design pattern refactoring
- TestingAgent: Test generation and coverage analysis
- DocumentationAgent: Documentation generation and improvement
- MetricsAgent: Code metrics aggregation and analytics

Example Usage:
    from code_scalpel.agents import CodeReviewAgent

    agent = CodeReviewAgent(workspace_root="/path/to/project")
    result = await agent.execute_ooda_loop("src/main.py")
"""

from .base_agent import BaseCodeAnalysisAgent, AgentContext
from .code_review_agent import CodeReviewAgent

# [20251221_TODO] Implement documentation_agent stub module
# from .documentation_agent import DocumentationAgent
# [20251221_TODO] Implement metrics_agent stub module
# from .metrics_agent import MetricsAgent
# [20251221_BUGFIX] Correct typo in filename: optimazation_agent -> optimization_agent
# Note: File exists as optimazation_agent.py - needs rename during refactoring
from .optimazation_agent import OptimizationAgent

# [20251221_TODO] Implement refactoring_agent stub module
# from .refactoring_agent import RefactoringAgent
from .security_agent import SecurityAgent

# [20251221_TODO] Implement testing_agent stub module
# from .testing_agent import TestingAgent

__all__ = [
    "BaseCodeAnalysisAgent",
    "AgentContext",
    "CodeReviewAgent",
    # [20251221_TODO] Add DocumentationAgent when implemented
    # "DocumentationAgent",
    # [20251221_TODO] Add MetricsAgent when implemented
    # "MetricsAgent",
    "OptimizationAgent",
    # [20251221_TODO] Add RefactoringAgent when implemented
    # "RefactoringAgent",
    "SecurityAgent",
    # [20251221_TODO] Add TestingAgent when implemented
    # "TestingAgent",
]
