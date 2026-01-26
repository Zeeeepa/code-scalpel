"""Tool metadata and docstring system.

This module implements a unified ToolDefinition class that standardizes
how tool capabilities, arguments, and documentation are described.

Key features:
- 3-tier docstring system: system_prompt, documentation, examples
- Dynamic capability matrix based on tier
- Lazy-loaded examples for token efficiency
- Machine-parseable schema for MCP protocol
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Tier(str, Enum):
    """License tiers supported by code-scalpel."""

    COMMUNITY = "community"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class CapabilitySpec:
    """Specifies what a tool can do at a given tier."""

    tier: Tier
    limits: dict[str, Any] = field(default_factory=dict)
    """Hard limits (e.g., max_files: 100, max_depth: 2)."""

    features: list[str] = field(default_factory=list)
    """Enabled features (e.g., "complexity_analysis", "duplicate_detection")."""

    description: str = ""
    """Human-readable description of what's available at this tier."""


@dataclass
class ToolDefinition:
    """Unified metadata for an MCP tool.

    This class decouples documentation from implementation, allowing:
    - Multiple docstring formats (system prompt vs. user-facing docs)
    - Dynamic examples that can be injected based on context
    - Capabilities that vary by tier
    - Clear schema for MCP protocol integration
    """

    tool_id: str
    """Canonical tool identifier (e.g., 'analyze_code')."""

    name: str
    """Human-readable tool name."""

    system_prompt: str
    """Minimal docstring optimized for LLM token usage.
    Format: Brief description + tier capabilities. ~100-200 tokens."""

    documentation: str
    """Comprehensive docstring for human readers and UI.
    Format: Full description + args + returns + examples. ~1000+ tokens."""

    args_schema: dict[str, Any]
    """Pydantic/JSON Schema for tool arguments.
    Used by MCP protocol for input validation."""

    capabilities: dict[Tier, CapabilitySpec] = field(default_factory=dict)
    """Tier-specific capabilities matrix."""

    examples: Optional[dict[str, str]] = field(default=None)
    """Lazy-loaded examples. Key=example_name, Value=example_code.
    Not included in system_prompt to save tokens."""

    category: str = "general"
    """Tool category for organization (e.g., 'analysis', 'extraction', 'security')."""

    deprecated: bool = False
    """Whether this tool is deprecated."""

    min_version: str = "1.0.0"
    """Minimum code-scalpel version required."""

    def get_prompt_for_tier(self, tier: Tier) -> str:
        """Get the system prompt, filtered for the given tier.

        Returns:
            system_prompt with tier-specific capabilities highlighted.
        """
        spec = self.capabilities.get(tier)
        if not spec:
            return self.system_prompt

        # Inject tier-specific details into prompt
        return f"{self.system_prompt}\n\nAvailable at {tier.value} tier: {', '.join(spec.features)}"

    def get_full_docs(self, include_examples: bool = False) -> str:
        """Get complete documentation for human readers.

        Args:
            include_examples: Whether to include examples section.

        Returns:
            Full documentation string.
        """
        doc = self.documentation

        if include_examples and self.examples:
            examples_section = "\n\nExamples:\n"
            for example_name, example_code in self.examples.items():
                examples_section += (
                    f"\n**{example_name}:**\n```python\n{example_code}\n```\n"
                )
            doc += examples_section

        return doc

    def get_capabilities_for_tier(self, tier: Tier) -> CapabilitySpec | None:
        """Get capability spec for a specific tier.

        Args:
            tier: License tier to query.

        Returns:
            CapabilitySpec if available, None otherwise.
        """
        return self.capabilities.get(tier)

    def has_feature_at_tier(self, feature: str, tier: Tier) -> bool:
        """Check if a specific feature is available at a tier.

        Args:
            feature: Feature name to check.
            tier: License tier.

        Returns:
            True if feature is available, False otherwise.
        """
        spec = self.get_capabilities_for_tier(tier)
        return spec is not None and feature in spec.features

    def to_mcp_tool_schema(self) -> dict[str, Any]:
        """Convert to MCP protocol ToolSchema format.

        Returns:
            Dict suitable for use in MCP ToolSchema.
        """
        return {
            "name": self.tool_id,
            "description": self.system_prompt,
            "inputSchema": {
                "type": "object",
                "properties": self.args_schema.get("properties", {}),
                "required": self.args_schema.get("required", []),
            },
        }


class ToolDefinitionRegistry:
    """Central registry for all tool definitions.

    This singleton-like class maintains the canonical metadata for every
    MCP tool, allowing tools to be self-documenting and tier-aware.
    """

    _definitions: dict[str, ToolDefinition] = {}

    @classmethod
    def register(cls, definition: ToolDefinition) -> None:
        """Register a tool definition.

        Args:
            definition: ToolDefinition to register.

        Raises:
            ValueError: If tool_id is already registered.
        """
        if definition.tool_id in cls._definitions:
            raise ValueError(f"Tool {definition.tool_id} already registered")
        cls._definitions[definition.tool_id] = definition

    @classmethod
    def get(cls, tool_id: str) -> ToolDefinition | None:
        """Retrieve a tool definition by ID.

        Args:
            tool_id: Canonical tool identifier.

        Returns:
            ToolDefinition if found, None otherwise.
        """
        return cls._definitions.get(tool_id)

    @classmethod
    def list_all(cls) -> list[ToolDefinition]:
        """List all registered tool definitions.

        Returns:
            List of all ToolDefinition objects.
        """
        return list(cls._definitions.values())

    @classmethod
    def list_by_category(cls, category: str) -> list[ToolDefinition]:
        """List all tools in a given category.

        Args:
            category: Tool category to filter by.

        Returns:
            List of ToolDefinition objects in the category.
        """
        return [d for d in cls._definitions.values() if d.category == category]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered definitions (for testing)."""
        cls._definitions.clear()


__all__ = [
    "Tier",
    "CapabilitySpec",
    "ToolDefinition",
    "ToolDefinitionRegistry",
]
