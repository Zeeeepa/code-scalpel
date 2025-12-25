"""
License Cache - Cached license state for performance.

[20251225_FEATURE] Created as part of Project Reorganization Issue #4.

This module provides caching for license validation results to avoid
repeated validation checks during a session.

TODO ITEMS: cache.py
============================================================================
COMMUNITY TIER (P0-P2)
============================================================================
# [P0_CRITICAL] In-memory cache implementation
# [P1_HIGH] Cache expiration handling
# [P2_MEDIUM] Thread-safe cache access

============================================================================
PRO TIER (P1-P3)
============================================================================
# [P1_HIGH] Persistent cache to disk
# [P2_MEDIUM] Cache invalidation on license change
# [P3_LOW] Cache statistics and metrics

============================================================================
ENTERPRISE TIER (P2-P4)
============================================================================
# [P2_MEDIUM] Distributed cache support
# [P3_LOW] Cache replication
# [P4_LOW] Cache encryption
============================================================================
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """A cached license validation result."""

    tier: str
    is_valid: bool
    timestamp: float
    ttl_seconds: float

    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return time.time() > (self.timestamp + self.ttl_seconds)


class LicenseCache:
    """
    Cache for license validation results.

    Provides thread-safe caching of license validation to avoid
    repeated validation checks during normal operation.

    Usage:
        cache = LicenseCache(ttl_seconds=3600)  # 1 hour TTL

        # Store validation result
        cache.set("my_license_key", tier="pro", is_valid=True)

        # Retrieve cached result
        entry = cache.get("my_license_key")
        if entry and not entry.is_expired():
            print(f"Cached tier: {entry.tier}")
    """

    DEFAULT_TTL_SECONDS = 3600  # 1 hour

    def __init__(self, ttl_seconds: float = DEFAULT_TTL_SECONDS):
        """
        Initialize the cache.

        Args:
            ttl_seconds: Time-to-live for cache entries
        """
        self._ttl_seconds = ttl_seconds
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[CacheEntry]:
        """
        Get a cached entry.

        Args:
            key: Cache key (typically license key hash)

        Returns:
            CacheEntry if found and not expired, None otherwise
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                return None

            if entry.is_expired():
                # Remove expired entry
                del self._cache[key]
                logger.debug(f"Cache entry expired for key: {key[:8]}...")
                return None

            return entry

    def set(
        self, key: str, tier: str, is_valid: bool, ttl_seconds: Optional[float] = None
    ) -> None:
        """
        Set a cache entry.

        Args:
            key: Cache key (typically license key hash)
            tier: License tier
            is_valid: Whether license is valid
            ttl_seconds: Optional custom TTL (uses default if not specified)
        """
        with self._lock:
            self._cache[key] = CacheEntry(
                tier=tier,
                is_valid=is_valid,
                timestamp=time.time(),
                ttl_seconds=ttl_seconds or self._ttl_seconds,
            )
            logger.debug(f"Cached license validation for key: {key[:8]}...")

    def invalidate(self, key: str) -> bool:
        """
        Invalidate a cache entry.

        Args:
            key: Cache key to invalidate

        Returns:
            True if entry was found and removed
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Invalidated cache entry for key: {key[:8]}...")
                return True
            return False

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.debug(f"Cleared {count} cache entries")
            return count

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of expired entries removed
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

            return len(expired_keys)

    def size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)

    def stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._lock:
            total = len(self._cache)
            expired = sum(1 for entry in self._cache.values() if entry.is_expired())
            valid = total - expired

            return {
                "total_entries": total,
                "valid_entries": valid,
                "expired_entries": expired,
            }
