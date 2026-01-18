"""
TypeScript/JavaScript Parser Module.

[20251224_REFACTOR] Migrated from polyglot/typescript/ to code_parsers/typescript_parsers/
for architectural consistency with {lang}_parsers/ naming convention.

This module provides AST parsing and analysis for TypeScript and JavaScript
using tree-sitter for parsing and a normalized IR for cross-language analysis.

Architecture:
    TypeScript/JS Source
           ↓
    tree-sitter-typescript (Native Parser)
           ↓
    ESTree-compatible AST
           ↓
    Code Scalpel Normalized IR  ← Same IR as Python
           ↓
    PDG/Symbolic/Security Analysis (Shared)

Dependencies:
    - tree-sitter>=0.21.0 (optional, fallback to regex)
    - tree-sitter-typescript>=0.21.0 (optional)
    - tree-sitter-javascript>=0.21.0 (optional)

Exports:
    - TypeScriptParser: Low-level AST parser
    - TypeScriptAnalyzer: Structural analysis and metrics
    - TypeNarrowing: Control-flow type narrowing analysis
    - DecoratorAnalyzer: TypeScript decorator extraction
    - AliasResolver: Module alias resolution (tsconfig, webpack, vite)
    - TSX Utilities: React component detection and JSX analysis


COMMUNITY TIER (Core Functionality):
# ============================================================================
# [P0_CRITICAL] Complete tree-sitter integration
# Status: STUB - Fallback regex parsing in place
#
#    - Initialize tree-sitter with TypeScript language
#    - Handle parse errors gracefully
#    - Test count: 25 tests (initialization, error handling, language selection)
#
#    - Map tree-sitter nodes to ESTree format
#    - Handle TypeScript-specific nodes (interface, type alias)
#    - Test count: 30 tests (node mapping, edge cases, TS extensions)
#
#    - Extract function declarations, expressions, arrow functions
#    - Extract class declarations with members
#    - Test count: 20 tests (extraction accuracy, nested structures)
#
# [P1_HIGH] Core parsing features
#    - Detect named imports, default imports, namespace imports
#    - Track export statements and re-exports
#    - Test count: 20 tests (import types, circular dependencies)
#
#    - Parse arrow function expressions
#    - Detect implicit returns
#    - Test count: 15 tests (syntax variations, this binding)
#
#    - Parse template literals with expressions
#    - Track interpolation points for taint analysis
#    - Test count: 15 tests (simple, tagged, nested)
#
# [P2_MEDIUM] Extended core features
#    - Detect async functions and methods
#    - Track await expressions
#    - Test count: 15 tests (async patterns, error handling)
#
#    - Graceful degradation on syntax errors
#    - Partial AST recovery
#    - Test count: 15 tests (malformed code, recovery quality)
#
#    - Unit tests for all parser components
#    - Integration tests for complex code
#    - Test count: 50 tests (coverage target: 95%)
#
#     - API reference documentation
#     - Usage examples for common scenarios
#     - Test count: 10 tests (doc examples validation)
# ============================================================================

PRO TIER (Enhanced Features):
# ============================================================================
# [P1_HIGH] Type system analysis
#     - Parse generic type parameters
#     - Track generic constraints
#     - Test count: 25 tests (generic patterns, constraints)
#
#     - Parse union types (A | B)
#     - Track discriminated unions
#     - Test count: 20 tests (union patterns, narrowing)
#
#     - Parse extends clauses
#     - Build interface hierarchy
#     - Test count: 15 tests (inheritance chains)
#
# [P2_MEDIUM] Advanced type features
#     - Resolve type aliases to base types
#     - Handle recursive types
#     - Test count: 20 tests (alias chains, recursion limits)
#
#     - Resolve node_modules paths
#     - Handle TypeScript project references
#     - Test count: 25 tests (module patterns, monorepos)
#
#     - Parse decorator metadata
#     - Extract decorator arguments
#     - Test count: 20 tests (decorator patterns, NestJS)
#
# [P3_LOW] Advanced analysis
#     - Integrate with type_narrowing.py
#     - Track narrowed types through branches
#     - Test count: 20 tests (narrowing patterns)
#
#     - Basic type inference
#     - Type compatibility checking
#     - Test count: 25 tests (type system edge cases)
#
#     - Build CFG from TypeScript AST
#     - Track unreachable code
#     - Test count: 20 tests (control flow patterns)
#
#     - Track data dependencies
#     - Support taint analysis
#     - Test count: 25 tests (dataflow accuracy)
# ============================================================================

ENTERPRISE TIER (Advanced Capabilities):
# ============================================================================
# [P2_MEDIUM] AI/ML integration
#     - Train on large TypeScript codebases
#     - Suggest missing type annotations
#     - Test count: 15 tests (inference quality)
#
#     - Parallel parsing across workers
#     - Incremental update support
#     - Test count: 20 tests (scalability, correctness)
#
#     - Context-aware type suggestions
#     - Integration with LLM providers
#     - Test count: 10 tests (suggestion quality)
#
# [P3_LOW] Enterprise governance
#     - Immutable type evolution history
#     - Cross-organization type sharing
#     - Test count: 10 tests (audit integrity)
#
#     - Post-quantum cryptographic hashing
#     - Hash-based code signatures
#     - Test count: 5 tests (hash properties)
#
#     - Type policy enforcement
#     - Compliance reporting
#     - Test count: 15 tests (governance rules)
#
# [P4_LOW] Future research
#     - SOC2 type documentation requirements
#     - GDPR PII type tracking
#     - Test count: 10 tests (compliance rules)
#
#     - Cross-repo type sharing
#     - Type version negotiation
#     - Test count: 10 tests (federation protocols)
#
#     - Handle JS dynamic typing in Z3
#     - Type coercion modeling
#     - Test count: 20 tests (symbolic accuracy)
#
#     - Quantum circuit type checking
#     - Future research placeholder
#     - Test count: 5 tests (quantum patterns)
# ============================================================================

TOTAL ESTIMATED TESTS: 570 tests
"""

from .alias_resolver import AliasResolver, create_alias_resolver
from .analyzer import (
    NormalizedClass,
    NormalizedFunction,
    TSAnalysisResult,
    TypeScriptAnalyzer,
    normalize_typescript_class,
    normalize_typescript_function,
)
from .decorator_analyzer import (
    SECURITY_SINK_DECORATORS,
    DecoratorAnalyzer,
    extract_decorators_from_code,
)

# [20251224_REFACTOR] Updated imports for new location
from .parser import Decorator, TSNode, TSNodeType, TSParseResult, TypeScriptParser
from .tsx_analyzer import (
    ReactComponentInfo,
    detect_server_directive,
    has_jsx_syntax,
    is_react_component,
    normalize_jsx_syntax,
)
from .type_narrowing import (
    REDUCED_RISK_TYPES,
    SAFE_PRIMITIVE_TYPES,
    BranchState,
    NarrowedType,
    NarrowingResult,
    TypeGuard,
    TypeNarrowing,
    analyze_type_narrowing,
)

__all__ = [
    # Parser
    "TypeScriptParser",
    "TSParseResult",
    "TSNode",
    "TSNodeType",
    "Decorator",
    # Analyzer
    "TypeScriptAnalyzer",
    "TSAnalysisResult",
    "NormalizedFunction",
    "NormalizedClass",
    "normalize_typescript_function",
    "normalize_typescript_class",
    # Type Narrowing
    "TypeNarrowing",
    "NarrowingResult",
    "TypeGuard",
    "BranchState",
    "NarrowedType",
    "analyze_type_narrowing",
    "SAFE_PRIMITIVE_TYPES",
    "REDUCED_RISK_TYPES",
    # Decorator Analyzer
    "DecoratorAnalyzer",
    "extract_decorators_from_code",
    "SECURITY_SINK_DECORATORS",
    # Alias Resolver
    "AliasResolver",
    "create_alias_resolver",
    # TSX Analyzer
    "ReactComponentInfo",
    "detect_server_directive",
    "has_jsx_syntax",
    "is_react_component",
    "normalize_jsx_syntax",
]

__version__ = "1.0.0"
