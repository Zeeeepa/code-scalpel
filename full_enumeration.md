# Code Scalpel v2.1.2 — Complete Feature/Function/Flow Enumeration

## Summary
- **Total Python files**: 394
- **Total functions**: 871
- **Total classes**: 1416

## 1. MCP Tools (23 registered)

### 1.1 Graph Tools (`mcp/tools/graph.py`)
| Tool | Parameters | Description |
|------|-----------|-------------|
| `get_call_graph` | project_root, entry_point, depth, include_circular_import_check, paths_from, paths_to, focus_functions | Build call graph showing function relationships |
| `get_graph_neighborhood` | center_node_id, k, max_nodes, direction, min_confidence, project_root | Extract k-hop neighborhood subgraph |
| `get_project_map` | project_root, include_complexity, complexity_threshold, include_circular_check, detect_service_boundaries, min_isolation_score | Generate comprehensive project structure map |
| `get_cross_file_dependencies` | target_file, target_symbol, project_root, max_depth, include_code, include_diagram, confidence_decay_factor, max_files, timeout_seconds | Analyze cross-file symbol dependencies |
| `cross_file_security_scan` | project_root, entry_points, max_depth, include_diagram, timeout_seconds, max_modules, confidence_threshold | Cross-file taint flow security analysis |

### 1.2 Analysis Tools (`mcp/tools/analyze.py`)
| Tool | Parameters | Description |
|------|-----------|-------------|
| `analyze_code` | code, language, file_path, static_tools | AST parsing + code metrics |

### 1.3 Security Tools (`mcp/tools/security.py`)
| Tool | Parameters | Description |
|------|-----------|-------------|
| `unified_sink_detect` | code, language, confidence_threshold | Polyglot security sink detection |
| `type_evaporation_scan` | frontend_code, backend_code, frontend_file_path, backend_file_path | Detect type system evaporation across FE/BE boundary |
| `scan_dependencies` | path, project_root, scan_vulnerabilities, include_dev, timeout | Dependency vulnerability scanning |
| `security_scan` | code, file_path, confidence_threshold | Taint analysis security scan |

### 1.4 Extraction Tools (`mcp/tools/extraction.py`)
| Tool | Parameters | Description |
|------|-----------|-------------|
| `extract_code` | target_type, target_name, file_path, code, language, include_context | Extract code elements with dependency context |
| `rename_symbol` | file_path, target_type, target_name, new_name, create_backup | Safe symbol renaming |
| `update_symbol` | file_path, target_type, target_name, new_code, operation, new_name | Safe symbol replacement |

### 1.5 Context Tools (`mcp/tools/context.py`)
| Tool | Parameters | Description |
|------|-----------|-------------|
| `crawl_project` | root_path, exclude_dirs, complexity_threshold, include_report, pattern, pattern_type | Project directory analysis |
| `get_file_context` | file_path | File overview without full read |
| `get_symbol_references` | symbol_name, project_root, scope_prefix, include_tests | Cross-project symbol reference finder |

### 1.6 Symbolic Tools (`mcp/tools/symbolic.py`)
| Tool | Parameters | Description |
|------|-----------|-------------|
| `symbolic_execute` | code, max_paths, max_depth | Symbolic execution on Python code |
| `generate_unit_tests` | code, file_path, function_name, framework, data_driven, crash_log | Test generation from symbolic execution |
| `simulate_refactor` | original_code, new_code, patch, strict_mode | Refactoring safety simulation |

### 1.7 Other Tools
| Tool | File | Description |
|------|------|-------------|
| `run_static_analysis` | static_analysis.py | Polyglot static analysis (bandit/ruff/eslint etc) |
| `get_capabilities` | system.py | License tier capability query |
| `validate_paths` | policy.py | Path accessibility validation |
| `verify_policy_integrity` | policy.py | Cryptographic policy file verification |
| `code_policy_check` | policy.py | Style/compliance/best-practice checking |

## 2. MCP Resources (7 registered)

| URI | Description |
|-----|-------------|
| `scalpel://project/call-graph` | Project call graph resource |
| `scalpel://project/dependencies` | Project dependencies resource |
| `scalpel://project/structure` | Project structure resource |
| `scalpel://version` | Version information |
| `scalpel://health` | Health check |
| `scalpel://capabilities` | Available capabilities |
| `scalpel://file/{path}` | Individual file access |

## 3. MCP Prompts (6 registered)

| Prompt | Description |
|--------|-------------|
| Deep Security Audit | Security audit workflow |
| Refactor Safely | Safe refactoring workflow |
| Modernize Legacy Code | Legacy code modernization |
| Map Architecture | Architecture mapping |
| Verify Supply Chain | Supply chain verification |
| Explain and Document | Code explanation/documentation |

## 4. Complete Module Index (394 modules, 871 functions, 1416 classes)

### 4._root `_root/` — 44 functions, 0 classes

#### `__init__.py` (333 LOC, 8 funcs, 0 classes)
- `def _get_autonomy_import(name)` L78 — Lazy loader for autonomy features (moved to codescalpel-agents package).
- `def __getattr__(name)` L90 — Lazy loader for optional dependencies (Autonomy, Flask REST API).
- `def _run_mcp_tool_sync()` L228 — 
- `def extract_code()` L243 — [20251228_FEATURE] Sync wrapper for MCP extract_code tool.
- `def security_scan(code, file_path)` L272 — [20251228_FEATURE] Sync wrapper for MCP security_scan tool.
- `def symbolic_execute(code, max_paths, max_depth)` L279 — [20251228_FEATURE] Sync wrapper for MCP symbolic_execute tool.
- `def generate_unit_tests(code, file_path, function_name, framework)` L296 — [20251228_FEATURE] Sync wrapper for MCP generate_unit_tests tool.
- `def simulate_refactor(original_code, new_code, patch, strict_mode)` L316 — [20251228_FEATURE] Sync wrapper for MCP simulate_refactor tool.

#### `cli.py` (2740 LOC, 36 funcs, 0 classes)
- `def analyze_file(filepath, output_format, language)` L10 — Analyze a file and print results.
- `def _analyze_javascript(code, output_format, source)` L83 — Analyze JavaScript code using SymbolicAnalyzer.
- `def _analyze_java(code, output_format, source)` L125 — Analyze Java code using SymbolicAnalyzer.
- `def _analyze_polyglot(code, output_format, source, language)` L167 — Analyze non-Python/JS/Java code via the polyglot IR extractor.
- `def analyze_code(code, output_format, source, language)` L228 — Analyze code string and print results.
- `def scan_security(filepath, output_format)` L338 — Scan a file for security vulnerabilities using taint analysis.
- `def scan_code_security(code, output_format)` L401 — Scan code string for security vulnerabilities.
- `def check_configuration(target_dir, json_output, fix)` L453 — Check .code-scalpel directory for missing configuration files.
- `def init_configuration(target_dir, force)` L743 — Initialize .code-scalpel configuration directory.
- `def start_server(host, port)` L837 — Start the REST API server (legacy, for non-MCP clients).
- `def start_mcp_server(transport, host, port, allow_lan)` L863 — Start the MCP-compliant server (for AI clients like Claude Desktop, Cursor).
- `def _license_install(source_path, dest_path, force)` L1002 — [20251228_FEATURE] Implements `code-scalpel license install`.
- `def verify_policies_command(policy_dir, manifest_source)` L1071 — Verify policy integrity using cryptographic signatures.
- `def regenerate_manifest_command(policy_dir, signed_by)` L1122 — Regenerate policy manifest after policy changes.
- `def show_capabilities(tier, tool_filter, json_output)` L1192 — Show available tools and limits for the current or specified tier.
- `def handle_extract_code(args)` L1315 — Handle 'codescalpel extract-code' command.
- `def handle_get_call_graph(args)` L1356 — Handle 'codescalpel get-call-graph' command.
- `def handle_rename_symbol(args)` L1389 — Handle 'codescalpel rename-symbol' command.
- `def handle_get_file_context(args)` L1406 — Handle 'codescalpel get-file-context' command.
- `def handle_get_symbol_references(args)` L1418 — Handle 'codescalpel get-symbol-references' command.
- `def handle_get_graph_neighborhood(args)` L1433 — Handle 'codescalpel get-graph-neighborhood' command.
- `def handle_get_project_map(args)` L1448 — Handle 'codescalpel get-project-map' command.
- `def handle_get_cross_file_dependencies(args)` L1462 — Handle 'codescalpel get-cross-file-dependencies' command.
- `def handle_crawl_project(args)` L1479 — Handle 'codescalpel crawl-project' command.
- `def handle_cross_file_security_scan(args)` L1497 — Handle 'codescalpel cross-file-security-scan' command.
- `def handle_type_evaporation_scan(args)` L1511 — Handle 'codescalpel type-evaporation-scan' command.
- `def handle_unified_sink_detect(args)` L1526 — Handle 'codescalpel unified-sink-detect' command.
- `def handle_symbolic_execute(args)` L1540 — Handle 'codescalpel symbolic-execute' command.
- `def handle_update_symbol(args)` L1555 — Handle 'codescalpel update-symbol' command.
- `def handle_simulate_refactor(args)` L1571 — Handle 'codescalpel simulate-refactor' command.
- `def handle_generate_unit_tests(args)` L1584 — Handle 'codescalpel generate-unit-tests' command.
- `def handle_validate_paths(args)` L1600 — Handle 'codescalpel validate-paths' command.
- `def handle_scan_dependencies(args)` L1613 — Handle 'codescalpel scan-dependencies' command.
- `def handle_code_policy_check(args)` L1627 — Handle 'codescalpel code-policy-check' command.
- `def handle_verify_policy_integrity(args)` L1641 — Handle 'codescalpel verify-policy-integrity' command.
- `def main()` L1653 — Main CLI entry point.

### 4.analysis `analysis/` — 13 functions, 69 classes

#### `analysis/code_analyzer.py` (1714 LOC, 1 funcs, 7 classes)
- **class AnalysisLevel** (line 65, 0 methods) — Level of analysis to perform.
- **class AnalysisLanguage** (line 73, 0 methods) — Supported analysis languages.
- **class DeadCodeItem** (line 84, 0 methods) — Represents a detected dead code element.
- **class AnalysisMetrics** (line 96, 0 methods) — Metrics from code analysis.
- **class RefactorSuggestion** (line 115, 0 methods) — A suggested refactoring operation.
- **class AnalysisResult** (line 126, 0 methods) — Complete result of code analysis.
- **class CodeAnalyzer** (line 146, 51 methods) — Unified code analysis pipeline with AST, PDG, and symbolic execution.
- `def analyze_code(code, level)` L1686 — Convenience function to quickly analyze code.

#### `analysis/core.py` (111 LOC, 0 funcs, 1 classes)
- **class CodeAnalysisToolkit** (line 21, 9 methods) — 

#### `analysis/cross_repo.py` (458 LOC, 1 funcs, 4 classes)
- **class ExternalDependency** (line 33, 0 methods) — An external package dependency.
- **class InternalLink** (line 44, 0 methods) — A link between two internal packages/modules.
- **class CrossRepoAnalysis** (line 56, 0 methods) — Complete cross-repository analysis.
- **class CrossRepoLinker** (line 67, 11 methods) — Analyze and link dependencies across repositories.
- `def analyze_cross_repo_deps(repo_paths, repo_names)` L438 — Convenience function to analyze cross-repository dependencies.

#### `analysis/custom_metrics.py` (579 LOC, 1 funcs, 11 classes)
- **class MetricValue** (line 37, 0 methods) — A single metric measurement.
- **class MetricSummary** (line 49, 0 methods) — Summary of a metric across all files.
- **class MetricsReport** (line 62, 2 methods) — Complete metrics report for a project.
- **class MetricCollector** (line 123, 3 methods) — Abstract base class for metric collectors.
- **class LinesOfCodeCollector** (line 152, 3 methods) — Collects lines of code metrics.
- **class CyclomaticComplexityCollector** (line 186, 3 methods) — Collects cyclomatic complexity for Python files.
- **class FunctionCountCollector** (line 228, 3 methods) — Counts functions/methods in files.
- **class ClassCountCollector** (line 268, 3 methods) — Counts classes in files.
- **class ImportCountCollector** (line 304, 3 methods) — Counts imports in files.
- **class TodoCountCollector** (line 339, 3 methods) — 
- **class MetricsCollector** (line 378, 5 methods) — Main metrics collection orchestrator.
- `def collect_metrics(project_path, custom_metrics)` L559 — Convenience function to collect project metrics.

#### `analysis/framework_detector.py` (412 LOC, 1 funcs, 3 classes)
- **class FrameworkRoute** (line 32, 0 methods) — Detected route or entry point in a framework.
- **class FrameworkDetectionResult** (line 45, 0 methods) — Result of framework detection.
- **class FrameworkDetector** (line 58, 14 methods) — Detects web framework entry points and components.
- `def detect_frameworks(project_root)` L409 — Detect web frameworks in a project.

#### `analysis/generated_code.py` (221 LOC, 1 funcs, 3 classes)
- **class GeneratedFileInfo** (line 30, 0 methods) — Information about a detected generated file.
- **class GeneratedCodeResult** (line 40, 0 methods) — Result of generated code detection.
- **class GeneratedCodeDetector** (line 49, 3 methods) — Detects auto-generated code in a project.
- `def detect_generated_files(project_root, check_headers, max_files)` L216 — Convenience function to detect generated files.

#### `analysis/gitignore.py` (101 LOC, 0 funcs, 1 classes)
- **class GitignoreParser** (line 13, 4 methods) — Simple gitignore pattern parser.

#### `analysis/incremental_index.py` (316 LOC, 0 funcs, 3 classes)
- **class CachedFileAnalysis** (line 37, 0 methods) — Cached analysis result for a file.
- **class IndexStats** (line 52, 0 methods) — Statistics about the incremental index.
- **class IncrementalIndex** (line 63, 15 methods) — SQLite-based incremental index for file analysis caching.

#### `analysis/incremental_indexer.py` (357 LOC, 1 funcs, 4 classes)
- **class FileHash** (line 50, 0 methods) — File hash entry.
- **class CachedAnalysis** (line 60, 0 methods) — Cached analysis result.
- **class IncrementalIndexResult** (line 71, 0 methods) — Result of incremental indexing.
- **class IncrementalIndexer** (line 83, 11 methods) — Incremental analysis with file-level caching.
- `def create_incremental_indexer(project_root, use_redis)` L352 — Factory function for creating an incremental indexer.

#### `analysis/monorepo.py` (446 LOC, 1 funcs, 3 classes)
- **class MonorepoProject** (line 34, 0 methods) — A project/package within a monorepo.
- **class MonorepoDetectionResult** (line 45, 0 methods) — Result of monorepo detection.
- **class MonorepoDetector** (line 56, 14 methods) — Detects and analyzes monorepo structures.
- `def detect_monorepo(project_root)` L443 — Convenience function to detect monorepo configuration.

#### `analysis/org_index.py` (827 LOC, 1 funcs, 8 classes)
- **class IndexedFile** (line 33, 0 methods) — A file indexed in the organization index.
- **class IndexedSymbol** (line 48, 0 methods) — A symbol (function, class, etc.) indexed for cross-project search.
- **class SearchResult** (line 62, 0 methods) — A search result from the organization index.
- **class IndexStats** (line 75, 0 methods) — Statistics about the organization index.
- **class SearchBackend** (line 86, 6 methods) — Abstract interface for search backends.
- **class InMemoryBackend** (line 131, 7 methods) — In-memory search backend for testing and small deployments.
- **class ElasticsearchBackend** (line 259, 9 methods) — Elasticsearch/OpenSearch backend for production deployments.
- **class OrganizationIndex** (line 572, 9 methods) — High-level interface for organization-wide code indexing.
- `def create_org_index(elasticsearch_host)` L815 — Create an organization index.

#### `analysis/parallel_crawler.py` (393 LOC, 1 funcs, 4 classes)
- **class FileInfo** (line 35, 0 methods) — Information about a discovered file.
- **class CrawlChunk** (line 45, 0 methods) — A chunk of crawled files with analysis results.
- **class ParallelCrawlResult** (line 57, 0 methods) — Final result of parallel crawl.
- **class ParallelCrawler** (line 69, 9 methods) — High-performance parallel file crawler for large repositories.
- `def parallel_crawl(project_root, max_workers, chunk_size)` L376 — Convenience function for parallel crawling.

#### `analysis/project_context.py` (514 LOC, 0 funcs, 3 classes)
- **class CacheMetadata** (line 28, 1 methods) — Metadata about a cached project map.
- **class DirectoryType** (line 46, 1 methods) — Classification of a directory.
- **class ProjectContext** (line 78, 17 methods) — Context manager for project analysis with caching and metadata.

#### `analysis/project_crawler.py` (953 LOC, 2 funcs, 7 classes)
- **class CrawlResultDict** (line 43, 0 methods) — Crawl results dictionary for JSON serialization.
- **class FunctionInfo** (line 94, 1 methods) — Information about a function or method.
- **class ClassInfo** (line 114, 0 methods) — Information about a class.
- **class FileAnalysisResult** (line 126, 1 methods) — Result of analyzing a single file.
- **class CrawlResult** (line 149, 6 methods) — Result of crawling an entire project.
- **class CodeAnalyzerVisitor** (line 204, 9 methods) — AST visitor that extracts code metrics.
- **class ProjectCrawler** (line 324, 14 methods) — Crawls a project directory and analyzes all Python files.
- `def _analyze_file_worker(file_path)` L83 — ProcessPool worker entrypoint for analyzing a single file.
- `def crawl_project(root_path, exclude_dirs, complexity_threshold)` L930 — Convenience function to crawl a project and return results as a dictionary.

#### `analysis/project_walker.py` (530 LOC, 0 funcs, 4 classes)
- **class FileInfo** (line 81, 2 methods) — Information about a discovered file.
- **class DirectoryInfo** (line 103, 1 methods) — Information about a discovered directory.
- **class ProjectMap** (line 119, 3 methods) — Complete map of a project's file structure.
- **class ProjectWalker** (line 149, 13 methods) — Smart file discovery engine for large codebases.

#### `analysis/smart_crawl.py` (267 LOC, 2 funcs, 3 classes)
- **class ProjectTypeInfo** (line 29, 0 methods) — Detected project type information.
- **class SmartCrawlConfig** (line 39, 0 methods) — Configuration generated by smart crawl detection.
- **class SmartCrawler** (line 50, 3 methods) — Adaptive crawler that adjusts behavior based on project type.
- `def detect_project_type(project_root)` L258 — Convenience function to detect project type.
- `def get_smart_crawl_config(project_root)` L264 — Convenience function to get smart crawl configuration.

### 4.ast_tools `ast_tools/` — 9 functions, 53 classes

#### `ast_tools/__init__.py` (135 LOC, 3 funcs, 0 classes)
- `def build_ast(code, preprocess, validate)` L34 — Build an AST from Python code.
- `def build_ast_from_file(filepath, preprocess, validate)` L39 — Build an AST from a Python source file.
- `def visualize_ast(tree, output_file, format, view)` L45 — Visualize an AST using graphviz.

#### `ast_tools/analyzer.py` (308 LOC, 0 funcs, 3 classes)
- **class FunctionMetrics** (line 15, 0 methods) — Metrics for a function.
- **class ClassMetrics** (line 29, 0 methods) — Metrics for a class.
- **class ASTAnalyzer** (line 40, 17 methods) — Advanced Python code analyzer using Abstract Syntax Trees (ASTs).

#### `ast_tools/architectural_rules.py` (651 LOC, 1 funcs, 7 classes)
- **class ViolationSeverity** (line 43, 0 methods) — Severity levels for architectural violations.
- **class ViolationAction** (line 52, 0 methods) — Actions to take when a violation is detected.
- **class ArchitecturalViolation** (line 61, 0 methods) — Represents a detected architectural violation.
- **class CustomRule** (line 87, 0 methods) — A custom dependency rule.
- **class CouplingLimits** (line 99, 0 methods) — Coupling limit configuration.
- **class ArchitectureConfig** (line 109, 0 methods) — Complete architecture configuration.
- **class ArchitecturalRuleEngine** (line 137, 15 methods) — Engine for checking architectural boundary violations.
- `def load_architecture_config(project_root)` L642 — Convenience loader for backward compatibility.

#### `ast_tools/ast_refactoring.py` (182 LOC, 0 funcs, 5 classes)
- **class RefactoringType** (line 33, 0 methods) — Types of refactoring opportunities.
- **class CodeSmellType** (line 52, 0 methods) — Types of code smells.
- **class RefactoringOpportunity** (line 68, 0 methods) — A refactoring opportunity.
- **class CodeSmell** (line 83, 0 methods) — A code smell detected in the code.
- **class RefactoringAnalyzer** (line 94, 18 methods) — Analyzes code for refactoring opportunities and code smells.

#### `ast_tools/builder.py` (158 LOC, 0 funcs, 1 classes)
- **class ASTBuilder** (line 13, 12 methods) — Advanced AST builder with preprocessing and validation capabilities.

#### `ast_tools/call_graph.py` (3119 LOC, 0 funcs, 5 classes)
- **class CallContext** (line 15, 0 methods) — Context information about where a call is made.
- **class CallNode** (line 31, 0 methods) — A node in the call graph with location information.
- **class CallEdge** (line 44, 0 methods) — An edge in the call graph representing a call relationship.
- **class CallGraphResult** (line 56, 0 methods) — Result of call graph analysis.
- **class CallGraphBuilder** (line 71, 87 methods) — Builds a static call graph for Python and supported polyglot projects.

#### `ast_tools/control_flow.py` (164 LOC, 0 funcs, 4 classes)
- **class BlockType** (line 35, 0 methods) — Types of basic blocks in control flow.
- **class BasicBlock** (line 48, 0 methods) — A basic block in control flow.
- **class ControlFlowGraph** (line 61, 0 methods) — Represents a control flow graph.
- **class ControlFlowBuilder** (line 70, 13 methods) — Build and analyze control flow graphs.

#### `ast_tools/cross_file_extractor.py` (967 LOC, 1 funcs, 4 classes)
- **class ExtractedSymbol** (line 33, 2 methods) — A single extracted code symbol.
- **class ExtractionResult** (line 109, 4 methods) — Result of a cross-file extraction operation.
- **class DependencyNode** (line 172, 0 methods) — Node in the dependency graph during extraction.
- **class CrossFileExtractor** (line 189, 20 methods) — Extract code symbols with their cross-file dependencies.
- `def calculate_confidence(depth, decay_factor)` L77 — Calculate confidence score with exponential decay based on depth.

#### `ast_tools/data_flow.py` (222 LOC, 0 funcs, 5 classes)
- **class DataFlowFact** (line 35, 0 methods) — Types of data flow facts.
- **class Definition** (line 45, 0 methods) — A definition of a variable.
- **class Usage** (line 58, 0 methods) — A usage of a variable.
- **class DataFlow** (line 68, 0 methods) — Data flow information for a program.
- **class DataFlowAnalyzer** (line 77, 15 methods) — Advanced data flow analyzer.

#### `ast_tools/dependency_parser.py` (162 LOC, 0 funcs, 1 classes)
- **class DependencyParser** (line 16, 7 methods) — Parses project dependencies from standard configuration files.

#### `ast_tools/import_resolver.py` (1499 LOC, 1 funcs, 7 classes)
- **class ImportType** (line 44, 0 methods) — Classification of import statement types.
- **class ImportInfo** (line 59, 3 methods) — Information about a single import statement.
- **class DynamicImportVisitor** (line 102, 6 methods) — Visitor to extract dynamic imports and track local string variables.
- **class SymbolDefinition** (line 179, 0 methods) — Definition of a symbol (function, class, variable) in a module.
- **class CircularImport** (line 205, 1 methods) — Information about a detected circular import.
- **class ImportGraphResult** (line 224, 0 methods) — Result of building the import graph.
- **class ImportResolver** (line 245, 45 methods) — Build and query module import relationships for a Python project.
- `def _parse_for_imports(file_path)` L37 — 

#### `ast_tools/transformer.py` (304 LOC, 0 funcs, 2 classes)
- **class TransformationRule** (line 11, 0 methods) — Defines a transformation rule.
- **class ASTTransformer** (line 19, 17 methods) — Advanced AST transformer with pattern matching and complex transformations.

#### `ast_tools/type_inference.py` (121 LOC, 0 funcs, 3 classes)
- **class TypeInfo** (line 33, 0 methods) — Information about an inferred type.
- **class FunctionTypeInfo** (line 45, 0 methods) — Type information for a function.
- **class TypeInference** (line 55, 12 methods) — Advanced type inference engine for Python code.

#### `ast_tools/utils.py` (211 LOC, 3 funcs, 1 classes)
- **class ASTUtils** (line 10, 14 methods) — Utility functions for working with ASTs.
- `def is_constant(node)` L197 — Check if a node represents a constant value.
- `def get_node_type(node)` L204 — Get the type name of an AST node.
- `def get_all_names(tree)` L209 — Get all names used in the AST.

#### `ast_tools/validator.py` (286 LOC, 0 funcs, 3 classes)
- **class Severity** (line 8, 0 methods) — Severity levels for validation issues.
- **class ValidationIssue** (line 17, 0 methods) — Represents a validation issue.
- **class ASTValidator** (line 27, 26 methods) — Advanced AST validator with configurable rules and detailed reporting.

#### `ast_tools/visualizer.py` (442 LOC, 0 funcs, 2 classes)
- **class VisualizationConfig** (line 17, 0 methods) — Configuration for AST visualization.
- **class ASTVisualizer** (line 30, 19 methods) — Advanced AST visualization with customizable styling and multiple output formats

### 4.cache `cache/` — 4 functions, 9 classes

#### `cache/ast_cache.py` (425 LOC, 1 funcs, 2 classes)
- **class CacheMetadata** (line 24, 0 methods) — Metadata for cached AST entries.
- **class IncrementalASTCache** (line 37, 15 methods) — [20251216_FEATURE] Incremental AST cache with dependency tracking.
- `def get_ast_cache(cache_dir)` L408 — Get the global AST cache instance.

#### `cache/incremental_analyzer.py` (47 LOC, 0 funcs, 1 classes)
- **class IncrementalAnalyzer** (line 15, 4 methods) — [20251214_FEATURE] Dependency-aware incremental analysis.

#### `cache/parallel_parser.py` (107 LOC, 1 funcs, 1 classes)
- **class ParallelParser** (line 34, 2 methods) — [20251214_FEATURE] Parallel file parsing with cache reuse.
- `def _batch_parse_worker(file_paths, parse_fn)` L19 — Parse a batch of files, returning (path, result, error) tuples.

#### `cache/unified_cache.py` (780 LOC, 2 funcs, 5 classes)
- **class CacheStatsDict** (line 46, 0 methods) — Cache statistics dictionary for JSON serialization.
- **class CacheConfig** (line 83, 0 methods) — Configuration for the analysis cache.
- **class CacheEntry** (line 107, 0 methods) — A single cache entry with metadata.
- **class CacheStats** (line 122, 8 methods) — Statistics about cache performance.
- **class AnalysisCache** (line 224, 23 methods) — Unified memory+disk cache for code analysis artifacts and results.
- `def get_cache(config)` L760 — Get the global cache instance.
- `def reset_cache()` L775 — Reset the global cache instance.

### 4.capabilities `capabilities/` — 8 functions, 3 classes

#### `capabilities/resolver.py` (166 LOC, 6 funcs, 0 classes)
- `def get_tool_capabilities(tool_id, tier)` L62 — Get the capabilities/limits for a specific tool at a specific tier.
- `def get_all_capabilities(tier)` L114 — Get all capabilities for all 23 tools at a specific tier.
- `def get_tool_names()` L148 — Get the list of all 23 tool names.
- `def get_tier_names()` L153 — Get the list of all supported tier names.
- `def validate_tier(tier)` L158 — Check if a tier name is valid.
- `def reload_limits_cache()` L163 — Force reload of the limits.toml file (delegates to config_loader).

#### `capabilities/schema.py` (281 LOC, 2 funcs, 3 classes)
- **class CapabilityLimits** (line 20, 2 methods) — Limits for a tool at a specific tier.
- **class Capability** (line 118, 2 methods) — A single capability/tool at a specific tier.
- **class CapabilityEnvelope** (line 153, 2 methods) — Envelope containing all capabilities for a tier.
- `def validate_capability(data)` L193 — Validate that a capability dictionary has the correct structure.
- `def get_json_schema()` L219 — Get the JSON Schema for a capability.

### 4.cli_tools `cli_tools/` — 8 functions, 0 classes

#### `cli_tools/tool_bridge.py` (334 LOC, 8 funcs, 0 classes)
- `def invoke_tool(tool_name, args)` L26 — Invoke an MCP tool from CLI context.
- `def invoke_tool_with_format(tool_name, args, output_format)` L54 — Invoke an MCP tool from CLI context with specified output format.
- `def _get_tool_function(tool_name)` L85 — Dynamically import and return MCP tool function.
- `def _format_and_print_response(response, output_format)` L137 — Format MCP tool response for terminal output.
- `def _print_error(error, tier)` L181 — Print formatted error message with upgrade hints.
- `def _print_success_data(data, tier, duration_ms)` L226 — Print formatted success data.
- `def _print_tool_specific_output(data)` L256 — Print tool-specific formatted output.
- `def format_tool_response(response)` L317 — Format MCP tool response as string (for testing).

### 4.code_parsers `code_parsers/` — 114 functions, 545 classes

#### `code_parsers/adapters/cpp_adapter.py` (53 LOC, 0 funcs, 1 classes)
- **class CppParserAdapter** (line 12, 4 methods) — Adapter wrapping CppNormalizer to implement the IParser interface.

#### `code_parsers/adapters/csharp_adapter.py` (89 LOC, 0 funcs, 1 classes)
- **class CSharpParserAdapter** (line 14, 6 methods) — Adapter for C# parsing backed by CSharpNormalizer (tree-sitter-c-sharp).

#### `code_parsers/adapters/go_adapter.py` (54 LOC, 0 funcs, 1 classes)
- **class GoParserAdapter** (line 11, 4 methods) — Adapter wrapping GoNormalizer to implement the IParser interface.

#### `code_parsers/adapters/java_adapter.py` (255 LOC, 0 funcs, 1 classes)
- **class JavaParserAdapter** (line 15, 9 methods) — Adapter that wraps TreeSitterJavaParser to implement IParser interface.

#### `code_parsers/adapters/javascript_adapter.py` (294 LOC, 0 funcs, 2 classes)
- **class JavaScriptParserAdapter** (line 19, 9 methods) — Adapter that wraps JavaScriptParser to implement IParser interface.
- **class TypeScriptParserAdapter** (line 229, 2 methods) — Adapter for TypeScript parsing using JavaScriptParser with TS mode.

#### `code_parsers/adapters/kotlin_adapter.py` (48 LOC, 0 funcs, 1 classes)
- **class KotlinParserAdapter** (line 11, 4 methods) — Adapter wrapping KotlinNormalizer to implement IParser.

#### `code_parsers/adapters/php_adapter.py` (69 LOC, 0 funcs, 1 classes)
- **class PHPParserAdapter** (line 11, 4 methods) — Adapter for PHP parsing via tree-sitter-php + PHPNormalizer.

#### `code_parsers/adapters/ruby_adapter.py` (86 LOC, 0 funcs, 1 classes)
- **class RubyParserAdapter** (line 15, 4 methods) — Adapter for Ruby parsing using the RubyNormalizer IR layer.

#### `code_parsers/adapters/rust_adapter.py` (52 LOC, 0 funcs, 1 classes)
- **class RustParserAdapter** (line 12, 4 methods) — Adapter wrapping RustNormalizer for the IParser interface.

#### `code_parsers/adapters/swift_adapter.py` (52 LOC, 0 funcs, 1 classes)
- **class SwiftParserAdapter** (line 12, 4 methods) — Adapter wrapping SwiftNormalizer for the IParser interface.

#### `code_parsers/base_parser.py` (282 LOC, 1 funcs, 5 classes)
- **class Language** (line 11, 0 methods) — Supported programming languages.
- **class ParseResult** (line 23, 0 methods) — Result of code parsing.
- **class PreprocessorConfig** (line 35, 0 methods) — Configuration for code preprocessing.
- **class BaseParser** (line 42, 6 methods) — 
- **class CodeParser** (line 147, 8 methods) — Advanced code parser with multi-language support.
- `def parse_code(code, language)` L279 — Convenience function to parse code.

#### `code_parsers/cpp_parsers/__init__.py` (203 LOC, 3 funcs, 1 classes)
- **class CppParserRegistry** (line 73, 2 methods) — Registry for C++ static-analysis tool parsers.
- `def _import_parser_module(class_name)` L145 — Import the module that defines *class_name*.
- `def _load_hyphenated_module(module_basename)` L163 — Load a .py file whose name contains hyphens using path-based loading.
- `def __getattr__(name)` L199 — 

#### `code_parsers/cpp_parsers/cpp_parsers_Clang-Static-Analyzer.py` (399 LOC, 4 funcs, 4 classes)
- **class BugType** (line 28, 0 methods) — Clang Static Analyzer bug types.
- **class AnalyzerFinding** (line 42, 0 methods) — Represents a Clang Static Analyzer finding.
- **class AnalyzerConfig** (line 56, 0 methods) — Clang Static Analyzer configuration.
- **class ClangStaticAnalyzerParser** (line 164, 13 methods) — Parser for Clang Static Analyzer deep bug detection.
- `def _check_to_bug_type(check_name)` L84 — Map a clang-sa check name to its BugType.
- `def _extract_file_list(plist_data)` L92 — Extract the 'files' list from plist data (file indices → paths).
- `def _parse_plist_diagnostic(diag, files)` L97 — Convert a single plist diagnostic dict to an AnalyzerFinding.
- `def _to_sarif_result(finding)` L141 — Convert an AnalyzerFinding to a SARIF 2.1 result dict.

#### `code_parsers/cpp_parsers/cpp_parsers_Cppcheck.py` (416 LOC, 3 funcs, 5 classes)
- **class CppcheckSeverity** (line 22, 0 methods) — Cppcheck issue severity levels.
- **class IssueCategory** (line 33, 0 methods) — Cppcheck issue categories.
- **class CppcheckIssue** (line 45, 0 methods) — Represents a Cppcheck analysis issue.
- **class CppcheckConfig** (line 61, 0 methods) — Cppcheck configuration for analysis.
- **class CppcheckParser** (line 209, 10 methods) — Parser for Cppcheck static analysis of C/C++ code.
- `def _infer_category(issue_id, severity)` L111 — Infer IssueCategory from error id and severity.
- `def _parse_error_element(error_elem)` L136 — Parse a single <error> XML element into a CppcheckIssue.
- `def _to_sarif_result(issue)` L183 — Convert a CppcheckIssue to a SARIF 2.1 result dict.

#### `code_parsers/cpp_parsers/cpp_parsers_SonarQube.py` (392 LOC, 2 funcs, 3 classes)
- **class SonarCppIssue** (line 25, 0 methods) — Represents a SonarQube C++ issue.
- **class SonarCppMetrics** (line 41, 0 methods) — SonarQube C++ project metrics.
- **class SonarQubeCppParser** (line 105, 13 methods) — Parser for SonarQube C++ code quality and security analysis.
- `def _rating_to_letter(value)` L74 — Convert SonarQube numeric rating to letter grade.
- `def _to_sarif_result(issue)` L80 — Convert a SonarCppIssue to a SARIF 2.1 result dict.

#### `code_parsers/cpp_parsers/cpp_parsers_clang_tidy.py` (460 LOC, 4 funcs, 4 classes)
- **class CheckCategory** (line 23, 0 methods) — Clang-Tidy check categories.
- **class ClangTidyCheck** (line 38, 0 methods) — Represents a clang-tidy check violation.
- **class ClangTidyConfig** (line 53, 0 methods) — Clang-Tidy configuration for analysis.
- **class ClangTidyParser** (line 127, 10 methods) — Parser for Clang-Tidy C++ modernization and best practices analysis.
- `def _check_to_category(check_id)` L87 — Map a clang-tidy check ID prefix to its CheckCategory.
- `def _modernization_level(check_id)` L95 — Infer C++ standard level from modernize-* check name.
- `def _to_sarif_result(check)` L104 — Convert a ClangTidyCheck to a SARIF 2.1 result dict.
- `def _parse_minimal_yaml_fixes(raw)` L408 — Minimal YAML parser for clang-tidy fixes export.

#### `code_parsers/cpp_parsers/cpp_parsers_coverity.py` (405 LOC, 5 funcs, 5 classes)
- **class DefectSeverity** (line 22, 0 methods) — Coverity defect severity levels.
- **class DefectType** (line 31, 0 methods) — Coverity defect type categories.
- **class CoverityDefect** (line 42, 0 methods) — Represents a Coverity defect finding.
- **class CoverityConfig** (line 57, 0 methods) — Coverity configuration for analysis.
- **class CoverityParser** (line 185, 11 methods) — Parser for Coverity deep security and quality analysis (enterprise tool).
- `def _checker_to_defect_type(checker_name)` L103 — Map a Coverity checker name to DefectType.
- `def _parse_severity(raw)` L112 — Normalise a Coverity severity string.
- `def _extract_event_chain(events)` L117 — Extract human-readable evidence chain from events array.
- `def _parse_single_issue(issue)` L129 — Parse one issue dict from Coverity JSON output.
- `def _to_sarif_result(defect)` L161 — Convert a CoverityDefect to a SARIF 2.1 result dict.

#### `code_parsers/cpp_parsers/cpp_parsers_cpplint.py` (332 LOC, 3 funcs, 4 classes)
- **class StyleViolationType** (line 23, 0 methods) — Style violation types from cpplint.
- **class CppLintViolation** (line 36, 0 methods) — Represents a cpplint style violation.
- **class CppLintConfig** (line 50, 0 methods) — CppLint configuration for style checking.
- **class CppLintParser** (line 123, 7 methods) — Parser for CppLint Google C++ style guide enforcement.
- `def _category_to_type(category)` L89 — Map a cpplint category string to StyleViolationType.
- `def _confidence_to_severity(confidence)` L94 — Map cpplint confidence (1-5) to a severity string.
- `def _to_sarif_result(v)` L103 — Convert a CppLintViolation to a SARIF 2.1 result dict.

#### `code_parsers/csharp_parsers/__init__.py` (240 LOC, 3 funcs, 2 classes)
- **class SarifFinding** (line 33, 0 methods) — Normalized representation of a single SARIF 2.1 result.
- **class CSharpParserRegistry** (line 129, 2 methods) — Registry for C# parser implementations with lazy-load factory pattern.
- `def _parse_sarif(sarif_source)` L49 — Parse a SARIF 2.1 document and return a flat list of SarifFinding.
- `def _get_parser_module(key)` L183 — Lazy-import the parser module for *key*.
- `def __getattr__(name)` L234 — 

#### `code_parsers/csharp_parsers/csharp_parsers_ReSharper.py` (193 LOC, 0 funcs, 4 classes)
- **class IssueCategory** (line 24, 0 methods) — ReSharper issue categories.
- **class ReSharperIssue** (line 36, 0 methods) — A single ReSharper InspectCode issue.
- **class IssueType** (line 52, 0 methods) — Metadata for a ReSharper issue type (from <IssueTypes> header).
- **class ReSharperParser** (line 71, 4 methods) — Parser for JetBrains ReSharper InspectCode XML output.

#### `code_parsers/csharp_parsers/csharp_parsers_Roslyn-Analyzers.py` (175 LOC, 1 funcs, 2 classes)
- **class RoslynDiagnostic** (line 24, 0 methods) — A single Roslyn analyzer diagnostic.
- **class RoslynAnalyzersParser** (line 50, 4 methods) — Parser for .NET Roslyn Analyzers output via SARIF.
- `def _sarif_to_roslyn(f)` L159 — Convert a SarifFinding to a RoslynDiagnostic.

#### `code_parsers/csharp_parsers/csharp_parsers_SecurityCodeScan.py` (253 LOC, 1 funcs, 4 classes)
- **class VulnerabilityType** (line 25, 0 methods) — Security vulnerability types.
- **class SecurityVulnerability** (line 42, 0 methods) — Represents a security vulnerability found by SCS.
- **class SecurityCodeScanConfig** (line 58, 0 methods) — Security Code Scan configuration.
- **class SecurityCodeScanParser** (line 105, 9 methods) — Parser for Security Code Scan C# security analysis.
- `def _sarif_to_vuln(f)` L234 — Convert a SarifFinding to a SecurityVulnerability.

#### `code_parsers/csharp_parsers/csharp_parsers_SonarQube.py` (259 LOC, 0 funcs, 3 classes)
- **class SonarIssue** (line 27, 0 methods) — Represents a SonarQube issue for C#.
- **class SonarMetrics** (line 43, 0 methods) — SonarQube project metrics.
- **class SonarQubeCSharpParser** (line 57, 10 methods) — Parser for SonarQube C# analysis results.

#### `code_parsers/csharp_parsers/csharp_parsers_StyleCop.py` (165 LOC, 2 funcs, 3 classes)
- **class StyleCopCategory** (line 24, 0 methods) — StyleCop rule categories based on SA1xxx rule ranges.
- **class StyleCopViolation** (line 50, 0 methods) — A single StyleCop rule violation.
- **class StyleCopParser** (line 65, 4 methods) — Parser for StyleCop Analyzers output (SARIF 2.1 via MSBuild).
- `def _sa_category(rule_id)` L144 — Determine StyleCop category from rule_id like 'SA1200'.
- `def _sarif_to_violation(f)` L156 — 

#### `code_parsers/csharp_parsers/csharp_parsers_fxcop.py` (265 LOC, 1 funcs, 5 classes)
- **class FxCopSeverity** (line 26, 0 methods) — FxCop violation severity levels.
- **class RuleCategory** (line 34, 0 methods) — FxCop rule categories.
- **class FxCopViolation** (line 51, 0 methods) — Represents an FxCop code analysis violation.
- **class FxCopConfig** (line 66, 0 methods) — FxCop configuration for analysis.
- **class FxCopParser** (line 93, 7 methods) — Parser for FxCop .NET code analysis (XML and SARIF formats).
- `def _sarif_to_violation(f)` L254 — Convert a SarifFinding (CA* rule) to an FxCopViolation.

#### `code_parsers/extractor.py` (791 LOC, 3 funcs, 3 classes)
- **class Language** (line 34, 0 methods) — Supported programming languages.
- **class PolyglotExtractionResult** (line 103, 0 methods) — Result of polyglot code extraction.
- **class PolyglotExtractor** (line 280, 18 methods) — Multi-language code extractor.
- `def detect_language(file_path, code)` L127 — Detect the programming language from file extension or content.
- `def extract_from_file(file_path, target_type, target_name, language)` L753 — Extract code element from a file.
- `def extract_from_code(code, target_type, target_name, language)` L775 — Extract code element from source string.

#### `code_parsers/factory.py` (243 LOC, 1 funcs, 1 classes)
- **class ParserFactory** (line 13, 6 methods) — Factory for creating language-specific parsers.
- `def _register_available_parsers()` L148 — Register parsers that are available in the installation.

#### `code_parsers/go_parsers/__init__.py` (120 LOC, 2 funcs, 1 classes)
- **class GoParserRegistry** (line 48, 2 methods) — Registry for Go parser implementations with lazy-load factory pattern.
- `def _import_parser_module(module_basename)` L103 — Import a go_parsers sub-module by basename.
- `def __getattr__(name)` L115 — 

#### `code_parsers/go_parsers/go_parsers_gofmt.py` (136 LOC, 0 funcs, 2 classes)
- **class FormattingIssue** (line 24, 0 methods) — A file that is not correctly formatted.
- **class GofmtParser** (line 31, 7 methods) — Parser for gofmt formatting output.

#### `code_parsers/go_parsers/go_parsers_golangci_lint.py` (240 LOC, 0 funcs, 5 classes)
- **class IssueSeverity** (line 23, 0 methods) — Issue severity levels.
- **class LinterType** (line 30, 0 methods) — Types of linters aggregated by golangci-lint (common subset).
- **class LintIssue** (line 52, 0 methods) — Represents a linting issue from golangci-lint.
- **class GolangciLintConfig** (line 69, 0 methods) — Golangci-lint configuration.
- **class GolangciLintParser** (line 82, 8 methods) — Parser for Golangci-Lint comprehensive Go linting.

#### `code_parsers/go_parsers/go_parsers_golint.py` (175 LOC, 1 funcs, 2 classes)
- **class LintSuggestion** (line 41, 0 methods) — A single golint style suggestion.
- **class GolintParser** (line 59, 6 methods) — Parser for golint output (deprecated linter).
- `def _infer_rule(message)` L51 — 

#### `code_parsers/go_parsers/go_parsers_gosec.py` (319 LOC, 0 funcs, 5 classes)
- **class VulnerabilityType** (line 23, 0 methods) — Security vulnerability types detected by gosec.
- **class SecurityIssue** (line 40, 0 methods) — Represents a security issue found by gosec.
- **class GosecStats** (line 56, 0 methods) — gosec scan statistics.
- **class GosecConfig** (line 66, 0 methods) — Gosec configuration for analysis.
- **class GosecParser** (line 119, 11 methods) — Parser for Gosec Go security vulnerability detection.

#### `code_parsers/go_parsers/go_parsers_govet.py` (167 LOC, 1 funcs, 2 classes)
- **class VetIssue** (line 30, 0 methods) — A single go vet diagnostic.
- **class GovetParser** (line 58, 7 methods) — Parser for go vet static analysis output.
- `def _infer_analyzer(message)` L40 — Guess the vet analyzer from the diagnostic message.

#### `code_parsers/go_parsers/go_parsers_staticcheck.py` (211 LOC, 1 funcs, 4 classes)
- **class CheckCategory** (line 29, 0 methods) — Staticcheck check category prefixes.
- **class StaticcheckLocation** (line 48, 0 methods) — File location referenced in a staticcheck finding.
- **class StaticcheckFinding** (line 57, 0 methods) — A single staticcheck finding from JSONL output.
- **class StaticcheckParser** (line 69, 8 methods) — Parser for staticcheck analysis output.
- `def _categorize_code(code)` L39 — Return the CheckCategory for a check code like 'SA1006', 'S1000'.

#### `code_parsers/interface.py` (55 LOC, 0 funcs, 3 classes)
- **class Language** (line 9, 0 methods) — Supported programming languages.
- **class ParseResult** (line 29, 0 methods) — Result of code parsing.
- **class IParser** (line 39, 3 methods) — Interface for language-specific parsers.

#### `code_parsers/java_parsers/__init__.py` (173 LOC, 0 funcs, 1 classes)
- **class JavaParserRegistry** (line 139, 1 methods) — Registry for Java static-analysis tool parsers.

#### `code_parsers/java_parsers/java_parser_treesitter.py` (1107 LOC, 0 funcs, 15 classes)
- **class JavaAnnotation** (line 37, 0 methods) — Represents a Java annotation.
- **class JavaField** (line 46, 0 methods) — Represents a Java field declaration.
- **class JavaParameter** (line 59, 0 methods) — Represents a method parameter.
- **class JavaMethod** (line 69, 0 methods) — Represents a Java method declaration.
- **class JavaEnumConstant** (line 89, 0 methods) — Represents an enum constant.
- **class JavaEnum** (line 98, 0 methods) — Represents a Java enum declaration.
- **class JavaInterface** (line 111, 0 methods) — Represents a Java interface declaration.
- **class JavaStaticInitializer** (line 124, 0 methods) — Represents a static initializer block.
- **class JavaRecordComponent** (line 133, 0 methods) — Represents a record component (parameter in record declaration).
- **class JavaRecord** (line 142, 0 methods) — Represents a Java record declaration (Java 14+).
- **class JavaModuleDirective** (line 157, 0 methods) — Represents a directive in a module declaration.
- **class JavaModule** (line 172, 0 methods) — Represents a Java module declaration (module-info.java).
- **class JavaClass** (line 183, 0 methods) — Represents a Java class declaration.
- **class JavaParseResult** (line 211, 0 methods) — Complete parse result for a Java file.
- **class JavaParser** (line 233, 29 methods) — Tree-sitter based Java parser for comprehensive structural analysis.

#### `code_parsers/java_parsers/java_parsers_Checkstyle.py` (162 LOC, 0 funcs, 2 classes)
- **class CheckstyleViolation** (line 22, 0 methods) — Represents a single Checkstyle violation.
- **class CheckstyleParser** (line 33, 6 methods) — Parser for Checkstyle Java code style analysis.

#### `code_parsers/java_parsers/java_parsers_DependencyCheck.py` (207 LOC, 1 funcs, 2 classes)
- **class CVEFinding** (line 22, 0 methods) — CVE finding from OWASP Dependency-Check.
- **class DependencyCheckParser** (line 44, 10 methods) — Parser for OWASP Dependency-Check JSON and XML reports.
- `def _cvss_to_severity(score)` L33 — Map a CVSS score to a severity label.

#### `code_parsers/java_parsers/java_parsers_ErrorProne.py` (154 LOC, 0 funcs, 2 classes)
- **class ErrorProneIssue** (line 21, 0 methods) — Represents an Error Prone finding.
- **class ErrorProneParser** (line 33, 5 methods) — Parser for Error Prone Java static analysis.

#### `code_parsers/java_parsers/java_parsers_FindSecBugs.py` (163 LOC, 0 funcs, 2 classes)
- **class SecurityBug** (line 21, 0 methods) — Represents a security vulnerability found by Find Security Bugs.
- **class FindSecBugsParser** (line 35, 5 methods) — Parser for Find Security Bugs security analysis.

#### `code_parsers/java_parsers/java_parsers_Gradle.py` (196 LOC, 0 funcs, 3 classes)
- **class GradleDependency** (line 32, 0 methods) — Gradle dependency entry.
- **class GradleCompileError** (line 42, 0 methods) — A compile error from Gradle build output.
- **class GradleParser** (line 52, 7 methods) — Parser for Gradle build configuration and dependency graphs.

#### `code_parsers/java_parsers/java_parsers_Infer.py` (171 LOC, 0 funcs, 2 classes)
- **class InferIssue** (line 21, 0 methods) — Represents an issue found by Facebook Infer.
- **class InferParser** (line 34, 6 methods) — Parser for Facebook Infer static analysis.

#### `code_parsers/java_parsers/java_parsers_JArchitect.py` (174 LOC, 0 funcs, 4 classes)
- **class QualityMetric** (line 18, 0 methods) — Code quality metric from JArchitect.
- **class DependencyIssue** (line 28, 0 methods) — Dependency or architecture issue from JArchitect.
- **class JArchitectReport** (line 39, 0 methods) — Full JArchitect analysis report.
- **class JArchitectParser** (line 51, 5 methods) — Parser for JArchitect Java architecture analysis.

#### `code_parsers/java_parsers/java_parsers_JaCoCo.py` (206 LOC, 1 funcs, 3 classes)
- **class CoverageMetrics** (line 22, 3 methods) — Code coverage metrics from JaCoCo.
- **class ClassCoverage** (line 51, 0 methods) — Coverage data for a single class.
- **class JaCoCoParser** (line 78, 8 methods) — Parser for JaCoCo code coverage XML reports.
- `def _parse_counters(elem)` L60 — Extract coverage counters from a JaCoCo XML element.

#### `code_parsers/java_parsers/java_parsers_Maven.py` (234 LOC, 1 funcs, 4 classes)
- **class MavenDependency** (line 25, 0 methods) — Maven dependency entry.
- **class MavenPlugin** (line 35, 0 methods) — Maven plugin entry.
- **class CompileError** (line 44, 0 methods) — A compile error extracted from Maven build output.
- **class MavenParser** (line 65, 11 methods) — Parser for Maven POM files and build output.
- `def _strip_ns(tag)` L59 — 

#### `code_parsers/java_parsers/java_parsers_PMD.py` (219 LOC, 0 funcs, 2 classes)
- **class PMDViolation** (line 19, 0 methods) — Represents a PMD rule violation.
- **class PMDParser** (line 34, 8 methods) — Parser for PMD Java static analysis.

#### `code_parsers/java_parsers/java_parsers_Pitest.py` (191 LOC, 1 funcs, 2 classes)
- **class MutationResult** (line 21, 0 methods) — Result from a single PIT mutation test.
- **class PitestParser** (line 41, 8 methods) — Parser for Pitest mutation testing XML reports.
- `def _short_mutator(full_name)` L34 — Extract the short mutator name from a fully-qualified class name.

#### `code_parsers/java_parsers/java_parsers_Semgrep.py` (168 LOC, 0 funcs, 2 classes)
- **class SemgrepFinding** (line 22, 0 methods) — Finding from Semgrep analysis.
- **class SemgrepParser** (line 34, 8 methods) — Parser for Semgrep ``--json`` output.

#### `code_parsers/java_parsers/java_parsers_SonarQube.py` (252 LOC, 0 funcs, 3 classes)
- **class SonarIssue** (line 20, 0 methods) — Represents a SonarQube issue.
- **class SonarMetrics** (line 36, 0 methods) — SonarQube project metrics.
- **class SonarQubeParser** (line 50, 8 methods) — Parser for SonarQube Java code quality analysis.

#### `code_parsers/java_parsers/java_parsers_SpotBugs.py` (249 LOC, 0 funcs, 2 classes)
- **class SpotBug** (line 19, 0 methods) — Represents a SpotBugs finding.
- **class SpotBugsParser** (line 34, 8 methods) — Parser for SpotBugs Java static analysis.

#### `code_parsers/java_parsers/java_parsers_javalang.py` (1679 LOC, 0 funcs, 10 classes)
- **class MethodCallInfo** (line 43, 0 methods) — Information about a method call.
- **class MethodMetrics** (line 54, 0 methods) — Comprehensive metrics for a single method.
- **class HalsteadMetrics** (line 71, 8 methods) — Halstead complexity metrics.
- **class TypeHierarchy** (line 127, 0 methods) — Represents a class/interface in the type hierarchy.
- **class DesignPatternMatch** (line 139, 0 methods) — Represents a detected design pattern.
- **class TryCatchPattern** (line 149, 0 methods) — Information about try-catch-finally usage.
- **class ThreadSafetyInfo** (line 160, 0 methods) — Thread safety analysis results.
- **class SecurityIssue** (line 170, 0 methods) — Security vulnerability detection.
- **class CodeMetrics** (line 180, 0 methods) — Comprehensive code metrics for a Java file.
- **class JavaParser** (line 218, 45 methods) — JavaParser is responsible for parsing and analyzing Java code.

#### `code_parsers/javascript_parsers/__init__.py` (339 LOC, 0 funcs, 1 classes)
- **class JavaScriptParserRegistry** (line 303, 1 methods) — Registry for JavaScript/TypeScript static-analysis tool parsers.

#### `code_parsers/javascript_parsers/javascript_parsers_babel.py` (672 LOC, 0 funcs, 11 classes)
- **class ECMAScriptVersion** (line 43, 0 methods) — ECMAScript versions.
- **class ProposalStage** (line 60, 0 methods) — TC39 proposal stages.
- **class BabelPlugin** (line 71, 0 methods) — A Babel plugin configuration.
- **class BabelPreset** (line 81, 0 methods) — A Babel preset configuration.
- **class BabelConfig** (line 90, 0 methods) — Babel configuration.
- **class SyntaxFeature** (line 104, 0 methods) — A JavaScript syntax feature detected in code.
- **class TransformationResult** (line 117, 0 methods) — Result of Babel transformation.
- **class JSXElement** (line 131, 0 methods) — A JSX element in the code.
- **class ModernJSSyntax** (line 145, 0 methods) — Modern JavaScript syntax usage analysis.
- **class BabelAnalysis** (line 166, 0 methods) — Complete Babel analysis results.
- **class BabelParser** (line 178, 13 methods) — Parser using Babel for modern JavaScript analysis.

#### `code_parsers/javascript_parsers/javascript_parsers_code_quality.py` (1025 LOC, 0 funcs, 11 classes)
- **class CodeSmellType** (line 46, 0 methods) — Types of code smells detected.
- **class CodeSmellSeverity** (line 75, 0 methods) — Severity levels for code smells.
- **class FrameworkType** (line 85, 0 methods) — Detected JavaScript frameworks.
- **class ModuleType** (line 108, 0 methods) — JavaScript module system type.
- **class CodeSmell** (line 120, 0 methods) — Represents a detected code smell.
- **class TodoComment** (line 136, 0 methods) — 
- **class DuplicateCodeBlock** (line 146, 0 methods) — Represents a detected duplicate code block.
- **class FrameworkDetection** (line 157, 0 methods) — Framework detection result.
- **class ModuleAnalysis** (line 167, 0 methods) — Module system analysis result.
- **class CodeQualityResult** (line 179, 0 methods) — Comprehensive code quality analysis result.
- **class CodeQualityAnalyzer** (line 197, 22 methods) — Comprehensive JavaScript code quality analyzer.

#### `code_parsers/javascript_parsers/javascript_parsers_eslint.py` (652 LOC, 0 funcs, 7 classes)
- **class ESLintSeverity** (line 48, 0 methods) — ESLint severity levels.
- **class ESLintDirectiveType** (line 56, 0 methods) — Types of ESLint inline directives.
- **class ESLintDirective** (line 69, 0 methods) — Represents an ESLint inline directive (comment).
- **class ESLintViolation** (line 80, 2 methods) — Represents a single ESLint rule violation.
- **class ESLintFileResult** (line 127, 2 methods) — ESLint results for a single file.
- **class ESLintConfig** (line 159, 0 methods) — ESLint configuration representation.
- **class ESLintParser** (line 173, 16 methods) — Parser for ESLint output and configuration files.

#### `code_parsers/javascript_parsers/javascript_parsers_esprima.py` (1434 LOC, 0 funcs, 12 classes)
- **class SecuritySeverity** (line 69, 0 methods) — Security issue severity levels.
- **class DesignPatternType** (line 79, 0 methods) — Common JavaScript design patterns.
- **class FunctionInfo** (line 96, 0 methods) — Information about a JavaScript function.
- **class FunctionCallInfo** (line 116, 0 methods) — Information about a function call.
- **class HalsteadMetrics** (line 130, 8 methods) — Halstead software complexity metrics.
- **class ScopeInfo** (line 190, 0 methods) — Information about a JavaScript scope.
- **class SecurityIssue** (line 204, 0 methods) — Security vulnerability or issue.
- **class DesignPatternMatch** (line 219, 0 methods) — Detected design pattern.
- **class ImportInfo** (line 230, 0 methods) — ES6 module import information.
- **class ExportInfo** (line 242, 0 methods) — ES6 module export information.
- **class CodeMetrics** (line 254, 0 methods) — Comprehensive code metrics.
- **class JavaScriptParser** (line 272, 31 methods) — JavaScriptParser is responsible for parsing and analyzing JavaScript code.

#### `code_parsers/javascript_parsers/javascript_parsers_flow.py` (688 LOC, 0 funcs, 12 classes)
- **class FlowSeverity** (line 55, 0 methods) — Flow error severity levels.
- **class FlowTypeKind** (line 62, 0 methods) — Flow type kinds.
- **class Variance** (line 83, 0 methods) — Type parameter variance.
- **class FlowTypeAnnotation** (line 92, 0 methods) — A Flow type annotation.
- **class FlowTypeParameter** (line 105, 0 methods) — A generic type parameter in Flow.
- **class FlowTypeAlias** (line 116, 0 methods) — A Flow type alias (type X = ...).
- **class FlowInterface** (line 130, 0 methods) — A Flow interface declaration.
- **class FlowError** (line 146, 0 methods) — A Flow type error.
- **class FlowCoverage** (line 161, 2 methods) — Flow type coverage information.
- **class FlowConfig** (line 180, 0 methods) — Flow configuration from .flowconfig.
- **class FlowAnalysis** (line 194, 0 methods) — Complete Flow analysis results.
- **class FlowParser** (line 212, 16 methods) — Parser for Flow type checker integration.

#### `code_parsers/javascript_parsers/javascript_parsers_jsdoc.py` (243 LOC, 0 funcs, 2 classes)
- **class JsDocComment** (line 37, 0 methods) — Parsed JSDoc comment block.
- **class JsDocParser** (line 47, 6 methods) — Pure-Python JSDoc comment extractor and coverage analyser.

#### `code_parsers/javascript_parsers/javascript_parsers_jshint.py` (408 LOC, 0 funcs, 5 classes)
- **class JSHintSeverity** (line 49, 0 methods) — JSHint severity levels.
- **class JSHintError** (line 58, 2 methods) — Represents a single JSHint error or warning.
- **class JSHintFileResult** (line 84, 3 methods) — JSHint results for a single file.
- **class JSHintConfig** (line 107, 0 methods) — JSHint configuration representation.
- **class JSHintParser** (line 185, 9 methods) — Parser for JSHint output and configuration files.

#### `code_parsers/javascript_parsers/javascript_parsers_npm_audit.py` (193 LOC, 0 funcs, 2 classes)
- **class NpmAuditFinding** (line 22, 0 methods) — Parsed finding from npm audit --json output.
- **class NpmAuditParser** (line 34, 6 methods) — Parser for npm audit --json vulnerability reports.

#### `code_parsers/javascript_parsers/javascript_parsers_package_json.py` (190 LOC, 0 funcs, 2 classes)
- **class PackageInfo** (line 45, 0 methods) — Structured representation of a package.json file.
- **class PackageJsonParser** (line 61, 8 methods) — Parser for package.json configuration files.

#### `code_parsers/javascript_parsers/javascript_parsers_prettier.py` (503 LOC, 0 funcs, 10 classes)
- **class PrettierParser** (line 51, 0 methods) — Prettier parser options.
- **class EndOfLine** (line 74, 0 methods) — End of line options.
- **class QuoteType** (line 83, 0 methods) — Quote type options.
- **class TrailingComma** (line 90, 0 methods) — Trailing comma options.
- **class ProseWrap** (line 98, 0 methods) — Prose wrap options for Markdown.
- **class HTMLWhitespaceSensitivity** (line 106, 0 methods) — HTML whitespace sensitivity.
- **class PrettierConfig** (line 115, 0 methods) — Prettier configuration representation.
- **class FormatDiff** (line 174, 1 methods) — Represents formatting differences.
- **class FormatResult** (line 193, 0 methods) — Result of formatting a file.
- **class PrettierFormatter** (line 205, 9 methods) — Parser for Prettier output and configuration files.

#### `code_parsers/javascript_parsers/javascript_parsers_standard.py` (367 LOC, 0 funcs, 5 classes)
- **class StandardSeverity** (line 51, 0 methods) — StandardJS severity levels (mirrors ESLint).
- **class StandardViolation** (line 59, 2 methods) — Represents a single StandardJS style violation.
- **class StandardFileResult** (line 84, 4 methods) — StandardJS results for a single file.
- **class StandardConfig** (line 112, 0 methods) — StandardJS configuration options.
- **class StandardJSParser** (line 136, 10 methods) — Parser for StandardJS output and execution.

#### `code_parsers/javascript_parsers/javascript_parsers_test_detection.py` (175 LOC, 0 funcs, 2 classes)
- **class TestDetectionResult** (line 61, 0 methods) — Result of test framework detection and file discovery.
- **class TestDetectionParser** (line 71, 5 methods) — Detect JavaScript test frameworks and enumerate test files.

#### `code_parsers/javascript_parsers/javascript_parsers_treesitter.py` (939 LOC, 1 funcs, 9 classes)
- **class JSLanguageVariant** (line 79, 0 methods) — JavaScript language variants supported by tree-sitter.
- **class TreeSitterNode** (line 89, 11 methods) — Wrapper for tree-sitter node with convenient accessors.
- **class SyntaxError** (line 162, 0 methods) — Represents a syntax error in the parsed code.
- **class JSSymbol** (line 174, 0 methods) — A JavaScript/TypeScript symbol (function, class, variable, etc.).
- **class JSXComponent** (line 196, 0 methods) — A JSX/TSX component usage.
- **class ImportStatement** (line 208, 0 methods) — An import statement.
- **class ExportStatement** (line 223, 0 methods) — An export statement.
- **class TreeSitterParseResult** (line 234, 0 methods) — Result of parsing with tree-sitter.
- **class TreeSitterJSParser** (line 248, 23 methods) — Fast JavaScript/TypeScript parser using tree-sitter.
- `def _set_parser_language(parser, language)` L71 — [20260122_BUGFIX] Support tree-sitter >=0.24 which dropped set_language().

#### `code_parsers/javascript_parsers/javascript_parsers_typescript.py` (815 LOC, 0 funcs, 17 classes)
- **class TypeKind** (line 63, 0 methods) — TypeScript type kinds.
- **class DecoratorKind** (line 85, 0 methods) — Common decorator categories.
- **class TypeAnnotation** (line 96, 0 methods) — A TypeScript type annotation.
- **class TypeParameter** (line 111, 0 methods) — A generic type parameter.
- **class InterfaceDeclaration** (line 121, 0 methods) — A TypeScript interface declaration.
- **class TypeAliasDeclaration** (line 138, 0 methods) — A TypeScript type alias (type X = ...).
- **class PropertySignature** (line 152, 0 methods) — A property in an interface or type.
- **class MethodSignature** (line 163, 0 methods) — A method signature in an interface.
- **class IndexSignature** (line 175, 0 methods) — An index signature [key: KeyType]: ValueType.
- **class ParameterDeclaration** (line 186, 0 methods) — A function/method parameter.
- **class EnumDeclaration** (line 198, 0 methods) — A TypeScript enum declaration.
- **class EnumMember** (line 210, 0 methods) — An enum member.
- **class DecoratorUsage** (line 220, 0 methods) — A decorator usage (@Decorator).
- **class NamespaceDeclaration** (line 232, 0 methods) — A TypeScript namespace/module declaration.
- **class TypeGuard** (line 246, 0 methods) — A type guard function/expression.
- **class TypeScriptAnalysis** (line 257, 0 methods) — Complete TypeScript analysis results.
- **class TypeScriptParser** (line 272, 17 methods) — Parser for TypeScript-specific features.

#### `code_parsers/javascript_parsers/javascript_parsers_webpack.py` (256 LOC, 0 funcs, 2 classes)
- **class WebpackConfig** (line 69, 0 methods) — Extracted information from a webpack configuration file.
- **class WebpackConfigParser** (line 81, 9 methods) — Heuristic static analyser for webpack.config.js / webpack.config.ts.

#### `code_parsers/kotlin_parsers/__init__.py` (392 LOC, 1 funcs, 1 classes)
- **class KotlinParserRegistry** (line 307, 2 methods) — Registry for Kotlin static-analysis tool parsers.
- `def __getattr__(name)` L175 — Lazy load parser classes on first access.

#### `code_parsers/kotlin_parsers/kotlin_parsers_Detekt.py` (569 LOC, 0 funcs, 6 classes)
- **class DetektSeverity** (line 27, 0 methods) — Detekt finding severity levels.
- **class DetektRuleSet** (line 36, 0 methods) — Detekt rule set categories.
- **class DetektFinding** (line 52, 2 methods) — Represents a single Detekt finding.
- **class DetektConfig** (line 79, 0 methods) — Detekt configuration representation.
- **class DetektReport** (line 103, 5 methods) — Complete Detekt analysis report.
- **class DetektParser** (line 146, 15 methods) — Parser for Detekt static analysis output.

#### `code_parsers/kotlin_parsers/kotlin_parsers_Konsist.py` (174 LOC, 0 funcs, 5 classes)
- **class KonsistSeverity** (line 16, 0 methods) — 
- **class KonsistRuleType** (line 22, 0 methods) — 
- **class KonsistViolation** (line 34, 0 methods) — 
- **class KonsistRule** (line 45, 0 methods) — 
- **class KonsistParser** (line 53, 6 methods) — Parser for Konsist architecture violations.

#### `code_parsers/kotlin_parsers/kotlin_parsers_compose.py` (216 LOC, 0 funcs, 5 classes)
- **class ComposeIssueType** (line 16, 0 methods) — 
- **class ComposeSeverity** (line 27, 0 methods) — 
- **class ComposeIssue** (line 35, 0 methods) — 
- **class ComposeMetrics** (line 47, 0 methods) — 
- **class ComposeLinterParser** (line 58, 6 methods) — Parser for Jetpack Compose compiler output and lint reports.

#### `code_parsers/kotlin_parsers/kotlin_parsers_diktat.py` (216 LOC, 1 funcs, 5 classes)
- **class DiktatSeverity** (line 16, 0 methods) — 
- **class DiktatRuleSet** (line 22, 0 methods) — 
- **class DiktatViolation** (line 32, 0 methods) — 
- **class DiktatConfig** (line 44, 0 methods) — 
- **class DiktatParser** (line 66, 8 methods) — Parser for diktat style and quality violations.
- `def _infer_rule_set(rule_id)` L61 — 

#### `code_parsers/kotlin_parsers/kotlin_parsers_gradle.py` (269 LOC, 0 funcs, 6 classes)
- **class ConfigurationType** (line 15, 0 methods) — 
- **class PluginType** (line 25, 0 methods) — 
- **class Dependency** (line 38, 1 methods) — 
- **class GradlePlugin** (line 51, 0 methods) — 
- **class BuildConfiguration** (line 58, 0 methods) — 
- **class GradleBuildParser** (line 96, 8 methods) — Parser for Gradle build files (build.gradle / build.gradle.kts).

#### `code_parsers/kotlin_parsers/kotlin_parsers_ktlint.py` (581 LOC, 0 funcs, 6 classes)
- **class KtlintSeverity** (line 27, 0 methods) — ktlint violation severity levels.
- **class KtlintRuleSet** (line 34, 0 methods) — ktlint rule set categories.
- **class KtlintViolation** (line 43, 3 methods) — Represents a single ktlint violation.
- **class KtlintConfig** (line 77, 0 methods) — ktlint configuration from .editorconfig.
- **class KtlintReport** (line 104, 6 methods) — Complete ktlint analysis report.
- **class KtlintParser** (line 153, 19 methods) — Parser for ktlint linter output.

#### `code_parsers/kotlin_parsers/kotlin_parsers_test.py` (307 LOC, 0 funcs, 6 classes)
- **class TestStatus** (line 15, 0 methods) — 
- **class TestFramework** (line 23, 0 methods) — 
- **class TestCase** (line 33, 0 methods) — 
- **class TestSuite** (line 45, 0 methods) — 
- **class CoverageMetrics** (line 58, 0 methods) — 
- **class KotlinTestParser** (line 69, 8 methods) — Parser for Kotlin test results (JUnit XML, Kotest JSON, JaCoCo XML).

#### `code_parsers/language_detection.py` (416 LOC, 8 funcs, 1 classes)
- **class Language** (line 21, 0 methods) — Supported programming languages.
- `def detect_language(filepath, code)` L201 — Detect the programming language from file path and/or content.
- `def _detect_from_extension(filepath)` L252 — Detect language from file extension.
- `def _detect_from_shebang(code)` L266 — Detect language from shebang line.
- `def _detect_from_content(code)` L280 — Detect language from content patterns.
- `def get_language_name(lang)` L307 — Get human-readable language name.
- `def get_file_extensions(lang)` L337 — Get list of file extensions for a language.
- `def is_parseable_language(lang)` L343 — Check if we have a parser available for this language.
- `def detect_language_confidence(filepath, code)` L355 — Detect language with confidence score.

#### `code_parsers/php_parsers/__init__.py` (280 LOC, 1 funcs, 1 classes)
- **class PHPParserRegistry** (line 246, 1 methods) — Registry for PHP static-analysis tool parsers.
- `def __getattr__(name)` L161 — Lazy load parser classes on first access.

#### `code_parsers/php_parsers/php_parsers_PHPCS.py` (274 LOC, 1 funcs, 5 classes)
- **class PHPCSSeverity** (line 36, 0 methods) — PHPCS violation severity levels.
- **class PHPCSStandard** (line 43, 0 methods) — Popular PHPCS coding standards.
- **class PHPCSViolation** (line 56, 0 methods) — Represents a single PHPCS code standard violation.
- **class PHPCSConfig** (line 69, 0 methods) — PHPCS configuration settings.
- **class PHPCSParser** (line 79, 9 methods) — Parser for PHP Code Sniffer violations.
- `def _find_phpcs()` L29 — 

#### `code_parsers/php_parsers/php_parsers_PHPStan.py` (323 LOC, 3 funcs, 5 classes)
- **class PHPStanLevel** (line 71, 0 methods) — PHPStan analysis levels (0=most lenient, 8=strictest).
- **class PHPStanErrorType** (line 85, 0 methods) — PHPStan error type categories.
- **class PHPStanError** (line 99, 0 methods) — Represents a single PHPStan analysis error.
- **class PHPStanConfig** (line 115, 0 methods) — PHPStan configuration settings.
- **class PHPStanParser** (line 125, 9 methods) — Parser for PHPStan static analysis results.
- `def _find_phpstan()` L41 — 
- `def _infer_error_type(message)` L48 — 
- `def _infer_cwe(message)` L63 — 

#### `code_parsers/php_parsers/php_parsers_Psalm.py` (318 LOC, 3 funcs, 5 classes)
- **class PsalmSeverity** (line 52, 0 methods) — Psalm error severity levels.
- **class PsalmErrorType** (line 60, 0 methods) — Psalm error type categories.
- **class PsalmError** (line 73, 0 methods) — Represents a single Psalm analysis error.
- **class PsalmConfig** (line 91, 0 methods) — Psalm configuration settings.
- **class PsalmParser** (line 125, 9 methods) — Parser for Psalm static analysis results.
- `def _find_psalm()` L45 — 
- `def _infer_error_type(psalm_type)` L102 — Infer our PsalmErrorType from Psalm's issue type string.
- `def _infer_cwe(psalm_type)` L118 — 

#### `code_parsers/php_parsers/php_parsers_ast.py` (291 LOC, 0 funcs, 3 classes)
- **class PHPClass** (line 21, 0 methods) — Represents a PHP class definition.
- **class PHPFunction** (line 37, 0 methods) — Represents a PHP function definition.
- **class PHPParserAST** (line 48, 9 methods) — PHP structure analyser using internal PHPNormalizer.

#### `code_parsers/php_parsers/php_parsers_composer.py` (269 LOC, 1 funcs, 3 classes)
- **class ComposerPackage** (line 23, 0 methods) — Represents a Composer package dependency.
- **class ComposerConfig** (line 35, 0 methods) — Composer project configuration.
- **class ComposerParser** (line 56, 8 methods) — Parser for Composer dependency management files.
- `def _extract_package(name, constraint, is_dev)` L46 — Build a ComposerPackage from name + version constraint.

#### `code_parsers/php_parsers/php_parsers_exakat.py` (270 LOC, 1 funcs, 3 classes)
- **class ExakatCategory** (line 40, 0 methods) — Exakat analysis categories.
- **class ExakatIssue** (line 52, 0 methods) — Represents a single Exakat analysis issue.
- **class ExakatParser** (line 75, 8 methods) — Parser for Exakat comprehensive PHP analysis output.
- `def _infer_cwe(category, title)` L68 — 

#### `code_parsers/php_parsers/php_parsers_phpmd.py` (296 LOC, 2 funcs, 5 classes)
- **class PHPMDPriority** (line 48, 0 methods) — PHPMD violation priority levels (1=critical, 5=minor).
- **class PHPMDRuleType** (line 58, 0 methods) — PHPMD rule type categories.
- **class PHPMDViolation** (line 70, 0 methods) — Represents a single PHPMD code violation.
- **class PHPMDConfig** (line 86, 0 methods) — PHPMD configuration settings.
- **class PHPMDParser** (line 111, 9 methods) — Parser for PHP Mess Detector violations.
- `def _find_phpmd()` L41 — 
- `def _infer_cwe(rule)` L104 — 

#### `code_parsers/python_parser.py` (67 LOC, 0 funcs, 1 classes)
- **class PythonParser** (line 9, 4 methods) — Python implementation of the parser interface.

#### `code_parsers/python_parsers/__init__.py` (503 LOC, 3 funcs, 1 classes)
- **class PythonParserRegistry** (line 464, 1 methods) — Registry for Python static-analysis tool parsers.
- `def __getattr__(name)` L84 — Lazy load parser classes on first access.
- `def get_available_parsers()` L344 — Get list of all available parsers (completed and planned).
- `def get_parser_info()` L372 — Get information about each available parser.

#### `code_parsers/python_parsers/python_parsers_ast.py` (4047 LOC, 3 funcs, 29 classes)
- **class SymbolKind** (line 435, 0 methods) — Kind of symbol in the symbol table.
- **class ScopeType** (line 454, 0 methods) — Type of scope in Python.
- **class NameContext** (line 465, 0 methods) — Context in which a name is used.
- **class SourceLocation** (line 480, 1 methods) — Location in source code.
- **class TypeAnnotation** (line 500, 8 methods) — Represents a type annotation.
- **class PythonSymbol** (line 740, 0 methods) — Represents a symbol in Python code.
- **class PythonParameter** (line 759, 0 methods) — Represents a function parameter.
- **class PythonFunction** (line 776, 1 methods) — Represents a function or method.
- **class PythonClass** (line 803, 1 methods) — Represents a class definition.
- **class PythonImport** (line 823, 1 methods) — Represents an import statement.
- **class PythonModule** (line 846, 0 methods) — Represents a parsed Python module.
- **class PythonScope** (line 875, 0 methods) — Represents a scope in Python code.
- **class NameReference** (line 896, 0 methods) — Represents a reference to a name.
- **class BasicBlock** (line 915, 2 methods) — Represents a basic block in a CFG.
- **class ControlFlowGraph** (line 940, 4 methods) — Control flow graph for a function.
- **class CallSite** (line 1084, 0 methods) — Represents a function call site.
- **class CallGraph** (line 1099, 4 methods) — Call graph for a module or set of modules.
- **class Definition** (line 1149, 2 methods) — Represents a variable definition.
- **class Expression** (line 1169, 2 methods) — Represents an expression for available/busy expression analysis.
- **class ConstantValue** (line 1191, 10 methods) — Represents a constant value or non-constant state.
- **class DataFlowInfo** (line 1275, 0 methods) — Data flow analysis results.
- **class PythonASTParser** (line 1305, 14 methods) — Comprehensive Python AST parser and analyzer.
- **class ParentTrackingVisitor** (line 1680, 5 methods) — Base visitor that tracks parent-child relationships in AST.
- **class SymbolVisitor** (line 1727, 14 methods) — Visitor for extracting symbols from AST.
- **class ScopeAnalyzer** (line 2155, 30 methods) — Visitor for analyzing scopes.
- **class NameResolver** (line 2423, 10 methods) — Visitor for resolving names to their definitions.
- **class CallGraphBuilder** (line 2591, 11 methods) — Visitor for building call graphs from AST.
- **class CFGBuilder** (line 2837, 17 methods) — Builder for Control Flow Graphs from Python AST.
- **class DataFlowAnalyzer** (line 3320, 21 methods) — Data flow analyzer for control flow graphs.
- `def get_qualified_name(node, parents)` L4024 — Get the qualified name for a node based on its parent chain.
- `def is_dunder(name)` L4040 — Check if a name is a dunder (double underscore) name.
- `def is_private(name)` L4045 — Check if a name is private (starts with underscore).

#### `code_parsers/python_parsers/python_parsers_bandit.py` (1647 LOC, 2 funcs, 10 classes)
- **class BanditSeverity** (line 41, 1 methods) — Severity levels for Bandit issues.
- **class BanditConfidence** (line 56, 1 methods) — Confidence levels for Bandit issues.
- **class BanditCategory** (line 71, 0 methods) — Categories of Bandit security checks.
- **class CWEInfo** (line 88, 1 methods) — Common Weakness Enumeration information.
- **class OWASPCategory** (line 323, 0 methods) — OWASP Top 10 2021 Categories.
- **class BanditIssue** (line 732, 5 methods) — A single Bandit security issue.
- **class BanditFileMetrics** (line 818, 1 methods) — Metrics for a single file.
- **class BanditConfig** (line 848, 1 methods) — Configuration for Bandit analysis.
- **class BanditReport** (line 902, 10 methods) — Complete Bandit security analysis report.
- **class BanditParser** (line 999, 18 methods) — Parser for Bandit security scanner output.
- `def parse_bandit_json(output)` L1579 — Parse Bandit JSON output into a report.
- `def format_security_report(report)` L1610 — Format a Bandit security report for display.

#### `code_parsers/python_parsers/python_parsers_code_quality.py` (1454 LOC, 1 funcs, 13 classes)
- **class SmellSeverity** (line 159, 0 methods) — Severity of code smells.
- **class SmellCategory** (line 168, 0 methods) — Categories of code smells.
- **class CodeQualityThresholds** (line 185, 0 methods) — Thresholds for code quality checks.
- **class LineMetrics** (line 212, 2 methods) — Line count metrics for code.
- **class HalsteadMetrics** (line 236, 7 methods) — Halstead software metrics.
- **class ComplexityMetrics** (line 285, 1 methods) — Complexity metrics for a function or class.
- **class MaintainabilityMetrics** (line 303, 1 methods) — Maintainability metrics for code.
- **class CodeSmell** (line 333, 2 methods) — Represents a detected code smell.
- **class TechnicalDebt** (line 367, 2 methods) — Technical debt estimation.
- **class FunctionQualityInfo** (line 392, 0 methods) — Quality information for a function.
- **class ClassQualityInfo** (line 410, 0 methods) — Quality information for a class.
- **class CodeQualityReport** (line 428, 5 methods) — Complete code quality analysis report.
- **class PythonCodeQualityAnalyzer** (line 500, 18 methods) — Comprehensive code quality analyzer for Python code.
- `def format_quality_report(report)` L1416 — Format a code quality report for display.

#### `code_parsers/python_parsers/python_parsers_flake8.py` (1228 LOC, 5 funcs, 5 classes)
- **class Flake8Violation** (line 475, 7 methods) — A single Flake8 violation.
- **class Flake8PluginInfo** (line 544, 1 methods) — Information about an installed Flake8 plugin.
- **class Flake8Config** (line 565, 7 methods) — Configuration for Flake8 analysis.
- **class Flake8Report** (line 766, 7 methods) — Complete Flake8 analysis report.
- **class Flake8Parser** (line 839, 10 methods) — Parser for Flake8 linter output.
- `def get_code_message(code)` L432 — Get the detailed message for an error code.
- `def get_code_category(code)` L437 — Get the category for an error code.
- `def get_code_source(code)` L447 — Get the source tool for an error code.
- `def parse_flake8_output(output)` L1185 — Parse Flake8 text output into violations.
- `def format_flake8_report(report)` L1203 — Format a Flake8 report for display.

#### `code_parsers/python_parsers/python_parsers_interrogate.py` (523 LOC, 0 funcs, 6 classes)
- **class SourceLocation** (line 242, 0 methods) — Location in source code.
- **class DocumentedItem** (line 252, 1 methods) — Represents a potentially documentable item (function, class, method).
- **class DocumentationCoverage** (line 273, 2 methods) — Aggregated documentation coverage metrics.
- **class InterrogateConfig** (line 302, 1 methods) — Configuration for Interrogate parser.
- **class InterrogateReport** (line 318, 3 methods) — Results from Interrogate documentation coverage analysis.
- **class InterrogateParser** (line 351, 10 methods) — Parser for documentation coverage using Interrogate.

#### `code_parsers/python_parsers/python_parsers_isort.py` (391 LOC, 0 funcs, 6 classes)
- **class SourceLocation** (line 128, 0 methods) — Location in source code.
- **class ImportGroup** (line 138, 0 methods) — Represents a group of imports (future, stdlib, third-party, local).
- **class ImportIssue** (line 148, 0 methods) — Represents an import sorting issue.
- **class IsortConfig** (line 159, 2 methods) — Configuration for isort parser.
- **class IsortReport** (line 185, 0 methods) — Results from isort analysis.
- **class IsortParser** (line 196, 9 methods) — Parser for import organization using isort.

#### `code_parsers/python_parsers/python_parsers_mypy.py` (1472 LOC, 2 funcs, 8 classes)
- **class MypySeverity** (line 138, 0 methods) — Severity levels for mypy diagnostics.
- **class MypyErrorCategory** (line 146, 0 methods) — Categories of mypy errors.
- **class MypyError** (line 202, 5 methods) — A single mypy diagnostic.
- **class RevealedType** (line 325, 4 methods) — A revealed type from reveal_type() or reveal_locals().
- **class TypeCoverageInfo** (line 406, 4 methods) — Type coverage statistics.
- **class MypyConfig** (line 459, 7 methods) — Configuration for mypy analysis.
- **class MypyReport** (line 741, 6 methods) — Complete mypy analysis report.
- **class MypyParser** (line 815, 13 methods) — Parser for mypy static type checker output.
- `def parse_mypy_output(output)` L1412 — Parse mypy text output into errors.
- `def format_type_coverage(coverage)` L1444 — Format type coverage for display.

#### `code_parsers/python_parsers/python_parsers_prospector.py` (1089 LOC, 3 funcs, 11 classes)
- **class Strictness** (line 125, 0 methods) — Prospector strictness levels.
- **class ProspectorTool** (line 135, 0 methods) — Tools that Prospector can use.
- **class MessageSeverity** (line 151, 0 methods) — Unified message severity levels.
- **class ProspectorConfig** (line 168, 0 methods) — Configuration for Prospector execution.
- **class ProspectorProfile** (line 197, 1 methods) — Represents a loaded Prospector profile.
- **class ProspectorProfileLoader** (line 291, 4 methods) — Loader for Prospector profile files.
- **class MessageLocation** (line 511, 1 methods) — Location of a message in source code.
- **class ProspectorMessage** (line 531, 1 methods) — A message from Prospector.
- **class ProspectorSummary** (line 549, 0 methods) — Summary of Prospector analysis.
- **class ProspectorReport** (line 565, 12 methods) — Complete Prospector analysis report.
- **class ProspectorParser** (line 760, 9 methods) — Parser for Prospector output - meta-linter.
- `def merge_profiles()` L445 — Merge multiple profiles with later profiles taking priority.
- `def format_prospector_report(report)` L1007 — Format a Prospector report for display.
- `def create_profile(name, strictness, with_tools, without_tools)` L1061 — Create a Prospector profile configuration.

#### `code_parsers/python_parsers/python_parsers_pycodestyle.py` (599 LOC, 3 funcs, 6 classes)
- **class StyleCategory** (line 90, 0 methods) — Categories of pycodestyle error codes.
- **class StyleSeverity** (line 104, 0 methods) — Severity of style issues.
- **class PycodestyleConfig** (line 246, 0 methods) — Configuration for pycodestyle execution.
- **class StyleViolation** (line 265, 2 methods) — Represents a pycodestyle violation.
- **class PycodestyleReport** (line 288, 7 methods) — Complete pycodestyle analysis report.
- **class PycodestyleParser** (line 360, 8 methods) — Parser for pycodestyle output - PEP 8 style checker.
- `def get_category_for_code(code)` L116 — Get the category for an error code.
- `def format_pycodestyle_report(report)` L560 — Format a pycodestyle report for display.
- `def get_error_description(code)` L597 — Get the description for an error code.

#### `code_parsers/python_parsers/python_parsers_pydocstyle.py` (1435 LOC, 2 funcs, 13 classes)
- **class DocstyleConvention** (line 119, 0 methods) — Docstring conventions supported by pydocstyle.
- **class DocstyleCategory** (line 128, 0 methods) — Categories of pydocstyle error codes.
- **class DocstringSeverity** (line 137, 0 methods) — Severity of docstring issues.
- **class PydocstyleConfig** (line 258, 0 methods) — Configuration for pydocstyle execution.
- **class DocstyleViolation** (line 277, 2 methods) — Represents a pydocstyle violation.
- **class DocstringCoverage** (line 305, 6 methods) — Docstring coverage statistics.
- **class DocstringQualityIssueType** (line 366, 0 methods) — Types of docstring quality issues.
- **class DocstringQualityIssue** (line 381, 0 methods) — A specific quality issue in a docstring.
- **class FunctionDocstringQuality** (line 392, 5 methods) — Quality analysis results for a function's docstring.
- **class ModuleDocstringQuality** (line 495, 4 methods) — Aggregated quality analysis for a module.
- **class DocstringQualityAnalyzer** (line 530, 18 methods) — Analyzer for docstring quality beyond basic style checks.
- **class PydocstyleReport** (line 930, 5 methods) — Complete pydocstyle analysis report.
- **class PydocstyleParser** (line 987, 15 methods) — Parser for pydocstyle output - docstring style checker.
- `def format_pydocstyle_report(report)` L1383 — Format a pydocstyle report for display.
- `def get_error_description(code)` L1431 — Get the description for an error code.

#### `code_parsers/python_parsers/python_parsers_pylint.py` (1687 LOC, 6 funcs, 8 classes)
- **class PylintSeverity** (line 221, 0 methods) — Severity levels for Pylint messages.
- **class PylintConfidence** (line 232, 0 methods) — Confidence levels for Pylint messages.
- **class PylintChecker** (line 243, 0 methods) — Pylint checker categories.
- **class PylintMessage** (line 766, 4 methods) — A single Pylint diagnostic message.
- **class PylintStatistics** (line 833, 2 methods) — Pylint analysis statistics.
- **class PylintConfig** (line 862, 7 methods) — Configuration for Pylint analysis.
- **class PylintReport** (line 1166, 10 methods) — Complete Pylint analysis report.
- **class PylintParser** (line 1257, 10 methods) — Parser for Pylint static analyzer output.
- `def get_checker_for_message(message_id)` L738 — Get the checker that generates a specific message.
- `def is_message_enabled_by_default(message_id)` L743 — Check if a message is enabled by default.
- `def get_severity_from_id(message_id)` L748 — Get severity from message ID.
- `def get_symbol_from_id(message_id)` L755 — Get message symbol from message ID.
- `def parse_pylint_json2(output)` L1640 — Parse Pylint JSON2 format output.
- `def format_pylint_report(report)` L1665 — Format a Pylint report for display.

#### `code_parsers/python_parsers/python_parsers_radon.py` (565 LOC, 0 funcs, 7 classes)
- **class SourceLocation** (line 255, 0 methods) — Location in source code.
- **class ComplexityMetrics** (line 265, 2 methods) — Code complexity metrics for a function or class.
- **class FunctionComplexity** (line 295, 0 methods) — Complexity metrics for a function.
- **class ClassComplexity** (line 305, 1 methods) — Complexity metrics for a class.
- **class RadonConfig** (line 323, 1 methods) — Configuration for Radon parser.
- **class RadonReport** (line 337, 3 methods) — Results from Radon complexity analysis.
- **class RadonParser** (line 370, 10 methods) — Parser for code complexity metrics using Radon.

#### `code_parsers/python_parsers/python_parsers_ruff.py` (1191 LOC, 4 funcs, 9 classes)
- **class RuffSeverity** (line 221, 0 methods) — Severity level for Ruff violations.
- **class FixApplicability** (line 230, 0 methods) — How safe it is to apply a fix.
- **class SourceLocation** (line 328, 1 methods) — Location in source code.
- **class RuffEdit** (line 341, 1 methods) — A single edit operation for a fix.
- **class RuffFix** (line 359, 2 methods) — A fix suggestion with edits.
- **class RuffViolation** (line 383, 8 methods) — A single Ruff violation/diagnostic.
- **class RuffConfig** (line 450, 5 methods) — Configuration for Ruff analysis.
- **class RuffReport** (line 643, 6 methods) — Complete Ruff analysis report.
- **class RuffParser** (line 708, 12 methods) — Parser for Ruff linter output.
- `def get_rule_category(code)` L300 — Get the category description for a rule code.
- `def get_rule_severity(code)` L310 — Determine severity based on rule code.
- `def parse_ruff_json(output)` L1116 — Parse Ruff JSON output into violations.
- `def format_violations(violations)` L1133 — Format violations for display.

#### `code_parsers/python_parsers/python_parsers_safety.py` (321 LOC, 0 funcs, 6 classes)
- **class CVSSScore** (line 14, 1 methods) — CVSS (Common Vulnerability Scoring System) score.
- **class Vulnerability** (line 38, 1 methods) — Represents a security vulnerability.
- **class DependencyVulnerability** (line 63, 2 methods) — Represents a vulnerable dependency.
- **class SafetyConfig** (line 91, 1 methods) — Configuration for Safety parser.
- **class SafetyReport** (line 105, 3 methods) — Results from Safety vulnerability analysis.
- **class SafetyParser** (line 130, 8 methods) — Parser for dependency security vulnerabilities using Safety.

#### `code_parsers/python_parsers/python_parsers_vulture.py` (318 LOC, 0 funcs, 5 classes)
- **class SourceLocation** (line 29, 0 methods) — Location in source code.
- **class UnusedItem** (line 39, 0 methods) — Represents an unused code item.
- **class VultureConfig** (line 50, 2 methods) — Configuration for Vulture parser.
- **class VultureReport** (line 70, 1 methods) — Results from Vulture analysis.
- **class VultureParser** (line 97, 9 methods) — 

#### `code_parsers/ruby_parsers/__init__.py` (137 LOC, 0 funcs, 1 classes)
- **class RubyParserRegistry** (line 45, 4 methods) — Registry for Ruby parser implementations with factory pattern.

#### `code_parsers/ruby_parsers/ruby_parsers_Reek.py` (214 LOC, 0 funcs, 4 classes)
- **class SmellType** (line 23, 0 methods) — Reek code smell types.
- **class ReekSmell** (line 40, 0 methods) — Represents a code smell detected by Reek.
- **class ReekConfig** (line 53, 0 methods) — Reek configuration for analysis.
- **class ReekParser** (line 64, 9 methods) — Parser for Reek code smell detection.

#### `code_parsers/ruby_parsers/ruby_parsers_RuboCop.py` (244 LOC, 0 funcs, 4 classes)
- **class RuboCopSeverity** (line 23, 0 methods) — RuboCop violation severity levels.
- **class RuboCopViolation** (line 35, 0 methods) — Represents a RuboCop code violation.
- **class RuboCopConfig** (line 50, 0 methods) — RuboCop configuration for analysis.
- **class RuboCopParser** (line 62, 9 methods) — Parser for RuboCop code style and linting analysis.

#### `code_parsers/ruby_parsers/ruby_parsers_ast.py` (364 LOC, 0 funcs, 4 classes)
- **class RubyClass** (line 18, 0 methods) — Represents a Ruby class definition.
- **class RubyMethod** (line 30, 0 methods) — Represents a Ruby method definition.
- **class RubyModuleInfo** (line 44, 0 methods) — Represents a Ruby module.
- **class RubyASTParser** (line 54, 17 methods) — Parser for Ruby AST analysis using the RubyNormalizer IR layer.

#### `code_parsers/ruby_parsers/ruby_parsers_brakeman.py` (201 LOC, 0 funcs, 3 classes)
- **class VulnerabilityType** (line 45, 0 methods) — Brakeman vulnerability types.
- **class BrakemanVulnerability** (line 60, 0 methods) — Represents a security vulnerability detected by Brakeman.
- **class BrakemanParser** (line 74, 9 methods) — Parser for Brakeman Rails security vulnerability scanning.

#### `code_parsers/ruby_parsers/ruby_parsers_bundler.py` (217 LOC, 0 funcs, 3 classes)
- **class Gem** (line 24, 0 methods) — Represents a Ruby gem dependency.
- **class BundleConfig** (line 38, 0 methods) — Bundler configuration.
- **class BundlerParser** (line 47, 10 methods) — Parser for Bundler Ruby dependency analysis.

#### `code_parsers/ruby_parsers/ruby_parsers_fasterer.py` (221 LOC, 0 funcs, 2 classes)
- **class PerformanceIssue** (line 23, 0 methods) — Represents a performance issue detected by Fasterer.
- **class FastererParser** (line 35, 11 methods) — Parser for Fasterer Ruby performance anti-pattern detection.

#### `code_parsers/ruby_parsers/ruby_parsers_simplecov.py` (233 LOC, 0 funcs, 3 classes)
- **class FileCoverage** (line 20, 0 methods) — Coverage data for a single source file.
- **class CoverageMetrics** (line 32, 0 methods) — Aggregate coverage metrics across all files.
- **class SimpleCovParser** (line 44, 11 methods) — Parser for SimpleCov Ruby test coverage reports.

#### `code_parsers/rust_parsers/__init__.py` (84 LOC, 0 funcs, 1 classes)
- **class RustParserRegistry** (line 17, 2 methods) — Registry for Rust static-analysis tool parsers.

#### `code_parsers/rust_parsers/rust_parsers_cargo_audit.py` (174 LOC, 0 funcs, 2 classes)
- **class CargoAuditFinding** (line 42, 1 methods) — A single cargo audit vulnerability.
- **class CargoAuditParser** (line 68, 2 methods) — Parser for ``cargo audit --json`` output.

#### `code_parsers/rust_parsers/rust_parsers_cargo_check.py` (164 LOC, 0 funcs, 2 classes)
- **class CargoCheckDiagnostic** (line 20, 1 methods) — Single cargo-check compiler diagnostic.
- **class CargoCheckParser** (line 44, 3 methods) — Parser for ``cargo check --message-format json`` output.

#### `code_parsers/rust_parsers/rust_parsers_clippy.py` (214 LOC, 0 funcs, 2 classes)
- **class ClippyDiagnostic** (line 23, 1 methods) — Single Clippy diagnostic finding.
- **class ClippyParser** (line 49, 4 methods) — Parser for `cargo clippy --message-format json` output.

#### `code_parsers/rust_parsers/rust_parsers_rust_analyzer.py` (220 LOC, 0 funcs, 2 classes)
- **class RustAnalyzerDiagnostic** (line 37, 1 methods) — Single rust-analyzer LSP diagnostic.
- **class RustAnalyzerParser** (line 63, 5 methods) — Parser for rust-analyzer LSP diagnostic output.

#### `code_parsers/rust_parsers/rust_parsers_rustfmt.py` (152 LOC, 0 funcs, 2 classes)
- **class RustfmtFinding** (line 24, 1 methods) — A single rustfmt formatting issue.
- **class RustfmtParser** (line 42, 2 methods) — Parser for ``rustfmt --check`` output.

#### `code_parsers/swift_parsers/__init__.py` (77 LOC, 0 funcs, 1 classes)
- **class SwiftParserRegistry** (line 16, 2 methods) — Registry for Swift static-analysis tool parsers.

#### `code_parsers/swift_parsers/swift_parsers_SwiftLint.py` (285 LOC, 0 funcs, 4 classes)
- **class SwiftLintSeverity** (line 23, 0 methods) — SwiftLint violation severity levels.
- **class SwiftLintViolation** (line 32, 0 methods) — Represents a SwiftLint code violation.
- **class SwiftLintConfig** (line 46, 0 methods) — SwiftLint configuration for analysis.
- **class SwiftLintParser** (line 68, 10 methods) — Parser for SwiftLint code style and linting analysis.

#### `code_parsers/swift_parsers/swift_parsers_Tailor.py` (266 LOC, 1 funcs, 4 classes)
- **class MetricType** (line 26, 0 methods) — Tailor metric types.
- **class TailorMetric** (line 37, 0 methods) — Represents a metric or violation detected by Tailor.
- **class TailorConfig** (line 50, 0 methods) — Tailor configuration for analysis.
- **class TailorParser** (line 86, 9 methods) — Parser for Tailor Swift code metrics analysis.
- `def _infer_metric_type(rule)` L77 — Guess MetricType from a rule identifier string.

#### `code_parsers/swift_parsers/swift_parsers_sourcekitten.py` (229 LOC, 1 funcs, 3 classes)
- **class SwiftSymbol** (line 25, 0 methods) — Represents a Swift symbol (class, function, var, etc.).
- **class SwiftComplexity** (line 39, 0 methods) — Represents code complexity metrics.
- **class SourceKittenParser** (line 97, 9 methods) — Parser for SourceKitten Swift AST and semantic analysis.
- `def _extract_symbols_recursive(substructure, file_path)` L67 — Recursively walk a SourceKit substructure list and build SwiftSymbols.

#### `code_parsers/swift_parsers/swift_parsers_swiftformat.py` (196 LOC, 0 funcs, 2 classes)
- **class FormattingIssue** (line 34, 0 methods) — Represents a formatting issue detected by SwiftFormat.
- **class SwiftFormatParser** (line 45, 7 methods) — Parser for SwiftFormat code formatting and style analysis.

#### `code_parsers/typescript_parsers/alias_resolver.py` (342 LOC, 1 funcs, 1 classes)
- **class AliasResolver** (line 18, 9 methods) — [20251216_FEATURE] Resolver for module aliases from various config files.
- `def create_alias_resolver(project_root)` L327 — Create an alias resolver for a project.

#### `code_parsers/typescript_parsers/analyzer.py` (372 LOC, 2 funcs, 4 classes)
- **class TSAnalysisResult** (line 21, 0 methods) — Result of TypeScript/JavaScript code analysis.
- **class TypeScriptAnalyzer** (line 51, 6 methods) — Analyzer for TypeScript and JavaScript code.
- **class NormalizedFunction** (line 297, 0 methods) — Normalized function representation for cross-language analysis.
- **class NormalizedClass** (line 322, 0 methods) — Normalized class representation for cross-language analysis.
- `def normalize_typescript_function(ts_func)` L342 — Convert TypeScript function dict to normalized representation.
- `def normalize_typescript_class(ts_class)` L356 — Convert TypeScript class dict to normalized representation.

#### `code_parsers/typescript_parsers/decorator_analyzer.py` (306 LOC, 1 funcs, 1 classes)
- **class DecoratorAnalyzer** (line 42, 5 methods) — [20251216_FEATURE] Analyzer for TypeScript decorators.
- `def extract_decorators_from_code(code)` L287 — Extract decorators from TypeScript code.

#### `code_parsers/typescript_parsers/parser.py` (428 LOC, 0 funcs, 5 classes)
- **class TSNodeType** (line 28, 0 methods) — TypeScript/JavaScript AST node types (ESTree-compatible subset).
- **class Decorator** (line 71, 0 methods) — Represents a TypeScript decorator.
- **class TSNode** (line 89, 0 methods) — Represents a node in the TypeScript AST.
- **class TSParseResult** (line 110, 0 methods) — Result of parsing TypeScript/JavaScript code.
- **class TypeScriptParser** (line 125, 6 methods) — Parser for TypeScript and JavaScript source code.

#### `code_parsers/typescript_parsers/tsx_analyzer.py` (182 LOC, 4 funcs, 1 classes)
- **class ReactComponentInfo** (line 21, 0 methods) — Metadata about a React component.
- `def detect_server_directive(code)` L31 — Detect React Server directive in code.
- `def has_jsx_syntax(code)` L54 — Detect JSX syntax in code.
- `def is_react_component(node, code)` L89 — Detect if a function or class is a React component.
- `def normalize_jsx_syntax(code)` L161 — Normalize JSX syntax for consistent analysis.

#### `code_parsers/typescript_parsers/type_narrowing.py` (709 LOC, 1 funcs, 5 classes)
- **class NarrowedType** (line 48, 0 methods) — Types that a variable can be narrowed to.
- **class TypeGuard** (line 88, 0 methods) — Represents a detected type guard in code.
- **class BranchState** (line 102, 2 methods) — Type state within a specific branch.
- **class NarrowingResult** (line 120, 0 methods) — Result of type narrowing analysis.
- **class TypeNarrowing** (line 130, 16 methods) — Analyze TypeScript control flow for type narrowing.
- `def analyze_type_narrowing(code)` L683 — Convenience function to analyze type narrowing in code.

### 4.config `config/` — 4 functions, 0 classes

#### `config/init_config.py` (556 LOC, 4 funcs, 0 classes)
- `def generate_secret_key()` L40 — Generate a cryptographically secure random secret key for HMAC.
- `def validate_config_files(config_dir)` L52 — Validate configuration file formats (JSON, YAML, Rego).
- `def add_missing_config_files(target_dir)` L127 — Add any missing .code-scalpel files without touching existing ones.
- `def init_config_dir(target_dir, mode)` L257 — Initialize .code-scalpel configuration directory with templates.

### 4.generators `generators/` — 0 functions, 12 classes

#### `generators/refactor_simulator.py` (1906 LOC, 0 funcs, 8 classes)
- **class SecurityIssueDict** (line 26, 0 methods) — Type for serialized security issue.
- **class RefactorResultDict** (line 36, 0 methods) — Type-safe dictionary for RefactorSimulationResult.to_dict().
- **class FileResultDict** (line 51, 0 methods) — Type for individual file simulation result.
- **class MultiFileResultDict** (line 63, 0 methods) — Type-safe dictionary for simulate_multi_file() return value.
- **class RefactorStatus** (line 74, 0 methods) — Status of a refactor simulation.
- **class SecurityIssue** (line 84, 0 methods) — A security issue detected in refactored code.
- **class RefactorResult** (line 95, 1 methods) — Result of simulating a refactor.
- **class RefactorSimulator** (line 141, 24 methods) — Simulate code refactors and verify safety.

#### `generators/test_generator.py` (1416 LOC, 0 funcs, 4 classes)
- **class SymbolicResultDict** (line 21, 0 methods) — Type-safe structure for symbolic execution results.
- **class TestCase** (line 35, 1 methods) — A single generated test case.
- **class GeneratedTestSuite** (line 108, 9 methods) — A complete generated test suite.
- **class TestGenerator** (line 411, 22 methods) — Generate unit tests from symbolic execution results.

### 4.governance `governance/` — 1 functions, 23 classes

#### `governance/change_budget.py` (462 LOC, 1 funcs, 5 classes)
- **class FileChange** (line 32, 1 methods) — Represents changes to a single file.
- **class Operation** (line 53, 2 methods) — Represents a code modification operation.
- **class BudgetViolation** (line 76, 1 methods) — Represents a specific budget constraint violation.
- **class BudgetDecision** (line 103, 2 methods) — Result of budget validation.
- **class ChangeBudget** (line 156, 6 methods) — Budget constraints for agent operations.
- `def load_budget_config(config_path)` L412 — Load budget configuration from YAML file.

#### `governance/compliance_reporter.py` (1028 LOC, 0 funcs, 7 classes)
- **class Recommendation** (line 23, 0 methods) — Actionable recommendation for improving security posture.
- **class SecurityPosture** (line 34, 0 methods) — Overall security posture assessment.
- **class OverrideAnalysis** (line 45, 0 methods) — Analysis of policy override requests and approvals.
- **class ViolationAnalysis** (line 57, 0 methods) — Detailed analysis of policy violations.
- **class ReportSummary** (line 68, 0 methods) — Executive summary statistics for compliance report.
- **class ComplianceReport** (line 81, 0 methods) — Complete compliance report with all analysis sections.
- **class ComplianceReporter** (line 93, 18 methods) — Generate compliance reports for governance audits.

#### `governance/governance_config.py` (403 LOC, 0 funcs, 6 classes)
- **class ChangeBudgetingConfig** (line 36, 0 methods) — Configuration for change budgeting limits.
- **class BlastRadiusConfig** (line 52, 1 methods) — Configuration for blast radius control.
- **class AutonomyConstraintsConfig** (line 98, 0 methods) — Configuration for autonomy constraints.
- **class AuditConfig** (line 112, 0 methods) — Configuration for audit trail.
- **class GovernanceConfig** (line 125, 0 methods) — Complete governance configuration.
- **class GovernanceConfigLoader** (line 138, 7 methods) — Load and validate governance configuration.

#### `governance/unified_governance.py` (733 LOC, 0 funcs, 5 classes)
- **class ViolationSource** (line 92, 0 methods) — Source of a governance violation.
- **class GovernanceViolation** (line 102, 1 methods) — A single governance constraint violation.
- **class GovernanceDecision** (line 128, 5 methods) — Result of unified governance evaluation.
- **class GovernanceContext** (line 180, 0 methods) — Context for governance evaluation.
- **class UnifiedGovernance** (line 194, 12 methods) — Unified governance system for policy + budget enforcement.

### 4.graph `graph/` — 5 functions, 26 classes

#### `graph/graph_query.py` (608 LOC, 1 funcs, 7 classes)
- **class QueryOperator** (line 31, 0 methods) — Query comparison operators.
- **class NodePredicate** (line 47, 1 methods) — A predicate to filter nodes.
- **class EdgePredicate** (line 86, 1 methods) — A predicate to filter edges.
- **class PathPattern** (line 105, 0 methods) — A pattern for matching paths in the graph.
- **class QueryResult** (line 117, 0 methods) — Result of a graph query.
- **class GraphQuery** (line 130, 0 methods) — A parsed graph query.
- **class GraphQueryEngine** (line 143, 13 methods) — Execute queries against a graph structure.
- `def create_query_engine(graph)` L606 — Convenience function to create a query engine.

#### `graph/logical_relationships.py` (475 LOC, 1 funcs, 4 classes)
- **class LogicalRelationship** (line 30, 0 methods) — A logical relationship between code elements.
- **class LogicalRelationshipResult** (line 42, 0 methods) — Result of logical relationship detection.
- **class FunctionContext** (line 53, 0 methods) — Context information for a function.
- **class LogicalRelationshipDetector** (line 68, 10 methods) — Detects logical relationships between code elements.
- `def find_logical_relationships(project_root, center_name, max_relationships)` L468 — Convenience function to find logical relationships.

#### `graph/path_constraints.py` (530 LOC, 1 funcs, 6 classes)
- **class ConstraintType** (line 40, 0 methods) — Types of path constraints.
- **class PathConstraint** (line 52, 0 methods) — A single path constraint.
- **class ConstraintSet** (line 63, 0 methods) — A collection of path constraints.
- **class ConstrainedPath** (line 79, 0 methods) — A path that satisfies constraints.
- **class PathConstraintResult** (line 94, 0 methods) — Result of constrained path finding.
- **class PathConstraintEngine** (line 106, 11 methods) — Engine for constraint-based path queries.
- `def create_path_constraint_engine()` L528 — Convenience function to create a path constraint engine.

#### `graph/semantic_neighbors.py` (430 LOC, 1 funcs, 4 classes)
- **class SemanticNeighbor** (line 30, 0 methods) — A semantically related node.
- **class SemanticNeighborResult** (line 43, 0 methods) — Result of semantic neighbor search.
- **class FunctionSignature** (line 55, 0 methods) — Extracted function signature for comparison.
- **class SemanticNeighborFinder** (line 67, 12 methods) — Finds semantically related nodes using various similarity metrics.
- `def find_semantic_neighbors(project_root, center_name, k, min_similarity)` L422 — Convenience function to find semantic neighbors.

#### `graph/traversal_rules.py` (575 LOC, 1 funcs, 5 classes)
- **class RuleType** (line 32, 0 methods) — Types of traversal rules.
- **class TraversalRule** (line 43, 0 methods) — A single traversal rule.
- **class TraversalPath** (line 55, 0 methods) — A path found during traversal.
- **class TraversalResult** (line 66, 0 methods) — Result of rule-based traversal.
- **class TraversalRuleEngine** (line 79, 13 methods) — Engine for rule-based graph traversal.
- `def create_rule_engine()` L573 — Convenience function to create a rule engine.

### 4.graph_engine `graph_engine/` — 2 functions, 15 classes

#### `graph_engine/confidence.py` (280 LOC, 0 funcs, 4 classes)
- **class EdgeType** (line 32, 0 methods) — Type of relationship between code elements.
- **class ConfidenceLevel** (line 63, 0 methods) — Confidence level categories.
- **class ConfidenceEvidence** (line 97, 1 methods) — Evidence that affects confidence scoring.
- **class ConfidenceEngine** (line 118, 8 methods) — Engine for scoring confidence in code relationships.

#### `graph_engine/graph.py` (511 LOC, 0 funcs, 5 classes)
- **class NeighborhoodResult** (line 44, 1 methods) — Result of a k-hop neighborhood extraction.
- **class GraphNode** (line 96, 2 methods) — A node in the universal code graph.
- **class GraphEdge** (line 135, 2 methods) — An edge in the universal code graph with confidence scoring.
- **class UniversalGraph** (line 193, 11 methods) — Universal cross-language code graph.
- **class GraphBuilder** (line 420, 5 methods) — Builder for constructing universal cross-language graphs.

#### `graph_engine/http_detector.py` (379 LOC, 0 funcs, 4 classes)
- **class HTTPMethod** (line 31, 0 methods) — HTTP request methods.
- **class HTTPLink** (line 63, 1 methods) — A detected link between a client API call and a server endpoint.
- **class RoutePatternMatcher** (line 102, 6 methods) — Matcher for HTTP route patterns with confidence scoring.
- **class HTTPLinkDetector** (line 214, 7 methods) — Detector for HTTP links between frontend and backend.

#### `graph_engine/node_id.py` (218 LOC, 2 funcs, 2 classes)
- **class NodeType** (line 32, 0 methods) — Type of code element.
- **class UniversalNodeID** (line 51, 4 methods) — Universal identifier for a code element across any language.
- `def parse_node_id(id_string)` L125 — Parse a universal node ID string into components.
- `def create_node_id(language, module, node_type, name)` L177 — Create a universal node ID.

### 4.hooks `hooks/` — 38 functions, 3 classes

#### `hooks/claude_hooks.py` (570 LOC, 11 funcs, 3 classes)
- **class HookStatus** (line 26, 0 methods) — Status codes for hook responses.
- **class HookContext** (line 37, 2 methods) — Context passed to hooks from Claude Code.
- **class HookResponse** (line 92, 2 methods) — Response from a hook execution.
- `def is_file_modifying_command(command)` L179 — Check if a bash command modifies files.
- `def _get_governance_engine()` L218 — Get the governance engine for validation.
- `def _get_audit_log()` L233 — Get the audit log for logging operations.
- `def _compute_content_hash(content)` L249 — Compute SHA-256 hash of content.
- `def _extract_file_path(tool_name, tool_input)` L261 — Extract file path from tool input based on tool type.
- `def _extract_content(tool_name, tool_input)` L276 — Extract content/changes from tool input.
- `def _extract_modified_files(tool_name, tool_input)` L296 — Extract list of files modified by a tool.
- `def pre_tool_use(context)` L320 — Run before a tool is used. Block if policy violated.
- `def post_tool_use(context)` L433 — Run after a tool is used. Log to audit trail.
- `def pre_tool_use_cli()` L525 — CLI entry point for pre-tool-use hook.
- `def post_tool_use_cli()` L549 — CLI entry point for post-tool-use hook.

#### `hooks/git_hooks.py` (511 LOC, 15 funcs, 0 classes)
- `def _compute_file_hash(file_path)` L59 — Compute SHA-256 hash of file contents.
- `def _is_code_file(file_path)` L72 — Check if a file is a code file that requires audit coverage.
- `def _get_audit_log_path()` L85 — Get the path to the audit log file.
- `def _get_audit_entries_for_file(file_path, audit_log_path)` L94 — Get all audit entries for a specific file.
- `def verify_audit_coverage(file_path, within_seconds)` L144 — Check if file changes have corresponding audit entries.
- `def _get_staged_files()` L205 — Get list of staged files from git.
- `def git_hook_pre_commit()` L224 — Run pre-commit audit verification.
- `def git_hook_commit_msg(msg_file)` L276 — Run commit-msg hook to log commit to audit trail.
- `def _log_blocked_commit(uncovered_files)` L316 — Log a blocked commit attempt to the audit trail.
- `def install_git_hooks(repo_path, force)` L345 — Install Code Scalpel git hooks.
- `def uninstall_git_hooks(repo_path)` L426 — Uninstall Code Scalpel git hooks.
- `def verify_audit_coverage_cli(file_path)` L462 — CLI entry point for verifying audit coverage.
- `def install_git_hooks_cli(force)` L479 — CLI entry point for installing git hooks.
- `def git_hook_pre_commit_cli()` L493 — CLI entry point for pre-commit hook.
- `def git_hook_commit_msg_cli(msg_file)` L502 — CLI entry point for commit-msg hook.

#### `hooks/installer.py` (419 LOC, 12 funcs, 0 classes)
- `def get_claude_settings_path(project_path)` L73 — Get the path to Claude Code settings.json.
- `def get_user_settings_path()` L94 — Get the path to user-level Claude Code settings.
- `def get_managed_settings_path()` L103 — Get the path to enterprise managed settings.
- `def _read_settings(settings_path)` L116 — Read existing settings from file.
- `def _write_settings(settings_path, settings)` L135 — Write settings to file.
- `def _merge_hooks(existing, new)` L149 — Merge hook configurations, avoiding duplicates.
- `def install_claude_hooks(project_path, user_level, enterprise, force)` L174 — Install Claude Code hooks for Code Scalpel governance.
- `def uninstall_claude_hooks(project_path, user_level, enterprise)` L268 — Uninstall Claude Code hooks for Code Scalpel.
- `def check_hooks_installed(project_path)` L331 — Check if Claude Code hooks are installed.
- `def get_settings_template()` L362 — Get the Claude Code settings.json template with hooks.
- `def install_claude_hooks_cli(project_path, user_level, enterprise, force)` L371 — CLI entry point for installing Claude Code hooks.
- `def uninstall_claude_hooks_cli(project_path, user_level, enterprise)` L398 — CLI entry point for uninstalling Claude Code hooks.

### 4.integrations `integrations/` — 15 functions, 47 classes

#### `integrations/__init__.py` (48 LOC, 1 funcs, 0 classes)
- `def __getattr__(name)` L19 — Lazy attribute loading for deprecated integration packages.

#### `integrations/protocol_analyzers/frontend/input_tracker.py` (920 LOC, 3 funcs, 8 classes)
- **class FrontendFramework** (line 55, 0 methods) — Supported frontend frameworks.
- **class InputSourceType** (line 66, 0 methods) — Types of frontend input sources.
- **class DangerousSinkType** (line 104, 0 methods) — Types of dangerous sinks for frontend code.
- **class InputSource** (line 122, 1 methods) — Detected frontend input source.
- **class DangerousSink** (line 149, 1 methods) — Detected dangerous sink.
- **class DataFlow** (line 174, 2 methods) — Represents data flow from input source to sink.
- **class FrontendAnalysisResult** (line 200, 4 methods) — Result of frontend input analysis.
- **class FrontendInputTracker** (line 399, 12 methods) — Tracks user input sources in frontend TypeScript/JavaScript code.
- `def analyze_frontend_file(file_path, framework)` L819 — Analyze a frontend file for input sources and XSS risks.
- `def analyze_frontend_codebase(directory, framework)` L846 — Analyze a frontend codebase for input sources and XSS risks.
- `def get_xss_risks(results)` L891 — Get all XSS risks from multiple analysis results.

#### `integrations/protocol_analyzers/graphql/schema_tracker.py` (1262 LOC, 3 funcs, 13 classes)
- **class GraphQLChangeType** (line 51, 0 methods) — Types of GraphQL schema changes.
- **class GraphQLChangeSeverity** (line 79, 0 methods) — Severity of schema changes.
- **class GraphQLTypeKind** (line 87, 0 methods) — Kinds of GraphQL types.
- **class GraphQLArgument** (line 99, 1 methods) — Represents a GraphQL field argument.
- **class GraphQLField** (line 114, 2 methods) — Represents a GraphQL field.
- **class GraphQLEnumValue** (line 137, 0 methods) — Represents a GraphQL enum value.
- **class GraphQLType** (line 147, 1 methods) — Represents a GraphQL type definition.
- **class GraphQLDirective** (line 169, 0 methods) — Represents a GraphQL directive definition.
- **class GraphQLSchema** (line 180, 11 methods) — Represents a complete GraphQL schema.
- **class GraphQLSchemaChange** (line 266, 1 methods) — Represents a single schema change.
- **class GraphQLSchemaDrift** (line 281, 5 methods) — Result of schema drift analysis.
- **class GraphQLSchemaParser** (line 334, 12 methods) — Parser for GraphQL SDL (Schema Definition Language).
- **class GraphQLSchemaTracker** (line 666, 14 methods) — Tracks GraphQL schema evolution and detects breaking changes.
- `def track_graphql_schema(sdl)` L1186 — Convenience function to parse a GraphQL SDL.
- `def compare_graphql_schemas(old_sdl, new_sdl, old_version, new_version)` L1200 — Convenience function to compare two GraphQL schemas.
- `def compare_graphql_files(old_path, new_path)` L1222 — Convenience function to compare two GraphQL schema files.

#### `integrations/protocol_analyzers/grpc/contract_analyzer.py` (780 LOC, 3 funcs, 7 classes)
- **class StreamingType** (line 49, 0 methods) — gRPC streaming patterns.
- **class IssueSeverity** (line 58, 0 methods) — Severity of contract issues.
- **class RpcMethod** (line 67, 2 methods) — Represents a gRPC RPC method.
- **class GrpcService** (line 107, 3 methods) — Represents a gRPC service definition.
- **class GrpcContract** (line 136, 6 methods) — Represents a complete gRPC contract from a .proto file.
- **class ContractIssue** (line 221, 1 methods) — Represents an issue found during contract validation.
- **class GrpcContractAnalyzer** (line 235, 16 methods) — Analyzes gRPC service contracts from .proto files.
- `def analyze_grpc_contract(proto_content)` L725 — Convenience function to analyze a .proto file.
- `def validate_grpc_contract(proto_content)` L739 — Convenience function to validate a .proto file.
- `def analyze_grpc_file(proto_path)` L754 — Convenience function to analyze a .proto file from disk.

#### `integrations/protocol_analyzers/kafka/taint_tracker.py` (1161 LOC, 3 funcs, 9 classes)
- **class KafkaLibrary** (line 59, 0 methods) — Supported Kafka client libraries.
- **class KafkaPatternType** (line 79, 0 methods) — Types of Kafka patterns detected.
- **class KafkaRiskLevel** (line 91, 0 methods) — Risk level for Kafka taint findings.
- **class KafkaProducer** (line 102, 1 methods) — Represents a Kafka producer send operation.
- **class KafkaConsumer** (line 131, 1 methods) — Represents a Kafka consumer subscription/handler.
- **class KafkaTaintBridge** (line 153, 1 methods) — Bridges taint from producer to consumer across async boundary.
- **class KafkaTopicInfo** (line 182, 3 methods) — Information about a Kafka topic's usage in the codebase.
- **class KafkaAnalysisResult** (line 205, 5 methods) — Result of analyzing a file/codebase for Kafka patterns.
- **class KafkaTaintTracker** (line 318, 22 methods) — Tracks taint propagation through Kafka message boundaries.
- `def analyze_kafka_file(file_path, tainted_variables)` L1002 — Analyze a file for Kafka taint patterns.
- `def analyze_kafka_codebase(directory, tainted_variables, extensions)` L1041 — Analyze an entire codebase for Kafka taint patterns.
- `def get_kafka_taint_bridges(results)` L1100 — Find all taint bridges across multiple analysis results.

#### `integrations/protocol_analyzers/schema/drift_detector.py` (1027 LOC, 2 funcs, 10 classes)
- **class ChangeType** (line 50, 0 methods) — Types of schema changes.
- **class ChangeSeverity** (line 70, 0 methods) — Severity of schema changes.
- **class SchemaChange** (line 79, 1 methods) — Represents a single schema change.
- **class SchemaDriftResult** (line 95, 5 methods) — Result of schema drift analysis.
- **class ProtobufField** (line 148, 0 methods) — Represents a Protobuf field.
- **class ProtobufEnum** (line 161, 0 methods) — Represents a Protobuf enum.
- **class ProtobufMessage** (line 169, 0 methods) — Represents a Protobuf message.
- **class ProtobufSchema** (line 179, 0 methods) — Represents a parsed Protobuf schema.
- **class ProtobufParser** (line 191, 7 methods) — Simple Protobuf schema parser.
- **class SchemaDriftDetector** (line 405, 8 methods) — Detects breaking changes between schema versions.
- `def compare_protobuf_files(old_path, new_path)` L959 — Convenience function to compare two .proto files.
- `def compare_json_schema_files(old_path, new_path)` L988 — Convenience function to compare two JSON Schema files.

### 4.ir `ir/` — 1 functions, 69 classes

#### `ir/nodes.py` (710 LOC, 0 funcs, 34 classes)
- **class SourceLocation** (line 34, 1 methods) — Source code location for error reporting and debugging.
- **class IRNode** (line 64, 1 methods) — Base class for all Unified IR nodes.
- **class IRModule** (line 107, 0 methods) — Root node representing a source file/module.
- **class IRFunctionDef** (line 121, 0 methods) — Function definition.
- **class IRClassDef** (line 150, 0 methods) — Class definition.
- **class IRIf** (line 173, 0 methods) — If statement with optional elif/else chain.
- **class IRFor** (line 195, 0 methods) — For loop (iteration over collection).
- **class IRWhile** (line 220, 0 methods) — While loop.
- **class IRReturn** (line 237, 0 methods) — Return statement.
- **class IRAssign** (line 250, 0 methods) — Assignment statement.
- **class IRAugAssign** (line 271, 0 methods) — Augmented assignment (+=, -=, etc.).
- **class IRExprStmt** (line 288, 0 methods) — Expression statement (expression used as statement).
- **class IRPass** (line 303, 0 methods) — Pass/no-op statement.
- **class IRBreak** (line 315, 0 methods) — Break statement - exit loop.
- **class IRContinue** (line 322, 0 methods) — Continue statement - skip to next iteration.
- **class IRImport** (line 330, 0 methods) — Import statement (ES6 modules, Python imports, Java imports).
- **class IRExport** (line 355, 0 methods) — Export statement (ES6 modules).
- **class IRSwitch** (line 378, 0 methods) — Switch statement.
- **class IRTry** (line 393, 0 methods) — Try/catch/finally statement.
- **class IRRaise** (line 411, 0 methods) — Raise/throw statement.
- **class IRExpr** (line 430, 0 methods) — Base class for expression nodes.
- **class IRBinaryOp** (line 441, 0 methods) — Binary operation (a + b, a * b, etc.).
- **class IRUnaryOp** (line 470, 0 methods) — Unary operation (-x, not x, ~x, etc.).
- **class IRCompare** (line 485, 0 methods) — Comparison operation.
- **class IRBoolOp** (line 509, 0 methods) — Boolean/logical operation (and, or).
- **class IRTernary** (line 527, 0 methods) — Ternary/conditional expression.
- **class IRCall** (line 547, 0 methods) — Function/method call.
- **class IRAttribute** (line 575, 0 methods) — Attribute access (obj.attr).
- **class IRSubscript** (line 590, 0 methods) — Subscript/index access (obj[key]).
- **class IRName** (line 605, 0 methods) — Variable/identifier reference.
- **class IRConstant** (line 617, 0 methods) — Literal constant value.
- **class IRList** (line 637, 0 methods) — List/Array literal.
- **class IRDict** (line 649, 0 methods) — Dictionary/Object literal.
- **class IRParameter** (line 663, 0 methods) — Function parameter.

#### `ir/normalizers/base.py` (90 LOC, 0 funcs, 1 classes)
- **class BaseNormalizer** (line 14, 4 methods) — Abstract base class for language-specific normalizers.

#### `ir/normalizers/c_normalizer.py` (912 LOC, 0 funcs, 2 classes)
- **class CVisitor** (line 93, 56 methods) — Visitor that converts tree-sitter C CST nodes to Unified IR.
- **class CNormalizer** (line 863, 5 methods) — Normalizes C source code to Unified IR using tree-sitter-c.

#### `ir/normalizers/cpp_normalizer.py` (582 LOC, 0 funcs, 2 classes)
- **class CppVisitor** (line 58, 24 methods) — Visitor for C++ CST nodes.
- **class CppNormalizer** (line 526, 5 methods) — Normalizes C++ source code to Unified IR using tree-sitter-cpp.

#### `ir/normalizers/csharp_normalizer.py` (1165 LOC, 1 funcs, 2 classes)
- **class CSharpVisitor** (line 123, 58 methods) — Visitor that converts tree-sitter C# CST nodes to Unified IR.
- **class CSharpNormalizer** (line 1114, 5 methods) — Normalizes C# source code to Unified IR using tree-sitter-c-sharp.
- `def _name_text(node, source)` L113 — Return dot-separated text of an identifier or qualified_name node.

#### `ir/normalizers/go_normalizer.py` (909 LOC, 0 funcs, 2 classes)
- **class GoVisitor** (line 99, 53 methods) — Visitor that converts tree-sitter Go CST nodes to Unified IR.
- **class GoNormalizer** (line 858, 5 methods) — Normalizes Go source code to Unified IR using tree-sitter-go.

#### `ir/normalizers/java_normalizer.py` (1033 LOC, 0 funcs, 2 classes)
- **class JavaVisitor** (line 47, 49 methods) — Visitor that converts Java CST nodes to IR nodes.
- **class JavaNormalizer** (line 984, 5 methods) — [20251224_FEATURE] Java CST normalization with comprehensive features.

#### `ir/normalizers/javascript_normalizer.py` (1796 LOC, 0 funcs, 1 classes)
- **class JavaScriptNormalizer** (line 138, 78 methods) — Normalizes JavaScript CST (from tree-sitter) to Unified IR.

#### `ir/normalizers/kotlin_normalizer.py` (1153 LOC, 0 funcs, 2 classes)
- **class KotlinVisitor** (line 103, 51 methods) — Visitor that converts tree-sitter Kotlin CST nodes to Unified IR.
- **class KotlinNormalizer** (line 1099, 5 methods) — Normalizes Kotlin source code to Unified IR using tree-sitter-kotlin.

#### `ir/normalizers/php_normalizer.py` (979 LOC, 0 funcs, 2 classes)
- **class PHPVisitor** (line 160, 58 methods) — Visitor that converts tree-sitter PHP CST nodes to Unified IR.
- **class PHPNormalizer** (line 929, 5 methods) — Normalize PHP source code to Unified IR.

#### `ir/normalizers/python_normalizer.py` (1067 LOC, 0 funcs, 1 classes)
- **class PythonNormalizer** (line 58, 53 methods) — Normalizes Python ast.* nodes to Unified IR.

#### `ir/normalizers/ruby_normalizer.py` (850 LOC, 0 funcs, 2 classes)
- **class RubyVisitor** (line 149, 57 methods) — Visitor that converts tree-sitter Ruby CST nodes to Unified IR.
- **class RubyNormalizer** (line 816, 3 methods) — Normalizer for Ruby source code.

#### `ir/normalizers/rust_normalizer.py` (956 LOC, 0 funcs, 2 classes)
- **class RustVisitor** (line 130, 56 methods) — Visitor that converts tree-sitter Rust CST nodes to Unified IR.
- **class RustNormalizer** (line 915, 4 methods) — Normalizer that converts Rust source code to Unified IR.

#### `ir/normalizers/swift_normalizer.py` (1142 LOC, 0 funcs, 2 classes)
- **class SwiftVisitor** (line 138, 64 methods) — Visitor that converts tree-sitter Swift CST nodes to Unified IR.
- **class SwiftNormalizer** (line 1106, 3 methods) — Normalizer for Swift source code.

#### `ir/normalizers/tree_sitter_visitor.py` (415 LOC, 0 funcs, 2 classes)
- **class VisitorContext** (line 53, 1 methods) — Context for tree-sitter visitor traversal.
- **class TreeSitterVisitor** (line 77, 24 methods) — Abstract base class for tree-sitter CST visitors.

#### `ir/normalizers/typescript_normalizer.py` (431 LOC, 0 funcs, 2 classes)
- **class TypeScriptNormalizer** (line 34, 6 methods) — Normalizes TypeScript CST (from tree-sitter) to Unified IR.
- **class TypeScriptTSXNormalizer** (line 257, 7 methods) — Normalizes TSX (TypeScript + JSX) CST to Unified IR.

#### `ir/operators.py` (111 LOC, 0 funcs, 5 classes)
- **class BinaryOperator** (line 11, 0 methods) — Binary operators normalized across languages.
- **class CompareOperator** (line 40, 0 methods) — Comparison operators normalized across languages.
- **class UnaryOperator** (line 67, 0 methods) — Unary operators normalized across languages.
- **class BoolOperator** (line 80, 0 methods) — Boolean/logical operators normalized across languages.
- **class AugAssignOperator** (line 92, 0 methods) — Augmented assignment operators (+=, -=, etc.).

#### `ir/semantics.py` (694 LOC, 0 funcs, 3 classes)
- **class LanguageSemantics** (line 13, 20 methods) — Abstract base class for language-specific operation semantics.
- **class PythonSemantics** (line 224, 20 methods) — Python language semantics.
- **class JavaScriptSemantics** (line 412, 21 methods) — JavaScript language semantics.

### 4.lib_scalpel `lib_scalpel/` — 5 functions, 27 classes

#### `lib_scalpel/analysis/__init__.py` (22 LOC, 1 funcs, 0 classes)
- `def generate_markdown_spec(graph, constraints, file_path, instruction)` L13 — Generate Markdown spec from graph and constraints.

#### `lib_scalpel/analysis/constraint_analyzer.py` (261 LOC, 0 funcs, 1 classes)
- **class ConstraintAnalyzer** (line 26, 9 methods) — Analyzes graphs and architectural constraints.

#### `lib_scalpel/analysis/spec_generator.py` (229 LOC, 0 funcs, 1 classes)
- **class SpecGenerator** (line 27, 3 methods) — Generates constraint specifications in Markdown format.

#### `lib_scalpel/graph_engine/confidence.py` (280 LOC, 0 funcs, 4 classes)
- **class EdgeType** (line 32, 0 methods) — Type of relationship between code elements.
- **class ConfidenceLevel** (line 63, 0 methods) — Confidence level categories.
- **class ConfidenceEvidence** (line 97, 1 methods) — Evidence that affects confidence scoring.
- **class ConfidenceEngine** (line 118, 8 methods) — Engine for scoring confidence in code relationships.

#### `lib_scalpel/graph_engine/node_id.py` (218 LOC, 2 funcs, 2 classes)
- **class NodeType** (line 32, 0 methods) — Type of code element.
- **class UniversalNodeID** (line 51, 4 methods) — Universal identifier for a code element across any language.
- `def parse_node_id(id_string)` L125 — Parse a universal node ID string into components.
- `def create_node_id(language, module, node_type, name)` L177 — Create a universal node ID.

#### `lib_scalpel/graph_engine/scanner.py` (690 LOC, 0 funcs, 1 classes)
- **class ProjectScanner** (line 62, 8 methods) — Lean project scanner for building UniversalGraph from Python files.

#### `lib_scalpel/graph_engine/universal_graph.py` (511 LOC, 0 funcs, 5 classes)
- **class NeighborhoodResult** (line 44, 1 methods) — Result of a k-hop neighborhood extraction.
- **class GraphNode** (line 96, 2 methods) — A node in the universal code graph.
- **class GraphEdge** (line 135, 2 methods) — An edge in the universal code graph with confidence scoring.
- **class UniversalGraph** (line 193, 11 methods) — Universal cross-language code graph.
- **class GraphBuilder** (line 420, 5 methods) — Builder for constructing universal cross-language graphs.

#### `lib_scalpel/models/__init__.py` (179 LOC, 0 funcs, 11 classes)
- **class FunctionSignature** (line 17, 0 methods) — Extracted function signature.
- **class ClassSignature** (line 29, 0 methods) — Extracted class signature.
- **class ImportStatement** (line 40, 0 methods) — Extracted import statement.
- **class SymbolTable** (line 49, 0 methods) — Extracted symbol table from a file.
- **class CallEdge** (line 65, 0 methods) — An edge in the call/dependency graph.
- **class GraphConstraints** (line 74, 0 methods) — Graph-based constraints for a file.
- **class TopologyRule** (line 85, 0 methods) — An architectural topology rule.
- **class TopologyViolation** (line 96, 0 methods) — A violation of an architectural rule.
- **class CodeContext** (line 112, 0 methods) — Relevant code context for the constraint spec.
- **class ConstraintSpec** (line 122, 0 methods) — Complete constraint specification for code generation.
- **class MarkdownSpec** (line 160, 1 methods) — A constraint spec in Markdown format for LLM consumption.

#### `lib_scalpel/oracle_pipeline.py` (213 LOC, 2 funcs, 1 classes)
- **class OraclePipeline** (line 30, 3 methods) — Serverless constraint injection pipeline.
- `async def generate_constraint_spec_async(repo_root, file_path, instruction, max_files)` L155 — Generate constraint spec asynchronously.
- `def generate_constraint_spec_sync(repo_root, file_path, instruction, max_files)` L189 — Generate constraint spec synchronously.

#### `lib_scalpel/visitors/symbol_extractor.py` (263 LOC, 0 funcs, 1 classes)
- **class SymbolExtractor** (line 23, 8 methods) — Extracts function/class signatures from Python ASTs.

### 4.licensing `licensing/` — 64 functions, 21 classes

#### `licensing/__init__.py` (185 LOC, 0 funcs, 1 classes)
- **class Tier** (line 97, 1 methods) — License tier levels for Code Scalpel.

#### `licensing/authorization.py` (163 LOC, 1 funcs, 0 classes)
- `def compute_effective_tier_for_startup()` L22 — Compute the effective tier for server startup.

#### `licensing/cache.py` (587 LOC, 0 funcs, 2 classes)
- **class CacheEntry** (line 38, 1 methods) — A cached license validation result.
- **class LicenseCache** (line 52, 19 methods) — Cache for license validation results.

#### `licensing/config_loader.py` (575 LOC, 17 funcs, 0 classes)
- `def _find_config_file()` L54 — Locate limits.toml in the package's capabilities/ directory.
- `def load_limits(config_path)` L77 — Load tier limits from TOML configuration file.
- `def get_tool_limits(tool_id, tier, config)` L114 — Get limits for a specific tool at a specific tier.
- `def merge_limits(defaults, overrides)` L149 — Merge config overrides into default limits.
- `def get_cached_limits()` L174 — Get cached limits config, loading if not already cached.
- `def clear_cache()` L212 — Clear the limits and features caches, forcing reload on next access.
- `def reload_config()` L222 — Force reload of limits and features from disk.
- `def _find_features_file()` L238 — Locate features.toml in the package's capabilities/ directory.
- `def load_features(config_path)` L259 — Load feature capabilities from TOML configuration file.
- `def get_cached_features()` L305 — Get cached features config, loading if stale.
- `def clear_features_cache()` L342 — Clear the features cache, forcing reload on next access.
- `def _find_response_config_file()` L362 — Find the response_config.json file using priority search order.
- `def load_response_config(config_path)` L407 — Load response configuration from JSON file.
- `def _get_default_response_config()` L440 — Return default response configuration.
- `def get_cached_response_config()` L467 — Get cached response config, loading if not already cached.
- `def filter_response(result, tool_id, config)` L499 — Filter response dict based on response_config.json settings.
- `def clear_response_config_cache()` L570 — Clear the response config cache, forcing reload on next access.

#### `licensing/crl_fetcher.py` (178 LOC, 9 funcs, 1 classes)
- **class CRLCachePaths** (line 35, 0 methods) — 
- `def _xdg_config_home()` L40 — 
- `def default_cache_paths()` L47 — 
- `def _now_epoch()` L54 — 
- `def _max_cache_age_seconds()` L58 — 
- `def fetch_crl_token(url, timeout_seconds)` L69 — 
- `def write_cache(token, paths)` L90 — 
- `def load_cache_if_fresh(paths)` L101 — 
- `def ensure_crl_available()` L122 — Ensure a CRL token is available via CODE_SCALPEL_LICENSE_CRL_PATH.
- `def start_crl_refresh_thread(interval_seconds)` L158 — Start a daemon thread to periodically refresh the CRL cache.

#### `licensing/features.py` (308 LOC, 7 funcs, 1 classes)
- **class _ToolCapabilitiesProxy** (line 64, 9 methods) — Lazy-loading dict shim that reconstructs the legacy TOOL_CAPABILITIES
- `def _convert_sentinel(value)` L141 — Convert the UNLIMITED sentinel used in limits.toml to Python None.
- `def _sanitise_limits(raw)` L153 — Apply sentinel conversion to every value in a limits dict.
- `def get_tool_capabilities(tool_id, tier)` L158 — Get capabilities and limits for a tool at a specific tier.
- `def has_capability(tool_id, capability, tier)` L228 — Check if a tool has a specific capability at a tier.
- `def get_upgrade_hint(tool_id, missing_capability, current_tier)` L244 — Generate upgrade hint for a missing capability.
- `def get_all_tools_for_tier(tier)` L272 — Get all tool IDs available at a tier.
- `def get_missing_capabilities(tool_id, current_tier, target_tier)` L288 — Get capabilities available in target tier but not in current tier.

#### `licensing/jwt_generator.py` (363 LOC, 2 funcs, 0 classes)
- `def generate_license(tier, customer_id, organization, features)` L97 — Generate a JWT license token.
- `def main()` L201 — CLI entry point for license generation.

#### `licensing/jwt_validator.py` (1213 LOC, 4 funcs, 4 classes)
- **class _LicenseValidationCacheEntry** (line 56, 0 methods) — 
- **class JWTAlgorithm** (line 130, 0 methods) — Supported JWT signing algorithms.
- **class JWTLicenseData** (line 138, 1 methods) — Parsed JWT license data.
- **class JWTLicenseValidator** (line 168, 14 methods) — Validate JWT-based license keys for Code Scalpel.
- `def _utcnow_naive()` L71 — 
- `def _utcfromtimestamp_naive(timestamp)` L77 — 
- `def get_current_tier()` L1074 — Get the current tier for the running Code Scalpel instance.
- `def get_license_info()` L1115 — Get detailed license information.

#### `licensing/license_manager.py` (582 LOC, 1 funcs, 2 classes)
- **class LicenseInfo** (line 45, 0 methods) — Information about the current license.
- **class LicenseManager** (line 102, 20 methods) — Central license management for Code Scalpel.
- `def _utcnow_naive()` L38 — 

#### `licensing/remote_verifier.py` (516 LOC, 18 funcs, 3 classes)
- **class VerifiedEntitlements** (line 80, 0 methods) — 
- **class LicenseCacheState** (line 92, 0 methods) — 
- **class AuthorizationDecision** (line 413, 0 methods) — 
- `def _is_loopback_verifier_url(url)` L60 — Return True if the verifier URL points at a local loopback interface.
- `def _utc_now_iso()` L109 — 
- `def _default_cache_path()` L113 — 
- `def cache_path()` L119 — 
- `def verifier_base_url()` L126 — 
- `def remote_verifier_configured()` L152 — 
- `def verifier_environment()` L156 — 
- `def sha256_token(token)` L164 — 
- `def _hash_hint(token_hash)` L168 — Return a short, non-sensitive identifier for logs/errors.
- `def _read_json_file(path)` L177 — 
- `def _atomic_write_json(path, payload)` L192 — 
- `def load_cache_state()` L216 — 
- `def save_cache_state(entitlements, token_hash)` L244 — 
- `def _verify_timeout_seconds()` L278 — 
- `def _verify_retries()` L288 — 
- `def remote_verify(token)` L298 — 
- `def authorize_token(token)` L419 — Authorize based on the on-demand policy described in the contract.
- `def refresh_cache(token)` L505 — Force a remote verification and update the persisted cache.

#### `licensing/runtime_revalidator.py` (98 LOC, 2 funcs, 1 classes)
- **class RevalidationState** (line 34, 0 methods) — 
- `def get_revalidation_state()` L44 — 
- `def start_license_revalidation_thread(interval_seconds)` L48 — Start a daemon thread that periodically re-validates the current license.

#### `licensing/tier_detector.py` (501 LOC, 1 funcs, 3 classes)
- **class Tier** (line 38, 0 methods) — Placeholder - real Tier enum is in __init__.py
- **class TierDetectionResult** (line 47, 0 methods) — Result of tier detection.
- **class TierDetector** (line 61, 16 methods) — Detect the current license tier from environment and configuration.
- `def get_current_tier()` L493 — Get the current license tier.

#### `licensing/validator.py` (615 LOC, 2 funcs, 3 classes)
- **class ValidationStatus** (line 63, 0 methods) — License validation status.
- **class ValidationResult** (line 74, 2 methods) — Result of license validation.
- **class LicenseValidator** (line 101, 13 methods) — Validate license keys for Code Scalpel.
- `def _utcnow_naive()` L51 — 
- `def _utcfromtimestamp_naive(timestamp)` L57 — 

### 4.mcp `mcp/` — 375 functions, 142 classes

#### `mcp/__init__.py` (98 LOC, 4 funcs, 0 classes)
- `def _load_server()` L59 — 
- `def get_mcp()` L67 — Return the FastMCP server instance (lazy import).
- `def run_server()` L73 — Run the MCP server (lazy import).
- `def __getattr__(name)` L79 — 

#### `mcp/contract.py` (606 LOC, 5 funcs, 5 classes)
- **class UpgradeRequiredError** (line 30, 1 methods) — Raised when a caller requests a capability unavailable at current tier.
- **class UpgradeHint** (line 71, 0 methods) — 
- **class ToolError** (line 77, 7 methods) — 
- **class DictWithDotAccess** (line 108, 2 methods) — Helper to allow dot access to dictionary fields for backward compatibility.
- **class ToolResponseEnvelope** (line 131, 2 methods) — 
- `def _classify_exception(exc)` L304 — 
- `def _maybe_get_success_and_error(payload)` L326 — Best-effort introspection of existing tool payloads.
- `def _classify_failure_message(message)` L347 — 
- `def make_envelope(data, tool_id, tool_version, tier)` L372 — [20260121_FEATURE] Create a ToolResponseEnvelope for internal tool use.
- `def envelop_tool_function(fn)` L447 — Wrap an MCP tool function to always return a ToolResponseEnvelope.

#### `mcp/debug.py` (37 LOC, 3 funcs, 0 classes)
- `def debug_enabled()` L18 — 
- `def debug_print()` L23 — Print to stderr (flushed) only when debug is enabled.
- `def debug_flush()` L32 — Force a stderr flush (small helper).

#### `mcp/governance.py` (992 LOC, 14 funcs, 0 classes)
- `def auto_init_config_dir()` L28 — Create .code-scalpel scaffolding if missing.
- `def _emit_governance_audit_event(policy_dir, event)` L112 — Emit a structured audit event.
- `def _parse_bool_env(name, default)` L138 — 
- `def _get_governance_enforcement(tier)` L150 — Resolve enforcement posture.
- `def _default_governance_features_for_tier(tier)` L186 — 
- `def _is_budgeted_write_tool(tool_id)` L198 — 
- `def _diff_added_removed_lines(old_code, new_code)` L204 — Compute added/removed lines for budget accounting.
- `def _evaluate_change_budget_for_write_tool()` L223 — Evaluate change budgets for write tools without mutating the filesystem.
- `def _supported_governance_features_for_tier(tier)` L510 — 
- `def _parse_governance_features_env()` L526 — 
- `def _compute_effective_governance_features(tier)` L535 — 
- `def _policy_state_fingerprint(policy_dir)` L558 — Create a cheap fingerprint for policy inputs to support caching.
- `def _governance_enforcement_for_tier(tier)` L583 — Deprecated shim: use _get_governance_enforcement().
- `def _maybe_enforce_governance_before_tool()` L591 — Apply tier-aware governance preflight.

#### `mcp/helpers/analyze_helpers.py` (1641 LOC, 26 funcs, 0 classes)
- `def _get_cache()` L56 — Get the analysis cache (lazy initialization).
- `def _validate_code(code)` L78 — Validate code before analysis.
- `def _count_complexity(tree)` L89 — Estimate cyclomatic complexity.
- `def _calculate_cognitive_complexity_python(tree)` L100 — Calculate cognitive complexity for Python code.
- `def _detect_code_smells_python(tree, code)` L145 — Detect code smells in Python code.
- `def _compute_halstead_metrics_python(tree)` L235 — Compute Halstead metrics for Python code using AST traversal.
- `def _detect_duplicate_code_blocks(code, min_lines)` L286 — Detect duplicate code blocks using line-hash sliding windows.
- `def _build_dependency_graph_python(tree)` L311 — Build a lightweight intra-module call graph for Python code.
- `def _detect_naming_issues_python(tree)` L330 — Detect simple naming convention issues (snake_case for functions, PascalCase for
- `def _apply_custom_rules_python(code)` L350 — Apply a small built-in custom rule set for Enterprise tier.
- `def _detect_compliance_issues_python(tree, code)` L375 — Detect simple compliance-related patterns (bare except, missing logging).
- `def _detect_organization_patterns_python(tree)` L390 — Detect coarse architectural hints from class naming conventions.
- `def _analyze_clike_code(code, language)` L404 — Analyze C, C++, or C# code using the tree-sitter IR normalizer layer.
- `def _analysis_result_from_ir_module(ir_module, code)` L452 — Build a basic AnalysisResult from a unified IR module.
- `def _analyze_adapter_backed_code(code, language)` L523 — Analyze languages backed by IParser adapters and unified IR normalizers.
- `def _analyze_java_code(code)` L600 — Analyze Java code using tree-sitter.
- `def _analyze_javascript_code(code, is_typescript)` L640 — Analyze JavaScript/TypeScript code using tree-sitter.
- `def _walk_ts_tree(node)` L819 — Generator to walk all nodes in a tree-sitter tree.
- `def _detect_frameworks_from_code(code, language, imports)` L826 — Heuristic framework detection for a single code blob.
- `def _detect_dead_code_hints_python(tree, code)` L881 — Best-effort dead code hints for Python.
- `def _summarize_decorators_python(tree)` L963 — 
- `def _summarize_types_python(tree)` L991 — 
- `def _compute_api_surface_from_symbols(functions, classes)` L1063 — 
- `def _priority_sort(items)` L1081 — Sort a list of issue/smell labels by severity keywords.
- `def _update_and_get_complexity_trends()` L1105 — 
- `def _analyze_code_sync(code, language, file_path)` L1138 — Synchronous implementation of analyze_code.

#### `mcp/helpers/ast_helpers.py` (60 LOC, 3 funcs, 0 classes)
- `def get_cached_ast(file_path)` L18 — Retrieve cached AST if fresh, otherwise return None.
- `def cache_ast(file_path, tree)` L35 — Cache an AST tree for path.
- `def parse_file_cached(file_path)` L44 — Parse a Python file with caching using unified parser.

#### `mcp/helpers/context_helpers.py` (4071 LOC, 25 funcs, 0 classes)
- `def _strip_csharp_line_comment(line)` L140 — Remove trailing single-line C# comments for lightweight parsing.
- `def _build_csharp_file_context_fallback(path, lines, tier, max_context_lines)` L147 — Return a conservative FileContextResult for a C# file without tree-sitter.
- `def _is_env_file(path)` L302 — Check whether a file is an environment file that should be redacted.
- `def _redact_sensitive_content(path, content)` L308 — Redact secrets/PII before analysis.
- `def _scan_js_ts_symbol_references(file_path, root, symbol_name, enable_categorization)` L362 — Best-effort JS/TS symbol reference scan.
- `def _scan_java_symbol_references(file_path, root, symbol_name, enable_categorization)` L512 — Best-effort Java symbol reference scan.
- `def _crawl_project_discovery(root_path, exclude_dirs)` L905 — Discovery-only crawl for Community tier.
- `def _crawl_project_sync(root_path, exclude_dirs, complexity_threshold, include_report)` L1152 — Synchronous implementation of crawl_project.
- `async def crawl_project(root_path, exclude_dirs, complexity_threshold, include_report)` L1790 —     Crawl an entire project directory and analyze all Python files.
- `def _get_file_context_sync(file_path, tier, capabilities)` L1994 — Synchronous implementation of get_file_context.
- `def _count_complexity_node(node)` L2434 — Count cyclomatic complexity for a single node.
- `def _detect_code_smells(tree, code, lines)` L2448 — Detect common code smells in Python code.
- `def _get_nesting_depth(node, current_depth)` L2551 — Calculate maximum nesting depth of a code block.
- `def _calculate_doc_coverage(tree, functions, classes)` L2561 — Calculate documentation coverage percentage.
- `def _calculate_maintainability_index(line_count, complexity, symbol_count)` L2595 — Calculate Maintainability Index (0-100 scale, higher is better).
- `def _load_custom_metadata(file_path)` L2633 — Load custom metadata from .code-scalpel/metadata.yaml if exists.
- `def _detect_compliance_flags(code, file_path)` L2664 — Detect compliance-relevant patterns in code.
- `def _calculate_technical_debt(code_smells, complexity, doc_coverage, line_count)` L2709 — Calculate technical debt score in estimated hours to fix.
- `def _get_code_owners(file_path)` L2742 — Parse CODEOWNERS file to find owners for the given file.
- `def _parse_codeowners(codeowners_file, target_file, repo_root)` L2771 — Parse CODEOWNERS and return owners matching the target file.
- `def _codeowners_pattern_matches(pattern, file_path)` L2801 — Check if a CODEOWNERS pattern matches a file path.
- `def _get_historical_metrics(file_path)` L2825 — Get historical metrics from git for the file.
- `async def get_file_context(file_path)` L2932 — Get a file overview without reading full content.
- `def _get_symbol_references_sync(symbol_name, project_root, max_files, max_references)` L2983 — Synchronous implementation of get_symbol_references.
- `async def get_symbol_references(symbol_name, project_root, scope_prefix, include_tests)` L3949 — Find all references to a symbol across the project.

#### `mcp/helpers/extraction_helpers.py` (2104 LOC, 18 funcs, 0 classes)
- `def _get_project_root()` L35 — Get the server's PROJECT_ROOT dynamically.
- `def _get_cache()` L57 — 
- `def _extraction_error(target_name, error, tier, language)` L71 — Create a standardized error result for extraction failures.
- `async def _extract_polyglot(target_type, target_name, file_path, code)` L95 — [20251214_FEATURE] v2.0.0 - Multi-language extraction using PolyglotExtractor.
- `def _create_extractor(file_path, code, target_name)` L201 — Create a SurgicalExtractor from file_path or code.
- `def _extract_method(extractor, target_name)` L239 — Extract a method, handling the ClassName.method_name parsing.
- `def _perform_extraction(extractor, target_type, target_name, include_context)` L249 — Perform the actual extraction based on target type and options.
- `def _process_cross_file_context(cross_file_result)` L317 — Process cross-file resolution results into context_code and context_items.
- `def _build_full_code(imports_needed, context_code, target_code)` L341 — Build the combined full_code for LLM consumption.
- `async def _extract_code_impl(target_type, target_name, file_path, code)` L354 — Surgically extract specific code elements (functions, classes, methods).
- `async def rename_symbol(file_path, target_type, target_name, new_name)` L811 — Rename a function, class, or method in a file.
- `async def update_symbol(file_path, target_type, target_name, new_code)` L958 — Surgically replace a function, class, or method in a file with new code.
- `async def _perform_atomic_git_refactor(file_path, target_name, new_code)` L1624 — Enterprise tier: Atomic refactoring with git branch creation and test execution.
- `async def _update_cross_file_references(modified_file, target_type, target_name, new_code)` L1750 — Pro tier: Update cross-file references when a symbol changes.
- `async def _check_code_review_approval(file_path, target_name, target_type, new_code)` L1860 — Enterprise tier: Check if code review approval is required and granted.
- `async def _check_compliance(file_path, target_name, new_code)` L1916 — Enterprise tier: Check compliance rules before allowing mutation.
- `async def _run_pre_update_hook(file_path, target_name, target_type, new_code)` L1977 — Pro tier: Run pre-update hook before applying changes.
- `async def _run_post_update_hook(file_path, target_name, target_type, result)` L2042 — Pro tier: Run post-update hook after applying changes.

#### `mcp/helpers/graph_helpers.py` (4242 LOC, 29 funcs, 0 classes)
- `def _project_map_detect_language(rel_path)` L81 — Return the canonical project-map language for a relative path.
- `def _calculate_js_ts_project_map_complexity(code)` L95 — Return a lightweight complexity heuristic for local JS/TS project-map scans.
- `def _scan_js_ts_project_map_module(file_path, root_path, include_complexity)` L100 — Build ModuleInfo for a local JS/TS source file.
- `def _scan_java_project_map_module(file_path, root_path, include_complexity)` L164 — Build ModuleInfo for a local Java source file.
- `def _resolve_project_map_import_target(import_name, source_path, module_index)` L225 — Resolve a project-map import string to a known module path.
- `def _get_project_root()` L264 — Get the server's PROJECT_ROOT dynamically.
- `def _get_cached_graph(project_root, cache_variant)` L289 — Get cached UniversalGraph for project if still valid.
- `def _cache_graph(project_root, graph, cache_variant)` L310 — Cache a UniversalGraph for a project.
- `def _get_call_graph_sync(project_root, entry_point, depth, include_circular_import_check)` L358 — Synchronous implementation of get_call_graph with tier-aware metadata.
- `def _generate_neighborhood_mermaid(nodes, edges, center_node_id)` L663 — Generate Mermaid diagram for neighborhood.
- `def _normalize_graph_center_node_id(center_node_id)` L699 — Normalize common legacy node-id formats into canonical IDs.
- `def _resolve_graph_module_candidate(root_path, language, module)` L773 — Resolve a canonical graph module to a local source file when possible.
- `def _fast_validate_js_ts_graph_node_exists(candidate, kind, name)` L819 — Best-effort validation for a local JS/TS function or method node.
- `def _fast_validate_java_graph_node_exists(candidate, kind, name)` L918 — Best-effort validation for a local Java method node.
- `def _parse_graph_center_node_id(center_node_id)` L999 — Parse a canonical graph center node ID.
- `def _fast_validate_graph_center_node_exists(root_path, center_node_id)` L1022 — Best-effort fast validation for supported graph-neighborhood node IDs.
- `def _get_graph_language_from_file(file_path)` L1093 — Infer graph language from a relative file path.
- `def _get_graph_module_from_file(file_path, language)` L1100 — Convert a relative file path to the canonical graph module form.
- `def _build_graph_node_id(file_path, symbol_name)` L1116 — Build a canonical graph node ID from a file/symbol pair.
- `def _get_java_symbol_base_name(symbol_name)` L1143 — Return the base member name from a Java selector or canonical method name.
- `def _read_node_code_slice(root_path, rel_file, line, end_line)` L1149 — Read a best-effort source slice for a graph node.
- `def _build_file_dependency_chains(import_graph, target_file, max_depth)` L1174 — Build bounded file-level dependency chains.
- `def _build_file_mermaid(import_graph, target_file, max_depth)` L1205 — Build a bounded Mermaid diagram from a file-level import graph.
- `def _get_js_ts_cross_file_dependencies_sync(root_path, target_path, target_symbol, target_language)` L1255 — Graph-backed JS/TS/Java dependency slice for get_cross_file_dependencies.
- `def _fast_validate_python_function_node_exists(root_path, center_node_id)` L1518 — Best-effort fast validation for python::<module>::function::<name>.
- `def _get_graph_neighborhood_sync(center_node_id, k, max_nodes, direction)` L1590 — Synchronous implementation of get_graph_neighborhood.
- `def _get_project_map_sync(project_root, include_complexity, complexity_threshold, include_circular_check)` L2057 — Synchronous implementation of get_project_map.
- `def _get_cross_file_dependencies_sync(target_file, target_symbol, project_root, max_depth)` L3051 — Synchronous implementation of get_cross_file_dependencies.
- `def _cross_file_security_scan_sync(project_root, entry_points, max_depth, include_diagram)` L3889 — Synchronous implementation of cross_file_security_scan.

#### `mcp/helpers/language_helpers.py` (100 LOC, 3 funcs, 0 classes)
- `def normalize_language_name(language)` L62 — Return a canonical lower-case language name or None for auto-detect.
- `def detect_tool_language()` L74 — Resolve the canonical language for a tool invocation.
- `def is_supported_language(language, supported_languages)` L98 — Return True when *language* is in the supported language set.

#### `mcp/helpers/policy_helpers.py` (530 LOC, 3 funcs, 0 classes)
- `def _validate_paths_sync(paths, project_root, tier, capabilities)` L20 — Synchronous implementation of validate_paths.
- `def _verify_policy_integrity_sync(policy_dir, manifest_source, tier, capabilities)` L260 — Synchronous implementation of policy integrity verification.
- `def _code_policy_check_sync(paths, rules, compliance_standards, generate_report)` L448 — Synchronous implementation of code_policy_check.

#### `mcp/helpers/polyglot_dispatch.py` (467 LOC, 3 funcs, 0 classes)
- `def call_parser_method(parser, method_name, file_path, call_style)` L38 — Unified adapter for per-language execute-method calling conventions.
- `def dispatch_tools(tools, registry, exec_map, file_path)` L72 — Enterprise-gate + exception-handling dispatch loop.
- `def run_static_tools(file_path, tools, tier)` L132 — Synchronously dispatch to every supported language's tool parsers.

#### `mcp/helpers/security_helpers.py` (3470 LOC, 49 funcs, 0 classes)
- `def _get_cache()` L70 — 
- `def _get_project_root()` L80 — Get the server's PROJECT_ROOT dynamically.
- `def _get_current_tier()` L94 — Return the current licensing tier, defaulting to community on failure.
- `def _validate_code(code)` L109 — Validate code before analysis.
- `def _get_sink_detector()` L123 — 
- `def validate_path_security(path, project_root)` L130 — Validate path is within allowed roots and return resolved path.
- `def _unified_sink_detect_sync(code, language, confidence_threshold, tier)` L150 — Synchronous unified sink detection wrapper.
- `def _sink_coverage_summary(detector)` L490 — Compute coverage summary across languages.
- `def _get_cwe_from_sink_type(sink_type)` L507 — [20251220_FEATURE] v3.0.4 - Map sink types to CWE IDs.
- `def _get_cwe_for_sink(vulnerability_type, sink_type)` L536 — Map vulnerability/sink type to CWE identifier.
- `def _analyze_sink_context(code, sinks, language)` L569 — [20251231_FEATURE] Analyze context around detected sinks for Pro tier.
- `def _detect_framework_sinks(code, language)` L655 — [20251231_FEATURE] Detect framework-specific sinks for Pro tier.
- `def _build_sink_compliance_mapping(sinks)` L714 — [20251231_FEATURE] Map sinks to compliance standards for Enterprise tier.
- `def _build_historical_comparison(sinks)` L785 — [20251231_FEATURE] Build historical comparison for Enterprise tier.
- `def _generate_sink_remediation(sinks, language)` L824 — [20251231_FEATURE] Generate automated remediation suggestions for Enterprise tie
- `def _analyze_reachability(project_root)` L890 — Analyze Python files to find imported packages.
- `def _fetch_package_license(package_name, ecosystem)` L934 — Fetch license information from package registries.
- `def _check_license_compliance(license_str)` L966 — Check if license complies with organization policy.
- `def _check_typosquatting(package_name, ecosystem)` L999 — Check for potential typosquatting by comparing against popular packages.
- `def _calculate_supply_chain_risk(package_name, version, ecosystem, vulnerabilities)` L1068 — Calculate supply chain risk score for a dependency.
- `def _generate_compliance_report(dependencies, severity_summary, total_vulnerabilities, vulnerable_count)` L1111 — Generate compliance report for SOC2/ISO standards.
- `def _generate_compliance_recommendations(severity_summary, license_issues, typosquat_risks)` L1161 — Generate prioritized compliance recommendations.
- `def _extract_severity(vuln)` L1197 — Extract severity from OSV vulnerability data.
- `def _extract_fixed_version(vuln, package_name)` L1241 — Extract fixed version from OSV vulnerability data.
- `def _scan_dependencies_sync(project_root, path, scan_vulnerabilities, include_dev)` L1252 — Synchronous implementation of dependency vulnerability scanning.
- `def _security_scan_sync(code, file_path, tier, capabilities)` L1546 — Synchronous implementation of security_scan.
- `async def _unified_sink_detect_impl(code, language, confidence_threshold)` L2140 — Unified polyglot sink detection with confidence thresholds.
- `async def _type_evaporation_scan_impl(frontend_code, backend_code, frontend_file, backend_file)` L2196 — Detect Type System Evaporation vulnerabilities across TypeScript frontend and Py
- `async def _scan_dependencies_impl(path, project_root, scan_vulnerabilities, include_dev)` L2288 — Scan project dependencies for known vulnerabilities (A06:2021 - Vulnerable Compo
- `def _split_virtual_files(code)` L2362 — Split a single code string into virtual files using // FILE: markers.
- `def _enforce_file_limits(frontend_code, backend_code, max_files)` L2392 — Apply virtual file limits using // FILE: markers; return truncated code and warn
- `def _type_evaporation_scan_sync(frontend_code, backend_code, frontend_file, backend_file)` L2419 — Synchronous implementation of cross-file type evaporation analysis.
- `def _detect_implicit_any(code)` L2688 — [20251226_FEATURE] Detect implicit any from untyped .json() responses.
- `def _detect_network_boundaries(code)` L2728 — [20251226_FEATURE] Detect network call boundaries where types evaporate.
- `def _detect_library_boundaries(code)` L2762 — [20251226_FEATURE] Detect library call boundaries where external data enters.
- `def _detect_json_parse_locations(code)` L2795 — [20251226_FEATURE] Detect JSON.parse() calls without validation.
- `def _detect_boundary_violations(code, frontend_result)` L2819 — [20251226_FEATURE] Detect type violations at serialization boundaries.
- `def _generate_zod_schemas(type_definitions, matched_endpoints)` L2852 — [20251226_FEATURE] Generate Zod validation schemas from TypeScript types.
- `def _ts_type_to_zod(type_name, definition)` L2890 — [20251226_FEATURE] Convert TypeScript type definition to Zod schema.
- `def _extract_interface_fields(definition)` L2934 — Extract field name -> type mapping from interface definition.
- `def _ts_primitive_to_zod(ts_type)` L2949 — Convert TypeScript primitive to Zod validator.
- `def _generate_validation_code(schemas)` L2975 — [20251226_FEATURE] Generate complete validation code from schemas.
- `def _generate_pydantic_models(type_definitions, matched_endpoints)` L3016 — [20251226_FEATURE] Generate Pydantic models for Python backend validation.
- `def _ts_type_to_pydantic(type_name, definition)` L3044 — [20251226_FEATURE] Convert TypeScript type to Pydantic model.
- `def _ts_to_python_type(ts_type)` L3075 — Convert TypeScript type to Python type annotation.
- `def _validate_api_contract(frontend_result, backend_vulnerabilities, matched_endpoints)` L3094 — [20251226_FEATURE] Validate API contract between frontend and backend.
- `def _generate_remediation_suggestions(vulnerabilities, generated_schemas, pydantic_models)` L3153 — [20251231_FEATURE] Generate automated remediation suggestions for type evaporati
- `def _check_custom_type_rules(frontend_code, backend_code, custom_rules)` L3249 — [20251231_FEATURE] Check code against custom type rules.
- `def _generate_type_compliance_report(vulnerabilities, api_contract, custom_rule_violations, generated_schemas)` L3337 — [20251231_FEATURE] Generate type compliance validation report.

#### `mcp/helpers/session.py` (245 LOC, 7 funcs, 1 classes)
- **class SessionManager** (line 59, 7 methods) — Manages session state and audit logs.
- `def _get_project_root()` L32 — Get current project root for locating .code-scalpel.
- `def _get_persistent_audit_log()` L46 — Return disk-backed audit log in .code-scalpel/audit.log if available.
- `def get_session_update_count(tool_name)` L137 — Get the current update count for a tool.
- `def increment_session_update_count(tool_name)` L142 — Increment and return the update count for a tool.
- `def add_audit_entry(operation, details, outcome, user_id)` L149 — Add an audit trail entry.
- `def get_audit_trail()` L230 — Return a copy of the audit trail.
- `def _get_audit_trail()` L235 — Internal: return the actual audit trail list (not a copy).

#### `mcp/helpers/symbolic_helpers.py` (916 LOC, 11 funcs, 0 classes)
- `def _get_server()` L29 — 
- `def _detect_requested_constraint_types(code)` L49 — Best-effort extraction of constraint types implied by code.
- `def _basic_symbolic_analysis(code, max_paths)` L108 — Fallback symbolic analysis using AST inspection.
- `def _build_path_prioritization(paths, code, smart)` L171 — Build path prioritization metadata for Pro/Enterprise tier.
- `def _build_concolic_results(paths, code)` L218 — Build concolic execution results for Pro/Enterprise tier.
- `def _build_state_space_analysis(paths, constraints)` L248 — Build state space reduction analysis for Enterprise tier.
- `def _build_memory_model(code)` L295 — Build memory modeling results for Enterprise tier.
- `def _symbolic_execute_sync(code, max_paths, max_depth, constraint_types)` L349 — Synchronous implementation of symbolic_execute.
- `def _add_tier_features_to_result(result, code, caps_set)` L544 — Add tier-aware features to a SymbolicResult (including fallback results).
- `def _generate_tests_sync(code, file_path, function_name, framework)` L572 — Synchronous implementation of generate_unit_tests.
- `def _simulate_refactor_sync(original_code, new_code, patch, strict_mode)` L754 — Synchronous implementation of simulate_refactor.

#### `mcp/logging.py` (45 LOC, 1 funcs, 0 classes)
- `def _load_stdlib_logging()` L23 — 

#### `mcp/mcp_logging.py` (388 LOC, 5 funcs, 4 classes)
- **class ToolUsageStatsDict** (line 24, 0 methods) — Statistics about MCP tool usage.
- **class ToolStatsDict** (line 35, 0 methods) — Statistics for a specific MCP tool.
- **class ToolInvocation** (line 90, 0 methods) — [20251216_FEATURE] v2.2.0 - Record of a single MCP tool invocation.
- **class MCPAnalytics** (line 115, 5 methods) — [20251216_FEATURE] v2.2.0 - Analytics engine for MCP tool usage.
- `def get_analytics()` L269 — Get the global analytics instance.
- `def log_tool_invocation(tool_name, params)` L274 — [20251216_FEATURE] v2.2.0 - Log MCP tool invocation start.
- `def log_tool_success(tool_name, duration_ms, metrics)` L289 — [20251216_FEATURE] v2.2.0 - Log successful MCP tool execution.
- `def log_tool_error(tool_name, error, duration_ms, params)` L316 — [20251216_FEATURE] v2.2.0 - Log MCP tool execution error.
- `def _sanitize_params(params)` L364 — Sanitize parameters to remove sensitive data.

#### `mcp/metrics.py` (393 LOC, 2 funcs, 4 classes)
- **class SuggestionType** (line 26, 0 methods) — Categories of suggestions we can make.
- **class SuggestionOutcome** (line 37, 0 methods) — Outcomes for tracked suggestions.
- **class SuggestionMetric** (line 48, 2 methods) — Single suggestion event with metadata.
- **class MetricsCollector** (line 91, 7 methods) — Thread-safe collector for suggestion metrics.
- `def get_metrics_collector()` L372 — Get or create global metrics collector.
- `def set_metrics_persistence(path)` L380 — Configure persistence path for metrics.

#### `mcp/models/context.py` (277 LOC, 0 funcs, 5 classes)
- **class Language** (line 23, 0 methods) — Supported programming languages with tier-1 AST support.
- **class BaseContext** (line 41, 0 methods) — Abstract base context for all analysis operations.
- **class SourceContext** (line 51, 7 methods) — Unified representation of a single source file with provenance.
- **class ProjectContext** (line 178, 3 methods) — Unified representation of a project directory.
- **class FileMetadata** (line 256, 0 methods) — Metadata about a file (lightweight, no content).

#### `mcp/models/core.py` (1015 LOC, 0 funcs, 26 classes)
- **class FunctionInfo** (line 12, 0 methods) — Information about a function.
- **class ClassInfo** (line 23, 0 methods) — Information about a class.
- **class AnalysisResult** (line 36, 3 methods) — Result of code analysis.
- **class VulnerabilityInfo** (line 194, 0 methods) — Information about a detected vulnerability.
- **class SecurityResult** (line 204, 0 methods) — Result of security analysis.
- **class UnifiedDetectedSink** (line 256, 0 methods) — Detected sink with confidence and OWASP mapping.
- **class UnifiedSinkResult** (line 289, 0 methods) — Result of unified polyglot sink detection.
- **class PathCondition** (line 359, 0 methods) — A condition along an execution path.
- **class ExecutionPath** (line 366, 0 methods) — An execution path discovered by symbolic execution.
- **class SymbolicResult** (line 378, 0 methods) — Result of symbolic execution.
- **class GeneratedTestCase** (line 422, 0 methods) — A generated test case.
- **class TestGenerationResult** (line 434, 0 methods) — Result of test generation.
- **class RefactorSecurityIssue** (line 479, 0 methods) — A security issue found in refactored code.
- **class RefactorSimulationResult** (line 489, 0 methods) — Result of refactor simulation.
- **class CrawlFunctionInfo** (line 507, 0 methods) — Information about a function from project crawl.
- **class CrawlClassInfo** (line 515, 0 methods) — Information about a class from project crawl.
- **class CrawlFileResult** (line 526, 0 methods) — Result of analyzing a single file during crawl.
- **class CrawlSummary** (line 545, 0 methods) — Summary statistics from project crawl.
- **class ProjectCrawlResult** (line 557, 0 methods) — Result of crawling an entire project.
- **class SurgicalExtractionResult** (line 614, 0 methods) — Result of surgical code extraction.
- **class ContextualExtractionResult** (line 634, 0 methods) — Result of extraction with dependencies included.
- **class PatchResultModel** (line 704, 0 methods) — Result of a surgical code modification.
- **class FileContextResult** (line 749, 0 methods) — Result of get_file_context - file overview without full content.
- **class SymbolReference** (line 864, 0 methods) — A single reference to a symbol.
- **class SymbolDisambiguationCandidate** (line 889, 0 methods) — A structured candidate for resolving symbol ambiguity.
- **class SymbolReferencesResult** (line 909, 0 methods) — Result of get_symbol_references - all usages of a symbol.

#### `mcp/models/envelope.py` (242 LOC, 0 funcs, 2 classes)
- **class SchemaVersion** (line 23, 0 methods) — Versioned schema identifiers.
- **class ResponseEnvelope** (line 39, 5 methods) — Standardized response wrapper for all tool outputs.

#### `mcp/models/graph.py` (902 LOC, 0 funcs, 24 classes)
- **class CallContextModel** (line 12, 0 methods) — Context information about where a call is made.
- **class CallNodeModel** (line 33, 0 methods) — Node in the call graph representing a function.
- **class CallEdgeModel** (line 52, 0 methods) — Edge in the call graph representing a function call.
- **class CallGraphResultModel** (line 75, 0 methods) — Result of call graph analysis.
- **class NeighborhoodNodeModel** (line 158, 0 methods) — A node in the neighborhood subgraph.
- **class NeighborhoodEdgeModel** (line 169, 0 methods) — An edge in the neighborhood subgraph.
- **class GraphNeighborhoodResult** (line 178, 0 methods) — Result of k-hop neighborhood extraction.
- **class ModuleInfo** (line 260, 0 methods) — Information about a Python module/file.
- **class PackageInfo** (line 278, 0 methods) — Information about a Python package (directory with __init__.py).
- **class ProjectMapResult** (line 289, 14 methods) — Result of project map analysis.
- **class ImportNodeModel** (line 478, 0 methods) — Information about an import in the import graph.
- **class SymbolDefinitionModel** (line 490, 0 methods) — Information about a symbol defined in a file.
- **class ExtractedSymbolModel** (line 500, 0 methods) — An extracted symbol with its code and dependencies.
- **class AliasResolutionModel** (line 522, 0 methods) — Import alias resolution details (Pro tier).
- **class WildcardExpansionModel** (line 538, 0 methods) — Wildcard import expansion details (Pro tier).
- **class ReexportChainModel** (line 548, 0 methods) — Re-export chain information (Pro tier).
- **class ChainedAliasResolutionModel** (line 556, 0 methods) — Multi-hop alias resolution details (Pro tier).
- **class CouplingViolationModel** (line 572, 0 methods) — Coupling metric violation (Enterprise tier).
- **class ArchitecturalViolationModel** (line 589, 0 methods) — Architectural rule violation (Enterprise tier).
- **class BoundaryAlertModel** (line 604, 0 methods) — Layer boundary alert (Enterprise tier).
- **class CrossFileDependenciesResult** (line 614, 0 methods) — Result of cross-file dependency analysis.
- **class TaintFlowModel** (line 792, 0 methods) — Model for a taint flow across files.
- **class CrossFileVulnerabilityModel** (line 807, 0 methods) — Model for a cross-file vulnerability.
- **class CrossFileSecurityResult** (line 821, 0 methods) — Result of cross-file security analysis.

#### `mcp/models/policy.py` (189 LOC, 0 funcs, 3 classes)
- **class PathValidationResult** (line 12, 0 methods) — Result of path validation.
- **class PolicyVerificationResult** (line 78, 0 methods) — Result of cryptographic policy verification.
- **class CodePolicyCheckResult** (line 120, 0 methods) — Result model for code_policy_check tool.

#### `mcp/models/security.py` (326 LOC, 0 funcs, 7 classes)
- **class SecurityResult** (line 13, 0 methods) — Result of security analysis.
- **class TypeEvaporationResultModel** (line 64, 0 methods) — Result of type evaporation analysis.
- **class DependencyVulnerability** (line 138, 0 methods) — Represents a vulnerability detected in a dependency.
- **class DependencyInfo** (line 174, 0 methods) — Represents a scanned dependency with vulnerability info.
- **class DependencyScanResult** (line 226, 0 methods) — Comprehensive result of dependency scan with per-dependency grouping.
- **class VulnerabilityFindingModel** (line 272, 0 methods) — A vulnerability found in a dependency.
- **class DependencyScanResultModel** (line 294, 0 methods) — Result of a dependency vulnerability scan.

#### `mcp/models/tool_definition.py` (230 LOC, 0 funcs, 4 classes)
- **class Tier** (line 20, 0 methods) — License tiers supported by code-scalpel.
- **class CapabilitySpec** (line 29, 0 methods) — Specifies what a tool can do at a given tier.
- **class ToolDefinition** (line 44, 5 methods) — Unified metadata for an MCP tool.
- **class ToolDefinitionRegistry** (line 163, 5 methods) — Central registry for all tool definitions.

#### `mcp/module_resolver.py` (416 LOC, 17 funcs, 0 classes)
- `def _normalize_module_path(module)` L16 — Normalize language module notation into a relative path fragment.
- `def _resolve_by_extensions(module, project_root, extensions)` L21 — Resolve a module using a small set of file extensions and roots.
- `def resolve_module_path(language, module, project_root)` L49 — Resolve a module name to a file path for a given language.
- `def _resolve_python_module(module, project_root)` L107 — Resolve Python module name to file path.
- `def _resolve_javascript_module(module, project_root)` L141 — Resolve JavaScript module name to file path.
- `def _resolve_typescript_module(module, project_root)` L189 — Resolve TypeScript module name to file path.
- `def _resolve_java_module(module, project_root)` L241 — Resolve Java module name (fully qualified class name) to file path.
- `def _resolve_c_module(module, project_root)` L271 — Resolve C translation unit or header paths.
- `def _resolve_cpp_module(module, project_root)` L281 — Resolve C++ source or header paths.
- `def _resolve_csharp_module(module, project_root)` L291 — Resolve C# modules to .cs files.
- `def _resolve_go_module(module, project_root)` L301 — Resolve Go modules to .go files.
- `def _resolve_kotlin_module(module, project_root)` L311 — Resolve Kotlin modules to .kt or .kts files.
- `def _resolve_php_module(module, project_root)` L321 — Resolve PHP modules to .php family files.
- `def _resolve_ruby_module(module, project_root)` L332 — Resolve Ruby modules to .rb or related files.
- `def _resolve_swift_module(module, project_root)` L343 — Resolve Swift modules to .swift files.
- `def _resolve_rust_module(module, project_root)` L353 — Resolve Rust modules to .rs files.
- `def get_mime_type(language)` L364 — Get MIME type for a programming language.

#### `mcp/normalizers.py` (301 LOC, 4 funcs, 1 classes)
- **class InputNormalizationError** (line 31, 0 methods) — Raised when input normalization fails.
- `def validate_file_exists(file_path)` L37 — Validate that a file exists and is readable.
- `def read_file_content(file_path, encoding)` L63 — Read file content with proper error handling.
- `def check_file_size_limit(file_path, max_bytes)` L89 — Check if file size exceeds limit.
- `def normalize_input(tool_id, language_param)` L109 — Decorator that normalizes tool inputs into a SourceContext.

#### `mcp/oracle_middleware.py` (984 LOC, 3 funcs, 9 classes)
- **class RecoveryStrategy** (line 37, 1 methods) — Base class for oracle recovery strategies.
- **class SymbolStrategy** (line 54, 1 methods) — Recovery strategy for missing symbols (functions, classes, methods).
- **class PathStrategy** (line 140, 1 methods) — Recovery strategy for missing files/directories.
- **class SafetyStrategy** (line 202, 1 methods) — Recovery strategy for collision detection (rename conflicts).
- **class NodeIdFormatStrategy** (line 293, 1 methods) — Recovery strategy for invalid graph node ID formats.
- **class MethodNameFormatStrategy** (line 362, 1 methods) — Recovery strategy for invalid method name formats.
- **class RenameSymbolStrategy** (line 420, 1 methods) — Recovery strategy for rename operations.
- **class CompositeStrategy** (line 475, 3 methods) — Recovery strategy that chains multiple recovery strategies together.
- **class GenerateTestsStrategy** (line 934, 1 methods) — Recovery strategy for generate_unit_tests tool.
- `def with_oracle_resilience(tool_id, strategy)` L554 — Decorator that adds oracle resilience to MCP tools.
- `def _enhance_error_envelope(envelope, tool_id, strategy, kwargs)` L734 — Post-process error envelopes to add oracle suggestions.
- `def _enhance_data_error(envelope, tool_id, strategy, kwargs)` L823 — Post-process envelopes where error is in data.error field (Stage 2b).

#### `mcp/path_resolver.py` (597 LOC, 2 funcs, 2 classes)
- **class PathResolutionResult** (line 36, 0 methods) — Result of path resolution attempt.
- **class PathResolver** (line 46, 12 methods) — Intelligent path resolver for file-based operations.
- `def get_default_resolver()` L566 — Get or create the default PathResolver instance.
- `def resolve_path(path, project_root)` L581 — Convenience function for path resolution using default resolver.

#### `mcp/paths.py` (67 LOC, 4 funcs, 0 classes)
- `def resolve_file_path(path, check_exists)` L9 — Resolve file path to absolute Path object.
- `def scalpel_home_dir()` L28 — Return the Code Scalpel home directory under the user's home.
- `def env_truthy(value)` L36 — 
- `def maybe_auto_init_config_dir()` L40 — Optionally initialize config directory scaffolding.

#### `mcp/prompts.py` (128 LOC, 6 funcs, 0 classes)
- `def deep_security_audit(path)` L16 — Guide a comprehensive, multi-tool security audit.
- `def safe_refactor(file_path, symbol_name, goal)` L36 — Guide a safe refactor workflow with verification steps.
- `def modernize_legacy(path)` L58 — Guide modernization of legacy codebases.
- `def map_architecture(module_path)` L78 — Guide architectural mapping and dependency visualization.
- `def verify_supply_chain(project_root)` L97 — Guide a software supply chain verification workflow.
- `def explain_and_document(target)` L115 — Guide explanation and documentation of code or architecture.

#### `mcp/protocol.py` (227 LOC, 6 funcs, 0 classes)
- `def _normalize_tier(value)` L33 — Normalize tier string to canonical form.
- `def format_tier_for_display(tier)` L61 — Format a tier string for user-facing display with proper capitalization.
- `def _requested_tier_from_env()` L86 — Get requested tier from environment variables (for testing/downgrade).
- `def _get_current_tier()` L99 — Get the current tier from license validation with env var override.
- `def set_current_tier(tier)` L153 — Set the current tier (called by run_server).
- `def _load_prompts_if_needed()` L217 — Lazy load prompts on first access to avoid circular import.

#### `mcp/resources.py` (606 LOC, 13 funcs, 0 classes)
- `def _server()` L17 — 
- `def _run_in_thread(func)` L21 — 
- `async def get_project_call_graph()` L33 — Return the project-wide call graph as JSON.
- `async def get_project_dependencies()` L61 — Return detected project dependencies as JSON.
- `async def get_project_structure()` L75 — Return the project directory structure as JSON.
- `def get_version()` L107 — Get Code Scalpel version information.
- `def get_health()` L125 — Health check endpoint for Docker and orchestration systems.
- `def get_capabilities()` L150 — Get information about Code Scalpel's capabilities.
- `def get_file_resource(path)` L195 — Read file contents by path (Resource Template).
- `async def get_analysis_resource(path)` L225 — Get code analysis for a file by path.
- `def _extract_code_sync(target_type, target_name, file_path, code)` L274 — 
- `async def get_symbol_resource(file_path, symbol_name)` L370 — Extract a specific symbol (function/class) from a file (Resource Template).
- `async def get_code_resource(language, module, symbol)` L457 — Access code elements via parameterized URI (Resource Template).

#### `mcp/response_config.py` (392 LOC, 2 funcs, 2 classes)
- **class FilteredResponseDict** (line 17, 0 methods) — Filtered response data after applying configuration.
- **class ResponseConfig** (line 76, 13 methods) — Load and apply response configuration for token efficiency.
- `def get_response_config()` L363 — Get the global response configuration instance.
- `def filter_tool_response(data, tool_name, tier, is_error)` L371 — Filter tool response data for token efficiency.

#### `mcp/response_formatter.py` (409 LOC, 0 funcs, 2 classes)
- **class ResponseProfile** (line 36, 2 methods) — Configuration for a response detail profile.
- **class ResponseFormatter** (line 140, 7 methods) — Formats tool responses according to profiles.

#### `mcp/routers.py` (386 LOC, 0 funcs, 2 classes)
- **class LanguageDetectionResult** (line 26, 2 methods) — Result of language detection.
- **class LanguageRouter** (line 48, 8 methods) — Routes code to appropriate parsers based on language.

#### `mcp/server.py` (5283 LOC, 65 funcs, 30 classes)
- **class UnifiedDetectedSink** (line 483, 0 methods) — Detected sink with confidence and OWASP mapping.
- **class UnifiedSinkResult** (line 500, 0 methods) — Result of unified polyglot sink detection.
- **class CrawlFunctionInfo** (line 516, 0 methods) — Information about a function from project crawl.
- **class CrawlClassInfo** (line 524, 0 methods) — Information about a class from project crawl.
- **class CrawlFileResult** (line 535, 0 methods) — Result of analyzing a single file during crawl.
- **class CrawlSummary** (line 554, 0 methods) — Summary statistics from project crawl.
- **class ProjectCrawlResult** (line 566, 0 methods) — Result of crawling an entire project.
- **class SurgicalExtractionResult** (line 623, 0 methods) — Result of surgical code extraction.
- **class ContextualExtractionResult** (line 643, 0 methods) — Result of extraction with dependencies included.
- **class PatchResultModel** (line 677, 0 methods) — Result of a surgical code modification.
- **class FileContextResult** (line 709, 0 methods) — Result of get_file_context - file overview without full content.
- **class SymbolReference** (line 760, 0 methods) — A single reference to a symbol.
- **class SymbolReferencesResult** (line 772, 0 methods) — Result of get_symbol_references - all usages of a symbol.
- **class TypeEvaporationResultModel** (line 1320, 0 methods) — Result of type evaporation analysis.
- **class DependencyVulnerability** (line 1450, 0 methods) — A vulnerability associated with a specific dependency.
- **class DependencyInfo** (line 1470, 0 methods) — Information about a scanned dependency.
- **class DependencyScanResult** (line 1484, 0 methods) — Result of a dependency vulnerability scan with per-dependency details.
- **class VulnerabilityFindingModel** (line 1525, 0 methods) — A vulnerability found in a dependency.
- **class DependencyScanResultModel** (line 1547, 0 methods) — Result of a dependency vulnerability scan.
- **class ModuleInfo** (line 3402, 0 methods) — Information about a Python module/file.
- **class PackageInfo** (line 3420, 0 methods) — Information about a Python package (directory with __init__.py).
- **class ProjectMapResult** (line 3431, 0 methods) — Result of project map analysis.
- **class ImportNodeModel** (line 3772, 0 methods) — Information about an import in the import graph.
- **class SymbolDefinitionModel** (line 3784, 0 methods) — Information about a symbol defined in a file.
- **class ExtractedSymbolModel** (line 3794, 0 methods) — An extracted symbol with its code and dependencies.
- **class CrossFileDependenciesResult** (line 3816, 0 methods) — Result of cross-file dependency analysis.
- **class TaintFlowModel** (line 4205, 0 methods) — Model for a taint flow across files.
- **class CrossFileVulnerabilityModel** (line 4220, 0 methods) — Model for a cross-file vulnerability.
- **class CrossFileSecurityResult** (line 4234, 0 methods) — Result of cross-file security analysis.
- **class PathValidationResult** (line 4512, 0 methods) — Result of path validation.
- `def get_project_root()` L95 — Get the current project root.
- `def set_project_root(path)` L100 — Set the project root (called by main()).
- `def _configure_logging(transport)` L112 — Configure logging based on transport type.
- `def _debug_print(msg)` L141 — Print debug output only when explicitly requested.
- `def _normalize_tier(value)` L162 — Normalize tier string to canonical form.
- `def _requested_tier_from_env()` L174 — Get requested tier from environment variables for downgrade testing.
- `def _get_current_tier()` L185 — Get the current tier from license validation with env var override.
- `def auto_init_if_enabled(project_root, tier, enabled, mode)` L273 — Auto-initialize .code-scalpel/ if enabled via env.
- `def _get_cached_ast(file_path)` L337 — Get cached AST for a file if it hasn't changed.
- `def _cache_ast(file_path, tree)` L347 — Cache a parsed AST for a file.
- `def _parse_file_cached(file_path)` L366 — Parse a Python file with caching.
- `def _get_sink_detector()` L386 — Get or create singleton UnifiedSinkDetector.
- `def _get_cached_graph(project_root)` L406 — Get cached UniversalGraph for project if still valid.
- `def _cache_graph(project_root, graph)` L423 — Cache a UniversalGraph for a project.
- `def _invalidate_graph_cache(project_root)` L432 — Invalidate graph cache for a project or all projects.
- `def _is_path_allowed(path)` L444 — Check if a path is within allowed roots.
- `def _validate_path_security(path)` L471 — Validate a path against configured security roots.
- `def _validate_code(code)` L823 — Validate code before analysis.
- `def _count_complexity(tree)` L834 — Estimate cyclomatic complexity.
- `def _analyze_clike_code(code, language)` L845 — Delegate C/C++/C# analysis to helper implementation (single source of truth).
- `def _analyze_java_code(code)` L850 — Delegate Java analysis to helper implementation (single source of truth).
- `def _analyze_javascript_code(code, is_typescript)` L856 — Delegate JavaScript/TypeScript analysis to helper implementation.
- `def _walk_ts_tree(node)` L862 — Generator to walk all nodes in a tree-sitter tree.
- `def _analyze_code_sync(code, language)` L869 — Delegate analyze_code to the shared helper implementation.
- `def _security_scan_sync(code, file_path)` L1004 — Synchronous implementation of security_scan.
- `def _get_cwe_from_sink_type(sink_type)` L1197 — [20251220_FEATURE] v3.0.4 - Map sink types to CWE IDs.
- `def _sink_coverage_summary(detector)` L1232 — Compute coverage summary across languages.
- `def _unified_sink_detect_sync(code, language, min_confidence)` L1249 — Synchronous unified sink detection wrapper.
- `def _type_evaporation_scan_sync(frontend_code, backend_code, frontend_file, backend_file)` L1356 — Synchronous implementation of cross-file type evaporation analysis.
- `def _scan_dependencies_sync(project_root, path, scan_vulnerabilities, include_dev)` L1586 — Synchronous implementation of dependency vulnerability scanning.
- `def _extract_severity(vuln)` L1745 — Extract severity from OSV vulnerability data.
- `def _extract_fixed_version(vuln, package_name)` L1800 — Extract fixed version from OSV vulnerability data.
- `def _scan_dependencies_sync_legacy(path, timeout)` L1811 — Synchronous implementation of dependency vulnerability scanning.
- `def _basic_security_scan(code)` L1904 — Fallback security scan using pattern matching.
- `def _symbolic_execute_sync(code, max_paths)` L1972 — Synchronous implementation of symbolic_execute.
- `def _basic_symbolic_analysis(code)` L2079 — Fallback symbolic analysis using AST inspection.
- `def _generate_tests_sync(code, file_path, function_name, framework)` L2139 — Synchronous implementation of generate_unit_tests.
- `def _simulate_refactor_sync(original_code, new_code, patch, strict_mode)` L2235 — Synchronous implementation of simulate_refactor.
- `def _crawl_project_discovery(root_path, exclude_dirs)` L2302 — Discovery-only crawl for Community tier.
- `def _crawl_project_sync(root_path, exclude_dirs, complexity_threshold, include_report)` L2463 — Synchronous implementation of crawl_project.
- `def _extraction_error(target_name, error)` L2558 — Create a standardized error result for extraction failures.
- `async def _extract_polyglot(target_type, target_name, file_path, code)` L2570 — [20251214_FEATURE] v2.0.0 - Multi-language extraction using PolyglotExtractor.
- `def _create_extractor(file_path, code, target_name)` L2645 — Create a SurgicalExtractor from file_path or code.
- `def _extract_method(extractor, target_name)` L2684 — Extract a method, handling the ClassName.method_name parsing.
- `def _perform_extraction(extractor, target_type, target_name, include_context)` L2694 — Perform the actual extraction based on target type and options.
- `def _process_cross_file_context(cross_file_result)` L2761 — Process cross-file resolution results into context_code and context_items.
- `def _build_full_code(imports_needed, context_code, target_code)` L2785 — Build the combined full_code for LLM consumption.
- `def _extract_code_sync(target_type, target_name, file_path, code)` L2798 — 
- `def _get_file_context_sync(file_path)` L2876 — Synchronous implementation of get_file_context.
- `def _count_complexity_node(node)` L3060 — Count cyclomatic complexity for a single node.
- `def _get_symbol_references_sync(symbol_name, project_root)` L3074 — Synchronous implementation of get_symbol_references.
- `def _get_call_graph_sync(project_root, entry_point, depth, include_circular_import_check)` L3219 — Synchronous implementation of get_call_graph.
- `def _generate_neighborhood_mermaid(nodes, edges, center_node_id)` L3266 — Generate Mermaid diagram for neighborhood.
- `def _normalize_graph_center_node_id(center_node_id)` L3302 — Normalize common legacy node-id formats into canonical IDs.
- `def _fast_validate_python_function_node_exists(root_path, center_node_id)` L3345 — Best-effort fast validation for python::<module>::function::<name>.
- `def _get_project_map_sync(project_root, include_complexity, complexity_threshold, include_circular_check)` L3501 — Synchronous implementation of get_project_map.
- `def _get_cross_file_dependencies_sync(target_file, target_symbol, project_root, max_depth)` L3890 — Synchronous implementation of get_cross_file_dependencies.
- `def _cross_file_security_scan_sync(project_root, entry_points, max_depth, include_diagram)` L4321 — Synchronous implementation of cross_file_security_scan.
- `def _validate_paths_sync(paths, project_root)` L4549 — Synchronous implementation of validate_paths.
- `def _verify_policy_integrity_sync(policy_dir, manifest_source, tier, capabilities)` L4585 — Synchronous implementation of policy integrity verification.
- `def _spawn_update_check(output)` L4611 — Spawn a background thread to check PyPI for a newer version.
- `def run_server(transport, host, port, allow_lan)` L4649 — Run the Code Scalpel MCP server.
- `def _apply_tier_tool_filter(tier)` L4935 — Apply tier-based limits to tool responses.
- `def _register_http_health_endpoint(mcp_instance, host, port, ssl_certfile)` L4956 — Register a simple HTTP/HTTPS /health endpoint for Docker health checks.
- `def _get_audit_trail()` L5202 — Return the session audit trail.

#### `mcp/tools/__init__.py` (20 LOC, 1 funcs, 0 classes)
- `def register_tools()` L8 — Import tool modules to trigger MCP registration.

#### `mcp/tools/analyze.py` (660 LOC, 5 funcs, 0 classes)
- `def _run_static_tools(file_path, tools, tier)` L31 — Synchronously dispatch to language tool parsers and return merged findings.
- `def _dispatch_tools(tools, registry, exec_map, file_path)` L328 — [20260305_REFACTOR] Thin wrapper — delegates to polyglot_dispatch.dispatch_tools
- `def _get_project_files(project_root, max_files)` L342 — Get list of all files in project for fuzzy matching suggestions.
- `def _find_similar_file_paths(invalid_path, project_files, max_suggestions)` L398 — Find similar file paths using fuzzy string matching.
- `async def analyze_code(code, language, file_path, static_tools)` L466 — Analyze source code structure with AST parsing and metrics.

#### `mcp/tools/context.py` (309 LOC, 3 funcs, 0 classes)
- `async def crawl_project(root_path, exclude_dirs, complexity_threshold, include_report)` L28 — Crawl a project directory and analyze Python files.
- `async def get_file_context(file_path)` L122 — Get a file overview without reading full content.
- `async def get_symbol_references(symbol_name, project_root, scope_prefix, include_tests)` L210 — Find all references to a symbol across the project.

#### `mcp/tools/extraction.py` (387 LOC, 3 funcs, 0 classes)
- `async def extract_code(target_type, target_name, file_path, code)` L37 — Extract code elements with optional dependency context.
- `async def rename_symbol(file_path, target_type, target_name, new_name)` L183 — Safely rename a function, class, or method in a file.
- `async def update_symbol(file_path, target_type, target_name, new_code)` L270 — Safely replace a function, class, or method in a file.

#### `mcp/tools/graph.py` (714 LOC, 6 funcs, 0 classes)
- `def _get_current_tier()` L31 — Get current tier using JWT validation (late import to avoid circular dependency)
- `async def _get_call_graph_tool(project_root, entry_point, depth, include_circular_import_check)` L38 — Build a call graph showing function relationships in the project.
- `async def _get_graph_neighborhood_tool(center_node_id, k, max_nodes, direction)` L166 — Extract k-hop neighborhood subgraph around a center node.
- `async def _get_project_map_tool(project_root, include_complexity, complexity_threshold, include_circular_check)` L313 — Generate a comprehensive map of the project structure.
- `async def _get_cross_file_dependencies_tool(target_file, target_symbol, project_root, max_depth)` L469 — Analyze and extract cross-file dependencies for a symbol.
- `async def _cross_file_security_scan_tool(project_root, entry_points, max_depth, include_diagram)` L589 — Perform cross-file security analysis tracking taint flow across module boundarie

#### `mcp/tools/oracle.py` (213 LOC, 4 funcs, 0 classes)
- `def _get_limits_for_tier(tier)` L33 — Get scan limits for a given tier.
- `async def _write_perfect_code_impl(file_path, instruction)` L45 — Implementation of write_perfect_code (async wrapper).
- `def _write_perfect_code_sync(file_path, instruction)` L65 — Synchronous implementation of write_perfect_code.
- `async def write_perfect_code(file_path, instruction)` L125 — Internal Oracle pipeline function — NOT a public MCP tool.

#### `mcp/tools/policy.py` (286 LOC, 3 funcs, 0 classes)
- `async def validate_paths(paths, project_root)` L25 — Validate that paths are accessible before running file-based operations.
- `async def verify_policy_integrity(policy_dir, manifest_source)` L101 — Verify policy file integrity using cryptographic signatures.
- `async def code_policy_check(paths, rules, compliance_standards, generate_report)` L179 — Check code against style guides, best practices, and compliance standards.

#### `mcp/tools/security.py` (485 LOC, 4 funcs, 0 classes)
- `async def unified_sink_detect(code, language, confidence_threshold)` L28 — Detect polyglot security sinks with confidence thresholds.
- `async def type_evaporation_scan(frontend_code, backend_code, frontend_file_path, backend_file_path)` L139 — Detect Type System Evaporation vulnerabilities across frontend/backend.
- `async def scan_dependencies(path, project_root, scan_vulnerabilities, include_dev)` L299 — Scan project dependencies for known vulnerabilities.
- `async def security_scan(code, file_path, confidence_threshold)` L403 — Scan code for security vulnerabilities using taint analysis.

#### `mcp/tools/static_analysis.py` (310 LOC, 4 funcs, 0 classes)
- `def _run_static_analysis_sync(language, paths, tool, report_path)` L43 — Run the appropriate tool parser and return structured findings.
- `def _parse_report(parser, tool_key, report_path)` L166 — Dispatch to the correct parse_*_report method based on tool key.
- `def _finding_to_dict(finding)` L189 — Convert a dataclass/object finding to a plain dict.
- `async def run_static_analysis(paths, tool, language, report_path)` L219 — Run polyglot static-analysis tools and return structured findings.

#### `mcp/tools/symbolic.py` (429 LOC, 3 funcs, 0 classes)
- `async def symbolic_execute(code, max_paths, max_depth)` L39 — Perform symbolic execution on Python code.
- `async def generate_unit_tests(code, file_path, function_name, framework)` L154 — Generate unit tests from code using symbolic execution.
- `async def simulate_refactor(original_code, new_code, patch, strict_mode)` L339 — Simulate applying a code change and check for safety issues.

#### `mcp/tools/system.py` (175 LOC, 1 funcs, 0 classes)
- `async def get_capabilities(tier, tool_name, ctx)` L22 — Get the capabilities available for the current license tier.

#### `mcp/v1_1_kernel_adapter.py` (213 LOC, 1 funcs, 1 classes)
- **class AnalyzeCodeKernelAdapter** (line 25, 4 methods) — Bridges Phase 6 Kernel to analyze_code tool.
- `def get_adapter()` L202 — Get or create global adapter instance.

#### `mcp/validators/core.py` (578 LOC, 1 funcs, 6 classes)
- **class ScopedSymbol** (line 31, 1 methods) — A symbol with scope and export information.
- **class ValidationError** (line 56, 1 methods) — Raised when validation detects a semantic error.
- **class ScopeTrackingVisitor** (line 64, 4 methods) — Tracks parent scope of functions and classes using a stack.
- **class SymbolExtractor** (line 142, 3 methods) — Shallow scanner to extract symbols from code without full parsing.
- **class SemanticValidator** (line 355, 4 methods) — Validates code references against actual symbols using weighted scoring.
- **class StructuralValidator** (line 519, 2 methods) — Validates structural properties of code.
- `def get_symbol_validator()` L567 — Get the global symbol validator instance.

#### `mcp/validators/weighted_scorer.py` (177 LOC, 0 funcs, 2 classes)
- **class ScoredCandidate** (line 19, 1 methods) — A symbol with its match score and diagnostic metadata.
- **class WeightedSymbolMatcher** (line 54, 2 methods) — Calculates match scores using weighted heuristics.

#### `mcp/version_check.py` (86 LOC, 3 funcs, 0 classes)
- `def get_latest_pypi_version()` L14 — Fetch the latest version of codescalpel from PyPI.
- `def check_version_mismatch()` L29 — Check if the current version matches the latest on PyPI.
- `def start_version_check_thread()` L83 — Start the version check in a background thread so it doesn't block startup.

### 4.oracle `oracle/` — 2 functions, 15 classes

#### `oracle/constraint_analyzer.py` (261 LOC, 0 funcs, 1 classes)
- **class ConstraintAnalyzer** (line 26, 9 methods) — Analyzes graphs and architectural constraints.

#### `oracle/models/__init__.py` (179 LOC, 0 funcs, 11 classes)
- **class FunctionSignature** (line 17, 0 methods) — Extracted function signature.
- **class ClassSignature** (line 29, 0 methods) — Extracted class signature.
- **class ImportStatement** (line 40, 0 methods) — Extracted import statement.
- **class SymbolTable** (line 49, 0 methods) — Extracted symbol table from a file.
- **class CallEdge** (line 65, 0 methods) — An edge in the call/dependency graph.
- **class GraphConstraints** (line 74, 0 methods) — Graph-based constraints for a file.
- **class TopologyRule** (line 85, 0 methods) — An architectural topology rule.
- **class TopologyViolation** (line 96, 0 methods) — A violation of an architectural rule.
- **class CodeContext** (line 112, 0 methods) — Relevant code context for the constraint spec.
- **class ConstraintSpec** (line 122, 0 methods) — Complete constraint specification for code generation.
- **class MarkdownSpec** (line 160, 1 methods) — A constraint spec in Markdown format for LLM consumption.

#### `oracle/oracle_pipeline.py` (226 LOC, 2 funcs, 1 classes)
- **class OraclePipeline** (line 30, 4 methods) — Serverless constraint injection pipeline.
- `async def generate_constraint_spec_async(repo_root, file_path, instruction, tier)` L172 — Generate constraint spec asynchronously.
- `def generate_constraint_spec_sync(repo_root, file_path, instruction, tier)` L204 — Generate constraint spec synchronously.

#### `oracle/spec_generator.py` (273 LOC, 0 funcs, 1 classes)
- **class SpecGenerator** (line 27, 5 methods) — Generates constraint specifications in Markdown format.

#### `oracle/symbol_extractor.py` (263 LOC, 0 funcs, 1 classes)
- **class SymbolExtractor** (line 23, 8 methods) — Extracts function/class signatures from Python ASTs.

### 4.parsing `parsing/` — 5 functions, 3 classes

#### `parsing/unified_parser.py` (293 LOC, 5 funcs, 3 classes)
- **class SanitizationReport** (line 21, 0 methods) — Report of code modifications during parsing.
- **class ParsingConfig** (line 31, 0 methods) — Parsing configuration from response_config.json.
- **class ParsingError** (line 40, 1 methods) — Raised when code cannot be parsed deterministically.
- `def _load_parsing_config()` L55 — Load parsing configuration from response_config.json.
- `def parse_python_code(code)` L85 — Parse Python code with deterministic error handling.
- `def parse_javascript_code(code)` L220 — Parse JavaScript/TypeScript with tree-sitter and error validation.
- `def _find_first_error_node(node)` L279 — Recursively find first ERROR node in tree-sitter tree.
- `def get_parsing_config()` L291 — Get current parsing configuration.

### 4.pdg_tools `pdg_tools/` — 6 functions, 20 classes

#### `pdg_tools/analyzer.py` (625 LOC, 0 funcs, 4 classes)
- **class DependencyType** (line 10, 0 methods) — Types of dependencies in the PDG.
- **class DataFlowAnomaly** (line 21, 0 methods) — Represents a data flow anomaly in the code.
- **class SecurityVulnerability** (line 32, 0 methods) — Represents a security vulnerability in the code.
- **class PDGAnalyzer** (line 43, 51 methods) — Advanced Program Dependence Graph Analyzer.

#### `pdg_tools/builder.py` (505 LOC, 1 funcs, 3 classes)
- **class NodeType** (line 10, 0 methods) — Types of nodes in the PDG.
- **class Scope** (line 27, 1 methods) — Represents a scope in the code.
- **class PDGBuilder** (line 41, 23 methods) — Enhanced Program Dependence Graph Builder.
- `def build_pdg(code, track_constants, interprocedural)` L490 — Build a Program Dependence Graph from Python code.

#### `pdg_tools/slicer.py` (387 LOC, 1 funcs, 4 classes)
- **class SliceType** (line 9, 0 methods) — Types of program slices.
- **class SlicingCriteria** (line 22, 0 methods) — Criteria for program slicing.
- **class SliceInfo** (line 34, 0 methods) — Information about a program slice.
- **class ProgramSlicer** (line 45, 22 methods) — Advanced program slicer with multiple slicing strategies.
- `def compute_slice(pdg, node, backward, criteria)` L373 — Convenience function to compute a program slice.

#### `pdg_tools/transformer.py` (634 LOC, 0 funcs, 3 classes)
- **class TransformationType** (line 11, 0 methods) — Types of PDG transformations.
- **class TransformationResult** (line 24, 0 methods) — Result of a PDG transformation.
- **class PDGTransformer** (line 35, 27 methods) — Advanced PDG transformer with optimization and refactoring capabilities.

#### `pdg_tools/utils.py` (318 LOC, 4 funcs, 3 classes)
- **class NodeInfo** (line 12, 0 methods) — Information about a PDG node.
- **class DependencyType** (line 24, 0 methods) — Types of dependencies in the PDG.
- **class PDGUtils** (line 34, 17 methods) — Utility functions for working with Program Dependence Graphs.
- `def get_node_info(pdg, node)` L301 — Convenience function to get node information.
- `def find_paths(pdg, source, target)` L306 — Convenience function to find paths between nodes.
- `def export_pdg(pdg, filepath)` L311 — Convenience function to export PDG.
- `def import_pdg(filepath)` L316 — Convenience function to import PDG.

#### `pdg_tools/visualizer.py` (573 LOC, 0 funcs, 3 classes)
- **class VisualizationFormat** (line 11, 0 methods) — Supported visualization output formats.
- **class VisualizationConfig** (line 21, 0 methods) — Configuration for PDG visualization.
- **class PDGVisualizer** (line 38, 25 methods) — Advanced PDG visualizer with customization and multiple output formats.

### 4.policy_engine `policy_engine/` — 12 functions, 39 classes

#### `policy_engine/__init__.py` (169 LOC, 1 funcs, 0 classes)
- `def __getattr__(name)` L81 — Lazy-load YAML/OPA-dependent policy engine symbols.

#### `policy_engine/audit_log.py` (223 LOC, 0 funcs, 1 classes)
- **class AuditLog** (line 22, 7 methods) — Tamper-resistant audit logging with HMAC signatures.

#### `policy_engine/code_policy_check/analyzer.py` (1196 LOC, 0 funcs, 1 classes)
- **class CodePolicyChecker** (line 55, 22 methods) — Main code policy checking engine.

#### `policy_engine/code_policy_check/models.py` (438 LOC, 0 funcs, 13 classes)
- **class PolicyViolationDict** (line 20, 0 methods) — Policy violation dictionary for JSON serialization.
- **class BestPracticeViolationDict** (line 34, 0 methods) — Best practice violation dictionary for JSON serialization.
- **class ViolationSeverity** (line 47, 0 methods) — Severity levels for policy violations.
- **class PolicyViolation** (line 57, 1 methods) — Represents a single policy violation found in code.
- **class BestPracticeViolation** (line 90, 1 methods) — Represents a best practice violation (Pro tier).
- **class PatternMatch** (line 121, 1 methods) — Represents a matched pattern (Pro tier custom rules).
- **class SecurityWarning** (line 146, 1 methods) — Represents a security-related warning (Pro tier).
- **class ComplianceReport** (line 175, 1 methods) — Represents a compliance audit report (Enterprise tier).
- **class AuditEntry** (line 202, 1 methods) — Represents an audit trail entry (Enterprise tier).
- **class Certification** (line 233, 1 methods) — Represents a compliance certification (Enterprise tier).
- **class ReportConfig** (line 260, 2 methods) — Organization-specific configuration for compliance PDF reports (Enterprise tier)
- **class CodePolicyResult** (line 342, 1 methods) — Complete result from code policy check.
- **class CustomRule** (line 413, 1 methods) — Represents a custom rule definition (Pro tier).

#### `policy_engine/code_policy_check/patterns.py` (869 LOC, 2 funcs, 2 classes)
- **class PatternCategory** (line 23, 0 methods) — Categories of patterns.
- **class PatternDefinition** (line 34, 0 methods) — Defines a pattern to detect in code.
- `def get_patterns_for_tier(tier)` L809 — Get all applicable patterns for a tier level.
- `def get_compliance_patterns(standards)` L842 — Get patterns for specific compliance standards.

#### `policy_engine/code_policy_check/policy_loader.py` (166 LOC, 7 funcs, 0 classes)
- `def find_policy_file(start_dir)` L26 — 
- `def load_policy_file(path)` L37 — 
- `def compute_policy_hash(policy)` L44 — 
- `def _merge_lists_unique(base, extra)` L50 — 
- `def merge_policies(base, override)` L66 — Merge two policy dicts.
- `def resolve_policy(policy, policy_dir)` L98 — Resolve a policy with inheritance via `extends`.
- `def load_effective_policy(start_dir)` L156 — Load policy if present and return (policy, policy_path, policy_hash).

#### `policy_engine/code_policy_check/report_builder.py` (1151 LOC, 0 funcs, 1 classes)
- **class ComplianceReportBuilder** (line 75, 14 methods) — Builds a professionally branded compliance PDF report.

#### `policy_engine/code_policy_check/templates.py` (43 LOC, 1 funcs, 0 classes)
- `def get_policy_template(name)` L42 — 

#### `policy_engine/crypto_verify.py` (601 LOC, 1 funcs, 4 classes)
- **class SecurityError** (line 36, 0 methods) — Raised when cryptographic verification fails.
- **class PolicyManifest** (line 43, 0 methods) — Signed manifest for policy files.
- **class VerificationResult** (line 65, 0 methods) — Result of cryptographic policy verification.
- **class CryptographicPolicyVerifier** (line 86, 12 methods) — Verify policy files against cryptographically signed manifests.
- `def verify_policy_integrity_crypto(policy_dir)` L571 — Verify policy integrity using cryptographic verification.

#### `policy_engine/exceptions.py` (35 LOC, 0 funcs, 5 classes)
- **class PolicyEngineError** (line 8, 0 methods) — Base exception for policy engine errors.
- **class TamperDetectedError** (line 14, 0 methods) — Raised when policy file tampering is detected.
- **class PolicyModificationError** (line 20, 0 methods) — Raised when agent attempts to modify protected policy files.
- **class OverrideTimeoutError** (line 26, 0 methods) — Raised when human override request times out.
- **class InvalidOverrideCodeError** (line 32, 0 methods) — Raised when invalid override code is provided.

#### `policy_engine/models.py` (12 LOC, 0 funcs, 1 classes)
- **class HumanResponse** (line 6, 0 methods) — Represents a human's response to an override challenge.

#### `policy_engine/policy_engine.py` (885 LOC, 0 funcs, 9 classes)
- **class PolicyError** (line 38, 0 methods) — Raised when policy loading, parsing, or evaluation fails.
- **class PolicySeverity** (line 44, 0 methods) — Severity levels for policy violations.
- **class PolicyAction** (line 54, 0 methods) — Actions to take when policy is violated.
- **class Policy** (line 63, 1 methods) — A single policy definition.
- **class PolicyViolation** (line 106, 0 methods) — A detected policy violation.
- **class PolicyDecision** (line 126, 0 methods) — Result of policy evaluation.
- **class Operation** (line 152, 0 methods) — An operation to be evaluated against policies.
- **class OverrideDecision** (line 179, 0 methods) — Result of override request.
- **class PolicyEngine** (line 203, 20 methods) — OPA/Rego policy enforcement engine.

#### `policy_engine/semantic_analyzer.py` (719 LOC, 0 funcs, 1 classes)
- **class SemanticAnalyzer** (line 33, 19 methods) — Semantic analysis for policy enforcement.

#### `policy_engine/tamper_resistance.py` (380 LOC, 0 funcs, 1 classes)
- **class TamperResistance** (line 25, 11 methods) — Tamper-resistant policy enforcement.

### 4.polyglot `polyglot/` — 13 functions, 27 classes

#### `polyglot/alias_resolver.py` (333 LOC, 1 funcs, 1 classes)
- **class AliasResolver** (line 9, 9 methods) — [20251216_FEATURE] Resolver for module aliases from various config files.
- `def create_alias_resolver(project_root)` L318 — Create an alias resolver for a project.

#### `polyglot/contract_breach_detector.py` (332 LOC, 1 funcs, 7 classes)
- **class BreachType** (line 8, 0 methods) — Types of contract breaches.
- **class Severity** (line 19, 0 methods) — Severity levels for contract breaches.
- **class ContractBreach** (line 29, 0 methods) — [20251216_FEATURE] Represents a contract breach between server and client.
- **class Edge** (line 60, 0 methods) — [20251216_FEATURE] Represents a dependency edge in the unified graph.
- **class Node** (line 72, 0 methods) — [20251216_FEATURE] Represents a node in the unified graph.
- **class UnifiedGraph** (line 84, 6 methods) — [20251216_FEATURE] Simplified unified graph for contract breach detection.
- **class ContractBreachDetector** (line 118, 6 methods) — [20251216_FEATURE] Detect contract breaches when a node changes.
- `def detect_breaches(graph, changed_node_id, min_confidence)` L313 — Detect contract breaches for a changed node.

#### `polyglot/extractor.py` (770 LOC, 3 funcs, 3 classes)
- **class Language** (line 35, 0 methods) — Supported programming languages.
- **class PolyglotExtractionResult** (line 102, 0 methods) — Result of polyglot code extraction.
- **class PolyglotExtractor** (line 262, 18 methods) — Multi-language code extractor.
- `def detect_language(file_path, code)` L126 — Detect the programming language from file extension or content.
- `def extract_from_file(file_path, target_type, target_name, language)` L732 — Extract code element from a file.
- `def extract_from_code(code, target_type, target_name, language)` L754 — Extract code element from source string.

#### `polyglot/tsx_analyzer.py` (182 LOC, 4 funcs, 1 classes)
- **class ReactComponentInfo** (line 21, 0 methods) — Metadata about a React component.
- `def detect_server_directive(code)` L31 — Detect React Server directive in code.
- `def has_jsx_syntax(code)` L54 — Detect JSX syntax in code.
- `def is_react_component(node, code)` L89 — Detect if a function or class is a React component.
- `def normalize_jsx_syntax(code)` L161 — Normalize JSX syntax for consistent analysis.

#### `polyglot/typescript/analyzer.py` (379 LOC, 2 funcs, 4 classes)
- **class TSAnalysisResult** (line 28, 0 methods) — Result of TypeScript/JavaScript code analysis.
- **class TypeScriptAnalyzer** (line 58, 6 methods) — Analyzer for TypeScript and JavaScript code.
- **class NormalizedFunction** (line 304, 0 methods) — Normalized function representation for cross-language analysis.
- **class NormalizedClass** (line 329, 0 methods) — Normalized class representation for cross-language analysis.
- `def normalize_typescript_function(ts_func)` L349 — Convert TypeScript function dict to normalized representation.
- `def normalize_typescript_class(ts_class)` L363 — Convert TypeScript class dict to normalized representation.

#### `polyglot/typescript/decorator_analyzer.py` (313 LOC, 1 funcs, 1 classes)
- **class DecoratorAnalyzer** (line 49, 5 methods) — [20251216_FEATURE] Analyzer for TypeScript decorators.
- `def extract_decorators_from_code(code)` L294 — Extract decorators from TypeScript code.

#### `polyglot/typescript/parser.py` (435 LOC, 0 funcs, 5 classes)
- **class TSNodeType** (line 35, 0 methods) — TypeScript/JavaScript AST node types (ESTree-compatible subset).
- **class Decorator** (line 78, 0 methods) — Represents a TypeScript decorator.
- **class TSNode** (line 96, 0 methods) — Represents a node in the TypeScript AST.
- **class TSParseResult** (line 117, 0 methods) — Result of parsing TypeScript/JavaScript code.
- **class TypeScriptParser** (line 132, 6 methods) — Parser for TypeScript and JavaScript source code.

#### `polyglot/typescript/type_narrowing.py` (716 LOC, 1 funcs, 5 classes)
- **class NarrowedType** (line 55, 0 methods) — Types that a variable can be narrowed to.
- **class TypeGuard** (line 95, 0 methods) — Represents a detected type guard in code.
- **class BranchState** (line 109, 2 methods) — Type state within a specific branch.
- **class NarrowingResult** (line 127, 0 methods) — Result of type narrowing analysis.
- **class TypeNarrowing** (line 137, 16 methods) — Analyze TypeScript control flow for type narrowing.
- `def analyze_type_narrowing(code)` L690 — Convenience function to analyze type narrowing in code.

### 4.quality_assurance `quality_assurance/` — 2 functions, 7 classes

#### `quality_assurance/error_fixer.py` (251 LOC, 1 funcs, 3 classes)
- **class FixResult** (line 34, 0 methods) — Result of a single fix operation.
- **class FixResults** (line 45, 1 methods) — Results from fixing a batch of files.
- **class ErrorFixer** (line 65, 4 methods) — Automatic whitespace error fixer.
- `def main()` L225 — Command-line interface.

#### `quality_assurance/error_scanner.py` (957 LOC, 1 funcs, 4 classes)
- **class ErrorSeverity** (line 54, 0 methods) — Error severity levels.
- **class CodeError** (line 63, 2 methods) — Represents a single code error.
- **class ScanResults** (line 88, 6 methods) — Results from a comprehensive scan.
- **class ErrorScanner** (line 145, 13 methods) — Comprehensive project error scanner.
- `def main()` L889 — Command-line interface for error scanning.

### 4.refactor `refactor/` — 0 functions, 12 classes

#### `refactor/build_verifier.py` (334 LOC, 0 funcs, 3 classes)
- **class BuildResultDict** (line 21, 0 methods) — Build verification result dictionary.
- **class BuildResult** (line 37, 0 methods) — Result of build verification.
- **class BuildVerifier** (line 49, 6 methods) — Verifies refactored code by running language-specific compilers.

#### `refactor/custom_rules.py` (288 LOC, 0 funcs, 3 classes)
- **class RuleSummaryDict** (line 27, 0 methods) — Custom rules validation summary dictionary.
- **class CustomRuleViolation** (line 39, 0 methods) — A custom rule violation.
- **class CustomRulesEngine** (line 50, 9 methods) — Enforces custom validation rules on refactored code.

#### `refactor/regression_predictor.py` (262 LOC, 0 funcs, 3 classes)
- **class RegressionPredictionDict** (line 21, 0 methods) — Regression prediction / coverage impact payload.
- **class CoverageImpact** (line 43, 0 methods) — Test coverage impact prediction.
- **class RegressionPredictor** (line 55, 9 methods) — Predicts test regression risk from refactored code.

#### `refactor/type_checker.py` (292 LOC, 0 funcs, 3 classes)
- **class TypeCheckResultDict** (line 20, 0 methods) — Type checking result dictionary.
- **class TypeCheckResult** (line 38, 0 methods) — Result of type checking.
- **class TypeChecker** (line 50, 5 methods) — Runs type checkers on refactored code.

### 4.release `release/` — 5 functions, 37 classes

#### `release/build_profiler.py` (90 LOC, 0 funcs, 2 classes)
- **class BuildStage** (line 10, 0 methods) — Represents a build stage with timing information.
- **class BuildProfiler** (line 19, 7 methods) — Profile build stages and identify bottlenecks.

#### `release/changelog_generator.py` (484 LOC, 0 funcs, 5 classes)
- **class ChangeType** (line 21, 0 methods) — Types of changes in changelog.
- **class ChangelogFormat** (line 35, 0 methods) — Supported changelog output formats.
- **class ChangeEntry** (line 44, 1 methods) — Represents a single change entry.
- **class ChangelogSection** (line 79, 3 methods) — Represents a section in the changelog.
- **class ChangelogGenerator** (line 123, 17 methods) — Generate changelogs from commit history with template support.

#### `release/cli.py` (308 LOC, 5 funcs, 0 classes)
- `def release_plan(repo_path, changelog_path)` L16 — Preview the next release plan.
- `def release_prepare(repo_path, changelog_path)` L49 — Prepare release in dry-run mode.
- `def release_execute(repo_path, changelog_path, skip_github, skip_pypi)` L88 — Execute the complete release process.
- `def release_publish(repo_path, tag, skip_github, skip_pypi)` L174 — Publish a release to PyPI and GitHub.
- `def build_docker_images(repo_path, registry, skip_push, dry_run)` L251 — Build Docker images for a release.

#### `release/docker_builder.py` (355 LOC, 0 funcs, 1 classes)
- **class DockerImageBuilder** (line 22, 6 methods) — Build and publish Docker images for Code Scalpel.

#### `release/failure_alerter.py` (104 LOC, 0 funcs, 3 classes)
- **class AlertChannel** (line 11, 0 methods) — Types of alert channels.
- **class Alert** (line 21, 1 methods) — Represents an alert.
- **class FailureAlerter** (line 36, 8 methods) — Send alerts on release failures.

#### `release/git_history.py` (282 LOC, 0 funcs, 2 classes)
- **class GitTag** (line 15, 1 methods) — Represents a git tag.
- **class GitHistoryAnalyzer** (line 33, 10 methods) — Analyzes git history for release automation.

#### `release/github_releases.py` (311 LOC, 0 funcs, 1 classes)
- **class GitHubReleaseManager** (line 24, 10 methods) — Manages GitHub releases via GitHub API.

#### `release/metrics_tracker.py` (178 LOC, 0 funcs, 3 classes)
- **class MetricType** (line 18, 0 methods) — Types of metrics.
- **class Metric** (line 29, 1 methods) — Represents a recorded metric.
- **class MetricsTracker** (line 57, 7 methods) — Track and analyze release metrics.

#### `release/notes.py` (190 LOC, 0 funcs, 2 classes)
- **class ReleaseNotesGenerator** (line 15, 3 methods) — Generates release notes from commits.
- **class ChangelogManager** (line 121, 5 methods) — Manages CHANGELOG.md file.

#### `release/orchestrator.py` (216 LOC, 0 funcs, 1 classes)
- **class ReleaseOrchestrator** (line 17, 7 methods) — Orchestrates the complete release process.

#### `release/pypi_publisher.py` (362 LOC, 0 funcs, 1 classes)
- **class PyPIPublisher** (line 18, 10 methods) — Handles building and publishing packages to PyPI.

#### `release/release_notes_templates.py` (516 LOC, 0 funcs, 3 classes)
- **class Template** (line 20, 3 methods) — Represents a release notes template.
- **class TemplateRegistry** (line 79, 11 methods) — Manages a collection of release notes templates.
- **class ReleaseNotesTemplate** (line 421, 6 methods) — Main interface for release notes template operations.

#### `release/rollback_manager.py` (310 LOC, 0 funcs, 4 classes)
- **class RollbackStatus** (line 19, 0 methods) — Status of a rollback operation.
- **class RollbackPoint** (line 30, 1 methods) — Represents a point in history that can be rolled back to.
- **class Hotfix** (line 59, 1 methods) — Represents a hotfix for a released version.
- **class RollbackManager** (line 90, 12 methods) — Manage release rollbacks and hotfix workflows.

#### `release/secrets_manager.py` (322 LOC, 0 funcs, 2 classes)
- **class Secret** (line 26, 3 methods) — Represents a secret with metadata.
- **class SecretsManager** (line 67, 9 methods) — Manage GitHub Actions secrets for release automation.

#### `release/status_dashboard.py` (113 LOC, 0 funcs, 3 classes)
- **class PublishStatus** (line 10, 0 methods) — Status of a publishing operation.
- **class PublishEvent** (line 21, 1 methods) — Represents a publishing event.
- **class StatusDashboard** (line 36, 6 methods) — Real-time publishing status tracking.

#### `release/versioning.py` (234 LOC, 0 funcs, 3 classes)
- **class ConventionalCommit** (line 22, 4 methods) — Parsed conventional commit.
- **class VersionBump** (line 102, 2 methods) — Represents a version bump.
- **class SemanticVersioner** (line 134, 3 methods) — Manages semantic versioning based on conventional commits.

#### `release/vscode_publisher.py` (341 LOC, 0 funcs, 1 classes)
- **class VSCodeExtensionPublisher** (line 19, 7 methods) — Build and publish VS Code extensions.

### 4.security `security/` — 21 functions, 98 classes

#### `security/analyzers/compliance_mapper.py` (291 LOC, 0 funcs, 1 classes)
- **class ComplianceMapper** (line 20, 8 methods) — Maps vulnerabilities to compliance frameworks.

#### `security/analyzers/confidence_scorer.py` (202 LOC, 0 funcs, 1 classes)
- **class ConfidenceScorer** (line 19, 6 methods) — Scores vulnerability confidence based on analysis quality.

#### `security/analyzers/cross_file_taint.py` (1552 LOC, 0 funcs, 12 classes)
- **class CrossFileTaintSource** (line 35, 0 methods) — Sources of taint in cross-file analysis.
- **class CrossFileSink** (line 45, 0 methods) — Dangerous sinks for cross-file taint.
- **class TaintedParameter** (line 59, 0 methods) — A function parameter that receives tainted data.
- **class CrossFileTaintFlow** (line 81, 1 methods) — A taint flow path across files.
- **class CrossFileVulnerability** (line 121, 1 methods) — A detected vulnerability that spans multiple files.
- **class CrossFileTaintResult** (line 162, 0 methods) — Result of cross-file taint analysis.
- **class CrossFileTaintTracker** (line 299, 24 methods) — Track taint flow across multiple files in a Python project.
- **class FunctionTaintInfo** (line 1066, 0 methods) — Information about taint characteristics of a function.
- **class SinkInfo** (line 1084, 0 methods) — Information about a dangerous sink.
- **class TaintSourceInfo** (line 1093, 0 methods) — Information about a taint source in a module.
- **class CallInfo** (line 1103, 2 methods) — Information about a cross-module function call.
- **class FunctionTaintVisitor** (line 1128, 15 methods) — AST visitor to analyze taint flow within a function.

#### `security/analyzers/custom_rules.py` (309 LOC, 0 funcs, 3 classes)
- **class CustomRule** (line 23, 0 methods) — A custom security rule.
- **class CustomRuleResult** (line 36, 0 methods) — Result of a custom rule check.
- **class CustomRulesEngine** (line 47, 15 methods) — Custom security rules engine.

#### `security/analyzers/false_positive_analyzer.py` (281 LOC, 0 funcs, 1 classes)
- **class FalsePositiveAnalyzer** (line 20, 6 methods) — Analyzes security findings for false positives.

#### `security/analyzers/policy_engine.py` (301 LOC, 0 funcs, 2 classes)
- **class PolicyViolation** (line 22, 0 methods) — A detected policy violation.
- **class PolicyEngine** (line 33, 9 methods) — Enforces custom security policies.

#### `security/analyzers/sanitizer_detector.py` (260 LOC, 0 funcs, 2 classes)
- **class SanitizerMatch** (line 23, 0 methods) — A detected sanitizer function or pattern.
- **class SanitizerDetector** (line 33, 5 methods) — Detects sanitization functions in code.

#### `security/analyzers/security_analyzer.py` (1104 LOC, 6 funcs, 4 classes)
- **class TaintFlowDict** (line 41, 0 methods) — Taint flow information for a variable.
- **class SecurityAnalysisResultDict** (line 49, 0 methods) — Security analysis result with vulnerabilities and taint flows.
- **class SecurityAnalysisResult** (line 91, 9 methods) — Result from security analysis.
- **class SecurityAnalyzer** (line 185, 19 methods) — High-level security analyzer for Python code.
- `def _ensure_config_loaded()` L82 — Load config once per process.
- `def analyze_security(code)` L1025 — Convenience function to analyze code for security vulnerabilities.
- `def find_sql_injections(code)` L1051 — Find SQL injection vulnerabilities in code.
- `def find_xss(code)` L1065 — Find XSS vulnerabilities in code.
- `def find_command_injections(code)` L1079 — Find command injection vulnerabilities in code.
- `def find_path_traversals(code)` L1093 — Find path traversal vulnerabilities in code.

#### `security/analyzers/taint_tracker.py` (2465 LOC, 9 funcs, 9 classes)
- **class VulnerabilityDict** (line 45, 0 methods) — Vulnerability information for JSON serialization.
- **class TaintSource** (line 63, 0 methods) — Categories of taint sources.
- **class SecuritySink** (line 84, 0 methods) — Categories of security sinks where tainted data is dangerous.
- **class TaintLevel** (line 142, 0 methods) — Confidence level of taint.
- **class TaintInfo** (line 159, 3 methods) — Taint metadata attached to a symbolic value.
- **class SanitizerInfo** (line 310, 0 methods) — Information about a sanitizer function.
- **class TaintedValue** (line 643, 2 methods) — A symbolic value with taint information attached.
- **class TaintTracker** (line 673, 12 methods) — Tracks taint propagation through symbolic execution.
- **class Vulnerability** (line 953, 7 methods) — A detected security vulnerability.
- `def register_sanitizer(name, clears_sinks, full_clear)` L506 — Register a custom sanitizer function.
- `def load_sanitizers_from_config(config_path)` L529 — Load custom sanitizers from pyproject.toml.
- `def _find_config_file()` L598 — Search for pyproject.toml in current and parent directories.
- `def _load_toml(path)` L618 — Load a TOML file using available parser.
- `def detect_ssr_framework(tree)` L2213 — [20251216_FEATURE] v2.2.0 - Auto-detect SSR framework from imports.
- `def is_server_action(node)` L2236 — [20251216_FEATURE] v2.2.0 - Check if node is a Next.js Server Action.
- `def has_input_validation(node)` L2266 — [20251216_BUGFIX] Accepts both FunctionDef and Lambda nodes for input validation
- `def is_dangerous_html(node)` L2332 — [20251216_FEATURE] v2.2.0 - Check if node uses dangerouslySetInnerHTML.
- `def detect_ssr_vulnerabilities(tree, framework, taint_tracker)` L2352 — [20251216_FEATURE] v2.2.0 - Detect SSR-specific vulnerabilities.

#### `security/analyzers/unified_sink_detector.py` (2307 LOC, 0 funcs, 5 classes)
- **class CoverageReportDict** (line 25, 0 methods) — Coverage report for security sinks.
- **class Language** (line 39, 0 methods) — Supported languages for unified sink detection.
- **class SinkDefinition** (line 50, 1 methods) — Definition of a security sink with confidence scoring.
- **class DetectedSink** (line 75, 1 methods) — A detected security sink in code.
- **class UnifiedSinkDetector** (line 1999, 12 methods) — Polyglot security sink detection with confidence scoring.

#### `security/contract_breach_detector.py` (346 LOC, 1 funcs, 7 classes)
- **class BreachType** (line 22, 0 methods) — Types of contract breaches.
- **class Severity** (line 33, 0 methods) — Severity levels for contract breaches.
- **class ContractBreach** (line 43, 0 methods) — [20251216_FEATURE] Represents a contract breach between server and client.
- **class Edge** (line 74, 0 methods) — [20251216_FEATURE] Represents a dependency edge in the unified graph.
- **class Node** (line 86, 0 methods) — [20251216_FEATURE] Represents a node in the unified graph.
- **class UnifiedGraph** (line 98, 6 methods) — [20251216_FEATURE] Simplified unified graph for contract breach detection.
- **class ContractBreachDetector** (line 132, 6 methods) — [20251216_FEATURE] Detect contract breaches when a node changes.
- `def detect_breaches(graph, changed_node_id, min_confidence)` L327 — Detect contract breaches for a changed node.

#### `security/dependencies/false_positive_reducer.py` (342 LOC, 0 funcs, 2 classes)
- **class FalsePositiveAssessment** (line 23, 0 methods) — Assessment of whether a vulnerability is a false positive.
- **class FalsePositiveReducer** (line 33, 13 methods) — Reduces false positives in vulnerability scanning.

#### `security/dependencies/license_compliance.py` (328 LOC, 0 funcs, 3 classes)
- **class LicenseInfo** (line 22, 0 methods) — License information for a dependency.
- **class ComplianceReport** (line 37, 0 methods) — License compliance analysis report.
- **class LicenseComplianceScanner** (line 50, 9 methods) — Scans dependencies for license compliance.

#### `security/dependencies/osv_client.py` (419 LOC, 0 funcs, 4 classes)
- **class OSVVulnerabilityDict** (line 26, 0 methods) — OSV vulnerability for JSON serialization.
- **class Vulnerability** (line 48, 1 methods) — Represents a security vulnerability from OSV.
- **class OSVClient** (line 74, 9 methods) — Client for querying the OSV (Open Source Vulnerabilities) API.
- **class OSVError** (line 402, 0 methods) — Exception raised for OSV API errors.

#### `security/dependencies/schema_tracker.py` (1265 LOC, 3 funcs, 13 classes)
- **class GraphQLChangeType** (line 51, 0 methods) — Types of GraphQL schema changes.
- **class GraphQLChangeSeverity** (line 79, 0 methods) — Severity of schema changes.
- **class GraphQLTypeKind** (line 87, 0 methods) — Kinds of GraphQL types.
- **class GraphQLArgument** (line 99, 1 methods) — Represents a GraphQL field argument.
- **class GraphQLField** (line 114, 2 methods) — Represents a GraphQL field.
- **class GraphQLEnumValue** (line 137, 0 methods) — Represents a GraphQL enum value.
- **class GraphQLType** (line 147, 1 methods) — Represents a GraphQL type definition.
- **class GraphQLDirective** (line 169, 0 methods) — Represents a GraphQL directive definition.
- **class GraphQLSchema** (line 180, 11 methods) — Represents a complete GraphQL schema.
- **class GraphQLSchemaChange** (line 266, 1 methods) — Represents a single schema change.
- **class GraphQLSchemaDrift** (line 281, 5 methods) — Result of schema drift analysis.
- **class GraphQLSchemaParser** (line 334, 12 methods) — Parser for GraphQL SDL (Schema Definition Language).
- **class GraphQLSchemaTracker** (line 667, 14 methods) — Tracks GraphQL schema evolution and detects breaking changes.
- `def track_graphql_schema(sdl)` L1189 — Convenience function to parse a GraphQL SDL.
- `def compare_graphql_schemas(old_sdl, new_sdl, old_version, new_version)` L1203 — Convenience function to compare two GraphQL schemas.
- `def compare_graphql_files(old_path, new_path)` L1225 — Convenience function to compare two GraphQL schema files.

#### `security/dependencies/severity_contextualizer.py` (351 LOC, 0 funcs, 2 classes)
- **class ContextualizedSeverity** (line 22, 0 methods) — Contextualized severity assessment for a vulnerability.
- **class SeverityContextualizer** (line 35, 9 methods) — Contextualizes vulnerability severity based on actual usage.

#### `security/dependencies/supply_chain_scorer.py` (428 LOC, 0 funcs, 3 classes)
- **class RiskScore** (line 24, 0 methods) — Risk score breakdown for a dependency.
- **class SupplyChainReport** (line 42, 0 methods) — Supply chain risk assessment report.
- **class SupplyChainRiskScorer** (line 56, 13 methods) — Assesses supply chain risk for dependencies.

#### `security/dependencies/typosquatting_detector.py` (355 LOC, 0 funcs, 3 classes)
- **class TyposquattingAlert** (line 23, 0 methods) — Alert for potential typosquatting.
- **class TyposquattingReport** (line 39, 0 methods) — Report of typosquatting scan results.
- **class TyposquattingDetector** (line 52, 11 methods) — Detects typosquatting attacks in dependencies.

#### `security/dependencies/vulnerability_reachability.py` (245 LOC, 0 funcs, 2 classes)
- **class ReachabilityResult** (line 19, 0 methods) — Result of reachability analysis for a vulnerability.
- **class VulnerabilityReachabilityAnalyzer** (line 30, 7 methods) — Analyzes whether vulnerable dependencies are actually reachable.

#### `security/dependencies/vulnerability_scanner.py` (674 LOC, 1 funcs, 7 classes)
- **class Ecosystem** (line 25, 0 methods) — Supported package ecosystems.
- **class Dependency** (line 35, 0 methods) — Represents a project dependency.
- **class VulnerabilityFinding** (line 46, 1 methods) — Represents a vulnerability found in a dependency.
- **class ScanResult** (line 71, 0 methods) — Result of a vulnerability scan.
- **class DependencyParser** (line 80, 6 methods) — Parses dependency files to extract package information.
- **class OSVClient** (line 379, 5 methods) — Client for the Google OSV (Open Source Vulnerabilities) API.
- **class VulnerabilityScanner** (line 459, 9 methods) — Scans project dependencies for known vulnerabilities.
- `def scan_dependencies(path)` L659 — Convenience function to scan a file or directory for vulnerable dependencies.

#### `security/ml/ml_vulnerability_predictor.py` (78 LOC, 0 funcs, 2 classes)
- **class VulnerabilityPrediction** (line 26, 0 methods) — Prediction result for code vulnerability.
- **class VulnerabilityPredictor** (line 36, 4 methods) — ML-based vulnerability predictor (stub).

#### `security/sanitization/sanitizer_analyzer.py` (103 LOC, 0 funcs, 4 classes)
- **class SanitizerType** (line 28, 0 methods) — Types of sanitizers.
- **class BypassTechnique** (line 41, 0 methods) — A technique that bypasses a sanitizer.
- **class SanitizerEffectiveness** (line 51, 0 methods) — Analysis of sanitizer effectiveness.
- **class SanitizerAnalyzer** (line 62, 4 methods) — Sanitizer effectiveness analyzer (stub).

#### `security/secrets/secret_scanner.py` (459 LOC, 0 funcs, 1 classes)
- **class SecretScanner** (line 39, 14 methods) — Scans AST for hardcoded secrets using comprehensive pattern matching.

#### `security/type_safety/type_evaporation_detector.py` (714 LOC, 1 funcs, 5 classes)
- **class TypeEvaporationRisk** (line 64, 0 methods) — Categories of type evaporation vulnerabilities.
- **class TypeEvaporationVulnerability** (line 75, 1 methods) — A detected type evaporation vulnerability.
- **class TypeEvaporationResult** (line 100, 2 methods) — Result of type evaporation analysis.
- **class TypeEvaporationDetector** (line 131, 13 methods) — Detects type system evaporation vulnerabilities in TypeScript/JavaScript code.
- **class CrossFileTypeEvaporationResult** (line 578, 1 methods) — Result from analyzing TypeScript frontend + Python backend together.
- `def analyze_type_evaporation_cross_file(typescript_code, python_code, ts_filename, py_filename)` L605 — Analyze TypeScript frontend and Python backend together for type evaporation.

### 4.surgery `surgery/` — 47 functions, 50 classes

#### `surgery/approval_workflow.py` (386 LOC, 0 funcs, 4 classes)
- **class ApprovalStatus** (line 60, 0 methods) — Status of an approval request.
- **class ApprovalRequest** (line 71, 0 methods) — Approval request for a code operation.
- **class ApprovalResponse** (line 97, 0 methods) — Response to an approval request.
- **class ApprovalWorkflow** (line 122, 9 methods) — Approval workflow manager for Enterprise tier.

#### `surgery/audit_trail.py` (285 LOC, 2 funcs, 2 classes)
- **class AuditEntry** (line 33, 0 methods) — Single audit log entry for a surgical operation.
- **class AuditTrail** (line 65, 4 methods) — Audit trail manager for Enterprise-tier surgical operations.
- `def get_audit_trail()` L252 — Get or create the global audit trail instance.
- `def configure_audit_trail(log_dir, enabled, log_to_file, log_to_stdout)` L260 — Configure the global audit trail instance.

#### `surgery/compliance.py` (177 LOC, 2 funcs, 1 classes)
- **class ComplianceCheckResult** (line 39, 1 methods) — Result of a compliance check.
- `def check_rename_compliance(target_file, target_type, target_name, new_name)` L51 — Check if a rename operation complies with governance policies.
- `def format_compliance_error(result)` L153 — Format compliance check result into user-friendly error message.

#### `surgery/multi_repo.py` (441 LOC, 0 funcs, 5 classes)
- **class SessionStatus** (line 67, 0 methods) — Status of a multi-repo session.
- **class RepoChange** (line 77, 0 methods) — Change to be applied in a repository.
- **class RepoState** (line 97, 0 methods) — State of a repository in a multi-repo session.
- **class SessionResult** (line 117, 0 methods) — Result of a multi-repo session operation.
- **class MultiRepoCoordinator** (line 138, 11 methods) — Multi-repository coordination for Enterprise tier.

#### `surgery/rename_symbol_refactor.py` (806 LOC, 16 funcs, 2 classes)
- **class RenameEdits** (line 66, 0 methods) — 
- **class CrossFileRenameResult** (line 72, 0 methods) — 
- `def _is_valid_python_identifier(name)` L53 — 
- `def _relativize(path, root)` L57 — Return a root-relative path string when possible to avoid leaking host paths.
- `def iter_python_files(project_root)` L83 — Yield Python files under project_root, skipping common virtualenv/build dirs.
- `def module_name_for_file(project_root, file_path)` L104 — Best-effort module name for a .py file relative to project_root.
- `def _read_text(path)` L130 — 
- `def _write_text_atomic(path, new_text)` L134 — 
- `def _tokenize(code)` L151 — 
- `def _apply_token_replacements(tokens, replacements)` L155 — 
- `def _collect_import_context(tree)` L168 — 
- `def _collect_reference_edits(code)` L222 — Collect token edits for a single file.
- `def _rewrite_from_imports()` L319 — Rewrite symbols in `from target_module import ...` statements.
- `def _rewrite_local_names()` L374 — Rename local `Name` nodes when imported directly without alias.
- `def _rewrite_module_attribute_calls()` L455 — Rename `module_alias.old_short` attribute references.
- `def _rewrite_method_calls()` L485 — Rename ClassName.old_method and module_alias.ClassName.old_method patterns.
- `def _collect_instance_names_for_class()` L547 — Collect local variable names bound to instances of the target class.
- `def rename_references_across_project()` L587 — Rename references/imports across a project for Pro/Enterprise tiers.

#### `surgery/repo_wide.py` (378 LOC, 0 funcs, 2 classes)
- **class RepoWideRenameResult** (line 49, 0 methods) — Result of a repository-wide rename operation.
- **class RepoWideRename** (line 62, 8 methods) — Repository-wide rename optimization for Enterprise tier.

#### `surgery/surgical_extractor.py` (3736 LOC, 12 funcs, 17 classes)
- **class CrossFileSymbol** (line 104, 0 methods) — A symbol resolved from an external file.
- **class CrossFileResolution** (line 121, 2 methods) — Result of cross-file dependency resolution.
- **class ExtractionResult** (line 159, 2 methods) — Result of a surgical extraction.
- **class ContextualExtraction** (line 208, 7 methods) — Extraction with all required context for LLM understanding.
- **class SurgicalExtractor** (line 454, 48 methods) — Precision code extractor using AST analysis.
- **class VariablePromotionResult** (line 1910, 0 methods) — Result of variable promotion analysis.
- **class MicroserviceExtractionResult** (line 2155, 0 methods) — Result of microservice extraction with deployment artifacts.
- **class ClosureVariable** (line 2545, 0 methods) — Information about a closure variable.
- **class ClosureAnalysisResult** (line 2561, 0 methods) — Result of closure variable analysis.
- **class DependencyInjectionSuggestion** (line 2780, 0 methods) — Suggestion for dependency injection refactoring.
- **class DependencyInjectionResult** (line 2796, 0 methods) — Result of dependency injection analysis.
- **class CrossRepoImport** (line 3043, 0 methods) — Information about a cross-repository import.
- **class OrganizationWideResolutionResult** (line 3057, 0 methods) — Result of organization-wide import resolution.
- **class PatternMatch** (line 3263, 0 methods) — A match found by custom extraction pattern.
- **class CustomPatternResult** (line 3279, 0 methods) — Result of custom pattern extraction.
- **class ServiceBoundary** (line 3519, 0 methods) — A suggested service boundary.
- **class ServiceBoundaryResult** (line 3535, 0 methods) — Result of service boundary detection.
- `def count_tokens(text, model)` L63 — Count tokens in text using tiktoken if available, else fallback to char/4.
- `def extract_function(code, name)` L1845 — Convenience function to extract a function from code.
- `def extract_class(code, name)` L1859 — Convenience function to extract a class from code.
- `def extract_method(code, class_name, method_name)` L1873 — Convenience function to extract a method from code.
- `def extract_with_context(code, name, target_type, max_depth)` L1888 — Convenience function to extract code with dependencies.
- `def promote_variables(code, function_name)` L1925 — Analyze a function and promote local variables to parameters.
- `def extract_as_microservice(code, function_name, host, port)` L2171 — Extract a function as a standalone microservice with Dockerfile and API spec.
- `def detect_closure_variables(code, function_name)` L2576 — Detect variables captured from outer scopes (closures).
- `def suggest_dependency_injection(code, function_name)` L2813 — Suggest dependency injection refactorings for better testability.
- `def resolve_organization_wide(code, function_name, workspace_root)` L3074 — Resolve imports across multiple repositories in a monorepo.
- `def extract_with_custom_pattern(pattern, pattern_type, project_root, include_related)` L3295 — Extract code using custom patterns (regex or AST).
- `def detect_service_boundaries(project_root, min_isolation_score)` L3550 — Detect architectural boundaries and suggest microservice splits.

#### `surgery/surgical_patcher.py` (2958 LOC, 12 funcs, 10 classes)
- **class PatchResult** (line 157, 1 methods) — Result of a surgical patch operation.
- **class _SymbolLocation** (line 184, 0 methods) — Internal: Location of a symbol in source code.
- **class SurgicalPatcher** (line 315, 19 methods) — Precision code patcher using AST-guided line replacement.
- **class PatchLanguage** (line 1349, 0 methods) — Supported languages for patching.
- **class PolyglotSymbolLocation** (line 1359, 1 methods) — Location of a symbol in source code (language-agnostic).
- **class BraceMatcher** (line 1385, 3 methods) — Utility for matching braces in C-style languages.
- **class JavaScriptParser** (line 1522, 7 methods) — Parser for JavaScript/TypeScript symbol extraction.
- **class JavaParser** (line 1833, 9 methods) — Parser for Java symbol extraction.
- **class PolyglotPatcher** (line 2154, 15 methods) — Multi-language surgical patcher for JS, TS, and Java.
- **class UnifiedPatcher** (line 2765, 12 methods) — Unified patching interface that routes to appropriate language patcher.
- `def _is_valid_python_identifier(name)` L90 — 
- `def _is_valid_js_identifier(name)` L146 — 
- `def _tokenize_code(code)` L200 — Tokenize Python code, returning list of tokens.
- `def _apply_token_replacements(tokens, replacements)` L208 — Apply token replacements and reconstruct code.
- `def _collect_same_file_references(code, target_type, target_name, new_name)` L222 — Collect token positions for all references to a symbol within the same file.
- `def update_function_in_file(file_path, function_name, new_code, backup)` L1272 — Update a function in a file (convenience function).
- `def update_class_in_file(file_path, class_name, new_code, backup)` L1294 — Update a class in a file (convenience function).
- `def update_method_in_file(file_path, class_name, method_name, new_code)` L1316 — Update a method in a file (convenience function).
- `def update_js_function(file_path, function_name, new_code, backup)` L2913 — Update a JavaScript function in a file.
- `def update_ts_function(file_path, function_name, new_code, backup)` L2924 — Update a TypeScript function in a file.
- `def update_java_method(file_path, class_name, method_name, new_code)` L2935 — Update a Java method in a file.
- `def update_java_class(file_path, class_name, new_code, backup)` L2950 — Update a Java class in a file.

#### `surgery/unified_extractor.py` (1559 LOC, 3 funcs, 7 classes)
- **class Language** (line 44, 0 methods) — Supported programming languages.
- **class SymbolInfo** (line 67, 1 methods) — Information about an extractable symbol.
- **class ImportInfo** (line 91, 1 methods) — Information about an import statement.
- **class FileSummary** (line 121, 2 methods) — Quick summary of a file's structure.
- **class SignatureInfo** (line 206, 2 methods) — Function/method signature information.
- **class UnifiedExtractionResult** (line 240, 5 methods) — Result of code extraction across any language.
- **class UnifiedExtractor** (line 519, 34 methods) — Universal code extractor for all supported languages.
- `def detect_language(file_path, code)` L428 — Detect programming language from file path or code content.
- `def extract_from_file(file_path, target_type, target_name, language)` L1500 — Extract code element from a file.
- `def extract_from_code(code, target_type, target_name, language)` L1524 — Extract code element from code string.

### 4.symbolic_execution_tools `symbolic_execution_tools/` — 6 functions, 34 classes

#### `symbolic_execution_tools/concolic_engine.py` (57 LOC, 0 funcs, 2 classes)
- **class ConcolicResult** (line 27, 0 methods) — Result from concolic execution.
- **class ConcolicEngine** (line 36, 2 methods) — Concolic execution engine (stub).

#### `symbolic_execution_tools/constraint_solver.py` (381 LOC, 3 funcs, 10 classes)
- **class SolverStatus** (line 11, 0 methods) — Result status from the solver.
- **class SolverResult** (line 22, 4 methods) — Result from constraint solving.
- **class ConstraintSolver** (line 59, 6 methods) — Z3-based constraint solver with Python-native output.
- **class SolverType** (line 284, 0 methods) — Supported constraint solver types.
- **class ConstraintType** (line 293, 0 methods) — Types of constraints.
- **class SolverConfig** (line 304, 0 methods) — Configuration for the constraint solver.
- **class SolverStatistics** (line 318, 0 methods) — Statistics about constraint solving.
- **class ConstraintError** (line 330, 0 methods) — Base class for constraint solver errors.
- **class UnsatisfiableError** (line 336, 0 methods) — Raised when constraints are unsatisfiable.
- **class SolverTimeoutError** (line 342, 0 methods) — Raised when solver times out.
- `def create_solver(timeout_ms)` L349 — Create a new constraint solver instance.
- `def solve_constraints(constraints, variables, timeout_ms)` L356 — Solve a list of constraints.
- `def is_satisfiable(constraints)` L377 — Check if a list of constraints is satisfiable.

#### `symbolic_execution_tools/engine.py` (551 LOC, 1 funcs, 4 classes)
- **class PathStatus** (line 57, 0 methods) — Status of an explored execution path.
- **class PathResult** (line 66, 2 methods) — Result of exploring a single execution path.
- **class AnalysisResult** (line 108, 4 methods) — Complete result from symbolic analysis.
- **class SymbolicAnalyzer** (line 160, 10 methods) — High-level symbolic analysis interface.
- `def create_analyzer(max_loop_iterations, solver_timeout)` L532 — Create a new symbolic analyzer.

#### `symbolic_execution_tools/ir_interpreter.py` (1276 LOC, 1 funcs, 6 classes)
- **class IRExecutionResult** (line 95, 2 methods) — Result of IR symbolic execution.
- **class IRNodeVisitor** (line 128, 2 methods) — Base class for IR node visitors.
- **class LanguageSemantics** (line 168, 15 methods) — Abstract base class for language-specific semantics.
- **class PythonSemantics** (line 314, 15 methods) — Python language semantics for symbolic execution.
- **class JavaScriptSemantics** (line 429, 15 methods) — JavaScript language semantics for symbolic execution.
- **class IRSymbolicInterpreter** (line 568, 21 methods) — Symbolic interpreter that operates on Unified IR nodes.
- `def get_semantics(language)` L549 — Get the semantics implementation for a language.

#### `symbolic_execution_tools/path_prioritization.py` (310 LOC, 1 funcs, 4 classes)
- **class PrioritizationStrategy** (line 30, 0 methods) — Path prioritization strategies.
- **class ErrorPattern** (line 46, 0 methods) — Types of error-prone patterns to detect.
- **class PathScore** (line 59, 1 methods) — Score for a symbolic execution path.
- **class PathPrioritizer** (line 88, 9 methods) — Prioritizes symbolic execution paths to find crash-triggering inputs faster.
- `def prioritize_for_crashes(code, states)` L286 — Convenience function to prioritize paths for crash discovery.

#### `symbolic_execution_tools/state_manager.py` (383 LOC, 0 funcs, 2 classes)
- **class SymbolicVariable** (line 51, 1 methods) — Wrapper around a Z3 symbolic variable with metadata.
- **class SymbolicState** (line 83, 17 methods) — Manages the symbolic state during execution.

#### `symbolic_execution_tools/symbolic_memory.py` (88 LOC, 0 funcs, 4 classes)
- **class MemoryType** (line 8, 0 methods) — Types of symbolic memory objects.
- **class SymbolicArray** (line 18, 0 methods) — Symbolic array representation.
- **class SymbolicDict** (line 28, 0 methods) — Symbolic dictionary representation.
- **class SymbolicMemory** (line 37, 5 methods) — Symbolic memory model (stub).

#### `symbolic_execution_tools/type_inference.py` (337 LOC, 0 funcs, 2 classes)
- **class InferredType** (line 39, 2 methods) — Types that can be inferred from Python code.
- **class TypeInferenceEngine** (line 72, 11 methods) — Infers types for variables in Python code.

### 4.testing `testing/` — 27 functions, 2 classes

#### `testing/adapters/tier_adapter.py` (256 LOC, 0 funcs, 2 classes)
- **class TierAdapter** (line 20, 13 methods) — Adapter for running tests on specific tiers.
- **class TierAdapterFactory** (line 218, 3 methods) — Factory for creating tier adapters.

#### `testing/assertions.py` (256 LOC, 8 funcs, 0 classes)
- `def assert_tool_available(tool_id, tier)` L23 — Assert that a tool is available in the specified tier.
- `def assert_tool_unavailable(tool_id, tier)` L45 — Assert that a tool is locked/unavailable in the specified tier.
- `def assert_capability_present(tool_id, capability, tier)` L64 — Assert that a capability is present for a tool in a tier.
- `def assert_limit_value(tool_id, limit_name, expected_value, tier)` L108 — Assert that a limit has a specific value.
- `def assert_limits_present(tool_id, expected_limits, tier)` L133 — Assert that expected limits are defined for a tool.
- `def assert_all_capabilities(tool_id, expected_capabilities, tier)` L157 — Assert that all expected capabilities are present.
- `def assert_tier_detected(license_path, expected_tier)` L188 — Assert that a license is detected as the expected tier.
- `def assert_tool_count(tier, expected_count, message)` L233 — Assert that a tier has a specific number of available tools.

#### `testing/fixtures.py` (229 LOC, 12 funcs, 0 classes)
- `def clear_all_caches()` L25 — Clear all tier and capability caches before and after test.
- `def community_adapter(clear_all_caches)` L41 — Provide a community tier adapter.
- `def pro_adapter(clear_all_caches)` L47 — Provide a pro tier adapter.
- `def enterprise_adapter(clear_all_caches)` L53 — Provide an enterprise tier adapter.
- `def all_adapters(clear_all_caches)` L59 — Provide adapters for all tiers.
- `def pro_license_path()` L69 — Provide path to pro test license if available.
- `def enterprise_license_path()` L81 — Provide path to enterprise test license if available.
- `def with_pro_license(clear_all_caches, pro_license_path)` L93 — Context manager fixture that temporarily sets Pro license.
- `def with_enterprise_license(clear_all_caches, enterprise_license_path)` L123 — Context manager fixture that temporarily sets Enterprise license.
- `def with_community_tier(clear_all_caches)` L155 — Context manager fixture that temporarily sets Community tier.
- `def pytest_generate_tests(metafunc)` L181 — Pytest hook to parametrize tier-aware tests.
- `def tier_adapter(request, clear_all_caches)` L201 — Provide a tier adapter for the current test.

#### `testing/markers.py` (145 LOC, 7 funcs, 0 classes)
- `def requires_tier()` L20 — Mark a test as requiring specific tier(s).
- `def requires_tool(tool_id)` L39 — Mark a test as requiring a specific tool to be available.
- `def requires_capability(tool_id, capability)` L58 — Mark a test as requiring a specific tool capability.
- `def tier_aware()` L78 — Mark a test as tier-aware.
- `def performance()` L96 — Mark a test as a performance test.
- `def security()` L112 — Mark a test as a security test.
- `def regression()` L128 — Mark a test as a regression test.

### 4.tiers `tiers/` — 10 functions, 7 classes

#### `tiers/__init__.py` (107 LOC, 0 funcs, 1 classes)
- **class Tier** (line 35, 5 methods) — License tier levels for Code Scalpel.

#### `tiers/decorators.py` (184 LOC, 4 funcs, 2 classes)
- **class Tier** (line 21, 0 methods) — License tier levels for Code Scalpel.
- **class TierRequirementError** (line 33, 1 methods) — Raised when a function is called without required tier access.
- `def _get_current_tier()` L49 — Get the current tier (lazy import to avoid circular deps).
- `def _tier_level(tier)` L56 — Get numeric level for tier comparison.
- `def requires_tier(tier, feature_name, graceful, fallback)` L62 — Decorator that restricts a function to users with the specified tier or higher.
- `def requires_feature(feature_name, graceful, fallback)` L145 — Decorator that restricts a function based on feature registry.

#### `tiers/feature_registry.py` (319 LOC, 3 funcs, 2 classes)
- **class Feature** (line 19, 0 methods) — Definition of a Code Scalpel feature.
- **class FeatureRegistry** (line 185, 10 methods) — Central registry of Code Scalpel features and their tier requirements.
- `def get_registry()` L304 — Get the global feature registry.
- `def is_feature_enabled(feature_name)` L312 — Check if a feature is enabled at the current tier.
- `def get_feature_tier(feature_name)` L317 — Get the minimum required tier for a feature.

#### `tiers/tool_registry.py` (390 LOC, 3 funcs, 2 classes)
- **class MCPTool** (line 19, 0 methods) — Definition of an MCP tool.
- **class ToolRegistry** (line 256, 10 methods) — Central registry of MCP tools and their tier requirements.
- `def get_tool_registry()` L375 — Get the global tool registry.
- `def is_tool_available(tool_name)` L383 — Check if a tool is available at the current tier.
- `def get_available_tools()` L388 — Get all tools available at the current tier.

### 4.utilities `utilities/` — 5 functions, 1 classes

#### `utilities/path_resolution.py` (191 LOC, 4 funcs, 1 classes)
- **class PathResolutionError** (line 17, 0 methods) — Raised when a file path cannot be resolved.
- `def resolve_file_path(file_path, workspace_root, check_exists)` L23 — Resolve a file path to an absolute path.
- `def get_workspace_root(start_path)` L113 — Detect workspace root by looking for common markers.
- `def normalize_path(path)` L150 — Normalize a path to use forward slashes on all platforms.
- `def get_relative_path(file_path, base_path)` L171 — Get relative path from base_path to file_path.

#### `utilities/source_sanitizer.py` (45 LOC, 1 funcs, 0 classes)
- `def sanitize_python_source(code)` L14 — Sanitize Python source for permissive parsing.

