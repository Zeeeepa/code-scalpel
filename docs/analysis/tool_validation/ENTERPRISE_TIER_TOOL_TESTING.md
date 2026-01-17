# Enterprise Tier MCP Tool Testing (22 tools)

**Date**: December 30, 2025  
**Goal**: Confirm (MCP-first) that Enterprise tier:
- Advertises all 22 canonical tools
- Enables Enterprise-only capabilities (compliance, org-wide, unlimited limits)

**Authoritative sources for expectations**
- Capability flags: `src/code_scalpel/licensing/features.py` (per-tool `capabilities` + conceptual `limits`)
- Runtime limit enforcement: `.code-scalpel/limits.toml` (per-tool tier limits; omitted keys mean “unlimited”)
- Timeouts are global safeguards (not tier limits): see `[global] default_timeout_seconds` in `.code-scalpel/limits.toml`

## Test Setup (MCP-first)
- Install a **valid Enterprise license** and point `CODE_SCALPEL_LICENSE_PATH` at it.
- Set `CODE_SCALPEL_TIER=enterprise`.
- Recommended logging: `SCALPEL_MCP_OUTPUT=DEBUG`

### Validation Command (recorded)
```bash
cd /mnt/k/backup/Develop/code-scalpel
CODE_SCALPEL_TIER=enterprise \
CODE_SCALPEL_LICENSE_PATH=/mnt/k/backup/Develop/.code-scalpel/license/code_scalpel_license_enterprise_final_test_ent_1766982522.jwt \
python scripts/mcp_validate_enterprise_tier.py
```

**Outcome (recorded)**
- 25/25 checks PASS (includes Enterprise-only compliance PDF, graph query language, and crypto policy verification).

> If you see `Invalid license signature - token may be tampered`, you are NOT running Enterprise.
> In that case, the server will clamp to a lower tier and this document cannot be validated.

### Canonical Tool Registry (must be stable)
Expected `list_tools()` returns exactly these 22 tool names:
- `analyze_code`
- `code_policy_check`
- `crawl_project`
- `cross_file_security_scan`
- `extract_code`
- `generate_unit_tests`
- `get_call_graph`
- `get_cross_file_dependencies`
- `get_file_context`
- `get_graph_neighborhood`
- `get_project_map`
- `get_symbol_references`
- `rename_symbol`
- `scan_dependencies`
- `security_scan`
- `simulate_refactor`
- `symbolic_execute`
- `type_evaporation_scan`
- `unified_sink_detect`
- `update_symbol`
- `validate_paths`
- `verify_policy_integrity`

**Recorded Result**:
- Tool registry matches expected: ☑ PASS / ☐ FAIL
- Effective tier is Enterprise (not Community/Pro): ☑ PASS / ☐ FAIL

---

## Tool-by-Tool Enterprise Expectations + Test Checklist

> Enterprise validation focuses on Enterprise-only features (compliance, org-wide, unlimited limits).

### 1) analyze_code
**Expected (Enterprise)**
- Capabilities: `basic_ast`, `function_inventory`, `class_inventory`, `imports`, `complexity_metrics`, `code_smells`, `halstead_metrics`, `cognitive_complexity`, `duplicate_code_detection`, `dependency_graph`, `custom_rules`, `compliance_checks`, `organization_patterns`, `naming_conventions`
- Limits: `max_file_size_mb=100`; languages are unlimited at Enterprise (`enterprise.analyze_code` omits `languages` in `.code-scalpel/limits.toml`)

**MCP Tests**
- Run on a large file and confirm it is accepted beyond Pro limits.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 2) security_scan
**Expected (Enterprise)**
- Capabilities: `basic_vulnerabilities`, `owasp_checks`, `ast_pattern_matching`, `sql_injection_detection`, `xss_detection`, `command_injection_detection`, `context_aware_scanning`, `sanitizer_recognition`, `data_flow_sensitive_analysis`, `false_positive_reduction`, `remediation_suggestions`, `owasp_categorization`, `full_vulnerability_list`, `cross_file_taint`, `custom_policy_engine`, `org_specific_rules`, `log_encryption_enforcement`, `compliance_rule_checking`, `custom_security_rules`, `compliance_reporting`, `priority_cve_alerts`
- Limits: unlimited (Enterprise removes caps for `max_findings` and `max_file_size_kb`; `vulnerability_types=all`)

**MCP Tests**
- Run on a multi-file fixture and confirm cross-file taint/correlation fields appear.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 3) extract_code
**Expected (Enterprise)**
- Capabilities: `single_file_extraction`, `basic_symbols`, `cross_file_deps`, `context_extraction`, `org_wide_resolution`, `custom_extraction_patterns`, `dockerfile_generation`, `service_boundaries`
- Limits: `include_cross_file_deps=true`; `max_depth=unlimited`; `max_extraction_size_mb=100`

**MCP Tests**
- Run with `include_cross_file_deps=True` and higher depth; confirm it is not clamped.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 4) symbolic_execute
**Expected (Enterprise)**
- Capabilities: `basic_symbolic_execution`, `simple_constraints`, `complex_constraints`, `string_constraints`, `custom_solvers`, `advanced_types`, `formal_verification`, `equivalence_checking`
- Limits: `max_paths=unlimited`; `max_depth=unlimited`; `constraint_types=all`

**MCP Tests**
- Request high `max_paths` and confirm it is not clamped.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 5) generate_unit_tests
**Expected (Enterprise)**
- Capabilities: `basic_test_generation`, `advanced_test_generation`, `edge_case_detection`, `custom_test_templates`, `coverage_optimization`
- Limits: `max_test_cases=unlimited`; `test_frameworks=all`; `data_driven_tests=true`; `bug_reproduction=true`

**MCP Tests**
- Generate tests for a complex function; confirm output remains MCP-serializable.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 6) crawl_project
**Expected (Enterprise)**
- Capabilities: `full_file_tree_indexing`, `language_breakdown`, `gitignore_respect`, `basic_statistics`, `entrypoint_detection`, `smart_crawl`, `framework_entrypoint_detection`, `generated_code_detection`, `nextjs_pages_detection`, `django_views_detection`, `flask_routes_detection`, `incremental_indexing`, `monorepo_support`, `cross_repo_dependency_linking`, `100k_plus_files_support`
- Limits: `max_files=unlimited`; parsing enabled (`parsing_enabled=true`); complexity enabled (`complexity_analysis=true`); `.gitignore` respected (`respect_gitignore=true`)

**MCP Tests**
- Run on a large repo; confirm it completes and returns complexity hotspots.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 7) get_call_graph
**Expected (Enterprise)**
- Capabilities: `static_call_graph`, `caller_analysis`, `callee_analysis`, `mermaid_diagram_generation`, `circular_import_detection`, `entry_point_detection`, `advanced_call_graph`, `interface_resolution`, `polymorphism_resolution`, `virtual_call_tracking`, `dynamic_dispatch_analysis`, `hot_path_identification`, `dead_code_detection`, `runtime_trace_overlay`, `custom_graph_analysis`
- Limits: `max_depth=unlimited`; `max_nodes=unlimited`

**MCP Tests**
- Request deep traversal and confirm it is not clamped.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 8) get_graph_neighborhood
**Expected (Enterprise)**
- Capabilities: `basic_neighborhood`, `advanced_neighborhood`, `semantic_neighbors`, `logical_relationship_detection`, `custom_traversal`, `weighted_paths`, `graph_query_language`, `custom_traversal_rules`, `path_constraint_queries`
- Limits: `max_k=unlimited`; `max_nodes=unlimited`

**MCP Tests**
- Request `k>5` and confirm it is accepted.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 9) get_symbol_references
**Expected (Enterprise)**
- Capabilities: `ast_based_find_usages`, `exact_reference_matching`, `comment_string_exclusion`, `definition_location`, `project_wide_search`, `usage_categorization`, `read_write_classification`, `import_classification`, `scope_filtering`, `test_file_filtering`, `impact_analysis`, `codeowners_integration`, `ownership_attribution`, `change_risk_assessment`
- Limits: unlimited (no `max_files_searched` / `max_references` caps at Enterprise)

**MCP Tests**
- Search a broad project and confirm results are not capped.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 10) simulate_refactor
**Expected (Enterprise)**
- Capabilities: `basic_simulation`, `structural_diff`, `advanced_simulation`, `behavior_preservation`, `type_checking`, `build_check`, `regression_prediction`, `impact_analysis`, `custom_rules`, `compliance_validation`
- Limits: `max_file_size_mb=100`; `analysis_depth=deep`

**MCP Tests**
- Run with `strict_mode=true` and confirm warnings flip to unsafe.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 11) scan_dependencies
**Expected (Enterprise)**
- Capabilities: `basic_dependency_scan`, `advanced_scan`, `update_recommendations`, `compliance_reporting`, `custom_policies`
- Limits: `max_dependencies=unlimited`; `osv_lookup=true`

**MCP Tests**
- Run with vulnerability lookup enabled; confirm vulnerability data is returned when reachable.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 12) get_cross_file_dependencies
**Expected (Enterprise)**
- Capabilities: `direct_import_mapping`, `circular_import_detection`, `import_graph_generation`, `transitive_dependency_mapping`, `dependency_chain_visualization`, `deep_coupling_analysis`, `architectural_firewall`, `boundary_violation_alerts`, `layer_constraint_enforcement`, `dependency_rule_engine`
- Limits: `max_depth=unlimited`; `max_files=unlimited`

**MCP Tests**
- Request `max_depth=10` with `include_code=true` and confirm it is accepted.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 13) cross_file_security_scan
**Expected (Enterprise)**
- Capabilities: `basic_cross_file_scan`, `single_module_taint_tracking`, `source_to_sink_tracing`, `basic_taint_propagation`, `advanced_taint_tracking`, `framework_aware_taint`, `spring_bean_tracking`, `react_context_tracking`, `dependency_injection_resolution`, `project_wide_scan`, `custom_taint_rules`, `global_taint_flow`, `frontend_to_backend_tracing`, `api_to_database_tracing`, `microservice_boundary_crossing`
- Limits: `max_modules=unlimited`; `max_depth=unlimited`

**MCP Tests**
- Run on a cross-file fixture and confirm diagram output is present.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 14) verify_policy_integrity
**Expected (Enterprise)**
- Capabilities: `basic_verification`, `signature_validation`, `full_integrity_check`, `audit_logging`
- Limits: unlimited (`max_rules` is omitted for `enterprise.verify_policy_integrity` in `.code-scalpel/limits.toml`)
- Notes: Crypto verification requires `SCALPEL_MANIFEST_SECRET` when validating signed manifests.

**MCP Tests**
- Provide a manifest + `SCALPEL_MANIFEST_SECRET` and confirm signature verification passes.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 15) code_policy_check
**Expected (Enterprise)**
- Capabilities: `style_guide_checking`, `pep8_validation`, `eslint_rules`, `basic_patterns`, `best_practice_analysis`, `async_error_patterns`, `security_patterns`, `custom_rules`, `compliance_auditing`, `hipaa_checks`, `soc2_checks`, `gdpr_checks`, `pci_dss_checks`, `pdf_certification`, `audit_trail`
- Limits: unlimited (`max_files`/`max_rules` omitted); `compliance_enabled=true`; `custom_rules_enabled=true`; `audit_trail_enabled=true`; `pdf_reports_enabled=true`

**MCP Tests**
- Call `code_policy_check` with `compliance_standards=["soc2"]` and `generate_report=true` and confirm a report is generated (or a clear deterministic error if the runtime cannot generate PDFs).

**Recorded Result**: ☑ PASS / ☐ FAIL

### 16) type_evaporation_scan
**Expected (Enterprise)**
- Capabilities: `explicit_any_detection`, `typescript_any_scanning`, `basic_type_check`, `frontend_backend_correlation`, `implicit_any_tracing`, `network_boundary_analysis`, `library_boundary_analysis`, `json_parse_tracking`, `runtime_validation_generation`, `zod_schema_generation`, `pydantic_model_generation`, `api_contract_validation`, `custom_type_rules`, `compliance_validation`
- Limits: `max_files=unlimited`; `frontend_only=false`

**MCP Tests**
- Provide a TS/py pair and confirm Enterprise-only schema suggestions appear.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 17) unified_sink_detect
**Expected (Enterprise)**
- Capabilities: `sql_sink_detection`, `shell_command_sink_detection`, `file_operation_sinks`, `xss_sink_detection`, `basic_multi_language_support`, `logic_sink_detection`, `s3_public_write_detection`, `email_send_detection`, `payment_api_detection`, `extended_language_support`, `sink_confidence_scoring`, `sink_categorization`, `risk_level_tagging`, `clearance_requirement_tagging`, `custom_sink_patterns`, `sink_inventory_reporting`
- Limits: languages unlimited (`enterprise.unified_sink_detect` omits `languages` in `.code-scalpel/limits.toml`); `max_sinks=unlimited`; `custom_sinks_limit=unlimited`

**MCP Tests**
- Run with a less-common language and confirm it is accepted.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 18) validate_paths
**Expected (Enterprise)**
- Capabilities: `file_existence_validation`, `import_path_checking`, `broken_reference_detection`, `basic_validation`, `docker_detection`, `volume_suggestions`, `path_alias_resolution`, `tsconfig_paths_support`, `webpack_alias_support`, `dynamic_import_resolution`, `extended_language_support`, `permission_checks`, `security_validation`, `path_traversal_simulation`, `symbolic_path_breaking`, `security_boundary_testing`
- Limits: `max_paths=unlimited`

**MCP Tests**
- Validate a large list of paths.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 19) update_symbol
**Expected (Enterprise)**
- Capabilities: `basic_replacement`, `semantic_validation`, `cross_file_updates`, `impact_analysis`, `rollback_support`, `git_integration`, `branch_creation`, `test_execution`
- Limits: `backup_enabled=true`; `validation_level=full`

**MCP Tests**
- Update a function and confirm backup created.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 20) rename_symbol
**Expected (Enterprise)**
- Capabilities: updates the symbol definition in-file and updates resolvable references/imports across the workspace/org scope.
- Limits: unlimited by default (no `max_files_*` keys in `limits.toml`); `create_backup` supported.

**MCP Tests**
- Rename a symbol and confirm success + backup created.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 21) get_project_map
**Expected (Enterprise)**
- Capabilities: `text_tree_generation`, `basic_mermaid_diagram`, `folder_structure_visualization`, `file_count_statistics`, `module_relationship_visualization`, `import_dependency_diagram`, `architectural_layer_detection`, `coupling_analysis`, `interactive_city_map`, `force_directed_graph`, `bug_hotspot_heatmap`, `code_churn_visualization`, `git_blame_integration`
- Limits: `detail_level=comprehensive`; `max_files=unlimited`; `max_modules=1000`

**MCP Tests**
- Run on a broad project and confirm comprehensive mapping.

**Recorded Result**: ☑ PASS / ☐ FAIL

### 22) get_file_context
**Expected (Enterprise)**
- Capabilities: `raw_source_retrieval`, `ast_based_outlining`, `function_folding`, `class_folding`, `line_range_extraction`, `semantic_summarization`, `intent_extraction`, `related_imports_inclusion`, `smart_context_expansion`, `pii_redaction`, `secret_masking`, `api_key_detection`, `rbac_aware_retrieval`, `file_access_control`
- Limits: `max_context_lines=unlimited`

**MCP Tests**
- Call on a file with known sinks and confirm warnings populate.

**Recorded Result**: ☑ PASS / ☐ FAIL
