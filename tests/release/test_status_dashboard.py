"""Tests for status dashboard system."""

from datetime import datetime


from code_scalpel.release.status_dashboard import (
    PublishStatus,
    PublishEvent,
    StatusDashboard,
)


class TestPublishEvent:
    """Test PublishEvent class."""

    def test_create_event(self):
        """Test creating an event."""
        event = PublishEvent(
            stage="build",
            status=PublishStatus.COMPLETED,
            timestamp=datetime.now(),
        )
        assert event.stage == "build"
        assert event.status == PublishStatus.COMPLETED


class TestStatusDashboard:
    """Test StatusDashboard class."""

    def test_update_status(self):
        """Test updating status."""
        dashboard = StatusDashboard()
        event = dashboard.update_status("build", PublishStatus.COMPLETED)
        assert len(dashboard.events) == 1
        assert event.stage == "build"

    def test_multiple_updates(self):
        """Test multiple status updates."""
        dashboard = StatusDashboard()
        dashboard.update_status("build", PublishStatus.IN_PROGRESS)
        dashboard.update_status("test", PublishStatus.IN_PROGRESS)
        dashboard.update_status("publish", PublishStatus.COMPLETED)
        assert len(dashboard.events) == 3

    def test_get_current_status(self):
        """Test getting current status."""
        dashboard = StatusDashboard()
        dashboard.current_version = "1.0.0"
        dashboard.update_status("build", PublishStatus.COMPLETED)
        status = dashboard.get_current_status()
        assert status["version"] == "1.0.0"
        assert status["overall_status"] == PublishStatus.COMPLETED.value

    def test_failure_updates_overall_status(self):
        """Test that failure updates overall status."""
        dashboard = StatusDashboard()
        dashboard.update_status("build", PublishStatus.IN_PROGRESS)
        dashboard.update_status("build", PublishStatus.FAILED)
        assert dashboard.overall_status == PublishStatus.FAILED

    def test_render_dashboard(self):
        """Test rendering dashboard."""
        dashboard = StatusDashboard()
        dashboard.current_version = "2.0.0"
        dashboard.update_status("build", PublishStatus.COMPLETED)
        dashboard.update_status("test", PublishStatus.COMPLETED)
        output = dashboard.render_dashboard()
        assert "2.0.0" in output
        assert "build" in output
        assert "test" in output

    def test_export_status(self):
        """Test exporting status."""
        dashboard = StatusDashboard()
        dashboard.current_version = "1.5.0"
        dashboard.update_status("build", PublishStatus.COMPLETED)
        exported = dashboard.export_status()
        assert exported["version"] == "1.5.0"
        assert len(exported["events"]) == 1

    def test_clear_events(self):
        """Test clearing events."""
        dashboard = StatusDashboard()
        dashboard.update_status("build", PublishStatus.COMPLETED)
        assert len(dashboard.events) == 1
        dashboard.clear_events()
        assert len(dashboard.events) == 0
