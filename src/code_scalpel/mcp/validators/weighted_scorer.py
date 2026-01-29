"""Weighted symbol matching for intelligent fuzzy suggestions.

This module implements a weighted scoring system for symbol matching that uses:
- Base score: Levenshtein distance (via difflib.SequenceMatcher)
- Locality boost: +0.2 if symbol is in same scope (file, class, function)
- Export boost: +0.1 if symbol is public API

Only returns suggestions with total_score > 0.6 (configurable threshold).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List
import difflib


@dataclass
class ScoredCandidate:
    """A symbol with its match score and diagnostic metadata."""

    name: str
    """The symbol name (e.g., 'process_data')."""

    base_score: float
    """Levenshtein distance score from difflib.SequenceMatcher."""

    locality_boost: float
    """+0.2 if symbol is in same scope as request context."""

    export_boost: float
    """+0.1 if symbol is public API."""

    total_score: float
    """base_score + locality_boost + export_boost."""

    scope: str
    """Where the symbol lives (e.g., 'module', 'UserService' class)."""

    is_exported: bool
    """True if symbol is public API (no leading underscore, etc)."""

    reason: str
    """Diagnostic string explaining the score breakdown."""

    def __repr__(self) -> str:
        """Return a concise representation."""
        return (
            f"ScoredCandidate({self.name}, score={self.total_score:.2f}, "
            f"scope={self.scope}, exported={self.is_exported})"
        )


class WeightedSymbolMatcher:
    """Calculates match scores using weighted heuristics.

    Formula:
        total_score = base_score + locality_boost + export_boost

    The scoring is designed to rank suggestions with preference for:
    1. Symbols in the same scope as the request (locality boost)
    2. Public API symbols (export boost)
    3. High string similarity (base score)

    Only returns candidates with total_score > threshold (default 0.6).
    """

    LOCALITY_BOOST = 0.2
    """Boost for symbols in the same scope."""

    EXPORT_BOOST = 0.1
    """Boost for public API symbols."""

    THRESHOLD = 0.6
    """Minimum score to include a candidate."""

    @staticmethod
    def calculate_match_score(
        target_symbol: str,
        candidate_symbol: str,
        candidate_scope: str,
        candidate_is_exported: bool,
        request_context_scope: Optional[str] = None,
    ) -> ScoredCandidate:
        """Calculate a match score for a symbol candidate.

        Args:
            target_symbol: What the user asked for (e.g., "process_dta").
            candidate_symbol: What we found (e.g., "process_data").
            candidate_scope: Where the symbol lives (e.g., "module", "UserService").
            candidate_is_exported: Is it a public API?
            request_context_scope: Where the request came from (e.g., "UserService" class).
                If this matches candidate_scope, locality boost is applied.

        Returns:
            ScoredCandidate with detailed breakdown of scoring.
        """
        # 1. Base score: SequenceMatcher is more accurate than Levenshtein for code
        base_score = difflib.SequenceMatcher(None, target_symbol, candidate_symbol).ratio()

        # 2. Locality boost: +0.2 if in same scope
        locality_boost = 0.0
        if request_context_scope and candidate_scope == request_context_scope:
            locality_boost = WeightedSymbolMatcher.LOCALITY_BOOST

        # 3. Export boost: +0.1 if public API
        export_boost = 0.0
        if candidate_is_exported:
            export_boost = WeightedSymbolMatcher.EXPORT_BOOST

        # 4. Total score (capped at 1.0 logically)
        total_score = min(1.0, base_score + locality_boost + export_boost)

        # 5. Diagnostic reason string
        reason = f"base={base_score:.2f}"
        if locality_boost > 0:
            reason += " +local"
        if export_boost > 0:
            reason += " +export"

        return ScoredCandidate(
            name=candidate_symbol,
            base_score=base_score,
            locality_boost=locality_boost,
            export_boost=export_boost,
            total_score=total_score,
            scope=candidate_scope,
            is_exported=candidate_is_exported,
            reason=reason,
        )

    @staticmethod
    def rank_candidates(
        candidates: List[ScoredCandidate],
        threshold: Optional[float] = None,
        top_k: int = 3,
    ) -> List[ScoredCandidate]:
        """Rank candidates by score and filter below threshold.

        Args:
            candidates: List of ScoredCandidate objects.
            threshold: Minimum score to include (default: 0.6). Set to None to skip filtering.
            top_k: Maximum number of candidates to return (default: 3).

        Returns:
            Sorted list of passing candidates (descending by score), up to top_k.

        Example:
            >>> candidates = [
            ...     ScoredCandidate("process_data", 0.85, 0.2, 0.1, 1.0, "module", True, "..."),
            ...     ScoredCandidate("process_item", 0.70, 0.0, 0.1, 0.8, "module", True, "..."),
            ... ]
            >>> ranked = WeightedSymbolMatcher.rank_candidates(candidates, top_k=2)
            >>> len(ranked)
            2
            >>> ranked[0].name
            'process_data'
        """
        if threshold is None:
            threshold = WeightedSymbolMatcher.THRESHOLD

        # Filter by threshold
        passing = [c for c in candidates if c.total_score >= threshold]

        # Sort by score (descending)
        passing.sort(key=lambda c: c.total_score, reverse=True)

        # Limit to top_k
        return passing[:top_k]


__all__ = [
    "ScoredCandidate",
    "WeightedSymbolMatcher",
]
