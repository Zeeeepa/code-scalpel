"""Project Scanner - Pure graph building from project directory.

[20260126_PHASE1] Lean scanner that traverses project directory and builds
UniversalGraph with symbol information from Python files.

This is library code with NO knowledge of:
- MCP protocols or tiers
- Network calls or external services
- LLM integration

It accepts pure config parameters:
- max_files: Maximum files to scan
- max_depth: Maximum directory depth to traverse

Usage:
    from code_scalpel.lib_scalpel.graph_engine.scanner import ProjectScanner

    scanner = ProjectScanner("/path/to/project", max_files=50, max_depth=2)
    graph = scanner.scan()
"""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import List, Set

from .universal_graph import GraphEdge, GraphNode, UniversalGraph
from .node_id import UniversalNodeID, NodeType
from .confidence import EdgeType
from code_scalpel.lib_scalpel.visitors.symbol_extractor import SymbolExtractor

logger = logging.getLogger(__name__)


# Default directories to exclude from scanning
DEFAULT_EXCLUDE_DIRS: Set[str] = {
    ".git",
    ".hg",
    ".svn",
    "venv",
    ".venv",
    "env",
    ".env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
    "egg-info",
    ".egg-info",
    ".tox",
    ".nox",
    "htmlcov",
    "site-packages",
}


class ProjectScanner:
    """Lean project scanner for building UniversalGraph from Python files.

    Traverses project directory up to configured limits and extracts:
    - File-level information (location, size)
    - Class and function definitions
    - Import relationships
    - Symbol dependencies

    All data is stored in UniversalGraph nodes and edges with confidence scores.
    """

    def __init__(
        self,
        root_dir: str | Path,
        max_files: int = 50,
        max_depth: int = 2,
        extract_symbols: bool = True,
    ):
        """Initialize the project scanner.

        Args:
            root_dir: Root directory of the project
            max_files: Maximum number of files to scan
            max_depth: Maximum directory depth to traverse
            extract_symbols: Whether to extract symbol info (default: True)
        """
        self.root_dir = Path(root_dir).resolve()
        self.max_files = max_files
        self.max_depth = max_depth
        self.extract_symbols = extract_symbols
        self.scanned_files: int = 0
        self.errors: List[tuple[str, str]] = []
        self.symbol_extractor = SymbolExtractor() if extract_symbols else None

    def scan(self) -> UniversalGraph:
        """Scan project and build UniversalGraph.

        Returns:
            UniversalGraph with nodes and edges from scanned files

        Raises:
            ValueError: If root_dir doesn't exist
        """
        if not self.root_dir.exists():
            raise ValueError(f"Root directory does not exist: {self.root_dir}")

        logger.info(
            f"[ProjectScanner] Starting scan: root={self.root_dir}, "
            f"max_files={self.max_files}, max_depth={self.max_depth}"
        )

        graph = UniversalGraph()

        # Traverse directory and collect Python files
        python_files = self._collect_python_files()
        logger.debug(f"[ProjectScanner] Found {len(python_files)} Python files")

        # Analyze each file and add to graph
        for file_path in python_files:
            if self.scanned_files >= self.max_files:
                logger.debug(
                    f"[ProjectScanner] Reached max_files limit ({self.max_files})"
                )
                break

            self._analyze_file(file_path, graph)
            self.scanned_files += 1

        # Set graph metadata
        graph.metadata = {
            "root_dir": str(self.root_dir),
            "scanned_files": self.scanned_files,
            "max_files_limit": self.max_files,
            "max_depth_limit": self.max_depth,
            "errors": len(self.errors),
        }

        logger.info(
            f"[ProjectScanner] Scan complete: "
            f"nodes={len(graph.nodes)}, edges={len(graph.edges)}, errors={len(self.errors)}"
        )

        return graph

    def _collect_python_files(self) -> List[Path]:
        """Collect Python files from project directory.

        Respects max_depth limit and excludes default directories.

        Returns:
            List of Path objects for Python files
        """
        python_files: List[Path] = []

        def _walk(directory: Path, current_depth: int) -> None:
            """Recursive directory walker with depth limit."""
            if current_depth > self.max_depth:
                return

            try:
                for item in directory.iterdir():
                    if item.name.startswith("."):
                        continue

                    if item.is_dir():
                        if item.name not in DEFAULT_EXCLUDE_DIRS:
                            _walk(item, current_depth + 1)
                    elif item.suffix == ".py" and item.is_file():
                        python_files.append(item)
                        if len(python_files) >= self.max_files:
                            return

            except (PermissionError, OSError) as e:
                logger.warning(f"[ProjectScanner] Error accessing {directory}: {e}")

        _walk(self.root_dir, 0)
        return python_files

    def _analyze_file(self, file_path: Path, graph: UniversalGraph) -> None:
        """Analyze a single Python file and add nodes/edges to graph.

        Args:
            file_path: Path to Python file
            graph: UniversalGraph to add nodes/edges to
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            file_path_relative = file_path.relative_to(self.root_dir)

            # Add file node
            file_node_id = UniversalNodeID(
                language="python",
                module=str(file_path_relative).replace("/", ".").replace(".py", ""),
                node_type=NodeType.MODULE,
                name=file_path.name,
                file=str(file_path_relative),
                line=1,
            )
            file_node = GraphNode(
                id=file_node_id,
                metadata={
                    "size": len(content),
                    "lines": len(content.split("\n")),
                },
            )
            graph.add_node(file_node)

            # Extract classes and functions
            self._extract_symbols(tree, file_path_relative, graph, str(file_node_id))
            # Extract imports and dependencies
            self._extract_imports(tree, file_path_relative, graph, str(file_node_id))

            # Extract rich symbol information if enabled
            if self.extract_symbols and self.symbol_extractor:
                symbol_table = self.symbol_extractor.extract_from_file(str(file_path))
                self._enrich_with_symbols(
                    symbol_table, file_path_relative, graph, str(file_node_id)
                )

            logger.debug(
                f"[ProjectScanner] Analyzed {file_path_relative}: "
                f"nodes added={len(graph.nodes) - (self.scanned_files)}"
            )

        except SyntaxError as e:
            error_msg = f"Syntax error in {file_path}: {e}"
            logger.warning(f"[ProjectScanner] {error_msg}")
            self.errors.append((str(file_path), error_msg))
        except Exception as e:
            error_msg = f"Error analyzing {file_path}: {e}"
            logger.warning(f"[ProjectScanner] {error_msg}")
            self.errors.append((str(file_path), error_msg))

    def _extract_symbols(
        self, tree: ast.AST, file_path: Path, graph: UniversalGraph, file_node_id: str
    ) -> None:
        """Extract class and function definitions from AST.

        Args:
            tree: AST tree
            file_path: Relative file path
            graph: UniversalGraph to add nodes to
            file_node_id: ID of file node for relationships
        """
        module_name = str(file_path).replace("/", ".").replace(".py", "")

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_node_id = UniversalNodeID(
                    language="python",
                    module=module_name,
                    node_type=NodeType.CLASS,
                    name=node.name,
                    file=str(file_path),
                    line=node.lineno,
                )
                class_node = GraphNode(
                    id=class_node_id,
                    metadata={"methods": []},
                )
                graph.add_node(class_node)

                # Add edge from file to class
                edge = GraphEdge(
                    from_id=file_node_id,
                    to_id=str(class_node_id),
                    edge_type=EdgeType.TYPE_ANNOTATION,
                    confidence=1.0,
                    evidence="Class defined in file",
                )
                graph.add_edge(edge)

                # Extract methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_node_id = UniversalNodeID(
                            language="python",
                            module=module_name,
                            node_type=NodeType.METHOD,
                            name=item.name,
                            method=node.name,
                            file=str(file_path),
                            line=item.lineno,
                        )
                        method_node = GraphNode(id=method_node_id)
                        graph.add_node(method_node)

                        # Add edge from class to method
                        method_edge = GraphEdge(
                            from_id=str(class_node_id),
                            to_id=str(method_node_id),
                            edge_type=EdgeType.TYPE_ANNOTATION,
                            confidence=1.0,
                            evidence="Method defined in class",
                        )
                        graph.add_edge(method_edge)

            elif isinstance(node, ast.FunctionDef):
                # Only process top-level functions (not in classes)
                if isinstance(tree, ast.Module):
                    func_node_id = UniversalNodeID(
                        language="python",
                        module=module_name,
                        node_type=NodeType.FUNCTION,
                        name=node.name,
                        file=str(file_path),
                        line=node.lineno,
                    )
                    func_node = GraphNode(id=func_node_id)
                    graph.add_node(func_node)

                    # Add edge from file to function
                    edge = GraphEdge(
                        from_id=file_node_id,
                        to_id=str(func_node_id),
                        edge_type=EdgeType.TYPE_ANNOTATION,
                        confidence=1.0,
                        evidence="Function defined in file",
                    )
                    graph.add_edge(edge)

    def _extract_imports(
        self, tree: ast.AST, file_path: Path, graph: UniversalGraph, file_node_id: str
    ) -> None:
        """Extract import statements and build dependency edges.

        Args:
            tree: AST tree
            file_path: Relative file path
            graph: UniversalGraph to add edges to
            file_node_id: ID of file node for relationships
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Import X
                    imported_module = alias.name.split(".")[0]
                    imported_node_id = UniversalNodeID(
                        language="python",
                        module=imported_module,
                        node_type=NodeType.MODULE,
                        name=alias.name,
                        file=str(file_path),
                        line=node.lineno,
                    )
                    imported_node = GraphNode(id=imported_node_id)
                    graph.add_node(imported_node)

                    edge = GraphEdge(
                        from_id=file_node_id,
                        to_id=str(imported_node_id),
                        edge_type=EdgeType.IMPORT_STATEMENT,
                        confidence=1.0,
                        evidence=f"Import statement: {alias.name}",
                    )
                    graph.add_edge(edge)

            elif isinstance(node, ast.ImportFrom):
                # From X import Y
                if node.module:
                    imported_module = node.module.split(".")[0]
                    imported_node_id = UniversalNodeID(
                        language="python",
                        module=imported_module,
                        node_type=NodeType.MODULE,
                        name=node.module,
                        file=str(file_path),
                        line=node.lineno,
                    )
                    imported_node = GraphNode(id=imported_node_id)
                    graph.add_node(imported_node)

                    edge = GraphEdge(
                        from_id=file_node_id,
                        to_id=str(imported_node_id),
                        edge_type=EdgeType.IMPORT_STATEMENT,
                        confidence=1.0,
                        evidence=f"Import from: {node.module}",
                    )
                    graph.add_edge(edge)

    def _enrich_with_symbols(
        self,
        symbol_table,
        file_path: Path,
        graph: UniversalGraph,
        file_node_id: str,
    ) -> None:
        """Enrich graph nodes with detailed symbol information.

        Uses SymbolExtractor to add function signatures, parameters, and metadata.

        Args:
            symbol_table: SymbolTable from SymbolExtractor
            file_path: Relative file path
            graph: UniversalGraph to update
            file_node_id: ID of file node
        """
        module_name = str(file_path).replace("/", ".").replace(".py", "")

        # Enrich function nodes with signature info
        for func_sig in symbol_table.functions:
            func_node_id = UniversalNodeID(
                language="python",
                module=module_name,
                node_type=NodeType.FUNCTION,
                name=func_sig.name,
                file=str(file_path),
                line=func_sig.line,
            )

            # Find and update existing node or create new one
            existing_node = graph.get_node(str(func_node_id))
            if existing_node:
                # Enrich metadata with signature details
                existing_node.metadata.update(
                    {
                        "parameters": func_sig.params,
                        "return_type": func_sig.returns,
                        "docstring": func_sig.docstring,
                        "decorators": func_sig.decorators,
                    }
                )
            else:
                # Create new enriched node
                func_node = GraphNode(
                    id=func_node_id,
                    metadata={
                        "parameters": func_sig.params,
                        "return_type": func_sig.returns,
                        "docstring": func_sig.docstring,
                        "decorators": func_sig.decorators,
                        "signature": func_sig.signature,
                    },
                )
                graph.add_node(func_node)
                # Add edge from file to function
                edge = GraphEdge(
                    from_id=file_node_id,
                    to_id=str(func_node_id),
                    edge_type=EdgeType.TYPE_ANNOTATION,
                    confidence=1.0,
                    evidence="Function defined in file",
                )
                graph.add_edge(edge)

        # Enrich class nodes with method and inheritance info
        for class_sig in symbol_table.classes:
            class_node_id = UniversalNodeID(
                language="python",
                module=module_name,
                node_type=NodeType.CLASS,
                name=class_sig.name,
                file=str(file_path),
                line=class_sig.line,
            )

            # Find and update existing node
            existing_node = graph.get_node(str(class_node_id))
            if existing_node:
                # Enrich with class metadata
                existing_node.metadata.update(
                    {
                        "base_classes": class_sig.bases,
                        "methods": [m.name for m in class_sig.methods],
                        "properties": class_sig.properties,
                        "docstring": class_sig.docstring,
                    }
                )
            else:
                # Create new enriched node
                class_node = GraphNode(
                    id=class_node_id,
                    metadata={
                        "base_classes": class_sig.bases,
                        "methods": [m.name for m in class_sig.methods],
                        "properties": class_sig.properties,
                        "docstring": class_sig.docstring,
                    },
                )
                graph.add_node(class_node)
                # Add edge from file to class
                edge = GraphEdge(
                    from_id=file_node_id,
                    to_id=str(class_node_id),
                    edge_type=EdgeType.TYPE_ANNOTATION,
                    confidence=1.0,
                    evidence="Class defined in file",
                )
                graph.add_edge(edge)

            # Add method nodes with signatures
            for method_sig in class_sig.methods:
                method_node_id = UniversalNodeID(
                    language="python",
                    module=module_name,
                    node_type=NodeType.METHOD,
                    name=method_sig.name,
                    method=class_sig.name,
                    file=str(file_path),
                    line=method_sig.line,
                )

                existing_node = graph.get_node(str(method_node_id))
                if existing_node:
                    # Enrich with method signature
                    existing_node.metadata.update(
                        {
                            "parameters": method_sig.params,
                            "return_type": method_sig.returns,
                            "docstring": method_sig.docstring,
                        }
                    )
                else:
                    # Create new method node
                    method_node = GraphNode(
                        id=method_node_id,
                        metadata={
                            "parameters": method_sig.params,
                            "return_type": method_sig.returns,
                            "docstring": method_sig.docstring,
                            "signature": method_sig.signature,
                        },
                    )
                    graph.add_node(method_node)
                    # Add edge from class to method
                    edge = GraphEdge(
                        from_id=str(class_node_id),
                        to_id=str(method_node_id),
                        edge_type=EdgeType.TYPE_ANNOTATION,
                        confidence=1.0,
                        evidence="Method defined in class",
                    )
                    graph.add_edge(edge)

        # Add import information to graph
        for import_stmt in symbol_table.imports:
            # Create edge for each import dependency
            imported_node_id = UniversalNodeID(
                language="python",
                module=import_stmt.module,
                node_type=NodeType.MODULE,
                name=import_stmt.module,
                file=str(file_path),
                line=import_stmt.line,
            )

            # Find or create import node
            import_node = graph.get_node(str(imported_node_id))
            if not import_node:
                import_node = GraphNode(id=imported_node_id)
                graph.add_node(import_node)

            # Create import edge with details
            edge = GraphEdge(
                from_id=file_node_id,
                to_id=str(imported_node_id),
                edge_type=EdgeType.IMPORT_STATEMENT,
                confidence=1.0,
                evidence=f"Import: {import_stmt.module} (line {import_stmt.line})",
                metadata={
                    "import_type": "from" if import_stmt.alias else "import",
                    "symbols": import_stmt.symbols,
                },
            )
            graph.add_edge(edge)

        # Enrich class nodes with method and inheritance info
        for class_sig in symbol_table.classes:
            class_node_id = UniversalNodeID(
                language="python",
                module=module_name,
                node_type=NodeType.CLASS,
                name=class_sig.name,
                file=str(file_path),
                line=class_sig.line,
            )

            # Find and update existing node
            existing_node = graph.get_node(str(class_node_id))
            if existing_node:
                # Enrich with class metadata
                existing_node.metadata.update(
                    {
                        "base_classes": class_sig.base_classes,
                        "methods": [m.name for m in class_sig.methods],
                        "docstring": class_sig.docstring,
                    }
                )
            else:
                # Create new enriched node
                class_node = GraphNode(
                    id=class_node_id,
                    metadata={
                        "base_classes": class_sig.base_classes,
                        "methods": [m.name for m in class_sig.methods],
                        "docstring": class_sig.docstring,
                    },
                )
                graph.add_node(class_node)
                # Add edge from file to class
                edge = GraphEdge(
                    from_id=file_node_id,
                    to_id=str(class_node_id),
                    edge_type=EdgeType.TYPE_ANNOTATION,
                    confidence=1.0,
                    evidence="Class defined in file",
                )
                graph.add_edge(edge)

            # Add method nodes with signatures
            for method_sig in class_sig.methods:
                method_node_id = UniversalNodeID(
                    language="python",
                    module=module_name,
                    node_type=NodeType.METHOD,
                    name=method_sig.name,
                    method=class_sig.name,
                    file=str(file_path),
                    line=method_sig.line,
                )

                existing_node = graph.get_node(str(method_node_id))
                if existing_node:
                    # Enrich with method signature
                    existing_node.metadata.update(
                        {
                            "parameters": method_sig.parameters,
                            "return_type": method_sig.return_type,
                            "docstring": method_sig.docstring,
                        }
                    )
                else:
                    # Create new method node
                    method_node = GraphNode(
                        id=method_node_id,
                        metadata={
                            "parameters": method_sig.parameters,
                            "return_type": method_sig.return_type,
                            "docstring": method_sig.docstring,
                            "signature": str(method_sig),
                        },
                    )
                    graph.add_node(method_node)
                    # Add edge from class to method
                    edge = GraphEdge(
                        from_id=str(class_node_id),
                        to_id=str(method_node_id),
                        edge_type=EdgeType.TYPE_ANNOTATION,
                        confidence=1.0,
                        evidence="Method defined in class",
                    )
                    graph.add_edge(edge)

        # Add import information to graph
        for import_stmt in symbol_table.imports:
            # Create edge for each import dependency
            imported_node_id = UniversalNodeID(
                language="python",
                module=import_stmt.module,
                node_type=NodeType.MODULE,
                name=import_stmt.module,
                file=str(file_path),
                line=import_stmt.line,
            )

            # Find or create import node
            import_node = graph.get_node(str(imported_node_id))
            if not import_node:
                import_node = GraphNode(id=imported_node_id)
                graph.add_node(import_node)

            # Create import edge with details
            edge = GraphEdge(
                from_id=file_node_id,
                to_id=str(imported_node_id),
                edge_type=EdgeType.IMPORT_STATEMENT,
                confidence=1.0,
                evidence=f"Import: {import_stmt.module} (line {import_stmt.line})",
                metadata={
                    "import_type": "from" if import_stmt.is_from else "import",
                    "items": import_stmt.items,
                },
            )
            graph.add_edge(edge)
