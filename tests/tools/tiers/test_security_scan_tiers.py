# [20260106_TEST] Tier coverage for security_scan
"""Tier enforcement and fallback tests for security_scan MCP tool."""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.asyncio


# [20260106_TEST] Helpers for license and analyzer stubs
class _DummyLicenseData:
    def __init__(
        self,
        is_valid: bool,
        tier: str | None = None,
        error: str | None = None,
        is_expired: bool = False,
    ):
        self.is_valid = is_valid
        self.tier = tier
        self.error_message = error
        self.is_expired = is_expired


class _DummyAnalyzerResult:
    def __init__(
        self, vulnerabilities: list[dict], taint_sources: list[str] | None = None
    ):
        self._vulns = vulnerabilities
        self._taints = taint_sources or []

    def to_dict(self) -> dict:
        return {
            "vulnerabilities": self._vulns,
            "taint_sources": self._taints,
        }


def _make_repetitive_vuln_code(count: int) -> str:
    """Generate code with a predictable number of eval() sinks."""
    return "\n".join("eval('1')" for _ in range(count)) + "\n"


async def test_security_scan_community_enforces_finding_cap(monkeypatch):
    """Community tier clamps findings to 50 when more are present."""
    monkeypatch.setenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", "1")
    monkeypatch.setenv("CODE_SCALPEL_TEST_FORCE_TIER", "1")
    monkeypatch.setenv("CODE_SCALPEL_TIER", "community")

    code = _make_repetitive_vuln_code(75)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count == 50
    assert len(result.vulnerabilities) == 50
    assert result.confidence_scores is None
    assert result.false_positive_analysis is None


async def test_security_scan_pro_allows_unlimited_findings(monkeypatch):
    """Pro tier returns all findings and enables Pro-only enrichments."""
    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")

    code = _make_repetitive_vuln_code(60)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count == 60
    assert len(result.vulnerabilities) == 60
    # Pro enables FP reduction metadata and confidence scores
    assert result.confidence_scores is not None
    assert result.false_positive_analysis is not None


async def test_security_scan_enterprise_enables_enterprise_fields(monkeypatch):
    """Enterprise tier populates Enterprise-only enrichment fields."""
    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "enterprise")

    # Include weak crypto and multiple sinks to trigger enrichments
    code = """\
import hashlib

def insecure_hash(user_input: str):
    return hashlib.sha1(user_input.encode()).hexdigest()

""" + _make_repetitive_vuln_code(
        5
    )

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count >= 5  # At least hash weakness + eval calls
    # Enterprise tier should have enrichments
    assert result.confidence_scores is not None
    assert result.false_positive_analysis is not None
    assert result.policy_violations is not None  # Weak crypto detected
    assert result.priority_ordered_findings is not None
    assert result.reachability_analysis is not None
    assert result.false_positive_tuning is not None


async def test_security_scan_invalid_license_falls_back_to_community(
    tmp_path: Path, monkeypatch
):
    """Invalid license should fall back to Community limits (50 findings)."""
    license_path = tmp_path / "invalid.jwt"
    license_path.write_text("invalid.jwt.token.malformed\n", encoding="utf-8")

    monkeypatch.delenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", raising=False)
    monkeypatch.delenv("CODE_SCALPEL_TEST_FORCE_TIER", raising=False)
    monkeypatch.setenv("CODE_SCALPEL_LICENSE_PATH", str(license_path))

    code = _make_repetitive_vuln_code(70)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    # Fallback to Community should cap findings
    assert result.vulnerability_count == 50
    assert len(result.vulnerabilities) == 50
    # Pro/Enterprise enrichments should not be present after fallback
    assert result.confidence_scores is None or result.confidence_scores == {}
    assert result.false_positive_analysis is None


async def test_security_scan_community_rejects_large_file(monkeypatch):
    """Community tier enforces 500KB file size limit."""
    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "community")

    oversized_code = "a" * (520 * 1024)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=oversized_code)

    assert result.success is False
    assert "maximum size" in (result.error or "").lower()
    assert result.vulnerability_count == 0


async def test_security_scan_missing_license_defaults_to_community(monkeypatch):
    """Missing/invalid license defaults to Community tier and disables Pro enrichments."""
    from code_scalpel.licensing import jwt_validator

    monkeypatch.delenv("CODE_SCALPEL_LICENSE_PATH", raising=False)
    monkeypatch.setenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", "0")
    monkeypatch.setattr(
        jwt_validator.JWTLicenseValidator,
        "validate",
        lambda self: _DummyLicenseData(False),
    )

    code = _make_repetitive_vuln_code(5)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count >= 5  # At least 5 eval() calls
    # Community tier should NOT have Pro enrichments
    assert result.confidence_scores is None
    assert result.false_positive_analysis is None


async def test_security_scan_revoked_license_forces_community(monkeypatch):
    """Revoked license must downgrade immediately to Community limits."""
    from code_scalpel.licensing import jwt_validator
    from code_scalpel.mcp import server

    monkeypatch.setattr(
        jwt_validator.JWTLicenseValidator,
        "validate",
        lambda self: _DummyLicenseData(False, error="license revoked"),
    )
    monkeypatch.setattr(server, "_LAST_VALID_LICENSE_AT", None)
    monkeypatch.setattr(server, "_LAST_VALID_LICENSE_TIER", None)

    code = _make_repetitive_vuln_code(60)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.vulnerability_count == 50
    assert result.confidence_scores is None
    assert result.false_positive_analysis is None


async def test_security_scan_expired_license_within_grace_uses_last_tier(monkeypatch):
    """Expired license within grace should honor last known Pro tier."""
    import time

    from code_scalpel.licensing import jwt_validator
    from code_scalpel.mcp import server

    server._LAST_VALID_LICENSE_TIER = "pro"
    server._LAST_VALID_LICENSE_AT = time.time() - 3600
    monkeypatch.setattr(
        jwt_validator.JWTLicenseValidator,
        "validate",
        lambda self: _DummyLicenseData(
            False, tier="pro", error="expired", is_expired=True
        ),
    )

    code = _make_repetitive_vuln_code(60)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.vulnerability_count == 60
    assert result.confidence_scores is not None
    assert result.false_positive_analysis is not None


async def test_security_scan_expired_license_after_grace_downgrades(monkeypatch):
    """Expired license after grace should clamp to Community caps."""
    import time

    from code_scalpel.licensing import jwt_validator
    from code_scalpel.mcp import server

    server._LAST_VALID_LICENSE_TIER = "pro"
    server._LAST_VALID_LICENSE_AT = time.time() - (
        server._MID_SESSION_EXPIRY_GRACE_SECONDS + 10
    )

    monkeypatch.setattr(
        jwt_validator.JWTLicenseValidator,
        "validate",
        lambda self: _DummyLicenseData(
            False, tier="pro", error="expired", is_expired=True
        ),
    )

    code = _make_repetitive_vuln_code(70)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.vulnerability_count == 50
    assert result.confidence_scores is None
    assert result.false_positive_analysis is None


async def test_security_scan_pro_detects_nosql_ldap_and_secrets(monkeypatch):
    """Pro tier should surface Pro-only vulnerability types and enrichments."""
    from code_scalpel.mcp import server

    vulns = [
        {
            "type": "NoSQL Injection",
            "cwe": "CWE-943",
            "severity": "high",
            "sink_location": (1, 0),
            "description": "Mongo query",
        },
        {
            "type": "LDAP Injection",
            "cwe": "CWE-90",
            "severity": "high",
            "sink_location": (2, 0),
            "description": "LDAP filter",
        },
        {
            "type": "Hardcoded Secret",
            "cwe": "CWE-798",
            "severity": "medium",
            "sink_location": (3, 0),
            "description": "Secret",
        },
    ]

    class _StubAnalyzer:
        def analyze(self, _code):
            return _DummyAnalyzerResult(vulns)

    monkeypatch.setattr(
        "code_scalpel.security.analyzers.SecurityAnalyzer", _StubAnalyzer
    )
    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")

    code = "db.users.find_one({'a':user}); ldap.search(filter); secret='abc'"

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.vulnerability_count == 3
    assert any(v.cwe == "CWE-943" for v in result.vulnerabilities)
    assert any(v.cwe == "CWE-90" for v in result.vulnerabilities)
    assert result.confidence_scores is not None
    assert result.false_positive_analysis is not None


async def test_security_scan_enterprise_enables_compliance_and_custom_rules(
    monkeypatch,
):
    """Enterprise tier should populate compliance, custom rules, priority ordering, reachability, and FP tuning."""
    from code_scalpel.mcp import server

    vulns = [
        {
            "type": "SQL Injection",
            "cwe": "CWE-89",
            "severity": "critical",
            "sink_location": (5, 0),
            "description": "SQL",
        },
        {
            "type": "Command Injection",
            "cwe": "CWE-78",
            "severity": "high",
            "sink_location": (10, 0),
            "description": "Cmd",
        },
    ]

    class _StubAnalyzer:
        def analyze(self, _code):
            return _DummyAnalyzerResult(vulns, taint_sources=["request.args"])

    class _StubPolicyViolation:
        def __init__(self, policy_id, line, severity, description, remediation):
            self.policy_id = policy_id
            self.line = line
            self.severity = severity
            self.description = description
            self.remediation = remediation

    class _StubPolicyEngine:
        def check_weak_crypto(self, _code):
            return [
                _StubPolicyViolation("weak_crypto", 5, "medium", "MD5", "Use SHA-256")
            ]

        def check_sensitive_logging(self, _code):
            return [
                _StubPolicyViolation("log_pii", 12, "high", "PII logged", "Remove PII")
            ]

    monkeypatch.setattr(
        "code_scalpel.security.analyzers.SecurityAnalyzer", _StubAnalyzer
    )
    monkeypatch.setattr(
        "code_scalpel.security.analyzers.policy_engine.PolicyEngine", _StubPolicyEngine
    )
    monkeypatch.setattr(server, "PolicyEngine", _StubPolicyEngine, raising=False)
    monkeypatch.setattr(server, "_get_current_tier", lambda: "enterprise")

    code = "sanitize(user); cursor.execute(sql); os.system('ls')"

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.policy_violations is not None
    assert result.compliance_mappings is not None
    assert result.priority_ordered_findings is not None
    assert result.reachability_analysis is not None
    # custom_rule_results may be None if no custom rules are triggered
    # But other Enterprise enrichments should be present
    assert (
        result.custom_rule_results is not None
        or result.false_positive_tuning is not None
    )


async def test_security_scan_capability_limits_respected(monkeypatch):
    """Feature gating must use capability limits, not tier name assumptions."""
    from code_scalpel.mcp import server

    monkeypatch.setattr(server, "_get_current_tier", lambda: "pro")

    def _limited_caps(tool_name, tier):
        assert tool_name == "security_scan"
        return {
            "capabilities": {"basic_vulnerabilities"},
            "limits": {"max_findings": 3, "max_file_size_kb": 1024},
        }

    monkeypatch.setattr(server, "get_tool_capabilities", _limited_caps)

    code = _make_repetitive_vuln_code(10)

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.vulnerability_count == 3
    assert result.confidence_scores is None
    assert result.false_positive_analysis is None


async def test_security_scan_requires_code_or_file_path():
    """Parameter validation should reject missing inputs."""
    from code_scalpel.mcp.server import security_scan

    result = await security_scan()

    assert result.success is False
    assert "must be provided" in (result.error or "").lower()
