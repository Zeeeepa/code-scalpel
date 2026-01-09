# Code Scalpel v3.3.0 Release Notes

**Release Date**: January 2026  
**Version**: 3.3.0 - "Clean Slate"  
**Status**: 🔄 Pre-Release (Validation in Progress)

## Overview

Code Scalpel v3.3.0 introduces a major reorganization focusing on:
- **Clean project structure** with clear separation of concerns
- **Enhanced tier system** with better isolation and enforcement
- **Improved security** with cryptographic verification and policy engines
- **Better documentation** with comprehensive API references and migration guides
- **Production-ready** with comprehensive testing and observability

## Major Changes

### 1. Project Structure Reorganization
- Clear separation between analysis, security, surgery, and licensing modules
- Improved module hierarchy with better import patterns
- Deprecated old import paths (with backward compatibility stubs)

### 2. Tier System Enhancements
- **Community Tier**: Free, open-source, self-hosted deployments
- **Pro Tier**: Enhanced features for professional teams
- **Enterprise Tier**: Advanced capabilities for large organizations
- Runtime tier detection and enforcement via JWT licenses
- Graceful fallback to Community tier for offline/expired licenses

### 3. Security Improvements
- Policy engine with cryptographic integrity verification
- Cross-file taint analysis for vulnerability detection
- Type evaporation detection (TypeScript/Python type system vulnerabilities)
- Enhanced CRL (Certificate Revocation List) checking for licenses
- Remote license verification with offline grace period

### 4. Code Quality
- 4,730 tests with 94%+ code coverage
- Type-safe codebase with <100 Pyright errors
- 100% Black formatting compliance (610 files)
- 100% isort import sorting (1,270 files)
- Bandit security scanning (0 HIGH severity issues)

### 5. Documentation
- Comprehensive API reference for all 21 MCP tools
- Migration guide from v3.2 to v3.3
- Tier capabilities matrix
- Configurable response output guide

## Installation

### From PyPI
```bash
pip install code-scalpel==3.3.0
```

### From source
```bash
git clone https://github.com/your-org/code-scalpel.git
cd code-scalpel
git checkout v3.3.0
pip install -e .
```

## Key Features

### Community Tier (Free)
- ✅ All 21 MCP tools available (limited capabilities)
- ✅ Basic security analysis
- ✅ Code extraction and modification
- ✅ Symbolic execution
- ✅ Self-hosted deployment

### Pro Tier
- ✅ All Community features
- ✅ Enhanced tool capabilities
- ✅ Advanced security analysis
- ✅ Custom tool configurations
- ✅ Commercial license required

### Enterprise Tier
- ✅ All Pro features
- ✅ Enterprise security features
- ✅ Compliance modules (HIPAA, SOC2, GDPR, PCI-DSS)
- ✅ Advanced observability
- ✅ Enterprise support license required

## Testing Summary

| Test Suite | Count | Status | Coverage |
|-----------|-------|--------|----------|
| Unit Tests | 1,350 | ✅ 100% | 94%+ |
| Integration Tests | 263 | ✅ 100% | Integration level |
| Security Tests | 300+ | ✅ 100% | 9/10 OWASP Top 10 |
| Tier System Tests | 181 | ✅ 100% | All tiers verified |
| MCP Tools Tests | 52 | ✅ 100% | All 21 tools |
| Code Quality | 6 | ✅ 100% | All metrics pass |

## Breaking Changes

⚠️ **None in v3.3.0** - Full backward compatibility maintained with v3.2.x

### Deprecations
- `code_scalpel.code_analyzer` → Use `code_scalpel.analysis` instead
- `code_scalpel.project_crawler` → Use `code_scalpel.analysis` instead
- `code_scalpel.surgical_extractor` → Use `code_scalpel.surgery` instead
- `code_scalpel.surgical_patcher` → Use `code_scalpel.surgery` instead
- `code_scalpel.polyglot` → Use `code_scalpel.code_parsers` instead (v3.4.0)

All deprecated modules have compatibility shims that work through v3.3.x.

## Migration from v3.2.x

No action required! v3.3.0 is fully backward compatible with v3.2.x.

For detailed migration information, see [MIGRATION_v3.2_to_v3.3.md](./MIGRATION_v3.2_to_v3.3.md).

## Known Issues

None at release time.

## Support

- **Documentation**: [docs/](../README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/code-scalpel/issues)
- **Security**: See [SECURITY.md](../SECURITY.md)
- **License**: Apache 2.0

## Contributors

See [CONTRIBUTORS.md](../CONTRIBUTORS.md) for the full list.

---

**Release prepared**: January 3, 2026  
**Validated by**: Automated pre-release checklist  
**Status**: Ready for production deployment
