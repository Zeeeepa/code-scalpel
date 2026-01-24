"""Debugging helper for MCP server.

This module centralizes debug prints so they are only emitted when the
SCALPEL_MCP_OUTPUT environment variable is set to DEBUG (or TRACE).

All debug output goes to stderr and is flushed immediately to avoid
interleaving with the stdio JSON-RPC stream on stdout.
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache


@lru_cache(maxsize=1)
def debug_enabled() -> bool:
    val = os.environ.get("SCALPEL_MCP_OUTPUT", "").upper().strip()
    return val in {"DEBUG", "TRACE"}


def debug_print(*args, **kwargs) -> None:
    """Print to stderr (flushed) only when debug is enabled."""
    if not debug_enabled():
        return
    kwargs.setdefault("file", sys.stderr)
    kwargs.setdefault("flush", True)
    print(*args, **kwargs)


def debug_flush():
    """Force a stderr flush (small helper)."""
    try:
        sys.stderr.flush()
    except Exception:
        pass
