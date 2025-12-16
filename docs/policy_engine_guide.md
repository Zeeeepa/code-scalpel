# Policy Engine Guide (v2.5.0 Guardian)

<!-- [20251216_DOCS] v2.5.0 Guardian - Policy Engine documentation -->

## Overview

The Policy Engine provides enterprise-grade, tamper-resistant policy enforcement for AI agents. It ensures that agents cannot circumvent security controls, modify policy files, or perform unauthorized operations without proper human oversight.

**Key Features:**
- **Tamper-Resistant Policy Enforcement**: SHA-256 integrity verification prevents unauthorized policy modifications
- **Read-Only Policy Files**: Automatic file permission locking prevents agent tampering
- **TOTP-Based Human Override**: Time-limited, one-time-use override codes for emergency operations
- **HMAC-Signed Audit Logging**: Cryptographically signed, append-only audit trail
- **Fail-Closed Security**: System denies all operations when policy tampering is detected

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Policy Engine                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │ TamperResistance │◄──────►│   AuditLog       │          │
│  │                  │        │                  │          │
│  │ • Integrity      │        │ • HMAC Signing   │          │
│  │ • File Locking   │        │ • Append-Only    │          │
│  │ • Override       │        │ • Verification   │          │
│  └──────────────────┘        └──────────────────┘          │
│           │                           │                     │
│           ▼                           ▼                     │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  Policy Files    │        │   Audit Logs     │          │
│  │  (Read-Only)     │        │  (Signed)        │          │
│  └──────────────────┘        └──────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Installation

The policy engine is included in Code Scalpel v2.5.0+:

```bash
pip install code-scalpel>=2.5.0
```

## Quick Start

### Basic Usage

```python
from pathlib import Path
from code_scalpel.policy_engine import (
    TamperResistance,
    AuditLog,
    Operation,
    PolicyDecision,
)

# Initialize tamper resistance
tr = TamperResistance(policy_path=".scalpel/policy.yaml")

# Verify policy integrity
tr.verify_policy_integrity()

# Check if operation violates policy
operation = Operation(
    type="file_write",
    affected_files=[Path(".scalpel/policy.yaml")]
)

# This will raise PolicyModificationError
tr.prevent_policy_modification(operation)

# Create audit log
audit_log = AuditLog(log_path=".scalpel/audit.log")

# Record events
audit_log.record_event(
    event_type="POLICY_CHECK",
    severity="LOW",
    details={"operation": "file_read"}
)

# Verify log integrity
audit_log.verify_integrity()
```

## Core Components

### 1. TamperResistance

The `TamperResistance` class provides policy enforcement and integrity verification.

#### Features

- **Policy Integrity Verification**: SHA-256 hashing detects unauthorized modifications
- **File Locking**: Automatically sets policy files to read-only (0o444)
- **Modification Prevention**: Blocks operations targeting protected files
- **Human Override System**: TOTP-based approval for policy violations

#### API

```python
class TamperResistance:
    def __init__(self, policy_path: str = ".scalpel/policy.yaml"):
        """Initialize tamper resistance with policy file path."""
        
    def verify_policy_integrity(self) -> bool:
        """
        Verify policy file has not been tampered with.
        
        Returns:
            True if policy is intact
            
        Raises:
            TamperDetectedError: If tampering detected
        """
        
    def prevent_policy_modification(self, operation: Operation) -> bool:
        """
        Prevent agent from modifying policy files.
        
        Args:
            operation: Operation to check
            
        Returns:
            True if allowed
            
        Raises:
            PolicyModificationError: If modification blocked
        """
        
    def require_human_override(
        self,
        operation: Operation,
        policy_decision: PolicyDecision,
        timeout_seconds: int = 300
    ) -> OverrideDecision:
        """
        Require human approval for policy override.
        
        Args:
            operation: Operation requiring override
            policy_decision: Policy decision being overridden
            timeout_seconds: Timeout for human response
            
        Returns:
            OverrideDecision with approval status
        """
```

### 2. AuditLog

The `AuditLog` class provides tamper-resistant event logging with cryptographic signatures.

#### Features

- **HMAC-SHA256 Signing**: Every event is cryptographically signed
- **Append-Only**: Log file cannot be modified or deleted
- **Integrity Verification**: Detect tampering attempts
- **Event Filtering**: Query events by type, severity, or limit

#### API

```python
class AuditLog:
    def __init__(self, log_path: str = ".scalpel/audit.log"):
        """Initialize audit log with file path."""
        
    def record_event(
        self,
        event_type: str,
        severity: str,
        details: dict
    ) -> None:
        """
        Record security event to tamper-resistant log.
        
        Args:
            event_type: Type of security event
            severity: Event severity (LOW, MEDIUM, HIGH, CRITICAL)
            details: Event details dictionary
        """
        
    def verify_integrity(self) -> bool:
        """
        Verify audit log has not been tampered with.
        
        Returns:
            True if log is intact
            
        Raises:
            TamperDetectedError: If tampering detected
        """
        
    def get_events(
        self,
        event_type: str = None,
        severity: str = None,
        limit: int = None
    ) -> list:
        """
        Retrieve events from audit log.
        
        Args:
            event_type: Filter by event type (optional)
            severity: Filter by severity (optional)
            limit: Maximum number of events (optional)
            
        Returns:
            List of events matching filters
        """
```

### 3. Data Models

#### Operation

```python
@dataclass
class Operation:
    """Represents an operation subject to policy enforcement."""
    
    type: str  # e.g., "file_write", "file_delete"
    affected_files: List[Path]
    metadata: dict
    timestamp: datetime
```

#### PolicyDecision

```python
@dataclass
class PolicyDecision:
    """Result of policy evaluation."""
    
    allowed: bool
    violated_policies: List[str]
    reason: Optional[str]
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
```

#### OverrideDecision

```python
@dataclass
class OverrideDecision:
    """Result of human override request."""
    
    approved: bool
    reason: str
    override_id: Optional[str]
    expires_at: Optional[datetime]
    justification: Optional[str]
    approved_by: Optional[str]
```

## Security Model

### Threat Model

The policy engine defends against:

1. **Agent Tampering**: Agents modifying policy files to bypass restrictions
2. **Log Tampering**: Agents modifying audit logs to hide malicious activity
3. **Policy Bypass**: Agents circumventing policy checks
4. **Override Reuse**: Reusing expired or one-time override codes

### Security Guarantees

| Threat | Mitigation | Verification |
|--------|-----------|-------------|
| Policy File Modification | Read-only file permissions (0o444) | File stat check |
| Policy Content Tampering | SHA-256 integrity verification | Hash comparison |
| Audit Log Tampering | HMAC-SHA256 signatures | Signature verification |
| Override Reuse | One-time use tracking | Override ID set |
| Override Expiry | Time-based expiration | Timestamp check |

### Protected File Paths

The following paths are automatically protected:

- `.scalpel/policy.yaml`
- `.scalpel/budget.yaml`
- `.scalpel/overrides.yaml`
- Any file starting with `.scalpel/`
- `scalpel.policy.yaml`
- `budget.yaml`
- `overrides.yaml`

## Configuration

### Environment Variables

- **SCALPEL_AUDIT_SECRET**: Secret key for HMAC signing (default: "default-secret")
- **SCALPEL_TOTP_SECRET**: Secret key for TOTP verification (default: "default-totp-secret")

**Production Deployment:**

```bash
# Generate secure random secrets
export SCALPEL_AUDIT_SECRET=$(openssl rand -hex 32)
export SCALPEL_TOTP_SECRET=$(openssl rand -hex 32)
```

### Policy File Format

```yaml
# .scalpel/policy.yaml
version: "1.0"

# Policy enforcement settings
enforcement:
  enabled: true
  fail_closed: true  # Deny all on tamper detection

# Complexity limits
limits:
  max_complexity: 10
  max_file_size: 10000
  max_changes_per_operation: 100

# Protected resources
protected:
  files:
    - "*.config"
    - "*.env"
    - ".scalpel/*"
  
  operations:
    - "delete"
    - "chmod"
    - "chown"
```

## Advanced Usage

### Human Override Workflow

```python
from code_scalpel.policy_engine import (
    TamperResistance,
    Operation,
    PolicyDecision,
)

# Initialize
tr = TamperResistance()

# Create operation that violates policy
operation = Operation(
    type="code_modification",
    affected_files=[Path("src/critical.py")],
    metadata={"complexity": 50}
)

# Policy violation
policy_decision = PolicyDecision(
    allowed=False,
    violated_policies=["max_complexity"],
    reason="Complexity exceeds limit",
    severity="HIGH"
)

# Request human override
decision = tr.require_human_override(
    operation=operation,
    policy_decision=policy_decision,
    timeout_seconds=300  # 5 minutes
)

if decision.approved:
    print(f"Override approved by {decision.approved_by}")
    print(f"Valid until: {decision.expires_at}")
    
    # Check override is still valid before proceeding
    if tr.is_override_valid(decision.override_id, decision.expires_at):
        # Proceed with operation
        pass
```

### Custom Event Types

```python
# Define custom event types
CUSTOM_EVENTS = {
    "CUSTOM_POLICY_CHECK": "MEDIUM",
    "CUSTOM_VIOLATION": "HIGH",
    "CUSTOM_OVERRIDE": "CRITICAL",
}

# Record custom events
audit_log.record_event(
    event_type="CUSTOM_POLICY_CHECK",
    severity=CUSTOM_EVENTS["CUSTOM_POLICY_CHECK"],
    details={
        "policy": "custom_security_check",
        "result": "passed",
        "metadata": {"check_version": "1.0"}
    }
)
```

### Batch Policy Checks

```python
# Check multiple operations
operations = [
    Operation(type="file_write", affected_files=[Path("file1.py")]),
    Operation(type="file_write", affected_files=[Path("file2.py")]),
    Operation(type="file_delete", affected_files=[Path("file3.py")]),
]

results = []
for op in operations:
    try:
        tr.prevent_policy_modification(op)
        results.append((op, True, None))
    except PolicyModificationError as e:
        results.append((op, False, str(e)))

# Process results
for op, allowed, error in results:
    if allowed:
        print(f"✓ {op.type} on {op.affected_files} allowed")
    else:
        print(f"✗ {op.type} blocked: {error}")
```

## Integration Examples

### With MCP Server

```python
from code_scalpel.mcp.server import MCPServer
from code_scalpel.policy_engine import TamperResistance, Operation

class PolicyEnforcedMCPServer(MCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tamper_resistance = TamperResistance()
        
    def handle_tool_call(self, tool_name, args):
        # Verify policy integrity before each operation
        self.tamper_resistance.verify_policy_integrity()
        
        # Check if operation is allowed
        operation = Operation(
            type=tool_name,
            affected_files=self._extract_files(args),
            metadata={"tool": tool_name, "args": args}
        )
        
        self.tamper_resistance.prevent_policy_modification(operation)
        
        # Proceed with operation
        return super().handle_tool_call(tool_name, args)
```

### With Agent Frameworks

```python
from code_scalpel.policy_engine import TamperResistance, AuditLog

class PolicyEnforcedAgent:
    def __init__(self):
        self.tamper_resistance = TamperResistance()
        self.audit_log = AuditLog()
        
    def execute_task(self, task):
        # Log task execution
        self.audit_log.record_event(
            event_type="TASK_EXECUTION",
            severity="MEDIUM",
            details={"task": task.description}
        )
        
        # Verify policy compliance
        self.tamper_resistance.verify_policy_integrity()
        
        # Execute task with monitoring
        try:
            result = self._do_execute(task)
            
            self.audit_log.record_event(
                event_type="TASK_SUCCESS",
                severity="LOW",
                details={"task": task.description, "result": result}
            )
            
            return result
            
        except Exception as e:
            self.audit_log.record_event(
                event_type="TASK_FAILURE",
                severity="HIGH",
                details={"task": task.description, "error": str(e)}
            )
            raise
```

## Troubleshooting

### Issue: Policy File Not Locked

**Symptom**: Policy file can be modified despite initialization

**Solution**: 
- Ensure policy file exists before creating TamperResistance instance
- Check file permissions: `stat -c "%a" .scalpel/policy.yaml`
- Should show `444` (read-only)

### Issue: Tampering False Positive

**Symptom**: TamperDetectedError raised on startup

**Cause**: Policy file was modified after initialization

**Solution**:
- Verify policy file content is correct
- If legitimate change, recreate TamperResistance instance
- Check for external processes modifying files

### Issue: Audit Log Signature Mismatch

**Symptom**: verify_integrity() fails with tampering error

**Cause**: SCALPEL_AUDIT_SECRET environment variable changed

**Solution**:
- Use consistent secret across restarts
- Store secret in secure keyring
- Do not rotate secret without recreating audit log

### Issue: Override Timeout

**Symptom**: All override requests timeout immediately

**Cause**: Response file mechanism not implemented

**Solution**:
- This is expected in basic implementation
- Integrate with UI or notification system
- Implement custom `_wait_for_human_response` method

## Best Practices

1. **Secret Management**
   - Use environment variables for secrets
   - Rotate secrets regularly
   - Never commit secrets to version control

2. **Policy File Management**
   - Version control policy files separately
   - Require code review for policy changes
   - Test policy changes in staging first

3. **Audit Log Retention**
   - Archive audit logs regularly
   - Implement log rotation
   - Verify integrity before archiving

4. **Override System**
   - Require justification for all overrides
   - Set appropriate timeout values
   - Monitor override frequency

5. **Testing**
   - Test policy enforcement in CI/CD
   - Verify tampering detection works
   - Validate audit log integrity

## Performance Considerations

| Operation | Complexity | Performance Impact |
|-----------|-----------|-------------------|
| Policy Integrity Check | O(n) file size | Minimal (< 1ms for typical files) |
| Audit Event Recording | O(1) | Minimal (< 1ms) |
| Audit Log Verification | O(n) events | Linear with log size |
| File Locking | O(1) | Negligible |
| Override Generation | O(1) | Minimal (< 1ms) |

**Recommendations:**
- Verify policy integrity on startup, not per-operation
- Archive old audit logs to keep verification fast
- Use efficient serialization for audit events

## See Also

- [Examples: policy_engine_example.py](../examples/policy_engine_example.py)
- [Security Analysis Guide](./security_analysis_guide.md)
- [MCP Server Documentation](./mcp_server_guide.md)
- [Development Roadmap: v2.5.0 Guardian](../DEVELOPMENT_ROADMAP.md)
