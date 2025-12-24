# Tier Configuration Guide

**Last Updated**: v3.2.8 (2025-12-23)

Code Scalpel uses an **open-core licensing model** with three tiers: Community (free), Pro (commercial), and Enterprise (commercial). All code ships in a single MIT-licensed package, but features are restricted at runtime based on your configured tier.

---

## Quick Reference

| Tier | License | Cost | Configuration |
|------|---------|------|---------------|
| **Community** | MIT | Free | Default (no configuration needed) |
| **Pro** | Commercial | Paid | Set `CODE_SCALPEL_TIER=pro` |
| **Enterprise** | Commercial | Paid | Set `CODE_SCALPEL_TIER=enterprise` |

---

## Configuration Methods

### 1. Environment Variable (Recommended)

Set the `CODE_SCALPEL_TIER` environment variable before starting the MCP server:

```bash
# Community (default - no configuration needed)
code-scalpel mcp

# Pro
export CODE_SCALPEL_TIER=pro
code-scalpel mcp

# Enterprise
export CODE_SCALPEL_TIER=enterprise
code-scalpel mcp
```

### 2. Command-Line Argument

Pass the `--tier` flag when starting the server:

```bash
# Community
code-scalpel mcp --tier community

# Pro
code-scalpel mcp --tier pro

# Enterprise
code-scalpel mcp --tier enterprise
```

### 3. MCP Configuration File

For **VS Code / GitHub Copilot**, configure in `.vscode/mcp.json`:

```json
{
  "servers": {
    "code-scalpel": {
      "type": "stdio",
      "command": "uvx",
      "args": ["code-scalpel", "mcp"],
      "env": {
        "CODE_SCALPEL_TIER": "pro"
      }
    }
  }
}
```

For **Claude Desktop**, configure in `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp"],
      "env": {
        "CODE_SCALPEL_TIER": "pro"
      }
    }
  }
}
```

### 4. Docker Environment

When running in Docker:

```bash
# Pro tier
docker run -e CODE_SCALPEL_TIER=pro -p 8593:8593 code-scalpel

# Enterprise tier
docker run -e CODE_SCALPEL_TIER=enterprise -p 8593:8593 code-scalpel
```

Or in `docker-compose.yml`:

```yaml
services:
  code-scalpel:
    image: code-scalpel
    environment:
      CODE_SCALPEL_TIER: pro
    ports:
      - "8593:8593"
```

---

## Feature Comparison

### Tool-Level Restrictions

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|------------|
| **All basic tools** | ✅ Full access | ✅ Full access | ✅ Full access |
| `extract_code` | ✅ Unlimited | ✅ Unlimited | ✅ Unlimited |
| `update_symbol` | ✅ Unlimited | ✅ Unlimited | ✅ Unlimited |
| `analyze_code` | ✅ Unlimited | ✅ Unlimited | ✅ Unlimited |
| `security_scan` | ✅ Unlimited | ✅ Unlimited | ✅ Unlimited |
| **Project-wide tools** | ⚠️ Limited | ✅ Full | ✅ Full |
| `crawl_project` | Discovery mode only | Deep analysis | Deep analysis |
| `get_symbol_references` | 10 files max | Unlimited | Unlimited |
| `get_call_graph` | 3 hops max | Configurable | Configurable |
| `get_graph_neighborhood` | 1 hop max | Configurable | Configurable |

### Detailed Feature Breakdown

#### `crawl_project`

**Community (Discovery Mode)**:
- ✅ File inventory (all .py files with paths)
- ✅ Line counts and directory structure
- ✅ Entrypoint detection (main blocks, CLI commands, Flask/Django routes)
- ✅ Basic statistics
- ❌ No AST parsing
- ❌ No complexity analysis
- ❌ No function/class details
- ❌ No dependency resolution

**Pro/Enterprise (Deep Mode)**:
- ✅ Everything in Community, plus:
- ✅ Full AST parsing
- ✅ Complexity analysis (cyclomatic, cognitive)
- ✅ Function/class inventories with line numbers
- ✅ Import statements and cross-file dependencies
- ✅ Complexity warnings
- ✅ Detailed metrics report

#### `get_symbol_references`

**Community**:
- ✅ First 10 files with references
- ⚠️ Truncation warning with upgrade hint

**Pro/Enterprise**:
- ✅ Full project-wide search
- ✅ Unlimited files

#### `get_call_graph`

**Community**:
- ✅ Maximum 3 hops from entry point
- ⚠️ Depth warning with upgrade hint

**Pro/Enterprise**:
- ✅ Configurable depth (up to 50 hops)
- ✅ Full control over traversal

#### `get_graph_neighborhood`

**Community**:
- ✅ 1-hop neighborhood (immediate neighbors only)
- ⚠️ Hop warning with upgrade hint

**Pro/Enterprise**:
- ✅ Configurable k-hop neighborhoods
- ✅ Multi-hop exploration

---

## Upgrade Hints

When Community tier encounters limitations, the response includes an `upgrade_hints` field:

```json
{
  "tier": "community",
  "upgrade_hints": [
    "Upgrade to Pro/Enterprise for deep analysis with complexity metrics and cross-file dependencies"
  ],
  "data": {
    "status": "discovered",
    "files_discovered": 127
  }
}
```

These hints are:
- Machine-readable (consistent format)
- Non-intrusive (not error messages)
- Informative (explain what's available in higher tiers)

---

## Verification

### Check Current Tier

The tier is included in every tool response:

```python
# Example response
{
  "tier": "community",  # or "pro" or "enterprise"
  "tool_version": "3.2.8",
  "tool_id": "crawl_project",
  "request_id": "abc123...",
  "data": { ... }
}
```

### Test Configuration

Use the echo-like behavior of any tool to verify tier:

```bash
# Check what tier is active
export CODE_SCALPEL_TIER=pro
code-scalpel mcp

# In your MCP client, call any tool and check the response tier field
```

### Automated Verification

Run the distribution verification script:

```bash
python scripts/verify_distribution_separation.py
```

Expected output:
```
✅ PASS: Distribution separation is correctly implemented
- 5 tier check calls found
- All 4 restricted features have tier checks
- Community: 4 checks, Pro: 1 checks, Enterprise: 1 checks
```

---

## Licensing

### Community Edition (Free)

- **License**: MIT
- **Usage**: Free for any purpose (personal, commercial, open source)
- **Restrictions**: Feature limitations (discovery mode, hop/depth/file limits)
- **Support**: Community support via GitHub Issues

### Pro Edition (Commercial License Required)

- **License**: Commercial license agreement
- **Usage**: Requires valid Pro license key
- **Features**: All Community features plus unlimited project-wide analysis
- **Support**: Email support with SLA

### Enterprise Edition (Commercial License Required)

- **License**: Commercial license agreement with enterprise terms
- **Usage**: Requires valid Enterprise license key
- **Features**: All Pro features plus enterprise governance and audit trails
- **Support**: Priority support with dedicated contact

**To Purchase**: Contact sales@code-scalpel.io (or see project documentation for purchasing info)

---

## Enforcement Model

Code Scalpel uses an **honor system** with commercial licensing:

1. **All Code Ships**: The complete codebase (including Pro/Enterprise features) ships in the MIT-licensed package
2. **Runtime Restrictions**: Features are restricted at runtime based on configured tier
3. **License Compliance**: Using Pro/Enterprise features without a license violates the license agreement
4. **Audit Trail**: All tool responses log the tier for compliance tracking

This model is intentional and aligns with standard open-core practices (MySQL, GitLab, Elastic).

**Why This Approach?**
- **Transparency**: All code visible for security auditing
- **Trust**: No hidden code or DRM
- **Simplicity**: One package, one distribution
- **Flexibility**: Easy to test all features locally

**Security Note**: Users can technically modify `CODE_SCALPEL_TIER`, but doing so without a valid license violates the license agreement and your organization's software compliance policies.

---

## Troubleshooting

### Tier Not Recognized

**Symptom**: Error: `Invalid tier. Expected one of: community, pro, enterprise`

**Solution**: Check spelling and casing:
```bash
# Wrong
export CODE_SCALPEL_TIER=Community  # Case-sensitive!

# Correct
export CODE_SCALPEL_TIER=community  # Lowercase
```

**Aliases**: These are automatically normalized:
- `free` → `community`
- `all` → `enterprise`

### Environment Variable Not Working

**Symptom**: Tier defaults to Community despite setting environment variable

**Solution**:
1. Verify the variable is set in the correct shell session:
   ```bash
   echo $CODE_SCALPEL_TIER
   ```

2. If using MCP config file, ensure `env` field is set:
   ```json
   "env": {
     "CODE_SCALPEL_TIER": "pro"
   }
   ```

3. Restart the MCP server after changing configuration

### Upgrade Hints Not Appearing

**Symptom**: No upgrade hints in Community tier responses

**Possible Causes**:
1. Already using Pro/Enterprise tier (check `tier` field in response)
2. Tool doesn't have tier-specific limitations (most basic tools are unrestricted)
3. Limitation not yet triggered (e.g., call graph with depth ≤ 3)

**Solution**: Call a restricted tool that will hit limits:
- `crawl_project` with a large project (always shows discovery mode in Community)
- `get_symbol_references` on a widely-used symbol (>10 files)
- `get_call_graph` with depth >3

### Docker Tier Configuration

**Symptom**: Docker container ignores tier configuration

**Solution**: Pass environment variable explicitly:
```bash
docker run -e CODE_SCALPEL_TIER=pro code-scalpel

# Or in docker-compose.yml
environment:
  CODE_SCALPEL_TIER: pro
```

---

## Migration Paths

### From Community to Pro/Enterprise

No code changes required:

```bash
# Before: Community tier
code-scalpel mcp

# After: Purchase Pro license, then:
export CODE_SCALPEL_TIER=pro
code-scalpel mcp
```

All existing integrations continue to work. Responses now include full data instead of truncated results.

### From Pro to Enterprise

Same process - update environment variable:

```bash
export CODE_SCALPEL_TIER=enterprise
code-scalpel mcp
```

Enterprise tier includes additional governance and audit features (when available).

---

## Best Practices

### For Individual Developers

1. **Start with Community**: Try Community tier for personal projects
2. **Evaluate Needs**: Check upgrade hints to see what you're missing
3. **Upgrade Strategically**: Purchase Pro when project-wide analysis becomes critical

### For Teams

1. **Standardize Configuration**: Use MCP config files for consistency
2. **Document Tier Usage**: Include tier configuration in team documentation
3. **Monitor Upgrade Hints**: Track when team hits Community limitations
4. **Budget for Licenses**: Plan for Pro/Enterprise licenses in tool budgets

### For Organizations

1. **Centralize Configuration**: Use environment variables in CI/CD
2. **Audit Trail**: Monitor tier logs for compliance tracking
3. **Policy Enforcement**: Ensure proper licenses for Pro/Enterprise usage
4. **Support Contracts**: Consider Enterprise tier for priority support

---

## API for Tier Detection

If building tools that consume Code Scalpel responses:

```python
import requests

response = requests.post("http://localhost:8593/mcp", json={
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "crawl_project",
        "arguments": {"path": "/my/project"}
    },
    "id": 1
})

result = response.json()["result"]
tier = result["tier"]  # "community", "pro", or "enterprise"
upgrade_hints = result.get("upgrade_hints", [])

if tier == "community" and upgrade_hints:
    print("Consider upgrading:", upgrade_hints[0])
```

---

## Support

- **Community**: GitHub Issues → https://github.com/yourorg/code-scalpel/issues
- **Pro**: Email support with 48-hour SLA → support@code-scalpel.io
- **Enterprise**: Priority support with dedicated contact → enterprise@code-scalpel.io

For licensing inquiries: sales@code-scalpel.io

---

## Related Documentation

- [Universal Response Envelope](reference/mcp_response_envelope.md)
- [Error Codes](reference/error_codes.md)
- [Distribution Separation Architecture](architecture/distribution_separation.md)
- [Release Notes v3.2.8](release_notes/RELEASE_NOTES_v3.2.8.md)
