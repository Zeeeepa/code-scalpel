"""Release metrics tracking and analytics.

Provides metrics collection and analysis for release automation including:
- Build time tracking
- Publishing metrics
- Test duration recording
- Statistical analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class MetricType(str, Enum):
    """Types of metrics."""

    BUILD_TIME = "build_time"
    TEST_DURATION = "test_duration"
    PUBLISH_TIME = "publish_time"
    DEPLOYMENT_TIME = "deployment_time"
    CUSTOM = "custom"


@dataclass
class Metric:
    """Represents a recorded metric.

    Attributes:
        name: Metric name
        value: Metric value
        type: Type of metric
        timestamp: When metric was recorded
        tags: Optional tags for grouping
    """

    name: str
    value: float
    type: MetricType
    timestamp: datetime
    tags: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
        }


class MetricsTracker:
    """Track and analyze release metrics.

    Provides methods for:
    - Recording metrics
    - Retrieving metrics
    - Computing statistics
    - Exporting metrics
    """

    def __init__(self):
        """Initialize metrics tracker."""
        self.metrics: list[Metric] = []

    def record_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.CUSTOM,
        tags: Optional[dict[str, str]] = None,
    ) -> Metric:
        """Record a metric.

        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            tags: Optional tags

        Returns:
            Recorded metric
        """
        if tags is None:
            tags = {}

        metric = Metric(
            name=name,
            value=value,
            type=metric_type,
            timestamp=datetime.now(),
            tags=tags,
        )
        self.metrics.append(metric)
        return metric

    def get_metrics(
        self,
        metric_type: Optional[MetricType] = None,
        tag_filter: Optional[dict] = None,
    ) -> list[Metric]:
        """Get metrics with optional filtering.

        Args:
            metric_type: Optional filter by type
            tag_filter: Optional filter by tags

        Returns:
            Filtered list of metrics
        """
        result = self.metrics
        if metric_type:
            result = [m for m in result if m.type == metric_type]
        if tag_filter:
            result = [
                m
                for m in result
                if all(m.tags.get(k) == v for k, v in tag_filter.items())
            ]
        return result

    def calculate_statistics(self, metric_type: Optional[MetricType] = None) -> dict:
        """Calculate statistics for metrics.

        Args:
            metric_type: Optional filter by type

        Returns:
            Dictionary with statistics (count, mean, min, max, total)
        """
        metrics = self.get_metrics(metric_type)
        if not metrics:
            return {
                "count": 0,
                "mean": 0,
                "min": 0,
                "max": 0,
                "total": 0,
            }

        values = [m.value for m in metrics]
        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "total": sum(values),
        }

    def export_metrics(self) -> list[dict]:
        """Export all metrics.

        Returns:
            List of metric dictionaries
        """
        return [m.to_dict() for m in self.metrics]

    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        self.metrics.clear()

    def get_metric_summary(self) -> dict:
        """Get summary of all metrics by type.

        Returns:
            Dictionary with statistics for each metric type
        """
        summary = {}
        for metric_type in MetricType:
            stats = self.calculate_statistics(metric_type)
            if stats["count"] > 0:
                summary[metric_type.value] = stats
        return summary
