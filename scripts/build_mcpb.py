#!/usr/bin/env python3
"""Build MCPB (MCP Bundle) for Claude Desktop installation.

This script creates a .mcpb file (ZIP archive) containing:
- manifest.json with server metadata and tool definitions
- pyproject.toml with dependencies
- Source code and config files
- Optional icon.png

Usage:
    python scripts/build_mcpb.py
    python scripts/build_mcpb.py --output dist/codescalpel-1.3.4.mcpb
"""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any

# Project root
ROOT = Path(__file__).parent.parent


def get_version() -> str:
    """Extract version from pyproject.toml."""
    import re

    pyproject = ROOT / "pyproject.toml"
    with open(pyproject, "r") as f:
        content = f.read()

    # Extract version using regex
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    return match.group(1)


def get_mcp_tools() -> list[dict[str, Any]]:
    """Extract MCP tool definitions from contract.py."""
    # In a full implementation, this would parse contract.py
    # For now, return a simplified list
    return [
        {
            "name": "analyze_code",
            "description": "Parse and analyze code structure with AST",
        },
        {
            "name": "extract_code",
            "description": "Extract functions or classes from code files",
        },
        {
            "name": "update_symbol",
            "description": "Update a symbol (function/class) with new implementation",
        },
        {
            "name": "rename_symbol",
            "description": "Safely rename symbols across the codebase",
        },
        {
            "name": "security_scan",
            "description": "Scan code for security vulnerabilities",
        },
        {
            "name": "cross_file_security_scan",
            "description": "Perform cross-file taint analysis",
        },
        {
            "name": "unified_sink_detect",
            "description": "Detect security sinks across multiple languages",
        },
        {
            "name": "type_evaporation_scan",
            "description": "Detect type mismatches at API boundaries",
        },
        {
            "name": "scan_dependencies",
            "description": "Analyze project dependencies for security issues",
        },
        {
            "name": "get_call_graph",
            "description": "Generate call graph for code analysis",
        },
        {
            "name": "get_cross_file_dependencies",
            "description": "Analyze dependencies across multiple files",
        },
        {
            "name": "get_graph_neighborhood",
            "description": "Extract subgraph from code structure",
        },
        {
            "name": "get_project_map",
            "description": "Generate high-level project architecture map",
        },
        {
            "name": "crawl_project",
            "description": "Index and crawl project structure",
        },
        {
            "name": "get_file_context",
            "description": "Get file overview with code folding",
        },
        {
            "name": "get_symbol_references",
            "description": "Find all references to a symbol",
        },
        {
            "name": "validate_paths",
            "description": "Validate file paths within security boundaries",
        },
        {
            "name": "generate_unit_tests",
            "description": "Generate unit tests for code",
        },
        {
            "name": "symbolic_execute",
            "description": "Symbolically execute code with Z3 solver",
        },
        {
            "name": "simulate_refactor",
            "description": "Simulate refactoring impact before applying",
        },
        {
            "name": "code_policy_check",
            "description": "Check code against compliance policies",
        },
        {
            "name": "verify_policy_integrity",
            "description": "Verify cryptographic integrity of policies",
        },
        {
            "name": "get_capabilities",
            "description": "Get current tier capabilities and limits",
        },
    ]


def create_manifest(version: str) -> dict[str, Any]:
    """Create manifest.json content."""
    tools = get_mcp_tools()

    manifest = {
        "name": "codescalpel",
        "version": version,
        "description": "MCP server toolkit for AI agents - surgical code analysis and modification",
        "author": "Timmothy Escolopio",
        "license": "MIT",
        "homepage": "https://github.com/3D-Tech-Solutions/code-scalpel",
        "repository": {
            "type": "git",
            "url": "https://github.com/3D-Tech-Solutions/code-scalpel.git",
        },
        "keywords": [
            "code-analysis",
            "ast",
            "pdg",
            "symbolic-execution",
            "ai-agents",
            "mcp",
            "static-analysis",
            "security-scanning",
        ],
        "server": {
            "type": "uv",
            "package": "codescalpel",
            "command": "codescalpel mcp",
            "env": {
                "CODE_SCALPEL_TIER": "community",
            },
        },
        "tools": [
            {
                "name": tool["name"],
                "description": tool["description"],
            }
            for tool in tools
        ],
        "resources": [
            {
                "name": "documentation",
                "uri": "https://github.com/3D-Tech-Solutions/code-scalpel#readme",
                "description": "Code Scalpel documentation",
            },
            {
                "name": "mcp-tools",
                "uri": "https://github.com/3D-Tech-Solutions/code-scalpel/blob/main/docs/deployment/ides/claude-desktop.md",
                "description": "MCP tools reference",
            },
        ],
    }

    return manifest


def build_mcpb(output_path: Path | None = None) -> Path:
    """Build MCPB bundle.

    Args:
        output_path: Optional output path for .mcpb file

    Returns:
        Path to created .mcpb file
    """
    version = get_version()

    if output_path is None:
        output_path = ROOT / "dist" / f"codescalpel-{version}.mcpb"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary build directory
    build_dir = ROOT / "build" / "mcpb"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    print(f"Building MCPB for Code Scalpel v{version}...")

    # 1. Create manifest.json
    print("  ✓ Creating manifest.json")
    manifest = create_manifest(version)
    manifest_path = build_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # 2. Copy pyproject.toml (required for uv runtime)
    print("  ✓ Copying pyproject.toml")
    shutil.copy(ROOT / "pyproject.toml", build_dir / "pyproject.toml")

    # 3. Copy source code
    print("  ✓ Copying source code")
    src_dest = build_dir / "src"
    shutil.copytree(ROOT / "src" / "code_scalpel", src_dest / "code_scalpel")

    # 4. Copy config files
    print("  ✓ Copying configuration files")
    config_dir = build_dir / ".code-scalpel"
    config_dir.mkdir()
    shutil.copy(ROOT / ".code-scalpel" / "limits.toml", config_dir / "limits.toml")
    shutil.copy(ROOT / ".code-scalpel" / "features.toml", config_dir / "features.toml")

    # 5. Copy README and LICENSE
    print("  ✓ Copying README and LICENSE")
    shutil.copy(ROOT / "README.md", build_dir / "README.md")
    shutil.copy(ROOT / "LICENSE", build_dir / "LICENSE")

    # 6. Copy icon if exists
    icon_path = ROOT / "docs" / "assets" / "icon.png"
    if icon_path.exists():
        print("  ✓ Copying icon.png")
        shutil.copy(icon_path, build_dir / "icon.png")

    # 7. Create .mcpb (ZIP archive)
    print(f"  ✓ Creating {output_path.name}")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in build_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(build_dir)
                zipf.write(file_path, arcname)

    # 8. Cleanup build directory
    shutil.rmtree(build_dir)

    file_size = output_path.stat().st_size / (1024 * 1024)  # MB
    print(f"\n✅ MCPB bundle created: {output_path}")
    print(f"   Size: {file_size:.2f} MB")
    print(f"   Version: {version}")
    print(f"   Tools: {len(manifest['tools'])} MCP tools")

    return output_path


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Build MCPB bundle for Claude Desktop")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path for .mcpb file (default: dist/codescalpel-{version}.mcpb)",
    )
    parser.add_argument(
        "--version", "-v", action="store_true", help="Print version and exit"
    )

    args = parser.parse_args()

    if args.version:
        print(f"Code Scalpel v{get_version()}")
        return

    try:
        mcpb_path = build_mcpb(args.output)
        print("\n🎉 Ready for Claude Desktop installation!")
        print(f"   Double-click {mcpb_path.name} to install")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        raise


if __name__ == "__main__":
    main()
