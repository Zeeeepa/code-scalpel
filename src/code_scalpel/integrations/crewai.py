"""
CrewAIScalpel - Integration wrapper for CrewAI with Code Scalpel analysis capabilities.

This module provides the CrewAIScalpel class that wraps Code Scalpel's
AST analysis capabilities for use with CrewAI agents and tools.

======================================================================
COMMUNITY TIER - Core CrewAI Integration
======================================================================
1. Add CrewAIClient initialization
2. Add Agent creation with role and goal
3. Add Task definition with description
4. Add Crew assembly with agents and tasks
5. Add CrewConfig dataclass
6. Add agent_role() definition
7. Add agent_goal() specification
8. Add agent_backstory() context
9. Add task_description() definition
10. Add task_expected_output() format
11. Add team_composition() agent grouping
12. Add execute_crew() run workflow
13. Add task_dependency() sequencing
14. Add parallel_task_execution() concurrent tasks
15. Add task_input_output() data flow
16. Add error_handling_crew() failure recovery
17. Add logging_crew() activity tracking
18. Add state_management_crew() persistent state
19. Add memory_management_crew() conversation context
20. Add configuration_validation_crew() setup verification
21. Add crew_monitoring() real-time stats
22. Add crew_metrics() performance analytics
23. Add task_metrics() individual task stats
24. Add agent_performance() agent metrics
25. Add crew_timeout() execution limits

PRO TIER - Advanced CrewAI Features
======================================================================
26. Add async_crew_execution() non-blocking
27. Add streaming_crew_output() real-time results
28. Add dynamic_task_generation() runtime tasks
29. Add adaptive_crew_composition() dynamic team
30. Add skill_sharing() agent capabilities
31. Add knowledge_sharing_crew() team learning
32. Add collaboration_patterns() cooperation models
33. Add delegation_support() task assignment
34. Add negotiation_support() consensus building
35. Add voting_mechanism() group decisions
36. Add consensus_building() agreement reaching
37. Add conflict_resolution_crew() handling disagreement
38. Add priority_handling_crew() urgent tasks
39. Add backpressure_handling() queue management
40. Add resource_allocation_crew() optimal distribution
41. Add workload_balancing_crew() even distribution
42. Add cost_optimization_crew() expense reduction
43. Add performance_profiling_crew() bottleneck detection
44. Add debugging_crew() error investigation
45. Add crew_visualization() workflow diagrams
46. Add crew_replay() execution replay
47. Add crew_checkpointing() save state
48. Add crew_versioning() version tracking
49. Add crew_rollback() revert capability
50. Add advanced_analytics_crew() detailed insights

ENTERPRISE TIER - Enterprise CrewAI Features
======================================================================
51. Add multi_crew_coordination() multiple teams
52. Add crew_federation() distributed teams
53. Add hierarchical_crew_structure() nested teams
54. Add crew_scaling() handle many agents
55. Add load_balancing_crew() distribute load
56. Add auto_scaling_crew() dynamic scaling
57. Add service_mesh_integration() networking
58. Add service_discovery() dynamic endpoints
59. Add circuit_breaker_crew() failure handling
60. Add bulkhead_pattern_crew() isolation
61. Add rate_limiting_crew() request throttling
62. Add quota_management_crew() usage limits
63. Add audit_logging_crew() forensic trail
64. Add compliance_crew() regulatory adherence
65. Add encryption_crew() data protection
66. Add key_management_crew() secret handling
67. Add authentication_crew() access control
68. Add authorization_crew() role enforcement
69. Add sso_integration_crew() enterprise auth
70. Add saml_support_crew() identity federation
71. Add sla_management_crew() service levels
72. Add incident_management_crew() crisis response
73. Add disaster_recovery_crew() backup operations
74. Add multi_region_crew() geographic distribution
75. Add executive_reporting_crew() leadership metrics

v0.3.1: Now includes taint-based SecurityAnalyzer and SymbolicAnalyzer.
"""

import asyncio
import warnings
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence, TypedDict


class RefactorResultDict(TypedDict, total=False):
    """Refactor result dictionary for JSON serialization."""

    original_code: str
    analysis: dict[str, Any]
    issues: list[dict[str, Any]]
    suggestions: list[str]
    refactored_code: str | None
    success: bool
    error: str | None


@dataclass
class RefactorResult:
    """Result of code refactoring analysis."""

    original_code: str
    analysis: dict[str, Any] = field(default_factory=dict)
    issues: list[dict[str, Any]] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    refactored_code: Optional[str] = None
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> RefactorResultDict:
        """Convert result to dictionary."""
        return {
            "original_code": self.original_code,
            "analysis": self.analysis,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "refactored_code": self.refactored_code,
            "success": self.success,
            "error": self.error,
        }


class CrewAIScalpel:
    """
    Wrapper class that integrates Code Scalpel's analysis capabilities
    with CrewAI agents for async code analysis and refactoring.

    This class provides async methods suitable for CrewAI tool integration,
    including code analysis, security scanning, and refactoring capabilities.
    """

    def __init__(self, cache_enabled: bool = True):
        """
        Initialize the CrewAIScalpel wrapper.

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

    async def analyze_async(self, code: str) -> RefactorResult:
        """
        Perform async code analysis using AST tools.

        Args:
            code: Python source code to analyze.

        Returns:
            RefactorResult containing analysis details.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._analyze_sync, code)

    def analyze(self, code: str) -> RefactorResult:
        """
        Synchronous code analysis (for non-async contexts).

        Args:
            code: Python source code to analyze.

        Returns:
            RefactorResult containing analysis details.
        """
        return self._analyze_sync(code)

    def _analyze_sync(self, code: str) -> RefactorResult:
        """
        Synchronous code analysis implementation.

        Args:
            code: Python source code to analyze.

        Returns:
            RefactorResult containing analysis details.
        """
        result = RefactorResult(original_code=code)

        try:
            # Parse to AST
            tree = self.analyzer.parse_to_ast(code)

            # Perform style analysis
            style_issues = self.analyzer.analyze_code_style(tree)

            # Find security issues
            security_issues = self.analyzer.find_security_issues(tree)

            # Combine all issues
            result.issues = [
                {"type": "style", "category": k, "details": v} for k, v in style_issues.items() if v
            ]
            result.issues.extend([{"type": "security", **issue} for issue in security_issues])

            # Generate suggestions
            result.suggestions = self._generate_suggestions(style_issues, security_issues)

            # Store analysis metadata
            result.analysis = {
                "parsed": True,
                "total_issues": len(result.issues),
                "style_issues": sum(len(v) for v in style_issues.values()),
                "security_issues": len(security_issues),
            }

        except SyntaxError as e:
            result.success = False
            result.error = f"Syntax error: {str(e)}"
            result.analysis = {"parsed": False, "error": str(e)}
        except Exception as e:
            result.success = False
            result.error = f"Analysis error: {str(e)}"
            result.analysis = {"parsed": False, "error": str(e)}

        return result

    async def refactor_async(
        self, code: str, task_description: str = "improve code quality"
    ) -> RefactorResult:
        """
        Perform async code refactoring based on analysis.

        Args:
            code: Python source code to refactor.
            task_description: Description of the refactoring task.

        Returns:
            RefactorResult with refactored code.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._refactor_sync, code, task_description)

    def refactor(self, code: str, task_description: str = "improve code quality") -> RefactorResult:
        """
        Synchronous code refactoring (for non-async contexts).

        Args:
            code: Python source code to refactor.
            task_description: Description of the refactoring task.

        Returns:
            RefactorResult with refactored code.
        """
        return self._refactor_sync(code, task_description)

    def _refactor_sync(self, code: str, task_description: str) -> RefactorResult:
        """
        Synchronous refactoring implementation.

        Args:
            code: Python source code to refactor.
            task_description: Description of the refactoring task.

        Returns:
            RefactorResult with refactored code.
        """
        # First perform analysis
        result = self._analyze_sync(code)

        if not result.success:
            return result

        try:
            tree = self.analyzer.parse_to_ast(code)
            # Return regenerated code - refactoring logic can be extended
            # [20251216_BUGFIX] Suppress upstream ast.* deprecations during regeneration on Python 3.13
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                result.refactored_code = self.analyzer.ast_to_code(tree)
        except Exception as e:
            result.success = False
            result.error = f"Refactoring error: {str(e)}"

        return result

    # =========================================================================
    # Symbolic Execution (v0.3.0+)
    # =========================================================================

    async def analyze_symbolic_async(self, code: str) -> dict[str, Any]:
        """
        Perform async symbolic execution analysis.

        Args:
            code: Python source code to analyze.

        Returns:
            Dictionary with symbolic execution results.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.analyze_symbolic, code)

    def analyze_symbolic(self, code: str) -> dict[str, Any]:
        """
        Perform symbolic execution analysis to find execution paths and edge cases.

        v0.3.0: Uses Z3-powered symbolic execution engine to:
        - Enumerate all possible execution paths
        - Generate concrete test inputs for each path
        - Identify dead code and unreachable branches

        Args:
            code: Python source code to analyze.

        Returns:
            Dictionary with symbolic execution results including:
            - paths: List of execution paths with constraints
            - test_inputs: Generated test cases
            - dead_code: Unreachable code segments
        """
        try:
            from ..symbolic_execution_tools import SymbolicAnalyzer

            analyzer = SymbolicAnalyzer()
            result = analyzer.analyze(code)

            # Extract path information
            paths_info = []
            for i, path in enumerate(result.paths[:10]):  # Limit to 10 paths
                path_data = {
                    "path_id": i,
                    "feasible": getattr(path, "is_feasible", True),
                }
                # Try to get variables from path
                if hasattr(path, "variables"):
                    path_data["variables"] = {k: str(v) for k, v in path.variables.items()}
                else:
                    state = getattr(path, "state", None)
                    if state and hasattr(state, "get_all_variables"):
                        path_data["variables"] = {
                            k: str(v) for k, v in state.get_all_variables().items()
                        }
                paths_info.append(path_data)

            return {
                "success": True,
                "total_paths": result.total_paths,
                "feasible_paths": result.feasible_count,
                "infeasible_paths": result.infeasible_count,
                "paths": paths_info,
                "all_variables": (
                    {k: str(v) for k, v in result.all_variables.items()}
                    if result.all_variables
                    else {}
                ),
                "analyzer": "z3-symbolic",
            }
        except ImportError as e:
            return {
                "success": False,
                "error": f"Symbolic execution tools not available: {e}",
                "paths": [],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "paths": [],
            }

    # =========================================================================
    # Security Analysis (v0.3.1 - Taint-based)
    # =========================================================================

    async def analyze_security_async(self, code: str) -> dict[str, Any]:
        """
        Perform async security-focused analysis.

        Args:
            code: Python source code to analyze.

        Returns:
            Dictionary with security analysis results.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.analyze_security, code)

    def analyze_security(self, code: str) -> dict[str, Any]:
        """
        Perform synchronous security-focused analysis using taint tracking.

        v0.3.1: Now uses the SecurityAnalyzer with taint-based vulnerability
        detection (SQL injection, XSS, command injection, path traversal).

        Args:
            code: Python source code to analyze.

        Returns:
            Dictionary with security analysis results including:
            - vulnerabilities: List of detected vulnerabilities with CWE IDs
            - taint_flows: Data flow paths from sources to sinks
            - risk_level: Overall risk assessment
        """
        try:
            # Use the new taint-based SecurityAnalyzer (v0.3.0+)
            try:
                from ..symbolic_execution_tools import analyze_security as taint_analyze

                result = taint_analyze(code)

                vulnerabilities = [v.to_dict() for v in result.vulnerabilities]

                return {
                    "success": True,
                    "vulnerabilities": vulnerabilities,
                    "vulnerability_count": result.vulnerability_count,
                    "has_vulnerabilities": result.has_vulnerabilities,
                    "sql_injections": len(result.get_sql_injections()),
                    "xss": len(result.get_xss()),
                    "command_injections": len(result.get_command_injections()),
                    "path_traversals": len(result.get_path_traversals()),
                    "risk_level": self._calculate_risk_from_vulns(vulnerabilities),
                    "summary": (
                        result.summary()
                        if result.has_vulnerabilities
                        else "No vulnerabilities detected"
                    ),
                }
            except ImportError:
                # Fallback to AST-based analysis if symbolic tools not available
                tree = self.analyzer.parse_to_ast(code)
                security_issues = self.analyzer.find_security_issues(tree)

                return {
                    "success": True,
                    "issues": security_issues,
                    "risk_level": self._calculate_risk_level(security_issues),
                    "recommendations": self._get_security_recommendations(security_issues),
                    "analyzer": "ast-based (fallback)",
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "vulnerabilities": [],
                "risk_level": "unknown",
            }

    def _calculate_risk_from_vulns(self, vulnerabilities: Sequence[Mapping[str, Any]]) -> str:
        """Calculate risk level from vulnerability list."""
        if not vulnerabilities:
            return "low"

        # Check for critical vulnerabilities
        critical_types = {"SQL Injection", "Command Injection"}
        high_types = {"Cross-Site Scripting (XSS)", "Path Traversal"}

        for vuln in vulnerabilities:
            vuln_type = vuln.get("type", "")
            if vuln_type in critical_types:
                return "critical"
            if vuln_type in high_types:
                return "high"

        return "medium" if vulnerabilities else "low"

    def _analyze_security_sync(self, code: str) -> dict[str, Any]:
        """
        Deprecated: Use analyze_security() instead.

        Synchronous security analysis implementation.

        Args:
            code: Python source code to analyze.

        Returns:
            Dictionary with security analysis results.
        """
        return self.analyze_security(code)

    def _generate_suggestions(
        self, style_issues: dict[str, list[str]], security_issues: list[dict[str, Any]]
    ) -> list[str]:
        """
        Generate suggestions based on analysis results.

        Args:
            style_issues: Dictionary of style issues by category.
            security_issues: List of security issue dictionaries.

        Returns:
            List of suggestion strings.
        """
        suggestions = []

        # Style-based suggestions
        if style_issues.get("long_functions"):
            suggestions.append("Break down long functions into smaller, single-purpose functions.")

        if style_issues.get("deep_nesting"):
            suggestions.append("Reduce nesting depth using early returns or extracting methods.")

        if style_issues.get("naming_conventions"):
            suggestions.append("Follow PEP 8 naming conventions for better code readability.")

        # Security-based suggestions
        dangerous_funcs = [
            issue for issue in security_issues if issue.get("type") == "dangerous_function"
        ]
        if dangerous_funcs:
            funcs = ", ".join({i.get("function", "") for i in dangerous_funcs})
            suggestions.append(f"Replace dangerous functions ({funcs}) with safer alternatives.")

        sql_issues = [issue for issue in security_issues if issue.get("type") == "sql_injection"]
        if sql_issues:
            suggestions.append("Use parameterized queries instead of string formatting for SQL.")

        return suggestions

    def _calculate_risk_level(self, security_issues: list[dict[str, Any]]) -> str:
        """
        Calculate overall security risk level.

        Args:
            security_issues: List of security issue dictionaries.

        Returns:
            Risk level string ("low", "medium", "high", "critical").
        """
        if not security_issues:
            return "low"

        # Count issue types
        dangerous_count = sum(1 for i in security_issues if i.get("type") == "dangerous_function")
        sql_count = sum(1 for i in security_issues if i.get("type") == "sql_injection")

        total_critical = dangerous_count + sql_count

        if total_critical >= 3:
            return "critical"
        elif total_critical >= 2:
            return "high"
        elif total_critical >= 1:
            return "medium"
        return "low"

    def _get_security_recommendations(self, security_issues: list[dict[str, Any]]) -> list[str]:
        """
        Get specific security recommendations.

        Args:
            security_issues: List of security issue dictionaries.

        Returns:
            List of recommendation strings.
        """
        recommendations = []

        for issue in security_issues:
            issue_type = issue.get("type")
            if issue_type == "dangerous_function":
                func = issue.get("function", "unknown")
                if "eval" in func or "exec" in func:
                    recommendations.append(
                        f"Replace '{func}' with ast.literal_eval or a safer parser."
                    )
                elif "os.system" in func or "subprocess" in func:
                    recommendations.append(
                        f"Replace '{func}' with subprocess.run with shell=False."
                    )
                elif "pickle" in func:
                    recommendations.append(
                        "Use json or other safe serialization instead of pickle."
                    )
            elif issue_type == "sql_injection":
                recommendations.append(
                    "Use parameterized queries (?, %s) instead of string formatting."
                )

        return list(set(recommendations))  # Remove duplicates

    def get_crewai_tools(self) -> list[dict[str, Any]]:
        """
        Get tool definitions for CrewAI integration.

        Returns:
            List of tool definition dictionaries for CrewAI.
        """
        return [
            {
                "name": "analyze_code",
                "description": (
                    "Analyzes Python code for style issues, security vulnerabilities, "
                    "and improvement opportunities using AST parsing."
                ),
                "func": self.analyze,
            },
            {
                "name": "refactor_code",
                "description": (
                    "Refactors Python code based on analysis to improve quality "
                    "and fix identified issues."
                ),
                "func": self.refactor,
            },
            {
                "name": "security_scan",
                "description": (
                    "Performs security-focused analysis to identify vulnerabilities "
                    "like dangerous function usage and SQL injection."
                ),
                "func": self.analyze_security,
            },
        ]
