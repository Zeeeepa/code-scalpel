"""
Example: Using Parameter-Level Feature Gating in MCP Tools

[20251225_FEATURE] Demonstrates how to implement all-tools-available
with parameter/feature restrictions.

This example shows how security_scan is now available at COMMUNITY tier
but with restricted features.
"""

from code_scalpel.licensing import (
    get_current_tier,
    get_tool_capabilities,
    has_capability,
    get_upgrade_hint,
)


async def security_scan(
    code: str,
    language: str = "python",
    file_path: str = None,
) -> dict:
    """
    Security vulnerability scanning with tier-based feature gating.

    Available at ALL tiers:
    - COMMUNITY: Basic vulnerabilities, max 10 findings
    - PRO: Advanced taint analysis, unlimited findings
    - ENTERPRISE: Cross-file taint, compliance reporting

    Args:
        code: Source code to scan
        language: Programming language
        file_path: Optional file path

    Returns:
        Security scan results with tier-appropriate features
    """
    # Get current tier and capabilities
    tier = get_current_tier()
    caps = get_tool_capabilities("security_scan", tier)

    # Perform basic scan (available at all tiers)
    vulnerabilities = _perform_basic_scan(code, language)

    # Apply tier-based limits and features
    result = {
        "tier": tier,
        "tool_id": "security_scan",
        "vulnerabilities": [],
        "capabilities": list(caps["capabilities"]),
    }

    # COMMUNITY: Limit to max_findings
    if tier == "community":
        max_findings = caps["limits"]["max_findings"]
        result["vulnerabilities"] = vulnerabilities[:max_findings]

        if len(vulnerabilities) > max_findings:
            result["truncated"] = True
            result["total_vulnerabilities"] = len(vulnerabilities)
            result["upgrade_hints"] = [
                f"Showing {max_findings}/{len(vulnerabilities)} vulnerabilities.",
                get_upgrade_hint("security_scan", "full_vulnerability_list", tier),
            ]
    else:
        result["vulnerabilities"] = vulnerabilities

    # PRO+: Add advanced taint flow analysis
    if has_capability("security_scan", "advanced_taint_flow", tier):
        result["taint_flows"] = _analyze_taint_flows(code, vulnerabilities)
        result["remediation"] = _generate_remediation(vulnerabilities)

    # PRO+: Add OWASP categorization
    if has_capability("security_scan", "owasp_categorization", tier):
        result["owasp_categories"] = _categorize_owasp(vulnerabilities)

    # ENTERPRISE: Add compliance reporting
    if has_capability("security_scan", "compliance_reporting", tier):
        result["compliance_report"] = _generate_compliance_report(vulnerabilities)

    # ENTERPRISE: Add custom security rules
    if has_capability("security_scan", "custom_security_rules", tier):
        custom_findings = _apply_custom_rules(code, language)
        result["vulnerabilities"].extend(custom_findings)

    # Add upgrade hints for missing capabilities
    if tier != "enterprise":
        missing_features = []
        if tier == "community":
            missing_features = [
                "advanced_taint_flow",
                "remediation_suggestions",
                "owasp_categorization",
            ]
        elif tier == "pro":
            missing_features = [
                "compliance_reporting",
                "custom_security_rules",
            ]

        if "upgrade_hints" not in result:
            result["upgrade_hints"] = []

        for feature in missing_features:
            hint = get_upgrade_hint("security_scan", feature, tier)
            if hint:
                result["upgrade_hints"].append(hint)

    return result


async def crawl_project(
    directory: str,
    complexity_threshold: int = 10,
) -> dict:
    """
    Project-wide code analysis with tier-based crawl depth.

    Available at ALL tiers:
    - COMMUNITY: Discovery mode (file inventory, entrypoints, max 100 files)
    - PRO: Deep crawl (full AST parsing, complexity, max 1000 files)
    - ENTERPRISE: Unlimited files with organization-wide indexing

    Args:
        directory: Project root directory
        complexity_threshold: Complexity warning threshold

    Returns:
        Project crawl results with tier-appropriate depth
    """
    tier = get_current_tier()
    caps = get_tool_capabilities("crawl_project", tier)

    result = {
        "tier": tier,
        "tool_id": "crawl_project",
        "capabilities": list(caps["capabilities"]),
    }

    # Get file inventory (all tiers)
    files = _discover_files(directory)

    # Apply file limit
    max_files = caps["limits"]["max_files"]
    if max_files and len(files) > max_files:
        files = files[:max_files]
        result["truncated"] = True
        result["upgrade_hints"] = [
            f"Analyzed {max_files} files. Upgrade for more.",
            get_upgrade_hint("crawl_project", "full_ast_parsing", tier),
        ]

    result["file_count"] = len(files)
    result["files"] = [f["path"] for f in files]

    # COMMUNITY: Discovery mode only
    if tier == "community":
        result["mode"] = "discovery"
        result["entrypoints"] = _detect_entrypoints(files)
        result["basic_stats"] = {
            "total_lines": sum(f.get("lines", 0) for f in files),
            "languages": list(set(f.get("language") for f in files)),
        }
        return result

    # PRO+: Full AST parsing and complexity analysis
    if has_capability("crawl_project", "full_ast_parsing", tier):
        result["mode"] = "deep"
        parsed_files = _parse_all_files(files)
        result["functions"] = _extract_all_functions(parsed_files)
        result["classes"] = _extract_all_classes(parsed_files)

    if has_capability("crawl_project", "complexity_analysis", tier):
        result["complexity_warnings"] = _find_complex_functions(
            result["functions"], complexity_threshold
        )

    if has_capability("crawl_project", "dependency_graph", tier):
        result["dependency_graph"] = _build_dependency_graph(parsed_files)

    # ENTERPRISE: Organization-wide features
    if has_capability("crawl_project", "org_indexing", tier):
        result["org_index"] = _index_for_organization(parsed_files)

    if has_capability("crawl_project", "custom_metrics", tier):
        result["custom_metrics"] = _apply_custom_metrics(parsed_files)

    return result


async def extract_code(
    file_path: str,
    target_type: str,
    target_name: str,
    include_cross_file_deps: bool = False,
    max_depth: int = 0,
) -> dict:
    """
    Code extraction with tier-based dependency depth.

    Available at ALL tiers:
    - COMMUNITY: Single-file extraction only
    - PRO: Cross-file dependencies (depth=1)
    - ENTERPRISE: Unlimited depth

    Args:
        file_path: File to extract from
        target_type: "function", "class", or "method"
        target_name: Symbol name
        include_cross_file_deps: Whether to resolve dependencies
        max_depth: Maximum dependency depth

    Returns:
        Extracted code with tier-appropriate dependencies
    """
    tier = get_current_tier()
    caps = get_tool_capabilities("extract_code", tier)

    result = {
        "tier": tier,
        "tool_id": "extract_code",
        "capabilities": list(caps["capabilities"]),
    }

    # Extract the target symbol (all tiers)
    extracted = _extract_symbol(file_path, target_type, target_name)
    result["code"] = extracted["code"]
    result["lines"] = extracted["lines"]

    # Check cross-file dependency permission
    if include_cross_file_deps:
        if not caps["limits"]["include_cross_file_deps"]:
            result["error"] = "Cross-file dependencies require PRO tier"
            result["upgrade_hints"] = [
                get_upgrade_hint("extract_code", "cross_file_deps", tier)
            ]
            return result

        # Apply depth limit
        tier_max_depth = caps["limits"]["max_depth"]
        if tier_max_depth is not None:
            actual_depth = min(max_depth, tier_max_depth)
            if max_depth > tier_max_depth:
                result["upgrade_hints"] = [
                    f"Depth limited to {tier_max_depth} (requested {max_depth}).",
                    get_upgrade_hint("extract_code", "org_wide_resolution", tier),
                ]
        else:
            actual_depth = max_depth

        # Resolve dependencies
        deps = _resolve_dependencies(file_path, extracted, actual_depth)
        result["dependencies"] = deps
        result["depth_used"] = actual_depth

    # ENTERPRISE: Organization-wide resolution
    if has_capability("extract_code", "org_wide_resolution", tier):
        result["org_symbols"] = _resolve_org_symbols(target_name)

    return result


# Mock implementations for demo
def _perform_basic_scan(code, language):
    return [
        {"type": "sql_injection", "line": 42, "severity": "high"},
        {"type": "xss", "line": 56, "severity": "medium"},
    ]


def _analyze_taint_flows(code, vulnerabilities):
    return [{"source": "user_input", "sink": "sql_execute"}]


def _generate_remediation(vulnerabilities):
    return ["Use parameterized queries", "Sanitize user input"]


def _categorize_owasp(vulnerabilities):
    return {"A03:2021": 2}  # Injection


def _generate_compliance_report(vulnerabilities):
    return {"soc2": "failed", "hipaa": "passed"}


def _apply_custom_rules(code, language):
    return []


def _discover_files(directory):
    return [{"path": "file1.py", "lines": 100}]


def _detect_entrypoints(files):
    return ["main", "app.run"]


def _parse_all_files(files):
    return files


def _extract_all_functions(parsed):
    return ["func1", "func2"]


def _extract_all_classes(parsed):
    return ["Class1"]


def _find_complex_functions(functions, threshold):
    return []


def _build_dependency_graph(parsed):
    return {}


def _index_for_organization(parsed):
    return {}


def _apply_custom_metrics(parsed):
    return {}


def _extract_symbol(file_path, target_type, target_name):
    return {"code": "def foo(): pass", "lines": (1, 1)}


def _resolve_dependencies(file_path, extracted, depth):
    return []


def _resolve_org_symbols(name):
    return []


if __name__ == "__main__":
    import asyncio

    # Example: Community user scans code
    print("=== COMMUNITY Tier Example ===")
    result = asyncio.run(security_scan("malicious_code_here"))
    print(f"Tier: {result['tier']}")
    print(f"Vulnerabilities shown: {len(result['vulnerabilities'])}")
    if "upgrade_hints" in result:
        print("Upgrade hints:")
        for hint in result["upgrade_hints"]:
            print(f"  - {hint}")

    print("\n=== Tool Availability at All Tiers ===")
    from code_scalpel.licensing.features import get_all_tools_for_tier

    community_tools = get_all_tools_for_tier("community")
    pro_tools = get_all_tools_for_tier("pro")
    enterprise_tools = get_all_tools_for_tier("enterprise")

    print(f"COMMUNITY: {len(community_tools)} tools")
    print(f"PRO: {len(pro_tools)} tools")
    print(f"ENTERPRISE: {len(enterprise_tools)} tools")
    print("\nAll tiers have the same tools, just different capabilities!")
