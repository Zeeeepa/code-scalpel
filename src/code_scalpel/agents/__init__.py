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

# [20251224_BUGFIX] Correct typo in filename: optimazation_agent -> optimization_agent
# Note: File exists as optimazation_agent.py - needs rename during refactoring
from .optimazation_agent import OptimizationAgent

from .security_agent import SecurityAgent

# [20251224_TIER1_TODO] Import stub modules when fully implemented (10 tests)
# from .documentation_agent import DocumentationAgent
# from .metrics_agent import MetricsAgent
# from .refactoring_agent import RefactoringAgent
# from .testing_agent import TestingAgent

# [20251224_TIER1_TODO] Phase 1 - Core Module Organization (COMMUNITY Tier - 25 items, 25 tests each)
# Purpose: Establish robust module structure and agent framework foundation
# Steps:
# 1. Complete all stub agent implementations (DocumentationAgent, MetricsAgent, RefactoringAgent, TestingAgent)
# 2. Create unified agent registry with capability discovery
# 3. Implement agent lifecycle management (init, start, stop, cleanup)
# 4. Add agent factory pattern for dynamic instantiation
# 5. Create agent configuration schema with validation
# 6. Implement agent plugin system for extensibility
# 7. Add agent versioning and compatibility checks
# 8. Create agent metadata and capability declaration
# 9. Implement agent health checks and diagnostics
# 10. Add agent telemetry collection
# 11. Create agent performance profiling
# 12. Implement agent error recovery mechanisms
# 13. Add agent state persistence and restoration
# 14. Create agent dependency injection container
# 15. Implement agent event bus for inter-agent communication
# 16. Add agent command pattern for action execution
# 17. Create agent observer pattern for state changes
# 18. Implement agent strategy pattern for algorithm selection
# 19. Add agent chain of responsibility for request handling
# 20. Create agent composite pattern for agent composition
# 21. Implement agent decorator pattern for behavior extension
# 22. Add comprehensive module documentation
# 23. Create agent usage examples and tutorials
# 24. Implement agent testing framework and utilities
# 25. Add agent benchmarking and comparison tools

# [20251224_TIER2_TODO] Phase 2 - Advanced Agent Capabilities (PRO Tier - 25 items, 30 tests each)
# Purpose: Add sophisticated agent coordination and learning capabilities
# Steps:
# 1. Implement multi-agent coordination and collaboration
# 2. Create agent negotiation protocols
# 3. Add agent consensus mechanisms
# 4. Implement agent task allocation and load balancing
# 5. Create agent workflow orchestration
# 6. Add agent learning from feedback (reinforcement learning)
# 7. Implement agent knowledge sharing and transfer
# 8. Create agent model fine-tuning infrastructure
# 9. Add agent A/B testing framework
# 10. Implement agent performance optimization
# 11. Create agent caching and memoization strategies
# 12. Add agent streaming and real-time processing
# 13. Implement agent asynchronous execution
# 14. Create agent parallel processing capabilities
# 15. Add agent distributed execution support
# 16. Implement agent fault tolerance and failover
# 17. Create agent circuit breaker pattern
# 18. Add agent retry logic with exponential backoff
# 19. Implement agent rate limiting and throttling
# 20. Create agent quota management
# 21. Add agent cost tracking and optimization
# 22. Implement agent usage analytics
# 23. Create agent recommendation engine
# 24. Add agent auto-scaling capabilities
# 25. Implement agent resource management

# [20251224_TIER3_TODO] Phase 3 - Enterprise Agent Features (ENTERPRISE Tier - 25 items, 35 tests each)
# Purpose: Enterprise-grade agent orchestration, governance, and compliance
# Steps:
# 1. Implement agent federation across multiple deployments
# 2. Create agent marketplace for discovery and sharing
# 3. Add agent certification and trust scoring
# 4. Implement agent access control and permissions
# 5. Create agent audit logging and compliance
# 6. Add agent security scanning and validation
# 7. Implement agent sandboxing and isolation
# 8. Create agent policy enforcement
# 9. Add agent SLA monitoring and enforcement
# 10. Implement agent contract verification
# 11. Create agent liability and accountability tracking
# 12. Add agent provenance and lineage tracking
# 13. Implement agent explainability and interpretability
# 14. Create agent bias detection and mitigation
# 15. Add agent fairness and ethics evaluation
# 16. Implement agent privacy-preserving techniques
# 17. Create agent differential privacy support
# 18. Add agent federated learning capabilities
# 19. Implement agent secure multi-party computation
# 20. Create agent homomorphic encryption support
# 21. Add agent regulatory compliance (GDPR, CCPA, SOX)
# 22. Implement agent industry standards (ISO, NIST)
# 23. Create agent certification programs
# 24. Add agent training and onboarding
# 25. Implement agent lifecycle governance

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
