"""
Root conftest.py for pytest configuration.

This file must be at the repository root to properly configure pytest plugins.
Moved from tests/tools/rename_symbol/conftest.py due to pytest 9.x requirement.
"""

import pytest

# Plugins for rename_symbol tier testing
pytest_plugins = ["tests.tools.rename_symbol.governance_profiles"]
