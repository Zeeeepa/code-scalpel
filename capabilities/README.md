# Code Scalpel Capability Files

This directory contains the golden capability files for Code Scalpel's tier-based feature gating system.

## Files

- **`free.json`** - Capabilities for the COMMUNITY tier (all 22 tools available)
- **`pro.json`** - Capabilities for the PRO tier (19 tools available)
- **`enterprise.json`** - Capabilities for the ENTERPRISE tier (10 tools available)
- **`schema.json`** - JSON Schema for validating capability files

## Usage

These files serve two purposes:

### 1. **Regression Testing** (Primary)
The golden files are compared against dynamically-generated capabilities during CI/CD:
- Tool count must match (always 22)
- Available count must not decrease
- Tool limits must match the limits.toml configuration

```bash
# In CI: Generate capabilities and compare against golden files
python3 scripts/generate_capabilities.py
pytest tests/capabilities/test_capability_snapshot.py
```

If there's a mismatch, the test fails and requires manual approval to update the golden files.

### 2. **Documentation**
The files serve as clear documentation of what's available at each tier:
- Agents can read these files to understand capabilities
- Customers can see exactly what they're paying for
- Implementation details are separated from user-facing limits

## Updating Golden Files

Golden files should only be updated when:
1. **New tool added** - Add it to the resolver with appropriate tier limits
2. **Tool removed** - Remove it from the resolver (rare)
3. **Limits changed intentionally** - Update limits.toml first, then regenerate
4. **New tier created** - Create new golden file

### To Regenerate:
```bash
# Option 1: Automatic (recommended)
python3 scripts/generate_capabilities.py

# Option 2: Via test suite
pytest tests/capabilities/test_capability_snapshot.py --regenerate-capabilities
```

## File Structure

Each file contains:
```json
{
  "tier": "pro",
  "generated_at": "2026-01-27T14:09:07.492883Z",
  "tool_count": 22,
  "available_count": 19,
  "capabilities": {
    "tool_id": {
      "tool_id": "analyze_code",
      "tier": "pro",
      "available": true,
      "limits": {
        "max_file_size_mb": 10,
        "languages": ["python", "javascript", "typescript", "java"]
      }
    },
    ...
  }
}
```

## Blocking Criteria

In the CI/CD pipeline, the following changes to capabilities WILL block a release:

1. **Tool count changed** - Adding/removing tools must be intentional
2. **Capability became unavailable** - Tier limits must not retroactively remove tools
3. **Limits decreased** - Only increases are allowed (or explicit pricing approval)
4. **Schema invalid** - Capabilities must validate against schema.json

## Tier Availability Summary

| Tool | Community | PRO | Enterprise |
|------|-----------|-----|------------|
| analyze_code | ✓ | ✓ | ✗ |
| code_policy_check | ✓ | ✓ | ✗ |
| crawl_project | ✓ | ✓ | ✓ |
| ... | ... | ... | ... |

(See the actual golden files for complete list)
