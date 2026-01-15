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

# TODO [CORE/Infrastructure] Add export for additional IR nodes: IRImport, IRExport, IRSwitch, IRTry, IRRaise (polyglot support)
# TODO [CORE/Infrastructure] Add export for generator IR nodes: IRYield, IRYieldFrom
# TODO [CORE/Infrastructure] Add export for conditional expressions: IRTernary
# TODO [CORE/Infrastructure] Add export for destructuring patterns: IRDestructure
# TODO [CORE/Infrastructure] Export JavaNormalizer and TypeScriptNormalizer
# TODO [CORE/Infrastructure] Export TypeScriptTSXNormalizer for JSX/TSX support
# TODO [CORE/Infrastructure] Add conditional imports for optional dependencies
# TODO [CORE/Utilities] Add ir_visitor(node, visitor) - Generic visitor pattern
# TODO [CORE/Utilities] Add ir_clone(node) - Deep copy IR subtree
# TODO [CORE/Utilities] Add ir_hash(node) - Compute IR node hash for caching
# TODO [CORE/Utilities] Add ir_compare(node1, node2) - Structural equality
# TODO [CORE/Utilities] Add ir_find(node, predicate) - Search IR tree
# TODO [CORE/Transformation] Add ir_replace(node, old, new) - Replace subtrees
# TODO [CORE/Transformation] Add ir_map(node, transform) - Functional map over IR
# TODO [CORE/Transformation] Add ir_fold(node, combiner, initial) - Fold over IR
# TODO [CORE/Transformation] Add ir_collect(node, collector) - Gather matching nodes
# TODO [CORE/Analysis] Add validate_ir(ir_module) - Type and structure validation
# TODO [CORE/Analysis] Add find_all_calls(ir_module) -> List[IRCall]
# TODO [CORE/Analysis] Add find_all_assignments(ir_module) -> List[IRAssign]
# TODO [CORE/Analysis] Add find_all_definitions(ir_module) -> List[IRFunctionDef | IRClassDef]
# TODO [CORE/Analysis] Add get_variable_scope(ir_node) - Scope analysis helper
"""

from .nodes import IRAttribute  # Base; Statements; Expressions
from .nodes import (
    IRAssign,
    IRAugAssign,
    IRBinaryOp,
    IRBoolOp,
    IRBreak,
    IRCall,
    IRClassDef,
    IRCompare,
    IRConstant,
    IRContinue,
    IRDict,
    IRExpr,
    IRExprStmt,
    IRFor,
    IRFunctionDef,
    IRIf,
    IRList,
    IRModule,
    IRName,
    IRNode,
    IRParameter,
    IRPass,
    IRReturn,
    IRSubscript,
    IRUnaryOp,
    IRWhile,
    SourceLocation,
)
from .normalizers import BaseNormalizer, PythonNormalizer
from .operators import BinaryOperator, BoolOperator, CompareOperator, UnaryOperator
from .semantics import JavaScriptSemantics, LanguageSemantics, PythonSemantics

# TODO [CORE/Utilities] Add utility function ir_visitor(node, visitor_func) for generic IR tree traversal
# TODO [CORE/Utilities] Add utility function ir_clone(node) for deep copying IR subtrees
# TODO [CORE/Utilities] Add utility function ir_find(node, predicate) to search IR tree by predicate
# TODO [CORE/Utilities] Add get_all_functions(ir_module) helper to extract all function defs
# TODO [CORE/Utilities] Add get_all_classes(ir_module) helper to extract all class defs
# TODO [CORE/Utilities] Add get_all_assignments(ir_module) helper to find all variable assignments
# TODO [CORE/Utilities] Add walk_tree(node, order='pre') generator for pre/post-order traversal
# TODO [CORE/Analysis] Add validate_ir(ir_module) function for IR structure validation
# TODO [CORE/Documentation] Document proper import patterns in module docstring with examples
# TODO [CORE/Documentation] Add example showing normalizer factory usage patterns
# TODO [CORE/Utilities] Add ir_collect(node, collector_func) to gather matching nodes
# TODO [CORE/Utilities] Add ir_collect_by_type(node, ir_node_type) to find nodes by type
# TODO [CORE/Analysis] Add get_all_calls(ir_module) helper to extract all call expressions
# TODO [CORE/Analysis] Add get_all_imports(ir_module) helper to list all imports
# TODO [CORE/Analysis] Add count_nodes(ir_module) to compute total node count
# TODO [CORE/Analysis] Add ir_depth(node) to calculate max tree depth
# TODO [CORE/Analysis] Add ir_width(node) to calculate node breadth
# TODO [CORE/Analysis] Add find_all_paths(node, target) to trace data flow paths
# TODO [CORE/Utilities] Add extract_subtree(node, path) to extract subtrees by path
# TODO [CORE/Analysis] Add ir_statistics(ir_module) to compute module-level statistics
# TODO [CORE/Utilities] Add pretty_print(ir_node, indent=0) for debugging output
# TODO [CORE/Utilities] Add ir_to_dict(node) for serialization to dict format
# TODO [CORE/Analysis] Add ir_summary(ir_module) for high-level module overview
# TODO [CORE/Utilities] Add normalize_ir(ir_node) to ensure consistent structure
# TODO [CORE/Analysis] Add ir_equivalence(node1, node2) for structural comparison
# TODO [PRO/Caching] Add ir_hash(node) function for content-based caching
# TODO [PRO/Caching] Add ir_hash_subtree(node) to cache subtrees independently
# TODO [PRO/Analysis] Add ir_compare(node1, node2, strict=False) for structural equality checking
# TODO [PRO/Metadata] Add ir_metadata(node, key, value) to attach analysis-specific data
# TODO [PRO/Metadata] Add get_metadata(node, key) to retrieve stored metadata
# TODO [PRO/Analysis] Add scope_analyzer(ir_module) to build variable scope information
# TODO [PRO/Analysis] Add type_inference_context(ir_node) for type analysis state
# TODO [PRO/Performance] Add memoized_traversal(node, cache_dict) for performance-sensitive analysis
# TODO [PRO/Analysis] Add ir_diff(node1, node2) to compute differences between IR versions
# TODO [PRO/Analysis] Add diff_summary(diff_result) for human-readable diff output
# TODO [PRO/Transformation] Add incremental_update(old_ir, changes) for partial IR regeneration
# TODO [PRO/Caching] Add IR caching layer for repeated normalizations (LRU cache)
# TODO [PRO/Caching] Add cache_stats() to monitor cache performance
# TODO [PRO/Caching] Add clear_ir_cache() to reset analysis cache
# TODO [PRO/Analysis] Add ir_fingerprint(node) for deduplication
# TODO [PRO/Analysis] Add detect_duplicates(ir_module) to find identical subtrees
# TODO [PRO/Analysis] Add ir_optimization_hints(node) for compiler-like suggestions
# TODO [PRO/Analysis] Add find_dead_code(ir_module) to identify unused definitions
# TODO [PRO/Analysis] Add control_flow_graph(ir_function) to extract CFG
# TODO [PRO/Analysis] Add data_flow_graph(ir_module) to extract data dependencies
# TODO [PRO/Metrics] Add complexity_metrics(ir_node) for cyclomatic/cognitive complexity
# TODO [PRO/Analysis] Add ir_compression(node) to find reusable substructures
# TODO [PRO/Analysis] Add pattern_match(node, pattern_template) for AST pattern matching
# TODO [PRO/Analysis] Add find_similar_structures(ir_module, threshold=0.8) for code clone detection
# TODO [PRO/Analysis] Add ir_validate_semantics(ir_node, target_language) for semantic checking
# TODO [ENTERPRISE/Serialization] Add distributed IR serialization (protobuf format)
# TODO [ENTERPRISE/Serialization] Add distributed IR serialization (MessagePack format)
# TODO [ENTERPRISE/Serialization] Add distributed IR serialization (JSON with schema validation)
# TODO [ENTERPRISE/Analysis] Add cross_language_ir_equivalence(ir1, ir2, lang1, lang2) detector
# TODO [ENTERPRISE/Analysis] Add polyglot_ir_composition(ir_python, ir_java) for multi-language analysis
# TODO [ENTERPRISE/Versioning] Add ir_versioning() system for backward compatibility
# TODO [ENTERPRISE/Versioning] Add check_ir_compatibility(ir_node, target_version) for version checking
# TODO [ENTERPRISE/Analysis] Add federated_analysis(ir_modules_dict) across multiple IR modules
# TODO [ENTERPRISE/Caching] Add distributed_ir_cache(cache_backend) for shared caching
# TODO [ENTERPRISE/ML] Add ml_based_ir_optimization(ir_node, model) for ML suggestions
# TODO [ENTERPRISE/ML] Add ir_compression_ml(node, compression_ratio=0.8) using ML
# TODO [ENTERPRISE/Performance] Add async_normalizer_support() for large codebases
# TODO [ENTERPRISE/Performance] Add streaming_ir_processor(stream_source) for memory efficiency
# TODO [ENTERPRISE/Extensibility] Add ir_plugin_system() for custom node type registration
# TODO [ENTERPRISE/Extensibility] Add register_custom_node(node_class, validator) for extensibility
# TODO [ENTERPRISE/Monitoring] Add audit_logging_all_ir_ops() comprehensive logging
# TODO [ENTERPRISE/Monitoring] Add ir_telemetry_collection() for monitoring
# TODO [ENTERPRISE/Monitoring] Add ir_performance_profiling() detailed performance metrics
# TODO [ENTERPRISE/Monitoring] Add ir_change_tracking() to monitor transformations
# TODO [ENTERPRISE/Distributed] Add distributed_ir_synchronization() for multi-agent analysis
# TODO [ENTERPRISE/ML] Add federated_learning_on_ir(ir_collection, model) integration
# TODO [ENTERPRISE/Security] Add ir_encryption() for secure analysis
# TODO [ENTERPRISE/Security] Add ir_signature_verification() for tamper detection
# TODO [ENTERPRISE/Analysis] Add cross_language_semantic_inference(ir_list) polyglot semantics
# TODO [ENTERPRISE/Performance] Add ir_optimization_autotuning() for performance tuning


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
