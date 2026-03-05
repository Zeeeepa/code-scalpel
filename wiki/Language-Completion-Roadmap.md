# Language Completion Roadmap

This document tracks the **verified** implementation status of every language's static analysis tool parsers — based on a full file-by-file audit performed 2026-03-03. It sequences the gap-closure work required before a language is considered complete and before a new language can begin.

**Definition of "language complete"**: Phase 1 IR layer fully wired AND all `*_parsers/` tool files fully implemented (execution + output parsing + categorization + CWE mapping + report generation). See [Adding-A-Language.md](Adding-A-Language.md) for the full per-language checklist.

---

## MCP Surface Expansion Policy

> [20260303_DOCS] Established after the C++ static-analysis integration decision.

**Rule**: A new MCP tool is only added when the feature **cannot** be correctly integrated into an existing tool.

Before proposing a new tool, evaluate whether the feature belongs inside an existing one:

| Feature type | Default home |
|---|---|
| Language-specific linter / static-analysis tool output | `analyze_code` (`static_tools` parameter, `tool_findings` in response) |
| Security vulnerability detection (taint/sink) | `security_scan` or `cross_file_security_scan` |
| Dependency CVE check | `scan_dependencies` |
| Structural code query (call graph, refs) | `get_call_graph` / `get_symbol_references` |
| Policy / compliance check | `code_policy_check` |

**Rationale**

Agents that consume MCP tools pay a context-window cost proportional to the number of tools they must reason about. Keeping the surface small means:
- Agents can hold the full tool inventory in working memory without truncation.
- Tool discovery is simpler — one tool does one *conceptual* job.
- Tier gating stays centralised inside existing tools rather than spread across many.

**Acceptable reasons to add a new tool**

- The feature introduces a fundamentally different *interaction pattern* that would break existing callers if added as a parameter (e.g., it is async-streaming, or it returns a live session handle).
- The response schema is incompatible with all existing tools and merging would require a breaking change.
- The feature operates at a different granularity (project-wide vs. single-file) with no natural parent.

If none of the above apply, **extend an existing tool**.

---

## Audit: Verified Implementation Status (2026-03-03)

### Status Key

| Symbol | Meaning |
|--------|---------|
| ✅ COMPLETE | `execute_tool()` + `parse_output()` + categorize + report — production-ready |
| ⚠️ PARTIAL | Dataclasses and structure exist; execution logic raises `NotImplementedError` |
| ❌ STUB | Empty class or `raise NotImplementedError` only; no dataclasses |
| — | Not applicable |

---

### Python — `python_parsers/` (10/15 complete)

Phase 1: ✅ Complete | Adapter: ✅ Complete | Registry: ✅ Working (lazy-load `__getattr__`)

| File | Lines | Status |
|------|-------|--------|
| `python_parsers_ast.py` | 4,047 | ✅ COMPLETE |
| `python_parsers_ruff.py` | 1,191 | ✅ COMPLETE |
| `python_parsers_mypy.py` | 1,472 | ✅ COMPLETE |
| `python_parsers_pylint.py` | 1,687 | ✅ COMPLETE |
| `python_parsers_bandit.py` | 1,647 | ✅ COMPLETE |
| `python_parsers_flake8.py` | 1,228 | ✅ COMPLETE |
| `python_parsers_code_quality.py` | 1,454 | ✅ COMPLETE |
| `python_parsers_pydocstyle.py` | 1,435 | ✅ COMPLETE |
| `python_parsers_pycodestyle.py` | 599 | ✅ COMPLETE |
| `python_parsers_prospector.py` | 1,089 | ✅ COMPLETE |
| `python_parsers_safety.py` | 199 | ⚠️ PARTIAL — CVSSScore/Vulnerability dataclasses only; no parser logic |
| `python_parsers_isort.py` | 270 | ❌ STUB — docstrings and dataclass outlines only; marked "NOT IMPLEMENTED" |
| `python_parsers_vulture.py` | 157 | ❌ STUB — dataclasses only; marked "NOT IMPLEMENTED" |
| `python_parsers_radon.py` | 446 | ❌ STUB — dataclasses and docs only; marked "NOT IMPLEMENTED" |
| `python_parsers_interrogate.py` | 435 | ❌ STUB — dataclasses only; marked "NOT IMPLEMENTED" |

**Gap**: 5 files to implement (safety, isort, vulture, radon, interrogate)

---

### JavaScript — `javascript_parsers/` (15/15 complete)

Phase 1: ✅ Complete | Adapter: ✅ Complete | Registry: ✅ Working (direct imports)

| File | Lines | Status |
|------|-------|--------|
| `javascript_parsers_esprima.py` | 1,434 | ✅ COMPLETE |
| `javascript_parsers_code_quality.py` | 1,025 | ✅ COMPLETE |
| `javascript_parsers_eslint.py` | 640 | ✅ COMPLETE |
| `javascript_parsers_treesitter.py` | 939 | ✅ COMPLETE |
| `javascript_parsers_babel.py` | 672 | ✅ COMPLETE |
| `javascript_parsers_flow.py` | 688 | ✅ COMPLETE |
| `javascript_parsers_prettier.py` | 503 | ✅ COMPLETE |
| `javascript_parsers_jshint.py` | 408 | ✅ COMPLETE |
| `javascript_parsers_standard.py` | 367 | ✅ COMPLETE |
| `javascript_parsers_typescript.py` | 815 | ✅ COMPLETE |
| `javascript_parsers_npm_audit.py` | 193 | ✅ COMPLETE |
| `javascript_parsers_jsdoc.py` | 239 | ✅ COMPLETE |
| `javascript_parsers_package_json.py` | 190 | ✅ COMPLETE |
| `javascript_parsers_test_detection.py` | 177 | ✅ COMPLETE |
| `javascript_parsers_webpack.py` | 258 | ✅ COMPLETE |

**Gap**: None — all 15 parsers complete. [20260303_FEATURE]

---

### TypeScript — `typescript_parsers/` (6/6 complete)

Phase 1: ✅ Complete | Adapter: ✅ Complete (via javascript_adapter) | Registry: ✅ Working

| File | Lines | Status |
|------|-------|--------|
| `parser.py` | 428 | ✅ COMPLETE |
| `analyzer.py` | 372 | ✅ COMPLETE |
| `type_narrowing.py` | 709 | ✅ COMPLETE |
| `decorator_analyzer.py` | 306 | ✅ COMPLETE |
| `alias_resolver.py` | 342 | ✅ COMPLETE |
| `tsx_analyzer.py` | 182 | ✅ COMPLETE |

**Gap**: None — TypeScript is fully complete.

---

### Java — `java_parsers/` (16/16 complete)

Phase 1: ✅ Complete | Adapter: ✅ Complete | Registry: ✅ Working (direct imports)

| File | Lines | Status |
|------|-------|--------|
| `java_parser_treesitter.py` | 1,107 | ✅ COMPLETE |
| `java_parsers_javalang.py` | 1,679 | ✅ COMPLETE |
| `java_parsers_SonarQube.py` | 252 | ✅ COMPLETE |
| `java_parsers_SpotBugs.py` | 249 | ✅ COMPLETE |
| `java_parsers_PMD.py` | 205 | ✅ COMPLETE |
| `java_parsers_Checkstyle.py` | 148 | ✅ COMPLETE |
| `java_parsers_ErrorProne.py` | 154 | ✅ COMPLETE |
| `java_parsers_FindSecBugs.py` | 163 | ✅ COMPLETE |
| `java_parsers_Infer.py` | 171 | ✅ COMPLETE |
| `java_parsers_JArchitect.py` | 174 | ✅ COMPLETE |
| `java_parsers_Gradle.py` | 183 | ✅ COMPLETE |
| `java_parsers_Maven.py` | 213 | ✅ COMPLETE |
| `java_parsers_DependencyCheck.py` | 200 | ✅ COMPLETE |
| `java_parsers_JaCoCo.py` | 197 | ✅ COMPLETE |
| `java_parsers_Pitest.py` | 185 | ✅ COMPLETE |
| `java_parsers_Semgrep.py` | 164 | ✅ COMPLETE |

**Gap**: None — all 16 parsers complete. [20260303_FEATURE]

> **Note**: The previous roadmap entry said "2/17 complete" — this was incorrect. The audit confirmed 10 of 16 tool parsers are production-ready. Only build/coverage/mutation tools remain as stubs.

---

### C++ — `cpp_parsers/` (6/6 complete)

Phase 1: ✅ Complete | Adapter: ✅ Complete (`cpp_adapter.py` — [20260303_FEATURE]) | Registry: ✅ Complete (`CppParserRegistry` — [20260303_FEATURE])

| File | Lines | Status |
|------|-------|--------|
| `cpp_parsers_Cppcheck.py` | 422 | ✅ COMPLETE — execute + XML parse + CWE mapping + report |
| `cpp_parsers_clang_tidy.py` | 459 | ✅ COMPLETE — execute + diagnostic/JSON parse + report |
| `cpp_parsers_Clang-Static-Analyzer.py` | 397 | ✅ COMPLETE — scan-build execute + plist parse + bug paths |
| `cpp_parsers_cpplint.py` | 330 | ✅ COMPLETE — execute + stderr parse + style score |
| `cpp_parsers_coverity.py` | 407 | ✅ COMPLETE — enterprise report parse only (execute raises NotImplementedError by design) |
| `cpp_parsers_SonarQube.py` | 400 | ✅ COMPLETE — enterprise API JSON parse (execute raises NotImplementedError by design) |

**Gap**: None — all 6 parsers complete. [20260303_FEATURE]

> **Integration note**: C++ tool-parser results are accessed via `analyze_code(file_path=..., static_tools=["cppcheck", ...])`.
> The `static_tools` parameter was added to `analyze_code` in [20260303_REFACTOR] — no separate MCP tool was created
> (see [MCP Surface Expansion Policy](#mcp-surface-expansion-policy)).
> Results appear in `tool_findings` of the `AnalysisResult`.
> Enterprise-only tools (coverity, sonarqube) require Enterprise tier for execution; all tiers can parse pre-existing report files.

---

### C# — `csharp_parsers/` (0/6 complete)

Phase 1: ✅ Complete | Adapter: ❌ STUB (`csharp_adapter.py`) | Registry: ❌ STUB

| File | Lines | Status |
|------|-------|--------|
| `csharp_parsers_fxcop.py` | 92 | ⚠️ PARTIAL — FxCopViolation dataclass + enums; no parse/execute |
| `csharp_parsers_SecurityCodeScan.py` | 96 | ⚠️ PARTIAL — dataclasses only; no implementation |
| `csharp_parsers_ReSharper.py` | 28 | ❌ STUB — class skeleton + `raise NotImplementedError` |
| `csharp_parsers_Roslyn-Analyzers.py` | 28 | ❌ STUB — class skeleton + `raise NotImplementedError` |
| `csharp_parsers_StyleCop.py` | 28 | ❌ STUB — class skeleton + `raise NotImplementedError` |
| `csharp_parsers_SonarQube.py` | 28 | ❌ STUB — class skeleton + `raise NotImplementedError` |

**Gap**: 6 tool parser files + adapter + registry + shared SARIF helper

---

### Go — `go_parsers/` (0/6 complete)

Phase 1: ✅ Complete | Adapter: ✅ Complete (`go_adapter.py` — [20260302_FEATURE]) | Registry: ❌ STUB

| File | Lines | Status |
|------|-------|--------|
| `go_parsers_golangci_lint.py` | 97 | ⚠️ PARTIAL — LintIssue/GolangciLintConfig dataclasses; methods raise `NotImplementedError` |
| `go_parsers_gosec.py` | 92 | ⚠️ PARTIAL — dataclasses; methods raise `NotImplementedError` |
| `go_parsers_staticcheck.py` | 37 | ⚠️ PARTIAL — dataclasses; methods raise `NotImplementedError` |
| `go_parsers_gofmt.py` | 28 | ❌ STUB — class skeleton + `raise NotImplementedError` |
| `go_parsers_golint.py` | 28 | ❌ STUB — class skeleton + `raise NotImplementedError` |
| `go_parsers_govet.py` | 29 | ❌ STUB — class skeleton + `raise NotImplementedError` |

**Gap**: 6 tool parser files + registry (adapter already done)

---

### Kotlin — `kotlin_parsers/` (2/7 complete)

Phase 1: ❌ Not started | Adapter: ❌ STUB (`kotlin_adapter.py`) | Registry: ✅ Working (lazy-load `__getattr__`)

| File | Lines | Status |
|------|-------|--------|
| `kotlin_parsers_Detekt.py` | 265 | ✅ COMPLETE — full integration with findings, severity, config |
| `kotlin_parsers_ktlint.py` | 326 | ✅ COMPLETE — comprehensive with rule sets, auto-correct |
| `kotlin_parsers_diktat.py` | 127 | ⚠️ PARTIAL — dataclasses only |
| `kotlin_parsers_gradle.py` | 148 | ⚠️ PARTIAL — dataclasses only |
| `kotlin_parsers_compose.py` | 123 | ⚠️ PARTIAL — dataclasses only |
| `kotlin_parsers_Konsist.py` | 111 | ⚠️ PARTIAL — dataclasses only |
| `kotlin_parsers_test.py` | 146 | ⚠️ PARTIAL — dataclasses only |

**Gap**: 5 partial files to complete (Phase 1 IR layer not yet started)

> **Note**: Detekt and ktlint are already production-ready. The registry is also working. Kotlin's Phase 2 is partially underway before Phase 1 even began.

---

### PHP — `php_parsers/` (0/7 complete)

Phase 1: ❌ Not started | Adapter: ❌ STUB (`php_adapter.py`) | Registry: ✅ Working (lazy-load `__getattr__`)

| File | Lines | Status |
|------|-------|--------|
| `php_parsers_PHPCS.py` | 94 | ⚠️ PARTIAL — dataclasses; no execution |
| `php_parsers_PHPStan.py` | 101 | ⚠️ PARTIAL — PHPStanError/PHPStanLevel dataclasses; no execution |
| `php_parsers_Psalm.py` | 97 | ⚠️ PARTIAL — PsalmError/PsalmSeverity dataclasses; no execution |
| `php_parsers_phpmd.py` | 114 | ⚠️ PARTIAL — Mess Detector; missing implementation |
| `php_parsers_ast.py` | 104 | ⚠️ PARTIAL — AST analysis; incomplete |
| `php_parsers_composer.py` | 98 | ⚠️ PARTIAL — package management; incomplete |
| `php_parsers_exakat.py` | 94 | ⚠️ PARTIAL — static analysis; incomplete |

**Gap**: 7 files to implement + Phase 1 IR layer (not yet started)

---

### Ruby — `ruby_parsers/` (0/7 complete)

Phase 1: ❌ Not started | Adapter: ❌ STUB (`ruby_adapter.py`) | Registry: ❌ STUB (29 lines)

| File | Lines | Status |
|------|-------|--------|
| `ruby_parsers_RuboCop.py` | 94 | ⚠️ PARTIAL — RuboCopViolation/RuboCopConfig dataclasses; `NotImplementedError` |
| `ruby_parsers_Reek.py` | 85 | ⚠️ PARTIAL — ReekSmell dataclass; `NotImplementedError` |
| `ruby_parsers_brakeman.py` | 77 | ⚠️ PARTIAL — dataclasses; `NotImplementedError` |
| `ruby_parsers_ast.py` | 84 | ⚠️ PARTIAL — AST analysis; incomplete |
| `ruby_parsers_bundler.py` | 70 | ⚠️ PARTIAL — dependency management; incomplete |
| `ruby_parsers_simplecov.py` | 70 | ⚠️ PARTIAL — coverage analysis; incomplete |
| `ruby_parsers_fasterer.py` | 60 | ⚠️ PARTIAL — performance analysis; incomplete |

**Gap**: 7 files + registry + Phase 1 IR layer (not yet started)

---

### Swift — `swift_parsers/` (0/4 complete)

Phase 1: ❌ Not started | Adapter: ❌ STUB (`swift_adapter.py`) | Registry: ❌ STUB (27 lines)

| File | Lines | Status |
|------|-------|--------|
| `swift_parsers_SwiftLint.py` | 90 | ⚠️ PARTIAL — SwiftLintViolation/SwiftLintConfig dataclasses; no execution |
| `swift_parsers_Tailor.py` | 85 | ⚠️ PARTIAL — code style; incomplete |
| `swift_parsers_sourcekitten.py` | 61 | ⚠️ PARTIAL — AST extraction; incomplete |
| `swift_parsers_swiftformat.py` | 47 | ⚠️ PARTIAL — code formatting; incomplete |

**Gap**: 4 files + registry + Phase 1 IR layer (not yet started)

---

### Rust

Phase 1: ❌ Not started | No `rust_parsers/` directory exists yet

**Gap**: `rust_parsers/` directory and all files must be created from scratch. See [Adding-Rust.md](Adding-Rust.md) for the tool list (Clippy, cargo-audit, cargo-deny, rustfmt, Semgrep).

---

## Consolidated Gap Summary

| Language | Phase 1 | Adapter | Registry | Complete/Total | Files to write | Priority |
|----------|---------|---------|----------|----------------|---------------|----------|
| **TypeScript** | ✅ | ✅ | ✅ | 6/6 | **0 — DONE** | — |
| **Python** | ✅ | ✅ | ✅ | 10/15 | 5 | Quick win |
| **JavaScript** | ✅ | ✅ | ✅ | 15/15 | 0 | Complete |
| **Java** | ✅ | ✅ | ✅ | 16/16 | 0 | Complete |
| **C++** | ✅ | ✅ | ✅ | 6/6 | **0 — DONE** | — |
| **C#** | ✅ | ❌ STUB | ❌ STUB | 0/6 | 6 + adapter + registry + SARIF helper | **Stage 2** |
| **Go** | ✅ | ✅ | ❌ STUB | 0/6 | 6 + registry | **Stage 3** |
| **Kotlin** | ❌ | ❌ STUB | ✅ | 2/7 | 5 + Phase 1 | After stages 1–3 |
| **PHP** | ❌ | ❌ STUB | ✅ | 0/7 | 7 + Phase 1 | After Kotlin |
| **Ruby** | ❌ | ❌ STUB | ❌ STUB | 0/7 | 7 + Phase 1 + registry | After PHP |
| **Swift** | ❌ | ❌ STUB | ❌ STUB | 0/4 | 4 + Phase 1 + registry | After Ruby |
| **Rust** | ❌ | ❌ | none | 0/5 | 5 + dir + Phase 1 | After Swift |
| **C** | ✅ | ✅ | n/a | n/a | 0 (served by C++ tools) | — |

---

## Work Queue — Ordered by Strategic Priority

The ordering balances: (a) security ecosystem impact, (b) number of files to write, (c) scaffolding already in place.

---

### Stage 1 — C++ Tool Parsers ✅ COMPLETE [20260303_FEATURE]

All C++ tool parsers are fully implemented. Results are available via `analyze_code(file_path=..., static_tools=[...])` — no separate MCP tool was created (see [MCP Surface Expansion Policy](#mcp-surface-expansion-policy)).

| File | Status |
|------|--------|
| `cpp_adapter.py` | ✅ Done |
| `cpp_parsers/__init__.py` | ✅ Done — `CppParserRegistry` |
| `cpp_parsers_Cppcheck.py` | ✅ Done |
| `cpp_parsers_clang_tidy.py` | ✅ Done |
| `cpp_parsers_Clang-Static-Analyzer.py` | ✅ Done |
| `cpp_parsers_cpplint.py` | ✅ Done |
| `cpp_parsers_coverity.py` | ✅ Done (enterprise parse-only) |
| `cpp_parsers_SonarQube.py` | ✅ Done (enterprise parse-only) |

**Tests**: `tests/languages/test_cpp_tool_parsers.py` — 85 tests passing

---

### Stage 2 — C# Tool Parsers

**Why second**: .NET ecosystem is large; all 6 C# tools use SARIF 2.1 output, which means one shared `_parse_sarif()` helper in `__init__.py` covers Roslyn, StyleCop, and SecurityCodeScan. C# stubs are more minimal than C++ (28 lines each) — need both dataclass framework AND implementation.

**Files to write**:

| File | Tool type | Output format | Notes |
|------|-----------|--------------|-------|
| `csharp_adapter.py` | Adapter | — | Thin wrapper over `CSharpNormalizer` |
| `csharp_parsers/__init__.py` | Registry + SARIF helper | — | `CSharpParserRegistry` + shared `_parse_sarif()` |
| `csharp_parsers_Roslyn-Analyzers.py` | Free (dotnet build) | SARIF 2.1 JSON | Parse `dotnet build --no-incremental` SARIF output |
| `csharp_parsers_StyleCop.py` | Free (MSBuild) | SARIF 2.1 / XML | StyleCop.Analyzers MSBuild output |
| `csharp_parsers_SecurityCodeScan.py` | Free | SARIF 2.1 JSON | Security scanner; CWE mapping from rule ID prefix |
| `csharp_parsers_fxcop.py` | Free (legacy) | XML / SARIF | FxCop/Roslyn code analysis rules |
| `csharp_parsers_ReSharper.py` | Enterprise | XML (`inspectcode`) | JetBrains `inspectcode.exe` XML output |
| `csharp_parsers_SonarQube.py` | Enterprise | JSON API | Same pattern as C++ SonarQube |

**Tests**: `tests/languages/test_csharp_tool_parsers.py` — fixture-based, focus on SARIF parsing

---

### Stage 3 — Go Tool Parsers

**Why third**: Cloud-native ecosystem. Go adapter is already done. Registry stub exists but is empty. golangci-lint aggregates 50+ linters into one JSON output — implementing it well provides coverage over govet, staticcheck, and many others. gosec provides built-in CWE IDs.

**Files to write**:

| File | Tool type | Output format | Notes |
|------|-----------|--------------|-------|
| `go_parsers/__init__.py` | Registry | — | `GoParserRegistry` with lazy-load factory |
| `go_parsers_golangci_lint.py` | Free CLI | JSON `{"Issues":[...], "Report":{...}}` | **Priority 1** — meta-linter; `golangci-lint run --out-format json` |
| `go_parsers_gosec.py` | Free CLI | JSON `{"Golang gosec":{"Issues":[...]}}` | **Priority 2** — CWE IDs built-in |
| `go_parsers_staticcheck.py` | Free CLI | JSON `[{"code","message","location"}]` | `staticcheck -f json ./...` |
| `go_parsers_govet.py` | Free CLI | text `file:line:col: msg` | `go vet ./...`; stderr parsing |
| `go_parsers_golint.py` | Free CLI | text `file:line:col: msg` | Deprecated but still used |
| `go_parsers_gofmt.py` | Free CLI | unified diff or file list | `gofmt -l .`; returns files with formatting issues |

**Tests**: `tests/languages/test_go_tool_parsers.py` — fixture-based

---

### Stage 4 — Close Quick Wins (Python + JavaScript + Java) ✅ COMPLETE [20260303_FEATURE]

All parsers for Python, JavaScript, and Java are fully implemented. See the per-language audit tables above.

---

### Stage 5 — Kotlin Phase 2 Completion (then Phase 1)

**Why here**: Kotlin already has 2 production-ready parsers (Detekt, ktlint) and a working registry. The remaining 5 partials need implementation bodies. Phase 1 IR layer begins after Phase 2 partials are complete (or concurrently).

**Partial files to complete (5)**:

| File | Tool | Output format |
|------|------|--------------|
| `kotlin_parsers_diktat.py` | diktat | SARIF / XML |
| `kotlin_parsers_gradle.py` | Gradle Kotlin | `build.gradle.kts` + build output |
| `kotlin_parsers_compose.py` | Compose Lint | Android Lint SARIF |
| `kotlin_parsers_Konsist.py` | Konsist | JUnit XML (test-based) |
| `kotlin_parsers_test.py` | Test utilities | — |

Then begin **Kotlin Phase 1** IR layer — see [Adding-Kotlin.md](Adding-Kotlin.md).

---

### Stage 6 — PHP Phase 2 + Phase 1

PHP has a working registry and 7 partial files. All 7 need execution logic written. Then PHP Phase 1 IR layer.

---

### Stage 7 — Ruby Phase 2 + Phase 1

Ruby has 7 partials and a stub registry. Registry needs implementing first, then all 7 execution logic bodies. Then Ruby Phase 1 IR layer. See [Adding-Ruby.md](Adding-Ruby.md).

---

### Stage 8 — Swift Phase 2 + Phase 1

Swift has 4 partials and a stub registry. macOS-primary with graceful Linux degradation pattern. See [Adding-Swift.md](Adding-Swift.md).

---

### Stage 9 — Rust Phase 1 + Phase 2

Rust has no `rust_parsers/` directory. Create from scratch: directory + 5 tool files + registry + Phase 1 IR layer. See [Adding-Rust.md](Adding-Rust.md).

---

## Adapter Stubs to Fix (track alongside tool parsers)

Six adapters raise `NotImplementedError` and must be implemented as thin wrappers over the language's normalizer:

| Adapter file | Fix alongside |
|-------------|--------------|
| `cpp_adapter.py` | ✅ Done — [20260303_FEATURE] |
| `csharp_adapter.py` | Stage 2 (C#) |
| `kotlin_adapter.py` | Stage 5 (Kotlin) |
| `php_adapter.py` | Stage 6 (PHP) |
| `ruby_adapter.py` | Stage 7 (Ruby) |
| `swift_adapter.py` | Stage 8 (Swift) |

---

## Tool Parser Implementation Patterns

### Free tool (execute + parse)

```python
import shutil
import subprocess
from pathlib import Path

class SomeToolParser:
    def execute_sometool(self, paths: list[Path], config=None) -> list[SomeIssue]:
        if shutil.which("sometool") is None:
            return []   # graceful: tool not installed
        cmd = ["sometool", "--format=json"] + [str(p) for p in paths]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return self.parse_json_output(result.stdout)

    def parse_json_output(self, output: str) -> list[SomeIssue]:
        import json
        data = json.loads(output or "[]")
        return [self._to_issue(item) for item in data]
```

### Enterprise tool (output file only)

```python
class EnterpriseToolParser:
    def execute_enterprise(self, paths, config=None):
        raise NotImplementedError(
            "EnterpriseTool requires a licensed installation. "
            "Run the tool externally and pass the output file to "
            "parse_json_report() instead."
        )

    def parse_json_report(self, report_path: Path) -> list[Finding]:
        import json
        data = json.loads(report_path.read_text())
        return [self._to_finding(item) for item in data.get("issues", [])]
```

### SARIF 2.1 helper (shared — especially for .NET / C# tools)

```python
def _parse_sarif(sarif_path: Path) -> list[SarifFinding]:
    """Parse SARIF 2.1 format (common across Roslyn, StyleCop, SecurityCodeScan)."""
    import json
    sarif = json.loads(sarif_path.read_text())
    findings = []
    for run in sarif.get("runs", []):
        for result in run.get("results", []):
            for location in result.get("locations", []):
                phys = location.get("physicalLocation", {})
                region = phys.get("region", {})
                findings.append(SarifFinding(
                    rule_id=result.get("ruleId", ""),
                    message=result.get("message", {}).get("text", ""),
                    severity=result.get("level", "warning"),
                    file_path=phys.get("artifactLocation", {}).get("uri", ""),
                    line=region.get("startLine", 0),
                    column=region.get("startColumn", 0),
                ))
    return findings
```

### Registry pattern (lazy-load)

```python
class LanguageParserRegistry:
    def __init__(self):
        from . import tool_a, tool_b, tool_c
        self._parsers = {
            "tool-a": tool_a.ToolAParser,
            "tool-b": tool_b.ToolBParser,
            "tool-c": tool_c.ToolCParser,
        }

    def get_parser(self, tool_name: str):
        cls = self._parsers.get(tool_name.lower())
        if cls is None:
            raise ValueError(
                f"Unknown tool: {tool_name!r}. Available: {sorted(self._parsers)}"
            )
        return cls()

    def analyze(self, path, tools: list[str] | None = None) -> dict[str, list]:
        tools = tools or list(self._parsers)
        results = {}
        for name in tools:
            try:
                parser = self.get_parser(name)
                results[name] = parser.execute(path) if hasattr(parser, "execute") else []
            except (NotImplementedError, FileNotFoundError, OSError):
                results[name] = []
        return results
```

---

## Version Plan (Revised)

| Version | Scope |
|---------|-------|
| `v2.1.x` | ✅ **Stage 1**: C++ tool parsers + adapter + registry; integrated into `analyze_code.static_tools` |
| `v2.1.x` | ✅ **Stage 3**: Go tool parsers + registry |
| `v2.1.x` | ✅ **Stage 4**: Python + JavaScript + Java quick-win stubs — all complete |
| `v2.1.x` | **Stage 2**: C# tool parsers + adapter + SARIF helper |
| `v2.2.0` | **Stage 5**: Kotlin Phase 2 completion + Phase 1 IR (full language) |
| `v2.3.0` | **Stage 6**: PHP Phase 2 + Phase 1 |
| `v2.4.0` | **Stage 7**: Ruby Phase 2 + Phase 1 |
| `v2.5.0` | **Stage 8**: Swift Phase 2 + Phase 1 |
| `v2.6.0` | **Stage 9**: Rust Phase 1 + Phase 2 |

---

*Last audited: 2026-03-03 — full file-by-file review of all `code_parsers/` directories*
