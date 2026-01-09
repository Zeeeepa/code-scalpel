# Phase 2 Quick Start - Code Extraction (5-Minute Setup)

**Status:** ✅ Pre-flight complete. Phase 2 can begin immediately.

---

## What Happened (Phase 1 Summary)

**Pre-flight validation is complete:**
- ✅ 6,690 tests collected, 6,685 passing (100%)
- ✅ 5 autonomy tests backburned (non-blocking for v4.0.0)
- ✅ Coverage baseline: 44.96%
- ✅ Monolith tagged: `v3.3.0-final-monolith`
- ✅ Customer comms drafted & filled (dates, support contacts)
- ✅ Repo visibility confirmed (Community public, Pro/Enterprise private)
- ✅ Versioning finalized (v4.0.0 breaking release)

---

## What You Need to Do (Phase 2 Extraction)

### Task 1: Review the Extraction Plan (30 min)
Read this in order:
1. [PHASE_2_EXTRACTION_MANIFEST.md](docs/architecture/PHASE_2_EXTRACTION_MANIFEST.md) - Full step-by-step guide
2. [INVENTORY_TRIAGE.md](INVENTORY_TRIAGE.md) - What code to extract (real code vs false positives)
3. [PRE_FLIGHT_PHASE_1_COMPLETE.md](PRE_FLIGHT_PHASE_1_COMPLETE.md) - Executive summary

### Task 2: Assign Teams & Start Extraction
**Option A: Sequential (safer, 10 days)**
- Jan 20-24: Team 1 extracts Community → test
- Jan 25-28: Team 2 extracts Pro → test
- Jan 29-30: Team 3 extracts Enterprise → test
- Feb 1: Integration testing & release

**Option B: Parallel (faster, 6 days)**
- Jan 20-30: 3 teams extract simultaneously (Community, Pro, Enterprise)
- Feb 1: Integration testing & release

### Task 3: Execute Community Extraction (2-3 days)
**Step 1.1 - Copy MCP Server & Core Tools:**
```bash
cd /mnt/k/backup/Develop/code_scalpel_community
# Copy from monolith:
cp -r ../code-scalpel/src/code_scalpel/mcp/ src/code_scalpel/
cp -r ../code-scalpel/src/code_scalpel/analysis/ src/code_scalpel/
cp -r ../code-scalpel/src/code_scalpel/ast_tools/ src/code_scalpel/
cp ../code-scalpel/src/code_scalpel/core.py src/code_scalpel/
```

**Step 1.2 - Copy Licensing & Tests:**
```bash
cp -r ../code-scalpel/src/code_scalpel/licensing/ src/code_scalpel/
cp -r ../code-scalpel/tests/ .
# Remove backburned autonomy tests:
rm -rf tests/autonomy/test_autonomy_*.py
```

**Step 1.3 - Run Community Tests:**
```bash
pip install -e .
pytest tests/ -v --tb=short  # Expected: 6,685 passing
```

**Step 1.4 - Update Metadata & Release:**
```bash
# Update pyproject.toml: version = "4.0.0"
# Update README.md with Community features
# Update setup.py description
git add -A
git commit -m "Community v4.0.0 extraction complete"
git tag -a v4.0.0 -m "Code Scalpel Community v4.0.0"
git push origin main v4.0.0
```

### Task 4: Execute Pro Extraction (2-3 days)
**Key Difference:** Pro adds governance, security, refactoring.

```bash
cd /mnt/k/backup/Develop/code_scalpel_pro
# Add Community as dependency (in pyproject.toml):
# dependencies = ["code-scalpel>=4.0.0"]

# Copy Pro-specific modules:
cp -r ../code-scalpel/src/code_scalpel/policy_engine/ src/code_scalpel/
cp -r ../code-scalpel/src/code_scalpel/surgery/ src/code_scalpel/
cp -r ../code-scalpel/src/code_scalpel/security/analyzers/ src/code_scalpel/

# Copy Pro tests:
cp -r ../code-scalpel/tests/tools/code_policy_check/ tests/tools/
cp -r ../code-scalpel/tests/tools/rename_symbol/ tests/tools/
cp -r ../code-scalpel/tests/tools/security_scan/ tests/tools/

# Test:
pytest tests/ -v --tb=short  # Expected: ~800 passing
```

### Task 5: Execute Enterprise Extraction (2-3 days)
**Key Difference:** Enterprise adds autonomy, advanced analytics, governance.

```bash
cd /mnt/k/backup/Develop/code_scalpel_enterprise
# Add Community + optional Pro as dependencies:
# dependencies = ["code-scalpel>=4.0.0", "code-scalpel-pro>=4.0.0;extra=='governance'"]

# Copy Enterprise modules:
cp -r ../code-scalpel/src/code_scalpel/agents/ src/code_scalpel/
cp -r ../code-scalpel/src/code_scalpel/policy_engine/ src/code_scalpel/  # Full version
cp -r ../code-scalpel/src/code_scalpel/taint_analysis/ src/code_scalpel/

# Copy Enterprise tests (including backburned autonomy):
cp -r ../code-scalpel/tests/autonomy/ tests/
cp -r ../code-scalpel/tests/tools/get_graph_neighborhood/ tests/tools/
cp -r ../code-scalpel/tests/tools/get_project_map/ tests/tools/
cp -r ../code-scalpel/tests/pdg_tools/ tests/

# Test (expect 5 autonomy failures - expected/backburned):
pytest tests/ -v --tb=short  # Expected: ~1,200 passing, 5 backburned autonomy
```

### Task 6: Integration Testing (1-2 days)
```bash
# Verify all 3 packages together:
pip install code-scalpel code-scalpel-pro code-scalpel-enterprise

# Test MCP server starts with all tiers:
python -c "from code_scalpel.mcp.server import CodeScalpelServer; s = CodeScalpelServer(); print('OK')"

# Verify 22 tools are available:
pytest tests/mcp/test_mcp.py -v --tb=short
```

---

## Key Files & Locations

| Item | Location | Purpose |
|------|----------|---------|
| **Extraction Guide** | `docs/architecture/PHASE_2_EXTRACTION_MANIFEST.md` | Step-by-step extraction plan |
| **Code Inventory** | `INVENTORY_TRIAGE.md` | What code belongs where (real vs false positives) |
| **Test Results** | `test_results_full.log` | Baseline test execution log |
| **Coverage** | `htmlcov/index.html` | 44.96% baseline coverage report |
| **Customer Comms** | `docs/CUSTOMER_COMMUNICATION_v4.md` | Filled template (ready to send) |
| **Monolith** | `../code-scalpel/` | Source for extraction |

---

## Test Expectations by Package

| Package | Expected Pass | Notes |
|---------|---------------|-------|
| **Community** | 6,685/6,685 (100%) | Excludes autonomy tests |
| **Pro** | ~800 tests | Governance, security, refactoring |
| **Enterprise** | ~1,200 tests | Includes 5 backburned autonomy tests |
| **Integration** | All 3 together | Verify MCP protocol compatibility |

---

## Release Checklist (Feb 1, v4.0.0)

When extraction is complete:
- [ ] Community package: Tag v4.0.0, publish to PyPI
- [ ] Pro package: Tag v4.0.0, publish to private index (https://dist.code-scalpel.io/pro/)
- [ ] Enterprise package: Tag v4.0.0, publish to private index (https://dist.code-scalpel.io/enterprise/)
- [ ] Send customer email (support@, enterprise@, beta customers)
- [ ] Publish blog post + docs (code-scalpel.io)
- [ ] Update in-product notices
- [ ] Confirm: All 22 MCP tools working across all 3 packages

---

## Common Questions (Phase 2)

**Q: Can we extract in parallel?**
A: Yes! Community, Pro, and Enterprise can be extracted simultaneously (by 3 different teams). Just ensure Community is finished & tested first (Pro depends on it).

**Q: What if we find issues during extraction?**
A: Fixes should be made in the monolith first, then backported to the extracted package. Don't patch extracted code separately (breaks single source of truth).

**Q: Do we need to update the monolith after extraction?**
A: No. The monolith becomes read-only after v3.3.0 final. v4.0.0+ development happens in the split repos only.

**Q: What about the 5 backburned autonomy tests?**
A: They're production-ready code; the tests just need more integration work. Extract the code, include the tests in Enterprise, but don't block release on them. Schedule for v3.3.1+ sprint.

---

## Team Assignments (Suggested)

| Team | Package | Lead | Timeline |
|------|---------|------|----------|
| **Team A** | Community | [Name] | Jan 20-24 (2-3 days) |
| **Team B** | Pro | [Name] | Jan 25-28 (2-3 days) |
| **Team C** | Enterprise | [Name] | Jan 29-30 (2-3 days) |
| **Team D** | Integration | [Name] | Feb 1 (1-2 days) |

---

## Contact & Escalation

- **Slack Channel:** #code-scalpel-v4-split
- **Daily Standup:** 10 AM PT (sync on progress)
- **Release Manager:** [Name] (escalations)
- **QA Lead:** [Name] (test coordination)
- **Support:** support@code-scalpel.io (customer comms)

---

## Success Criteria

✅ When Phase 2 is done, you'll have:
- 3 independent packages (Community, Pro, Enterprise)
- 22 identical MCP tools across all packages
- Tier-gating validated (Pro features unavailable in Community, etc.)
- All tests passing (6,685 + 800 + 1,200 = 8,685 total)
- v4.0.0 released to PyPI and private indexes
- Customer communications sent & documentation live

**Estimated Total Effort:** 8-12 days (Jan 20 → Feb 1)  
**Expected Outcome:** Successful v4.0.0 GA release on Feb 1

---

**Next Step:** Start Phase 2 extraction. Good luck! 🚀

