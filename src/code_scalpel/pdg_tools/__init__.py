# src/pdg_tools/__init__.py
"""
Program Dependence Graph (PDG) Tools - Advanced program analysis toolkit.

PDG is a fundamental program representation that captures both data and control
dependencies between program statements, enabling sophisticated code analysis
for security, optimization, and refactoring.

[20251221_TODO] Add polyglot PDG support:
    - Extend PDGBuilder to support JavaScript/TypeScript (using tree-sitter)
    - Extend to support Java (using tree-sitter-java)
    - Add C/C++ support for security analysis of system-level code
    - Implement language-specific exception/error handling models

[20251221_TODO] Add incremental/differential PDG:
    - Support PDG updates for code changes without rebuilding
    - Track minimal delta between original and modified PDGs
    - Enable efficient diff-based analysis for CI/CD pipelines
    - Support file-level PDG with cross-file dependency tracking

[20251221_TODO] Add distributed PDG computation:
    - Implement sharded PDG for large codebases (split by module/package)
    - Support inter-shard dependency tracking
    - Implement MapReduce-style analysis over distributed PDGs
    - Add horizontal scaling for enterprise codebases

[20251221_TODO] Add PDG query language:
    - Implement DSL for expressing PDG traversal queries
    - Support declarative vulnerability pattern matching
    - Add query optimization and plan caching
    - Support batch query execution with result streaming

[20251221_TODO] Add visualization improvements:
    - Implement interactive web-based PDG explorer
    - Add focus+context navigation for large graphs
    - Support real-time PDG updates in visualizer
    - Add syntax highlighting and code preview on hover
"""

from .analyzer import (
    DataFlowAnomaly,
    DependencyType,
    PDGAnalyzer,
    SecurityVulnerability,
)
from .builder import NodeType, PDGBuilder, Scope, build_pdg
from .slicer import ProgramSlicer, SliceInfo, SliceType, SlicingCriteria

__all__ = [
    # Builder
    "PDGBuilder",
    "build_pdg",
    "NodeType",
    "Scope",
    # Analyzer
    "PDGAnalyzer",
    "DependencyType",
    "DataFlowAnomaly",
    "SecurityVulnerability",
    # Slicer
    "ProgramSlicer",
    "SlicingCriteria",
    "SliceType",
    "SliceInfo",
]
