"""Publishing status dashboard and monitoring."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PublishStatus(str, Enum):
    """Status of a publishing operation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class PublishEvent:
    """Represents a publishing event."""

    stage: str
    status: PublishStatus
    timestamp: datetime
    message: str = ""
    details: dict | None = None

    def __post_init__(self):
        """Initialize details."""
        if self.details is None:
            self.details = {}


class StatusDashboard:
    """Real-time publishing status tracking."""

    def __init__(self):
        """Initialize status dashboard."""
        self.events: list[PublishEvent] = []
        self.current_version: str = ""
        self.overall_status = PublishStatus.PENDING

    def update_status(
        self, stage: str, status: PublishStatus, message: str = ""
    ) -> PublishEvent:
        """Update status for a stage."""
        event = PublishEvent(
            stage=stage,
            status=status,
            timestamp=datetime.now(),
            message=message,
        )
        self.events.append(event)
        if status == PublishStatus.FAILED:
            self.overall_status = PublishStatus.FAILED
        elif status == PublishStatus.IN_PROGRESS:
            self.overall_status = PublishStatus.IN_PROGRESS
        elif (
            status == PublishStatus.COMPLETED
            and self.overall_status != PublishStatus.FAILED
        ):
            self.overall_status = PublishStatus.COMPLETED
        return event

    def get_current_status(self) -> dict:
        """Get current overall status."""
        return {
            "overall_status": self.overall_status.value,
            "version": self.current_version,
            "last_update": (
                self.events[-1].timestamp.isoformat() if self.events else None
            ),
            "total_events": len(self.events),
        }

    def render_dashboard(self) -> str:
        """Render dashboard as text."""
        lines = [
            "=== Release Status Dashboard ===",
            f"Version: {self.current_version}",
            f"Overall Status: {self.overall_status.value.upper()}",
            "",
            "Event History:",
        ]
        for event in self.events:
            lines.append(
                f"  [{event.timestamp.strftime('%H:%M:%S')}] {event.stage}: {event.status.value}"
            )
            if event.message:
                lines.append(f"    → {event.message}")
        return "\n".join(lines)

    def export_status(self) -> dict:
        """Export status as dictionary."""
        return {
            "status": self.overall_status.value,
            "version": self.current_version,
            "events": [
                {
                    "stage": e.stage,
                    "status": e.status.value,
                    "timestamp": e.timestamp.isoformat(),
                    "message": e.message,
                }
                for e in self.events
            ],
        }

    def clear_events(self) -> None:
        """Clear all events."""
        self.events.clear()
