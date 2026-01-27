"""Validate that project documentation stays in sync with released version.

This script ensures:
1. README.md version matches pyproject.toml version
2. README.md mentions of tool counts match actual MCP tool registry (20 dev + 3 system = 23 total)
3. All critical metadata is consistent across documentation

This should be run in CI to catch stale documentation before release.

Exit codes:
  0 - All validations passed
  1 - Validation failed
"""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_pyproject_version() -> str:
    """Read version from pyproject.toml."""
    pyproject = _repo_root() / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")

    # Find version = "X.Y.Z"
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def _read_readme_version() -> str:
    """Read version from README.md."""
    readme = _repo_root() / "README.md"
    content = readme.read_text(encoding="utf-8")

    # Find "Latest Release: vX.Y.Z"
    match = re.search(r"Latest Release:\s*v(\d+\.\d+\.\d+)", content)
    if not match:
        raise ValueError("Could not find 'Latest Release' version in README.md")
    return match.group(1)


def _read_readme_tool_count() -> int | None:
    """Extract tool count mentioned in README.md."""
    readme = _repo_root() / "README.md"
    content = readme.read_text(encoding="utf-8")

    # Find patterns like "22 specialized tools" or "23 tools"
    match = re.search(r"(\d+)\s+(?:specialized\s+)?tools", content)
    if match:
        return int(match.group(1))
    return None


async def _fetch_actual_tool_count() -> int:
    """Query the MCP server to get actual tool count."""
    repo_root = _repo_root()

    # Always document the full tool surface shipped by this repo.
    import os

    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    parts = [str(repo_root)]
    if existing:
        parts.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(parts)

    # Use a tiny, empty project root so tools that require a root can still initialize.
    project_root = Path(os.environ.get("CODE_SCALPEL_DOC_PROJECT_ROOT", ""))
    if not project_root:
        project_root = repo_root / "evidence" / "mcp_tools_docgen"
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "README.txt").write_text(
            "Temporary project root for docs validation.\n", encoding="utf-8"
        )

    # Set tier to community (no license needed)
    env["CODE_SCALPEL_TIER"] = "community"
    env["CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY"] = "1"

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "code_scalpel.mcp.server", "--root", str(project_root)],
        env=env,
    )

    try:
        return await asyncio.wait_for(
            _fetch_tools_with_session(params),
            timeout=90,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to query MCP server for tool count: {e}")


async def _fetch_tools_with_session(params: StdioServerParameters) -> int:
    """Helper to fetch tool count from MCP server."""
    from mcp.client.stdio import stdio_client

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            return len(tools_result.tools)


def main() -> int:
    """Run all validations."""
    errors: list[str] = []

    # 1. Check version consistency
    try:
        pyproject_version = _read_pyproject_version()
        readme_version = _read_readme_version()

        if pyproject_version != readme_version:
            errors.append(
                f"Version mismatch:\n"
                f"  pyproject.toml: v{pyproject_version}\n"
                f"  README.md: v{readme_version}\n"
                f"  → Update README.md 'Latest Release' to match pyproject.toml"
            )
        else:
            print(f"✓ Version consistent: v{pyproject_version}")
    except Exception as e:
        errors.append(f"Version check failed: {e}")

    # 2. Check tool count (async)
    try:
        actual_tool_count = asyncio.run(_fetch_actual_tool_count())
        readme_tool_count = _read_readme_tool_count()

        if readme_tool_count is not None and readme_tool_count != actual_tool_count:
            errors.append(
                f"Tool count mismatch:\n"
                f"  README.md claims: {readme_tool_count} tools\n"
                f"  Actually registered: {actual_tool_count} tools\n"
                f"  → Update README.md tool count mentions to {actual_tool_count}"
            )
        else:
            print(f"✓ Tool count: {actual_tool_count} tools registered")
    except Exception as e:
        errors.append(f"Tool count check failed: {e}")

    # Print results
    if errors:
        print("\n❌ Documentation validation failed:\n")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}\n")
        return 1

    print("\n✅ All documentation validations passed!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
