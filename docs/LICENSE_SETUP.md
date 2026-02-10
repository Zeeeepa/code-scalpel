# Code Scalpel License Setup Guide

**[20260210_FEATURE]** Complete guide for setting up licenses in Code Scalpel.

---

## Overview

Code Scalpel uses JWT-based licenses to unlock Pro and Enterprise features. The license system automatically discovers license files in standard locations.

---

## License Tiers

### Community (Free)
- **Cost**: Free forever
- **Features**: Core analysis tools
- **Use Case**: Individual developers, open-source projects
- **License Required**: No

### Pro
- **Cost**: Paid subscription
- **Features**: Advanced analysis, cross-file operations, priority support
- **Use Case**: Professional developers, small teams
- **License Required**: Yes (JWT file)

### Enterprise
- **Cost**: Custom pricing
- **Features**: Full feature set, unlimited usage, dedicated support
- **Use Case**: Large organizations, security teams
- **License Required**: Yes (JWT file + activation)

---

## License File Locations

### Priority Order

Code Scalpel searches for license files in this order:

1. **Environment Variable (Highest Priority)**
   ```bash
   export CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt
   # OR point to a directory
   export CODE_SCALPEL_LICENSE_PATH=/path/to/licenses/
   ```

2. **Project-Level License (Recommended)** ⭐
   ```
   your-project/
   └── .code-scalpel/
       └── license/
           └── license.jwt    ← Place your license here
   ```

   **Why use this location:**
   - Created automatically by `codescalpel init`
   - Shared with your team (commit to git)
   - Works immediately when MCP server starts
   - Clearly documented for team members

3. **XDG User Directory (User-Level)**
   ```
   ~/.config/code-scalpel/license.jwt
   ```

   **Why use this location:**
   - Personal license (not shared)
   - Works across all projects
   - Standard Linux/Mac location

4. **Home Directory (Legacy)**
   ```
   ~/.code-scalpel/license.jwt
   ```

5. **Current Directory (Fallback)**
   ```
   .code-scalpel/license.jwt
   .scalpel-license
   ```

### Case Sensitivity

Code Scalpel checks both lowercase and capitalized variants:
- `.code-scalpel/` AND `.code-Scalpel/`
- This handles filesystem inconsistencies across platforms

---

## Installation Methods

### Method 1: Using `codescalpel init` (Recommended)

The `codescalpel init` command automatically creates the license directory:

```bash
# Navigate to your project
cd /path/to/your-project

# Initialize configuration
codescalpel init

# Copy your license file
cp ~/Downloads/code_scalpel_license_pro_*.jwt .code-scalpel/license/license.jwt

# Verify installation
codescalpel mcp
```

**What `codescalpel init` creates:**
```
.code-scalpel/
├── license/
│   └── README.md          ← Instructions for placing license
├── policy.yaml           ← Security policies
├── budget.yaml           ← Change budgets
├── config.json           ← MCP configuration
└── README.md             ← Configuration guide
```

### Method 2: Using `codescalpel license install` (CLI)

```bash
# Install license to default location (~/.config/code-scalpel/license.jwt)
codescalpel license install ~/Downloads/code_scalpel_license_pro_*.jwt

# Install to custom location
codescalpel license install ~/Downloads/license.jwt --dest .code-scalpel/license/

# Force overwrite existing license
codescalpel license install license.jwt --force
```

### Method 3: Manual Copy

```bash
# Create directory
mkdir -p .code-scalpel/license

# Copy license file
cp ~/Downloads/code_scalpel_license_*.jwt .code-scalpel/license/license.jwt

# Set permissions (recommended for security)
chmod 600 .code-scalpel/license/license.jwt
```

### Method 4: Environment Variable (Deployments)

For Docker, Kubernetes, or CI/CD:

```bash
# Point to license file
export CODE_SCALPEL_LICENSE_PATH=/etc/code-scalpel/license.jwt

# OR point to directory (will scan for .jwt files)
export CODE_SCALPEL_LICENSE_PATH=/etc/code-scalpel/licenses/

# Start server
codescalpel mcp
```

---

## Verification

### Check License Status

```bash
# Start MCP server and check boot display
codescalpel mcp
```

**Expected output:**
```
============================================================
Code Scalpel MCP Server v1.3.4
============================================================
Project Root: /path/to/your-project
License Tier: PRO
License File: ./.code-scalpel/license/license.jwt
Transport: stdio
...
```

### Boot Display Indicators

- **COMMUNITY**: No license file (free tier)
- **PRO**: Valid Pro license detected
- **ENTERPRISE**: Valid Enterprise license detected

### Troubleshooting

**Issue**: Server shows "Community" tier despite having a license

**Solution**:
1. Verify license file exists and is readable:
   ```bash
   ls -la .code-scalpel/license/license.jwt
   cat .code-scalpel/license/license.jwt
   ```

2. Check license file format (should be a JWT):
   ```bash
   # Should look like: eyJ0eXAiOiJKV1QiLCJhbGci...
   head -c 50 .code-scalpel/license/license.jwt
   ```

3. Enable debug logging:
   ```bash
   export SCALPEL_MCP_OUTPUT=DEBUG
   codescalpel mcp
   ```

4. Check for validation errors:
   ```bash
   # License may be expired or invalid
   # Look for messages about license validation
   ```

**Issue**: "License File: Not found" but file exists

**Solution**:
- Check file permissions: `chmod 600 .code-scalpel/license/license.jwt`
- Verify file path matches one of the standard locations
- Use absolute path with environment variable:
  ```bash
  export CODE_SCALPEL_LICENSE_PATH=/absolute/path/to/license.jwt
  ```

**Issue**: Multiple license files found

**Solution**:
- Code Scalpel uses the **first valid license** found in priority order
- To force a specific license:
  ```bash
  export CODE_SCALPEL_LICENSE_PATH=/path/to/specific/license.jwt
  ```

---

## Team Setup

### Recommended Workflow

1. **Project Administrator**:
   ```bash
   # Initialize project
   codescalpel init

   # Install team license
   cp company_license.jwt .code-scalpel/license/license.jwt

   # Commit to git (license is team-shared)
   git add .code-scalpel/
   git commit -m "Add Code Scalpel configuration"
   git push
   ```

2. **Team Members**:
   ```bash
   # Clone repository
   git clone repo
   cd repo

   # License is already present!
   codescalpel mcp
   ```

### Git Considerations

**Should you commit the license file?**

| Scenario | Commit License? | Reason |
|----------|-----------------|--------|
| Team license (same for all) | ✅ Yes | Everyone uses the same license |
| Personal licenses | ❌ No | Each developer has their own license |
| Open source project | ❌ No | Contributors use their own licenses |
| Company internal tool | ✅ Yes | Shared company license |

**If NOT committing license:**

Add to `.gitignore`:
```gitignore
# Code Scalpel license (personal)
.code-scalpel/license/license.jwt
```

And document in README:
```markdown
## Setup for Developers

1. Obtain your Code Scalpel license from [portal]
2. Run: `codescalpel init`
3. Copy license: `cp ~/Downloads/license.jwt .code-scalpel/license/`
4. Start server: `codescalpel mcp`
```

---

## Security Best Practices

### File Permissions

```bash
# Make license readable only by owner
chmod 600 .code-scalpel/license/license.jwt

# Prevent accidental modifications
chmod -w .code-scalpel/license/
```

### Environment Variables

For production deployments:

```bash
# Store in secrets manager (e.g., AWS Secrets Manager)
# Inject at runtime, not in Dockerfile

# Docker
docker run -e CODE_SCALPEL_LICENSE_PATH=/secrets/license.jwt ...

# Kubernetes
# Use Secret volume mount or sealed secrets
```

### License Rotation

When updating licenses:

```bash
# Backup old license
cp .code-scalpel/license/license.jwt .code-scalpel/license/license.jwt.bak

# Install new license
codescalpel license install new_license.jwt --force

# Test
codescalpel mcp

# If successful, remove backup
rm .code-scalpel/license/license.jwt.bak
```

---

## Claude Desktop Integration

### MCP Server Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "codescalpel",
      "args": ["mcp"],
      "env": {
        "CODE_SCALPEL_LICENSE_PATH": "/path/to/license.jwt"
      }
    }
  }
}
```

### Verification

1. Restart Claude Desktop
2. Open Claude Desktop logs
3. Look for:
   ```
   ============================================================
   Code Scalpel MCP Server v1.3.4
   ============================================================
   License Tier: PRO
   License File: /path/to/license.jwt
   ```

---

## FAQ

**Q: Can I use the same license on multiple machines?**
A: Depends on your license type:
- **Personal Pro**: Single developer, any machine
- **Team Pro**: Multiple developers, number specified in license
- **Enterprise**: Custom terms, usually unlimited

**Q: What happens if my license expires?**
A: The server automatically falls back to Community tier. You'll see:
```
License Tier: COMMUNITY
License File: ./.code-scalpel/license/license.jwt (expired)
```

**Q: How do I check license expiration?**
A: Enable debug logging:
```bash
export SCALPEL_MCP_OUTPUT=DEBUG
codescalpel mcp 2>&1 | grep -i license
```

**Q: Can I have multiple licenses?**
A: Yes, but only the first valid license in priority order is used.

**Q: Where can I get a license?**
A: Visit https://code-scalpel.ai or contact sales@code-scalpel.ai

---

## Related Documentation

- [Configuration Guide](../README.md)
- [Release Notes](../docs/release_notes/)
- [API Reference](../docs/reference/mcp_tools_current.md)
- [Troubleshooting](../wiki/Troubleshooting.md)

---

## Summary

✅ **Recommended Setup** (Team):
```bash
codescalpel init
cp license.jwt .code-scalpel/license/
git add .code-scalpel/
git commit -m "Add Code Scalpel config"
```

✅ **Recommended Setup** (Personal):
```bash
codescalpel license install ~/Downloads/license.jwt
# Or manually:
mkdir -p ~/.config/code-scalpel
cp license.jwt ~/.config/code-scalpel/license.jwt
```

✅ **Verify**:
```bash
codescalpel mcp
# Look for "License Tier: PRO" in output
```

Your license file will be automatically discovered and validated!
