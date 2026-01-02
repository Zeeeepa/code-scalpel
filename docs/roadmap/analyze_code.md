# analyze_code Tool Roadmap

**Tool Name:** `analyze_code`  
**Tool Version:** v1.0  
**Code Scalpel Version:** v3.3  
**Current Status:** Stable  
**Primary Module (MCP Tool Implementation):** `src/code_scalpel/mcp/server.py` (`_analyze_code_sync`)  
**Related Module (Python-only deeper analysis pipeline):** `src/code_scalpel/analysis/code_analyzer.py`  
**Tier Availability:** All tiers (Community, Pro, Enterprise)

---

## Overview

The `analyze_code` MCP tool provides static (non-executing) code structure analysis.

What it does today (v3.3):
- Supports **Python** via `ast`.
- Supports **JavaScript/TypeScript** via `tree-sitter`.
- Supports **Java** via a dedicated analyzer.

It extracts functions/classes/imports, computes a basic complexity score, and returns basic heuristics ("issues"). It does **not** run a full vulnerability scan; use `security_scan` for that.

---

## Current Capabilities (v1.0)

### Community Tier
- Parse Python, JavaScript, TypeScript, Java
- Extract functions and classes
- Extract methods list per class (via class details)
- Import parsing
- Basic complexity scoring (cyclomatic-ish)
- Line count metrics
- Notes:
	- No docstring extraction in the MCP `analyze_code` response.
	- “Issues” are lightweight heuristics (e.g., naming heuristics), not a vulnerability scan.
- Configured limits (see `.code-scalpel/limits.toml`):
	- `max_file_size_mb = 1`
	- `languages = ["python", "javascript", "typescript", "java"]`

### Pro Tier
- All Community features
- Tier-gated enrichments (capability-dependent; some are language-specific):
	- Cognitive complexity (Python)
	- Code smell detection (Python)
	- Halstead metrics (Python)
	- Duplicate code block detection (Python)
	- Dependency graph extraction (Python)
	- Framework detection (as `frameworks`) (Python/Java/JS/TS best-effort)
	- Dead code hints (as `dead_code_hints`) (Python best-effort)
	- Decorator summary (as `decorator_summary`) (Python best-effort)
	- Type/generic usage summary (as `type_summary`) (Python best-effort)
- Configured limits (see `.code-scalpel/limits.toml`):
	- `max_file_size_mb = 10`
	- `languages` includes `go`/`rust` in config, but the MCP `analyze_code` implementation currently only routes `python/javascript/typescript/java`.

### Enterprise Tier

- All Pro features
- Tier-gated enrichments (capability-dependent; some are language-specific):
	- Custom rules (as violations) (Python)
	- Compliance checks (as issues) (Python)
	- Organization pattern heuristics (Python)
	- Naming convention checks (Python)
	- Architecture pattern hints (as `architecture_patterns`) (best-effort)
	- Technical debt scoring summary (as `technical_debt`) (Python best-effort)
	- API surface summary (as `api_surface`) (Python/Java/JS/TS best-effort)
	- Priority ordering marker (as `prioritized`) (best-effort)
	- Complexity trends (as `complexity_trends`, requires `file_path`) (best-effort, in-memory per server process)
- Configured limits (see `.code-scalpel/limits.toml`):
	- `max_file_size_mb = 100`
	- `languages` is “unlimited by omission” in config, but the MCP `analyze_code` implementation currently only routes `python/javascript/typescript/java`.

---
## MCP Request/Response Examples

### MCP Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "mcp_code-scalpel_analyze_code",
    "arguments": {
      "code": "def calculate_tax(amount, rate):\n    if rate > 1:\n        rate = rate / 100\n    return amount * rate\n\nclass TaxCalculator:\n    def __init__(self, default_rate=0.1):\n        self.rate = default_rate\n    \n    def compute(self, amount):\n        return calculate_tax(amount, self.rate)",
      "language": "python"
    }
  },
  "id": 1
}
```

### Community Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "language": "python",
    "functions": ["calculate_tax"],
    "classes": ["TaxCalculator"],
    "imports": [],
    "complexity_score": 2,
    "lines_of_code": 11,
    "has_main": false,
    "issues": [
      {
        "type": "naming",
        "message": "Function 'calculate_tax' uses snake_case (OK)",
        "severity": "info"
      }
    ]
  },
  "id": 1
}
```

### Pro Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "language": "python",
    "functions": ["calculate_tax"],
    "classes": ["TaxCalculator"],
    "imports": [],
    "complexity_score": 2,
    "cognitive_complexity": 3,
    "lines_of_code": 11,
    "has_main": false,
    "issues": [],
    "code_smells": [],
    "halstead_metrics": {
      "vocabulary": 12,
      "length": 18,
      "difficulty": 4.5,
      "effort": 81.0
    },
    "duplicate_blocks": [],
    "dependency_graph": {},
    "frameworks": [],
    "dead_code_hints": [],
    "decorator_summary": [],
    "type_summary": {
      "typed_params": 0,
      "untyped_params": 4,
      "return_annotations": 0
    }
  },
  "id": 1
}
```

### Enterprise Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "language": "python",
    "functions": ["calculate_tax"],
    "classes": ["TaxCalculator"],
    "imports": [],
    "complexity_score": 2,
    "cognitive_complexity": 3,
    "lines_of_code": 11,
    "has_main": false,
    "issues": [],
    "code_smells": [],
    "halstead_metrics": {
      "vocabulary": 12,
      "length": 18,
      "difficulty": 4.5,
      "effort": 81.0
    },
    "violations": [],
    "architecture_patterns": ["utility-module"],
    "technical_debt": {
      "score": 0.15,
      "category": "low",
      "factors": ["missing_type_hints"]
    },
    "api_surface": {
      "public_functions": ["calculate_tax"],
      "public_classes": ["TaxCalculator"],
      "exported_symbols": 2
    },
    "prioritized": true,
    "complexity_trends": {
      "current": 2,
      "previous": null,
      "trend": "stable"
    }
  },
  "id": 1
}
```

---
## Roadmap

### Cross-Cutting Research Topics

**Research topics (cross-cutting):**
- Evaluation harness: golden fixtures per language, regression scoring, and release gates
- False-positive/false-negative budgets per feature class (smells, dead code hints, patterns)
- Confidence scoring and “best-effort” semantics: when to omit fields vs return partials
- Determinism guarantees: stable outputs across platforms, parser versions, and parallelism
- Security and privacy boundaries: ensure analysis artifacts do not leak source or secrets
- Schema/versioning strategy: adding fields safely, deprecations, and compatibility tests

**Success metrics (cross-cutting):**
- Determinism: identical outputs for the same input across OS/CPU within supported matrix
- Contract stability: backward-compatible schema changes only; automated compatibility checks in CI
- Quality gates: measurable FP/FN budgets per feature category with tracked regressions
- Security hygiene: zero known secret exfiltration paths in generated artifacts; routine scanning in CI

### Q1 2026: Enhanced Language Support

#### Community Tier
- [ ] Add Rust AST parsing support
- [ ] Add PHP AST parsing support
- [ ] Improve TypeScript generic handling
- [ ] Enhanced error messages for parsing failures
- [ ] Reconcile `.code-scalpel/limits.toml` language lists with MCP routing (either implement routing or narrow config/docs)

**Research topics (Q1 / Community):**
- Rust parsing options tradeoffs (tree-sitter-rust vs rust-analyzer AST vs `syn`-based parsing)
- PHP parsing options (tree-sitter-php vs nikic/php-parser) and error recovery behavior
- TypeScript generic/type extraction quality using the TypeScript compiler API vs tree-sitter heuristics
- Parser error UX: actionable diagnostics, snippet localization, and recovery strategies

**Success metrics (Q1 / Community):**
- New languages: function/class extraction accuracy meets or exceeds existing Community baselines
- Error UX: parse failures include actionable reason + localized span for the majority of failures
- Limits alignment: config and routing agree (no “advertised but unsupported” languages)

#### Pro Tier
- [ ] Add Swift AST parsing
- [ ] Add Kotlin AST parsing
- [ ] Cross-language dependency tracking
- [ ] Semantic code search within analysis

**Research topics (Q1 / Pro):**
- “Good enough” dependency graphs across languages: import graphs vs symbol graphs vs call graphs
- Multi-language symbol resolution strategies (LSP-backed vs static heuristics)
- Semantic search quality metrics (precision/recall, hallucination avoidance) and privacy constraints
- Duplicate-code detection beyond Python (token-based vs AST-based, normalization strategies)

**Success metrics (Q1 / Pro):**
- Dependency tracking: stable graphs on representative repos with bounded false edges
- Semantic search: measured precision/recall targets on a curated benchmark; no source invention
- Duplicate detection: configurable threshold with acceptable false-positive rates on real-world code

#### Enterprise Tier
- [ ] Custom language grammar support
- [ ] Multi-file analysis orchestration
- [ ] Architecture diagram generation
- [ ] Automated refactoring suggestions

**Research topics (Q1 / Enterprise):**
- User-supplied grammar safety model and sandboxing (tree-sitter grammar ingestion risks)
- Multi-file orchestration: incremental dependency ordering, partial failures, and caching boundaries
- Architecture diagram extraction approaches (C4-ish hints, package boundaries, dependency slicing)
- Refactoring suggestion safety: behavior-preservation checks and confidence scoring

**Success metrics (Q1 / Enterprise):**
- Orchestration: multi-file analysis completes under defined time/memory budgets on large repos
- Diagram generation: produces usable, stable diagrams for a curated set of architectures
- Refactoring suggestions: includes confidence + safety checks; low regression rate in evaluation suite

### Q2 2026: Performance & Scalability

#### All Tiers
- [ ] Incremental analysis (only re-analyze changed code)
- [ ] Parallel file processing
- [ ] Memory optimization for large files
- [ ] Streaming analysis for huge codebases

**Research topics (Q2 / All):**
- Incremental parsing primitives per language (AST diffing vs reparse-on-change)
- Deterministic parallelism (stable outputs across worker counts)
- Memory profiles per parser (tree-sitter vs language-native parsers) and mitigation tactics
- Streaming outputs contract (partial result schemas, progress reporting, backpressure)

**Success metrics (Q2 / All):**
- Incremental: re-analysis time scales with changed regions, not full file size
- Parallel: throughput improves with cores while preserving deterministic results
- Memory: bounded peak memory usage for large files within defined envelopes
- Streaming: partial outputs are schema-valid and order-stable under backpressure

#### Pro Tier
- [ ] Distributed analysis across worker nodes
- [ ] Smart caching with invalidation
- [ ] Delta analysis (compare versions)

**Research topics (Q2 / Pro):**
- Cache invalidation keys (file content hash vs semantic hash) and correctness pitfalls
- Delta analysis UX: presenting diffs in a stable, low-noise way
- Cost model for distributed analysis (fan-out, queueing, shard boundaries)

**Success metrics (Q2 / Pro):**
- Caching: correctness-preserving invalidation (no stale results in benchmark suite)
- Delta: low-noise diff output with stable ordering and minimal churn between runs
- Distributed: predictable scaling with observability (queue time, worker utilization)

#### Enterprise Tier
- [ ] Cluster-based analysis
- [ ] Real-time analysis streaming
- [ ] Historical trend analysis
- [ ] Predictive analysis ("this will likely cause issues")

**Research topics (Q2 / Enterprise):**
- Persistence model for historical trends (in-memory vs durable store; retention/aggregation)
- Real-time streaming transport choices and failure semantics
- “Predictive analysis” framing and calibration (avoid overconfident outputs; measure accuracy)

**Success metrics (Q2 / Enterprise):**
- Trends: durable, queryable history with clear retention/aggregation policies
- Streaming: defined delivery guarantees and graceful degradation under failures
- Predictive: calibrated confidence; tracked precision/recall against post-merge outcomes

### Q3 2026: AI-Enhanced Analysis

#### Pro Tier
- [ ] ML-based code smell detection
- [ ] Intelligent complexity prediction
- [ ] Automated documentation generation
- [ ] Code pattern mining

**Research topics (Q3 / Pro):**
- Ground truth for “code smells”: labeling strategy and inter-rater reliability
- Complexity prediction evaluation (baseline heuristics vs learned models)
- Documentation generation constraints (non-executing, no invented APIs, source-grounded)
- Pattern mining: clustering methods and how to avoid leaking sensitive code in artifacts

**Success metrics (Q3 / Pro):**
- Smells: measurable reduction in high-severity false positives vs heuristic baselines
- Complexity prediction: outperforms baseline on held-out benchmark; calibrated uncertainty
- Docs: source-grounded outputs with quality rubric and low hallucination rate
- Pattern mining: produces stable clusters with clear utility and privacy guarantees

#### Enterprise Tier
- [ ] Custom ML model training on org codebase
- [ ] Anomaly detection ("this doesn't match your patterns")
- [ ] Security vulnerability prediction
- [ ] Technical debt forecasting

**Research topics (Q3 / Enterprise):**
- Org-trained models: data governance, opt-in boundaries, and reproducibility
- Anomaly detection: defining “normal” per repo/team and reducing false positives
- Vulnerability prediction: positioning vs deterministic scanners; validation and disclaimers
- Debt forecasting: what signals matter (churn, complexity trends, ownership) and how to calibrate

**Success metrics (Q3 / Enterprise):**
- Org training: reproducible builds with clear data lineage and opt-out controls
- Anomaly detection: false-positive rate within defined budgets per repo/team
- Vulnerability prediction: measured lift over baseline heuristics; conservative confidence
- Debt forecasting: correlates with later remediation effort; clear uncertainty bounds

### Q4 2026: Integration & Automation

#### Community Tier
- [ ] GitHub Action integration
- [ ] GitLab CI integration
- [ ] Pre-commit hook support

**Research topics (Q4 / Community):**
- Minimal CI contract (inputs/outputs) that works across providers
- Pre-commit ergonomics: speed budgets, caching, and “changed files only” operation

**Success metrics (Q4 / Community):**
- CI: drop-in setup with predictable exit codes and machine-readable outputs
- Pre-commit: completes within agreed latency budgets on typical changed-file sets

#### Pro Tier
- [ ] IDE plugin (VSCode, IntelliJ)
- [ ] Slack/Teams notifications
- [ ] Jira integration for technical debt tracking
- [ ] SonarQube export compatibility

**Research topics (Q4 / Pro):**
- IDE integration surface: LSP vs direct extension APIs; latency and offline behavior
- Notifications: deduping, routing, and severity mapping to avoid alert fatigue
- Interop formats: SARIF vs Sonar formats vs custom JSON; compatibility testing

**Success metrics (Q4 / Pro):**
- IDE: interactive latency within defined bounds; resilient offline behavior
- Notifications: low duplicate alert rate; configurable routing by severity/category
- Exports: validated compatibility with at least one reference pipeline per target format

#### Enterprise Tier
- [ ] ServiceNow integration
- [ ] Custom webhook support
- [ ] SSO/SAML authentication
- [ ] Audit log streaming to SIEM

**Research topics (Q4 / Enterprise):**
- Audit log schema and integrity (tamper evidence, correlation IDs)
- SIEM export formats and volume control (sampling/aggregation)
- Auth boundary decisions (tool server vs platform identity) and deployment patterns

**Success metrics (Q4 / Enterprise):**
- Audit logs: complete, tamper-evident records with correlation across tool invocations
- SIEM: controlled volume with clear severity mapping and reliable delivery
- Auth: supports common enterprise deployment patterns with least-privilege defaults

---

## Known Issues & Limitations

### Current Limitations
- **Large files:** Files >10MB may experience performance degradation
- **Obfuscated code:** Cannot analyze minified/obfuscated JavaScript
- **Macros:** C/C++ macro expansion not yet supported
- **Dynamic imports:** Runtime-only imports may not be detected

### Planned Fixes
- Q1 2026: Large file chunking strategy
- Q2 2026: Partial obfuscation handling
- Q3 2026: Macro expansion support
- Q4 2026: Dynamic import inference

---

## Success Metrics

### Performance Targets
- **Parse time:** <100ms for files <1000 LOC
- **Memory usage:** <50MB per 10,000 LOC analyzed
- **Accuracy:** >98% correct function/class extraction
- **Coverage:** Support 15+ languages by EOY 2026

### Adoption Metrics
- **Usage:** 1M+ API calls per month by Q4 2026
- **Satisfaction:** >4.5/5 average rating
- **Retention:** >85% monthly active users

---

## Dependencies

### Internal Dependencies
- `code_parsers/` - Language-specific parsers
- `ast_tools/analyzer.py` - Core AST analysis
- `cache/unified_cache.py` - Result caching
- `licensing/` - Tier enforcement

### External Dependencies
- `tree-sitter` - Polyglot parsing
- Language-specific parsers (varies by language)

---

## Breaking Changes

None planned. Committed to backward compatibility.

**API Stability Promise:** 
- Tool signature stable through 2026
- New fields may be added (non-breaking)
- Deprecated fields marked 6 months before removal

---

**Last Updated:** December 30, 2025  
**Next Review:** March 31, 2026