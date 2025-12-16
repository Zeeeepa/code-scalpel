"""
Policy Engine Example - v2.5.0 "Guardian"

[20251216_FEATURE] Demonstrates declarative policy enforcement using OPA/Rego

This example shows how to use the Policy Engine to enforce security policies
on code operations, with semantic analysis and human override capabilities.

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
    PolicyEngine,
    Operation,
    SemanticAnalyzer,
    PolicyError,
)


def example_1_basic_policy_evaluation():
    """Example 1: Basic policy evaluation."""
    print("=" * 70)
    print("Example 1: Basic Policy Evaluation")
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
    """Example 3: Human override system."""
    print("\n" + "=" * 70)
    print("Example 3: Human Override System")
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
        # [20240613_BUGFIX] Remove unused variable assignment; call constructor for side effect only
        PolicyEngine("nonexistent.yaml")
        print("✗ Should have failed!")
    except PolicyError as e:
        print(f"✓ Correctly failed CLOSED: {str(e)[:50]}...")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Policy Engine Examples - Code Scalpel v2.5.0 Guardian")
    print("=" * 70)
    
    # Run examples
    example_1_basic_policy_evaluation()
    example_2_semantic_analysis()
    example_3_human_override()
    example_4_fail_closed_demonstration()
    
    print("\n" + "=" * 70)
    print("Examples Complete")
    print("=" * 70)
    print("\nNext Steps:")
    print("  1. Install OPA CLI: https://www.openpolicyagent.org/docs/latest/#running-opa")
    print("  2. Copy .scalpel/policy.yaml.example to .scalpel/policy.yaml")
    print("  3. Customize policies for your organization")
    print("  4. Integrate with your AI agent workflows")


if __name__ == "__main__":
    main()
