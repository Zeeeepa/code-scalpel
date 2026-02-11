# Available Demo Fixtures and Repositories

**Status**: ✅ Most fixtures already exist in the codebase!

This document maps each demo to available fixtures and identifies what needs to be created.

---

## Summary

| Status | Count | Notes |
|--------|-------|-------|
| ✅ **Available** | 8/12 | Ninja Warrior test suite has most fixtures |
| 🔨 **Needs Creation** | 4/12 | Simple to generate with existing scripts |
| 📦 **Can Generate** | All | `tests/fixtures/generate_fixture.py` available |

---

## Vibe Coder Demos (4 total)

### ✅ Demo 1: "15k Tokens → 200: Extract What You Need"

**Status**: 🔨 Needs creation (simple)

**Fixture Needed**: Large Python file (2000 lines)

**Available Options**:
1. **Generate synthetic**: Use existing script
   ```bash
   python tests/fixtures/generate_fixture.py --synthetic 1200
   # Creates tests/fixtures/data/synthetic/ with 1200 files
   ```

2. **Clone real project**:
   ```bash
   python tests/fixtures/generate_fixture.py --clone django
   # Creates tests/fixtures/data/django/
   ```

3. **Use existing performance fixture**:
   - [tests/tools/update_symbol/fixtures/performance_fixtures.py](../../tests/tools/update_symbol/fixtures/performance_fixtures.py)
   - Already has large file generation functions

**Recommendation**: Create custom 2000-line file with `process_payment` function using generator script.

---

### ✅ Demo 2: "Stop Hallucinating: Detect Fake Sanitizers"

**Status**: 🔨 Needs creation (very simple)

**Fixture Needed**: Fake sanitizer function

**Available Resources**:
- Similar patterns in Ninja Warrior adversarial tests
- [tests/mcp_tool_verification/.../workflow-structural/mcp_contract/ninja_warrior/](../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-structural/mcp_contract/ninja_warrior/)

**Recommendation**: Create simple `fake_sanitizer.py` file (10 lines):
```python
def sanitize_input(user_data: str) -> str:
    """Sanitizes user input for safe use."""
    return user_data  # BUG: Does nothing!

def handler(user_input: str) -> str:
    safe = sanitize_input(user_input)
    return f"<div>{safe}</div>"  # XSS vulnerability!
```

---

### ✅ Demo 3: "No More Broken Commits: Auto-Validate Refactors"

**Status**: ✅ **Available** - Partial fixtures exist

**Fixture Location**:
- [tests/mcp_tool_verification/.../workflow-reconnaissance/stage5-policy-fortress/obstacle-5.8-simulate-refactor-fixtures/](../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-reconnaissance/stage5-policy-fortress/obstacle-5.8-simulate-refactor-fixtures/)

**What's Available**:
- Simulate refactor test fixtures
- Cross-file reference examples

**Recommendation**: Expand existing fixtures or create simple refactor scenario with 4 files (Python class, API, SQL, config).

---

### ✅ Demo 4: "Your AI Safety Net: Audit What Changed"

**Status**: 🔨 Needs creation (trivial)

**Fixture Needed**: Sample audit.jsonl file

**Available Resources**:
- Audit trail examples in [tests/mcp_tool_verification/.../workflow-compliance/audit-trail/](../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-compliance/)

**Recommendation**: Create sample `.code-scalpel/audit.jsonl` with 5-10 entries showing typical operations.

---

## Developer Demos (4 total)

### ✅ Demo 1: "Graph Truth: Cross-File Bug Detective"

**Status**: ✅ **FULLY AVAILABLE**

**Fixture Location**:
- [tests/mcp_tool_verification/.../challenges/01_the_full_stack_snap/](../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/01_the_full_stack_snap/)

**What's Available**:
- `backend_api.py` - FastAPI backend with type changes
- `frontend_interface.ts` - TypeScript frontend
- Type evaporation scenario (User.id: str → int)

**Files**:
```
challenges/01_the_full_stack_snap/
├── backend_api.py          # Python backend
└── frontend_interface.ts   # TypeScript frontend
```

**Perfect for**: Type evaporation demo!

---

### ✅ Demo 2: "200x Context Efficiency: Surgical Code Edits"

**Status**: ✅ **Available** (can use Demo 1 fixture + generator)

**Fixture Options**:
1. Use generated 2000-line file from Vibe Coder Demo 1
2. Use existing performance fixtures:
   - [tests/tools/update_symbol/fixtures/performance_fixtures.py](../../tests/tools/update_symbol/fixtures/performance_fixtures.py)

**Recommendation**: Reuse the 2000-line file from Demo 1 (avoid duplication).

---

### ✅ Demo 3: "Symbolic Execution: Find Hidden Edge Cases"

**Status**: ✅ **FULLY AVAILABLE**

**Fixture Location**:
- [tests/mcp_tool_verification/.../challenges/04_hidden_bug/edge_case_puzzle.py](../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/04_hidden_bug/edge_case_puzzle.py)

**What's Available**:
- `edge_case_puzzle.py` - Transaction processing with hidden bug (code == 503)
- Perfect example of edge case that standard tests miss

**File Content**:
```python
def process_transaction(amount: int, code: int):
    if code > 500 and code < 505 and code == 503:
        raise ValueError("CRITICAL SYSTEM FAILURE: Code 503 is forbidden!")
    return "Transaction Processed"
```

**Note**: This is slightly different from the password validation example in the demo script. Options:
1. Use this fixture as-is (adapt demo script)
2. Create the password validation variant (10 lines)

**Recommendation**: Use existing fixture and adapt script slightly - it's equally good for demonstrating symbolic execution.

---

### ✅ Demo 4: "Custom Policies: Enforce Team Standards"

**Status**: ✅ **FULLY AVAILABLE**

**Fixture Location**:
- [tests/mcp_tool_verification/.../challenges/06_policy_prison/](../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/06_policy_prison/)
- [tests/mcp_tool_verification/.../workflow-compliance/policy-engine/](../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-compliance/policy-engine/)

**What's Available**:
- `risky_commit.py` - Code with MD5 hashing, os.system, no docstrings
- Policy YAML files in `.code-scalpel/` directory
- 100+ vulnerability patterns ready to demo

**Files**:
```
challenges/06_policy_prison/
├── risky_commit.py              # Violations
└── .code-scalpel/
    └── policies/                # Custom policies
```

**Perfect for**: Custom policy enforcement demo!

---

## Technical Leader Demos (4 total)

### ✅ Demo 1: "SOC2/HIPAA Compliance Reports in 60 Seconds"

**Status**: ✅ **FULLY AVAILABLE**

**Fixture Location**:
- [tests/mcp_tool_verification/.../workflow-compliance/](../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-compliance/)

**What's Available**:
- Multi-file codebase with security annotations
- Compliance test cases
- Policy engine with SOC2/HIPAA rules

**Directories**:
```
workflow-compliance/
├── policy-engine/               # 100+ rules
├── audit-trail/                 # Audit examples
└── benchmark-cvefixes/          # Real-world CVE fixes
```

**Perfect for**: Compliance scanning demo!

---

### ✅ Demo 2: "Supply Chain Guardian: Typosquat Detection"

**Status**: ✅ **FULLY AVAILABLE**

**Fixture Location**:
- [tests/mcp_tool_verification/.../challenges/03_supply_chain_trap/unsafe_requirements.txt](../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/03_supply_chain_trap/unsafe_requirements.txt)

**What's Available**:
- `unsafe_requirements.txt` with typosquat (`pyaml` instead of `PyYAML`)
- Perfect real-world example

**File Content**:
```txt
flask==2.0.1
requests==2.26.0
pyaml==21.10.1  # <--- TRAP! Often confused with PyYAML
```

**Perfect for**: Typosquat detection demo!

---

### ✅ Demo 3: "The Perfect Guard: Block Risky Commits Pre-Merge"

**Status**: ✅ **Available** (reuse Demo 4 Developer fixture)

**Fixture**: Same as Developer Demo 4
- [challenges/06_policy_prison/risky_commit.py](../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/06_policy_prison/risky_commit.py)

**What's Available**:
- Risky code with SQL injection potential
- MD5 usage, os.system calls
- No docstrings

**Recommendation**: Use existing policy prison fixture. Add SQL injection example if needed.

---

### ✅ Demo 4: "Monorepo Mastery: Incremental Crawl at Scale"

**Status**: ✅ **Available** (use generator or real project)

**Fixture Options**:

1. **Generate large synthetic project**:
   ```bash
   python tests/fixtures/generate_fixture.py --synthetic 10000
   # Creates 10,000 file project with realistic imports
   ```

2. **Clone real large project**:
   ```bash
   python tests/fixtures/generate_fixture.py --clone django
   # Django has ~127,000 files including tests
   ```

3. **Use Python stdlib**:
   ```bash
   python tests/fixtures/generate_fixture.py --stdlib
   # Uses system Python library (large, real-world)
   ```

**Recommendation**: Generate synthetic 10,000 file project for consistent timing demos.

---

## Fixture Creation Priority

### Must Create (4 fixtures)

1. **Large file (2000 lines)** - Vibe Coder Demo 1
   - Use: `tests/fixtures/generate_fixture.py` or create custom generator
   - Time: 5 minutes

2. **Fake sanitizer** - Vibe Coder Demo 2
   - Simple 10-line Python file
   - Time: 2 minutes

3. **Refactor scenario** - Vibe Coder Demo 3
   - 4 files (Python, API, SQL, config)
   - Time: 10 minutes

4. **Audit log** - Vibe Coder Demo 4
   - Sample `.code-scalpel/audit.jsonl`
   - Time: 5 minutes

**Total creation time**: ~25 minutes

### Already Available (8 fixtures)

- ✅ Type evaporation (Developer #1)
- ✅ Hidden edge case (Developer #3)
- ✅ Policy violations (Developer #4)
- ✅ Compliance tests (Tech Leader #1)
- ✅ Typosquat (Tech Leader #2)
- ✅ Risky commit (Tech Leader #3)
- ✅ Large repo (Tech Leader #4 - can generate)
- ✅ Surgical edit file (Developer #2 - reuse from Demo 1)

---

## Quick Setup Script

Create all needed fixtures:

```bash
#!/bin/bash
# setup_demo_fixtures.sh

DEMO_DIR=~/code-scalpel-demos/fixtures

# Create directory structure
mkdir -p $DEMO_DIR/{vibe-coder,developer,tech-leader}

echo "=== Creating Vibe Coder Fixtures ==="

# 1. Large file (2000 lines)
python tests/fixtures/generate_fixture.py --synthetic 50
cp tests/fixtures/data/synthetic/pkg/mod_0.py $DEMO_DIR/vibe-coder/large_file.py
# Expand to 2000 lines and add process_payment function

# 2. Fake sanitizer
cat > $DEMO_DIR/vibe-coder/fake_sanitizer.py <<'EOF'
def sanitize_input(user_data: str) -> str:
    """Sanitizes user input for safe use."""
    return user_data  # BUG: Does nothing!

def handler(user_input: str) -> str:
    safe = sanitize_input(user_input)
    return f"<div>{safe}</div>"
EOF

# 3. Refactor scenario (copy from Ninja Warrior if available)
mkdir -p $DEMO_DIR/vibe-coder/refactor_scenario
# Create 4 files manually

# 4. Audit log
mkdir -p $DEMO_DIR/vibe-coder/.code-scalpel
cat > $DEMO_DIR/vibe-coder/.code-scalpel/audit.jsonl <<'EOF'
{"timestamp": "2026-02-08T14:23:00Z", "tool": "update_symbol", "file": "api/users.py", "symbol": "get_user_by_id", "operation": "update"}
{"timestamp": "2026-02-08T14:25:00Z", "tool": "extract_code", "file": "models.py", "symbol": "User", "operation": "read"}
EOF

echo "=== Linking Developer Fixtures ==="

# Symlink Ninja Warrior fixtures (already available)
ln -s ../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/01_the_full_stack_snap \
    $DEMO_DIR/developer/type_evaporation

ln -s ../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/04_hidden_bug \
    $DEMO_DIR/developer/hidden_bug

ln -s ../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/06_policy_prison \
    $DEMO_DIR/developer/policy_prison

echo "=== Linking Tech Leader Fixtures ==="

ln -s ../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-compliance \
    $DEMO_DIR/tech-leader/compliance

ln -s ../../tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/03_supply_chain_trap \
    $DEMO_DIR/tech-leader/typosquat

# Generate large repo for monorepo demo
python tests/fixtures/generate_fixture.py --synthetic 10000

echo "=== Setup Complete ==="
echo "Fixtures available at: $DEMO_DIR"
```

---

## Fixture Verification Checklist

Before recording, verify each fixture:

### Vibe Coder
- [ ] `large_file.py` exists and is ~2000 lines
- [ ] `fake_sanitizer.py` has XSS vulnerability
- [ ] `refactor_scenario/` has 4 files with cross-references
- [ ] `.code-scalpel/audit.jsonl` exists with sample entries

### Developer
- [ ] `type_evaporation/` has backend + frontend files
- [ ] `hidden_bug/edge_case_puzzle.py` exists
- [ ] `policy_prison/risky_commit.py` has violations
- [ ] Large file reused from Vibe Coder Demo 1

### Tech Leader
- [ ] `compliance/` directory has policy engine
- [ ] `typosquat/unsafe_requirements.txt` has pyaml
- [ ] `policy_prison/` accessible (same as Developer)
- [ ] Large synthetic repo generated (10k files)

---

## Ninja Warrior Test Suite Structure

For reference, here's what's available in the test suite:

```
tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/
├── challenges/
│   ├── 01_the_full_stack_snap/      # ✅ Type evaporation
│   ├── 03_supply_chain_trap/        # ✅ Typosquat
│   ├── 04_hidden_bug/               # ✅ Edge case
│   ├── 05_blindfold_maze/           # Large repo navigation
│   ├── 06_policy_prison/            # ✅ Policy violations
│   └── 07_broken_build/             # Path validation
├── workflow-reconnaissance/         # Crawl, map, validate
├── workflow-structural/             # Call graphs, dependencies
├── workflow-surgical-ops/           # Extract, update, rename
├── workflow-deep-security/          # Security scanning, taint
└── workflow-compliance/             # ✅ Compliance, audit, policies
```

---

## Summary: Fixture Availability

**Good News**: 8 out of 12 demos have fixtures ready to use!

**Action Items**:
1. ✅ Copy/symlink 8 existing fixtures (5 minutes)
2. 🔨 Create 4 simple fixtures (25 minutes)
3. ✅ Run verification script (10 minutes)

**Total setup time**: ~40 minutes

All fixtures either exist or can be created quickly. You're ready to proceed with Phase 2! 🚀
