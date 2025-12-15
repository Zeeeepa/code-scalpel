#!/bin/bash
# =============================================================================
# Code Scalpel - Pre-commit Verification Script
# =============================================================================
# This script must pass before any commit or PyPI publication.
# Run with: ./scripts/verify.sh
# =============================================================================
# [20251214_REFACTOR] Normalize line endings for bash portability on Windows.

set -e  # Exit on any error

echo "=============================================="
echo "🔬 Code Scalpel Verification Suite"
echo "=============================================="
echo ""

# Check we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "ERROR: Must run from project root (where pyproject.toml is)"
    exit 1
fi

# [20251214_REFACTOR] Resolve Python executable for cross-shell portability.
PYTHON_BIN=$(command -v python.exe || command -v py.exe || command -v py || command -v python || command -v python3 || true)
if [ -z "$PYTHON_BIN" ]; then
    echo "ERROR: Python executable not found in PATH"
    exit 1
fi

echo "Step 1/4: Running Formatter (Black)..."
echo "----------------------------------------------"
# [20251214_REFACTOR] Use python -m to avoid PATH issues in bash on Windows.
$PYTHON_BIN -m black src tests examples --check --diff 2>&1 || {
    echo ""
    echo "WARNING: Formatting issues found. Run 'black src tests examples' to fix."
    echo "    Or run './scripts/verify.sh --fix' to auto-fix."
    exit 1
}
echo "Formatting check passed"
echo ""

echo "🧹 Step 2/4: Running Linter (Ruff)..."
echo "----------------------------------------------"
$PYTHON_BIN -m ruff check src tests examples 2>&1 || {
    echo ""
    echo "WARNING: Linting issues found. Run 'ruff check src tests examples --fix' to auto-fix."
    echo "    Or run './scripts/verify.sh --fix' to auto-fix."
    exit 1
}
echo "Linting check passed"
echo ""

echo "🧪 Step 3/4: Running Tests with Coverage..."
echo "----------------------------------------------"
$PYTHON_BIN -m pytest --cov=code_scalpel --cov-report=term-missing --cov-fail-under=24 tests/ 2>&1 || {
    echo ""
    echo "ERROR: Tests failed or coverage below 24%"
    exit 1
}
echo "Tests passed with required coverage"
echo ""

echo "📦 Step 4/4: Verifying Package Build..."
echo "----------------------------------------------"
$PYTHON_BIN -m build --sdist --wheel --outdir /tmp/code-scalpel-test-build 2>&1 || {
    echo ""
    echo "ERROR: Package build failed"
    exit 1
}
rm -rf /tmp/code-scalpel-test-build
echo "Package builds successfully"
echo ""

echo "=============================================="
echo "ALL VERIFICATION PASSED"
echo "=============================================="
echo ""
echo "You are ready to commit and publish."
echo ""
