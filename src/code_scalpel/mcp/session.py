"""Session counters and audit helpers for MCP server."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


_SESSION_UPDATE_COUNTS: dict[str, int] = {}
_SESSION_AUDIT_TRAIL: list[dict[str, Any]] = []


def get_session_update_count(tool_name: str) -> int:
    return _SESSION_UPDATE_COUNTS.get(tool_name, 0)


def increment_session_update_count(tool_name: str) -> int:
    current = _SESSION_UPDATE_COUNTS.get(tool_name, 0)
    _SESSION_UPDATE_COUNTS[tool_name] = current + 1
    return current + 1


def add_audit_entry(
    *,
    tool_name: str,
    file_path: str,
    target_name: str,
    operation: str,
    success: bool,
    tier: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool_name,
        "file_path": file_path,
        "target_name": target_name,
        "operation": operation,
        "success": success,
        "tier": tier,
        "metadata": metadata or {},
    }
    _SESSION_AUDIT_TRAIL.append(entry)
