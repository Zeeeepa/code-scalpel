# Demo: "Your AI Safety Net: Audit What Changed"

**Persona**: Vibe Coder
**Pillar**: Governable AI
**Tier**: Pro ($49/month)
**Duration**: 6 minutes
**Fixture**: Use audit.jsonl from `.code-scalpel/audit.jsonl`

## Scenario

AI agent makes multiple code changes. Developer reviews audit trail to see exactly what was modified, when, and why.

## Tools Used

- `update_symbol` (with audit trail)
- Audit log inspection

## Recording Script

### Step 1: The Problem (0:00-1:00)

- "AI agents modify code, but how do you track changes?"
- Show scenario: overnight agent run updated 15 functions
- On-screen: "What changed? Why? Can I trust it?"

### Step 2: AI Makes Changes (1:00-2:30)

- Run agent task: "Optimize all database queries for performance"
- Code Scalpel makes changes via `update_symbol`
- Each change logged to `.code-scalpel/audit.jsonl`

### Step 3: Inspect Audit Trail (2:30-4:30)

- Open audit.jsonl
- Show JSON entries:
  ```json
  {
    "timestamp": "2026-02-08T14:23:00Z",
    "tool": "update_symbol",
    "file": "api/users.py",
    "symbol": "get_user_by_id",
    "operation": "update",
    "backup_path": ".code-scalpel/backups/2026-02-08/...",
    "tier": "pro",
    "request_id": "req_abc123"
  }
  ```
- Highlight: every change is traceable

### Step 4: Rollback Demo (4:30-5:00)

- One change looks suspicious
- Use backup path to compare: `diff original backup`
- Decision: rollback that one function
- Other 14 changes: approved

### Step 5: Enterprise Upgrade Preview (5:00-5:30)

- "Pro tier logs changes"
- "Enterprise adds: compliance reports, cryptographic signatures, PDF exports"
- On-screen: SOC2 audit report example

### Step 6: Key Benefit (5:30-6:00)

- "Trust but verify"
- "Full audit trail in Pro tier"
- "Required for regulated industries"

## Expected Outputs

- audit.jsonl with timestamped entries
- Backup files in `.code-scalpel/backups/`
- Diff view of changes
- Rollback capability demonstration

## Audit Log Format

```json
{
  "timestamp": "ISO-8601",
  "tool": "update_symbol|extract_code|...",
  "file": "path/to/file.py",
  "symbol": "function_or_class_name",
  "operation": "create|update|delete",
  "backup_path": "relative/path/to/backup",
  "tier": "community|pro|enterprise",
  "request_id": "unique_request_identifier",
  "user": "developer_username",
  "metadata": {
    "reason": "Optimize database query",
    "confidence": 0.95
  }
}
```

## Key Talking Points

- "AI agents are powerful but need oversight"
- "Pro tier logs every change with automatic backups"
- "Trust but verify - full audit trail for compliance"
- "Rollback capability for suspicious changes"
- "Required for regulated industries (finance, healthcare)"

## Tier Comparison

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|------------|
| Audit logging | ❌ | ✓ | ✓ |
| Automatic backups | ❌ | ✓ | ✓ |
| Rollback capability | ❌ | ✓ | ✓ |
| Compliance reports | ❌ | ❌ | ✓ |
| Cryptographic signatures | ❌ | ❌ | ✓ |
| PDF exports | ❌ | ❌ | ✓ |
