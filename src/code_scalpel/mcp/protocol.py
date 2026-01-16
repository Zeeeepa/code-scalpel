"""MCP protocol wiring and shared MCP instance.

[20260116_REFACTOR] Consolidated shared MCP instance with ToolResponseEnvelope wrapper.
All tools, resources, and prompts should import `mcp` from this module.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from code_scalpel import __version__
from code_scalpel.mcp.contract import ToolResponseEnvelope

# [20260116_FEATURE] Import license validator for tier determination
from code_scalpel.licensing.jwt_validator import JWTLicenseValidator

# Current tier for response envelope metadata.
# Initialized to "community" (free tier) by default.
# Can be overridden via CODE_SCALPEL_TIER environment variable.
CURRENT_TIER = "community"

# [20260116_FEATURE] Runtime license grace for long-lived server processes.
# If a license expires mid-session, keep the last known valid tier for 24h.
_LAST_VALID_LICENSE_TIER: str | None = None
_LAST_VALID_LICENSE_AT: float | None = None
_MID_SESSION_EXPIRY_GRACE_SECONDS = 24 * 60 * 60


def _normalize_tier(value: str | None) -> str:
    """Normalize tier string to canonical form."""
    if not value:
        return "community"
    v = value.strip().lower()
    if v == "free":
        return "community"
    if v == "all":
        return "enterprise"
    return v


def _requested_tier_from_env() -> str | None:
    """Get requested tier from environment variables (for testing/downgrade)."""
    import os
    requested = os.environ.get("CODE_SCALPEL_TIER") or os.environ.get("SCALPEL_TIER")
    if requested is None:
        return None
    requested = _normalize_tier(requested)
    if requested not in {"community", "pro", "enterprise"}:
        return None
    return requested


def _get_current_tier() -> str:
    """Get the current tier from license validation with env var override.

    [20260116_FEATURE] Updated to do full license validation, not just env var check.

    The tier system works as follows:
    1. License file determines the MAXIMUM tier you're entitled to
    2. Environment variable can REQUEST a tier (for testing/downgrade)
    3. The effective tier is the MINIMUM of licensed and requested

    Returns:
        str: One of 'community', 'pro', or 'enterprise'
    """
    import os
    import time as time_module

    global _LAST_VALID_LICENSE_AT, _LAST_VALID_LICENSE_TIER

    requested = _requested_tier_from_env()
    disable_license_discovery = (
        os.environ.get("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY") == "1"
    )
    force_tier_override = os.environ.get("CODE_SCALPEL_TEST_FORCE_TIER") == "1"

    # [TESTING/OFFLINE] If license discovery is disabled and explicit test override
    # is set, honor the requested tier (used for tier-gated contract tests only).
    if disable_license_discovery and force_tier_override and requested:
        return requested

    # When discovery is disabled and no explicit license path is provided, clamp to
    # Community to avoid silently elevating tier just via env vars.
    if disable_license_discovery and not force_tier_override:
        if not os.environ.get("CODE_SCALPEL_LICENSE_PATH"):
            return "community"

    validator = JWTLicenseValidator()
    license_data = validator.validate()
    licensed = "community"

    if license_data.is_valid:
        licensed = _normalize_tier(license_data.tier)
        _LAST_VALID_LICENSE_TIER = licensed
        _LAST_VALID_LICENSE_AT = time_module.time()
    else:
        # Revocation is immediate: no grace.
        err = (license_data.error_message or "").lower()
        if "revoked" in err:
            licensed = "community"
        # Expiration mid-session: allow 24h grace based on last known valid tier.
        elif getattr(license_data, "is_expired", False) and _LAST_VALID_LICENSE_AT:
            now = time_module.time()
            if now - _LAST_VALID_LICENSE_AT <= _MID_SESSION_EXPIRY_GRACE_SECONDS:
                if _LAST_VALID_LICENSE_TIER in {"pro", "enterprise"}:
                    licensed = _LAST_VALID_LICENSE_TIER

    # If no tier requested via env var, use the licensed tier
    if requested is None:
        return licensed

    # Allow downgrade only: effective tier = min(requested, licensed)
    rank = {"community": 0, "pro": 1, "enterprise": 2}
    return requested if rank[requested] <= rank[licensed] else licensed


def set_current_tier(tier: str) -> None:
    """Set the current tier (called by run_server)."""
    global CURRENT_TIER
    CURRENT_TIER = tier


mcp = FastMCP(
    name="Code Scalpel",
    instructions=f"""Code Scalpel v{__version__} - AI-powered code analysis tools:

**TOKEN-EFFICIENT EXTRACTION (READ):**
- extract_code: Surgically extract functions/classes/methods by FILE PATH.
  The SERVER reads the file - YOU pay ~50 tokens instead of ~10,000.
  Supports Python, JavaScript, TypeScript, Java, JSX, TSX (React components).
  Example: extract_code(file_path="/src/utils.py", target_type="function", target_name="calculate_tax")
  React: extract_code(file_path="/components/Button.tsx", target_type="function", target_name="Button", language="tsx")

**JSX/TSX EXTRACTION (v2.0.2):**
- Extract React components with full metadata
- Detects Server Components (Next.js async components)
- Detects Server Actions ('use server' directive)
- Normalizes JSX for consistent analysis
- Returns component_type: "functional" or "class"

**RESOURCE TEMPLATES (v2.0.2):**
Access code via URIs without knowing file paths:
- code:///python/utils/calculate_tax
- code:///typescript/components/UserCard
- code:///java/services.AuthService/authenticate

**SURGICAL MODIFICATION (WRITE):**
- update_symbol: Replace a function/class/method in a file with new code.
  YOU provide only the new symbol - the SERVER handles safe replacement.
  Example: update_symbol(file_path="/src/utils.py", target_type="function",
           target_name="calculate_tax", new_code="def calculate_tax(amount): ...")
  Creates backup, validates syntax, preserves surrounding code.

**ANALYSIS TOOLS:**
- analyze_code: Parse Python/Java code, extract structure (functions, classes, imports)
- security_scan: Detect vulnerabilities using taint analysis (SQL injection, XSS, etc.)
- symbolic_execute: Explore execution paths using symbolic execution
- generate_unit_tests: Generate pytest/unittest tests from symbolic execution paths
- simulate_refactor: Verify a code change is safe before applying it
- crawl_project: Crawl entire project directory, analyze all Python files

**WORKFLOW OPTIMIZATION:**
1. Use extract_code(file_path=...) to get ONLY the symbol you need
2. Modify the extracted code
3. Use update_symbol(file_path=..., new_code=...) to apply the change safely

Code is PARSED only, never executed.""",
)


# ============================================================================
# TOOL RESPONSE ENVELOPE WRAPPER
# [20260116_REFACTOR] Moved from server.py to apply to all tool registrations
# ============================================================================

_original_add_tool = mcp._tool_manager.add_tool


def _add_tool_with_envelope_output(
    fn: Callable[..., Any], **add_tool_kwargs: Any
) -> Any:
    """Register a tool normally, then wrap its run() method to return ToolResponseEnvelope."""
    # Force structured_output=False so FastMCP doesn't validate output against schema
    # We'll return ToolResponseEnvelope as unstructured JSON
    add_tool_kwargs["structured_output"] = False

    # Register the tool - let FastMCP build input schema from the original function
    tool = _original_add_tool(fn, **add_tool_kwargs)

    # Save the original run method
    original_run = tool.run

    async def _enveloped_run(
        arguments: dict[str, Any], context: Any = None, convert_result: bool = False
    ) -> dict[str, Any]:
        """Wrapped run() that returns ToolResponseEnvelope as a dict."""
        import time as time_module
        import uuid as uuid_module

        started = time_module.perf_counter()
        request_id = uuid_module.uuid4().hex
        tier = _get_current_tier()

        try:
            # Call the original run method with convert_result=False to get raw tool output
            # We'll wrap it in an envelope, so FastMCP's conversion happens at envelope level
            result = await original_run(
                arguments, context=context, convert_result=False
            )

            duration_ms = int((time_module.perf_counter() - started) * 1000)

            # Check for failure indicators in the result
            success = None
            err_msg = None
            if isinstance(result, BaseModel):
                success = getattr(result, "success", None)
                err_msg = getattr(result, "error", None)
            elif isinstance(result, dict):
                success = result.get("success")
                err_msg = result.get("error")

            error_obj = None
            if success is False and err_msg:
                from code_scalpel.mcp.contract import (
                    ToolError,
                    _classify_failure_message,
                )

                code = _classify_failure_message(err_msg) or "internal_error"
                error_obj = ToolError(error=err_msg, error_code=code)

            return ToolResponseEnvelope(
                tier=tier,
                tool_version=__version__,
                tool_id=tool.name,
                request_id=request_id,
                capabilities=["envelope-v1"],
                duration_ms=duration_ms,
                error=error_obj,
                upgrade_hints=[],
                data=result,
            ).model_dump(mode="json")

        except BaseException as exc:
            duration_ms = int((time_module.perf_counter() - started) * 1000)
            from code_scalpel.mcp.contract import ToolError, _classify_exception

            code = _classify_exception(exc)
            return ToolResponseEnvelope(
                tier=tier,
                tool_version=__version__,
                tool_id=tool.name,
                request_id=request_id,
                capabilities=["envelope-v1"],
                duration_ms=duration_ms,
                error=ToolError(error=str(exc) or "Tool error", error_code=code),
                upgrade_hints=[],
                data=None,
            ).model_dump(mode="json")

    # Replace the tool's run method (Tool is a Pydantic model, use object.__setattr__)
    object.__setattr__(tool, "run", _enveloped_run)

    return tool


mcp._tool_manager.add_tool = _add_tool_with_envelope_output  # type: ignore[method-assign]


__all__ = ["mcp", "set_current_tier", "_get_current_tier"]
