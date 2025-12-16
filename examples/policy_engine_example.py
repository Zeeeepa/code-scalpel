"""
Policy Engine Example - v2.5.0 "Guardian"

[20251216_FEATURE] Demonstrates complete policy enforcement for AI agents:
- Part 1: PolicyEngine - OPA/Rego declarative policies
- Part 2: SemanticAnalyzer - SQL injection detection
- Part 3: TamperResistance - Tamper-resistant controls
- Part 4: AuditLog - HMAC-signed audit trail

Prerequisites:
    - Install OPA CLI: https://www.openpolicyagent.org/docs/latest/#running-opa
    - Create .scalpel/policy.yaml in your project

Usage:
    python examples/policy_engine_example.py
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from code_scalpel.policy_engine import (
    # Policy Engine core
    PolicyEngine,
    Operation,
    SemanticAnalyzer,
    PolicyError,
    PolicyDecision,
    # Tamper Resistance
    TamperResistance,
    AuditLog,
    TamperDetectedError,
    PolicyModificationError,
)


# =============================================================================
# Part 1: PolicyEngine - OPA/Rego Integration
# =============================================================================

def example_1_basic_policy_evaluation():
    """Example 1: Basic policy evaluation with OPA/Rego."""
    print("=" * 70)
    print("Example 1: Basic Policy Evaluation (OPA/Rego)")
    print("=" * 70)
    
    try:
        # Initialize policy engine
        # Note: This requires .scalpel/policy.yaml and OPA CLI installed
        engine = PolicyEngine(".scalpel/policy.yaml")
        print(f"✓ Loaded {len(engine.policies)} policies")
        
        # Example: Safe code (should pass)
        print("\n--- Testing Safe Code ---")
        safe_operation = Operation(
            type="code_edit",
            code='print("Hello, World!")',
            language="python",
            file_path="app.py"
        )
        
        decision = engine.evaluate(safe_operation)
        print(f"Decision: {'ALLOWED' if decision.allowed else 'DENIED'}")
        print(f"Reason: {decision.reason}")
        
        # Example: Dangerous code (should fail)
        print("\n--- Testing Dangerous Code ---")
        dangerous_operation = Operation(
            type="code_edit",
            code='query = "SELECT * FROM users WHERE id=" + user_id\ncursor.execute(query)',
            language="python",
            file_path="app.py"
        )
        
        decision = engine.evaluate(dangerous_operation)
        print(f"Decision: {'ALLOWED' if decision.allowed else 'DENIED'}")
        print(f"Reason: {decision.reason}")
        
        if decision.violations:
            print("\nViolations:")
            for v in decision.violations:
                print(f"  - [{v.severity}] {v.policy_name}: {v.message}")
        
    except PolicyError as e:
        print(f"✗ Policy Engine Error: {e}")
        print("\nTip: Ensure OPA CLI is installed and .scalpel/policy.yaml exists")
        print("     See: https://www.openpolicyagent.org/docs/latest/#running-opa")


def example_2_semantic_analysis():
    """Example 2: Semantic analysis without OPA."""
    print("\n" + "=" * 70)
    print("Example 2: Semantic Analysis (No OPA Required)")
    print("=" * 70)
    
    analyzer = SemanticAnalyzer()
    
    # Test various SQL injection patterns
    test_cases = [
        ("String concatenation", 'query = "SELECT * FROM users WHERE id=" + user_id'),
        ("F-string", 'query = f"SELECT * FROM {table} WHERE id={user_id}"'),
        ("String format", 'query = "SELECT * FROM users WHERE id={}".format(user_id)'),
        ("% formatting", 'query = "SELECT * FROM users WHERE id=%s" % user_id'),
        ("Safe parameterized", 'cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))'),
    ]
    
    print("\nSQL Injection Detection:")
    for name, code in test_cases:
        has_sql = analyzer.contains_sql_sink(code, "python")
        has_param = analyzer.has_parameterization(code, "python")
        status = "✗ VULNERABLE" if (has_sql and not has_param) else "✓ SAFE"
        print(f"  {status} - {name}")
        if has_sql and not has_param:
            print(f"           SQL detected without parameterization")
    
    # Test Java patterns
    print("\nJava SQL Detection:")
    java_code = """
    StringBuilder query = new StringBuilder();
    query.append("SELECT * FROM users");
    query.append(" WHERE id=");
    query.append(userId);
    """
    has_sql = analyzer.contains_sql_sink(java_code, "java")
    print(f"  {'✗ VULNERABLE' if has_sql else '✓ SAFE'} - StringBuilder pattern")
    
    # Test JavaScript patterns
    print("\nJavaScript SQL Detection:")
    js_code = 'const query = `SELECT * FROM users WHERE id=${userId}`;'
    has_sql = analyzer.contains_sql_sink(js_code, "javascript")
    print(f"  {'✗ VULNERABLE' if has_sql else '✓ SAFE'} - Template literal pattern")


def example_3_human_override():
    """Example 3: Human override system with PolicyEngine."""
    print("\n" + "=" * 70)
    print("Example 3: Human Override System (PolicyEngine)")
    print("=" * 70)
    
    try:
        engine = PolicyEngine(".scalpel/policy.yaml")
        
        # Create a dangerous operation
        operation = Operation(
            type="code_edit",
            code='sql = "DELETE FROM users WHERE id=" + user_id',
            language="python",
            file_path="app.py"
        )
        
        # Evaluate (should be denied)
        decision = engine.evaluate(operation)
        print(f"Initial Decision: {'ALLOWED' if decision.allowed else 'DENIED'}")
        
        if not decision.allowed and decision.requires_override:
            print("\n--- Requesting Human Override ---")
            
            # Request override with justification
            override = engine.request_override(
                operation=operation,
                decision=decision,
                justification="Emergency hotfix for ticket SEC-1234",
                human_code="secure_override_123"
            )
            
            if override.approved:
                print("✓ Override APPROVED")
                print(f"  Override ID: {override.override_id}")
                print(f"  Expires: {override.expires_at}")
                print(f"  Can proceed with operation under supervision")
            else:
                print(f"✗ Override DENIED: {override.reason}")
            
            # Try to reuse the same code (should fail)
            print("\n--- Attempting to Reuse Override Code ---")
            override2 = engine.request_override(
                operation=operation,
                decision=decision,
                justification="Another operation",
                human_code="secure_override_123"  # Same code
            )
            print(f"Result: {override2.reason}")
        
    except PolicyError as e:
        print(f"✗ Policy Engine Error: {e}")


def example_4_fail_closed_demonstration():
    """Example 4: Demonstrate fail CLOSED security model."""
    print("\n" + "=" * 70)
    print("Example 4: Fail CLOSED Security Model")
    print("=" * 70)
    
    print("\nThe Policy Engine fails CLOSED on all errors:")
    print("  ✓ Missing policy file → DENY ALL")
    print("  ✓ Invalid YAML → DENY ALL")
    print("  ✓ Invalid Rego → DENY ALL")
    print("  ✓ OPA not found → DENY ALL")
    print("  ✓ Evaluation error → DENY operation")
    
    print("\nTesting with nonexistent policy file:")
    try:
        PolicyEngine("nonexistent.yaml")
        print("✗ Should have failed!")
    except PolicyError as e:
        print(f"✓ Correctly failed CLOSED: {str(e)[:50]}...")


# =============================================================================
# Part 2: TamperResistance - Tamper-Proof Controls
# =============================================================================

def example_5_tamper_resistance():
    """Example 5: Tamper-resistant policy enforcement."""
    print("\n" + "=" * 70)
    print("Example 5: Tamper-Resistant Policy Enforcement")
    print("=" * 70)

    # Create a temporary policy file
    policy_path = Path(".scalpel/policy.yaml")
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Only write if it doesn't exist or is empty
    if not policy_path.exists() or policy_path.stat().st_size == 0:
        policy_path.write_text("# Policy v1.0\nmax_complexity: 10\n")

    try:
        # Initialize tamper resistance
        tr = TamperResistance(policy_path=str(policy_path))
        print(f"✓ Policy file locked: {policy_path}")

        # Verify policy integrity
        if tr.verify_policy_integrity():
            print("✓ Policy integrity verified")

        # Try to modify protected policy file (will be blocked)
        tamper_operation = Operation(
            type="file_write",
            file_path=str(policy_path),
        )

        try:
            tr.prevent_policy_modification(tamper_operation)
            print("✗ Policy modification was NOT blocked (should not reach here)")
        except PolicyModificationError as e:
            print(f"✓ Policy modification blocked: {e}")

    except Exception as e:
        print(f"✗ Tamper resistance error: {e}")


def example_6_audit_logging():
    """Example 6: HMAC-signed audit logging."""
    print("\n" + "=" * 70)
    print("Example 6: Tamper-Resistant Audit Logging")
    print("=" * 70)

    # Create audit log
    audit_log = AuditLog(log_path=".scalpel/audit.log")

    # Record security events
    audit_log.record_event(
        event_type="POLICY_CHECK",
        severity="LOW",
        details={"operation": "file_read", "file": "src/main.py"},
    )
    print("✓ Event recorded: POLICY_CHECK")

    audit_log.record_event(
        event_type="POLICY_VIOLATION",
        severity="HIGH",
        details={"operation": "file_delete", "file": "critical_config.yaml"},
    )
    print("✓ Event recorded: POLICY_VIOLATION")

    # Verify log integrity
    if audit_log.verify_integrity():
        print("✓ Audit log integrity verified")

    # Retrieve events
    events = audit_log.get_events(severity="HIGH")
    print(f"✓ Found {len(events)} HIGH severity events")


def example_7_tampering_detection():
    """Example 7: Detecting policy tampering."""
    print("\n" + "=" * 70)
    print("Example 7: Policy Tampering Detection")
    print("=" * 70)

    # Create policy file
    policy_path = Path(".scalpel/policy_test.yaml")
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    policy_path.write_text("# Original policy\nversion: 1.0\n")

    try:
        # Initialize tamper resistance
        tr = TamperResistance(policy_path=str(policy_path))
        original_hash = tr.policy_hash
        print(f"✓ Original policy hash: {original_hash[:16]}...")

        # Make policy writable and tamper with it
        policy_path.chmod(0o644)
        policy_path.write_text("# TAMPERED policy\nversion: 2.0\n")
        print("⚠ Policy file modified externally")

        # Try to verify integrity (should detect tampering)
        try:
            tr.verify_policy_integrity()
            print("✗ Tampering NOT detected (should not reach here)")
        except TamperDetectedError as e:
            print(f"✓ Tampering detected: {e}")

    except Exception as e:
        print(f"Note: {e}")


def example_8_audit_filtering():
    """Example 8: Filtering audit log events."""
    print("\n" + "=" * 70)
    print("Example 8: Audit Log Event Filtering")
    print("=" * 70)

    # Create audit log
    audit_log = AuditLog(log_path=".scalpel/audit_filter.log")

    # Record various events
    events_to_record = [
        ("POLICY_CHECK", "LOW", {"file": "file1.py"}),
        ("POLICY_VIOLATION", "HIGH", {"file": "file2.py"}),
        ("POLICY_CHECK", "LOW", {"file": "file3.py"}),
        ("OVERRIDE_APPROVED", "MEDIUM", {"user": "admin"}),
        ("POLICY_TAMPERING_DETECTED", "CRITICAL", {"hash": "abc123"}),
    ]

    for event_type, severity, details in events_to_record:
        audit_log.record_event(event_type, severity, details)

    print(f"✓ Recorded {len(events_to_record)} events")

    # Filter by event type
    violations = audit_log.get_events(event_type="POLICY_VIOLATION")
    print(f"✓ POLICY_VIOLATION events: {len(violations)}")

    # Filter by severity
    critical_events = audit_log.get_events(severity="CRITICAL")
    print(f"✓ CRITICAL severity events: {len(critical_events)}")

    # Get all events with limit
    recent_events = audit_log.get_events(limit=3)
    print(f"✓ Most recent 3 events retrieved")


# =============================================================================
# Main
# =============================================================================

def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "POLICY ENGINE EXAMPLES - v2.5.0 GUARDIAN" + " " * 17 + "║")
    print("║" + " " * 68 + "║")
    print("║  Part 1: PolicyEngine (OPA/Rego)" + " " * 35 + "║")
    print("║  Part 2: TamperResistance (Tamper-Proof Controls)" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # Part 1: PolicyEngine Examples
    print("─" * 70)
    print("PART 1: PolicyEngine - Declarative Policy Enforcement")
    print("─" * 70)
    
    example_1_basic_policy_evaluation()
    example_2_semantic_analysis()
    example_3_human_override()
    example_4_fail_closed_demonstration()
    
    # Part 2: TamperResistance Examples
    print("\n" + "─" * 70)
    print("PART 2: TamperResistance - Tamper-Proof Controls")
    print("─" * 70)
    
    example_5_tamper_resistance()
    example_6_audit_logging()
    example_7_tampering_detection()
    example_8_audit_filtering()
    
    # Summary
    print("\n" + "=" * 70)
    print("All Examples Complete")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Install OPA CLI: https://www.openpolicyagent.org/docs/latest/#running-opa")
    print("  2. Copy .scalpel/policy.yaml.example to .scalpel/policy.yaml")
    print("  3. Customize policies for your organization")
    print("  4. Integrate with your AI agent workflows")


if __name__ == "__main__":
    main()
