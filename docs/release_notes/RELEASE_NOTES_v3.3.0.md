# Release Notes - v3.3.0

**Release Date:** December 25, 2025  
**Version:** 3.3.0 "Clean Slate"  
**Release Type:** Minor (Breaking Change + Usability Enhancement)

---

## Executive Summary

Version 3.3.0 marks a major milestone with two significant changes:
1. **Breaking Change**: Removal of backward compatibility stubs from `symbolic_execution_tools/`, completing the project reorganization
2. **Usability Enhancement**: Auto-generation of policy integrity manifests, making security features accessible to all users

---

## 🚨 Breaking Changes

### Backward Compatibility Stub Removal

**What Changed:**
- Removed 14 stub files from `src/code_scalpel/symbolic_execution_tools/`
- Old import paths no longer work
- All imports must use new canonical locations

**Migration Required:**
```python
# OLD (no longer works):
from code_scalpel.symbolic_execution_tools.taint_tracker import TaintTracker
from code_scalpel.symbolic_execution_tools.security_analyzer import SecurityAnalyzer

# NEW (required):
from code_scalpel.security.analyzers import TaintTracker
from code_scalpel.security.analyzers import SecurityAnalyzer
```

**Full Migration Guide:**
See "Migration Guide" section below for complete search/replace patterns.

---

## ✨ New Features

### 1. Policy Integrity Manifest Auto-Generation

**What Changed:**
- `code-scalpel init` now automatically generates cryptographic policy manifests
- Auto-generates secure HMAC-SHA256 secret keys (256 bits entropy)
- Creates `.env` file with secret for local development
- Validates all configuration files (JSON, YAML, Rego) for syntax errors
- Provides clear security guidance for production deployments

**New CLI Commands:**
```bash
# Initialize project with policy manifest
code-scalpel init

# Verify policy integrity
code-scalpel verify-policies --dir .code-scalpel --manifest-source file

# Regenerate manifest after policy changes
code-scalpel regenerate-manifest --dir .code-scalpel --signed-by "your-name"
```

**What You Get:**
```
.code-scalpel/
├── policy_manifest.json     # ← NEW: Cryptographically signed manifest
├── .gitignore              # Updated to exclude .env
├── config.json
├── policy.yaml
├── budget.yaml
└── policies/...

.env                         # ← NEW: Contains SCALPEL_MANIFEST_SECRET
```

**Before:**
```python
# Manual manifest generation was complex:
from code_scalpel.policy_engine.crypto_verify import CryptographicPolicyVerifier
import secrets

secret = secrets.token_hex(32)  # User had to do this
manifest = CryptographicPolicyVerifier.create_manifest(...)
# No validation, no guidance
```

**After:**
```bash
# Single command does everything:
$ code-scalpel init

[SUCCESS] Configuration directory created
[VALIDATION] Checked 10 configuration files: ✅ All valid
[SECURITY] Policy Integrity Manifest Generated:
   ✅ Cryptographic manifest created: policy_manifest.json
   ✅ HMAC secret saved to: .env
   
Next steps for production:
   1. Copy SCALPEL_MANIFEST_SECRET from .env to CI/CD secrets
   2. Commit policy_manifest.json to git
   3. Test with: code-scalpel verify-policies
```

### 2. Configuration File Validation

**What Changed:**
- `code-scalpel init` now validates all config files during creation
- Checks JSON, YAML, and Rego files for syntax errors
- Reports validation results with actionable error messages

**Validation Coverage:**
- ✅ JSON files: `config.json`, `policy_manifest.json`
- ✅ YAML files: `policy.yaml`, `budget.yaml`, `dev-governance.yaml`, `project-structure.yaml`
- ✅ Rego files: All `.rego` policy files in subdirectories

---

## 🐛 Bug Fixes

### Policy Manifest Format Compatibility

**Fixed**: Multiple format incompatibilities in `verify_policy_integrity` that caused verification failures

**Root Cause**: Mismatches between manifest formats (flat vs nested dicts, missing prefixes, null signatures)

**12 Fixes Applied** to `crypto_verify.py`:
1. Added `Any` type support for flexible manifest formats
2. Changed `files` type to handle both flat strings and nested dicts
3. Made `signed_by` optional with default value
4. Updated hash extraction to handle both formats
5. Fixed signature verification to use canonical JSON
6. Added "hmac-sha256:" prefix stripping
7. Added null signature handling
8. Standardized hash format with "sha256:" prefix
9. Fixed manifest creation signature format

**Impact**: `verify_policy_integrity` now works reliably with all manifest formats

---

## Migration Guide

### Stub Removal Migration

**Automated Migration (Recommended):**

```bash
# Search and replace all old imports
find . -name "*.py" -type f -exec sed -i \
  -e 's/from code_scalpel\.symbolic_execution_tools\.taint_tracker/from code_scalpel.security.analyzers.taint_tracker/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.security_analyzer/from code_scalpel.security.analyzers.security_analyzer/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.unified_sink_detector/from code_scalpel.security.analyzers.unified_sink_detector/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.cross_file_taint/from code_scalpel.security.analyzers.cross_file_taint/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.secret_scanner/from code_scalpel.security.secrets.secret_scanner/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.type_evaporation_detector/from code_scalpel.security.type_safety.type_evaporation_detector/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.vulnerability_scanner/from code_scalpel.security.dependencies.vulnerability_scanner/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.schema_drift_detector/from code_scalpel.integrations.protocol_analyzers.schema.drift_detector/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.grpc_contract_analyzer/from code_scalpel.integrations.protocol_analyzers.grpc.contract_analyzer/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.graphql_schema_tracker/from code_scalpel.integrations.protocol_analyzers.graphql.schema_tracker/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.kafka_taint_tracker/from code_scalpel.integrations.protocol_analyzers.kafka.taint_tracker/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.frontend_input_tracker/from code_scalpel.integrations.protocol_analyzers.frontend.input_tracker/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.ml_vulnerability_predictor/from code_scalpel.security.ml.ml_vulnerability_predictor/g' \
  -e 's/from code_scalpel\.symbolic_execution_tools\.sanitizer_analyzer/from code_scalpel.security.sanitization.sanitizer_analyzer/g' \
  {} \;
```

**Import Mapping Table:**

| Old Import | New Import |
|------------|------------|
| `symbolic_execution_tools.taint_tracker` | `security.analyzers.taint_tracker` |
| `symbolic_execution_tools.security_analyzer` | `security.analyzers.security_analyzer` |
| `symbolic_execution_tools.unified_sink_detector` | `security.analyzers.unified_sink_detector` |
| `symbolic_execution_tools.cross_file_taint` | `security.analyzers.cross_file_taint` |
| `symbolic_execution_tools.secret_scanner` | `security.secrets.secret_scanner` |
| `symbolic_execution_tools.type_evaporation_detector` | `security.type_safety.type_evaporation_detector` |
| `symbolic_execution_tools.vulnerability_scanner` | `security.dependencies.vulnerability_scanner` |
| `symbolic_execution_tools.schema_drift_detector` | `integrations.protocol_analyzers.schema.drift_detector` |
| `symbolic_execution_tools.grpc_contract_analyzer` | `integrations.protocol_analyzers.grpc.contract_analyzer` |
| `symbolic_execution_tools.graphql_schema_tracker` | `integrations.protocol_analyzers.graphql.schema_tracker` |
| `symbolic_execution_tools.kafka_taint_tracker` | `integrations.protocol_analyzers.kafka.taint_tracker` |
| `symbolic_execution_tools.frontend_input_tracker` | `integrations.protocol_analyzers.frontend.input_tracker` |
| `symbolic_execution_tools.ml_vulnerability_predictor` | `security.ml.ml_vulnerability_predictor` |
| `symbolic_execution_tools.sanitizer_analyzer` | `security.sanitization.sanitizer_analyzer` |

### Policy Integrity Migration

**No Migration Required**. Existing projects can start using the new features:

```bash
# Regenerate manifest for existing project
export SCALPEL_MANIFEST_SECRET=<generate-or-use-existing>
code-scalpel regenerate-manifest --dir .code-scalpel
```

---

## Statistics

### Test Results
| Metric | Value |
|--------|-------|
| Total Tests | 4,431 |
| Passed | 4,431 |
| Skipped | 17 |
| Pass Rate | 100% |

### Code Changes
| Category | Count |
|----------|-------|
| Files Modified | 180+ |
| Files Deleted | 14 (stub files) |
| Import Statements Updated | 400+ |
| New Lines Added | 242 (policy features) |

### Quality Gates
| Check | Status |
|-------|--------|
| Black Formatting | ✅ PASSED |
| Ruff Linting | ✅ PASSED |
| Pyright Type Checking | ✅ PASSED (0 errors) |
| Bandit Security Scan | ✅ PASSED (163 low - baseline) |
| pip-audit Dependencies | ✅ PASSED |
| Package Build | ✅ PASSED |
| twine check | ✅ PASSED |
| MCP Contracts (stdio) | ✅ PASSED |
| MCP Tool Testing | ✅ 20/20 PASSED (100%) |

---

## Upgrade Instructions

```bash
# Upgrade to v3.3.0
pip install --upgrade code-scalpel==3.3.0

# Verify version
python -c "import code_scalpel; print(code_scalpel.__version__)"  # Should print: 3.3.0

# Update imports (run migration script above)

# Initialize new policy features (optional)
code-scalpel init  # Will create manifest if not exists
```

---

## Acknowledgments

- **Ninja Warrior Test Suite**: Identified critical policy verification bugs
- **Community Feedback**: Highlighted usability issues with manual manifest generation
- **Contributors**: All contributors who helped with testing and migration

---

## Links

- **GitHub Release**: https://github.com/tescolopio/code-scalpel/releases/tag/v3.3.0
- **PyPI Package**: https://pypi.org/project/code-scalpel/3.3.0/
- **Documentation**: https://github.com/tescolopio/code-scalpel/blob/main/README.md
- **Changelog**: https://github.com/tescolopio/code-scalpel/blob/main/CHANGELOG.md

---
| Metric | Value |
|--------|-------|
| Total Tests | 4,431 |
| Passed | 4,431 |
| Skipped | 17 |
| Pass Rate | 100% |

### Quality Gates
| Check | Status |
|-------|--------|
| Black Formatting | ✅ PASSED |
| Ruff Linting | ✅ PASSED (32 E402 expected in compat stubs) |
| Pyright Type Checking | ✅ PASSED (0 errors) |
| Bandit Security Scan | ✅ PASSED (No Medium/High issues) |
| pip-audit Dependencies | ✅ PASSED (No vulnerabilities) |
| Package Build | ✅ PASSED |
| twine check | ✅ PASSED |

### Package Size
| Artifact | Size |
|----------|------|
| Wheel | code_scalpel-3.3.0-py3-none-any.whl |
| Source | code_scalpel-3.3.0.tar.gz |

### Lines of Code
| Category | Count |
|----------|-------|
| Lines Scanned (Bandit) | 102,972 |
| Files | 520 |

---

## Migration Guide

### Import Path Changes

| Old Path | New Path |
|----------|----------|
| `code_scalpel.code_analyzer` | `code_scalpel.analysis` |
| `code_scalpel.project_crawler` | `code_scalpel.analysis` |
| `code_scalpel.surgical_extractor` | `code_scalpel.surgery` |
| `code_scalpel.unified_extractor` | `code_scalpel.surgery` |
| `code_scalpel.surgical_patcher` | `code_scalpel.surgery` |
| `code_scalpel.symbolic_execution_tools.taint_tracker` | `code_scalpel.security.analyzers` |
| `code_scalpel.symbolic_execution_tools.security_analyzer` | `code_scalpel.security.analyzers` |
| `code_scalpel.symbolic_execution_tools.unified_sink_detector` | `code_scalpel.security.analyzers` |
| `code_scalpel.symbolic_execution_tools.type_evaporation_detector` | `code_scalpel.security.type_safety` |
| `code_scalpel.symbolic_execution_tools.vulnerability_scanner` | `code_scalpel.security.dependencies` |
| `code_scalpel.symbolic_execution_tools.graphql_schema_tracker` | `code_scalpel.integrations.protocol_analyzers.graphql` |
| `code_scalpel.symbolic_execution_tools.grpc_contract_analyzer` | `code_scalpel.integrations.protocol_analyzers.grpc` |
| `code_scalpel.symbolic_execution_tools.kafka_taint_tracker` | `code_scalpel.integrations.protocol_analyzers.kafka` |
| `code_scalpel.symbolic_execution_tools.schema_drift_detector` | `code_scalpel.integrations.protocol_analyzers.schema` |
| `code_scalpel.symbolic_execution_tools.frontend_input_tracker` | `code_scalpel.integrations.protocol_analyzers.frontend` |
| `code_scalpel.config.governance_config` | `code_scalpel.governance` |
| `code_scalpel.ast_tools.osv_client` | `code_scalpel.security.dependencies` |

### Deprecation Timeline

- **v3.3.0** - Deprecation warnings added
- **v4.0.0** - Old import paths will be removed

---

## Known Issues

- 1 Pyright warning (invalid escape sequence in path_resolver.py) - cosmetic only

---

## Contributors

- Tim Escolopio (@tescolopio)

---

## Upgrade Instructions

```bash
# Upgrade from PyPI (when published)
pip install --upgrade code-scalpel==3.3.0

# Or install from source
git checkout v3.3.0
pip install -e .
```

---

## Full Changelog

See [CHANGELOG.md](../../CHANGELOG.md) for complete history.
