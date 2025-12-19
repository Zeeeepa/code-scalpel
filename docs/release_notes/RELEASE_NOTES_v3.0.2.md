# Code Scalpel v3.0.2 "Configuration Init" Release Notes

**Release Date:** December 19, 2025  
**Codename:** Configuration Init  
**Previous Version:** v3.0.1 "Autonomy"  

---

## Executive Summary

Code Scalpel v3.0.2 introduces the `code-scalpel init` command, dramatically improving the first-run experience for new users. When installing Code Scalpel via `pip install code-scalpel`, users can now run a single command to initialize a complete `.code-scalpel` configuration directory with all necessary governance files.

**Key Highlight:** Zero-to-configured in one command.

---

## What's New

### 1. `code-scalpel init` Command

A new CLI subcommand that creates the `.code-scalpel` configuration directory with sensible defaults.

**Usage:**
```bash
# Initialize in current directory
code-scalpel init

# Initialize in a specific directory
code-scalpel init --dir /path/to/project

# Check help
code-scalpel init --help
```

**Output:**
```
Code Scalpel Configuration Initialization
============================================================

[SUCCESS] Configuration directory created:
   Path: /your/project/.code-scalpel

Created 5 files:
   - policy.yaml
   - budget.yaml
   - README.md
   - .gitignore
   - config.json

Next steps:
   1. Review policy.yaml to configure security rules
   2. Review budget.yaml to set change limits
   3. Read README.md for configuration guidance
   4. Add .code-scalpel/ to version control (optional)
```

### 2. Configuration Templates

The init command creates five comprehensive configuration files:

| File | Purpose | Key Settings |
|------|---------|--------------|
| `config.json` | Main governance configuration | Blast radius limits, protected paths, allowed/denied operations |
| `policy.yaml` | Security rules | SQL injection, XSS, command injection blocking |
| `budget.yaml` | Change budgeting | Max files, lines, functions per operation |
| `README.md` | User guide | Configuration overview, links to documentation |
| `.gitignore` | Runtime exclusions | Excludes audit.log, temporary files |

### 3. Idempotent Behavior

Running `init` on an existing configuration directory is safe:

```bash
$ code-scalpel init
[OK] Configuration directory already exists.
   Path: /your/project/.code-scalpel

Use --force to attempt reinitialization.
```

---

## Files Created

### New Source Files

| File | Purpose |
|------|---------|
| `src/code_scalpel/config/templates.py` | Template strings for all configuration files |
| `src/code_scalpel/config/init_config.py` | `init_config_dir()` function implementation |

### Modified Files

| File | Change |
|------|--------|
| `src/code_scalpel/cli.py` | Added `init` subparser and `init_configuration()` handler |
| `src/code_scalpel/config/__init__.py` | Export `init_config_dir` |

---

## Template Contents

### config.json (Main Governance)

```json
{
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
      "analyze", "extract", "security_scan",
      "get_file_context", "get_symbol_references"
    ],
    "denied_operations": [
      "delete_file", "bulk_replace"
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
```

### policy.yaml (Security Rules)

```yaml
version: "1.0.0"
enforcement: "warn"  # Options: "warn", "block", "disabled"

security:
  sql_injection: true
  command_injection: true
  path_traversal: true
  xss: true

budgeting:
  enabled: false
  max_files_per_session: 10
  max_lines_per_file: 500
  max_total_changes: 1000

audit:
  enabled: true
  log_file: ".code-scalpel/audit.log"
```

---

## Metrics

| Metric | Value |
|--------|-------|
| Tests Passing | 4,133 |
| Tests Skipped | 20 (optional dependencies) |
| Combined Coverage | 94% |
| MCP Tools | 19 |
| New CLI Commands | 1 (`init`) |
| Configuration Files Generated | 5 |

---

## Upgrade Guide

### From v3.0.1

No breaking changes. Simply update:

```bash
pip install --upgrade code-scalpel
```

Then initialize configuration in your projects:

```bash
cd /your/project
code-scalpel init
```

### New Installations

```bash
pip install code-scalpel
cd /your/project
code-scalpel init
```

---

## Known Limitations

1. **No `--force` reinitialize**: The `--force` flag is accepted but does not overwrite existing files. Use manual deletion if you need to regenerate templates.

2. **Templates are static**: Generated templates contain example values. Review and customize for your project's needs.

---

## Contributors

- 3D Tech Solutions LLC - Core development and documentation

---

## Links

- [GitHub Repository](https://github.com/tescolopio/code-scalpel)
- [PyPI Package](https://pypi.org/project/code-scalpel/)
- [Documentation](https://github.com/tescolopio/code-scalpel/blob/main/docs/INDEX.md)
- [Configuration Guide](https://github.com/tescolopio/code-scalpel/blob/main/docs/configuration/governance_config_schema.md)

---

## What's Next

**v3.1.0 "Gatekeeper"** (Q1 2026):
- CI/CD enforcement via GitHub Actions
- Cryptographic proof verification
- Bot detection for AI-generated PRs

**v4.0.0 "Swarm"** (H2 2026):
- Multi-agent collaboration
- Shared graph memory
- Conflict resolution engine
