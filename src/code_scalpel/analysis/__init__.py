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

# [P0_CRITICAL] Complete module integration:
#     - Ensure CodeAnalyzer and ProjectCrawler work seamlessly together
#     - Unified configuration for analysis depth/scope
#     - Test count: 20 tests (integration)

# [P1_HIGH] Add analysis orchestration:
#     - analyze_project() convenience function
#     - Combined metrics from all analyzers
#     - Unified report generation
#     - Test count: 25 tests (orchestration)

# [P2_MEDIUM] Add caching layer:
#     - Cache analysis results
#     - Incremental analysis support
#     - Cache invalidation on file change
#     - Test count: 20 tests (caching)

============================================================================
PRO TIER - Advanced Analysis Features (P1-P3)
============================================================================

# [P1_HIGH] Multi-language analysis:
#     - JavaScript/TypeScript analysis
#     - Java analysis
#     - Unified metrics across languages
#     - Test count: 40 tests (multi-lang)

# [P2_MEDIUM] Advanced metrics:
#     - Cognitive complexity
#     - Halstead metrics
#     - Maintainability index
#     - Test count: 30 tests (metrics)

# [P3_LOW] CI/CD integration:
#     - JUnit XML reports
#     - Threshold-based exit codes
#     - GitHub Actions integration
#     - Test count: 15 tests (CI/CD)

============================================================================
ENTERPRISE TIER - Enterprise Analysis Features (P2-P4)
============================================================================

# [P2_MEDIUM] Security analysis:
#     - SAST rule engine
#     - Vulnerability scanning
#     - SARIF output
#     - Test count: 35 tests (security)

# [P3_LOW] Advanced visualization:
#     - Interactive HTML reports
#     - D3.js graphs
#     - Trend analysis
#     - Test count: 20 tests (visualization)

# [P4_LOW] Enterprise features:
#     - Parallel analysis
#     - Distributed workers
#     - Neo4j export
#     - Test count: 15 tests (enterprise)

============================================================================
TOTAL ESTIMATED TESTS: 220 tests
============================================================================
"""

# [20251224_REFACTOR] Import from submodules
from .code_analyzer import (AnalysisLanguage, AnalysisLevel, AnalysisMetrics,
                            AnalysisResult, CodeAnalyzer, DeadCodeItem,
                            RefactorSuggestion)
from .core import CodeAnalysisToolkit
from .project_crawler import (ClassInfo, CrawlResult, FileAnalysisResult,
                              FunctionInfo, ProjectCrawler, crawl_project)

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
