"""
Tests for Compliance Reporting functionality.

This test suite validates the compliance reporting feature for v2.5.0 Guardian,
including report generation, analysis, and export in multiple formats.
"""

# [20251216_TEST] Compliance reporting test suite

import pytest
from datetime import datetime, timedelta

from code_scalpel.governance import (
    ComplianceReporter,
    ComplianceReport,
    ReportSummary,
    ViolationAnalysis,
    OverrideAnalysis,
    SecurityPosture,
    Recommendation,
    AuditLog,
    PolicyEngine,
)


class TestAuditLog:
    """Test AuditLog functionality."""

    def test_audit_log_initialization(self):
        """Test that audit log can be initialized."""
        audit_log = AuditLog()
        assert audit_log is not None
        assert len(audit_log.get_events()) == 0

    def test_log_event(self):
        """Test logging events to audit log."""
        audit_log = AuditLog()
        timestamp = datetime.now()

        audit_log.log_event(
            event_type="OPERATION_ALLOWED",
            details={"operation": "test"},
            timestamp=timestamp,
        )

        events = audit_log.get_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "OPERATION_ALLOWED"
        assert events[0]["timestamp"] == timestamp
        assert events[0]["details"]["operation"] == "test"

    def test_get_events_with_time_range(self):
        """Test filtering events by time range."""
        audit_log = AuditLog()
        base_time = datetime.now()

        # Log events at different times
        audit_log.log_event(
            "EVENT1", {"data": "1"}, timestamp=base_time - timedelta(hours=2)
        )
        audit_log.log_event(
            "EVENT2", {"data": "2"}, timestamp=base_time - timedelta(hours=1)
        )
        audit_log.log_event("EVENT3", {"data": "3"}, timestamp=base_time)

        # Query events in the last 90 minutes
        time_range = (base_time - timedelta(minutes=90), base_time)
        filtered_events = audit_log.get_events(time_range)

        assert len(filtered_events) == 2  # EVENT2 and EVENT3
        assert filtered_events[0]["event_type"] == "EVENT2"
        assert filtered_events[1]["event_type"] == "EVENT3"

    def test_clear_events(self):
        """Test clearing all events from audit log."""
        audit_log = AuditLog()
        audit_log.log_event("TEST", {})
        assert len(audit_log.get_events()) == 1

        audit_log.clear()
        assert len(audit_log.get_events()) == 0


class TestPolicyEngine:
    """Test PolicyEngine functionality."""

    def test_policy_engine_initialization(self):
        """Test that policy engine can be initialized."""
        policy_engine = PolicyEngine()
        assert policy_engine is not None
        assert len(policy_engine.get_policies()) == 0

    def test_load_policy(self):
        """Test loading a policy."""
        policy_engine = PolicyEngine()
        policy_engine.load_policy("test_policy", {"rule": "test"})

        assert "test_policy" in policy_engine.get_policies()

    def test_evaluate_operation(self):
        """Test evaluating an operation."""
        policy_engine = PolicyEngine()
        result = policy_engine.evaluate({"action": "test"})

        assert "allowed" in result
        assert isinstance(result["allowed"], bool)


class TestComplianceReporter:
    """Test ComplianceReporter functionality."""

    @pytest.fixture
    def audit_log(self):
        """Create audit log with sample events."""
        log = AuditLog()
        base_time = datetime.now()

        # Add various event types
        for i in range(10):
            log.log_event(
                "OPERATION_ALLOWED",
                {"operation": f"op_{i}"},
                timestamp=base_time - timedelta(minutes=i),
            )

        for i in range(5):
            log.log_event(
                "POLICY_VIOLATION",
                {
                    "policy_name": "test_policy",
                    "severity": "HIGH",
                    "operation_type": "file_edit",
                },
                timestamp=base_time - timedelta(minutes=i + 10),
            )

        for i in range(2):
            log.log_event(
                "OVERRIDE_REQUESTED",
                {"policy_name": "test_policy", "reason": "urgent_fix"},
                timestamp=base_time - timedelta(minutes=i + 20),
            )

        log.log_event(
            "OVERRIDE_APPROVED",
            {"policy_name": "test_policy"},
            timestamp=base_time - timedelta(minutes=25),
        )

        log.log_event(
            "TAMPER_ATTEMPT_DETECTED",
            {"details": "suspicious_activity"},
            timestamp=base_time - timedelta(minutes=30),
        )

        return log

    @pytest.fixture
    def policy_engine(self):
        """Create policy engine."""
        engine = PolicyEngine()
        engine.load_policy("test_policy", {"severity": "HIGH"})
        return engine

    @pytest.fixture
    def reporter(self, audit_log, policy_engine):
        """Create compliance reporter."""
        return ComplianceReporter(audit_log, policy_engine)

    def test_reporter_initialization(self, audit_log, policy_engine):
        """Test that reporter can be initialized."""
        reporter = ComplianceReporter(audit_log, policy_engine)
        assert reporter is not None
        assert reporter.audit_log == audit_log
        assert reporter.policy_engine == policy_engine

    def test_generate_report_basic(self, reporter):
        """Test basic report generation."""
        time_range = (
            datetime.now() - timedelta(hours=1),
            datetime.now(),
        )

        report = reporter.generate_report(time_range, format="object")

        assert isinstance(report, ComplianceReport)
        assert report.generated_at is not None
        assert report.time_range == time_range
        assert isinstance(report.summary, ReportSummary)
        assert isinstance(report.policy_violations, ViolationAnalysis)
        assert isinstance(report.override_analysis, OverrideAnalysis)
        assert isinstance(report.security_posture, SecurityPosture)
        assert isinstance(report.recommendations, list)

    def test_summary_generation(self, reporter):
        """Test executive summary generation."""
        time_range = (datetime.now() - timedelta(hours=1), datetime.now())
        report = reporter.generate_report(time_range, format="object")

        summary = report.summary
        assert summary.total_operations == 10  # 10 allowed operations
        assert summary.blocked_operations == 5  # 5 violations
        assert summary.allowed_operations == 10
        assert summary.overrides_requested == 2
        assert summary.overrides_approved == 1
        assert summary.tamper_attempts == 1
        assert len(summary.most_violated_policies) > 0

    def test_violation_analysis(self, reporter):
        """Test policy violation analysis."""
        time_range = (datetime.now() - timedelta(hours=1), datetime.now())
        report = reporter.generate_report(time_range, format="object")

        violations = report.policy_violations
        assert violations.total == 5
        assert "HIGH" in violations.by_severity
        assert len(violations.by_severity["HIGH"]) == 5
        assert "test_policy" in violations.by_policy
        assert len(violations.by_policy["test_policy"]) == 5
        assert "file_edit" in violations.by_operation_type

    def test_override_analysis(self, reporter):
        """Test override analysis."""
        time_range = (datetime.now() - timedelta(hours=1), datetime.now())
        report = reporter.generate_report(time_range, format="object")

        overrides = report.override_analysis
        assert overrides.total_requested == 2
        assert overrides.total_approved == 1
        assert overrides.total_denied == 0
        assert overrides.approval_rate == 0.5  # 1/2
        assert "test_policy" in overrides.by_policy
        assert "urgent_fix" in overrides.by_reason

    def test_security_posture_assessment(self, reporter):
        """Test security posture assessment."""
        time_range = (datetime.now() - timedelta(hours=1), datetime.now())
        report = reporter.generate_report(time_range, format="object")

        posture = report.security_posture
        assert 0 <= posture.score <= 100
        assert posture.grade in ["A", "B", "C", "D", "F"]
        assert posture.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        assert len(posture.strengths) > 0
        assert isinstance(posture.weaknesses, list)

    def test_score_to_grade_conversion(self, reporter):
        """Test security score to grade conversion."""
        assert reporter._score_to_grade(95) == "A"
        assert reporter._score_to_grade(85) == "B"
        assert reporter._score_to_grade(75) == "C"
        assert reporter._score_to_grade(65) == "D"
        assert reporter._score_to_grade(55) == "F"

    def test_risk_level_assessment(self, reporter):
        """Test risk level assessment based on score."""
        assert reporter._assess_risk_level(90) == "LOW"
        assert reporter._assess_risk_level(70) == "MEDIUM"
        assert reporter._assess_risk_level(50) == "HIGH"
        assert reporter._assess_risk_level(30) == "CRITICAL"

    def test_recommendation_generation(self, reporter):
        """Test actionable recommendation generation."""
        time_range = (datetime.now() - timedelta(hours=1), datetime.now())
        report = reporter.generate_report(time_range, format="object")

        recommendations = report.recommendations
        assert isinstance(recommendations, list)

        # Check recommendation structure if any exist
        if recommendations:
            rec = recommendations[0]
            assert isinstance(rec, Recommendation)
            assert rec.priority in ["HIGH", "MEDIUM", "LOW"]
            assert rec.category != ""
            assert rec.title != ""
            assert rec.description != ""
            assert rec.action != ""

    def test_json_export(self, reporter):
        """Test JSON report export."""
        time_range = (datetime.now() - timedelta(hours=1), datetime.now())
        json_report = reporter.generate_report(time_range, format="json")

        assert isinstance(json_report, str)
        assert "generated_at" in json_report
        assert "time_range" in json_report
        assert "summary" in json_report
        assert "violations" in json_report
        assert "security_posture" in json_report
        assert "recommendations" in json_report

        # Validate JSON is parseable
        import json

        parsed = json.loads(json_report)
        assert "generated_at" in parsed
        assert "summary" in parsed

    def test_html_export(self, reporter):
        """Test HTML report export."""
        time_range = (datetime.now() - timedelta(hours=1), datetime.now())
        html_report = reporter.generate_report(time_range, format="html")

        assert isinstance(html_report, str)
        assert "<!DOCTYPE html>" in html_report
        assert "<title>Compliance Report" in html_report
        assert "Security Posture" in html_report
        assert "Executive Summary" in html_report
        assert "Policy Violations" in html_report
        assert "Recommendations" in html_report

    def test_pdf_export(self, reporter):
        """Test PDF report export."""
        # [20251216_BUGFIX] Skip test if reportlab is not installed
        try:
            import reportlab
        except ImportError:
            pytest.skip("reportlab package not installed")
        
        time_range = (datetime.now() - timedelta(hours=1), datetime.now())
        pdf_report = reporter.generate_report(time_range, format="pdf")

        assert isinstance(pdf_report, bytes)
        # PDF should have reasonable size
        assert len(pdf_report) > 100

    def test_empty_audit_log(self):
        """Test report generation with empty audit log."""
        empty_log = AuditLog()
        engine = PolicyEngine()
        reporter = ComplianceReporter(empty_log, engine)

        time_range = (datetime.now() - timedelta(hours=1), datetime.now())
        report = reporter.generate_report(time_range, format="object")

        assert report.summary.total_operations == 0
        assert report.summary.blocked_operations == 0
        assert report.policy_violations.total == 0
        assert report.security_posture.score == 100  # Perfect score with no operations

    def test_high_override_rate_recommendation(self):
        """Test that high override rate generates recommendation."""
        log = AuditLog()
        base_time = datetime.now()

        # Create scenario with high override rate
        for i in range(10):
            log.log_event(
                "POLICY_VIOLATION",
                {"policy_name": "strict_policy", "severity": "MEDIUM"},
                timestamp=base_time - timedelta(minutes=i),
            )

        for i in range(4):  # 40% override rate
            log.log_event(
                "OVERRIDE_APPROVED",
                {"policy_name": "strict_policy"},
                timestamp=base_time - timedelta(minutes=i + 10),
            )

        engine = PolicyEngine()
        reporter = ComplianceReporter(log, engine)

        time_range = (base_time - timedelta(hours=1), base_time)
        report = reporter.generate_report(time_range, format="object")

        # Should have recommendation about high override rate
        rec_titles = [r.title for r in report.recommendations]
        assert any("override rate" in title.lower() for title in rec_titles)

    def test_frequently_violated_policy_recommendation(self):
        """Test that frequently violated policies generate recommendations."""
        log = AuditLog()
        base_time = datetime.now()

        # Create 15 violations of the same policy (> 10 threshold)
        for i in range(15):
            log.log_event(
                "POLICY_VIOLATION",
                {"policy_name": "frequent_policy", "severity": "LOW"},
                timestamp=base_time - timedelta(minutes=i),
            )

        engine = PolicyEngine()
        reporter = ComplianceReporter(log, engine)

        time_range = (base_time - timedelta(hours=1), base_time)
        report = reporter.generate_report(time_range, format="object")

        # Should have recommendation about frequently violated policy
        rec_titles = [r.title for r in report.recommendations]
        assert any("frequent_policy" in title for title in rec_titles)

    def test_critical_violations_identified(self):
        """Test that critical violations are properly identified."""
        log = AuditLog()
        base_time = datetime.now()

        # Add critical violations
        for i in range(3):
            log.log_event(
                "POLICY_VIOLATION",
                {
                    "policy_name": "security_policy",
                    "severity": "CRITICAL",
                    "operation_type": "security_bypass",
                },
                timestamp=base_time - timedelta(minutes=i),
            )

        engine = PolicyEngine()
        reporter = ComplianceReporter(log, engine)

        time_range = (base_time - timedelta(hours=1), base_time)
        report = reporter.generate_report(time_range, format="object")

        violations = report.policy_violations
        assert len(violations.critical_violations) == 3
        assert "CRITICAL" in violations.by_severity

    def test_multiple_policies_ranking(self):
        """Test ranking of multiple policies by violation count."""
        log = AuditLog()
        base_time = datetime.now()

        # Policy A: 5 violations
        for i in range(5):
            log.log_event(
                "POLICY_VIOLATION",
                {"policy_name": "policy_a", "severity": "MEDIUM"},
                timestamp=base_time - timedelta(minutes=i),
            )

        # Policy B: 10 violations
        for i in range(10):
            log.log_event(
                "POLICY_VIOLATION",
                {"policy_name": "policy_b", "severity": "LOW"},
                timestamp=base_time - timedelta(minutes=i + 10),
            )

        # Policy C: 3 violations
        for i in range(3):
            log.log_event(
                "POLICY_VIOLATION",
                {"policy_name": "policy_c", "severity": "HIGH"},
                timestamp=base_time - timedelta(minutes=i + 20),
            )

        engine = PolicyEngine()
        reporter = ComplianceReporter(log, engine)

        time_range = (base_time - timedelta(hours=1), base_time)
        report = reporter.generate_report(time_range, format="object")

        # Check ranking
        ranked_policies = report.summary.most_violated_policies
        assert len(ranked_policies) == 3
        # Should be sorted by count (descending)
        assert ranked_policies[0][0] == "policy_b"  # 10 violations
        assert ranked_policies[0][1] == 10
        assert ranked_policies[1][0] == "policy_a"  # 5 violations
        assert ranked_policies[1][1] == 5
        assert ranked_policies[2][0] == "policy_c"  # 3 violations
        assert ranked_policies[2][1] == 3

    def test_strengths_identified(self):
        """Test that security strengths are identified."""
        log = AuditLog()
        base_time = datetime.now()

        # Add events that show strengths
        log.log_event(
            "POLICY_VIOLATION",
            {"policy_name": "test", "severity": "HIGH"},
            timestamp=base_time,
        )
        log.log_event(
            "TAMPER_ATTEMPT_DETECTED", {"details": "test"}, timestamp=base_time
        )
        log.log_event("OPERATION_ALLOWED", {"op": "test"}, timestamp=base_time)

        engine = PolicyEngine()
        reporter = ComplianceReporter(log, engine)

        time_range = (base_time - timedelta(hours=1), base_time + timedelta(minutes=1))
        report = reporter.generate_report(time_range, format="object")

        strengths = report.security_posture.strengths
        assert len(strengths) > 0
        # Should identify at least one strength
        assert any("policy enforcement" in s.lower() for s in strengths)

    def test_weaknesses_identified(self):
        """Test that security weaknesses are identified."""
        log = AuditLog()
        base_time = datetime.now()

        # Create scenario with weaknesses
        # Add critical violations
        for i in range(2):
            log.log_event(
                "POLICY_VIOLATION",
                {"policy_name": "test", "severity": "CRITICAL"},
                timestamp=base_time - timedelta(minutes=i),
            )

        engine = PolicyEngine()
        reporter = ComplianceReporter(log, engine)

        time_range = (base_time - timedelta(hours=1), base_time)
        report = reporter.generate_report(time_range, format="object")

        weaknesses = report.security_posture.weaknesses
        assert len(weaknesses) > 0
        # Should identify critical violations as weakness
        assert any("critical" in w.lower() for w in weaknesses)


class TestReportDataModels:
    """Test report data model creation and serialization."""

    def test_recommendation_creation(self):
        """Test Recommendation dataclass creation."""
        rec = Recommendation(
            priority="HIGH",
            category="Policy Tuning",
            title="Test Recommendation",
            description="Test description",
            action="Test action",
        )

        assert rec.priority == "HIGH"
        assert rec.category == "Policy Tuning"
        assert rec.title == "Test Recommendation"
        assert rec.description == "Test description"
        assert rec.action == "Test action"

    def test_security_posture_creation(self):
        """Test SecurityPosture dataclass creation."""
        posture = SecurityPosture(
            score=85,
            grade="B",
            strengths=["Strength 1"],
            weaknesses=["Weakness 1"],
            risk_level="MEDIUM",
        )

        assert posture.score == 85
        assert posture.grade == "B"
        assert len(posture.strengths) == 1
        assert len(posture.weaknesses) == 1
        assert posture.risk_level == "MEDIUM"

    def test_violation_analysis_creation(self):
        """Test ViolationAnalysis dataclass creation."""
        analysis = ViolationAnalysis(
            total=10,
            by_severity={"HIGH": []},
            by_policy={"test_policy": []},
            by_operation_type={"edit": []},
            critical_violations=[],
        )

        assert analysis.total == 10
        assert "HIGH" in analysis.by_severity
        assert "test_policy" in analysis.by_policy

    def test_override_analysis_creation(self):
        """Test OverrideAnalysis dataclass creation."""
        analysis = OverrideAnalysis(
            total_requested=10,
            total_approved=7,
            total_denied=3,
            approval_rate=0.7,
            by_policy={},
            by_reason={},
        )

        assert analysis.total_requested == 10
        assert analysis.total_approved == 7
        assert analysis.approval_rate == 0.7

    def test_report_summary_creation(self):
        """Test ReportSummary dataclass creation."""
        summary = ReportSummary(
            total_operations=100,
            blocked_operations=10,
            allowed_operations=90,
            overrides_requested=5,
            overrides_approved=3,
            tamper_attempts=1,
            most_violated_policies=[("policy_a", 5)],
        )

        assert summary.total_operations == 100
        assert summary.blocked_operations == 10
        assert summary.allowed_operations == 90
        assert len(summary.most_violated_policies) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
