# Code Scalpel Pipeline Summary

**Generated:** 2026-01-17 10:27:00  
**Environment:** conda  
**Python:** 3.10.19

## Artifact Categories

### 🔒 Security Artifacts (for buyers/auditors)
| File | Description |
|------|-------------|
| `security/bandit-sast-report.json` | SAST scan results (JSON) |
| `security/bandit-sast-report.html` | SAST scan results (human-readable) |
| `security/pip-audit-report.json` | Dependency CVE audit |
| `security/sbom-cyclonedx.json` | Software Bill of Materials |
| `security/license-compliance.json` | License audit (JSON) |
| `security/license-summary.md` | License audit (readable) |

### 📊 Test Coverage
| File | Description |
|------|-------------|
| `coverage/html/index.html` | Interactive coverage report |
| `coverage/coverage.json` | Coverage metrics (JSON) |
| `test_results_*.xml` | JUnit XML test results |

### 📈 Code Quality Metrics
| File | Description |
|------|-------------|
| `compliance/complexity-cc.json` | Cyclomatic complexity |
| `compliance/maintainability-index.json` | Maintainability scores |
| `compliance/loc-stats.json` | Lines of code statistics |

### 📝 Documentation
| File | Description |
|------|-------------|
| `docs/todos.json` | All TODOs consolidated |
| `docs/TODO_BY_MODULE.md` | TODOs organized by module |

### 📦 Build Artifacts
| File | Description |
|------|-------------|
| `code_scalpel-*.whl` | Wheel distribution |
| `code_scalpel-*.tar.gz` | Source distribution |

## Verification Steps for Buyers

1. **Security:** Review `security/bandit-sast-report.html` for SAST findings
2. **Dependencies:** Check `security/pip-audit-report.json` for known CVEs
3. **Supply Chain:** Examine `security/sbom-cyclonedx.json` for full dependency tree
4. **Licenses:** Verify `security/license-summary.md` for license compatibility
5. **Test Coverage:** Open `coverage/html/index.html` in browser
6. **Code Quality:** Review `compliance/*.json` for complexity metrics
