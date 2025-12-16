import pytest
import textwrap

from code_scalpel.symbolic_execution_tools.taint_tracker import (
    SINK_PATTERNS,
    SecuritySink,
)
from code_scalpel.mcp.server import security_scan


# [20251215_TEST] Validate Spring/JPA/LDAP/OAuth/SAML sink coverage
@pytest.mark.parametrize(
    "key, sink",
    [
        ("entityManager.createNamedQuery", SecuritySink.SQL_QUERY),
        ("entityManager.createStoredProcedureQuery", SecuritySink.SQL_QUERY),
        ("Query.setParameter", SecuritySink.SQL_QUERY),
        ("TypedQuery.setParameter", SecuritySink.SQL_QUERY),
        ("JpaRepository.deleteBy", SecuritySink.SQL_QUERY),
        ("JdbcTemplate.batchUpdate", SecuritySink.SQL_QUERY),
        ("LdapTemplate.authenticate", SecuritySink.SQL_QUERY),
        ("BindAuthenticator.authenticate", SecuritySink.SQL_QUERY),
        ("JwtDecoder.decode", SecuritySink.SSTI),
        ("JwtEncoder.encode", SecuritySink.SSTI),
        (
            "Saml2AuthenticationRequestFactory.createAuthenticationRequest",
            SecuritySink.SSTI,
        ),
        ("Saml2AuthenticationRequestContext", SecuritySink.SSTI),
    ],
)
def test_spring_jpa_oauth_saml_sinks_present(key, sink):
    assert key in SINK_PATTERNS, f"Missing sink: {key}"
    assert SINK_PATTERNS[key] == sink


# [20251215_TEST] Security scan should flag Spring/JPA sinks when tainted data reaches them
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sink_call, expected_line",
    [
        (
            'entityManager.createNamedQuery(f"SELECT * FROM users WHERE name = {user}")',
            6,
        ),
        (
            'JdbcTemplate.batchUpdate(f"DELETE FROM users WHERE name = {user}")',
            6,
        ),
    ],
)
async def test_spring_jpa_taint_flow_detected(sink_call, expected_line):
    code = textwrap.dedent(
        f"""
        from flask import request

        def handler():
            user = request.args.get("name")
            return {sink_call}
        """
    )

    result = await security_scan(code=code)

    assert result.success
    assert result.has_vulnerabilities
    assert any(vuln.line == expected_line for vuln in result.vulnerabilities)
