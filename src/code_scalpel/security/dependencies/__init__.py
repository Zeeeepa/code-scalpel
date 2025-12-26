"""
Dependencies - Dependency vulnerability scanning.

[20251225_FEATURE] Created as part of Project Reorganization Issue #10.

This module contains dependency analysis tools:
- vulnerability_scanner.py: Dependency vulnerability scanning (OSV API)
- osv_client.py: OSV API client (moved from ast_tools/ in Phase 4)
"""

from .vulnerability_scanner import (
    VulnerabilityScanner,
    ScanResult,
    VulnerabilityFinding,
    DependencyParser,  # [20251225_BUGFIX] Export for MCP tools
)

# [20251225_FEATURE] OSV client (moved from ast_tools/)
from .osv_client import (
    OSVClient,
    Vulnerability,
    OSVError,
    # Constants for backward compatibility
    OSV_API_URL,
    OSV_BATCH_URL,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
)

__all__ = [
    "VulnerabilityScanner",
    "ScanResult",
    "VulnerabilityFinding",
    "DependencyParser",
    # OSV client
    "OSVClient",
    "Vulnerability",
    "OSVError",
    # OSV constants
    "OSV_API_URL",
    "OSV_BATCH_URL",
    "DEFAULT_TIMEOUT",
    "MAX_RETRIES",
    "RETRY_DELAY",
]
