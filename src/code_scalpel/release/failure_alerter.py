"""Failure notifications and alerting system."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Optional


class AlertChannel(str, Enum):
    """Types of alert channels."""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    CONSOLE = "console"


@dataclass
class Alert:
    """Represents an alert."""

    title: str
    message: str
    severity: str = "error"
    timestamp: datetime = None
    channel: AlertChannel = AlertChannel.CONSOLE

    def __post_init__(self):
        """Initialize timestamp."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


class FailureAlerter:
    """Send alerts on release failures."""

    def __init__(self):
        """Initialize failure alerter."""
        self.alerts: list[Alert] = []
        self.channels: dict[AlertChannel, dict] = {}
        self.handlers: dict[AlertChannel, Callable] = {}

    def configure_channel(self, channel: AlertChannel, config: dict) -> None:
        """Configure a notification channel."""
        self.channels[channel] = config

    def list_channels(self) -> list[AlertChannel]:
        """List configured channels."""
        return list(self.channels.keys())

    def register_handler(self, channel: AlertChannel, handler: Callable) -> None:
        """Register a handler for a channel."""
        self.handlers[channel] = handler

    def create_alert(
        self,
        title: str,
        message: str,
        severity: str = "error",
        channel: AlertChannel = AlertChannel.CONSOLE,
    ) -> Alert:
        """Create an alert."""
        alert = Alert(
            title=title,
            message=message,
            severity=severity,
            channel=channel,
        )
        self.alerts.append(alert)
        return alert

    def send_alert(
        self,
        title: str,
        message: str,
        channel: AlertChannel = AlertChannel.CONSOLE,
        severity: str = "error",
    ) -> bool:
        """Send an alert through a channel."""
        alert = self.create_alert(title, message, severity, channel)

        if channel not in self.channels:
            return False

        if channel in self.handlers:
            return self.handlers[channel](alert)

        if channel == AlertChannel.CONSOLE:
            print(f"[{severity.upper()}] {title}: {message}")
            return True

        return False

    def get_alerts(self, channel: Optional[AlertChannel] = None) -> list[Alert]:
        """Get alerts, optionally filtered by channel."""
        if channel is None:
            return self.alerts
        return [a for a in self.alerts if a.channel == channel]

    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()
