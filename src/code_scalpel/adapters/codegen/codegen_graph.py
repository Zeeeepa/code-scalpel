"""
Codegen Graph Adapter

Direct imports from Codegen SDK graph extension - no reimplementation.
Provides graph-based codebase analysis with tier unification.
"""

from codegen.extensions.graph.create_graph import (
    create_codebase_graph as _create_codebase_graph
)

from codegen.extensions.graph.main import (
    visualize_codebase as _visualize_codebase
)

# Re-export with tier unification
# All graph functionality is now Community tier accessible


def create_codebase_graph(*args, **kwargs):
    """
    Create codebase graph - Community tier (unified from Enterprise)
    Direct passthrough to Codegen SDK
    
    Creates a graph representation of the codebase structure,
    including dependencies, imports, and symbol relationships.
    """
    return _create_codebase_graph(*args, **kwargs)


def visualize_codebase(*args, **kwargs):
    """
    Visualize codebase in Neo4j - Community tier (unified from Enterprise)
    Direct passthrough to Codegen SDK
    
    Args:
        codebase: The codebase to visualize
        neo4j_uri: Neo4j database URI
        username: Neo4j username
        password: Neo4j password
    """
    return _visualize_codebase(*args, **kwargs)

