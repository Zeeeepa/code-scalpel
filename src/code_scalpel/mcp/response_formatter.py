"""Response formatting and filtering based on profiles.

This module implements the ResponseFormatter that controls output detail
levels through cascading profile logic:

1. Check tool argument for profile override
2. Check response_config.json for default profile
3. Fall back to 'standard' profile

Profiles control:
- Which envelope fields are included
- Which data fields are included
- Token budget optimization
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from pydantic import BaseModel

from code_scalpel.mcp.models.envelope import ResponseEnvelope
from code_scalpel.mcp.response_config import get_response_config

logger = logging.getLogger(__name__)


class ResponseProfile:
    """Configuration for a response detail profile."""

    def __init__(
        self,
        name: str,
        description: str,
        include_envelope_fields: list[str],
        exclude_data_fields: list[str],
        preserve_structure: bool = True,
    ):
        """Initialize a response profile.

        Args:
            name: Profile name (e.g., 'minimal', 'standard', 'verbose').
            description: Human-readable description.
            include_envelope_fields: Envelope fields to include (tier, tool_version, etc).
            exclude_data_fields: Data fields to exclude/strip.
            preserve_structure: Whether to preserve nested object structure.
        """
        self.name = name
        self.description = description
        self.include_envelope_fields = set(include_envelope_fields)
        self.exclude_data_fields = set(exclude_data_fields)
        self.preserve_structure = preserve_structure

    def __repr__(self) -> str:
        return f"ResponseProfile(name={self.name})"


# Predefined profiles
PROFILE_MINIMAL = ResponseProfile(
    name="minimal",
    description="Minimal output: only essential data, no envelope metadata",
    include_envelope_fields=[],
    exclude_data_fields=[
        "raw_ast",
        "intermediate_results",
        "timing",
        "metadata",
        "duration_ms",
    ],
)

PROFILE_STANDARD = ResponseProfile(
    name="standard",
    description="Standard output: data + error/upgrade hints",
    include_envelope_fields=[
        "error",
        "upgrade_hints",
        "suggestions",
        "capabilities_used",
    ],
    exclude_data_fields=[
        "raw_ast",
        "intermediate_results",
        "timing",
    ],
)

PROFILE_VERBOSE = ResponseProfile(
    name="verbose",
    description="Verbose output: all data + envelope fields",
    include_envelope_fields=[
        "tier",
        "tool_version",
        "error",
        "upgrade_hints",
        "suggestions",
        "capabilities_used",
        "duration_ms",
    ],
    exclude_data_fields=[
        "raw_ast",
        "intermediate_results",
    ],
)

PROFILE_DEBUG = ResponseProfile(
    name="debug",
    description="Debug output: everything, no filtering",
    include_envelope_fields=[
        "tier",
        "tool_version",
        "tool_id",
        "request_id",
        "capabilities",
        "duration_ms",
        "error",
        "upgrade_hints",
        "suggestions",
        "capabilities_used",
    ],
    exclude_data_fields=[],
)

PROFILES = {
    "minimal": PROFILE_MINIMAL,
    "standard": PROFILE_STANDARD,
    "verbose": PROFILE_VERBOSE,
    "debug": PROFILE_DEBUG,
}


class ResponseFormatter:
    """Formats tool responses according to profiles.

    Handles:
    - Profile resolution (argument override -> config default -> fallback)
    - Data filtering (removing excluded fields)
    - Envelope field selection
    - Structure preservation (keeping nested objects intact)
    """

    @staticmethod
    def get_profile(profile_name: Optional[str] = None) -> ResponseProfile:
        """Get a response profile by name.

        Args:
            profile_name: Profile name. If None, uses config default or 'standard'.

        Returns:
            ResponseProfile instance.
        """
        if profile_name and profile_name in PROFILES:
            return PROFILES[profile_name]

        # Fall back to config default
        config = get_response_config()
        default = config.get_profile() or "standard"
        if default in PROFILES:
            return PROFILES[default]

        # Ultimate fallback
        return PROFILE_STANDARD

    @staticmethod
    def filter_data(data: Any, profile: ResponseProfile) -> Any:
        """Filter data according to profile rules.

        Args:
            data: Data to filter (dict, BaseModel, or other).
            profile: ResponseProfile to apply.

        Returns:
            Filtered data structure.
        """
        if data is None:
            return None

        # Convert Pydantic model to dict
        if isinstance(data, BaseModel):
            data = data.model_dump(mode="json", exclude_none=False)

        if not isinstance(data, dict):
            # Non-dict data: return as-is
            return data

        # Recursively filter dict
        filtered = {}
        for key, value in data.items():
            # Skip excluded fields
            if key in profile.exclude_data_fields:
                logger.debug(f"Excluding field: {key}")
                continue

            # Recursively filter nested dicts
            if isinstance(value, dict):
                filtered[key] = ResponseFormatter.filter_data(value, profile)
            elif isinstance(value, list):
                filtered[key] = [
                    (
                        ResponseFormatter.filter_data(item, profile)
                        if isinstance(item, dict)
                        else item
                    )
                    for item in value
                ]
            else:
                filtered[key] = value

        return filtered

    @staticmethod
    def resolve_profile_cascading(
        tool_argument_profile: Optional[str] = None,
    ) -> ResponseProfile:
        """Resolve profile with cascading logic.

        Precedence:
        1. tool_argument_profile (if provided)
        2. response_config.json global.profile
        3. 'standard' (default)

        Args:
            tool_argument_profile: Profile passed as tool argument.

        Returns:
            Resolved ResponseProfile.
        """
        # Check tool argument
        if tool_argument_profile:
            if tool_argument_profile in PROFILES:
                logger.debug(f"Using profile from argument: {tool_argument_profile}")
                return PROFILES[tool_argument_profile]
            logger.warning(
                f"Unknown profile '{tool_argument_profile}', using config default"
            )

        # Check config
        config = get_response_config()
        config_profile = config.get_profile() or "standard"
        if config_profile and config_profile in PROFILES:
            logger.debug(f"Using profile from config: {config_profile}")
            return PROFILES[config_profile]

        # Fallback
        logger.debug("Using default profile: standard")
        return PROFILE_STANDARD

    @staticmethod
    def list_profiles() -> list[str]:
        """List all available profile names.

        Returns:
            List of profile names.
        """
        return list(PROFILES.keys())

    @staticmethod
    def get_profile_description(profile_name: str) -> str:
        """Get description of a profile.

        Args:
            profile_name: Profile name.

        Returns:
            Description string or empty if unknown.
        """
        profile = PROFILES.get(profile_name)
        return profile.description if profile else f"Unknown profile: {profile_name}"

    @staticmethod
    def filter_envelope(
        envelope: ResponseEnvelope,
        profile: ResponseProfile,
    ) -> dict:
        """Filter a ResponseEnvelope according to profile.

        Args:
            envelope: ResponseEnvelope to filter.
            profile: ResponseProfile to apply.

        Returns:
            Filtered envelope as dictionary.
        """
        # Convert envelope to dict
        envelope_dict = envelope.to_dict(exclude_none=True)

        # Determine which envelope fields to include
        envelope_fields_to_keep = {
            # Always include
            "schema_version",
            "tool_id",
            "tool_name",
            "tool_version",
            "request_id",
            "timestamp",
            "data",
            "error",
            "validation_passed",
            "response_profile",
        }

        # Add profile-specified envelope fields
        envelope_fields_to_keep.update(profile.include_envelope_fields)

        # Filter envelope to keep only specified fields
        filtered_envelope = {
            k: v for k, v in envelope_dict.items() if k in envelope_fields_to_keep
        }

        # Filter the data field using standard data filtering
        if "data" in filtered_envelope and filtered_envelope["data"]:
            filtered_envelope["data"] = ResponseFormatter.filter_data(
                filtered_envelope["data"],
                profile,
            )

        return filtered_envelope

    @staticmethod
    def format_with_envelope(
        tool_id: str,
        tool_name: str,
        tool_version: str,
        data: Any,
        profile_name: Optional[str] = None,
        error: Optional[str] = None,
        suggestions: Optional[list[str]] = None,
        request_id: Optional[str] = None,
        duration_ms: float = 0.0,
        tier: Optional[str] = None,
        capabilities_used: Optional[list[str]] = None,
    ) -> dict:
        """Format a response with ResponseEnvelope and profile filtering.

        Args:
            tool_id: Tool identifier.
            tool_name: Human-readable tool name.
            tool_version: Tool version.
            data: Tool output data.
            profile_name: Response profile to apply.
            error: Optional error message.
            suggestions: Optional validation suggestions.
            request_id: Optional request ID for tracing.
            duration_ms: Execution duration in milliseconds.
            tier: User tier.
            capabilities_used: List of capabilities invoked.

        Returns:
            Filtered envelope dictionary ready for JSON serialization.
        """
        # Resolve profile
        profile = ResponseFormatter.resolve_profile_cascading(profile_name)

        # Create envelope
        envelope = ResponseEnvelope(
            tool_id=tool_id,
            tool_name=tool_name,
            tool_version=tool_version,
            data=data,
            request_id=request_id,
            duration_ms=duration_ms,
            tier=tier,
            capabilities_used=capabilities_used or [],
            response_profile=profile.name,
        )

        # Add error if present
        if error:
            envelope.with_error(error, suggestions=suggestions)

        # Add suggestions if present
        if suggestions:
            envelope.with_suggestions(suggestions)

        # Filter and return
        return ResponseFormatter.filter_envelope(envelope, profile)


__all__ = [
    "ResponseProfile",
    "ResponseFormatter",
    "PROFILE_MINIMAL",
    "PROFILE_STANDARD",
    "PROFILE_VERBOSE",
    "PROFILE_DEBUG",
    "PROFILES",
]
