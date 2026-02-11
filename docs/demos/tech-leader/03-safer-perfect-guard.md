# Demo: "The Perfect Guard: Block Risky Commits Pre-Merge"

**Persona**: Technical Leader
**Pillar**: Safer AI
**Tier**: Enterprise (Custom pricing)
**Duration**: 12 minutes
**Fixture**: From Ninja Warrior "Perfect Guard" obstacle

## Scenario

CI pipeline enforces security and quality gates. Developer tries to commit code with SQL injection. Policy engine blocks merge automatically.

## Tools Used

- `code_policy_check` (Enterprise: policy_gated_mutations=true)
- `security_scan`
- `verify_policy_integrity`

## Recording Script

### Step 1: The Problem: Post-Merge Discoveries (0:00-1:30)

- Show typical workflow:
  1. Developer writes code
  2. Push to branch
  3. Code review (human)
  4. Merge to main
  5. Bug found in production 🔥
- On-screen: "Bugs are 10x more expensive after merge"

### Step 2: The Perfect Guard Concept (1:30-3:00)

- Explain: "What if security was automatic and mandatory?"
- Show CI workflow with Code Scalpel gates:
  ```yaml
  jobs:
    security-gate:
      - Security scan (must pass)
      - Policy compliance (must pass)
      - Type safety check (must pass)

    only-if-secure:
      needs: security-gate
      - Unit tests
      - Integration tests
      - Deploy
  ```

### Step 3: Demo: The Risky Commit (3:00-5:00)

- Developer creates PR:
  ```python
  def get_user(user_id):
      query = f"SELECT * FROM users WHERE id = {user_id}"
      return db.execute(query)
  ```
- Commit message: "feat: add user lookup endpoint"
- Push to GitHub

### Step 4: CI Pipeline Execution (5:00-7:00)

- GitHub Actions triggers
- Code Scalpel runs security scan
- Finding: SQL injection vulnerability (HIGH severity)
- Policy check: FAIL - "No SQL interpolation allowed"
- CI status: ❌ Blocked

### Step 5: PR Comment (7:00-8:00)

- Bot posts comment on PR:
  ```
  🛡️ Code Scalpel Security Gate

  ❌ BLOCKED: Security violations found

  Findings:
  1. SQL Injection at line 2 (HIGH severity)
     - Use parameterized queries
     - Example: db.execute("SELECT * FROM users WHERE id = ?", (user_id,))

  Policy Violations:
  1. "SQL Safety Policy" - No string interpolation in SQL

  This PR cannot be merged until violations are fixed.
  ```

### Step 6: Developer Fixes Issues (8:00-9:00)

- Update code:
  ```python
  def get_user(user_id):
      query = "SELECT * FROM users WHERE id = ?"
      return db.execute(query, (user_id,))
  ```
- Push fix
- CI re-runs: ✓ All checks pass
- PR now mergeable

### Step 7: Policy Integrity (9:00-10:30)

- Show how policies are protected:
  - Stored in `.code-scalpel/policies/`
  - Signed by security team (Enterprise)
  - Verified before each check
  - Audit trail of all enforcement actions
- On-screen: "Policies can't be bypassed"

### Step 8: Enterprise Scale (10:30-11:30)

- Stats from month:
  - PRs analyzed: 847
  - Blocked merges: 23 (2.7%)
  - Vulnerabilities prevented: 31
  - False positives: 1 (0.1%)
- Time to fix: avg 12 minutes
- On-screen: "Shift left = catch early = cheaper"

### Step 9: ROI Calculation (11:30-12:00)

- Production bug fix cost: $10,000 (incident + patch + deploy)
- Prevented bugs: 31/month × $10,000 = $310,000/month
- Enterprise cost: $25,000/month (50 seats)
- ROI: 12x

## Expected Outputs

- CI logs with security gate results
- PR comment with findings and fixes
- Audit trail of enforcement actions
- Monthly security report

## Key Features

- Zero false negatives (all vulns caught)
- 0.1% false positives
- Automatic blocking (no human override)
- Signed policies (tamper-proof)

## GitHub Actions Integration

### Complete Workflow

```yaml
name: Security Gate

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  code-scalpel-gate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Install Code Scalpel
        run: |
          pip install codescalpel
          code-scalpel --version

      - name: Security Scan
        id: security
        run: |
          code-scalpel security-scan \
            --format json \
            --output security-report.json \
            --fail-on HIGH,CRITICAL
        continue-on-error: true

      - name: Policy Check
        id: policy
        run: |
          code-scalpel policy-check \
            --policy .code-scalpel/policies/ \
            --verify-integrity \
            --format json \
            --output policy-report.json \
            --fail-on-violation
        continue-on-error: true

      - name: Type Safety Check
        id: types
        run: |
          code-scalpel type-evaporation-scan \
            --format json \
            --output types-report.json \
            --fail-on HIGH
        continue-on-error: true

      - name: Generate Combined Report
        if: always()
        run: |
          code-scalpel merge-reports \
            --reports security-report.json policy-report.json types-report.json \
            --output combined-report.json

      - name: Comment on PR
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('combined-report.json'));

            let comment = '## 🛡️ Code Scalpel Security Gate\n\n';

            if (report.blocked) {
              comment += '❌ **BLOCKED**: Security violations found\n\n';
              comment += '### Findings\n\n';

              report.findings.forEach((finding, idx) => {
                comment += `${idx + 1}. **${finding.severity}**: ${finding.title}\n`;
                comment += `   - File: \`${finding.file}:${finding.line}\`\n`;
                comment += `   - Issue: ${finding.description}\n`;
                if (finding.fix) {
                  comment += `   - Fix: ${finding.fix}\n`;
                }
                comment += '\n';
              });

              comment += '\n⚠️ **This PR cannot be merged until violations are fixed.**\n';
            } else {
              comment += '✅ **PASSED**: All security checks passed\n\n';
              comment += `- Security scan: ✓ No vulnerabilities\n`;
              comment += `- Policy check: ✓ Compliant\n`;
              comment += `- Type safety: ✓ No type mismatches\n`;
            }

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            security-report.json
            policy-report.json
            types-report.json
            combined-report.json

      - name: Fail if Blocked
        if: steps.security.outcome == 'failure' || steps.policy.outcome == 'failure' || steps.types.outcome == 'failure'
        run: |
          echo "Security gate failed. PR is blocked."
          exit 1

  # Only run if security gate passes
  tests:
    needs: code-scalpel-gate
    runs-on: ubuntu-latest
    steps:
      - name: Run unit tests
        run: pytest tests/

  deploy-staging:
    needs: tests
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: ./deploy.sh staging
```

## Policy Configuration

### SQL Safety Policy

```yaml
# .code-scalpel/policies/sql-safety.yml
name: "SQL Safety Policy"
version: "1.0"
signed_by: "security-team@company.com"
signature: "SHA256:abc123..."  # Cryptographic signature

rules:
  - id: "sql-001"
    name: "No SQL Interpolation"
    severity: "CRITICAL"
    description: "Prevent SQL injection by forbidding string interpolation"

    patterns:
      - type: "ast"
        match: |
          Call(
            func=Attribute(value=Name(id="db"), attr="execute"),
            args=[
              JoinedStr() | FormattedValue() | BinOp(op=Add())
            ]
          )

    fix_template: |
      Replace string formatting with parameterized query:

      Bad:
      db.execute(f"SELECT * FROM users WHERE id = {user_id}")

      Good:
      db.execute("SELECT * FROM users WHERE id = ?", (user_id,))

  - id: "sql-002"
    name: "Parameterized Queries Only"
    severity: "CRITICAL"
    description: "All database queries must use parameterized statements"

    allow_patterns:
      - "db.execute(*, args=*)"  # Parameterized
      - "session.query(*)"       # ORM (safe)

    deny_patterns:
      - "db.execute(f*)"         # f-string
      - "db.execute(* + *)"      # Concatenation
```

### General Security Policy

```yaml
# .code-scalpel/policies/security.yml
name: "Security Policy"
version: "2.0"
signed_by: "security-team@company.com"
signature: "SHA256:def456..."

rules:
  - id: "sec-001"
    name: "No Hardcoded Secrets"
    severity: "CRITICAL"
    patterns:
      - 'api_key\s*=\s*["\'][A-Za-z0-9+/=]{20,}["\']'
      - 'password\s*=\s*["\'][^"\']{8,}["\']'
      - 'secret\s*=\s*["\'][^"\']+["\']'
    exclude:
      - "tests/**"
      - "*.example"
      - "docs/**"

  - id: "sec-002"
    name: "XSS Prevention"
    severity: "HIGH"
    description: "All user input must be sanitized before HTML rendering"
    patterns:
      - type: "taint"
        source: ["request.args", "request.form", "request.json"]
        sink: ["render_template", "Markup", "f'<.*{.*}.*>'"]
        require_sanitizer: true

  - id: "sec-003"
    name: "Command Injection Prevention"
    severity: "CRITICAL"
    patterns:
      - type: "ast"
        match: |
          Call(
            func=Attribute(value=Name(id="os"), attr="system"),
            args=[JoinedStr() | FormattedValue() | BinOp()]
          )
    message: "Never use os.system() with user input. Use subprocess with shell=False"
```

## Monthly Security Report

```json
{
  "report_period": "2026-01-01 to 2026-01-31",
  "organization": "Acme Corp",

  "summary": {
    "total_prs": 847,
    "blocked_prs": 23,
    "block_rate": "2.7%",
    "vulnerabilities_prevented": 31,
    "false_positives": 1,
    "false_positive_rate": "0.1%",
    "avg_fix_time_minutes": 12
  },

  "vulnerabilities_by_severity": {
    "CRITICAL": 8,
    "HIGH": 15,
    "MEDIUM": 6,
    "LOW": 2
  },

  "vulnerabilities_by_type": {
    "SQL Injection": 8,
    "XSS": 5,
    "Command Injection": 3,
    "Hardcoded Secrets": 7,
    "Path Traversal": 2,
    "SSRF": 1,
    "Insecure Deserialization": 3,
    "Weak Cryptography": 2
  },

  "top_contributors": [
    {"developer": "alice@company.com", "blocked_prs": 7, "avg_fix_time": 8},
    {"developer": "bob@company.com", "blocked_prs": 4, "avg_fix_time": 15}
  ],

  "policy_violations": {
    "SQL Safety Policy": 12,
    "XSS Prevention": 8,
    "Secret Management": 7,
    "API Resilience": 4
  },

  "roi_analysis": {
    "prevented_incidents": 31,
    "avg_incident_cost": "$10,000",
    "total_prevented_cost": "$310,000",
    "code_scalpel_cost": "$25,000",
    "roi_ratio": "12.4x"
  }
}
```

## Key Talking Points

- "Shift left - catch vulnerabilities before merge, not in production"
- "Automatic enforcement - no human error, no bypass"
- "Cryptographic policy signatures prevent tampering"
- "2.7% block rate - catches real issues without noise"
- "0.1% false positive rate - developers trust it"
- "12 minute average fix time - instant feedback"
- "12x ROI - prevents expensive production incidents"
- "Required for regulated industries and SOC2 compliance"

## Enterprise Advantages

1. **Signed Policies**: Cryptographic signatures prevent unauthorized changes
2. **Policy Integrity Verification**: Ensures policies haven't been tampered with
3. **Audit Trail**: Complete history of all enforcement actions
4. **Custom Rules**: Encode organization-specific security requirements
5. **Zero False Negatives**: Graph-based analysis catches what regex misses
6. **Minimal False Positives**: Semantic understanding reduces noise
7. **Automatic Blocking**: No manual approval needed - enforces consistently
8. **Integration**: Works with GitHub, GitLab, Bitbucket, Jenkins
