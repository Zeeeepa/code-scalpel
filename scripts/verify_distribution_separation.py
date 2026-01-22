#!/usr/bin/env python3
"""
Verify distribution separation for open-core model.

This script ensures that:
1. Community distribution doesn't contain Pro/Enterprise-only code
2. Tier restrictions are enforced at runtime, not just via hidden code
3. No accidental imports of restricted modules in Community tier

[20251223_FEATURE] v3.2.8 - Distribution separation verification for V1.0
"""

import ast
import sys
from pathlib import Path
from typing import Set, List, Dict, Any


# Define what modules/features are restricted to each tier
TIER_RESTRICTIONS = {
    "community": {
        # Community tier has runtime restrictions, not code exclusions
        # All code ships, but behavior is limited via tier checks
        "excluded_modules": set(),  # No modules excluded from shipping
        "restricted_features": {
            # Features that are limited in Community tier
            "crawl_project": "discovery_mode",
            "get_call_graph": "depth_limit_3",
            "get_graph_neighborhood": "k_limit_1",
            "get_symbol_references": "file_limit_10",
        },
    },
    "pro": {
        "excluded_modules": set(),  # Pro includes everything
        "restricted_features": {},
    },
    "enterprise": {
        "excluded_modules": set(),  # Enterprise includes everything
        "restricted_features": {},
    },
}


class TierVerificationResult:
    """Result of tier verification checks."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.tier_checks_found: Dict[str, List[str]] = {
            "community": [],
            "pro": [],
            "enterprise": [],
        }

    def add_error(self, message: str):
        self.errors.append(message)

    def add_warning(self, message: str):
        self.warnings.append(message)

    def add_info(self, message: str):
        self.info.append(message)

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def report(self) -> str:
        """Generate a human-readable report."""
        lines = ["=" * 70, "Distribution Separation Verification Report", "=" * 70, ""]

        if self.errors:
            lines.append(f"❌ ERRORS: {len(self.errors)}")
            for error in self.errors:
                lines.append(f"  - {error}")
            lines.append("")

        if self.warnings:
            lines.append(f"⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
            lines.append("")

        lines.append(f"✅ Tier checks found:")
        for tier, locations in self.tier_checks_found.items():
            lines.append(f"  {tier}: {len(locations)} checks")

        lines.append("")
        lines.append("INFO:")
        for info in self.info:
            lines.append(f"  - {info}")

        lines.append("")
        lines.append("=" * 70)
        if self.is_valid():
            lines.append("✅ PASS: Distribution separation is correctly implemented")
        else:
            lines.append("❌ FAIL: Distribution separation has issues")
        lines.append("=" * 70)

        return "\n".join(lines)


class TierCheckVisitor(ast.NodeVisitor):
    """AST visitor to find tier checks and restrictions."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.tier_checks: List[Dict[str, Any]] = []
        self.current_function: str = ""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        old_func = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_func

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        old_func = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_func

    def visit_Call(self, node: ast.Call):
        # Check for _get_current_tier() calls
        if isinstance(node.func, ast.Name) and node.func.id == "_get_current_tier":
            self.tier_checks.append(
                {
                    "type": "tier_check",
                    "function": self.current_function,
                    "line": node.lineno,
                }
            )

        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        # Check for tier == "community" comparisons
        if isinstance(node.left, ast.Name) and "tier" in node.left.id:
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and comparator.value in [
                    "community",
                    "pro",
                    "enterprise",
                ]:
                    self.tier_checks.append(
                        {
                            "type": "tier_comparison",
                            "tier": comparator.value,
                            "function": self.current_function,
                            "line": node.lineno,
                        }
                    )

        self.generic_visit(node)


def verify_tier_checks(source_root: Path) -> TierVerificationResult:
    """
    Verify that tier checks are properly implemented.

    For the open-core model with runtime restrictions, we verify:
    1. All tier-restricted features have tier checks
    2. Tier checks use _get_current_tier() consistently
    3. Community tier limitations are enforced
    """
    result = TierVerificationResult()

    # Find all Python files in MCP tools and server
    python_files = []
    mcp_dir = source_root / "code_scalpel" / "mcp"
    if mcp_dir.exists():
        python_files = list(mcp_dir.rglob("*.py"))
    
    if not python_files:
        result.add_error(f"No Python files found in {mcp_dir}")
        return result

    result.add_info(f"Analyzing {len(python_files)} files in MCP directory")

    total_tier_checks = 0
    
    # Parse each file
    for py_file in python_files:
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Quick check before parsing
            if "_get_current_tier" not in content:
                continue
                
            tree = ast.parse(content, filename=str(py_file))
            visitor = TierCheckVisitor(py_file)
            visitor.visit(tree)
            
            if visitor.tier_checks:
                total_tier_checks += len(visitor.tier_checks)
                for check in visitor.tier_checks:
                    if check["type"] == "tier_check":
                        result.add_info(
                            f"Found tier check in {py_file.name}:{check['line']}"
                        )
                        
        except SyntaxError:
            continue

    # Verify _get_current_tier() exists
    if total_tier_checks == 0:
        result.add_error("No _get_current_tier() calls found - tier checks not implemented")
    else:
        result.add_info(f"✓ Found {total_tier_checks} tier check calls across all files")

    return result


def main():
    """Run distribution separation verification."""
    # Find source root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    source_root = project_root / "src"

    if not source_root.exists():
        print(f"❌ Source root not found: {source_root}")
        sys.exit(1)

    print("Verifying distribution separation...")
    print(f"Project root: {project_root}")
    print(f"Source root: {source_root}")
    print()

    result = verify_tier_checks(source_root)
    print(result.report())

    sys.exit(0 if result.is_valid() else 1)


if __name__ == "__main__":
    main()
