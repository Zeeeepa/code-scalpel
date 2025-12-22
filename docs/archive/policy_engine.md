# Policy Engine - Enterprise Governance for AI Agents

**Version:** v2.5.0 "Guardian"  
**Status:** Implemented  
**Last Updated:** December 16, 2025

## Overview

The Policy Engine provides declarative policy enforcement using Open Policy Agent's (OPA) Rego language. It enables organizations to define rules that AI agents must follow when modifying code, ensuring compliance with security policies and organizational standards.

## Key Features

- **Declarative Policies:** Define rules in YAML using Rego language
- **Semantic Analysis:** Detect vulnerabilities through code pattern analysis, not just text matching
- **Fail CLOSED Security:** All errors result in DENY (never fails open)
- **Human Override:** Policy violations can be overridden with justification and approval
- **Full Audit Trail:** All policy decisions and overrides are logged

## Installation

### Prerequisites

1. **Install OPA CLI:**

```bash
# macOS (Homebrew)
brew install opa

# Linux
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
sudo mv opa /usr/local/bin/

# Windows
# Download from https://www.openpolicyagent.org/docs/latest/#running-opa
```

2. **Install Code Scalpel:**

```bash
pip install code-scalpel
```

## Quick Start

### 1. Create Policy File

Create `.code-scalpel/policy.yaml` in your project root:

```yaml
version: "1.0"
policies:
  - name: "no-raw-sql"
    description: "Prevent agents from introducing raw SQL queries"
    rule: |
      package scalpel.security
      
      deny[msg] {
        input.operation == "code_edit"
        contains(input.code, "SELECT")
        not contains(input.code, "?")
        not contains(input.code, "PreparedStatement")
        msg = "Raw SQL detected without parameterized queries"
      }
    severity: "CRITICAL"
    action: "DENY"
```

### 2. Use Policy Engine

```python
from code_scalpel.policy_engine import PolicyEngine, Operation

# Initialize engine (loads and validates policies)
engine = PolicyEngine(".code-scalpel/policy.yaml")

# Create operation to evaluate
operation = Operation(
    type="code_edit",
    code='query = "SELECT * FROM users WHERE id=" + user_id',
    language="python",
    file_path="app.py"
)

# Evaluate against policies
decision = engine.evaluate(operation)

if not decision.allowed:
    print(f"Policy violation: {decision.reason}")
    for violation in decision.violations:
        print(f"  - {violation.policy_name}: {violation.message}")
    
    # Request human override if needed
    if decision.requires_override:
        override = engine.request_override(
            operation=operation,
            decision=decision,
            justification="Emergency hotfix approved by security team",
            human_code="abc123456"
        )
        
        if override.approved:
            print(f"Override approved: {override.override_id}")
            print(f"Expires: {override.expires_at}")
```

## Policy Configuration

### Policy Structure

Each policy has the following fields:

```yaml
- name: "policy-identifier"           # Unique ID
  description: "Human-readable text"  # What this policy does
  rule: |                             # Rego policy code
    package scalpel.security
    
    deny[msg] {
      # Rego conditions
      msg = "Violation message"
    }
  severity: "CRITICAL"                # CRITICAL, HIGH, MEDIUM, LOW, INFO
  action: "DENY"                      # DENY, WARN, AUDIT
```

### Severity Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `CRITICAL` | Immediate security risk | SQL injection, XSS, hardcoded secrets |
| `HIGH` | Significant security issue | Missing authorization, insecure crypto |
| `MEDIUM` | Moderate issue | Code complexity, missing tests |
| `LOW` | Minor issue | Style violations, minor warnings |
| `INFO` | Informational only | Statistics, usage tracking |

### Actions

| Action | Behavior | Use Case |
|--------|----------|----------|
| `DENY` | Block operation completely | Critical security violations |
| `WARN` | Allow but log warning | Non-critical issues |
| `AUDIT` | Allow and log for review | Tracking operations |

## Semantic Analysis

The Policy Engine includes semantic analysis capabilities that go beyond simple text matching:

### SQL Injection Detection

Detects SQL operations across multiple patterns:

```python
from code_scalpel.policy_engine import SemanticAnalyzer

analyzer = SemanticAnalyzer()

# Detects concatenation
code1 = 'query = "SELECT * FROM users WHERE id=" + user_id'
assert analyzer.contains_sql_sink(code1, "python")

# Detects f-strings
code2 = 'query = f"SELECT * FROM {table} WHERE id={user_id}"'
assert analyzer.contains_sql_sink(code2, "python")

# Detects string.format()
code3 = 'query = "SELECT * FROM users WHERE id={}".format(user_id)'
assert analyzer.contains_sql_sink(code3, "python")

# Detects % formatting
code4 = 'query = "SELECT * FROM users WHERE id=%s" % user_id'
assert analyzer.contains_sql_sink(code4, "python")

# Detects StringBuilder (Java)
code5 = """
StringBuilder query = new StringBuilder();
query.append("SELECT * FROM users");
query.append(" WHERE id=");
query.append(userId);
"""
assert analyzer.contains_sql_sink(code5, "java")

# Detects template literals (JavaScript)
code6 = 'const query = `SELECT * FROM users WHERE id=${userId}`;'
assert analyzer.contains_sql_sink(code6, "javascript")
```

### Parameterization Detection

Recognizes safe SQL patterns:

```python
# Python parameterized query (safe)
safe_code = 'cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))'
assert analyzer.has_parameterization(safe_code, "python")

# Java PreparedStatement (safe)
safe_java = """
PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE id=?");
stmt.setString(1, userId);
"""
assert analyzer.has_parameterization(safe_java, "java")
```

## Human Override System

When a policy violation occurs with `action: DENY`, humans can override the decision:

### Override Requirements

1. **Justification:** Human-readable explanation
2. **Override Code:** One-time code (6+ characters)
3. **Single Use:** Codes cannot be reused
4. **Time Limited:** Overrides expire after 1 hour

### Override Example

```python
# Operation was denied by policy
decision = engine.evaluate(operation)

if not decision.allowed and decision.requires_override:
    override = engine.request_override(
        operation=operation,
        decision=decision,
        justification="Emergency hotfix - ticket SEC-1234",
        human_code="secure_code_123"
    )
    
    if override.approved:
        # Proceed with operation
        print(f"Override ID: {override.override_id}")
        print(f"Valid until: {override.expires_at}")
    else:
        print(f"Override denied: {override.reason}")
```

## Fail CLOSED Security Model

The Policy Engine follows a **fail CLOSED** security model:

| Error Condition | Behavior |
|----------------|----------|
| Policy file not found | DENY ALL |
| Invalid YAML syntax | DENY ALL |
| Invalid Rego syntax | DENY ALL |
| OPA CLI not found | DENY ALL |
| Policy evaluation timeout | DENY operation |
| Policy evaluation error | DENY operation |

**Never fails open.** All errors result in denial to ensure security.

## Example Policies

### SQL Injection Prevention

```yaml
- name: "no-raw-sql"
  description: "Prevent raw SQL queries"
  rule: |
    package scalpel.security
    
    deny[msg] {
      input.operation == "code_edit"
      contains(input.code, "SELECT")
      not contains(input.code, "?")
      not contains(input.code, "PreparedStatement")
      msg = "Raw SQL detected without parameterized queries"
    }
  severity: "CRITICAL"
  action: "DENY"
```

### Spring Security Requirement

```yaml
- name: "spring-security-required"
  description: "All Java controllers must use Spring Security"
  rule: |
    package scalpel.security
    
    deny[msg] {
      input.language == "java"
      contains(input.code, "@RestController")
      not contains(input.code, "@PreAuthorize")
      msg = "REST controller missing @PreAuthorize annotation"
    }
  severity: "HIGH"
  action: "DENY"
```

### Safe File Operations

```yaml
- name: "safe-file-operations"
  description: "File operations must not use user-controlled paths"
  rule: |
    package scalpel.security
    
    deny[msg] {
      input.operation == "code_edit"
      contains(input.code, "open(")
      contains(input.code, "request.")
      msg = "File operation uses user-controlled path"
    }
  severity: "HIGH"
  action: "DENY"
```

## Testing

Run the test suite:

```bash
# Run all policy engine tests
pytest tests/test_policy_engine.py -v

# Run specific test categories
pytest tests/test_policy_engine.py::TestPolicyLoading -v
pytest tests/test_policy_engine.py::TestSemanticAnalyzer -v
pytest tests/test_policy_engine.py::TestFailClosed -v
```

## Acceptance Criteria

All P0 acceptance criteria from the problem statement are met:

- [x] Policy Engine: Loads and parses `.code-code-scalpel/policy.yaml`
- [x] Policy Engine: Validates Rego syntax at startup
- [x] Policy Engine: Evaluates operations against all policies
- [x] Policy Engine: Fails CLOSED on policy parsing error
- [x] Policy Engine: Fails CLOSED on policy evaluation error
- [x] Semantic Blocking: Detects SQL via string concatenation
- [x] Semantic Blocking: Detects SQL via StringBuilder/StringBuffer
- [x] Semantic Blocking: Detects SQL via f-strings/template literals
- [x] Semantic Blocking: Detects SQL via string.format()
- [x] Override System: Requires valid human code
- [x] Override System: Logs all override requests
- [x] Override System: Override expires after time limit
- [x] Override System: Override cannot be reused

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Policy Engine                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐         ┌─────────────────┐        │
│  │  YAML Parser   │────────>│  Policy Store   │        │
│  └────────────────┘         └─────────────────┘        │
│          │                           │                  │
│          v                           v                  │
│  ┌────────────────┐         ┌─────────────────┐        │
│  │ Rego Validator │         │  OPA Evaluator  │        │
│  └────────────────┘         └─────────────────┘        │
│          │                           │                  │
│          └───────────┬───────────────┘                  │
│                      v                                  │
│            ┌──────────────────┐                         │
│            │ Semantic Analyzer│                         │
│            └──────────────────┘                         │
│                      │                                  │
│                      v                                  │
│            ┌──────────────────┐                         │
│            │ Policy Decision  │                         │
│            └──────────────────┘                         │
│                      │                                  │
│                      v                                  │
│            ┌──────────────────┐                         │
│            │ Override System  │                         │
│            └──────────────────┘                         │
└─────────────────────────────────────────────────────────┘
```

## Troubleshooting

### OPA Not Found

```
PolicyError: OPA CLI not found. Install from https://www.openpolicyagent.org/docs/latest/#running-opa
```

**Solution:** Install OPA CLI following the installation instructions above.

### Invalid Rego Syntax

```
PolicyError: Invalid Rego in policy 'my-policy': ...
```

**Solution:** Validate your Rego syntax:

```bash
opa check policy.rego
```

### Policy File Not Found

```
PolicyError: Policy file not found: .code-scalpel/policy.yaml
```

**Solution:** Create the policy file or specify the correct path.

## References

- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Rego Language Reference](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Code Scalpel Documentation](https://github.com/tescolopio/code-scalpel)
