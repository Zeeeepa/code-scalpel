# Demo: "SOC2/HIPAA Compliance Reports in 60 Seconds"

**Persona**: Technical Leader
**Pillar**: Governable AI
**Tier**: Enterprise (Custom pricing)
**Duration**: 10 minutes
**Fixture**: Multi-file codebase with security annotations

## Scenario

Company needs SOC2 audit. Manually documenting security controls takes weeks. Code Scalpel generates compliance report automatically.

## Tools Used

- `code_policy_check` (Enterprise: compliance_enabled=true)
- Built-in compliance report generator

## Recording Script

### Step 1: The Compliance Burden (0:00-1:30)

- Show typical SOC2 audit requirements:
  - Data encryption at rest/transit
  - Access control mechanisms
  - Audit logging
  - Secret management
- Cost: 2-4 weeks of engineering time
- On-screen: "Manual documentation is slow and error-prone"

### Step 2: Enterprise Compliance Mode (1:30-3:00)

- Show `.code-scalpel/limits.toml`:
  ```toml
  [enterprise.code_policy_check]
  compliance_enabled = true
  pdf_reports_enabled = true
  ```
- Explain: Enterprise tier includes compliance rule packs

### Step 3: Run Compliance Scan (3:00-5:00)

- Prompt: "Generate SOC2 compliance report for our API"
- Code Scalpel runs checks for:
  - CC6.1: Logical Access Controls
  - CC6.6: Encryption
  - CC6.7: System Monitoring
  - CC7.2: System Monitoring
- Progress: "Analyzing 247 files..."

### Step 4: Automated Report (5:00-7:00)

- Tool generates PDF report:
  - **Summary**: 94% compliant
  - **Details by Control**:
    - CC6.1 (Access): ✓ RBAC implemented
    - CC6.6 (Encryption): ⚠ 3 endpoints missing TLS
    - CC7.2 (Monitoring): ✓ Audit logs present
  - **Evidence**: Code snippets showing compliance
  - **Gaps**: 3 findings requiring fixes

### Step 5: Visual Dashboard (7:00-8:00)

- Show compliance dashboard:
  - Bar chart: Controls pass rate
  - Trend: Compliance over time
  - Risk heatmap: Critical gaps highlighted
- Export to PDF: "SOC2_Compliance_Report_2026-02-08.pdf"

### Step 6: Fix Workflow (8:00-9:00)

- Focus on gap: "3 endpoints missing TLS"
- Code Scalpel provides:
  - File locations
  - Current code (HTTP)
  - Fix suggestion (HTTPS redirect)
- Apply fixes, re-scan: 100% compliant ✓

### Step 7: Auditor Handoff (9:00-9:30)

- Export package for auditor:
  - PDF report
  - Evidence bundle (code excerpts)
  - Audit trail (all scans timestamped)
- On-screen: "From weeks to minutes"

### Step 8: Enterprise ROI (9:30-10:00)

- Manual SOC2 prep: $50,000 (2 engineers × 2 weeks)
- Code Scalpel: $300,000/year (50 seats)
- But: automated compliance saves $200,000/audit
- Plus: continuous compliance (not yearly scramble)
- ROI: Positive in first audit cycle

## Expected Outputs

- PDF compliance report (30+ pages)
- Evidence bundle (ZIP file)
- Remediation plan (JSON)

## Compliance Frameworks Supported

### SOC2 (Trust Service Criteria)

| Control | Description | Code Scalpel Check |
|---------|-------------|-------------------|
| CC6.1 | Logical and Physical Access Controls | RBAC implementation, authentication |
| CC6.6 | Encryption | TLS/SSL, data-at-rest encryption |
| CC6.7 | System Monitoring | Audit logging, anomaly detection |
| CC7.2 | System Monitoring | Error logging, alerting |
| CC8.1 | Change Management | Version control, deployment gates |

### HIPAA (Technical Safeguards)

| Requirement | Description | Code Scalpel Check |
|-------------|-------------|-------------------|
| 164.312(a)(1) | Access Control | User authentication, authorization |
| 164.312(a)(2)(iv) | Encryption | PHI encryption at rest and transit |
| 164.312(b) | Audit Controls | Access logs, modification tracking |
| 164.312(c)(1) | Integrity | Data validation, checksums |
| 164.312(d) | Authentication | Multi-factor authentication |

### PCI-DSS (Data Security Standards)

| Requirement | Description | Code Scalpel Check |
|-------------|-------------|-------------------|
| 3.4 | Render PAN unreadable | Credit card masking, encryption |
| 6.5.1 | Injection flaws | SQL injection prevention |
| 6.5.7 | XSS prevention | Output sanitization |
| 8.2 | Authentication | Password policies, MFA |
| 10.1 | Audit trails | Logging of access to cardholder data |

### GDPR (Data Protection)

| Article | Description | Code Scalpel Check |
|---------|-------------|-------------------|
| Art. 25 | Data protection by design | Privacy controls in code |
| Art. 32 | Security of processing | Encryption, access controls |
| Art. 33 | Breach notification | Audit logging mechanisms |
| Art. 35 | Data protection impact | Privacy annotations |

## Sample Report Structure

```markdown
# SOC2 Compliance Report
**Generated**: 2026-02-08 14:23:00 UTC
**Codebase**: api-service (247 files)
**Framework**: SOC2 Type II

## Executive Summary
- **Overall Compliance**: 94%
- **Critical Gaps**: 3
- **Warnings**: 7
- **Pass Rate**: 47/50 controls

## Control Details

### CC6.1: Logical Access Controls ✓
**Status**: COMPLIANT
**Evidence**:
- RBAC implementation: `auth/rbac.py:45`
- JWT token validation: `auth/middleware.py:23`
- Session management: `auth/sessions.py:12`

**Code Excerpt**:
```python
# auth/rbac.py:45
@require_role("admin")
def delete_user(user_id: str):
    # Role-based access control enforced
    ...
```

### CC6.6: Encryption ⚠
**Status**: PARTIAL - 3 gaps found
**Evidence**:
- TLS enforced: 12/15 endpoints ✓
- Missing TLS: 3/15 endpoints ❌

**Gaps**:
1. `api/health.py:23` - HTTP endpoint (should be HTTPS)
2. `api/metrics.py:45` - No TLS enforcement
3. `api/legacy.py:67` - Cleartext transmission

**Remediation**:
```python
# Add HTTPS redirect
@app.before_request
def force_https():
    if not request.is_secure:
        return redirect(request.url.replace("http://", "https://"))
```

[... 48 more controls ...]

## Recommendations
1. Fix 3 TLS gaps (estimated 2 hours)
2. Add audit logging to 7 endpoints (estimated 4 hours)
3. Implement rate limiting (estimated 8 hours)

## Audit Trail
- Scan started: 2026-02-08 14:22:15 UTC
- Scan completed: 2026-02-08 14:23:03 UTC
- Duration: 48 seconds
- Scanned files: 247
- Rules evaluated: 150
```

## Key Talking Points

- "Manual SOC2 prep takes weeks, Code Scalpel does it in 60 seconds"
- "Continuous compliance, not yearly scramble"
- "Automated evidence collection for auditors"
- "Covers SOC2, HIPAA, PCI-DSS, GDPR out of the box"
- "Enterprise = compliance rule packs + PDF reports + audit trail"
- "ROI positive in first audit cycle"

## Cost-Benefit Analysis

### Traditional SOC2 Audit Prep

| Activity | Time | Cost (2 engineers @ $150k) |
|----------|------|----------------------------|
| Map controls to code | 2 days | $4,800 |
| Document evidence | 3 days | $7,200 |
| Review and verify | 2 days | $4,800 |
| Generate reports | 1 day | $2,400 |
| **Total** | **8 days** | **$19,200** |

### Code Scalpel Enterprise

| Activity | Time | Cost |
|----------|------|------|
| Run compliance scan | 60 seconds | $0 (included) |
| Review findings | 2 hours | $600 |
| Fix gaps | 4 hours | $1,200 |
| Export reports | 5 minutes | $0 (included) |
| **Total** | **6 hours** | **$1,800** |

**Savings per audit**: $17,400
**Annual audits**: 1-2 times
**Annual savings**: $17,400 - $34,800

**Enterprise cost**: $300,000/year (50 seats = $6,000/seat)
**Break-even**: 9-17 audits across organization
**Typical ROI**: 2-4x (considering continuous compliance)
