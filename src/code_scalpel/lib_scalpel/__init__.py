"""lib_scalpel - The Pure Logic Engine.

[20260126_LIB_SCALPEL] Core static analysis library with zero MCP/LLM knowledge.

This is the "brain" of Code Scalpel: pure Python logic for:
- Graph construction (UniversalGraph)
- Symbol extraction (SymbolExtractor)
- Project scanning (ProjectScanner)
- Constraint analysis (ConstraintAnalyzer)
- Markdown spec generation (generate_markdown_spec)

You can use lib_scalpel completely independently of MCP or LLMs.

Example:
    >>> from code_scalpel.lib_scalpel import OraclePipeline
    >>> pipeline = OraclePipeline(repo_root=".", max_files=50, max_depth=2)
    >>> spec = pipeline.generate_constraint_spec("src/auth.py", "Add JWT")
    >>> print(spec)
    # 🔮 ORACLE SPEC...
"""

from .graph_engine import UniversalGraph, GraphNode, GraphEdge, ProjectScanner
from .visitors import SymbolExtractor
from .analysis import ConstraintAnalyzer, generate_markdown_spec
from .oracle_pipeline import OraclePipeline

__all__ = [
    "UniversalGraph",
    "GraphNode",
    "GraphEdge",
    "ProjectScanner",
    "SymbolExtractor",
    "ConstraintAnalyzer",
    "generate_markdown_spec",
    "OraclePipeline",
]
