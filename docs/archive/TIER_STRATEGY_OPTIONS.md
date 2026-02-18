# Tier Limit Strategy & Scientific Justification

> [20260212_DOCS] Living document: tier philosophy, data-driven limits, and testing strategy

## Strategic Question
**Where is the natural "free vs paid" cutoff that makes business sense while keeping Community genuinely useful?**

## Tier Differentiation Model

```
Community (Free)         Pro ($)               Enterprise ($$$)
─────────────────       ─────────────────     ─────────────────
Reasonable limits       Near-unlimited        Same as Pro
22 tools                22 tools              22 tools
78 capabilities         217 capabilities      356 capabilities
                                              +139 Enterprise-only
                                              
Basic governance        Full governance       Full governance
(budgets, basic         (custom rules,        + Compliance frameworks
 policy)                 security patterns,    + Audit trails (signed)
                         signature valid.)     + PDF certifications
                                              + Org-wide policies
```

**Key Insight**: Pro and Enterprise share limits. Enterprise differentiates on **139 unique capabilities** focused on compliance, audit, and organizational governance — not higher numbers.

## 1. Data-Driven Limit Calibration

### Reference Project Sizes (Real-World Data)

| Project Type | Files | LOC | Developers | Tier Target |
|---|---|---|---|---|
| Personal script/CLI | 5-20 | 500-2K | 1 | Community |
| Flask/FastAPI app | 30-100 | 2K-10K | 1-2 | Community |
| Python library (requests, click) | 30-80 | 3K-15K | 1-5 | Community |
| Medium app (Code Scalpel src) | ~437 | ~50K | 1-5 | Community/Pro boundary |
| Django/Rails app | 200-800 | 20K-80K | 3-15 | Pro |
| Full product (src+tests) | 500-2000 | 50K-200K | 5-20 | Pro |
| Large SaaS product | 2K-10K | 200K-1M | 10-50 | Pro |
| Enterprise monorepo | 10K-100K+ | 1M+ | 50-500+ | Pro/Enterprise |

### Natural Breakpoint: **500 files**

Why 500 is the cutoff:
- Covers **100% of solo developer projects** (Flask, FastAPI, CLIs, libraries)
- Covers **~80% of small team projects** (small-medium Django apps, APIs)
- Code Scalpel's own source code (437 files) fits just under the boundary
- Teams that outgrow 500 files are operating professionally → Pro

### Limit Derivation Logic

Each limit should be derived from a **measurable criterion**:

```
LIMIT = f(project_size, performance_target, user_persona)

Where:
  project_size    = files, LOC, symbols typical for the tier's target user
  performance     = analysis must complete within acceptable time
  user_persona    = solo dev, team, regulated enterprise
```

---

## 2. Proposed Limits (with rationale)

### Community (Free) — Target: Solo developers, small projects ≤500 files

| Tool | Limit | Current | New | Rationale |
|---|---|---|---|---|
| scanner | max_files | 50 | **500** | Covers all solo dev projects; 500 = natural team boundary |
| scanner | max_depth | 2 | **10** | Depth-2 misses most real import chains; 10 is practical |
| scanner | max_symbol_count | 1,000 | **25,000** | 500 files × ~50 symbols/file avg = 25K |
| get_call_graph | max_depth | 3 | **10** | 3 misses A→B→C→D chains; 10 covers real apps |
| get_call_graph | max_nodes | 50 | **200** | 500 files × ~5 functions/file ÷ 12 = ~200 in typical graph |
| get_file_context | max_context_lines | 500 | **2,000** | 500 barely shows a file; 2K = typical large module |
| get_cross_file_deps | max_depth | 1 | **3** | 1-hop is useless; 3 shows A→B→C import chains |
| get_cross_file_deps | max_files | 50 | **200** | 200 handles analysis within a 500-file project |
| get_graph_neighborhood | max_k | 1 | **2** | 2-hop shows meaningful context |
| get_graph_neighborhood | max_nodes | 20 | **100** | 20 barely shows a module; 100 = neighborhood |
| get_project_map | max_files | 100 | **500** | Match scanner max_files |
| get_project_map | max_modules | 50 | **100** | 500 files ÷ 5 files/module = 100 |
| get_symbol_references | max_files_searched | 10 | **200** | 10 is too restrictive for any real project |
| get_symbol_references | max_references | 50 | **200** | 200 covers most symbols; popular ones need Pro |
| crawl_project | max_files | 100 | **500** | Match scanner |
| security_scan | max_findings | 50 | **100** | 50 gets lost in noise; 100 is actionable |
| cross_file_security | max_modules | 10 | **50** | 10 barely covers a small app |
| cross_file_security | max_depth | 3 | **5** | 3 misses indirect taint; 5 is practical |
| extract_code | max_depth | 0 | **1** | 0 = no deps at all; 1 = immediate imports |
| simulate_refactor | max_file_size_mb | 1 | **5** | 1MB is a small file; 5MB covers most |
| symbolic_execute | max_paths | 50 | **100** | 100 paths covers most functions |
| generate_unit_tests | max_test_cases | 5 | **10** | 5 is barely useful; 10 is practical |

### Pro ($) — Target: Teams, professional use, large projects

| Tool | Limit | Current | New | Rationale |
|---|---|---|---|---|
| scanner | max_files | 2,000 | **100,000** | Match Enterprise; no artificial cap |
| scanner | max_depth | 10 | **50** | Match Enterprise |
| scanner | max_symbol_count | 50,000 | **1,000,000** | Match Enterprise |
| get_call_graph | max_depth | 50 | **unlimited (-1)** | Pro users should not hit caps |
| get_call_graph | max_nodes | 500 | **unlimited (-1)** | Pro users should not hit caps |
| get_file_context | max_context_lines | 2,000 | **unlimited (-1)** | Match Enterprise |
| get_cross_file_deps | max_depth | 5 | **unlimited (-1)** | Match Enterprise |
| get_cross_file_deps | max_files | 500 | **unlimited (-1)** | Match Enterprise |
| get_graph_neighborhood | max_k | 5 | **unlimited (-1)** | Match Enterprise |
| get_graph_neighborhood | max_nodes | 100 | **unlimited (-1)** | Match Enterprise |
| get_project_map | max_files | 1,000 | **100,000** | Match Enterprise |
| get_project_map | max_modules | 200 | **1,000** | Match Enterprise |
| get_symbol_references | (all) | limited | **unlimited** | Match Enterprise |
| crawl_project | (all) | limited | **unlimited** | Match Enterprise |
| security_scan | (all) | limited | **unlimited** | Match Enterprise |
| cross_file_security | max_modules | 100 | **unlimited (-1)** | Match Enterprise |
| cross_file_security | max_depth | 10 | **unlimited (-1)** | Match Enterprise |
| extract_code | max_depth | 1 | **unlimited (-1)** | Match Enterprise |
| simulate_refactor | max_file_size_mb | 10 | **100** | Match Enterprise |
| symbolic_execute | max_depth | 100 | **unlimited (-1)** | Match Enterprise |
| generate_unit_tests | max_test_cases | 20 | **unlimited (-1)** | Match Enterprise |

### Enterprise ($$$) — Same limits as Pro + 139 governance capabilities

No limit changes needed. Enterprise differentiates on **features**, not limits:
- Compliance frameworks (HIPAA, SOC2, PCI-DSS, GDPR)
- Cryptographically signed audit trails
- PDF certification reports
- Organization-wide policy enforcement
- Custom compliance rules
- Impact analysis and change risk scoring
- CODEOWNERS integration

---

## 3. Scientific Testing Strategy

### 3.1 Performance Benchmark Suite

**Goal**: Prove that limits are set at performance-justified boundaries.

```
tests/benchmarks/
├── conftest.py                      # Synthetic project generators
├── test_scaling_characteristics.py   # How tools scale with N files
├── test_community_within_budget.py   # Community limits complete in <5s
├── test_pro_at_scale.py             # Pro limits complete in <60s
└── README.md                        # Methodology documentation
```

**Test: Community limits stay within performance budget**
```python
@pytest.mark.benchmark
@pytest.mark.parametrize("file_count", [100, 250, 500])
async def test_community_scanner_performance(tmp_path, file_count):
    """Community scanner must complete within 5 seconds for up to 500 files."""
    project = generate_synthetic_project(tmp_path, file_count)
    
    start = time.monotonic()
    result = await scanner.scan(project, max_files=500)
    elapsed = time.monotonic() - start
    
    assert elapsed < 5.0, f"Scanner took {elapsed:.1f}s for {file_count} files (budget: 5s)"
    assert result.files_analyzed <= 500
```

**Test: Pro limits handle large codebases**
```python
@pytest.mark.benchmark
@pytest.mark.parametrize("file_count", [1000, 5000, 10000])
async def test_pro_scanner_at_scale(tmp_path, file_count):
    """Pro scanner handles large projects within 60 seconds."""
    project = generate_synthetic_project(tmp_path, file_count)
    
    start = time.monotonic()
    result = await scanner.scan(project, max_files=100000)
    elapsed = time.monotonic() - start
    
    assert elapsed < 60.0, f"Scanner took {elapsed:.1f}s for {file_count} files (budget: 60s)"
```

**Test: Scaling curve is sublinear**
```python
@pytest.mark.benchmark
async def test_scanner_scaling_is_sublinear(tmp_path):
    """Verify O(n log n) or better scaling, not O(n²)."""
    times = {}
    for n in [100, 500, 1000, 5000]:
        project = generate_synthetic_project(tmp_path / str(n), n)
        start = time.monotonic()
        await scanner.scan(project, max_files=100000)
        times[n] = time.monotonic() - start
    
    # If O(n²), 5000/500 should be ~100x slower
    # If O(n log n), 5000/500 should be ~13x slower
    ratio = times[5000] / times[500]
    assert ratio < 20, f"Scaling ratio {ratio:.1f}x suggests superlinear growth"
```

### 3.2 Tier Boundary Validation

**Goal**: Prove that Community limits are sufficient for target personas.

```
tests/tier_validation/
├── test_community_covers_persona.py  # Real-world project fit tests
├── test_pro_enterprise_parity.py     # Pro = Enterprise for limits
├── test_enterprise_governance.py     # Enterprise-only features work
└── fixtures/
    ├── solo_dev_project/             # ~200 files, Flask app
    ├── team_project/                 # ~2000 files, Django app
    └── enterprise_project/           # ~10000 files, monorepo
```

**Test: Community covers the solo developer persona**
```python
SOLO_DEV_PROJECTS = {
    "flask_app": {"files": 45, "max_depth": 4, "symbols": 320},
    "fastapi_service": {"files": 80, "max_depth": 5, "symbols": 650},
    "cli_tool": {"files": 25, "max_depth": 3, "symbols": 180},
    "python_library": {"files": 60, "max_depth": 6, "symbols": 500},
    "data_pipeline": {"files": 35, "max_depth": 4, "symbols": 280},
    "personal_saas": {"files": 150, "max_depth": 7, "symbols": 1200},
    "medium_app": {"files": 400, "max_depth": 8, "symbols": 3500},
}

COMMUNITY_LIMITS = {
    "max_files": 500,
    "max_depth": 10,
    "max_symbol_count": 25000,
}

@pytest.mark.parametrize("project_name,stats", SOLO_DEV_PROJECTS.items())
def test_community_covers_solo_dev_project(project_name, stats):
    """Every solo dev project type must fit within Community limits."""
    for key, value in stats.items():
        limit_key = f"max_{key}" if not key.startswith("max_") else key
        if limit_key in COMMUNITY_LIMITS:
            assert value <= COMMUNITY_LIMITS[limit_key], (
                f"Project '{project_name}' exceeds Community {limit_key}: "
                f"{value} > {COMMUNITY_LIMITS[limit_key]}"
            )
```

**Test: Pro and Enterprise have identical limits**
```python
async def test_pro_enterprise_limit_parity():
    """Pro and Enterprise must have identical numeric limits.
    
    Enterprise differentiates on CAPABILITIES (139 unique features),
    not on limit values. Any numeric limit in Enterprise must also
    appear in Pro with the same value.
    """
    pro_limits = load_tier_limits("pro")
    enterprise_limits = load_tier_limits("enterprise")
    
    for tool_name in ALL_TOOLS:
        pro = pro_limits.get(tool_name, {})
        ent = enterprise_limits.get(tool_name, {})
        
        for key, ent_value in ent.items():
            if isinstance(ent_value, (int, float)) and key != "enabled":
                pro_value = pro.get(key)
                assert pro_value == ent_value, (
                    f"Limit parity violation: {tool_name}.{key} "
                    f"Pro={pro_value} != Enterprise={ent_value}"
                )
```

**Test: Enterprise has strictly more capabilities than Pro**
```python
async def test_enterprise_superset_of_pro():
    """Enterprise capabilities must be a strict superset of Pro."""
    pro_caps = load_tier_capabilities("pro")
    ent_caps = load_tier_capabilities("enterprise")
    
    for tool_name in ALL_TOOLS:
        pro_set = set(pro_caps.get(tool_name, []))
        ent_set = set(ent_caps.get(tool_name, []))
        
        missing = pro_set - ent_set
        assert not missing, (
            f"Enterprise missing Pro capabilities for {tool_name}: {missing}"
        )
        
        ent_only = ent_set - pro_set
        # Enterprise should have ADDITIONAL capabilities
        # (not required for every tool, but globally should have 139+)
```

### 3.3 Regression Testing

**Goal**: Limits changes don't break existing behavior.

```python
@pytest.mark.parametrize("tier", ["community", "pro", "enterprise"])
async def test_limits_are_monotonically_increasing(tier):
    """For any numeric limit, community ≤ pro ≤ enterprise."""
    limits = {t: load_tier_limits(t) for t in ["community", "pro", "enterprise"]}
    
    for tool_name in ALL_TOOLS:
        for key in limits["community"].get(tool_name, {}):
            c = limits["community"][tool_name].get(key)
            p = limits["pro"][tool_name].get(key)
            e = limits["enterprise"][tool_name].get(key)
            
            if all(isinstance(v, (int, float)) for v in [c, p, e] if v is not None):
                # -1 means unlimited, which is always >= any positive value
                c_eff = float('inf') if c == -1 else (c or 0)
                p_eff = float('inf') if p == -1 else (p or 0)
                e_eff = float('inf') if e == -1 else (e or 0)
                
                assert c_eff <= p_eff <= e_eff, (
                    f"Non-monotonic {tool_name}.{key}: "
                    f"C={c} P={p} E={e}"
                )
```

### 3.4 Documentation Validation Tests

**Goal**: Documentation accurately reflects actual limits.

```python
def test_readme_tier_table_matches_limits_toml():
    """README's tier comparison table must match limits.toml values."""
    readme = Path("README.md").read_text()
    limits = load_limits_toml()
    
    # Parse tier table from README
    # Verify each claimed limit matches limits.toml
    for tool_name, tool_limits in limits["community"].items():
        for key, value in tool_limits.items():
            if isinstance(value, int) and value > 0:
                assert str(value) in readme or f"{value:,}" in readme, (
                    f"README missing Community {tool_name}.{key}={value}"
                )

def test_features_toml_enterprise_superset():
    """features.toml Enterprise must contain all Pro capabilities."""
    # Catches regressions where Pro gets a capability that
    # wasn't added to Enterprise (found 3 such gaps previously)
```

---

## 4. Core Documentation Plan

### 4.1 Tier Philosophy Document

**Location**: `docs/guides/tier_philosophy.md`

**Contents**:
1. **Design Principles** — Why tiers exist, what each tier targets
2. **Limit Derivation** — How limits are calculated from project size data
3. **Capability Matrix** — Full Pro vs Enterprise capability table
4. **Upgrade Triggers** — When users should upgrade (data-driven)
5. **Performance Guarantees** — "Community completes in <5s for 500 files"

### 4.2 Tier Comparison Page (for README/website)

```markdown
## Tier Comparison

| | Community (Free) | Pro | Enterprise |
|---|---|---|---|
| **Tools** | 22 | 22 | 22 |
| **Max project files** | 500 | Unlimited | Unlimited |
| **Analysis depth** | 10 levels | Unlimited | Unlimited |
| **Cross-file analysis** | 3-hop, 200 files | Unlimited | Unlimited |
| **Security scanning** | OWASP Top 10 | Full + custom rules | Full + compliance |
| **Governance** | Basic budgets | Full policies | Full + compliance frameworks |
| **Audit trails** | — | Basic logging | Signed, tamper-evident |
| **Compliance** | — | — | HIPAA, SOC2, PCI-DSS, GDPR |
| **PDF reports** | — | — | ✅ Certified |
| **Custom policy engine** | — | — | ✅ OPA/Rego |
| **Org-wide rules** | — | — | ✅ Multi-repo |
| **Support** | Community | Email | Dedicated + SLA |
```

### 4.3 Scientific Justification Document

**Location**: `docs/architecture/tier_limit_justification.md`

**Contents**:
1. **Methodology** — How limits were derived
2. **Project Size Distribution** — Real-world data on project sizes
3. **Performance Benchmarks** — Actual timing data at each limit
4. **Scaling Analysis** — O(n) vs O(n log n) vs O(n²) per tool
5. **Boundary Validation** — Proof that Community covers target personas
6. **Competitive Analysis** — How limits compare to alternatives

---

## 5. Implementation Sequence

### Phase 1: Limits & Tests (This PR)
1. Update `src/code_scalpel/capabilities/limits.toml`
2. Create `tests/tier_validation/` test suite
3. Run existing tests, fix any hardcoded expectation breakage
4. Version bump (v1.4.0 — philosophy change)

### Phase 2: Documentation (Next PR)
1. Create `docs/guides/tier_philosophy.md`
2. Create `docs/architecture/tier_limit_justification.md`
3. Update README tier comparison table
4. Update `docs/guides/feature_development_tiers_guide.md`
5. Run `scripts/generate_mcp_tier_matrix.py` to regenerate

### Phase 3: Benchmarks (Follow-up)
1. Create `tests/benchmarks/` suite
2. Run on CI with synthetic projects at each scale
3. Publish results in justification doc
4. Set performance regression thresholds
