"""Response envelope with versioned schema support.

This module provides the ResponseEnvelope class that wraps tool responses
with standardized metadata and versioning information.

Key features:
- Versioned schema for backward compatibility
- Tool metadata tracking (version, tier, capabilities)
- Error and suggestion propagation
- Envelope filtering based on response profiles
- Request tracking (request_id, duration_ms)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from enum import Enum

from pydantic import BaseModel, Field


class SchemaVersion(str, Enum):
    """Versioned schema identifiers."""

    V1_0 = "1.0"
    """Initial version with basic metadata."""

    V1_1 = "1.1"
    """Added validation suggestions and self-correction hints."""

    V2_0 = "2.0"
    """Major revision with metrics and telemetry."""

    CURRENT = V1_1
    """Current schema version."""


class ResponseEnvelope(BaseModel):
    """Standardized response wrapper for all tool outputs.

    The envelope provides:
    1. Schema versioning for forward/backward compatibility
    2. Tool metadata (version, tier, capabilities used)
    3. Request metadata (ID, duration, timestamp)
    4. Error and suggestion propagation
    5. Profile-based filtering hints
    """

    # Schema versioning
    schema_version: SchemaVersion = Field(
        default=SchemaVersion.CURRENT,
        description="Versioned schema identifier for backward compatibility",
    )

    # Tool metadata
    tool_id: str = Field(..., description="Canonical tool identifier (e.g., 'analyze_code')")
    tool_version: str = Field(..., description="Tool version (e.g., '1.0.0')")
    tool_name: str = Field(..., description="Human-readable tool name (e.g., 'Code Analyzer')")

    # Request metadata
    request_id: Optional[str] = Field(
        default=None,
        description="Unique request identifier for tracing",
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the response was generated",
    )
    duration_ms: float = Field(
        default=0.0,
        description="Total execution time in milliseconds",
    )

    # Tier and capability information
    tier: Optional[str] = Field(
        default=None,
        description="User tier that performed the analysis (community, pro, enterprise)",
    )
    capabilities_used: list[str] = Field(
        default_factory=list,
        description="Capabilities invoked for this request",
    )

    # Core response data
    data: Any = Field(
        ...,
        description="Tool output data (format varies by tool)",
    )

    # Error handling
    error: Optional[str] = Field(
        default=None,
        description="Error message if tool execution failed",
    )
    error_details: Optional[dict] = Field(
        default=None,
        description="Structured error information (traceback, field, etc)",
    )

    # Self-correction and suggestions
    suggestions: list[str] = Field(
        default_factory=list,
        description="Did you mean? suggestions from validation layer",
    )
    upgrade_hints: list[str] = Field(
        default_factory=list,
        description="Feature recommendations (e.g., upgrade to pro)",
    )

    # Telemetry
    validation_passed: bool = Field(
        default=True,
        description="Whether pre-execution validation passed",
    )
    validation_errors: list[str] = Field(
        default_factory=list,
        description="Validation warnings (non-fatal)",
    )

    # Profile filter metadata
    response_profile: Optional[str] = Field(
        default="standard",
        description="Profile used to filter response (minimal, standard, verbose, debug)",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "schema_version": "1.1",
                "tool_id": "analyze_code",
                "tool_version": "1.0.0",
                "tool_name": "Code Analyzer",
                "request_id": "req-12345",
                "timestamp": "2025-01-26T17:00:00Z",
                "duration_ms": 250.5,
                "tier": "pro",
                "capabilities_used": ["ast_analysis", "type_checking"],
                "data": {"functions": 5, "classes": 2},
                "error": None,
                "suggestions": [],
                "upgrade_hints": [],
                "validation_passed": True,
                "response_profile": "standard",
            }
        }

    def with_error(
        self,
        error_msg: str,
        error_details: Optional[dict] = None,
        suggestions: Optional[list[str]] = None,
    ) -> ResponseEnvelope:
        """Create a failed response with error details.

        Args:
            error_msg: Human-readable error message.
            error_details: Structured error information.
            suggestions: "Did you mean?" suggestions for self-correction.

        Returns:
            Self (for chaining).
        """
        self.error = error_msg
        self.error_details = error_details or {}
        self.suggestions = suggestions or []
        self.validation_passed = False
        return self

    def with_suggestions(self, suggestions: list[str], upgrade_hints: Optional[list[str]] = None) -> ResponseEnvelope:
        """Add self-correction suggestions to response.

        Args:
            suggestions: "Did you mean?" suggestions.
            upgrade_hints: Optional feature upgrade recommendations.

        Returns:
            Self (for chaining).
        """
        self.suggestions = suggestions
        if upgrade_hints:
            self.upgrade_hints = upgrade_hints
        return self

    def with_validation_warning(self, warning: str) -> ResponseEnvelope:
        """Add a non-fatal validation warning.

        Args:
            warning: Warning message.

        Returns:
            Self (for chaining).
        """
        self.validation_errors.append(warning)
        return self

    def to_dict(
        self,
        exclude_none: bool = True,
        exclude_unset: bool = False,
        include: Optional[set[str]] = None,
        exclude: Optional[set[str]] = None,
    ) -> dict:
        """Serialize envelope to dict with filtering.

        Args:
            exclude_none: Exclude None values.
            exclude_unset: Exclude unset fields.
            include: Only include these fields.
            exclude: Exclude these fields.

        Returns:
            Dictionary representation.
        """
        return self.model_dump(
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            include=include,
            exclude=exclude,
        )

    def to_json(self) -> str:
        """Serialize to JSON string.

        Returns:
            JSON-encoded envelope.
        """
        return self.model_dump_json(exclude_none=True)


__all__ = [
    "SchemaVersion",
    "ResponseEnvelope",
]
