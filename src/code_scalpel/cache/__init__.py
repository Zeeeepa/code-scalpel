"""Cache utilities for Code Scalpel.

[20251223_CONSOLIDATION] v3.0.5 - Unified cache merges analysis_cache.py + utilities/cache.py

[20251221_TODO] Phase 2: Add cache statistics export (Prometheus format)
[20251221_TODO] Phase 2: Implement cache warming (pre-populate on server startup)
[20251221_TODO] Phase 2: Add debugging tools (cache inspection, visualization)
[20251221_TODO] Phase 2: Support cache sharing between processes (via Redis)
[20251221_TODO] Phase 2: Add instrumentation for cache performance monitoring
"""

# [20251223_CONSOLIDATION] Export from unified cache implementation
from .unified_cache import (
    AnalysisCache,
    CacheConfig,
    CacheEntry,
    CacheStats,
    get_cache,
    reset_cache,
)
from .parallel_parser import ParallelParser
from .incremental_analyzer import IncrementalAnalyzer

__all__ = [
    "AnalysisCache",
    "CacheConfig",
    "CacheEntry",
    "CacheStats",
    "ParallelParser",
    "IncrementalAnalyzer",
    "get_cache",
    "reset_cache",
]
