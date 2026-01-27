"""
Tier-aware test adapter framework.

Provides utilities to run tests across different tiers with automatic
capability checking and license injection.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, Optional

from code_scalpel.capabilities.resolver import get_all_capabilities
from code_scalpel.licensing.features import TOOL_CAPABILITIES

Tier = Literal["community", "pro", "enterprise"]


class TierAdapter:
    """Adapter for running tests on specific tiers.

    Handles:
    - Tier detection and validation
    - License path management
    - Capability checking
    - Test execution with proper setup/teardown
    """

    def __init__(self, tier: Tier = "community"):
        """Initialize adapter for a specific tier.

        Args:
            tier: The tier to test ('community', 'pro', or 'enterprise')

        Raises:
            ValueError: If tier is invalid
        """
        if tier not in ("community", "pro", "enterprise"):
            raise ValueError(
                f"Invalid tier '{tier}'. Must be 'community', 'pro', or 'enterprise'"
            )
        self.tier: Tier = tier
        self._original_license_path: Optional[str] = None

    def get_tier(self) -> Tier:
        """Get the tier this adapter is configured for."""
        return self.tier

    def get_available_tools(self) -> set[str]:
        """Get set of tools available in this tier.

        Returns:
            Set of tool IDs that are available
        """
        capabilities = get_all_capabilities(self.tier)
        return {
            tool_id
            for tool_id, cap in capabilities.items()
            if cap.get("available", False)
        }

    def get_unavailable_tools(self) -> set[str]:
        """Get set of tools locked in this tier.

        Returns:
            Set of tool IDs that are unavailable/locked
        """
        capabilities = get_all_capabilities(self.tier)
        return {
            tool_id
            for tool_id, cap in capabilities.items()
            if not cap.get("available", False)
        }

    def tool_available(self, tool_id: str) -> bool:
        """Check if a tool is available in this tier.

        Args:
            tool_id: The tool ID to check

        Returns:
            True if tool is available, False if locked
        """
        capabilities = get_all_capabilities(self.tier)
        cap = capabilities.get(tool_id, {})
        return cap.get("available", False)

    def get_tool_limits(self, tool_id: str) -> dict:
        """Get the limits for a tool in this tier.

        Args:
            tool_id: The tool ID

        Returns:
            Dictionary of limits (e.g., {'max_lines': 500})
        """
        capabilities = get_all_capabilities(self.tier)
        cap = capabilities.get(tool_id, {})
        return cap.get("limits", {})

    def get_tool_capabilities(self, tool_id: str) -> set[str]:
        """Get the capabilities for a tool in this tier.

        Args:
            tool_id: The tool ID

        Returns:
            Set of capability names (e.g., {'basic_ast', 'imports'})
        """
        # Use legacy TOOL_CAPABILITIES for detailed capability lists
        if tool_id in TOOL_CAPABILITIES:
            tool_cap = TOOL_CAPABILITIES[tool_id]
            tiers = tool_cap.get("tiers", {})
            tier_cap = tiers.get(self.tier, {})
            return set(tier_cap.get("capabilities", []))
        return set()

    def assert_tool_available(self, tool_id: str) -> None:
        """Assert that a tool is available in this tier.

        Args:
            tool_id: The tool ID to check

        Raises:
            AssertionError: If tool is not available
        """
        if not self.tool_available(tool_id):
            locked_by = "community" if self.tier != "community" else "licensing"
            raise AssertionError(
                f"Tool '{tool_id}' is not available in {self.tier} tier "
                f"(locked for {locked_by})"
            )

    def assert_tool_unavailable(self, tool_id: str) -> None:
        """Assert that a tool is locked in this tier.

        Args:
            tool_id: The tool ID to check

        Raises:
            AssertionError: If tool is available
        """
        if self.tool_available(tool_id):
            raise AssertionError(
                f"Tool '{tool_id}' is available in {self.tier} tier "
                f"(expected it to be locked)"
            )

    def assert_capability_present(self, tool_id: str, capability: str) -> None:
        """Assert that a capability is present for a tool.

        Args:
            tool_id: The tool ID
            capability: The capability name

        Raises:
            AssertionError: If capability is not present
        """
        caps = self.get_tool_capabilities(tool_id)
        if capability not in caps:
            raise AssertionError(
                f"Capability '{capability}' not present for tool '{tool_id}' "
                f"in {self.tier} tier. Available: {caps}"
            )

    def assert_limit_value(
        self, tool_id: str, limit_name: str, expected_value: int | float
    ) -> None:
        """Assert that a limit has a specific value.

        Args:
            tool_id: The tool ID
            limit_name: The limit name (e.g., 'max_lines')
            expected_value: The expected value

        Raises:
            AssertionError: If limit doesn't match
        """
        limits = self.get_tool_limits(tool_id)
        actual_value = limits.get(limit_name)
        if actual_value != expected_value:
            raise AssertionError(
                f"Limit '{limit_name}' for tool '{tool_id}' in {self.tier} tier "
                f"is {actual_value}, expected {expected_value}"
            )

    def setup_license(self, license_path: str | Path | None) -> None:
        """Set up license for this tier.

        Args:
            license_path: Path to license file (or None for community tier)

        Raises:
            FileNotFoundError: If license file doesn't exist
            ValueError: If license_path is required for non-community tier
        """
        # Save original for cleanup
        self._original_license_path = os.environ.get("CODE_SCALPEL_LICENSE_PATH")

        if license_path is None:
            # Remove license for community tier
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
        else:
            license_path = Path(license_path)
            if not license_path.exists():
                raise FileNotFoundError(f"License file not found: {license_path}")
            os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(license_path)

    def cleanup_license(self) -> None:
        """Restore original license path."""
        if self._original_license_path is None:
            os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
        else:
            os.environ["CODE_SCALPEL_LICENSE_PATH"] = self._original_license_path


class TierAdapterFactory:
    """Factory for creating tier adapters."""

    @staticmethod
    def create(tier: Tier) -> TierAdapter:
        """Create an adapter for the specified tier.

        Args:
            tier: The tier ('community', 'pro', or 'enterprise')

        Returns:
            TierAdapter instance
        """
        return TierAdapter(tier)

    @staticmethod
    def create_for_all_tiers() -> list[TierAdapter]:
        """Create adapters for all tiers.

        Returns:
            List of TierAdapter instances for all tiers
        """
        return [
            TierAdapter("community"),
            TierAdapter("pro"),
            TierAdapter("enterprise"),
        ]

    @staticmethod
    def create_for_tiers(*tiers: Tier) -> list[TierAdapter]:
        """Create adapters for specified tiers.

        Args:
            *tiers: Tier IDs to create adapters for

        Returns:
            List of TierAdapter instances
        """
        return [TierAdapter(tier) for tier in tiers]
