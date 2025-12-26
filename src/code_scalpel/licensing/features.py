"""
Feature Capabilities - Hierarchical feature gating for all MCP tools.

[20251225_FEATURE] Implements parameter-level feature gating instead of tool-level hiding.

This module defines capabilities and limits for each tool at each tier.
ALL tools are available at COMMUNITY tier, but with restricted parameters/features.

Architecture:
    - All 20 MCP tools available at all tiers
    - Features/parameters gated by capabilities
    - Limits enforced at runtime
    - Automatic upgrade hints generation

Usage:
    from code_scalpel.licensing.features import get_tool_capabilities

    caps = get_tool_capabilities("security_scan", "community")
    if "full_vulnerability_list" in caps["capabilities"]:
        # Show all findings
    else:
        # Limit to caps["limits"]["max_findings"]
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# [20251225_FEATURE] Comprehensive tool capability matrix
# Every tool has capabilities and limits defined for each tier
TOOL_CAPABILITIES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "analyze_code": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_ast", "function_inventory", "class_inventory", "imports"},
            "limits": {"max_file_size_mb": 1},
            "description": "Basic AST parsing and structure extraction",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_ast", "function_inventory", "class_inventory", "imports",
                "complexity_metrics", "halstead_metrics", "cognitive_complexity",
                "dependency_graph", "code_smells"
            },
            "limits": {"max_file_size_mb": 10},
            "description": "Full analysis with complexity metrics",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_ast", "function_inventory", "class_inventory", "imports",
                "complexity_metrics", "halstead_metrics", "cognitive_complexity",
                "dependency_graph", "custom_rules", "compliance_checks",
                "organization_patterns", "code_smells"
            },
            "limits": {"max_file_size_mb": 100},
            "description": "Advanced analysis with custom rules and compliance",
        },
    },
    
    "security_scan": {
        "community": {
            "enabled": True,
            "capabilities": {
                "basic_vulnerabilities",
                "owasp_top_10_checks",
                "ast_pattern_matching",
                "sql_injection_detection",
                "xss_detection",
                "command_injection_detection"
            },
            "limits": {
                "max_findings": 50,
                "max_file_size_kb": 500,
            },
            "description": "Standard OWASP Top 10 checks using AST pattern matching (50 findings max, 500KB files)",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_vulnerabilities",
                "owasp_top_10_checks",
                "ast_pattern_matching",
                "sql_injection_detection",
                "xss_detection",
                "command_injection_detection",
                "context_aware_scanning",
                "sanitizer_recognition",
                "data_flow_sensitive_analysis",
                "false_positive_reduction",
            },
            "limits": {
                "max_findings": None,
                "max_file_size_kb": None,
            },
            "description": "Context-Aware scanning that recognizes sanitization functions (unlimited)",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_vulnerabilities",
                "owasp_top_10_checks",
                "ast_pattern_matching",
                "sql_injection_detection",
                "xss_detection",
                "command_injection_detection",
                "context_aware_scanning",
                "sanitizer_recognition",
                "data_flow_sensitive_analysis",
                "false_positive_reduction",
                "custom_policy_engine",
                "org_specific_rules",
                "log_encryption_enforcement",
                "compliance_rule_checking",
            },
            "limits": {
                "max_findings": None,
                "max_file_size_kb": None,
                "custom_rules_limit": None,
            },
            "description": "Custom Policy Engine for org-specific security rules (unlimited)",
        },
    },
    "get_project_map": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_map", "mermaid_diagram"},
            "limits": {"max_modules": 50},
            "description": "Basic project structure and package diagram",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_map", "mermaid_diagram",
                "module_relationships", "architectural_layers"
            },
            "limits": {"max_modules": 200},
            "description": "Architecture analysis with layer detection",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_map", "mermaid_diagram",
                "module_relationships", "architectural_layers",
                "city_map_visualization", "churn_analysis", "bug_hotspots"
            },
            "limits": {"max_modules": 1000},
            "description": "Full codebase visualization with churn and hotspots",
        },
    },    
    "extract_code": {
        "community": {
            "enabled": True,
            "capabilities": {"single_file_extraction", "basic_symbols"},
            "limits": {
                "include_cross_file_deps": False,
                "max_depth": 0,
                "max_extraction_size_mb": 1,
            },
            "description": "Single-file symbol extraction only",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "single_file_extraction", "basic_symbols",
                "cross_file_deps", "context_extraction"
            },
            "limits": {
                "include_cross_file_deps": True,
                "max_depth": 1,  # Direct dependencies only
                "max_extraction_size_mb": 10,
            },
            "description": "Cross-file extraction with direct dependencies",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "single_file_extraction", "basic_symbols",
                "cross_file_deps", "context_extraction",
                "org_wide_resolution", "custom_extraction_patterns"
            },
            "limits": {
                "include_cross_file_deps": True,
                "max_depth": None,  # Unlimited
                "max_extraction_size_mb": 100,
            },
            "description": "Unlimited depth with organization-wide resolution",
        },
    },
    
    "symbolic_execute": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_symbolic_execution", "simple_constraints"},
            "limits": {
                "max_paths": 3,
                "max_depth": 5,
                "constraint_types": ["int", "bool"],
            },
            "description": "Basic symbolic execution (3 paths max)",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_symbolic_execution", "simple_constraints",
                "complex_constraints", "string_constraints"
            },
            "limits": {
                "max_paths": 10,
                "max_depth": 10,
                "constraint_types": ["int", "bool", "string", "float"],
            },
            "description": "Advanced symbolic execution with string constraints",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_symbolic_execution", "simple_constraints",
                "complex_constraints", "string_constraints",
                "custom_solvers", "advanced_types"
            },
            "limits": {
                "max_paths": None,  # Unlimited
                "max_depth": None,
                "constraint_types": "all",
            },
            "description": "Unlimited symbolic execution with custom solvers",
        },
    },
    
    "generate_unit_tests": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_test_generation"},
            "limits": {
                "max_test_cases": 5,
                "test_frameworks": ["pytest"],
            },
            "description": "Basic test generation (5 tests max)",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_test_generation",
                "advanced_test_generation", "edge_case_detection"
            },
            "limits": {
                "max_test_cases": 20,
                "test_frameworks": ["pytest", "unittest"],
            },
            "description": "Advanced test generation with edge cases",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_test_generation",
                "advanced_test_generation", "edge_case_detection",
                "custom_test_templates", "coverage_optimization"
            },
            "limits": {
                "max_test_cases": None,
                "test_frameworks": "all",
            },
            "description": "Unlimited tests with custom templates",
        },
    },
    
    "crawl_project": {
        "community": {
            "enabled": True,
            "capabilities": {"file_inventory", "entrypoint_detection", "basic_stats"},
            "limits": {
                "max_files": 100,
                "parsing_enabled": False,
                "complexity_analysis": False,
            },
            "description": "Discovery mode: file inventory and entrypoints only",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "file_inventory", "entrypoint_detection", "basic_stats",
                "full_ast_parsing", "complexity_analysis", "dependency_graph"
            },
            "limits": {
                "max_files": 1000,
                "parsing_enabled": True,
                "complexity_analysis": True,
            },
            "description": "Deep crawl with full AST parsing and complexity",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "file_inventory", "entrypoint_detection", "basic_stats",
                "full_ast_parsing", "complexity_analysis", "dependency_graph",
                "cross_repo_analysis", "custom_metrics", "org_indexing"
            },
            "limits": {
                "max_files": None,  # Unlimited
                "parsing_enabled": True,
                "complexity_analysis": True,
            },
            "description": "Unlimited files with organization-wide indexing",
        },
    },
    
    "get_call_graph": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_call_graph"},
            "limits": {
                "max_depth": 3,
                "max_nodes": 50,
            },
            "description": "Call graph limited to 3 hops",
        },
        "pro": {
            "enabled": True,
            "capabilities": {"basic_call_graph", "advanced_call_graph"},
            "limits": {
                "max_depth": 50,
                "max_nodes": 500,
            },
            "description": "Configurable depth call graphs",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_call_graph", "advanced_call_graph",
                "cross_project_graph", "custom_graph_analysis"
            },
            "limits": {
                "max_depth": None,
                "max_nodes": None,
            },
            "description": "Unlimited depth with cross-project analysis",
        },
    },
    
    "get_cross_file_dependencies": {
        "community": {
            "enabled": True,
            "capabilities": {
                "direct_import_mapping",
                "circular_dependency_detection",
                "import_graph_generation"
            },
            "limits": {
                "max_depth": 1,
                "max_files": 50,
            },
            "description": "Direct imports only, circular dependency detection",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "direct_import_mapping",
                "circular_dependency_detection",
                "import_graph_generation",
                "transitive_dependency_mapping",
                "deep_coupling_analysis",
                "dependency_chain_visualization"
            },
            "limits": {
                "max_depth": 5,
                "max_files": 500,
            },
            "description": "Transitive dependencies with coupling analysis",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "direct_import_mapping",
                "circular_dependency_detection",
                "import_graph_generation",
                "transitive_dependency_mapping",
                "deep_coupling_analysis",
                "dependency_chain_visualization",
                "architectural_firewall",
                "boundary_violation_alerts",
                "layer_constraint_enforcement",
                "dependency_rule_engine"
            },
            "limits": {
                "max_depth": None,
                "max_files": None,
            },
            "description": "Unlimited with architectural boundary enforcement",
        },
    },
    
    "get_graph_neighborhood": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_neighborhood"},
            "limits": {
                "max_k": 1,  # Immediate neighbors only
                "max_nodes": 20,
            },
            "description": "1-hop neighborhood only",
        },
        "pro": {
            "enabled": True,
            "capabilities": {"basic_neighborhood", "advanced_neighborhood"},
            "limits": {
                "max_k": 5,
                "max_nodes": 100,
            },
            "description": "Configurable k-hop traversal",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_neighborhood", "advanced_neighborhood",
                "custom_traversal", "weighted_paths"
            },
            "limits": {
                "max_k": None,
                "max_nodes": None,
            },
            "description": "Unlimited hops with custom traversal",
        },
    },
    
    "get_symbol_references": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_reference_search"},
            "limits": {
                "max_files": 10,
                "max_references": 50,
            },
            "description": "Reference search limited to 10 files",
        },
        "pro": {
            "enabled": True,
            "capabilities": {"basic_reference_search", "project_wide_search"},
            "limits": {
                "max_files": None,  # Project-wide
                "max_references": None,
            },
            "description": "Full project-wide reference search",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_reference_search", "project_wide_search",
                "cross_repo_search", "semantic_search"
            },
            "limits": {
                "max_files": None,
                "max_references": None,
            },
            "description": "Cross-repository semantic search",
        },
    },
    
    "simulate_refactor": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_simulation"},
            "limits": {
                "max_file_size_mb": 1,
                "analysis_depth": "basic",
            },
            "description": "Basic refactor simulation",
        },
        "pro": {
            "enabled": True,
            "capabilities": {"basic_simulation", "advanced_simulation", "behavior_preservation"},
            "limits": {
                "max_file_size_mb": 10,
                "analysis_depth": "advanced",
            },
            "description": "Advanced simulation with behavior checks",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_simulation", "advanced_simulation", "behavior_preservation",
                "custom_rules", "compliance_validation"
            },
            "limits": {
                "max_file_size_mb": 100,
                "analysis_depth": "deep",
            },
            "description": "Deep simulation with custom validation",
        },
    },
    
    "scan_dependencies": {
        "community": {
            "enabled": True,
            "capabilities": {
                "basic_dependency_scan",
                "cve_database_check",
                "osv_integration",
                "severity_classification"
            },
            "limits": {
                "max_dependencies": 50,
                "osv_lookup": True,
            },
            "description": "Basic CVE scanning against OSV database (50 dependencies max)",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_dependency_scan",
                "cve_database_check",
                "osv_integration",
                "severity_classification",
                "reachability_analysis",
                "vulnerable_function_call_check",
                "false_positive_reduction",
                "update_recommendations"
            },
            "limits": {
                "max_dependencies": None,
                "osv_lookup": True,
            },
            "description": "Reachability analysis - checks if vulnerable code is actually called",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_dependency_scan",
                "cve_database_check",
                "osv_integration",
                "severity_classification",
                "reachability_analysis",
                "vulnerable_function_call_check",
                "false_positive_reduction",
                "update_recommendations",
                "license_compliance_scanning",
                "typosquatting_detection",
                "supply_chain_risk_scoring",
                "compliance_reporting"
            },
            "limits": {
                "max_dependencies": None,
                "osv_lookup": True,
            },
            "description": "License compliance, typosquatting detection, supply chain risk",
        },
    },
    
    "cross_file_security_scan": {
        "community": {
            "enabled": True,
            "capabilities": {
                "basic_cross_file_scan",
                "single_module_taint_tracking",
                "source_to_sink_tracing",
                "basic_taint_propagation"
            },
            "limits": {
                "max_modules": 10,
                "max_depth": 3,
            },
            "description": "Traces taint from Source to Sink within a single service/module (10 modules, depth 3)",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_cross_file_scan",
                "single_module_taint_tracking",
                "source_to_sink_tracing",
                "basic_taint_propagation",
                "framework_aware_taint",
                "spring_bean_tracking",
                "react_context_tracking",
                "dependency_injection_resolution",
            },
            "limits": {
                "max_modules": 100,
                "max_depth": 10,
            },
            "description": "Framework-aware taint through Spring Beans, React Context (100 modules, depth 10)",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_cross_file_scan",
                "single_module_taint_tracking",
                "source_to_sink_tracing",
                "basic_taint_propagation",
                "framework_aware_taint",
                "spring_bean_tracking",
                "react_context_tracking",
                "dependency_injection_resolution",
                "global_taint_flow",
                "frontend_to_backend_tracing",
                "api_to_database_tracing",
                "microservice_boundary_crossing",
            },
            "limits": {
                "max_modules": None,
                "max_depth": None,
            },
            "description": "Global Taint Flow across Frontend, API, and Database (unlimited)",
        },
    },
    
    "verify_policy_integrity": {
        "community": {
            "enabled": True,
            "capabilities": {
                "style_guide_checking",
                "pep8_compliance",
                "eslint_rule_checking",
                "basic_policy_validation",
            },
            "limits": {
                "max_rules": 50,
            },
            "description": "Checks code against standard style guides (PEP8, ESLint)",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "style_guide_checking",
                "pep8_compliance",
                "eslint_rule_checking",
                "basic_policy_validation",
                "best_practice_checking",
                "async_try_catch_enforcement",
                "error_handling_patterns",
                "code_pattern_enforcement",
                "signature_validation",
            },
            "limits": {
                "max_rules": 200,
            },
            "description": "Best Practices checking (e.g., async error handling)",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "style_guide_checking",
                "pep8_compliance",
                "eslint_rule_checking",
                "basic_policy_validation",
                "best_practice_checking",
                "async_try_catch_enforcement",
                "error_handling_patterns",
                "code_pattern_enforcement",
                "signature_validation",
                "regulatory_compliance_audit",
                "hipaa_compliance_check",
                "soc2_compliance_check",
                "pdf_certification_generation",
                "audit_trail_logging",
            },
            "limits": {
                "max_rules": None,
            },
            "description": "Regulatory Compliance Audit with PDF certification",
        },
    },
    
    "type_evaporation_scan": {
        "community": {
            "enabled": True,
            "capabilities": {
                "explicit_any_detection",
                "typescript_any_scanning",
                "python_any_equivalent_detection",
                "basic_type_checking"
            },
            "limits": {
                "max_files": 50,
            },
            "description": "Identifies explicit 'any' usage in TypeScript/Python (50 files max)",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "explicit_any_detection",
                "typescript_any_scanning",
                "python_any_equivalent_detection",
                "basic_type_checking",
                "implicit_any_tracing",
                "network_boundary_analysis",
                "library_boundary_analysis",
                "json_parse_tracking"
            },
            "limits": {
                "max_files": 500,
            },
            "description": "Traces Implicit Any through network calls and library boundaries",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "explicit_any_detection",
                "typescript_any_scanning",
                "python_any_equivalent_detection",
                "basic_type_checking",
                "implicit_any_tracing",
                "network_boundary_analysis",
                "library_boundary_analysis",
                "json_parse_tracking",
                "runtime_validation_generation",
                "zod_schema_generation",
                "pydantic_model_generation",
                "api_contract_validation"
            },
            "limits": {
                "max_files": None,
            },
            "description": "Auto-generates runtime validation schemas (Zod/Pydantic)",
        },
    },
    
    "unified_sink_detect": {
        "community": {
            "enabled": True,
            "capabilities": {
                "sql_sink_detection",
                "shell_command_sink_detection",
                "file_operation_sinks",
                "xss_sink_detection",
                "basic_multi_language_support"
            },
            "limits": {
                "languages": ["python", "javascript", "typescript", "java"],
                "max_sinks": 50,
            },
            "description": "Identifies dangerous sinks (SQL execution, Shell commands, File operations, XSS) in 4 languages",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "sql_sink_detection",
                "shell_command_sink_detection",
                "file_operation_sinks",
                "xss_sink_detection",
                "basic_multi_language_support",
                "logic_sink_detection",
                "s3_public_write_detection",
                "email_send_detection",
                "payment_api_detection",
                "extended_language_support",
                "sink_confidence_scoring"
            },
            "limits": {
                "languages": ["python", "javascript", "typescript", "java", "go", "rust"],
                "max_sinks": None,
            },
            "description": "Logic Sinks - detects risky business operations (S3, email, payment) in 6 languages with confidence scoring",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "sql_sink_detection",
                "shell_command_sink_detection",
                "file_operation_sinks",
                "xss_sink_detection",
                "basic_multi_language_support",
                "logic_sink_detection",
                "s3_public_write_detection",
                "email_send_detection",
                "payment_api_detection",
                "extended_language_support",
                "sink_confidence_scoring",
                "sink_categorization",
                "risk_level_tagging",
                "clearance_requirement_tagging",
                "custom_sink_patterns",
                "sink_inventory_reporting"
            },
            "limits": {
                "languages": None,  # All languages supported
                "max_sinks": None,
                "custom_sinks_limit": None,
            },
            "description": "Sink Categorization with risk levels, clearance requirements, custom patterns, unlimited languages",
        },
    },
    
    "update_symbol": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_replacement"},
            "limits": {
                "backup_enabled": True,
                "validation_level": "syntax",
            },
            "description": "Basic symbol replacement with syntax validation",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_replacement",
                "semantic_validation"
            },
            "limits": {
                "backup_enabled": True,
                "validation_level": "semantic",
            },
            "description": "Semantic validation before replacement",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_replacement",
                "semantic_validation",
                "impact_analysis", "rollback_support"
            },
            "limits": {
                "backup_enabled": True,
                "validation_level": "full",
            },
            "description": "Full validation with impact analysis",
        },
    },
    
    "get_file_context": {
        "community": {
            "enabled": True,
            "capabilities": {
                "raw_source_retrieval", "ast_based_outlining",
                "function_folding", "class_folding", "line_range_extraction"
            },
            "limits": {
                "max_context_lines": 500,
            },
            "description": "Raw source code with AST-based outlining",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "raw_source_retrieval", "ast_based_outlining",
                "function_folding", "class_folding", "line_range_extraction",
                "semantic_summarization", "intent_extraction", "related_imports_inclusion"
            },
            "limits": {
                "max_context_lines": 2000,
            },
            "description": "Semantic summarization and related imports",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "raw_source_retrieval", "ast_based_outlining",
                "function_folding", "class_folding", "line_range_extraction",
                "semantic_summarization", "intent_extraction", "related_imports_inclusion",
                "pii_redaction", "secret_masking", "rbac_aware_retrieval"
            },
            "limits": {
                "max_context_lines": None,
            },
            "description": "PII redaction and RBAC-aware retrieval",
        },
    },
    
    "get_project_map": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_structure"},
            "limits": {
                "max_files": 100,
                "detail_level": "basic",
            },
            "description": "Basic project structure map",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_structure",
                "detailed_map", "dependency_tracking"
            },
            "limits": {
                "max_files": 1000,
                "detail_level": "detailed",
            },
            "description": "Detailed map with dependencies",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_structure",
                "detailed_map", "dependency_tracking",
                "cross_repo_map", "custom_views"
            },
            "limits": {
                "max_files": None,
                "detail_level": "comprehensive",
            },
            "description": "Comprehensive map with custom views",
        },
    },
    
    "validate_paths": {
        "community": {
            "enabled": True,
            "capabilities": {
                "file_existence_validation",
                "import_path_checking",
                "broken_reference_detection",
            },
            "limits": {
                "max_paths": 100,
            },
            "description": "Validates file paths in imports/reads actually exist",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "file_existence_validation",
                "import_path_checking",
                "broken_reference_detection",
                "path_alias_resolution",
                "tsconfig_paths_support",
                "webpack_alias_support",
                "dynamic_import_resolution",
                "extended_language_support",
            },
            "limits": {
                "max_paths": None,
            },
            "description": "Resolves complex path aliases and dynamic imports",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "file_existence_validation",
                "import_path_checking",
                "broken_reference_detection",
                "path_alias_resolution",
                "tsconfig_paths_support",
                "webpack_alias_support",
                "dynamic_import_resolution",
                "extended_language_support",
                "path_traversal_simulation",
                "symbolic_path_breaking",
                "security_boundary_testing",
            },
            "limits": {
                "max_paths": None,
            },
            "description": "Path traversal simulation to find security holes",
        },
    },
}


def get_tool_capabilities(tool_id: str, tier: str) -> Dict[str, Any]:
    """
    Get capabilities and limits for a tool at a specific tier.
    
    Args:
        tool_id: MCP tool identifier
        tier: Tier level ("community", "pro", "enterprise")
    
    Returns:
        Dictionary with enabled, capabilities, limits, description
    
    Example:
        caps = get_tool_capabilities("security_scan", "community")
        if "full_vulnerability_list" in caps["capabilities"]:
            # Show all findings
        else:
            # Limit to caps["limits"]["max_findings"]
    """
    tool_caps = TOOL_CAPABILITIES.get(tool_id, {})
    tier_caps = tool_caps.get(tier.lower(), {})
    
    if not tier_caps:
        logger.warning(f"Unknown tool or tier: {tool_id}/{tier}")
        # Return minimal fallback
        return {
            "enabled": True,
            "capabilities": set(),
            "limits": {},
            "description": "Unknown tool/tier",
        }
    
    return tier_caps


def has_capability(tool_id: str, capability: str, tier: str) -> bool:
    """
    Check if a tool has a specific capability at a tier.
    
    Args:
        tool_id: MCP tool identifier
        capability: Capability name
        tier: Tier level
    
    Returns:
        True if capability is available
    """
    caps = get_tool_capabilities(tool_id, tier)
    return capability in caps.get("capabilities", set())


def get_upgrade_hint(tool_id: str, missing_capability: str, current_tier: str) -> Optional[str]:
    """
    Generate upgrade hint for a missing capability.
    
    Args:
        tool_id: MCP tool identifier
        missing_capability: Capability user tried to use
        current_tier: Current tier level
    
    Returns:
        Upgrade hint message or None if capability not found in higher tiers
    """
    # Check which tier provides this capability
    for tier in ["pro", "enterprise"]:
        if tier == current_tier:
            continue
        
        if has_capability(tool_id, missing_capability, tier):
            return (
                f"Feature '{missing_capability}' requires {tier.upper()} tier. "
                f"Current tier: {current_tier.upper()}. "
                f"Upgrade at https://code-scalpel.dev/pricing"
            )
    
    return None


def get_all_tools_for_tier(tier: str) -> List[str]:
    """
    Get all tool IDs available at a tier.
    
    NOTE: This returns ALL tools since all tools are available at all tiers.
    Use get_tool_capabilities() to check feature restrictions.
    
    Args:
        tier: Tier level
    
    Returns:
        List of all tool IDs
    """
    return list(TOOL_CAPABILITIES.keys())


def get_missing_capabilities(tool_id: str, current_tier: str, target_tier: str) -> Set[str]:
    """
    Get capabilities available in target tier but not in current tier.
    
    Args:
        tool_id: MCP tool identifier
        current_tier: Current tier level
        target_tier: Target tier level
    
    Returns:
        Set of capability names
    """
    current_caps = get_tool_capabilities(tool_id, current_tier)
    target_caps = get_tool_capabilities(tool_id, target_tier)
    
    current_set = current_caps.get("capabilities", set())
    target_set = target_caps.get("capabilities", set())
    
    return target_set - current_set
