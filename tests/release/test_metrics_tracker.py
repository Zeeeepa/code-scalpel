"""Tests for release metrics tracking system."""

from datetime import datetime


from code_scalpel.release.metrics_tracker import Metric, MetricType, MetricsTracker


class TestMetric:
    """Test Metric class."""

    def test_create_metric(self):
        """Test creating a metric."""
        metric = Metric(
            name="build_time",
            value=45.5,
            type=MetricType.BUILD_TIME,
            timestamp=datetime.now(),
        )
        assert metric.name == "build_time"
        assert metric.value == 45.5

    def test_metric_with_tags(self):
        """Test metric with tags."""
        metric = Metric(
            name="test_duration",
            value=120,
            type=MetricType.TEST_DURATION,
            timestamp=datetime.now(),
            tags={"version": "1.0.0", "branch": "main"},
        )
        assert metric.tags["version"] == "1.0.0"

    def test_metric_to_dict(self):
        """Test converting metric to dict."""
        now = datetime.now()
        metric = Metric(
            name="test",
            value=100,
            type=MetricType.CUSTOM,
            timestamp=now,
        )
        result = metric.to_dict()
        assert result["name"] == "test"
        assert result["value"] == 100


class TestMetricsTrackerRecord:
    """Test recording metrics."""

    def test_record_metric(self):
        """Test recording a metric."""
        tracker = MetricsTracker()
        metric = tracker.record_metric("build_time", 45.5, MetricType.BUILD_TIME)
        assert metric.name == "build_time"
        assert len(tracker.metrics) == 1

    def test_record_multiple_metrics(self):
        """Test recording multiple metrics."""
        tracker = MetricsTracker()
        tracker.record_metric("build_time", 45.5, MetricType.BUILD_TIME)
        tracker.record_metric("test_duration", 120, MetricType.TEST_DURATION)
        assert len(tracker.metrics) == 2

    def test_record_metric_with_tags(self):
        """Test recording metric with tags."""
        tracker = MetricsTracker()
        metric = tracker.record_metric(
            "build_time",
            30,
            MetricType.BUILD_TIME,
            tags={"version": "1.0.0"},
        )
        assert metric.tags["version"] == "1.0.0"

    def test_record_metric_default_type(self):
        """Test recording metric with default type."""
        tracker = MetricsTracker()
        metric = tracker.record_metric("custom_metric", 99)
        assert metric.type == MetricType.CUSTOM


class TestMetricsTrackerRetrieval:
    """Test retrieving metrics."""

    def test_get_all_metrics(self):
        """Test getting all metrics."""
        tracker = MetricsTracker()
        tracker.record_metric("metric1", 10, MetricType.BUILD_TIME)
        tracker.record_metric("metric2", 20, MetricType.TEST_DURATION)
        metrics = tracker.get_metrics()
        assert len(metrics) == 2

    def test_get_metrics_by_type(self):
        """Test filtering metrics by type."""
        tracker = MetricsTracker()
        tracker.record_metric("build1", 10, MetricType.BUILD_TIME)
        tracker.record_metric("build2", 15, MetricType.BUILD_TIME)
        tracker.record_metric("test1", 100, MetricType.TEST_DURATION)
        metrics = tracker.get_metrics(MetricType.BUILD_TIME)
        assert len(metrics) == 2

    def test_get_metrics_by_tags(self):
        """Test filtering metrics by tags."""
        tracker = MetricsTracker()
        tracker.record_metric("m1", 10, tags={"env": "prod"})
        tracker.record_metric("m2", 20, tags={"env": "staging"})
        metrics = tracker.get_metrics(tag_filter={"env": "prod"})
        assert len(metrics) == 1
        assert metrics[0].value == 10

    def test_get_empty_metrics(self):
        """Test getting metrics from empty tracker."""
        tracker = MetricsTracker()
        metrics = tracker.get_metrics()
        assert len(metrics) == 0


class TestMetricsTrackerStatistics:
    """Test statistics calculation."""

    def test_calculate_statistics(self):
        """Test calculating statistics."""
        tracker = MetricsTracker()
        tracker.record_metric("time1", 10, MetricType.BUILD_TIME)
        tracker.record_metric("time2", 20, MetricType.BUILD_TIME)
        tracker.record_metric("time3", 30, MetricType.BUILD_TIME)
        stats = tracker.calculate_statistics(MetricType.BUILD_TIME)
        assert stats["count"] == 3
        assert stats["mean"] == 20
        assert stats["min"] == 10
        assert stats["max"] == 30
        assert stats["total"] == 60

    def test_calculate_statistics_empty(self):
        """Test calculating statistics with no metrics."""
        tracker = MetricsTracker()
        stats = tracker.calculate_statistics(MetricType.BUILD_TIME)
        assert stats["count"] == 0
        assert stats["mean"] == 0

    def test_calculate_statistics_all_types(self):
        """Test calculating statistics without type filter."""
        tracker = MetricsTracker()
        tracker.record_metric("m1", 10, MetricType.BUILD_TIME)
        tracker.record_metric("m2", 20, MetricType.TEST_DURATION)
        stats = tracker.calculate_statistics()
        assert stats["count"] == 2
        assert stats["total"] == 30

    def test_get_metric_summary(self):
        """Test getting summary by metric type."""
        tracker = MetricsTracker()
        tracker.record_metric("build1", 30, MetricType.BUILD_TIME)
        tracker.record_metric("build2", 40, MetricType.BUILD_TIME)
        tracker.record_metric("test1", 100, MetricType.TEST_DURATION)
        summary = tracker.get_metric_summary()
        assert "build_time" in summary
        assert "test_duration" in summary
        assert summary["build_time"]["count"] == 2


class TestMetricsTrackerExport:
    """Test exporting metrics."""

    def test_export_metrics(self):
        """Test exporting metrics."""
        tracker = MetricsTracker()
        tracker.record_metric("m1", 100, MetricType.CUSTOM)
        tracker.record_metric("m2", 200, MetricType.CUSTOM)
        exported = tracker.export_metrics()
        assert len(exported) == 2
        assert exported[0]["name"] == "m1"

    def test_export_empty_metrics(self):
        """Test exporting empty metrics."""
        tracker = MetricsTracker()
        exported = tracker.export_metrics()
        assert len(exported) == 0


class TestMetricsTrackerManagement:
    """Test metrics management."""

    def test_clear_metrics(self):
        """Test clearing metrics."""
        tracker = MetricsTracker()
        tracker.record_metric("m1", 10)
        assert len(tracker.metrics) == 1
        tracker.clear_metrics()
        assert len(tracker.metrics) == 0
