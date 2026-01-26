# Code Scalpel MCP Tools - Tier Matrix

**Generated:** January 26, 2026  
**Version:** 1.1.0

## Tools by Tier

### Community Tier (Free)

Core analysis and basic security features available to all users.

| Tool | Description | Parameters |
|------|-------------|------------|
| analyze_code | Analyze source code structure, metrics, quality | `code` \| `file_path`, `language` |
| unified_sink_detect | Detect security sinks and data flows | `code` \| `file_path` |
| type_evaporation_scan | Scan for type annotation gaps | `code` \| `file_path` |
| security_scan | Basic security analysis | `code` \| `file_path` |
| extract_code | Extract functions/classes/methods | `target_type`, `target_name`, `file_path` \| `code` |
| symbolic_execute | Perform symbolic execution | `code`, `max_paths`, `max_depth` |
| generate_unit_tests | Generate unit tests | `code` \| `file_path`, `function_name`, `framework` |
| simulate_refactor | Simulate refactoring changes | `original_code`, `new_code` \| `patch` |
| get_file_context | Get context for a file | `file_path`, `context_depth` |
| validate_paths | Validate file paths | `paths` |
| verify_policy_integrity | Verify policy configuration | (no parameters) |

### Pro Tier

Advanced cross-file analysis, symbol operations, and dependency tracking.

**Additional Tools:**

| Tool | Description | Parameters |
|------|-------------|------------|
| scan_dependencies | Scan dependencies for vulnerabilities | `file_path` \| `code` |
| rename_symbol | Rename symbols across codebase | `target_name`, `new_name`, `file_path`, `scope` |
| update_symbol | Update symbol references | `target_name`, `new_code`, `file_path` |
| crawl_project | Analyze project structure | `project_root`, `discovery_mode` |
| get_symbol_references | Find all symbol references | `symbol_name`, `file_path`, `file_limit` |
| get_call_graph | Analyze call graphs | `function_name`, `file_path` |
| get_graph_neighborhood | Get graph neighborhood | `symbol_name`, `file_path`, `k_limit` |
| get_project_map | Get project structure map | `project_root` |
| get_cross_file_dependencies | Analyze cross-file dependencies | `file_path`, `depth_limit` |
| cross_file_security_scan | Security scan across files | `project_root` |

### Enterprise Tier

Custom policies, advanced governance, compliance checking, and organization-wide controls.

**Additional Tools:**

| Tool | Description | Parameters |
|------|-------------|------------|
| code_policy_check | Check code against custom policies | `code` \| `file_path`, `policy_id`, `org_context` |

**Additional Features:**

- Custom policy definitions and enforcement
- Organization-wide governance rules
- Compliance checking and reporting
- Advanced audit logging
- Multi-team access controls

## Feature Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|------------|
| Code Analysis | ✅ | ✅ | ✅ |
| Basic Security | ✅ | ✅ | ✅ |
| Unit Test Generation | ✅ | ✅ | ✅ |
| Cross-File Analysis | ❌ | ✅ | ✅ |
| Symbol Operations | ❌ | ✅ | ✅ |
| Dependency Analysis | ❌ | ✅ | ✅ |
| Custom Policies | ❌ | ❌ | ✅ |
| Org Governance | ❌ | ❌ | ✅ |
| Compliance Checking | ❌ | ❌ | ✅ |

## Licensing

Tools requiring specific tiers will return an error if accessed without an appropriate license. See the [license documentation](../guides/license_discovery.md) for setup instructions.

For detailed parameter documentation, see the [MCP Tools Reference](./mcp_tools_current.md).
