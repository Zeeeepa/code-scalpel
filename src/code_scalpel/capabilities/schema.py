"""
Capability Schema - Validation schemas for capabilities.

[20260127_FEATURE] Pydantic models and validators for capability definitions.

This module defines the structure and validation rules for capabilities.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import logging

logger = logging.getLogger(__name__)


@dataclass
class CapabilityLimits:
    """Limits for a tool at a specific tier."""

    # Maximum values (optional, depends on tool)
    max_file_size_mb: Optional[int] = None
    max_files: Optional[int] = None
    max_depth: Optional[int] = None
    max_nodes: Optional[int] = None
    max_context_lines: Optional[int] = None
    max_findings: Optional[int] = None
    max_references: Optional[int] = None
    max_files_searched: Optional[int] = None
    max_modules: Optional[int] = None
    max_symbol_count: Optional[int] = None

    # Feature toggles (optional)
    parsing_enabled: Optional[bool] = None
    complexity_analysis: Optional[bool] = None
    respect_gitignore: Optional[bool] = None

    # Feature lists (optional)
    languages: Optional[List[str]] = None
    detail_level: Optional[str] = None

    # Cache settings (optional)
    cache_ttl_seconds: Optional[int] = None

    # Extra fields (for forward compatibility)
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CapabilityLimits:
        """Create CapabilityLimits from a dictionary."""
        known_fields = {
            "max_file_size_mb",
            "max_files",
            "max_depth",
            "max_nodes",
            "max_context_lines",
            "max_findings",
            "max_references",
            "max_files_searched",
            "max_modules",
            "max_symbol_count",
            "parsing_enabled",
            "complexity_analysis",
            "respect_gitignore",
            "languages",
            "detail_level",
            "cache_ttl_seconds",
        }

        # Separate known and unknown fields
        kwargs = {}
        extra = {}

        for key, value in data.items():
            if key in known_fields:
                kwargs[key] = value
            else:
                extra[key] = value

        kwargs["extra"] = extra
        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values and empty extra."""
        result = {}
        for field_name in [
            "max_file_size_mb",
            "max_files",
            "max_depth",
            "max_nodes",
            "max_context_lines",
            "max_findings",
            "max_references",
            "max_files_searched",
            "max_modules",
            "max_symbol_count",
            "parsing_enabled",
            "complexity_analysis",
            "respect_gitignore",
            "languages",
            "detail_level",
            "cache_ttl_seconds",
        ]:
            value = getattr(self, field_name)
            if value is not None:
                result[field_name] = value

        # Include extra fields
        if self.extra:
            result.update(self.extra)

        return result


@dataclass
class Capability:
    """A single capability/tool at a specific tier."""

    tool_id: str
    tier: str
    available: bool
    limits: CapabilityLimits
    deprecated: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Capability:
        """Create Capability from a dictionary."""
        limits_dict = data.get("limits", {})
        limits = CapabilityLimits.from_dict(limits_dict)

        return cls(
            tool_id=data["tool_id"],
            tier=data["tier"],
            available=data.get("available", True),
            limits=limits,
            deprecated=data.get("deprecated", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_id": self.tool_id,
            "tier": self.tier,
            "available": self.available,
            "limits": self.limits.to_dict(),
            "deprecated": self.deprecated,
        }


@dataclass
class CapabilityEnvelope:
    """Envelope containing all capabilities for a tier."""

    tier: str
    tool_count: int
    available_count: int
    capabilities: Dict[str, Capability]
    generated_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CapabilityEnvelope:
        """Create CapabilityEnvelope from a dictionary."""
        capabilities = {
            tool_id: Capability.from_dict(cap)
            for tool_id, cap in data.get("capabilities", {}).items()
        }

        return cls(
            tier=data["tier"],
            tool_count=data.get("tool_count", len(capabilities)),
            available_count=data.get(
                "available_count", sum(1 for c in capabilities.values() if c.available)
            ),
            capabilities=capabilities,
            generated_at=data.get("generated_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tier": self.tier,
            "tool_count": self.tool_count,
            "available_count": self.available_count,
            "capabilities": {
                tool_id: cap.to_dict() for tool_id, cap in self.capabilities.items()
            },
            "generated_at": self.generated_at,
        }


def validate_capability(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that a capability dictionary has the correct structure.

    Returns:
        (is_valid, error_message)
        If valid: (True, None)
        If invalid: (False, "error description")
    """
    required_fields = ["tool_id", "tier", "available"]

    for field_name in required_fields:
        if field_name not in data:
            return False, f"Missing required field: {field_name}"

    tier = data.get("tier")
    if tier not in ["community", "pro", "enterprise"]:
        return False, f"Invalid tier: {tier}"

    available = data.get("available")
    if not isinstance(available, bool):
        return False, f"available must be boolean, got {type(available).__name__}"

    return True, None


def get_json_schema() -> Dict[str, Any]:
    """
    Get the JSON Schema for a capability.

    This can be used to validate capability files.
    """
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Code Scalpel Capability Schema",
        "description": "Schema for tool capabilities at a specific tier",
        "type": "object",
        "properties": {
            "tool_id": {
                "type": "string",
                "description": "Unique tool identifier",
                "examples": ["analyze_code", "get_file_context"],
            },
            "tier": {
                "type": "string",
                "enum": ["community", "pro", "enterprise"],
                "description": "License tier",
            },
            "available": {
                "type": "boolean",
                "description": "Whether tool is available at this tier",
            },
            "limits": {
                "type": "object",
                "description": "Limits and parameters for the tool at this tier",
                "properties": {
                    "max_file_size_mb": {"type": "integer"},
                    "max_files": {"type": "integer"},
                    "max_depth": {"type": "integer"},
                    "max_nodes": {"type": "integer"},
                    "max_context_lines": {"type": "integer"},
                    "max_findings": {"type": "integer"},
                    "max_references": {"type": "integer"},
                    "max_files_searched": {"type": "integer"},
                    "max_modules": {"type": "integer"},
                    "max_symbol_count": {"type": "integer"},
                    "parsing_enabled": {"type": "boolean"},
                    "complexity_analysis": {"type": "boolean"},
                    "respect_gitignore": {"type": "boolean"},
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of supported languages",
                    },
                    "detail_level": {
                        "type": "string",
                        "description": "Level of detail (e.g., 'basic', 'detailed', 'comprehensive')",
                    },
                    "cache_ttl_seconds": {"type": "integer"},
                },
            },
            "deprecated": {
                "type": "boolean",
                "description": "Whether the tool is deprecated",
                "default": False,
            },
        },
        "required": ["tool_id", "tier", "available"],
    }
