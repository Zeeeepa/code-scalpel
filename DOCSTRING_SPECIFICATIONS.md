# MCP Tool Docstring Specifications

This document contains unified docstring specifications for all 22 Code Scalpel MCP tools. Each specification follows the standardized format:
- Brief one-line description
- Tier Behavior (Community/Pro/Enterprise)
- Tier Capabilities (feature lists with limits)
- Args (parameter descriptions)
- Returns (response structure)

**No legacy tags** (`[REFACTOR]`, `[BUGFIX]`, etc.) are included in these docstrings.

---

## CONTEXT TOOLS

### 1. crawl_project

```
Crawl a project directory and analyze Python files.

Tier Behavior:
  Community: Limited to 100 files, basic file tree indexing with language breakdown and entrypoint detection
  Pro: Unlimited files/depth, parallel processing, incremental crawling, framework detection, dependency mapping, hotspot identification
  Enterprise: Unlimited files/depth/repos, distributed crawling, historical trends, custom rules, compliance scanning, monorepo support

Tier Capabilities:
  Community: Full file tree indexing, language breakdown, gitignore respect, basic statistics, entrypoint detection (max 100 files, 10 depth)
  Pro: All Community features + parallel processing, incremental crawling, smart crawl, framework entrypoint detection, dependency mapping, hotspot identification, generated code detection, Next.js/Django/Flask route detection (unlimited files/depth)
  Enterprise: All Pro features + distributed crawling, historical trend analysis, custom crawl rules, compliance scanning, incremental indexing, monorepo support, cross-repo dependency linking, 100k+ files support (unlimited files/depth/repos)

Args:
  root_path (str, optional): Root directory to crawl. Default: server's project root.
  exclude_dirs (list[str], optional): List of directory names to exclude from crawl.
  complexity_threshold (int): Threshold for complexity analysis. Default: 10.
  include_report (bool): Whether to include detailed markdown report. Default: True.
  pattern (str, optional): Optional pattern to filter files during crawl.
  pattern_type (str): Type of pattern matching - "regex" or "glob". Default: "regex".
  include_related (list[str], optional): Optional list of related file types to include alongside target files.
  ctx (Context, optional): MCP context for progress reporting.

Returns:
  ToolResponseEnvelope with ProjectCrawlResult containing:
    - success (bool): True if crawl completed successfully
    - root_path (str): Project root path that was crawled
    - timestamp (str): ISO timestamp when crawl was performed
    - summary (CrawlSummary): Statistics with total_files, total_lines_of_code, total_functions, total_classes, complexity_warnings
    - files (list[CrawlFileResult]): Detailed analysis per file with structure, complexity, language
    - errors (list[CrawlFileResult]): Files that failed analysis with error details
    - markdown_report (str): Human-readable Markdown report of crawl results
    - language_breakdown (dict): Files per detected language (Pro/Enterprise)
    - cache_hits (int): Number of files reused from cache (Pro/Enterprise incremental)
    - framework_hints (list[str]): Detected frameworks (Pro/Enterprise)
    - entrypoints (list[str]): Detected entrypoint file paths (Pro/Enterprise)
    - compliance_summary (dict): Enterprise compliance scanning results (Enterprise)
    - tier_applied (str): Tier used ("community"/"pro"/"enterprise")
    - crawl_mode (str): "discovery" (Community) or "deep" (Pro/Enterprise)
    - files_limit_applied (int, optional): Max files limit applied (None=unlimited)
    - error (str, optional): Error message if crawl failed
  - error (str): Error message if analysis failed (permission denied, invalid path, etc.)
  - tier_applied (str): Tier used for analysis (community/pro/enterprise)
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 2. get_file_context

```
Get a file overview without reading full content.

Tier Behavior:
  Community: Limited to 500 lines of context, basic file structure analysis
  Pro: Up to 2000 lines of context, code quality metrics and semantic analysis
  Enterprise: Unlimited context lines, security redaction and organizational metadata

Tier Capabilities:
  Community: Basic file structure (functions, classes, imports), up to 500 lines context limit
  Pro: All Community + code smells detection, documentation coverage, maintainability index, semantic summarization, intent extraction, related imports, smart context expansion (up to 2000 lines)
  Enterprise: All Pro + PII redaction, secret masking, API key detection, RBAC-aware retrieval, file access control, custom metadata extraction, compliance flags, technical debt scoring, owner team mapping, historical metrics (unlimited lines)

Args:
  file_path (str): Path to the file to analyze for context information.

Returns:
  ToolResponseEnvelope with FileContextResult containing:
    - success (bool): True if analysis completed successfully
    - file_path (str): Path to the analyzed file
    - language (str): Detected programming language
    - line_count (int): Total lines in file
    - functions (list): Function names and metadata
    - classes (list): Class names and metadata
    - imports (list): Import statements (max 20)
    - exports (list): Exported symbols (__all__ or equivalent)
    - complexity_score (float): Overall cyclomatic complexity
    - has_security_issues (bool): Whether file has security issues
    - summary (str): Brief description of file purpose
    - imports_truncated (bool): Whether imports list was truncated
    - total_imports (int): Total imports before truncation
    - semantic_summary (str): AI-lite semantic summary (Pro)
    - intent_tags (list[str]): Extracted intents/topics (Pro)
    - related_imports (list[str]): Resolved related imports (Pro)
    - expanded_context (str): Smartly expanded context (Pro)
    - pii_redacted (bool): Whether PII was redacted (Enterprise)
    - secrets_masked (bool): Whether secrets/API keys were masked (Enterprise)
    - redaction_summary (str): Redactions/masking actions taken (Enterprise)
    - access_controlled (bool): Whether RBAC/file access controls were applied (Enterprise)
    - code_smells (list): Detected code smells (Pro)
    - doc_coverage (float): Documentation coverage percentage (Pro)
    - maintainability_index (float): Maintainability index score (Pro)
    - custom_metadata (dict): Custom metadata from .code-scalpel/metadata.yaml (Enterprise)
    - compliance_flags (list): Compliance flags detected (Enterprise)
    - technical_debt_score (float): Technical debt score (Enterprise)
    - owners (list): Code owners from CODEOWNERS file (Enterprise)
    - historical_metrics (dict): Historical metrics from git (Enterprise)
    - tier_applied (str): The tier used for analysis
    - max_context_lines_applied (int): The max context lines limit applied
    - pro_features_enabled (bool): Whether Pro tier features were enabled
    - enterprise_features_enabled (bool): Whether Enterprise tier features were enabled
    - error (str, optional): Error message if failed
  - error (str): Error message if analysis failed (file not found, invalid syntax, etc.)
  - tier_applied (str): Tier used for analysis (community/pro/enterprise)
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 3. get_symbol_references

```
Find all references to a symbol across the project.

Tier Behavior:
  Community: Limited to 100 files searched, 100 references returned, basic symbol location
  Pro: Unlimited files and references, enhanced categorization (definition/import/call/read/write), scope filtering, test file filtering
  Enterprise: Unlimited files and references, CODEOWNERS integration, ownership attribution, impact analysis with risk scoring

Tier Capabilities:
  Community: Up to 100 files searched, 100 references max, basic location tracking
  Pro: All Community + unlimited files/references, reference type categorization, scope prefix filtering, test file inclusion control
  Enterprise: All Pro + CODEOWNERS integration, ownership attribution, impact analysis, risk scoring

Args:
  symbol_name (str): Name of the symbol to find references for.
  project_root (str, optional): Project root directory. Default: server's project root.
  scope_prefix (str, optional): Optional prefix to limit search scope (e.g., "module.submodule").
  include_tests (bool): Whether to include test files in search. Default: True.
  ctx (Context, optional): MCP context for progress reporting.

Returns:
  ToolResponseEnvelope with SymbolReferencesResult containing:
    - success (bool): True if search completed successfully
    - symbol_name (str): Name of the searched symbol
    - definition_file (str, optional): File where symbol is defined (if found)
    - definition_line (int, optional): Line number where symbol is defined (if found)
    - references (list[SymbolReference]): List of references up to tier limit:
      - file (str): File path containing reference
      - line (int): Line number of reference
      - column (int): Column number of reference
      - context (str): Code snippet showing usage context
      - is_definition (bool): Whether this is the definition
      - reference_type (str): Category (definition/import/call/read/write/reference) (Pro+)
      - is_test_file (bool): Whether reference is in a test file
      - owners (list[str]): CODEOWNERS owners for the file (Enterprise)
    - total_references (int): Total reference count before truncation
    - files_scanned (int): Number of files actually scanned
    - total_files (int): Total candidate files before filtering
    - files_truncated (bool): Whether file scanning was truncated
    - file_truncation_warning (str, optional): Warning if file scan was truncated
    - category_counts (dict): Counts by reference category (Pro+)
    - owner_counts (dict): Counts by CODEOWNERS owner (Enterprise)
    - change_risk (str): Heuristic change risk assessment (Enterprise)
    - references_truncated (bool): Whether references list was truncated
    - truncation_warning (str, optional): Warning if results truncated
    - risk_score (int, 0-100): Weighted risk score for changes (Enterprise)
    - risk_factors (list[str]): Factors contributing to risk (Enterprise)
    - tier_applied (str): Tier used for search
    - max_files_applied (int, optional): Max files limit applied
    - max_references_applied (int, optional): Max references limit applied
    - pro_features_enabled (list[str]): List of Pro features enabled
    - enterprise_features_enabled (list[str]): List of Enterprise features enabled
  - error (str): Error message if search failed (invalid symbol, permission denied, etc.)
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Search duration in milliseconds
```

---

## EXTRACTION TOOLS

### 4. extract_code

```
Extract code elements with optional dependency context.

Extracts a specified code element (function, class, method) along with optional
context, cross-file dependencies, and refactoring suggestions. Provide either
'file_path' (recommended) or 'code' for the source.

Tier Behavior:
  Community: Single-file extraction only, basic symbols, max depth 0, 1MB limit
  Pro: Cross-file dependencies, variable promotion, closure detection, max depth 1, 10MB limit
  Enterprise: Organization-wide resolution, custom patterns, Dockerfile generation, unlimited depth, 100MB limit

Tier Capabilities:
  Community: single_file_extraction, basic_symbols (max_depth=0, max_file_size_mb=1)
  Pro: All Community + cross_file_deps, context_extraction, variable_promotion, closure_detection, dependency_injection_suggestions (max_depth=1, max_file_size_mb=10)
  Enterprise: All Pro + org_wide_resolution, custom_extraction_patterns, dockerfile_generation, service_boundaries (max_depth=unlimited, max_file_size_mb=100)

Args:
  target_type (str): Type of element to extract - "function", "class", or "method".
  target_name (str): Name of the element to extract.
  file_path (str, optional): Path to source file. Either file_path or code required.
  code (str, optional): Source code string. Either file_path or code required.
  language (str, optional): Programming language. Default: auto-detect.
  include_context (bool): Include surrounding code context. Default: False.
  context_depth (int): Depth of context to include. Default: 1.
  include_cross_file_deps (bool): Include cross-file dependencies (Pro+ only). Default: False.
  include_token_estimate (bool): Include token count estimate. Default: True.
  variable_promotion (bool): Suggest variables for external dependencies (Pro+ only). Default: False.
  closure_detection (bool): Detect closure requirements (Pro+ only). Default: False.
  dependency_injection_suggestions (bool): Suggest DI patterns (Pro+ only). Default: False.
  as_microservice (bool): Refactor as microservice (Enterprise only). Default: False.
  microservice_host (str): Host for microservice. Default: "127.0.0.1".
  microservice_port (int): Port for microservice. Default: 8000.
  organization_wide (bool): Organization-wide scope (Enterprise only). Default: False.
  workspace_root (str, optional): Workspace root directory.
  ctx (Context, optional): MCP context for progress reporting.

Returns:
  ToolResponseEnvelope with ContextualExtractionResult containing:
    - success (bool): True if extraction completed successfully
    - server_version (str): Code Scalpel version
    - target_name (str): Name of target element
    - target_code (str): Target element source code
    - context_code (str): Combined dependency source code
    - full_code (str): Complete code block for LLM consumption
    - context_items (list[str]): Names of included dependencies
    - total_lines (int): Total lines in extraction
    - line_start (int): Starting line number of target
    - line_end (int): Ending line number of target
    - token_estimate (int): Estimated token count
    - tier_applied (str): Tier used ("community"/"pro"/"enterprise")
    - language_detected (str): Language detected/used
    - cross_file_deps_enabled (bool): Whether cross-file deps were enabled
    - max_depth_applied (int, optional): Max depth limit applied (None=unlimited)
    - jsx_normalized (bool): Whether JSX syntax was normalized
    - is_server_component (bool): Next.js Server Component flag
    - is_server_action (bool): Next.js Server Action flag
    - component_type (str): React component type ("functional"/"class")
    - warnings (list[str]): Non-fatal warnings
    - advanced (dict): Tier-specific metadata
    - error (str, optional): Error message if extraction failed
  - error (str): Error message if tool execution failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 5. rename_symbol

```
Safely rename a function, class, or method in a file.

Tier Behavior:
  Community: Single-file renames only (definition + local references)
  Pro: Cross-file renames within project scope
  Enterprise: Unlimited cross-file renames with audit trail and approval workflows

Tier Capabilities:
  Community: Single-file renames, definition + local references only (max_files_searched=0, max_files_updated=0)
  Pro: All Community + cross-file renames (max_files_searched=500, max_files_updated=200)
  Enterprise: All Pro + audit trail, approval workflows, unlimited scope (max_files_searched=None, max_files_updated=None)

Args:
  file_path (str): Path to the file containing the symbol to rename.
  target_type (str): Type of symbol - "function", "class", or "method".
  target_name (str): Current name of the symbol to rename.
  new_name (str): New name for the symbol.
  create_backup (bool): Whether to create a backup before renaming. Default: True.

Returns:
  ToolResponseEnvelope containing PatchResultModel with:
    - success (bool): Whether the rename was successful
    - file_path (str): Path to the modified file
    - target_name (str): Name of the modified symbol
    - target_type (str): Type - function, class, or method
    - backup_path (str, optional): Path to backup file if created
    - error (str, optional): Error message if rename failed
    - tier_applied (str): Tier applied ("community"/"pro"/"enterprise")
    - max_files_searched (int): Maximum files that could be searched
    - max_files_updated (int): Maximum files that could be updated
    - warnings (list[str]): Non-fatal warnings
  - error (str): Error message if operation failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 6. update_symbol

```
Safely replace a function, class, or method in a file.

Tier Behavior:
  Community: Syntax validation only, up to 10 updates per call
  Pro: Syntax + semantic validation, unlimited updates per call
  Enterprise: Syntax + semantic + full compliance validation, unlimited updates per call

Tier Capabilities:
  Community: Syntax validation, automatic backups (max_updates=10)
  Pro: All Community + semantic validation, unlimited updates
  Enterprise: All Pro + full compliance validation, unlimited updates

Args:
  file_path (str): Path to the file containing the symbol to update.
  target_type (str): Type of symbol - "function", "class", "method".
  target_name (str): Name of the symbol to update.
  new_code (str, optional): New code for the symbol (required for "replace" operation).
  operation (str): Operation type. Default: "replace" (only supported operation).
  new_name (str, optional): Optional new name for the symbol.
  create_backup (bool): Whether to create a backup before updating. Default: True.

Returns:
  ToolResponseEnvelope containing PatchResultModel with:
    - success (bool): Whether the update was successful
    - file_path (str): Path to the modified file
    - target_name (str): Name of the modified symbol
    - target_type (str): Type - function, class, or method
    - error (str, optional): Error message if update failed
    - tier_applied (str): Tier applied ("community"/"pro"/"enterprise")
    - warnings (list[str]): Non-fatal warnings
  - error (str): Error message if operation failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

## ANALYSIS TOOLS

### 7. analyze_code

```
Analyze source code structure with AST parsing and metrics.

Provide either 'code' (string) or 'file_path' (to read from file). Language is
auto-detected if set to 'auto' (default). Use this tool to understand high-level
architecture before attempting to edit, preventing hallucinated methods or classes.

Tier Behavior:
  Community: Basic AST parsing, functions/classes, complexity metrics, imports
  Pro: All Community + cognitive complexity, code smells, Halstead metrics, duplicate detection
  Enterprise: All Pro + custom rules, compliance checks, organization patterns, technical debt

Tier Capabilities:
  Community: Basic metrics only (max_file_size_mb=1)
  Pro: All Community + advanced metrics and smells (max_file_size_mb=10)
  Enterprise: All Pro + custom rules, compliance checks (max_file_size_mb=100)

Args:
  code (str, optional): Source code to analyze. Either code or file_path required.
  language (str): Programming language for analysis. Default: "auto" (auto-detect).
  file_path (str, optional): Path to file to analyze. Either code or file_path required.

Returns:
  ToolResponseEnvelope with AnalysisResult containing:
    - success (bool): True if analysis completed successfully
    - functions (list[str]): Function names found
    - classes (list[str]): Class names found
    - imports (list[str]): Import statements
    - complexity (int): Cyclomatic complexity estimate
    - lines_of_code (int): Total lines of code
    - function_details (list[dict]): Function info with line numbers, async status
    - class_details (list[dict]): Class info with line numbers, methods
    - issues (list[dict]): Issues found during analysis
    - cognitive_complexity (int): Cognitive complexity score (Pro/Enterprise, 0 if Community)
    - code_smells (list[dict]): Detected code smells (Pro/Enterprise, empty if Community)
    - halstead_metrics (dict, optional): Halstead complexity metrics (Pro/Enterprise, None if not computed)
    - duplicate_code_blocks (list[dict]): Detected duplicate code blocks (Pro/Enterprise)
    - dependency_graph (dict): Function call adjacency map (Pro/Enterprise)
    - naming_issues (list[dict]): Naming convention issues (Enterprise)
    - compliance_issues (list[dict]): Compliance findings (Enterprise)
    - custom_rule_violations (list[dict]): Custom rule matches (Enterprise)
    - organization_patterns (list[dict]): Detected architectural patterns (Enterprise)
    - frameworks (list[str]): Detected frameworks (Pro/Enterprise)
    - dead_code_hints (list[dict]): Dead code candidates (Pro/Enterprise)
    - decorator_summary (dict): Decorator/annotation summary (Pro/Enterprise)
    - type_summary (dict): Type annotation summary (Pro/Enterprise)
    - architecture_patterns (list[str]): Architecture/service-pattern hints (Enterprise)
    - technical_debt (dict): Technical debt scoring summary (Enterprise)
    - api_surface (dict): API surface summary (Enterprise)
    - prioritized (bool): Whether outputs were priority-ordered (Enterprise)
    - complexity_trends (dict): Historical complexity trend summary (Enterprise)
    - language_detected (str): Language that was actually analyzed
    - tier_applied (str): Tier applied for feature gating
    - error_location (dict, optional): Line/column of syntax error if applicable
    - suggested_fix (str, optional): Suggested fix for syntax error when applicable
    - sanitization_report (dict, optional): Parsing sanitization details
    - parser_warnings (list[str]): Parser warnings (e.g., sanitization notices)
  - error (str): Error message if analysis failed (invalid code, file not found, etc.)
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

## SECURITY TOOLS

### 8. unified_sink_detect

```
Detect polyglot security sinks with confidence thresholds.

Identifies dangerous sinks (functions that handle untrusted data) across multiple
languages. Language is auto-detected from code if set to 'auto' (default).

Tier Behavior:
  Community: Basic sink detection, CWE mapping, confidence scoring
  Pro: All Community + context-aware detection, framework-specific sinks, custom patterns
  Enterprise: All Pro + compliance reporting, risk scoring, remediation suggestions

Tier Capabilities:
  Community: Pattern-based detection only
  Pro: All Community + context analysis, custom patterns
  Enterprise: All Pro + compliance mappings, remediation suggestions

Args:
  code (str): Source code to scan for sinks.
  language (str): Programming language. Default: "auto" (auto-detect).
              Supported: python, javascript, typescript, java
  confidence_threshold (float): Minimum confidence score (0.0-1.0). Default: 0.7 (70%).

Returns:
  ToolResponseEnvelope with UnifiedSinkResult containing:
    - success (bool): True if detection completed successfully
    - language (str): Language analyzed
    - sink_count (int): Number of sinks detected
    - sinks (list[dict]): Detected sinks meeting confidence threshold
    - coverage_summary (dict): Summary of sink pattern coverage
    - logic_sinks (list[dict]): Logic sinks detected (Pro)
    - extended_language_sinks (dict): Additional language sink details (Pro)
    - confidence_scores (dict): Per-sink confidence scores (Pro/Enterprise)
    - sink_categories (dict): Sink categorization by risk level (Enterprise)
    - risk_assessments (list[dict]): Risk assessments with clearance (Enterprise)
    - custom_sink_matches (list[dict]): Custom sink pattern matches (Enterprise)
    - context_analysis (dict): Context-aware detection results (Pro)
    - framework_sinks (dict): Framework-specific sink detections (Pro)
    - compliance_mapping (dict): Compliance standard mappings (Enterprise)
    - historical_comparison (dict): Historical sink tracking comparison (Enterprise)
    - remediation_suggestions (list[str]): Automated remediation suggestions (Enterprise)
    - truncated (bool): Whether results were truncated
    - sinks_detected (int): Total sinks detected before truncation
    - max_sinks_applied (int, optional): Max sinks limit applied
    - error (str, optional): Error message if detection failed
  - error (str): Error message if detection failed
  - tier_applied (str): Tier used for detection
  - duration_ms (int): Detection duration in milliseconds
```

---

### 9. type_evaporation_scan

```
Detect Type System Evaporation vulnerabilities across frontend/backend.

Identifies security issues when type information is lost at frontend/backend boundaries.
Provide either code strings or file paths for both frontend and backend code.

Tier Behavior:
  Community: Frontend-only analysis, basic type checking
  Pro: All Community + network boundary analysis, implicit any tracing, library boundary checks
  Enterprise: All Pro + runtime validation generation, Zod schema generation, API contract validation

Tier Capabilities:
  Community: Frontend analysis only, single file
  Pro: All Community + network boundary analysis (max_files=10)
  Enterprise: All Pro + API contracts and validation generation (max_files=unlimited)

Args:
  frontend_code (str, optional): Frontend TypeScript/JavaScript code. Either frontend_code or frontend_file_path required.
  backend_code (str, optional): Backend Python code. Either backend_code or backend_file_path required.
  frontend_file_path (str, optional): Path to frontend file. Either frontend_code or frontend_file_path required.
  backend_file_path (str, optional): Path to backend file. Either backend_code or backend_file_path required.
  frontend_file (str): Display name for frontend file. Default: "frontend.ts".
  backend_file (str): Display name for backend file. Default: "backend.py".

Returns:
  ToolResponseEnvelope with TypeEvaporationResultModel containing:
    - success (bool): True if analysis completed successfully
    - frontend_vulnerabilities (int): Number of frontend vulnerabilities
    - backend_vulnerabilities (int): Number of backend vulnerabilities
    - cross_file_issues (int): Number of cross-file issues
    - matched_endpoints (list[dict]): Correlated API endpoints
    - vulnerabilities (list[dict]): All vulnerabilities found
    - summary (str): Analysis summary
    - implicit_any_count (int): Count of implicit any detections (Pro)
    - network_boundaries (list[dict]): Detected network call boundaries (Pro)
    - boundary_violations (list[dict]): Type violations at boundaries (Pro)
    - library_boundaries (list[dict]): Library call type boundaries (Pro)
    - json_parse_locations (list[dict]): JSON.parse() without validation (Pro)
    - generated_schemas (list[str]): Generated Zod schemas (Enterprise)
    - validation_code (str): Generated validation code (Enterprise)
    - schema_coverage (float): Coverage ratio of validated endpoints (Enterprise)
    - pydantic_models (list[str]): Generated Pydantic models (Enterprise)
    - api_contract (dict): API contract validation results (Enterprise)
    - remediation_suggestions (list[str]): Automated remediation suggestions (Enterprise)
    - custom_rule_violations (list[dict]): Custom type rule violations (Enterprise)
    - compliance_report (dict): Type compliance validation report (Enterprise)
    - warnings (list[str]): Non-fatal warnings
    - error (str, optional): Error message if analysis failed
  - error (str): Error message if analysis failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 10. scan_dependencies

```
Scan project dependencies for known vulnerabilities.

Analyzes project dependency manifests (package.json, requirements.txt, pom.xml, etc.)
for known security vulnerabilities using CVE databases.

Tier Behavior:
  Community: Basic vulnerability scanning, CVE mapping only
  Pro: All Community + license analysis, supply chain insights, automated updates
  Enterprise: All Pro + priority scoring, compliance reports, SLA tracking

Tier Capabilities:
   Community: Vulnerabilities only (max_packages=50)
   Pro: All Community + license and supply chain (max_packages=10000)
   Enterprise: All Pro + compliance and SLA tracking (max_packages=unlimited)

Args:
  path (str, optional): Path to scan for dependencies. If None, uses project root.
  project_root (str, optional): Project root directory. If None, uses server default.
  scan_vulnerabilities (bool): Scan for vulnerabilities. Default: True.
  include_dev (bool): Include development dependencies. Default: True.
  timeout (float): Scan timeout in seconds. Default: 30.0.
  ctx (Context, optional): MCP context for progress reporting.

Returns:
  ToolResponseEnvelope with DependencyScanResult containing:
    - scanned_files (list[str]): Dependency files scanned
    - total_dependencies (int): Total number of dependencies found
    - vulnerable_count (int): Number of dependencies with vulnerabilities
    - total_vulnerabilities (int): Total number of vulnerabilities found
    - severity_summary (dict): Count by severity (critical, high, medium, low)
    - dependencies (list[dict]): All scanned dependencies with vulnerabilities
    - compliance_report (dict): Compliance report for SOC2/ISO standards (Enterprise)
    - policy_violations (list[dict]): Policy violations detected (Enterprise)
    - errors (list[dict]): Non-fatal errors/warnings encountered during scan
    - success (bool): Whether the scan completed successfully
    - error (str, optional): Error message if failed
  - error (str): Error message if scan failed
  - tier_applied (str): Tier used for scanning
  - duration_ms (int): Scan duration in milliseconds
```

---

### 11. security_scan

```
Scan code for security vulnerabilities using taint analysis.

Identifies security vulnerabilities using taint analysis and pattern matching.
Provide either 'code' or 'file_path'. Language is auto-detected from code content.

Tier Behavior:
  Community: Basic pattern matching, CWE mapping, confidence scoring
  Pro: All Community + taint analysis, reachability, false positive tuning, custom rules
  Enterprise: All Pro + compliance mappings, priority ordering, remediation suggestions

Tier Capabilities:
  Community: Pattern matching only
  Pro: All Community + taint analysis, custom patterns (max_complexity=10000)
  Enterprise: All Pro + compliance and remediation (max_complexity=unlimited)

Args:
  code (str, optional): Source code to scan. Either code or file_path required.
  file_path (str, optional): Path to file to scan. Either code or file_path required.
  confidence_threshold (float): Minimum confidence score (0.0-1.0). Default: 0.7 (70%).

Returns:
  ToolResponseEnvelope with SecurityResult containing:
    - success (bool): True if scan completed successfully
    - has_vulnerabilities (bool): Whether vulnerabilities were found
    - vulnerability_count (int): Number of vulnerabilities
    - risk_level (str): Overall risk level
    - vulnerabilities (list[dict]): List with CWE, severity, location
    - taint_sources (list[str]): Identified taint sources
    - sanitizer_paths (list[dict]): Detected sanitizer usages (Pro/Enterprise)
    - confidence_scores (dict): Heuristic confidence scores per finding
    - false_positive_analysis (dict): False-positive reduction metadata
    - remediation_suggestions (list[str]): Remediation suggestions (Pro/Enterprise)
    - policy_violations (list[dict]): Custom policy violations (Enterprise)
    - compliance_mappings (dict): Compliance framework mappings (Enterprise)
    - custom_rule_results (list[dict]): Custom rule matches (Enterprise)
    - priority_ordered_findings (list[dict]): Findings sorted by priority (Enterprise)
    - reachability_analysis (dict): Vulnerability reachability analysis (Enterprise)
    - false_positive_tuning (dict): False positive tuning results (Enterprise)
    - error (str, optional): Error message if failed
  - error (str): Error message if scan failed
  - tier_applied (str): Tier used for scanning
  - duration_ms (int): Scan duration in milliseconds
```

---

## GRAPH TOOLS

### 12. get_call_graph

```
Build a call graph showing function relationships in the project.

Tier Behavior:
  Community: Max depth 3, max nodes 50, basic call graph only
  Pro: Max depth 50, max nodes 500, includes path queries, focus mode, call context, confidence scoring
  Enterprise: Unlimited depth and nodes, hot path identification, dead code detection, custom graph analysis

Tier Capabilities:
  Community: Basic call graph (max_depth=3, max_nodes=50)
  Pro: All Community + advanced features (max_depth=50, max_nodes=500)
  Enterprise: All Pro + enterprise metrics (max_depth=unlimited, max_nodes=unlimited)

Args:
  project_root (str, optional): Project root directory. Default: server's project root.
  entry_point (str, optional): Starting function name (e.g., "main" or "app.py:main"). If None, includes all functions.
  depth (int): Maximum depth to traverse from entry point. Default: 10.
  include_circular_import_check (bool): Check for circular imports. Default: True.
  paths_from (str, optional): Source function for path query (e.g., "routes.py:handle_request").
  paths_to (str, optional): Sink function for path query (e.g., "db.py:execute_query").
  focus_functions (list[str], optional): List of functions to focus the subgraph on.
  ctx (Context, optional): MCP context for progress reporting.

Returns:
  ToolResponseEnvelope containing CallGraphResultModel with:
    - success (bool): True if graph built successfully
    - nodes (list[dict]): Function nodes with metadata
    - edges (list[dict]): Call relationships between functions
    - mermaid (str): Mermaid diagram representation
    - paths (list[list[str]], optional): Query paths from source to sink (Pro)
    - circular_imports (list[list[str]], optional): Detected circular dependencies
    - metadata (dict): Graph metadata
    - truncated (bool): Whether results were truncated
    - tier_applied (str): Tier used
  - error (str): Error message if graph building failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 13. get_graph_neighborhood

```
Extract k-hop neighborhood subgraph around a center node.

Tier Behavior:
  Community: Max k=1, max nodes=20
  Pro: Max k=5, max nodes=100
  Enterprise: Unlimited k and nodes

Tier Capabilities:
  Community: Limited neighborhood (max_k=1, max_nodes=20)
  Pro: Expanded neighborhood (max_k=5, max_nodes=100)
  Enterprise: Unlimited neighborhood (max_k=unlimited, max_nodes=unlimited)

Args:
  center_node_id (str): ID of the center node (format: language::module::type::name).
  k (int): Maximum hops from center. Default: 2.
  max_nodes (int): Maximum nodes to include. Default: 100.
  direction (str): "outgoing", "incoming", or "both". Default: "both".
  min_confidence (float): Minimum edge confidence to follow. Default: 0.0.
  project_root (str, optional): Project root directory. Default: server's project root.
  query (str, optional): Graph query language (Enterprise tier only).

Returns:
  ToolResponseEnvelope containing GraphNeighborhoodResult with:
    - success (bool): True if extraction succeeded
    - center_node (dict): Center node details
    - nodes (list[dict]): Subgraph nodes
    - edges (list[dict]): Subgraph edges
    - mermaid (str): Mermaid diagram of neighborhood
    - truncated (bool): Whether results were truncated
    - tier_applied (str): Tier used
  - error (str): Error message if extraction failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 14. get_project_map

```
Generate a comprehensive map of the project structure.

Tier Behavior:
  Community: Up to 100 files, 50 modules, basic detail level
  Pro: Up to 1000 files, 200 modules, detailed level
  Enterprise: Unlimited files, 1000 modules, comprehensive detail level

Tier Capabilities:
  Community: Basic project map (max_files=100, max_modules=50)
  Pro: Detailed project map (max_files=1000, max_modules=200)
  Enterprise: Comprehensive project map (max_files=unlimited, max_modules=1000)

Args:
  project_root (str, optional): Project root directory. Default: server's project root.
  include_complexity (bool): Calculate cyclomatic complexity. Default: True.
  complexity_threshold (int): Threshold for flagging hotspots. Default: 10.
  include_circular_check (bool): Check for circular imports. Default: True.
  detect_service_boundaries (bool): Detect service boundaries. Default: False.
  min_isolation_score (float): Isolation score threshold for boundaries. Default: 0.6.
  ctx (Context, optional): MCP context for progress reporting.

Returns:
  ToolResponseEnvelope containing ProjectMapResult with:
    - success (bool): True if mapping succeeded
    - total_files (int): Total files analyzed
    - total_lines (int): Total lines of code
    - modules (list[dict]): Module metadata
    - dependencies (list[dict]): Inter-module dependencies
    - complexity_hotspots (list[dict]): High complexity locations
    - circular_dependencies (list[list[str]], optional): Detected circular dependencies
    - mermaid (str): Mermaid diagram of structure
    - suggested_services (list[dict], optional): Service boundary suggestions (Enterprise)
    - tier_applied (str): Tier used
  - error (str): Error message if mapping failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 15. get_cross_file_dependencies

```
Analyze and extract cross-file dependencies for a symbol.

Tier Behavior:
  Community: Max depth=1, max files=50
  Pro: Max depth=5, max files=500
  Enterprise: Unlimited depth and files

Tier Capabilities:
  Community: Limited depth analysis (max_depth=1, max_files=50)
  Pro: Extended depth analysis (max_depth=5, max_files=500)
  Enterprise: Unlimited depth and files

Args:
  target_file (str): Path to file containing the target symbol (relative to project root).
  target_symbol (str): Name of the function or class to analyze.
  project_root (str, optional): Project root directory. Default: server's project root.
  max_depth (int): Maximum depth of dependency resolution. Default: 3.
  include_code (bool): Include full source code in result. Default: True.
  include_diagram (bool): Include Mermaid diagram of imports. Default: True.
  confidence_decay_factor (float): Decay factor per depth level. Default: 0.9. Range: 0.0-1.0.
  max_files (int, optional): Maximum files to include (subject to tier limit).
  timeout_seconds (float, optional): Timeout in seconds.

Returns:
  ToolResponseEnvelope containing CrossFileDependenciesResult with:
    - success (bool): True if analysis succeeded
    - target_symbol (str): The analyzed symbol
    - extracted_symbols (list[dict]): Extracted dependencies
    - dependency_graph (dict): Dependency relationships
    - combined_code (str): Combined code from all dependencies
    - confidence_scores (dict): Confidence per symbol (Pro+)
    - mermaid (str): Mermaid diagram of dependencies
    - truncated (bool): Whether results were truncated
    - tier_applied (str): Tier used
  - error (str): Error message if analysis failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 16. cross_file_security_scan

```
Perform cross-file security analysis tracking taint flow across module boundaries.

Use this tool to detect vulnerabilities where tainted data crosses file boundaries
before reaching a dangerous sink. This catches security issues that single-file
analysis would miss.

Tier Behavior:
  Community: Basic cross-file scan with single-module taint tracking (max 10 modules, depth 3)
  Pro: Advanced taint tracking with framework-aware analysis (max 100 modules, depth 10)
  Enterprise: Project-wide scan with custom rules and global flows (unlimited modules/depth)

Tier Capabilities:
  Community: basic_cross_file_scan, single_module_taint_tracking, source_to_sink_tracing (max_modules=10, max_depth=3)
  Pro: All Community + advanced_taint_tracking, framework_aware_taint, dependency_injection_resolution (max_modules=100, max_depth=10)
  Enterprise: All Pro + project_wide_scan, custom_taint_rules, global_taint_flow, microservice_boundary_crossing (max_modules=unlimited, max_depth=unlimited)

Args:
  project_root (str, optional): Project root directory. Default: server's project root.
  entry_points (list[str], optional): Entry point functions (e.g., ["app.py:main", "routes.py:index"]). If None, analyzes all.
  max_depth (int): Maximum call depth to trace. Default: 5.
  include_diagram (bool): Include Mermaid diagram of taint flows. Default: True.
  timeout_seconds (float, optional): Maximum time in seconds. Default: 120. None for no timeout.
  max_modules (int, optional): Maximum modules to analyze. Default: 500. None for no limit.
  confidence_threshold (float): Minimum confidence for reporting. Default: 0.7.
  ctx (Context, optional): MCP context for progress reporting.

Returns:
  ToolResponseEnvelope containing CrossFileSecurityResult with:
    - success (bool): True if analysis completed successfully
    - server_version (str): Code Scalpel version
    - tier_applied (str): Tier used ("community"/"pro"/"enterprise")
    - max_depth_applied (int, optional): Max depth limit applied
    - max_modules_applied (int, optional): Max modules limit applied
    - framework_aware_enabled (bool): Whether framework-aware tracking enabled (Pro+)
    - enterprise_features_enabled (bool): Whether enterprise features enabled
    - files_analyzed (int): Number of files analyzed
    - has_vulnerabilities (bool): Whether vulnerabilities were found
    - vulnerability_count (int): Total vulnerabilities found
    - risk_level (str): Overall risk ("low"/"medium"/"high"/"critical")
    - vulnerabilities (list[CrossFileVulnerabilityModel]): Detailed vulnerabilities
    - taint_flows (list[TaintFlowModel]): Data flow paths
    - taint_sources (list[str]): Functions with taint sources
    - dangerous_sinks (list[str]): Functions with dangerous sinks
    - framework_contexts (dict): Framework detection (Pro+)
    - dependency_chains (list[dict]): Inter-file chains (Pro+)
    - confidence_scores (dict): Confidence per flow (Pro+)
    - global_flows (list[dict]): Global flows (Enterprise)
    - microservice_boundaries (list[dict]): Service boundaries (Enterprise)
    - distributed_trace (dict): Distributed trace (Enterprise)
    - mermaid (str): Mermaid diagram of taint flows
    - error (str, optional): Error message if analysis failed
  - error (str): Error message if tool execution failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

## POLICY TOOLS

### 17. validate_paths

```
Validate that paths are accessible before running file-based operations.

Checks that provided file paths exist and are accessible within the project,
preventing invalid file access errors in subsequent operations.

Tier Behavior:
  Community: Basic path validation (max 100 paths)
  Pro: All Community + alias resolution and dynamic import detection (unlimited paths)
  Enterprise: All Pro + security validation and boundary testing (unlimited paths)

Tier Capabilities:
  Community: path_accessibility_checking, docker_environment_detection, workspace_root_detection (max_paths=100)
  Pro: All Community + path_alias_resolution, tsconfig_paths_support, webpack_alias_support, dynamic_import_resolution (max_paths=None)
  Enterprise: All Pro + permission_checks, security_validation, path_traversal_simulation, security_boundary_testing (max_paths=None)

Args:
  paths (list[str]): List of file paths to validate.
  project_root (str, optional): Project root directory for relative path resolution.

Returns:
  ToolResponseEnvelope containing PathValidationResult with:
    - success (bool): True if all paths validated successfully
    - accessible (list[str]): Successfully resolved paths
    - inaccessible (list[str]): Paths that could not be resolved
    - suggestions (list[str]): Actionable suggestions for inaccessible paths
    - workspace_roots (list[str]): Detected workspace root directories
    - is_docker (bool): Whether running in Docker container
    - alias_resolutions (dict): Resolved path aliases (Pro+)
    - dynamic_imports (list[dict]): Detected dynamic import patterns (Pro+)
    - traversal_vulnerabilities (list[dict]): Directory traversal attempts (Enterprise)
    - boundary_violations (list[dict]): Workspace boundary violations (Enterprise)
    - security_score (float, 0.0-10.0): Overall security score (Enterprise)
    - truncated (bool): Whether input was truncated
    - paths_received (int): Original number of paths
    - paths_checked (int): Number of paths actually validated
    - max_paths_applied (int, optional): Applied max_paths limit
  - error (str): Error message if validation failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 18. code_policy_check

```
Check code against style guides, best practices, and compliance standards.

Analyzes source code files for adherence to coding standards, style guides,
and best practices. Can optionally enforce organizational compliance standards.

Tier Behavior:
  Community: Basic style checks (PEP8, ESLint rules, basic patterns)
  Pro: All Community + best practice analysis, security patterns, async error patterns, custom rules
  Enterprise: All Pro + compliance standards (HIPAA, SOC2, GDPR, PCI-DSS), auditing, certifications, PDF reports

Tier Capabilities:
  Community: Style guide checking, PEP8 validation (max_files=100, max_rules=50)
  Pro: All Community + best practice analysis, custom rules (max_files=1000, max_rules=200)
  Enterprise: All Pro + compliance standards, PDF reports (max_files=unlimited, max_rules=unlimited)

Args:
  paths (list[str]): List of file paths to check against policies.
  rules (list[str], optional): Specific rules to enforce. If None, use defaults.
  compliance_standards (list[str], optional): Compliance frameworks (HIPAA, SOC2, GDPR, PCI-DSS). Enterprise tier only.
  generate_report (bool): Generate compliance report. Default: False. Enterprise tier only.

Returns:
  ToolResponseEnvelope with CodePolicyCheckResult containing:
    - success (bool): True if check completed (no critical violations)
    - files_checked (int): Number of files analyzed
    - rules_applied (int): Number of rules applied
    - summary (str): Human-readable summary of results
    - violations (list[dict]): Policy violations found
    - best_practices_violations (list[dict]): Best practice violations (Pro/Enterprise)
    - security_warnings (list[dict]): Security warnings detected (Pro/Enterprise)
    - custom_rule_results (list[dict]): Custom rule matches (Pro/Enterprise)
    - compliance_reports (dict): Compliance audit reports by standard (Enterprise)
    - compliance_score (int, 0-100): Overall compliance score (Enterprise)
    - certifications (list[str]): Generated certifications (Enterprise)
    - audit_trail (list[dict]): Audit log entries (Enterprise)
    - pdf_report (str): Base64-encoded PDF report (Enterprise)
    - tier_applied (str): Tier used for analysis
    - files_limit_applied (int, optional): Max files limit applied
    - rules_limit_applied (int, optional): Max rules limit applied
    - error (str, optional): Error message if check failed
  - error (str): Error message if analysis failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

## SYMBOLIC & TESTING TOOLS

### 19. symbolic_execute

```
Perform symbolic execution on Python code.

Analyzes Python code symbolically to explore execution paths, discover constraints,
and identify potential issues without concrete execution.

Tier Behavior:
  Community: Basic symbolic execution (max_paths=50, max_depth=10)
  Pro: Advanced symbolic execution (max_paths=unlimited, max_depth=100, concolic execution)
  Enterprise: Unlimited symbolic execution (max_paths=unlimited, max_depth=unlimited, distributed execution, memory modeling)

Tier Capabilities:
  Community: Basic symbolic execution (max_paths=50, max_depth=10, basic constraint types)
  Pro: All Community + concolic execution (max_paths=unlimited, max_depth=100)
  Enterprise: All Pro + distributed execution, memory modeling (max_paths=unlimited, max_depth=unlimited)

Args:
  code (str): Python code to symbolically execute.
  max_paths (int, optional): Maximum execution paths to explore (subject to tier limits).
  max_depth (int, optional): Maximum loop unrolling depth (subject to tier limits).

Returns:
  ToolResponseEnvelope containing SymbolicResult with:
    - success (bool): True if analysis succeeded
    - paths_explored (int): Number of execution paths explored
    - paths (list[ExecutionPath]): Discovered paths with conditions and constraints
    - symbolic_variables (list[str]): Variables treated symbolically
    - constraints (list[str]): Discovered constraints
    - total_paths (int, optional): Total paths before limiting
    - truncated (bool): Whether paths were limited
    - truncation_warning (str, optional): Warning when limited
    - path_prioritization (dict, optional): Path prioritization (Pro/Enterprise)
    - concolic_results (dict, optional): Concolic execution (Pro/Enterprise)
    - state_space_analysis (dict, optional): State space reduction (Enterprise)
    - memory_model (dict, optional): Memory modeling (Enterprise)
    - error (str, optional): Error message if analysis failed
  - error (str): Error message if operation failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 20. generate_unit_tests

```
Generate unit tests from code using symbolic execution.

Tier Behavior:
  Community: Max 5 test cases, pytest framework only
  Pro: Max 20 test cases, pytest/unittest frameworks, data-driven tests
  Enterprise: Unlimited test cases, all frameworks, data-driven tests, bug reproduction

Tier Capabilities:
  Community: Limited test generation (max_test_cases=5, test_frameworks=["pytest"])
  Pro: All Community + data-driven tests (max_test_cases=20)
  Enterprise: All Pro + bug reproduction (max_test_cases=unlimited)

Input Methods (choose one):
  - `code`: Direct Python code string to analyze
  - `file_path`: Path to Python file containing the code
  - `function_name`: Name of function to generate tests for (requires file_path)

Args:
  code (str, optional): Python code string to generate tests for.
  file_path (str, optional): Path to Python file to analyze.
  function_name (str, optional): Specific function name to target.
  framework (str): Test framework. Default: "pytest".
  data_driven (bool): Generate parameterized data-driven tests (Pro+). Default: False.
  crash_log (str, optional): Crash log for bug reproduction tests (Enterprise only).

Returns:
  ToolResponseEnvelope containing TestGenerationResult with:
    - success (bool): True if generation succeeded
    - function_name (str): Target function name
    - test_count (int): Number of test cases generated
    - test_cases (list[dict]): Generated test cases with code, expected results
    - total_test_cases (int): Total tests before truncation
    - framework_used (str): Test framework used
    - data_driven_enabled (bool): Whether data-driven tests were enabled
    - bug_reproduction_enabled (bool): Whether bug reproduction was enabled
    - coverage_estimate (float, 0-100): Code coverage estimate
    - warnings (list[str]): Non-fatal warnings
    - tier_applied (str): Tier used
    - error (str, optional): Error message if generation failed
  - error (str): Error message if operation failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

### 21. simulate_refactor

```
Simulate applying a code change and check for safety issues.

Verifies code changes are safe before applying them by detecting security issues
and structural changes that could break functionality.

Tier Behavior:
  Community: Basic refactor simulation (max 1MB file size, basic analysis depth)
  Pro: Advanced simulation with type checking (max 10MB file size, advanced analysis depth)
  Enterprise: Deep simulation with compliance validation (max 100MB file size, deep analysis depth)

Tier Capabilities:
  Community: basic_simulation, structural_diff (max_file_size_mb=1, analysis_depth="basic")
  Pro: All Community + advanced_simulation, behavior_preservation, type_checking (max_file_size_mb=10, analysis_depth="advanced")
  Enterprise: All Pro + regression_prediction, impact_analysis, compliance_validation (max_file_size_mb=100, analysis_depth="deep")

Args:
  original_code (str): Original code before changes.
  new_code (str, optional): Complete new code after changes (alternative to patch).
  patch (str, optional): Patch/diff describing the changes (alternative to new_code).
  strict_mode (bool): Enable strict validation checks. Default: False.

Returns:
  ToolResponseEnvelope with RefactorSimulationResult containing:
    - success (bool): Whether simulation succeeded
    - is_safe (bool): Whether the refactor is safe to apply
    - status (str): Status (safe, unsafe, warning, or error)
    - reason (str, optional): Reason if not safe
    - security_issues (list[dict]): Security issues with type, severity, line, CWE
    - structural_changes (dict): Functions/classes added/removed/modified
    - warnings (list[str]): Non-critical warnings
    - impact_summary (str): Summary of potential impact
    - behavior_changes (list[dict]): Detected behavior changes (Pro+)
    - type_errors (list[dict]): Type checking errors (Pro+)
    - regression_predictions (dict): Regression likelihood (Enterprise)
    - impact_analysis (dict): Detailed impact analysis (Enterprise)
    - tier_applied (str): Tier used
    - error (str, optional): Error message if simulation failed
  - error (str): Error message if operation failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

## SYSTEM TOOLS

### 22. verify_policy_integrity

```
Verify policy file integrity using cryptographic signatures.

Validates that policy files have not been tampered with by checking their
cryptographic signatures against a manifest.

Tier Behavior:
  Community: Basic verification only
  Pro: All Community + cryptographic signature validation
  Enterprise: All Pro + full integrity checking and audit logging

Tier Capabilities:
  Community: basic_verification only (signature_validation=False, tamper_detection=False)
  Pro: All Community + signature_validation (signature_validation=True, tamper_detection=True)
  Enterprise: All Pro + full_integrity_check, audit_logging (signature_validation=True, tamper_detection=True)

Args:
  policy_dir (str, optional): Directory containing policy files. If None, uses project root.
  manifest_source (str): Where to load manifest from. Default: "file". Options: "file", "embedded", "remote".

Returns:
  ToolResponseEnvelope containing PolicyVerificationResult with:
    - success (bool): Whether all policy files verified successfully
    - manifest_valid (bool): Whether manifest signature is valid
    - files_verified (int): Number of files successfully verified
    - files_failed (list[str]): List of files that failed verification
    - error (str, optional): Error message if verification failed
    - error_code (str, optional): Machine-readable error code
    - manifest_source (str, optional): Source of the policy manifest
    - policy_dir (str, optional): Policy directory that was verified
    - tier (str): Tier used for verification
    - signature_validated (bool): Whether HMAC signature was validated
    - tamper_detection_enabled (bool): Whether tamper detection is active
    - audit_log_entry (dict, optional): Enterprise audit log entry
  - error (str): Error message if operation failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

### 23. get_capabilities

```
Get the capabilities available for the current license tier.

Returns a complete list of all Code Scalpel tools and their availability/limits
at the specified tier or current tier.

Tier Behavior:
  Community: Returns capabilities for community tier (basic limits on all tools)
  Pro: Returns capabilities for pro tier (expanded limits on most tools)
  Enterprise: Returns capabilities for enterprise tier (no limits on core tools)

Tier Capabilities:
  Community: Returns community tier capabilities and limits
  Pro: Returns pro tier capabilities and limits
  Enterprise: Returns enterprise tier capabilities and limits

Args:
  tier (str, optional): Tier to query. Default: current tier from license. Options: "community", "pro", "enterprise".
  ctx (Context, optional): MCP context for progress reporting.

Returns:
  ToolResponseEnvelope containing capabilities dict with:
    - tier (str): The tier that was queried
    - tool_count (int): Total number of tools
    - available_count (int): Number of tools available at this tier
    - capabilities (dict): Maps tool_id to capability info:
      - tool_id (str): The tool identifier
      - tier (str): The tier being described
      - available (bool): Whether tool is available at this tier
      - limits (dict): The limits applied at this tier
      - capabilities (list): Feature list for this tier
  - error (str): Error message if operation failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

## ORACLE TOOLS (PIPELINE - NOT A STANDARD MCP TOOL)

### 24. write_perfect_code

```
Generate constraint specification for AI-assisted code generation.

**IMPORTANT: This is documented as a pipeline trigger, not a standard MCP tool.**
It should be reclassified as part of the Oracle pipeline that kicks off when
a tool fails, rather than being called directly by users.

Provides a Markdown specification containing strict symbol table (function/class
signatures), graph constraints (dependencies, callers), architectural rules, code
context, and implementation notes. The LLM uses this spec to generate code that
compiles and integrates.

Tier Behavior:
  Community: Basic symbol table and context (max 50 files, depth 2)
  Pro: All Community + graph constraints and dependencies (max 2000 files, depth 10)
  Enterprise: All Pro + architectural rules and deep analysis (unlimited files, depth 50)

Tier Capabilities:
  Community: Basic context only (max_files=50, max_depth=2)
  Pro: All Community + graph constraints (max_files=2000, max_depth=10)
  Enterprise: All Pro + architectural rules (max_files=unlimited, max_depth=50)

Args:
  file_path (str): Path to target file (e.g., "src/auth.py").
  instruction (str): What needs to be implemented (e.g., "Add JWT validation").

Returns:
  ToolResponseEnvelope containing Markdown constraint specification with:
    - data (str): Markdown specification containing symbols, graph, rules, context
    - success (bool): True if specification generated
    - error (str, optional): Error message if generation failed (file not found, invalid instruction, etc.)
  - error (str): Error message if operation failed
  - tier_applied (str): Tier used for analysis
  - duration_ms (int): Analysis duration in milliseconds
```

---

## NOTES

- All docstrings follow the pattern: Brief description → Tier Behavior → Tier Capabilities → Args → Returns
- No legacy tags are included in any docstring
- Each tier builds on the previous tier (Community ≤ Pro ≤ Enterprise)
- Args section uses format: `name (type, [optional_tier_requirement]): description`
- Returns section always documents the ToolResponseEnvelope structure with data field containing tool-specific result model
- All tools include tier_applied, error, and duration_ms in the response envelope
