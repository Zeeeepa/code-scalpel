"""
Analysis Module - Code analysis, metrics, and project crawling tools.

[20251224_REFACTOR] Created as part of Project Reorganization Issue #3.
Consolidated analysis tools from top-level modules.

This module provides:
- CodeAnalyzer: Unified AST analysis, PDG construction, dead code detection
- ProjectCrawler: Whole-project analysis with metrics and reports
- CodeAnalysisToolkit: Core PDG and AST utilities

Migration Guide:
    # Old imports (deprecated in v3.3.0):
    from code_scalpel.code_analyzer import CodeAnalyzer
    from code_scalpel.project_crawler import ProjectCrawler
    from code_scalpel.core import CodeAnalysisToolkit

    # New imports (recommended):
    from code_scalpel.analysis import CodeAnalyzer, ProjectCrawler, CodeAnalysisToolkit
    # Or:
    from code_scalpel.analysis.code_analyzer import CodeAnalyzer
    from code_scalpel.analysis.project_crawler import ProjectCrawler
    from code_scalpel.analysis.core import CodeAnalysisToolkit

TODO ITEMS: analysis/__init__.py
============================================================================
COMMUNITY TIER - Core Analysis Features (P0-P2)
============================================================================

# TODO [COMMUNITY][P0_CRITICAL]: Complete module integration
# TODO [COMMUNITY]: Ensure CodeAnalyzer and ProjectCrawler work seamlessly together
# TODO [COMMUNITY]: Unified configuration for analysis depth/scope
# TODO [COMMUNITY]: Test count: 20 tests (integration)

# TODO [COMMUNITY][P1_HIGH]: Add analysis orchestration
# TODO [COMMUNITY]: analyze_project() convenience function
# TODO [COMMUNITY]: Combined metrics from all analyzers
# TODO [COMMUNITY]: Unified report generation
# TODO [COMMUNITY]: Test count: 25 tests (orchestration)

# TODO [COMMUNITY][P2_MEDIUM]: Add caching layer
# TODO [COMMUNITY]: Cache analysis results
# TODO [COMMUNITY]: Incremental analysis support
# TODO [COMMUNITY]: Cache invalidation on file change
# TODO [COMMUNITY]: Test count: 20 tests (caching)

============================================================================
PRO TIER - Advanced Analysis Features (P1-P3)
============================================================================

# TODO [PRO][P1_HIGH]: Multi-language analysis
# TODO [PRO]: JavaScript/TypeScript analysis
# TODO [PRO]: Java analysis
# TODO [PRO]: Unified metrics across languages
# TODO [PRO]: Test count: 40 tests (multi-lang)

# TODO [PRO][P2_MEDIUM]: Advanced metrics
# TODO [PRO]: Cognitive complexity
# TODO [PRO]: Halstead metrics
# TODO [PRO]: Maintainability index
# TODO [PRO]: Test count: 30 tests (metrics)

# TODO [PRO][P3_LOW]: CI/CD integration
# TODO [PRO]: JUnit XML reports
# TODO [PRO]: Threshold-based exit codes
# TODO [PRO]: GitHub Actions integration
# TODO [PRO]: Test count: 15 tests (CI/CD)

============================================================================
ENTERPRISE TIER - Enterprise Analysis Features (P2-P4)
============================================================================

# TODO [ENTERPRISE][P2_MEDIUM]: Security analysis
# TODO [ENTERPRISE]: SAST rule engine
# TODO [ENTERPRISE]: Vulnerability scanning
# TODO [ENTERPRISE]: SARIF output
# TODO [ENTERPRISE]: Test count: 35 tests (security)

# TODO [ENTERPRISE][P3_LOW]: Advanced visualization
# TODO [ENTERPRISE]: Interactive HTML reports
# TODO [ENTERPRISE]: D3.js graphs
# TODO [ENTERPRISE]: Trend analysis
# TODO [ENTERPRISE]: Test count: 20 tests (visualization)

# TODO [ENTERPRISE][P4_LOW]: Enterprise features
# TODO [ENTERPRISE]: Parallel analysis
# TODO [ENTERPRISE]: Distributed workers
# TODO [ENTERPRISE]: Neo4j export
# TODO [ENTERPRISE]: Test count: 15 tests (enterprise)

============================================================================
TOTAL ESTIMATED TESTS: 220 tests
============================================================================
"""

# [20251224_REFACTOR] Import from submodules
from .code_analyzer import (
    AnalysisLanguage,
    AnalysisLevel,
    AnalysisMetrics,
    AnalysisResult,
    CodeAnalyzer,
    DeadCodeItem,
    RefactorSuggestion,
)
from .core import CodeAnalysisToolkit
from .project_crawler import (
    ClassInfo,
    CrawlResult,
    FileAnalysisResult,
    FunctionInfo,
    ProjectCrawler,
    crawl_project,
)

__all__ = [
    # Code Analyzer
    "CodeAnalyzer",
    "AnalysisResult",
    "AnalysisMetrics",
    "AnalysisLevel",
    "AnalysisLanguage",
    "DeadCodeItem",
    "RefactorSuggestion",
    # Project Crawler
    "ProjectCrawler",
    "CrawlResult",
    "FileAnalysisResult",
    "FunctionInfo",
    "ClassInfo",
    "crawl_project",
    # Core
    "CodeAnalysisToolkit",
]

__version__ = "1.0.0"
