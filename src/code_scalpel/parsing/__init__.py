"""
Unified parsing infrastructure with deterministic error handling.

All AST parsing flows through this module, ensuring consistent behavior
controlled by response_config.json.
"""

from .unified_parser import (
    parse_python_code,
    parse_javascript_code,
    ParsingError,
    SanitizationReport,
)

__all__ = [
    "parse_python_code",
    "parse_javascript_code",
    "ParsingError",
    "SanitizationReport",
]
