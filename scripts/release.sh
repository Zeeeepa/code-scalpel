#!/bin/bash
# Code Scalpel Release Script
# [20260123_FEATURE] Automated release workflow for PyPI and VS Code Marketplace
#
# Usage: ./scripts/release.sh [major|minor|patch] [--dry-run] [--skip-tests] [--skip-pypi] [--skip-vsce]
#
# Prerequisites:
#   - TWINE_API_TOKEN or TWINE_USERNAME/TWINE_PASSWORD for PyPI
#   - VSCE_PAT for VS Code Marketplace (Personal Access Token)
#   - npm installed for VS Code extension
#   - Python virtual environment active

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
BUMP_TYPE="${1:-patch}"
DRY_RUN=false
SKIP_TESTS=false
SKIP_PYPI=false
SKIP_VSCE=false

for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-pypi)
            SKIP_PYPI=true
            shift
            ;;
        --skip-vsce)
            SKIP_VSCE=true
            shift
            ;;
    esac
done

# Validate bump type
if [[ "$BUMP_TYPE" != "major" && "$BUMP_TYPE" != "minor" && "$BUMP_TYPE" != "patch" ]]; then
    echo -e "${RED}Invalid bump type: $BUMP_TYPE${NC}"
    echo "Usage: ./scripts/release.sh [major|minor|patch] [--dry-run] [--skip-tests] [--skip-pypi] [--skip-vsce]"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Code Scalpel Release Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}Project root: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}Bump type: $BUMP_TYPE${NC}"
echo -e "${YELLOW}Dry run: $DRY_RUN${NC}"
echo ""

# ============================================================================
# Step 1: Validate working directory is clean
# ============================================================================
echo -e "${BLUE}[1/8] Checking working directory...${NC}"
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${RED}Working directory not clean. Commit or stash changes first.${NC}"
    git status --short
    exit 1
fi
echo -e "${GREEN}Working directory is clean.${NC}"
echo ""

# ============================================================================
# Step 2: Get current version
# ============================================================================
echo -e "${BLUE}[2/8] Getting current version...${NC}"

# Extract version from pyproject.toml
CURRENT_VERSION=$(grep -Po '(?<=^version = ")[^"]+' pyproject.toml | head -1)
if [[ -z "$CURRENT_VERSION" ]]; then
    echo -e "${RED}Could not extract version from pyproject.toml${NC}"
    exit 1
fi

echo -e "${YELLOW}Current version: $CURRENT_VERSION${NC}"

# Parse version components
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Calculate new version
case $BUMP_TYPE in
    major)
        NEW_VERSION="$((MAJOR + 1)).0.0"
        ;;
    minor)
        NEW_VERSION="$MAJOR.$((MINOR + 1)).0"
        ;;
    patch)
        NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"
        ;;
esac

echo -e "${GREEN}New version: $NEW_VERSION${NC}"
echo ""

# ============================================================================
# Step 3: Run quality checks (unless skipped)
# ============================================================================
if [[ "$SKIP_TESTS" == false ]]; then
    echo -e "${BLUE}[3/8] Running quality checks...${NC}"

    # Activate virtual environment if available
    if [[ -d ".venv" ]]; then
        source .venv/bin/activate
    elif [[ -n "$CONDA_PREFIX" ]]; then
        echo "Using Conda environment: $CONDA_PREFIX"
    fi

    # Run the local pipeline
    if [[ -f "local_pipeline/pipeline.py" ]]; then
        python local_pipeline/pipeline.py --env=conda || {
            echo -e "${RED}Quality checks failed. Fix issues before releasing.${NC}"
            exit 1
        }
    else
        # Fallback to individual checks
        echo "Running black..."
        black --check src/ tests/ || exit 1
        echo "Running ruff..."
        ruff check src/ tests/ || exit 1
        echo "Running tests..."
        pytest tests/core/ tests/licensing/ tests/mcp/ -v --tb=short || exit 1
    fi

    echo -e "${GREEN}All quality checks passed.${NC}"
else
    echo -e "${YELLOW}[3/8] Skipping quality checks (--skip-tests)${NC}"
fi
echo ""

# ============================================================================
# Step 4: Update version in all files
# ============================================================================
echo -e "${BLUE}[4/8] Updating version in files...${NC}"

if [[ "$DRY_RUN" == false ]]; then
    # Update pyproject.toml
    sed -i "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
    echo "  Updated pyproject.toml"

    # Update src/code_scalpel/__init__.py
    sed -i "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" src/code_scalpel/__init__.py
    echo "  Updated src/code_scalpel/__init__.py"

    # Update vscode-extension/package.json
    if [[ -f "vscode-extension/package.json" ]]; then
        sed -i "s/\"version\": \"$CURRENT_VERSION\"/\"version\": \"$NEW_VERSION\"/" vscode-extension/package.json
        echo "  Updated vscode-extension/package.json"
    fi

    echo -e "${GREEN}Version updated to $NEW_VERSION${NC}"
else
    echo -e "${YELLOW}DRY RUN: Would update version to $NEW_VERSION in:${NC}"
    echo "  - pyproject.toml"
    echo "  - src/code_scalpel/__init__.py"
    echo "  - vscode-extension/package.json"
fi
echo ""

# ============================================================================
# Step 5: Commit version bump and create tag
# ============================================================================
echo -e "${BLUE}[5/8] Creating version commit and tag...${NC}"

if [[ "$DRY_RUN" == false ]]; then
    git add pyproject.toml src/code_scalpel/__init__.py
    if [[ -f "vscode-extension/package.json" ]]; then
        git add vscode-extension/package.json
    fi

    git commit -m "chore: bump version to $NEW_VERSION

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

    git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

    echo -e "${GREEN}Created commit and tag v$NEW_VERSION${NC}"
else
    echo -e "${YELLOW}DRY RUN: Would create commit and tag v$NEW_VERSION${NC}"
fi
echo ""

# ============================================================================
# Step 6: Build Python package
# ============================================================================
echo -e "${BLUE}[6/8] Building Python package...${NC}"

# Clean previous builds
rm -rf dist/ build/ *.egg-info

if [[ "$DRY_RUN" == false ]]; then
    python -m build
    twine check dist/*
    echo -e "${GREEN}Package built successfully.${NC}"
else
    echo -e "${YELLOW}DRY RUN: Would run 'python -m build' and 'twine check'${NC}"
fi
echo ""

# ============================================================================
# Step 7: Publish to PyPI
# ============================================================================
if [[ "$SKIP_PYPI" == false ]]; then
    echo -e "${BLUE}[7/8] Publishing to PyPI...${NC}"

    if [[ "$DRY_RUN" == false ]]; then
        # Check for credentials
        if [[ -z "$TWINE_API_TOKEN" && -z "$TWINE_USERNAME" ]]; then
            echo -e "${YELLOW}No PyPI credentials found. Set TWINE_API_TOKEN or TWINE_USERNAME/TWINE_PASSWORD${NC}"
            echo -e "${YELLOW}Skipping PyPI upload. You can manually upload with: twine upload dist/*${NC}"
        else
            twine upload dist/*
            echo -e "${GREEN}Published to PyPI.${NC}"
        fi
    else
        echo -e "${YELLOW}DRY RUN: Would run 'twine upload dist/*'${NC}"
    fi
else
    echo -e "${YELLOW}[7/8] Skipping PyPI publish (--skip-pypi)${NC}"
fi
echo ""

# ============================================================================
# Step 8: Publish VS Code Extension
# ============================================================================
if [[ "$SKIP_VSCE" == false ]]; then
    echo -e "${BLUE}[8/8] Publishing VS Code extension...${NC}"

    if [[ -d "vscode-extension" ]]; then
        cd vscode-extension

        if [[ "$DRY_RUN" == false ]]; then
            # Install dependencies if needed
            if [[ ! -d "node_modules" ]]; then
                npm install
            fi

            # Compile TypeScript
            npm run compile 2>/dev/null || echo "No compile script, continuing..."

            # Check for VSCE credentials
            if [[ -z "$VSCE_PAT" ]]; then
                echo -e "${YELLOW}No VSCE_PAT found. Set VSCE_PAT environment variable.${NC}"
                echo -e "${YELLOW}Skipping VS Code publish. You can manually publish with: vsce publish${NC}"
            else
                # Package and publish
                npx vsce publish -p "$VSCE_PAT"
                echo -e "${GREEN}Published to VS Code Marketplace.${NC}"
            fi
        else
            echo -e "${YELLOW}DRY RUN: Would run 'vsce publish'${NC}"
        fi

        cd "$PROJECT_ROOT"
    else
        echo -e "${YELLOW}vscode-extension directory not found, skipping.${NC}"
    fi
else
    echo -e "${YELLOW}[8/8] Skipping VS Code publish (--skip-vsce)${NC}"
fi
echo ""

# ============================================================================
# Summary
# ============================================================================
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Release Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Version: ${GREEN}$NEW_VERSION${NC}"
echo ""

if [[ "$DRY_RUN" == false ]]; then
    echo "Next steps:"
    echo "  1. Push the commit and tag: git push && git push --tags"
    echo "  2. Create a GitHub release at: https://github.com/3DTechus/code-scalpel/releases/new"
else
    echo -e "${YELLOW}This was a DRY RUN. No changes were made.${NC}"
    echo "Run without --dry-run to perform the actual release."
fi
