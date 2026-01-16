"""Tier state and caching helpers for MCP server."""

from __future__ import annotations

from typing import Optional

CURRENT_TIER = "community"
_LAST_VALID_LICENSE_TIER: Optional[str] = None
_LAST_VALID_LICENSE_AT: Optional[float] = None
_MID_SESSION_EXPIRY_GRACE_SECONDS = 24 * 60 * 60
