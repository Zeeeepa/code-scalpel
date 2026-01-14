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

from .base_agent import AgentContext, BaseCodeAnalysisAgent
from .code_review_agent import CodeReviewAgent

# [20251224_BUGFIX] Correct typo in filename: optimazation_agent -> optimization_agent
# Note: File exists as optimazation_agent.py - needs rename during refactoring
from .optimazation_agent import OptimizationAgent
from .security_agent import SecurityAgent

# TODO [COMMUNITY]: Import stub modules when fully implemented (10 tests)
# from .documentation_agent import DocumentationAgent
# from .metrics_agent import MetricsAgent
# from .refactoring_agent import RefactoringAgent
# from .testing_agent import TestingAgent

# TODO [COMMUNITY]: Phase 1 - Core Module Organization (25 items, 25 tests each)
# Purpose: Establish robust module structure and agent framework foundation
# TODO [COMMUNITY]: Complete all stub agent implementations (DocumentationAgent, MetricsAgent, RefactoringAgent, TestingAgent)
# TODO [COMMUNITY]: Create unified agent registry with capability discovery
# TODO [COMMUNITY]: Implement agent lifecycle management (init, start, stop, cleanup)
# TODO [COMMUNITY]: Add agent factory pattern for dynamic instantiation
# TODO [COMMUNITY]: Create agent configuration schema with validation
# TODO [COMMUNITY]: Implement agent plugin system for extensibility
# TODO [COMMUNITY]: Add agent versioning and compatibility checks
# TODO [COMMUNITY]: Create agent metadata and capability declaration
# TODO [COMMUNITY]: Implement agent health checks and diagnostics
# TODO [COMMUNITY]: Add agent telemetry collection
# TODO [COMMUNITY]: Create agent performance profiling
# TODO [COMMUNITY]: Implement agent error recovery mechanisms
# TODO [COMMUNITY]: Add agent state persistence and restoration
# TODO [COMMUNITY]: Create agent dependency injection container
# TODO [COMMUNITY]: Implement agent event bus for inter-agent communication
# TODO [COMMUNITY]: Add agent command pattern for action execution
# TODO [COMMUNITY]: Create agent observer pattern for state changes
# TODO [COMMUNITY]: Implement agent strategy pattern for algorithm selection
# TODO [COMMUNITY]: Add agent chain of responsibility for request handling
# TODO [COMMUNITY]: Create agent composite pattern for agent composition
# TODO [COMMUNITY]: Implement agent decorator pattern for behavior extension
# TODO [COMMUNITY]: Add comprehensive module documentation
# TODO [COMMUNITY]: Create agent usage examples and tutorials
# TODO [COMMUNITY]: Implement agent testing framework and utilities
# TODO [COMMUNITY]: Add agent benchmarking and comparison tools

# TODO [PRO]: Phase 2 - Advanced Agent Capabilities (25 items, 30 tests each)
# Purpose: Add sophisticated agent coordination and learning capabilities
# TODO [PRO]: Implement multi-agent coordination and collaboration
# TODO [PRO]: Create agent negotiation protocols
# TODO [PRO]: Add agent consensus mechanisms
# TODO [PRO]: Implement agent task allocation and load balancing
# TODO [PRO]: Create agent workflow orchestration
# TODO [PRO]: Add agent learning from feedback (reinforcement learning)
# TODO [PRO]: Implement agent knowledge sharing and transfer
# TODO [PRO]: Create agent model fine-tuning infrastructure
# TODO [PRO]: Add agent A/B testing framework
# TODO [PRO]: Implement agent performance optimization
# TODO [PRO]: Create agent caching and memoization strategies
# TODO [PRO]: Add agent streaming and real-time processing
# TODO [PRO]: Implement agent asynchronous execution
# TODO [PRO]: Create agent parallel processing capabilities
# TODO [PRO]: Add agent distributed execution support
# TODO [PRO]: Implement agent fault tolerance and failover
# TODO [PRO]: Create agent circuit breaker pattern
# TODO [PRO]: Add agent retry logic with exponential backoff
# TODO [PRO]: Implement agent rate limiting and throttling
# TODO [PRO]: Create agent quota management
# TODO [PRO]: Add agent cost tracking and optimization
# TODO [PRO]: Implement agent usage analytics
# TODO [PRO]: Create agent recommendation engine
# TODO [PRO]: Add agent auto-scaling capabilities
# TODO [PRO]: Implement agent resource management

# TODO [ENTERPRISE]: Phase 3 - Enterprise Agent Features (25 items, 35 tests each)
# Purpose: Enterprise-grade agent orchestration, governance, and compliance
# TODO [ENTERPRISE]: Implement agent federation across multiple deployments
# TODO [ENTERPRISE]: Create agent marketplace for discovery and sharing
# TODO [ENTERPRISE]: Add agent certification and trust scoring
# TODO [ENTERPRISE]: Implement agent access control and permissions
# TODO [ENTERPRISE]: Create agent audit logging and compliance
# TODO [ENTERPRISE]: Add agent security scanning and validation
# TODO [ENTERPRISE]: Implement agent sandboxing and isolation
# TODO [ENTERPRISE]: Create agent policy enforcement
# TODO [ENTERPRISE]: Add agent SLA monitoring and enforcement
# TODO [ENTERPRISE]: Implement agent contract verification
# TODO [ENTERPRISE]: Create agent liability and accountability tracking
# TODO [ENTERPRISE]: Add agent provenance and lineage tracking
# TODO [ENTERPRISE]: Implement agent explainability and interpretability
# TODO [ENTERPRISE]: Create agent bias detection and mitigation
# TODO [ENTERPRISE]: Add agent fairness and ethics evaluation
# TODO [ENTERPRISE]: Implement agent privacy-preserving techniques
# TODO [ENTERPRISE]: Create agent differential privacy support
# TODO [ENTERPRISE]: Add agent federated learning capabilities
# TODO [ENTERPRISE]: Implement agent secure multi-party computation
# TODO [ENTERPRISE]: Create agent homomorphic encryption support
# TODO [ENTERPRISE]: Add agent regulatory compliance (GDPR, CCPA, SOX)
# TODO [ENTERPRISE]: Implement agent industry standards (ISO, NIST)
# TODO [ENTERPRISE]: Create agent certification programs
# TODO [ENTERPRISE]: Add agent training and onboarding
# TODO [ENTERPRISE]: Implement agent lifecycle governance

__all__ = [
    "BaseCodeAnalysisAgent",
    "AgentContext",
    "CodeReviewAgent",
    "OptimizationAgent",
    "SecurityAgent",
    # Add when implemented:
    # "DocumentationAgent",
    # "MetricsAgent",
    # "RefactoringAgent",
    # "TestingAgent",
]
