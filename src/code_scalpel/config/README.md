# Configuration Module

**Purpose:** Configuration management for Code Scalpel components

## Overview

This module provides configuration classes and templates for:
- Governance policies and compliance settings
- Code Scalpel initialization and server configuration  
- Template definitions for reports and policy files

## Key Components

### governance_config.py
Configuration for governance and compliance features:
- Audit log settings
- Compliance reporter configuration
- Policy enforcement rules
- Evidence collection settings

### init_config.py
Initialization configuration for Code Scalpel:
- Server startup parameters
- Default MCP tool settings
- Cache configuration defaults
- Path resolution settings

### templates.py
Templates for generated reports and policy files:
- Compliance report templates
- Security scan report formats
- Evidence file structures
- Policy file templates

## Usage

```python
from code_scalpel.config import governance_config, init_config, templates

# Load governance configuration
config = governance_config.GovernanceConfig.load()

# Initialize with custom config
from code_scalpel import create_app
app = create_app(config=init_config.ServerConfig())
```

## Integration

Used by:
- `governance/` - Compliance and audit logging
- `policy_engine/` - Policy enforcement
- `mcp/server.py` - MCP server initialization
- `integrations/` - External framework integrations
