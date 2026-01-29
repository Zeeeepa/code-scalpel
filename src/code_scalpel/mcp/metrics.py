"""Metrics and telemetry tracking for suggestion effectiveness.

This module tracks how well our suggestions (self-correction hints) work:
- suggestion_accepted: Agent used our suggestion to correct the request
- suggestion_ignored: Agent ignored our suggestion
- suggestion_accuracy: Correctness of suggestions made
- suggestion_type: Categories of suggestions (symbol_typo, import_missing, etc)

Metrics can be stored in-memory or persisted to file/database.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SuggestionType(str, Enum):
    """Categories of suggestions we can make."""

    SYMBOL_TYPO = "symbol_typo"  # Symbol name misspelled
    IMPORT_MISSING = "import_missing"  # Missing import statement
    SCOPE_ERROR = "scope_error"  # Symbol not in expected scope
    SYNTAX_ERROR = "syntax_error"  # Syntax issues
    FILE_NOT_FOUND = "file_not_found"  # File not found or wrong path
    UNKNOWN = "unknown"  # Uncategorized


class SuggestionOutcome(str, Enum):
    """Outcomes for tracked suggestions."""

    ACCEPTED = "accepted"  # Agent accepted and used suggestion
    IGNORED = "ignored"  # Agent ignored suggestion
    PARTIALLY_USED = "partially_used"  # Agent used some but not all suggestions
    PENDING = "pending"  # Not yet resolved (not yet reported)
    ERROR = "error"  # Suggestion led to error


@dataclass
class SuggestionMetric:
    """Single suggestion event with metadata."""

    timestamp: datetime
    request_id: str
    tool_id: str
    suggestion_type: SuggestionType
    suggestions_offered: list[str]  # The suggestions we provided
    agent_choice: Optional[str] = None  # Which suggestion (if any) agent used
    outcome: SuggestionOutcome = SuggestionOutcome.PENDING
    accuracy_score: float = 0.0  # 0.0-1.0: how correct was the suggestion?
    context: dict[str, Any] = field(default_factory=dict)  # Additional metadata

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id,
            "tool_id": self.tool_id,
            "suggestion_type": self.suggestion_type.value,
            "suggestions_offered": self.suggestions_offered,
            "agent_choice": self.agent_choice,
            "outcome": self.outcome.value,
            "accuracy_score": self.accuracy_score,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SuggestionMetric:
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            request_id=data["request_id"],
            tool_id=data["tool_id"],
            suggestion_type=SuggestionType(data["suggestion_type"]),
            suggestions_offered=data["suggestions_offered"],
            agent_choice=data.get("agent_choice"),
            outcome=SuggestionOutcome(data.get("outcome", "pending")),
            accuracy_score=data.get("accuracy_score", 0.0),
            context=data.get("context", {}),
        )


class MetricsCollector:
    """Thread-safe collector for suggestion metrics.

    Tracks suggestion effectiveness to understand how well our self-correction
    hints work. Supports in-memory storage with optional file persistence.
    """

    def __init__(self, persist_path: Optional[Path] = None):
        """Initialize metrics collector.

        Args:
            persist_path: Optional path to persist metrics to JSON file.
        """
        self._lock = Lock()
        self._metrics: list[SuggestionMetric] = []
        self._persist_path = persist_path
        self._stats_cache: Optional[dict[str, Any]] = None

        # Load existing metrics if persist_path exists
        if persist_path and persist_path.exists():
            self._load_from_file()

    def track_suggestion(
        self,
        request_id: str,
        tool_id: str,
        suggestion_type: SuggestionType,
        suggestions: list[str],
        context: Optional[dict[str, Any]] = None,
    ) -> SuggestionMetric:
        """Track a suggestion that was offered to the agent.

        Args:
            request_id: Unique request identifier.
            tool_id: Which tool made the suggestion.
            suggestion_type: Category of suggestion.
            suggestions: List of suggestions offered.
            context: Additional context (symbol_name, import_path, etc).

        Returns:
            The created SuggestionMetric for later reference.
        """
        metric = SuggestionMetric(
            timestamp=datetime.utcnow(),
            request_id=request_id,
            tool_id=tool_id,
            suggestion_type=suggestion_type,
            suggestions_offered=suggestions,
            context=context or {},
        )

        with self._lock:
            self._metrics.append(metric)
            self._stats_cache = None  # Invalidate stats cache

        logger.debug(f"Tracked {suggestion_type.value} suggestion: {suggestions}")
        return metric

    def report_outcome(
        self,
        request_id: str,
        outcome: SuggestionOutcome,
        agent_choice: Optional[str] = None,
        accuracy_score: float = 0.0,
    ) -> bool:
        """Report the outcome of a tracked suggestion.

        Args:
            request_id: Request ID to match with tracked suggestion.
            outcome: How agent responded to suggestion.
            agent_choice: Which suggestion (if any) agent used.
            accuracy_score: Score 0.0-1.0 of suggestion correctness.

        Returns:
            True if outcome was recorded, False if request_id not found.
        """
        with self._lock:
            for metric in reversed(self._metrics):
                if metric.request_id == request_id and metric.outcome == SuggestionOutcome.PENDING:
                    metric.outcome = outcome
                    metric.agent_choice = agent_choice
                    metric.accuracy_score = max(0.0, min(1.0, accuracy_score))
                    self._stats_cache = None  # Invalidate stats cache
                    logger.debug(f"Recorded outcome for {request_id}: {outcome.value}")
                    return True

        logger.warning(f"Could not find pending suggestion for request {request_id}")
        return False

    def get_statistics(self) -> dict[str, Any]:
        """Get aggregated metrics statistics.

        Returns:
            Dict with acceptance rate, accuracy, breakdown by type, etc.
        """
        with self._lock:
            if self._stats_cache is not None:
                return self._stats_cache

            if not self._metrics:
                return {
                    "total_suggestions": 0,
                    "acceptance_rate": 0.0,
                    "avg_accuracy": 0.0,
                    "by_type": {},
                }

            # Count outcomes
            accepted = sum(1 for m in self._metrics if m.outcome == SuggestionOutcome.ACCEPTED)
            ignored = sum(1 for m in self._metrics if m.outcome == SuggestionOutcome.IGNORED)
            partial = sum(1 for m in self._metrics if m.outcome == SuggestionOutcome.PARTIALLY_USED)
            errors = sum(1 for m in self._metrics if m.outcome == SuggestionOutcome.ERROR)
            completed = accepted + ignored + partial + errors

            # Calculate rates
            completion_rate = completed / len(self._metrics) if self._metrics else 0.0
            acceptance_rate = accepted / completed if completed > 0 else 0.0
            avg_accuracy = sum(m.accuracy_score for m in self._metrics) / len(self._metrics)

            # Breakdown by type
            by_type = {}
            for metric in self._metrics:
                type_name = metric.suggestion_type.value
                if type_name not in by_type:
                    by_type[type_name] = {
                        "count": 0,
                        "accepted": 0,
                        "accuracy": [],
                    }
                by_type[type_name]["count"] += 1
                if metric.outcome == SuggestionOutcome.ACCEPTED:
                    by_type[type_name]["accepted"] += 1
                by_type[type_name]["accuracy"].append(metric.accuracy_score)

            # Compute average accuracy per type
            for type_name in by_type:
                accuracies = by_type[type_name].pop("accuracy")
                by_type[type_name]["avg_accuracy"] = sum(accuracies) / len(accuracies) if accuracies else 0.0
                by_type[type_name]["acceptance_rate"] = (
                    by_type[type_name]["accepted"] / by_type[type_name]["count"]
                    if by_type[type_name]["count"] > 0
                    else 0.0
                )

            stats = {
                "total_suggestions": len(self._metrics),
                "completed_outcomes": completed,
                "completion_rate": completion_rate,
                "acceptance_rate": acceptance_rate,
                "avg_accuracy": avg_accuracy,
                "counts": {
                    "accepted": accepted,
                    "ignored": ignored,
                    "partially_used": partial,
                    "error": errors,
                    "pending": len(self._metrics) - completed,
                },
                "by_type": by_type,
            }

            self._stats_cache = stats
            return stats

    def persist_to_file(self, path: Optional[Path] = None) -> Path:
        """Save metrics to JSON file.

        Args:
            path: Path to save to. Uses self._persist_path if not provided.

        Returns:
            Path where metrics were saved.
        """
        target_path = path or self._persist_path
        if not target_path:
            raise ValueError("No persist path configured")

        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Get stats without lock (call before acquiring lock)
        stats = self.get_statistics()

        with self._lock:
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_metrics": len(self._metrics),
                "metrics": [m.to_dict() for m in self._metrics],
                "statistics": stats,
            }

        with open(target_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Persisted {len(self._metrics)} metrics to {target_path}")
        return target_path

    def _load_from_file(self) -> None:
        """Load metrics from existing JSON file."""
        if not self._persist_path or not self._persist_path.exists():
            return

        try:
            with open(self._persist_path) as f:
                data = json.load(f)

            self._metrics = [SuggestionMetric.from_dict(m) for m in data.get("metrics", [])]
            logger.info(f"Loaded {len(self._metrics)} metrics from {self._persist_path}")
        except Exception as e:
            logger.warning(f"Failed to load metrics from {self._persist_path}: {e}")

    def export_csv(self, path: Path) -> Path:
        """Export metrics to CSV format.

        Args:
            path: Path to save CSV to.

        Returns:
            Path where CSV was saved.
        """
        import csv

        path.parent.mkdir(parents=True, exist_ok=True)

        with self._lock:
            with open(path, "w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "timestamp",
                        "request_id",
                        "tool_id",
                        "suggestion_type",
                        "suggestions_offered",
                        "agent_choice",
                        "outcome",
                        "accuracy_score",
                    ],
                )
                writer.writeheader()
                for metric in self._metrics:
                    writer.writerow(
                        {
                            "timestamp": metric.timestamp.isoformat(),
                            "request_id": metric.request_id,
                            "tool_id": metric.tool_id,
                            "suggestion_type": metric.suggestion_type.value,
                            "suggestions_offered": "|".join(metric.suggestions_offered),
                            "agent_choice": metric.agent_choice or "",
                            "outcome": metric.outcome.value,
                            "accuracy_score": metric.accuracy_score,
                        }
                    )

        logger.info(f"Exported {len(self._metrics)} metrics to {path}")
        return path


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def set_metrics_persistence(path: Path) -> None:
    """Configure persistence path for metrics."""
    global _metrics_collector
    _metrics_collector = MetricsCollector(persist_path=path)


__all__ = [
    "SuggestionType",
    "SuggestionOutcome",
    "SuggestionMetric",
    "MetricsCollector",
    "get_metrics_collector",
    "set_metrics_persistence",
]
