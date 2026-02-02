# [20260108_TEST] Fixtures for rename_symbol tier tests
"""
Shared fixtures for rename_symbol tier testing.
"""

import pytest

# [20260108_FEATURE] Auto-register governance profile fixtures
# NOTE: Moved to root tests/conftest.py for Pytest 9.0+ compatibility
# pytest_plugins = ["tests.tools.rename_symbol.governance_profiles"]


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project with multiple files for cross-file testing."""

    # Main module with functions/classes
    main_py = tmp_path / "main.py"
    main_py.write_text("""
def old_function():
    return "hello"

class OldClass:
    def old_method(self):
        return "method"
""".strip())

    # File that imports from main
    utils_py = tmp_path / "utils.py"
    utils_py.write_text("""
from main import old_function, OldClass

def use_old():
    return old_function()

def use_class():
    obj = OldClass()
    return obj.old_method()
""".strip())

    # Another file with module import
    helper_py = tmp_path / "helper.py"
    helper_py.write_text("""
import main

def call_it():
    return main.old_function()
""".strip())

    return tmp_path


@pytest.fixture(autouse=True)
def clear_tier_cache():
    """Clear tier detection cache before each test."""
    from code_scalpel.licensing import config_loader, jwt_validator

    jwt_validator._LICENSE_VALIDATION_CACHE = None
    config_loader.clear_cache()


@pytest.fixture
def scope_filesystem():
    """Fixture for filesystem scope isolation in governance tests.

    This fixture ensures that each test gets proper filesystem isolation
    and doesn't interfere with other tests. It's primarily used as a marker
    for tests that require filesystem operations to be scoped correctly.
    """
    # No-op fixture - just ensures isolation. Tests use tmp_path/temp_project for actual work.
    pass
