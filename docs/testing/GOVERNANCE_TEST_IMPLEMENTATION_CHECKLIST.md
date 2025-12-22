# Unified Governance Test Implementation Checklist

**Phase 1 - Critical Test Suite Implementation**  
**Target Completion:** 60-80 hours  
**Status:** Ready for implementation

---

## Core Test Classes (50+ tests)

### ✅ TestUnifiedGovernanceEvaluation (15 tests)

Core evaluation logic - unified decision making from policy + budget + semantic

```
[ ] test_evaluate_policy_violation_only
    - Policy engine returns violation
    - Budget permits change
    - Semantic analysis passes
    → Decision.allowed = False, violations include policy violation

[ ] test_evaluate_budget_violation_only
    - Policy passes
    - Budget constraint exceeded
    - Semantic analysis passes
    → Decision.allowed = False, violations include budget violation

[ ] test_evaluate_semantic_violation_only
    - Policy passes
    - Budget permits
    - Semantic analysis detects SQL injection
    → Decision.allowed = False, violations include semantic violation

[ ] test_evaluate_multiple_violations
    - Policy + Budget + Semantic all have violations
    → Decision includes all 3 violation types
    → Violations sorted by severity

[ ] test_evaluate_all_passed
    - Policy: pass
    - Budget: within limits
    - Semantic: no issues
    → Decision.allowed = True
    → reason = "No governance violations detected"

[ ] test_evaluate_aggregates_violations_correctly
    - Multiple violations per source
    → All violations included in decision
    → Total count = sum of all sources

[ ] test_evaluate_violation_severity_ordering
    - Mix of CRITICAL, HIGH, MEDIUM, LOW
    → Violations ordered by severity descending
    → decision.primary_severity = highest

[ ] test_evaluate_with_custom_operation_type
    - code_review operation
    - file_deletion operation
    - database_migration operation
    → Each type handled correctly

[ ] test_evaluate_language_specific_analysis
    - Python code with SQL injection
    - JavaScript with XSS
    - Java with command injection
    → Semantic analysis language-specific

[ ] test_evaluate_creates_decision_metadata
    - Decision includes:
      - timestamp
      - operation_id
      - rule_id
      - decision_version
    → All metadata present and correct

[ ] test_evaluate_includes_remediation_suggestions
    - Violation includes remediation_hint
    → Suggestions are actionable
    → Suggestions are language-specific

[ ] test_evaluate_respects_config_overrides
    - Environment variable: SCALPEL_POLICY_MODE=disabled
    → Policy engine skipped
    → Budget + Semantic still evaluated

[ ] test_evaluate_handles_partial_availability
    - Policy engine unavailable (OPA not installed)
    - Budget available
    - Semantic available
    → Evaluation completes
    → Audit log notes policy engine unavailable

[ ] test_evaluate_fail_closed_on_budget_error
    - Budget calculation throws exception
    → Decision.allowed = False (fail closed)
    → Error recorded in audit log

[ ] test_evaluate_fail_closed_on_semantic_error
    - Semantic analyzer throws exception
    → Decision.allowed = False (fail closed)
    → Error recorded in audit log
```

**File:** `tests/test_unified_governance.py::TestUnifiedGovernanceEvaluation`

### ✅ TestRoleBasedPolicies (8 tests)

Role hierarchy and role-specific constraints

```
[ ] test_developer_role_default_limits
    - Role: "developer"
    → max_lines_per_change = 500
    → max_files_per_change = 10
    → can_modify_critical_paths = False
    → requires_review = True

[ ] test_reviewer_role_higher_limits
    - Role: "reviewer"
    → max_lines_per_change = 1500
    → max_files_per_change = 30
    → can_modify_critical_paths = False
    → requires_review = False

[ ] test_architect_role_unrestricted
    - Role: "architect"
    → max_lines_per_change = unlimited
    → max_files_per_change = unlimited
    → can_modify_critical_paths = True
    → requires_review = False

[ ] test_role_hierarchy_inheritance
    - Custom role: "security_reviewer"
    - Inherits from: "reviewer"
    → Gets reviewer limits + additional policy

[ ] test_role_override_enforcement
    - Role attempts override
    - Override requires architect approval
    → Check override_required logic

[ ] test_role_based_critical_path_restrictions
    - developer role tries critical path modification
    → Blocked regardless of budget
    - architect role tries critical path modification
    → Allowed if semantic analysis passes

[ ] test_role_missing_uses_default
    - Operation with unknown role
    → Falls back to "developer" defaults

[ ] test_role_change_mid_evaluation
    - Role changes during long-running evaluation
    → Uses role at time of operation start
    → Does not switch mid-evaluation
```

**File:** `tests/test_unified_governance.py::TestRoleBasedPolicies`

### ✅ TestSemanticSecurityIntegration (8 tests)

Semantic analyzer integration with unified governance

```
[ ] test_semantic_check_detects_sql_injection
    - Code: cursor.execute(f"SELECT * FROM users WHERE id={uid}")
    - Language: python
    → Violation: SQL Injection (CRITICAL)

[ ] test_semantic_check_detects_xss
    - Code: document.innerHTML = user_input;
    - Language: javascript
    → Violation: XSS (HIGH)

[ ] test_semantic_check_detects_command_injection
    - Code: os.system(f"rm {filename}")
    - Language: python
    → Violation: Command Injection (CRITICAL)

[ ] test_semantic_check_detects_path_traversal
    - Code: open(request.args['file'], 'r')
    - Language: python
    → Violation: Path Traversal (HIGH)

[ ] test_semantic_check_language_specific
    - Same vulnerability, different languages
    - Python: SQL via string format
    - Java: SQL via StringBuilder
    → Both detected with language-specific patterns

[ ] test_semantic_violations_included_in_decision
    - Evaluation includes semantic violations
    → decision.violations includes SemanticViolation
    → Source = ViolationSource.SEMANTIC

[ ] test_semantic_analysis_optional_by_config
    - Config: semantic_analysis_enabled = False
    → Semantic checks skipped
    → Policy + Budget still evaluated

[ ] test_semantic_analysis_error_fails_closed
    - Semantic analyzer crashes
    → Decision.allowed = False
    → Violation reason includes error message
```

**File:** `tests/test_unified_governance.py::TestSemanticSecurityIntegration`

### ✅ TestComplianceReporting (10 tests)

Compliance metrics and reporting

```
[ ] test_generate_compliance_report
    - No operations evaluated yet
    → Report generated successfully
    → All fields populated

[ ] test_report_includes_all_violations
    - 3 operations with violations
    → Report includes all 3
    → Violations grouped by type (policy, budget, semantic)

[ ] test_report_tracks_decision_history
    - 5 operations evaluated
    → Report shows: 3 allowed, 2 denied
    → Metrics: allow_rate = 60%

[ ] test_report_metrics_calculations
    - 100 operations, 80 allowed
    → allow_rate = 80%
    → deny_rate = 20%
    → average_changes_per_operation = X

[ ] test_report_includes_violation_distribution
    - 10 policy violations, 5 budget violations, 8 semantic
    → Report shows distribution
    → Top violations listed

[ ] test_report_export_formats_json
    - Export to JSON format
    → Valid JSON schema
    → All required fields present
    → Date fields are ISO8601

[ ] test_report_export_formats_csv
    - Export to CSV format
    → One row per operation
    → Headers match fields
    → Special characters escaped

[ ] test_report_time_range_filtering
    - Filter by date range
    → Only operations in range included
    → Metrics recalculated

[ ] test_report_includes_remediation_summary
    - Report lists all remediation suggestions
    → Grouped by category
    → Includes implementation count

[ ] test_report_compliance_score
    - Report calculates compliance_score
    - 0-100 scale
    → Higher score = fewer violations
    → Score trend tracked over time
```

**File:** `tests/test_unified_governance.py::TestComplianceReporting`

### ✅ TestPolicyOverrides (10 tests)

Override mechanism and approval workflow

```
[ ] test_policy_override_requires_justification
    - Attempt override without justification
    → Rejected: requires_justification error

[ ] test_policy_override_with_justification
    - Provide justification text
    → Override accepted (if allowed)
    → Creates audit entry

[ ] test_override_creates_audit_entry
    - Issue override
    → Audit log includes:
        - override_timestamp
        - original_decision
        - justification
        - approver (if needed)

[ ] test_override_respects_max_overrides_per_day
    - Config: max_overrides_per_day = 3
    - 3 overrides already issued
    → 4th override rejected

[ ] test_override_blocked_on_critical_path
    - File: src/security/auth.py (critical path)
    - Try to override budget violation
    → Rejected: cannot override critical path

[ ] test_override_approval_required_for_critical
    - Config: critical_override_requires_approval = True
    - Try to override critical path violation
    → Blocked until approved by architect

[ ] test_override_approval_workflow
    - Override requested (needs approval)
    → Approval sent to architect
    → Architect approves
    → Override applied
    → Audit trail shows approver

[ ] test_override_time_expiration
    - Override approved until tomorrow
    - Next evaluation after expiration
    → Override no longer valid
    → Re-evaluation against original constraints

[ ] test_override_scope_limitations
    - Override applies only to specific operation
    - Similar operation next day
    → Override not reused
    → Requires new override

[ ] test_override_metrics_in_compliance_report
    - 5 overrides issued
    - Report shows: override_count = 5
    - Report shows: override_rate = X%
```

**File:** `tests/test_unified_governance.py::TestPolicyOverrides`

### ✅ TestAuditTrail (10 tests)

Comprehensive audit logging and integrity

```
[ ] test_all_decisions_logged
    - 10 operations evaluated
    → 10 entries in audit log
    → Each entry has unique audit_id

[ ] test_audit_trail_immutable
    - Try to modify audit entry after creation
    → Modification blocked or detected
    → Integrity check fails

[ ] test_audit_trail_includes_metadata
    - Audit entry includes:
      - operation_id
      - decision_id
      - timestamp (UTC)
      - user_context (role, workspace, etc)
      - decision_summary

[ ] test_audit_trail_searchable
    - Query audit log by:
      - date range
      - operation_type
      - violation_type
      - decision (allow/deny)
    → Correct entries returned

[ ] test_audit_retention_enforced
    - Config: retention_days = 30
    - Run cleanup
    - Entries older than 30 days deleted
    → Newer entries retained

[ ] test_audit_export_integrity
    - Export audit log
    → All entries present
    → Chronological order
    → Signatures valid (if cryptographic)

[ ] test_audit_includes_error_conditions
    - Operation with error in semantic analysis
    → Audit log records error details
    → Error not hidden

[ ] test_audit_trail_chain_of_custody
    - Policy change at 10am
    - Evaluation at 11am uses new policy
    → Audit log shows both events
    → Clear causality chain

[ ] test_audit_includes_override_decisions
    - Override issued
    - Evaluation uses override
    → Both override and evaluation logged
    → Linked in audit trail

[ ] test_audit_export_tamper_detection
    - Export audit log
    - Manually modify exported file
    - Re-import modified file
    → Tamper detection fails (or detects change)
```

**File:** `tests/test_unified_governance.py::TestAuditTrail`

### ✅ TestErrorHandling (8 tests)

Fail-closed error handling across all subsystems

```
[ ] test_policy_engine_error_fails_closed
    - OPA syntax error in policy
    → Decision.allowed = False
    → reason includes error details

[ ] test_budget_calculation_error_fails_closed
    - Negative line count in operation
    → Decision.allowed = False
    → Fails closed, not ignored

[ ] test_semantic_analysis_error_fails_closed
    - Language parser crashes
    → Decision.allowed = False
    → Does not silently skip semantic check

[ ] test_config_load_error_fails_closed
    - Config file corrupted
    → UnifiedGovernance initialization fails
    → Default deny policy applied

[ ] test_partial_failures_handled_gracefully
    - Policy engine error
    - Budget calculation works
    - Semantic analysis works
    → Evaluation completes
    → Policy engine marked unavailable in log
    → Decision based on budget + semantic

[ ] test_timeout_handling
    - Policy evaluation takes > 30s
    → Timeout triggered
    → Decision.allowed = False
    → Partial results not used

[ ] test_out_of_memory_handling
    - Large operation causes memory spike
    → Graceful failure
    → Decision.allowed = False
    → Not a crash

[ ] test_concurrent_access_error_handling
    - Multiple threads evaluate simultaneously
    → No data corruption
    → Audit log entries not lost
    → Consistent decisions
```

**File:** `tests/test_unified_governance.py::TestErrorHandling`

---

## Integration Test Classes (20+ tests)

### ✅ TestCompleteWorkflows (10 tests)

End-to-end workflows combining all subsystems

```
[ ] test_workflow_developer_safe_change
    1. Developer evaluates change
    2. All checks pass
    3. Change approved
    → audit_log records: APPROVED

[ ] test_workflow_developer_risky_change_rejected
    1. Developer evaluates SQL injection code
    2. Semantic analysis detects issue
    3. Change rejected
    → audit_log records: DENIED (semantic)

[ ] test_workflow_budget_exceeded_escalation
    1. Developer tries 600-line change
    2. Budget exceeded (max 500)
    3. Override requested
    4. Reviewer approves override
    5. Change applied
    → audit_log records: DENIED → OVERRIDE_APPROVED → APPLIED

[ ] test_workflow_critical_path_with_approval
    1. Change to src/security/auth.py
    2. Critical path detected
    3. Requires architect review
    4. Architect reviews and approves
    5. Change applied
    → Clear approval chain in audit log

[ ] test_workflow_multiple_violations_remediation
    1. Code has multiple violations:
       - SQL injection (CRITICAL)
       - Budget exceeded (HIGH)
       - Weak crypto (MEDIUM)
    2. Developer sees all 3 in violation list
    3. Developer fixes all 3
    4. Re-evaluation passes
    → Audit log shows both attempts

[ ] test_workflow_compliance_report_generation
    1. 100 operations evaluated over week
    2. Generate compliance report
    3. Report shows:
       - Allow rate: 92%
       - Top violations: SQL injection (8), budget (4)
       - Top remediators: Developer A, B, C
    4. Export report
    → Report can be shared with compliance team

[ ] test_workflow_policy_update_affects_evaluation
    1. Evaluation with policy V1 → allowed
    2. Policy updated to V2 (stricter)
    3. Same operation re-evaluated with V2 → denied
    4. Audit log shows policy version in each entry
    → Clear before/after comparison

[ ] test_workflow_role_change_impacts_limits
    1. Developer with default limits
    2. Promote to reviewer
    3. Limits increase
    4. Operation that was denied now allowed
    → Audit log shows role change + decision change

[ ] test_workflow_violation_remediation_tracking
    1. Code change has violation
    2. Developer gets remediation suggestion
    3. Developer implements fix
    4. Re-evaluation passes
    → Audit log links violation → remediation → re-eval

[ ] test_workflow_escalation_path
    1. Developer encounters unknown error
    2. System fails closed
    3. Error escalated to security team
    4. Security team investigates
    5. Root cause fixed
    6. Operations resume
    → Clear escalation trail in audit log
```

**File:** `tests/test_governance_integration.py::TestCompleteWorkflows`

### ✅ TestPolicyPriority (5 tests)

Policy interaction and priority handling

```
[ ] test_policy_deny_overrides_allow
    - Policy A: DENY (CRITICAL)
    - Policy B: ALLOW
    → Decision: DENY

[ ] test_multiple_deny_policies_show_all
    - 3 DENY policies violated
    → Decision includes all 3
    → Not just first denial

[ ] test_policy_custom_priority_ordering
    - Config: policy_priority = [policy_a, policy_b, policy_c]
    - All violated
    → Violations ordered by priority
    → Not by severity alone

[ ] test_policy_exception_list
    - Policy would deny
    - But operation in exception list
    → Operation allowed
    → Audit log notes exception

[ ] test_policy_temporary_override_expiration
    - Temporary policy override set
    - Time expires
    → Override no longer applies
    → Next evaluation uses original policy
```

**File:** `tests/test_governance_integration.py::TestPolicyPriority`

### ✅ TestConfigurationValidation (5 tests)

Configuration loading and validation in unified system

```
[ ] test_config_validation_on_load
    - Load config with invalid values
    → Validation error
    → Specific field identified

[ ] test_config_default_fallback
    - Missing optional config field
    → Uses default value
    → No error

[ ] test_config_environment_override_validation
    - Env var: SCALPEL_MAX_LINES_PER_CHANGE=invalid
    → Validation error
    → Falls back to config file value

[ ] test_config_hot_reload
    - Update config file
    - UnifiedGovernance with reload=True
    → New config loaded
    - UnifiedGovernance with reload=False
    → Old config still used

[ ] test_config_mutual_exclusivity
    - Config: both policy_disabled AND policy_required
    → Validation error (mutually exclusive)
```

**File:** `tests/test_governance_integration.py::TestConfigurationValidation`

---

## Test Infrastructure (Fixtures & Utilities)

### Core Fixtures

```python
# tests/conftest.py additions

@pytest.fixture
def unified_governance_default(tmp_path, monkeypatch):
    """UnifiedGovernance with default configuration."""
    config_dir = tmp_path / ".code-scalpel"
    config_dir.mkdir()
    # Write default config
    return UnifiedGovernance(str(config_dir))

@pytest.fixture
def unified_governance_restrictive(tmp_path, monkeypatch):
    """UnifiedGovernance with restrictive configuration."""
    config_dir = tmp_path / ".code-scalpel"
    config_dir.mkdir()
    # Write restrictive config
    return UnifiedGovernance(str(config_dir))

@pytest.fixture
def governance_with_mock_policy_engine(tmp_path, monkeypatch):
    """UnifiedGovernance with mocked PolicyEngine."""
    monkeypatch.setattr(
        "code_scalpel.governance.unified_governance.PolicyEngine",
        MockPolicyEngine
    )
    return UnifiedGovernance(str(tmp_path))

@pytest.fixture
def audit_log_reader(tmp_path):
    """Helper to read audit log from temp directory."""
    def _read():
        log_file = tmp_path / ".code-scalpel" / "audit.log"
        return json.loads(log_file.read_text())
    return _read

@pytest.fixture
def sample_operations():
    """Collection of sample operations for testing."""
    return {
        "safe": Operation(type="code_edit", code="x = 1", language="python"),
        "sql_injection": Operation(
            type="code_edit",
            code="cursor.execute(f'SELECT * FROM users WHERE id={uid}')",
            language="python"
        ),
        "large": Operation(
            type="code_edit",
            code="x = 1\n" * 600,  # 600 lines
            language="python"
        ),
        "critical_path": Operation(
            type="code_edit",
            code="x = 1",
            language="python",
            file_path="src/security/auth.py"
        ),
    }
```

### Helper Functions

```python
# tests/helpers/governance_helpers.py

def assert_violation(decision, source, rule, severity=None):
    """Assert specific violation in decision."""
    matching = [v for v in decision.violations 
                if v.source == source and v.rule == rule]
    assert len(matching) > 0, f"No {rule} violation found in {source}"
    if severity:
        assert any(v.severity == severity for v in matching)

def assert_audit_entry_count(governance, expected_count):
    """Assert number of audit entries."""
    entries = governance.get_audit_log()
    assert len(entries) == expected_count

def assert_audit_entry_sequence(governance, expected_sequence):
    """Assert sequence of decision outcomes."""
    entries = governance.get_audit_log()
    actual = [e.decision.allowed for e in entries]
    assert actual == expected_sequence

def create_test_operation(code, language="python", file_path="test.py", 
                         operation_type="code_edit", size_bytes=None):
    """Factory for creating test operations."""
    return Operation(
        type=operation_type,
        code=code,
        language=language,
        file_path=file_path,
        size_bytes=size_bytes or len(code.encode())
    )
```

---

## Estimated Effort Breakdown

| Task | Est. Hours | Dependencies | Priority |
|------|-----------|--------------|----------|
| Set up test infrastructure | 8 | None | P0 |
| TestUnifiedGovernanceEvaluation | 12 | Infrastructure | P0 |
| TestRoleBasedPolicies | 10 | Evaluation tests | P0 |
| TestSemanticSecurityIntegration | 8 | Evaluation tests | P0 |
| TestComplianceReporting | 12 | Evaluation tests | P0 |
| TestPolicyOverrides | 10 | Evaluation tests | P0 |
| TestAuditTrail | 12 | Evaluation tests | P0 |
| TestErrorHandling | 10 | Evaluation tests | P0 |
| TestCompleteWorkflows | 12 | All classes | P1 |
| TestPolicyPriority | 6 | All classes | P1 |
| TestConfigurationValidation | 6 | Infrastructure | P1 |
| Documentation & cleanup | 4 | All tests | P1 |
| **TOTAL** | **110** | - | - |
| **Target** | **60-80** | - | Aggressive |
| **Realistic** | **80-100** | - | Comfortable |

**Note:** With parallel implementation and test-driven development, 60-80 hours is achievable.

---

## Checkpoints & Validation

### Checkpoint 1: Basic Evaluation (Day 1-2)
- [ ] TestUnifiedGovernanceEvaluation complete
- [ ] All 15 tests passing
- [ ] Coverage >80% for unified_governance.py

### Checkpoint 2: Roles & Policies (Day 2-3)
- [ ] TestRoleBasedPolicies complete
- [ ] TestPolicyOverrides complete
- [ ] All 18 tests passing
- [ ] Coverage >85% for unified_governance.py

### Checkpoint 3: Integration & Reporting (Day 3-5)
- [ ] TestComplianceReporting complete
- [ ] TestAuditTrail complete
- [ ] TestErrorHandling complete
- [ ] All 28 tests passing
- [ ] Coverage >90% for unified_governance.py

### Checkpoint 4: End-to-End Workflows (Day 5-6)
- [ ] TestCompleteWorkflows complete
- [ ] TestPolicyPriority complete
- [ ] TestConfigurationValidation complete
- [ ] All 50+ tests passing
- [ ] Coverage ≥95% for unified_governance.py

### Final Validation
- [ ] All tests passing: `pytest tests/test_unified_governance.py -v`
- [ ] All tests passing: `pytest tests/test_governance_integration.py -v`
- [ ] Coverage report: `pytest --cov=src/code_scalpel/governance --cov-report=html`
- [ ] Coverage ≥95%
- [ ] No flaky tests (run 5 times)
- [ ] No memory leaks
- [ ] Performance acceptable (<100ms per test on average)

---

## Success Criteria (Go/No-Go)

**GO Criteria (must have all):**
- ✅ 50+ tests implemented
- ✅ All tests passing
- ✅ Coverage ≥95% for unified_governance.py
- ✅ Coverage ≥90% for related modules (policy_engine, governance)
- ✅ Zero flaky tests
- ✅ Documented test purpose and assertions
- ✅ All error scenarios covered

**NO-GO Criteria (fail if any):**
- ❌ Coverage <90% for unified_governance.py
- ❌ Any flaky/unreliable tests
- ❌ Critical error paths untested
- ❌ >20% tests failing
- ❌ Test performance >500ms average per test

---

## Next Steps

1. **Approve checklist** - Review and sign off on test scope
2. **Set up test environment** - Create test files and fixtures
3. **Implement in priority order** - Start with evaluation tests
4. **Run checkpoint validations** - Pause at each checkpoint
5. **Full validation** - Complete suite validation
6. **Documentation** - Update README with new test counts
7. **Commit to repository** - Code review and merge

---

**Document Version:** 1.0.0  
**Last Updated:** December 2025  
**Status:** Ready for implementation
