from __future__ import annotations

import logging
import os
import threading
from concurrent.futures import (ProcessPoolExecutor, ThreadPoolExecutor,
                                as_completed)
from pathlib import Path
from typing import (Callable, Dict, Generic, List, Optional, Sequence, Tuple,
                    TypeVar)

# [20251223_CONSOLIDATION] Import from unified_cache
from .unified_cache import AnalysisCache

logger = logging.getLogger(__name__)

T = TypeVar("T")


# [20251214_PERF] Batch worker - parse multiple files per worker
def _batch_parse_worker(
    file_paths: List[str], parse_fn: Callable[[Path], T]
) -> List[Tuple[str, T | None, str | None]]:
    """Parse a batch of files, returning (path, result, error) tuples."""
    results = []
    for file_path in file_paths:
        try:
            path = Path(file_path)
            value = parse_fn(path)
            results.append((file_path, value, None))
        except Exception as exc:
            results.append((file_path, None, str(exc)))
    return results


class ParallelParser(Generic[T]):
    """[20251214_FEATURE] Parallel file parsing with cache reuse.

    TODO ITEMS: cache/parallel_parser.py
    ======================================================================
    COMMUNITY TIER - Core Parallel Parsing
    ======================================================================
    1. Add ParallelParser.parse_files() batch parsing
    2. Add ParallelParser.parse_one() single file parsing
    3. Add ParallelParser.get_results() result collection
    4. Add ParallelParser.get_errors() error handling
    5. Add batch worker function with error recovery
    6. Add process pool executor with threading fallback
    7. Add thread pool executor support
    8. Add worker batch creation (DEFAULT_BATCH_SIZE)
    9. Add cache lookup for already-parsed files
    10. Add results dict collection
    11. Add error list accumulation
    12. Add future handling with as_completed
    13. Add worker exception handling
    14. Add file resolution with Path.resolve()
    15. Add parse function invocation
    16. Add result tuple unpacking
    17. Add worker threading detection
    18. Add main thread detection
    19. Add worker count detection (cpu_count)
    20. Add batch size configuration
    21. Add parse progress tracking
    22. Add timing metrics collection
    23. Add cache hit/miss counting
    24. Add file parsing statistics
    25. Add error reporting and logging

    ======================================================================
    PRO TIER - Advanced Parallel Parsing
    ======================================================================
    26. Add implement adaptive batch sizing based on file sizes
    27. Add progress callbacks for long-running operations
    28. Add per-worker timeout to handle hung workers
    29. Add priority-based scheduling (prioritize hot files)
    30. Add implement memory-aware batching to prevent OOM
    31. Add worker affinity/pinning for NUMA systems
    32. Add dynamic worker scaling based on load
    33. Add incremental result streaming
    34. Add parse job queuing system
    35. Add worker health monitoring
    36. Add graceful worker shutdown
    37. Add worker restart on failure
    38. Add parse caching across runs
    39. Add incremental parsing (delta updates)
    40. Add parse result validation
    41. Add distributed parsing support
    42. Add parse scheduling optimization
    43. Add parse dependency ordering
    44. Add parse resource pooling
    45. Add parse memory pooling
    46. Add parse profiling instrumentation
    47. Add parse performance optimization
    48. Add parse cancellation support
    49. Add parse retry logic
    50. Add parse load balancing

    ======================================================================
    ENTERPRISE TIER - Distributed & Federated Parsing
    ======================================================================
    51. Add distributed parsing across agents
    52. Add federated parsing across organizations
    53. Add multi-region parsing coordination
    54. Add parsing consensus and voting
    55. Add distributed parsing locking
    56. Add parse event streaming
    57. Add parse change notifications
    58. Add parse cost tracking per org
    59. Add parse quota enforcement
    60. Add parse SLA monitoring
    61. Add parse audit trail logging
    62. Add parse access control (RBAC)
    63. Add parse multi-tenancy isolation
    64. Add parse disaster recovery
    65. Add parse cross-region failover
    66. Add parse data retention policies
    67. Add parse billing integration
    68. Add parse executive reporting
    69. Add parse anomaly detection
    70. Add parse circuit breaker
    71. Add parse health monitoring
    72. Add parse chaos engineering tests
    73. Add parse capacity planning
    74. Add parse AI-based optimization
    75. Add parse predictive prefetching

    [20251221_TODO] Phase 2: Implement memory-aware batching to prevent OOM
    """

    # [20251214_PERF] Default batch size to amortize pickle overhead
    DEFAULT_BATCH_SIZE = 100

    def __init__(
        self,
        cache: AnalysisCache[T],
        max_workers: Optional[int] = None,
        batch_size: Optional[int] = None,
    ) -> None:
        self.cache = cache
        self.max_workers = max_workers or os.cpu_count() or 1
        self.batch_size = batch_size or self.DEFAULT_BATCH_SIZE

    def parse_files(
        self, files: Sequence[Path | str], parse_fn: Callable[[Path], T]
    ) -> Tuple[Dict[str, T], List[str]]:
        """Parse multiple files in parallel with caching.

        [20251221_TODO] Phase 2: Add progress callback parameter for UI feedback
        [20251221_TODO] Phase 2: Implement timeout per worker thread
        [20251221_TODO] Phase 2: Add support for cancellation tokens
        [20251221_TODO] Phase 2: Return detailed metrics (parse time per file)
        """
        results: Dict[str, T] = {}
        errors: List[str] = []
        to_parse: List[str] = []

        for file_path in files:
            path = Path(file_path).resolve()
            cached = self.cache.get_cached(path)
            if cached is not None:
                results[str(path)] = cached
            else:
                to_parse.append(str(path))

        if to_parse:
            # [20251214_PERF] Batch files to reduce per-file pickle overhead
            batches = [
                to_parse[i : i + self.batch_size]
                for i in range(0, len(to_parse), self.batch_size)
            ]

            # Spawning/forking processes from a non-main thread can hang on some
            # platforms/configs. Since this parser may be invoked from MCP tool
            # handlers running in worker threads (e.g., stdio/async transports),
            # fall back to threads when not on the main thread.
            executor_cls = (
                ProcessPoolExecutor
                if threading.current_thread() is threading.main_thread()
                else ThreadPoolExecutor
            )

            with executor_cls(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(_batch_parse_worker, batch, parse_fn): batch
                    for batch in batches
                }
                for future in as_completed(futures):
                    batch = futures[future]
                    try:
                        batch_results = future.result()
                        for file_path, value, error in batch_results:
                            if error is None and value is not None:
                                results[file_path] = value
                                self.cache.store(file_path, value)
                            else:
                                logger.warning(
                                    "Parse failed for %s: %s", file_path, error
                                )
                                errors.append(file_path)
                    except Exception as exc:
                        logger.warning(
                            "Batch parse failed for %d files: %s", len(batch), exc
                        )
                        errors.extend(batch)

        return results, errors
