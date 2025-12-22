# Archived Cache Implementations

**Archived Date:** December 23, 2025  
**Reason:** Consolidation into unified_cache.py

## Files in This Directory

### analysis_cache.py (217 LOC)
**Original Purpose:** Generic memory+disk cache for parsed artifacts  
**Key Features:**
- Memory+disk hybrid with mmap support for large files
- Simple path+hash keying
- CacheStats for hit/miss tracking

### utilities_cache.py (460 LOC)
**Original Purpose:** Content-addressable cache for code analysis results  
**Key Features:**
- SHA-256 content-addressable caching
- CacheConfig with TTL support
- Multiple result types (analysis, security, symbolic, tests)
- Dual serialization (pickle/JSON)

## Why Archived?

These two implementations were consolidated into `unified_cache.py` as part of v3.0.5 "Ninja Consolidation" release. The unified implementation combines:
- Best features from both implementations
- Eliminates 277 LOC of redundancy
- Provides unified API for all caching needs
- Maintains backward compatibility through re-exports

## Migration

All imports now resolve to `unified_cache.py`:
```python
# Old (still works due to re-exports):
from code_scalpel.cache import AnalysisCache
from code_scalpel.utilities import AnalysisCache, CacheConfig

# New (canonical):
from code_scalpel.cache import AnalysisCache, CacheConfig, get_cache
```

## For Future Reference

If you need to understand the original implementations or restore functionality:
1. These files are preserved as-is from v3.0.4
2. All tests pass with unified_cache.py
3. No functionality was lost in the consolidation
4. See `ORGANIZATIONAL_ANALYSIS.md` for detailed comparison

**Do not restore these files without updating all imports throughout the codebase.**
