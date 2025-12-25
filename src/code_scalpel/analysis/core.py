"""
CodeAnalysisToolkit - Core AST and PDG analysis utilities.

# [20251224_REFACTOR] Moved from code_scalpel/core.py to
# code_scalpel/analysis/core.py as part of Issue #3
# in PROJECT_REORG_REFACTOR.md Phase 1.

This module provides foundational code analysis capabilities:
- AST parsing and code generation
- Program Dependence Graph (PDG) construction
- Graph visualization

TODO: Core Module Enhancement Roadmap
=====================================

COMMUNITY (Current & Planned):
- TODO [COMMUNITY]: Add inter-procedural data flow edges (current)
- TODO [COMMUNITY]: Implement context-sensitive call graph construction
- TODO [COMMUNITY]: Add exception flow edges (try/except/finally)
- TODO [COMMUNITY]: Add generator/yield control flow edges
- TODO [COMMUNITY]: Add def-use chain queries
- TODO [COMMUNITY]: Implement reaching definitions analysis
- TODO [COMMUNITY]: Add live variable analysis
- TODO [COMMUNITY]: Implement available expressions analysis

PRO (Enhanced Features):
- TODO [PRO]: Replace direct ast.parse() with code_parsers.ParserFactory
- TODO [PRO]: Use code_parsers.Language enum for language detection
- TODO [PRO]: Integrate code_parsers.ParseResult for error propagation
- TODO [PRO]: Support async/await control flow
- TODO [PRO]: Implement PDG slicing (forward and backward)
- TODO [PRO]: Create JavaScript PDG builder using tree-sitter
- TODO [PRO]: Create TypeScript PDG builder with type information
- TODO [PRO]: Add dominance frontier computation
- TODO [PRO]: Support custom graph queries via DSL
- TODO [PRO]: Implement incremental PDG updates (avoid full rebuild)
- TODO [PRO]: Add persistent PDG cache
- TODO [PRO]: Support lazy PDG construction (build on-demand)
- TODO [PRO]: Support exporting to DOT, JSON, GraphML formats

ENTERPRISE (Advanced Capabilities):
- TODO [ENTERPRISE]: Support multi-language PDG construction via code_parsers
- TODO [ENTERPRISE]: Add fallback to code_parsers when astor unavailable
- TODO [ENTERPRISE]: Create Java PDG builder for method-level analysis
- TODO [ENTERPRISE]: Implement unified PDG interface across languages
- TODO [ENTERPRISE]: Support cross-language call graphs (e.g., Python calling C extension)
- TODO [ENTERPRISE]: Add interactive HTML visualization (D3.js or Cytoscape.js)
- TODO [ENTERPRISE]: Support hierarchical PDG layout for large graphs
- TODO [ENTERPRISE]: Add node filtering by type (data deps only, control deps only)
- TODO [ENTERPRISE]: Implement graph diff visualization
- TODO [ENTERPRISE]: Add animation for data flow paths
- TODO [ENTERPRISE]: Implement parallel PDG construction for multi-file projects
- TODO [ENTERPRISE]: Add PDG compression for large codebases
- TODO [ENTERPRISE]: Add MCP tool for PDG queries
- TODO [ENTERPRISE]: Export PDG to Neo4j for advanced graph queries
- TODO [ENTERPRISE]: Integrate with IDE extensions for visual debugging
- TODO [ENTERPRISE]: Add REST API endpoint for PDG construction
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
