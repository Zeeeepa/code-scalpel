"""Parser Interface - Unified parser contract across all languages.

============================================================================
TODO ITEMS: code_parsers/interface.py
============================================================================
COMMUNITY TIER - Core Interface Features (P0-P2)
============================================================================

[P0_CRITICAL] Extend ParseResult dataclass:
    - Add tokens: List[Token] with detailed token information
    - Add source_map: Optional[SourceMap] for position tracking
    - Add metadata: Dict[str, Any] for parser-specific information
    - Add parse_time_ms: float for performance tracking
    - Add file_path: Optional[str] for context
    - Test count: 15 tests (result validation, serialization)

[P1_HIGH] Add parser capability interface:
    - Add get_capabilities() -> ParserCapabilities method
    - Support capability flags: incremental, types, formatting, etc.
    - Add get_version() -> str method for parser versioning
    - Add get_supported_features() -> List[str] method
    - Test count: 10 tests (capability queries)

[P1_HIGH] Enhance IParser interface methods:
    - Add get_imports(ast_tree) -> List[Import] method
    - Add get_variables(ast_tree) -> List[Variable] method
    - Add get_comments(ast_tree) -> List[Comment] method
    - Add get_complexity(ast_tree) -> ComplexityMetrics method
    - Test count: 20 tests (extraction methods)

[P2_MEDIUM] Add error reporting interface:
    - Create ParseError dataclass with detailed information
    - Add get_errors() -> List[ParseError] method
    - Add get_warnings() -> List[ParseWarning] method
    - Support severity levels: error, warning, info, hint
    - Test count: 15 tests (error reporting, severity)

[P2_MEDIUM] Add configuration interface:
    - Create ParserConfig dataclass
    - Add configure(config: ParserConfig) method
    - Support parser-specific configuration options
    - Add get_config() -> ParserConfig method
    - Test count: 10 tests (configuration)

============================================================================
PRO TIER - Advanced Interface Features (P1-P3)
============================================================================

[P1_HIGH] Add incremental parsing support:
    - Add parse_incremental(code, changes) -> ParseResult method
    - Add get_changed_nodes(old_ast, new_ast) -> List[Node] method
    - Support efficient AST updates
    - Add parse_stream(code_stream) -> Iterator[ParseResult]
    - Test count: 25 tests (incremental parsing, streaming)

[P1_HIGH] Add semantic analysis interface:
    - Add resolve_symbol(name, position) -> Symbol method
    - Add get_type_info(node) -> TypeInfo method
    - Add find_references(symbol) -> List[Reference] method
    - Add get_hover_info(position) -> HoverInfo method
    - Test count: 30 tests (semantic analysis, symbol resolution)

[P2_MEDIUM] Add code transformation interface:
    - Add transform(ast_tree, transformer) -> AST method
    - Add apply_refactoring(refactoring) -> CodeEdit method
    - Add format(code, style) -> str method
    - Add generate_code(ast_tree) -> str method
    - Test count: 25 tests (transformation, formatting, generation)

[P2_MEDIUM] Add validation interface:
    - Add validate(code) -> ValidationResult method
    - Add check_style(code, style_guide) -> List[StyleViolation] method
    - Add find_security_issues(ast_tree) -> List[SecurityIssue]
    - Add check_complexity(ast_tree, thresholds) -> ComplexityReport
    - Test count: 30 tests (validation, style, security)

[P3_LOW] Add performance profiling interface:
    - Add get_parse_metrics() -> ParseMetrics method
    - Add benchmark(code, iterations) -> BenchmarkResult method
    - Add profile_memory_usage() -> MemoryProfile method
    - Add get_bottlenecks() -> List[Bottleneck] method
    - Test count: 20 tests (profiling, benchmarking)

============================================================================
ENTERPRISE TIER - Enterprise Interface Features (P2-P4)
============================================================================

[P2_MEDIUM] Add distributed parsing interface:
    - Add parse_distributed(files, workers) -> List[ParseResult] method
    - Add coordinate_parsers(parser_nodes) -> Coordinator method
    - Add aggregate_results(results) -> AggregateResult method
    - Add get_parsing_status(job_id) -> JobStatus method
    - Test count: 30 tests (distribution, coordination)

[P2_MEDIUM] Add audit and compliance interface:
    - Add get_audit_log() -> List[AuditEntry] method
    - Add record_parsing_event(event) method
    - Add check_compliance(policy) -> ComplianceReport method
    - Add generate_compliance_report() -> Report method
    - Test count: 25 tests (audit, compliance)

[P3_LOW] Add multi-tenant interface:
    - Add set_tenant_context(tenant_id) method
    - Add get_tenant_quota() -> Quota method
    - Add get_tenant_metrics() -> TenantMetrics method
    - Add isolate_resources(tenant_id) method
    - Test count: 20 tests (multi-tenancy, isolation)

[P3_LOW] Add enterprise monitoring interface:
    - Add export_metrics(exporter) method
    - Add get_health_status() -> HealthStatus method
    - Add configure_alerts(alert_config) method
    - Add get_sla_metrics() -> SLAMetrics method
    - Test count: 20 tests (monitoring, health, alerts)

[P4_LOW] Add ML-driven interface:
    - Add predict_parse_time(code) -> float method
    - Add suggest_optimizations() -> List[Optimization] method
    - Add detect_anomalies(parse_results) -> List[Anomaly] method
    - Add adaptive_configure() method
    - Test count: 25 tests (ML integration, predictions)

============================================================================
TOTAL TEST ESTIMATE: 355 tests (90 COMMUNITY + 130 PRO + 135 ENTERPRISE)
============================================================================
"""

from abc import ABC, abstractmethod
from typing import Any, List, Dict
from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CPP = "cpp"
    UNKNOWN = "unknown"


@dataclass
class ParseResult:
    """Result of code parsing."""

    ast: Any  # AST structure (language-dependent)
    errors: List[Dict[str, Any]]
    warnings: List[str]
    metrics: Dict[str, Any]
    language: Language


class IParser(ABC):
    """Interface for language-specific parsers."""

    @abstractmethod
    def parse(self, code: str) -> ParseResult:
        """Parse source code into an AST."""
        pass

    @abstractmethod
    def get_functions(self, ast_tree: Any) -> List[str]:
        """Get list of function names."""
        pass

    @abstractmethod
    def get_classes(self, ast_tree: Any) -> List[str]:
        """Get list of class names."""
        pass
