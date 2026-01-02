import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import networkx as nx

# [20251221_TODO] Add PDG serialization formats:
#     - Implement efficient binary PDG format
#     - Support compressed PDG storage for distribution
#     - Add incremental serialization for updates
#     - Support multiple versions for backwards compatibility

# [20251221_TODO] Add PDG comparison and diffing:
#     - Compute structural differences between PDGs
#     - Support semantic diff (behavior changes, not just syntax)
#     - Generate human-readable PDG diffs
#     - Support merging PDG changes from different branches

"""
TODO ITEMS:

COMMUNITY TIER (Basic Utilities):
1. TODO: Implement PDG to JSON serialization
2. TODO: Add JSON deserialization to reconstruct PDG
3. TODO: Create GraphML export format
4. TODO: Implement GML export for compatibility
5. TODO: Add DOT format export for Graphviz
6. TODO: Create basic node and edge info accessors
7. TODO: Implement PDG statistics (size, complexity metrics)
8. TODO: Add dependency type filtering utilities
9. TODO: Create scope traversal helpers
10. TODO: Document utility functions and formats

PRO TIER (Advanced Analysis):
11. TODO: Implement PDG comparison and structural diffing
12. TODO: Add semantic diff detection (behavior changes)
13. TODO: Create human-readable diff reports
14. TODO: Implement PDG merging from different branches
15. TODO: Add binary PDG serialization format
16. TODO: Create compressed PDG storage
17. TODO: Implement incremental PDG serialization
18. TODO: Add PDG hashing and fingerprinting
19. TODO: Support version-based PDG compatibility
20. TODO: Create performance optimization utilities

ENTERPRISE TIER (Distribution & Intelligence):
21. TODO: Implement distributed PDG serialization
22. TODO: Add stream-based serialization for large graphs
23. TODO: Create polyglot utility support (JS, Java, C++)
24. TODO: Implement federated PDG comparison
25. TODO: Add machine learning-based diff prediction
26. TODO: Support quantum-safe PDG hashing
27. TODO: Implement blockchain-based PDG integrity verification
28. TODO: Add zero-knowledge proofs for PDG properties
29. TODO: Create AI-powered PDG optimization suggestions
30. TODO: Implement distributed caching for PDG computations
"""


@dataclass
class NodeInfo:
    """Information about a PDG node."""

    id: str
    type: str
    data: dict[str, Any]
    dependencies: list[tuple[str, str]]
    dependents: list[tuple[str, str]]
    scope: Optional[str]
    metrics: dict[str, Any]


class DependencyType(Enum):
    """Types of dependencies in the PDG."""

    CONTROL = "control"
    DATA = "data"
    CALL = "call"
    PARAMETER = "parameter"
    EXCEPTION = "exception"


class PDGUtils:
    """Utility functions for working with Program Dependence Graphs."""

    # [20251221_TODO] Add performance optimization utilities:
    #     - Implement PDG pruning for irrelevant nodes
    #     - Add graph summarization for large PDGs
    #     - Support memoization of expensive analyses
    #     - Implement caching strategies for multi-use analyses

    # [20251221_TODO] Add PDG validation and sanity checks:
    #     - Verify PDG structural properties
    #     - Detect cycles that shouldn't exist
    #     - Check node/edge consistency
    #     - Validate dependency type classifications

    # [20251221_TODO] Add PDG statistics and profiling:
    #     - Compute detailed PDG metrics (density, diameter, etc.)
    #     - Profile analysis performance per node type
    #     - Track cache hit rates and memory usage
    #     - Generate performance reports

    @staticmethod
    def analyze_node(pdg: nx.DiGraph, node: str) -> NodeInfo:
        """Get comprehensive information about a PDG node."""
        if not pdg.has_node(node):
            raise ValueError(f"Node {node} not found in PDG")

        node_data = pdg.nodes[node]

        # Get dependencies
        dependencies = [
            (pred, pdg.edges[pred, node]["type"]) for pred in pdg.predecessors(node)
        ]

        # Get dependents
        dependents = [
            (succ, pdg.edges[node, succ]["type"]) for succ in pdg.successors(node)
        ]

        # Calculate node metrics
        metrics = PDGUtils.calculate_node_metrics(pdg, node)

        return NodeInfo(
            id=node,
            type=node_data.get("type", "unknown"),
            data=node_data,
            dependencies=dependencies,
            dependents=dependents,
            scope=PDGUtils.get_node_scope(pdg, node),
            metrics=metrics,
        )

    @staticmethod
    def find_paths(
        pdg: nx.DiGraph, source: str, target: str, dep_types: Optional[set[str]] = None
    ) -> list[list[str]]:
        """Find all paths between nodes considering dependency types."""
        if not pdg.has_node(source) or not pdg.has_node(target):
            return []

        paths = []
        visited = set()

        def dfs(current: str, path: list[str]):
            if current == target:
                paths.append(path[:])
                return

            visited.add(current)
            for succ in pdg.successors(current):
                edge_type = pdg.edges[current, succ]["type"]
                if succ not in visited and (not dep_types or edge_type in dep_types):
                    dfs(succ, path + [succ])
            visited.remove(current)

        dfs(source, [source])
        return paths

    @staticmethod
    def calculate_node_metrics(pdg: nx.DiGraph, node: str) -> dict[str, Any]:
        """Calculate various metrics for a node."""
        return {
            "in_degree": pdg.in_degree(node),
            "out_degree": pdg.out_degree(node),
            "betweenness_centrality": nx.betweenness_centrality(pdg)[node],
            "dependency_types": PDGUtils.get_dependency_types(pdg, node),
            "reachable_nodes": len(nx.descendants(pdg, node)),
            "dependent_nodes": len(nx.ancestors(pdg, node)),
        }

    @staticmethod
    def get_dependency_types(pdg: nx.DiGraph, node: str) -> dict[str, int]:
        """Get count of different dependency types for a node."""
        dep_types = defaultdict(int)

        # Incoming dependencies
        for pred in pdg.predecessors(node):
            dep_type = pdg.edges[pred, node]["type"]
            dep_types[f"in_{dep_type}"] += 1

        # Outgoing dependencies
        for succ in pdg.successors(node):
            dep_type = pdg.edges[node, succ]["type"]
            dep_types[f"out_{dep_type}"] += 1

        return dict(dep_types)

    @staticmethod
    def get_node_scope(pdg: nx.DiGraph, node: str) -> Optional[str]:
        """Determine the scope (function/class/module) of a node."""
        for pred in pdg.predecessors(node):
            pred_type = pdg.nodes[pred].get("type")
            if pred_type in ("function", "class", "module"):
                return f"{pred_type}:{pdg.nodes[pred].get('name', 'unknown')}"
        return None

    @staticmethod
    def find_common_ancestors(pdg: nx.DiGraph, nodes: list[str]) -> set[str]:
        """Find common ancestors of multiple nodes."""
        if not nodes:
            return set()

        ancestors = [nx.ancestors(pdg, node) for node in nodes]
        return set.intersection(*ancestors)

    @staticmethod
    def find_common_descendants(pdg: nx.DiGraph, nodes: list[str]) -> set[str]:
        """Find common descendants of multiple nodes."""
        if not nodes:
            return set()

        descendants = [nx.descendants(pdg, node) for node in nodes]
        return set.intersection(*descendants)

    @staticmethod
    def get_subgraph_between(
        pdg: nx.DiGraph, start_nodes: list[str], end_nodes: list[str]
    ) -> nx.DiGraph:
        """Extract subgraph between start and end nodes."""
        # Find all nodes in paths between start and end nodes
        nodes_in_paths = set()
        for start in start_nodes:
            for end in end_nodes:
                paths = PDGUtils.find_paths(pdg, start, end)
                for path in paths:
                    nodes_in_paths.update(path)

        subgraph = pdg.subgraph(nodes_in_paths)
        return nx.DiGraph(subgraph)

    @staticmethod
    def compute_node_hash(node_data: dict[str, Any]) -> str:
        """Compute a stable hash for node data."""
        # Sort dictionary to ensure stable hash
        sorted_items = sorted(node_data.items(), key=lambda x: str(x[0]))

        # Convert to string and hash
        data_str = json.dumps(sorted_items, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    @staticmethod
    def find_similar_nodes(
        pdg: nx.DiGraph, node: str, similarity_threshold: float = 0.8
    ) -> list[str]:
        """Find nodes with similar structure and dependencies."""
        PDGUtils.compute_node_hash(pdg.nodes[node])
        similar_nodes = []

        for other_node in pdg.nodes:
            if other_node != node:
                PDGUtils.compute_node_hash(pdg.nodes[other_node])
                similarity = PDGUtils.calculate_node_similarity(pdg, node, other_node)
                if similarity >= similarity_threshold:
                    similar_nodes.append(other_node)

        return similar_nodes

    @staticmethod
    def calculate_node_similarity(pdg: nx.DiGraph, node1: str, node2: str) -> float:
        """Calculate similarity between two nodes."""
        # Compare node types
        type_similarity = pdg.nodes[node1].get("type") == pdg.nodes[node2].get("type")

        # Compare dependency patterns
        deps1 = PDGUtils.get_dependency_types(pdg, node1)
        deps2 = PDGUtils.get_dependency_types(pdg, node2)

        dep_similarity = PDGUtils._calculate_dict_similarity(deps1, deps2)

        # Weight and combine similarities
        return 0.4 * type_similarity + 0.6 * dep_similarity

    @staticmethod
    def find_node_clusters(pdg: nx.DiGraph, min_size: int = 2) -> list[set[str]]:
        """Find clusters of related nodes."""
        # Create similarity graph
        sim_graph = nx.Graph()

        for node1 in pdg.nodes:
            for node2 in pdg.nodes:
                if node1 < node2:  # Avoid duplicate comparisons
                    similarity = PDGUtils.calculate_node_similarity(pdg, node1, node2)
                    if similarity > 0.7:  # Threshold for clustering
                        sim_graph.add_edge(node1, node2, weight=similarity)

        # Find connected components (clusters)
        clusters = [
            cluster
            for cluster in nx.connected_components(sim_graph)
            if len(cluster) >= min_size
        ]

        return clusters

    @staticmethod
    def export_to_json(pdg: nx.DiGraph, filepath: str):
        """Export PDG to JSON format."""
        data = {
            "nodes": [
                {"id": node, "data": PDGUtils._clean_for_json(data)}
                for node, data in pdg.nodes(data=True)
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "data": PDGUtils._clean_for_json(data),
                }
                for source, target, data in pdg.edges(data=True)
            ],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def import_from_json(filepath: str) -> nx.DiGraph:
        """Import PDG from JSON format."""
        with open(filepath) as f:
            data = json.load(f)

        pdg = nx.DiGraph()

        # Add nodes
        for node_data in data["nodes"]:
            pdg.add_node(node_data["id"], **node_data["data"])

        # Add edges
        for edge_data in data["edges"]:
            pdg.add_edge(edge_data["source"], edge_data["target"], **edge_data["data"])

        return pdg

    @staticmethod
    def _calculate_dict_similarity(dict1: dict, dict2: dict) -> float:
        """Calculate similarity between two dictionaries."""
        keys = set(dict1.keys()) | set(dict2.keys())
        if not keys:
            return 1.0

        differences = sum(abs(dict1.get(k, 0) - dict2.get(k, 0)) for k in keys)

        max_possible_diff = sum(max(dict1.get(k, 0), dict2.get(k, 0)) for k in keys)

        if max_possible_diff == 0:
            return 1.0

        return 1 - (differences / (2 * max_possible_diff))

    @staticmethod
    def _clean_for_json(data: dict) -> dict:
        """Clean dictionary values for JSON serialization."""
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool, type(None))):
                cleaned[key] = value
            elif isinstance(value, (list, tuple, set)):
                cleaned[key] = list(value)
            elif isinstance(value, dict):
                cleaned[key] = PDGUtils._clean_for_json(value)
            else:
                cleaned[key] = str(value)
        return cleaned


def get_node_info(pdg: nx.DiGraph, node: str) -> NodeInfo:
    """Convenience function to get node information."""
    return PDGUtils.analyze_node(pdg, node)


def find_paths(pdg: nx.DiGraph, source: str, target: str) -> list[list[str]]:
    """Convenience function to find paths between nodes."""
    return PDGUtils.find_paths(pdg, source, target)


def export_pdg(pdg: nx.DiGraph, filepath: str):
    """Convenience function to export PDG."""
    PDGUtils.export_to_json(pdg, filepath)


def import_pdg(filepath: str) -> nx.DiGraph:
    """Convenience function to import PDG."""
    return PDGUtils.import_from_json(filepath)
