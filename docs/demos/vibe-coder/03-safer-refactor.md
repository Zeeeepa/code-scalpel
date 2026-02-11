# Demo: "No More Broken Commits: Auto-Validate Refactors"

**Persona**: Vibe Coder
**Pillar**: Safer AI
**Tier**: Pro ($49/month)
**Duration**: 8 minutes
**Fixture**: Custom refactor scenario with cross-file references

## Scenario

Developer renames a function but misses string references in SQL queries and dict keys. Code Scalpel's `simulate_refactor` catches broken references before committing.

## Tools Used

- `simulate_refactor` (Pro tier)
- `get_symbol_references`

## Recording Script

### Step 1: The Common Mistake (0:00-1:00)

- Show class with method `user_id`
- References in code, SQL strings, dict keys, config files
- Developer wants to rename: `user_id` → `account_id`

### Step 2: Standard Refactor Tool Failure (1:00-2:30)

- Use IDE "Rename Symbol"
- Shows: "3 references updated"
- Commit and run tests → 5 tests fail ❌
- Debug: missed SQL query reference, dict key, config

### Step 3: Code Scalpel Simulation (2:30-5:00)

- Prompt: "Simulate renaming `user_id` to `account_id`"
- Code Scalpel calls `simulate_refactor` (Pro tier)
- Tool performs:
  - Static analysis of all references
  - String literal scanning
  - Dynamic key detection
  - Type-aware simulation
- Returns: "8 locations would be affected"

### Step 4: Visual Diff Preview (5:00-6:00)

- Show diff of proposed changes:
  - Code references (AST-based) ✓
  - SQL string interpolation ✓
  - Dict key access ✓
  - JSON config file ✓
- On-screen: "All 8 references found before breaking anything"

### Step 5: Safe Execution (6:00-7:00)

- Apply changes
- Run tests → all pass ✓
- Show git diff: clean refactor
- On-screen: "Parse-before-write prevents broken code"

### Step 6: Pro Tier Value (7:00-8:00)

- Compare tiers:
  - Community: Basic AST refactoring
  - Pro: Cross-file, string literals, dynamic keys
- Cost: $49/month, prevents 1 broken deploy/month → $2,500 savings

## Expected Outputs

- Simulation report with confidence scores
- Risk assessment: "Medium risk - 2 dynamic references"
- Backup created automatically

## Before/After Comparison

| Tool | References Found | Tests Pass | Risk Level |
|------|------------------|------------|------------|
| IDE Rename | 3 | ❌ 5 fail | High |
| Code Scalpel | 8 (all) | ✓ All pass | Low |

## Key Talking Points

- "IDE refactoring tools miss string references"
- "Parse-before-write means no broken commits"
- "Pro tier finds references across files, strings, and configs"
- "Prevents production breakage - ROI from first saved incident"

## Pro Tier Features

- Cross-file reference tracking
- String literal analysis (SQL queries, templates)
- Dynamic key detection (dict access, JSON)
- Type-aware refactoring
- Automatic backups
- Risk assessment and confidence scores
