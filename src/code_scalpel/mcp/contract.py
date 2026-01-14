"""MCP response contract utilities.

This module implements the V1.0 production contract requirements from
`docs/guides/production_release_v1.0.md`:
- Universal response envelope for all tools
- Stable, machine-parseable error codes

The intent is to enforce the contract at the MCP tool boundary so individual
tool implementations can remain focused on their domain logic.

TODO ITEMS:

COMMUNITY TIER (Basic Contract Enforcement):
1. TODO: Implement ToolResponseEnvelope with all required fields
2. TODO: Define error codes enum (invalid_argument, not_found, etc.)
3. TODO: Create error contract with machine-parseable codes
4. TODO: Implement envelope wrapping for all tool responses
5. TODO: Add tier metadata to responses
6. TODO: Validate response schema on serialization
7. TODO: Implement request correlation IDs
8. TODO: Add tool version tracking in envelope
9. TODO: Create contract validation tests
10. TODO: Document contract specification

PRO TIER (Advanced Contract Features):
11. TODO: Implement conditional response fields based on tier
12. TODO: Add upgrade hint generation for tier-restricted features
13. TODO: Implement response streaming with envelope markers
14. TODO: Add structured error details (non-sensitive)
15. TODO: Support custom error codes per tool
16. TODO: Implement contract versioning and migration
17. TODO: Add response compression hints
18. TODO: Create envelope validation middleware
19. TODO: Implement response filtering based on capabilities
20. TODO: Add trace context propagation

ENTERPRISE TIER (Contract Extension & Compliance):
21. TODO: Implement multi-version contract support
22. TODO: Add compliance metadata (GDPR, HIPAA, SOC2)
23. TODO: Implement digital signatures for responses
24. TODO: Add encryption support for sensitive data
25. TODO: Implement audit trail in contract
26. TODO: Support blockchain-based response hashing
27. TODO: Add federated contract validation
28. TODO: Implement zero-knowledge proofs for contract compliance
29. TODO: Add quantum-safe signature schemes
30. TODO: Create AI-powered contract optimization
"""

from __future__ import annotations

import inspect
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Literal

from pydantic import BaseModel, Field


class UpgradeRequiredError(RuntimeError):
    """Raised when a caller requests a capability unavailable at current tier.

    [20251228_FEATURE] Enables structured upgrade-required errors.
    [20260112_REFACTOR] Removed upgrade_url from message - hints belong in docs only.
    """

    def __init__(
        self,
        *,
        tool_id: str,
        feature: str,
        required_tier: str,
        upgrade_url: str | None = None,  # Deprecated, kept for backwards compat
        message: str | None = None,
    ) -> None:
        if message is None:
            message = f"Feature '{feature}' requires {required_tier.upper()} tier."
        super().__init__(message)
        self.tool_id = tool_id
        self.feature = feature
        self.required_tier = required_tier
        self.upgrade_url = upgrade_url  # Deprecated - do not use in new code


ErrorCode = Literal[
    "invalid_argument",
    "invalid_path",
    "forbidden",
    "not_found",
    "timeout",
    "too_large",
    "resource_exhausted",
    "not_implemented",
    "upgrade_required",
    "dependency_unavailable",
    "internal_error",
]


class UpgradeHint(BaseModel):
    feature: str = Field(description="What is unlocked")
    tier: str = Field(description="Tier that unlocks it")
    reason: str = Field(description="Why it is unavailable at current tier")


class ToolError(BaseModel):
    error: str = Field(description="Human-readable error message")
    error_code: ErrorCode = Field(description="Machine-parseable error code")
    error_details: dict[str, Any] | None = Field(
        default=None,
        description="Optional structured details safe for clients; never include code contents",
    )


class ToolResponseEnvelope(BaseModel):
    tier: str | None = Field(
        default=None,
        description="One of: community, pro, enterprise (omitted by default for token efficiency)",
    )
    tool_version: str | None = Field(
        default=None,
        description="Semantic version of tool implementation (omitted by default)",
    )
    tool_id: str | None = Field(
        default=None,
        description="Canonical MCP tool ID (omitted by default - client knows which tool was called)",
    )
    request_id: str | None = Field(
        default=None,
        description="Correlation ID (omitted by default unless client-provided)",
    )
    capabilities: list[str] | None = Field(
        default=None,
        description="Capabilities for this invocation (omitted by default)",
    )
    duration_ms: int | None = Field(
        default=None,
        description="End-to-end runtime in milliseconds (omitted by default)",
    )
    error: ToolError | None = Field(
        default=None,
        description="Standardized error model (only included when error occurs)",
    )
    upgrade_hints: list[UpgradeHint] | None = Field(
        default=None,
        description="Upgrade hints when a feature is unavailable at this tier (only included when hints exist)",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings emitted by the MCP boundary (e.g., governance WARN mode)",
    )
    data: Any | None = Field(default=None, description="Tool-specific payload")


def _classify_exception(exc: BaseException) -> ErrorCode:
    # Keep classification conservative; do not leak details.
    if isinstance(exc, UpgradeRequiredError):
        return "upgrade_required"
    if isinstance(exc, (ValueError, TypeError)):
        return "invalid_argument"
    if isinstance(exc, FileNotFoundError):
        return "not_found"
    if isinstance(exc, PermissionError):
        return "forbidden"
    if isinstance(exc, (TimeoutError,)):
        return "timeout"
    # asyncio.TimeoutError is a subclass of TimeoutError in modern Python, but keep safe.
    if exc.__class__.__name__ in {"TimeoutError", "CancelledError"}:
        return "timeout"
    if isinstance(exc, NotImplementedError):
        return "not_implemented"
    if isinstance(exc, MemoryError):
        return "resource_exhausted"
    return "internal_error"


def _maybe_get_success_and_error(payload: Any) -> tuple[bool | None, str | None]:
    """Best-effort introspection of existing tool payloads.

    Many tools in this repo return Pydantic models that include `success` and `error`.
    Some tools return dicts without `success`.
    """

    try:
        if isinstance(payload, BaseModel):
            success = getattr(payload, "success", None)
            err = getattr(payload, "error", None)
            return (bool(success) if success is not None else None, err)
        if isinstance(payload, dict):
            success = payload.get("success")
            err = payload.get("error")
            return (bool(success) if success is not None else None, err)
    except Exception:
        return None, None
    return None, None


def _classify_failure_message(message: str | None) -> ErrorCode | None:
    if not message:
        return None
    lowered = message.lower()
    if "file not found" in lowered or "no such file" in lowered:
        return "not_found"
    if "not a file" in lowered or "must be" in lowered or "cannot be empty" in lowered:
        return "invalid_argument"
    if "invalid path" in lowered or "path traversal" in lowered:
        return "invalid_path"
    if "permission" in lowered or "forbidden" in lowered:
        return "forbidden"
    if "timeout" in lowered:
        return "timeout"
    if "requires pro tier" in lowered or "requires enterprise tier" in lowered:
        return "upgrade_required"
    if "upgrade:" in lowered or "upgrade at" in lowered:
        return "upgrade_required"
    if "too large" in lowered or "exceeds maximum" in lowered:
        return "too_large"
    if "not implemented" in lowered:
        return "not_implemented"
    return None


def envelop_tool_function(
    fn: Callable[..., Any] | Callable[..., Awaitable[Any]],
    *,
    tool_id: str,
    tool_version: str,
    tier_getter: Callable[[], str],
) -> Callable[..., Awaitable[ToolResponseEnvelope]]:
    """Wrap an MCP tool function to always return a ToolResponseEnvelope.

    Preserves the original function signature (via __signature__) so FastMCP can
    generate the same JSON schema for inputs.
    """

    sig = inspect.signature(fn)

    async def _wrapped(*args: Any, **kwargs: Any) -> ToolResponseEnvelope:
        started = time.perf_counter()
        request_id = uuid.uuid4().hex
        tier = (tier_getter() or "enterprise").strip().lower()

        # If the tool received a Context, try to use its request id if available.
        ctx = kwargs.get("ctx")
        for candidate in ("request_id", "requestId", "correlation_id", "correlationId"):
            if ctx is not None and hasattr(ctx, candidate):
                try:
                    val = getattr(ctx, candidate)
                    if isinstance(val, str) and val.strip():
                        request_id = val.strip()
                        break
                except Exception:
                    pass

        try:
            result = fn(*args, **kwargs)
            if inspect.isawaitable(result):
                result = await result

            duration_ms = int((time.perf_counter() - started) * 1000)
            success, err_msg = _maybe_get_success_and_error(result)

            error_obj: ToolError | None = None
            if success is False:
                code = _classify_failure_message(err_msg) or "internal_error"
                error_obj = ToolError(error=err_msg or "Tool failed", error_code=code)

            return ToolResponseEnvelope(
                tier=tier,
                tool_version=tool_version,
                tool_id=tool_id,
                request_id=request_id,
                capabilities=["envelope-v1"],
                duration_ms=duration_ms,
                error=error_obj,
                upgrade_hints=[],
                data=result,
            )
        except BaseException as exc:  # noqa: BLE001
            duration_ms = int((time.perf_counter() - started) * 1000)
            code = _classify_exception(exc)
            return ToolResponseEnvelope(
                tier=tier,
                tool_version=tool_version,
                tool_id=tool_id,
                request_id=request_id,
                capabilities=["envelope-v1"],
                duration_ms=duration_ms,
                error=ToolError(error=str(exc) or "Tool error", error_code=code),
                upgrade_hints=[],
                data=None,
            )

    _wrapped.__signature__ = sig  # type: ignore[attr-defined]
    _wrapped.__name__ = getattr(fn, "__name__", tool_id)
    _wrapped.__qualname__ = getattr(fn, "__qualname__", tool_id)
    _wrapped.__doc__ = getattr(fn, "__doc__", None)
    _wrapped.__module__ = getattr(fn, "__module__", __name__)
    _wrapped.__annotations__ = getattr(fn, "__annotations__", {})

    # Copy __globals__ so Pydantic can resolve type annotations
    if hasattr(fn, "__globals__"):
        _wrapped.__globals__.update(fn.__globals__)  # type: ignore[attr-defined]

    return _wrapped
