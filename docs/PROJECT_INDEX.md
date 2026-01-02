# Code Scalpel Project Index

**Version:** 3.3.0  
**Last Updated:** December 30, 2025  
**Purpose:** Comprehensive index of all files and directories in the Code Scalpel project

---

## Table of Contents

- [Root Configuration Files](#root-configuration-files)
- [Core Source Code (src/code_scalpel/)](#core-source-code)
  - [Main Modules](#main-modules)
  - [Agents](#agents)
  - [Analysis](#analysis)
  - [AST Tools](#ast-tools)
  - [Autonomy](#autonomy)
  - [Cache](#cache)
  - [Code Parsers](#code-parsers)
  - [Configuration](#configuration)
  - [Generators](#generators)
  - [Governance](#governance)
  - [Graph Engine](#graph-engine)
  - [Integrations](#integrations)
  - [IR (Intermediate Representation)](#ir-intermediate-representation)
  - [Licensing](#licensing)
  - [MCP (Model Context Protocol)](#mcp-model-context-protocol)
  - [PDG Tools](#pdg-tools)
  - [Policy Engine](#policy-engine)
  - [Polyglot](#polyglot)
  - [Quality Assurance](#quality-assurance)
  - [Refactoring](#refactoring)
  - [Security](#security)
  - [Surgery](#surgery)
  - [Symbolic Execution](#symbolic-execution)
  - [Tiers](#tiers)
  - [Utilities](#utilities)
- [Test Suite](#test-suite)
- [Scripts](#scripts)
- [Examples](#examples)
- [Documentation](#documentation)
- [Build and Distribution](#build-and-distribution)

---

## Root Configuration Files

### pyproject.toml
**Purpose:** Python project configuration and build system specification  
**Relationship:** Defines project metadata, dependencies, build backend (Poetry), and tool configurations for ruff, black, pytest, and mypy. Central to Code Scalpel's distribution and dependency management.

### pytest.ini
**Purpose:** Pytest configuration file  
**Relationship:** Configures test discovery, coverage reporting, and pytest behavior for the entire test suite. Ensures 95%+ combined coverage gate.

### pyrightconfig.json
**Purpose:** Pyright type checker configuration  
**Relationship:** Configures static type analysis settings for improved code quality and IDE integration.

### requirements.txt
**Purpose:** Python dependency specification for pip  
**Relationship:** Lists all runtime dependencies required for Code Scalpel to function. Used for non-Poetry installations.

### requirements-secure.txt
**Purpose:** Security-hardened dependency specification  
**Relationship:** Contains pinned dependency versions that have passed security audits. Used in production deployments.

### MANIFEST.in
**Purpose:** Package distribution file inclusion specification  
**Relationship:** Tells setuptools which non-Python files to include in the distribution package (configs, templates, etc.).

### docker-compose.yml
**Purpose:** Multi-container Docker orchestration  
**Relationship:** Defines Docker services for running Code Scalpel MCP server with all dependencies.

### Dockerfile
**Purpose:** Container image build specification  
**Relationship:** Defines the Docker image for Code Scalpel MCP server, including Python environment, dependencies, and entry point.

### Dockerfile.rest
**Purpose:** REST API server container specification  
**Relationship:** Specialized Dockerfile for running Code Scalpel as a REST API server (alternative to MCP protocol).

### docker-entrypoint.sh
**Purpose:** Docker container initialization script  
**Relationship:** Handles container startup, environment configuration, and service initialization.

### server.json
**Purpose:** MCP server configuration  
**Relationship:** Configures the Model Context Protocol server settings, tool registrations, and communication parameters.

### README.md
**Purpose:** Main project documentation and entry point  
**Relationship:** Primary documentation for users, containing overview, installation, usage, and tier information. Updated for v3.3.0 with 22 tools across 3 tiers.

### CHANGELOG.md
**Purpose:** Version history and release notes  
**Relationship:** Documents all changes, features, and fixes across versions. Essential for tracking project evolution.

### CONTRIBUTING.md
**Purpose:** Contributor guidelines  
**Relationship:** Instructions for developers contributing to Code Scalpel, including code style, testing requirements, and PR process.

### SECURITY.md
**Purpose:** Security policies and vulnerability reporting  
**Relationship:** Defines security practices, responsible disclosure process, and contact information for security issues.

### DEVELOPMENT_ROADMAP.md
**Purpose:** Future features and strategic direction  
**Relationship:** Documents planned features, milestones, and release criteria. Used to guide development priorities.

### DOCKER_QUICK_START.md
**Purpose:** Quick Docker deployment guide  
**Relationship:** Step-by-step instructions for running Code Scalpel in Docker containers.

### LICENSE
**Purpose:** MIT license terms  
**Relationship:** Legal terms governing use, modification, and distribution of Code Scalpel.

---

## Core Source Code

### src/code_scalpel/

#### Main Modules

##### `__init__.py`
**Purpose:** Package initialization and public API exposure  
**Relationship:** Defines what's available when importing `code_scalpel`. Entry point for library usage.

##### `cli.py`
**Purpose:** Command-line interface  
**Relationship:** Provides CLI commands for running Code Scalpel operations from terminal. Wraps MCP tools for shell usage.

##### `core.py`
**Purpose:** Core functionality and shared utilities  
**Relationship:** Central module containing shared functions used across all Code Scalpel components.

##### `code_analyzer.py`
**Purpose:** Legacy code analysis wrapper  
**Relationship:** Maintained for backward compatibility. Wraps newer analysis modules.

##### `project_crawler.py`
**Purpose:** Legacy project crawling interface  
**Relationship:** Maintained for backward compatibility. See `analysis/project_crawler.py` for current implementation.

##### `surgical_extractor.py`
**Purpose:** Legacy surgical extraction wrapper  
**Relationship:** Maintained for backward compatibility. See `surgery/surgical_extractor.py` for current implementation.

##### `surgical_patcher.py`
**Purpose:** Legacy surgical patching wrapper  
**Relationship:** Maintained for backward compatibility. See `surgery/surgical_patcher.py` for current implementation.

##### `unified_extractor.py`
**Purpose:** Legacy unified extraction wrapper  
**Relationship:** Maintained for backward compatibility. See `surgery/unified_extractor.py` for current implementation.

##### `error_fixer.py`
**Purpose:** Legacy error fixing wrapper  
**Relationship:** Maintained for backward compatibility. See `quality_assurance/error_fixer.py` for current implementation.

##### `error_scanner.py`
**Purpose:** Legacy error scanning wrapper  
**Relationship:** Maintained for backward compatibility. See `quality_assurance/error_scanner.py` for current implementation.

---

### Agents

AI-powered autonomous agents for specialized code operations.

##### `agents/__init__.py`
**Purpose:** Agent module initialization  
**Relationship:** Exposes agent classes for external use.

##### `agents/base_agent.py`
**Purpose:** Base agent class and common functionality  
**Relationship:** Abstract base for all specialized agents. Defines agent interface and shared methods.

##### `agents/code_review_agent.py`
**Purpose:** Automated code review agent  
**Relationship:** Performs code review using AST analysis, security scanning, and quality metrics.

##### `agents/documentation_agent.py`
**Purpose:** Documentation generation agent  
**Relationship:** Analyzes code and generates/updates documentation automatically.

##### `agents/metrics_agent.py`
**Purpose:** Code metrics collection agent  
**Relationship:** Computes complexity, maintainability, and quality metrics across projects.

##### `agents/optimazation_agent.py`
**Purpose:** Performance optimization agent (note typo in filename)  
**Relationship:** Identifies performance bottlenecks and suggests optimizations using symbolic execution.

##### `agents/refactoring_agent.py`
**Purpose:** Automated refactoring agent  
**Relationship:** Performs safe refactorings using AST transformation and behavior verification.

##### `agents/security_agent.py`
**Purpose:** Security vulnerability detection agent  
**Relationship:** Runs comprehensive security analysis using taint tracking and vulnerability detection.

##### `agents/testing_agent.py`
**Purpose:** Test generation agent  
**Relationship:** Generates unit tests using symbolic execution and code analysis.

---

### Analysis

Code analysis and project inspection modules.

##### `analysis/__init__.py`
**Purpose:** Analysis module initialization  
**Relationship:** Exposes analysis classes and functions.

##### `analysis/code_analyzer.py`
**Purpose:** Main code analysis engine  
**Relationship:** **CRITICAL** - Core AST analysis, extracts functions, classes, imports, complexity. Used by MCP tool `analyze_code`.

##### `analysis/core.py`
**Purpose:** Core analysis utilities  
**Relationship:** Shared utilities for analysis modules. Used across analyzer implementations.

##### `analysis/project_crawler.py`
**Purpose:** Project-wide code crawler  
**Relationship:** **CRITICAL** - Crawls entire projects, analyzes all files. Powers MCP tool `crawl_project`.

##### `analysis/parallel_crawler.py`
**Purpose:** Multi-threaded project crawler  
**Relationship:** Parallel version of project crawler for faster analysis of large codebases.

##### `analysis/smart_crawl.py`
**Purpose:** Intelligent selective crawling  
**Relationship:** Crawls projects intelligently, skipping irrelevant files based on heuristics.

##### `analysis/cross_repo.py`
**Purpose:** Cross-repository analysis  
**Relationship:** Analyzes dependencies and relationships across multiple repositories.

##### `analysis/custom_metrics.py`
**Purpose:** Custom code metric calculations  
**Relationship:** Computes custom metrics beyond standard complexity measures.

##### `analysis/framework_detector.py`
**Purpose:** Framework and library detection  
**Relationship:** Identifies frameworks (Django, Flask, Spring, React) used in projects.

##### `analysis/generated_code.py`
**Purpose:** Generated code detection  
**Relationship:** Identifies auto-generated code to exclude from analysis.

##### `analysis/incremental_index.py`
**Purpose:** Incremental indexing data structures  
**Relationship:** Data structures for incremental code analysis and caching.

##### `analysis/incremental_indexer.py`
**Purpose:** Incremental code indexer  
**Relationship:** Builds and maintains incremental indexes for fast re-analysis.

##### `analysis/monorepo.py`
**Purpose:** Monorepo analysis support  
**Relationship:** Handles analysis of monorepo structures with multiple projects.

##### `analysis/org_index.py`
**Purpose:** Organization-wide code indexing  
**Relationship:** Creates organization-level code indexes across all repositories.

---

### AST Tools

Abstract Syntax Tree manipulation and analysis tools.

##### `ast_tools/__init__.py`
**Purpose:** AST tools module initialization  
**Relationship:** Exposes AST manipulation functions.

##### `ast_tools/analyzer.py`
**Purpose:** AST analysis utilities  
**Relationship:** **CRITICAL** - Core AST inspection, used by all code analysis features.

##### `ast_tools/builder.py`
**Purpose:** AST construction utilities  
**Relationship:** Builds AST nodes programmatically for code generation.

##### `ast_tools/transformer.py`
**Purpose:** AST transformation engine  
**Relationship:** **CRITICAL** - Transforms AST for refactoring and code modification. Used by `update_symbol` MCP tool.

##### `ast_tools/ast_refactoring.py`
**Purpose:** Refactoring-specific AST operations  
**Relationship:** High-level refactoring operations built on transformer.

##### `ast_tools/call_graph.py`
**Purpose:** Call graph generation  
**Relationship:** **CRITICAL** - Builds call graphs showing function relationships. Powers MCP tool `get_call_graph`.

##### `ast_tools/control_flow.py`
**Purpose:** Control flow graph construction  
**Relationship:** Builds control flow graphs for symbolic execution and analysis.

##### `ast_tools/data_flow.py`
**Purpose:** Data flow analysis  
**Relationship:** Tracks data dependencies and variable flow through code.

##### `ast_tools/cross_file_extractor.py`
**Purpose:** Cross-file code extraction  
**Relationship:** **CRITICAL** - Extracts code with dependencies across files. Used by MCP tool `extract_code`.

##### `ast_tools/dependency_parser.py`
**Purpose:** Dependency extraction from AST  
**Relationship:** **CRITICAL** - Parses import/require statements. Powers `get_cross_file_dependencies` MCP tool.

##### `ast_tools/import_resolver.py`
**Purpose:** Import path resolution  
**Relationship:** Resolves relative imports to absolute file paths.

##### `ast_tools/type_inference.py`
**Purpose:** Type inference engine  
**Relationship:** Infers types for dynamically typed languages (Python, JavaScript).

##### `ast_tools/utils.py`
**Purpose:** AST utility functions  
**Relationship:** Helper functions for AST manipulation across all tools.

##### `ast_tools/validator.py`
**Purpose:** AST validation  
**Relationship:** Validates AST correctness before code generation.

##### `ast_tools/visualizer.py`
**Purpose:** AST visualization  
**Relationship:** Generates visual representations of AST (Graphviz, Mermaid).

---

### Autonomy

Autonomous code modification with safety guarantees.

##### `autonomy/__init__.py`
**Purpose:** Autonomy module initialization  
**Relationship:** Exposes autonomy engine and related classes.

##### `autonomy/engine.py`
**Purpose:** Autonomous operation engine  
**Relationship:** **CRITICAL** - Orchestrates autonomous code modifications with governance checks.

##### `autonomy/audit.py`
**Purpose:** Autonomy audit logging  
**Relationship:** Records all autonomous operations for compliance and debugging.

##### `autonomy/error_to_diff.py`
**Purpose:** Error-to-patch translation  
**Relationship:** Converts error messages into code diffs for automated fixing.

##### `autonomy/fix_loop.py`
**Purpose:** Iterative fix-and-verify loop  
**Relationship:** Repeatedly applies fixes until tests pass or budget exhausted.

##### `autonomy/mutation_gate.py`
**Purpose:** Mutation approval gating  
**Relationship:** **CRITICAL** - Enforces governance policies before allowing code mutations.

##### `autonomy/sandbox.py`
**Purpose:** Sandboxed execution environment  
**Relationship:** Runs code modifications in isolated environment for safety testing.

##### `autonomy/stubs.py`
**Purpose:** Stub generation for testing  
**Relationship:** Generates test stubs for isolated execution.

##### `autonomy/integrations/__init__.py`
**Purpose:** Autonomy integration module initialization  
**Relationship:** Exposes integrations with agent frameworks.

##### `autonomy/integrations/autogen.py`
**Purpose:** AutoGen framework integration  
**Relationship:** Integrates autonomy engine with Microsoft AutoGen multi-agent framework.

##### `autonomy/integrations/crewai.py`
**Purpose:** CrewAI framework integration  
**Relationship:** Integrates autonomy engine with CrewAI multi-agent framework.

##### `autonomy/integrations/langgraph.py`
**Purpose:** LangGraph framework integration  
**Relationship:** Integrates autonomy engine with LangChain's LangGraph orchestration.

---

### Cache

Performance caching for analysis results.

##### `cache/__init__.py`
**Purpose:** Cache module initialization  
**Relationship:** Exposes caching interfaces.

##### `cache/unified_cache.py`
**Purpose:** Unified caching layer  
**Relationship:** **CRITICAL** - Consolidated cache implementation (v3.0.5+). Single source of truth for all caching.

##### `cache/ast_cache.py`
**Purpose:** AST-specific caching  
**Relationship:** Caches parsed AST trees to avoid re-parsing.

##### `cache/incremental_analyzer.py`
**Purpose:** Incremental analysis cache  
**Relationship:** Caches incremental analysis results for fast updates.

##### `cache/parallel_parser.py`
**Purpose:** Parallel parsing with cache  
**Relationship:** Parses multiple files in parallel using cached results.

##### `cache/archived/analysis_cache.py`
**Purpose:** ARCHIVED - Old analysis cache implementation  
**Relationship:** Deprecated in v3.0.5. Functionality merged into `unified_cache.py`.

##### `cache/archived/utilities_cache.py`
**Purpose:** ARCHIVED - Old utilities cache implementation  
**Relationship:** Deprecated in v3.0.5. Functionality merged into `unified_cache.py`.

---

### Code Parsers

Polyglot language parsers for multi-language support.

##### `code_parsers/__init__.py`
**Purpose:** Parser module initialization  
**Relationship:** Exposes parser factory and interfaces.

##### `code_parsers/factory.py`
**Purpose:** Parser factory pattern implementation  
**Relationship:** **CRITICAL** - Creates appropriate parser for detected language.

##### `code_parsers/base_parser.py`
**Purpose:** Base parser interface  
**Relationship:** Abstract base class defining parser contract for all languages.

##### `code_parsers/interface.py`
**Purpose:** Parser protocol/interface definition  
**Relationship:** Defines type hints and protocols for parser implementations.

##### `code_parsers/extractor.py`
**Purpose:** Code extraction from parsed results  
**Relationship:** Extracts specific code elements from parser output.

##### `code_parsers/language_detection.py`
**Purpose:** Programming language detection  
**Relationship:** Detects language from file extension, shebang, or content analysis.

##### `code_parsers/python_parser.py`
**Purpose:** Main Python parser  
**Relationship:** **CRITICAL** - Primary Python parsing using built-in `ast` module.

#### Python Parsers

##### `code_parsers/python_parsers/__init__.py`
**Purpose:** Python parser submodule initialization

##### `code_parsers/python_parsers/python_parsers_ast.py`
**Purpose:** Enhanced Python AST parser  
**Relationship:** Advanced Python parsing with additional metadata extraction.

##### `code_parsers/python_parsers/python_parsers_bandit.py`
**Purpose:** Bandit security scanner integration  
**Relationship:** Integrates Bandit security tool output into Code Scalpel.

##### `code_parsers/python_parsers/python_parsers_flake8.py`
**Purpose:** Flake8 linter integration

##### `code_parsers/python_parsers/python_parsers_mypy.py`
**Purpose:** MyPy type checker integration

##### `code_parsers/python_parsers/python_parsers_pylint.py`
**Purpose:** Pylint linter integration

##### `code_parsers/python_parsers/python_parsers_ruff.py`
**Purpose:** Ruff linter integration

##### `code_parsers/python_parsers/python_parsers_*`
**Purpose:** Additional Python tool integrations (isort, pycodestyle, pydocstyle, radon, safety, vulture, code_quality, interrogate, prospector)

#### JavaScript/TypeScript Parsers

##### `code_parsers/javascript_parsers/__init__.py`
**Purpose:** JavaScript parser submodule initialization

##### `code_parsers/javascript_parsers/javascript_parsers_treesitter.py`
**Purpose:** Tree-sitter-based JavaScript parser  
**Relationship:** **CRITICAL** - Primary JavaScript parsing using tree-sitter grammar.

##### `code_parsers/javascript_parsers/javascript_parsers_esprima.py`
**Purpose:** Esprima parser integration  
**Relationship:** Alternative JavaScript parser using Esprima library.

##### `code_parsers/javascript_parsers/javascript_parsers_babel.py`
**Purpose:** Babel parser integration  
**Relationship:** Parses modern JavaScript with Babel transformations.

##### `code_parsers/javascript_parsers/javascript_parsers_typescript.py`
**Purpose:** TypeScript parser integration  
**Relationship:** Handles TypeScript-specific syntax.

##### `code_parsers/javascript_parsers/javascript_parsers_*`
**Purpose:** Additional JS tool integrations (eslint, flow, jshint, prettier, standard, webpack, npm_audit, package_json, jsdoc, test_detection, code_quality)

#### TypeScript Parsers

##### `code_parsers/typescript_parsers/__init__.py`
**Purpose:** TypeScript parser submodule initialization

##### `code_parsers/typescript_parsers/parser.py`
**Purpose:** Main TypeScript parser  
**Relationship:** **CRITICAL** - Primary TypeScript parsing.

##### `code_parsers/typescript_parsers/analyzer.py`
**Purpose:** TypeScript code analysis  
**Relationship:** Analyzes TypeScript-specific constructs (interfaces, generics, decorators).

##### `code_parsers/typescript_parsers/tsx_analyzer.py`
**Purpose:** TSX (TypeScript + JSX) analysis  
**Relationship:** Handles React TypeScript components.

##### `code_parsers/typescript_parsers/decorator_analyzer.py`
**Purpose:** TypeScript decorator analysis  
**Relationship:** Analyzes decorator patterns (Angular, NestJS).

##### `code_parsers/typescript_parsers/alias_resolver.py`
**Purpose:** TypeScript path alias resolution  
**Relationship:** Resolves TypeScript path mappings from tsconfig.json.

##### `code_parsers/typescript_parsers/type_narrowing.py`
**Purpose:** Type narrowing analysis  
**Relationship:** Tracks TypeScript type narrowing in control flow.

#### Java Parsers

##### `code_parsers/java_parsers/__init__.py`
**Purpose:** Java parser submodule initialization

##### `code_parsers/java_parsers/java_parser_treesitter.py`
**Purpose:** Tree-sitter-based Java parser  
**Relationship:** **CRITICAL** - Primary Java parsing using tree-sitter grammar.

##### `code_parsers/java_parsers/java_parsers_javalang.py`
**Purpose:** Javalang library integration  
**Relationship:** Alternative Java parser using pure Python library.

##### `code_parsers/java_parsers/java_parsers_*`
**Purpose:** Java tool integrations (Maven, Gradle, Checkstyle, PMD, SpotBugs, FindSecBugs, ErrorProne, JaCoCo, Semgrep, SonarQube, Infer, DependencyCheck, JArchitect, Pitest)

#### Other Language Parsers

##### `code_parsers/adapters/`
**Purpose:** Language adapter pattern implementations  
**Relationship:** Adapters that normalize different parser outputs to common interface.

- `cpp_adapter.py` - C++ parser adapter
- `csharp_adapter.py` - C# parser adapter
- `go_adapter.py` - Go parser adapter
- `kotlin_adapter.py` - Kotlin parser adapter
- `php_adapter.py` - PHP parser adapter
- `ruby_adapter.py` - Ruby parser adapter
- `swift_adapter.py` - Swift parser adapter

##### `code_parsers/{language}_parsers/`
**Purpose:** Language-specific parser collections  
**Relationship:** Tool integrations for C++, C#, Go, Kotlin, PHP, Ruby, Swift.

---

### Configuration

Configuration management and templates.

##### `config/__init__.py`
**Purpose:** Config module initialization

##### `config/init_config.py`
**Purpose:** Configuration initialization  
**Relationship:** Creates default configuration files on first run.

##### `config/templates.py`
**Purpose:** Configuration templates  
**Relationship:** Template configurations for different deployment scenarios.

---

### Generators

Code generation and test generation tools.

##### `generators/__init__.py`
**Purpose:** Generators module initialization

##### `generators/test_generator.py`
**Purpose:** Unit test generation  
**Relationship:** **CRITICAL** - Generates unit tests from symbolic execution. Powers MCP tool `generate_unit_tests`.

##### `generators/refactor_simulator.py`
**Purpose:** Refactoring simulation and verification  
**Relationship:** **CRITICAL** - Simulates refactors before applying. Powers MCP tool `simulate_refactor`.

---

### Governance

Code governance and policy enforcement.

##### `governance/__init__.py`
**Purpose:** Governance module initialization

##### `governance/unified_governance.py`
**Purpose:** Unified governance framework  
**Relationship:** **CRITICAL** - Consolidates all governance rules and policies.

##### `governance/governance_config.py`
**Purpose:** Governance configuration loader  
**Relationship:** Loads governance policies from YAML/TOML files.

##### `governance/audit_log.py`
**Purpose:** Governance audit logging  
**Relationship:** Records all governance decisions and policy violations.

##### `governance/change_budget.py`
**Purpose:** Change budget tracking  
**Relationship:** Tracks and enforces change budgets (lines changed, files modified).

##### `governance/compliance_reporter.py`
**Purpose:** Compliance report generation  
**Relationship:** Generates compliance reports for audits (SOC2, ISO).

---

### Graph Engine

Knowledge graph and dependency graph engine.

##### `graph_engine/__init__.py`
**Purpose:** Graph engine module initialization

##### `graph_engine/graph.py`
**Purpose:** Main graph data structure  
**Relationship:** **CRITICAL** - Core graph implementation for code relationships.

##### `graph_engine/confidence.py`
**Purpose:** Confidence scoring for edges  
**Relationship:** Assigns confidence scores to dependency relationships.

##### `graph_engine/node_id.py`
**Purpose:** Graph node ID generation  
**Relationship:** Creates unique identifiers for code entities in graph.

##### `graph_engine/http_detector.py`
**Purpose:** HTTP endpoint detection  
**Relationship:** Detects HTTP endpoints for API graph construction.

##### `graph/__init__.py`
**Purpose:** Graph analysis module initialization

##### `graph/graph_query.py`
**Purpose:** Graph query language (Enterprise)  
**Relationship:** Query language for advanced graph traversals (Enterprise tier).

##### `graph/semantic_neighbors.py`
**Purpose:** Semantic neighbor detection (Pro)  
**Relationship:** Finds semantically related code (Pro tier).

##### `graph/logical_relationships.py`
**Purpose:** Logical relationship inference (Pro)  
**Relationship:** Infers logical relationships between code elements (Pro tier).

##### `graph/path_constraints.py`
**Purpose:** Graph path constraint evaluation  
**Relationship:** Evaluates constraints on graph paths.

##### `graph/traversal_rules.py`
**Purpose:** Graph traversal rules  
**Relationship:** Defines rules for graph traversal algorithms.

---

### Integrations

Integration with AI frameworks and protocols.

##### `integrations/__init__.py`
**Purpose:** Integrations module initialization

##### `integrations/claude.py`
**Purpose:** Anthropic Claude API integration  
**Relationship:** Integrates Code Scalpel with Claude AI via direct API calls.

##### `integrations/langchain.py`
**Purpose:** LangChain integration  
**Relationship:** LangChain tools and chains for Code Scalpel operations.

##### `integrations/autogen.py`
**Purpose:** Microsoft AutoGen integration  
**Relationship:** AutoGen agents powered by Code Scalpel tools.

##### `integrations/crewai.py`
**Purpose:** CrewAI integration  
**Relationship:** CrewAI multi-agent system integration.

##### `integrations/rest_api_server.py`
**Purpose:** REST API server  
**Relationship:** Alternative to MCP protocol - HTTP REST API for Code Scalpel tools.

##### `integrations/protocol_analyzers/`
**Purpose:** Protocol-specific analyzers  
**Relationship:** Analyzes various communication protocols for security and compliance.

- `frontend/input_tracker.py` - Tracks frontend user input
- `graphql/schema_tracker.py` - GraphQL schema analysis
- `grpc/contract_analyzer.py` - gRPC contract analysis
- `kafka/taint_tracker.py` - Kafka message taint tracking
- `schema/drift_detector.py` - Schema drift detection

---

### IR (Intermediate Representation)

Language-agnostic intermediate representation for polyglot analysis.

##### `ir/__init__.py`
**Purpose:** IR module initialization

##### `ir/nodes.py`
**Purpose:** IR node definitions  
**Relationship:** **CRITICAL** - Defines IR node types for all languages.

##### `ir/operators.py`
**Purpose:** IR operator definitions  
**Relationship:** Defines operators in IR (binary, unary, logical).

##### `ir/semantics.py`
**Purpose:** IR semantic analysis  
**Relationship:** Analyzes semantic properties of IR.

##### `ir/normalizers/__init__.py`
**Purpose:** IR normalizers module initialization

##### `ir/normalizers/base.py`
**Purpose:** Base normalizer interface  
**Relationship:** Abstract base for language-specific normalizers.

##### `ir/normalizers/python_normalizer.py`
**Purpose:** Python to IR normalizer  
**Relationship:** **CRITICAL** - Converts Python AST to IR.

##### `ir/normalizers/java_normalizer.py`
**Purpose:** Java to IR normalizer  
**Relationship:** **CRITICAL** - Converts Java AST to IR.

##### `ir/normalizers/javascript_normalizer.py`
**Purpose:** JavaScript to IR normalizer  
**Relationship:** **CRITICAL** - Converts JavaScript AST to IR.

##### `ir/normalizers/typescript_normalizer.py`
**Purpose:** TypeScript to IR normalizer  
**Relationship:** **CRITICAL** - Converts TypeScript AST to IR.

##### `ir/normalizers/tree_sitter_visitor.py`
**Purpose:** Tree-sitter visitor for IR conversion  
**Relationship:** Generic visitor pattern for tree-sitter ASTs.

---

### Licensing

Tiered licensing and feature gating system.

##### `licensing/__init__.py`
**Purpose:** Licensing module initialization

##### `licensing/license_manager.py`
**Purpose:** Main license management orchestrator  
**Relationship:** **CRITICAL** - Orchestrates license validation and tier detection.

##### `licensing/jwt_validator.py`
**Purpose:** JWT license validation  
**Relationship:** **CRITICAL** - Validates JWT license tokens cryptographically.

##### `licensing/jwt_generator.py`
**Purpose:** JWT license generation (internal)  
**Relationship:** Generates JWT licenses (used by license server only).

##### `licensing/tier_detector.py`
**Purpose:** Tier detection logic  
**Relationship:** Detects current tier (Community, Pro, Enterprise) from license or defaults.

##### `licensing/authorization.py`
**Purpose:** Feature authorization checks  
**Relationship:** Checks if current tier authorizes specific features.

##### `licensing/features.py`
**Purpose:** Feature flag definitions  
**Relationship:** Defines all tier-gated features.

##### `licensing/cache.py`
**Purpose:** License validation caching  
**Relationship:** Caches license validation results for performance.

##### `licensing/config_loader.py`
**Purpose:** License configuration loader  
**Relationship:** Loads license configuration from files and environment.

##### `licensing/crl_fetcher.py`
**Purpose:** Certificate Revocation List fetcher  
**Relationship:** Fetches CRLs to check for revoked licenses.

##### `licensing/remote_verifier.py`
**Purpose:** Remote license verification  
**Relationship:** Verifies licenses against remote server for enterprise.

##### `licensing/runtime_revalidator.py`
**Purpose:** Runtime license revalidation  
**Relationship:** Periodically revalidates licenses during long-running sessions.

##### `licensing/validator.py`
**Purpose:** License validation utilities  
**Relationship:** Utility functions for license validation logic.

---

### MCP (Model Context Protocol)

MCP server implementation for AI agent integration.

##### `mcp/__init__.py`
**Purpose:** MCP module initialization

##### `mcp/server.py`
**Purpose:** Main MCP server implementation  
**Relationship:** **CRITICAL** - Core MCP protocol server exposing 22 tools to AI agents.

##### `mcp/contract.py`
**Purpose:** MCP contract definitions  
**Relationship:** Defines MCP tool contracts and schemas.

##### `mcp/logging.py`
**Purpose:** MCP server logging  
**Relationship:** Logs MCP requests/responses for debugging.

##### `mcp/mcp_logging.py`
**Purpose:** Enhanced MCP logging utilities  
**Relationship:** Advanced logging with structured output.

##### `mcp/response_config.py`
**Purpose:** MCP response configuration  
**Relationship:** Configures response formats and tier-specific truncation.

##### `mcp/path_resolver.py`
**Purpose:** MCP path resolution  
**Relationship:** Resolves file paths for MCP tool invocations.

##### `mcp/module_resolver.py`
**Purpose:** MCP module resolution  
**Relationship:** Resolves Python modules dynamically for MCP tools.

---

### PDG Tools

Program Dependence Graph construction and analysis.

##### `pdg_tools/__init__.py`
**Purpose:** PDG tools module initialization

##### `pdg_tools/builder.py`
**Purpose:** PDG construction  
**Relationship:** **CRITICAL** - Builds program dependence graphs from AST.

##### `pdg_tools/analyzer.py`
**Purpose:** PDG analysis  
**Relationship:** **CRITICAL** - Analyzes PDG for slicing and dependency tracking.

##### `pdg_tools/slicer.py`
**Purpose:** Program slicing  
**Relationship:** **CRITICAL** - Performs program slicing using PDG.

##### `pdg_tools/transformer.py`
**Purpose:** PDG transformation  
**Relationship:** Transforms PDG for optimization and analysis.

##### `pdg_tools/utils.py`
**Purpose:** PDG utilities  
**Relationship:** Helper functions for PDG operations.

##### `pdg_tools/visualizer.py`
**Purpose:** PDG visualization  
**Relationship:** Generates visual PDG diagrams.

---

### Policy Engine

Code policy enforcement and governance.

##### `policy_engine/__init__.py`
**Purpose:** Policy engine module initialization

##### `policy_engine/policy_engine.py`
**Purpose:** Main policy enforcement engine  
**Relationship:** **CRITICAL** - Enforces code policies and governance rules.

##### `policy_engine/models.py`
**Purpose:** Policy data models  
**Relationship:** Defines policy rule data structures.

##### `policy_engine/exceptions.py`
**Purpose:** Policy engine exceptions  
**Relationship:** Custom exceptions for policy violations.

##### `policy_engine/audit_log.py`
**Purpose:** Policy audit logging  
**Relationship:** Logs policy enforcement decisions.

##### `policy_engine/crypto_verify.py`
**Purpose:** Cryptographic policy verification  
**Relationship:** **CRITICAL** - Verifies policy file integrity using signatures. Powers MCP tool `verify_policy_integrity`.

##### `policy_engine/tamper_resistance.py`
**Purpose:** Tamper resistance mechanisms  
**Relationship:** Prevents tampering with policy files.

##### `policy_engine/semantic_analyzer.py`
**Purpose:** Semantic policy analysis  
**Relationship:** Analyzes code semantics against policies.

##### `policy_engine/code_policy_check/__init__.py`
**Purpose:** Code policy check submodule initialization

##### `policy_engine/code_policy_check/analyzer.py`
**Purpose:** Policy check analyzer  
**Relationship:** **CRITICAL** - Analyzes code against style and compliance policies. Powers MCP tool `code_policy_check`.

##### `policy_engine/code_policy_check/models.py`
**Purpose:** Policy check data models

##### `policy_engine/code_policy_check/patterns.py`
**Purpose:** Policy check patterns  
**Relationship:** Defines pattern matching rules for policy checks.

---

### Polyglot

Multi-language support and cross-language analysis.

##### `polyglot/__init__.py`
**Purpose:** Polyglot module initialization

##### `polyglot/extractor.py`
**Purpose:** Polyglot code extraction  
**Relationship:** **CRITICAL** - Extracts code across multiple languages.

##### `polyglot/contract_breach_detector.py`
**Purpose:** Cross-language contract breach detection  
**Relationship:** Detects API contract violations across language boundaries.

##### `polyglot/alias_resolver.py`
**Purpose:** Cross-language alias resolution  
**Relationship:** Resolves aliases across language boundaries.

##### `polyglot/tsx_analyzer.py`
**Purpose:** TSX/React component analysis  
**Relationship:** Specialized TSX analyzer for React components.

##### `polyglot/typescript/__init__.py`
**Purpose:** Polyglot TypeScript submodule initialization

##### `polyglot/typescript/parser.py`
**Purpose:** TypeScript parser for polyglot  
**Relationship:** TypeScript parsing in polyglot context.

##### `polyglot/typescript/analyzer.py`
**Purpose:** TypeScript analyzer for polyglot

##### `polyglot/typescript/decorator_analyzer.py`
**Purpose:** TypeScript decorator analyzer for polyglot

##### `polyglot/typescript/type_narrowing.py`
**Purpose:** TypeScript type narrowing for polyglot

---

### Quality Assurance

Code quality and error detection/fixing.

##### `quality_assurance/__init__.py`
**Purpose:** QA module initialization

##### `quality_assurance/error_scanner.py`
**Purpose:** Error detection scanner  
**Relationship:** Scans code for errors using linters and static analysis.

##### `quality_assurance/error_fixer.py`
**Purpose:** Automated error fixing  
**Relationship:** Applies automated fixes to detected errors.

---

### Refactoring

Safe code refactoring with verification.

##### `refactor/__init__.py`
**Purpose:** Refactor module initialization

##### `refactor/build_verifier.py`
**Purpose:** Build verification after refactoring  
**Relationship:** Verifies builds pass after refactoring.

##### `refactor/type_checker.py`
**Purpose:** Type checking after refactoring  
**Relationship:** Verifies types remain correct after refactoring.

##### `refactor/custom_rules.py`
**Purpose:** Custom refactoring rules  
**Relationship:** User-defined refactoring patterns and rules.

##### `refactor/regression_predictor.py`
**Purpose:** Regression risk prediction  
**Relationship:** Predicts likelihood of regression from refactoring.

---

### Security

Security analysis and vulnerability detection.

##### `security/__init__.py`
**Purpose:** Security module initialization

##### `security/contract_breach_detector.py`
**Purpose:** Contract breach detection  
**Relationship:** Detects violations of security contracts.

##### `security/analyzers/__init__.py`
**Purpose:** Security analyzers submodule initialization

##### `security/analyzers/security_analyzer.py`
**Purpose:** Main security analyzer  
**Relationship:** **CRITICAL** - Core security analysis. Powers MCP tool `security_scan`.

##### `security/analyzers/taint_tracker.py`
**Purpose:** Taint tracking engine  
**Relationship:** **CRITICAL** - Tracks tainted data flow through code.

##### `security/analyzers/cross_file_taint.py`
**Purpose:** Cross-file taint tracking  
**Relationship:** **CRITICAL** - Tracks taint across file boundaries. Powers MCP tool `cross_file_security_scan`.

##### `security/analyzers/unified_sink_detector.py`
**Purpose:** Unified sink detection  
**Relationship:** **CRITICAL** - Detects dangerous sinks across languages. Powers MCP tool `unified_sink_detect`.

##### `security/analyzers/sanitizer_detector.py`
**Purpose:** Sanitizer detection  
**Relationship:** Detects sanitization functions to reduce false positives.

##### `security/analyzers/confidence_scorer.py`
**Purpose:** Vulnerability confidence scoring  
**Relationship:** Assigns confidence scores to vulnerability findings.

##### `security/analyzers/compliance_mapper.py`
**Purpose:** Compliance framework mapping  
**Relationship:** Maps vulnerabilities to compliance frameworks (OWASP, CWE, PCI-DSS).

##### `security/analyzers/false_positive_analyzer.py`
**Purpose:** False positive reduction  
**Relationship:** Reduces false positives using contextual analysis.

##### `security/analyzers/custom_rules.py`
**Purpose:** Custom security rules  
**Relationship:** User-defined security detection rules.

##### `security/analyzers/policy_engine.py`
**Purpose:** Security policy enforcement  
**Relationship:** Enforces security policies on code changes.

##### `security/dependencies/__init__.py`
**Purpose:** Dependency security submodule initialization

##### `security/dependencies/vulnerability_scanner.py`
**Purpose:** Dependency vulnerability scanning  
**Relationship:** **CRITICAL** - Scans dependencies for CVEs. Powers MCP tool `scan_dependencies`.

##### `security/dependencies/osv_client.py`
**Purpose:** OSV API client  
**Relationship:** Queries Google's OSV database for vulnerability information.

##### `security/dependencies/license_compliance.py`
**Purpose:** License compliance checking  
**Relationship:** Checks dependency licenses for compliance.

##### `security/dependencies/typosquatting_detector.py`
**Purpose:** Typosquatting detection  
**Relationship:** Detects potential typosquatting attacks in dependencies.

##### `security/dependencies/supply_chain_scorer.py`
**Purpose:** Supply chain risk scoring  
**Relationship:** Scores dependencies based on supply chain risk.

##### `security/dependencies/vulnerability_reachability.py`
**Purpose:** Vulnerability reachability analysis  
**Relationship:** Determines if vulnerable code paths are actually reachable.

##### `security/dependencies/severity_contextualizer.py`
**Purpose:** Severity contextualization  
**Relationship:** Adjusts vulnerability severity based on usage context.

##### `security/dependencies/false_positive_reducer.py`
**Purpose:** Dependency false positive reduction  
**Relationship:** Reduces false positives in dependency scanning.

##### `security/dependencies/schema_tracker.py`
**Purpose:** Schema tracking for dependencies  
**Relationship:** Tracks schema changes in dependencies.

##### `security/type_safety/__init__.py`
**Purpose:** Type safety submodule initialization

##### `security/type_safety/type_evaporation_detector.py`
**Purpose:** Type evaporation detection  
**Relationship:** **CRITICAL** - Detects TypeScript type evaporation vulnerabilities. Powers MCP tool `type_evaporation_scan`.

##### `security/sanitization/__init__.py`
**Purpose:** Sanitization analysis submodule initialization

##### `security/sanitization/sanitizer_analyzer.py`
**Purpose:** Sanitizer effectiveness analysis  
**Relationship:** Analyzes if sanitizers are effective against threats.

##### `security/secrets/__init__.py`
**Purpose:** Secret detection submodule initialization

##### `security/secrets/secret_scanner.py`
**Purpose:** Secret detection scanner  
**Relationship:** Detects hardcoded secrets (API keys, passwords).

##### `security/ml/__init__.py`
**Purpose:** ML-based security submodule initialization

##### `security/ml/ml_vulnerability_predictor.py`
**Purpose:** ML vulnerability prediction  
**Relationship:** Uses ML to predict likely vulnerabilities.

---

### Surgery

Surgical code extraction and modification.

##### `surgery/__init__.py`
**Purpose:** Surgery module initialization

##### `surgery/surgical_extractor.py`
**Purpose:** Surgical code extraction  
**Relationship:** **CRITICAL** - Extracts specific code elements. Powers MCP tool `extract_code`.

##### `surgery/surgical_patcher.py`
**Purpose:** Surgical code patching  
**Relationship:** **CRITICAL** - Patches specific code elements. Powers MCP tool `update_symbol`.

##### `surgery/unified_extractor.py`
**Purpose:** Unified extraction interface  
**Relationship:** Unified interface for surgical and cross-file extraction.

---

### Symbolic Execution

Symbolic execution engine for path exploration.

##### `symbolic_execution_tools/__init__.py`
**Purpose:** Symbolic execution module initialization

##### `symbolic_execution_tools/engine.py`
**Purpose:** Main symbolic execution engine  
**Relationship:** **CRITICAL** - Core symbolic execution. Powers MCP tool `symbolic_execute`.

##### `symbolic_execution_tools/constraint_solver.py`
**Purpose:** Z3 constraint solver integration  
**Relationship:** **CRITICAL** - Integrates Z3 for constraint solving.

##### `symbolic_execution_tools/state_manager.py`
**Purpose:** Symbolic state management  
**Relationship:** Manages symbolic execution state across paths.

##### `symbolic_execution_tools/symbolic_memory.py`
**Purpose:** Symbolic memory model  
**Relationship:** Models memory symbolically for execution.

##### `symbolic_execution_tools/path_prioritization.py`
**Purpose:** Path exploration prioritization  
**Relationship:** Prioritizes which paths to explore first.

##### `symbolic_execution_tools/concolic_engine.py`
**Purpose:** Concolic execution engine  
**Relationship:** Combines concrete and symbolic execution.

##### `symbolic_execution_tools/ir_interpreter.py`
**Purpose:** IR interpreter for symbolic execution  
**Relationship:** Interprets IR symbolically.

##### `symbolic_execution_tools/type_inference.py`
**Purpose:** Symbolic type inference  
**Relationship:** Infers types during symbolic execution.

---

### Tiers

Tiered feature gating and tool registry.

##### `tiers/__init__.py`
**Purpose:** Tiers module initialization

##### `tiers/decorators.py`
**Purpose:** Tier gating decorators  
**Relationship:** **CRITICAL** - Decorators for tier-based feature gating (@require_tier).

##### `tiers/tool_registry.py`
**Purpose:** Tool registry with tier information  
**Relationship:** **CRITICAL** - Registry of all 22 MCP tools with tier requirements.

##### `tiers/feature_registry.py`
**Purpose:** Feature registry with tier information  
**Relationship:** Registry of all features with tier gates.

---

### Utilities

Shared utility functions.

##### `utilities/__init__.py`
**Purpose:** Utilities module initialization

##### `utilities/path_resolution.py`
**Purpose:** Path resolution utilities  
**Relationship:** Cross-platform path resolution and normalization.

---

## Test Suite

Comprehensive test suite with 4,033+ tests.

### Key Test Files

##### `tests/test_init_license.py`
**Purpose:** License initialization tests  
**Relationship:** Tests license system initialization.

##### `tests/test_rename.py`
**Purpose:** Symbol renaming tests  
**Relationship:** Tests `rename_symbol` MCP tool functionality.

**Note:** Full test suite listing available in test directories. Test coverage: 94.86% combined (96.28% statement, 90.95% branch).

---

## Scripts

Automation and utility scripts.

##### `scripts/verify.sh`
**Purpose:** Full verification script  
**Relationship:** **CRITICAL** - Runs all verification: tests, coverage, linting, type checks. Pre-commit requirement.

##### `scripts/fix.sh`
**Purpose:** Auto-fix script  
**Relationship:** Automatically fixes linting and formatting issues.

##### `scripts/mcp_smoke_test.py`
**Purpose:** MCP server smoke test  
**Relationship:** Quick validation that MCP server starts and responds.

##### `scripts/mcp_tool_explicit_test.py`
**Purpose:** Explicit MCP tool testing  
**Relationship:** Tests each MCP tool explicitly.

##### `scripts/mcp_validate_22_tools.py`
**Purpose:** 22-tool validation script  
**Relationship:** **CRITICAL** - Validates all 22 MCP tools are registered and functional.

##### `scripts/mcp_validate_pro_tier.py`
**Purpose:** Pro tier validation  
**Relationship:** Validates Pro tier features.

##### `scripts/mcp_validate_enterprise_tier.py`
**Purpose:** Enterprise tier validation  
**Relationship:** Validates Enterprise tier features.

##### `scripts/generate_mcp_tier_matrix.py`
**Purpose:** Tier matrix generation  
**Relationship:** Generates tier comparison matrices for documentation.

##### `scripts/generate_mcp_tools_reference.py`
**Purpose:** Tools reference generation  
**Relationship:** Generates tool reference documentation.

##### `scripts/benchmark_polyglot.py`
**Purpose:** Polyglot parser benchmarking  
**Relationship:** Benchmarks performance of polyglot parsers.

##### `scripts/regression_test.py`
**Purpose:** Regression testing  
**Relationship:** Runs regression tests against previous versions.

##### `scripts/test_docker_tools.py`
**Purpose:** Docker-specific tool testing  
**Relationship:** Tests tools in Docker environment.

##### `scripts/policy_manifest_manager.py`
**Purpose:** Policy manifest management  
**Relationship:** Manages policy file manifests and signatures.

##### `scripts/verify_distribution_separation.py`
**Purpose:** Distribution separation verification  
**Relationship:** Verifies code/tier separation in distribution.

##### `scripts/validate_all_releases.py`
**Purpose:** Release validation  
**Relationship:** Validates all releases against quality gates.

##### `scripts/generate_demos.py`
**Purpose:** Demo generation  
**Relationship:** Generates demonstration code and examples.

##### `scripts/docker_setup.sh`
**Purpose:** Docker environment setup  
**Relationship:** Sets up Docker environment for development.

##### `scripts/migrate_to_code_scalpel.sh`
**Purpose:** Migration script  
**Relationship:** Migrates from old versions to current version.

---

## Examples

Runnable example code demonstrating all features.

##### `examples/claude_example.py`
**Purpose:** Claude API integration example  
**Relationship:** Shows how to use Code Scalpel with Claude API.

##### `examples/autogen_example.py`
**Purpose:** AutoGen integration example  
**Relationship:** Demonstrates AutoGen multi-agent with Code Scalpel.

##### `examples/autogen_autonomy_example.py`
**Purpose:** AutoGen autonomy example  
**Relationship:** Shows autonomous code modification with AutoGen.

##### `examples/crewai_example.py`
**Purpose:** CrewAI integration example  
**Relationship:** Demonstrates CrewAI with Code Scalpel tools.

##### `examples/crewai_autonomy_example.py`
**Purpose:** CrewAI autonomy example  
**Relationship:** Shows autonomous operations with CrewAI.

##### `examples/langchain_example.py`
**Purpose:** LangChain integration example  
**Relationship:** LangChain tools and chains with Code Scalpel.

##### `examples/langgraph_example.py`
**Purpose:** LangGraph orchestration example  
**Relationship:** LangGraph graph-based orchestration with Code Scalpel.

##### `examples/security_analysis_example.py`
**Purpose:** Security analysis demonstration  
**Relationship:** Shows taint tracking and vulnerability detection.

##### `examples/symbolic_execution_example.py`
**Purpose:** Symbolic execution demonstration  
**Relationship:** Shows symbolic execution and path exploration.

##### `examples/ast_example.py`
**Purpose:** AST manipulation example  
**Relationship:** Demonstrates AST analysis and transformation.

##### `examples/pdg_example.py`
**Purpose:** PDG construction example  
**Relationship:** Shows program dependence graph construction.

##### `examples/graph_engine_example.py`
**Purpose:** Graph engine demonstration  
**Relationship:** Shows code dependency graph construction.

##### `examples/policy_engine_example.py`
**Purpose:** Policy enforcement example  
**Relationship:** Demonstrates policy engine and governance.

##### `examples/policy_crypto_verification_example.py`
**Purpose:** Policy integrity verification example  
**Relationship:** Shows cryptographic policy verification.

##### `examples/jwt_license_example.py`
**Purpose:** License management example  
**Relationship:** Demonstrates JWT license validation.

##### `examples/jsx_tsx_extraction_example.py`
**Purpose:** JSX/TSX extraction example  
**Relationship:** Shows React component extraction.

##### `examples/polyglot_extraction_demo.py`
**Purpose:** Polyglot extraction demonstration  
**Relationship:** Shows multi-language code extraction.

##### `examples/polyglot_extractor_demo.py`
**Purpose:** Enhanced polyglot extractor demo  
**Relationship:** Advanced polyglot extraction patterns.

##### `examples/polyglot_usage_guide.py`
**Purpose:** Polyglot usage guide  
**Relationship:** Complete guide to polyglot features.

##### `examples/simple_polyglot_demo.py`
**Purpose:** Simple polyglot demonstration  
**Relationship:** Basic polyglot extraction example.

##### `examples/resource_template_example.py`
**Purpose:** Resource template example  
**Relationship:** Shows resource URI templates for code access.

##### `examples/surgical_extractor_enhanced_example.py`
**Purpose:** Enhanced surgical extraction example  
**Relationship:** Advanced surgical extraction patterns.

##### `examples/unified_governance_examples.py`
**Purpose:** Unified governance demonstrations  
**Relationship:** Shows unified governance framework usage.

##### `examples/unified_sink_detector_example.py`
**Purpose:** Unified sink detector example  
**Relationship:** Demonstrates polyglot sink detection.

##### `examples/sandbox_example.py`
**Purpose:** Sandboxed execution example  
**Relationship:** Shows sandboxed code execution.

##### `examples/autonomy_audit_example.py`
**Purpose:** Autonomy audit example  
**Relationship:** Demonstrates autonomy audit trail.

##### `examples/change_budgeting_example.py`
**Purpose:** Change budgeting example  
**Relationship:** Shows change budget tracking.

##### `examples/compliance_reporting_demo.py`
**Purpose:** Compliance reporting demonstration  
**Relationship:** Generates compliance reports.

##### `examples/error_to_diff_example.py`
**Purpose:** Error-to-diff translation example  
**Relationship:** Shows automatic error fixing workflow.

##### `examples/feature_gating_example.py`
**Purpose:** Feature gating demonstration  
**Relationship:** Shows tier-based feature gating.

##### `examples/deployer_config_example.py`
**Purpose:** Deployer configuration example  
**Relationship:** Shows deployment configuration patterns.

---

## Documentation

Comprehensive documentation in `docs/`.

### Root Documentation

##### `docs/README.md`
**Purpose:** Documentation index and overview  
**Relationship:** Entry point for all documentation.

##### `docs/INDEX.md`
**Purpose:** Master documentation table of contents  
**Relationship:** **CRITICAL** - Central index of all documentation files.

##### `docs/COMPREHENSIVE_GUIDE.md`
**Purpose:** Complete user guide  
**Relationship:** **CRITICAL** - End-to-end guide for all Code Scalpel features.

##### `docs/QUICK_REFERENCE_DOCS.md`
**Purpose:** Quick reference guide  
**Relationship:** Quick lookup for documentation locations.

##### `docs/TIER_CONFIGURATION.md`
**Purpose:** Tier system configuration guide  
**Relationship:** Documents tier system configuration and customization.

##### `docs/DEVELOPMENT_ROADMAP.md`
**Purpose:** Development roadmap (docs copy)  
**Relationship:** Copy of root DEVELOPMENT_ROADMAP.md for documentation context.

##### `docs/PROJECT_REORG_REFACTOR.md`
**Purpose:** Project reorganization documentation  
**Relationship:** Documents project restructuring history and decisions.

### Documentation Subdirectories

##### `docs/architecture/`
**Purpose:** Architecture documentation  
**Relationship:** System design, module descriptions, architectural decisions.

##### `docs/guides/`
**Purpose:** How-to guides  
**Relationship:** Step-by-step guides for specific tasks.

##### `docs/modules/`
**Purpose:** Module-specific documentation  
**Relationship:** Per-module API reference and internal design.

##### `docs/parsers/`
**Purpose:** Parser documentation  
**Relationship:** Language parser implementation details.

##### `docs/ci_cd/`
**Purpose:** CI/CD documentation  
**Relationship:** Pipeline configuration and automation.

##### `docs/deployment/`
**Purpose:** Deployment guides  
**Relationship:** Production deployment procedures.

##### `docs/compliance/`
**Purpose:** Compliance documentation  
**Relationship:** Regulatory compliance, security standards, audit documents.

##### `docs/release_notes/`
**Purpose:** Release documentation  
**Relationship:** Version-specific release notes and changelogs.

##### `docs/examples.md`
**Purpose:** Examples documentation  
**Relationship:** Index of all example files with descriptions.

##### `docs/agent_integration.md`
**Purpose:** AI agent integration guide  
**Relationship:** Guide for integrating Code Scalpel with AI agents.

##### `docs/analysis/tool_validation/`
**Purpose:** Tool verification documents  
**Relationship:** Documents verifying each of the 22 MCP tools. Used as source for README v3.3.0 updates.

---

## Build and Distribution

##### `pyproject.toml`
**Purpose:** Build configuration (see Root Configuration)

##### `MANIFEST.in`
**Purpose:** Distribution manifest (see Root Configuration)

##### `setup.py`
**Purpose:** NOT PRESENT - Using pyproject.toml only  
**Relationship:** Code Scalpel uses modern pyproject.toml-based build system.

---

## Configuration Directories

##### `.code-scalpel/`
**Purpose:** Code Scalpel runtime configuration directory  
**Relationship:** Contains runtime configs, audit logs, license files (gitignored).

##### `.github/`
**Purpose:** GitHub-specific configuration  
**Relationship:** GitHub Actions workflows, issue templates, PR templates.

##### `.github/prompts/`
**Purpose:** Internal GitHub workflow prompts  
**Relationship:** Prompt templates for internal development (gitignored).

---

## Archived/Legacy Code

##### `src/code_scalpel/archived_parsers/legacy_parsers/`
**Purpose:** Archived parser implementations  
**Relationship:** Legacy parsers kept for reference. Not used in current codebase.

##### `src/code_scalpel/cache/archived/`
**Purpose:** Archived cache implementations  
**Relationship:** Old cache modules replaced by `unified_cache.py` in v3.0.5.

---

## Summary

**Total Source Files:** 300+ Python modules  
**Total Test Files:** 4,033+ tests  
**Total Scripts:** 18 automation scripts  
**Total Examples:** 30 runnable examples  
**Documentation Files:** 100+ markdown files  

**Critical Entry Points:**
- MCP Server: `src/code_scalpel/mcp/server.py`
- CLI: `src/code_scalpel/cli.py`
- Public API: `src/code_scalpel/__init__.py`

**Critical MCP Tools:**
1. `analyze_code` → `analysis/code_analyzer.py`
2. `extract_code` → `surgery/surgical_extractor.py`
3. `update_symbol` → `surgery/surgical_patcher.py`
4. `security_scan` → `security/analyzers/security_analyzer.py`
5. `cross_file_security_scan` → `security/analyzers/cross_file_taint.py`
6. `symbolic_execute` → `symbolic_execution_tools/engine.py`
7. `generate_unit_tests` → `generators/test_generator.py`
8. `simulate_refactor` → `generators/refactor_simulator.py`
9. `crawl_project` → `analysis/project_crawler.py`
10. `scan_dependencies` → `security/dependencies/vulnerability_scanner.py`
11. `get_call_graph` → `ast_tools/call_graph.py`
12. `get_cross_file_dependencies` → `ast_tools/dependency_parser.py`
13. `get_graph_neighborhood` → `graph_engine/graph.py`
14. `verify_policy_integrity` → `policy_engine/crypto_verify.py`
15. `code_policy_check` → `policy_engine/code_policy_check/analyzer.py`
16. `type_evaporation_scan` → `security/type_safety/type_evaporation_detector.py`
17. `unified_sink_detect` → `security/analyzers/unified_sink_detector.py`
18. `get_file_context` → `ast_tools/analyzer.py`
19. `get_symbol_references` → `ast_tools/call_graph.py`
20. `get_project_map` → `graph_engine/graph.py`
21. `validate_paths` → `utilities/path_resolution.py`
22. `rename_symbol` → `ast_tools/transformer.py`

---

**Last Updated:** December 30, 2025  
**Document Version:** 1.0.0  
**Code Scalpel Version:** 3.3.0
