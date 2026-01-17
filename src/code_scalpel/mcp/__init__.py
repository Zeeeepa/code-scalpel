"""
Code Scalpel MCP Server - Model Context Protocol integration.

[20260116_REFACTOR] This is the canonical public API for the MCP module.
All tests and external code should import from here, not from server.py.

Usage:
    from code_scalpel.mcp import mcp, analyze_code, extract_code
    from code_scalpel.mcp import AnalysisResult, SecurityResult
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# =============================================================================
# [20260116_REFACTOR] Canonical Public API
# Import everything from their proper locations and re-export
# =============================================================================

# Protocol and MCP instance
from code_scalpel.mcp.protocol import mcp, _get_current_tier, set_current_tier

# =============================================================================
# MODELS - Pydantic result models
# =============================================================================
from code_scalpel.mcp.models.core import (
    AnalysisResult,
    ClassInfo,
    ContextualExtractionResult,
    CrawlClassInfo,
    CrawlFileResult,
    CrawlFunctionInfo,
    CrawlSummary,
    ExecutionPath,
    FileContextResult,
    FunctionInfo,
    GeneratedTestCase,
    PathCondition,
    PatchResultModel,
    ProjectCrawlResult,
    RefactorSecurityIssue,
    RefactorSimulationResult,
    SurgicalExtractionResult,
    SymbolicResult,
    SymbolReference,
    SymbolReferencesResult,
    TestGenerationResult,
    UnifiedSinkResult,
)

from code_scalpel.mcp.models.security import (
    DependencyInfo,
    DependencyScanResult,
    DependencyScanResultModel,
    DependencyVulnerability,
    SecurityResult,
    TypeEvaporationResultModel,
    VulnerabilityFindingModel,
    VulnerabilityInfo,
)

from code_scalpel.mcp.models.graph import (
    CallEdgeModel,
    CallGraphResultModel,
    CallNodeModel,
    CrossFileDependenciesResult,
    CrossFileSecurityResult,
    CrossFileVulnerabilityModel,
    ExtractedSymbolModel,
    GraphNeighborhoodResult,
    ImportNodeModel,
    ModuleInfo,
    NeighborhoodEdgeModel,
    NeighborhoodNodeModel,
    PackageInfo,
    ProjectMapResult,
    SymbolDefinitionModel,
    TaintFlowModel,
)

from code_scalpel.mcp.models.policy import (
    CodePolicyCheckResult,
    PathValidationResult,
    PolicyVerificationResult,
)

# =============================================================================
# TOOLS - Async MCP tool functions
# =============================================================================
from code_scalpel.mcp.tools.analyze import analyze_code
from code_scalpel.mcp.tools.security import (
    scan_dependencies,
    security_scan,
    type_evaporation_scan,
    unified_sink_detect,
)
from code_scalpel.mcp.tools.extraction import (
    extract_code,
    rename_symbol,
    update_symbol,
)
from code_scalpel.mcp.tools.symbolic import (
    generate_unit_tests,
    simulate_refactor,
    symbolic_execute,
)
from code_scalpel.mcp.tools.context import (
    crawl_project,
    get_file_context,
    get_symbol_references,
)
from code_scalpel.mcp.tools.graph import (
    cross_file_security_scan,
    get_call_graph,
    get_cross_file_dependencies,
    get_graph_neighborhood,
    get_project_map,
)
from code_scalpel.mcp.tools.policy import (
    code_policy_check,
    validate_paths,
    verify_policy_integrity,
)

# =============================================================================
# RESOURCES - MCP resource handlers
# =============================================================================
from code_scalpel.mcp.resources import (
    get_code_resource,
    get_project_call_graph,
    get_project_dependencies,
    get_project_structure,
)

# =============================================================================
# PROMPTS - Intent-driven workflow prompts
# =============================================================================
from code_scalpel.mcp.prompts import (
    deep_security_audit,
    explain_and_document,
    map_architecture,
    modernize_legacy,
    safe_refactor,
    verify_supply_chain,
)

# =============================================================================
# LOGGING
# =============================================================================
from code_scalpel.mcp.mcp_logging import (
    MCPAnalytics,
    ToolInvocation,
    get_analytics,
    log_tool_error,
    log_tool_invocation,
    log_tool_success,
    mcp_logger,
)

# =============================================================================
# SYNC HELPERS - For testing (internal use, prefixed with _)
# These remain in server.py but are re-exported for test compatibility
# =============================================================================

if TYPE_CHECKING:
    # Make sync helpers visible to type checkers
    pass


def _load_server():
    """Lazy import server module to avoid circular imports."""
    from code_scalpel.mcp import server as _server
    return _server


def __getattr__(name: str) -> Any:
    """Lazy load sync helpers and constants from server.py."""
    # Sync helper functions (internal, for testing)
    _server_attrs = {
        "_analyze_code_sync",
        "_count_complexity",
        "_crawl_project_sync",
        "_generate_tests_sync",
        "_get_call_graph_sync",
        "_get_cross_file_dependencies_sync",
        "_get_file_context_sync",
        "_get_project_map_sync",
        "_get_symbol_references_sync",
        "_security_scan_sync",
        "_simulate_refactor_sync",
        "_symbolic_execute_sync",
        "_validate_code",
        "_validate_paths_sync",
        "_verify_policy_integrity_sync",
        # Constants
        "MAX_CODE_SIZE",
        "PROJECT_ROOT",
        "ALLOWED_ROOTS",
        # Deprecated prompts (redirect to new names)
        "security_audit_workflow_prompt",
        "safe_refactor_workflow_prompt",
    }
    if name in _server_attrs:
        server = _load_server()
        return getattr(server, name)

    raise AttributeError(f"module 'code_scalpel.mcp' has no attribute {name!r}")


def get_mcp():
    """Return the FastMCP server instance."""
    return mcp


def run_server(*args, **kwargs):
    """Run the MCP server."""
    return _load_server().run_server(*args, **kwargs)


__all__ = [
    # Protocol
    "mcp",
    "get_mcp",
    "run_server",
    "_get_current_tier",
    "set_current_tier",
    # Models - Core
    "AnalysisResult",
    "ClassInfo",
    "ContextualExtractionResult",
    "CrawlClassInfo",
    "CrawlFileResult",
    "CrawlFunctionInfo",
    "CrawlSummary",
    "ExecutionPath",
    "FileContextResult",
    "FunctionInfo",
    "GeneratedTestCase",
    "PathCondition",
    "PatchResultModel",
    "ProjectCrawlResult",
    "RefactorSecurityIssue",
    "RefactorSimulationResult",
    "SurgicalExtractionResult",
    "SymbolicResult",
    "SymbolReference",
    "SymbolReferencesResult",
    "TestGenerationResult",
    "UnifiedSinkResult",
    # Models - Security
    "DependencyInfo",
    "DependencyScanResult",
    "DependencyScanResultModel",
    "DependencyVulnerability",
    "SecurityResult",
    "TypeEvaporationResultModel",
    "VulnerabilityFindingModel",
    "VulnerabilityInfo",
    # Models - Graph
    "CallEdgeModel",
    "CallGraphResultModel",
    "CallNodeModel",
    "CrossFileDependenciesResult",
    "CrossFileSecurityResult",
    "CrossFileVulnerabilityModel",
    "ExtractedSymbolModel",
    "GraphNeighborhoodResult",
    "ImportNodeModel",
    "ModuleInfo",
    "NeighborhoodEdgeModel",
    "NeighborhoodNodeModel",
    "PackageInfo",
    "ProjectMapResult",
    "SymbolDefinitionModel",
    "TaintFlowModel",
    # Models - Policy
    "CodePolicyCheckResult",
    "PathValidationResult",
    "PolicyVerificationResult",
    # Tools
    "analyze_code",
    "code_policy_check",
    "crawl_project",
    "cross_file_security_scan",
    "extract_code",
    "generate_unit_tests",
    "get_call_graph",
    "get_cross_file_dependencies",
    "get_file_context",
    "get_graph_neighborhood",
    "get_project_map",
    "get_symbol_references",
    "rename_symbol",
    "scan_dependencies",
    "security_scan",
    "simulate_refactor",
    "symbolic_execute",
    "type_evaporation_scan",
    "unified_sink_detect",
    "update_symbol",
    "validate_paths",
    "verify_policy_integrity",
    # Resources
    "get_code_resource",
    "get_project_call_graph",
    "get_project_dependencies",
    "get_project_structure",
    # Prompts
    "deep_security_audit",
    "explain_and_document",
    "map_architecture",
    "modernize_legacy",
    "safe_refactor",
    "verify_supply_chain",
    # Logging
    "MCPAnalytics",
    "ToolInvocation",
    "get_analytics",
    "log_tool_error",
    "log_tool_invocation",
    "log_tool_success",
    "mcp_logger",
]
