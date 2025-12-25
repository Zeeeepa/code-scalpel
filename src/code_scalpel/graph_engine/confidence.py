"""
Confidence Engine - Scoring system for graph edges and relationships.

[20251216_FEATURE] v2.1.0 - Confidence scoring for cross-language graph edges

This module implements a confidence scoring system that assigns scores (0.0-1.0)
to relationships between code elements. AI agents must request human confirmation
if confidence is below a threshold.

Key principles:
- Definite relationships (imports, type annotations) = 1.0
- High-confidence heuristics (route matching) = 0.8-0.95
- Medium-confidence patterns (string matching) = 0.5-0.7
- Uncertain/dynamic patterns = 0.3-0.5

Example:
    >>> engine = ConfidenceEngine()
    >>> score = engine.score_edge(EdgeType.IMPORT_STATEMENT, {"source": "direct"})
    >>> print(score)  # 1.0 (definite)
    >>> score = engine.score_edge(EdgeType.ROUTE_PATTERN_MATCH, {})
    >>> print(score)  # 0.8 (high confidence)

TODO ITEMS: graph_engine/confidence.py
======================================================================
COMMUNITY TIER - Core Confidence System
======================================================================
1. Add confidence_score() base function for all edge types
2. Add CONFIDENCE_RULES dict documentation with all rules
3. Add ConfidenceLevel enum with LOW, MEDIUM, HIGH, DEFINITE values
4. Add EdgeType enum with all relationship types
5. Add ConfidenceEngine class initialization
6. Add score_import_statement() for import edges
7. Add score_type_annotation() for type relationships
8. Add score_function_call() for call edges
9. Add score_route_pattern_match() for HTTP routes
10. Add score_string_match() for heuristic matching
11. Add score_property_access() for object property edges
12. Add score_inheritance() for class inheritance
13. Add score_interface_implementation() for interface relationships
14. Add get_confidence_level(score) to categorize scores
15. Add confidence_threshold_check(score, threshold) for gating
16. Add explain_confidence(edge, score) for reasoning
17. Add confidence_trend(edge_list) for pattern analysis
18. Add validate_confidence_score(score) range checking
19. Add confidence_metrics(edge_list) for statistical analysis
20. Add confidence_histogram(edge_list) for distribution
21. Add high_confidence_edges(graph, threshold)
22. Add low_confidence_edges(graph, threshold)
23. Add medium_confidence_edges(graph, threshold)
24. Add confidence_distribution(graph) for analytics
25. Add confidence_rules_documentation() for reference

PRO TIER - Advanced Confidence Features
======================================================================
26. Add ML-based confidence scoring (trained models)
27. Add confidence_context_aware() using surrounding code
28. Add confidence_history_tracking() over time
29. Add confidence_improvement_suggestions()
30. Add confidence_validation_feedback() for ML training
31. Add confidence_cross_validation() with multiple methods
32. Add ensemble_confidence(scores_list) combining methods
33. Add bayesian_confidence_update() with prior/posterior
34. Add confidence_decay_with_depth() for multi-hop edges
35. Add confidence_with_evidence_strength(evidence_list)
36. Add confidence_anomaly_detection() for outliers
37. Add confidence_pattern_learning() from user feedback
38. Add confidence_human_feedback_integration()
39. Add confidence_calibration() for model accuracy
40. Add confidence_score_normalization(scores) 0.0-1.0
41. Add confidence_uncertainty_estimation() confidence intervals
42. Add confidence_explanation_tree() for detailed reasoning
43. Add confidence_comparison(edge1, edge2) relative scoring
44. Add confidence_grouping(edges) by confidence level
45. Add confidence_threshold_optimization() for precision/recall
46. Add confidence_cost_benefit_analysis()
47. Add confidence_risk_assessment()
48. Add confidence_recommendation_engine()
49. Add confidence_feedback_loop() for improvement
50. Add confidence_performance_analysis()

ENTERPRISE TIER - Distributed Confidence System
======================================================================
51. Add distributed confidence aggregation across services
52. Add federated confidence training across organizations
53. Add multi-region confidence consensus
54. Add confidence model versioning
55. Add confidence model rollback capability
56. Add confidence audit logging (for compliance)
57. Add confidence encryption for sensitive edges
58. Add confidence access control (role-based)
59. Add confidence SLA monitoring
60. Add confidence performance guarantees
61. Add confidence scaling for large graphs
62. Add confidence caching with invalidation
63. Add confidence async scoring
64. Add confidence batch processing
65. Add confidence circuit breaker
66. Add confidence monitoring/alerting
67. Add ML confidence model training pipeline
68. Add confidence hyperparameter tuning
69. Add confidence model deployment
70. Add confidence A/B testing
71. Add confidence shadow mode testing
72. Add confidence gradual rollout
73. Add confidence disaster recovery
74. Add confidence compliance reporting (HIPAA/SOC2)
75. Add confidence commercial licensing
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


# [20251216_FEATURE] Edge types for confidence scoring
class EdgeType(Enum):
    """Type of relationship between code elements."""

    # Definite relationships (1.0 confidence)
    IMPORT_STATEMENT = "import_statement"  # import X from Y
    TYPE_ANNOTATION = "type_annotation"  # User: UserType
    INHERITANCE = "inheritance"  # extends/implements
    DIRECT_CALL = "direct_call"  # function()

    # High confidence (0.8-0.95)
    ROUTE_EXACT_MATCH = "route_exact_match"  # "/api/users" == "/api/users"
    ROUTE_PATTERN_MATCH = "route_pattern_match"  # "/api/users/{id}" ~= "/api/users/123"
    METHOD_REFERENCE = "method_reference"  # this.method()

    # Medium confidence (0.5-0.7)
    STRING_LITERAL_MATCH = "string_literal_match"  # Heuristic based on string
    FIELD_ACCESS = "field_access"  # object.field

    # Low confidence (0.3-0.5)
    DYNAMIC_ROUTE = "dynamic_route"  # "/api/" + version + "/user"
    INDIRECT_CALL = "indirect_call"  # Callback, higher-order function

    # HTTP relationships
    HTTP_CALL = "http_call"  # Frontend to backend


# [20251216_FEATURE] Confidence levels for human-in-the-loop thresholds
class ConfidenceLevel(Enum):
    """Confidence level categories."""

    DEFINITE = "definite"  # 1.0 - No human review needed
    HIGH = "high"  # 0.8-0.99 - Optional review
    MEDIUM = "medium"  # 0.5-0.79 - Recommended review
    LOW = "low"  # 0.3-0.49 - Required review
    UNCERTAIN = "uncertain"  # < 0.3 - Block until reviewed


# [20251216_FEATURE] Confidence scoring rules as per problem statement
CONFIDENCE_RULES: Dict[EdgeType, float] = {
    # Definite relationships
    EdgeType.IMPORT_STATEMENT: 1.0,
    EdgeType.TYPE_ANNOTATION: 1.0,
    EdgeType.INHERITANCE: 1.0,
    EdgeType.DIRECT_CALL: 0.95,
    # High confidence
    EdgeType.ROUTE_EXACT_MATCH: 0.95,
    EdgeType.ROUTE_PATTERN_MATCH: 0.8,
    EdgeType.METHOD_REFERENCE: 0.9,
    # Medium confidence
    EdgeType.STRING_LITERAL_MATCH: 0.7,
    EdgeType.FIELD_ACCESS: 0.85,
    # Low confidence
    EdgeType.DYNAMIC_ROUTE: 0.5,
    EdgeType.INDIRECT_CALL: 0.6,
    # HTTP relationships
    EdgeType.HTTP_CALL: 0.8,  # Base score, adjusted by route matching
}


# [20251216_FEATURE] Evidence for confidence adjustments
@dataclass
class ConfidenceEvidence:
    """Evidence that affects confidence scoring."""

    edge_type: EdgeType
    base_score: float
    adjustments: Dict[str, float]  # reason -> adjustment
    final_score: float
    explanation: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON."""
        return {
            "edge_type": self.edge_type.value,
            "base_score": self.base_score,
            "adjustments": self.adjustments,
            "final_score": self.final_score,
            "explanation": self.explanation,
        }


# [20251216_FEATURE] Main confidence engine
class ConfidenceEngine:
    """
    Engine for scoring confidence in code relationships.

    This class assigns confidence scores (0.0-1.0) to edges in the code graph.
    Scores help AI agents decide when to request human confirmation.

    Example:
        >>> engine = ConfidenceEngine()
        >>> edge_data = {"route": "/api/users", "match_type": "exact"}
        >>> evidence = engine.score_edge(EdgeType.ROUTE_EXACT_MATCH, edge_data)
        >>> print(evidence.final_score)  # 0.95
        >>> print(evidence.level)  # ConfidenceLevel.HIGH
    """

    def __init__(self, min_threshold: float = 0.8):
        """
        Initialize confidence engine.

        Args:
            min_threshold: Minimum confidence for automatic approval (default 0.8)
        """
        self.min_threshold = min_threshold
        self.rules = CONFIDENCE_RULES.copy()

    def score_edge(
        self, edge_type: EdgeType, context: Dict[str, Any]
    ) -> ConfidenceEvidence:
        """
        Calculate confidence score for an edge.

        Args:
            edge_type: Type of relationship
            context: Additional context for scoring adjustments

        Returns:
            ConfidenceEvidence with score and explanation
        """
        base_score = self.rules.get(edge_type, 0.5)
        adjustments: Dict[str, float] = {}

        # Apply context-specific adjustments
        if edge_type == EdgeType.HTTP_CALL:
            base_score = self._score_http_call(context, adjustments)
        elif edge_type == EdgeType.ROUTE_PATTERN_MATCH:
            base_score = self._score_route_match(context, adjustments)
        elif edge_type == EdgeType.STRING_LITERAL_MATCH:
            base_score = self._score_string_match(context, adjustments)

        # Clamp to [0.0, 1.0]
        final_score = max(0.0, min(1.0, base_score + sum(adjustments.values())))

        explanation = self._build_explanation(edge_type, final_score, adjustments)

        return ConfidenceEvidence(
            edge_type=edge_type,
            base_score=base_score,
            adjustments=adjustments,
            final_score=final_score,
            explanation=explanation,
        )

    def _score_http_call(
        self, context: Dict[str, Any], adjustments: Dict[str, float]
    ) -> float:
        """Score HTTP call edges based on route matching."""
        base = 0.8

        # Exact route match increases confidence
        if context.get("route_match") == "exact":
            adjustments["exact_route_match"] = 0.15
        elif context.get("route_match") == "pattern":
            adjustments["pattern_route_match"] = 0.0  # Already high
        elif context.get("route_match") == "dynamic":
            adjustments["dynamic_route"] = -0.3  # Reduce confidence

        # Type safety increases confidence
        if context.get("typed_client"):
            adjustments["typed_client"] = 0.05

        return base

    def _score_route_match(
        self, context: Dict[str, Any], adjustments: Dict[str, float]
    ) -> float:
        """Score route pattern matching."""
        base = 0.8

        # Exact string match
        if context.get("exact_match"):
            adjustments["exact_string"] = 0.15

        # Multiple matching routes reduce confidence
        match_count = context.get("match_count", 1)
        if match_count > 1:
            adjustments["multiple_matches"] = -0.1 * (match_count - 1)

        return base

    def _score_string_match(
        self, context: Dict[str, Any], adjustments: Dict[str, float]
    ) -> float:
        """Score string literal matching."""
        base = 0.7

        # Longer strings are more specific
        string_length = context.get("string_length", 0)
        if string_length > 20:
            adjustments["long_string"] = 0.1

        # URL patterns are more reliable
        if context.get("is_url_pattern"):
            adjustments["url_pattern"] = 0.1

        return base

    def _build_explanation(
        self, edge_type: EdgeType, score: float, adjustments: Dict[str, float]
    ) -> str:
        """Build human-readable explanation of confidence score."""
        parts = [f"Base: {edge_type.value}"]

        if adjustments:
            adj_str = ", ".join(f"{k}={v:+.2f}" for k, v in adjustments.items())
            parts.append(f"Adjustments: {adj_str}")

        level = self.get_confidence_level(score)
        parts.append(f"Level: {level.value}")

        return " | ".join(parts)

    def get_confidence_level(self, score: float) -> ConfidenceLevel:
        """
        Get confidence level category for a score.

        Args:
            score: Confidence score (0.0-1.0)

        Returns:
            ConfidenceLevel enum
        """
        if score >= 1.0:
            return ConfidenceLevel.DEFINITE
        elif score >= 0.8:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN

    def requires_human_approval(self, score: float) -> bool:
        """
        Check if a score requires human approval.

        Args:
            score: Confidence score

        Returns:
            True if score is below threshold
        """
        return score < self.min_threshold
