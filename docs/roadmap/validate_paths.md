# validate_paths Tool Roadmap

**Tool Name:** `validate_paths`  
**Tool Version:** v1.0  
**Code Scalpel Version:** v3.3.1  
**Current Status:** Stable  
**Primary Module:** `src/code_scalpel/mcp/server.py` (lines 17438-17680)  
**Tier Availability:** All tiers (Community, Pro, Enterprise)

---

## Configuration Files

| File | Purpose |
|------|---------|
| `src/code_scalpel/licensing/features.py` | Tier capability definitions |
| `.code-scalpel/limits.toml` | Numeric limits (max_paths) |
| `.code-scalpel/response_config.json` | Output filtering (exclude validation_metadata, stat_results) |

---

## Overview

The `validate_paths` tool checks if file paths are accessible before running operations. Essential for Docker deployments where volume mounts must be configured correctly.

**Why AI Agents Need This:**
- **Pre-flight validation:** Verify paths before expensive operations
- **Docker awareness:** Detect container vs host path issues automatically
- **Clear guidance:** Actionable error messages with mount suggestions
- **Batch efficiency:** Validate multiple paths in one call
- **Deployment debugging:** Essential for containerized AI agent deployments

---

## Research Queries for Future Development

### Foundational Research
| Topic | Query | Purpose |
|-------|-------|---------|
| Path Resolution | "cross-platform path resolution algorithms" | Better OS support |
| Docker Volumes | "docker volume mount best practices troubleshooting" | Improve suggestions |
| Filesystem | "filesystem permission checking techniques" | Permission detection |
| Network Storage | "network filesystem latency detection timeout" | Network drive support |

### Platform-Specific Research
| Topic | Query | Purpose |
|-------|-------|---------|
| Windows | "windows UNC path handling best practices" | Windows support |
| Linux | "linux symbolic link resolution security" | Symlink handling |
| macOS | "macos file system case sensitivity handling" | macOS quirks |
| Container | "container filesystem overlay mount detection" | Container detection |

### Advanced Techniques
| Topic | Query | Purpose |
|-------|-------|---------|
| Auto-Mount | "automated docker volume mount configuration" | Smart mounting |
| Cloud Storage | "cloud storage path validation S3 Azure GCS" | Cloud support |
| Kubernetes | "kubernetes persistent volume path validation" | K8s integration |
| Performance | "filesystem operation caching strategies" | Fast validation |

---

## Current Capabilities (v1.0)

### All Tiers
| Capability | Config Name |
|------------|-------------|
| ✅ Path accessibility checking | `path_accessibility_checking` |
| ✅ Docker environment detection | `docker_environment_detection` |
| ✅ Workspace root detection | `workspace_root_detection` |
| ✅ Actionable error messages | `actionable_error_messages` |
| ✅ Docker volume mount suggestions | `docker_volume_mount_suggestions` |
| ✅ Batch path validation | `batch_path_validation` |

### Community Tier Limits
- `max_paths`: 100 (from limits.toml)

### Pro/Enterprise Tier Limits
- `max_paths`: unlimited

---

## Return Model: PathValidationResult

```python
class PathValidationResult(BaseModel):
    # Core fields (All Tiers)
    success: bool                              # Whether validation succeeded
    paths_checked: int                         # Number of paths validated
    all_valid: bool                            # Quick check if all accessible
    results: list[PathResult]                  # Per-path validation results
    docker_detected: bool                      # Running in container
    workspace_root: str | None                 # Detected workspace root
    suggestions: list[str]                     # Mount/fix suggestions
    
    # Pro Tier
    permission_details: dict[str, PermInfo]    # Read/write/execute per path
    symlink_resolution: dict[str, str]         # Symlink target paths
    mount_recommendations: list[MountRec]      # Docker volume suggestions
    
    # Enterprise Tier
    policy_violations: list[PolicyViolation]   # Path policy violations
    audit_log: list[AuditEntry]                # Path access attempts logged
    compliance_status: str                     # Policy compliance status
    
    error: str | None                          # Error message if failed
```

### PathResult Model

```python
class PathResult(BaseModel):
    path: str                                  # The validated path
    exists: bool                               # Path exists
    accessible: bool                           # Can be accessed
    is_file: bool                              # Is a file (vs directory)
    is_directory: bool                         # Is a directory
    error_message: str | None                  # Why inaccessible
    suggestion: str | None                     # How to fix
```

---

## Usage Examples

### Community Tier
```python
result = await validate_paths(
    paths=["/app/src/main.py", "/app/data/config.json"]
)
# Returns: all_valid, results per path, docker_detected, suggestions
# Max 100 paths
```

### Pro Tier
```python
result = await validate_paths(
    paths=["/app/src", "/app/data"],
    check_permissions=True,
    resolve_symlinks=True
)
# Additional: permission_details, symlink_resolution, mount_recommendations
# Unlimited paths
```

### Enterprise Tier
```python
result = await validate_paths(
    paths=["/sensitive/data", "/app/logs"],
    enforce_policy=True,
    audit=True
)
# Additional: policy_violations, audit_log, compliance_status
```

---

## Integration Points

### Related Tools
| Tool | Relationship |
|------|--------------|
| `crawl_project` | Validate project root before crawling |
| `extract_code` | Validate file paths before extraction |
| `update_symbol` | Ensure file accessible before update |
| `security_scan` | Validate file paths before scanning |

### Export Formats
| Format | Status | Use Case |
|--------|--------|----------|
| **JSON** | ✅ v1.0 | Programmatic results |
| **Text** | ✅ v1.0 | Human-readable output |
| **Docker Compose** | 🔄 v1.2 | Volume mount YAML |

---

## Competitive Analysis

| Tool | Strengths | Weaknesses | Our Differentiation |
|------|-----------|------------|---------------------|
| **os.path.exists** | Built-in | No suggestions | Actionable guidance |
| **pathlib** | Modern API | No Docker awareness | Container detection |
| **Docker CLI** | Authoritative | Manual checking | Automated batch |
| **test -f/-d** | Simple | No cross-platform | Cross-platform |
| **fs.access (Node)** | JS native | Node only | Multi-language |

---

## MCP Request/Response Examples

### MCP Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "mcp_code-scalpel_validate_paths",
    "arguments": {
      "paths": ["/app/src/main.py", "/app/data/config.json"]
    }
  },
  "id": 1
}
```

### Community Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "paths_checked": 2,
    "all_valid": false,
    "results": [
      {
        "path": "/app/src/main.py",
        "exists": true,
        "accessible": true,
        "is_file": true,
        "is_directory": false,
        "error_message": null,
        "suggestion": null
      },
      {
        "path": "/app/data/config.json",
        "exists": false,
        "accessible": false,
        "is_file": false,
        "is_directory": false,
        "error_message": "Path does not exist",
        "suggestion": "Check if volume mount is configured for /app/data"
      }
    ],
    "docker_detected": true,
    "workspace_root": "/app",
    "suggestions": [
      "Docker detected: Ensure volume mount for '/app/data' in docker-compose.yml:",
      "  volumes:",
      "    - ./data:/app/data"
    ],
    "permission_details": null,
    "symlink_resolution": null,
    "mount_recommendations": null,
    "policy_violations": null,
    "audit_log": null,
    "compliance_status": null,
    "error": null
  },
  "id": 1
}
```

### Pro Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "paths_checked": 2,
    "all_valid": true,
    "results": [
      {
        "path": "/app/src/main.py",
        "exists": true,
        "accessible": true,
        "is_file": true,
        "is_directory": false,
        "error_message": null,
        "suggestion": null
      },
      {
        "path": "/app/data/config.json",
        "exists": true,
        "accessible": true,
        "is_file": true,
        "is_directory": false,
        "error_message": null,
        "suggestion": null
      }
    ],
    "docker_detected": true,
    "workspace_root": "/app",
    "suggestions": [],
    "permission_details": {
      "/app/src/main.py": {
        "readable": true,
        "writable": true,
        "executable": false,
        "owner": "app",
        "group": "app",
        "mode": "0644"
      },
      "/app/data/config.json": {
        "readable": true,
        "writable": false,
        "executable": false,
        "owner": "root",
        "group": "root",
        "mode": "0444"
      }
    },
    "symlink_resolution": {
      "/app/src/main.py": "/app/src/main.py",
      "/app/data/config.json": "/mnt/config/app.json"
    },
    "mount_recommendations": [
      {
        "source_path": "/home/user/project/src",
        "container_path": "/app/src",
        "type": "bind",
        "status": "mounted"
      },
      {
        "source_path": "/home/user/project/data",
        "container_path": "/app/data",
        "type": "bind",
        "status": "mounted"
      }
    ],
    "policy_violations": null,
    "audit_log": null,
    "compliance_status": null,
    "error": null
  },
  "id": 1
}
```

### Enterprise Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "paths_checked": 2,
    "all_valid": true,
    "results": [
      {
        "path": "/app/src/main.py",
        "exists": true,
        "accessible": true,
        "is_file": true,
        "is_directory": false,
        "error_message": null,
        "suggestion": null
      },
      {
        "path": "/app/data/config.json",
        "exists": true,
        "accessible": true,
        "is_file": true,
        "is_directory": false,
        "error_message": null,
        "suggestion": null
      }
    ],
    "docker_detected": true,
    "workspace_root": "/app",
    "suggestions": [],
    "permission_details": {
      "/app/src/main.py": {
        "readable": true,
        "writable": true,
        "executable": false
      },
      "/app/data/config.json": {
        "readable": true,
        "writable": false,
        "executable": false
      }
    },
    "symlink_resolution": {},
    "mount_recommendations": [],
    "policy_violations": [],
    "audit_log": [
      {
        "timestamp": "2025-12-29T14:30:22Z",
        "action": "path_validation",
        "paths": ["/app/src/main.py", "/app/data/config.json"],
        "result": "all_valid",
        "user": "ai-agent-001",
        "audit_id": "audit-path-20251229-143022-abc123"
      }
    ],
    "compliance_status": "compliant",
    "error": null
  },
  "id": 1
}
```

### Enterprise Tier Response (Policy Violation)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "paths_checked": 2,
    "all_valid": false,
    "results": [
      {
        "path": "/app/src/main.py",
        "exists": true,
        "accessible": true,
        "is_file": true,
        "is_directory": false,
        "error_message": null,
        "suggestion": null
      },
      {
        "path": "/etc/passwd",
        "exists": true,
        "accessible": true,
        "is_file": true,
        "is_directory": false,
        "error_message": "Path blocked by policy",
        "suggestion": "Access to /etc/passwd is restricted by security policy"
      }
    ],
    "docker_detected": true,
    "workspace_root": "/app",
    "suggestions": [
      "Remove restricted path /etc/passwd from request"
    ],
    "permission_details": {},
    "symlink_resolution": {},
    "mount_recommendations": [],
    "policy_violations": [
      {
        "path": "/etc/passwd",
        "policy": "restricted-paths",
        "rule": "no-system-files",
        "severity": "critical",
        "message": "Access to system files is not permitted"
      }
    ],
    "audit_log": [
      {
        "timestamp": "2025-12-29T14:30:25Z",
        "action": "path_validation",
        "paths": ["/app/src/main.py", "/etc/passwd"],
        "result": "policy_violation",
        "violation_count": 1,
        "audit_id": "audit-path-20251229-143025-def456"
      }
    ],
    "compliance_status": "violation",
    "error": null
  },
  "id": 1
}
```

---

## Roadmap

### v1.1 (Q1 2026): Enhanced Validation

#### All Tiers
- [ ] Permission checking (read/write/execute)
- [ ] Symlink resolution
- [ ] Network path support
- [ ] Path normalization suggestions

#### Pro Tier
- [ ] Automated mount detection
- [ ] Volume mount recommendations
- [ ] Path conflict detection

#### Enterprise Tier
- [ ] Custom validation rules
- [ ] Policy-based path restrictions
- [ ] Audit logging for path access

### v1.2 (Q2 2026): Integration Features

#### Community Tier
- [ ] GitHub Actions integration
- [ ] GitLab CI helpers
- [ ] Docker Compose validation

#### Pro Tier
- [ ] Kubernetes volume validation
- [ ] Cloud storage path validation
- [ ] Remote filesystem support

#### Enterprise Tier
- [ ] Multi-cloud path validation
- [ ] VPN/VPC path checking
- [ ] Compliance-based path rules

### v1.3 (Q3 2026): Performance & Reliability

#### All Tiers
- [ ] Faster path validation (<10ms)
- [ ] Batch optimization
- [ ] Caching for repeated checks

#### Pro Tier
- [ ] Async path validation
- [ ] Parallel validation

#### Enterprise Tier
- [ ] Distributed path validation
- [ ] Real-time path monitoring

### v1.4 (Q4 2026): Advanced Features

#### Pro Tier
- [ ] Path recommendation engine
- [ ] Automated mount configuration
- [ ] Path migration helpers

#### Enterprise Tier
- [ ] Custom validation plugins
- [ ] Infrastructure-as-code generation
- [ ] Automated remediation

---

## Known Issues & Limitations

### Current Limitations
- **Windows paths:** Limited Windows UNC path support
- **Network drives:** Network drive latency may cause timeouts
- **Container paths:** Complex container path mapping not fully detected

### Planned Fixes
- v1.1: Full Windows path support
- v1.2: Network drive optimization
- v1.3: Better container detection

---

## Success Metrics

### Performance Targets
- **Validation time:** <50ms per path
- **Accuracy:** >99% correct accessibility detection
- **Docker detection:** 100% accurate

### Adoption Metrics
- **Usage:** 200K+ validations per month by Q4 2026
- **Error prevention:** 90% of path errors caught early

---

## Dependencies

### Internal Dependencies
- None

### External Dependencies
- Python `os` and `pathlib` modules

---

## Breaking Changes

None planned for v1.x series.

---

**Last Updated:** December 30, 2025  
**Next Review:** March 31, 2026
