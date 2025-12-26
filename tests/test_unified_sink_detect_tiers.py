"""
Tests for unified_sink_detect tier-specific features.

[20251225_TESTS] v3.3.0 - Tier overhaul tests for unified_sink_detect
"""

import pytest
from unittest.mock import patch, MagicMock

from code_scalpel.licensing import get_tool_capabilities

# Sample code snippets for testing
BASIC_SQL_INJECTION = '''
import sqlite3
def get_user(user_id):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchall()
'''

LOGIC_SINK_CODE = '''
import boto3
import stripe

def handle_payment(amount, customer_email):
    # S3 public write
    s3_client = boto3.client('s3')
    s3_client.put_object(Bucket='mybucket', Key='file.txt', Body='data', ACL='public-read')
    
    # Payment processing
    stripe.charge.create(amount=amount, currency='usd', source='tok_visa')
    
    # Email send
    from sendgrid import SendGridAPIClient
    sg = SendGridAPIClient()
    sg.mail.send(to=customer_email, subject='Payment', body='Thanks')
'''

CUSTOM_SINK_CODE = '''
def process_request(user_input):
    # Custom internal API call
    result = internal_api_call(user_input)
    
    # Legacy system call
    legacy_system.execute(result)
    
    # Privileged operation
    privileged_operation(user_input)
    return result
'''

XSS_CODE = '''
def render_comment(comment):
    return f"<div>{comment}</div>"
'''


@pytest.fixture
def mock_community_tier():
    """Mock Community tier capabilities."""
    return {
        "enabled": True,
        "capabilities": {
            "sql_sink_detection",
            "shell_command_sink_detection",
            "file_operation_sinks",
            "xss_sink_detection",
            "basic_multi_language_support"
        },
        "limits": {
            "languages": ["python", "javascript", "typescript", "java"],
            "max_sinks": 50,
        }
    }


@pytest.fixture
def mock_pro_tier():
    """Mock Pro tier capabilities."""
    return {
        "enabled": True,
        "capabilities": {
            "sql_sink_detection",
            "shell_command_sink_detection",
            "file_operation_sinks",
            "xss_sink_detection",
            "basic_multi_language_support",
            "logic_sink_detection",
            "s3_public_write_detection",
            "email_send_detection",
            "payment_api_detection",
            "extended_language_support",
            "sink_confidence_scoring"
        },
        "limits": {
            "languages": ["python", "javascript", "typescript", "java", "go", "rust"],
            "max_sinks": None,
        }
    }


@pytest.fixture
def mock_enterprise_tier():
    """Mock Enterprise tier capabilities."""
    return {
        "enabled": True,
        "capabilities": {
            "sql_sink_detection",
            "shell_command_sink_detection",
            "file_operation_sinks",
            "xss_sink_detection",
            "basic_multi_language_support",
            "logic_sink_detection",
            "s3_public_write_detection",
            "email_send_detection",
            "payment_api_detection",
            "extended_language_support",
            "sink_confidence_scoring",
            "sink_categorization",
            "risk_level_tagging",
            "clearance_requirement_tagging",
            "custom_sink_patterns",
            "sink_inventory_reporting"
        },
        "limits": {
            "languages": None,  # All languages
            "max_sinks": None,
            "custom_sinks_limit": None,
        }
    }


def test_unified_sink_detect_community(mock_community_tier):
    """Test Community tier detects basic sinks without Pro/Enterprise fields."""
    from code_scalpel.mcp.server import _unified_sink_detect_sync
    
    result = _unified_sink_detect_sync(
        code=BASIC_SQL_INJECTION,
        language="python",
        min_confidence=0.7,
        tier="community",
        capabilities=mock_community_tier
    )
    
    assert result.success
    assert result.sink_count >= 1  # Should detect SQL injection
    assert len(result.sinks) >= 1
    
    # Community tier should NOT have Pro/Enterprise fields populated
    assert result.logic_sinks == []
    assert result.extended_language_sinks == {}
    assert result.confidence_scores == {}
    assert result.sink_categories == {}
    assert result.risk_assessments == []
    assert result.custom_sink_matches == []


def test_unified_sink_detect_pro(mock_pro_tier):
    """Test Pro tier detects logic sinks and provides confidence scores."""
    from code_scalpel.mcp.server import _unified_sink_detect_sync
    
    result = _unified_sink_detect_sync(
        code=LOGIC_SINK_CODE,
        language="python",
        min_confidence=0.7,
        tier="pro",
        capabilities=mock_pro_tier
    )
    
    assert result.success
    
    # Pro tier should detect logic sinks
    assert len(result.logic_sinks) >= 1
    
    # Check for S3, payment, or email logic sinks
    logic_types = [ls["type"] for ls in result.logic_sinks]
    assert any(t in logic_types for t in ["S3_PUBLIC_WRITE", "S3_PUBLIC_ACL", "PAYMENT_STRIPE", "EMAIL_SEND"])
    
    # Pro tier should provide confidence scores if sinks detected
    if result.sink_count > 0:
        assert len(result.confidence_scores) > 0
        # Confidence should be 0-1 range
        for score in result.confidence_scores.values():
            assert 0.0 <= score <= 1.0
    
    # Pro tier should NOT have Enterprise fields
    assert result.sink_categories == {}
    assert result.risk_assessments == []
    assert result.custom_sink_matches == []


def test_unified_sink_detect_enterprise(mock_enterprise_tier):
    """Test Enterprise tier provides categorization and risk assessments."""
    from code_scalpel.mcp.server import _unified_sink_detect_sync
    
    result = _unified_sink_detect_sync(
        code=BASIC_SQL_INJECTION,
        language="python",
        min_confidence=0.7,
        tier="enterprise",
        capabilities=mock_enterprise_tier
    )
    
    assert result.success
    assert result.sink_count >= 1
    
    # Enterprise should have sink categories
    assert result.sink_categories is not None
    if result.sink_count > 0:
        # Should categorize into risk levels
        assert "critical" in result.sink_categories or \
               "high" in result.sink_categories or \
               "medium" in result.sink_categories or \
               "low" in result.sink_categories
    
    # Enterprise should have risk assessments
    assert len(result.risk_assessments) >= 1
    for assessment in result.risk_assessments:
        assert "risk_score" in assessment
        assert "clearance_required" in assessment
        assert assessment["clearance_required"] in ["ADMIN_ONLY", "SENIOR_DEV", "DEVELOPER", "ANY"]
        assert 0 <= assessment["risk_score"] <= 10


def test_tier_language_restrictions():
    """Test language restrictions are enforced per tier."""
    from code_scalpel.mcp.server import _unified_sink_detect_sync
    
    # Community tier only supports 4 languages
    community_caps = {
        "enabled": True,
        "capabilities": {"sql_sink_detection"},
        "limits": {"languages": ["python", "javascript", "typescript", "java"]}
    }
    
    # Try unsupported language at Community tier
    result = _unified_sink_detect_sync(
        code="fn main() { }",
        language="rust",
        min_confidence=0.7,
        tier="community",
        capabilities=community_caps
    )
    
    assert not result.success
    assert "Unsupported language" in result.error or "not supported" in result.error


def test_pro_logic_sink_detection(mock_pro_tier):
    """Test Pro tier logic sink detection with S3, email, payment patterns."""
    from code_scalpel.mcp.server import _unified_sink_detect_sync
    
    result = _unified_sink_detect_sync(
        code=LOGIC_SINK_CODE,
        language="python",
        min_confidence=0.7,
        tier="pro",
        capabilities=mock_pro_tier
    )
    
    assert result.success
    assert len(result.logic_sinks) >= 2  # Should find multiple logic sinks
    
    # Check for specific logic sink types
    for logic_sink in result.logic_sinks:
        assert "type" in logic_sink
        assert "line" in logic_sink
        assert "confidence" in logic_sink
        assert "recommendation" in logic_sink
        assert 0.0 <= logic_sink["confidence"] <= 1.0


def test_enterprise_custom_patterns(mock_enterprise_tier):
    """Test Enterprise custom sink pattern matching."""
    from code_scalpel.mcp.server import _unified_sink_detect_sync
    
    result = _unified_sink_detect_sync(
        code=CUSTOM_SINK_CODE,
        language="python",
        min_confidence=0.7,
        tier="enterprise",
        capabilities=mock_enterprise_tier
    )
    
    assert result.success
    
    # Enterprise should detect custom patterns
    assert len(result.custom_sink_matches) >= 1
    
    # Check custom sink structure
    custom_types = [cs["type"] for cs in result.custom_sink_matches]
    assert any(t.startswith("CUSTOM_") for t in custom_types)
    
    for custom_sink in result.custom_sink_matches:
        assert "type" in custom_sink
        assert "line" in custom_sink
        assert "confidence" in custom_sink
        assert "recommendation" in custom_sink


def test_enterprise_categorization(mock_enterprise_tier):
    """Test Enterprise sink categorization by risk level."""
    from code_scalpel.mcp.server import _unified_sink_detect_sync
    
    # Use code with both high-risk (SQL) and lower-risk (XSS) sinks
    mixed_code = BASIC_SQL_INJECTION + "\n\n" + XSS_CODE
    
    result = _unified_sink_detect_sync(
        code=mixed_code,
        language="python",
        min_confidence=0.7,
        tier="enterprise",
        capabilities=mock_enterprise_tier
    )
    
    assert result.success
    
    # Should have categorized sinks
    assert result.sink_categories is not None
    
    # Count sinks across categories
    total_categorized = sum(
        len(sinks) 
        for sinks in result.sink_categories.values()
    )
    assert total_categorized == result.sink_count
    
    # Verify category structure
    for category in ["critical", "high", "medium", "low"]:
        assert category in result.sink_categories
        for sink in result.sink_categories[category]:
            assert "sink_id" in sink
            assert "type" in sink
            assert "confidence" in sink


def test_max_sinks_limit():
    """Test Community tier max_sinks limit is enforced."""
    from code_scalpel.mcp.server import _unified_sink_detect_sync
    
    # Create code with many potential sinks
    many_sinks_code = "\n".join([
        f"cursor.execute(f'SELECT * FROM t WHERE id={{user_id_{i}}}')"
        for i in range(100)
    ])
    
    community_caps = {
        "enabled": True,
        "capabilities": {"sql_sink_detection"},
        "limits": {"languages": ["python"], "max_sinks": 50}
    }
    
    result = _unified_sink_detect_sync(
        code=many_sinks_code,
        language="python",
        min_confidence=0.7,
        tier="community",
        capabilities=community_caps
    )
    
    assert result.success
    # Should be limited to 50 sinks at Community tier
    assert len(result.sinks) <= 50


def test_pro_confidence_scoring_accuracy(mock_pro_tier):
    """Test Pro tier confidence scoring adjusts by severity."""
    from code_scalpel.mcp.server import _unified_sink_detect_sync
    
    result = _unified_sink_detect_sync(
        code=BASIC_SQL_INJECTION,
        language="python",
        min_confidence=0.7,
        tier="pro",
        capabilities=mock_pro_tier
    )
    
    assert result.success
    
    if result.sink_count > 0 and result.confidence_scores:
        # SQL injection should have high confidence
        for score in result.confidence_scores.values():
            # SQL_INJECTION has 0.95 multiplier, should be high
            assert score >= 0.65  # Base 0.7 * 0.95 = 0.665
