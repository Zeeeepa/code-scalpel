"""[20260119_TEST] Compat shim to keep CI paths stable after test relocation.

Delegates to the autonomy governance budget enforcement tests in
tests/autonomy/test_governance_budget_enforcement.py.
"""

from tests.autonomy.test_governance_budget_enforcement import *  # noqa: F401,F403
