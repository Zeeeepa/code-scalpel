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

# Current tier for response envelope metadata.
# Initialized to "community" (free tier) by default.
# Can be overridden via CODE_SCALPEL_TIER environment variable.
CURRENT_TIER = "community"


def _get_current_tier() -> str:
    """Get the current tier from environment or global."""
    import os

    env_tier = os.environ.get("CODE_SCALPEL_TIER") or os.environ.get("SCALPEL_TIER")
    if env_tier:
        tier = env_tier.strip().lower()
        if tier == "free":
            return "community"
        if tier == "all":
            return "enterprise"
        if tier in {"community", "pro", "enterprise"}:
            return tier
    return CURRENT_TIER


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
