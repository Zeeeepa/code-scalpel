#!/usr/bin/env python3
"""
[20260218_FEATURE] Validate internal markdown links within a directory.

Checks that relative cross-reference links in .md files resolve to real files.
Ignores external URLs, anchors-only links, and mailto: links.

Usage:
    python scripts/check_links.py --dir website/docs --ext .md
    python scripts/check_links.py --dir docs --exit-on-broken
"""

import argparse
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
URL_PREFIXES = ("http://", "https://", "mailto:", "//", "#", "ftp://")


def is_external(href: str) -> bool:
    return any(href.startswith(p) for p in URL_PREFIXES)


def check_file(path: Path, root: Path) -> list[tuple[int, str, str]]:
    """Returns list of (lineno, display_text, broken_href)."""
    broken = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return broken

    for lineno, line in enumerate(lines, 1):
        for m in LINK_RE.finditer(line):
            href = m.group(2).strip()
            display = m.group(1).strip()

            # Strip anchor from href for file existence check
            href_no_anchor = href.split("#")[0]
            if not href_no_anchor or is_external(href_no_anchor):
                continue

            # Resolve relative to the file's directory
            target = (path.parent / href_no_anchor).resolve()
            if not target.exists():
                broken.append((lineno, display, href))

    return broken


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate internal markdown links")
    parser.add_argument("--dir", default="docs", help="Directory to check")
    parser.add_argument("--ext", default=".md", help="File extension to check")
    parser.add_argument(
        "--exit-on-broken", action="store_true", help="Exit 1 if broken links found"
    )
    args = parser.parse_args()

    root = Path(args.dir)
    if not root.exists():
        print(f"⚠️  Directory not found: {root} — skipping link check")
        return 0

    files = list(root.rglob(f"*{args.ext}"))
    total_broken = 0
    files_with_issues: list[tuple[Path, list]] = []

    for path in sorted(files):
        broken = check_file(path, root)
        if broken:
            files_with_issues.append((path, broken))
            total_broken += len(broken)

    if files_with_issues:
        print(
            f"⚠️  {total_broken} broken internal link(s) in {len(files_with_issues)} file(s):"
        )
        for path, broken_list in files_with_issues:
            try:
                rel = path.relative_to(Path.cwd())
            except ValueError:
                rel = path
            for lineno, display, href in broken_list:
                print(f"   {rel}:{lineno}  [{display}]({href})")
        return 1 if args.exit_on_broken else 0
    else:
        print(f"✅ All internal links resolve ({len(files)} files checked).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
