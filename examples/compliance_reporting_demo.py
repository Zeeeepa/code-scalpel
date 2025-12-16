"""
Compliance Reporting Demo

Demonstrates the compliance reporting feature for v2.5.0 Guardian.
Shows how to generate comprehensive compliance reports in JSON, HTML, and PDF formats.
"""

# [20251216_FEATURE] Compliance reporting demonstration

import os
from datetime import datetime, timedelta
from pathlib import Path

from code_scalpel.governance import (
    ComplianceReporter,
    AuditLog,
    PolicyEngine,
)


def create_sample_audit_data():
    """Create sample audit log data for demonstration."""
    audit_log = AuditLog()
    base_time = datetime.now()

    print("Creating sample audit data...")

    # Simulate 50 operations over the past week
    for i in range(50):
        audit_log.log_event(
            "OPERATION_ALLOWED",
            {
                "operation": f"code_analysis_{i}",
                "file": f"src/module_{i % 5}.py",
                "agent": "code_analyzer",
            },
            timestamp=base_time - timedelta(hours=i * 3),
        )

    # Simulate 15 policy violations
    for i in range(15):
        severity = ["LOW", "MEDIUM", "HIGH", "CRITICAL"][i % 4]
        audit_log.log_event(
            "POLICY_VIOLATION",
            {
                "policy_name": ["security_policy", "quality_policy", "style_policy"][
                    i % 3
                ],
                "severity": severity,
                "operation_type": "file_edit",
                "details": f"Violation #{i + 1}: {severity} severity issue detected",
            },
            timestamp=base_time - timedelta(hours=i * 5),
        )

    # Simulate override requests
    for i in range(5):
        audit_log.log_event(
            "OVERRIDE_REQUESTED",
            {
                "policy_name": "security_policy",
                "reason": ["urgent_fix", "false_positive", "approved_exception"][i % 3],
                "requester": "senior_engineer",
            },
            timestamp=base_time - timedelta(hours=i * 8),
        )

    # Simulate override approvals
    for i in range(2):
        audit_log.log_event(
            "OVERRIDE_APPROVED",
            {
                "policy_name": "security_policy",
                "approver": "security_lead",
                "reason": "approved_exception",
            },
            timestamp=base_time - timedelta(hours=i * 10),
        )

    # Simulate tamper attempts
    for i in range(3):
        audit_log.log_event(
            "TAMPER_ATTEMPT_DETECTED",
            {
                "details": f"Suspicious activity #{i + 1}",
                "source": "unknown_agent",
                "action_taken": "blocked",
            },
            timestamp=base_time - timedelta(hours=i * 12),
        )

    print(f"✓ Created {len(audit_log.get_events())} audit events")
    return audit_log


def generate_reports(audit_log, policy_engine):
    """Generate reports in all supported formats."""
    print("\nGenerating compliance reports...")

    # Create output directory
    output_dir = Path("compliance_reports")
    output_dir.mkdir(exist_ok=True)

    # Time range: last 7 days
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    time_range = (start_time, end_time)

    # Create reporter
    reporter = ComplianceReporter(audit_log, policy_engine)

    # Generate JSON report
    print("\n1. Generating JSON report...")
    json_report = reporter.generate_report(time_range, format="json")
    json_path = output_dir / "compliance_report.json"
    with open(json_path, "w") as f:
        f.write(json_report)
    print(f"   ✓ JSON report saved to: {json_path}")
    print(f"   Size: {len(json_report):,} bytes")

    # Generate HTML report
    print("\n2. Generating HTML report...")
    html_report = reporter.generate_report(time_range, format="html")
    html_path = output_dir / "compliance_report.html"
    with open(html_path, "w") as f:
        f.write(html_report)
    print(f"   ✓ HTML report saved to: {html_path}")
    print(f"   Size: {len(html_report):,} bytes")
    print(f"   Open in browser: file://{html_path.absolute()}")

    # Generate PDF report
    print("\n3. Generating PDF report...")
    pdf_report = reporter.generate_report(time_range, format="pdf")
    pdf_path = output_dir / "compliance_report.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf_report)
    print(f"   ✓ PDF report saved to: {pdf_path}")
    print(f"   Size: {len(pdf_report):,} bytes")

    # Show summary of report object
    print("\n4. Report summary:")
    report_obj = reporter.generate_report(time_range, format="object")

    print(f"\n   Security Posture:")
    print(f"   - Score: {report_obj.security_posture.score}/100")
    print(f"   - Grade: {report_obj.security_posture.grade}")
    print(f"   - Risk Level: {report_obj.security_posture.risk_level}")

    print(f"\n   Executive Summary:")
    print(f"   - Total Operations: {report_obj.summary.total_operations}")
    print(f"   - Allowed: {report_obj.summary.allowed_operations}")
    print(f"   - Blocked: {report_obj.summary.blocked_operations}")
    print(f"   - Overrides Requested: {report_obj.summary.overrides_requested}")
    print(f"   - Overrides Approved: {report_obj.summary.overrides_approved}")
    print(f"   - Tamper Attempts: {report_obj.summary.tamper_attempts}")

    print(f"\n   Policy Violations:")
    print(f"   - Total: {report_obj.policy_violations.total}")
    for severity, violations in report_obj.policy_violations.by_severity.items():
        print(f"   - {severity}: {len(violations)}")

    print(f"\n   Recommendations: {len(report_obj.recommendations)}")
    for i, rec in enumerate(report_obj.recommendations, 1):
        print(f"   {i}. [{rec.priority}] {rec.title}")

    return report_obj


def main():
    """Main demonstration function."""
    print("=" * 70)
    print("Compliance Reporting Demo - Code Scalpel v2.5.0 Guardian")
    print("=" * 70)

    # Create sample data
    audit_log = create_sample_audit_data()

    # Create policy engine
    policy_engine = PolicyEngine()
    policy_engine.load_policy(
        "security_policy",
        {"severity": "HIGH", "category": "security"},
    )
    policy_engine.load_policy(
        "quality_policy",
        {"severity": "MEDIUM", "category": "quality"},
    )
    policy_engine.load_policy(
        "style_policy",
        {"severity": "LOW", "category": "style"},
    )

    # Generate reports
    report = generate_reports(audit_log, policy_engine)

    print("\n" + "=" * 70)
    print("Demo completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Open compliance_reports/compliance_report.html in your browser")
    print("2. Review compliance_reports/compliance_report.json for API integration")
    print("3. Open compliance_reports/compliance_report.pdf for executive review")


if __name__ == "__main__":
    main()
