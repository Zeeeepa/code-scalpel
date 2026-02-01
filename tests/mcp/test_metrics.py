"""Tests for metrics and telemetry tracking.

This test suite validates:
- Suggestion metric tracking
- Outcome reporting and matching
- Statistics aggregation
- CSV export
- File persistence
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path


from code_scalpel.mcp.metrics import (
    MetricsCollector,
    SuggestionMetric,
    SuggestionOutcome,
    SuggestionType,
    get_metrics_collector,
    set_metrics_persistence,
)


class TestSuggestionMetric:
    """Test SuggestionMetric data class."""

    def test_create_metric(self):
        """Can create a suggestion metric."""
        metric = SuggestionMetric(
            timestamp=datetime.utcnow(),
            request_id="req_123",
            tool_id="analyze_code",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions_offered=["process_data", "process_item"],
        )
        assert metric.request_id == "req_123"
        assert metric.tool_id == "analyze_code"
        assert len(metric.suggestions_offered) == 2
        assert metric.outcome == SuggestionOutcome.PENDING

    def test_metric_to_dict(self):
        """Metric can be serialized to dict."""
        metric = SuggestionMetric(
            timestamp=datetime(2024, 1, 15, 10, 30, 45),
            request_id="req_123",
            tool_id="analyze_code",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions_offered=["process_data"],
            agent_choice="process_data",
            outcome=SuggestionOutcome.ACCEPTED,
            accuracy_score=0.95,
        )
        data = metric.to_dict()
        assert data["request_id"] == "req_123"
        assert data["suggestion_type"] == "symbol_typo"
        assert data["outcome"] == "accepted"
        assert data["accuracy_score"] == 0.95

    def test_metric_from_dict(self):
        """Metric can be deserialized from dict."""
        original = SuggestionMetric(
            timestamp=datetime(2024, 1, 15, 10, 30, 45),
            request_id="req_123",
            tool_id="analyze_code",
            suggestion_type=SuggestionType.IMPORT_MISSING,
            suggestions_offered=["from os import path"],
            context={"missing_import": "path"},
        )
        data = original.to_dict()
        restored = SuggestionMetric.from_dict(data)
        assert restored.request_id == original.request_id
        assert restored.suggestion_type == SuggestionType.IMPORT_MISSING
        assert restored.context == {"missing_import": "path"}


class TestMetricsCollectorTracking:
    """Test metric tracking in MetricsCollector."""

    def test_track_suggestion(self):
        """Can track a suggestion."""
        collector = MetricsCollector()
        metric = collector.track_suggestion(
            request_id="req_001",
            tool_id="validator",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions=["correct_symbol"],
        )
        assert metric.request_id == "req_001"
        assert metric.outcome == SuggestionOutcome.PENDING

    def test_track_multiple_suggestions(self):
        """Can track multiple suggestions."""
        collector = MetricsCollector()
        for i in range(5):
            collector.track_suggestion(
                request_id=f"req_{i}",
                tool_id="validator",
                suggestion_type=SuggestionType.SYMBOL_TYPO,
                suggestions=[f"option_{i}"],
            )
        stats = collector.get_statistics()
        assert stats["total_suggestions"] == 5

    def test_report_outcome_accepted(self):
        """Can report suggestion was accepted."""
        collector = MetricsCollector()
        collector.track_suggestion(
            request_id="req_001",
            tool_id="validator",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions=["correct_name"],
        )
        success = collector.report_outcome(
            request_id="req_001",
            outcome=SuggestionOutcome.ACCEPTED,
            agent_choice="correct_name",
            accuracy_score=1.0,
        )
        assert success is True
        stats = collector.get_statistics()
        assert stats["acceptance_rate"] == 1.0

    def test_report_outcome_ignored(self):
        """Can report suggestion was ignored."""
        collector = MetricsCollector()
        collector.track_suggestion(
            request_id="req_001",
            tool_id="validator",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions=["option_a", "option_b"],
        )
        success = collector.report_outcome(
            request_id="req_001",
            outcome=SuggestionOutcome.IGNORED,
            accuracy_score=0.5,
        )
        assert success is True
        stats = collector.get_statistics()
        assert stats["counts"]["ignored"] == 1
        assert stats["acceptance_rate"] == 0.0

    def test_report_outcome_not_found(self):
        """Returns False if request ID not found."""
        collector = MetricsCollector()
        collector.track_suggestion(
            request_id="req_001",
            tool_id="validator",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions=["option"],
        )
        success = collector.report_outcome(
            request_id="req_999",  # Non-existent
            outcome=SuggestionOutcome.ACCEPTED,
        )
        assert success is False

    def test_report_outcome_matching_pending(self):
        """Only matches PENDING outcomes (not already reported)."""
        collector = MetricsCollector()
        collector.track_suggestion(
            request_id="req_001",
            tool_id="validator",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions=["option"],
        )
        # First report succeeds
        assert (
            collector.report_outcome(
                request_id="req_001",
                outcome=SuggestionOutcome.ACCEPTED,
            )
            is True
        )

        # Second report with same request_id fails (now it's ACCEPTED, not PENDING)
        assert (
            collector.report_outcome(
                request_id="req_001",
                outcome=SuggestionOutcome.IGNORED,
            )
            is False
        )


class TestMetricsStatistics:
    """Test statistics aggregation."""

    def test_empty_statistics(self):
        """Empty collector has zero statistics."""
        collector = MetricsCollector()
        stats = collector.get_statistics()
        assert stats["total_suggestions"] == 0
        assert stats["acceptance_rate"] == 0.0
        assert stats["avg_accuracy"] == 0.0

    def test_acceptance_rate_calculation(self):
        """Acceptance rate is correct."""
        collector = MetricsCollector()
        # Track 4 suggestions
        for i in range(4):
            collector.track_suggestion(
                request_id=f"req_{i}",
                tool_id="validator",
                suggestion_type=SuggestionType.SYMBOL_TYPO,
                suggestions=["option"],
            )

        # Accept 3, ignore 1
        collector.report_outcome("req_0", SuggestionOutcome.ACCEPTED)
        collector.report_outcome("req_1", SuggestionOutcome.ACCEPTED)
        collector.report_outcome("req_2", SuggestionOutcome.ACCEPTED)
        collector.report_outcome("req_3", SuggestionOutcome.IGNORED)

        stats = collector.get_statistics()
        assert stats["counts"]["accepted"] == 3
        assert stats["counts"]["ignored"] == 1
        assert stats["acceptance_rate"] == 0.75

    def test_accuracy_score_averaging(self):
        """Average accuracy is calculated correctly."""
        collector = MetricsCollector()
        collector.track_suggestion(
            request_id="req_1",
            tool_id="validator",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions=["option"],
        )
        collector.track_suggestion(
            request_id="req_2",
            tool_id="validator",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions=["option"],
        )

        collector.report_outcome(
            "req_1", SuggestionOutcome.ACCEPTED, accuracy_score=0.8
        )
        collector.report_outcome(
            "req_2", SuggestionOutcome.ACCEPTED, accuracy_score=0.6
        )

        stats = collector.get_statistics()
        assert stats["avg_accuracy"] == 0.7

    def test_statistics_by_type(self):
        """Statistics breakdown by suggestion type."""
        collector = MetricsCollector()

        # Track typos
        collector.track_suggestion(
            request_id="req_1",
            tool_id="validator",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions=["correct"],
        )
        collector.track_suggestion(
            request_id="req_2",
            tool_id="validator",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions=["correct"],
        )

        # Track imports
        collector.track_suggestion(
            request_id="req_3",
            tool_id="validator",
            suggestion_type=SuggestionType.IMPORT_MISSING,
            suggestions=["from x import y"],
        )

        # Report outcomes
        collector.report_outcome(
            "req_1", SuggestionOutcome.ACCEPTED, accuracy_score=1.0
        )
        collector.report_outcome("req_2", SuggestionOutcome.IGNORED, accuracy_score=0.0)
        collector.report_outcome(
            "req_3", SuggestionOutcome.ACCEPTED, accuracy_score=0.9
        )

        stats = collector.get_statistics()
        by_type = stats["by_type"]

        assert by_type["symbol_typo"]["count"] == 2
        assert by_type["symbol_typo"]["accepted"] == 1
        assert by_type["symbol_typo"]["acceptance_rate"] == 0.5

        assert by_type["import_missing"]["count"] == 1
        assert by_type["import_missing"]["accepted"] == 1
        assert by_type["import_missing"]["acceptance_rate"] == 1.0

    def test_completion_rate(self):
        """Completion rate includes all resolved outcomes."""
        collector = MetricsCollector()

        # Track 5 suggestions
        for i in range(5):
            collector.track_suggestion(
                request_id=f"req_{i}",
                tool_id="validator",
                suggestion_type=SuggestionType.SYMBOL_TYPO,
                suggestions=["option"],
            )

        # Report 3 outcomes
        collector.report_outcome("req_0", SuggestionOutcome.ACCEPTED)
        collector.report_outcome("req_1", SuggestionOutcome.IGNORED)
        collector.report_outcome("req_2", SuggestionOutcome.PARTIALLY_USED)

        stats = collector.get_statistics()
        assert stats["total_suggestions"] == 5
        assert stats["completed_outcomes"] == 3
        assert stats["completion_rate"] == 0.6
        assert stats["counts"]["pending"] == 2


class TestMetricsPersistence:
    """Test file persistence and loading."""

    def test_persist_to_file(self):
        """Can persist metrics to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "metrics.json"
            collector = MetricsCollector(persist_path=path)

            # Track and report
            collector.track_suggestion(
                request_id="req_1",
                tool_id="validator",
                suggestion_type=SuggestionType.SYMBOL_TYPO,
                suggestions=["correct"],
            )
            collector.report_outcome("req_1", SuggestionOutcome.ACCEPTED)

            # Persist
            result_path = collector.persist_to_file()
            assert result_path.exists()

            # Verify file contents
            with open(result_path) as f:
                data = json.load(f)
            assert data["total_metrics"] == 1
            assert data["metrics"][0]["request_id"] == "req_1"
            assert data["statistics"]["acceptance_rate"] == 1.0

    def test_load_from_file(self):
        """Can load persisted metrics from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "metrics.json"

            # Create and persist metrics
            collector1 = MetricsCollector(persist_path=path)
            collector1.track_suggestion(
                request_id="req_1",
                tool_id="validator",
                suggestion_type=SuggestionType.IMPORT_MISSING,
                suggestions=["from x import y"],
            )
            collector1.report_outcome(
                "req_1", SuggestionOutcome.ACCEPTED, accuracy_score=0.9
            )
            collector1.persist_to_file()

            # Load in new collector
            collector2 = MetricsCollector(persist_path=path)
            stats = collector2.get_statistics()

            assert stats["total_suggestions"] == 1
            assert stats["acceptance_rate"] == 1.0
            assert stats["avg_accuracy"] == 0.9


class TestMetricsExport:
    """Test exporting metrics in various formats."""

    def test_export_csv(self):
        """Can export metrics to CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "metrics.csv"
            collector = MetricsCollector()

            # Track a few metrics
            collector.track_suggestion(
                request_id="req_1",
                tool_id="validator",
                suggestion_type=SuggestionType.SYMBOL_TYPO,
                suggestions=["correct_name"],
            )
            collector.track_suggestion(
                request_id="req_2",
                tool_id="validator",
                suggestion_type=SuggestionType.IMPORT_MISSING,
                suggestions=["from x import y", "from z import w"],
            )

            collector.report_outcome(
                "req_1", SuggestionOutcome.ACCEPTED, accuracy_score=1.0
            )
            collector.report_outcome(
                "req_2", SuggestionOutcome.IGNORED, accuracy_score=0.5
            )

            # Export
            result_path = collector.export_csv(csv_path)
            assert result_path.exists()

            # Verify CSV contents
            with open(result_path) as f:
                lines = f.readlines()

            assert len(lines) == 3  # Header + 2 metrics
            assert "req_1" in lines[1]
            assert "correct_name" in lines[1]
            assert "req_2" in lines[2]
            assert "from x import y|from z import w" in lines[2]


class TestMetricsGlobalInstance:
    """Test global metrics collector instance."""

    def test_get_metrics_collector(self):
        """Can get global metrics collector."""
        collector = get_metrics_collector()
        assert collector is not None
        assert isinstance(collector, MetricsCollector)

    def test_set_metrics_persistence(self):
        """Can set global persistence path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "metrics.json"
            set_metrics_persistence(path)

            collector = get_metrics_collector()
            assert collector._persist_path == path


class TestMetricsThreadSafety:
    """Test thread safety of metrics collector."""

    def test_concurrent_tracking(self):
        """Multiple threads can track simultaneously."""
        import threading

        collector = MetricsCollector()

        def track_suggestions(thread_id: int):
            for i in range(10):
                collector.track_suggestion(
                    request_id=f"req_t{thread_id}_i{i}",
                    tool_id="validator",
                    suggestion_type=SuggestionType.SYMBOL_TYPO,
                    suggestions=["option"],
                )

        threads = [
            threading.Thread(target=track_suggestions, args=(i,)) for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = collector.get_statistics()
        assert stats["total_suggestions"] == 50

    def test_concurrent_reporting(self):
        """Multiple threads can report outcomes simultaneously."""
        import threading

        collector = MetricsCollector()

        # Pre-track suggestions
        for i in range(50):
            collector.track_suggestion(
                request_id=f"req_{i}",
                tool_id="validator",
                suggestion_type=SuggestionType.SYMBOL_TYPO,
                suggestions=["option"],
            )

        def report_outcomes(thread_id: int):
            for i in range(10):
                req_id = f"req_{thread_id * 10 + i}"
                collector.report_outcome(req_id, SuggestionOutcome.ACCEPTED)

        threads = [
            threading.Thread(target=report_outcomes, args=(i,)) for i in range(5)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = collector.get_statistics()
        assert stats["completed_outcomes"] == 50
        assert stats["acceptance_rate"] == 1.0
