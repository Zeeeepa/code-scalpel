"""Policy and governance MCP tool registrations.

[20260121_REFACTOR] Wrap tool responses with ToolResponseEnvelope to satisfy
MCP contract tests (tier metadata included).
"""

from __future__ import annotations

import asyncio
import time

from code_scalpel.licensing.features import get_tool_capabilities
from code_scalpel.mcp.helpers.policy_helpers import (
    _code_policy_check_sync,
    _get_current_tier,
    _validate_paths_sync,
    _verify_policy_integrity_sync,
)
from code_scalpel.mcp.protocol import mcp
from code_scalpel.mcp.contract import ToolResponseEnvelope, ToolError, make_envelope
from code_scalpel import __version__ as _pkg_version


@mcp.tool()
async def validate_paths(
    paths: list[str], project_root: str | None = None
) -> ToolResponseEnvelope:
    """Validate that paths are accessible before running file-based operations.

    Checks that provided file paths exist and are accessible within the project,
    preventing invalid file access errors in subsequent operations.

    **Tier Behavior:**
    - Community: Basic path validation (max 100 paths)
    - Pro: + Symlink detection and depth checking (max 1000 paths)
    - Enterprise: + Permission analysis and policy compliance (unlimited paths)

    **Tier Capabilities:**
    The following features/limits vary by tier:
    - Community: Basic existence check, max 100 paths
    - Pro: + Symlink detection, max 1000 paths
    - Enterprise: + Permission checks, unlimited paths

    **Args:**
        paths (list[str]): List of file paths to validate
        project_root (str, optional): Project root directory for relative path resolution

    **Returns:**
        ToolResponseEnvelope:
        - success: True if all paths validated
        - data: Validation results for each path (exists, accessible, permissions)
        - error: Error message if validation failed (invalid path list, etc.)

    **Example:**
        ```python
        result = await validate_paths(
            paths=["/src/main.py", "/tests/test.py"],
            project_root="/home/user/project"
        )
        if result.success:
            print(result.data['valid_paths'])
        ```
    """
    started = time.perf_counter()
    try:
        tier = _get_current_tier()
        capabilities = get_tool_capabilities("validate_paths", tier) or {}
        result = await asyncio.to_thread(
            _validate_paths_sync, paths, project_root, tier, capabilities
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="validate_paths",
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
            tool_id="validate_paths",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


@mcp.tool()
async def verify_policy_integrity(
    policy_dir: str | None = None,
    manifest_source: str = "file",
) -> ToolResponseEnvelope:
    """Verify policy file integrity using cryptographic signatures.

    Validates that policy files have not been tampered with by checking their
    cryptographic signatures against a manifest. Supports policy versioning and
    chain-of-custody tracking.

    **Tier Behavior:**
    - Community: Basic signature verification only
    - Pro: + Manifest validation and version tracking
    - Enterprise: + Chain-of-custody, policy evolution, audit logging

    **Tier Capabilities:**
    The following features/limits vary by tier:
    - Community: Signature verification only
    - Pro: + Manifest validation and versioning
    - Enterprise: + Audit trails and evolution tracking

    **Args:**
        policy_dir (str, optional): Directory containing policy files. If None, uses project root.
        manifest_source (str): Where to load manifest from. Default: 'file'
                              Options: 'file', 'embedded', 'remote'

    **Returns:**
        ToolResponseEnvelope:
        - success: True if all policy files verified
        - data: Verification results for each policy file (valid, signature, version)
        - error: Error message if verification failed (corrupt policy, bad signature, etc.)

    **Example:**
        ```python
        result = await verify_policy_integrity(
            policy_dir="/home/user/project/.policies",
            manifest_source="file"
        )
        if result.success:
            print(result.data['verified_files'])
        ```
    """
    started = time.perf_counter()
    try:
        tier = _get_current_tier()
        capabilities = get_tool_capabilities("verify_policy_integrity", tier) or {}
        result = await asyncio.to_thread(
            _verify_policy_integrity_sync,
            policy_dir,
            manifest_source,
            tier,
            capabilities,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="verify_policy_integrity",
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
            tool_id="verify_policy_integrity",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


@mcp.tool()
async def code_policy_check(
    paths: list[str],
    rules: list[str] | None = None,
    compliance_standards: list[str] | None = None,
    generate_report: bool = False,
) -> ToolResponseEnvelope:
    """Check code against style guides, best practices, and compliance standards.

    Analyzes source code files for adherence to coding standards, style guides,
    and best practices. Can optionally enforce organizational compliance standards.

    **Tier Behavior:**
    - Community: Basic style checks (PEP8, ESLint rules)
    - Pro: + Best practice patterns, complexity metrics, code smell detection
    - Enterprise: + Compliance standards (GDPR, SOC2), custom org policies, reports

    **Tier Capabilities:**
    The following features/limits vary by tier:
    - Community: Style rules only, max 100 files
    - Pro: + Best practices and metrics, max 1000 files
    - Enterprise: + Compliance checks and reporting, unlimited files

    **Args:**
        paths (list[str]): List of file paths to check against policies
        rules (list[str], optional): Specific rules to enforce. If None, use defaults.
        compliance_standards (list[str], optional): Compliance frameworks (GDPR, SOC2).
                                                    Enterprise tier only.
        generate_report (bool): Generate compliance report. Default: False.
                               Enterprise tier only.

    **Returns:**
        ToolResponseEnvelope:
        - success: True if check completed
        - data: Policy violations found with severity, location, and fix suggestions
        - error: Error message if check failed (invalid paths, bad rules, etc.)

    **Example:**
        ```python
        result = await code_policy_check(
            paths=["/src/main.py"],
            rules=["no-hardcoded-secrets", "max-complexity:10"]
        )
        if result.success:
            print(f"Found {result.data['violation_count']} policy violations")
        ```
    """
    started = time.perf_counter()
    try:
        tier = _get_current_tier()
        capabilities = get_tool_capabilities("code_policy_check", tier) or {}

        if compliance_standards and tier != "enterprise":
            compliance_standards = None

        if generate_report and tier != "enterprise":
            generate_report = False

        result = await asyncio.to_thread(
            _code_policy_check_sync,
            paths,
            rules,
            compliance_standards,
            generate_report,
            tier,
            capabilities,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        return make_envelope(
            data=result,
            tool_id="code_policy_check",
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
            tool_id="code_policy_check",
            tool_version=_pkg_version,
            tier=tier,
            duration_ms=duration_ms,
            error=error_obj,
        )


__all__ = ["validate_paths", "verify_policy_integrity", "code_policy_check"]
