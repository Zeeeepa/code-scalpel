"""C++ (and future polyglot) static-analysis tool MCP registration.

[20260303_FEATURE] New MCP tool ``run_static_analysis`` wires the C++ tool
parser registry (Cppcheck, clang-tidy, Clang-SA, cpplint, Coverity, SonarQube)
to the MCP surface and, via tool_bridge, to the CLI.

Design notes
------------
- Free/open tools (Cppcheck, clang-tidy, Clang-SA, cpplint) are available at
  Community tier and above.
- Enterprise-only tools (Coverity, SonarQube) require Enterprise tier for
  execution; all tiers can *parse* a pre-existing report file.
- Community: max 50 findings returned.
- Pro / Enterprise: unlimited findings returned.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from code_scalpel import __version__ as _pkg_version
from code_scalpel.mcp.contract import ToolError, ToolResponseEnvelope, make_envelope
from code_scalpel.mcp.protocol import _get_current_tier, mcp

# ---------------------------------------------------------------------------
# Tier / capability helpers
# ---------------------------------------------------------------------------

# Tools that raise NotImplementedError for execution (server/enterprise required).
_ENTERPRISE_EXEC_TOOLS = {"coverity", "sonarqube", "sonar", "sonar-cpp"}

# Max findings returned at Community tier.
_COMMUNITY_MAX_FINDINGS = 50


def _get_max_findings(tier: str) -> int:
    """Return the findings cap for the given tier."""
    return _COMMUNITY_MAX_FINDINGS if tier == "community" else -1


def _check_enterprise_exec(tool_key: str, tier: str) -> Optional[ToolError]:
    """Return a ToolError if a non-enterprise user attempts to *execute*
    an enterprise-only tool without providing a pre-existing report_path."""
    if tool_key in _ENTERPRISE_EXEC_TOOLS and tier != "enterprise":
        return ToolError(
            error=(
                f"Executing '{tool_key}' requires Enterprise tier. "
                "Provide a pre-existing 'report_path' to parse an existing "
                "report at your current tier, or upgrade to Enterprise."
            ),
            error_code="upgrade_required",
            error_details={"required_tier": "enterprise"},
        )
    return None


# ---------------------------------------------------------------------------
# Synchronous implementation (runs in a thread)
# ---------------------------------------------------------------------------


def _run_static_analysis_sync(
    language: str,
    paths: List[str],
    tool: str,
    report_path: Optional[str],
    tier: str,
) -> Dict[str, Any]:
    """Run the appropriate tool parser and return structured findings.

    [20260303_FEATURE] Core sync implementation dispatched via asyncio.to_thread.
    """
    language_lower = language.lower()

    # -----------------------------------------------------------------------
    # C++ dispatch
    # -----------------------------------------------------------------------
    if language_lower in ("cpp", "c++", "cxx"):
        from code_scalpel.code_parsers.cpp_parsers import CppParserRegistry

        registry = CppParserRegistry()
        try:
            parser = registry.get_parser(tool)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

        tool_key = tool.lower()
        findings: List[Any] = []

        if report_path is not None:
            # Parse a pre-existing report file — allowed at all tiers.
            findings = _parse_report(parser, tool_key, Path(report_path))
        else:
            # Execute the tool CLI — enterprise-only tools raise UpgradeRequired.
            exec_err = _check_enterprise_exec(tool_key, tier)
            if exec_err is not None:
                raise _UpgradeRequired(exec_err)
            findings = _execute_tool(parser, tool_key, paths)

        # Apply community cap.
        max_findings = _get_max_findings(tier)
        truncated = False
        if max_findings > 0 and len(findings) > max_findings:
            findings = findings[:max_findings]
            truncated = True

        # Convert dataclass findings to dicts for serialisation.
        findings_dicts = [_finding_to_dict(f) for f in findings]

        # Attempt to generate a structured report via the parser.
        try:
            report_json = parser.generate_report(findings, format="json")
            import json as _json
            report_data = _json.loads(report_json)
        except Exception:
            report_data = {"tool": tool_key, "findings": findings_dicts}

        return {
            "success": True,
            "language": "cpp",
            "tool": tool_key,
            "finding_count": len(findings_dicts),
            "findings": findings_dicts,
            "truncated": truncated,
            "max_findings_applied": max_findings if max_findings > 0 else None,
            "report": report_data,
            "tier_applied": tier,
        }

    raise ValueError(
        f"Language '{language}' is not supported by run_static_analysis. "
        "Supported: cpp"
    )


# ---------------------------------------------------------------------------
# Parser dispatch helpers
# ---------------------------------------------------------------------------


def _execute_tool(parser: Any, tool_key: str, paths: List[str]) -> List[Any]:
    """Dispatch to the correct execute_* method based on tool key."""
    methods = {
        "cppcheck": "execute_cppcheck",
        "clang-tidy": "execute_clang_tidy",
        "clang_tidy": "execute_clang_tidy",
        "clangtidy": "execute_clang_tidy",
        "clang-sa": "execute_scan_build",
        "clang-static-analyzer": "execute_scan_build",
        "clangsa": "execute_scan_build",
        "cpplint": "execute_cpplint",
        "coverity": "execute_coverity",
        "sonarqube": "execute_sonarqube",
        "sonar": "execute_sonarqube",
        "sonar-cpp": "execute_sonarqube",
    }
    method_name = methods.get(tool_key)
    if method_name and hasattr(parser, method_name):
        method = getattr(parser, method_name)
        # Most execute methods take a list of paths.
        try:
            return method(paths) or []
        except TypeError:
            # Some take a single path.
            return method(paths[0] if paths else ".") or []
    return []


def _parse_report(parser: Any, tool_key: str, report_path: Path) -> List[Any]:
    """Dispatch to the correct parse_*_report method based on tool key."""
    suffix = report_path.suffix.lower()

    # Try format-specific methods first.
    if suffix in (".xml",) and hasattr(parser, "parse_xml_report"):
        return parser.parse_xml_report(report_path) or []
    if suffix in (".json",) and hasattr(parser, "parse_json_report"):
        return parser.parse_json_report(report_path) or []
    if suffix in (".plist",) and hasattr(parser, "parse_plist_report"):
        return parser.parse_plist_report(report_path) or []

    # Fallback: try xml then json then plist.
    for attr_name in ("parse_xml_report", "parse_json_report", "parse_plist_report"):
        if hasattr(parser, attr_name):
            try:
                result = getattr(parser, attr_name)(report_path) or []
                return result
            except Exception:
                continue
    return []


def _finding_to_dict(finding: Any) -> Dict[str, Any]:
    """Convert a dataclass/object finding to a plain dict."""
    if hasattr(finding, "__dataclass_fields__"):
        import dataclasses
        return dataclasses.asdict(finding)
    if hasattr(finding, "model_dump"):
        return finding.model_dump()
    if hasattr(finding, "__dict__"):
        return {k: v for k, v in finding.__dict__.items() if not k.startswith("_")}
    return {"value": str(finding)}


# ---------------------------------------------------------------------------
# Sentinel exception for upgrade-required signalling
# ---------------------------------------------------------------------------


class _UpgradeRequired(Exception):
    """Carries a ToolError for tier-upgrade scenarios."""

    def __init__(self, tool_error: ToolError) -> None:
        super().__init__(tool_error.error)
        self.tool_error = tool_error


# ---------------------------------------------------------------------------
# MCP tool registration
# ---------------------------------------------------------------------------


@mcp.tool(
    description=(
        "Run C++ static-analysis tools (Cppcheck, clang-tidy, Clang-SA, cpplint, "
        "Coverity, SonarQube) against source files or pre-existing report files."
    )
)
async def run_static_analysis(
    paths: List[str],
    tool: str = "cppcheck",
    language: str = "cpp",
    report_path: Optional[str] = None,
) -> ToolResponseEnvelope:
    """Run C++ static-analysis tools and return structured findings.

    Dispatches to the appropriate tool parser from ``CppParserRegistry``.
    When a tool CLI binary is not installed the parser returns an empty
    findings list (no error).  Provide ``report_path`` to parse a
    pre-existing report file instead of executing the tool.

    **Tier Behavior:**
    - Community: Free tools (cppcheck, clang-tidy, clang-sa, cpplint) — max 50
      findings.  Parse-only for enterprise tools.
    - Pro: Free tools — unlimited findings.  Parse-only for enterprise tools.
    - Enterprise: All tools including Coverity and SonarQube — unlimited
      findings.

    **Supported tools (``tool`` parameter):**
    - ``cppcheck``             — Cppcheck open-source static analyser
    - ``clang-tidy``           — LLVM clang-tidy modernisation checks
    - ``clang-sa``             — Clang Static Analyzer (scan-build)
    - ``cpplint``              — Google C++ style-guide linter
    - ``coverity``             — Synopsys Coverity (Enterprise; exec only)
    - ``sonarqube``            — SonarQube platform (Enterprise; exec only)

    **Args:**
        paths (List[str]): Source files or directories to analyse.
        tool (str): Static analysis tool to run. Default: ``cppcheck``.
        language (str): Source language. Currently only ``cpp`` is supported.
            Default: ``cpp``.
        report_path (str, optional): Path to a pre-existing report file.
            When provided the tool CLI is *not* executed; the report is parsed
            instead.  All tiers may parse enterprise tool reports.

    **Returns:**
        ToolResponseEnvelope with a dict containing:
        - success (bool): True if analysis completed without fatal errors.
        - language (str): Language analysed (``cpp``).
        - tool (str): Canonical tool name used.
        - finding_count (int): Number of findings returned.
        - findings (list[dict]): Structured findings.
        - truncated (bool): True if Community tier cap was applied.
        - max_findings_applied (int | None): Cap applied (None = unlimited).
        - report (dict): Full structured report from the parser.
        - tier_applied (str): Tier used for the request.
        - error (str, optional): Error message on failure.
        - duration_ms (int): Elapsed time in milliseconds.
    """
    import asyncio

    started = time.perf_counter()
    tier = _get_current_tier()

    try:
        result = await asyncio.to_thread(
            _run_static_analysis_sync,
            language,
            paths,
            tool,
            report_path,
            tier,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="run_static_analysis",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
        )
    except _UpgradeRequired as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=None,
            tool_id="run_static_analysis",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=exc.tool_error,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=None,
            tool_id="run_static_analysis",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=ToolError(error=str(exc), error_code="internal_error"),
        )
