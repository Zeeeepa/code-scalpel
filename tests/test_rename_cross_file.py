"""[20260119_TEST] Compat shim to keep CI paths stable after test relocation.

This delegates to the current rename_symbol cross-file tests in
tests/tools/rename_symbol/test_rename_cross_file.py.
"""

from tests.tools.rename_symbol.test_rename_cross_file import *  # noqa: F401,F403
