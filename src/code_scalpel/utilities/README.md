# Utilities Module

**Purpose:** Shared utilities for path resolution and caching

## Overview

This module provides utility functions used across Code Scalpel. After v3.0.5 consolidation, cache functionality is now re-exported from the main cache module.

## Key Components

### path_resolution.py (5,367 LOC)
**File path resolution and normalization**

```python
def resolve_file_path(path: str | Path, project_root: Path | None = None) -> Path:
    """Resolve relative paths to absolute paths."""
    pass

def get_workspace_root(start_path: Path | None = None) -> Path:
    """Find workspace root (looks for .git, pyproject.toml, package.json)."""
    pass

def normalize_path(path: str | Path) -> Path:
    """Normalize path (resolve .., symlinks, etc.)."""
    pass

def get_relative_path(path: Path, base: Path) -> Path:
    """Get relative path from base to path."""
    pass
```

**Key Features:**
- Cross-platform path handling (Windows/Unix)
- Workspace root detection
- Symlink resolution
- Relative path conversion

**Example:**
```python
from code_scalpel.utilities import resolve_file_path, get_workspace_root

# Resolve relative path
abs_path = resolve_file_path("src/main.py")

# Find workspace root
root = get_workspace_root()

# Get relative path
rel_path = get_relative_path(abs_path, root)
```

### Cache (Re-exported)
**Unified cache implementation**

[20251223_CONSOLIDATION] Cache functionality is now provided by `cache/unified_cache.py` and re-exported here for backward compatibility.

```python
from code_scalpel.utilities import AnalysisCache, CacheConfig, get_cache

# Get global cache
cache = get_cache()

# Or create configured cache
config = CacheConfig(max_size_mb=1000, ttl_seconds=3600)
cache = AnalysisCache(config=config)
```

**See:** `cache/README.md` for full cache documentation

## Usage

```python
from code_scalpel.utilities import (
    resolve_file_path,
    get_workspace_root,
    normalize_path,
    AnalysisCache,
    get_cache
)

# Path utilities
project_root = get_workspace_root()
file_path = resolve_file_path("src/main.py", project_root)
normalized = normalize_path(file_path)

# Cache utilities (re-exported)
cache = get_cache()
result = cache.get(code, "analysis")
```

## Integration

Used by:
- `mcp/server.py` - Path resolution for MCP tools
- `surgical_extractor.py` - File path normalization
- `project_crawler.py` - Workspace root detection
- All modules - Caching (via re-exports)

## v3.0.5 Status

- Path resolution: Stable, 100% coverage
- Cache (re-exported): Stable, 95% coverage
- Cross-platform support: Stable

## Migration Notes

**v3.0.5 Change:** Cache implementation moved to `cache/unified_cache.py` but still accessible via:
```python
from code_scalpel.utilities import AnalysisCache  # Still works!
```

**Canonical import:**
```python
from code_scalpel.cache import AnalysisCache  # Preferred in new code
```
