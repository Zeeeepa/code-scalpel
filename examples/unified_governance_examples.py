"""
Unified Governance Examples - Complete Integration of Policy + Budget + Semantic Analysis.

[20251221_FEATURE] v3.1.0 - Comprehensive governance examples

This file demonstrates the complete unified governance system integrating:
1. PolicyEngine (OPA/Rego declarative policies)
2. ChangeBudget (quantitative constraints)
3. SemanticAnalyzer (security pattern detection)
4. ComplianceReporter (metrics and audit)

Key Capabilities:
- Single evaluation call checks all constraints
- Combined violation reporting
- Role-based policy hierarchy (developer, reviewer, architect)
- Semantic security analysis (SQL, XSS, command injection, etc.)
- Comprehensive audit trail
- Human override workflows with justification

Usage Pattern:
    1. Initialize UnifiedGovernance with config directory
    2. Create Operation or dict with code details
    3. Evaluate with optional GovernanceContext
    4. Handle decision (allow/deny with violations)
    5. Request override if needed with justification
    6. Track metrics in compliance reports
"""

from code_scalpel.governance import (
    UnifiedGovernance,
    GovernanceContext,
)
from code_scalpel.governance.change_budget import (
    Operation as BudgetOperation,
    FileChange,
)


# ==============================================================================
# Example 1: Preventing SQL Injection
# ==============================================================================


def example_sql_injection_prevention():
    """
    Demonstrate SQL injection detection via semantic analysis.

    The governance system detects SQL operations without parameterization
    and blocks them automatically.
    """
    gov = UnifiedGovernance(".code-scalpel")

    # Vulnerable code: SQL without parameterization
    vulnerable_operation = {
        "type": "code_edit",
        "code": """
    def get_user(user_id):
        query = "SELECT * FROM users WHERE id=" + user_id
        cursor.execute(query)
        return cursor.fetchone()
    """,
        "language": "python",
        "file_path": "app.py",
    }

    # Evaluate against governance policies
    decision = gov.evaluate(vulnerable_operation)

    print("=== SQL Injection Prevention ===")
    print(f"Decision: {'ALLOWED' if decision.allowed else 'DENIED'}")
    print(f"Reason: {decision.reason}")

    for violation in decision.violations:
        print(f"  - [{violation.source.value}] {violation.rule}: {violation.message}")

    # Expected output:
    # Decision: DENIED
    # Reason: Denied - 1 CRITICAL violation(s) detected
    #   - [semantic] sql_injection_risk: SQL operation detected without parameterization


# ==============================================================================
# Example 2: Allowing Parameterized SQL
# ==============================================================================


def example_secure_sql():
    """
    Demonstrate that parameterized SQL is allowed.

    When SQL is properly parameterized, it passes governance checks.
    """
    gov = UnifiedGovernance(".code-scalpel")

    # Secure code: SQL with parameterization
    secure_operation = {
        "type": "code_edit",
        "code": """
    def get_user(user_id):
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    """,
        "language": "python",
        "file_path": "app.py",
    }

    decision = gov.evaluate(secure_operation)

    print("\n=== Secure Parameterized SQL ===")
    print(f"Decision: {'ALLOWED' if decision.allowed else 'DENIED'}")
    print(f"Reason: {decision.reason}")

    # Should have no SQL injection violations
    sql_violations = [v for v in decision.violations if "sql_injection" in v.rule]
    print(f"SQL injection violations: {len(sql_violations)}")

    # Expected output:
    # Decision: ALLOWED
    # Reason: Allowed - No violations (role: developer)
    # SQL injection violations: 0


# ==============================================================================
# Example 3: XSS Prevention in JavaScript
# ==============================================================================


def example_xss_prevention():
    """
    Demonstrate XSS (Cross-Site Scripting) detection.

    The system detects unsafe DOM manipulation patterns.
    """
    gov = UnifiedGovernance(".code-scalpel")

    # Vulnerable code: Unsafe DOM manipulation
    vulnerable_js = {
        "type": "code_edit",
        "code": """
    function setUserContent(userInput) {
        document.getElementById('profile').innerHTML = userInput;
    }
    """,
        "language": "javascript",
        "file_path": "profile.js",
    }

    decision = gov.evaluate(vulnerable_js)

    print("\n=== XSS Prevention ===")
    print(f"Decision: {'ALLOWED' if decision.allowed else 'DENIED'}")
    print(f"Reason: {decision.reason}")

    xss_violations = [v for v in decision.violations if v.rule == "xss_risk"]
    print(f"XSS violations detected: {len(xss_violations)}")

    # Expected output:
    # Decision: DENIED
    # Reason: Denied - 1 CRITICAL violation(s) detected
    # XSS violations detected: 1


# ==============================================================================
# Example 4: Command Injection Prevention
# ==============================================================================


def example_command_injection_prevention():
    """
    Demonstrate command injection detection.

    The system blocks shell command execution with user input.
    """
    gov = UnifiedGovernance(".code-scalpel")

    # Vulnerable code: Shell command with user input
    vulnerable_cmd = {
        "type": "code_edit",
        "code": """
    import os
    def search_logs(query):
        os.system(f"grep '{query}' /var/log/app.log")
    """,
        "language": "python",
        "file_path": "log_handler.py",
    }

    decision = gov.evaluate(vulnerable_cmd)

    print("\n=== Command Injection Prevention ===")
    print(f"Decision: {'ALLOWED' if decision.allowed else 'DENIED'}")

    cmd_violations = [v for v in decision.violations if "command_injection" in v.rule]
    print(f"Command injection violations: {len(cmd_violations)}")


# ==============================================================================
# Example 5: Role-Based Governance (Developer vs Reviewer)
# ==============================================================================


def example_role_based_governance():
    """
    Demonstrate role-aware governance decisions.

    Different roles (developer, reviewer, architect) can have different constraints.
    """
    gov = UnifiedGovernance(".code-scalpel")

    operation = {
        "type": "code_edit",
        "code": "x = y + z",
        "language": "python",
        "file_path": "math.py",
    }

    # Evaluate as developer
    dev_context = GovernanceContext(
        user_role="developer",
        team="backend",
        environment="development",
    )

    dev_decision = gov.evaluate(operation, dev_context)

    print("\n=== Role-Based Governance ===")
    print(f"Developer decision: {'ALLOWED' if dev_decision.allowed else 'DENIED'}")

    # Evaluate as reviewer (stricter constraints)
    reviewer_context = GovernanceContext(
        user_role="reviewer",
        team="backend",
        environment="staging",
    )

    reviewer_decision = gov.evaluate(operation, reviewer_context)
    print(f"Reviewer decision: {'ALLOWED' if reviewer_decision.allowed else 'DENIED'}")

    # Check audit trail
    history = gov.get_decision_history(limit=2)
    print(f"\nDecisions logged: {len(history)}")
    for decision_log in history:
        print(
            f"  - Role: {decision_log['user_role']}, Allowed: {decision_log['allowed']}"
        )


# ==============================================================================
# Example 6: Change Budget Enforcement
# ==============================================================================


def example_change_budget_enforcement():
    """
    Demonstrate quantitative change budget constraints.

    The system limits the scope of changes to prevent runaway modifications.
    """
    gov = UnifiedGovernance(".code-scalpel")

    # Create a large operation (exceeds budget)
    large_operation = BudgetOperation(
        changes=[
            FileChange(
                file_path="core/module.py",
                added_lines=[
                    f"line {i}" for i in range(200)
                ],  # 200 lines exceeds budget
            ),
        ],
    )

    decision = gov.evaluate(large_operation)

    print("\n=== Change Budget Enforcement ===")
    print(f"Decision: {'ALLOWED' if decision.allowed else 'DENIED'}")
    print(f"Reason: {decision.reason}")

    budget_violations = decision.budget_violations
    print(f"Budget violations: {len(budget_violations)}")

    for violation in budget_violations:
        print(f"  - {violation.rule}: {violation.message}")


# ==============================================================================
# Example 7: Combined Semantic + Budget Constraints
# ==============================================================================


def example_combined_constraints():
    """
    Demonstrate combined semantic security + budget constraints.

    Violations can come from multiple sources simultaneously.
    """
    gov = UnifiedGovernance(".code-scalpel")

    # Operation with both SQL injection AND exceeds budget
    combined_operation = BudgetOperation(
        description="Add user search with logging",
        changes=[
            FileChange(
                file_path="search.py",
                added_lines=[
                    "def search_users(query):",
                    "    cursor.execute('SELECT * FROM users WHERE name=' + query)",
                    "    log.info(f'Searched for {query}')",
                ]
                + ["x = 1"] * 100,  # Exceeds line limits
            ),
        ],
    )

    decision = gov.evaluate(combined_operation)

    print("\n=== Combined Constraints ===")
    print(f"Decision: {'ALLOWED' if decision.allowed else 'DENIED'}")
    print(f"Total violations: {len(decision.violations)}")

    print("\nViolation breakdown:")
    print(f"  - Semantic: {len(decision.semantic_violations)}")
    print(f"  - Budget: {len(decision.budget_violations)}")
    print(f"  - Policy: {len(decision.policy_violations)}")


# ==============================================================================
# Example 8: Override Workflow
# ==============================================================================


def example_override_workflow():
    """
    Demonstrate human override workflow for denied operations.

    Developers can request override with justification and human approval.
    """
    gov = UnifiedGovernance(".code-scalpel")

    vulnerable_operation = {
        "type": "code_edit",
        "code": "cursor.execute('SELECT * FROM users WHERE id=' + user_id)",
        "language": "python",
    }

    decision = gov.evaluate(vulnerable_operation)

    print("\n=== Override Workflow ===")
    print(f"Initial decision: {'ALLOWED' if decision.allowed else 'DENIED'}")

    if not decision.allowed:
        # Request override from human reviewer
        override_decision = gov.request_override(
            operation=vulnerable_operation,
            decision=decision,
            justification="Legacy system requires dynamic query building for backward compatibility",
            human_code="REVIEWER123456",
        )

        print(
            f"Override decision: {'APPROVED' if override_decision.approved else 'DENIED'}"
        )
        if override_decision.approved:
            print(f"Override ID: {override_decision.override_id}")
            print(f"Expires: {override_decision.expires_at}")


# ==============================================================================
# Example 9: Comprehensive Violation Summary
# ==============================================================================


def example_violation_summary():
    """
    Demonstrate comprehensive violation reporting.

    Get detailed summary of all violations for developer feedback.
    """
    gov = UnifiedGovernance(".code-scalpel")

    operation = {
        "type": "code_edit",
        "code": """
    import os
    def handle_upload(user_file):
        os.system(f"unzip {user_file}")
        with open(user_file.replace('../', '')) as f:
            data = eval(f.read())
    """,
        "language": "python",
    }

    decision = gov.evaluate(operation)

    print("\n=== Comprehensive Violation Report ===")
    summary = decision.get_summary()
    print(summary)


# ==============================================================================
# Example 10: Metrics and Compliance Tracking
# ==============================================================================


def example_metrics_tracking():
    """
    Demonstrate governance metrics and compliance tracking.

    Track violations over time for compliance reports.
    """
    gov = UnifiedGovernance(".code-scalpel")

    # Simulate multiple operations
    operations = [
        {
            "type": "code_edit",
            "code": "x = y + z",  # Clean
            "language": "python",
        },
        {
            "type": "code_edit",
            "code": "cursor.execute('SELECT * FROM users WHERE id=' + user_id)",  # Violation
            "language": "python",
        },
        {
            "type": "code_edit",
            "code": "data = json.loads(user_input)  # Secure",  # Clean
            "language": "python",
        },
    ]

    contexts = [
        GovernanceContext(user_role="developer", team="backend"),
        GovernanceContext(user_role="developer", team="frontend"),
        GovernanceContext(user_role="reviewer", team="security"),
    ]

    for op, ctx in zip(operations, contexts):
        gov.evaluate(op, ctx)

    # Get decision history
    history = gov.get_decision_history()

    print("\n=== Governance Metrics ===")
    print(f"Total evaluations: {len(history)}")

    allowed = sum(1 for d in history if d["allowed"])
    denied = len(history) - allowed

    print(f"Allowed: {allowed}")
    print(f"Denied: {denied}")

    # Violations by source
    total_policy = sum(d["sources"]["policy"] for d in history)
    total_budget = sum(d["sources"]["budget"] for d in history)
    total_semantic = sum(d["sources"]["semantic"] for d in history)

    print("\nViolations by source:")
    print(f"  - Policy: {total_policy}")
    print(f"  - Budget: {total_budget}")
    print(f"  - Semantic: {total_semantic}")


# ==============================================================================
# Main Entry Point
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("UNIFIED GOVERNANCE SYSTEM - COMPREHENSIVE EXAMPLES")
    print("=" * 80)

    try:
        example_sql_injection_prevention()
        example_secure_sql()
        example_xss_prevention()
        example_command_injection_prevention()
        example_role_based_governance()
        example_change_budget_enforcement()
        example_combined_constraints()
        example_violation_summary()
        example_metrics_tracking()

        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback

        traceback.print_exc()
