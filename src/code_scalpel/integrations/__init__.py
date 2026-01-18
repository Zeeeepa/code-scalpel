"""
Code Scalpel Integrations - Integration wrappers for AI agent frameworks.

This module provides integration wrappers for various AI agent frameworks
including Autogen, CrewAI, LangChain, and Claude.

For MCP (Model Context Protocol) integration, use:
    from code_scalpel.mcp import mcp, run_server

For the legacy REST API server (not MCP-compliant), use:
    from code_scalpel.integrations.rest_api_server import create_app

======================================================================
COMMUNITY TIER - Core Integration Infrastructure
======================================================================
1. Add IntegrationRegistry class for dynamic framework discovery
2. Add integration_factory() function for creating framework instances
3. Add list_available_integrations() to enumerate supported frameworks
4. Add get_integration(framework_name) to retrieve integration by name
5. Add IntegrationConfig dataclass for framework configuration
6. Add validate_framework_config(config) for configuration validation
7. Add initialize_integration(framework, config) for setup
8. Add shutdown_integration(framework) for cleanup
9. Export all framework integrations from __init__.py
10. Add integration version tracking
11. Add framework capability detection
12. Add feature_available(framework, feature) checking
13. Add integration_status() for health checks
14. Add list_all_tools(framework) to enumerate available tools
15. Add integration_metrics() for tracking usage
16. Add integration_compatibility_matrix() for version compatibility
17. Add migration_guide(from_framework, to_framework)
18. Add integration_examples() for getting started
19. Add validate_api_keys(framework) for credential checking
20. Add integration_documentation(framework) link generator
21. Add supported_languages(framework) listing
22. Add supported_models(framework) enumeration
23. Add framework_dependencies() for requirement checking
24. Add integration_logging_setup(framework, level)
25. Add integration_error_handler() for exception handling

PRO TIER - Advanced Integration Features
======================================================================
26. Add integration_caching() for response caching across frameworks
27. Add rate_limit_management(framework) for API rate limits
28. Add request_batching(framework) for efficiency
29. Add response_filtering(framework, filter_func) for customization
30. Add integration_middleware() for request/response processing
31. Add integration_hooks(framework) for lifecycle events
32. Add integration_retry_policy(framework) configuration
33. Add integration_timeout_management(framework)
34. Add multi_framework_routing() for load balancing
35. Add integration_metrics_collection(framework)
36. Add integration_performance_profiling(framework)
37. Add integration_error_recovery(framework)
38. Add integration_circuit_breaker(framework)
39. Add integration_feature_flags(framework) for A/B testing
40. Add integration_fallback_strategy(primary, fallback)
41. Add async_integration_support(framework)
42. Add streaming_response_support(framework)
43. Add integration_cost_tracking(framework)
44. Add integration_quota_management(framework)
45. Add integration_authentication_refresh(framework)
46. Add integration_token_management(framework)
47. Add integration_request_signing(framework)
48. Add integration_ssl_verification(framework)
49. Add integration_proxy_support(framework)
50. Add integration_custom_headers(framework)

ENTERPRISE TIER - Distributed and Advanced Features
======================================================================
51. Add distributed_integration_coordination() for multi-agent
52. Add federated_framework_deployment() across multiple services
53. Add integration_load_balancing() with smart routing
54. Add integration_failover(primary, secondary) for HA
55. Add integration_circuit_breaker_advanced() with detailed metrics
56. Add multi_region_integration() for geographic distribution
57. Add integration_data_encryption() end-to-end
58. Add integration_audit_logging() for compliance
59. Add integration_rate_limiting_advanced() with adaptive limits
60. Add integration_anomaly_detection() for security
61. Add integration_compliance_checking(framework, policy)
62. Add integration_sso_support() for enterprise auth
63. Add integration_rbac_integration() role-based access
64. Add integration_cost_optimization() recommendations
65. Add integration_ml_based_routing() using ML models
66. Add integration_predictive_caching() forecasting
67. Add integration_auto_scaling() for variable load
68. Add integration_chaos_testing() for resilience
69. Add integration_blue_green_deployment() zero downtime
70. Add integration_canary_deployment() gradual rollout
71. Add integration_shadow_mode() for testing
72. Add integration_real_time_sync() across systems
73. Add integration_transaction_support() ACID operations
74. Add integration_messaging_queue() asynchronous
75. Add integration_workflow_orchestration() complex sequences
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# [20251230_REFACTOR] MCP-first: keep integrations importable without optional deps.
# This module lazily imports agent/web integrations only when accessed.


if TYPE_CHECKING:
    # Agent integrations
    from .autogen import AnalysisResult, AutogenCodeAnalysisAgent, AutogenScalpel
    from .crewai import CrewAIScalpel, RefactorResult

    # Legacy REST API server (Flask)
    from .rest_api_server import MCPServerConfig, create_app
    from .rest_api_server import run_server as run_rest_server

__all__ = [
    # Autogen integration
    "AutogenScalpel",
    "AutogenCodeAnalysisAgent",  # Backward compatibility alias
    "AnalysisResult",
    # CrewAI integration
    "CrewAIScalpel",
    "RefactorResult",
    # REST API Server (legacy, not MCP-compliant)
    "create_app",
    "run_rest_server",
    "MCPServerConfig",
]


def __getattr__(name: str) -> Any:
    """Lazy attribute loading for optional integrations (PEP 562)."""
    if name in {"AutogenScalpel", "AutogenCodeAnalysisAgent", "AnalysisResult"}:
        try:
            from .autogen import (
                AnalysisResult,
                AutogenCodeAnalysisAgent,
                AutogenScalpel,
            )
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "AutoGen integration requires optional dependencies. "
                'Install with: pip install "code-scalpel[agents]"'
            ) from e
        return {
            "AutogenScalpel": AutogenScalpel,
            "AutogenCodeAnalysisAgent": AutogenCodeAnalysisAgent,
            "AnalysisResult": AnalysisResult,
        }[name]

    if name in {"CrewAIScalpel", "RefactorResult"}:
        try:
            from .crewai import CrewAIScalpel, RefactorResult
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "CrewAI integration requires optional dependencies. "
                'Install with: pip install "code-scalpel[agents]"'
            ) from e
        return {"CrewAIScalpel": CrewAIScalpel, "RefactorResult": RefactorResult}[name]

    if name in {"MCPServerConfig", "create_app", "run_rest_server"}:
        try:
            from .rest_api_server import MCPServerConfig, create_app
            from .rest_api_server import run_server as run_rest_server
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "The legacy REST API server requires Flask. "
                'Install with: pip install "code-scalpel[web]"'
            ) from e
        return {
            "MCPServerConfig": MCPServerConfig,
            "create_app": create_app,
            "run_rest_server": run_rest_server,
        }[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
