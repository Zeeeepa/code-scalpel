"""
Codebase Session Manager

Manages Codebase instances per MCP session with caching.
"""

import time
import threading
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from collections import OrderedDict
import logging

from code_scalpel.core.codegen_bridge import get_bridge

logger = logging.getLogger(__name__)


@dataclass
class SessionContext:
    """Context for a single MCP session"""
    session_id: str
    workspace_path: Path
    codebase: Any
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    
    def touch(self):
        self.last_accessed = time.time()


class LRUCache:
    """Thread-safe LRU cache"""
    
    def __init__(self, maxsize: int = 1000):
        self.maxsize = maxsize
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def put(self, key: str, value: Any):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.maxsize:
                    self.cache.popitem(last=False)
            self.cache[key] = value


class CodebaseSessionManager:
    """Manages Codebase instances per MCP session"""
    
    def __init__(self, max_sessions: int = 100, cache_size: int = 1000):
        self.max_sessions = max_sessions
        self._sessions: Dict[str, SessionContext] = {}
        self._cache = LRUCache(maxsize=cache_size)
        self._lock = threading.RLock()
        self._bridge = get_bridge()
    
    def create_session(self, session_id: str, workspace_path: Path) -> SessionContext:
        with self._lock:
            if session_id in self._sessions:
                return self._sessions[session_id]
            
            if len(self._sessions) >= self.max_sessions:
                raise RuntimeError(f"Max sessions ({self.max_sessions}) exceeded")
            
            if not self._bridge.is_available:
                raise RuntimeError("Codegen is not available")
            
            codebase = self._bridge.create_codebase(workspace_path)
            context = SessionContext(
                session_id=session_id,
                workspace_path=workspace_path,
                codebase=codebase
            )
            self._sessions[session_id] = context
            return context
    
    def get_session(self, session_id: str) -> Optional[SessionContext]:
        with self._lock:
            context = self._sessions.get(session_id)
            if context:
                context.touch()
            return context


_manager: Optional[CodebaseSessionManager] = None


def get_session_manager() -> CodebaseSessionManager:
    global _manager
    if _manager is None:
        _manager = CodebaseSessionManager()
    return _manager

