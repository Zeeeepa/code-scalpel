#!/usr/bin/env python3
# [20260102_REFACTOR] Lazy exports via __getattr__; suppress unused-import lint for optional parsers.
# ruff: noqa: F401
"""
Kotlin Parser Module - Comprehensive Kotlin code analysis tooling.

This module provides parsers and analyzers for Kotlin code, integrating with
popular Kotlin tooling including Detekt, ktlint, and the Kotlin compiler.

Planned Features:
    Static Analysis:
        - Detekt integration for code smell detection
        - ktlint integration for style enforcement
        - Kotlin compiler diagnostics parsing

    Code Quality:
        - Cyclomatic complexity calculation
        - Cognitive complexity metrics
        - Code smell detection (long methods, large classes, etc.)
        - Duplicate code detection

    Type Analysis:
        - Type inference tracking
        - Null safety analysis
        - Smart cast detection
        - Generic type analysis

    Coroutine Analysis:
        - Coroutine scope detection
        - Suspend function tracking
        - Flow/Channel usage analysis
        - Structured concurrency validation

    DSL Detection:
        - Builder pattern detection
        - Type-safe builder analysis
        - Custom DSL identification

TODO: HIGH PRIORITY - Core Parsers
===================================
TODO: Implement DetektParser for code smell detection
TODO: Implement KtlintParser for style violation detection
TODO: Implement KotlinCompilerParser for compiler diagnostics
TODO: Add SARIF output parsing for IDE integration
TODO: Add baseline file support for legacy code

TODO: HIGH PRIORITY - AST Analysis
===================================
TODO: Implement tree-sitter Kotlin parser integration
TODO: Add PSI (Program Structure Interface) analysis via ANTLR
TODO: Implement symbol extraction (classes, functions, properties)
TODO: Add import/export analysis
TODO: Implement call graph generation

TODO: MEDIUM PRIORITY - Kotlin-Specific Features
=================================================
TODO: Add null safety analysis (nullable types, !! usage, safe calls)
TODO: Add coroutine detection (suspend, launch, async, flow)
TODO: Add extension function tracking
TODO: Add data class analysis
TODO: Add sealed class/interface hierarchy analysis
TODO: Add companion object detection
TODO: Add operator overloading detection
TODO: Add inline/reified function analysis
TODO: Add delegation pattern detection (by keyword)

TODO: MEDIUM PRIORITY - Multiplatform Support
==============================================
TODO: Add expect/actual declaration matching
TODO: Add platform-specific code detection
TODO: Add source set analysis
TODO: Add Kotlin/JS specific analysis
TODO: Add Kotlin/Native specific analysis

TODO: MEDIUM PRIORITY - Framework Detection
============================================
TODO: Add Android-specific detection (Activity, Fragment, ViewModel)
TODO: Add Jetpack Compose component detection
TODO: Add Ktor route detection
TODO: Add Spring Boot Kotlin detection
TODO: Add kotlinx.serialization usage

# [20260102_REFACTOR] Lazy exports via __getattr__; imported parsers appear unused locally.
# ruff: noqa: F401

TODO: LOW PRIORITY - Advanced Analysis
=======================================
TODO: Add contract analysis (Kotlin contracts)
TODO: Add context receivers detection (experimental)
TODO: Add value class analysis
TODO: Add builder inference analysis
TODO: Add SAM conversion tracking

TODO: LOW PRIORITY - Tooling Integration
=========================================
TODO: Add Gradle Kotlin DSL analysis
TODO: Add build.gradle.kts parsing
TODO: Add KSP (Kotlin Symbol Processing) integration
TODO: Add kapt annotation processor detection

TODO: HIGH PRIORITY - Module Registry & Aggregation
====================================================
[20251221_TODO] Implement KotlinParserRegistry with unified interface
[20251221_TODO] Add parser factory pattern for lazy initialization
[20251221_TODO] Create aggregation metrics across multiple parsers
[20251221_TODO] Add configuration management for all Kotlin parsers

TODO: MEDIUM PRIORITY - Integration & Performance
==================================================
[20251221_TODO] Implement async/concurrent parser execution
[20251221_TODO] Add caching layer for repeated analyses
[20251221_TODO] Implement incremental analysis support
[20251221_TODO] Add result aggregation and deduplication
[20251221_TODO] Create unified JSON/SARIF output format
[20251221_TODO] Add progress reporting for long-running analyses
[20251221_TODO] Implement parser health checks and diagnostics

TODO: MEDIUM PRIORITY - New Tool Integrations
==============================================
[20251221_TODO] Add Konsist library integration (architecture rules)
[20251221_TODO] Add diktat integration (alternative linter)
[20251221_TODO] Add compose linter integration
[20251221_TODO] Add JUnit test analyzer for Kotlin tests
[20251221_TODO] Add benchmarking tool support

TODO: MEDIUM PRIORITY - Output & Reporting
============================================================
[20251221_TODO] Generate HTML report templates
[20251221_TODO] Implement trend analysis (historical metrics)
[20251221_TODO] Add severity-based filtering and sorting
[20251221_TODO] Create detailed violation categories
[20251221_TODO] Implement diff/comparison reports

TODO: LOW PRIORITY - Advanced Features
=======================================
[20251221_TODO] Add IDE plugin integration stubs
[20251221_TODO] Create Maven Central dependency scanning
[20251221_TODO] Add Gradle dependency vulnerability checking
[20251221_TODO] Implement license compliance checking
[20251221_TODO] Add automated metric export (CSV, JSON)
"""

from typing import TYPE_CHECKING

# Lazy imports to avoid circular dependencies
if TYPE_CHECKING:
    from .kotlin_parsers_Detekt import (
        DetektConfig,
        DetektFinding,
        DetektParser,
        DetektReport,
        DetektRuleSet,
        DetektSeverity,
    )
    from .kotlin_parsers_ktlint import (
        KtlintConfig,
        KtlintParser,
        KtlintReport,
        KtlintRuleSet,
        KtlintSeverity,
        KtlintViolation,
    )

__all__ = [
    # Detekt
    "DetektParser",
    "DetektFinding",
    "DetektSeverity",
    "DetektRuleSet",
    "DetektConfig",
    "DetektReport",
    # ktlint
    "KtlintParser",
    "KtlintViolation",
    "KtlintSeverity",
    "KtlintRuleSet",
    "KtlintConfig",
    "KtlintReport",
]


def __getattr__(name: str):
    """Lazy load parser classes on first access."""
    if name in (
        "DetektParser",
        "DetektFinding",
        "DetektSeverity",
        "DetektRuleSet",
        "DetektConfig",
        "DetektReport",
    ):
        from .kotlin_parsers_Detekt import DetektConfig  # noqa: F401
        from .kotlin_parsers_Detekt import (
            DetektFinding,
            DetektParser,
            DetektReport,
            DetektRuleSet,
            DetektSeverity,
        )

        return locals()[name]

    if name in (
        "KtlintParser",
        "KtlintViolation",
        "KtlintSeverity",
        "KtlintRuleSet",
        "KtlintConfig",
        "KtlintReport",
    ):
        from .kotlin_parsers_ktlint import KtlintConfig  # noqa: F401
        from .kotlin_parsers_ktlint import (
            KtlintParser,
            KtlintReport,
            KtlintRuleSet,
            KtlintSeverity,
            KtlintViolation,
        )

        return locals()[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
