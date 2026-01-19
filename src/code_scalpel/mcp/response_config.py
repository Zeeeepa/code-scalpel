"""
Response configuration loader and filter for MCP tools.

[20251226_FEATURE] v3.3.0 - Configurable output for token efficiency.

Allows teams to customize which fields are returned in MCP responses
via .code-scalpel/response_config.json configuration file.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, Set, TypedDict, cast


class FilteredResponseDict(TypedDict, total=False):
    """Filtered response data after applying configuration.

    This is a flexible dictionary that can contain any fields from the original
    response data after filtering based on profile and tier settings.
    """

    success: bool  # Always preserved (contract-critical)
    # Other fields are dynamic based on tool output and filter config


logger = logging.getLogger(__name__)

# Default configuration (fallback)
DEFAULT_CONFIG = {
    "global": {
        "profile": "minimal",
        "exclude_empty_arrays": True,
        "exclude_empty_objects": True,
        "exclude_null_values": True,
        "exclude_default_values": True,
    },
    "profiles": {
        "minimal": {
            "envelope": {"include": []},
            "common_exclusions": [
                "success",
                "server_version",
                "function_count",
                "class_count",
                "error",
            ],
        },
        "standard": {
            "envelope": {"include": ["error", "upgrade_hints"]},
            "common_exclusions": ["server_version", "function_count", "class_count"],
        },
        "debug": {
            "envelope": {
                "include": [
                    "tier",
                    "tool_version",
                    "tool_id",
                    "request_id",
                    "capabilities",
                    "duration_ms",
                    "error",
                    "upgrade_hints",
                ]
            },
            "common_exclusions": [],
        },
    },
    "tool_overrides": {},
}


class ResponseConfig:
    """
    Load and apply response configuration for token efficiency.
    Supports hot-reloading when the configuration file changes.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize response configuration.

        Args:
            config_path: Path to response_config.json. If None, searches common locations.
        """
        self._config_path: Optional[Path] = None
        self._last_mtime: float = 0.0
        self._last_check_time: float = 0.0
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if config_path and config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    logger.info(f"Loaded response config from {config_path}")

                    # Update tracking for hot reload
                    self._config_path = config_path
                    self._last_mtime = config_path.stat().st_mtime
                    return config
            except Exception as e:
                logger.warning(f"Failed to load response config from {config_path}: {e}")

        # Search common locations
        search_paths = [
            Path.cwd() / ".code-scalpel" / "response_config.json",
            Path.home() / ".config" / "code-scalpel" / "response_config.json",
            Path(__file__).parent.parent.parent / ".code-scalpel" / "response_config.json",
        ]

        for path in search_paths:
            if path.exists():
                try:
                    with open(path, "r") as f:
                        config = json.load(f)
                        logger.info(f"Loaded response config from {path}")

                        # Update tracking for hot reload
                        self._config_path = path
                        self._last_mtime = path.stat().st_mtime
                        return config
                except Exception as e:
                    logger.warning(f"Failed to load response config from {path}: {e}")

        logger.info("Using default response configuration")
        self._config_path = None
        return DEFAULT_CONFIG

    def _check_reload(self) -> None:
        """Check if config file has changed and reload if necessary."""
        # Throttle checks to once per second to avoid excessive I/O
        current_time = time.time()
        if current_time - self._last_check_time < 1.0:
            return

        self._last_check_time = current_time

        if self._config_path and self._config_path.exists():
            try:
                current_mtime = self._config_path.stat().st_mtime
                if current_mtime > self._last_mtime:
                    logger.info(f"Detected change in {self._config_path}, reloading...")
                    new_config = self._load_config(self._config_path)

                    # Only apply if load was successful (basic partial update check)
                    # _load_config will return DEFAULT_CONFIG if file vanishes/fails,
                    # but if it returns a dict, we assume it's good or fell back safely.
                    if new_config:
                        self.config = new_config
            except Exception as e:
                logger.warning(f"Error checking config reload: {e}")

    def get_profile(self, tool_name: Optional[str] = None) -> str:
        """Get the profile to use for a tool."""
        if tool_name and tool_name in self.config.get("tool_overrides", {}):
            return self.config["tool_overrides"][tool_name].get(
                "profile", self.config["global"]["profile"]
            )
        return self.config["global"]["profile"]

    def get_envelope_fields(self, tool_name: Optional[str] = None) -> Set[str]:
        """Get which envelope fields to include."""
        profile = self.get_profile(tool_name)
        profile_config = self.config["profiles"].get(profile, {})
        return set(profile_config.get("envelope", {}).get("include", []))

    def get_exclusions(
        self, tool_name: Optional[str] = None, tier: Optional[str] = None
    ) -> Set[str]:
        """Get fields to exclude from response."""
        exclusions = set()

        # Profile-level exclusions
        profile = self.get_profile(tool_name)
        profile_config = self.config["profiles"].get(profile, {})
        exclusions.update(profile_config.get("common_exclusions", []))

        # Tool-specific exclusions
        if tool_name and tool_name in self.config.get("tool_overrides", {}):
            tool_config = self.config["tool_overrides"][tool_name]
            exclusions.update(tool_config.get("exclude_fields", []))

            # Tier-specific exclusions
            if tier:
                tier_exclusions = tool_config.get("exclude_when_tier", {}).get(tier, [])
                exclusions.update(tier_exclusions)

        return exclusions

    def get_inclusions(self, tool_name: Optional[str] = None) -> Optional[Set[str]]:
        """Get whitelist of fields to include (if specified)."""
        if tool_name and tool_name in self.config.get("tool_overrides", {}):
            tool_config = self.config["tool_overrides"][tool_name]
            include_only = tool_config.get("include_only")
            if include_only:
                return set(include_only)
        return None

    def should_exclude_empty_arrays(self) -> bool:
        """Check if empty arrays should be excluded."""
        return self.config["global"].get("exclude_empty_arrays", True)

    def should_exclude_empty_objects(self) -> bool:
        """Check if empty objects should be excluded."""
        return self.config["global"].get("exclude_empty_objects", True)

    def should_exclude_null_values(self) -> bool:
        """Check if null values should be excluded."""
        return self.config["global"].get("exclude_null_values", True)

    def should_exclude_default_values(self) -> bool:
        """Check if default values should be excluded."""
        return self.config["global"].get("exclude_default_values", True)

    def filter_response(
        self,
        data: Dict[str, Any],
        tool_name: Optional[str] = None,
        tier: Optional[str] = None,
    ) -> FilteredResponseDict:
        """
        Filter response data according to configuration.

        Args:
            data: Response data to filter
            tool_name: Name of the tool that generated the response
            tier: Current tier (community, pro, enterprise)

        Returns:
            Filtered response data
        """
        if not isinstance(data, dict):
            return data

        filtered = {}
        exclusions = self.get_exclusions(tool_name, tier)
        inclusions = self.get_inclusions(tool_name)

        for key, value in data.items():
            # [20251228_BUGFIX] Preserve contract-critical fields.
            # Many MCP clients (and our contract tests) depend on `success` being present
            # in the tool-specific payload, even when token-efficiency exclusions are
            # enabled.
            if key == "success":
                filtered[key] = value
                continue

            # Skip if in exclusion list
            if key in exclusions:
                continue

            # Skip if whitelist exists and key not in it
            if inclusions is not None and key not in inclusions:
                continue

            # Skip empty arrays
            if self.should_exclude_empty_arrays() and isinstance(value, list) and len(value) == 0:
                continue

            # Skip empty objects
            if self.should_exclude_empty_objects() and isinstance(value, dict) and len(value) == 0:
                continue

            # Skip null values
            if self.should_exclude_null_values() and value is None:
                continue

            # Recursively filter nested dicts
            if isinstance(value, dict):
                filtered_value = self.filter_response(value, tool_name, tier)
                if filtered_value:  # Only include if not empty after filtering
                    filtered[key] = filtered_value
            else:
                filtered[key] = value

        return cast(FilteredResponseDict, filtered)


# Global instance
_response_config: Optional[ResponseConfig] = None


def get_response_config() -> ResponseConfig:
    """Get the global response configuration instance."""
    global _response_config
    if _response_config is None:
        _response_config = ResponseConfig()
    return _response_config


def filter_tool_response(
    data: Dict[str, Any], tool_name: Optional[str] = None, tier: Optional[str] = None
) -> FilteredResponseDict:
    """
    Filter tool response data for token efficiency.

    Args:
        data: Response data to filter
        tool_name: Name of the tool that generated the response
        tier: Current tier (community, pro, enterprise)

    Returns:
        Filtered response data
    """
    config = get_response_config()
    return config.filter_response(data, tool_name, tier)
