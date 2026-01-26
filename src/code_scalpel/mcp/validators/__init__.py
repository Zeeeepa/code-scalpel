"""Validation engine for code analysis.

This package exports validation components used for pre-execution checks:
- Symbol extraction with scope tracking
- Weighted fuzzy matching for error suggestions
- Semantic and structural validators
"""

from code_scalpel.mcp.validators.core import (
    ScopedSymbol,
    ValidationError,
    ScopeTrackingVisitor,
    SymbolExtractor,
    SemanticValidator,
    StructuralValidator,
    get_symbol_validator,
)
from code_scalpel.mcp.validators.weighted_scorer import (
    ScoredCandidate,
    WeightedSymbolMatcher,
)

__all__ = [
    # From core
    "ScopedSymbol",
    "ValidationError",
    "ScopeTrackingVisitor",
    "SymbolExtractor",
    "SemanticValidator",
    "StructuralValidator",
    "get_symbol_validator",
    # From weighted_scorer
    "ScoredCandidate",
    "WeightedSymbolMatcher",
]
