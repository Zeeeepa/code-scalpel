# Security Tools

Advanced code security scanning tools for vulnerability detection, dependency analysis, and type system vulnerabilities.

**Tools in this category:**
- `security_scan` - Comprehensive vulnerability detection with OWASP focus
- `unified_sink_detect` - Polyglot sink detection across multiple languages
- `type_evaporation_scan` - Detect type system evaporation vulnerabilities
- `scan_dependencies` - Scan project dependencies for known vulnerabilities

---

## security_scan

Comprehensive vulnerability detection with support for multiple vulnerability types and OWASP categorization.

### Overview

`security_scan` analyzes code for security vulnerabilities including:
- OWASP Top 10 vulnerabilities (Community)
- Injection attacks (SQL, NoSQL, LDAP, command)
- XSS, CSRF, SSRF, and JWT vulnerabilities
- Secret detection (API keys, passwords)
- Cross-file taint analysis (Enterprise)
- Custom security policies (Enterprise)

**Use cases:**
- Find injection vulnerabilities in user-facing code
- Detect hardcoded secrets before committing
- Analyze security patterns across files
- Ensure OWASP compliance
- Generate security reports

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `code` | string | No | ✓ | ✓ | ✓ | Code to scan (or use `file_path`) |
| `file_path` | string | No | ✓ | ✓ | ✓ | Path to file to scan |
| `language` | string | No | ✓ | ✓ | ✓ | Programming language (auto-detected) |
| `include_context` | boolean | No | ✓ | ✓ | ✓ | Include surrounding code context |
| `confidence_threshold` | float | No | ✓ | ✓ | ✓ | Minimum confidence (0.0-1.0) |

#### Tier-Specific Constraints

**Community:**
- Max file size: 500 KB
- Max findings: 50 (before stopping)
- Vulnerability types: OWASP Top 10 only
- Features: Basic pattern matching, OWASP checks
- No false positive reduction

**Pro:**
- Max file size: Unlimited
- Max findings: Unlimited
- All vulnerability types
- Features: Sanitizer recognition, context-aware scanning, FP reduction, remediation suggestions

**Enterprise:**
- All Pro features
- Cross-file taint analysis
- Custom security policies
- Compliance rule checking
- Priority-based finding ordering
- Reachability analysis

### Output Specification

#### Response Structure (All Tiers)

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "security_scan",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "error": null,
  "data": {
    "success": true,
    "findings": [
      {
        "finding_id": "vuln-001",
        "type": "sql_injection",
        "severity": "high",
        "confidence": 0.95,
        "location": {
          "file": "app.py",
          "line": 42,
          "column": 10
        },
        "message": "User input directly concatenated into SQL query",
        "code_snippet": "query = f'SELECT * FROM users WHERE id={user_id}'",
        "remediation": "Use parameterized queries or ORM"
      }
    ],
    "summary": {
      "total_findings": 3,
      "by_severity": {
        "critical": 0,
        "high": 2,
        "medium": 1,
        "low": 0
      },
      "by_type": {
        "sql_injection": 2,
        "xss": 1
      }
    }
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Basic vulnerabilities** | ✓ | ✓ | ✓ |
| **Max findings** | 50 | Unlimited | Unlimited |
| **Max file size** | 500 KB | Unlimited | Unlimited |
| **Vulnerability types** | OWASP Top 10 | All | All |
| **SQL injection** | ✓ | ✓ | ✓ |
| **XSS detection** | ✓ | ✓ | ✓ |
| **Command injection** | ✓ | ✓ | ✓ |
| **NoSQL injection** | ✗ | ✓ | ✓ |
| **LDAP injection** | ✗ | ✓ | ✓ |
| **Secret detection** | ✗ | ✓ | ✓ |
| **Sanitizer recognition** | ✗ | ✓ | ✓ |
| **Context-aware scanning** | ✗ | ✓ | ✓ |
| **Cross-file taint** | ✗ | ✗ | ✓ |
| **Custom policies** | ✗ | ✗ | ✓ |
| **Reachability analysis** | ✗ | ✗ | ✓ |

### Error Handling

- `invalid_argument` - Invalid parameters
- `invalid_path` - File not found
- `too_large` - Exceeds file size (Community only)
- `not_implemented` - Language not supported
- `internal_error` - Scan error

### Example Requests & Responses

#### Example 1: SQL Injection Detection (Community)

**Request:**
```json
{
  "code": "user_id = request.get('id')\nquery = f'SELECT * FROM users WHERE id={user_id}'\ndb.execute(query)",
  "language": "python"
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "security_scan",
  "duration_ms": 120,
  "data": {
    "success": true,
    "findings": [
      {
        "finding_id": "sql-001",
        "type": "sql_injection",
        "severity": "high",
        "confidence": 0.98,
        "location": {
          "line": 2,
          "column": 25
        },
        "message": "User input directly interpolated into SQL query",
        "remediation": "Use parameterized queries: db.execute('SELECT * FROM users WHERE id=?', [user_id])"
      }
    ],
    "summary": {
      "total_findings": 1,
      "by_severity": {"high": 1},
      "by_type": {"sql_injection": 1}
    }
  }
}
```

### Performance Considerations

- **Community**: 200-800ms (500 KB max)
- **Pro**: 500-3000ms
- **Enterprise**: 1000-10000ms (cross-file analysis)

### Upgrade Paths

**Community → Pro:**
- Remove finding limits (50 → unlimited)
- All vulnerability types (not just OWASP Top 10)
- Sanitizer recognition and FP reduction
- Secret detection
- Unlimited file size

**Pro → Enterprise:**
- Cross-file taint analysis
- Custom security policies
- Compliance rule checking
- Priority finding ordering
- Reachability analysis

---

## unified_sink_detect

Polyglot sink detection across multiple programming languages.

### Overview

`unified_sink_detect` identifies security-critical sinks (data destinations) across:
- Python, JavaScript, TypeScript, Java (Community)
- Go, Rust (Pro)
- Extended languages (Pro+)
- Context-aware detection (Pro+)
- Framework-specific sinks (Pro+)

**Use cases:**
- Identify all SQL execution points in code
- Find shell command execution sinks
- Detect file operation sinks
- Locate XSS sinks (DOM manipulation)
- Map data flow to security-critical operations

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `code` | string | Yes | ✓ | ✓ | ✓ | Source code to analyze |
| `language` | string | Yes | ✓ | ✓ | ✓ | Programming language |
| `confidence_threshold` | float | No | ✓ | ✓ | ✓ | Minimum confidence (0.0-1.0) |

#### Tier-Specific Constraints

**Community:**
- Languages: Python, JavaScript, TypeScript, Java
- Max sinks: 50
- Sink types: Basic (SQL, shell, file operations, XSS)
- Features: Basic confidence scoring, CWE mapping

**Pro:**
- Languages: All Community + Go, Rust
- Max sinks: Unlimited
- Advanced confidence scoring
- Context-aware detection
- Framework-specific sinks
- Custom sink definitions

**Enterprise:**
- All Pro features + extended language support
- Custom sink definitions
- Organization-specific sinks
- Sink coverage analysis

### Output Specification

#### Response Structure

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "unified_sink_detect",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "sinks_found": 5,
    "language": "python",
    "sinks": [
      {
        "sink_id": "sink-001",
        "type": "sql_sink",
        "location": {
          "line": 42,
          "column": 10
        },
        "code": "db.execute(query)",
        "confidence": 0.95,
        "cwe": "CWE-89",
        "context": "database query execution"
      }
    ]
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Max sinks** | 50 | Unlimited | Unlimited |
| **Python** | ✓ | ✓ | ✓ |
| **JavaScript** | ✓ | ✓ | ✓ |
| **TypeScript** | ✓ | ✓ | ✓ |
| **Java** | ✓ | ✓ | ✓ |
| **Go** | ✗ | ✓ | ✓ |
| **Rust** | ✗ | ✓ | ✓ |
| **Framework-specific** | ✗ | ✓ | ✓ |
| **Custom definitions** | ✗ | ✓ | ✓ |

---

## type_evaporation_scan

Detect type system evaporation vulnerabilities between frontend and backend code.

### Overview

`type_evaporation_scan` identifies security gaps where type information is lost across frontend/backend boundaries:
- TypeScript `any` type detection (Community)
- Frontend-backend type correlation (Pro)
- Implicit `any` tracing (Pro)
- Network/library boundary analysis (Pro)
- Schema generation (Enterprise)
- Automated remediation (Enterprise)

**Use cases:**
- Find `any` types in TypeScript code
- Detect missing type validation at API boundaries
- Generate Zod/Pydantic schemas from type information
- Validate API contracts
- Enforce type safety across services

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `frontend_code` | string | Yes | ✓ | ✓ | ✓ | Frontend TypeScript code |
| `backend_code` | string | Yes | ✓ | ✓ | ✓ | Backend code (Python, etc.) |
| `frontend_file` | string | No | ✓ | ✓ | ✓ | Frontend file name |
| `backend_file` | string | No | ✓ | ✓ | ✓ | Backend file name |

#### Tier-Specific Constraints

**Community:**
- Frontend only analysis
- Max files: 50
- Basic TypeScript `any` detection
- Explicit `any` only

**Pro:**
- Frontend and backend analysis
- Max files: 500
- Implicit `any` tracing
- Network boundary analysis
- Library boundary analysis
- JSON parse tracking

**Enterprise:**
- Max files: Unlimited
- Schema generation (Zod, Pydantic)
- API contract validation
- Schema coverage metrics
- Automated remediation
- Custom type rules

### Output Specification

#### Response Structure

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "type_evaporation_scan",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "evaporation_issues": 3,
    "frontend_any_count": 2,
    "implicit_any_count": 1,
    "issues": [
      {
        "issue_id": "evap-001",
        "type": "explicit_any",
        "location": {
          "file": "api.ts",
          "line": 15
        },
        "message": "Explicit 'any' type used for API response",
        "code": "const response: any = await fetch('/api/user')"
      }
    ],
    "schema_suggestions": null
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Explicit any detection** | ✓ | ✓ | ✓ |
| **Frontend only** | ✓ | ✗ | ✗ |
| **Max files** | 50 | 500 | Unlimited |
| **Implicit any tracing** | ✗ | ✓ | ✓ |
| **Network boundary analysis** | ✗ | ✓ | ✓ |
| **JSON parse tracking** | ✗ | ✓ | ✓ |
| **Zod schema generation** | ✗ | ✗ | ✓ |
| **Pydantic generation** | ✗ | ✗ | ✓ |
| **API contract validation** | ✗ | ✗ | ✓ |
| **Remediation** | ✗ | ✗ | ✓ |

---

## scan_dependencies

Scan project dependencies for known vulnerabilities and security issues.

### Overview

`scan_dependencies` analyzes project dependencies using OSV and custom databases:
- OSV vulnerability detection
- License compliance checking (Pro+)
- Typosquatting detection (Pro+)
- Reachability analysis (Pro+)
- Supply chain risk scoring (Pro+)
- Automated remediation (Enterprise)
- Custom policies (Enterprise)

**Use cases:**
- Find vulnerable dependencies before deployment
- Check license compatibility
- Detect supply chain attacks (typosquatting)
- Get update recommendations
- Ensure compliance with organizational policies

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `path` | string | No | ✓ | ✓ | ✓ | Path to dependency file or project root |
| `project_root` | string | No | ✓ | ✓ | ✓ | Project root for scanning |
| `scan_vulnerabilities` | boolean | No | ✓ | ✓ | ✓ | Scan for CVEs (default: true) |
| `include_dev` | boolean | No | ✓ | ✓ | ✓ | Include dev dependencies (default: true) |
| `timeout` | float | No | ✓ | ✓ | ✓ | Scan timeout in seconds (default: 30) |

#### Tier-Specific Constraints

**Community:**
- Max dependencies: 50
- OSV lookup: Enabled
- Features: Basic vulnerability detection, severity scoring

**Pro:**
- Max dependencies: Unlimited
- OSV lookup: Enabled
- Reachability analysis
- License compliance
- Typosquatting detection
- Supply chain risk scoring
- Update recommendations

**Enterprise:**
- All Pro features
- Custom vulnerability database
- Private dependency scanning
- Automated remediation
- Policy-based blocking
- Compliance reporting

### Output Specification

#### Response Structure

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "scan_dependencies",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "vulnerabilities": [
      {
        "vulnerability_id": "vuln-001",
        "package": "requests",
        "version": "2.25.0",
        "severity": "high",
        "cvss_score": 7.5,
        "description": "Session fixation vulnerability",
        "affected_versions": ["<2.28.0"],
        "patched_version": "2.28.0",
        "remediation": "Upgrade to 2.28.0 or later"
      }
    ],
    "summary": {
      "total_dependencies": 25,
      "vulnerable_dependencies": 1,
      "critical_count": 0,
      "high_count": 1,
      "medium_count": 0
    }
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Max dependencies** | 50 | Unlimited | Unlimited |
| **Vulnerability detection** | ✓ | ✓ | ✓ |
| **License compliance** | ✗ | ✓ | ✓ |
| **Typosquatting detection** | ✗ | ✓ | ✓ |
| **Reachability analysis** | ✗ | ✓ | ✓ |
| **Update recommendations** | ✗ | ✓ | ✓ |
| **Custom database** | ✗ | ✗ | ✓ |
| **Automated remediation** | ✗ | ✗ | ✓ |
| **Policy-based blocking** | ✗ | ✗ | ✓ |

### Error Handling

- `invalid_argument` - Invalid parameters
- `invalid_path` - Path not found
- `timeout` - Scan timeout
- `resource_exhausted` - Too many dependencies (Community: max 50)
- `internal_error` - Scan error

### Example Requests & Responses

#### Example 1: Vulnerability Scan (Community)

**Request:**
```json
{
  "path": "/project/requirements.txt",
  "scan_vulnerabilities": true
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "scan_dependencies",
  "duration_ms": 1200,
  "data": {
    "success": true,
    "vulnerabilities": [
      {
        "package": "requests",
        "version": "2.25.0",
        "severity": "high",
        "patched_version": "2.28.0"
      }
    ],
    "summary": {
      "total_dependencies": 12,
      "vulnerable_dependencies": 1,
      "high_count": 1
    }
  }
}
```

### Performance Considerations

- **Community**: 500-2000ms (50 deps limit)
- **Pro**: 1000-5000ms (unlimited deps)
- **Enterprise**: 2000-10000ms (custom database, policies)

---

## Response Envelope Specification

All tools in this category return responses wrapped in a standard envelope:

```json
{
  "tier": "community|pro|enterprise|null",
  "tool_version": "1.x.x",
  "tool_id": "security_scan|unified_sink_detect|type_evaporation_scan|scan_dependencies",
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

- **`cross_file_security_scan`** (graph-tools.md) - Cross-file security analysis
- **`analyze_code`** (analysis-tools.md) - Code analysis complementing security scans
- **`get_cross_file_dependencies`** (graph-tools.md) - Map dependencies for security context
