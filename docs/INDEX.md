# Code Scalpel – Pre-Release Pipeline Documentation Index

**Created:** January 27, 2026  
**Status:** Architecture Complete & Ready for Implementation  
**Version:** 1.0

---

## Document Overview

### 📘 Main Documents

#### 1. **PRE_RELEASE_PIPELINE.md** (50 KB, 1583 lines)
**Full Specification for Development Team**

This is the **primary reference document** for implementing the entire pre-release validation system.

**What It Contains:**
- Executive summary with key decisions
- Purpose, goals, and success criteria
- Current state analysis
- Proposed architecture with detailed diagrams
- Core principles (5 non-negotiable rules)
- Capability model specification
- License architecture (existing + enhancements)
- Test matrix & coverage (300 tests)
- CI/CD pipeline specification (8 stages)
- Enforcement rules & blockers (7 blockers, 4 warnings)
- Design patterns (forbidden vs required)
- 4-phase implementation roadmap
- Success criteria & metrics
- FAQ & troubleshooting
- Appendices with glossary

**Who Should Read:** Development Team Leads, Architecture Review, Implementation Team

**Read Time:** 20-30 minutes (or reference as needed)

**Key Sections:**
- [Core Principles](#core-principles) - Non-negotiable rules
- [Capability Model](#capability-model) - How tier limits work
- [Test Matrix](#test-matrix--coverage) - All test scenarios
- [CI/CD Pipeline](#cicd-pipeline-specification) - 8-stage workflow
- [Design Patterns](#design-patterns--best-practices) - What to do/not do
- [Implementation Roadmap](#implementation-roadmap) - 4-week plan

---

#### 2. **QUICK_REFERENCE.md** (9 KB, 340 lines)
**Quick Start Guide for All Teams**

A **condensed, scannable reference** for developers, DevOps, QA, and product teams.

**What It Contains:**
- TL;DR (60 seconds)
- Key changes overview
- New files/directories
- For tool developers (new pattern)
- For DevOps (secrets setup)
- For QA (test coverage)
- For product (pricing enforcement)
- Adding new tier-gated features (step-by-step)
- Capability snapshot approval workflow
- Troubleshooting section
- Key files to know
- One-minute recap table

**Who Should Read:** All team members (especially non-architects)

**Read Time:** 2-3 minutes

**Best For:** Onboarding new team members, quick lookups

---

### 📋 Supporting Documents

#### 3. **CODEBASE_EXPLORATION_REPORT.md** (Existing)
**Deep Dive: Current Licensing & Tier System**

Understanding what already exists before building on it.

**What It Contains:**
- License/tier implementation (JWT, offline validation)
- Tool registration (21 MCP tools, tier mapping)
- CLI architecture
- Test infrastructure
- License storage/injection patterns

**Read When:** Need to understand existing systems (Phase 1)

---

## Quick Navigation

### For Architects & Decision-Makers

**Start Here:**
1. Read: PRE_RELEASE_PIPELINE.md → [Executive Summary](#executive-summary)
2. Review: [Key Decisions](#what-weve-delivered)
3. Approve: [Sign-Off & Approval](#sign-off--approval) section

**Deliverables to Evaluate:**
- Test matrix scope: 300+ tests across 3 tiers × 3 transports
- Capability model: auto-generated golden files + manual approval
- CI pipeline: 8-stage workflow with blocker enforcement
- Timeline: 4 weeks (Jan 27 – Feb 21)

**Decision Gates:**
- ✅ Full coverage test matrix approved
- ✅ Hybrid capability snapshots approved  
- ✅ GitHub secrets ready
- ✅ Timeline acceptable

---

### For Implementation Team (Phase 1-4 Leaders)

**Phase 1 Lead:** Capability Model & Resolver
- Read: PRE_RELEASE_PIPELINE.md → [Capability Model](#capability-model)
- Read: PRE_RELEASE_PIPELINE.md → [Implementation Roadmap](#implementation-roadmap) → Phase 1
- Deliverables: Resolver function, golden files, MCP method

**Phase 2 Lead:** Test Infrastructure
- Read: PRE_RELEASE_PIPELINE.md → [Test Architecture](#test-architecture)
- Read: QUICK_REFERENCE.md → [For QA](#for-qa-new-test-coverage)
- Deliverables: Adapters, matrix tests, 150+ test cases

**Phase 3 Lead:** CI/CD Pipeline
- Read: PRE_RELEASE_PIPELINE.md → [CI/CD Pipeline](#cicd-pipeline-specification)
- Reference: GitHub Actions YAML template in document
- Deliverables: 8-stage pipeline, blockers functional

**Phase 4 Lead:** Documentation & Training
- Read: PRE_RELEASE_PIPELINE.md → [Design Patterns](#design-patterns--best-practices)
- Reference: Quick Reference guide
- Deliverables: Guides, examples, team training

---

### For Tool Developers

**Essential Reading:**
1. QUICK_REFERENCE.md → [For Tool Developers](#for-tool-developers-new-pattern-required)
2. PRE_RELEASE_PIPELINE.md → [Design Patterns](#design-patterns--best-practices)
3. PRE_RELEASE_PIPELINE.md → [Adding New Tier-Gated Features](#adding-a-new-tier-gated-feature)

**What You Need to Know:**
- ❌ Don't: Hardcode tier limits in tool code
- ✅ Do: Read limits from `get_tool_capabilities()`
- ✅ Do: Use `limits.toml` as single source of truth
- ✅ Do: Write tests for each tier
- ⚠️ Remember: All 22 tools always registered, schema never changes

---

### For DevOps Engineers

**Essential Reading:**
1. QUICK_REFERENCE.md → [For DevOps](#for-devops-new-secrets-required)
2. PRE_RELEASE_PIPELINE.md → [License Architecture](#license-architecture-existing-enhanced)
3. PRE_RELEASE_PIPELINE.md → [CI/CD Pipeline Specification](#cicd-pipeline-specification)

**What You Need to Do:**
- [ ] Configure GitHub secrets: `CODESCALPEL_LICENSE_PRO` and `CODESCALPEL_LICENSE_ENTERPRISE`
- [ ] Deploy 8-stage GitHub Actions workflow
- [ ] Set calendar reminder: 30 days before license expiry
- [ ] Implement secret rotation procedure

---

### For QA Engineers

**Essential Reading:**
1. QUICK_REFERENCE.md → [For QA](#for-qa-new-test-coverage)
2. PRE_RELEASE_PIPELINE.md → [Test Matrix & Coverage](#test-matrix--coverage)
3. PRE_RELEASE_PIPELINE.md → [Enforcement Rules](#enforcement-rules--blockers)

**What You'll Test:**
- Tool availability (22 tools × 3 tiers = 66 tests)
- Tier limits (enforcement, not just documentation)
- License validation (secrets injection, expiry)
- Capability snapshots (regression detection)
- All 3 transports (stdio, HTTP, Docker)

**Total Coverage:** ~300 tests, 15-minute runtime

---

### For Product Managers

**Essential Reading:**
1. QUICK_REFERENCE.md → [For Product](#for-product-what-changes)
2. PRE_RELEASE_PIPELINE.md → [Core Principles](#core-principles)
3. PRE_RELEASE_PIPELINE.md → [Capability Model](#capability-model)

**What Changes:**
- Pricing is now **executable code** (tested in CI)
- Capabilities are **discoverable** (agents can query)
- Changes are **auditable** (golden files show diffs)
- Releases are **validated** (no pricing escapes)

**Tier Change Process:**
1. Update limits in `limits.toml`
2. PR generates new capability snapshot
3. CI shows diff for review
4. Approve with "regenerate-capabilities" label
5. Golden files auto-update on merge
6. Release with confidence

---

## Key Concepts Explained

### Stable Tool Surface
**What It Means:** All 22 tools always present, never hidden

- ✅ 22 tools in tool list (always)
- ✅ Tool schemas immutable
- ❌ No per-tier tool hiding
- ❌ No per-tier schema changes

**Why?** Prevents LLM agents from hallucinating unavailable tools

---

### Capability Envelope
**What It Means:** Runtime vector describing what's available

```json
{
  "tier": "pro",
  "tools": {
    "analyze_code": {
      "available": true,
      "max_files": 5000,
      "max_depth": 15
    },
    "unified_sink_detect": {
      "available": false,
      "requires_tier": "enterprise"
    }
  }
}
```

**Queryable Via:**
- MPC method: `capabilities/get`
- CLI: `codescalpel capabilities --json`
- Programmatically: `get_tool_capabilities(tool_id)`

---

### Golden Capability Files
**What They Are:** Committed reference files for regression testing

- `capabilities/free.json` - All capabilities at FREE tier
- `capabilities/pro.json` - All capabilities at PRO tier
- `capabilities/enterprise.json` - All capabilities at ENTERPRISE tier

**What Happens on Change:**
1. Code changes → CI generates new capability
2. CI compares against golden file
3. If different → CI fails with diff
4. Developer reviews diff
5. If intentional → Approve PR with "regenerate-capabilities" label
6. Golden file auto-regenerates on merge

---

### Blocker Violations
**What They Are:** Tests that MUST pass for release

| Blocker | Why | Example |
|---------|-----|---------|
| Tool count ≠ 22 | Schema stability | Expected 22, got 21 |
| Schema changed | Client contract | Input type changed |
| Limits not enforced | Pricing integrity | PRO can access FREE limit |
| Capability mismatch | Pricing audit | max_files changed without approval |
| License not injected | Tier detection | Secret empty |

**CI Behavior:** Automatic PR block (no manual override possible)

---

## File Locations

```
Code Scalpel Repository Root
│
├── docs/
│   ├── PRE_RELEASE_PIPELINE.md         ← Primary specification
│   ├── QUICK_REFERENCE.md              ← Quick start guide
│   ├── CODEBASE_EXPLORATION_REPORT.md  ← Existing systems
│   └── CI_ENHANCED_ARCHITECTURE.md     ← Early draft (reference)
│
├── src/code_scalpel/
│   ├── capabilities/
│   │   ├── resolver.py                 ← NEW: Capability lookup
│   │   └── limits.toml                 ← Central tier limits
│   │
│   └── mcp/
│       └── protocol.py                 ← NEW: get_capabilities() method
│
├── capabilities/
│   ├── free.json                       ← NEW: Golden file
│   ├── pro.json                        ← NEW: Golden file
│   ├── enterprise.json                 ← NEW: Golden file
│   └── schema.json                     ← NEW: JSON schema
│
├── tests/
│   ├── transports/
│   │   ├── adapter.py                  ← NEW: Unified interface
│   │   ├── stdio_adapter.py            ← NEW: Subprocess adapter
│   │   ├── http_adapter.py             ← NEW: HTTP adapter
│   │   └── docker_adapter.py           ← NEW: Container adapter
│   │
│   ├── tier_enforcement/
│   │   ├── test_tool_availability.py   ← NEW: Tool matrix tests
│   │   ├── test_tool_limits.py         ← NEW: Limit tests
│   │   └── test_feature_gating.py      ← NEW: Feature tests
│   │
│   └── capabilities/
│       ├── test_capability_snapshot.py ← NEW: Regression tests
│       └── test_capability_schema.py   ← NEW: Schema validation
│
└── .github/workflows/
    └── ci-tier-validation.yml          ← NEW: 8-stage pipeline
```

---

## Timeline at a Glance

```
Week 1 (Jan 27-31): Foundation
├── Capability resolver ✓
├── Golden files ✓
├── MCP method ✓
└── GitHub secrets ✓

Week 2 (Feb 3-7): Test Infrastructure
├── Transport adapters
├── Tool tests (22 tools × 3 tiers)
├── Limit tests
└── Feature tests (24 features × 3 tiers)

Week 3 (Feb 10-14): CI Pipeline
├── 8-stage workflow
├── Blocker enforcement
└── Real PR testing

Week 4 (Feb 17-21): Documentation
├── Development guide
├── Examples
└── Team training

Week 5+: Production Use
├── Full CI/CD active
├── All PRs validated
└── Continuous improvement
```

---

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Tool Stability** | 0 breaking changes | JSON schema diff |
| **Tier Limits** | 100% enforced | All 66 limit tests pass |
| **Capability Accuracy** | 100% match | Golden file comparison |
| **License Validation** | 100% working | Secret injection tests |
| **CI Runtime** | <15 minutes | GitHub Actions timer |
| **Coverage** | ≥95% tools/tier | Pytest coverage report |
| **False Positives** | <2% | Alert ratio over time |
| **Release Confidence** | 100% pass | Release test results |

---

## Common Questions

**Q: Do I need to read the entire 50KB document?**
A: No. Start with QUICK_REFERENCE.md (2 min), then read relevant sections in PRE_RELEASE_PIPELINE.md as needed.

**Q: When do I need this?**
A: Immediately if you're on implementation team. Soon if you're a tool developer. Before release for everyone else.

**Q: What if I don't understand something?**
A: Check the FAQ section in PRE_RELEASE_PIPELINE.md. Ask your team lead.

**Q: Can we start before all 4 phases?**
A: No. Phase 1 foundation is required before phases 2-4.

**Q: What if the timeline slips?**
A: Document will be updated. Current plan: 4 weeks.

---

## Next Actions

### For Architects (Today)
- [ ] Review both documents
- [ ] Check against template provided
- [ ] Approve architecture
- [ ] Assign implementation leads

### For Implementation Team (This Week)
- [ ] Read PRE_RELEASE_PIPELINE.md
- [ ] Schedule Phase 1 kickoff
- [ ] Plan Phase 1 deliverables

### For DevOps (This Week)
- [ ] Verify GitHub secrets configured
- [ ] Review CI/CD pipeline spec
- [ ] Plan GitHub Actions deployment

### For QA (This Week)
- [ ] Review test matrix (300 tests)
- [ ] Understand blocker rules
- [ ] Prepare test environment

### For All Teams (Week 2)
- [ ] Read QUICK_REFERENCE.md
- [ ] Understand new patterns
- [ ] Get ready for Phase 1 completion

---

## Document Maintenance

**Version History:**
| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 27, 2026 | Initial specification |

**Last Updated:** January 27, 2026  
**Next Review:** Upon Phase 1 completion (Week 1)

---

## Questions or Issues?

**Report bugs/feedback:** GitHub Issues with label `[docs]`  
**Architecture questions:** Contact Development Team Lead  
**Implementation help:** Contact Phase Lead  

---

**Status: ✅ Ready for Implementation**

These documents provide the complete specification for a commercial-grade, pre-release validation system ensuring Code Scalpel's tier enforcement is correct, testable, and auditable.

Every release will be validated automatically against this specification.

---

**Created by:** OpenCode Agent  
**Date:** January 27, 2026  
**Version:** 1.0
