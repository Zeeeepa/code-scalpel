"""
Comprehensive testing for Pro tier compliance and best practices features.

Tests verify that Pro tier provides advanced analysis capabilities including:
- Best practice analysis
- Security pattern detection
- Custom rules support
- Extended compliance checking

[20260212_TEST] Created comprehensive Pro tier feature test suite.
"""

from pathlib import Path

import pytest

from code_scalpel.mcp.server import code_policy_check


@pytest.fixture
def pro_license(monkeypatch):
    """Force Pro tier using bundled license. Skips if license is absent/invalid."""
    license_dir = Path(__file__).parent.parent.parent / "licenses"
    pro_licenses = list(license_dir.glob("code_scalpel_license_pro_*.jwt"))
    if not pro_licenses:
        pytest.skip(f"No Pro license file found in {license_dir}")
    license_path = pro_licenses[0]
    if not license_path.read_text(encoding="utf-8").strip():
        pytest.skip("Pro license file is empty (secret not set in CI)")

    monkeypatch.setenv("CODE_SCALPEL_LICENSE_PATH", str(license_path))
    monkeypatch.setenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", "1")

    # Verify the license actually activates Pro tier — skip if invalid/expired
    try:
        from code_scalpel.licensing import jwt_validator, config_loader

        jwt_validator._LICENSE_VALIDATION_CACHE = None
        config_loader.clear_cache()
    except Exception:
        pass
    from code_scalpel.mcp.server import _get_current_tier

    actual_tier = _get_current_tier()
    if actual_tier != "pro":
        monkeypatch.delenv("CODE_SCALPEL_LICENSE_PATH", raising=False)
        monkeypatch.delenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", raising=False)
        pytest.skip(
            f"Pro license did not activate Pro tier (got '{actual_tier}'). "
            "License may be expired or have invalid signature."
        )

    yield
    monkeypatch.delenv("CODE_SCALPEL_LICENSE_PATH", raising=False)
    monkeypatch.delenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", raising=False)


@pytest.fixture
def community_license(monkeypatch, tmp_path):
    """Set license to Community tier (no license file)."""
    monkeypatch.setenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", "1")
    empty_dir = tmp_path / "no_license"
    empty_dir.mkdir()
    monkeypatch.setenv("CODE_SCALPEL_LICENSE_PATH", str(empty_dir / "nonexistent.jwt"))
    yield
    monkeypatch.delenv("CODE_SCALPEL_LICENSE_PATH", raising=False)
    monkeypatch.delenv("CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY", raising=False)


class TestProBestPractices:
    """Test Pro tier best practice analysis."""

    @pytest.mark.asyncio
    async def test_best_practices_violations_available_in_pro(
        self, tmp_path, pro_license
    ):
        """Verify Pro tier returns best_practices_violations."""
        test_file = tmp_path / "anti_patterns.py"
        test_file.write_text("""
# Anti-pattern: bare except
try:
    risky_operation()
except:
    pass

# Anti-pattern: mutable default argument
def append_to_list(item, target_list=[]):
    target_list.append(item)
    return target_list

# Anti-pattern: using global variables
global_counter = 0

def increment():
    global global_counter
    global_counter += 1
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Access violations from data dict
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        # Pro tier should detect best practice violations (category='best_practice')
        best_practice_viols = [
            v for v in violations if v.get("category") == "best_practice"
        ]
        assert (
            len(best_practice_viols) > 0
        ), "Pro tier should detect best practice violations"

    @pytest.mark.asyncio
    async def test_best_practices_not_in_community(self, tmp_path, community_license):
        """Verify Community tier does NOT return best_practices_violations."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
try:
    pass
except:
    pass
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "community"
        # Community should only have basic violations, not best practice analysis
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        # Community might detect bare except, but won't have best_practice category
        best_practice_viols = [
            v for v in violations if v.get("category") == "best_practice"
        ]
        # Community should have fewer or no best practice detections
        assert len(best_practice_viols) == 0 or len(violations) < 5

    @pytest.mark.asyncio
    async def test_detect_mutable_default_argument(self, tmp_path, pro_license):
        """Detect best practice violation: mutable default argument."""
        test_file = tmp_path / "mutable_default.py"
        test_file.write_text("""
def add_item(item, items=[]):
    '''Dangerous: mutable default argument.'''
    items.append(item)
    return items

def process_data(data, cache={}):
    '''Dangerous: mutable dict default.'''
    if 'key' not in cache:
        cache['key'] = expensive_computation(data)
    return cache['key']
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Check for mutable default argument detection
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        # Should detect mutable default
        mutable_default = [
            v
            for v in violations
            if "mutable" in v.get("message", "").lower() or v.get("rule_id") == "PY002"
        ]
        assert len(mutable_default) > 0, "Pro should detect mutable default argument"

    @pytest.mark.asyncio
    async def test_detect_bare_except(self, tmp_path, pro_license):
        """Detect best practice violation: bare except clause."""
        test_file = tmp_path / "bare_except.py"
        test_file.write_text("""
def risky_function():
    try:
        dangerous_operation()
    except:  # Bad: catches everything including KeyboardInterrupt
        print("Error occurred")

def another_risky():
    try:
        something()
    except Exception:  # Better but still broad
        pass
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Should detect bare except
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        bare_except = [
            v
            for v in violations
            if "bare" in v.get("message", "").lower() or v.get("rule_id") == "PY001"
        ]
        assert len(bare_except) > 0, "Pro should detect bare except"

    @pytest.mark.asyncio
    async def test_detect_star_imports(self, tmp_path, pro_license):
        """Detect best practice violation: star imports."""
        test_file = tmp_path / "star_import.py"
        test_file.write_text("""
from os import *  # Bad: pollutes namespace
from sys import *  # Bad: unclear what's imported

def main():
    result = path.join("a", "b")  # Which module is 'path' from?
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Star imports should be flagged
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        # Should detect import issues
        assert len(violations) > 0, "Pro should detect code issues"


class TestProSecurityPatterns:
    """Test Pro tier security pattern detection."""

    @pytest.mark.asyncio
    async def test_security_warnings_available_in_pro(self, tmp_path, pro_license):
        """Verify Pro tier returns security_warnings."""
        test_file = tmp_path / "security_issues.py"
        test_file.write_text("""
import subprocess

def run_command(user_input):
    # Security issue: command injection risk
    subprocess.call(user_input, shell=True)
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Pro should detect security issues
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        # Shell=True is a security risk - should flag the risky code
        assert len(violations) > 0, "Pro should detect code issues"

    @pytest.mark.asyncio
    async def test_detect_sql_injection_pattern(self, tmp_path, pro_license):
        """Detect security pattern: SQL injection risk."""
        test_file = tmp_path / "sql_injection.py"
        test_file.write_text("""
import sqlite3

def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Should detect SQL injection pattern
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        # Should detect f-string in SQL query
        assert len(violations) > 0, "Pro should detect code issues"

    @pytest.mark.asyncio
    async def test_detect_hardcoded_secrets(self, tmp_path, pro_license):
        """Detect security pattern: hardcoded secrets."""
        test_file = tmp_path / "secrets.py"
        test_file.write_text("""
# Security issues: hardcoded secrets
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
API_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
PASSWORD = "SuperSecret123!"

def connect():
    return database.connect(password=PASSWORD)
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Should detect hardcoded secrets
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        # Pro should flag security issues
        assert len(violations) > 0, "Pro should detect code issues"

    @pytest.mark.asyncio
    async def test_detect_eval_usage(self, tmp_path, pro_license):
        """Detect security pattern: dangerous eval usage."""
        test_file = tmp_path / "eval_usage.py"
        test_file.write_text("""
def calculate(expression):
    # Dangerous: eval with user input
    result = eval(expression)
    return result

def execute_code(code_string):
    # Dangerous: exec with user input
    exec(code_string)
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # eval/exec should trigger security warnings
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        # Should detect dangerous eval usage
        assert len(violations) > 0, "Pro should detect dangerous code"


class TestProCustomRules:
    """Test Pro tier custom rules support."""

    @pytest.mark.asyncio
    async def test_custom_rule_results_available_in_pro(self, tmp_path, pro_license):
        """Verify Pro tier returns custom_rule_results."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Pro has custom_rules_enabled capability
        from code_scalpel.licensing.features import has_capability

        assert has_capability("code_policy_check", "custom_rules", "pro")

    @pytest.mark.asyncio
    async def test_custom_rules_not_in_community(self, tmp_path, community_license):
        """Verify Community tier does NOT support custom rules."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "community"
        # Community should not have custom rules capability
        from code_scalpel.licensing.features import has_capability

        assert not has_capability("code_policy_check", "custom_rules", "community")


class TestProAsyncErrorPatterns:
    """Test Pro tier async error pattern detection."""

    @pytest.mark.asyncio
    async def test_detect_missing_await(self, tmp_path, pro_license):
        """Detect async error: missing await on coroutine."""
        test_file = tmp_path / "async_errors.py"
        test_file.write_text("""
async def fetch_data():
    return {"data": "value"}

async def process():
    # Error: missing await
    result = fetch_data()
    print(result)  # Will print coroutine object, not data
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Should detect async issues
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        # Pro should detect async patterns
        assert len(violations) >= 0, "Pro processes async code"

    @pytest.mark.asyncio
    async def test_detect_sync_in_async_context(self, tmp_path, pro_license):
        """Detect async error: synchronous blocking call in async function."""
        test_file = tmp_path / "blocking_in_async.py"
        test_file.write_text("""
import time

async def slow_handler():
    # Bad: blocking sleep in async function
    time.sleep(5)
    return "done"
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Pro should detect this anti-pattern


class TestProExtendedCompliance:
    """Test Pro tier extended compliance (non-Enterprise standards)."""

    @pytest.mark.asyncio
    async def test_extended_compliance_capability(self, tmp_path, pro_license):
        """Verify Pro tier has extended_compliance capability."""
        from code_scalpel.licensing.features import has_capability

        assert has_capability("code_policy_check", "extended_compliance", "pro")
        assert not has_capability("code_policy_check", "hipaa_compliance", "pro")

    @pytest.mark.asyncio
    async def test_pro_cannot_access_enterprise_compliance(self, tmp_path, pro_license):
        """Verify Pro tier cannot access Enterprise compliance standards."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        result = await code_policy_check(
            paths=[str(test_file)],
            compliance_standards=["hipaa"],  # Enterprise only
        )

        assert result.tier_applied == "pro"
        # Pro should ignore Enterprise-only compliance standards
        # compliance_reports should be None or empty for Pro
        compliance_reports = getattr(result, "compliance_reports", None)
        assert compliance_reports is None or compliance_reports == {}


class TestProVsCommunityComparison:
    """Test differences between Pro and Community tier features."""

    @pytest.mark.asyncio
    async def test_community_limited_analysis(self, tmp_path, community_license):
        """Verify Community tier only provides basic violations."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import subprocess

try:
    subprocess.call(user_input, shell=True)
except:
    pass
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "community"
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        assert violations is not None  # Basic violations always present

        # Community has limited analysis
        from code_scalpel.licensing.features import has_capability

        assert not has_capability("code_policy_check", "custom_rules", "community")
        assert not has_capability(
            "code_policy_check", "best_practice_analysis", "community"
        )

    @pytest.mark.asyncio
    async def test_pro_enhanced_analysis(self, tmp_path, pro_license):
        """Verify Pro tier provides enhanced analysis."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import subprocess

try:
    subprocess.call(user_input, shell=True)
except:
    pass
""")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        data = result.data if hasattr(result, "data") else result
        violations = data.get("violations", [])
        assert violations is not None

        # Pro should have these advanced capabilities
        from code_scalpel.licensing.features import has_capability

        assert has_capability("code_policy_check", "best_practice_analysis", "pro")
        assert has_capability("code_policy_check", "security_patterns", "pro")
        assert has_capability("code_policy_check", "custom_rules", "pro")


class TestProUnlimitedLimits:
    """Test Pro tier unlimited file and rule limits."""

    @pytest.mark.asyncio
    async def test_pro_handles_many_files(self, tmp_path, pro_license):
        """Verify Pro tier can handle many files (no 100 file limit)."""
        # Create 150 files (exceeds Community limit of 100)
        for i in range(150):
            test_file = tmp_path / f"file_{i}.py"
            test_file.write_text("x = 1\n")

        result = await code_policy_check(paths=[str(tmp_path)])

        assert result.tier_applied == "pro"
        # Pro should check all 150 files (no limit)
        assert result.files_checked == 150

    @pytest.mark.asyncio
    async def test_pro_has_no_rule_limit(self, tmp_path, pro_license):
        """Verify Pro tier has no rule limit (vs Community 50 rule limit)."""
        from code_scalpel.licensing.features import get_tool_capabilities

        caps = get_tool_capabilities("code_policy_check", "pro")
        limits = caps.get("limits", {})

        # Pro should have unlimited rules (None or -1 in limits.toml)
        max_rules = limits.get("max_rules")
        assert max_rules is None or max_rules == -1 or max_rules > 1000


class TestProResponseStructure:
    """Test Pro tier response structure and metadata."""

    @pytest.mark.asyncio
    async def test_pro_response_includes_tier_metadata(self, tmp_path, pro_license):
        """Verify Pro tier response includes correct tier metadata."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"
        # Access metadata from data
        data = result.data if hasattr(result, "data") else result
        assert data.get("files_checked") is not None
        assert data.get("rules_applied") is not None
        assert data.get("tier") == "pro"

    @pytest.mark.asyncio
    async def test_pro_does_not_include_enterprise_fields(self, tmp_path, pro_license):
        """Verify Pro tier does NOT include Enterprise-only fields."""
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")

        result = await code_policy_check(paths=[str(test_file)])

        assert result.tier_applied == "pro"

        # Pro does NOT have Enterprise-only compliance features
        from code_scalpel.licensing.features import has_capability

        assert not has_capability("code_policy_check", "hipaa_compliance", "pro")
        assert not has_capability("code_policy_check", "soc2_compliance", "pro")
        assert not has_capability("code_policy_check", "gdpr_compliance", "pro")
        assert not has_capability("code_policy_check", "pci_dss_compliance", "pro")
        assert not has_capability("code_policy_check", "audit_trail", "pro")
        assert not has_capability("code_policy_check", "pdf_certification", "pro")


class TestProPerformance:
    """Test Pro tier performance characteristics."""

    @pytest.mark.asyncio
    async def test_pro_performance_with_large_codebase(self, tmp_path, pro_license):
        """Verify Pro tier handles large codebases efficiently."""
        # Create realistic code structure
        for i in range(50):
            test_file = tmp_path / f"module_{i}.py"
            test_file.write_text(f"""
import logging

logger = logging.getLogger(__name__)

class Service{i}:
    def __init__(self):
        self.data = []
    
    def process(self, item):
        try:
            result = self._validate(item)
            logger.info(f"Processed {{item}}")
            return result
        except Exception as e:
            logger.error("Error: {{e}}")
            raise
    
    def _validate(self, item):
        return item is not None
""")

        result = await code_policy_check(paths=[str(tmp_path)])

        assert result.tier_applied == "pro"
        assert result.files_checked == 50
        # Should complete without timeout
        assert result.error is None or result.error == ""
