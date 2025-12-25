"""
Universal Node ID System - Standardized AST node identification across languages.

[20251216_FEATURE] v2.1.0 - Universal node ID format for cross-language graphs

This module implements a standardized format for identifying code elements
across Python, Java, TypeScript, and JavaScript. The format is:

    language::module::type::name[:method]

Examples:
    "python::app.handlers::class::RequestHandler"
    "java::com.example.api::controller::UserController:getUser"
    "typescript::src/api/client::function::fetchUsers"
    "javascript::utils/helpers::function::formatDate"

The universal ID enables the graph engine to:
- Reference any code element uniformly
- Build cross-language dependency graphs
- Track taint flow across module boundaries
- Detect HTTP links between frontend and backend

TODO ITEMS: graph_engine/node_id.py
======================================================================
COMMUNITY TIER - Core Node ID System
======================================================================
1. Add UniversalNodeID dataclass for ID representation
2. Add NodeIDParser class for parsing ID strings
3. Add parse_node_id(id_string) main parser
4. Add validate_node_id(id_string) format validation
5. Add create_node_id(language, module, type, name, method=None)
6. Add Language enum (PYTHON, JAVA, JAVASCRIPT, TYPESCRIPT)
7. Add NodeType enum (class, function, method, variable, endpoint)
8. Add get_language() from node ID
9. Add get_module() from node ID
10. Add get_type() from node ID
11. Add get_name() from node ID
12. Add get_method() from node ID
13. Add is_function(node_id) predicate
14. Add is_class(node_id) predicate
15. Add is_method(node_id) predicate
16. Add is_endpoint(node_id) predicate
17. Add is_variable(node_id) predicate
18. Add node_id_to_string(node_id) serialization
19. Add node_id_equality(id1, id2) comparison
20. Add node_id_contains(parent_id, child_id) relationship
21. Add get_parent_node_id(node_id) hierarchy
22. Add get_siblings_node_ids(node_id) locality
23. Add node_id_depth(node_id) nesting level
24. Add normalize_module_path() path consistency
25. Add node_id_documentation() format guide

PRO TIER - Advanced Node ID Features
======================================================================
26. Add fuzzy_match_node_id(id1, id2, threshold)
27. Add node_id_similarity(id1, id2) similarity scoring
28. Add find_node_by_name(graph, name) search
29. Add find_nodes_by_module(graph, module) filtering
30. Add find_nodes_by_type(graph, node_type) filtering
31. Add find_similar_node_ids(node_id, threshold)
32. Add node_id_aliasing() support for aliases
33. Add create_alias(canonical_id, alias_id)
34. Add resolve_alias(alias_id) to canonical
35. Add node_id_versioning() for tracking changes
36. Add node_id_history() audit trail
37. Add node_id_renaming() refactoring support
38. Add node_id_path_compression() for efficiency
39. Add node_id_context() surrounding information
40. Add node_id_metadata(node_id) properties
41. Add node_id_provenance() source tracking
42. Add node_id_confidence() reliability
43. Add node_id_alternative_names() equivalences
44. Add node_id_language_conversion() cross-language
45. Add node_id_regex_pattern() for pattern matching
46. Add node_id_glob_pattern() for wildcards
47. Add node_id_ranking() importance ordering
48. Add node_id_statistics() usage analytics
49. Add node_id_deduplication() normalization
50. Add node_id_collision_detection() uniqueness

ENTERPRISE TIER - Distributed Node ID System
======================================================================
51. Add distributed_node_id_generation() across services
52. Add federated_node_id_resolution() across orgs
53. Add multi_region_node_id_consistency()
54. Add node_id_global_registry() centralized tracking
55. Add node_id_synchronization() distributed sync
56. Add node_id_replication() for redundancy
57. Add node_id_backup_recovery() disaster recovery
58. Add node_id_encryption() security
59. Add node_id_audit_logging() compliance
60. Add node_id_access_control() permissions
61. Add node_id_versioning_system() history tracking
62. Add node_id_rollback() revert changes
63. Add node_id_sharding() horizontal scaling
64. Add node_id_caching() performance
65. Add node_id_invalidation() cache management
66. Add node_id_async_resolution() non-blocking
67. Add node_id_streaming_updates() real-time
68. Add node_id_monitoring() metrics
69. Add node_id_alerting() anomaly detection
70. Add node_id_ml_enrichment() ML features
71. Add node_id_semantic_similarity() meaning
72. Add node_id_graph_embedding() vector representation
73. Add node_id_performance_profiling()
74. Add node_id_cost_tracking() billing
75. Add node_id_commercial_licensing()
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# [20251216_FEATURE] Node types for universal identification
class NodeType(Enum):
    """Type of code element."""

    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    FIELD = "field"
    PROPERTY = "property"
    VARIABLE = "variable"
    INTERFACE = "interface"
    ENDPOINT = "endpoint"  # HTTP endpoint
    CLIENT = "client"  # HTTP client call
    CONTROLLER = "controller"  # Java/TypeScript controller
    MODULE = "module"
    PACKAGE = "package"


# [20251216_FEATURE] Universal node ID data structure
@dataclass
class UniversalNodeID:
    """
    Universal identifier for a code element across any language.

    Attributes:
        language: Programming language (python, java, typescript, javascript)
        module: Module/package path (e.g., "app.handlers", "com.example.api")
        node_type: Type of code element (function, class, method, etc.)
        name: Name of the element
        method: Optional method name (for class methods)
        line: Optional line number
        file: Optional file path
    """

    language: str
    module: str
    node_type: NodeType
    name: str
    method: Optional[str] = None
    line: Optional[int] = None
    file: Optional[str] = None

    def __str__(self) -> str:
        """Format as universal ID string."""
        parts = [self.language, self.module, self.node_type.value, self.name]
        id_str = "::".join(parts)
        if self.method:
            id_str += f":{self.method}"
        return id_str

    def to_short_id(self) -> str:
        """Short ID without module for display."""
        if self.method:
            return f"{self.language}::{self.name}:{self.method}"
        return f"{self.language}::{self.name}"

    def to_dict(self) -> dict[str, str | int]:
        """
        Convert to dictionary for JSON serialization.

        [20251220_BUGFIX] Fixed return type annotation to accept both str and int values.
        The dict contains string fields (id, language, module, type, name, method, file)
        and optional integer field (line).
        """
        result: dict[str, str | int] = {
            "id": str(self),
            "language": self.language,
            "module": self.module,
            "type": self.node_type.value,
            "name": self.name,
        }
        if self.method:
            result["method"] = self.method
        if self.line is not None:
            result["line"] = self.line
        if self.file:
            result["file"] = self.file
        return result

    @staticmethod
    def from_dict(data: dict) -> UniversalNodeID:
        """Create from dictionary."""
        return UniversalNodeID(
            language=data["language"],
            module=data["module"],
            node_type=NodeType(data["type"]),
            name=data["name"],
            method=data.get("method"),
            line=data.get("line"),
            file=data.get("file"),
        )


# [20251216_FEATURE] Parser for universal node IDs
def parse_node_id(id_string: str) -> UniversalNodeID:
    """
    Parse a universal node ID string into components.

    Args:
        id_string: ID in format "language::module::type::name[:method]"

    Returns:
        UniversalNodeID object

    Raises:
        ValueError: If format is invalid

    Examples:
        >>> parse_node_id("python::app.handlers::class::RequestHandler")
        UniversalNodeID(language='python', module='app.handlers', ...)

        >>> parse_node_id("java::com.example::controller::UserController:getUser")
        UniversalNodeID(language='java', ..., method='getUser')
    """
    # Split by :: for main components
    parts = id_string.split("::")
    if len(parts) != 4:
        raise ValueError(
            f"Invalid node ID format: {id_string}. "
            f"Expected: language::module::type::name[:method]"
        )

    language, module, type_str, name_part = parts

    # Check for method suffix (after :)
    method = None
    if ":" in name_part:
        name, method = name_part.split(":", 1)
    else:
        name = name_part

    try:
        node_type = NodeType(type_str)
    except ValueError:
        raise ValueError(f"Invalid node type: {type_str}")

    return UniversalNodeID(
        language=language,
        module=module,
        node_type=node_type,
        name=name,
        method=method,
    )


# [20251216_FEATURE] Factory function for creating node IDs
def create_node_id(
    language: str,
    module: str,
    node_type: str | NodeType,
    name: str,
    method: Optional[str] = None,
    line: Optional[int] = None,
    file: Optional[str] = None,
) -> UniversalNodeID:
    """
    Create a universal node ID.

    Args:
        language: Programming language
        module: Module/package path
        node_type: Type of node (as string or NodeType enum)
        name: Name of the element
        method: Optional method name
        line: Optional line number
        file: Optional file path

    Returns:
        UniversalNodeID object

    Examples:
        >>> create_node_id("python", "app.handlers", "class", "RequestHandler")
        >>> create_node_id(
        ...     "java", "com.example", NodeType.METHOD, "UserController", "getUser"
        ... )
    """
    if isinstance(node_type, str):
        node_type = NodeType(node_type)

    return UniversalNodeID(
        language=language,
        module=module,
        node_type=node_type,
        name=name,
        method=method,
        line=line,
        file=file,
    )
