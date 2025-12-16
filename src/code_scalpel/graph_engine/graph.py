"""
Universal Graph - Omni-schema graph representation for cross-language code.

[20251216_FEATURE] v2.1.0 - Unified graph structure with nodes and edges

This module implements the omni-schema JSON format for representing code
relationships across multiple programming languages. The graph contains:

- Nodes: Code elements (functions, classes, endpoints, etc.)
- Edges: Relationships with confidence scores and evidence

Example JSON output:
{
  "graph": {
    "nodes": [
      {"id": "java::UserController:getUser", "type": "endpoint", "route": "/api/users"},
      {"id": "typescript::fetchUsers", "type": "client", "target": "/api/users"}
    ],
    "edges": [
      {
        "from": "typescript::fetchUsers",
        "to": "java::UserController:getUser",
        "confidence": 0.95,
        "evidence": "Route string match: /api/users",
        "type": "http_call"
      }
    ]
  }
}
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .node_id import UniversalNodeID, NodeType
from .confidence import ConfidenceEngine, ConfidenceEvidence, EdgeType


# [20251216_FEATURE] Graph node representation
@dataclass
class GraphNode:
    """
    A node in the universal code graph.

    Attributes:
        id: Universal node ID
        metadata: Additional properties (route, file, line, etc.)
    """

    id: UniversalNodeID
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = self.id.to_dict()
        result.update(self.metadata)
        return result

    @staticmethod
    def from_dict(data: dict) -> GraphNode:
        """Create from dictionary."""
        node_id = UniversalNodeID.from_dict(data)
        # Extract metadata (everything except node_id fields)
        node_id_keys = {"id", "language", "module", "type", "name", "method", "line", "file"}
        metadata = {k: v for k, v in data.items() if k not in node_id_keys}
        return GraphNode(id=node_id, metadata=metadata)


# [20251216_FEATURE] Graph edge with confidence scoring
@dataclass
class GraphEdge:
    """
    An edge in the universal code graph with confidence scoring.

    Attributes:
        from_id: Source node ID (as string)
        to_id: Target node ID (as string)
        edge_type: Type of relationship
        confidence: Confidence score (0.0-1.0)
        evidence: Human-readable explanation
        metadata: Additional context
    """

    from_id: str
    to_id: str
    edge_type: EdgeType
    confidence: float
    evidence: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "from": self.from_id,
            "to": self.to_id,
            "type": self.edge_type.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }
        result.update(self.metadata)
        return result

    @staticmethod
    def from_dict(data: dict) -> GraphEdge:
        """Create from dictionary."""
        # Extract core fields
        from_id = data["from"]
        to_id = data["to"]
        edge_type = EdgeType(data["type"])
        confidence = data["confidence"]
        evidence = data["evidence"]

        # Extract metadata
        metadata_keys = {"from", "to", "type", "confidence", "evidence"}
        metadata = {k: v for k, v in data.items() if k not in metadata_keys}

        return GraphEdge(
            from_id=from_id,
            to_id=to_id,
            edge_type=edge_type,
            confidence=confidence,
            evidence=evidence,
            metadata=metadata,
        )


# [20251216_FEATURE] Universal graph container
@dataclass
class UniversalGraph:
    """
    Universal cross-language code graph.

    This graph represents code elements and their relationships across
    Python, Java, TypeScript, and JavaScript. Each edge carries a
    confidence score indicating reliability of the relationship.

    Attributes:
        nodes: List of graph nodes
        edges: List of graph edges
        metadata: Graph-level metadata (project info, timestamps, etc.)
    """

    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        # Check if node already exists
        node_id_str = str(node.id)
        if not any(str(n.id) == node_id_str for n in self.nodes):
            self.nodes.append(node)

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by its ID string."""
        for node in self.nodes:
            if str(node.id) == node_id:
                return node
        return None

    def get_edges_from(self, node_id: str) -> List[GraphEdge]:
        """Get all edges originating from a node."""
        return [edge for edge in self.edges if edge.from_id == node_id]

    def get_edges_to(self, node_id: str) -> List[GraphEdge]:
        """Get all edges targeting a node."""
        return [edge for edge in self.edges if edge.to_id == node_id]

    def get_dependencies(
        self, node_id: str, min_confidence: float = 0.8
    ) -> Dict[str, List[GraphEdge]]:
        """
        Get dependencies with confidence filtering.

        Args:
            node_id: Node to analyze
            min_confidence: Minimum confidence threshold

        Returns:
            Dictionary with "definite" and "uncertain" edge lists,
            plus "requires_human_approval" flag
        """
        edges = self.get_edges_from(node_id)

        definite = [e for e in edges if e.confidence >= min_confidence]
        uncertain = [e for e in edges if e.confidence < min_confidence]

        return {
            "definite": definite,
            "uncertain": uncertain,
            "requires_human_approval": len(uncertain) > 0,
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "graph": {
                "nodes": [node.to_dict() for node in self.nodes],
                "edges": [edge.to_dict() for edge in self.edges],
            },
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @staticmethod
    def from_dict(data: dict) -> UniversalGraph:
        """Create from dictionary."""
        graph_data = data.get("graph", {})
        nodes = [GraphNode.from_dict(n) for n in graph_data.get("nodes", [])]
        edges = [GraphEdge.from_dict(e) for e in graph_data.get("edges", [])]
        metadata = data.get("metadata", {})

        graph = UniversalGraph(metadata=metadata)
        graph.nodes = nodes
        graph.edges = edges
        return graph

    @staticmethod
    def from_json(json_str: str) -> UniversalGraph:
        """Create from JSON string."""
        data = json.loads(json_str)
        return UniversalGraph.from_dict(data)


# [20251216_FEATURE] Graph builder for constructing universal graphs
class GraphBuilder:
    """
    Builder for constructing universal cross-language graphs.

    This class provides a high-level interface for building graphs from
    code files in different languages.

    Example:
        >>> builder = GraphBuilder()
        >>> builder.add_python_module("app/handlers.py", code)
        >>> builder.add_java_class("UserController.java", code)
        >>> graph = builder.build()
    """

    def __init__(self):
        """Initialize graph builder."""
        self.graph = UniversalGraph()
        self.confidence_engine = ConfidenceEngine()
        self._node_registry: Dict[str, GraphNode] = {}

    def add_node(
        self,
        node_id: UniversalNodeID,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GraphNode:
        """
        Add a node to the graph.

        Args:
            node_id: Universal node ID
            metadata: Optional metadata

        Returns:
            Created GraphNode
        """
        node = GraphNode(id=node_id, metadata=metadata or {})
        node_id_str = str(node_id)

        # Check if already exists
        if node_id_str not in self._node_registry:
            self.graph.add_node(node)
            self._node_registry[node_id_str] = node

        return self._node_registry[node_id_str]

    def add_edge(
        self,
        from_id: str,
        to_id: str,
        edge_type: EdgeType,
        context: Optional[Dict[str, Any]] = None,
    ) -> GraphEdge:
        """
        Add an edge with automatic confidence scoring.

        Args:
            from_id: Source node ID (as string)
            to_id: Target node ID (as string)
            edge_type: Type of relationship
            context: Optional context for confidence scoring

        Returns:
            Created GraphEdge
        """
        # Score the edge
        evidence = self.confidence_engine.score_edge(edge_type, context or {})

        edge = GraphEdge(
            from_id=from_id,
            to_id=to_id,
            edge_type=edge_type,
            confidence=evidence.final_score,
            evidence=evidence.explanation,
            metadata=context or {},
        )

        self.graph.add_edge(edge)
        return edge

    def build(self) -> UniversalGraph:
        """
        Build and return the final graph.

        Returns:
            UniversalGraph with all nodes and edges
        """
        return self.graph

    def reset(self) -> None:
        """Reset the builder to empty state."""
        self.graph = UniversalGraph()
        self._node_registry = {}
