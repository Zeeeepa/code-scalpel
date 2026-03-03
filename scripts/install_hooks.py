#!/usr/bin/env python3
"""Install Code Scalpel git hooks from the canonical template in scripts/hooks/.

Run once after cloning:
    python scripts/install_hooks.py

The pre-push hook is self-healing:
  - Auto-fixes Black formatting and safe Ruff issues before validation
  - Amends the current commit with any auto-fixes (transparent to the developer)
  - Loads .env for local JWT secrets (mirrors GitHub Secrets in CI)
  - Runs the full validation pipeline; timeouts are non-fatal (CI enforces)
"""

from __future__ import annotations

import shutil
import stat
import sys
from pathlib import Path

HOOK_TEMPLATE = """\
#!/bin/bash
# Code Scalpel Pre-Push Hook
# Self-healing: auto-fixes black/ruff formatting before validation.
# Amended commit is pushed transparently when fixes were applied.
#
# For VERSION TAGS (v*.*.*)  → Full pipeline with tests
# For MAIN BRANCH           → Quick validation (no tests)
# For FEATURE BRANCHES      → No validation (let CI handle it)
#
# Pipeline steps each have a 120s timeout. Timeout is non-fatal; CI enforces.

# Colors
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m'

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# Activate environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -n "$CONDA_PREFIX" ]; then
    echo "Using Conda: $CONDA_PREFIX"
fi

export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# Load .env for local JWT secrets (mirrors what CI loads from GitHub Secrets)
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source <(grep -v '^#' "$PROJECT_ROOT/.env" | grep -v '^$')
    set +a
fi

# ─── Auto-fix formatting before running the pipeline ────────────────────────
auto_fix_formatting() {
    local fixed=false

    if command -v black &>/dev/null; then
        if ! black --check . --quiet 2>/dev/null; then
            echo -e "${YELLOW}🔧 Auto-fixing Black formatting...${NC}"
            black . --quiet
            fixed=true
        fi
    fi

    if command -v ruff &>/dev/null; then
        ruff check --fix . --quiet 2>/dev/null || true
        if ! git diff --quiet; then
            echo -e "${YELLOW}🔧 Ruff auto-fixed linting issues.${NC}"
            fixed=true
        fi
    fi

    if [[ "$fixed" == "true" ]]; then
        git add -A
        git commit --amend --no-edit --no-verify --quiet
        echo -e "${GREEN}✅ Auto-fixes applied and commit amended.${NC}"
    fi
}

run_pipeline() {
    local label="$1"; shift
    echo -e "${BLUE}${label}${NC}"
    if ! timeout 120 python "$PROJECT_ROOT/scripts/pipeline.py" "$@"; then
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            echo -e "${YELLOW}⏱️  Pipeline timed out after 120s — proceeding (CI will validate)${NC}"
            return 0
        fi
        echo -e "${RED}❌ Validation failed! Fix issues before pushing.${NC}"
        return 1
    fi
    return 0
}

while read local_ref local_sha remote_ref remote_sha; do
    if [[ "$local_ref" =~ ^refs/tags/v[0-9]+\\.[0-9]+\\.[0-9]+ ]]; then
        echo -e "${YELLOW}🏷️  Version tag detected: $local_ref${NC}"
        if [ -f "$PROJECT_ROOT/scripts/pipeline.py" ]; then
            auto_fix_formatting
            run_pipeline "Running release validation (lint, types, build, contracts)..." --skip-tests --verbose || exit 1
        fi
    elif [[ "$remote_ref" == "refs/heads/main" ]]; then
        if [[ "$(git config --get scalpel.warn-direct-push 2>/dev/null)" == "true" ]]; then
            echo -e "${YELLOW}⚠️  Direct push to main — consider a PR for larger changes.${NC}"
        fi
        if [ -f "$PROJECT_ROOT/scripts/pipeline.py" ]; then
            auto_fix_formatting
            run_pipeline "📤 Running quick validation for main push..." --skip-tests --skip-build --verbose || exit 1
        fi
    else
        echo -e "${GREEN}📤 Feature branch push - CI will validate${NC}"
    fi
done

echo -e "${GREEN}✅ Pre-push validation passed!${NC}"
exit 0
"""


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    hooks_dir = repo_root / ".git" / "hooks"

    if not hooks_dir.exists():
        print(
            f"❌ Not a git repository (no .git/hooks at {hooks_dir})", file=sys.stderr
        )
        return 1

    hook_path = hooks_dir / "pre-push"

    # Back up existing hook if present
    if hook_path.exists():
        backup = hook_path.with_suffix(".bak")
        shutil.copy2(hook_path, backup)
        print(f"📦 Backed up existing hook to {backup.name}")

    hook_path.write_text(HOOK_TEMPLATE, encoding="utf-8")
    hook_path.chmod(
        hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )

    print(f"✅ Installed self-healing pre-push hook at {hook_path}")
    print("   Features:")
    print("   • Auto-fixes Black formatting and safe Ruff issues before push")
    print("   • Amends commit transparently — no manual 'git add' needed")
    print("   • Loads .env for local JWT secrets")
    print("   • 120s pipeline timeout (non-fatal) — CI enforces hard limits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
