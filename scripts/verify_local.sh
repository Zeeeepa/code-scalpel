#!/bin/bash
set -e
echo "🔍 Running Local Pre-Flight Checks..."

echo "----------------------------------------------------------------"
echo "1️⃣  Formatting (Black)"
black .
echo "✅ Formatting OK"

echo "----------------------------------------------------------------"
echo "2️⃣  Linting (Ruff)"
ruff check .
echo "✅ Linting OK"

echo "----------------------------------------------------------------"
echo "3️⃣  Type Checking (Pyright)"
pyright
echo "✅ Type Checking OK"

echo "----------------------------------------------------------------"
echo "4️⃣  Unit Tests (Pytest)"
# Run fast tests first or all tests? Let's run all but exclude integration if needed.
# For pre-push, running all is safer.
pytest
echo "✅ Tests OK"

echo "----------------------------------------------------------------"
echo "🎉 All local checks passed! You are ready to push."
