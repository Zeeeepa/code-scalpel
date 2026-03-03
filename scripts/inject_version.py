#!/usr/bin/env python3
"""
[20260218_FEATURE] Version injector — reads version from pyproject.toml and
stamps it into all website HTML/JS/MD files that contain the placeholder
{{ SCALPEL_VERSION }}.

Also validates that no stale hardcoded version strings exist post-injection.

Usage:
    python scripts/inject_version.py [--dry-run] [--website-dir PATH]
"""

import argparse
import re
import sys
from pathlib import Path

PLACEHOLDER = "{{ SCALPEL_VERSION }}"
# Pattern for hardcoded version in HTML/JS — catches v1.x.y that aren't
# from changelog/release notes/release_artifacts paths
VERSION_RE = re.compile(r"\bv\d+\.\d+\.\d+\b")
SKIP_PATHS = (
    "release_artifacts",
    "changelog",
    "CHANGELOG",
    "release_notes",
    "validation.html",
    ".deprecated",
)


def load_version(project_root: Path) -> str:
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        raise FileNotFoundError(f"pyproject.toml not found at {pyproject}")
    text = pyproject.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        raise ValueError("Could not find version in pyproject.toml")
    return m.group(1)


def should_skip(path: Path) -> bool:
    return any(s in str(path) for s in SKIP_PATHS)


def inject_into_file(path: Path, version: str, dry_run: bool) -> bool:
    """Replace {{ SCALPEL_VERSION }} placeholder. Returns True if file was changed."""
    try:
        original = path.read_text(encoding="utf-8")
    except OSError:
        return False

    if PLACEHOLDER not in original:
        return False

    updated = original.replace(PLACEHOLDER, version)
    if not dry_run:
        path.write_text(updated, encoding="utf-8")

    count = original.count(PLACEHOLDER)
    print(
        f"  {'[dry-run] ' if dry_run else ''}✓ {path.relative_to(path.parents[4] if len(path.parents) > 4 else path.parent)} — replaced {count} placeholder(s)"
    )
    return True


def find_stale_versions(
    website_dir: Path, current_version: str
) -> list[tuple[Path, int, str]]:
    """Find hardcoded version strings that don't match current version."""
    stale = []
    for ext in (".html", ".js", ".md"):
        for path in website_dir.rglob(f"*{ext}"):
            if "site/" in str(path) or should_skip(path):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                for m in VERSION_RE.finditer(line):
                    found = m.group(0)[1:]  # strip leading 'v'
                    if found != current_version:
                        stale.append((path, lineno, line.strip()))
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inject version from pyproject.toml into website files"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would change without writing"
    )
    parser.add_argument(
        "--website-dir", default="website", help="Path to website directory"
    )
    parser.add_argument(
        "--check-stale",
        action="store_true",
        help="After injection, report any remaining hardcoded versions",
    )
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    website_dir = Path(args.website_dir)
    if not website_dir.is_absolute():
        website_dir = project_root / website_dir

    try:
        version = load_version(project_root)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1

    print(f"🔖 Injecting version v{version} into {website_dir}")
    if args.dry_run:
        print("   (dry-run mode — no files will be written)\n")

    changed = 0
    for ext in (".html", ".js", ".md"):
        for path in website_dir.rglob(f"*{ext}"):
            if "site/" in str(path) or should_skip(path):
                continue
            if inject_into_file(path, version, args.dry_run):
                changed += 1

    if changed == 0:
        print(f"\n  No {PLACEHOLDER!r} placeholders found — nothing to inject.")
        print(
            "  To use: add {{ SCALPEL_VERSION }} to HTML/MD files where the version should appear."
        )
    else:
        print(f"\n✅ Injected v{version} into {changed} file(s).")

    if args.check_stale:
        print("\n🔍 Checking for remaining stale hardcoded versions...")
        stale = find_stale_versions(website_dir, version)
        if stale:
            print(f"⚠️  Found {len(stale)} line(s) with non-current version strings:")
            for path, lineno, line in stale[:10]:
                try:
                    rel = path.relative_to(project_root)
                except ValueError:
                    rel = path
                print(f"   {rel}:{lineno}  {line[:100]}")
            if len(stale) > 10:
                print(f"   ... and {len(stale) - 10} more")
        else:
            print("  ✅ No stale version strings found.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
