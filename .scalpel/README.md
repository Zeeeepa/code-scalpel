# Code Scalpel Policy Configuration

This directory contains policy configurations for Code Scalpel's Policy Engine (v2.5.0 "Guardian").

## Quick Start

1. **Copy the example policy:**
   ```bash
   cp policy.yaml.example policy.yaml
   ```

2. **Install OPA CLI:**
   ```bash
   # macOS
   brew install opa
   
   # Linux
   curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
   chmod +x opa
   sudo mv opa /usr/local/bin/
   ```

3. **Test your policies:**
   ```bash
   opa check policy.yaml
   ```

4. **Use in your code:**
   ```python
   from code_scalpel.policy_engine import PolicyEngine
   
   engine = PolicyEngine(".scalpel/policy.yaml")
   ```

## Policy File Structure

```yaml
version: "1.0"
policies:
  - name: "policy-id"
    description: "What this policy does"
    rule: |
      package scalpel.security
      
      deny[msg] {
        # Rego conditions
        msg = "Violation message"
      }
    severity: "CRITICAL"  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    action: "DENY"         # DENY, WARN, AUDIT
```

## Example Policies

See `policy.yaml.example` for production-ready policy templates including:
- SQL injection prevention
- Spring Security enforcement (Java)
- Safe file operations
- Complexity budgeting
- Hardcoded secret detection
- Audit trail for critical operations

## Documentation

Full documentation available at:
- [Policy Engine Guide](../docs/policy_engine.md)
- [Acceptance Criteria](../docs/v2.5.0_policy_engine_acceptance.md)
- [Usage Examples](../examples/policy_engine_example.py)

## Security Model

The Policy Engine follows a **fail CLOSED** security model:
- All errors result in DENY (never fails open)
- Full audit trail for all decisions
- Human override requires justification
- Single-use override codes
- Time-limited overrides (1 hour)

## Support

For issues or questions:
- [GitHub Issues](https://github.com/tescolopio/code-scalpel/issues)
- [Documentation](https://github.com/tescolopio/code-scalpel#readme)
