#!/bin/bash
set -e
#!/bin/bash
set -e
echo "🔍 Running Local Pre-Flight Checks..."

if [ ! -f "pyproject.toml" ]; then
    echo "ERROR: Must run from project root (where pyproject.toml is)"
    exit 1
fi

echo "----------------------------------------------------------------"
echo "1️⃣  Formatting (Black)"
black src/ tests/
echo "✅ Formatting OK"

echo "----------------------------------------------------------------"
echo "2️⃣  Linting (Ruff)"
ruff check --fix src/ tests/
echo "✅ Linting OK"

echo "----------------------------------------------------------------"
echo "3️⃣  Type Checking (Pyright)"
pyright
echo "✅ Type Checking OK"

echo "----------------------------------------------------------------"
echo "4️⃣  Security Scan (Bandit) - Optional"
if command -v bandit >/dev/null 2>&1; then
    bandit -r src/ -ll -ii -x '**/test_*.py' 2>&1 || {
        echo "⚠️  WARNING: Bandit found issues (non-blocking in local validation)"
    }
else
    echo "⚠️  Bandit not installed. Install: pip install bandit"
    echo "    (Will run in CI)"
fi

echo "----------------------------------------------------------------"
echo "5️⃣  Dependency Audit (pip-audit) - Optional"
if command -v pip-audit >/dev/null 2>&1 && [ -f "requirements-secure.txt" ]; then
    pip-audit -r requirements-secure.txt 2>&1 || {
        echo "⚠️  WARNING: Vulnerabilities found (non-blocking in local validation)"
    }
else
    echo "⚠️  pip-audit not available. Install: pip install pip-audit"
    echo "    (Will run in CI)"
fi

echo "----------------------------------------------------------------"
echo "6️⃣  Unit Tests (Pytest)"
# [20260129] Explicitly ignore 'ninja-warrior' obstacle course which contains intentional errors
# [20260202] Match CI paths - only check src/ tests/
pytest --ignore=tests/mcp_tool_verification/mcp_inspector -q
echo "✅ Tests OK"

echo "----------------------------------------------------------------"
echo "🎉 All local checks passed! Ready for commit."
echo ""
echo "Before pushing, run: ./scripts/verify.sh"
echo "This will run comprehensive checks including coverage and docs."
