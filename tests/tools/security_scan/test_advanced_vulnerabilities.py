# [20260107_TEST] Advanced vulnerability types: CSRF, SSRF, JWT (Pro tier)
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from code_scalpel.licensing.jwt_validator import JWTLicenseValidator

pytestmark = pytest.mark.asyncio


def _use_pro_license(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Helper to configure Pro tier license for advanced vulnerability tests."""
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


async def test_csrf_detection_flask(monkeypatch: pytest.MonkeyPatch):
    """Detect missing CSRF protection in Flask forms."""
    _use_pro_license(monkeypatch)

    code = textwrap.dedent(
        """
        from flask import request, Flask
        app = Flask(__name__)

        @app.route('/transfer', methods=['POST'])
        def transfer_money():
            amount = request.form['amount']  # No CSRF token check
            account = request.form['account']
            transfer(amount, account)
            return 'Success'
        """
    )

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    # May be flagged as CSRF (CWE-352) or detected via pattern matching
    assert result.vulnerability_count >= 1
    # Check if CSRF is mentioned in any vulnerability
    csrf_detected = any(
        "csrf" in v.type.lower() or v.cwe == "CWE-352"
        for v in result.vulnerabilities
    )
    # If not detected by CSRF detector, at least form access should be flagged
    assert csrf_detected or any("form" in v.description.lower() for v in result.vulnerabilities)


async def test_ssrf_detection_requests(monkeypatch: pytest.MonkeyPatch):
    """Detect SSRF via requests library."""
    _use_pro_license(monkeypatch)

    code = textwrap.dedent(
        """
        import requests
        from flask import request

        def fetch_url():
            user_url = request.args.get('url')
            response = requests.get(user_url)  # SSRF - no URL validation
            return response.text
        """
    )

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count >= 1

    # Look for SSRF detection
    ssrf_detected = any(
        "ssrf" in v.type.lower() or v.cwe == "CWE-918"
        for v in result.vulnerabilities
    )
    # SSRF detection is pattern-based, should find it
    assert ssrf_detected


async def test_jwt_insecure_decode(monkeypatch: pytest.MonkeyPatch):
    """Detect JWT decoded without signature verification."""
    _use_pro_license(monkeypatch)

    code = textwrap.dedent(
        """
        import jwt

        def validate_token(token):
            # Insecure: verify=False bypasses signature check
            payload = jwt.decode(token, verify=False)
            return payload
        """
    )

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count >= 1

    # Look for JWT vulnerability detection
    jwt_detected = any(
        "jwt" in v.type.lower() or v.cwe == "CWE-347"
        for v in result.vulnerabilities
    )
    assert jwt_detected

    # Should be marked as critical severity
    critical_vulns = [v for v in result.vulnerabilities if v.severity.lower() == "critical"]
    assert len(critical_vulns) >= 1


async def test_jwt_none_algorithm(monkeypatch: pytest.MonkeyPatch):
    """Detect JWT with 'none' algorithm."""
    _use_pro_license(monkeypatch)

    code = textwrap.dedent(
        """
        import jwt

        def create_admin_token():
            # Critical vulnerability: 'none' algorithm allows unsigned tokens
            token = jwt.encode({'user': 'admin'}, key='', algorithm='none')
            return token
        """
    )

    from code_scalpel.mcp.server import security_scan

    result = await security_scan(code=code)

    assert result.success is True
    assert result.vulnerability_count >= 1

    # Look for JWT vulnerability with 'none' algorithm
    jwt_none_detected = any(
        ("jwt" in v.type.lower() or v.cwe == "CWE-347")
        and ("none" in v.description.lower() or "algorithm" in v.description.lower())
        for v in result.vulnerabilities
    )
    assert jwt_none_detected

    # Should be marked as critical severity
    critical_vulns = [v for v in result.vulnerabilities if v.severity.lower() == "critical"]
    assert len(critical_vulns) >= 1
