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

TODO ITEMS:

COMMUNITY TIER (Core PDG Functionality):
1. TODO: Verify PDGBuilder handles all Python AST node types
2. TODO: Add control flow graph (CFG) extraction from PDG
3. TODO: Implement basic data dependency tracking
4. TODO: Create PDG visualization in Graphviz format
5. TODO: Add PDG export to standard graph formats (GML, GraphML)
6. TODO: Implement program slicer for basic backward slicing
7. TODO: Create PDG analysis framework for query execution
8. TODO: Add performance metrics collection (nodes, edges, complexity)
9. TODO: Implement PDG debugging/inspection tools
10. TODO: Document PDG algorithms and analysis techniques

PRO TIER (Advanced Analysis):
11. TODO: Add interprocedural analysis (function call chains)
12. TODO: Implement context-sensitive data flow analysis
13. TODO: Add taint tracking with custom sources/sinks
14. TODO: Create forward slicing capabilities
15. TODO: Implement PDG comparison and diffing
16. TODO: Add incremental PDG updates (delta computation)
17. TODO: Support multiple slicing criteria simultaneously
18. TODO: Implement advanced alias analysis
19. TODO: Add security vulnerability pattern detection in PDG
20. TODO: Create HTML/interactive visualization reports

ENTERPRISE TIER (Scalability & Intelligence):
21. TODO: Implement distributed PDG computation for large codebases
22. TODO: Add polyglot PDG support (JavaScript, Java, C++)
23. TODO: Create PDG query DSL for complex analysis patterns
24. TODO: Implement semantic equivalence checking via symbolic execution
25. TODO: Add machine learning-based vulnerability detection on PDG
26. TODO: Support real-time PDG updates in distributed systems
27. TODO: Implement federated PDG analysis across multiple repositories
28. TODO: Add quantum-safe PDG hashing for integrity verification
29. TODO: Create blockchain-based PDG provenance tracking
30. TODO: Implement AI-powered PDG-based code recommendations
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
