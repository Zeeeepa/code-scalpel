"""Policy and governance MCP tool registrations."""

from __future__ import annotations

import asyncio

from code_scalpel.licensing.features import get_tool_capabilities
from code_scalpel.mcp.helpers.policy_helpers import (
    _code_policy_check_sync,
    _get_current_tier,
    _validate_paths_sync,
    _verify_policy_integrity_sync,
)
from code_scalpel.mcp.models.policy import (
    CodePolicyCheckResult,
    PathValidationResult,
    PolicyVerificationResult,
)
from code_scalpel.mcp.protocol import mcp


@mcp.tool()
async def validate_paths(
    paths: list[str], project_root: str | None = None
) -> PathValidationResult:
    """Validate that paths are accessible before running file-based operations."""
    tier = _get_current_tier()
    capabilities = get_tool_capabilities("validate_paths", tier) or {}
    return await asyncio.to_thread(
        _validate_paths_sync, paths, project_root, tier, capabilities
    )


@mcp.tool()
async def verify_policy_integrity(
    policy_dir: str | None = None,
    manifest_source: str = "file",
) -> PolicyVerificationResult:
    """Verify policy file integrity using cryptographic signatures."""
    tier = _get_current_tier()
    capabilities = get_tool_capabilities("verify_policy_integrity", tier) or {}
    return await asyncio.to_thread(
        _verify_policy_integrity_sync,
        policy_dir,
        manifest_source,
        tier,
        capabilities,
    )


@mcp.tool()
async def code_policy_check(
    paths: list[str],
    rules: list[str] | None = None,
    compliance_standards: list[str] | None = None,
    generate_report: bool = False,
) -> CodePolicyCheckResult:
    """Check code against style guides, best practices, and compliance standards."""
    tier = _get_current_tier()
    capabilities = get_tool_capabilities("code_policy_check", tier) or {}

    if compliance_standards and tier != "enterprise":
        compliance_standards = None

    if generate_report and tier != "enterprise":
        generate_report = False

    return await asyncio.to_thread(
        _code_policy_check_sync,
        paths,
        rules,
        compliance_standards,
        generate_report,
        tier,
        capabilities,
    )


__all__ = ["validate_paths", "verify_policy_integrity", "code_policy_check"]
