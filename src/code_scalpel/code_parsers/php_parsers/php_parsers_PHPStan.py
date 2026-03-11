#!/usr/bin/env python3
"""PHPStan Parser — PHP static type checker (levels 0–9).

[20260304_FEATURE] Phase 2: full implementation.

Reference: https://phpstan.org/
Command:   vendor/bin/phpstan analyse --error-format=json [paths...]
Output:    {"totals":{...},"files":{...},"errors":[...]}
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# ---------------------------------------------------------------------------
# CWE mapping
# ---------------------------------------------------------------------------

_CWE_MAP: Dict[str, str] = {
    "undefined": "CWE-824",
    "null": "CWE-476",
    "division by zero": "CWE-369",
    "type": "CWE-704",
    "dead code": "CWE-561",
    "unreachable": "CWE-561",
}

_PHPSTAN_BINARY_CANDIDATES = [
    "phpstan",
    "./vendor/bin/phpstan",
    "vendor/bin/phpstan",
]


def _find_phpstan() -> Optional[str]:
    for candidate in _PHPSTAN_BINARY_CANDIDATES:
        if shutil.which(candidate):
            return candidate
    return None


def _infer_error_type(message: str) -> str:
    lower = message.lower()
    if "undefined" in lower or "not found" in lower or "does not exist" in lower:
        return PHPStanErrorType.UNDEFINED.value
    if "dead code" in lower or "unreachable" in lower:
        return PHPStanErrorType.DEAD_CODE.value
    if "method" in lower and "signature" in lower:
        return PHPStanErrorType.METHOD_SIGNATURE.value
    if "property" in lower or "cannot access" in lower:
        return PHPStanErrorType.PROPERTY_ACCESS.value
    if "type" in lower or "does not accept" in lower or "expect" in lower:
        return PHPStanErrorType.TYPE_ERROR.value
    return PHPStanErrorType.UNKNOWN.value


def _infer_cwe(message: str) -> Optional[str]:
    lower = message.lower()
    for keyword, cwe in _CWE_MAP.items():
        if keyword in lower:
            return cwe
    return None


class PHPStanLevel(Enum):
    """PHPStan analysis levels (0=most lenient, 8=strictest)."""

    LEVEL0 = 0
    LEVEL1 = 1
    LEVEL2 = 2
    LEVEL3 = 3
    LEVEL4 = 4
    LEVEL5 = 5
    LEVEL6 = 6
    LEVEL7 = 7
    LEVEL8 = 8


class PHPStanErrorType(Enum):
    """PHPStan error type categories."""

    TYPE_ERROR = "type_error"
    DEAD_CODE = "dead_code"
    UNDEFINED = "undefined"
    LOGIC_ERROR = "logic_error"
    METHOD_SIGNATURE = "method_signature"
    PROPERTY_ACCESS = "property_access"
    UNKNOWN = "unknown"


@dataclass
@dataclass
class PHPStanError:
    """Represents a single PHPStan analysis error.

    [20260304_FEATURE] Added cwe_id field.
    """

    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    error_type: Optional[str] = None
    level: Optional[int] = None
    rule: Optional[str] = None
    cwe_id: Optional[str] = None


@dataclass
class PHPStanConfig:
    """PHPStan configuration settings."""

    config_file: Optional[Path] = None
    analysis_level: int = 5
    paths: List[str] = field(default_factory=list)
    excluded_paths: List[str] = field(default_factory=list)
    memory_limit: str = "2GB"


class PHPStanParser:
    """Parser for PHPStan static analysis results."""

    def __init__(self) -> None:
        """Initialize PHPStan parser."""
        self.errors: List[PHPStanError] = []
        self.config: Optional[PHPStanConfig] = None
        self.language = "php"

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute_phpstan(
        self,
        paths: Union[List[str], str, None] = None,
        level: int = 5,
        config_file: Optional[Path] = None,
        memory_limit: str = "2GB",
    ) -> List["PHPStanError"]:
        """Run phpstan analyse and return parsed errors.

        Returns ``[]`` gracefully when phpstan is not on PATH.
        """
        binary = _find_phpstan()
        if binary is None:
            return []
        target_paths: List[str] = (
            ["."]
            if paths is None
            else [paths] if isinstance(paths, str) else list(paths)
        )
        cmd = [
            binary,
            "analyse",
            "--error-format=json",
            f"--level={level}",
            f"--memory-limit={memory_limit}",
        ]
        if config_file:
            cmd += ["-c", str(config_file)]
        cmd += ["--no-progress"] + target_paths
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            self.errors = self.parse_json_report(result.stdout)
            return self.errors
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def parse_json_report(self, json_data: str) -> List["PHPStanError"]:
        """Parse PHPStan --error-format=json output.

        [20260304_FEATURE] Handles both ``files`` (per-file) and top-level ``errors``.

        Args:
            json_data: JSON text from phpstan stdout.
        Returns:
            List of PHPStanError objects.
        """
        errors: List[PHPStanError] = []
        if not json_data:
            return errors
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return errors
        for file_path, file_data in data.get("files", {}).items():
            for msg_obj in file_data.get("messages", []):
                message = msg_obj.get("message", "")
                errors.append(
                    PHPStanError(
                        message=message,
                        file_path=file_path,
                        line_number=msg_obj.get("line"),
                        error_type=_infer_error_type(message),
                        cwe_id=_infer_cwe(message),
                    )
                )
        for msg in data.get("errors", []):
            if isinstance(msg, str):
                errors.append(
                    PHPStanError(
                        message=msg,
                        error_type=PHPStanErrorType.UNKNOWN.value,
                        cwe_id=_infer_cwe(msg),
                    )
                )
        return errors

    def parse_json_inline(self, json_data: str) -> List["PHPStanError"]:
        """Parse PHPStan --error-format=json-inline output (one JSON object per line)."""
        errors: List[PHPStanError] = []
        for line in json_data.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = obj.get("message", "")
            errors.append(
                PHPStanError(
                    message=message,
                    file_path=obj.get("file"),
                    line_number=obj.get("line"),
                    error_type=_infer_error_type(message),
                    cwe_id=_infer_cwe(message),
                )
            )
        return errors

    def parse_output(self, output: str) -> List["PHPStanError"]:
        """Parse raw phpstan output — tries JSON then JSON-inline."""
        output = output.strip()
        if not output:
            return []
        if output.startswith("{"):
            return self.parse_json_report(output)
        return self.parse_json_inline(output)

    def load_config(self, config_path: Path) -> PHPStanConfig:
        """Load phpstan.neon config file (best-effort)."""
        config = PHPStanConfig(config_file=config_path)
        try:
            text = config_path.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("level:"):
                    try:
                        config.analysis_level = int(stripped.split(":", 1)[1].strip())
                    except ValueError:
                        pass
        except OSError:
            pass
        return config

    def generate_type_coverage(self) -> dict[str, Any]:
        """Return type-coverage stub (needs phpstan extension)."""
        return {
            "tool": "phpstan",
            "coverage": None,
            "note": "Requires phpstan/phpstan-strict-rules or phpstan-coverage extension",
        }

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def categorize_by_type(
        self, errors: List["PHPStanError"]
    ) -> dict[str, List["PHPStanError"]]:
        """Group errors by error_type."""
        result: dict[str, List[PHPStanError]] = {}
        for e in errors:
            key = e.error_type or PHPStanErrorType.UNKNOWN.value
            result.setdefault(key, []).append(e)
        return result

    def generate_report(
        self,
        errors: Optional[List["PHPStanError"]] = None,
        fmt: str = "json",
    ) -> str:
        """Return JSON or text summary report.

        Args:
            errors: Errors to report; defaults to ``self.errors``.
            fmt: ``"json"`` (default) or ``"text"``.
        """
        errs = errors if errors is not None else self.errors
        by_type = self.categorize_by_type(errs)
        if fmt == "json":
            return json.dumps(
                {
                    "tool": "phpstan",
                    "total_errors": len(errs),
                    "by_type": {k: len(v) for k, v in by_type.items()},
                    "errors": [
                        {
                            "file": e.file_path,
                            "line": e.line_number,
                            "type": e.error_type,
                            "cwe": e.cwe_id,
                            "message": e.message,
                        }
                        for e in errs
                    ],
                },
                indent=2,
            )
        return "\n".join(
            f"{e.file_path or '<project>'}:{e.line_number or '?'}: {e.message}"
            for e in errs
        )
