"""
Normalizers - Convert language-specific AST/CST to Unified IR.

Each normalizer converts its language's native parse tree to our Unified IR.
The IR preserves source_language for semantic dispatch.

Available Normalizers:
    - PythonNormalizer: Python ast.* -> IR
    - JavaNormalizer: Java tree-sitter CST -> IR (v2.0.0)
    - JavaScriptNormalizer: JavaScript tree-sitter CST -> IR (v0.4.0)
    - TypeScriptNormalizer: TypeScript tree-sitter CST -> IR (v2.0.0)

Base Classes:
    - BaseNormalizer: Abstract interface for all normalizers
    - TreeSitterVisitor: Base class for tree-sitter based normalizers

TODO ITEMS:

COMMUNITY TIER (Basic Normalizer Integration):
1. TODO: Export all language-specific normalizers
2. TODO: Create normalizer factory function
3. TODO: Support auto-detection of source language
4. TODO: Implement error handling for missing dependencies
5. TODO: Document normalizer usage patterns
6. TODO: Create basic normalizer tests
7. TODO: Support version tracking for normalizers
8. TODO: Implement fallback for unsupported languages
9. TODO: Create normalizer performance benchmarks
10. TODO: Document IR compatibility across languages

PRO TIER (Advanced Normalizer Features):
11. TODO: Implement normalizer caching layer
12. TODO: Support incremental normalization
13. TODO: Add normalizer composition for dialects
14. TODO: Implement custom normalizer registration
15. TODO: Support normalizer plugins
16. TODO: Add performance profiling per normalizer
17. TODO: Implement distributed normalization
18. TODO: Support streaming normalization for large files
19. TODO: Add metadata preservation layer
20. TODO: Implement normalizer validation framework

ENTERPRISE TIER (Advanced Analysis & Optimization):
21. TODO: Implement ML-based normalizer selection
22. TODO: Support polyglot project-wide normalization
23. TODO: Add cross-language type inference
24. TODO: Implement adaptive normalization strategies
25. TODO: Support federated normalizer services
26. TODO: Add encrypted IR generation
27. TODO: Implement AI-driven normalization optimization
28. TODO: Support quantum-safe normalizer signing
29. TODO: Create ML-based dialect detection
30. TODO: Implement predictive caching for normalization
"""

from .base import BaseNormalizer
from .java_normalizer import \
    JavaNormalizer  # [20251215_FEATURE] Export Java normalizer
from .python_normalizer import PythonNormalizer
from .tree_sitter_visitor import TreeSitterVisitor, VisitorContext

# JavaScript normalizer requires tree-sitter, import conditionally
try:
    from .javascript_normalizer import JavaScriptNormalizer

    _HAS_JAVASCRIPT = True
except ImportError:
    JavaScriptNormalizer = None
    _HAS_JAVASCRIPT = False

__all__ = [
    "BaseNormalizer",
    "PythonNormalizer",
    "JavaNormalizer",
    "TreeSitterVisitor",
    "VisitorContext",
]

if _HAS_JAVASCRIPT:
    __all__.append("JavaScriptNormalizer")
