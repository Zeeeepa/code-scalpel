# All-Tools-Available Architecture Diagram

[20251225_DOCS] Visual representation of the parameter-level feature gating architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MCP CLIENT (Claude, Copilot)                │
└─────────────────────────────────────┬───────────────────────────────┘
                                      │
                                      │ MCP Request
                                      │
┌─────────────────────────────────────▼───────────────────────────────┐
│                          MCP Server Entry Point                      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Tool Handler (e.g., security_scan)                           │  │
│  │                                                               │  │
│  │  1. get_current_tier() → "community"                         │  │
│  │  2. get_tool_capabilities("security_scan", "community")      │  │
│  │  3. Perform basic operation (all tiers)                      │  │
│  │  4. Apply tier-based limits                                  │  │
│  │  5. Check capabilities for advanced features                 │  │
│  │  6. Add upgrade hints if limited/missing features            │  │
│  │  7. Return tier-appropriate result                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────┬───────────────────────────────┘
                                       │
                                       │
┌──────────────────────────────────────▼───────────────────────────────┐
│                        Licensing System                              │
│                                                                      │
│  ┌────────────────┐    ┌────────────────┐    ┌──────────────────┐  │
│  │ tier_detector  │◄───│ license_manager│◄───│ validator        │  │
│  │ .detect_tier() │    │ .get_tier()    │    │ .validate_key()  │  │
│  └────────────────┘    └────────────────┘    └──────────────────┘  │
│          │                                                           │
│          │                                                           │
│          ▼                                                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    features.py                                 │ │
│  │                                                                │ │
│  │  TOOL_CAPABILITIES = {                                        │ │
│  │    "security_scan": {                                         │ │
│  │      "community": {                                           │ │
│  │        "limits": {"max_findings": 10},                        │ │
│  │        "capabilities": {"basic_vulnerabilities"}              │ │
│  │      },                                                        │ │
│  │      "pro": {                                                  │ │
│  │        "limits": {"max_findings": None},                      │ │
│  │        "capabilities": {"advanced_taint_flow", ...}           │ │
│  │      },                                                        │ │
│  │      "enterprise": { ... }                                    │ │
│  │    }                                                           │ │
│  │  }                                                             │ │
│  │                                                                │ │
│  │  get_tool_capabilities(tool_id, tier)                         │ │
│  │  has_capability(tool_id, capability, tier)                    │ │
│  │  get_upgrade_hint(tool_id, capability, tier)                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Request Flow Example: security_scan

```
┌──────────────┐
│  User calls  │
│security_scan │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 1. Get Tier                           │
│    tier = get_current_tier()          │
│    → "community"                      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 2. Get Capabilities                   │
│    caps = get_tool_capabilities(      │
│      "security_scan", "community"     │
│    )                                  │
│    → {"limits": {"max_findings": 10}} │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 3. Run Scan (ALL TIERS)               │
│    vulnerabilities = scan(code)       │
│    → [25 vulnerabilities found]       │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 4. Apply Limits                       │
│    max = caps["limits"]["max_findings"]│
│    if len(vulns) > max:               │
│      vulns = vulns[:max]              │
│      truncated = True                 │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 5. Check Advanced Features            │
│    if has_capability(                 │
│      "advanced_taint_flow", tier      │
│    ): # False for community           │
│      # Skip advanced analysis         │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 6. Add Upgrade Hints                  │
│    if truncated:                      │
│      hints = [                        │
│        "Showing 10/25 vulnerabilities"│
│        get_upgrade_hint(...)          │
│      ]                                │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 7. Return Result                      │
│    {                                  │
│      "tier": "community",             │
│      "vulnerabilities": [10 vulns],   │
│      "truncated": true,               │
│      "upgrade_hints": [...]           │
│    }                                  │
└──────────────────────────────────────┘
```

## Capability Lookup Flow

```
get_tool_capabilities("security_scan", "community")
    │
    ├─ Check TOOL_CAPABILITIES dict
    │
    ├─ TOOL_CAPABILITIES["security_scan"]
    │   │
    │   ├─ ["community"]
    │   │   │
    │   │   ├─ "enabled": True
    │   │   ├─ "capabilities": {"basic_vulnerabilities", "single_file_taint"}
    │   │   ├─ "limits": {"max_findings": 10, "vulnerability_types": [...]}
    │   │   └─ "description": "Basic security scanning"
    │   │
    │   ├─ ["pro"]
    │   │   │
    │   │   ├─ "enabled": True
    │   │   ├─ "capabilities": {all community + "advanced_taint_flow", ...}
    │   │   ├─ "limits": {"max_findings": None, "vulnerability_types": "all"}
    │   │   └─ "description": "Advanced security analysis"
    │   │
    │   └─ ["enterprise"]
    │       │
    │       ├─ "enabled": True
    │       ├─ "capabilities": {all pro + "compliance_reporting", ...}
    │       ├─ "limits": {"max_findings": None, "vulnerability_types": "all"}
    │       └─ "description": "Enterprise security with compliance"
    │
    └─ Return capabilities dict for community tier
```

## Registry Architecture (Before vs After)

### BEFORE (v3.2.8) - Tool-Level Hiding

```
tool_registry.py:
┌────────────────────────────────────┐
│ DEFAULT_TOOLS = {                  │
│   "analyze_code": tier="community" │ ✅ Available
│   "extract_code": tier="community" │ ✅ Available
│   "security_scan": tier="pro"      │ ❌ Hidden from community
│   "symbolic_execute": tier="pro"   │ ❌ Hidden from community
│   ...                              │
│ }                                  │
└────────────────────────────────────┘

Result: Only 10/20 tools available to COMMUNITY
```

### AFTER (v3.3.0) - Parameter-Level Gating

```
tool_registry.py:
┌────────────────────────────────────┐
│ DEFAULT_TOOLS = {                  │
│   "analyze_code": tier="community" │ ✅ Available
│   "extract_code": tier="community" │ ✅ Available
│   "security_scan": tier="community"│ ✅ Available (features gated)
│   "symbolic_execute": tier="community"│ ✅ Available (features gated)
│   ...                              │
│ }                                  │
└────────────────────────────────────┘

features.py:
┌─────────────────────────────────────────────┐
│ TOOL_CAPABILITIES = {                       │
│   "security_scan": {                        │
│     "community": {limits, capabilities},    │
│     "pro": {more limits, more capabilities},│
│     "enterprise": {unlimited, all features} │
│   }                                         │
│ }                                           │
└─────────────────────────────────────────────┘

Result: All 20/20 tools available, capabilities differ by tier
```

## Tier Comparison Flowchart

```
                    ┌──────────────────┐
                    │  User executes   │
                    │  security_scan   │
                    └────────┬─────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼───────┐         ┌──────▼──────┐
        │ COMMUNITY     │         │ PRO/        │
        │ TIER          │         │ ENTERPRISE  │
        └───────┬───────┘         └──────┬──────┘
                │                         │
        ┌───────▼──────────┐     ┌───────▼──────────┐
        │ Get capabilities │     │ Get capabilities │
        │ max_findings: 10 │     │ max_findings: ∞  │
        └───────┬──────────┘     └───────┬──────────┘
                │                         │
        ┌───────▼──────────┐     ┌───────▼──────────┐
        │ Run scan         │     │ Run scan         │
        │ → 25 vulns found │     │ → 25 vulns found │
        └───────┬──────────┘     └───────┬──────────┘
                │                         │
        ┌───────▼──────────┐     ┌───────▼──────────┐
        │ Truncate to 10   │     │ Return all 25    │
        │ truncated: true  │     │                  │
        └───────┬──────────┘     └───────┬──────────┘
                │                         │
        ┌───────▼──────────┐     ┌───────▼──────────┐
        │ Add upgrade hint │     │ Add taint flows  │
        │ "Upgrade to PRO" │     │ Add remediation  │
        └───────┬──────────┘     └───────┬──────────┘
                │                         │
        ┌───────▼──────────┐     ┌───────▼──────────┐
        │ Return {         │     │ Return {         │
        │   vulns: [10],   │     │   vulns: [25],   │
        │   truncated: true│     │   taint_flows,   │
        │   hints: [...]   │     │   remediation    │
        │ }                │     │ }                │
        └──────────────────┘     └──────────────────┘
```

## Upgrade Hint Generation

```
get_upgrade_hint("security_scan", "advanced_taint_flow", "community")
    │
    ├─ Look up feature requirements
    │   TOOL_CAPABILITIES["security_scan"]["pro"]["capabilities"]
    │   contains "advanced_taint_flow"
    │
    ├─ Determine required tier: "pro"
    │
    ├─ Generate hint:
    │   "advanced_taint_flow requires PRO tier. Upgrade to access
    │    multi-path taint analysis and data flow tracking."
    │
    └─ Return hint string
```

## Tool Categories by Restriction Type

```
┌─────────────────────────────────────────────────────────────┐
│                    ALL 20 TOOLS                             │
├─────────────────────────────────┬───────────────────────────┤
│  10 TOOLS WITH TIER LIMITS      │  10 TOOLS NO LIMITS       │
│  (Gated by parameters/features) │  (Fully available)        │
├─────────────────────────────────┼───────────────────────────┤
│ • security_scan                 │ • analyze_code            │
│   Max findings (10 → ∞)         │   No restrictions         │
│                                 │                           │
│ • symbolic_execute              │ • update_symbol           │
│   Max paths (3 → 10 → ∞)        │   No restrictions         │
│                                 │                           │
│ • crawl_project                 │ • unified_sink_detect     │
│   Max files (100 → 1K → ∞)      │   No restrictions         │
│   Mode (discovery → deep)       │                           │
│                                 │ • simulate_refactor       │
│ • extract_code                  │   No restrictions         │
│   Depth (0 → 1 → ∞)             │                           │
│                                 │ • get_file_context        │
│ • generate_unit_tests           │   No restrictions         │
│   Max tests (5 → 20 → ∞)        │                           │
│                                 │ • get_symbol_references   │
│ • get_call_graph                │   No restrictions         │
│   Depth (3 → 10 → ∞)            │                           │
│                                 │ • get_project_map         │
│ • get_graph_neighborhood        │   No restrictions         │
│   k-hops (1 → 2 → ∞)            │                           │
│                                 │ • validate_paths          │
│ • scan_dependencies             │   No restrictions         │
│   Max deps (50 → ∞)             │                           │
│                                 │ • verify_policy_integrity │
│ • get_cross_file_dependencies   │   No restrictions         │
│   Depth (1 → 3 → ∞)             │                           │
│                                 │ • type_evaporation_scan   │
│ • cross_file_security_scan      │   No restrictions         │
│   Depth/modules (limited → ∞)   │                           │
└─────────────────────────────────┴───────────────────────────┘
```

## Capability Progression Example: security_scan

```
┌────────────────────────────────────────────────────────────────┐
│                        COMMUNITY TIER                          │
├────────────────────────────────────────────────────────────────┤
│ Capabilities:                                                  │
│   ✅ basic_vulnerabilities                                     │
│   ✅ single_file_taint                                         │
│                                                                │
│ Limits:                                                        │
│   • max_findings: 10                                           │
│   • vulnerability_types: [sql_injection, xss, command_injection]│
│                                                                │
│ Result:                                                        │
│   {                                                            │
│     "vulnerabilities": [10 of 25],                             │
│     "truncated": true,                                         │
│     "upgrade_hints": ["Upgrade to PRO for unlimited findings"] │
│   }                                                            │
└────────────────────────────────────────────────────────────────┘
                             ▼ UPGRADE
┌────────────────────────────────────────────────────────────────┐
│                           PRO TIER                             │
├────────────────────────────────────────────────────────────────┤
│ Capabilities:                                                  │
│   ✅ All COMMUNITY capabilities +                              │
│   ✅ advanced_taint_flow                                       │
│   ✅ full_vulnerability_list                                   │
│   ✅ remediation_suggestions                                   │
│   ✅ owasp_categorization                                      │
│                                                                │
│ Limits:                                                        │
│   • max_findings: None (unlimited)                             │
│   • vulnerability_types: "all"                                 │
│                                                                │
│ Result:                                                        │
│   {                                                            │
│     "vulnerabilities": [all 25],                               │
│     "taint_flows": [...],                                      │
│     "remediation": [...],                                      │
│     "owasp_categories": {...}                                  │
│   }                                                            │
└────────────────────────────────────────────────────────────────┘
                             ▼ UPGRADE
┌────────────────────────────────────────────────────────────────┐
│                       ENTERPRISE TIER                          │
├────────────────────────────────────────────────────────────────┤
│ Capabilities:                                                  │
│   ✅ All PRO capabilities +                                    │
│   ✅ cross_file_taint                                          │
│   ✅ compliance_reporting                                      │
│   ✅ custom_security_rules                                     │
│   ✅ automated_remediation                                     │
│   ✅ org_wide_scanning                                         │
│                                                                │
│ Limits:                                                        │
│   • max_findings: None (unlimited)                             │
│   • vulnerability_types: "all" + custom                        │
│                                                                │
│ Result:                                                        │
│   {                                                            │
│     "vulnerabilities": [all + custom rules],                   │
│     "taint_flows": [...],                                      │
│     "remediation": [...],                                      │
│     "compliance_report": {"soc2": "passed", "hipaa": "passed"},│
│     "automated_fixes": [...]                                   │
│   }                                                            │
└────────────────────────────────────────────────────────────────┘
```

## See Also

- [all_tools_available_summary.md](all_tools_available_summary.md) - Complete summary
- [features.py](../../src/code_scalpel/licensing/features.py) - Implementation
- [tier_capabilities_matrix.md](../reference/tier_capabilities_matrix.md) - Reference
