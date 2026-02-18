#!/usr/bin/env python3
"""
[20260218_FEATURE] Pre-release content accuracy checker.

Greps website source files for known bad patterns before deploy/release.
Exits non-zero if any violations are found — designed to run as a CI gate.

Usage:
    python scripts/check_release_content.py [--website-dir PATH] [--strict]

Flags:
    --website-dir  Path to website directory (default: ./website)
    --strict       Exit 1 on warnings as well as errors
"""

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class Check(NamedTuple):
    name: str
    pattern: str
    extensions: tuple[str, ...]
    exclude: tuple[str, ...] = ()
    severity: str = "error"  # "error" | "warning"
    message: str = ""
    is_regex: bool = False


# ── Canonical checks ──────────────────────────────────────────────────────────
CHECKS: list[Check] = [
    # MCP invocation args — only inside Claude config JSON blocks
    # Pattern: "args": ["codescalpel"] (without the "mcp" second arg)
    # Excludes Dockerfile ENTRYPOINT lines and binary paths
    Check(
        name="missing-mcp-arg",
        pattern=r'"args"\s*:\s*\[\s*"codescalpel"\s*\]',
        extensions=(".html", ".md", ".json"),
        exclude=(".deprecated", "ENTRYPOINT", "Dockerfile"),
        severity="error",
        message='MCP config missing "mcp" second arg. Should be ["codescalpel", "mcp"].',
        is_regex=True,
    ),
    # Dead /contact page links
    Check(
        name="dead-contact-link",
        pattern="codescalpel.dev/contact",
        extensions=(".html", ".md"),
        exclude=(".deprecated",),
        severity="error",
        message="Dead /contact link — /contact page does not exist. Use mailto:sales@codescalpel.dev.",
    ),
    # Hardcoded dollar pricing — exclude internal dev/planning docs
    Check(
        name="hardcoded-pricing",
        pattern=r"\$[0-9]+(?:/mo|/month|/year)",
        extensions=(".html", ".md"),
        exclude=(".deprecated", "assets/docs/", "personas/", "pricing/", "archive/"),
        severity="error",
        message="Hardcoded pricing found. Site is in beta — use beta messaging or config.js.",
        is_regex=True,
    ),
    # Stale 22+ tool count (actual count is 22)
    Check(
        name="stale-tool-count",
        pattern="22+",
        extensions=(".html", ".md"),
        exclude=(".deprecated",),
        severity="error",
        message="22+ tool count is stale — the count is exactly 22.",
    ),
    # Raw markdown bold in HTML files
    Check(
        name="raw-markdown-in-html",
        pattern=r"\*\*[^<>]+\*\*",
        extensions=(".html",),
        exclude=(".deprecated", "assets/"),
        severity="warning",
        message="Raw markdown **bold** found inside .html file — should be <strong>.</strong>",
        is_regex=True,
    ),
    # Dead /pricing page links
    Check(
        name="dead-pricing-link",
        pattern="codescalpel.dev/pricing",
        extensions=(".html", ".md"),
        exclude=(".deprecated",),
        severity="warning",
        message="/pricing may redirect — verify the 301 .htaccess is deployed.",
    ),
    # Stale version references (read dynamically from pyproject.toml)
    # Added dynamically below based on current version
]


def load_version(project_root: Path) -> str:
    """Extract version from pyproject.toml."""
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return ""
    text = pyproject.read_text()
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    return m.group(1) if m else ""


def build_stale_version_check(current_version: str) -> list[Check]:
    """Return checks for version strings OLDER than current (not the current one)."""
    if not current_version:
        return []
    major, minor, patch = current_version.split(".")
    patch_int = int(patch)
    # Build alternation pattern matching any older patch in same major.minor
    # e.g. if current is 1.3.5, flag v1.3.0 through v1.3.4
    if patch_int == 0:
        return []  # nothing older in this minor series to flag
    old_patches = "|".join(
        re.escape(f"{major}.{minor}.{p}") for p in range(0, patch_int)
    )
    pattern = r"v(?:" + old_patches + r")\b"
    return [
        Check(
            name="stale-version",
            pattern=pattern,
            extensions=(".html", ".md"),
            exclude=(
                ".deprecated", "release_artifacts", "validation.html",
                "changelog", "CHANGELOG", "release_notes", "archive/",
                "CONSOLIDATION_SUMMARY", "DEPLOYMENT_READY",
            ),
            severity="warning",
            message=f"Stale version reference — current is v{current_version}. Update or remove.",
            is_regex=True,
        )
    ]


class Violation(NamedTuple):
    check: str
    severity: str
    file: str
    line: int
    content: str
    message: str


def scan_file(path: Path, check: Check) -> list[Violation]:
    violations = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return violations

    lines = text.splitlines()
    for lineno, line in enumerate(lines, 1):
        if check.is_regex:
            if re.search(check.pattern, line):
                violations.append(
                    Violation(check.name, check.severity, str(path), lineno, line.strip(), check.message)
                )
        else:
            if check.pattern in line:
                violations.append(
                    Violation(check.name, check.severity, str(path), lineno, line.strip(), check.message)
                )
    return violations


def should_exclude(path: Path, exclude: tuple[str, ...]) -> bool:
    path_str = str(path)
    return any(excl in path_str for excl in exclude)


SKIP_DIRS = frozenset({
    "site", "dist", "node_modules", ".venv", "venv", ".git",
    "__pycache__", ".cache", ".tox", "build", ".internal_docs",
    "docs_backup_20260207_094705",
})


def iter_source_files(website_dir: Path, ext: str):
    """Walk website_dir skipping generated/dependency directories."""
    import os
    for dirpath_str, dirnames, filenames in os.walk(website_dir):
        # Prune skip dirs in-place so os.walk doesn't descend into them
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        dirpath = Path(dirpath_str)
        for fname in filenames:
            if fname.endswith(ext):
                yield dirpath / fname


def run_checks(website_dir: Path, checks: list[Check]) -> list[Violation]:
    all_violations: list[Violation] = []

    for check in checks:
        for ext in check.extensions:
            for path in iter_source_files(website_dir, ext):
                if should_exclude(path, check.exclude):
                    continue
                all_violations.extend(scan_file(path, check))

    return all_violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-release content accuracy checker")
    parser.add_argument("--website-dir", default="website", help="Path to website directory")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--summary-only", action="store_true", help="Print summary only, no per-line output")
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    website_dir = Path(args.website_dir)
    if not website_dir.is_absolute():
        website_dir = project_root / website_dir

    if not website_dir.exists():
        print(f"❌ Website directory not found: {website_dir}", file=sys.stderr)
        return 1

    # Build full check list including dynamic version check
    current_version = load_version(project_root)
    all_checks = CHECKS + build_stale_version_check(current_version)

    print(f"🔍 Checking website content in: {website_dir}")
    if current_version:
        print(f"   Current version: v{current_version}")
    print(f"   Running {len(all_checks)} content checks...\n")

    violations = run_checks(website_dir, all_checks)

    errors = [v for v in violations if v.severity == "error"]
    warnings = [v for v in violations if v.severity == "warning"]

    # Group by check name for reporting
    by_check: dict[str, list[Violation]] = {}
    for v in violations:
        by_check.setdefault(v.check, []).append(v)

    for check_name, viols in sorted(by_check.items()):
        sev = viols[0].severity
        icon = "❌" if sev == "error" else "⚠️ "
        print(f"{icon} [{sev.upper()}] {check_name} — {len(viols)} occurrence(s)")
        print(f"   {viols[0].message}")
        if not args.summary_only:
            for v in viols[:5]:  # Show first 5 per check to avoid noise
                rel_path = Path(v.file).relative_to(project_root) if project_root in Path(v.file).parents else v.file
                print(f"   {rel_path}:{v.line}  {v.content[:100]}")
            if len(viols) > 5:
                print(f"   ... and {len(viols) - 5} more")
        print()

    # Summary
    print("─" * 60)
    if not violations:
        print("✅ All content checks passed — site is clean for release.\n")
        return 0

    print(f"{'❌' if errors else '⚠️ '} Found {len(errors)} error(s), {len(warnings)} warning(s) across {len(violations)} total occurrence(s).")

    if errors:
        print("\nErrors BLOCK release. Fix them before deploying.")
    if warnings and not args.strict:
        print("Warnings are advisory. Use --strict to treat them as errors.")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
