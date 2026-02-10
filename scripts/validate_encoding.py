#!/usr/bin/env python3
"""
Validate that all write_text() and read_text() calls specify encoding='utf-8'.

[20260210_FEATURE] Pre-release validation to prevent Windows encoding issues.

This script scans the codebase for any write_text() or read_text() calls that
don't explicitly specify encoding='utf-8', which can cause UnicodeEncodeError
on Windows systems that default to cp1252 encoding.

Exit codes:
    0: All calls properly specify encoding
    1: Found calls missing encoding parameter
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class EncodingValidator(ast.NodeVisitor):
    """AST visitor that checks for write_text/read_text calls without encoding."""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.violations: List[Tuple[int, str]] = []

    def visit_Call(self, node: ast.Call):
        """Check if this is a write_text/read_text call without encoding."""
        # Check if this is a method call on a Path-like object
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr

            # Check for write_text or read_text methods
            if method_name in ("write_text", "read_text"):
                # Check if 'encoding' keyword argument is present
                has_encoding = any(
                    kw.arg == "encoding" for kw in node.keywords if kw.arg
                )

                if not has_encoding:
                    # Get the line number and method name
                    self.violations.append((node.lineno, method_name))

        # Continue visiting child nodes
        self.generic_visit(node)


def validate_file(filepath: Path) -> List[Tuple[int, str]]:
    """
    Parse a Python file and check for write_text/read_text without encoding.

    Args:
        filepath: Path to Python file to check

    Returns:
        List of (line_number, method_name) tuples for violations
    """
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))

        validator = EncodingValidator(filepath)
        validator.visit(tree)

        return validator.violations
    except SyntaxError:
        # Skip files with syntax errors (they'll be caught by other checks)
        return []
    except Exception as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)
        return []


def main() -> int:
    """
    Main entry point. Scans all Python files in src/ and config/ directories.

    Returns:
        0 if all checks pass, 1 if violations found
    """
    project_root = Path(__file__).parent.parent

    # Directories to scan
    scan_dirs = [
        project_root / "src",
        project_root / "scripts",
    ]

    # Collect all Python files
    python_files = []
    for scan_dir in scan_dirs:
        if scan_dir.exists():
            python_files.extend(scan_dir.rglob("*.py"))

    if not python_files:
        print("Error: No Python files found to check", file=sys.stderr)
        return 1

    # Track violations
    all_violations = []

    # Check each file
    for filepath in sorted(python_files):
        violations = validate_file(filepath)
        if violations:
            all_violations.append((filepath, violations))

    # Report results
    if all_violations:
        print("❌ ENCODING VALIDATION FAILED\n")
        print(
            "Found write_text() or read_text() calls without explicit encoding='utf-8':"
        )
        print()

        for filepath, violations in all_violations:
            rel_path = filepath.relative_to(project_root)
            print(f"  {rel_path}:")
            for line_num, method_name in violations:
                print(
                    f"    Line {line_num}: {method_name}() missing encoding parameter"
                )
            print()

        print("This can cause UnicodeEncodeError on Windows (cp1252 encoding).")
        print()
        print("Fix: Add encoding='utf-8' parameter to all calls:")
        print("  - path.write_text(content, encoding='utf-8')")
        print("  - path.read_text(encoding='utf-8')")
        print()
        print(f"Total violations: {sum(len(v) for _, v in all_violations)}")

        return 1

    # Success!
    print("✅ ENCODING VALIDATION PASSED")
    print(f"   Checked {len(python_files)} Python files")
    print("   All write_text() and read_text() calls specify encoding='utf-8'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
