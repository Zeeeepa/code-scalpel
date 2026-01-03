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

from .nodes import IRAttribute  # Base; Statements; Expressions
from .nodes import (IRAssign, IRAugAssign, IRBinaryOp, IRBoolOp, IRBreak,
                    IRCall, IRClassDef, IRCompare, IRConstant, IRContinue,
                    IRDict, IRExpr, IRExprStmt, IRFor, IRFunctionDef, IRIf,
                    IRList, IRModule, IRName, IRNode, IRParameter, IRPass,
                    IRReturn, IRSubscript, IRUnaryOp, IRWhile, SourceLocation)
from .normalizers import BaseNormalizer, PythonNormalizer
from .operators import (BinaryOperator, BoolOperator, CompareOperator,
                        UnaryOperator)
from .semantics import JavaScriptSemantics, LanguageSemantics, PythonSemantics

# TODO ITEMS: IR Module (__init__.py)
# ======================================================================
# COMMUNITY TIER - Core IR Infrastructure
# ======================================================================
# 1. Add utility function ir_visitor(node, visitor_func) for generic IR tree traversal
# 2. Add utility function ir_clone(node) for deep copying IR subtrees
# 3. Add utility function ir_find(node, predicate) to search IR tree by predicate
# 4. Add get_all_functions(ir_module) helper to extract all function defs
# 5. Add get_all_classes(ir_module) helper to extract all class defs
# 6. Add get_all_assignments(ir_module) helper to find all variable assignments
# 7. Add walk_tree(node, order='pre') generator for pre/post-order traversal
# 8. Add validate_ir(ir_module) function for IR structure validation
# 9. Document proper import patterns in module docstring with examples
# 10. Add example showing normalizer factory usage patterns
# 11. Add ir_collect(node, collector_func) to gather matching nodes
# 12. Add ir_collect_by_type(node, ir_node_type) to find nodes by type
# 13. Add get_all_calls(ir_module) helper to extract all call expressions
# 14. Add get_all_imports(ir_module) helper to list all imports
# 15. Add count_nodes(ir_module) to compute total node count
# 16. Add ir_depth(node) to calculate max tree depth
# 17. Add ir_width(node) to calculate node breadth
# 18. Add find_all_paths(node, target) to trace data flow paths
# 19. Add extract_subtree(node, path) to extract subtrees by path
# 20. Add ir_statistics(ir_module) to compute module-level statistics
# 21. Add pretty_print(ir_node, indent=0) for debugging output
# 22. Add ir_to_dict(node) for serialization to dict format
# 23. Add ir_summary(ir_module) for high-level module overview
# 24. Add normalize_ir(ir_node) to ensure consistent structure
# 25. Add ir_equivalence(node1, node2) for structural comparison

# PRO TIER - IR Analysis and Caching
# ======================================================================
# 26. Add ir_hash(node) function for content-based caching
# 27. Add ir_hash_subtree(node) to cache subtrees independently
# 28. Add ir_compare(node1, node2, strict=False) for structural equality checking
# 29. Add ir_metadata(node, key, value) to attach analysis-specific data
# 30. Add get_metadata(node, key) to retrieve stored metadata
# 31. Add scope_analyzer(ir_module) to build variable scope information
# 32. Add type_inference_context(ir_node) for type analysis state
# 33. Add memoized_traversal(node, cache_dict) for performance-sensitive analysis
# 34. Add ir_diff(node1, node2) to compute differences between IR versions
# 35. Add diff_summary(diff_result) for human-readable diff output
# 36. Add incremental_update(old_ir, changes) for partial IR regeneration
# 37. Add IR caching layer for repeated normalizations (LRU cache)
# 38. Add cache_stats() to monitor cache performance
# 39. Add clear_ir_cache() to reset analysis cache
# 40. Add ir_fingerprint(node) for deduplication
# 41. Add detect_duplicates(ir_module) to find identical subtrees
# 42. Add ir_optimization_hints(node) for compiler-like suggestions
# 43. Add find_dead_code(ir_module) to identify unused definitions
# 44. Add control_flow_graph(ir_function) to extract CFG
# 45. Add data_flow_graph(ir_module) to extract data dependencies
# 46. Add complexity_metrics(ir_node) for cyclomatic/cognitive complexity
# 47. Add ir_compression(node) to find reusable substructures
# 48. Add pattern_match(node, pattern_template) for AST pattern matching
# 49. Add find_similar_structures(ir_module, threshold=0.8) for code clone detection
# 50. Add ir_validate_semantics(ir_node, target_language) for semantic checking

# ENTERPRISE TIER - Distributed IR and Advanced Features
# ======================================================================
# 51. Add distributed IR serialization (protobuf format)
# 52. Add distributed IR serialization (MessagePack format)
# 53. Add distributed IR serialization (JSON with schema validation)
# 54. Add cross_language_ir_equivalence(ir1, ir2, lang1, lang2) detector
# 55. Add polyglot_ir_composition(ir_python, ir_java) for multi-language analysis
# 56. Add ir_versioning() system for backward compatibility
# 57. Add check_ir_compatibility(ir_node, target_version) for version checking
# 58. Add federated_analysis(ir_modules_dict) across multiple IR modules
# 59. Add distributed_ir_cache(cache_backend) for shared caching
# 60. Add ml_based_ir_optimization(ir_node, model) for ML suggestions
# 61. Add ir_compression_ml(node, compression_ratio=0.8) using ML
# 62. Add async_normalizer_support() for large codebases
# 63. Add streaming_ir_processor(stream_source) for memory efficiency
# 64. Add ir_plugin_system() for custom node type registration
# 65. Add register_custom_node(node_class, validator) for extensibility
# 66. Add audit_logging_all_ir_ops() comprehensive logging
# 67. Add ir_telemetry_collection() for monitoring
# 68. Add ir_performance_profiling() detailed performance metrics
# 69. Add ir_change_tracking() to monitor transformations
# 70. Add distributed_ir_synchronization() for multi-agent analysis
# 71. Add federated_learning_on_ir(ir_collection, model) integration
# 72. Add ir_encryption() for secure analysis
# 73. Add ir_signature_verification() for tamper detection
# 74. Add cross_language_semantic_inference(ir_list) polyglot semantics
# 75. Add ir_optimization_autotuning() for performance tuning

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
