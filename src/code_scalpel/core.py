"""
CodeAnalysisToolkit - Core AST and PDG analysis utilities.

This module provides foundational code analysis capabilities:
- AST parsing and code generation
- Program Dependence Graph (PDG) construction
- Graph visualization

TODO: Core Module Enhancement Roadmap
=====================================

Phase 1 - code_parsers Integration:
- TODO: Replace direct ast.parse() with code_parsers.ParserFactory
- TODO: Use code_parsers.Language enum for language detection
- TODO: Support multi-language PDG construction via code_parsers
- TODO: Integrate code_parsers.ParseResult for error propagation
- TODO: Add fallback to code_parsers when astor unavailable

Phase 2 - PDG Enhancements:
- TODO: Add inter-procedural data flow edges
- TODO: Implement context-sensitive call graph construction
- TODO: Add exception flow edges (try/except/finally)
- TODO: Support async/await control flow
- TODO: Add generator/yield control flow edges
- TODO: Implement PDG slicing (forward and backward)

Phase 3 - Multi-Language PDG:
- TODO: Create JavaScript PDG builder using tree-sitter
- TODO: Create TypeScript PDG builder with type information
- TODO: Create Java PDG builder for method-level analysis
- TODO: Implement unified PDG interface across languages
- TODO: Support cross-language call graphs (e.g., Python calling C extension)

Phase 4 - Visualization Improvements:
- TODO: Add interactive HTML visualization (D3.js or Cytoscape.js)
- TODO: Support hierarchical PDG layout for large graphs
- TODO: Add node filtering by type (data deps only, control deps only)
- TODO: Implement graph diff visualization
- TODO: Add animation for data flow paths
- TODO: Support exporting to DOT, JSON, GraphML formats

Phase 5 - Analysis Queries:
- TODO: Add def-use chain queries
- TODO: Implement reaching definitions analysis
- TODO: Add live variable analysis
- TODO: Implement available expressions analysis
- TODO: Add dominance frontier computation
- TODO: Support custom graph queries via DSL

Phase 6 - Caching & Performance:
- TODO: Implement incremental PDG updates (avoid full rebuild)
- TODO: Add persistent PDG cache
- TODO: Support lazy PDG construction (build on-demand)
- TODO: Implement parallel PDG construction for multi-file projects
- TODO: Add PDG compression for large codebases

Phase 7 - Integration:
- TODO: Add MCP tool for PDG queries
- TODO: Export PDG to Neo4j for advanced graph queries
- TODO: Integrate with IDE extensions for visual debugging
- TODO: Add REST API endpoint for PDG construction
"""

import ast

import astor
import networkx as nx
from graphviz import Digraph


class CodeAnalysisToolkit:
    def __init__(self):
        self.ast_cache = {}
        self.pdg_cache = {}
        self.symbolic_state = {}

    def parse_to_ast(self, code: str) -> ast.AST:
        """Parse Python code into an AST."""
        if code not in self.ast_cache:
            self.ast_cache[code] = ast.parse(code)
        return self.ast_cache[code]

    def ast_to_code(self, node: ast.AST) -> str:
        """Convert AST back to source code."""
        return astor.to_source(node)

    class PDGBuilder(ast.NodeVisitor):
        def __init__(self):
            self.graph = nx.DiGraph()
            self.current_scope = []
            self.var_defs = {}
            self.control_deps = []

        def visit_Assign(self, node):
            target_id = astor.to_source(node.targets[0]).strip()
            value_code = astor.to_source(node.value).strip()
            node_id = f"assign_{target_id}"

            self.graph.add_node(
                node_id, type="assign", target=target_id, value=value_code
            )

            # Add data dependencies
            for var in self._extract_variables(node.value):
                if var in self.var_defs:
                    self.graph.add_edge(
                        self.var_defs[var], node_id, type="data_dependency"
                    )

            self.var_defs[target_id] = node_id
            self.generic_visit(node)

        def visit_If(self, node):
            cond_code = astor.to_source(node.test).strip()
            node_id = f"if_{cond_code}"

            self.graph.add_node(node_id, type="if", condition=cond_code)
            self.control_deps.append(node_id)

            # Process body with control dependency
            for stmt in node.body:
                self.visit(stmt)
                stmt_id = list(self.graph.nodes)[-1]
                self.graph.add_edge(node_id, stmt_id, type="control_dependency")

            self.control_deps.pop()
            self.generic_visit(node)

        def _extract_variables(self, node):
            variables = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Name):
                    variables.add(child.id)
            return variables

    def build_pdg(self, code: str) -> nx.DiGraph:
        """Build a Program Dependence Graph from code."""
        if code not in self.pdg_cache:
            tree = self.parse_to_ast(code)
            builder = self.PDGBuilder()
            builder.visit(tree)
            self.pdg_cache[code] = builder.graph
        return self.pdg_cache[code]

    def visualize_pdg(self, graph: nx.DiGraph, output_file: str = "pdg.png"):
        """Visualize the PDG using graphviz."""
        dot = Digraph(comment="Program Dependence Graph")

        for node in graph.nodes:
            attrs = graph.nodes[node]
            label = f"{node}\n{attrs.get('type', '')}"
            if "value" in attrs:
                label += f"\nvalue: {attrs['value']}"
            dot.node(str(node), label)

        for edge in graph.edges:
            edge_type = graph.edges[edge]["type"]
            color = "blue" if edge_type == "data_dependency" else "red"
            dot.edge(str(edge[0]), str(edge[1]), color=color)

        dot.render(output_file, view=True)
