"""
Code Scalpel - AI Agent toolkit for code analysis using ASTs, PDGs, and Symbolic Execution.

Code Scalpel provides precision tools for AI-driven code analysis and transformation,
enabling AI agents to perform deep analysis and surgical modifications of code.

Quick Start:
    >>> from code_scalpel import CodeAnalyzer
    >>> analyzer = CodeAnalyzer()
    >>> result = analyzer.analyze("def hello(): return 42")
    >>> print(result.metrics.num_functions)
    1

For MCP server:
    >>> from code_scalpel import run_server
    >>> run_server(port=8080)

For AI agent integrations:
    >>> from code_scalpel.integrations import AutogenScalpel, CrewAIScalpel
"""

# [20251223_BUGFIX] v3.2.4 - CI contract + regression runner reliability
__version__ = "3.2.6"
__author__ = "Tim Escolopio"
__email__ = "3dtsus@gmail.com"

# Core analysis
# AST tools
from .ast_tools import (
    ASTAnalyzer,
    ASTBuilder,
    ClassMetrics,
    FunctionMetrics,
    build_ast,
    build_ast_from_file,
)
from .code_analyzer import (
    AnalysisLevel,
    AnalysisMetrics,
    AnalysisResult,
    CodeAnalyzer,
    DeadCodeItem,
    RefactorSuggestion,
    analyze_code,
)

# REST API Server (legacy, renamed from mcp_server)
from .integrations.rest_api_server import (
    MCPServerConfig,
    create_app,
    run_server,
)

# PDG tools
from .pdg_tools import (
    PDGAnalyzer,
    PDGBuilder,
    build_pdg,
)

# Project Crawler
from .project_crawler import (
    ProjectCrawler,
    CrawlResult,
    FileAnalysisResult,
    crawl_project,
)

# Surgical Extractor (Token-efficient extraction)
from .surgical_extractor import (
    SurgicalExtractor,
    ExtractionResult,
    ContextualExtraction,
    CrossFileSymbol,
    CrossFileResolution,
    extract_function,
    extract_class,
    extract_method,
    extract_with_context,
)

# Unified Extractor (Multi-language extraction) - v3.1.0
# [20251221_FEATURE] v3.1.0 - Unified interface for all languages
from .unified_extractor import (
    UnifiedExtractor,
    UnifiedExtractionResult,
    Language,
    detect_language,
    extract_from_file,
    extract_from_code,
)

# Surgical Patcher (Safe code modification)
from .surgical_patcher import (
    SurgicalPatcher,
    PatchResult,
    update_function_in_file,
    update_class_in_file,
    update_method_in_file,
)

# Autonomy (Error-to-Diff Engine) - v3.0.0
# [20251217_FEATURE] v3.0.0 Autonomy - Error-to-Diff Engine
from .autonomy import (
    ErrorToDiffEngine,
    ErrorType,
    ErrorAnalysis,
    FixHint,
    ParsedError,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Core analysis
    "CodeAnalyzer",
    "AnalysisResult",
    "AnalysisLevel",
    "AnalysisMetrics",
    "DeadCodeItem",
    "RefactorSuggestion",
    "analyze_code",
    # AST tools
    "ASTAnalyzer",
    "ASTBuilder",
    "FunctionMetrics",
    "ClassMetrics",
    "build_ast",
    "build_ast_from_file",
    # PDG tools
    "PDGBuilder",
    "PDGAnalyzer",
    "build_pdg",
    # Project Crawler
    "ProjectCrawler",
    "CrawlResult",
    "FileAnalysisResult",
    "crawl_project",
    # Surgical Extractor
    "SurgicalExtractor",
    "ExtractionResult",
    "ContextualExtraction",
    "CrossFileSymbol",
    "CrossFileResolution",
    "extract_function",
    "extract_class",
    "extract_method",
    "extract_with_context",
    # Unified Extractor (v3.1.0)
    "UnifiedExtractor",
    "UnifiedExtractionResult",
    "Language",
    "detect_language",
    "extract_from_file",
    "extract_from_code",
    # Surgical Patcher
    "SurgicalPatcher",
    "PatchResult",
    "update_function_in_file",
    "update_class_in_file",
    "update_method_in_file",
    # MCP Server
    "create_app",
    "run_server",
    "MCPServerConfig",
    # Autonomy (v3.0.0)
    "ErrorToDiffEngine",
    "ErrorType",
    "ErrorAnalysis",
    "FixHint",
    "ParsedError",
]
