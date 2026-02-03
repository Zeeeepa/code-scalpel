#!/usr/bin/env bash
# =============================================================================
# verify_version_sync.sh - Version Consistency Checker
# =============================================================================
# Purpose: Verify that version is consistent across package files
# Usage: ./scripts/verify_version_sync.sh
# Exit codes: 0=versions match, 1=version mismatch detected
# =============================================================================

set -e

# Check we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "ERROR: Must run from project root (where pyproject.toml is)"
    exit 1
fi

# Extract versions using grep with Perl regex
PYPROJECT_VERSION=$(grep -Po 'version = "\K[^"]+' pyproject.toml 2>/dev/null)
INIT_VERSION=$(grep -Po '__version__ = "\K[^"]+' src/code_scalpel/__init__.py 2>/dev/null)

# Check if extraction succeeded
if [ -z "$PYPROJECT_VERSION" ]; then
    echo "ERROR: Could not extract version from pyproject.toml"
    exit 1
fi

if [ -z "$INIT_VERSION" ]; then
    echo "ERROR: Could not extract version from src/code_scalpel/__init__.py"
    exit 1
fi

# Compare versions
if [ "$PYPROJECT_VERSION" != "$INIT_VERSION" ]; then
    echo "❌ ERROR: Version mismatch detected!"
    echo "  pyproject.toml: $PYPROJECT_VERSION"
    echo "  __init__.py:    $INIT_VERSION"
    echo ""
    echo "Fix by updating both files to match."
    echo "Example:"
    echo "  sed -i 's/version = \".*\"/version = \"$INIT_VERSION\"/' pyproject.toml"
    echo "  sed -i 's/__version__ = \".*\"/__version__ = \"$INIT_VERSION\"/' src/code_scalpel/__init__.py"
    exit 1
fi

echo "✓ Version sync verified: $PYPROJECT_VERSION"
exit 0
