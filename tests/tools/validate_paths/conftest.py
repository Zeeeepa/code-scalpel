"""
Conftest for validate_paths tests.

[20260219_BUGFIX] Add autouse cache-clearing fixture to prevent tier state
leakage across tests. The licensing/test_license_validation.py tests mock
JWTLicenseValidator.validate, which can leave stale state in:
  - jwt_validator._LICENSE_VALIDATION_CACHE
  - protocol._LAST_VALID_LICENSE_TIER / _LAST_VALID_LICENSE_AT

Without this fixture, the MCP interface tests (which use monkeypatch.setenv
to request a specific tier) can pick up stale cached tier values from the
licensing tests that run before them.
"""

import pytest

from tests.utils.tier_setup import clear_tier_caches


@pytest.fixture(autouse=True)
def clear_tier_cache_for_validate_paths():
    """Clear tier caches before/after every test in validate_paths suite."""
    clear_tier_caches()
    yield
    clear_tier_caches()
