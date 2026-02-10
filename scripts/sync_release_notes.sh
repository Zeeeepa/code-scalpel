#!/usr/bin/env bash
# sync_release_notes.sh - Verify all CHANGELOG versions have website release pages
#
# Usage:
#   ./scripts/sync_release_notes.sh          # Report status (exit 0 always)
#   ./scripts/sync_release_notes.sh --check  # Exit 1 if any gaps (CI-safe)
#
# Checks:
#   1. Every version in CHANGELOG.md has website/docs/releases/vX.Y.Z.md
#   2. Every release page is listed in website/mkdocs.yml nav
#   3. Website changelog includes the latest version

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

CHECK_MODE=false
[[ "${1:-}" == "--check" ]] && CHECK_MODE=true

CHANGELOG="$PROJECT_ROOT/CHANGELOG.md"
RELEASES_DIR="$PROJECT_ROOT/website/docs/releases"
MKDOCS="$PROJECT_ROOT/website/mkdocs.yml"
WEB_CHANGELOG="$RELEASES_DIR/changelog.md"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

MISSING=0
NAV_MISSING=0
FOUND=0

echo "🔍 Release Notes Sync Check"
echo "==========================="
echo ""

# Extract versions (## [X.Y.Z] lines, skips [Unreleased])
VERSIONS=$(sed -n 's/^## \[\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)\].*/\1/p' "$CHANGELOG")

if [ -z "$VERSIONS" ]; then
    echo -e "${RED}✗ No versions found in CHANGELOG.md${NC}"
    exit 1
fi

# --- 1: release page files ---
echo "📄 Release pages:"
for ver in $VERSIONS; do
    if [ -f "$RELEASES_DIR/v${ver}.md" ]; then
        echo -e "  ${GREEN}✓${NC} v${ver}"
        FOUND=$((FOUND + 1))
    else
        echo -e "  ${RED}✗${NC} v${ver}  ← missing"
        MISSING=$((MISSING + 1))
    fi
done

# --- 2: mkdocs.yml nav ---
echo ""
echo "📋 mkdocs.yml nav:"
for ver in $VERSIONS; do
    if grep -q "v${ver}.md" "$MKDOCS"; then
        echo -e "  ${GREEN}✓${NC} v${ver}"
    else
        echo -e "  ${YELLOW}⚠${NC} v${ver}  ← not in nav"
        NAV_MISSING=$((NAV_MISSING + 1))
    fi
done

# --- 3: website changelog freshness ---
echo ""
echo "📝 Website changelog:"
LATEST_VER=$(echo "$VERSIONS" | head -1)
if [ -f "$WEB_CHANGELOG" ]; then
    if grep -q "$LATEST_VER" "$WEB_CHANGELOG"; then
        echo -e "  ${GREEN}✓${NC} latest version ${LATEST_VER} present"
    else
        echo -e "  ${RED}✗${NC} latest version ${LATEST_VER} missing"
        MISSING=$((MISSING + 1))
    fi
else
    echo -e "  ${RED}✗${NC} file missing"
    MISSING=$((MISSING + 1))
fi

# --- summary ---
echo ""
echo "================================="
TOTAL=$((MISSING + NAV_MISSING))
if [ $TOTAL -eq 0 ]; then
    echo -e "${GREEN}✓ All release notes in sync.${NC} ($FOUND versions)"
else
    echo -e "  Pages:    ${GREEN}${FOUND} synced${NC}  ${RED}${MISSING} missing${NC}"
    echo -e "  Nav gaps: ${YELLOW}${NAV_MISSING}${NC}"
    echo ""
    echo "  See docs/PIPELINE.md → Website Release Notes for instructions."
    [ "$CHECK_MODE" = true ] && exit 1
fi
