# Tier Philosophy Audit - February 12, 2026

## Target Philosophy

**Pro ≈ Enterprise limits** (very similar)  
**Enterprise differentiation = Governance/Policy features**

Enterprise gets:
- Compliance reporting (HIPAA, SOC2, PCI-DSS, GDPR)
- Audit trails (cryptographically signed)
- PDF certification reports
- Policy signature validation
- Tamper detection
- Advanced architectural protections via `.code-scalpel/` configs

## Current State Analysis

### ✅ CORRECT: features.toml

Enterprise governance capabilities properly defined:

```toml
[enterprise.code_policy_check]
capabilities = [
    "audit_trail",
    "compliance_auditing",
    "gdpr_compliance",
    "hipaa_compliance",
    "pci_dss_compliance",
    "pdf_certification",
    "soc2_compliance",
    # ... plus Pro capabilities
]

[enterprise.verify_policy_integrity]
capabilities = [
    "audit_logging",
    "cryptographic_verification",
    "policy_signing",
    "tamper_detection",
    # ... etc
]
```

### ❌ PROBLEM: limits.toml - Pro limits too restrictive

**Scanner (50x gap!):**
- Pro: 2,000 files, depth 10, 50K symbols
- Enterprise: 100,000 files, depth 50, 1M symbols

**Call Graph (unlimited vs capped):**
- Pro: max_depth=50, max_nodes=500
- Enterprise: enabled=true (unlimited)

**File Context:**
- Pro: max_context_lines=2000
- Enterprise: enabled=true (unlimited)

**Cross-File Dependencies:**
- Pro: max_depth=5, max_files=500
- Enterprise: enabled=true (unlimited)

## Recommended Changes to limits.toml

### Three-Tier Strategy: Community → Pro/Enterprise (governance differentiation)

**Philosophy:**
- **Community**: Generous limits for solo developers and small teams (1-10 devs)
- **Pro**: Near-unlimited limits for large teams and enterprise codebases
- **Enterprise**: Identical to Pro + governance/compliance features

### Proposed Limits

#### Community Tier (Increase 10-20x)
```toml
[community.scanner]
max_files = 1000           # Was: 50 → Now: 20x increase
max_depth = 10             # Was: 2 → Now: 5x increase
max_symbol_count = 50000   # Was: 1000 → Now: 50x increase

[community.get_call_graph]
max_depth = 20             # Was: 3 → Now: 7x increase
max_nodes = 500            # Was: 50 → Now: 10x increase

[community.get_file_context]
max_context_lines = 5000   # Was: 500 → Now: 10x increase

[community.get_cross_file_dependencies]
max_depth = 5              # Was: 1 → Now: 5x increase
max_files = 500            # Was: 50 → Now: 10x increase

[community.get_graph_neighborhood]
max_k = 3                  # Was: 1 → Now: 3x increase
max_nodes = 200            # Was: 20 → Now: 10x increase
```

**Rationale**: Community tier becomes useful for real projects (up to 1000 files covers 80% of solo developer codebases).

#### Pro Tier (Match Enterprise limits)
```toml
[pro.scanner]
max_files = 100000         # Was: 2000 → Same as Enterprise
max_depth = 50             # Was: 10 → Same as Enterprise
max_symbol_count = 1000000 # Was: 50K → Same as Enterprise

[pro.get_call_graph]
enabled = true             # Was: max_depth=50 → Now unlimited

[pro.get_file_context]
enabled = true             # Was: 2000 lines → Now unlimited

[pro.get_cross_file_dependencies]
enabled = true             # Was: max_depth=5, max_files=500 → Now unlimited

[pro.get_graph_neighborhood]
enabled = true             # Was: max_k=5, max_nodes=100 → Now unlimited
```

#### Enterprise Tier (No change - already unlimited)
```toml
# Enterprise keeps existing limits + governance flags:
# - compliance_enabled = true
# - audit_trail_enabled = true
# - pdf_reports_enabled = true
# - signature_validation = true
# - tamper_detection = true
```

**Recommendation: Implement all three tier changes** - Maintains sensible progression while emphasizing Enterprise = governance.

## Documentation Fixes Needed

### 1. feature_development_tiers_guide.md (Line 35-50)

**Current:**
```markdown
| Tier | Value Proposition |
|------|-------------------|
| Pro | Team collaboration, advanced analysis, custom rules |
| Enterprise | Compliance, audit trails, unlimited scale, governance |
```

**Should be:**
```markdown
| Tier | Value Proposition |
|------|-------------------|
| Pro | Full-featured analysis, unlimited scale for code operations |
| Enterprise | Compliance (SOC2/HIPAA/PCI-DSS), audit trails, cryptographic policy verification, governance |
```

### 2. README.md (Tier System section)

**Add:**
```markdown
### Tier Differentiation Philosophy

Code Scalpel's tiers differ in **governance features**, not operational limits:

- **Community**: Essential functionality with reasonable limits
- **Pro**: Full-featured analysis with high limits (suitable for teams 1-100 developers)
- **Enterprise**: Pro features + **governance layer**:
  - Compliance reporting (SOC2, HIPAA, PCI-DSS, GDPR)
  - Cryptographically signed audit trails
  - PDF certification reports  
  - Policy integrity verification
  - `.code-scalpel/` architectural protections
```

### 3. .code-scalpel/README.md

**Emphasize:** Enterprise value = governance configurations, not just higher limits

## Testing Impact

If limits change significantly, these test files need updates:
- `tests/tools/tiers/test_*_tiers.py` - May have hardcoded limit expectations
- `tests/integration/test_tool_pipelines.py` - Tier limit validation tests
- `tests/testing/test_fixtures.py` - Already skipped (expects old architecture)

## Rollout Plan

1. **Update limits.toml** - Pro limits → near-Enterprise
2. **Update feature_development_tiers_guide.md** - Correct tier philosophy
3. **Update README.md** - Add tier differentiation explanation
4. **Update .code-scalpel/README.md** - Emphasize governance value
5. **Run tier tests** - Verify no regressions
6. **Update CHANGELOG** - Document philosophy clarification
7. **Version bump** - 1.3.6 with "Tier philosophy alignment"

## Impact Analysis

### Community Tier Changes
**Files affected by 10-20x limit increase:**
- Individual developers with 500-1000 file projects
- OSS projects with medium complexity
- Tutorial/learning projects

**Value proposition**: Community becomes genuinely useful (not artificially crippled)

### Pro Tier Changes  
**Files affected by 5-50x limit increase:**
- Teams working on large monorepos (10K+ files)
- Microservices architectures
- Multi-language polyglot projects

**Value proposition**: Pro = "full scale analysis" without artificial caps

### Enterprise Differentiation
**Value comes from**:
- Compliance reporting (SOC2, HIPAA, PCI-DSS, GDPR)
- Cryptographically signed audit trails  
- Policy integrity verification (tamper detection)
- PDF certification reports
- .code-scalpel/ architectural protections
- Custom governance rules

### Test Impact
**Tests that may need updates:**
- `tests/tools/tiers/test_*_tiers.py` - Hardcoded limit expectations
- `tests/integration/test_tool_pipelines.py` - Tier validation tests
- Any test asserting `max_files < 100` or `max_depth < 5`

## Questions for Confirmation

1. **Approve Community limit increases (10-20x)?** Makes Community genuinely useful
2. **Approve Pro = Enterprise limits?** Differentiation = governance only
3. **Version bump: v1.3.6 (patch) or v1.4.0 (minor)?** Philosophy change suggests minor
4. **Breaking change communication?** Tests may fail, users may expect limits
