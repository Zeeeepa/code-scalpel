from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Dict, Generic, Set, TypeVar

# [20251223_CONSOLIDATION] Import from unified_cache
from .unified_cache import AnalysisCache

logger = logging.getLogger(__name__)

T = TypeVar("T")


class IncrementalAnalyzer(Generic[T]):
    """[20251214_FEATURE] Dependency-aware incremental analysis.

    [20251221_TODO] Phase 2: Persist dependency graph to disk across restarts
    [20251221_TODO] Phase 2: Add cycle detection in dependency graph
    [20251221_TODO] Phase 2: Support bidirectional dependencies (call graphs)
    [20251221_TODO] Phase 2: Implement partial invalidation for unchanged parts
    [20251221_TODO] Phase 2: Add dependency weight tracking for prioritization
    """

    def __init__(self, cache: AnalysisCache[T]) -> None:
        self.cache = cache
        self.dependency_graph: Dict[str, Set[str]] = {}
        # [20251221_TODO] Phase 2: Add reverse graph for faster lookups

    def record_dependency(self, source: Path | str, depends_on: Path | str) -> None:
        source_key = str(Path(source).resolve())
        target_key = str(Path(depends_on).resolve())
        self.dependency_graph.setdefault(target_key, set()).add(source_key)

    def get_dependents(self, file_path: Path | str) -> Set[str]:
        return set(self.dependency_graph.get(str(Path(file_path).resolve()), set()))

    def update_file(
        self, file_path: Path | str, recompute_fn: Callable[[Path], T]
    ) -> Set[str]:
        """Update a file and return affected dependents.

        [20251221_TODO] Phase 2: Add batch update support for multiple files
        [20251221_TODO] Phase 2: Implement depth limit to prevent cascading invalidation
        [20251221_TODO] Phase 2: Return invalidation chain for debugging
        [20251221_TODO] Phase 2: Add metrics for invalidation size/depth
        """
        path = Path(file_path).resolve()
        key = str(path)

        # Invalidate the changed file and recompute
        # [20251222_BUGFIX] AnalysisCache stores file artifacts keyed by resolved path.
        # invalidate() targets analysis-result entries; invalidate_file() clears file entries.
        self.cache.invalidate_file(key)
        self.cache.get_or_parse(path, parse_fn=recompute_fn)

        affected = self.get_dependents(key)
        for dependent in affected:
            self.cache.invalidate_file(dependent)
        return affected
