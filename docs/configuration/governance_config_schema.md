# Governance Configuration Schema

<!-- [20251218_FEATURE] Immutable configuration for Change Budgeting and Blast Radius control -->

## Overview

This document defines the configuration schema for governance controls including Change Budgeting and Blast Radius limits. These settings can be configured in `.vscode/mcp.json` (workspace-specific) or environment variables (system-wide), with cryptographic integrity protection to prevent tampering.

## Configuration Locations

### 1. VS Code MCP Configuration (Workspace-Specific)

**File:** `.vscode/mcp.json`

```json
{
  "servers": {
    "code-scalpel": {
      "type": "stdio",
      "command": "/path/to/code-scalpel",
      "args": ["mcp", "--root", "${workspaceFolder}"],
      "env": {
        "SCALPEL_CONFIG": "${workspaceFolder}/.scalpel/config.json",
        "SCALPEL_CONFIG_HASH": "sha256:abc123..."
      }
    }
  }
}
```

### 2. Scalpel Configuration File (Immutable)

**File:** `.scalpel/config.json`

```json
{
  "version": "3.0.0",
  "governance": {
    "change_budgeting": {
      "enabled": true,
      "max_lines_per_change": 500,
      "max_files_per_change": 10,
      "max_complexity_delta": 50,
      "require_justification": true,
      "budget_refresh_interval_hours": 24
    },
    "blast_radius": {
      "enabled": true,
      "max_affected_functions": 20,
      "max_affected_classes": 5,
      "max_call_graph_depth": 3,
      "warn_on_public_api_changes": true,
      "block_on_critical_paths": true
    },
    "autonomy_constraints": {
      "max_autonomous_iterations": 10,
      "require_approval_for_breaking_changes": true,
      "require_approval_for_security_changes": true,
      "sandbox_execution_required": true
    },
    "audit": {
      "log_all_changes": true,
      "log_rejected_changes": true,
      "retention_days": 90
    }
  }
}
```

### 3. Environment Variables (System-Wide Override)

Override individual settings via environment variables with `SCALPEL_` prefix:

```bash
# Change Budgeting
export SCALPEL_CHANGE_BUDGET_MAX_LINES=500
export SCALPEL_CHANGE_BUDGET_MAX_FILES=10
export SCALPEL_CHANGE_BUDGET_MAX_COMPLEXITY_DELTA=50

# Blast Radius
export SCALPEL_BLAST_RADIUS_MAX_FUNCTIONS=20
export SCALPEL_BLAST_RADIUS_MAX_CLASSES=5
export SCALPEL_BLAST_RADIUS_MAX_DEPTH=3

# Autonomy
export SCALPEL_MAX_AUTONOMOUS_ITERATIONS=10
export SCALPEL_REQUIRE_APPROVAL_BREAKING=true
export SCALPEL_REQUIRE_APPROVAL_SECURITY=true
```

## Immutability Protection

### Configuration Hash Validation

To prevent tampering, configuration files use SHA-256 hash verification:

```python
# Generate hash for config.json
import hashlib
import json

with open('.scalpel/config.json', 'rb') as f:
    config_hash = hashlib.sha256(f.read()).hexdigest()
    print(f"SCALPEL_CONFIG_HASH=sha256:{config_hash}")
```

Set the hash in `.vscode/mcp.json`:

```json
{
  "servers": {
    "code-scalpel": {
      "env": {
        "SCALPEL_CONFIG_HASH": "sha256:abc123..."
      }
    }
  }
}
```

### Signed Configuration (Enterprise)

For enterprise deployments, use HMAC-SHA256 signed configurations:

```bash
# Generate signed config
export SCALPEL_CONFIG_SECRET="your-secret-key"
python -c "
import hmac
import hashlib
with open('.scalpel/config.json', 'rb') as f:
    sig = hmac.new(b'your-secret-key', f.read(), hashlib.sha256).hexdigest()
    print(f'SCALPEL_CONFIG_SIGNATURE={sig}')
"
```

## Configuration Schema Reference

### Change Budgeting Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable change budgeting |
| `max_lines_per_change` | integer | `500` | Maximum lines modified per change |
| `max_files_per_change` | integer | `10` | Maximum files modified per change |
| `max_complexity_delta` | integer | `50` | Maximum cyclomatic complexity increase |
| `require_justification` | boolean | `true` | Require reason for large changes |
| `budget_refresh_interval_hours` | integer | `24` | Budget reset interval |

### Blast Radius Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable blast radius control |
| `max_affected_functions` | integer | `20` | Max functions impacted by change |
| `max_affected_classes` | integer | `5` | Max classes impacted by change |
| `max_call_graph_depth` | integer | `3` | Max depth for impact analysis |
| `warn_on_public_api_changes` | boolean | `true` | Warn when public API modified |
| `block_on_critical_paths` | boolean | `true` | Block changes to critical code paths |

### Autonomy Constraints

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `max_autonomous_iterations` | integer | `10` | Max autonomous fix attempts |
| `require_approval_for_breaking_changes` | boolean | `true` | Human approval for breaking changes |
| `require_approval_for_security_changes` | boolean | `true` | Human approval for security changes |
| `sandbox_execution_required` | boolean | `true` | Require sandboxed testing before apply |

### Audit Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `log_all_changes` | boolean | `true` | Log all code modifications |
| `log_rejected_changes` | boolean | `true` | Log rejected changes |
| `retention_days` | integer | `90` | Log retention period |

## Usage Examples

### Example 1: Restrictive Configuration (Security-Critical Projects)

```json
{
  "governance": {
    "change_budgeting": {
      "enabled": true,
      "max_lines_per_change": 100,
      "max_files_per_change": 3,
      "max_complexity_delta": 10,
      "require_justification": true
    },
    "blast_radius": {
      "enabled": true,
      "max_affected_functions": 5,
      "max_affected_classes": 2,
      "max_call_graph_depth": 2,
      "block_on_critical_paths": true
    },
    "autonomy_constraints": {
      "max_autonomous_iterations": 3,
      "require_approval_for_breaking_changes": true,
      "require_approval_for_security_changes": true,
      "sandbox_execution_required": true
    }
  }
}
```

### Example 2: Permissive Configuration (Experimental Projects)

```json
{
  "governance": {
    "change_budgeting": {
      "enabled": true,
      "max_lines_per_change": 2000,
      "max_files_per_change": 50,
      "max_complexity_delta": 200,
      "require_justification": false
    },
    "blast_radius": {
      "enabled": true,
      "max_affected_functions": 100,
      "max_affected_classes": 20,
      "max_call_graph_depth": 5,
      "warn_on_public_api_changes": false,
      "block_on_critical_paths": false
    },
    "autonomy_constraints": {
      "max_autonomous_iterations": 50,
      "require_approval_for_breaking_changes": false,
      "require_approval_for_security_changes": true,
      "sandbox_execution_required": true
    }
  }
}
```

### Example 3: Team-Specific Configuration (Gradual Rollout)

```json
{
  "governance": {
    "change_budgeting": {
      "enabled": true,
      "max_lines_per_change": 300,
      "max_files_per_change": 5,
      "budget_refresh_interval_hours": 8
    },
    "blast_radius": {
      "enabled": true,
      "max_affected_functions": 15,
      "max_affected_classes": 4,
      "warn_on_public_api_changes": true
    },
    "autonomy_constraints": {
      "max_autonomous_iterations": 5,
      "require_approval_for_breaking_changes": true,
      "sandbox_execution_required": true
    }
  }
}
```

## Implementation

### Configuration Loader (src/code_scalpel/config/governance_config.py)

```python
import os
import json
import hashlib
import hmac
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class ChangeBudgetingConfig:
    enabled: bool = True
    max_lines_per_change: int = 500
    max_files_per_change: int = 10
    max_complexity_delta: int = 50
    require_justification: bool = True
    budget_refresh_interval_hours: int = 24

@dataclass
class BlastRadiusConfig:
    enabled: bool = True
    max_affected_functions: int = 20
    max_affected_classes: int = 5
    max_call_graph_depth: int = 3
    warn_on_public_api_changes: bool = True
    block_on_critical_paths: bool = True

@dataclass
class AutonomyConstraintsConfig:
    max_autonomous_iterations: int = 10
    require_approval_for_breaking_changes: bool = True
    require_approval_for_security_changes: bool = True
    sandbox_execution_required: bool = True

@dataclass
class AuditConfig:
    log_all_changes: bool = True
    log_rejected_changes: bool = True
    retention_days: int = 90

@dataclass
class GovernanceConfig:
    change_budgeting: ChangeBudgetingConfig
    blast_radius: BlastRadiusConfig
    autonomy_constraints: AutonomyConstraintsConfig
    audit: AuditConfig

class GovernanceConfigLoader:
    """Load and validate governance configuration with integrity protection."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.cwd() / ".scalpel" / "config.json"
    
    def load(self) -> GovernanceConfig:
        """Load configuration with hash validation."""
        # Check for environment variable overrides
        config_path_env = os.getenv("SCALPEL_CONFIG")
        if config_path_env:
            self.config_path = Path(config_path_env)
        
        # Load and validate configuration
        if self.config_path.exists():
            config_data = self._load_and_validate()
        else:
            config_data = self._get_defaults()
        
        # Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data)
        
        return self._parse_config(config_data)
    
    def _load_and_validate(self) -> dict:
        """Load config file and validate integrity."""
        with open(self.config_path, 'rb') as f:
            content = f.read()
        
        # Validate hash if provided
        expected_hash = os.getenv("SCALPEL_CONFIG_HASH")
        if expected_hash:
            actual_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
            if actual_hash != expected_hash:
                raise ValueError(
                    f"Configuration hash mismatch. Expected {expected_hash}, "
                    f"got {actual_hash}. Configuration may have been tampered with."
                )
        
        # Validate HMAC signature if secret provided
        secret = os.getenv("SCALPEL_CONFIG_SECRET")
        expected_sig = os.getenv("SCALPEL_CONFIG_SIGNATURE")
        if secret and expected_sig:
            actual_sig = hmac.new(
                secret.encode(), content, hashlib.sha256
            ).hexdigest()
            if actual_sig != expected_sig:
                raise ValueError(
                    "Configuration signature invalid. Configuration may have been tampered with."
                )
        
        return json.loads(content)
    
    def _get_defaults(self) -> dict:
        """Return default configuration."""
        return {
            "governance": {
                "change_budgeting": {
                    "enabled": True,
                    "max_lines_per_change": 500,
                    "max_files_per_change": 10,
                    "max_complexity_delta": 50,
                    "require_justification": True,
                    "budget_refresh_interval_hours": 24
                },
                "blast_radius": {
                    "enabled": True,
                    "max_affected_functions": 20,
                    "max_affected_classes": 5,
                    "max_call_graph_depth": 3,
                    "warn_on_public_api_changes": True,
                    "block_on_critical_paths": True
                },
                "autonomy_constraints": {
                    "max_autonomous_iterations": 10,
                    "require_approval_for_breaking_changes": True,
                    "require_approval_for_security_changes": True,
                    "sandbox_execution_required": True
                },
                "audit": {
                    "log_all_changes": True,
                    "log_rejected_changes": True,
                    "retention_days": 90
                }
            }
        }
    
    def _apply_env_overrides(self, config: dict) -> dict:
        """Apply environment variable overrides."""
        gov = config.get("governance", {})
        
        # Change Budgeting overrides
        cb = gov.get("change_budgeting", {})
        cb["max_lines_per_change"] = int(os.getenv(
            "SCALPEL_CHANGE_BUDGET_MAX_LINES",
            cb.get("max_lines_per_change", 500)
        ))
        cb["max_files_per_change"] = int(os.getenv(
            "SCALPEL_CHANGE_BUDGET_MAX_FILES",
            cb.get("max_files_per_change", 10)
        ))
        cb["max_complexity_delta"] = int(os.getenv(
            "SCALPEL_CHANGE_BUDGET_MAX_COMPLEXITY_DELTA",
            cb.get("max_complexity_delta", 50)
        ))
        
        # Blast Radius overrides
        br = gov.get("blast_radius", {})
        br["max_affected_functions"] = int(os.getenv(
            "SCALPEL_BLAST_RADIUS_MAX_FUNCTIONS",
            br.get("max_affected_functions", 20)
        ))
        br["max_affected_classes"] = int(os.getenv(
            "SCALPEL_BLAST_RADIUS_MAX_CLASSES",
            br.get("max_affected_classes", 5)
        ))
        br["max_call_graph_depth"] = int(os.getenv(
            "SCALPEL_BLAST_RADIUS_MAX_DEPTH",
            br.get("max_call_graph_depth", 3)
        ))
        
        # Autonomy overrides
        ac = gov.get("autonomy_constraints", {})
        ac["max_autonomous_iterations"] = int(os.getenv(
            "SCALPEL_MAX_AUTONOMOUS_ITERATIONS",
            ac.get("max_autonomous_iterations", 10)
        ))
        ac["require_approval_for_breaking_changes"] = os.getenv(
            "SCALPEL_REQUIRE_APPROVAL_BREAKING",
            str(ac.get("require_approval_for_breaking_changes", True))
        ).lower() == "true"
        ac["require_approval_for_security_changes"] = os.getenv(
            "SCALPEL_REQUIRE_APPROVAL_SECURITY",
            str(ac.get("require_approval_for_security_changes", True))
        ).lower() == "true"
        
        return config
    
    def _parse_config(self, config_data: dict) -> GovernanceConfig:
        """Parse config dict into typed dataclasses."""
        gov = config_data.get("governance", {})
        
        return GovernanceConfig(
            change_budgeting=ChangeBudgetingConfig(**gov.get("change_budgeting", {})),
            blast_radius=BlastRadiusConfig(**gov.get("blast_radius", {})),
            autonomy_constraints=AutonomyConstraintsConfig(**gov.get("autonomy_constraints", {})),
            audit=AuditConfig(**gov.get("audit", {}))
        )
```

## Security Considerations

1. **Hash Validation**: Always set `SCALPEL_CONFIG_HASH` to detect tampering
2. **Signature Verification**: Use `SCALPEL_CONFIG_SECRET` for enterprise deployments
3. **File Permissions**: Set `.scalpel/config.json` to read-only (`chmod 444`)
4. **Audit Logging**: Enable audit logging to track all configuration changes
5. **Version Control**: Commit `.scalpel/config.json` to git for team consistency

## Migration from Previous Versions

For projects using older Code Scalpel versions without governance config:

1. Run `code-scalpel init-governance` to create `.scalpel/config.json`
2. Review and adjust settings for your project's risk tolerance
3. Generate and set `SCALPEL_CONFIG_HASH`
4. Update `.vscode/mcp.json` with hash environment variable
5. Test with `code-scalpel check-governance` to validate configuration

## See Also

- [Policy Engine Guide](../policy_engine_guide.md) - Policy-based access control
- [Autonomy Integration](../autonomy_integration_summary.md) - Autonomous change management
- [Security Documentation](../../SECURITY.md) - Overall security practices
