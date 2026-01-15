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
"""

# TODO [COMMUNITY] Export all language-specific normalizers
# TODO [COMMUNITY] Create normalizer factory function
# TODO [COMMUNITY] Support auto-detection of source language
# TODO [COMMUNITY] Implement error handling for missing dependencies
# TODO [COMMUNITY] Document normalizer usage patterns
# TODO [COMMUNITY] Create basic normalizer tests
# TODO [COMMUNITY] Support version tracking for normalizers
# TODO [COMMUNITY] Implement fallback for unsupported languages
# TODO [COMMUNITY] Create normalizer performance benchmarks
# TODO [COMMUNITY] Document IR compatibility across languages
# TODO [PRO] Implement normalizer caching layer
# TODO [PRO] Support incremental normalization
# TODO [PRO] Add normalizer composition for dialects
# TODO [PRO] Implement custom normalizer registration
# TODO [PRO] Support normalizer plugins
# TODO [PRO] Add performance profiling per normalizer
# TODO [PRO] Implement distributed normalization
# TODO [PRO] Support streaming normalization for large files
# TODO [PRO] Add metadata preservation layer
# TODO [PRO] Implement normalizer validation framework
# TODO [ENTERPRISE] Implement ML-based normalizer selection
# TODO [ENTERPRISE] Support polyglot project-wide normalization
# TODO [ENTERPRISE] Add cross-language type inference
# TODO [ENTERPRISE] Implement adaptive normalization strategies
# TODO [ENTERPRISE] Support federated normalizer services
# TODO [ENTERPRISE] Add encrypted IR generation
# TODO [ENTERPRISE] Implement AI-driven normalization optimization
# TODO [ENTERPRISE] Support quantum-safe normalizer signing
# TODO [ENTERPRISE] Create ML-based dialect detection
# TODO [ENTERPRISE] Implement predictive caching for normalization

from .base import BaseNormalizer
from .java_normalizer import JavaNormalizer  # [20251215_FEATURE] Export Java normalizer
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
