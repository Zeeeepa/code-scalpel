"""
[20251214_TEST] Coverage for symbolic_execution_tools package initialization.
"""

import importlib


def test_symbolic_execution_init_exports_and_warns(recwarn):
    """Test symbolic_execution_tools module exports correctly."""
    module = importlib.reload(
        importlib.import_module("code_scalpel.symbolic_execution_tools")
    )

    assert "SymbolicAnalyzer" in module.__all__
    assert module.CrossFileTaintTracker is None or module.CrossFileTaintTracker
    # [20251218_TEST] Warning was disabled in v3.0.0 - no longer checking for it


# [20251214_TEST] Ensure import gracefully handles missing cross_file_taint module.
def test_symbolic_execution_init_missing_cross_file(monkeypatch):
    import sys
    import types

    fake = types.ModuleType("code_scalpel.symbolic_execution_tools.cross_file_taint")
    monkeypatch.setitem(
        sys.modules, "code_scalpel.symbolic_execution_tools.cross_file_taint", fake
    )

    module = importlib.reload(
        importlib.import_module("code_scalpel.symbolic_execution_tools")
    )

    assert module.CrossFileTaintTracker is None
