# Demo: "Custom Policies: Enforce Team Standards"

**Persona**: Developer
**Pillar**: Governable AI
**Tier**: Enterprise (Custom pricing)
**Duration**: 12 minutes
**Fixture**: Custom policy YAML examples

## Scenario

Team has internal standards (no f-strings in logging, must use structured logging). Standard linters miss semantic rules. Code Scalpel policy engine enforces custom rules.

## Tools Used

- `code_policy_check` (Enterprise tier with custom rules)
- `verify_policy_integrity`

## Recording Script

### Step 1: Team Standards Problem (0:00-2:00)

- Show team's coding standards doc:
  - Use structured logging (not print/f-strings)
  - No hardcoded secrets
  - All API calls must have retries
  - Database queries must be parameterized
- Problem: "How do we enforce this in code review?"

### Step 2: Standard Linters Fall Short (2:00-3:30)

- Run pylint/ruff: misses semantic rules
- Example: catches syntax, but not "use structured logging"
- On-screen: "Generic linters can't encode team knowledge"

### Step 3: Create Custom Policy (3:30-6:00)

- Show `.code-scalpel/policies/team_standards.yml`:
  ```yaml
  policies:
    - name: "Structured Logging Only"
      rule: |
        Forbid print() or f-string in logging
      patterns:
        - "logging.info(f'"
        - "print("
      severity: "error"

    - name: "API Resilience"
      rule: |
        All HTTP calls must have retry logic
      ast_pattern: "requests.get|post"
      require: "retry" or "tenacity"
      severity: "warning"
  ```
- Voiceover: "Turn tribal knowledge into enforceable rules"

### Step 4: Run Policy Check (6:00-8:00)

- Prompt: "Check this codebase against our team policies"
- Code Scalpel runs `code_policy_check` with custom rules
- Findings:
  - 5 violations of "Structured Logging Only"
  - 2 API calls without retries
  - 1 potential secret (API key pattern)

### Step 5: Detailed Report (8:00-9:00)

- Show JSON output:
  ```json
  {
    "policy_violations": [
      {
        "policy": "Structured Logging Only",
        "file": "api/users.py",
        "line": 42,
        "code": "logging.info(f'User {user_id} logged in')",
        "fix_suggestion": "Use structured logging: logger.info('User logged in', extra={'user_id': user_id})"
      }
    ]
  }
  ```
- On-screen: Actionable fixes for each violation

### Step 6: CI Integration (9:00-10:30)

- Show GitHub Actions workflow:
  ```yaml
  - name: Check Team Policies
    run: |
      code-scalpel policy-check \
        --policy .code-scalpel/policies/team_standards.yml \
        --fail-on-violation
  ```
- Demo: PR blocked until violations fixed
- On-screen: "Enforce standards at pull request time"

### Step 7: Policy Integrity (10:30-11:30)

- Show `verify_policy_integrity`
- Enterprise feature: cryptographic signatures on policies
- Prevents tampering: policies signed by security team
- Audit log: who modified policies when

### Step 8: Enterprise Value (11:30-12:00)

- "Encode institutional knowledge"
- "Consistent enforcement across 100+ developers"
- "Required for SOC2/ISO27001 compliance"

## Expected Outputs

- Policy violation report with fix suggestions
- Compliance dashboard (% of codebase compliant)
- Audit trail of policy changes

## Custom Policy Examples

### Example 1: Structured Logging

```yaml
- name: "Structured Logging Only"
  description: "Enforce structured logging for better observability"
  severity: "error"
  patterns:
    - "logging.\\w+\\(f['\"]"  # f-string in logging
    - "print\\("             # print statements
  fix_template: |
    Replace: logging.info(f"User {user_id}")
    With: logger.info("User action", extra={"user_id": user_id})
```

### Example 2: API Resilience

```yaml
- name: "API Resilience"
  description: "All external API calls must have retry logic"
  severity: "warning"
  ast_match:
    - type: "Call"
      func: ["requests.get", "requests.post", "httpx.get"]
  require_decorator: ["@retry", "@tenacity.retry"]
  fix_suggestion: |
    Add retry decorator:
    from tenacity import retry, stop_after_attempt
    @retry(stop=stop_after_attempt(3))
```

### Example 3: Secret Detection

```yaml
- name: "No Hardcoded Secrets"
  description: "Prevent secrets in source code"
  severity: "critical"
  patterns:
    - "api_key\\s*=\\s*['\"][A-Za-z0-9]{20,}['\"]"
    - "password\\s*=\\s*['\"][^'\"]+['\"]"
    - "secret\\s*=\\s*['\"][^'\"]+['\"]"
  exclude_files: ["tests/**", "*.example"]
  fix_suggestion: "Use environment variables or secret manager"
```

### Example 4: Database Safety

```yaml
- name: "Parameterized Queries Only"
  description: "Prevent SQL injection"
  severity: "critical"
  ast_match:
    - type: "Call"
      func: ["db.execute", "cursor.execute"]
      args:
        - type: "JoinedStr"  # f-string
        - type: "BinOp"      # string concatenation
  fix_template: |
    Replace: db.execute(f"SELECT * FROM users WHERE id = {user_id}")
    With: db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Policy Check

on: [pull_request]

jobs:
  policy-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Code Scalpel
        run: pip install codescalpel

      - name: Run Policy Check
        run: |
          code-scalpel policy-check \
            --policy .code-scalpel/policies/ \
            --format json \
            --output policy-report.json \
            --fail-on-violation

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: policy-report
          path: policy-report.json

      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('policy-report.json'));
            // Post violations as PR comment
```

## Key Talking Points

- "Linters check syntax, policies enforce semantics"
- "Encode tribal knowledge as code"
- "Consistent enforcement across entire team"
- "Cryptographic signatures prevent policy tampering"
- "Required for compliance frameworks (SOC2, ISO27001)"
- "Enterprise = custom rules + verification + audit trail"

## ROI Analysis

### Traditional Approach
- Code reviews: 10 hours/week finding policy violations
- Production incidents: 2/month from missed violations
- Cost: $50,000/year (developer time + incidents)

### Code Scalpel Enterprise
- Automated policy checks: 30 seconds per PR
- Zero policy violations reach production
- Cost: $300,000/year (50 seats)
- Savings: $200,000/year (prevented incidents)

**Break-even**: First major incident prevented
