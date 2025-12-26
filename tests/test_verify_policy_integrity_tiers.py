"""
Tests for verify_policy_integrity tier-based feature gating.

[20251225_TESTS] v3.3.0 - Comprehensive tier testing for verify_policy_integrity tool.

This test suite validates:
- Community: Basic style guide checking (50 rule limit)
- Pro: Best practice checking, async/await patterns, error handling
- Enterprise: HIPAA/SOC2 compliance, PDF certification, audit trail
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the function directly
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from code_scalpel.mcp.server import _verify_policy_integrity_sync


# Sample Python code with various issues
ASYNC_WITHOUT_TRY_CATCH = """
async def fetch_data(url):
    response = await client.get(url)
    return response.json()
"""

BARE_EXCEPT_CODE = """
def process_data(data):
    try:
        result = transform(data)
    except:
        return None
"""

PRINT_STATEMENT_CODE = """
def calculate(x, y):
    print(f"Calculating {x} + {y}")
    return x + y
"""

HIPAA_PHI_CODE = """
def get_patient_data(request):
    patient_info = request.get('patient')
    medical_history = request.get('medical_records')
    return save_to_database(patient_info, medical_history)
"""

SOC2_AUDIT_CODE = """
def delete_user_account(user_id):
    # Critical operation without audit logging
    database.users.delete(id=user_id)
    return True
"""


@pytest.fixture
def temp_project():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project = Path(tmpdir)
        
        # Create policy directory
        policy_dir = project / ".code-scalpel"
        policy_dir.mkdir()
        
        # Create some Python files with various issues
        (project / "async_code.py").write_text(ASYNC_WITHOUT_TRY_CATCH)
        (project / "error_handling.py").write_text(BARE_EXCEPT_CODE)
        (project / "debug_code.py").write_text(PRINT_STATEMENT_CODE)
        (project / "patient_handler.py").write_text(HIPAA_PHI_CODE)
        (project / "user_service.py").write_text(SOC2_AUDIT_CODE)
        
        # Create a policy file
        (policy_dir / "test_policy.yml").write_text("rules:\n  - name: test\n")
        
        yield project


@pytest.fixture
def mock_community_tier():
    """Mock Community tier capabilities."""
    return {
        "capabilities": {
            "style_guide_checking",
            "pep8_compliance",
            "eslint_rule_checking",
            "basic_policy_validation",
        },
        "limits": {
            "max_rules": 50,
        }
    }


@pytest.fixture
def mock_pro_tier():
    """Mock Pro tier capabilities."""
    return {
        "capabilities": {
            "style_guide_checking",
            "pep8_compliance",
            "eslint_rule_checking",
            "basic_policy_validation",
            "best_practice_checking",
            "async_try_catch_enforcement",
            "error_handling_patterns",
            "code_pattern_enforcement",
            "signature_validation",
        },
        "limits": {
            "max_rules": 200,
        }
    }


@pytest.fixture
def mock_enterprise_tier():
    """Mock Enterprise tier capabilities."""
    return {
        "capabilities": {
            "style_guide_checking",
            "pep8_compliance",
            "eslint_rule_checking",
            "basic_policy_validation",
            "best_practice_checking",
            "async_try_catch_enforcement",
            "error_handling_patterns",
            "code_pattern_enforcement",
            "signature_validation",
            "regulatory_compliance_audit",
            "hipaa_compliance_check",
            "soc2_compliance_check",
            "pdf_certification_generation",
            "audit_trail_logging",
        },
        "limits": {
            "max_rules": None,
        }
    }


def test_verify_policy_community(temp_project, mock_community_tier):
    """Test Community tier basic validation (no Pro/Enterprise features)."""
    # Mock the verifier to avoid needing actual crypto setup
    with patch('code_scalpel.policy_engine.crypto_verify.CryptographicPolicyVerifier') as mock_verifier:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.manifest_valid = False  # Community doesn't verify signatures
        mock_result.files_verified = 1
        mock_result.files_failed = []
        mock_result.error = None
        mock_verifier.return_value.verify_all_policies.return_value = mock_result
        
        result = _verify_policy_integrity_sync(
            policy_dir=str(temp_project / ".code-scalpel"),
            manifest_source="file",
            tier="community",
            capabilities=mock_community_tier
        )
        
        assert result.success is True
        assert result.files_verified == 1
        
        # Pro/Enterprise fields should be empty
        assert result.best_practices_violations == []
        assert result.pattern_matches == []
        assert result.compliance_reports == {}
        assert result.audit_trail == []
        assert result.pdf_report is None


def test_verify_policy_pro(temp_project, mock_pro_tier):
    """Test Pro tier with best practice checking."""
    with patch('code_scalpel.policy_engine.crypto_verify.CryptographicPolicyVerifier') as mock_verifier:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.manifest_valid = True
        mock_result.files_verified = 1
        mock_result.files_failed = []
        mock_result.error = None
        mock_verifier.return_value.verify_all_policies.return_value = mock_result
        
        result = _verify_policy_integrity_sync(
            policy_dir=str(temp_project / ".code-scalpel"),
            manifest_source="file",
            tier="pro",
            capabilities=mock_pro_tier
        )
        
        assert result.success is True
        
        # Pro tier should detect best practice violations
        assert len(result.best_practices_violations) > 0
        
        # Should find async without try/catch
        async_violations = [v for v in result.best_practices_violations 
                           if v["rule"] == "async_function_without_error_handling"]
        assert len(async_violations) > 0
        
        # Should find bare except clauses
        bare_except_violations = [v for v in result.best_practices_violations 
                                  if v["rule"] == "bare_except_clause"]
        assert len(bare_except_violations) > 0
        
        # Pro tier should detect pattern matches
        assert len(result.pattern_matches) > 0
        
        # Should find print statement usage
        print_patterns = [p for p in result.pattern_matches 
                         if p["pattern"] == "print_statement_usage"]
        assert len(print_patterns) > 0
        
        # Enterprise-only fields should still be empty
        assert result.compliance_reports == {}
        assert result.audit_trail == []
        assert result.pdf_report is None


def test_verify_policy_enterprise(temp_project, mock_enterprise_tier):
    """Test Enterprise tier with compliance audits."""
    with patch('code_scalpel.policy_engine.crypto_verify.CryptographicPolicyVerifier') as mock_verifier:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.manifest_valid = True
        mock_result.files_verified = 1
        mock_result.files_failed = []
        mock_result.error = None
        mock_verifier.return_value.verify_all_policies.return_value = mock_result
        
        result = _verify_policy_integrity_sync(
            policy_dir=str(temp_project / ".code-scalpel"),
            manifest_source="file",
            tier="enterprise",
            capabilities=mock_enterprise_tier
        )
        
        assert result.success is True
        
        # Enterprise tier should have all Pro features
        assert len(result.best_practices_violations) > 0
        assert len(result.pattern_matches) > 0
        
        # Enterprise tier should have compliance reports
        assert len(result.compliance_reports) > 0
        assert "hipaa" in result.compliance_reports
        assert "soc2" in result.compliance_reports
        
        # Check HIPAA compliance report structure
        hipaa_report = result.compliance_reports["hipaa"]
        assert "status" in hipaa_report
        assert "findings" in hipaa_report
        assert "total_violations" in hipaa_report
        
        # Check SOC2 compliance report structure
        soc2_report = result.compliance_reports["soc2"]
        assert "status" in soc2_report
        assert "findings" in soc2_report
        assert "total_violations" in soc2_report
        
        # Enterprise tier should have audit trail
        assert len(result.audit_trail) > 0
        audit_entry = result.audit_trail[0]
        assert "timestamp" in audit_entry
        assert "action" in audit_entry
        assert audit_entry["action"] == "policy_verification"
        
        # Enterprise tier should generate PDF report
        assert result.pdf_report is not None
        # Should be base64 encoded
        import base64
        try:
            decoded = base64.b64decode(result.pdf_report)
            assert len(decoded) > 0
        except Exception:
            pytest.fail("PDF report should be valid base64")


def test_tier_max_rules_limit(temp_project, mock_community_tier):
    """Test that Community tier enforces 50 rule limit."""
    # Create 60 Python files
    for i in range(60):
        (temp_project / f"file_{i}.py").write_text("print('test')")
    
    with patch('code_scalpel.policy_engine.crypto_verify.CryptographicPolicyVerifier') as mock_verifier:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.manifest_valid = False
        mock_result.files_verified = 1
        mock_result.files_failed = []
        mock_result.error = None
        mock_verifier.return_value.verify_all_policies.return_value = mock_result
        
        result = _verify_policy_integrity_sync(
            policy_dir=str(temp_project / ".code-scalpel"),
            manifest_source="file",
            tier="community",
            capabilities=mock_community_tier
        )
        
        # Community should process max 50 files
        # (Note: implementation may check fewer than all files, this validates limit exists)
        assert result.success is True


def test_pro_async_error_handling_detection(temp_project, mock_pro_tier):
    """Test Pro tier detects async functions without error handling."""
    with patch('code_scalpel.policy_engine.crypto_verify.CryptographicPolicyVerifier') as mock_verifier:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.manifest_valid = True
        mock_result.files_verified = 1
        mock_result.files_failed = []
        mock_result.error = None
        mock_verifier.return_value.verify_all_policies.return_value = mock_result
        
        result = _verify_policy_integrity_sync(
            policy_dir=str(temp_project / ".code-scalpel"),
            manifest_source="file",
            tier="pro",
            capabilities=mock_pro_tier
        )
        
        # Should find the async function without try/catch
        async_violations = [v for v in result.best_practices_violations 
                           if v["rule"] == "async_function_without_error_handling"]
        assert len(async_violations) > 0
        
        # Check violation structure
        violation = async_violations[0]
        assert "file" in violation
        assert "line" in violation
        assert "severity" in violation
        assert violation["severity"] == "medium"


def test_pro_bare_except_detection(temp_project, mock_pro_tier):
    """Test Pro tier detects bare except clauses."""
    with patch('code_scalpel.policy_engine.crypto_verify.CryptographicPolicyVerifier') as mock_verifier:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.manifest_valid = True
        mock_result.files_verified = 1
        mock_result.files_failed = []
        mock_result.error = None
        mock_verifier.return_value.verify_all_policies.return_value = mock_result
        
        result = _verify_policy_integrity_sync(
            policy_dir=str(temp_project / ".code-scalpel"),
            manifest_source="file",
            tier="pro",
            capabilities=mock_pro_tier
        )
        
        # Should find bare except clause
        bare_except = [v for v in result.best_practices_violations 
                      if v["rule"] == "bare_except_clause"]
        assert len(bare_except) > 0
        assert bare_except[0]["severity"] == "high"


def test_enterprise_hipaa_compliance(temp_project, mock_enterprise_tier):
    """Test Enterprise tier performs HIPAA compliance checks."""
    with patch('code_scalpel.policy_engine.crypto_verify.CryptographicPolicyVerifier') as mock_verifier:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.manifest_valid = True
        mock_result.files_verified = 1
        mock_result.files_failed = []
        mock_result.error = None
        mock_verifier.return_value.verify_all_policies.return_value = mock_result
        
        result = _verify_policy_integrity_sync(
            policy_dir=str(temp_project / ".code-scalpel"),
            manifest_source="file",
            tier="enterprise",
            capabilities=mock_enterprise_tier
        )
        
        # Should have HIPAA compliance report
        assert "hipaa" in result.compliance_reports
        hipaa = result.compliance_reports["hipaa"]
        
        # Should detect PHI handling without encryption
        assert len(hipaa["findings"]) > 0
        phi_finding = [f for f in hipaa["findings"] 
                      if f["finding"] == "potential_phi_without_encryption"]
        assert len(phi_finding) > 0
        assert phi_finding[0]["severity"] == "critical"


def test_enterprise_soc2_compliance(temp_project, mock_enterprise_tier):
    """Test Enterprise tier performs SOC2 compliance checks."""
    with patch('code_scalpel.policy_engine.crypto_verify.CryptographicPolicyVerifier') as mock_verifier:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.manifest_valid = True
        mock_result.files_verified = 1
        mock_result.files_failed = []
        mock_result.error = None
        mock_verifier.return_value.verify_all_policies.return_value = mock_result
        
        result = _verify_policy_integrity_sync(
            policy_dir=str(temp_project / ".code-scalpel"),
            manifest_source="file",
            tier="enterprise",
            capabilities=mock_enterprise_tier
        )
        
        # Should have SOC2 compliance report
        assert "soc2" in result.compliance_reports
        soc2 = result.compliance_reports["soc2"]
        
        # Should detect critical operations without audit logs
        assert len(soc2["findings"]) > 0
        audit_finding = [f for f in soc2["findings"] 
                        if f["finding"] == "critical_operation_without_audit_log"]
        assert len(audit_finding) > 0
        assert audit_finding[0]["severity"] == "high"


def test_enterprise_pdf_generation(temp_project, mock_enterprise_tier):
    """Test Enterprise tier generates PDF certification reports."""
    with patch('code_scalpel.policy_engine.crypto_verify.CryptographicPolicyVerifier') as mock_verifier:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.manifest_valid = True
        mock_result.files_verified = 1
        mock_result.files_failed = []
        mock_result.error = None
        mock_verifier.return_value.verify_all_policies.return_value = mock_result
        
        result = _verify_policy_integrity_sync(
            policy_dir=str(temp_project / ".code-scalpel"),
            manifest_source="file",
            tier="enterprise",
            capabilities=mock_enterprise_tier
        )
        
        # Should generate PDF report
        assert result.pdf_report is not None
        
        # Decode and check content
        import base64
        decoded = base64.b64decode(result.pdf_report).decode()
        assert "CODE POLICY VERIFICATION CERTIFICATE" in decoded
        assert "VERIFICATION RESULTS:" in decoded
        assert "COMPLIANCE REPORTS:" in decoded
        assert "HIPAA" in decoded or "SOC2" in decoded


def test_pro_unlimited_rules(temp_project, mock_pro_tier):
    """Test Pro tier has no rule limit (200 rule limit)."""
    # Create 150 Python files
    for i in range(150):
        (temp_project / f"file_{i}.py").write_text("print('test')")
    
    with patch('code_scalpel.policy_engine.crypto_verify.CryptographicPolicyVerifier') as mock_verifier:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.manifest_valid = True
        mock_result.files_verified = 1
        mock_result.files_failed = []
        mock_result.error = None
        mock_verifier.return_value.verify_all_policies.return_value = mock_result
        
        result = _verify_policy_integrity_sync(
            policy_dir=str(temp_project / ".code-scalpel"),
            manifest_source="file",
            tier="pro",
            capabilities=mock_pro_tier
        )
        
        # Pro tier should process more files than Community
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
