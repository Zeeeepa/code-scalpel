# [20260106_TEST] Pro-tier extended detections: NoSQL, LDAP, Secrets
from __future__ import annotations

from pathlib import Path
import textwrap

import pytest
from code_scalpel.licensing.jwt_validator import JWTLicenseValidator

pytestmark = pytest.mark.asyncio


def _use_pro_license(monkeypatch: pytest.MonkeyPatch) -> Path:
    validator = JWTLicenseValidator()
    candidates = [
        Path("tests/licenses/code_scalpel_license_pro_20260101_190345.jwt"),
        Path("tests/licenses/code_scalpel_license_pro_20260101_170435.jwt"),
    ]
    for candidate in candidates:
        if candidate.exists():
            token = candidate.read_text().strip()
            data = validator.validate_token(token)
            if data.is_valid and data.tier == "pro":
                monkeypatch.setenv("CODE_SCALPEL_LICENSE_PATH", str(candidate))
                monkeypatch.delenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", raising=False)
                monkeypatch.delenv("CODE_SCALPEL_TEST_FORCE_TIER", raising=False)
                monkeypatch.delenv("CODE_SCALPEL_TIER", raising=False)
                return candidate
    pytest.skip("Valid Pro license not found; generate a signed test license")


async def test_nosql_injection_detection(monkeypatch: pytest.MonkeyPatch):
    _use_pro_license(monkeypatch)
    code = textwrap.dedent(
        """
        from flask import request
        def find_docs(collection):
            qv = request.args.get('q')
            return collection.find(qv)
        """
    )
    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)
    assert result.success is True
    assert any(v.cwe == "CWE-943" or "nosql" in v.type.lower() for v in result.vulnerabilities)


async def test_ldap_injection_detection(monkeypatch: pytest.MonkeyPatch):
    _use_pro_license(monkeypatch)
    code = (
        "from flask import request\n"
        "import ldap\n"
        "def do_search(conn):\n"
        "    u = request.args.get('u')\n"
        "    filt = '(uid=' + u + ')'\n"
        "    return ldap.search_s('dc=example,dc=com', 2, filt)\n"
    )
    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)
    assert result.success is True
    assert any(v.cwe == "CWE-90" or "ldap" in v.type.lower() for v in result.vulnerabilities)


async def test_secret_detection(monkeypatch: pytest.MonkeyPatch):
    _use_pro_license(monkeypatch)
    code = (
        "def cfg():\n"
        "    api_key = 'apikey' + '012345678901234567890'\n"
        "    password = 'SuperSecret123!'\n"
        "    return api_key, password\n"
    )
    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)
    assert result.success is True
    assert result.vulnerability_count >= 1
    assert any("Secret" in v.type or "secret" in v.description.lower() or v.cwe == "CWE-798" for v in result.vulnerabilities)


# [20260107_TEST] Pro tier remediation_suggestions field tests
async def test_remediation_suggestions_pro_tier(monkeypatch: pytest.MonkeyPatch):
    """Pro tier returns remediation_suggestions field with actionable advice."""
    _use_pro_license(monkeypatch)
    code = textwrap.dedent(
        """
        import subprocess
        def run_cmd(user_input):
            subprocess.run(f"ls {user_input}", shell=True)  # CWE-78
        """
    )
    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)
    assert result.success is True
    assert result.remediation_suggestions is not None
    assert len(result.remediation_suggestions) > 0

    # Verify remediation content is useful
    remediation_text = " ".join(result.remediation_suggestions).lower()
    assert "subprocess" in remediation_text or "shell" in remediation_text or "command" in remediation_text


async def test_remediation_suggestions_community_none(monkeypatch: pytest.MonkeyPatch):
    """Community tier does not return remediation_suggestions."""
    # Force Community tier
    monkeypatch.setenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", "1")
    monkeypatch.delenv("CODE_SCALPEL_LICENSE_PATH", raising=False)

    code = textwrap.dedent(
        """
        import subprocess
        def run_cmd(user_input):
            subprocess.run(f"ls {user_input}", shell=True)
        """
    )
    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)
    assert result.success is True
    # Community tier should NOT have remediation_suggestions
    assert result.remediation_suggestions is None
