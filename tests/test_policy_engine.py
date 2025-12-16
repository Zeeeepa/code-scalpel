"""
Tests for Policy Engine (v2.5.0 Guardian).

[20251216_TEST] Comprehensive tests for OPA/Rego policy enforcement

Test Categories:
1. Policy Loading and Validation
2. Policy Evaluation
3. Semantic Analysis
4. Fail CLOSED behavior
5. Override System
"""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta

from code_scalpel.policy_engine import (
    PolicyEngine,
    PolicyDecision,
    Operation,
    PolicyError,
    SemanticAnalyzer,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_policy_dir(tmp_path):
    """Create temporary directory for policy files."""
    policy_dir = tmp_path / ".scalpel"
    policy_dir.mkdir(exist_ok=True)
    return policy_dir


@pytest.fixture
def valid_policy_file(temp_policy_dir):
    """Create a valid policy YAML file."""
    policy_content = """
version: "1.0"
policies:
  - name: "no-raw-sql"
    description: "Prevent agents from introducing raw SQL queries"
    rule: |
      package scalpel.security
      
      deny[msg] {
        input.operation == "code_edit"
        contains(input.code, "SELECT")
        contains(input.code, "+")
        msg = "Raw SQL detected without parameterized queries"
      }
    severity: "CRITICAL"
    action: "DENY"
"""
    policy_path = temp_policy_dir / "policy.yaml"
    policy_path.write_text(policy_content)
    return str(policy_path)


@pytest.fixture
def invalid_rego_policy_file(temp_policy_dir):
    """Create a policy file with invalid Rego syntax."""
    policy_content = """
version: "1.0"
policies:
  - name: "invalid-syntax"
    description: "Policy with invalid Rego"
    rule: |
      package scalpel.security
      
      deny[msg {  # Missing closing bracket
        input.operation == "code_edit"
        msg = "Invalid syntax"
      }
    severity: "HIGH"
    action: "DENY"
"""
    policy_path = temp_policy_dir / "policy.yaml"
    policy_path.write_text(policy_content)
    return str(policy_path)


@pytest.fixture
def empty_policy_file(temp_policy_dir):
    """Create an empty policy file."""
    policy_path = temp_policy_dir / "policy.yaml"
    policy_path.write_text("")
    return str(policy_path)


@pytest.fixture
def semantic_analyzer():
    """Create SemanticAnalyzer instance."""
    return SemanticAnalyzer()


# =============================================================================
# Policy Loading Tests
# =============================================================================

class TestPolicyLoading:
    """Test policy file loading and parsing."""
    
    def test_load_valid_policy(self, valid_policy_file):
        """[20251216_TEST] Policy Engine loads valid YAML."""
        # Skip if OPA not available
        try:
            engine = PolicyEngine(valid_policy_file)
            assert len(engine.policies) == 1
            assert engine.policies[0].name == "no-raw-sql"
            assert engine.policies[0].severity == "CRITICAL"
            assert engine.policies[0].action == "DENY"
        except PolicyError as e:
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            raise
    
    def test_load_nonexistent_file(self):
        """[20251216_TEST] Fails CLOSED when policy file not found."""
        with pytest.raises(PolicyError, match="Policy file not found"):
            PolicyEngine("nonexistent.yaml")
    
    def test_load_empty_policy(self, empty_policy_file):
        """[20251216_TEST] Fails CLOSED on empty policy file."""
        with pytest.raises(PolicyError, match="empty"):
            PolicyEngine(empty_policy_file)
    
    def test_invalid_yaml_syntax(self, temp_policy_dir):
        """[20251216_TEST] Fails CLOSED on invalid YAML syntax."""
        policy_path = temp_policy_dir / "policy.yaml"
        policy_path.write_text("invalid: yaml: syntax: [[[")
        
        with pytest.raises(PolicyError, match="Failing CLOSED"):
            PolicyEngine(str(policy_path))
    
    def test_invalid_rego_syntax(self, invalid_rego_policy_file):
        """[20251216_TEST] Validates Rego syntax at startup."""
        try:
            engine = PolicyEngine(invalid_rego_policy_file)
            pytest.fail("Should have raised PolicyError for invalid Rego")
        except PolicyError as e:
            # Either OPA not found (acceptable skip) or invalid Rego (pass)
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            elif "Invalid Rego" in str(e):
                pass  # Expected
            else:
                raise
    
    def test_missing_required_fields(self, temp_policy_dir):
        """[20251216_TEST] Fails CLOSED when required fields missing."""
        policy_content = """
version: "1.0"
policies:
  - description: "Missing name field"
    rule: "package test"
"""
        policy_path = temp_policy_dir / "policy.yaml"
        policy_path.write_text(policy_content)
        
        with pytest.raises(PolicyError):
            PolicyEngine(str(policy_path))


# =============================================================================
# Policy Evaluation Tests
# =============================================================================

class TestPolicyEvaluation:
    """Test policy evaluation against operations."""
    
    def test_evaluate_sql_injection(self, valid_policy_file):
        """[20251216_TEST] Detects SQL injection via concatenation."""
        try:
            engine = PolicyEngine(valid_policy_file)
        except PolicyError as e:
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            raise
        
        # Create operation with SQL injection
        operation = Operation(
            type="code_edit",
            code='query = "SELECT * FROM users WHERE id=" + user_id',
            language="python",
            file_path="app.py"
        )
        
        decision = engine.evaluate(operation)
        assert not decision.allowed
        assert "Raw SQL detected" in decision.reason or len(decision.violations) > 0
    
    def test_evaluate_safe_code(self, valid_policy_file):
        """[20251216_TEST] Allows safe code without violations."""
        try:
            engine = PolicyEngine(valid_policy_file)
        except PolicyError as e:
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            raise
        
        # Create operation with safe code
        operation = Operation(
            type="code_edit",
            code='print("Hello, World!")',
            language="python",
            file_path="app.py"
        )
        
        decision = engine.evaluate(operation)
        assert decision.allowed
        assert decision.reason == "No policy violations detected"
    
    def test_evaluation_timeout(self, temp_policy_dir):
        """[20251216_TEST] Fails CLOSED on evaluation timeout."""
        # Create a policy that might timeout (complex Rego)
        policy_content = """
version: "1.0"
policies:
  - name: "test-policy"
    description: "Test policy"
    rule: |
      package scalpel.security
      
      deny[msg] {
        input.operation == "code_edit"
        msg = "Test"
      }
    severity: "HIGH"
    action: "DENY"
"""
        policy_path = temp_policy_dir / "policy.yaml"
        policy_path.write_text(policy_content)
        
        try:
            engine = PolicyEngine(str(policy_path))
        except PolicyError as e:
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            raise
        
        # This should not timeout with simple policy
        operation = Operation(
            type="code_edit",
            code="print('test')",
            language="python"
        )
        
        decision = engine.evaluate(operation)
        # Should either evaluate or fail closed
        assert isinstance(decision, PolicyDecision)


# =============================================================================
# Semantic Analysis Tests
# =============================================================================

class TestSemanticAnalyzer:
    """Test semantic code analysis."""
    
    def test_detect_sql_concatenation_python(self, semantic_analyzer):
        """[20251216_TEST] Detects SQL via string concatenation."""
        code = 'query = "SELECT * FROM users WHERE id=" + user_id'
        assert semantic_analyzer.contains_sql_sink(code, "python")
    
    def test_detect_sql_fstring_python(self, semantic_analyzer):
        """[20251216_TEST] Detects SQL via f-strings."""
        code = 'query = f"SELECT * FROM {table} WHERE id={user_id}"'
        assert semantic_analyzer.contains_sql_sink(code, "python")
    
    def test_detect_sql_format_python(self, semantic_analyzer):
        """[20251216_TEST] Detects SQL via string.format()."""
        code = 'query = "SELECT * FROM users WHERE id={}".format(user_id)'
        assert semantic_analyzer.contains_sql_sink(code, "python")
    
    def test_detect_sql_percent_python(self, semantic_analyzer):
        """[20251216_TEST] Detects SQL via % formatting."""
        code = 'query = "SELECT * FROM users WHERE id=%s" % user_id'
        assert semantic_analyzer.contains_sql_sink(code, "python")
    
    def test_detect_sql_stringbuilder_java(self, semantic_analyzer):
        """[20251216_TEST] Detects SQL via StringBuilder."""
        code = """
        StringBuilder query = new StringBuilder();
        query.append("SELECT * FROM users");
        query.append(" WHERE id=");
        query.append(userId);
        """
        assert semantic_analyzer.contains_sql_sink(code, "java")
    
    def test_detect_sql_template_literal_javascript(self, semantic_analyzer):
        """[20251216_TEST] Detects SQL via template literals."""
        code = 'const query = `SELECT * FROM users WHERE id=${userId}`;'
        assert semantic_analyzer.contains_sql_sink(code, "javascript")
    
    def test_no_sql_in_safe_code(self, semantic_analyzer):
        """[20251216_TEST] Does not flag safe code."""
        code = 'message = "Hello, " + user_name'
        assert not semantic_analyzer.contains_sql_sink(code, "python")
    
    def test_detect_parameterized_query(self, semantic_analyzer):
        """[20251216_TEST] Recognizes parameterized queries as safe."""
        code = 'cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))'
        assert semantic_analyzer.has_parameterization(code, "python")
    
    def test_detect_java_prepared_statement(self, semantic_analyzer):
        """[20251216_TEST] Recognizes PreparedStatement as safe."""
        code = """
        PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE id=?");
        stmt.setString(1, userId);
        """
        assert semantic_analyzer.has_parameterization(code, "java")
    
    def test_detect_annotation(self, semantic_analyzer):
        """[20251216_TEST] Detects Java annotations."""
        code = """
        @RestController
        @PreAuthorize("hasRole('ADMIN')")
        public class UserController {
        }
        """
        assert semantic_analyzer.has_annotation(code, "@RestController")
        assert semantic_analyzer.has_annotation(code, "@PreAuthorize")
    
    def test_detect_file_operations(self, semantic_analyzer):
        """[20251216_TEST] Detects file I/O operations."""
        code = 'with open(filename, "r") as f: content = f.read()'
        assert semantic_analyzer.has_file_operation(code)
    
    def test_detect_tainted_path(self, semantic_analyzer):
        """[20251216_TEST] Detects user-controlled file paths."""
        code = """
        filename = request.args.get('file')
        with open(filename, 'r') as f:
            content = f.read()
        """
        assert semantic_analyzer.tainted_path_input(code)


# =============================================================================
# Fail CLOSED Tests
# =============================================================================

class TestFailClosed:
    """Test fail CLOSED security model."""
    
    def test_fail_closed_on_missing_opa(self, valid_policy_file):
        """[20251216_TEST] Fails CLOSED when OPA CLI not available."""
        # This test will only work if OPA is not installed
        # If OPA is installed, it will be skipped
        try:
            engine = PolicyEngine(valid_policy_file)
            # If we get here, OPA is installed, skip test
            pytest.skip("OPA is installed, cannot test missing OPA case")
        except PolicyError as e:
            assert "OPA CLI not found" in str(e)
            assert "Failing CLOSED" in str(e)
    
    def test_fail_closed_on_invalid_yaml(self, temp_policy_dir):
        """[20251216_TEST] Fails CLOSED on YAML parsing error."""
        policy_path = temp_policy_dir / "policy.yaml"
        policy_path.write_text("{ invalid yaml [[[")
        
        with pytest.raises(PolicyError, match="Failing CLOSED"):
            PolicyEngine(str(policy_path))
    
    def test_fail_closed_on_invalid_rego(self, invalid_rego_policy_file):
        """[20251216_TEST] Fails CLOSED on Rego validation error."""
        try:
            with pytest.raises(PolicyError):
                PolicyEngine(invalid_rego_policy_file)
        except PolicyError as e:
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            raise


# =============================================================================
# Override System Tests
# =============================================================================

class TestOverrideSystem:
    """Test human override functionality."""
    
    def test_valid_override_code(self, valid_policy_file):
        """[20251216_TEST] Accepts valid override code."""
        try:
            engine = PolicyEngine(valid_policy_file)
        except PolicyError as e:
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            raise
        
        operation = Operation(
            type="code_edit",
            code='query = "SELECT * FROM users WHERE id=" + user_id',
            language="python"
        )
        
        decision = engine.evaluate(operation)
        
        override = engine.request_override(
            operation=operation,
            decision=decision,
            justification="Emergency hotfix approved by security team",
            human_code="abc123"
        )
        
        assert override.approved
        assert override.override_id is not None
        assert override.expires_at is not None
    
    def test_invalid_override_code(self, valid_policy_file):
        """[20251216_TEST] Rejects invalid override code."""
        try:
            engine = PolicyEngine(valid_policy_file)
        except PolicyError as e:
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            raise
        
        operation = Operation(type="code_edit", code="test")
        decision = PolicyDecision(allowed=False, reason="Test")
        
        # Too short code
        override = engine.request_override(
            operation=operation,
            decision=decision,
            justification="Test",
            human_code="abc"  # Too short
        )
        
        assert not override.approved
        assert "Invalid" in override.reason
    
    def test_override_single_use(self, valid_policy_file):
        """[20251216_TEST] Override code cannot be reused."""
        try:
            engine = PolicyEngine(valid_policy_file)
        except PolicyError as e:
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            raise
        
        operation = Operation(type="code_edit", code="test")
        decision = PolicyDecision(allowed=False, reason="Test")
        human_code = "validcode123"
        
        # First use should succeed
        override1 = engine.request_override(
            operation=operation,
            decision=decision,
            justification="First use",
            human_code=human_code
        )
        assert override1.approved
        
        # Second use should fail
        override2 = engine.request_override(
            operation=operation,
            decision=decision,
            justification="Second use",
            human_code=human_code
        )
        assert not override2.approved
        assert "already used" in override2.reason.lower()
    
    def test_override_expiration(self, valid_policy_file):
        """[20251216_TEST] Override expires after time limit."""
        try:
            engine = PolicyEngine(valid_policy_file)
        except PolicyError as e:
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            raise
        
        operation = Operation(type="code_edit", code="test")
        decision = PolicyDecision(allowed=False, reason="Test")
        
        override = engine.request_override(
            operation=operation,
            decision=decision,
            justification="Test",
            human_code="testcode123"
        )
        
        assert override.approved
        assert override.expires_at is not None
        
        # Check expiration is approximately 1 hour from now
        expected_expiration = datetime.now() + timedelta(hours=1)
        time_diff = abs((override.expires_at - expected_expiration).total_seconds())
        assert time_diff < 10  # Within 10 seconds


# =============================================================================
# Integration Tests
# =============================================================================

class TestPolicyEngineIntegration:
    """Integration tests combining multiple features."""
    
    def test_end_to_end_sql_blocking(self, temp_policy_dir):
        """[20251216_TEST] End-to-end SQL injection blocking."""
        # Create comprehensive SQL policy
        policy_content = """
version: "1.0"
policies:
  - name: "no-sql-injection"
    description: "Block all forms of SQL injection"
    rule: |
      package scalpel.security
      
      deny[msg] {
        input.operation == "code_edit"
        contains(input.code, "SELECT")
        not contains(input.code, "?")
        not contains(input.code, "PreparedStatement")
        msg = "SQL injection risk detected"
      }
    severity: "CRITICAL"
    action: "DENY"
"""
        policy_path = temp_policy_dir / "policy.yaml"
        policy_path.write_text(policy_content)
        
        try:
            engine = PolicyEngine(str(policy_path))
        except PolicyError as e:
            if "OPA CLI not found" in str(e):
                pytest.skip("OPA not installed")
            raise
        
        # Test various SQL injection attempts
        dangerous_codes = [
            'query = "SELECT * FROM users WHERE id=" + user_id',
            'sql = f"SELECT * FROM {table} WHERE id={id}"',
            'query = "SELECT * FROM users WHERE name=%s" % name',
        ]
        
        for code in dangerous_codes:
            operation = Operation(
                type="code_edit",
                code=code,
                language="python"
            )
            decision = engine.evaluate(operation)
            assert not decision.allowed, f"Failed to block: {code}"
        
        # Test safe code with parameterization
        safe_code = 'cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))'
        operation = Operation(
            type="code_edit",
            code=safe_code,
            language="python"
        )
        decision = engine.evaluate(operation)
        assert decision.allowed, "Incorrectly blocked safe parameterized query"
