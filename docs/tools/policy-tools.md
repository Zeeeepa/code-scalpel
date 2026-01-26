# Policy Tools

Governance, compliance, and policy validation tools for enforcing organizational standards and security boundaries.

**Tools in this category:**
- `validate_paths` - Validate file paths with Docker environment detection
- `verify_policy_integrity` - Verify policy file integrity using cryptographic signatures
- `code_policy_check` - Check code compliance with organizational policies and standards

---

## validate_paths

Validate file paths with support for Docker environments and path alias resolution.

### Overview

`validate_paths` checks path accessibility and provides actionable guidance for path issues:
- Path existence and accessibility validation
- Docker environment detection
- Workspace root resolution
- Path alias resolution (Pro+)
- Dynamic import resolution (Pro+)
- Security validation (Enterprise)

**Use cases:**
- Validate paths before running file operations
- Detect Docker environment and provide volume mount suggestions
- Resolve path aliases in TypeScript/webpack configs
- Check permission issues
- Test path traversal security boundaries

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `paths` | array[string] | Yes | ✓ | ✓ | ✓ | List of paths to validate |
| `project_root` | string | No | ✓ | ✓ | ✓ | Project root for relative path resolution |

#### Tier-Specific Constraints

**Community:**
- Max paths: 100
- Core features: Path accessibility, Docker detection, workspace root detection
- Docker volume mount suggestions
- Actionable error messages

**Pro:**
- Max paths: Unlimited
- All Community features + path alias resolution
- TypeScript tsconfig.json path support
- Webpack alias support
- Dynamic import resolution
- Extended language support

**Enterprise:**
- Max paths: Unlimited
- All Pro features + security features
- Permission checks
- Path traversal simulation
- Symbolic path testing
- Security boundary testing

### Output Specification

#### Response Structure (All Tiers)

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "validate_paths",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "error": null,
  "data": {
    "success": true,
    "valid_paths": 4,
    "invalid_paths": 1,
    "docker_detected": true,
    "results": [
      {
        "path": "/src/utils.py",
        "valid": true,
        "accessible": true,
        "type": "file",
        "docker_info": {
          "in_docker": true,
          "volume_mount": "/app/src"
        }
      },
      {
        "path": "/nonexistent.py",
        "valid": false,
        "error": "Path does not exist",
        "suggestion": "Did you mean '/src/utils.py'?"
      }
    ],
    "docker_environment": {
      "detected": true,
      "container_id": "abc123...",
      "volume_mounts": ["/app:/app", "/data:/data"]
    },
    "workspace_root": "/app"
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Path accessibility** | ✓ | ✓ | ✓ |
| **Docker detection** | ✓ | ✓ | ✓ |
| **Volume suggestions** | ✓ | ✓ | ✓ |
| **Max paths** | 100 | Unlimited | Unlimited |
| **Alias resolution** | ✗ | ✓ | ✓ |
| **tsconfig.json support** | ✗ | ✓ | ✓ |
| **Webpack aliases** | ✗ | ✓ | ✓ |
| **Dynamic imports** | ✗ | ✓ | ✓ |
| **Permission checks** | ✗ | ✗ | ✓ |
| **Path traversal testing** | ✗ | ✗ | ✓ |

### Error Handling

- `invalid_argument` - Invalid path list
- `invalid_path` - Path does not exist or not accessible
- `forbidden` - Permission denied
- `resource_exhausted` - Too many paths (Community: max 100)
- `internal_error` - Validation error

### Example Requests & Responses

#### Example 1: Path Validation (Community)

**Request:**
```json
{
  "paths": ["/src/utils.py", "/src/tests/test_utils.py", "/nonexistent.py"],
  "project_root": "/app"
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "validate_paths",
  "duration_ms": 45,
  "data": {
    "success": true,
    "valid_paths": 2,
    "invalid_paths": 1,
    "docker_detected": true,
    "results": [
      {
        "path": "/src/utils.py",
        "valid": true,
        "accessible": true,
        "type": "file"
      },
      {
        "path": "/src/tests/test_utils.py",
        "valid": true,
        "accessible": true,
        "type": "file"
      },
      {
        "path": "/nonexistent.py",
        "valid": false,
        "error": "Path does not exist",
        "suggestion": "Relative path from project root: src/utils.py?"
      }
    ],
    "workspace_root": "/app"
  }
}
```

#### Example 2: Docker Environment (Community)

**Request:**
```json
{
  "paths": ["/app/src", "/data/config.json"],
  "project_root": "/app"
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "validate_paths",
  "duration_ms": 60,
  "data": {
    "success": true,
    "valid_paths": 2,
    "docker_detected": true,
    "docker_environment": {
      "detected": true,
      "container_id": "abc1234567...",
      "volume_mounts": [
        "/app:/app",
        "/data:/data"
      ]
    },
    "results": [
      {
        "path": "/app/src",
        "valid": true,
        "accessible": true,
        "docker_info": {
          "in_docker": true,
          "volume_mount": "/app:/app"
        }
      }
    ]
  }
}
```

#### Example 3: Alias Resolution (Pro)

**Request:**
```json
{
  "paths": ["@/utils", "@/components/Button"],
  "project_root": "/app"
}
```

**Response:**
```json
{
  "tier": "pro",
  "tool_id": "validate_paths",
  "duration_ms": 120,
  "data": {
    "success": true,
    "valid_paths": 2,
    "results": [
      {
        "path": "@/utils",
        "valid": true,
        "resolved_path": "/app/src/utils",
        "alias_source": "tsconfig.json",
        "accessible": true
      }
    ]
  }
}
```

### Performance Considerations

- **Community**: 30-100ms (100 paths max)
- **Pro**: 50-200ms (unlimited paths, with alias resolution)
- **Enterprise**: 100-500ms (security checks)

### Upgrade Paths

**Community → Pro:**
- Unlimited path validation (100 → unlimited)
- Alias resolution (tsconfig.json, webpack)
- Extended language support
- Dynamic import resolution

**Pro → Enterprise:**
- Security validation
- Permission checks
- Path traversal simulation
- Symbolic link testing

---

## verify_policy_integrity

Verify policy file integrity using cryptographic signatures and tamper detection.

### Overview

`verify_policy_integrity` validates that policy files have not been modified:
- Basic policy file structure validation (Community)
- Cryptographic signature validation (Pro+)
- Tamper detection (Pro+)
- Full integrity checking (Enterprise)
- Audit logging (Enterprise)

**Use cases:**
- Verify policy configuration before applying
- Detect unauthorized policy modifications
- Ensure policy compliance across organization
- Audit policy changes with logging
- Maintain policy integrity in distributed teams

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `policy_dir` | string | No | ✓ | ✓ | ✓ | Directory containing policy files |
| `manifest_source` | string | No | ✓ | ✓ | ✓ | `file` (default) or `server` |

#### Tier-Specific Constraints

**Community:**
- Basic verification only
- No signature validation
- No tamper detection

**Pro:**
- Cryptographic signature validation enabled
- Tamper detection enabled
- Hash-based integrity checks

**Enterprise:**
- Full integrity checking
- Audit logging of all verifications
- Detailed change history

### Output Specification

#### Response Structure

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "verify_policy_integrity",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "integrity_verified": true,
    "policy_files": 3,
    "verified_files": 3,
    "tampering_detected": false,
    "results": [
      {
        "file": "security.policy",
        "valid": true,
        "signature_valid": true,
        "last_modified": "2025-01-20T10:30:00Z",
        "hash": "sha256:abc123..."
      }
    ]
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Basic verification** | ✓ | ✓ | ✓ |
| **Signature validation** | ✗ | ✓ | ✓ |
| **Tamper detection** | ✗ | ✓ | ✓ |
| **Audit logging** | ✗ | ✗ | ✓ |

---

## code_policy_check

Check code compliance with organizational policies and coding standards.

### Overview

`code_policy_check` validates code against organizational policies:
- Style guide checking (PEP8, ESLint)
- Pattern validation
- Best practice analysis (Pro+)
- Security pattern detection (Pro+)
- Custom policy rules (Pro+)
- Compliance auditing (Enterprise)
- Standards certifications (Enterprise): HIPAA, SOC2, GDPR, PCI-DSS

**Use cases:**
- Enforce coding standards across projects
- Check compliance with organizational policies
- Verify HIPAA/SOC2/GDPR compliance
- Detect security anti-patterns
- Validate best practices
- Generate compliance audit reports

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `paths` | array[string] | Yes | ✓ | ✓ | ✓ | Files to check |
| `rules` | array[string] | No | ✓ | ✓ | ✓ | Specific rules to apply |

#### Tier-Specific Constraints

**Community:**
- Max files: 100
- Max rules: 50
- Style guide checking
- Basic patterns only
- PEP8 and ESLint rules

**Pro:**
- Max files: 1,000
- Max rules: 200
- All Community features
- Best practice analysis
- Async/await error patterns
- Security patterns
- Custom rule support

**Enterprise:**
- Max files: Unlimited
- Max rules: Unlimited
- All Pro features
- Compliance auditing
- Standards certifications (HIPAA, SOC2, GDPR, PCI-DSS)
- PDF certification generation
- Audit trail

### Output Specification

#### Response Structure

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "code_policy_check",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "files_checked": 5,
    "issues_found": 8,
    "compliance_score": 92.5,
    "issues": [
      {
        "file": "app.py",
        "line": 42,
        "rule": "pep8_line_too_long",
        "severity": "warning",
        "message": "Line too long (95 > 79 characters)",
        "suggestion": "Break line into multiple lines"
      }
    ],
    "compliance": {
      "standards": ["PEP8"],
      "compliant": true,
      "score": 92.5
    }
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Max files** | 100 | 1,000 | Unlimited |
| **Max rules** | 50 | 200 | Unlimited |
| **Style guide** | ✓ | ✓ | ✓ |
| **Best practices** | ✗ | ✓ | ✓ |
| **Security patterns** | ✗ | ✓ | ✓ |
| **Custom rules** | ✗ | ✓ | ✓ |
| **Compliance auditing** | ✗ | ✗ | ✓ |
| **HIPAA checks** | ✗ | ✗ | ✓ |
| **SOC2 checks** | ✗ | ✗ | ✓ |
| **GDPR checks** | ✗ | ✗ | ✓ |
| **PCI-DSS checks** | ✗ | ✗ | ✓ |
| **PDF certification** | ✗ | ✗ | ✓ |

### Error Handling

- `invalid_argument` - Invalid paths or rules
- `invalid_path` - Path not found
- `resource_exhausted` - Too many files (Community: max 100; Pro: max 1000)
- `not_implemented` - Rule not supported
- `internal_error` - Check error

### Example Requests & Responses

#### Example 1: Style Guide Check (Community)

**Request:**
```json
{
  "paths": ["/src/app.py", "/src/utils.py"],
  "rules": ["pep8", "line_length"]
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "code_policy_check",
  "duration_ms": 180,
  "data": {
    "success": true,
    "files_checked": 2,
    "issues_found": 3,
    "compliance_score": 85.0,
    "issues": [
      {
        "file": "/src/app.py",
        "line": 42,
        "rule": "pep8_line_too_long",
        "severity": "warning",
        "message": "Line too long (95 > 79 characters)"
      }
    ]
  }
}
```

#### Example 2: Security Patterns (Pro)

**Request:**
```json
{
  "paths": ["/src/auth.py", "/src/api.py"],
  "rules": ["security_patterns", "async_errors"]
}
```

**Response:**
```json
{
  "tier": "pro",
  "tool_id": "code_policy_check",
  "duration_ms": 420,
  "data": {
    "success": true,
    "files_checked": 2,
    "issues_found": 2,
    "compliance_score": 88.5,
    "issues": [
      {
        "file": "/src/auth.py",
        "line": 28,
        "rule": "security_hardcoded_password",
        "severity": "critical",
        "message": "Hardcoded password detected",
        "suggestion": "Use environment variables or config files"
      }
    ]
  }
}
```

#### Example 3: Compliance Audit (Enterprise)

**Request:**
```json
{
  "paths": ["/src"],
  "rules": ["hipaa", "gdpr", "pci_dss"]
}
```

**Response:**
```json
{
  "tier": "enterprise",
  "tool_id": "code_policy_check",
  "duration_ms": 2500,
  "data": {
    "success": true,
    "files_checked": 42,
    "issues_found": 0,
    "compliance_score": 100.0,
    "compliance": {
      "standards": ["HIPAA", "GDPR", "PCI-DSS"],
      "hipaa_compliant": true,
      "gdpr_compliant": true,
      "pci_dss_compliant": true,
      "pdf_certification_available": true,
      "audit_trail": [
        "2025-01-20 10:30:00 - HIPAA check passed",
        "2025-01-20 10:30:30 - GDPR check passed"
      ]
    }
  }
}
```

### Performance Considerations

- **Community**: 150-500ms (100 files max)
- **Pro**: 300-1500ms (1000 files max)
- **Enterprise**: 1000-5000ms (unlimited files, compliance checks)

### Upgrade Paths

**Community → Pro:**
- Increase file limit (100 → 1,000)
- Add best practice analysis
- Security pattern detection
- Custom rule support
- Rule limit increase (50 → 200)

**Pro → Enterprise:**
- Unlimited file and rule limits
- Compliance certifications (HIPAA, SOC2, GDPR, PCI-DSS)
- PDF certification generation
- Full audit trail

---

## Response Envelope Specification

All tools in this category return responses wrapped in a standard envelope:

```json
{
  "tier": "community|pro|enterprise|null",
  "tool_version": "1.x.x",
  "tool_id": "validate_paths|verify_policy_integrity|code_policy_check",
  "request_id": "uuid-v4",
  "capabilities": ["envelope-v1"],
  "duration_ms": 1234,
  "error": null,
  "warnings": [],
  "upgrade_hints": [],
  "data": { /* tool-specific */ }
}
```

See `README.md` for complete envelope specification.

## Related Tools

- **`security_scan`** (security-tools.md) - Scan code for vulnerabilities
- **`analyze_code`** (analysis-tools.md) - Analyze code structure and metrics
- **`crawl_project`** (context-tools.md) - Understand project structure for policy application
