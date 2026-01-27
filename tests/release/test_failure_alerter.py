"""Tests for failure alerting system."""

from code_scalpel.release.failure_alerter import (
    Alert,
    AlertChannel,
    FailureAlerter,
)


class TestAlert:
    """Test Alert class."""

    def test_create_alert(self):
        """Test creating an alert."""
        alert = Alert(title="Build Failed", message="Compilation error")
        assert alert.title == "Build Failed"
        assert alert.message == "Compilation error"
        assert alert.severity == "error"


class TestFailureAlerter:
    """Test FailureAlerter class."""

    def test_configure_channel(self):
        """Test configuring a channel."""
        alerter = FailureAlerter()
        alerter.configure_channel(AlertChannel.EMAIL, {"address": "admin@example.com"})
        assert AlertChannel.EMAIL in alerter.channels

    def test_list_channels(self):
        """Test listing configured channels."""
        alerter = FailureAlerter()
        alerter.configure_channel(AlertChannel.EMAIL, {})
        alerter.configure_channel(AlertChannel.SLACK, {})
        channels = alerter.list_channels()
        assert len(channels) == 2

    def test_create_alert(self):
        """Test creating an alert."""
        alerter = FailureAlerter()
        alert = alerter.create_alert("Test", "Message")
        assert len(alerter.alerts) == 1
        assert alert.title == "Test"

    def test_send_console_alert(self):
        """Test sending console alert."""
        alerter = FailureAlerter()
        alerter.configure_channel(AlertChannel.CONSOLE, {})
        result = alerter.send_alert("Title", "Message", AlertChannel.CONSOLE)
        assert result is True

    def test_send_alert_unconfigured_channel(self):
        """Test sending alert to unconfigured channel."""
        alerter = FailureAlerter()
        result = alerter.send_alert("Title", "Message", AlertChannel.EMAIL)
        assert result is False

    def test_register_handler(self):
        """Test registering custom handler."""
        alerter = FailureAlerter()
        alerter.configure_channel(AlertChannel.SLACK, {"webhook": "http://example.com"})
        handler_called = []

        def custom_handler(alert):
            handler_called.append(alert)
            return True

        alerter.register_handler(AlertChannel.SLACK, custom_handler)
        alerter.send_alert("Test", "Message", AlertChannel.SLACK)
        assert len(handler_called) == 1

    def test_get_alerts(self):
        """Test getting alerts."""
        alerter = FailureAlerter()
        alerter.create_alert("Alert1", "Message1", channel=AlertChannel.EMAIL)
        alerter.create_alert("Alert2", "Message2", channel=AlertChannel.SLACK)
        alerts = alerter.get_alerts()
        assert len(alerts) == 2

    def test_get_alerts_by_channel(self):
        """Test getting alerts filtered by channel."""
        alerter = FailureAlerter()
        alerter.create_alert("Alert1", "Message1", channel=AlertChannel.EMAIL)
        alerter.create_alert("Alert2", "Message2", channel=AlertChannel.SLACK)
        alerts = alerter.get_alerts(AlertChannel.EMAIL)
        assert len(alerts) == 1
        assert alerts[0].title == "Alert1"

    def test_clear_alerts(self):
        """Test clearing alerts."""
        alerter = FailureAlerter()
        alerter.create_alert("Alert1", "Message1")
        assert len(alerter.alerts) == 1
        alerter.clear_alerts()
        assert len(alerter.alerts) == 0
