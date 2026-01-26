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
from .project_walker import (
    ALL_SUPPORTED_EXTENSIONS,
    CPP_EXTENSIONS,
    CSHARP_EXTENSIONS,
    DEFAULT_EXCLUDE_DIRS,
    GO_EXTENSIONS,
    JAVA_EXTENSIONS,
    JAVASCRIPT_EXTENSIONS,
    PYTHON_EXTENSIONS,
    RUBY_EXTENSIONS,
    RUST_EXTENSIONS,
    TYPESCRIPT_EXTENSIONS,
    DirectoryInfo,
    FileInfo,
    ProjectMap,
    ProjectWalker,
)
from .project_context import (
    CacheMetadata,
    DirectoryType,
    ProjectContext,
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
    # Project Awareness Engine (v1.2.0)
    "ProjectWalker",
    "ProjectContext",
    "FileInfo",
    "DirectoryInfo",
    "ProjectMap",
    "CacheMetadata",
    "DirectoryType",
    # Extensions and constants
    "DEFAULT_EXCLUDE_DIRS",
    "PYTHON_EXTENSIONS",
    "JAVASCRIPT_EXTENSIONS",
    "TYPESCRIPT_EXTENSIONS",
    "JAVA_EXTENSIONS",
    "CPP_EXTENSIONS",
    "CSHARP_EXTENSIONS",
    "RUBY_EXTENSIONS",
    "GO_EXTENSIONS",
    "RUST_EXTENSIONS",
    "ALL_SUPPORTED_EXTENSIONS",
]

__version__ = "1.0.0"
