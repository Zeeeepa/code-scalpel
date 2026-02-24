# Tier Philosophy
<!-- [20260201_DOCS] Created to document data-driven tier differentiation strategy -->

## Design Principles

Code Scalpel uses a **feature-gating** architecture: all 22 MCP tools are available
at every tier. Tiers differ in **capabilities** (what features are enabled) and
**limits** (how much data a tool can process).

### The Three Tiers

| Tier | Target User | Project Scale | Differentiator |
|------|------------|---------------|----------------|
| **Community** (Free) | Solo developers, learners, OSS contributors | ≤500 files | All tools, practical limits |
| **Pro** ($) | Teams, professional use | Unlimited | Advanced features (217 capabilities) |
| **Enterprise** ($$$) | Regulated industries | Unlimited | Governance + compliance (356 capabilities) |

### Key Insight: Pro = Enterprise Limits

Pro and Enterprise have **identical numeric limits**. Enterprise does not
differentiate on scale — it differentiates on **governance capabilities**:

- Compliance frameworks (HIPAA, SOC2, PCI-DSS, GDPR)
- Cryptographically signed audit trails
- PDF certification reports
- Organization-wide policy enforcement
- Custom compliance rules and OPA/Rego policies
- Impact analysis with risk scoring
- CODEOWNERS integration

This means a team of 5 developers gets the same analysis power as a Fortune 500
company. The Fortune 500 pays more for compliance **features**, not for
bigger numbers.

---

## Community Tier: The 500-File Boundary

### Why 500?

The Community tier uses 500 files as its primary boundary, derived from real-world
project size data:

| Project Type | Typical Files | Fits in Community? |
|---|---|---|
| Personal CLI tool | 5-25 | ✅ Yes |
| Flask/FastAPI app | 30-100 | ✅ Yes |
| Python library (requests, click) | 30-80 | ✅ Yes |
| Data pipeline | 20-50 | ✅ Yes |
| Personal SaaS product | 100-200 | ✅ Yes |
| Medium application | 300-500 | ✅ Yes |
| Django/Rails app | 200-800 | ⚠️ Partial |
| Full product (src+tests) | 500-2000 | ❌ Upgrade to Pro |

**500 files covers 100% of solo developer projects** and most small team projects.
The boundary is set at the natural transition point where a codebase typically
requires a team to maintain — which is the natural upgrade trigger.

### Limit Derivation Formula

Each Community limit is derived from:

```
LIMIT = f(project_size, performance_target, user_persona)
```

Where:
- `project_size` = 500 files (maximum for solo dev persona)
- `performance_target` = analysis completes in <5 seconds
- `user_persona` = solo developer working on a single project

Example derivations:
- `max_symbol_count = 25,000` → 500 files × ~50 symbols/file average
- `max_nodes = 200` → 500 files × ~5 functions/file ÷ 12 (typical graph density)
- `max_modules = 100` → 500 files ÷ 5 files/module average

### What Community Users CAN Do

- Analyze any project with ≤500 source files
- Run security scans detecting OWASP Top 10 vulnerabilities
- Generate call graphs up to 10 levels deep
- Trace cross-file dependencies through 3 hops
- Extract code with immediate dependency resolution
- Generate up to 10 test cases per function
- Simulate refactors on files up to 5MB

### What Triggers an Upgrade

A Community user should upgrade to Pro when:
1. Their project exceeds 500 source files
2. They need deeper cross-file dependency analysis
3. They're working professionally and need team features
4. They need advanced constraint types (list, dict) in symbolic execution

---

## Pro Tier: Advanced Features, Not Bigger Numbers

### Philosophy

Pro users pay for **capabilities**, not for higher ceilings. Every Pro numeric
limit matches Enterprise exactly. The value of Pro is in features like:

- **217 capabilities** across 22 tools (vs 78 in Community)
- Advanced analysis depth settings
- Cognitive complexity metrics and code smell detection
- Halstead metrics and duplicate code detection
- Framework-aware taint analysis
- Custom security rules
- Dependency injection resolution
- Type checking during refactor simulation
- Advanced constraint types (list, dict) in symbolic execution
- Multiple test framework support (pytest + unittest)

### What Triggers an Enterprise Upgrade

A Pro user should upgrade to Enterprise when:
1. They need compliance reports (HIPAA, SOC2, PCI-DSS, GDPR)
2. Auditors require signed, tamper-evident logs
3. They need PDF certification reports
4. They have organization-wide coding policies to enforce
5. They need custom governance rules via OPA/Rego

---

## Enterprise Tier: 139 Unique Governance Capabilities

Enterprise adds **139 capabilities** not available in Pro, across categories:

### Compliance Frameworks
- HIPAA compliance scanning and reporting
- SOC2 control validation
- PCI-DSS payment security checks
- GDPR data handling verification

### Audit & Certification
- Cryptographically signed audit trails
- PDF certification reports
- Tamper-evident policy file verification
- Policy integrity validation with RSA signatures

### Organization-Wide Governance
- CODEOWNERS integration for change risk analysis
- Custom compliance rules via OPA/Rego engine
- Organization-wide architectural policies
- Multi-repository policy enforcement

### Advanced Analysis (Enterprise-only)
- Formal verification with proof generation
- Distributed project crawling
- Microservice boundary crossing detection
- Global taint flow analysis across services
- Technical debt scoring and trends
- Historical complexity comparison

---

## Tier Limit Reference

For the canonical numeric limits, see:
- [`src/code_scalpel/capabilities/limits.toml`](../../src/code_scalpel/capabilities/limits.toml)

For capabilities per tier per tool, see:
- [`src/code_scalpel/capabilities/features.toml`](../../src/code_scalpel/capabilities/features.toml)

For the auto-generated tool matrix:
- [`docs/reference/mcp_tools_by_tier.md`](../reference/mcp_tools_by_tier.md)

### Quick Reference

| Limit | Community | Pro | Enterprise |
|-------|-----------|-----|------------|
| Scanner max files | 500 | 100,000 | 100,000 |
| Scanner max depth | 10 | 50 | 50 |
| Call graph depth | 10 | Unlimited | Unlimited |
| Call graph nodes | 200 | Unlimited | Unlimited |
| Cross-file deps depth | 3 | Unlimited | Unlimited |
| Context lines | 2,000 | Unlimited | Unlimited |
| Symbol references | 200 | Unlimited | Unlimited |
| Extract code depth | 1 | Unlimited | Unlimited |
| Simulate refactor size | 5 MB | 100 MB | 100 MB |
| Test cases generated | 10 | Unlimited | Unlimited |
| Security findings | 100 | Unlimited | Unlimited |

---

## Validation

The tier system is validated by automated tests in `tests/tier_validation/`:

1. **Monotonicity** — Community ≤ Pro ≤ Enterprise for all numeric limits
2. **Parity** — Pro numeric limits = Enterprise numeric limits
3. **Superset** — Enterprise capabilities ⊃ Pro capabilities ⊃ Community capabilities
4. **Persona coverage** — Community limits accommodate all solo dev project types
5. **Regression** — Specific limit values match documented strategy

See `tests/tier_validation/test_tier_structure.py` for the full test suite.
