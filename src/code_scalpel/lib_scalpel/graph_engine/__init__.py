"""Graph Engine - The Senses.

Provides core data structures and scanning logic:
- UniversalGraph: Cross-language code graph
- GraphNode/GraphEdge: Graph elements
- UniversalNodeID: Standardized node identification
- ProjectScanner: Pure project crawler with config-based limits
"""

from .universal_graph import UniversalGraph, GraphNode, GraphEdge, NeighborhoodResult
from .node_id import UniversalNodeID, NodeType
from .confidence import ConfidenceEngine, EdgeType
from .scanner import ProjectScanner

__all__ = [
    "UniversalGraph",
    "GraphNode",
    "GraphEdge",
    "NeighborhoodResult",
    "UniversalNodeID",
    "NodeType",
    "ConfidenceEngine",
    "EdgeType",
    "ProjectScanner",
]
