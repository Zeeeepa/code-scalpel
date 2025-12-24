"""MCP response contract utilities.

This module implements the V1.0 production contract requirements from
`docs/guides/production_release_v1.0.md`:
- Universal response envelope for all tools
- Stable, machine-parseable error codes

The intent is to enforce the contract at the MCP tool boundary so individual
tool implementations can remain focused on their domain logic.
"""

from __future__ import annotations

import inspect
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Literal

from pydantic import BaseModel, Field


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
    tier: str = Field(description="One of: community, pro, enterprise")
    tool_version: str = Field(description="Semantic version of tool implementation")
    tool_id: str = Field(description="Canonical MCP tool ID")
    request_id: str = Field(description="Correlation ID (caller-provided or server-generated)")
    capabilities: list[str] = Field(description="Capabilities for this invocation")
    duration_ms: int | None = Field(
        default=None, description="End-to-end runtime in milliseconds"
    )
    error: ToolError | None = Field(default=None, description="Standardized error model")
    upgrade_hints: list[UpgradeHint] = Field(
        default_factory=list,
        description="Upgrade hints when a feature is unavailable at this tier",
    )
    data: Any | None = Field(default=None, description="Tool-specific payload")


def _classify_exception(exc: BaseException) -> ErrorCode:
    # Keep classification conservative; do not leak details.
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
