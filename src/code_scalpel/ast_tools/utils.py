from __future__ import annotations

import ast
import tokenize
from collections import defaultdict
from io import StringIO
from typing import Any, Callable, Union


class ASTUtils:
    """
    Utility functions for working with ASTs.

    ====================================================================
    TIER 1: COMMUNITY (Free - High Priority)
    ====================================================================
            TODO [COMMUNITY][FEATURE]: Extract all names from AST
        TODO [COMMUNITY]: Walk AST for Name nodes
        TODO [COMMUNITY]: Collect unique names
        TODO [COMMUNITY]: Distinguish variables vs functions
        TODO [COMMUNITY]: Add 10+ tests for name extraction
            TODO [COMMUNITY][FEATURE]: Get function information
        TODO [COMMUNITY]: Extract function signature
        TODO [COMMUNITY]: Get parameter names and defaults
        TODO [COMMUNITY]: Extract decorators and type hints
        TODO [COMMUNITY]: Add 12+ tests for function info
            TODO [COMMUNITY][FEATURE]: Find nodes matching condition
        TODO [COMMUNITY]: Walk entire AST
        TODO [COMMUNITY]: Apply predicate function
        TODO [COMMUNITY]: Return matching nodes
        TODO [COMMUNITY]: Add 10+ tests for finding nodes
            TODO [COMMUNITY][FEATURE]: Get source code for node
        TODO [COMMUNITY]: Extract line range from AST node
        TODO [COMMUNITY]: Pull source from line array
        TODO [COMMUNITY]: Handle multi-line nodes
        TODO [COMMUNITY]: Add 10+ tests for source extraction
    ====================================================================
    TIER 2: PRO (Commercial - Medium Priority)
    ====================================================================
            TODO [PRO][FEATURE]: Analyze variable dependencies
        TODO [PRO]: Track assignments and uses
        TODO [PRO]: Build dependency graph
        TODO [PRO]: Identify chains of dependencies
        TODO [PRO]: Add 15+ tests for dependency analysis
            TODO [PRO][FEATURE]: Constant folding and evaluation
        TODO [PRO]: Evaluate constant expressions
        TODO [PRO]: Simplify arithmetic operations
        TODO [PRO]: Fold built-in function calls
        TODO [PRO]: Add 15+ tests for folding
            TODO [PRO][FEATURE]: Dead code detection
        TODO [PRO]: Find unreachable statements
        TODO [PRO]: Detect unused variables
        TODO [PRO]: Identify dead branches
        TODO [PRO]: Add 15+ tests for dead code
            TODO [PRO][FEATURE]: Find similar nodes
        TODO [PRO]: Compare AST structures
        TODO [PRO]: Calculate similarity score
        TODO [PRO]: Support pattern-based matching
        TODO [PRO]: Add 12+ tests for similarity
            TODO [PRO][FEATURE]: Remove comments preserving line numbers
        TODO [PRO]: Strip comment text
        TODO [PRO]: Replace with whitespace
        TODO [PRO]: Maintain line count
        TODO [PRO]: Add 12+ tests for comment removal
    ====================================================================
    TIER 3: ENTERPRISE (Commercial - Lower Priority)
    ====================================================================
            TODO [ENTERPRISE][FEATURE]: Data flow analysis utilities
        TODO [ENTERPRISE]: Compute reaching definitions
        TODO [ENTERPRISE]: Calculate liveness sets
        TODO [ENTERPRISE]: Build use-def chains
        TODO [ENTERPRISE]: Add 15+ tests for data flow
            TODO [ENTERPRISE][FEATURE]: Control flow graph generation
        TODO [ENTERPRISE]: Build CFG from AST
        TODO [ENTERPRISE]: Identify basic blocks
        TODO [ENTERPRISE]: Handle loops and branches
        TODO [ENTERPRISE]: Add 15+ tests for CFG
            TODO [ENTERPRISE][FEATURE]: Advanced traversal strategies
        TODO [ENTERPRISE]: Depth-first and breadth-first
        TODO [ENTERPRISE]: Topological ordering
        TODO [ENTERPRISE]: Reverse post-order
        TODO [ENTERPRISE]: Add 12+ tests for traversal
            TODO [ENTERPRISE][FEATURE]: Semantic code comparison
        TODO [ENTERPRISE]: Compare semantics (not syntax)
        TODO [ENTERPRISE]: Identify refactored code
        TODO [ENTERPRISE]: Match equivalent structures
        TODO [ENTERPRISE]: Add 12+ tests for semantic comparison    """


    @staticmethod
    def get_all_names(tree: ast.AST) -> set[str]:
        """Get all names used in the AST."""
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
        return names

    @staticmethod
    def get_function_info(node: ast.FunctionDef) -> dict[str, Any]:
        """Get detailed information about a function."""
        return {
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "defaults": [ast.unparse(d) for d in node.args.defaults],
            "kwonlyargs": [arg.arg for arg in node.args.kwonlyargs],
            "vararg": node.args.vararg.arg if node.args.vararg else None,
            "kwarg": node.args.kwarg.arg if node.args.kwarg else None,
            "decorators": [ast.unparse(d) for d in node.decorator_list],
            "returns": ast.unparse(node.returns) if node.returns else None,
            "docstring": ast.get_docstring(node),
            "line_number": node.lineno,
            "end_line_number": node.end_lineno if hasattr(node, "end_lineno") else None,
        }

    @staticmethod
    def find_all(tree: ast.AST, condition: Callable[[ast.AST], bool]) -> list[ast.AST]:
        """Find all nodes matching a condition."""
        return [node for node in ast.walk(tree) if condition(node)]

    @staticmethod
    def get_node_source(node: ast.AST, source_lines: list[str]) -> str:
        """Get the source code for a node."""
        lineno = getattr(node, "lineno", None)
        end_lineno = getattr(node, "end_lineno", None)
        if lineno is not None and end_lineno is not None:
            return "\n".join(source_lines[lineno - 1 : end_lineno])
        return ast.unparse(node)

    @staticmethod
    def analyze_dependencies(tree: ast.AST) -> dict[str, set[str]]:
        """Analyze variable dependencies in the code."""
        deps = defaultdict(set)

        class DependencyVisitor(ast.NodeVisitor):
            def visit_Assign(self, node):
                # Get variables being assigned to
                targets = set()
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        targets.add(target.id)

                # Get variables used in the assignment
                used = set()
                for subnode in ast.walk(node.value):
                    if isinstance(subnode, ast.Name):
                        used.add(subnode.id)

                # Record dependencies
                for target in targets:
                    deps[target].update(used)

                self.generic_visit(node)

        DependencyVisitor().visit(tree)
        return dict(deps)

    @staticmethod
    def format_code(tree: ast.AST) -> str:
        """Format AST as properly indented code."""
        return ast.unparse(tree)

    @classmethod
    def find_similar_nodes(
        cls, tree: ast.AST, pattern: Union[str, ast.AST], threshold: float = 0.8
    ) -> list[ast.AST]:
        """Find nodes similar to a pattern."""
        if isinstance(pattern, str):
            pattern = ast.parse(pattern).body[0]

        similar_nodes = []
        for node in ast.walk(tree):
            if cls.calculate_similarity(node, pattern) >= threshold:
                similar_nodes.append(node)
        return similar_nodes

    @staticmethod
    def calculate_similarity(node1: ast.AST, node2: ast.AST) -> float:
        """Calculate similarity between two AST nodes."""
        # Placeholder for actual similarity calculation logic
        return 1.0 if type(node1) is type(node2) else 0.0

    @staticmethod
    def remove_comments(code: str) -> str:
        """Remove comments while preserving line numbers."""
        result = []
        prev_toktype = tokenize.INDENT
        first_line = True

        tokens = tokenize.generate_tokens(StringIO(code).readline)

        for toktype, ttext, (_slineno, _scol), (_elineno, _ecol), _ltext in tokens:
            if toktype == tokenize.COMMENT:
                continue
            elif toktype == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
                    result.append(" ")
                result.append(ttext)
            elif toktype == tokenize.NEWLINE or toktype == tokenize.INDENT:
                result.append(ttext)
            elif toktype == tokenize.DEDENT:
                pass
            else:
                if not first_line and prev_toktype != tokenize.INDENT:
                    result.append(" ")
                result.append(ttext)
            prev_toktype = toktype
            first_line = False

        return "".join(result)

    @staticmethod
    def traverse_ast(tree: ast.AST, strategy: str = "depth-first") -> list[ast.AST]:
        """Traverse the AST using the specified strategy."""
        nodes = []
        if strategy == "depth-first":
            nodes = list(ast.walk(tree))
        elif strategy == "breadth-first":
            queue = [tree]
            while queue:
                node = queue.pop(0)
                nodes.append(node)
                queue.extend(ast.iter_child_nodes(node))
        return nodes

    @staticmethod
    def compare_nodes(node1: ast.AST, node2: ast.AST) -> bool:
        """Compare two AST nodes for structural equality."""
        if type(node1) is not type(node2):
            return False
        for field in node1._fields:
            val1 = getattr(node1, field)
            val2 = getattr(node2, field)
            if isinstance(val1, list):
                if not isinstance(val2, list) or len(val1) != len(val2):
                    return False
                for v1, v2 in zip(val1, val2):
                    if not ASTUtils.compare_nodes(v1, v2):
                        return False
            elif isinstance(val1, ast.AST):
                if not ASTUtils.compare_nodes(val1, val2):
                    return False
            elif val1 != val2:
                return False
        return True

    @staticmethod
    def generate_docstring(node: ast.FunctionDef) -> str:
        """Generate a docstring for a function from its AST node."""
        signature = ASTUtils.extract_function_signature(node)
        docstring = f'"""{signature}\n\n'
        docstring += "Args:\n"
        for arg in node.args.args:
            docstring += f"  {arg.arg}: \n"
        if node.returns:
            docstring += f"\nReturns:\n  {ast.unparse(node.returns)}\n"
        docstring += '"""'
        return docstring

    @staticmethod
    def extract_function_signature(node: ast.FunctionDef) -> str:
        """Extract the signature of a function from its AST node."""
        args = [arg.arg for arg in node.args.args]
        defaults = [ast.unparse(d) for d in node.args.defaults]
        args_with_defaults = args[: len(args) - len(defaults)] + [
            f"{a}={d}" for a, d in zip(args[len(args) - len(defaults) :], defaults)
        ]
        return f"def {node.name}({', '.join(args_with_defaults)})"


# Standalone utility functions for convenience
def is_constant(node: ast.AST) -> bool:
    """Check if a node represents a constant value."""
    return isinstance(
        node, (ast.Constant, ast.Num, ast.Str, ast.Bytes, ast.NameConstant)
    )


def get_node_type(node: ast.AST) -> str:
    """Get the type name of an AST node."""
    return type(node).__name__


def get_all_names(tree: ast.AST) -> set[str]:
    """Get all names used in the AST."""
    return ASTUtils.get_all_names(tree)
