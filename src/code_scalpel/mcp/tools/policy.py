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
async def validate_paths(paths: list[str], project_root: str | None = None) -> ToolResponseEnvelope:
    """Validate that paths are accessible before running file-based operations.

    **Description:**
    Checks that provided file paths exist and are accessible within the project,
    preventing invalid file access errors in subsequent operations.

    **Tier Behavior:**
    - Community: Basic path validation (max 100 paths)
    - Pro: + Alias resolution and dynamic import detection (unlimited paths)
    - Enterprise: + Security validation and boundary testing (unlimited paths)

    **Tier Capabilities:**
    - Community: path_accessibility_checking, docker_environment_detection, workspace_root_detection, actionable_error_messages, docker_volume_mount_suggestions, batch_path_validation, file_existence_validation, import_path_checking, broken_reference_detection, basic_validation (max_paths=100)
    - Pro: Community capabilities + path_alias_resolution, tsconfig_paths_support, webpack_alias_support, dynamic_import_resolution, extended_language_support (max_paths=None)
    - Enterprise: Pro capabilities + permission_checks, security_validation, path_traversal_simulation, symbolic_path_breaking, security_boundary_testing (max_paths=None)

    **Args:**
        paths (list[str]): List of file paths to validate
        project_root (str, optional): Project root directory for relative path resolution

    **Returns:**
        ToolResponseEnvelope:
        - success: True if all paths validated successfully
        - data: PathValidationResult with detailed validation results:
            - success: Whether all paths were accessible
            - accessible: List of successfully resolved paths
            - inaccessible: List of paths that could not be resolved
            - suggestions: Actionable suggestions for resolving inaccessible paths
            - workspace_roots: Detected workspace root directories
            - is_docker: Whether running in Docker container
            - alias_resolutions: Resolved path aliases (Pro+)
            - dynamic_imports: Detected dynamic import patterns (Pro+)
            - traversal_vulnerabilities: Directory traversal attempts (Enterprise)
            - boundary_violations: Workspace boundary violations (Enterprise)
            - security_score: Overall security score 0.0-10.0 (Enterprise)
            - truncated: Whether input was truncated due to limits
            - paths_received: Original number of paths before truncation
            - paths_checked: Number of paths actually validated
            - max_paths_applied: Applied max_paths limit
        - error: Error message if validation failed
    """
    started = time.perf_counter()
    try:
        tier = _get_current_tier()
        capabilities = get_tool_capabilities("validate_paths", tier) or {}
        result = await asyncio.to_thread(_validate_paths_sync, paths, project_root, tier, capabilities)
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
    """
    Verify policy file integrity using cryptographic signatures. Validates that policy files have not been tampered with by checking their cryptographic signatures against a manifest.

    **Tier Behavior:**
    - **Community**: Basic verification only
    - **Pro**: Adds cryptographic signature validation
    - **Enterprise**: Adds full integrity checking and audit logging

    **Tier Capabilities:**
    - **Community:** Basic verification only (capabilities: basic_verification, limits: signature_validation=False, tamper_detection=False)
    - **Pro:** Cryptographic signature validation (capabilities: basic_verification + signature_validation, limits: signature_validation=True, tamper_detection=True)
    - **Enterprise:** Full integrity with audit logging (capabilities: basic_verification + signature_validation + full_integrity_check + audit_logging, limits: signature_validation=True, tamper_detection=True)

    **Args:**
    - policy_dir (str, optional): Directory containing policy files. If None, uses project root.
    - manifest_source (str): Where to load manifest from. Default: 'file'. Options: 'file', 'embedded', 'remote'

    **Returns:**
    - ToolResponseEnvelope: Standardized MCP response envelope containing:
      - data (PolicyVerificationResult): Verification results with:
        - success (bool): Whether all policy files verified successfully
        - manifest_valid (bool): Whether manifest signature is valid
        - files_verified (int): Number of files successfully verified
        - files_failed (list[str]): List of files that failed verification
        - error (str, optional): Error message if verification failed
        - error_code (str, optional): Machine-readable error code
        - manifest_source (str, optional): Source of the policy manifest
        - policy_dir (str, optional): Policy directory that was verified
        - tier (str): Tier used for verification ("community", "pro", "enterprise")
        - signature_validated (bool): Whether HMAC signature was validated
        - tamper_detection_enabled (bool): Whether tamper detection is active
        - audit_log_entry (dict, optional): Enterprise audit log entry
      - tier (str, optional): Applied tier ("community", "pro", "enterprise")
      - error (ToolError, optional): Standardized error if operation failed
      - warnings (list[str]): Non-fatal warnings from MCP boundary
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
    - Community: Basic style checks (PEP8, ESLint rules, basic patterns)
    - Pro: + Best practice analysis, security patterns, async error patterns, custom rules
    - Enterprise: + Compliance standards (HIPAA, SOC2, GDPR, PCI-DSS), auditing, certifications, PDF reports

    **Tier Capabilities:**
    - Community: Style guide checking, PEP8 validation, ESLint rules, basic patterns (max 100 files, 50 rules)
    - Pro: All Community features + extended compliance, best practice analysis, security patterns, async error patterns, custom rules (max 1000 files, 200 rules)
    - Enterprise: All Pro features + HIPAA/SOC2/GDPR/PCI-DSS compliance, compliance auditing, PDF certification, audit trail (unlimited files/rules)

    **Args:**
        paths (list[str]): List of file paths to check against policies
        rules (list[str], optional): Specific rules to enforce. If None, use defaults.
        compliance_standards (list[str], optional): Compliance frameworks (HIPAA, SOC2, GDPR, PCI-DSS).
                                                    Enterprise tier only.
        generate_report (bool): Generate compliance report. Default: False.
                               Enterprise tier only.

    **Returns:**
        ToolResponseEnvelope with policy check results:
        - success: True if check completed successfully
        - data: CodePolicyCheckResult containing:
          - success: True if check passed (no critical violations)
          - files_checked: Number of files analyzed
          - rules_applied: Number of rules applied
          - summary: Human-readable summary of results
          - violations: List of policy violations found (all tiers)
          - best_practices_violations: Best practice violations (Pro/Enterprise)
          - security_warnings: Security warnings detected (Pro/Enterprise)
          - custom_rule_results: Custom rule matches (Pro/Enterprise)
          - compliance_reports: Compliance audit reports by standard (Enterprise)
          - compliance_score: Overall compliance score 0-100 (Enterprise)
          - certifications: Generated certifications (Enterprise)
          - audit_trail: Audit log entries (Enterprise)
          - pdf_report: Base64-encoded PDF report (Enterprise)
          - tier_applied: Tier used for analysis (community/pro/enterprise)
          - files_limit_applied: Max files limit applied (None=unlimited)
          - rules_limit_applied: Max rules limit applied (None=unlimited)
          - error: Error message if check failed
        - error: Error message if analysis failed (invalid paths, permission issues, etc.)
        - tier_applied: Tier used for analysis (community/pro/enterprise)
        - duration_ms: Analysis duration in milliseconds
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
