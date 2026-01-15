from __future__ import annotations

import logging
import os
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Dict, Generic, List, Optional, Sequence, Tuple, TypeVar

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
    """[20251214_FEATURE] Parallel file parsing with cache reuse."""

    # TODO [COMMUNITY] Add ParallelParser.parse_one() single file parsing
    # TODO [COMMUNITY] Add ParallelParser.get_results() result collection
    # TODO [COMMUNITY] Add ParallelParser.get_errors() error handling
    # TODO [COMMUNITY] Add batch worker function with error recovery
    # TODO [COMMUNITY] Add process pool executor with threading fallback
    # TODO [COMMUNITY] Add thread pool executor support
    # TODO [COMMUNITY] Add worker batch creation (DEFAULT_BATCH_SIZE)
    # TODO [COMMUNITY] Add cache lookup for already-parsed files
    # TODO [COMMUNITY] Add results dict collection
    # TODO [COMMUNITY] Add error list accumulation
    # TODO [COMMUNITY] Add future handling with as_completed
    # TODO [COMMUNITY] Add worker exception handling
    # TODO [COMMUNITY] Add file resolution with Path.resolve()
    # TODO [COMMUNITY] Add parse function invocation
    # TODO [COMMUNITY] Add result tuple unpacking
    # TODO [COMMUNITY] Add worker threading detection
    # TODO [COMMUNITY] Add main thread detection
    # TODO [COMMUNITY] Add worker count detection (cpu_count)
    # TODO [COMMUNITY] Add batch size configuration
    # TODO [COMMUNITY] Add parse progress tracking
    # TODO [COMMUNITY] Add timing metrics collection
    # TODO [COMMUNITY] Add cache hit/miss counting
    # TODO [COMMUNITY] Add file parsing statistics
    # TODO [COMMUNITY] Add error reporting and logging
    # TODO [PRO] Add implement adaptive batch sizing based on file sizes
    # TODO [PRO] Add progress callbacks for long-running operations
    # TODO [PRO] Add per-worker timeout to handle hung workers
    # TODO [PRO] Add priority-based scheduling (prioritize hot files)
    # TODO [PRO] Add implement memory-aware batching to prevent OOM
    # TODO [PRO] Add worker affinity/pinning for NUMA systems
    # TODO [PRO] Add dynamic worker scaling based on load
    # TODO [PRO] Add incremental result streaming
    # TODO [PRO] Add parse job queuing system
    # TODO [PRO] Add worker health monitoring
    # TODO [PRO] Add graceful worker shutdown
    # TODO [PRO] Add worker restart on failure
    # TODO [PRO] Add parse caching across runs
    # TODO [PRO] Add incremental parsing (delta updates)
    # TODO [PRO] Add parse result validation
    # TODO [PRO] Add distributed parsing support
    # TODO [PRO] Add parse scheduling optimization
    # TODO [PRO] Add parse dependency ordering
    # TODO [PRO] Add parse resource pooling
    # TODO [PRO] Add parse memory pooling
    # TODO [PRO] Add parse profiling instrumentation
    # TODO [PRO] Add parse performance optimization
    # TODO [PRO] Add parse cancellation support
    # TODO [PRO] Add parse retry logic
    # TODO [PRO] Add parse load balancing
    # TODO [ENTERPRISE] Add distributed parsing across agents
    # TODO [ENTERPRISE] Add federated parsing across organizations
    # TODO [ENTERPRISE] Add multi-region parsing coordination
    # TODO [ENTERPRISE] Add parsing consensus and voting
    # TODO [ENTERPRISE] Add distributed parsing locking
    # TODO [ENTERPRISE] Add parse event streaming
    # TODO [ENTERPRISE] Add parse change notifications
    # TODO [ENTERPRISE] Add parse cost tracking per org
    # TODO [ENTERPRISE] Add parse quota enforcement
    # TODO [ENTERPRISE] Add parse SLA monitoring
    # TODO [ENTERPRISE] Add parse audit trail logging
    # TODO [ENTERPRISE] Add parse access control (RBAC)
    # TODO [ENTERPRISE] Add parse multi-tenancy isolation
    # TODO [ENTERPRISE] Add parse disaster recovery
    # TODO [ENTERPRISE] Add parse cross-region failover
    # TODO [ENTERPRISE] Add parse data retention policies
    # TODO [ENTERPRISE] Add parse billing integration
    # TODO [ENTERPRISE] Add parse executive reporting
    # TODO [ENTERPRISE] Add parse anomaly detection
    # TODO [ENTERPRISE] Add parse circuit breaker
    # TODO [ENTERPRISE] Add parse health monitoring
    # TODO [ENTERPRISE] Add parse chaos engineering tests
    # TODO [ENTERPRISE] Add parse capacity planning
    # TODO [ENTERPRISE] Add parse AI-based optimization
    # TODO [ENTERPRISE] Add parse predictive prefetching

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

        # TODO [COMMUNITY] Add progress callback parameter for UI feedback
        # TODO [COMMUNITY] Implement timeout per worker thread
        # TODO [COMMUNITY] Add support for cancellation tokens
        # TODO [COMMUNITY] Return detailed metrics (parse time per file)
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
