"""
Security tests for cryptographic verification.

Re-exports from packages/codescalpel-agents/tests/autonomy/test_crypto_verify.py for compatibility
with standard test directory layout.

# [20250125_REFACTOR] v3.3.0 - Re-export from agents package after reorganization
"""

# Re-export all test classes and fixtures from the canonical location in agents package
# Note: This requires the agents package to be installed (pip install codescalpel[agents])
import sys
import os

# Add agents package tests to path
agents_tests = os.path.join(
    os.path.dirname(__file__), "../../packages/codescalpel-agents/tests"
)
if agents_tests not in sys.path:
    sys.path.insert(0, agents_tests)

try:
    from autonomy.test_crypto_verify import *  # noqa: F401, F403
except ImportError as e:
    raise ImportError(
        "This test requires the agents package. Install with: pip install codescalpel[agents]"
    ) from e
