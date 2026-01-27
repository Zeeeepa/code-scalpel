"""Pytest configuration for testing framework tests.

Imports and exposes all fixtures from the testing framework.
"""

from code_scalpel.testing.fixtures import (  # noqa: F401
    all_adapters,
    clear_all_caches,
    community_adapter,
    enterprise_adapter,
    enterprise_license_path,
    pro_adapter,
    pro_license_path,
    pytest_generate_tests,
    tier_adapter,
    with_community_tier,
    with_enterprise_license,
    with_pro_license,
)
