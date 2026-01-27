"""
Fixtures for capabilities tests.

Provides utilities for testing the capabilities resolver in CI environment.
"""

import os
from pathlib import Path

import pytest

LICENSE_DIR = Path(__file__).parent.parent / "licenses"


@pytest.fixture
def clear_capabilities_cache():
    """Clear capabilities resolver cache before and after each test."""
    from code_scalpel.capabilities import resolver

    # Clear before test
    resolver._LIMITS_CACHE = None

    yield

    # Clear after test
    resolver._LIMITS_CACHE = None


@pytest.fixture
def clear_tier_cache():
    """Clear tier detection cache before and after each test."""
    from code_scalpel.licensing import config_loader, jwt_validator
    from code_scalpel.mcp import server

    # Clear before test
    jwt_validator._LICENSE_VALIDATION_CACHE = None
    config_loader.clear_cache()
    if hasattr(server, "_cached_tier"):
        server._cached_tier = None
    if hasattr(server, "_LAST_VALID_LICENSE_AT"):
        server._LAST_VALID_LICENSE_AT = None
    if hasattr(server, "_LAST_VALID_LICENSE_TIER"):
        server._LAST_VALID_LICENSE_TIER = None

    # Clear environment variables
    os.environ.pop("CODE_SCALPEL_TIER", None)
    os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
    os.environ.pop("CODE_SCALPEL_LICENSE_KEY", None)
    os.environ.pop("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", None)
    os.environ.pop("CODE_SCALPEL_TEST_FORCE_TIER", None)

    yield

    # Clear after test
    jwt_validator._LICENSE_VALIDATION_CACHE = None
    config_loader.clear_cache()
    if hasattr(server, "_cached_tier"):
        server._cached_tier = None
    if hasattr(server, "_LAST_VALID_LICENSE_AT"):
        server._LAST_VALID_LICENSE_AT = None
    if hasattr(server, "_LAST_VALID_LICENSE_TIER"):
        server._LAST_VALID_LICENSE_TIER = None

    os.environ.pop("CODE_SCALPEL_TIER", None)
    os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
    os.environ.pop("CODE_SCALPEL_LICENSE_KEY", None)
    os.environ.pop("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", None)
    os.environ.pop("CODE_SCALPEL_TEST_FORCE_TIER", None)


@pytest.fixture
def clear_all_caches():
    """Clear both capabilities and tier caches."""
    from code_scalpel.capabilities import resolver
    from code_scalpel.licensing import config_loader, jwt_validator
    from code_scalpel.mcp import server

    # Clear before test
    resolver._LIMITS_CACHE = None
    jwt_validator._LICENSE_VALIDATION_CACHE = None
    config_loader.clear_cache()
    if hasattr(server, "_cached_tier"):
        server._cached_tier = None
    if hasattr(server, "_LAST_VALID_LICENSE_AT"):
        server._LAST_VALID_LICENSE_AT = None
    if hasattr(server, "_LAST_VALID_LICENSE_TIER"):
        server._LAST_VALID_LICENSE_TIER = None

    # Clear environment variables
    os.environ.pop("CODE_SCALPEL_TIER", None)
    os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
    os.environ.pop("CODE_SCALPEL_LICENSE_KEY", None)
    os.environ.pop("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", None)
    os.environ.pop("CODE_SCALPEL_TEST_FORCE_TIER", None)
    os.environ.pop("CODE_SCALPEL_LIMITS_FILE", None)

    yield

    # Clear after test
    resolver._LIMITS_CACHE = None
    jwt_validator._LICENSE_VALIDATION_CACHE = None
    config_loader.clear_cache()
    if hasattr(server, "_cached_tier"):
        server._cached_tier = None
    if hasattr(server, "_LAST_VALID_LICENSE_AT"):
        server._LAST_VALID_LICENSE_AT = None
    if hasattr(server, "_LAST_VALID_LICENSE_TIER"):
        server._LAST_VALID_LICENSE_TIER = None

    os.environ.pop("CODE_SCALPEL_TIER", None)
    os.environ.pop("CODE_SCALPEL_LICENSE_PATH", None)
    os.environ.pop("CODE_SCALPEL_LICENSE_KEY", None)
    os.environ.pop("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", None)
    os.environ.pop("CODE_SCALPEL_TEST_FORCE_TIER", None)
    os.environ.pop("CODE_SCALPEL_LIMITS_FILE", None)


@pytest.fixture
def pro_license_path() -> Path:
    """Path to valid Pro tier test license."""
    # Try different possible names since CI may inject with different naming
    candidates = [
        LICENSE_DIR / "code_scalpel_pro_20260127_004058.jwt",
        LICENSE_DIR / "code_scalpel_license_pro_20260101_190345.jwt",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"No Pro license found in {LICENSE_DIR}")


@pytest.fixture
def enterprise_license_path() -> Path:
    """Path to valid Enterprise tier test license."""
    # Try different possible names since CI may inject with different naming
    candidates = [
        LICENSE_DIR / "code_scalpel_enterprise_20260127_003946.jwt",
        LICENSE_DIR / "code_scalpel_license_enterprise_20260101_190754.jwt",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"No Enterprise license found in {LICENSE_DIR}")
