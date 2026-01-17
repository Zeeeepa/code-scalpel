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




============================================================================
PRO TIER - Advanced Analysis Features (P1-P3)
============================================================================




============================================================================
ENTERPRISE TIER - Enterprise Analysis Features (P2-P4)
============================================================================




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
