import json
import logging
import os
import sys
import threading
import urllib.request
from typing import Optional

from code_scalpel import __version__

logger = logging.getLogger(__name__)


def get_latest_pypi_version() -> Optional[str]:
    """Fetch the latest version of codescalpel from PyPI."""
    try:
        req = urllib.request.Request(
            "https://pypi.org/pypi/codescalpel/json",
            headers={"User-Agent": f"CodeScalpel/{__version__}"},
        )
        with urllib.request.urlopen(req, timeout=5) as response:  # nosec B310
            data = json.loads(response.read().decode("utf-8"))
            return data.get("info", {}).get("version")
    except Exception as e:
        logger.debug(f"Failed to check PyPI for updates: {e}")
        return None


def check_version_mismatch():
    """
    Check if the current version matches the latest on PyPI.
    Action is determined by CODE_SCALPEL_VERSION_MISMATCH_ACTION env var.
    Valid actions: 'warn' (default), 'error', 'ignore', 'auto-upgrade'
    """
    action = os.environ.get("CODE_SCALPEL_VERSION_MISMATCH_ACTION", "warn").lower()

    if action == "ignore":
        return

    latest_version = get_latest_pypi_version()
    if not latest_version:
        return

    if latest_version != __version__:
        msg = (
            f"\n{'='*60}\n"
            f"VERSION MISMATCH DETECTED\n"
            f"Current Code Scalpel version: {__version__}\n"
            f"Latest PyPI version: {latest_version}\n"
            f"{'='*60}\n"
        )

        if action == "error":
            print(msg, file=sys.stderr)
            print(
                "Exiting due to CODE_SCALPEL_VERSION_MISMATCH_ACTION=error",
                file=sys.stderr,
            )
            os._exit(1)  # Hard exit to kill the server immediately

        elif action == "auto-upgrade":
            print(msg, file=sys.stderr)
            print("Auto-upgrading Code Scalpel...", file=sys.stderr)
            import subprocess

            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "codescalpel"]
                )
                print(
                    "Upgrade successful. Please restart the MCP server.",
                    file=sys.stderr,
                )
                os._exit(0)
            except subprocess.CalledProcessError as e:
                print(f"Auto-upgrade failed: {e}", file=sys.stderr)

        else:  # default to warn
            print(msg, file=sys.stderr)
            print("To upgrade, run: pip install --upgrade codescalpel", file=sys.stderr)


def start_version_check_thread():
    """Start the version check in a background thread so it doesn't block startup."""
    thread = threading.Thread(target=check_version_mismatch, daemon=True)
    thread.start()
