# Verification + V1.0 Spec: rename_symbol

**Date**: December 30, 2025  
**Status**: ✅ VERIFIED (current behavior) + 📌 V1.0 starting-point spec (proposed)

This document has two goals:
1) Record what `rename_symbol` does today (verified against implementation).
2) Define a clear, tier-differentiated starting point for `rename_symbol` V1.0 so future work is testable and unambiguous.

---

## 1) Tool Overview

**Intent**: Rename a symbol safely.

**Symbol kinds**:
- `function` (e.g., `old_func` → `new_func`)
- `class` (e.g., `OldClass` → `NewClass`)
- `method` (e.g., `OldClass.old_method` → `new_method`)

---

## 2) Current Behavior (V0) — VERIFIED

### What it does
- Renames the **definition only** inside the provided file.
- Does **not** rewrite references in other files.
- Does **not** rewrite call sites in the same file (unless they happen to be part of the definition itself).
- Can write a `.bak` backup when `create_backup=True`.

### Tier behavior (current)
- **Community / Pro / Enterprise:** same execution behavior (no tier-specific limits defined for this tool today).

### Implementation anchors
- **MCP tool:** `src/code_scalpel/mcp/server.py` (`rename_symbol`)
- **Patch engine:** `code_scalpel.surgery.surgical_patcher.SurgicalPatcher.rename_symbol`

---

## 3) Scope Rules (V1.0) — PROPOSED

### Definitions
- **Definition rename**: rename only the symbol’s defining `def`/`class` line.
- **Reference rename**: update call sites and attribute references that point to the renamed symbol.
- **Import rename**: update import statements that reference the renamed symbol.

### Non-goals (explicitly out of scope for V1.0)
- Renaming inside strings/comments (e.g., docstrings, log messages).
- "Search and replace" across arbitrary text.
- Dynamic/reflection-heavy rewrites (e.g., `getattr(x, "old_name")`).
- Language-server integration (LSP) requirements.

---

## 4) Tier Feature Split (V1.0) — PROPOSED

The repo posture is that tools exist at all tiers; tiers differ by **capabilities and limits**. For `rename_symbol`, the V1.0 split below creates meaningful differentiation while staying safe.

### Community (V1.0)
**Goal**: Safe, deterministic, single-file rename.
- ✅ Definition rename (single file)
- ✅ Backup support (`create_backup`)
- ✅ Strict safety checks: path resolution + path security validation
- ✅ Clear warnings when references are not updated
- ❌ No cross-file reference rewriting
- ❌ No import rewriting

**Suggested limits (if/when we add them to `.code-scalpel/limits.toml`)**
- `max_files_searched = 0`, `max_files_updated = 0` (no cross-file updates)

### Pro (V1.0)
**Goal**: Project-level refactor with bounded scope.
- ✅ Everything in Community
- ✅ Cross-file **reference rename** within the workspace/project root
- ✅ Import renaming for straightforward cases (`from x import OldName`, `import module; module.OldName` where resolvable)
- ✅ Optional dry-run/preview output (rename plan) so callers can see the impact before write
- ❌ No organization-wide / multi-repo rewriting

**Suggested limits**
- `max_files_searched` and/or `max_files_updated` (e.g., 500 / 200)

### Enterprise (V1.0)
**Goal**: Enterprise-scale refactor with governance hooks.
- ✅ Everything in Pro
- ✅ Organization-wide renaming (monorepo-aware / workspace collection aware)
- ✅ Optional governance metadata (e.g., ownership attribution if present in repo conventions)
- ✅ Optional integration path with higher-level “atomic refactor” workflows (git branch + tests + rollback) via separate orchestration

**Suggested limits**
- Unlimited (omit keys in `.code-scalpel/limits.toml`)

---

## 5) Acceptance Criteria & Test Plan (V1.0)

### Community acceptance (definition-only)
- Given a file defining `def old_func(): ...`, calling `rename_symbol(..., target_type="function", target_name="old_func", new_name="new_func")`:
  - returns `success=True`
  - changes the `def` line to `def new_func(...):`
  - leaves other files untouched
  - emits a warning (or documented behavior) that references were not updated

### Pro acceptance (project references)
- Given two files:
  - `a.py` defines `def old_func(): ...`
  - `b.py` calls `old_func()`
- Pro-tier rename updates both definition and call site, returns success, and records which files were changed.

### Enterprise acceptance (org-wide)
- Given a monorepo/workspace collection fixture with symbol references across multiple packages/modules, Enterprise-tier rename updates all resolvable references within the org/workspace scope.

---

## 6) Notes / Guardrails

- `rename_symbol` should stay **surgical** and conservative: update only where the symbol resolution is sufficiently confident.
- Any broader workflows (branch creation, test execution, rollback) should remain **separately orchestrated**, even if Enterprise is the tier that enables them.

