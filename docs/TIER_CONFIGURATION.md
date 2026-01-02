# Tier Configuration Guide

**Last Updated**: v3.3.0 (2025-12-28)
> [20251228_DOCS] Updated for strict licensing posture and file-only license discovery (`CODE_SCALPEL_LICENSE_PATH` / `--license-file` / `.code-scalpel/license.jwt`).

Code Scalpel uses an **open-core licensing model** with three tiers: Community (free), Pro (commercial), and Enterprise (commercial). All code ships in a single MIT-licensed package, but features are restricted at runtime based on your configured tier.

---

## Quick Reference

| Tier | License | Cost | Configuration |
|------|---------|------|---------------|
| **Community** | MIT | Free | Default (no configuration needed) |
| **Pro** | Commercial | Paid | Request `pro` tier + provide a valid license file |
| **Enterprise** | Commercial | Paid | Request `enterprise` tier + provide a valid license file |

### License File (Required for Pro/Enterprise)

Code Scalpel uses **file-only** license discovery for paid tiers.

- Preferred: put your license at `.code-scalpel/license.jwt` in your project
- Or set `CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt`
- Or pass `--license-file /path/to/license.jwt` when starting the MCP server

## Keysets, Rotation, and Environments

> [20251228_DOCS] Documented how to configure keysets for rotation and beta/prod separation.

Code Scalpel supports verifying multiple signing keys via `kid`.

- `CODE_SCALPEL_LICENSE_PUBLIC_KEYS_PATH`: path to a JSON dict mapping `kid → public key PEM`
- `CODE_SCALPEL_LICENSE_PUBLIC_KEYS_JSON`: inline JSON dict mapping `kid → public key PEM`

Recommended deployment posture:
- Production deployments load a keyset that contains only `prod-*` keys.
- Beta deployments load a keyset that contains only `beta-*` keys.

This ensures beta and production licenses cannot be mixed accidentally.

---

## Configuration Methods

### 1. Environment Variable (Recommended)

Set the `CODE_SCALPEL_TIER` environment variable before starting the MCP server:

```bash
# Community (default - no configuration needed)
code-scalpel mcp

# Pro
export CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt
export CODE_SCALPEL_TIER=pro
code-scalpel mcp

# Enterprise
export CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt
export CODE_SCALPEL_TIER=enterprise
code-scalpel mcp
```

### 2. Command-Line Argument

Pass the `--tier` flag when starting the server:

```bash
# Community
code-scalpel mcp --tier community

# Pro
code-scalpel mcp --tier pro --license-file /path/to/license.jwt

# Enterprise
code-scalpel mcp --tier enterprise --license-file /path/to/license.jwt
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
        "CODE_SCALPEL_TIER": "pro",
        "CODE_SCALPEL_LICENSE_PATH": "/path/to/license.jwt"
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
        "CODE_SCALPEL_TIER": "pro",
        "CODE_SCALPEL_LICENSE_PATH": "/path/to/license.jwt"
      }
    }
  }
}
```

### 4. Docker Environment

When running in Docker:

```bash
# Pro tier
docker run \
  -e CODE_SCALPEL_TIER=pro \
  -e CODE_SCALPEL_LICENSE_PATH=/app/.code-scalpel/license.jwt \
  -v /path/to/license.jwt:/app/.code-scalpel/license.jwt \
  -p 8593:8593 code-scalpel

# Enterprise tier
docker run \
  -e CODE_SCALPEL_TIER=enterprise \
  -e CODE_SCALPEL_LICENSE_PATH=/app/.code-scalpel/license.jwt \
  -v /path/to/license.jwt:/app/.code-scalpel/license.jwt \
  -p 8593:8593 code-scalpel
```

Or in `docker-compose.yml`:

```yaml
services:
  code-scalpel:
    image: code-scalpel
    environment:
      CODE_SCALPEL_TIER: pro
      CODE_SCALPEL_LICENSE_PATH: /app/.code-scalpel/license.jwt
    volumes:
      - /path/to/license.jwt:/app/.code-scalpel/license.jwt
    ports:
      - "8593:8593"
```

---

## Feature Comparison

> **Important**: As of v3.3.0, ALL 20 MCP tools are available at ALL tiers.
> Tiers differ in **capabilities and limits** within each tool, not in tool availability.

### Tool Availability

| Category | Community | Pro | Enterprise |
|----------|-----------|-----|------------|
| **MCP Tools** | ✅ All 20 tools | ✅ All 20 tools | ✅ All 20 tools |
| **Core Extraction** | ✅ Available | ✅ Available | ✅ Available |
| **Security Analysis** | ✅ Available | ✅ Available | ✅ Available |
| **Symbolic Execution** | ✅ Available | ✅ Available | ✅ Available |
| **Project Analysis** | ✅ Available | ✅ Available | ✅ Available |
| **Cross-File Analysis** | ✅ Available | ✅ Available | ✅ Available |

**The difference is in what each tool can do, not whether it's available.**

### Capability Progression by Tool

#### `security_scan` - Security Vulnerability Detection

| Capability | Community | Pro | Enterprise |
|------------|-----------|-----|------------|
| Basic vulnerabilities | ✅ | ✅ | ✅ |
| Max findings | 10 | Unlimited | Unlimited |
| Vulnerability types | SQL, XSS, Command Injection | All types | All types + custom |
| Taint analysis | Single-file | Advanced multi-path | Cross-file |
| Remediation | ❌ | ✅ Suggestions | ✅ Automated |
| OWASP categorization | ❌ | ✅ | ✅ |
| Compliance reporting | ❌ | ❌ | ✅ SOC2, HIPAA |

#### `symbolic_execute` - Symbolic Path Exploration

| Capability | Community | Pro | Enterprise |
|------------|-----------|-----|------------|
| Basic paths | ✅ | ✅ | ✅ |
| Max paths | 3 | 10 | Unlimited |
| Constraint solving | Basic (Z3) | Advanced | Advanced + custom |
| Path prioritization | ❌ | ✅ | ✅ |
| Branch coverage | ❌ | ✅ | ✅ |

#### `crawl_project` - Project-Wide Analysis

| Capability | Community | Pro | Enterprise |
|------------|-----------|-----|------------|
| File discovery | ✅ | ✅ | ✅ |
| Max files | 100 | 1,000 | Unlimited |
| Mode | Discovery | Deep AST parsing | Deep + org indexing |
| Complexity analysis | ❌ | ✅ | ✅ |
| Dependency graph | ❌ | ✅ | ✅ |
| Custom metrics | ❌ | ❌ | ✅ |

#### `extract_code` - Code Extraction with Dependencies

| Capability | Community | Pro | Enterprise |
|------------|-----------|-----|------------|
| Single-file extraction | ✅ | ✅ | ✅ |
| Cross-file deps | ❌ | ✅ | ✅ |
| Max dependency depth | 0 | 1 | Unlimited |
| Org-wide resolution | ❌ | ❌ | ✅ |

#### `generate_unit_tests` - Test Generation

| Capability | Community | Pro | Enterprise |
|------------|-----------|-----|------------|
| Basic test generation | ✅ | ✅ | ✅ |
| Max test cases | 5 | 20 | Unlimited |
| Test frameworks | pytest | pytest, unittest | All + custom |
| Coverage targeting | ❌ | ✅ | ✅ |

#### `get_call_graph` - Function Call Analysis

| Capability | Community | Pro | Enterprise |
|------------|-----------|-----|------------|
| Basic call graph | ✅ | ✅ | ✅ |
| Max depth | 3 hops | 10 hops | Unlimited |
| Circular import check | ✅ | ✅ | ✅ |
| Mermaid diagram | ✅ | ✅ | ✅ |

#### `get_graph_neighborhood` - Graph Subgraph Extraction

| Capability | Community | Pro | Enterprise |
|------------|-----------|-----|------------|
| Neighborhood extraction | ✅ | ✅ | ✅ |
| Max k-hops | 1 | 2 | Unlimited |
| Max nodes | 50 | 100 | Unlimited |
| Confidence filtering | ✅ | ✅ | ✅ |

#### `scan_dependencies` - Vulnerability Scanning

| Capability | Community | Pro | Enterprise |
|------------|-----------|-----|------------|
| OSV database lookup | ✅ | ✅ | ✅ |
| Max dependencies | 50 | Unlimited | Unlimited |
| Vulnerability details | Basic | Full | Full + remediation |
| Auto-update PR | ❌ | ❌ | ✅ |

#### `get_cross_file_dependencies` - Dependency Resolution

| Capability | Community | Pro | Enterprise |
|------------|-----------|-----|------------|
| Dependency resolution | ✅ | ✅ | ✅ |
| Max depth | 1 | 3 | Unlimited |
| Confidence decay | ✅ | ✅ | ✅ |
| Circular detection | ✅ | ✅ | ✅ |

#### `cross_file_security_scan` - Multi-File Taint Analysis

| Capability | Community | Pro | Enterprise |
|------------|-----------|-----|------------|
| Cross-file taint | ✅ Limited | ✅ Full | ✅ Full |
| Max depth | 2 | 5 | Unlimited |
| Max modules | 50 | 500 | Unlimited |
| Timeout | 30s | 120s | Configurable |

### All Other Tools

All remaining tools (`analyze_code`, `update_symbol`, `simulate_refactor`, `unified_sink_detect`, `get_file_context`, `get_symbol_references`, `get_project_map`, `validate_paths`, `verify_policy_integrity`, `type_evaporation_scan`) are **fully available** at all tiers with no restrictions in v3.3.0.

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

## Budget-Conscious Governance Selection

> [20251226_DOCS] Guide for selecting tier AND governance profile based on budget constraints.

### The Core Tension: Token Efficiency vs. Governance Overhead

Code Scalpel is designed for **context-size-aware AI agent development** - enabling small-context AI agents (8K-32K tokens) to operate on large codebases with surgical precision.

**Key insight:** Governance is **server-side**, not agent-side. The AI agent never sees policy files - it only receives pass/fail responses (~50 tokens).

### Break-Even Analysis

| Team Size | Annual Dev Cost | Governance Setup | ROI Threshold |
|-----------|-----------------|------------------|---------------|
| 1 solo | $0 (hobby) | 2 hours | Not worth it |
| 1 contractor | $50K | 4 hours | 1 prevented bug = ROI |
| 2-5 devs | $300K | 8 hours | 1 security incident avoided |
| 5-20 devs | $1M+ | 16 hours | Audit compliance = mandatory |
| 20+ devs | $5M+ | 40 hours | Full Enterprise tier justified |

### Tier + Governance Profile Matrix

| Scenario | Recommended Tier | Governance Profile | Total Overhead |
|----------|-----------------|-------------------|----------------|
| Solo hobby project | Community | `permissive` | 0 tokens |
| Contractor, client work | Community/Pro | `minimal` | ~50 tokens |
| Small team, internal tools | Pro | `minimal` | ~50 tokens |
| Startup, pre-revenue | Pro | `minimal` | ~50 tokens |
| Standard enterprise | Pro | `default` | ~100 tokens |
| Regulated industry | Enterprise | `restrictive` | ~150 tokens |
| Multi-agent orchestration | Enterprise | `default`/`restrictive` | ~100-150 tokens |

### When Governance Is NOT Worth It

- Solo development, side projects → Skip governance entirely
- Rapid prototyping / hackathons → Use `permissive` profile
- Learning and experimentation → Use `permissive` profile
- One-off scripts → No governance needed

### When Governance IS Worth It

- Client deliverables → Audit trail for liability protection
- Team > 2 people → Coordination and standards
- Any paid project → Basic compliance coverage
- Production code → Quality assurance
- Regulated industry → Legal requirement

### Governance Profile Quick Start

```bash
# Set governance profile alongside tier
export CODE_SCALPEL_TIER=pro
export CODE_SCALPEL_CONFIG_PROFILE=minimal
```

See [Governance Profile Selection Guide](../.code-scalpel/GOVERNANCE_PROFILES.md) for detailed profile comparison.

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
