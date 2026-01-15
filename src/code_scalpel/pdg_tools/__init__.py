# src/pdg_tools/__init__.py
"""
Program Dependence Graph (PDG) Tools - Advanced program analysis toolkit.

PDG is a fundamental program representation that captures both data and control
dependencies between program statements, enabling sophisticated code analysis
for security, optimization, and refactoring.
"""

# TODO [POLYGLOT] Add polyglot PDG support for JavaScript/TypeScript using tree-sitter
# TODO [POLYGLOT] Extend PDGBuilder to support Java with tree-sitter-java
# TODO [POLYGLOT] Add C/C++ support for security analysis of system-level code
# TODO [POLYGLOT] Implement language-specific exception/error handling models

# TODO [INCREMENTAL] Support PDG updates for code changes without rebuilding
# TODO [INCREMENTAL] Track minimal delta between original and modified PDGs
# TODO [INCREMENTAL] Enable efficient diff-based analysis for CI/CD pipelines
# TODO [INCREMENTAL] Support file-level PDG with cross-file dependency tracking

# TODO [DISTRIBUTED] Implement sharded PDG for large codebases (split by module/package)
# TODO [DISTRIBUTED] Support inter-shard dependency tracking
# TODO [DISTRIBUTED] Implement MapReduce-style analysis over distributed PDGs
# TODO [DISTRIBUTED] Add horizontal scaling for enterprise codebases

# TODO [QUERY_LANGUAGE] Implement DSL for expressing PDG traversal queries
# TODO [QUERY_LANGUAGE] Support declarative vulnerability pattern matching
# TODO [QUERY_LANGUAGE] Add query optimization and plan caching
# TODO [QUERY_LANGUAGE] Support batch query execution with result streaming

# TODO [VISUALIZATION] Implement interactive web-based PDG explorer
# TODO [VISUALIZATION] Add focus+context navigation for large graphs
# TODO [VISUALIZATION] Support real-time PDG updates in visualizer
# TODO [VISUALIZATION] Add syntax highlighting and code preview on hover

# TODO [COMMUNITY] Verify PDGBuilder handles all Python AST node types
# TODO [COMMUNITY] Add control flow graph (CFG) extraction from PDG
# TODO [COMMUNITY] Implement basic data dependency tracking
# TODO [COMMUNITY] Create PDG visualization in Graphviz format
# TODO [COMMUNITY] Add PDG export to standard graph formats (GML, GraphML)
# TODO [COMMUNITY] Implement program slicer for basic backward slicing
# TODO [COMMUNITY] Create PDG analysis framework for query execution
# TODO [COMMUNITY] Add performance metrics collection (nodes, edges, complexity)
# TODO [COMMUNITY] Implement PDG debugging/inspection tools
# TODO [COMMUNITY] Document PDG algorithms and analysis techniques

# TODO [PRO] Add interprocedural analysis (function call chains)
# TODO [PRO] Implement context-sensitive data flow analysis
# TODO [PRO] Add taint tracking with custom sources/sinks
# TODO [PRO] Create forward slicing capabilities
# TODO [PRO] Implement PDG comparison and diffing
# TODO [PRO] Add incremental PDG updates (delta computation)
# TODO [PRO] Support multiple slicing criteria simultaneously
# TODO [PRO] Implement advanced alias analysis
# TODO [PRO] Add security vulnerability pattern detection in PDG
# TODO [PRO] Create HTML/interactive visualization reports

# TODO [ENTERPRISE] Implement distributed PDG computation for large codebases
# TODO [ENTERPRISE] Add polyglot PDG support (JavaScript, Java, C++)
# TODO [ENTERPRISE] Create PDG query DSL for complex analysis patterns
# TODO [ENTERPRISE] Implement semantic equivalence checking via symbolic execution
# TODO [ENTERPRISE] Add machine learning-based vulnerability detection on PDG
# TODO [ENTERPRISE] Support real-time PDG updates in distributed systems
# TODO [ENTERPRISE] Implement federated PDG analysis across multiple repositories
# TODO [ENTERPRISE] Add quantum-safe PDG hashing for integrity verification
# TODO [ENTERPRISE] Create blockchain-based PDG provenance tracking
# TODO [ENTERPRISE] Implement AI-powered PDG-based code recommendations

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
