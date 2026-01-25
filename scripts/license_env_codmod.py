#!/usr/bin/env python3
"""
A conservative dry-run codemod to suggest replacements for subprocess env population
patterns in tests that set CODE_SCALPEL_LICENSE_PATH / CODE_SCALPEL_SECRET_KEY / CODE_SCALPEL_ALLOW_HS256.

This script does NOT modify files by default. It prints a proposed replacement for each file
containing a contiguous block of env modifications and a suggested single-line replacement:

    populate_subprocess_license_env(env, license_path=str(...), secret=...)

Run from repo root. Use --apply to actually update files (not recommended without review).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

ENV_LINE_RE = re.compile(
    r"^(?P<indent>\s*)(?P<var>\w+)\.(?:setdefault|pop|__setitem__|update|__setattr__)?\(?\s*['\"]CODE_SCALPEL_LICENSE_PATH['\"]"
)
ENV_ASSIGN_RE = re.compile(
    r"^(?P<indent>\s*)(?P<var>\w+)\s*\[\s*['\"]CODE_SCALPEL_LICENSE_PATH['\"]\s*\]\s*=\s*(?P<value>.+)$"
)
SET_ALLOW_RE = re.compile(r"CODE_SCALPEL_ALLOW_HS256")
SET_SECRET_RE = re.compile(r"CODE_SCALPEL_SECRET_KEY")


def find_env_blocks(lines: List[str]) -> List[Tuple[int, int]]:
    """Return list of (start, end) line indices (0-based, end exclusive) for contiguous env ops."""
    blocks: List[Tuple[int, int]] = []
    i = 0
    n = len(lines)
    while i < n:
        m = re.search(r"\b(env|environment)\b.*CODE_SCALPEL_LICENSE_PATH", lines[i])
        if m:
            # start a block, include surrounding setdefault/secret/allow/pop lines nearby
            start = i
            j = i + 1
            while j < n and re.search(
                r"CODE_SCALPEL_(LICENSE_PATH|SECRET_KEY|ALLOW_HS256)|\b(env|environment)\b.*CODE_SCALPEL_LICENSE_PATH",
                lines[j],
            ):
                j += 1
            blocks.append((start, j))
            i = j
        else:
            i += 1
    return blocks


def analyze_file(path: Path) -> Optional[Tuple[List[str], List[Tuple[int, int]]]]:
    text = path.read_text(encoding="utf8")
    lines = text.splitlines()
    blocks = find_env_blocks(lines)
    if not blocks:
        return None
    return lines, blocks


def render_replacement(lines: List[str], start: int, end: int) -> Tuple[str, int, int]:
    """Create a suggested replacement string for the block lines[start:end].

    Returns (replacement_text, start, end)
    """
    block = lines[start:end]
    # try to find license_path variable and secret variable names
    license_var = None
    secret_var = None
    for ln in block:
        m_assign = re.search(r"CODE_SCALPEL_LICENSE_PATH", ln)
        if m_assign:
            # try to capture the RHS if present
            m_rhs = re.search(r"\bstr\(([^)]+)\)|\b([^,\s)]+)\b", ln)
            # crude: look for 'license_path' token
            if "license_path" in ln:
                license_var = "license_path"
            elif "expired_path" in ln:
                license_var = "expired_path"
            elif "explicit_path" in ln:
                license_var = "explicit_path"
    for ln in block:
        if "CODE_SCALPEL_SECRET_KEY" in ln:
            # try to capture token used as secret value
            m = re.search(r"CODE_SCALPEL_SECRET_KEY['\"]?\s*,?\s*(?P<val>[^)]+)\)?", ln)
            if m:
                v = m.group("val").strip()
                # extract variable name if present
                var_m = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", v)
                if var_m:
                    secret_var = var_m.group(1)
    # default to 'env' indent
    indent = ""
    if block:
        m_indent = re.match(r"^(\s*)", block[0])
        indent = m_indent.group(1) if m_indent else ""

    args = ["env"]
    kw = []
    if license_var:
        kw.append(f"license_path=str({license_var})")
    else:
        # try to capture literal path
        kw.append("license_path=license_path")
    if secret_var:
        kw.append(f"secret={secret_var}")

    rep = indent + f"populate_subprocess_license_env(env, {', '.join(kw)})"
    return rep, start, end


def main(argv: Optional[List[str]] = None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "--apply", action="store_true", help="Actually modify files (dangerous)"
    )
    args = p.parse_args(argv)

    files = sorted(TESTS.rglob("*.py"))
    changes = {}
    for f in files:
        res = analyze_file(f)
        if not res:
            continue
        lines, blocks = res
        rep_list = []
        for s, e in blocks:
            rep_text, s, e = render_replacement(lines, s, e)
            rep_list.append((s, e, rep_text))
        changes[f.relative_to(ROOT)] = rep_list

    if not changes:
        print("No candidate blocks found for replacement.")
        return

    total_blocks = sum(len(v) for v in changes.values())
    print(
        f"Found {total_blocks} candidate blocks across {len(changes)} files. Dry-run suggestions:"
    )
    for path, reps in sorted(changes.items()):
        print("\nFile:", path)
        for s, e, rep in reps:
            print(f"  Replace lines {s + 1}-{e} with:")
            print("    ", rep)

    if args.apply:
        print(
            "\n--apply requested but modifying files via codemod is discouraged without manual review."
        )


if __name__ == "__main__":
    main()
