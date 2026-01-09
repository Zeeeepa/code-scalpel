# Pro/Enterprise Code Inventory - Triage Summary

**Generated:** 2026-01-09  
**Source:** Grep for: pro_tier|Pro|enterprise|governance|policy|compliance|audit  
**Total Lines:** 23,928

## Categorization

### False Positives (Remove from Extraction List)
- **Docs:** All matches in `docs/` (roadmaps, tier comparisons, documentation examples)
- **Test Names:** Compliance-related test names, policy validation tests
- **Comments:** TODOs, feature roadmap comments, aspirational features not yet implemented
- **Examples:** Template code, configuration examples, placeholder implementations

### Real Proprietary Code (Extract to Pro/Enterprise)

#### 1. Licensing & Tier System
- `src/code_scalpel/licensing/` - MIT verification, tier detection, feature gating
- `src/code_scalpel/licensing/features.py` - Tier-specific feature flags
- `src/code_scalpel/licensing/validator.py` - License validation and tier mapping

#### 2. Pro Tier Enhancements
**Files with Pro-specific logic:**
- `src/code_scalpel/analysis/` - Enhanced analysis features (advanced patterns, framework detection)
- `src/code_scalpel/ast_tools/call_graph.py` - Advanced polymorphism resolution (Pro tier marker at line 956)
- `src/code_scalpel/ast_tools/import_resolver.py` - Re-export tracking (Pro feature at line 84)
- Policy enforcement stubs in various analysis modules

#### 3. Enterprise Tier Features
**Files with Enterprise-specific logic:**
- `src/code_scalpel/agents/` - Autonomy agents (AutoGen, CrewAI integration)
  - `base_agent.py` - Enterprise governance, audit logging, compliance tracking
  - `security_agent.py` - Security analysis with compliance reporting
- `src/code_scalpel/policy_engine/` - Policy enforcement and governance
- Compliance audit trails, GDPR/SOX tracking comments

#### 4. Governance & Compliance
- `src/code_scalpel/policy_engine/` - Policy validation and enforcement
- Comments in various files about SOC2, HIPAA, audit trails (TODO/planned features)

## Extraction Strategy

### Phase 2a: Community Tier (No Proprietary Code)
- Core MCP tools with basic capabilities
- Basic licensing validation (MIT, free tier)
- All public documentation

### Phase 2b: Pro Tier
Extract these files/modules:
```
src/code_scalpel/analysis/framework_detector.py      [Pro tier feature]
src/code_scalpel/analysis/smart_crawl.py             [Pro tier feature]
src/code_scalpel/analysis/generated_code.py          [Pro tier feature]
src/code_scalpel/ast_tools/call_graph.py             [Advanced resolution - Pro]
src/code_scalpel/ast_tools/import_resolver.py        [Alias/wildcard/reexport - Pro]
src/code_scalpel/licensing/features.py               [Pro feature flags]
src/code_scalpel/licensing/pro_limits.py             [Pro-specific limits]
```

### Phase 2c: Enterprise Tier
Extract these files/modules:
```
src/code_scalpel/agents/                             [Autonomy agents]
  ├── base_agent.py                                  [Enterprise governance]
  ├── security_agent.py                              [Enterprise compliance]
  └── [other agents]                                 [Enterprise features]

src/code_scalpel/policy_engine/                      [Governance & compliance]
  ├── code_policy_check/                             [Compliance auditing]
  └── [governance modules]                           [Policy enforcement]

src/code_scalpel/licensing/enterprise_limits.py      [Enterprise feature gates]
```

## Key Findings

1. **Most matches are documentation** - Tier descriptions, roadmaps, examples
2. **Real code is concentrated** in:
   - Licensing system (`licensing/` directory)
   - Analysis enhancements (`analysis/` and `ast_tools/`)
   - Autonomy agents (`agents/` directory)
   - Policy enforcement (`policy_engine/` directory)

3. **Backburned autonomy tests** should stay in monolith until v3.3.1:
   - `tests/autonomy/test_autonomy_autogen.py` - 3 tests (5 failures)
   - `tests/autonomy/test_autonomy_crewai.py` - 2 tests (2 failures)

## Next Action

- [ ] Verify this categorization against actual file contents
- [ ] Create extraction manifest: which files go to Community/Pro/Enterprise
- [ ] Begin Phase 2 code extraction using this guide
