# Migration Guide: v3.2.x → v3.3.0

**Version**: Code Scalpel v3.3.0  
**Date**: January 2026  
**Status**: Full backward compatibility maintained

## Quick Start

**Good news**: v3.3.0 is **100% backward compatible** with v3.2.x. Most users can upgrade without any code changes.

```bash
pip install --upgrade code-scalpel==3.3.0
```

That's it! Your existing code will continue to work.

## What Changed

### Project Structure Reorganization

v3.3.0 reorganizes the codebase for better maintainability:

**Old Structure** → **New Structure** (both work in v3.3.0)

```
code_scalpel/
├── code_analyzer.py          → analysis/code_analyzer.py (deprecated)
├── project_crawler.py        → analysis/project_crawler.py (deprecated)
├── surgical_extractor.py     → surgery/surgical_extractor.py (deprecated)
├── surgical_patcher.py       → surgery/surgical_patcher.py (deprecated)
└── polyglot/                 → code_parsers/ (deprecated, v3.4.0 removal)
```

### Import Migration (Optional)

**Old imports still work** (with deprecation warnings):

```python
# v3.2.x style - STILL WORKS ✅
from code_scalpel.code_analyzer import CodeAnalyzer
from code_scalpel.surgical_extractor import SurgicalExtractor
from code_scalpel.polyglot.tsx_analyzer import TSXAnalyzer
```

**New imports (recommended)** - No warnings:

```python
# v3.3.0 style - RECOMMENDED ✅
from code_scalpel.analysis import CodeAnalyzer
from code_scalpel.surgery import SurgicalExtractor
from code_scalpel.code_parsers.tsx_analyzer import TSXAnalyzer
```

## Breaking Changes

**NONE** - v3.3.0 maintains full backward compatibility.

All deprecated imports have compatibility shims that work identically to the old code.

## Tier System (New in v3.3.0)

v3.3.0 introduces a **tier system** (Community/Pro/Enterprise). All v3.2.x users automatically default to **Community tier**.

### Community Tier Features (Free)
- ✅ All 21 MCP tools available (with capability limits)
- ✅ Basic security analysis (essential features)
- ✅ Code extraction and modification
- ✅ Symbolic execution
- ✅ Self-hosted deployments

### How to Upgrade to Pro/Enterprise

1. **Obtain a license** from `https://your-org.com/licenses`
2. **Set license via environment variable**:
   ```bash
   export CODE_SCALPEL_LICENSE="your-jwt-token-here"
   ```
3. **Or via file** (`~/.code-scalpel/license.jwt`):
   ```bash
   mkdir -p ~/.code-scalpel
   echo "your-jwt-token-here" > ~/.code-scalpel/license.jwt
   ```

### Checking Your Current Tier

```python
from code_scalpel.licensing import tier_detector

tier = tier_detector.get_current_tier()
print(f"Current tier: {tier}")  # Output: "community", "pro", or "enterprise"
```

## Security Improvements

### License Verification (New)

v3.3.0 validates licenses for Pro/Enterprise features:

- **Remote verification**: License checked against issuer for revocation
- **Offline grace period**: 24 hours of offline operation supported
- **Automatic downgrade**: Expired/revoked licenses automatically downgrade to Community

No action needed - all automatic!

### Policy Engine (New)

v3.3.0 includes a policy engine for compliance:

```python
from code_scalpel.policy_engine import PolicyEngine

engine = PolicyEngine()
violations = engine.check_policy("path/to/code/")
```

## Configuration Changes

v3.3.0 adds new configuration options in `.code-scalpel/config.json`:

```json
{
  "version": "3.3.0",
  "tier": "community",
  "license_check_interval_hours": 24,
  "cache_dir": "~/.code-scalpel/cache",
  "log_level": "INFO"
}
```

All settings are optional with sensible defaults.

## Performance Impact

v3.3.0 introduces **minimal performance overhead**:

- **License checking**: <100ms per operation (cached after first check)
- **Memory**: <10MB additional for new tier system and policy engine
- **Disk**: ~50MB for new documentation and type hints

No measurable impact on core analysis performance.

## Testing Your Migration

```bash
# Run existing v3.2.x tests - should still pass
pytest tests/

# Check for deprecation warnings (optional cleanup)
pytest tests/ -W error::DeprecationWarning

# Verify your code with new imports (if you update them)
python -c "from code_scalpel.analysis import CodeAnalyzer; print('✅ Works')"
```

## Deprecated Modules Timeline

| Module | v3.3.0 | v3.4.0 | v3.5.0 |
|--------|--------|--------|--------|
| `code_scalpel.code_analyzer` | ⚠️ Warning | ⚠️ Warning | ❌ Removed |
| `code_scalpel.surgical_extractor` | ⚠️ Warning | ⚠️ Warning | ❌ Removed |
| `code_scalpel.project_crawler` | ⚠️ Warning | ⚠️ Warning | ❌ Removed |
| `code_scalpel.surgical_patcher` | ⚠️ Warning | ⚠️ Warning | ❌ Removed |
| `code_scalpel.polyglot` | ⚠️ Warning | ❌ Removed | — |

**Action**: Update imports before v3.4.0 to avoid breakage.

```bash
# Find deprecated imports in your code
grep -r "from code_scalpel.code_analyzer" .
grep -r "from code_scalpel.polyglot" .
```

## Rollback (If Needed)

If you encounter issues, roll back to v3.2.x:

```bash
pip install code-scalpel==3.2.9
```

No data migration needed - all v3.3.0 changes are backward compatible.

## Common Issues & FAQ

### Q: Will my v3.2.x code still work?
**A**: Yes! 100% backward compatible. No changes required.

### Q: Do I need a license?
**A**: No. Community tier is free and unlimited for self-hosted use.

### Q: Can I use Pro features in Community tier?
**A**: Community tier has all tools but with limits. See tier capabilities matrix.

### Q: How do I get Pro/Enterprise?
**A**: Contact support@your-org.com or visit https://your-org.com/licenses

### Q: What if my license expires?
**A**: Automatic downgrade to Community tier. Licensed features stop working; Community tier continues.

### Q: How do I report issues with v3.3.0?
**A**: GitHub Issues: https://github.com/your-org/code-scalpel/issues

## Next Steps

1. **Upgrade**: `pip install --upgrade code-scalpel==3.3.0`
2. **Test**: Run your existing tests to verify
3. **(Optional) Migrate imports**: Update to new import paths
4. **(Optional) Configure**: Set up custom config in `.code-scalpel/config.json`

## Support

- **Documentation**: https://github.com/your-org/code-scalpel/docs
- **Security Issues**: See [SECURITY.md](../SECURITY.md)
- **Questions**: GitHub Discussions or Email support

---

**Last Updated**: January 3, 2026  
**Compatibility**: v3.2.0 → v3.3.0 ✅ 100% compatible
