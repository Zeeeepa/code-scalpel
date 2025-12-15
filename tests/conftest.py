"""
Pytest configuration and fixtures for Code Scalpel tests.

[20251213_FEATURE] v1.5.2 - OSV client test isolation fixtures with proper mock cleanup.
[20251214_FEATURE] v1.5.3 - OSV client import in ast_tools __init__ for full-suite fix.
"""

import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch
import urllib.error

# Add the src directory to the path so tests can import code_scalpel
# This allows tests to run both before and after pip install
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# [20251214_FEATURE] v1.5.3 - Ensure osv_client is imported early
# Now that ast_tools.__init__ imports osv_client, this will automatically
# make osv_client available in the ast_tools namespace
try:
    import code_scalpel.ast_tools  # noqa
except ImportError:
    pass


# =====================================================================
# OSV Client Fixtures (v1.5.2 - Test Isolation)
# =====================================================================
# [20251213_FEATURE] Function-scoped mocks ensure proper test isolation
# Prevents mock state leakage when running full test suite


@pytest.fixture(scope="function")
def osv_mock_urlopen():
    """
    Function-scoped mock for urllib.request.urlopen.

    Ensures complete isolation between tests - each test gets a fresh mock instance.
    This prevents mock state leakage which was the root cause of test failures when
    running the full test suite.

    Now that osv_client is imported in ast_tools.__init__, the patch target
    'code_scalpel.ast_tools.osv_client.urllib.request.urlopen' is always valid.

    Yields:
        MagicMock: A mock object configured to behave like urlopen.
    """
    patcher = patch("code_scalpel.ast_tools.osv_client.urllib.request.urlopen")
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture(scope="function")
def osv_client_no_cache(osv_mock_urlopen):
    """
    OSVClient instance with caching disabled and mocked network calls.

    Use this fixture when you want to test the OSV client without making real API calls.
    The mock is automatically cleaned up after each test.

    Args:
        osv_mock_urlopen: Injected osv_mock_urlopen fixture

    Returns:
        OSVClient: Configured client instance
    """
    # Import here to avoid module resolution issues
    from code_scalpel.ast_tools.osv_client import OSVClient

    return OSVClient(cache_enabled=False)


@pytest.fixture(scope="function")
def osv_client_with_cache(osv_mock_urlopen):
    """
    OSVClient instance with caching enabled and mocked network calls.

    Use this fixture when testing caching behavior.

    Args:
        osv_mock_urlopen: Injected osv_mock_urlopen fixture

    Returns:
        OSVClient: Configured client instance with caching
    """
    # Import here to avoid module resolution issues
    from code_scalpel.ast_tools.osv_client import OSVClient

    return OSVClient(cache_enabled=True)


@pytest.fixture(scope="function")
def mock_osv_response():
    """
    Factory fixture for creating mock OSV API responses.

    Returns:
        Callable: Function that creates a properly configured mock response

    Example:
        >>> mock_response = mock_osv_response()
        >>> mock_response.configure(vulns=[{"id": "CVE-123"}])
        >>> mock_urlopen.return_value = mock_response
    """

    def _create_response(data=None):
        """Create a mock response with proper context manager behavior."""
        mock_response = MagicMock()

        if data is None:
            data = {"vulns": []}

        mock_response.read.return_value = json.dumps(data).encode()
        # Context manager support for 'with' statement
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        return mock_response

    return _create_response


@pytest.fixture(scope="function")
def mock_osv_error():
    """
    Factory fixture for creating mock OSV API errors.

    Returns:
        Callable: Function that creates various error types

    Example:
        >>> mock_urlopen.side_effect = mock_osv_error("URLError")
    """

    def _create_error(error_type="URLError"):
        """Create appropriate error for the given type."""
        if error_type == "URLError":
            return urllib.error.URLError("Connection failed")
        elif error_type == "HTTPError":
            return urllib.error.HTTPError(
                "https://api.osv.dev/v1/query", 503, "Service Unavailable", {}, None
            )
        elif error_type == "Timeout":
            return TimeoutError("Request timeout")
        else:
            return Exception(f"Unknown error: {error_type}")

    return _create_error


# Auto-use fixture for cleanup
@pytest.fixture(autouse=True)
def reset_osv_cache():
    """
    Auto-used fixture to reset OSV client cache before each test.

    This ensures no state leakage from caching between tests.

    [20251213_FEATURE] v1.5.2 - Automatic cleanup for test isolation
    """
    yield
    # Cleanup after test
    try:
        from code_scalpel.ast_tools.osv_client import OSVClient

        client = OSVClient()
        client.clear_cache()
    except Exception:
        pass  # Ignore errors on cleanup
