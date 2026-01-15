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

# TODO [COMMUNITY] Add GraphBuilder class for constructing graphs programmatically
# TODO [COMMUNITY] Add graph_from_json() to deserialize JSON graphs
# TODO [COMMUNITY] Add graph_to_json() to serialize graphs to JSON
# TODO [COMMUNITY] Add merge_graphs(graph1, graph2) to combine multiple graphs
# TODO [COMMUNITY] Add validate_graph(graph) to check structural integrity
# TODO [COMMUNITY] Add list_all_nodes(graph) to enumerate all nodes
# TODO [COMMUNITY] Add list_all_edges(graph) to enumerate all edges
# TODO [COMMUNITY] Add find_node(graph, node_id) to locate nodes by ID
# TODO [COMMUNITY] Add find_edges_by_type(graph, edge_type) to filter edges
# TODO [COMMUNITY] Add get_node_neighbors(graph, node_id) to find adjacent nodes
# TODO [COMMUNITY] Add count_nodes(graph) for graph size metrics
# TODO [COMMUNITY] Add count_edges(graph) for relationship metrics
# TODO [COMMUNITY] Add get_graph_statistics(graph) for comprehensive metrics
# TODO [COMMUNITY] Add export_graph_to_file(graph, filename, format) for persistence
# TODO [COMMUNITY] Add import_graph_from_file(filename, format) for loading
# TODO [COMMUNITY] Add create_empty_graph() factory method
# TODO [COMMUNITY] Add GraphConfig dataclass for configuration
# TODO [COMMUNITY] Add validate_node_id(node_id) format checker
# TODO [COMMUNITY] Add validate_edge_type(edge_type) validator
# TODO [COMMUNITY] Add list_supported_languages() enumeration
# TODO [COMMUNITY] Add get_language_parser(language) factory
# TODO [COMMUNITY] Add add_custom_node_type(node_type) extensibility
# TODO [COMMUNITY] Add add_custom_edge_type(edge_type) extensibility
# TODO [COMMUNITY] Add graph_to_dict() for dict serialization
# TODO [COMMUNITY] Add graph_from_dict() for dict deserialization
# TODO [PRO] Add async graph building with async_build_graph()
# TODO [PRO] Add streaming graph processing with streaming_add_node()
# TODO [PRO] Add graph caching with cache_graph(graph, cache_key)
# TODO [PRO] Add retrieve_cached_graph(cache_key) for performance
# TODO [PRO] Add graph_diff(graph1, graph2) to compare graphs
# TODO [PRO] Add merge_with_conflict_detection(graph1, graph2)
# TODO [PRO] Add graph_cleanup(graph) to remove orphaned nodes/edges
# TODO [PRO] Add deduplicate_edges(graph) to remove duplicates
# TODO [PRO] Add normalize_node_ids(graph) for consistency
# TODO [PRO] Add graph_compression(graph) to reduce size
# TODO [PRO] Add graph_decompression(compressed_graph)
# TODO [PRO] Add incremental_update(graph, changes) for partial updates
# TODO [PRO] Add graph_versioning() to track graph evolution
# TODO [PRO] Add rollback_to_version(graph, version)
# TODO [PRO] Add graph_change_log() to audit modifications
# TODO [PRO] Add parallel_graph_building(file_list) for multi-file
# TODO [PRO] Add distributed_graph_merge(graph_list, strategy)
# TODO [PRO] Add graph_visualization() for debugging
# TODO [PRO] Add graph_to_mermaid() for diagram generation
# TODO [PRO] Add graph_to_cytoscape_json() for interactive visualization
# TODO [PRO] Add graph_statistics_comparison(graph1, graph2)
# TODO [PRO] Add detect_graph_anomalies(graph) for quality checks
# TODO [PRO] Add filter_edges_by_confidence(graph, threshold)
# TODO [PRO] Add sort_nodes_by_centrality(graph) for importance
# TODO [PRO] Add graph_summary_report(graph) for analysis
# TODO [ENTERPRISE] Add distributed graph construction across services
# TODO [ENTERPRISE] Add federated graph integration across organizations
# TODO [ENTERPRISE] Add multi-region graph synchronization
# TODO [ENTERPRISE] Add sharded graph processing for large codebases
# TODO [ENTERPRISE] Add graph replication for high availability
# TODO [ENTERPRISE] Add graph backup and recovery procedures
# TODO [ENTERPRISE] Add encrypted graph storage (end-to-end)
# TODO [ENTERPRISE] Add audit logging for all graph operations
# TODO [ENTERPRISE] Add compliance reporting for graph access
# TODO [ENTERPRISE] Add multi-tenancy graph isolation
# TODO [ENTERPRISE] Add graph access control enforcement
# TODO [ENTERPRISE] Add role-based graph permissions
# TODO [ENTERPRISE] Add graph monitoring and alerting
# TODO [ENTERPRISE] Add performance profiling on graph operations
# TODO [ENTERPRISE] Add graph optimization recommendations
# TODO [ENTERPRISE] Add ML-based graph anomaly detection
# TODO [ENTERPRISE] Add graph compression ML models
# TODO [ENTERPRISE] Add predictive graph caching
# TODO [ENTERPRISE] Add graph auto-scaling
# TODO [ENTERPRISE] Add circuit breaker for graph operations
# TODO [ENTERPRISE] Add rate limiting graph API
# TODO [ENTERPRISE] Add cost allocation per graph
# TODO [ENTERPRISE] Add billing integration
# TODO [ENTERPRISE] Add SLA monitoring for graph availability
# TODO [ENTERPRISE] Add executive reporting on graph metrics

from .confidence import CONFIDENCE_RULES, ConfidenceEngine, ConfidenceLevel, EdgeType
from .graph import (
    GraphBuilder,
    GraphEdge,
    GraphNode,
    NeighborhoodResult,
    UniversalGraph,
)
from .http_detector import HTTPLink, HTTPLinkDetector, HTTPMethod
from .node_id import NodeType, UniversalNodeID, create_node_id, parse_node_id

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
    # [20251216_FEATURE] v2.5.0 - Graph Neighborhood View
    "NeighborhoodResult",
    # HTTP detection
    "HTTPLinkDetector",
    "HTTPMethod",
    "HTTPLink",
]
