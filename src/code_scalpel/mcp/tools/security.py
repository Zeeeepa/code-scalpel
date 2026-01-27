"""Security MCP tool registrations.

[20260121_REFACTOR] Apply ToolResponseEnvelope to all tool responses to
meet MCP contract requirements (tier, duration, standardized errors).
"""

from __future__ import annotations

import asyncio
import os
import time
from importlib import import_module
from typing import Optional

from mcp.server.fastmcp import Context
from code_scalpel.licensing.features import get_tool_capabilities
from code_scalpel.mcp.helpers.security_helpers import (
    _unified_sink_detect_sync,
    _type_evaporation_scan_sync,
    _scan_dependencies_sync,
    _security_scan_sync,
)
from code_scalpel.mcp.protocol import mcp, _get_current_tier
from code_scalpel.mcp.contract import ToolResponseEnvelope, ToolError, make_envelope
from code_scalpel import __version__ as _pkg_version


@mcp.tool()
async def unified_sink_detect(
    code: str, language: str = "auto", confidence_threshold: float = 0.7
) -> ToolResponseEnvelope:
    """Detect polyglot security sinks with confidence thresholds.

    Identifies dangerous sinks (functions that handle untrusted data) across multiple languages.
    Language is auto-detected from code if set to 'auto' (default).

    **Tier Behavior:**
    - Community: Basic sink detection, CWE mapping, confidence scoring
    - Pro: + Context-aware detection, framework-specific sinks, custom patterns
    - Enterprise: + Compliance reporting, risk scoring, remediation suggestions

    **Tier Capabilities:**
    The following features/limits vary by tier:
    - Community: Pattern-based detection only
    - Pro: + Context analysis and custom patterns
    - Enterprise: + Compliance mappings and remediation suggestions

    **Args:**
        code (str): Source code to scan for sinks.
        language (str): Programming language. Default: 'auto' (auto-detect).
                       Supported: python, javascript, typescript, java
        confidence_threshold (float): Minimum confidence score (0.0-1.0) to report sinks.
                                     Default: 0.7 (70% confidence minimum)

    **Returns:**
        ToolResponseEnvelope:
        - success: True if scan completed
        - data: List of detected sinks with CWE mappings and confidence scores
        - error: Error message if scan failed (unsupported language, invalid code, etc.)

    **Example:**
        ```python
        result = await unified_sink_detect(
            code="exec(user_input)",
            language="python",
            confidence_threshold=0.7
        )
        if result.success:
            print(f"Found {len(result.data['sinks'])} sinks")
        ```
    """
    started = time.perf_counter()
    try:
        # [20260126_FEATURE] Auto-detect language if not specified
        if language == "auto" or language is None:
            # [20251228_BUGFIX] Avoid deprecated shim imports.
            from code_scalpel.surgery.unified_extractor import Language, detect_language

            detected = detect_language(None, code)
            lang_map = {
                Language.PYTHON: "python",
                Language.JAVASCRIPT: "javascript",
                Language.TYPESCRIPT: "typescript",
                Language.JAVA: "java",
            }
            language = lang_map.get(detected, "python")

        tier = _get_current_tier()
        capabilities = get_tool_capabilities("unified_sink_detect", tier)
        result = await asyncio.to_thread(
            _unified_sink_detect_sync,
            code,
            language,
            confidence_threshold,
            tier,
            capabilities,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="unified_sink_detect",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(error=str(exc), error_code="internal_error")
        return make_envelope(
            data=None,
            tool_id="unified_sink_detect",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


@mcp.tool()
async def type_evaporation_scan(
    frontend_code: str | None = None,
    backend_code: str | None = None,
    frontend_file_path: str | None = None,
    backend_file_path: str | None = None,
    frontend_file: str = "frontend.ts",
    backend_file: str = "backend.py",
) -> ToolResponseEnvelope:
    """Detect Type System Evaporation vulnerabilities across frontend/backend.

    Identifies security issues when type information is lost at frontend/backend boundaries.
    Provide either code strings or file paths for both frontend and backend code.

    **Tier Behavior:**
    - Community: Frontend-only analysis, basic type checking
    - Pro: + Network boundary analysis, implicit any tracing, library boundary checks
    - Enterprise: + Runtime validation generation, Zod schema generation, API contract validation

    **Tier Capabilities:**
    The following features/limits vary by tier:
    - Community: Frontend analysis only, single file
    - Pro: + Network boundary analysis, max 10 files
    - Enterprise: + API contracts and validation generation, unlimited files

    **Args:**
        frontend_code (str, optional): Frontend TypeScript/JavaScript code. Either frontend_code or frontend_file_path required.
        backend_code (str, optional): Backend Python code. Either backend_code or backend_file_path required.
        frontend_file_path (str, optional): Path to frontend file. Either frontend_code or frontend_file_path required.
        backend_file_path (str, optional): Path to backend file. Either backend_code or backend_file_path required.
        frontend_file (str): Display name for frontend file. Default: 'frontend.ts'
        backend_file (str): Display name for backend file. Default: 'backend.py'

    **Returns:**
        ToolResponseEnvelope:
        - success: True if analysis completed
        - data: Type evaporation issues with affected boundaries and severity
        - error: Error message if analysis failed (missing files, invalid code, etc.)

    **Example:**
        ```python
        result = await type_evaporation_scan(
            frontend_code="const data = await fetch('/api')",
            backend_code="def api(): return {'any': 'value'}"
        )
        if result.success:
            print(result.data['issues'])
        ```
    """
    started = time.perf_counter()
    try:
        # Validate input: at least one way to provide each code
        if frontend_code is None and frontend_file_path is None:
            raise ValueError(
                "Either 'frontend_code' or 'frontend_file_path' must be provided"
            )
        if backend_code is None and backend_file_path is None:
            raise ValueError(
                "Either 'backend_code' or 'backend_file_path' must be provided"
            )

        # Read from files if codes not provided
        if frontend_code is None and frontend_file_path is not None:
            if not os.path.isfile(frontend_file_path):
                raise ValueError(f"Frontend file not found: {frontend_file_path}")
            with open(frontend_file_path, "r", encoding="utf-8") as f:
                frontend_code = f.read()
            frontend_file = os.path.basename(frontend_file_path)

        if backend_code is None and backend_file_path is not None:
            if not os.path.isfile(backend_file_path):
                raise ValueError(f"Backend file not found: {backend_file_path}")
            with open(backend_file_path, "r", encoding="utf-8") as f:
                backend_code = f.read()
            backend_file = os.path.basename(backend_file_path)

        tier = _get_current_tier()
        caps = get_tool_capabilities("type_evaporation_scan", tier) or {}
        cap_set = set(caps.get("capabilities", []))
        limits = caps.get("limits", {}) or {}
        frontend_only = bool(limits.get("frontend_only", False))
        raw_max_files = limits.get("max_files")
        try:
            max_files = int(raw_max_files) if raw_max_files is not None else None
        except (TypeError, ValueError):
            max_files = None

        enable_pro = bool(
            {
                "implicit_any_tracing",
                "network_boundary_analysis",
                "library_boundary_analysis",
            }
            & cap_set
        )
        enable_enterprise = bool(
            {
                "runtime_validation_generation",
                "zod_schema_generation",
                "api_contract_validation",
            }
            & cap_set
        )

        # At this point, both frontend_code and backend_code are guaranteed to be set
        # (validated above at lines 111-133)
        assert frontend_code is not None, (
            "frontend_code must be provided or read from file"
        )
        assert backend_code is not None, (
            "backend_code must be provided or read from file"
        )

        result = await asyncio.to_thread(
            _type_evaporation_scan_sync,
            frontend_code,
            backend_code,
            frontend_file,
            backend_file,
            enable_pro,
            enable_enterprise,
            frontend_only,
            max_files,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="type_evaporation_scan",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(error=str(exc), error_code="internal_error")
        return make_envelope(
            data=None,
            tool_id="type_evaporation_scan",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


@mcp.tool()
async def scan_dependencies(
    path: str | None = None,
    project_root: str | None = None,
    scan_vulnerabilities: bool = True,
    include_dev: bool = True,
    timeout: float = 30.0,
    ctx: Context | None = None,
) -> ToolResponseEnvelope:
    """Scan project dependencies for known vulnerabilities.

    Analyzes project dependency manifests (package.json, requirements.txt, pom.xml, etc.)
    for known security vulnerabilities using CVE databases.

    **Tier Behavior:**
    - Community: Basic vulnerability scanning, CVE mapping only
    - Pro: + License analysis, supply chain insights, automated updates
    - Enterprise: + Priority scoring, compliance reports, SLA tracking

    **Tier Capabilities:**
    The following features/limits vary by tier:
    - Community: Vulnerabilities only, max 1000 packages
    - Pro: + Licenses and supply chain, max 10000 packages
    - Enterprise: + Compliance and SLA tracking, unlimited packages

    **Args:**
        path (str, optional): Path to scan for dependencies. If None, uses project root.
        project_root (str, optional): Project root directory. If None, uses server default.
        scan_vulnerabilities (bool): Scan for vulnerabilities. Default: True
        include_dev (bool): Include development dependencies. Default: True
        timeout (float): Scan timeout in seconds. Default: 30.0
        ctx (Context, optional): MCP context for progress reporting

    **Returns:**
        ToolResponseEnvelope:
        - success: True if scan completed
        - data: Dependencies with vulnerability info, licenses, version info
        - error: Error message if scan failed (invalid path, scan timeout, etc.)

    **Example:**
        ```python
        result = await scan_dependencies(
            project_root="/home/user/myproject",
            scan_vulnerabilities=True
        )
        if result.success:
            print(f"Found {result.data['total_vulnerabilities']} vulnerabilities")
        ```
    """
    started = time.perf_counter()
    try:
        # Import PROJECT_ROOT from server to avoid circular import issues
        server = import_module("code_scalpel.mcp.server")
        resolved_path = path or project_root or str(server.PROJECT_ROOT)
        tier = _get_current_tier()
        caps = get_tool_capabilities("scan_dependencies", tier)

        if ctx:
            await ctx.report_progress(
                0, 100, f"Scanning dependencies in {resolved_path}..."
            )

        result = await asyncio.to_thread(
            _scan_dependencies_sync,
            project_root=resolved_path,
            scan_vulnerabilities=scan_vulnerabilities,
            include_dev=include_dev,
            timeout=timeout,
            tier=tier,
            capabilities=caps,
            ctx=ctx,
        )

        if ctx:
            vuln_count = result.total_vulnerabilities
            await ctx.report_progress(
                100, 100, f"Scan complete: {vuln_count} vulnerabilities found"
            )

        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="scan_dependencies",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(error=str(exc), error_code="internal_error")
        return make_envelope(
            data=None,
            tool_id="scan_dependencies",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


@mcp.tool()
async def security_scan(
    code: Optional[str] = None,
    file_path: Optional[str] = None,
    confidence_threshold: float = 0.7,
) -> ToolResponseEnvelope:
    """Scan code for security vulnerabilities using taint analysis.

    Identifies security vulnerabilities using taint analysis and pattern matching.
    Provide either 'code' or 'file_path'. Language is auto-detected from code content.

    **Tier Behavior:**
    - Community: Basic pattern matching, CWE mapping, confidence scoring
    - Pro: + Taint analysis, reachability, false positive tuning, custom rules
    - Enterprise: + Compliance mappings, priority ordering, remediation suggestions

    **Tier Capabilities:**
    The following features/limits vary by tier:
    - Community: Pattern matching only
    - Pro: + Taint analysis and custom patterns, max complexity 10000
    - Enterprise: + Compliance and remediation, unlimited complexity

    **Args:**
        code (str, optional): Source code to scan. Either code or file_path required.
        file_path (str, optional): Path to file to scan. Either code or file_path required.
        confidence_threshold (float): Minimum confidence score (0.0-1.0) to report issues.
                                     Default: 0.7 (70% confidence minimum)

    **Returns:**
        ToolResponseEnvelope:
        - success: True if scan completed
        - data: List of security vulnerabilities with CWE, severity, and location info
        - error: Error message if scan failed (file not found, invalid code, etc.)

    **Example:**
        ```python
        result = await security_scan(
            code="password = input('Enter password: ')",
            confidence_threshold=0.7
        )
        if result.success:
            print(f"Found {len(result.data['vulnerabilities'])} issues")
        ```
    """
    started = time.perf_counter()
    try:
        tier = _get_current_tier()
        caps = get_tool_capabilities("security_scan", tier)
        result = await asyncio.to_thread(
            _security_scan_sync, code, file_path, tier, caps, confidence_threshold
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="security_scan",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
        )
    except Exception as exc:
        duration_ms = int((time.perf_counter() - started) * 1000)
        tier = _get_current_tier()
        error_obj = ToolError(error=str(exc), error_code="internal_error")
        return make_envelope(
            data=None,
            tool_id="security_scan",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


__all__ = [
    "security_scan",
    "scan_dependencies",
    "type_evaporation_scan",
    "unified_sink_detect",
]
