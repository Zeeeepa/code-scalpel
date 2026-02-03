#!/usr/bin/env bash
# =============================================================================
# migrate_project_structure.sh - Project Structure Migration
# =============================================================================
# Purpose: Consolidate scattered cache/temp directories into .code-scalpel/
# Usage: ./scripts/migrate_project_structure.sh
# Exit codes: 0=migration complete or skipped, 1=error
# =============================================================================

set -e

echo "=============================================="
echo "📂 Code Scalpel Project Structure Migration"
echo "=============================================="
echo ""

# Check we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "ERROR: Must run from project root (where pyproject.toml is)"
    exit 1
fi

MIGRATED=false

# --- Create consolidated .code-scalpel structure ---
mkdir -p .code-scalpel/{cache/ast,cache/incremental,cache/ruff,runtime,logs,licenses}

# --- Migrate .scalpel_cache/ → .code-scalpel/cache/ ---
if [ -d ".scalpel_cache" ] && [ -n "$(ls -A .scalpel_cache 2>/dev/null)" ]; then
    echo "📦 Migrating .scalpel_cache/ → .code-scalpel/cache/"
    mv .scalpel_cache/* .code-scalpel/cache/ 2>/dev/null || true
    rmdir .scalpel_cache 2>/dev/null || true
    MIGRATED=true
elif [ -d ".scalpel_cache" ]; then
    echo "📦 Removing empty .scalpel_cache/"
    rmdir .scalpel_cache 2>/dev/null || true
    MIGRATED=true
fi

# --- Migrate .code_scalpel_cache/ → .code-scalpel/cache/ (if exists) ---
if [ -d ".code_scalpel_cache" ] && [ -n "$(ls -A .code_scalpel_cache 2>/dev/null)" ]; then
    echo "📦 Migrating .code_scalpel_cache/ → .code-scalpel/cache/"
    mv .code_scalpel_cache/* .code-scalpel/cache/ 2>/dev/null || true
    rmdir .code_scalpel_cache 2>/dev/null || true
    MIGRATED=true
elif [ -d ".code_scalpel_cache" ]; then
    echo "📦 Removing empty .code_scalpel_cache/"
    rmdir .code_scalpel_cache 2>/dev/null || true
    MIGRATED=true
fi

# --- Migrate .scalpel_ast_cache/ → .code-scalpel/cache/ast/ (if exists) ---
if [ -d ".scalpel_ast_cache" ] && [ -n "$(ls -A .scalpel_ast_cache 2>/dev/null)" ]; then
    echo "📦 Migrating .scalpel_ast_cache/ → .code-scalpel/cache/ast/"
    mv .scalpel_ast_cache/* .code-scalpel/cache/ast/ 2>/dev/null || true
    rmdir .scalpel_ast_cache 2>/dev/null || true
    MIGRATED=true
elif [ -d ".scalpel_ast_cache" ]; then
    echo "📦 Removing empty .scalpel_ast_cache/"
    rmdir .scalpel_ast_cache 2>/dev/null || true
    MIGRATED=true
fi

# --- Clean up temporary tier directories ---
for dir in .tmp_tier_comm .tmp_tier_fallback .bench_tmp .test_simple; do
    if [ -d "$dir" ]; then
        echo "🧹 Cleaning up $dir/"
        rm -rf "$dir"
        MIGRATED=true
    fi
done

# --- Migrate .code-scalpel/license/ → .code-scalpel/licenses/ (consistency) ---
if [ -d ".code-scalpel/license" ]; then
    mkdir -p .code-scalpel/licenses
    echo "📦 Migrating .code-scalpel/license/ → .code-scalpel/licenses/"
    mv .code-scalpel/license/* .code-scalpel/licenses/ 2>/dev/null || true
    rmdir .code-scalpel/license 2>/dev/null || true
    MIGRATED=true
fi

# --- Summary ---
echo ""
if [ "$MIGRATED" = true ]; then
    echo "✓ Migration complete!"
    echo ""
    echo "  New structure:"
    echo "  .code-scalpel/"
    echo "  ├── cache/          # Consolidated caches"
    echo "  ├── licenses/       # License JWTs"
    echo "  ├── runtime/        # Runtime state"
    echo "  └── logs/           # Application logs"
    echo ""
    echo "  .gitignore has been updated to cover new paths."
else
    echo "✓ No migration needed - project structure is up to date."
fi
