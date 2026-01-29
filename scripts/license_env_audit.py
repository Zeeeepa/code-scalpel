#!/usr/bin/env python3
"""
Scan tests/ for occurrences of CODE_SCALPEL_LICENSE_* env usage and report suggestions.

This is a non-destructive audit tool: it prints matches and a recommended replacement
pattern. Run from repo root. Intended for dry-run before making edits.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

patterns = {
    "monkeypatch.setenv": re.compile(
        r"monkeypatch\.setenv\(\s*['\"][^'\"]*CODE_SCALPEL_LICENSE_PATH[^'\"]*['\"]\s*,.*\)"
    ),
    "monkeypatch.delenv": re.compile(r"monkeypatch\.delenv\(\s*['\"]CODE_SCALPEL_LICENSE_PATH['\"].*\)"),
    "os.environ_assign": re.compile(r"os\.environ\[(?:'|\")CODE_SCALPEL_LICENSE_PATH(?:'|\")\]\s*=\s*.*"),
    "os.environ_pop": re.compile(r"os\.environ\.pop\(\s*['\"]CODE_SCALPEL_LICENSE_PATH['\"].*\)"),
    "env_setdefault": re.compile(r"\b(env|environment)\.setdefault\(\s*['\"]CODE_SCALPEL_LICENSE_PATH['\"].*\)"),
    "env_index_assign": re.compile(r"\b(env|environment)\[\s*['\"]CODE_SCALPEL_LICENSE_PATH['\"]\s*\]\s*=\s*.*"),
    "env_pop": re.compile(r"\b(env|environment)\.pop\(\s*['\"]CODE_SCALPEL_LICENSE_PATH['\"].*\)"),
    "other_var": re.compile(r"CODE_SCALPEL_(SECRET_KEY|ALLOW_HS256)"),
}


def scan_file(path: Path):
    text = path.read_text(encoding="utf8")
    lines = text.splitlines()
    matches = []
    for i, line in enumerate(lines, start=1):
        for name, pat in patterns.items():
            if pat.search(line):
                matches.append((i, name, line.strip()))
    return matches


def main():
    if not TESTS.exists():
        print("No tests/ directory found under repo root:", TESTS)
        sys.exit(1)

    files = sorted(TESTS.rglob("*.py"))
    total = 0
    file_matches = {}
    for f in files:
        m = scan_file(f)
        if m:
            file_matches[f.relative_to(ROOT)] = m
            total += len(m)

    print("\nLicense env audit report")
    print("Repository root:", ROOT)
    print("Scanned files under tests/:", len(files))
    print("Total matches found:", total)

    for path, matches in sorted(file_matches.items()):
        print("\nFile:", path)
        for ln, kind, line in matches:
            print(f"  {ln:4d}: {kind:20s}  {line}")

    print("\nSuggested next steps:")
    print('  - For subprocess env dicts (look for env.setdefault or env["CODE_SCALPEL_LICENSE_PATH"] = ...),')
    print("    prefer calling populate_subprocess_license_env(env, license_path=str(...)) before launching subprocess.")
    print(
        "  - For in-process tests using monkeypatch.setenv(...), prefer the use_license fixture or set_hs256_license_env for HS256 tests."
    )
    print("  - Remove direct os.environ modifications in favor of fixtures where possible to avoid cross-test leakage.")
    print("\nTo apply automated replacements, I can produce a codemod that edits files.\n")


if __name__ == "__main__":
    main()
