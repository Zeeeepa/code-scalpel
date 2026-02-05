"""
Configuration Loader - Load tier limits from the bundled TOML.

[20251225_FEATURE] v3.3.0 - Centralized configuration for tier limits.
[20251231_FEATURE] v3.3.1 - Added response_config.json support for output filtering.
[20260205_REFACTOR] Bundled-only limits: removed all user-override search paths.

limits.toml is packaged inside the wheel at code_scalpel/capabilities/limits.toml
(copied from .code-scalpel/limits.toml at build time via pyproject.toml force-include).
At runtime the loader reads only that bundled copy.  During development (editable
install / source checkout) it falls back to .code-scalpel/limits.toml in the repo root.
No environment-variable or filesystem overrides are honoured for limits — the file is
owned by the package build.

response_config.json (verbosity / output filtering) retains its existing user-facing
search behaviour, as that IS intended to be configurable per deployment.

Usage:
    from code_scalpel.licensing.config_loader import load_limits, load_response_config

    limits = load_limits()
    extract_limits = limits.get("pro", {}).get("extract_code", {})
    max_depth = extract_limits.get("max_depth", 2)

    # Response filtering
    response_config = load_response_config()
    filtered = filter_response(result_dict, "validate_paths", response_config)
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Python 3.11+ has tomllib built-in, earlier versions need tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        logger.warning(
            "tomli not installed and Python < 3.11. "
            "Install with: pip install tomli. "
            "Falling back to hardcoded defaults."
        )
        tomllib = None  # type: ignore


def _find_config_file() -> Optional[Path]:
    """
    Locate the bundled limits.toml.

    Resolution order (first hit wins):
        1. Package-bundled copy  – code_scalpel/capabilities/limits.toml
           (installed via hatch force-include; present in any wheel/sdist install)
        2. Dev-checkout fallback – <repo-root>/.code-scalpel/limits.toml
           (only reachable when running from a source checkout / editable install)

    No environment-variable or user-filesystem overrides are honoured.

    Returns:
        Path to limits.toml, or None if neither location exists.
    """
    # 1. Bundled copy: sits next to this file's grandparent package dir.
    #    __file__ = .../code_scalpel/licensing/config_loader.py
    #    parent.parent = .../code_scalpel/
    bundled = Path(__file__).resolve().parent.parent / "capabilities" / "limits.toml"
    if bundled.exists():
        logger.debug("Using bundled limits.toml: %s", bundled)
        return bundled

    # 2. Dev fallback: four levels up reaches the repo root when the package
    #    is installed in editable mode or run directly from a checkout.
    try:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        dev_copy = repo_root / ".code-scalpel" / "limits.toml"
        if dev_copy.exists():
            logger.debug("Dev mode: using limits.toml from %s", dev_copy)
            return dev_copy
    except Exception:
        pass

    logger.info("No limits.toml located; hardcoded defaults will be used.")
    return None


def load_limits(
    config_path: Optional[Path] = None,
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Load tier limits from TOML configuration file.

    Args:
        config_path: Optional explicit path to config file.
                    If None, searches standard locations.

    Returns:
        Nested dict: {tier: {tool: {limit_key: value}}}
        Example: {"pro": {"extract_code": {"max_depth": 2}}}

    Raises:
        No exceptions - falls back to empty dict on any error
    """
    if tomllib is None:
        logger.debug("tomllib not available, skipping config load")
        return {}

    if config_path is None:
        config_path = _find_config_file()

    if config_path is None:
        return {}

    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
            logger.debug(f"Successfully loaded {len(config)} tier sections from config")
            return config
    except Exception as e:
        logger.warning(f"Failed to load config from {config_path}: {e}")
        return {}


def get_tool_limits(
    tool_id: str,
    tier: str,
    config: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    """
    Get limits for a specific tool at a specific tier.

    Args:
        tool_id: Tool identifier (e.g., "extract_code")
        tier: Tier name ("community", "pro", "enterprise")
        config: Optional pre-loaded config dict. If None, loads from file.

    Returns:
        Dict of limit key-value pairs for this tool/tier

    Example:
        limits = get_tool_limits("extract_code", "pro")
        # Returns: {"cross_file_deps": True, "max_depth": 2, ...}
    """
    if config is None:
        config = load_limits()

    tier_config = config.get(tier, {})
    tool_limits = tier_config.get(tool_id, {})

    return tool_limits


def merge_limits(defaults: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge config overrides into default limits.

    Args:
        defaults: Default limit values from features.py
        overrides: Override values from config file

    Returns:
        Merged dict with overrides taking precedence
    """
    merged = defaults.copy()
    merged.update(overrides)
    return merged


# Cache the loaded config to avoid repeated file I/O.
# IMPORTANT: The resolved config path depends on env vars + CWD.
# To avoid stale overrides (especially in tests), we track the source file.
_config_cache: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None
_config_cache_path: Optional[str] = None
_config_cache_mtime_ns: int = -1
_config_cache_size: int = -1


def get_cached_limits() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Get cached limits config, loading if not already cached.

    Returns:
        Cached config dict
    """
    global _config_cache, _config_cache_path, _config_cache_mtime_ns, _config_cache_size

    config_path = _find_config_file()
    cache_path = str(config_path) if config_path is not None else None

    mtime_ns = -1
    size = -1
    if config_path is not None:
        try:
            stat = config_path.stat()
            mtime_ns = int(stat.st_mtime_ns)
            size = int(stat.st_size)
        except Exception:
            # If we can't stat the file, force reload.
            mtime_ns = -2
            size = -2

    if (
        _config_cache is None
        or _config_cache_path != cache_path
        or _config_cache_mtime_ns != mtime_ns
        or _config_cache_size != size
    ):
        _config_cache = load_limits(config_path=config_path)
        _config_cache_path = cache_path
        _config_cache_mtime_ns = mtime_ns
        _config_cache_size = size

    return _config_cache


def clear_cache() -> None:
    """Clear the limits and features caches, forcing reload on next access."""
    global _config_cache, _config_cache_path, _config_cache_mtime_ns, _config_cache_size
    _config_cache = None
    _config_cache_path = None
    _config_cache_mtime_ns = -1
    _config_cache_size = -1
    clear_features_cache()


def reload_config() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Force reload of limits and features from disk.

    Returns:
        Freshly loaded limits config dict
    """
    clear_cache()
    return get_cached_limits()


# ============================================================================
# Features Configuration (features.toml)
# ============================================================================


def _find_features_file() -> Optional[Path]:
    """
    Locate the bundled features.toml.

    Resolution order (first hit wins):
        1. Package-bundled copy  – code_scalpel/capabilities/features.toml
        2. Dev-checkout fallback – <repo-root>/.code-scalpel/features.toml

    No environment-variable or user-filesystem overrides are honoured.

    Returns:
        Path to features.toml, or None if neither location exists.
    """
    bundled = Path(__file__).resolve().parent.parent / "capabilities" / "features.toml"
    if bundled.exists():
        logger.debug("Using bundled features.toml: %s", bundled)
        return bundled

    try:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        dev_copy = repo_root / ".code-scalpel" / "features.toml"
        if dev_copy.exists():
            logger.debug("Dev mode: using features.toml from %s", dev_copy)
            return dev_copy
    except Exception:
        pass

    logger.info("No features.toml located; hardcoded defaults will be used.")
    return None


def load_features(
    config_path: Optional[Path] = None,
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Load feature capabilities from TOML configuration file.

    Args:
        config_path: Optional explicit path to config file.
                    If None, searches standard locations.

    Returns:
        Nested dict: {tier: {tool: {key: value}}}
        Example: {"pro": {"analyze_code": {"enabled": True, "capabilities": [...], ...}}}

    Raises:
        No exceptions – falls back to empty dict on any error.
    """
    if tomllib is None:
        logger.debug("tomllib not available, skipping features load")
        return {}

    if config_path is None:
        config_path = _find_features_file()

    if config_path is None:
        return {}

    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
            logger.debug(
                f"Successfully loaded features.toml with {len(config)} tier sections"
            )
            return config
    except Exception as e:
        logger.warning(f"Failed to load features from {config_path}: {e}")
        return {}


# Cache variables – same pattern as limits cache.
_features_cache: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None
_features_cache_path: Optional[str] = None
_features_cache_mtime_ns: int = -1
_features_cache_size: int = -1


def get_cached_features() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Get cached features config, loading if stale.

    Returns:
        Cached features config dict {tier: {tool: {key: value}}}
    """
    global _features_cache, _features_cache_path, _features_cache_mtime_ns, _features_cache_size

    config_path = _find_features_file()
    cache_path = str(config_path) if config_path is not None else None

    mtime_ns = -1
    size = -1
    if config_path is not None:
        try:
            stat = config_path.stat()
            mtime_ns = int(stat.st_mtime_ns)
            size = int(stat.st_size)
        except Exception:
            mtime_ns = -2
            size = -2

    if (
        _features_cache is None
        or _features_cache_path != cache_path
        or _features_cache_mtime_ns != mtime_ns
        or _features_cache_size != size
    ):
        _features_cache = load_features(config_path=config_path)
        _features_cache_path = cache_path
        _features_cache_mtime_ns = mtime_ns
        _features_cache_size = size

    return _features_cache


def clear_features_cache() -> None:
    """Clear the features cache, forcing reload on next access."""
    global _features_cache, _features_cache_path, _features_cache_mtime_ns, _features_cache_size
    _features_cache = None
    _features_cache_path = None
    _features_cache_mtime_ns = -1
    _features_cache_size = -1


# ============================================================================
# Response Configuration (response_config.json)
# ============================================================================

# [20251231_FEATURE] v3.3.1 - Response config loader for output filtering

_response_config_cache: Optional[Dict[str, Any]] = None
_response_config_path: Optional[str] = None
_response_config_mtime_ns: int = -1


def _find_response_config_file() -> Optional[Path]:
    """
    Find the response_config.json file using priority search order.

    Returns:
        Path to config file, or None if not found
    """
    # Priority 1: Environment variable override
    env_path = os.environ.get("CODE_SCALPEL_RESPONSE_CONFIG")
    if env_path:
        path = Path(env_path).expanduser()
        if path.exists():
            logger.info(
                f"Using response config from CODE_SCALPEL_RESPONSE_CONFIG: {path}"
            )
            return path

    # Priority 2-5: Standard search locations
    candidates = [
        Path.cwd() / ".code-scalpel" / "response_config.json",  # Project config
        Path.home() / ".code-scalpel" / "response_config.json",  # User config
        Path("/etc/code-scalpel/response_config.json"),  # System config
    ]

    # Priority 6: Package default
    try:
        import code_scalpel

        package_root = Path(code_scalpel.__file__).parent.parent.parent
        package_config = package_root / ".code-scalpel" / "response_config.json"
        if package_config.exists():
            candidates.append(package_config)
    except Exception:
        pass

    for path in candidates:
        expanded = path.expanduser()
        if expanded.exists():
            logger.debug(f"Loading response config from: {expanded}")
            return expanded

    logger.debug("No response_config.json found, using defaults")
    return None


def load_response_config(
    config_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Load response configuration from JSON file.

    Args:
        config_path: Optional explicit path to config file.
                    If None, searches standard locations.

    Returns:
        Response configuration dict with profiles and tool_overrides
    """
    import json

    if config_path is None:
        config_path = _find_response_config_file()

    if config_path is None:
        return _get_default_response_config()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            logger.debug(
                f"Loaded response config with {len(config.get('tool_overrides', {}))} tool overrides"
            )
            return config
    except Exception as e:
        logger.warning(f"Failed to load response config from {config_path}: {e}")
        return _get_default_response_config()


def _get_default_response_config() -> Dict[str, Any]:
    """Return default response configuration."""
    return {
        "global": {
            "profile": "minimal",
            "exclude_empty_arrays": True,
            "exclude_empty_objects": True,
            "exclude_null_values": True,
            "exclude_default_values": True,
        },
        "profiles": {
            "minimal": {
                "common_exclusions": [
                    "server_version",
                    "request_id",
                    "duration_ms",
                    "capabilities",
                ]
            },
            "standard": {"common_exclusions": ["server_version", "request_id"]},
            "verbose": {"common_exclusions": ["server_version"]},
            "debug": {"common_exclusions": []},
        },
        "tool_overrides": {},
    }


def get_cached_response_config() -> Dict[str, Any]:
    """
    Get cached response config, loading if not already cached.

    Returns:
        Cached config dict
    """
    global _response_config_cache, _response_config_path, _response_config_mtime_ns

    config_path = _find_response_config_file()
    cache_path = str(config_path) if config_path is not None else None

    mtime_ns = -1
    if config_path is not None:
        try:
            stat = config_path.stat()
            mtime_ns = int(stat.st_mtime_ns)
        except Exception:
            mtime_ns = -2

    if (
        _response_config_cache is None
        or _response_config_path != cache_path
        or _response_config_mtime_ns != mtime_ns
    ):
        _response_config_cache = load_response_config(config_path=config_path)
        _response_config_path = cache_path
        _response_config_mtime_ns = mtime_ns

    return _response_config_cache


def filter_response(
    result: Dict[str, Any],
    tool_id: str,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Filter response dict based on response_config.json settings.

    Removes excluded fields and empty values based on profile and tool overrides.

    Args:
        result: The result dictionary to filter
        tool_id: Tool identifier (e.g., "validate_paths")
        config: Optional pre-loaded config. If None, loads from cache.

    Returns:
        Filtered result dict with excluded fields removed
    """
    if config is None:
        config = get_cached_response_config()

    global_settings = config.get("global", {})
    profiles = config.get("profiles", {})
    tool_overrides = config.get("tool_overrides", {})

    # Get profile for this tool
    tool_config = tool_overrides.get(tool_id, {})
    profile_name = tool_config.get("profile", global_settings.get("profile", "minimal"))
    profile = profiles.get(profile_name, {})

    # Collect all fields to exclude
    exclude_fields: set = set()

    # 1. Profile common exclusions
    exclude_fields.update(profile.get("common_exclusions", []))

    # 2. Tool-specific exclusions
    exclude_fields.update(tool_config.get("exclude_fields", []))

    # Filter the result
    filtered = {}
    for key, value in result.items():
        # Skip excluded fields
        if key in exclude_fields:
            continue

        # Skip empty arrays if configured
        if (
            global_settings.get("exclude_empty_arrays", False)
            and isinstance(value, list)
            and len(value) == 0
        ):
            continue

        # Skip empty objects if configured
        if (
            global_settings.get("exclude_empty_objects", False)
            and isinstance(value, dict)
            and len(value) == 0
        ):
            continue

        # Skip null values if configured
        if global_settings.get("exclude_null_values", False) and value is None:
            continue

        filtered[key] = value

    return filtered


def clear_response_config_cache() -> None:
    """Clear the response config cache, forcing reload on next access."""
    global _response_config_cache, _response_config_path, _response_config_mtime_ns
    _response_config_cache = None
    _response_config_path = None
    _response_config_mtime_ns = -1
