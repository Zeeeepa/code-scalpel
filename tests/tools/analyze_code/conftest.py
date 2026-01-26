"""Pytest configuration for analyze_code tests."""

import os
import pytest


@pytest.fixture(autouse=True)
def disable_cache():
    """Disable caching for all analyze_code tests."""
    old_value = os.environ.get("SCALPEL_CACHE_ENABLED")
    os.environ["SCALPEL_CACHE_ENABLED"] = "0"
    yield
    if old_value is not None:
        os.environ["SCALPEL_CACHE_ENABLED"] = old_value
    else:
        os.environ.pop("SCALPEL_CACHE_ENABLED", None)
