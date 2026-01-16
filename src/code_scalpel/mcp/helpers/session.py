"""Session management and audit logging for Code Scalpel MCP."""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("code_scalpel.mcp.session")

class SessionManager:
    """Manages session state and audit logs."""
    _instance: Optional[SessionManager] = None
    
    def __init__(self):
        self._update_counts: Dict[str, int] = defaultdict(int)
        self._audit_log: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> SessionManager:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_update_count(self, key: str) -> int:
        return self._update_counts[key]

    def increment_update_count(self, key: str) -> int:
        self._update_counts[key] += 1
        return self._update_counts[key]

    def add_audit_entry(self, entry: Dict[str, Any]) -> None:
        """Add entry with timestamp."""
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        self._audit_log.append(entry)
        # Log minimal info
        logger.info(f"AUDIT [{entry.get('operation', 'unknown')}] {entry.get('outcome', '-')}")

# Singleton accessors
def get_session_update_count(key: str) -> int:
    return SessionManager.get_instance().get_update_count(key)

def increment_session_update_count(key: str) -> int:
    return SessionManager.get_instance().increment_update_count(key)

def add_audit_entry(
    operation: str, 
    details: Dict[str, Any], 
    outcome: str = "success",
    user_id: Optional[str] = None
) -> None:
    entry = {
        "operation": operation,
        "details": details,
        "outcome": outcome,
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    SessionManager.get_instance().add_audit_entry(entry)
