"""
Codegen Multigraph Adapter

Direct imports from Codegen SDK multigraph - no reimplementation.
Provides advanced graph algorithms for dependency analysis.

Features:
- Multi-graph algorithms
- Circular dependency detection
- Impact analysis
- Module coupling metrics
"""

from codegen.sdk.codebase.multigraph import (
    MultiGraph as _MultiGraph
)

# Re-export with tier unification
# All multigraph functionality is now Community tier accessible

MultiGraph = _MultiGraph
"""
Multi-graph class - Community tier (unified from Enterprise)

Advanced graph data structure for codebase analysis with:
- Multiple edge types (imports, calls, inheritance)
- Graph algorithms (shortest path, cycles, components)
- Dependency analysis
- Impact calculation

Example:
    graph = codebase.build_graph()
    cycles = graph.find_cycles()
    impact = graph.calculate_impact(symbol)
"""

__all__ = [
    'MultiGraph',
]

