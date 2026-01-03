# src/symbolic_execution_tools/__init__.py
"""
Symbolic Execution Tools for Code Scalpel.

v0.3.0 "The Mathematician" - Security Analysis Edition

This module provides symbolic execution capabilities for Python code analysis.
Building on v0.2.0 "Redemption", this release adds STRING SUPPORT and
SECURITY ANALYSIS for detecting vulnerabilities.

Working Features (v0.3.0):
    - SymbolicAnalyzer: Main entry point for symbolic analysis
    - SecurityAnalyzer: Taint-based vulnerability detection
    - ConstraintSolver: Z3-powered satisfiability checking
    - SymbolicInterpreter: Path exploration with smart forking
    - TypeInferenceEngine: Int/Bool/String type tracking
    - TaintTracker: Data flow tracking for security analysis

Security Detectors:
    - SQL Injection (CWE-89)
    - Cross-Site Scripting (CWE-79)
    - Path Traversal (CWE-22)
    - Command Injection (CWE-78)

Sanitizer Support (v0.3.1):
    - Built-in sanitizer registry (html.escape, shlex.quote, etc.)
    - Custom sanitizer registration via register_sanitizer()
    - Configuration via pyproject.toml [tool.code-scalpel.sanitizers]
    - Type coercion (int, float, bool) fully clears taint

Float Support (v2.0.0):
    - [20251215_FEATURE] Full float/Real support in symbolic execution
    - Float constants evaluated using Z3 RealVal
    - Float type inference via TypeInferenceEngine
    - Float arithmetic operations (add, sub, mul, div)
    - Mixed int/float operations return float

Current Limitations:
    - Loops bounded to 10 iterations
    - Function calls are stubbed (not symbolically executed)

For production use cases with full type support:
    - code_scalpel.ast_tools (AST analysis)
    - code_scalpel.pdg_tools (Program Dependence Graphs)

Example (Symbolic Analysis):
    >>> from code_scalpel.symbolic_execution_tools import SymbolicAnalyzer
    >>> analyzer = SymbolicAnalyzer()
    >>> result = analyzer.analyze("x = 5; y = x * 2 if x > 0 else -x")
    >>> print(f"Paths: {result.total_paths}, Feasible: {result.feasible_count}")

Example (Security Analysis):
    >>> from code_scalpel.symbolic_execution_tools import analyze_security
    >>> result = analyze_security('''
    ...     user_id = request.args.get("id")
    ...     cursor.execute("SELECT * FROM users WHERE id=" + user_id)
    ... ''')
    >>> if result.has_vulnerabilities:
    ...     print(result.summary())

Example (Custom Sanitizer):
    >>> from code_scalpel.symbolic_execution_tools import (
    ...     register_sanitizer, SecuritySink
    ... )
    >>> register_sanitizer(
    ...     "my_sanitize_sql",
    ...     clears_sinks={SecuritySink.SQL_QUERY},
    ...     full_clear=False
    ... )
"""

import warnings

# [20251220_FEATURE] v3.0.4: Frontend Input Tracker (TypeScript/JS DOM Detection)
# [20251225_REFACTOR] Import from new location
from code_scalpel.integrations.protocol_analyzers.frontend.input_tracker import (
    DangerousSink,
    DangerousSinkType,
    DataFlow,
    FrontendAnalysisResult,
    FrontendFramework,
    FrontendInputTracker,
    InputSource,
    InputSourceType,
    analyze_frontend_codebase,
    analyze_frontend_file,
    get_xss_risks,
)

# [20251219_FEATURE] v3.0.4: GraphQL Schema Tracking
# [20251225_REFACTOR] Import from new location
from code_scalpel.integrations.protocol_analyzers.graphql.schema_tracker import (
    GraphQLArgument,
    GraphQLChangeSeverity,
    GraphQLChangeType,
    GraphQLField,
    GraphQLSchema,
    GraphQLSchemaChange,
    GraphQLSchemaDrift,
    GraphQLSchemaTracker,
    GraphQLType,
    GraphQLTypeKind,
    compare_graphql_files,
    compare_graphql_schemas,
    track_graphql_schema,
)

# [20251219_FEATURE] v3.0.4: gRPC Contract Analysis
# [20251225_REFACTOR] Import from new location
from code_scalpel.integrations.protocol_analyzers.grpc.contract_analyzer import (
    ContractIssue,
    GrpcContract,
    GrpcContractAnalyzer,
    GrpcService,
    IssueSeverity,
    RpcMethod,
    StreamingType,
    analyze_grpc_contract,
    analyze_grpc_file,
    validate_grpc_contract,
)

# [20251220_FEATURE] v3.0.4: Kafka Taint Tracking
# [20251225_REFACTOR] Import from new location
from code_scalpel.integrations.protocol_analyzers.kafka.taint_tracker import (
    KafkaAnalysisResult,
    KafkaConsumer,
    KafkaLibrary,
    KafkaPatternType,
    KafkaProducer,
    KafkaRiskLevel,
    KafkaTaintBridge,
    KafkaTaintTracker,
    KafkaTopicInfo,
    analyze_kafka_codebase,
    analyze_kafka_file,
    get_kafka_taint_bridges,
)

# [20251219_FEATURE] v3.0.4: Schema Drift Detection
# [20251225_REFACTOR] Import from new location
from code_scalpel.integrations.protocol_analyzers.schema.drift_detector import (
    ChangeSeverity,
    ChangeType,
    ProtobufParser,
    SchemaChange,
    SchemaDriftDetector,
    SchemaDriftResult,
    compare_json_schema_files,
    compare_protobuf_files,
)

# [20251225_REFACTOR] Import from new location
from code_scalpel.security.analyzers.security_analyzer import (
    SecurityAnalysisResult,
    SecurityAnalyzer,
    analyze_security,
    find_command_injections,
    find_path_traversals,
    find_sql_injections,
    find_xss,
)

# v0.3.0: Security Analysis
# [20251225_REFACTOR] Import from new location
from code_scalpel.security.analyzers.taint_tracker import (  # v0.3.1: Sanitizer Support; [20251216_FEATURE] v2.2.0: SSR Security
    SANITIZER_REGISTRY,
    SSR_SINK_PATTERNS,
    SanitizerInfo,
    SecuritySink,
    TaintedValue,
    TaintInfo,
    TaintLevel,
    TaintSource,
    TaintTracker,
    Vulnerability,
    detect_ssr_framework,
    detect_ssr_vulnerabilities,
    load_sanitizers_from_config,
    register_sanitizer,
)

# [20251216_FEATURE] v2.3.0: Unified Polyglot Sink Detection
# [20251225_REFACTOR] Import from new location
from code_scalpel.security.analyzers.unified_sink_detector import (
    OWASP_COVERAGE,
    UNIFIED_SINKS,
    DetectedSink,
    Language,
    SinkDefinition,
    UnifiedSinkDetector,
)

from .constraint_solver import ConstraintSolver
from .engine import SymbolicAnalyzer, SymbolicExecutionEngine

# [20251215_REFACTOR] Move warning configuration after imports to satisfy import-order lint rules.
warnings.filterwarnings(
    "ignore",
    message="ast.(Num|Str) is deprecated and will be removed in Python 3.14",
    category=DeprecationWarning,
)

# [20251213_FEATURE] v1.5.1: Cross-File Taint Analysis
# [20251225_REFACTOR] Import from new location
try:
    from code_scalpel.security.analyzers.cross_file_taint import (
        CrossFileSink,
        CrossFileTaintFlow,
        CrossFileTaintResult,
        CrossFileTaintTracker,
        CrossFileVulnerability,
        TaintedParameter,
    )
except ImportError:
    CrossFileTaintTracker = None
    CrossFileTaintResult = None
    CrossFileTaintFlow = None
    CrossFileVulnerability = None
    TaintedParameter = None
    CrossFileSink = None

# [20251226_FEATURE] v3.2.9: Path Prioritization (Pro Tier - Crash Optimization)
from .path_prioritization import (
    CrashPrioritizer,
    ErrorPattern,
    PathPrioritizer,
    PathScore,
    PrioritizationStrategy,
    prioritize_for_crashes,
)

# [20251218_BUGFIX] Disabled import warning - info is in docs
# warnings.warn(
#     "symbolic_execution_tools v1.2.0 (Stable). "
#     "Supports Int/Bool/String. See docs for type limitations.",
#     category=UserWarning,
#     stacklevel=2,
# )

__all__ = [
    # Core symbolic execution
    "ConstraintSolver",
    "SymbolicExecutionEngine",
    "SymbolicAnalyzer",
    # v0.3.0: Security Analysis
    "TaintTracker",
    "TaintSource",
    "TaintLevel",
    "SecuritySink",
    "TaintInfo",
    "TaintedValue",
    "Vulnerability",
    "SecurityAnalyzer",
    "SecurityAnalysisResult",
    "analyze_security",
    "find_sql_injections",
    "find_xss",
    "find_command_injections",
    "find_path_traversals",
    # v0.3.1: Sanitizer Support
    "SanitizerInfo",
    "SANITIZER_REGISTRY",
    "register_sanitizer",
    "load_sanitizers_from_config",
    # [20251216_FEATURE] v2.2.0: SSR Security
    "SSR_SINK_PATTERNS",
    "detect_ssr_vulnerabilities",
    "detect_ssr_framework",
    # [20251216_FEATURE] v2.3.0: Unified Polyglot Sink Detection
    "UnifiedSinkDetector",
    "SinkDefinition",
    "DetectedSink",
    "Language",
    "UNIFIED_SINKS",
    "OWASP_COVERAGE",
    # [20251219_FEATURE] v3.0.4: Schema Drift Detection
    "SchemaDriftDetector",
    "SchemaDriftResult",
    "SchemaChange",
    "ChangeType",
    "ChangeSeverity",
    "ProtobufParser",
    "compare_protobuf_files",
    "compare_json_schema_files",
    # [20251219_FEATURE] v3.0.4: gRPC Contract Analysis
    "GrpcContractAnalyzer",
    "GrpcContract",
    "GrpcService",
    "RpcMethod",
    "StreamingType",
    "ContractIssue",
    "IssueSeverity",
    "analyze_grpc_contract",
    "validate_grpc_contract",
    "analyze_grpc_file",
    # [20251219_FEATURE] v3.0.4: GraphQL Schema Tracking
    "GraphQLSchemaTracker",
    "GraphQLSchema",
    "GraphQLType",
    "GraphQLTypeKind",
    "GraphQLField",
    "GraphQLArgument",
    "GraphQLSchemaDrift",
    "GraphQLSchemaChange",
    "GraphQLChangeType",
    "GraphQLChangeSeverity",
    "track_graphql_schema",
    "compare_graphql_schemas",
    "compare_graphql_files",
    # [20251220_FEATURE] v3.0.4: Kafka Taint Tracking
    "KafkaTaintTracker",
    "KafkaProducer",
    "KafkaConsumer",
    "KafkaTaintBridge",
    "KafkaTopicInfo",
    "KafkaAnalysisResult",
    "KafkaLibrary",
    "KafkaPatternType",
    "KafkaRiskLevel",
    "analyze_kafka_file",
    "analyze_kafka_codebase",
    "get_kafka_taint_bridges",
    # [20251220_FEATURE] v3.0.4: Frontend Input Tracker
    "FrontendInputTracker",
    "FrontendAnalysisResult",
    "FrontendFramework",
    "InputSource",
    "InputSourceType",
    "DangerousSink",
    "DangerousSinkType",
    "DataFlow",
    "analyze_frontend_file",
    "analyze_frontend_codebase",
    "get_xss_risks",
    # v1.5.1: Cross-File Taint Analysis
    "CrossFileTaintTracker",
    "CrossFileTaintResult",
    "CrossFileTaintFlow",
    "CrossFileVulnerability",
    "TaintedParameter",
    "CrossFileSink",
    # [20251226_FEATURE] v3.2.9: Path Prioritization (Pro Tier)
    "PathPrioritizer",
    "PathScore",
    "PrioritizationStrategy",
    "ErrorPattern",
    "prioritize_for_crashes",
    "CrashPrioritizer",
]

# TODO: Module Enhancement Roadmap
# ===================================
#
# COMMUNITY (Current & Planned):
# Documentation & Guides:
# - TODO [COMMUNITY]: Improve documentation and examples (current)
# - TODO [COMMUNITY]: Add type annotations for all exported functions
# - TODO [COMMUNITY]: Create troubleshooting guide for common analysis issues
# - TODO [COMMUNITY]: Add performance benchmarks and optimization tips
# - TODO [COMMUNITY]: Document constraint solver limitations
# - TODO [COMMUNITY]: Create quick-start guide for each major tool
# - TODO [COMMUNITY]: Add configuration file format documentation
# - TODO [COMMUNITY]: Create API reference documentation for all exports
# - TODO [COMMUNITY]: Document supported Python versions and dependencies
# - TODO [COMMUNITY]: Add FAQ for common user questions
# - TODO [COMMUNITY]: Create migration guide from symbolic_execution v0.x to v1.x
# - TODO [COMMUNITY]: Document Z3 version compatibility
#
# Examples & Tutorials:
# - TODO [COMMUNITY]: Add basic symbolic analysis tutorial
# - TODO [COMMUNITY]: Create security analysis step-by-step guide
# - TODO [COMMUNITY]: Add sanitizer registration examples
# - TODO [COMMUNITY]: Document taint tracking workflow
# - TODO [COMMUNITY]: Create end-to-end vulnerability detection example
# - TODO [COMMUNITY]: Add Jupyter notebook tutorials
#
# Testing & Validation:
# - TODO [COMMUNITY]: Add integration tests for all exported functions
# - TODO [COMMUNITY]: Create test coverage dashboard
# - TODO [COMMUNITY]: Add regression test suite
# - TODO [COMMUNITY]: Document test execution procedure
#
# PRO (Enhanced Features):
# Core Engine Enhancements:
# - TODO [PRO]: Implement concolic execution for better path coverage
# - TODO [PRO]: Add support for symbolic List/Dict types
# - TODO [PRO]: Implement path prioritization heuristics
# - TODO [PRO]: Add performance profiling and optimization
# - TODO [PRO]: Implement incremental constraint solving
# - TODO [PRO]: Support async/await taint propagation
# - TODO [PRO]: Implement lambda function analysis
# - TODO [PRO]: Add generator and coroutine support
# - TODO [PRO]: Support context manager analysis
# - TODO [PRO]: Implement decorator analysis
#
# Analysis Capabilities:
# - TODO [PRO]: Add machine learning-based sanitizer detection
# - TODO [PRO]: Support custom vulnerability patterns via DSL
# - TODO [PRO]: Implement cross-language taint tracking
# - TODO [PRO]: Add real-time analysis mode for IDE integration
# - TODO [PRO]: Support module-level taint analysis
# - TODO [PRO]: Implement call graph visualization
# - TODO [PRO]: Add data flow graph visualization
# - TODO [PRO]: Support incremental re-analysis on code changes
#
# Performance & Scalability:
# - TODO [PRO]: Implement constraint caching system
# - TODO [PRO]: Add result memoization for repeated analyses
# - TODO [PRO]: Optimize Z3 solver configuration
# - TODO [PRO]: Implement adaptive timeout strategies
# - TODO [PRO]: Add parallel path exploration support
# - TODO [PRO]: Implement garbage collection for old states
#
# Vulnerability Detection:
# - TODO [PRO]: Add NoSQL injection detection
# - TODO [PRO]: Support LDAP injection detection
# - TODO [PRO]: Add Server-Side Template Injection (SSTI) detection
# - TODO [PRO]: Implement XXE injection detection
# - TODO [PRO]: Add CORS misconfiguration detection
# - TODO [PRO]: Support authentication bypass detection
# - TODO [PRO]: Implement insecure randomness detection
#
# ENTERPRISE (Advanced Capabilities):
# Distributed & Scalability:
# - TODO [ENTERPRISE]: Implement distributed symbolic execution
# - TODO [ENTERPRISE]: Add distributed constraint solving
# - TODO [ENTERPRISE]: Support all languages in polyglot parsing
# - TODO [ENTERPRISE]: Implement advanced path exploration strategies
# - TODO [ENTERPRISE]: Add full async/coroutine support
# - TODO [ENTERPRISE]: Implement cluster-aware analysis distribution
# - TODO [ENTERPRISE]: Support horizontal scaling via Kubernetes
# - TODO [ENTERPRISE]: Add load balancing for solver instances
#
# Advanced Analysis:
# - TODO [ENTERPRISE]: Implement dataflow-sensitive taint tracking
# - TODO [ENTERPRISE]: Add probabilistic vulnerability scoring
# - TODO [ENTERPRISE]: Support custom vulnerability databases
# - TODO [ENTERPRISE]: Implement semantic similarity for exploit detection
# - TODO [ENTERPRISE]: Add continuous security monitoring mode
# - TODO [ENTERPRISE]: Implement vulnerability prediction via ML
# - TODO [ENTERPRISE]: Support zero-day vulnerability detection
# - TODO [ENTERPRISE]: Add exploit chain analysis
#
# Integration & Compliance:
# - TODO [ENTERPRISE]: Add SIEM integration (Splunk, ELK, etc.)
# - TODO [ENTERPRISE]: Support compliance reporting (PCI-DSS, HIPAA, SOC2)
# - TODO [ENTERPRISE]: Implement audit trail and logging
# - TODO [ENTERPRISE]: Add SAML/OAuth integration for multi-tenant access
# - TODO [ENTERPRISE]: Support custom policy engines
# - TODO [ENTERPRISE]: Implement vulnerability remediation workflows
# - TODO [ENTERPRISE]: Add AI-powered remediation suggestions
#
# Intelligence & Automation:
# - TODO [ENTERPRISE]: Implement ML-based false positive filtering
# - TODO [ENTERPRISE]: Support automated exploit generation
# - TODO [ENTERPRISE]: Add behavioral analysis for code anomalies
# - TODO [ENTERPRISE]: Implement supply chain attack detection
# - TODO [ENTERPRISE]: Support monorepo-wide analysis
# - TODO [ENTERPRISE]: Add intelligent input generation via genetic algorithms
# - TODO [ENTERPRISE]: Implement continuous fuzzing integration
