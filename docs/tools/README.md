# Code Scalpel MCP Tools Reference Documentation

**Last Updated:** January 25, 2026  
**Version:** 1.0.2  
**Tool Count:** 22 MCP Tools  
**Status:** Phase 3 - Transport Optimization Complete

---

## Quick Navigation

### By Category

- **[Extraction & Refactoring](./extraction-tools.md)** (3 tools)
  - extract_code
  - rename_symbol
  - update_symbol

- **[Symbolic Execution & Testing](./symbolic-tools.md)** (3 tools)
  - symbolic_execute
  - generate_unit_tests
  - simulate_refactor

- **[Security & Vulnerability Scanning](./security-tools.md)** (4 tools)
  - unified_sink_detect
  - type_evaporation_scan
  - scan_dependencies
  - security_scan

- **[Policy & Governance](./policy-tools.md)** (3 tools)
  - validate_paths
  - verify_policy_integrity
  - code_policy_check

- **[Context & Discovery](./context-tools.md)** (3 tools)
  - crawl_project
  - get_file_context
  - get_symbol_references

- **[Code Analysis](./analysis-tools.md)** (1 tool)
  - analyze_code

- **[Graph & Dependency Analysis](./graph-tools.md)** (5 tools)
  - get_call_graph
  - get_graph_neighborhood
  - get_project_map
  - get_cross_file_dependencies
  - cross_file_security_scan

---

## Tier System Overview

Code Scalpel uses a **3-tier licensing model** with cumulative capabilities:

### Tier Hierarchy

```
┌─────────────────────────────────────────────┐
│         ENTERPRISE (Unlimited)              │
│    • All Pro features                       │
│    • Enterprise-grade limits                │
│    • Custom policies & compliance           │
│    • Advanced analytics & reporting         │
└─────────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────────┐
│   PRO (Scaled for Teams)                    │
│    • All Community features                 │
│    • Higher limits                          │
│    • Advanced analysis features             │
│    • Cross-file analysis                    │
└─────────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────────┐
│  COMMUNITY (Free, Single Developer)         │
│    • Basic analysis features                │
│    • Single-file operations                 │
│    • Limited scope (100-500 units)          │
│    • No custom policies                     │
└─────────────────────────────────────────────┘
```

**All 22 tools are available at all tiers.** Tier differences manifest as:
1. **Input constraints** - Max size, depth, scope (Community < Pro < Enterprise)
2. **Output scope** - What data is returned (Basic < Enhanced < Complete)
3. **Feature availability** - Advanced features unlock at higher tiers
4. **Performance** - Response time goals differ by tier
5. **Error handling** - More forgiving at higher tiers

---

## Documentation Structure

Each tool document includes:

### 1. **Overview**
   - Purpose and use cases
   - Primary benefits
   - Common workflows

### 2. **Input Specification**
   - Parameter list with types
   - Tier-specific constraints
   - Validation rules
   - Error conditions

### 3. **Output Specification**
   - Response structure (JSON schema)
   - Tier-specific variations
   - Example responses for each tier

### 4. **Tier Comparison Matrix**
   - Side-by-side limits and capabilities
   - Feature availability table
   - Performance characteristics

### 5. **Error Handling**
   - Standard error codes
   - Tier-specific error messages
   - Mitigation strategies

### 6. **Example Requests & Responses**
   - Real-world usage examples
   - Multi-tier demonstrations
   - Error case handling

### 7. **Performance Considerations**
   - Latency expectations per tier
   - Throughput limits
   - Memory/CPU implications

### 8. **Upgrade Paths**
   - Feature migration from Community→Pro→Enterprise
   - When to upgrade
   - Architectural considerations

---

## Response Envelope Structure

All tools return responses wrapped in a standardized `ToolResponseEnvelope`:

### Standard Response Format

```json
{
  "tier": "community|pro|enterprise|null",
  "tool_version": "1.0.2",
  "tool_id": "extract_code|rename_symbol|...",
  "request_id": "uuid-v4",
  "capabilities": ["envelope-v1"],
  "duration_ms": 1234,
  "error": null,
  "warnings": [],
  "upgrade_hints": [],
  "data": {}
}
```

### Error Response Format

```json
{
  "tier": "community",
  "tool_version": "1.0.2",
  "tool_id": "extract_code",
  "request_id": "uuid-v4",
  "error": {
    "code": "resource_exhausted",
    "message": "File size exceeds limit (max 1 MB for Community tier)",
    "details": {
      "limit_mb": 1,
      "actual_mb": 5,
      "tier": "community"
    }
  },
  "upgrade_hints": [
    {
      "hint": "upgrade_tier",
      "feature": "Large file support",
      "current_limit": "1 MB",
      "pro_limit": "10 MB",
      "enterprise_limit": "100 MB",
      "upgrade_url": "https://code-scalpel.ai/pricing"
    }
  ]
}
```

### Standard Error Codes

| Code | Tier Impact | Meaning |
|------|-------------|---------|
| `invalid_argument` | All | Invalid input parameter |
| `invalid_path` | All | File/directory path not found |
| `forbidden` | All | Permission denied (RBAC) |
| `not_found` | All | Symbol/entity not found |
| `timeout` | All | Execution exceeded time limit |
| `too_large` | Community/Pro | Input exceeds size limit |
| `resource_exhausted` | Community/Pro | Hit tier-specific limit |
| `not_implemented` | All | Feature not available in tier |
| `upgrade_required` | Community/Pro | Feature requires higher tier |
| `dependency_unavailable` | All | External dependency missing |
| `internal_error` | All | Server error |

---

## Common Input Constraints by Tier

### File Size Limits

| Tool Category | Community | Pro | Enterprise |
|---------------|-----------|-----|-----------|
| Single file analysis | 500 KB | 10 MB | 100 MB |
| Project crawl | 100 files | 1,000 files | Unlimited |
| Batch operations | 10 items | 100 items | Unlimited |

### Search & Traversal Limits

| Operation | Community | Pro | Enterprise |
|-----------|-----------|-----|-----------|
| Graph depth | 3 | 50 | Unlimited |
| Node count | 50-100 | 500 | Unlimited |
| File search | 100 | 1,000 | Unlimited |
| Reference count | 100 | Unlimited | Unlimited |

### Feature Availability

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| Cross-file analysis | No | Limited | Full |
| Custom rules | No | Limited | Yes |
| Compliance checks | No | No | Yes |
| Data redaction | No | No | Yes |
| Audit logging | No | No | Yes |

---

## How to Use This Documentation

### For API Users
1. Find your tool in the category links above
2. Read the **Overview** section for quick understanding
3. Check **Input Specification** for parameter details
4. Review **Output Specification** for response structure
5. Jump to **Example Requests** for working code

### For Administrators
1. Review **Tier Comparison Matrix** for feature planning
2. Check **Input Constraints** to understand deployment limits
3. Reference **Performance Considerations** for capacity planning
4. Review error handling for support planning

### For Product/Sales
1. Check **Tier Comparison Matrix** for feature differentiation
2. Review **Upgrade Paths** to understand customer journey
3. Reference **Upgrade Hints** for upsell opportunities
4. Use examples in customer discussions

---

## Global Configuration

### Environment Variables

```bash
# License tier (overrides JWT)
export CODE_SCALPEL_TIER=enterprise  # community|pro|enterprise

# Debug output with detailed logging
export SCALPEL_MCP_OUTPUT=DEBUG      # DEBUG|INFO|WARNING

# Override limits file location
export CODE_SCALPEL_LIMITS_FILE=~/.code-scalpel/custom-limits.toml
```

### Configuration File

Edit `~/.code-scalpel/limits.toml` to customize tier limits:

```toml
[community]
max_file_size_mb = 1
max_files_crawl = 100
max_graph_depth = 3

[pro]
max_file_size_mb = 10
max_files_crawl = 1000
max_graph_depth = 50

[enterprise]
max_file_size_mb = 100
max_files_crawl = "unlimited"
max_graph_depth = "unlimited"
```

---

## Migration from Tier to Tier

### Community → Pro

**When to upgrade:**
- Working with multiple files (>100)
- Need cross-file dependency analysis
- Require advanced features (data-driven tests, framework detection)
- Team of 2-5 developers

**Code changes:** Minimal - same API, just higher limits and new optional parameters

### Pro → Enterprise

**When to upgrade:**
- Working with monorepos or large projects (>1,000 files)
- Need compliance/audit features (HIPAA, SOC2, GDPR)
- Require custom rules and policies
- Enterprise team (50+ developers)

**Code changes:** Optional new parameters for compliance, policies, audit logging

---

## Support & Resources

- **Documentation Site:** https://docs.code-scalpel.ai
- **GitHub Issues:** https://github.com/3D-Tech-Solutions/code-scalpel/issues
- **API Reference:** See individual tool docs in this directory
- **Examples:** https://github.com/3D-Tech-Solutions/code-scalpel/tree/main/examples
- **Community Forum:** https://community.code-scalpel.ai

---

## Tool Index Summary

| # | Tool | Category | Community | Pro | Enterprise |
|---|------|----------|-----------|-----|-----------|
| 1 | extract_code | Extraction | 1 file | Direct deps | Unlimited |
| 2 | rename_symbol | Extraction | Definition | Cross-file | Organization |
| 3 | update_symbol | Extraction | 10/call | Unlimited | Unlimited + audit |
| 4 | symbolic_execute | Testing | 50 paths | Unlimited | Unlimited + distributed |
| 5 | generate_unit_tests | Testing | 5 tests | 20 tests | Unlimited + bug repro |
| 6 | simulate_refactor | Testing | Basic | Advanced | Deep + custom rules |
| 7 | unified_sink_detect | Security | 4 langs | Extended | All langs + remediation |
| 8 | type_evaporation_scan | Security | Frontend | Frontend+backend | Schema generation |
| 9 | scan_dependencies | Security | 50 deps | Unlimited | Unlimited + custom DB |
| 10 | security_scan | Security | OWASP | NoSQL/LDAP | Custom policies |
| 11 | validate_paths | Policy | 100 paths | Unlimited | Unlimited |
| 12 | verify_policy_integrity | Policy | No verify | Verify | Verify + audit |
| 13 | code_policy_check | Policy | Style guide | Best practice | Compliance (HIPAA/SOC2) |
| 14 | crawl_project | Context | 100 files | Framework detect | Monorepo + cross-repo |
| 15 | get_file_context | Context | 500 lines | 2,000 lines | Unlimited + RBAC |
| 16 | get_symbol_references | Context | 100 refs | Unlimited | Impact analysis |
| 17 | analyze_code | Analysis | Basic AST | Code smells | Custom rules |
| 18 | get_call_graph | Graph | depth=3 | depth=50 | Unlimited + traces |
| 19 | get_graph_neighborhood | Graph | k=1 | k=5 | Unlimited |
| 20 | get_project_map | Graph | 100 files | 1,000 files | Service boundaries |
| 21 | get_cross_file_dependencies | Graph | depth=1-2 | depth=5 | Unlimited |
| 22 | cross_file_security_scan | Graph | 10 modules | 100 modules | Unlimited |

---

## Document Versions

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-25 | Initial comprehensive documentation for 22 tools, all tiers |

---

**Next:** Read individual tool documentation in the categories above for detailed API reference.
