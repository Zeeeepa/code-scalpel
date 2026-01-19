"""
AutogenScalpel - Integration wrapper for Autogen with Code Scalpel analysis capabilities.

This module provides the AutogenScalpel class that wraps Code Scalpel's
AST analysis capabilities for use with Autogen agents.

======================================================================
COMMUNITY TIER - Core AutoGen Integration
======================================================================
1. Add AutoGenClient initialization
2. Add ConversableAgent creation
3. Add register_tool() for agent tools
4. Add initiate_chat(agent, message) for conversations
5. Add AutoGenConfig dataclass
6. Add agent_profile() defining agent capabilities
7. Add agent_system_prompt() context for agent
8. Add function_map() tool registration
9. Add llm_config() model configuration
10. Add conversation_termination_condition() exit criteria
11. Add max_consecutive_auto_reply() limit
12. Add human_input_mode() (ALWAYS, TERMINATE, NEVER)
13. Add code_execution_support() Python execution
14. Add code_executor_setup() environment config
15. Add multi_agent_orchestration() group chat
16. Add agent_communication_protocol() message format
17. Add agent_state_management() persistent state
18. Add agent_memory() conversation history
19. Add error_handling() for agent failures
20. Add timeout_handling() agent hanging
21. Add agent_restart() recovery
22. Add session_management() conversation sessions
23. Add agent_logging() activity tracking
24. Add agent_metrics() performance stats
25. Add configuration_validation() setup checking

PRO TIER - Advanced AutoGen Features
======================================================================
26. Add user_proxy_agent_advanced() enhanced user interaction
27. Add assistant_agent_optimization() improved responses
28. Add nested_chat_support() group conversations
29. Add message_routing() intelligent direction
30. Add cost_tracking_autogen() token usage
31. Add prompt_engineering_support() template system
32. Add few_shot_examples() in agent context
33. Add tool_use_optimization() best tool selection
34. Add code_generation_support() code writing
35. Add code_review_agent() automated review
36. Add planning_agent() task decomposition
37. Add retrieval_augmented_generation() RAG integration
38. Add vector_database_integration() semantic search
39. Add knowledge_base_support() documentation
40. Add reasoning_chain_support() multi-step thinking
41. Add agent_specialization() role-specific configs
42. Add skill_composition() combining capabilities
43. Add workflow_definition() agent sequences
44. Add conditional_routing() smart message direction
45. Add async_agent_support() non-blocking
46. Add streaming_output() real-time results
47. Add conversation_branching() alternative paths
48. Add checkpointing() save/restore state
49. Add replay_support() conversation replay
50. Add analysis_metrics() detailed statistics

ENTERPRISE TIER - Enterprise AutoGen Features
======================================================================
51. Add multi_agent_scaling() handling many agents
52. Add distributed_agent_deployment() across services
53. Add agent_orchestration_advanced() complex workflows
54. Add load_balancing_agents() distribute work
55. Add agent_pool_management() resource optimization
56. Add priority_queue_support() task prioritization
57. Add service_level_agreement() uptime guarantees
58. Add disaster_recovery_autogen() backup agents
59. Add multi_region_agents() geographic distribution
60. Add agent_versioning() version management
61. Add rollback_support() revert to previous
62. Add canary_deployment() gradual rollout
63. Add blue_green_deployment() zero downtime
64. Add A_B_testing_agents() experiment framework
65. Add performance_tuning() optimization
66. Add cost_optimization_autogen() reduce spending
67. Add security_hardening() vulnerability fixes
68. Add compliance_autogen() regulatory adherence
69. Add audit_trail_autogen() forensic analysis
70. Add encryption_autogen() data protection
71. Add authentication_autogen() access control
72. Add authorization_autogen() role enforcement
73. Add rate_limiting_autogen() throttling
74. Add quota_enforcement_autogen() limits
75. Add sla_monitoring_autogen() uptime tracking
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional, TypedDict


class AnalysisResultDict(TypedDict, total=False):
    """Analysis result dictionary for JSON serialization."""

    code: str
    ast_analysis: dict[str, Any]
    security_issues: list[dict[str, Any]]
    style_issues: dict[str, list[str]]
    suggestions: list[str]
    refactored_code: str | None
    error: str | None


@dataclass
class AnalysisResult:
    """Result of code analysis."""

    code: str
    ast_analysis: dict[str, Any] = field(default_factory=dict)
    security_issues: list[dict[str, Any]] = field(default_factory=list)
    style_issues: dict[str, list[str]] = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)
    refactored_code: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> AnalysisResultDict:
        """Convert result to dictionary."""
        return {
            "code": self.code,
            "ast_analysis": self.ast_analysis,
            "security_issues": self.security_issues,
            "style_issues": self.style_issues,
            "suggestions": self.suggestions,
            "refactored_code": self.refactored_code,
            "error": self.error,
        }


class AutogenScalpel:
    """
    Wrapper class that integrates Code Scalpel's analysis capabilities
    with Autogen agents for async code analysis.

    This class provides async methods for analyzing code using AST,
    detecting security issues, and suggesting refactoring improvements.
    """

    def __init__(self, cache_enabled: bool = True):
        """
        Initialize the AutogenScalpel wrapper.

        Args:
            cache_enabled: Whether to cache AST parsing results for performance.
        """
        # Import ASTAnalyzer - handle different import contexts
        try:
            from ..ast_tools.analyzer import ASTAnalyzer
        except (ImportError, ValueError):
            try:
                from code_scalpel.ast_tools.analyzer import ASTAnalyzer
            except ImportError:
                # Direct import as fallback
                import os
                import sys

                src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if src_path not in sys.path:
                    sys.path.insert(0, src_path)
                from code_scalpel.ast_tools.analyzer import ASTAnalyzer
        self.analyzer = ASTAnalyzer(cache_enabled=cache_enabled)
        self._cache_enabled = cache_enabled

    async def analyze_async(self, code: str) -> AnalysisResult:
        """
        Perform async code analysis using AST tools.

        Args:
            code: Python source code to analyze.

        Returns:
            AnalysisResult containing analysis details.
        """
        # Run the synchronous analysis in a thread pool to make it async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._analyze_sync, code)

    def _analyze_sync(self, code: str) -> AnalysisResult:
        """
        Synchronous code analysis implementation.

        Args:
            code: Python source code to analyze.

        Returns:
            AnalysisResult containing analysis details.
        """
        result = AnalysisResult(code=code)

        try:
            # Parse to AST
            tree = self.analyzer.parse_to_ast(code)

            # Perform style analysis
            result.style_issues = self.analyzer.analyze_code_style(tree)

            # Find security issues
            result.security_issues = self.analyzer.find_security_issues(tree)

            # Generate suggestions based on analysis
            result.suggestions = self._generate_suggestions(result)

            # Collect basic AST info
            result.ast_analysis = {
                "parsed": True,
                "style_issues_count": sum(len(v) for v in result.style_issues.values()),
                "security_issues_count": len(result.security_issues),
            }

        except SyntaxError as e:
            result.error = f"Syntax error: {str(e)}"
            result.ast_analysis = {"parsed": False, "error": str(e)}
        except Exception as e:
            result.error = f"Analysis error: {str(e)}"
            result.ast_analysis = {"parsed": False, "error": str(e)}

        return result

    async def refactor_async(self, code: str, refactor_type: str = "auto") -> AnalysisResult:
        """
        Perform async code refactoring based on analysis.

        Args:
            code: Python source code to refactor.
            refactor_type: Type of refactoring ("auto", "simplify", "optimize").

        Returns:
            AnalysisResult with refactored code.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._refactor_sync, code, refactor_type)

    def _refactor_sync(self, code: str, refactor_type: str) -> AnalysisResult:
        """
        Synchronous refactoring implementation.

        Args:
            code: Python source code to refactor.
            refactor_type: Type of refactoring.

        Returns:
            AnalysisResult with refactored code.
        """
        # First perform analysis
        result = self._analyze_sync(code)

        if result.error:
            return result

        try:
            tree = self.analyzer.parse_to_ast(code)
            # For now, return the same code - refactoring logic can be extended
            result.refactored_code = self.analyzer.ast_to_code(tree)
        except Exception as e:
            result.error = f"Refactoring error: {str(e)}"

        return result

    def _generate_suggestions(self, result: AnalysisResult) -> list[str]:
        """
        Generate suggestions based on analysis results.

        Args:
            result: AnalysisResult from analysis.

        Returns:
            List of suggestion strings.
        """
        suggestions = []

        # Add suggestions based on style issues
        for issue_type, _issues in result.style_issues.items():
            if issue_type == "long_functions":
                suggestions.append(
                    "Consider breaking down long functions into smaller, focused functions."
                )
            elif issue_type == "deep_nesting":
                suggestions.append(
                    "Consider reducing nesting depth using early returns or guard clauses."
                )
            elif issue_type == "naming_conventions":
                suggestions.append(
                    "Follow PEP 8 naming conventions: snake_case for functions, CamelCase for classes."
                )

        # Add suggestions based on security issues
        if result.security_issues:
            for issue in result.security_issues:
                if issue.get("type") == "dangerous_function":
                    suggestions.append(
                        f"Avoid using dangerous function '{issue.get('function')}' - consider safer alternatives."
                    )
                elif issue.get("type") == "sql_injection":
                    suggestions.append(
                        "Use parameterized queries to prevent SQL injection vulnerabilities."
                    )

        return suggestions

    def get_tool_description(self) -> dict[str, str | dict[str, str]]:
        """
        Get description for use as an Autogen tool.

        Returns:
            Tool description dictionary for Autogen integration.
        """
        return {
            "name": "code_scalpel_analyzer",
            "description": (
                "Analyzes Python code using AST parsing to detect style issues, "
                "security vulnerabilities, and suggest improvements."
            ),
            "parameters": {
                "code": "Python source code to analyze",
                "refactor": "Whether to include refactoring suggestions (optional)",
            },
        }


# Backward compatibility alias
AutogenCodeAnalysisAgent = AutogenScalpel
