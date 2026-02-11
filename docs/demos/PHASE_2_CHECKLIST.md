# Phase 2: Asset Preparation Checklist

**Quick reference checklist for Phase 2 completion**

Print this document and check off items as you complete them.

---

## Day 1-2: Environment Setup

### Test Workspace
- [ ] Created demo workspace at `~/code-scalpel-demos`
- [ ] Cloned Code Scalpel repository
- [ ] Installed Code Scalpel in editable mode
- [ ] Verified installation: `codescalpel version`

### Tier Configuration
- [ ] Community tier limits configured
- [ ] Pro tier license installed (if available)
- [ ] Enterprise tier license installed (if available)
- [ ] Verified capabilities: `code-scalpel get-capabilities`

### MCP Server
- [ ] Created `~/.config/claude-desktop/mcp_settings.json`
- [ ] Added Code Scalpel MCP server configuration
- [ ] Restarted Claude Desktop
- [ ] Verified tools available in Claude Desktop

### Git Setup
- [ ] Initialized git in demo workspace
- [ ] Created initial commit
- [ ] Set up demo-specific directories (vibe-coder, developer, tech-leader)

---

## Day 3-4: Fixture Preparation

### Vibe Coder Fixtures
- [ ] **Large File (2000 lines)**
  - [ ] Created `fixtures/large_file_2000_lines.py`
  - [ ] Verified: `wc -l` shows ~2000 lines
  - [ ] Tested: `code-scalpel extract-code` works

- [ ] **Fake Sanitizer**
  - [ ] Created `fixtures/fake_sanitizer.py`
  - [ ] Tested: `code-scalpel security-scan` detects XSS

- [ ] **Refactor Scenario**
  - [ ] Created `fixtures/refactor_scenario/models.py`
  - [ ] Created `fixtures/refactor_scenario/api.py`
  - [ ] Created `fixtures/refactor_scenario/queries.sql`
  - [ ] Created `fixtures/refactor_scenario/config.json`
  - [ ] Tested: `code-scalpel simulate-refactor` finds 8 references

- [ ] **Audit Trail Example**
  - [ ] Created sample `.code-scalpel/audit.jsonl`
  - [ ] Verified format and readability

### Developer Fixtures
- [ ] **Type Evaporation**
  - [ ] Created `fixtures/type_evaporation/backend/models.py`
  - [ ] Created `fixtures/type_evaporation/backend/api.py`
  - [ ] Created `fixtures/type_evaporation/frontend/api_client.ts`
  - [ ] Tested: `code-scalpel type-evaporation-scan` detects mismatch

- [ ] **Large Legacy File**
  - [ ] Created 2000-line file for surgical editing demo
  - [ ] Verified: File is parseable

- [ ] **Hidden Bug**
  - [ ] Created `fixtures/hidden_bug/edge_case_puzzle.py`
  - [ ] Tested: `code-scalpel symbolic-execute` finds edge case

- [ ] **Custom Policy**
  - [ ] Created `.code-scalpel/policies/team_standards.yml`
  - [ ] Tested: `code-scalpel code-policy-check` validates

### Tech Leader Fixtures
- [ ] **Typosquat Trap**
  - [ ] Created `fixtures/typosquat_trap/requirements.txt` with pyaml
  - [ ] Tested: `code-scalpel scan-dependencies` detects typosquat

- [ ] **Policy Violations**
  - [ ] Created `fixtures/policy_violations/risky_commit.py`
  - [ ] Tested: `code-scalpel code-policy-check` finds violations

- [ ] **Compliance Sample**
  - [ ] Created multi-file codebase for compliance demo
  - [ ] Tested: `code-scalpel code-policy-check --compliance` works

- [ ] **Monorepo Sample**
  - [ ] Created large repo simulation or real example
  - [ ] Tested: `code-scalpel crawl-project` completes

---

## Day 5: Recording Equipment

### Screen Recording
- [ ] **OBS Studio installed**
- [ ] **OBS configured**:
  - [ ] Video: 1920×1080, 30fps
  - [ ] Output: x264, CBR, 6000 Kbps
  - [ ] Audio: 48kHz stereo
- [ ] **Scenes created**:
  - [ ] Scene 1: Full screen
  - [ ] Scene 2: Split screen
  - [ ] Scene 3: Browser only
- [ ] **Test recording completed** (30 seconds)
- [ ] **Playback verified** (smooth, no dropped frames)

### Audio
- [ ] **Blue Yeti microphone connected** (or equivalent)
- [ ] **Configured**:
  - [ ] Pattern: Cardioid
  - [ ] Gain: 50-60%
  - [ ] Monitoring: Off
- [ ] **Test recording** (say "Testing 1, 2, 3")
- [ ] **Verified**:
  - [ ] No background noise
  - [ ] Clear voice
  - [ ] No clipping

### Terminal
- [ ] **iTerm2/Terminal configured**:
  - [ ] Font: 18pt minimum
  - [ ] Theme: High contrast (Solarized Dark or Nord)
  - [ ] Size: 120 columns × 40 rows
- [ ] **Readability test** (view from 6 feet away)
- [ ] **Command history cleared**

### IDE (VS Code)
- [ ] **Settings configured**:
  - [ ] Font size: 16pt
  - [ ] Line height: 24
  - [ ] Theme: GitHub Dark or similar
  - [ ] Minimap: Disabled
  - [ ] Whitespace: Hidden
  - [ ] Zoom: 1.0 or 1.2
- [ ] **Extensions installed**:
  - [ ] Better Comments
  - [ ] Error Lens
  - [ ] GitLens
- [ ] **Readability test** (view from 6 feet away)

### Environment
- [ ] **Workspace clean**:
  - [ ] Desktop icons hidden
  - [ ] Unnecessary apps closed
  - [ ] Notifications disabled (Do Not Disturb)
  - [ ] Browser bookmarks cleaned
- [ ] **Physical setup**:
  - [ ] Clean desk
  - [ ] Good lighting
  - [ ] Quiet environment

---

## Day 6-7: Visual Assets

### Comparison Tables (8 total)
- [ ] **Token usage comparison** (Vibe Coder #1)
  - Size: 1920×400px, PNG, transparent
- [ ] **LLM vs Code Scalpel accuracy** (Vibe Coder #2)
- [ ] **IDE vs Code Scalpel refactoring** (Vibe Coder #3)
- [ ] **Type checking results** (Developer #1)
- [ ] **Surgical edit costs** (Developer #2)
- [ ] **Symbolic execution paths** (Developer #3)
- [ ] **Supply chain scan results** (Tech Leader #2)
- [ ] **Monorepo performance** (Tech Leader #4)

### Mermaid Diagrams (5 total)
- [ ] **Taint flow** (Vibe Coder #2)
  - Size: 1920×1080px, PNG, transparent
- [ ] **Type evaporation data flow** (Developer #1)
- [ ] **Symbolic execution CFG** (Developer #3)
- [ ] **Supply chain dependency graph** (Tech Leader #2)
- [ ] **CI/CD pipeline** (Tech Leader #3)

### On-Screen Overlays (10 total)
- [ ] "75x cheaper" (Vibe Coder #1)
- [ ] "Graph-based analysis = ground truth" (Vibe Coder #2)
- [ ] "Parse-before-write prevents broken code" (Vibe Coder #3)
- [ ] "Graph sees what context windows miss" (Developer #1)
- [ ] "30x cheaper, 10x ROI" (Developer #2)
- [ ] "NASA-grade verification" (Developer #3)
- [ ] "SOC2 in 60 seconds" (Tech Leader #1)
- [ ] "Zero-day supply chain detection" (Tech Leader #2)
- [ ] "12x ROI" (Tech Leader #3)
- [ ] "1200x faster updates" (Tech Leader #4)

**Overlay Specs**: 1920×200px, Inter Bold 48pt, white on dark semi-transparent

### Thumbnail Templates (6 total)
- [ ] Vibe Coder template (2 variations)
- [ ] Developer template (2 variations)
- [ ] Tech Leader template (2 variations)

**Thumbnail Specs**: 1280×720px, high contrast, persona icon + pillar badge

---

## Verification: Command Testing

### Vibe Coder Commands
- [ ] **Demo 1**: `code-scalpel extract-code large_file.py process_payment`
- [ ] **Demo 2**: `code-scalpel security-scan fake_sanitizer.py`
- [ ] **Demo 3**: `code-scalpel simulate-refactor models.py --old user_id --new account_id`
- [ ] **Demo 4**: `cat .code-scalpel/audit.jsonl | jq`

### Developer Commands
- [ ] **Demo 1**: `code-scalpel type-evaporation-scan fixtures/type_evaporation/`
- [ ] **Demo 2**: `code-scalpel update-symbol legacy_system.py process_transaction`
- [ ] **Demo 3**: `code-scalpel symbolic-execute edge_case_puzzle.py validate_password`
- [ ] **Demo 4**: `code-scalpel code-policy-check --policy team_standards.yml`

### Tech Leader Commands
- [ ] **Demo 1**: `code-scalpel code-policy-check --compliance SOC2`
- [ ] **Demo 2**: `code-scalpel scan-dependencies --enable-typosquat-detection`
- [ ] **Demo 3**: `code-scalpel security-scan risky_commit.py`
- [ ] **Demo 4**: `code-scalpel crawl-project --incremental`

---

## Dry Runs (At least 3)

### Vibe Coder Dry Run
- [ ] **Demo 1** (Cheaper AI): Full execution with timer
  - [ ] All commands work
  - [ ] Outputs match expected
  - [ ] Timing: Target 5 min ±30s
  - [ ] Adjustments noted

### Developer Dry Run
- [ ] **Demo 1** (Accurate AI): Full execution with timer
  - [ ] All commands work
  - [ ] Outputs match expected
  - [ ] Timing: Target 12 min ±30s
  - [ ] Adjustments noted

### Tech Leader Dry Run
- [ ] **Demo 1** (Governable AI): Full execution with timer
  - [ ] All commands work
  - [ ] Outputs match expected
  - [ ] Timing: Target 10 min ±30s
  - [ ] Adjustments noted

---

## Final Sign-Off

### Quality Checks
- [ ] **All fixtures tested and working**
- [ ] **All commands produce expected outputs**
- [ ] **Recording quality meets standards** (1080p, clear audio)
- [ ] **Visual assets match brand guidelines**
- [ ] **Timing verified** (all within ±30s of target)

### Approvals
- [ ] **Team lead approval**: Fixture quality
- [ ] **Design approval**: Visual assets
- [ ] **Technical approval**: Command accuracy
- [ ] **Ready for Phase 3**: Recording

---

## Notes / Issues

Record any issues encountered during preparation:

```
Issue 1:
[Description]
[Resolution]

Issue 2:
[Description]
[Resolution]
```

---

## Phase 2 Completion

**Date Started**: __________________

**Date Completed**: __________________

**Total Days**: __________________

**Ready for Phase 3**: ☐ Yes  ☐ No (explain: _________________)

---

**Prepared by**: __________________

**Reviewed by**: __________________

**Approved by**: __________________

---

**Next Step**: Proceed to Phase 3 (Recording)

**Phase 3 Priority**: Record Developer demos first (highest impact)
