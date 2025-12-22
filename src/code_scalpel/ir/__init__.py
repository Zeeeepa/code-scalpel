"""
Unified Intermediate Representation (IR) for Multi-Language Analysis.

This module provides a language-agnostic IR that normalizes AST/CST structures
from different languages (Python, JavaScript, TypeScript) into a common format.

Architecture:
    Source Code -> Language Parser -> Normalizer -> Unified IR -> Analysis Engine

Key Design Decisions (RFC-003):
    1. STRUCTURE is normalized (IRBinaryOp, IRAssign, etc.)
    2. SEMANTICS are NOT normalized (delegated to LanguageSemantics)
    3. Source language is preserved for semantic dispatch

Example:
    >>> from code_scalpel.ir import PythonNormalizer, IRBinaryOp
    >>> normalizer = PythonNormalizer()
    >>> ir = normalizer.normalize("x = 1 + 2")
    >>> isinstance(ir.body[0].value, IRBinaryOp)
    True

Modules:
    nodes: IR node dataclasses (IRModule, IRFunction, IRBinaryOp, etc.)
    operators: Operator enums (BinaryOperator, CompareOperator, etc.)
    normalizers: Language-specific normalizers (PythonNormalizer, etc.)
    semantics: Language-specific behavior (PythonSemantics, JavaScriptSemantics)

[20251220_TODO] Add export for additional IR nodes:
    - IRImport, IRExport, IRSwitch, IRTry, IRRaise (polyglot support)
    - IRYield, IRYieldFrom (generator support)
    - IRTernary (conditional expressions)
    - IRDestructure (destructuring patterns) when implemented

[20251220_TODO] Export additional normalizers:
    - JavaNormalizer, TypeScriptNormalizer
    - TypeScriptTSXNormalizer for JSX/TSX support
    - Add conditional imports for optional dependencies

[20251220_TODO] Add IR utility functions:
    - ir_visitor(node, visitor) - Generic visitor pattern
    - ir_clone(node) - Deep copy IR subtree
    - ir_hash(node) - Compute IR node hash for caching
    - ir_compare(node1, node2) - Structural equality
    - ir_find(node, predicate) - Search IR tree

[20251220_TODO] Add IR transformation utilities:
    - ir_replace(node, old, new) - Replace subtrees
    - ir_map(node, transform) - Functional map over IR
    - ir_fold(node, combiner, initial) - Fold over IR
    - ir_collect(node, collector) - Gather matching nodes

[20251220_TODO] Add IR validation and analysis helpers:
    - validate_ir(ir_module) - Type and structure validation
    - find_all_calls(ir_module) -> List[IRCall]
    - find_all_assignments(ir_module) -> List[IRAssign]
    - find_all_definitions(ir_module) -> List[IRFunctionDef | IRClassDef]
    - get_variable_scope(ir_node) - Scope analysis helper
"""

from .nodes import (
    # Base
    IRNode,
    SourceLocation,
    # Statements
    IRModule,
    IRFunctionDef,
    IRClassDef,
    IRIf,
    IRFor,
    IRWhile,
    IRReturn,
    IRAssign,
    IRAugAssign,
    IRExprStmt,
    IRPass,
    IRBreak,
    IRContinue,
    # Expressions
    IRExpr,
    IRBinaryOp,
    IRUnaryOp,
    IRCompare,
    IRBoolOp,
    IRCall,
    IRAttribute,
    IRSubscript,
    IRName,
    IRConstant,
    IRList,
    IRDict,
    IRParameter,
)

from .operators import (
    BinaryOperator,
    UnaryOperator,
    CompareOperator,
    BoolOperator,
)

from .semantics import (
    LanguageSemantics,
    PythonSemantics,
    JavaScriptSemantics,
)

from .normalizers import (
    BaseNormalizer,
    PythonNormalizer,
)

__all__ = [
    # Nodes
    "IRNode",
    "SourceLocation",
    "IRModule",
    "IRFunctionDef",
    "IRClassDef",
    "IRIf",
    "IRFor",
    "IRWhile",
    "IRReturn",
    "IRAssign",
    "IRAugAssign",
    "IRExprStmt",
    "IRPass",
    "IRBreak",
    "IRContinue",
    "IRExpr",
    "IRBinaryOp",
    "IRUnaryOp",
    "IRCompare",
    "IRBoolOp",
    "IRCall",
    "IRAttribute",
    "IRSubscript",
    "IRName",
    "IRConstant",
    "IRList",
    "IRDict",
    "IRParameter",
    # Operators
    "BinaryOperator",
    "UnaryOperator",
    "CompareOperator",
    "BoolOperator",
    # Semantics
    "LanguageSemantics",
    "PythonSemantics",
    "JavaScriptSemantics",
    # Normalizers
    "BaseNormalizer",
    "PythonNormalizer",
]
