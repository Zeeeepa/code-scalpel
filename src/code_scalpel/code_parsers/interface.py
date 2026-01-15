"""Parser Interface - Unified parser contract across all languages.

# TODO [COMMUNITY] Add tokens: List[Token] with detailed token information
# TODO [COMMUNITY] Add source_map: Optional[SourceMap] for position tracking
# TODO [COMMUNITY] Add metadata: Dict[str, Any] for parser-specific information
# TODO [COMMUNITY] Add parse_time_ms: float for performance tracking
# TODO [COMMUNITY] Add file_path: Optional[str] for context
# TODO [COMMUNITY] Add get_capabilities() -> ParserCapabilities method
# TODO [COMMUNITY] Support capability flags: incremental, types, formatting, etc.
# TODO [COMMUNITY] Add get_version() -> str method for parser versioning
# TODO [COMMUNITY] Add get_supported_features() -> List[str] method
# TODO [COMMUNITY] Add get_imports(ast_tree) -> List[Import] method
# TODO [COMMUNITY] Add get_variables(ast_tree) -> List[Variable] method
# TODO [COMMUNITY] Add get_comments(ast_tree) -> List[Comment] method
# TODO [COMMUNITY] Add get_complexity(ast_tree) -> ComplexityMetrics method
# TODO [COMMUNITY] Create ParseError dataclass with detailed information
# TODO [COMMUNITY] Add get_errors() -> List[ParseError] method
# TODO [COMMUNITY] Add get_warnings() -> List[ParseWarning] method
# TODO [COMMUNITY] Support severity levels: error, warning, info, hint
# TODO [COMMUNITY] Create ParserConfig dataclass
# TODO [COMMUNITY] Add configure(config: ParserConfig) method
# TODO [COMMUNITY] Support parser-specific configuration options
# TODO [COMMUNITY] Add get_config() -> ParserConfig method
# TODO [PRO] Add parse_incremental(code, changes) -> ParseResult method
# TODO [PRO] Add get_changed_nodes(old_ast, new_ast) -> List[Node] method
# TODO [PRO] Support efficient AST updates
# TODO [PRO] Add parse_stream(code_stream) -> Iterator[ParseResult]
# TODO [PRO] Add resolve_symbol(name, position) -> Symbol method
# TODO [PRO] Add get_type_info(node) -> TypeInfo method
# TODO [PRO] Add find_references(symbol) -> List[Reference] method
# TODO [PRO] Add get_hover_info(position) -> HoverInfo method
# TODO [PRO] Add transform(ast_tree, transformer) -> AST method
# TODO [PRO] Add apply_refactoring(refactoring) -> CodeEdit method
# TODO [PRO] Add format(code, style) -> str method
# TODO [PRO] Add generate_code(ast_tree) -> str method
# TODO [PRO] Add validate(code) -> ValidationResult method
# TODO [PRO] Add check_style(code, style_guide) -> List[StyleViolation] method
# TODO [PRO] Add find_security_issues(ast_tree) -> List[SecurityIssue]
# TODO [PRO] Add check_complexity(ast_tree, thresholds) -> ComplexityReport
# TODO [PRO] Add get_parse_metrics() -> ParseMetrics method
# TODO [PRO] Add benchmark(code, iterations) -> BenchmarkResult method
# TODO [PRO] Add profile_memory_usage() -> MemoryProfile method
# TODO [PRO] Add get_bottlenecks() -> List[Bottleneck] method
# TODO [ENTERPRISE] Add parse_distributed(files, workers) -> List[ParseResult] method
# TODO [ENTERPRISE] Add coordinate_parsers(parser_nodes) -> Coordinator method
# TODO [ENTERPRISE] Add aggregate_results(results) -> AggregateResult method
# TODO [ENTERPRISE] Add get_parsing_status(job_id) -> JobStatus method
# TODO [ENTERPRISE] Add get_audit_log() -> List[AuditEntry] method
# TODO [ENTERPRISE] Add record_parsing_event(event) method
# TODO [ENTERPRISE] Add check_compliance(policy) -> ComplianceReport method
# TODO [ENTERPRISE] Add generate_compliance_report() -> Report method
# TODO [ENTERPRISE] Add set_tenant_context(tenant_id) method
# TODO [ENTERPRISE] Add get_tenant_quota() -> Quota method
# TODO [ENTERPRISE] Add get_tenant_metrics() -> TenantMetrics method
# TODO [ENTERPRISE] Add isolate_resources(tenant_id) method
# TODO [ENTERPRISE] Add export_metrics(exporter) method
# TODO [ENTERPRISE] Add get_health_status() -> HealthStatus method
# TODO [ENTERPRISE] Add configure_alerts(alert_config) method
# TODO [ENTERPRISE] Add get_sla_metrics() -> SLAMetrics method
# TODO [ENTERPRISE] Add predict_parse_time(code) -> float method
# TODO [ENTERPRISE] Add suggest_optimizations() -> List[Optimization] method
# TODO [ENTERPRISE] Add detect_anomalies(parse_results) -> List[Anomaly] method
# TODO [ENTERPRISE] Add adaptive_configure() method
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


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
