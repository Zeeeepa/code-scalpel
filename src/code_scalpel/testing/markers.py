"""
Pytest markers for tier-aware testing.

Provides markers to:
- Require specific tiers
- Require specific tools
- Run tests across multiple tiers
- Mark performance and security tests
"""

from __future__ import annotations

from typing import Literal

import pytest

Tier = Literal["community", "pro", "enterprise"]


def requires_tier(*tiers: Tier) -> pytest.MarkDecorator:
    """Mark a test as requiring specific tier(s).

    The test will only run if at least one of the specified tiers is available.

    Example:
        @pytest.mark.requires_tier("pro", "enterprise")
        def test_pro_feature():
            pass

    Args:
        *tiers: One or more tier IDs

    Returns:
        Pytest mark decorator
    """
    return pytest.mark.requires_tier(*tiers)


def requires_tool(tool_id: str) -> pytest.MarkDecorator:
    """Mark a test as requiring a specific tool to be available.

    The test will skip if the tool is not available in the current tier.

    Example:
        @pytest.mark.requires_tool("get_file_context")
        def test_file_context_feature():
            pass

    Args:
        tool_id: The tool ID required

    Returns:
        Pytest mark decorator
    """
    return pytest.mark.requires_tool(tool_id)


def requires_capability(tool_id: str, capability: str) -> pytest.MarkDecorator:
    """Mark a test as requiring a specific tool capability.

    The test will skip if the capability is not available in the current tier.

    Example:
        @pytest.mark.requires_capability("analyze_code", "code_smell_detection")
        def test_code_smells():
            pass

    Args:
        tool_id: The tool ID
        capability: The capability name

    Returns:
        Pytest mark decorator
    """
    return pytest.mark.requires_capability(tool_id, capability)


def tier_aware() -> pytest.MarkDecorator:
    """Mark a test as tier-aware.

    Tier-aware tests will run for all tiers and should handle
    both available and locked tools gracefully.

    Example:
        @pytest.mark.tier_aware
        def test_multi_tier():
            # Test can run on any tier
            pass

    Returns:
        Pytest mark decorator
    """
    return pytest.mark.tier_aware


def performance() -> pytest.MarkDecorator:
    """Mark a test as a performance test.

    Performance tests may be skipped in some CI configurations.

    Example:
        @pytest.mark.performance
        def test_large_file_parsing():
            pass

    Returns:
        Pytest mark decorator
    """
    return pytest.mark.performance


def security() -> pytest.MarkDecorator:
    """Mark a test as a security test.

    Security tests validate licensing and capability enforcement.

    Example:
        @pytest.mark.security
        def test_tier_enforcement():
            pass

    Returns:
        Pytest mark decorator
    """
    return pytest.mark.security


def regression() -> pytest.MarkDecorator:
    """Mark a test as a regression test.

    Regression tests validate that previously fixed bugs don't reoccur.

    Example:
        @pytest.mark.regression
        def test_cache_isolation():
            pass

    Returns:
        Pytest mark decorator
    """
    return pytest.mark.regression


# Make markers available as direct markers on pytest.mark
pytest_plugins = ["code_scalpel.testing.markers"]
