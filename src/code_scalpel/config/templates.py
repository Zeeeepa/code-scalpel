"""
Configuration templates for .code-scalpel directory.

[20251219_FEATURE] v3.0.2 - Auto-initialize .code-scalpel configuration
"""

# Template for policy.yaml
POLICY_YAML_TEMPLATE = """# Code Scalpel Policy Configuration
# Learn more: https://github.com/tescolopio/code-scalpel/blob/main/docs/policy_engine_guide.md

version: "1.0.0"

# Policy enforcement mode
enforcement: "warn"  # Options: "warn", "block", "disabled"

# Security rules
security:
  # Block SQL injection attempts
  sql_injection: true

  # Block command injection attempts
  command_injection: true

  # Block path traversal attempts
  path_traversal: true

  # Block XSS attempts
  xss: true

# Change budgeting - limit blast radius
budgeting:
  enabled: false
  max_files_per_session: 10
  max_lines_per_file: 500
  max_total_changes: 1000

# Audit trail
audit:
  enabled: true
  log_file: ".code-scalpel/audit.log"
"""

# Template for budget.yaml
BUDGET_YAML_TEMPLATE = """# Code Scalpel Change Budget Configuration
# Learn more: https://github.com/tescolopio/code-scalpel/blob/main/docs/guides/change_budgeting.md

version: "1.0.0"

# Maximum changes allowed per session
budgets:
  # File-level limits
  max_files_modified: 10
  max_files_created: 5
  max_files_deleted: 2

  # Line-level limits (per file)
  max_lines_added: 500
  max_lines_deleted: 300
  max_lines_modified: 400

  # Total session limits
  max_total_line_changes: 1000

# Reset behavior
reset:
  # Options: "session", "daily", "manual"
  mode: "session"

# Exemptions (files that don't count against budget)
exemptions:
  - "tests/**/*.py"
  - "docs/**/*.md"
"""

# Template for README.md in .code-scalpel/
README_TEMPLATE = """# Code Scalpel Configuration Directory

This directory contains configuration files for Code Scalpel policy engine and governance features.

## Files

- `policy.yaml` - Main policy configuration (security rules, enforcement mode)
- `budget.yaml` - Change budget limits (blast radius control)
- `config.json` - Governance and enforcement settings
- `policy.manifest.json` - Signed manifest for tamper detection (optional)
- `audit.log` - Audit trail of policy decisions (auto-generated)
- `autonomy_audit/` - Autonomy engine audit logs (auto-generated)

## Environment Variables

Check `../.env.example` in the project root for required environment variables:

- **SCALPEL_MANIFEST_SECRET** - Required for cryptographic policy verification
- **SCALPEL_TOTP_SECRET** - Optional, for TOTP-based human verification

Copy `.env.example` to `.env` and update with your actual secrets.

## Getting Started

1. **Review `policy.yaml`** - Configure security rules and enforcement mode
2. **Review `budget.yaml`** - Set change budget limits (optional)
3. **Set environment variables** - Copy `.env.example` to `.env` and configure secrets
4. **Enable audit logging** - Track all policy decisions

## Documentation

- [Policy Engine Guide](https://github.com/tescolopio/code-scalpel/blob/main/docs/policy_engine_guide.md)
- [Change Budgeting Guide](https://github.com/tescolopio/code-scalpel/blob/main/docs/guides/change_budgeting.md)
- [Tamper Resistance](https://github.com/tescolopio/code-scalpel/blob/main/docs/security/tamper_resistance.md)

## Cryptographic Verification (Optional)

To enable tamper-resistant policies:

```bash
# Generate signed manifest
code-scalpel policy sign

# Verify integrity
code-scalpel policy verify
```

Learn more: https://github.com/tescolopio/code-scalpel
"""

# Template for config.json (main governance configuration)
CONFIG_JSON_TEMPLATE = """{
  "version": "1.0.0",
  "governance": {
    "blast_radius": {
      "max_files_per_operation": 10,
      "max_lines_changed": 500,
      "max_functions_modified": 5,
      "max_classes_modified": 3
    },
    "protected_paths": [
      "src/security/**",
      "src/auth/**",
      "*.key",
      "*.pem",
      ".env"
    ],
    "allowed_operations": [
      "analyze",
      "extract",
      "security_scan",
      "get_file_context",
      "get_symbol_references"
    ],
    "denied_operations": [
      "delete_file",
      "bulk_replace"
    ]
  },
  "enforcement": {
    "mode": "warn",
    "fail_on_violation": false,
    "log_violations": true
  },
  "audit": {
    "enabled": true,
    "log_file": ".code-scalpel/audit.log",
    "include_diffs": true,
    "cryptographic_signing": false
  },
  "integrity": {
    "verify_on_startup": true,
    "hash_algorithm": "sha256"
  }
}
"""

# .gitignore template for .code-scalpel/
GITIGNORE_TEMPLATE = """# Runtime audit logs
audit.log
autonomy_audit/

# Policy override responses (generated at runtime)
override_response.json

# Signed manifest (optional - commit if using tamper resistance)
# policy.manifest.json
"""

# .env.example template for environment variables documentation
ENV_EXAMPLE_TEMPLATE = """# Code Scalpel Environment Variables
# =====================================
# Copy this file to .env and update with your actual secrets
# DO NOT commit .env file to version control

# ----------------------------------------------------------------------------
# Policy Engine Secrets
# ----------------------------------------------------------------------------

# SCALPEL_MANIFEST_SECRET (REQUIRED for production with cryptographic verification)
# Used to sign and verify policy manifests to prevent tampering
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SCALPEL_MANIFEST_SECRET=your-64-char-hex-secret-key-here

# SCALPEL_TOTP_SECRET (Optional - for human override verification)
# Used for TOTP-based human verification when overriding policy decisions
# Generate with: python -c "import secrets; print(secrets.token_hex(16))"
# SCALPEL_TOTP_SECRET=your-32-char-hex-totp-secret-here

# ----------------------------------------------------------------------------
# Additional Configuration (Optional)
# ----------------------------------------------------------------------------

# Enable debug logging for policy engine
# DEBUG_POLICY_ENGINE=false

# Custom policy file location
# SCALPEL_POLICY_PATH=.code-scalpel/policy.yaml
"""
