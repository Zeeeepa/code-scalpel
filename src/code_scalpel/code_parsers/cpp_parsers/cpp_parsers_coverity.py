#!/usr/bin/env python3
"""
Coverity Parser - Deep Security and Quality Analysis (Enterprise).

[20260303_FEATURE] Full implementation: parse Coverity JSON export files,
categorize defects, map to CWE, and generate normalized reports.

Coverity requires a licensed installation and server. This parser handles
the *output* of cov-analyze / cov-commit-defects JSON exports, not execution.

Reference: https://scan.coverity.com/
Export:    cov-format-errors --dir /path/to/idir --json-output-v2 report.json
"""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class DefectSeverity(Enum):
    """Coverity defect severity levels."""

    UNCLASSIFIED = "unclassified"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DefectType(Enum):
    """Coverity defect type categories."""

    SECURITY = "security"
    RELIABILITY = "reliability"
    MAINTAINABILITY = "maintainability"
    PERFORMANCE = "performance"
    CONCURRENCY = "concurrency"


@dataclass
class CoverityDefect:
    """Represents a Coverity defect finding."""

    defect_id: str
    defect_type: DefectType
    severity: DefectSeverity
    message: str
    file_path: str
    line_number: int
    cwe_id: Optional[str] = None
    impact: Optional[str] = None
    evidence_chain: Optional[List[str]] = None


@dataclass
class CoverityConfig:
    """Coverity configuration for analysis."""

    coverity_version: str = "2024.12"
    api_endpoint: Optional[str] = None
    auth_token: Optional[str] = None
    project_name: Optional[str] = None
    stream_name: Optional[str] = None


# --- Internal helpers ------------------------------------------------------- #

# Map Coverity checkerName prefixes/keywords to DefectType
_CHECKER_TYPE_MAP: List[tuple] = [
    ("NULL_RETURNS", DefectType.RELIABILITY),
    ("FORWARD_NULL", DefectType.RELIABILITY),
    ("DEREFERENCE", DefectType.RELIABILITY),
    ("USE_AFTER_FREE", DefectType.SECURITY),
    ("BUFFER_SIZE", DefectType.SECURITY),
    ("TAINTED", DefectType.SECURITY),
    ("HARDCODED_CREDENTIALS", DefectType.SECURITY),
    ("RESOURCE_LEAK", DefectType.RELIABILITY),
    ("MEMORY_LEAK", DefectType.RELIABILITY),
    ("DEADLOCK", DefectType.CONCURRENCY),
    ("DATA_RACE", DefectType.CONCURRENCY),
    ("LOCK", DefectType.CONCURRENCY),
    ("DIVIDE_BY_ZERO", DefectType.RELIABILITY),
    ("OVERRUN", DefectType.SECURITY),
    ("UNUSED_VALUE", DefectType.MAINTAINABILITY),
    ("DEAD_CODE", DefectType.MAINTAINABILITY),
    ("COPY_PASTE_ERROR", DefectType.MAINTAINABILITY),
    ("INEFFICIENT", DefectType.PERFORMANCE),
]

# Coverity severity string normalisation
_SEVERITY_MAP: Dict[str, DefectSeverity] = {
    "high": DefectSeverity.HIGH,
    "medium": DefectSeverity.MEDIUM,
    "low": DefectSeverity.LOW,
    "major": DefectSeverity.HIGH,
    "moderate": DefectSeverity.MEDIUM,
    "minor": DefectSeverity.LOW,
    "unclassified": DefectSeverity.UNCLASSIFIED,
}


def _checker_to_defect_type(checker_name: str) -> DefectType:
    """Map a Coverity checker name to DefectType."""
    upper = checker_name.upper()
    for keyword, dtype in _CHECKER_TYPE_MAP:
        if keyword in upper:
            return dtype
    return DefectType.RELIABILITY


def _parse_severity(raw: str) -> DefectSeverity:
    """Normalise a Coverity severity string."""
    return _SEVERITY_MAP.get(raw.lower(), DefectSeverity.UNCLASSIFIED)


def _extract_event_chain(events: List[Dict[str, Any]]) -> List[str]:
    """Extract human-readable evidence chain from events array."""
    chain = []
    for event in events:
        desc = event.get("eventDescription", event.get("description", ""))
        file_path = event.get("filePathname", event.get("filePath", ""))
        line = event.get("lineNumber", event.get("line", 0))
        if desc:
            chain.append(f"{file_path}:{line}: {desc}")
    return chain


def _parse_single_issue(issue: Dict[str, Any]) -> CoverityDefect:
    """Parse one issue dict from Coverity JSON output."""
    checker_name = issue.get("checkerName", "")
    cwe_raw = issue.get("cwe")
    cwe_id = f"CWE-{cwe_raw}" if cwe_raw else None
    severity_raw = issue.get("severity", issue.get("impact", "unclassified"))

    events = issue.get("events", [])
    # Primary location is typically the first event
    if events:
        primary = events[0]
        file_path = primary.get("filePathname", primary.get("filePath", ""))
        line_number = primary.get("lineNumber", primary.get("line", 0))
        message = primary.get("eventDescription", primary.get("description", ""))
    else:
        file_path = issue.get("filePathname", "")
        line_number = issue.get("lineNumber", 0)
        message = issue.get("extra", checker_name)

    return CoverityDefect(
        defect_id=str(issue.get("mergeKey", issue.get("cid", checker_name))),
        defect_type=_checker_to_defect_type(checker_name),
        severity=_parse_severity(severity_raw),
        message=message,
        file_path=file_path,
        line_number=line_number,
        cwe_id=cwe_id,
        impact=issue.get("impact"),
        evidence_chain=_extract_event_chain(events) or None,
    )


def _to_sarif_result(defect: CoverityDefect) -> Dict[str, Any]:
    """Convert a CoverityDefect to a SARIF 2.1 result dict."""
    level = "error" if defect.severity == DefectSeverity.HIGH else "warning"
    result: Dict[str, Any] = {
        "ruleId": defect.defect_id,
        "level": level,
        "message": {"text": defect.message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": defect.file_path},
                    "region": {"startLine": defect.line_number},
                }
            }
        ],
    }
    if defect.cwe_id:
        result["taxa"] = [{"id": defect.cwe_id, "toolComponent": {"name": "CWE"}}]
    return result


# ---------------------------------------------------------------------------- #


class CoverityParser:
    """
    Parser for Coverity deep security and quality analysis (enterprise tool).

    [20260303_FEATURE] Handles Coverity JSON export files.
    Coverity requires a licensed installation; this parser handles the
    *output* of cov-format-errors, not direct execution.

    Execution raises NotImplementedError with instructive message.
    """

    def __init__(self) -> None:
        """Initialize Coverity parser."""
        self.config = CoverityConfig()
        self.defects: List[CoverityDefect] = []

    # ------------------------------------------------------------------ #
    # Execution (enterprise — raises NotImplementedError)                 #
    # ------------------------------------------------------------------ #

    def execute_coverity(
        self,
        _paths: List[Path],
        _config: Optional[CoverityConfig] = None,
    ) -> List[CoverityDefect]:
        """
        Not available — Coverity requires a licensed installation.

        To use this parser:
          1. Run cov-build / cov-analyze / cov-format-errors externally.
          2. Export findings with:
               cov-format-errors --dir /path/to/idir --json-output-v2 report.json
          3. Pass the exported JSON file to parse_json_report().
        """
        raise NotImplementedError(
            "Coverity requires a licensed Coverity Static Analysis installation. "
            "Run cov-build + cov-analyze + cov-format-errors externally, then "
            "pass the resulting JSON file to parse_json_report() instead."
        )

    # ------------------------------------------------------------------ #
    # Parsing                                                              #
    # ------------------------------------------------------------------ #

    def parse_json_report(self, report_path: Path) -> List[CoverityDefect]:
        """
        Parse a Coverity JSON export file (cov-format-errors --json-output-v2).

        The top-level key may be 'issues' (v2 format) or 'mergedDefects'
        (Coverity Connect REST API format).
        """
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return self.parse_coverity_json(data)

    def parse_json_string(self, json_str: str) -> List[CoverityDefect]:
        """Parse Coverity JSON from a string."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return []
        return self.parse_coverity_json(data)

    def parse_coverity_json(self, json_data: Dict[str, Any]) -> List[CoverityDefect]:
        """
        Parse Coverity JSON data dict.

        Handles:
          - cov-format-errors v2: {"issues": [...]}
          - Coverity Connect REST API: {"mergedDefects": [...]}
        """
        issues = json_data.get("issues", json_data.get("mergedDefects", []))
        return [_parse_single_issue(issue) for issue in issues]

    # ------------------------------------------------------------------ #
    # Configuration                                                        #
    # ------------------------------------------------------------------ #

    def load_config(self, config_file: Path) -> CoverityConfig:
        """Load Coverity config from a JSON file."""
        cfg = CoverityConfig()
        try:
            data = json.loads(config_file.read_text(encoding="utf-8"))
            cfg.api_endpoint = data.get("server_url", cfg.api_endpoint)
            cfg.auth_token = data.get("auth_key", cfg.auth_token)
            cfg.project_name = data.get("project", cfg.project_name)
            cfg.stream_name = data.get("stream", cfg.stream_name)
        except (OSError, json.JSONDecodeError):
            pass
        return cfg

    # ------------------------------------------------------------------ #
    # Analysis                                                             #
    # ------------------------------------------------------------------ #

    def categorize_defects(
        self, defects: List[CoverityDefect]
    ) -> Dict[DefectType, List[CoverityDefect]]:
        """Group defects by DefectType."""
        result: Dict[DefectType, List[CoverityDefect]] = {
            dt: [] for dt in DefectType
        }
        for defect in defects:
            result[defect.defect_type].append(defect)
        return result

    def analyze_security_risks(
        self, defects: List[CoverityDefect]
    ) -> Dict[str, Any]:
        """Summarize security-relevant defects and CWE coverage."""
        security = [d for d in defects if d.defect_type == DefectType.SECURITY]
        high = [d for d in defects if d.severity == DefectSeverity.HIGH]
        cwe_ids = sorted({d.cwe_id for d in defects if d.cwe_id})
        return {
            "total_defects": len(defects),
            "security_defects": len(security),
            "high_severity": len(high),
            "cwe_ids": cwe_ids,
            "security_by_severity": {
                sev.value: len([d for d in security if d.severity == sev])
                for sev in DefectSeverity
                if any(d.severity == sev for d in security)
            },
        }

    def map_to_cwe(
        self, defects: List[CoverityDefect]
    ) -> Dict[str, List[CoverityDefect]]:
        """Group defects by CWE identifier (e.g. 'CWE-476')."""
        result: Dict[str, List[CoverityDefect]] = {}
        for defect in defects:
            if defect.cwe_id:
                result.setdefault(defect.cwe_id, []).append(defect)
        return result

    def track_defect_trends(
        self, historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare defect counts across historical snapshots.

        Each item in historical_data should be a dict with keys:
            timestamp (str), total (int), by_type (dict), by_severity (dict)
        """
        if not historical_data:
            return {"trend": "no_data", "snapshots": 0}

        counts = [entry.get("total", 0) for entry in historical_data]
        if len(counts) > 1:
            delta = counts[-1] - counts[-2]
            trend = "improving" if delta < 0 else ("worsening" if delta > 0 else "stable")
        else:
            trend = "baseline"

        return {
            "trend": trend,
            "snapshots": len(historical_data),
            "latest_total": counts[-1] if counts else 0,
            "delta_from_previous": (counts[-1] - counts[-2]) if len(counts) > 1 else 0,
            "history": counts,
        }

    # ------------------------------------------------------------------ #
    # Reporting                                                            #
    # ------------------------------------------------------------------ #

    def generate_report(
        self, defects: List[CoverityDefect], format: str = "json"
    ) -> str:
        """Generate a normalized report in JSON or SARIF 2.1 format."""
        if format == "sarif":
            sarif = {
                "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {
                            "driver": {
                                "name": "Coverity",
                                "version": self.config.coverity_version,
                            }
                        },
                        "results": [_to_sarif_result(d) for d in defects],
                    }
                ],
            }
            return json.dumps(sarif, indent=2)

        by_type: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        for defect in defects:
            by_type[defect.defect_type.value] = (
                by_type.get(defect.defect_type.value, 0) + 1
            )
            by_severity[defect.severity.value] = (
                by_severity.get(defect.severity.value, 0) + 1
            )

        report = {
            "tool": "coverity",
            "defects": [
                {
                    "id": d.defect_id,
                    "type": d.defect_type.value,
                    "severity": d.severity.value,
                    "message": d.message,
                    "file": d.file_path,
                    "line": d.line_number,
                    "cwe": d.cwe_id,
                    "impact": d.impact,
                }
                for d in defects
            ],
            "summary": {
                "total": len(defects),
                "by_type": by_type,
                "by_severity": by_severity,
                "cwe_coverage": sorted({d.cwe_id for d in defects if d.cwe_id}),
            },
        }
        return json.dumps(report, indent=2)
