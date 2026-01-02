import importlib
import os
from sys import path

# [20251214_TEST] Preserve static imports for resolver coverage; keep them referenced to satisfy lint
_ = (os.name, len(path))


# Dynamic imports (should NOT be detected yet)
def dynamic_loader():
    # importlib.import_module
    importlib.import_module("math")

    # __import__
    __import__("json")

    # Variable import (should be detected in Phase 2)
    mod_name = "datetime"
    importlib.import_module(mod_name)

    # Variable import with __import__
    json_name = "json"
    __import__(json_name)
