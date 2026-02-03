#!/usr/bin/env bash
# =============================================================================
# verify.sh - Comprehensive Pre-Push Validation (Tier 2)
# =============================================================================
# Purpose: Run all checks that will be executed in GitHub Actions CI
# Runtime: ~5-10 minutes
# Prerequisites: Python 3.10+, pip install -e '.[dev]'
# Exit codes: 0=all checks passed, 1=one or more checks failed
#
# Usage:
#   ./scripts/verify.sh              # Run all checks
#   ./scripts/verify.sh --skip-build # Skip expensive build check
#
# This script must pass before pushing to GitHub or publishing to PyPI.
# =============================================================================
# [20251214_REFACTOR] Normalize line endings for bash portability on Windows.
# [20260202_ENHANCEMENT] Added header docs and --skip-build flag

set -e  # Exit on any error

# Parse command-line options
SKIP_BUILD=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-build]"
            exit 1
            ;;
    esac
done

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

echo "🔗 Pre-check: Version Sync..."
echo "----------------------------------------------"
PYPROJECT_VERSION=$(grep -Po 'version = "\K[^"]+' pyproject.toml 2>/dev/null)
INIT_VERSION=$(grep -Po '__version__ = "\K[^"]+' src/code_scalpel/__init__.py 2>/dev/null)
if [ "$PYPROJECT_VERSION" != "$INIT_VERSION" ]; then
    echo "❌ ERROR: Version mismatch!"
    echo "  pyproject.toml: $PYPROJECT_VERSION"
    echo "  __init__.py:    $INIT_VERSION"
    echo "Run: ./scripts/verify_version_sync.sh for details"
    exit 1
fi
echo "✓ Version sync verified: $PYPROJECT_VERSION"
echo ""

echo "Step 1/11: Running Formatter (Black)..."
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

echo "🧹 Step 2/11: Running Linter (Ruff)..."
echo "----------------------------------------------"
$PYTHON_BIN -m ruff check src tests examples 2>&1 || {
    echo ""
    echo "WARNING: Linting issues found. Run 'ruff check src tests examples --fix' to auto-fix."
    echo "    Or run './scripts/verify.sh --fix' to auto-fix."
    exit 1
}
echo "Linting check passed"
echo ""

echo "🔎 Step 3/11: Type Check (Pyright)..."
echo "----------------------------------------------"
pyright --version >/dev/null 2>&1 || {
    echo ""
    echo "ERROR: pyright is not installed. Install dev deps: pip install -e '.[dev]' && pip install pyright"
    exit 1
}
pyright -p pyrightconfig.json 2>&1 || {
    echo ""
    echo "ERROR: Pyright type check failed"
    exit 1
}
echo "Type checking passed"
echo ""

echo "🛡️  Step 4/11: Security Scan (Bandit)..."
echo "----------------------------------------------"
bandit --version >/dev/null 2>&1 || {
    echo ""
    echo "ERROR: bandit is not installed. Install dev deps: pip install -e '.[dev]' && pip install bandit"
    exit 1
}
bandit -r src/ -ll -ii -x '**/test_*.py' 2>&1 || {
    echo ""
    echo "ERROR: Bandit reported issues"
    exit 1
}
echo "Bandit scan passed"
echo ""

echo "🧾 Step 5/11: Dependency Audit (pip-audit)..."
echo "----------------------------------------------"
pip-audit --version >/dev/null 2>&1 || {
    echo ""
    echo "ERROR: pip-audit is not installed. Install dev deps: pip install -e '.[dev]' && pip install pip-audit"
    exit 1
}
pip-audit -r requirements-secure.txt 2>&1 || {
    echo ""
    echo "ERROR: pip-audit found vulnerabilities"
    exit 1
}
echo "Dependency audit passed"
echo ""

echo "🧪 Step 6/11: Running Tests with Coverage..."
echo "----------------------------------------------"
$PYTHON_BIN -m pytest --cov=code_scalpel --cov-report=term-missing --cov-fail-under=24 tests/ 2>&1 || {
    echo ""
    echo "ERROR: Tests failed or coverage below 24%"
    exit 1
}
echo "Tests passed with required coverage"
echo ""

echo "🧩 Step 7/11: MCP Contract (All Tools)..."
echo "----------------------------------------------"
for transport in stdio streamable-http sse; do
    echo "Running MCP contract for transport: $transport"
    MCP_CONTRACT_TRANSPORT="$transport" $PYTHON_BIN -m pytest -q tests/mcp/test_mcp_all_tools_contract.py 2>&1 || {
        echo ""
        echo "ERROR: MCP contract test failed for transport: $transport"
        exit 1
    }
done
echo "MCP contract passed"
echo ""

echo "📦 Step 8/11: Verifying Package Build..."
echo "----------------------------------------------"
if [ "$SKIP_BUILD" = false ]; then
    $PYTHON_BIN -m build --sdist --wheel --outdir /tmp/code-scalpel-test-build 2>&1 || {
        echo ""
        echo "ERROR: Package build failed"
        exit 1
    }
    rm -rf /tmp/code-scalpel-test-build
    echo "Package builds successfully"
else
    echo "⚠️  Build check skipped (--skip-build flag)"
fi
echo ""

echo "📚 Step 9/11: MCP Tools Reference Documentation..."
echo "----------------------------------------------"
if [ -f "scripts/generate_mcp_tools_reference.py" ] && [ -n "$TEST_ENTERPRISE_LICENSE_JWT" ]; then
    TEMP_DIR=$(mktemp -d)
    export CODE_SCALPEL_DOC_PROJECT_ROOT="$TEMP_DIR"
    $PYTHON_BIN scripts/generate_mcp_tools_reference.py >/dev/null 2>&1

    if [ -n "$(git diff --name-only docs/reference/mcp_tools_current.md 2>/dev/null)" ]; then
        echo "ERROR: docs/reference/mcp_tools_current.md out of date"
        echo "Run: python scripts/generate_mcp_tools_reference.py"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    rm -rf "$TEMP_DIR"
    echo "MCP tools reference validated"
elif [ -n "$TEST_ENTERPRISE_LICENSE_JWT" ]; then
    echo "⚠️  Script not found, skipping MCP tools reference validation"
else
    echo "⚠️  Skipping MCP tools reference validation (no TEST_ENTERPRISE_LICENSE_JWT)"
    echo "    This will be validated in CI with injected secrets"
fi
echo ""

echo "📚 Step 10/11: MCP Tools Tier Matrix..."
echo "----------------------------------------------"
if [ -f "scripts/generate_mcp_tier_matrix.py" ] && [ -n "$TEST_PRO_LICENSE_JWT" ]; then
    TEMP_DIR=$(mktemp -d)
    export CODE_SCALPEL_DOC_PROJECT_ROOT="$TEMP_DIR"
    $PYTHON_BIN scripts/generate_mcp_tier_matrix.py >/dev/null 2>&1

    if [ -n "$(git diff --name-only docs/reference/mcp_tools_by_tier.md 2>/dev/null)" ]; then
        echo "ERROR: docs/reference/mcp_tools_by_tier.md out of date"
        echo "Run: python scripts/generate_mcp_tier_matrix.py"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
    rm -rf "$TEMP_DIR"
    echo "MCP tier matrix validated"
elif [ -n "$TEST_PRO_LICENSE_JWT" ]; then
    echo "⚠️  Script not found, skipping MCP tier matrix validation"
else
    echo "⚠️  Skipping MCP tier matrix validation (no TEST_PRO_LICENSE_JWT)"
    echo "    This will be validated in CI with injected secrets"
fi
echo ""

echo "📚 Step 11/11: Documentation Sync Validation..."
echo "----------------------------------------------"
if [ -f "scripts/validate_docs_sync.py" ]; then
    $PYTHON_BIN scripts/validate_docs_sync.py 2>&1 || {
        echo ""
        echo "ERROR: Documentation out of sync with code"
        exit 1
    }
    echo "Documentation sync validated"
else
    echo "⚠️  Script not found, skipping docs sync validation"
fi
echo ""

echo "=============================================="
echo "ALL VERIFICATION PASSED (11/11 checks)"
echo "=============================================="
echo ""
echo "You are ready to commit and publish."
echo ""
