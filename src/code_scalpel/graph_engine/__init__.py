"""
Graph Engine - Universal cross-language code graph with confidence scoring.

[20251216_FEATURE] v2.1.0 - Cross-language unified graph with confidence engine

This module provides a unified graph representation for code across multiple
programming languages (Python, Java, TypeScript, JavaScript). It implements:

1. Universal Node IDs - Standardized format: language::module::type::name[:method]
2. Omni-Schema JSON Format - Graph with nodes and edges
3. Confidence Engine - Scoring edges with confidence levels (0.0-1.0)
4. Cross-Boundary Analysis - Track taint and dependencies across languages
5. HTTP Link Detection - Connect frontend API calls to backend endpoints

Example:
    >>> from code_scalpel.graph_engine import UniversalGraphBuilder
    >>> builder = UniversalGraphBuilder()
    >>> builder.add_python_file("app.py", code)
    >>> builder.add_java_file("UserController.java", code)
    >>> graph = builder.build()
    >>> print(graph.to_json())
"""

from .node_id import (
    UniversalNodeID,
    NodeType,
    parse_node_id,
    create_node_id,
)

from .confidence import (
    ConfidenceEngine,
    ConfidenceLevel,
    EdgeType,
    CONFIDENCE_RULES,
)

from .graph import (
    GraphNode,
    GraphEdge,
    UniversalGraph,
    GraphBuilder,
)

from .http_detector import (
    HTTPLinkDetector,
    HTTPMethod,
    HTTPLink,
)

__all__ = [
    # Node ID system
    "UniversalNodeID",
    "NodeType",
    "parse_node_id",
    "create_node_id",
    # Confidence engine
    "ConfidenceEngine",
    "ConfidenceLevel",
    "EdgeType",
    "CONFIDENCE_RULES",
    # Graph structure
    "GraphNode",
    "GraphEdge",
    "UniversalGraph",
    "GraphBuilder",
    # HTTP detection
    "HTTPLinkDetector",
    "HTTPMethod",
    "HTTPLink",
]
