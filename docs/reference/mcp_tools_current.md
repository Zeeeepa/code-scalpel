# Code Scalpel MCP Tools Reference

**Generated:** January 26, 2026  
**Version:** 1.1.0

## Available Tools

Code Scalpel v1.1.0 exposes the following MCP tools:

### Analysis Tools

- **analyze_code** - Analyze source code structure, metrics, and quality indicators
- **unified_sink_detect** - Detect security sinks and data flow vulnerabilities
- **type_evaporation_scan** - Scan for type annotation gaps and weaknesses
- **scan_dependencies** - Scan project dependencies for vulnerabilities (requires Pro tier)

### Security & Refactoring

- **security_scan** - Comprehensive security analysis of code
- **extract_code** - Extract specific functions, classes, or methods from code
- **rename_symbol** - Rename symbols across a codebase (requires Pro tier)
- **update_symbol** - Update symbol references in files (requires Pro tier)

### Symbolic Analysis

- **symbolic_execute** - Perform symbolic execution to find execution paths
- **generate_unit_tests** - Generate unit tests for code functions
- **simulate_refactor** - Simulate refactoring changes with dry-run

### Context & Dependency Analysis

- **crawl_project** - Crawl project structure and analyze organization (requires Pro tier)
- **get_file_context** - Get surrounding context for a specific file
- **get_symbol_references** - Find all references to a symbol (requires Pro tier)
- **get_call_graph** - Analyze call graphs and function dependencies (requires Pro tier)
- **get_graph_neighborhood** - Get neighborhood around a symbol in the graph (requires Pro tier)
- **get_project_map** - Get high-level project structure map (requires Pro tier)
- **get_cross_file_dependencies** - Analyze dependencies across files (requires Pro tier)
- **cross_file_security_scan** - Security scan across multiple files (requires Pro tier)

### Policy & Validation

- **validate_paths** - Validate file paths and project structure
- **verify_policy_integrity** - Verify policy configuration integrity
- **code_policy_check** - Check code against custom policies (requires Enterprise tier)

## Tier Availability

- **Community**: Basic analysis, security scanning, unit test generation
- **Pro**: Advanced analysis, cross-file dependencies, symbol operations
- **Enterprise**: Custom policies, advanced governance, compliance checking

For feature details and parameters, see individual tool documentation or the [MCP Tools Tier Matrix](./mcp_tools_by_tier.md).
