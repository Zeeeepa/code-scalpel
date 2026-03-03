#!/usr/bin/env python3
# [20260303_FEATURE] Complete implementation of package.json parser (was stub)
"""
Package.json JavaScript Parser - npm package configuration analysis.

Reference: https://docs.npmjs.com/cli/v10/configuring-npm/package-json

No external tool execution required; reads and analyses package.json directly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Known framework identifiers mapped to a canonical name
_FRAMEWORK_MAP: dict[str, str] = {
    "react": "react",
    "react-dom": "react",
    "vue": "vue",
    "@angular/core": "angular",
    "next": "next",
    "nuxt": "nuxt",
    "svelte": "svelte",
    "@sveltejs/kit": "sveltekit",
    "gatsby": "gatsby",
    "remix": "remix",
    "@remix-run/react": "remix",
    "astro": "astro",
    "ember-cli": "ember",
    "ember-source": "ember",
    "preact": "preact",
    "solid-js": "solidjs",
    "@solidjs/start": "solidjs",
    "express": "express",
    "fastify": "fastify",
    "hapi": "hapi",
    "koa": "koa",
}


@dataclass
class PackageInfo:
    """Structured representation of a package.json file."""

    # [20260303_FEATURE] Dataclass matching Stage 4b specification
    name: str = ""
    version: str = ""
    description: str = ""
    dependencies: dict = field(default_factory=dict)
    dev_dependencies: dict = field(default_factory=dict)
    scripts: dict = field(default_factory=dict)
    engines: dict = field(default_factory=dict)
    license: str = ""
    main: str = ""
    raw: dict = field(default_factory=dict)


class PackageJsonParser:
    """Parser for package.json configuration files.

    All operations are pure (no subprocess calls).
    """

    # [20260303_FEATURE] Complete parser implementation

    def __init__(self) -> None:
        """Initialise PackageJsonParser."""
        pass

    def parse_package_json(self, path: str | Path) -> PackageInfo:
        """Read and parse a package.json file.

        Args:
            path: Path to the package.json file.

        Returns:
            PackageInfo dataclass with the parsed data.

        Raises:
            FileNotFoundError: If *path* does not exist.
            json.JSONDecodeError: If file content is not valid JSON.
        """
        raw_text = Path(path).read_text(encoding="utf-8")
        data: dict[str, Any] = json.loads(raw_text)
        return PackageInfo(
            name=str(data.get("name", "")),
            version=str(data.get("version", "")),
            description=str(data.get("description", "")),
            dependencies=dict(data.get("dependencies") or {}),
            dev_dependencies=dict(data.get("devDependencies") or {}),
            scripts=dict(data.get("scripts") or {}),
            engines=dict(data.get("engines") or {}),
            license=str(data.get("license", "")),
            main=str(data.get("main", "")),
            raw=data,
        )

    def get_dependencies(self, pkg: PackageInfo) -> list[tuple[str, str]]:
        """Return production dependencies as (name, version) tuples.

        Args:
            pkg: A parsed PackageInfo instance.

        Returns:
            List of (name, version) tuples from ``dependencies``.
        """
        return list(pkg.dependencies.items())

    def get_dev_dependencies(self, pkg: PackageInfo) -> list[tuple[str, str]]:
        """Return dev dependencies as (name, version) tuples.

        Args:
            pkg: A parsed PackageInfo instance.

        Returns:
            List of (name, version) tuples from ``devDependencies``.
        """
        return list(pkg.dev_dependencies.items())

    def get_scripts(self, pkg: PackageInfo) -> dict[str, str]:
        """Return the npm scripts defined in the package.

        Args:
            pkg: A parsed PackageInfo instance.

        Returns:
            Dict mapping script name to shell command.
        """
        return dict(pkg.scripts)

    def detect_framework(self, pkg: PackageInfo) -> str:
        """Detect the primary JavaScript framework used by the package.

        Checks both ``dependencies`` and ``devDependencies`` against a known
        set of framework package names.

        Args:
            pkg: A parsed PackageInfo instance.

        Returns:
            A lowercase framework name (e.g. ``"react"``, ``"vue"``) or
            ``"unknown"`` if none is recognised.
        """
        all_deps = {**pkg.dependencies, **pkg.dev_dependencies}
        for dep_name in all_deps:
            canonical = _FRAMEWORK_MAP.get(dep_name.lower())
            if canonical:
                return canonical
        return "unknown"

    def get_node_engine_requirement(self, pkg: PackageInfo) -> str | None:
        """Extract the required Node.js version string from ``engines.node``.

        Args:
            pkg: A parsed PackageInfo instance.

        Returns:
            Version string (e.g. ``">=18.0.0"``) or ``None`` if not specified.
        """
        node_req = pkg.engines.get("node")
        if node_req:
            return str(node_req)
        return None

    def generate_report(self, pkg: PackageInfo, format: str = "json") -> str:
        """Generate a structured package.json report.

        Args:
            pkg: A parsed PackageInfo instance.
            format: Output format (currently only "json" is supported).

        Returns:
            JSON string with tool name and key package metadata.
        """
        report = {
            "tool": "package-json",
            "name": pkg.name,
            "version": pkg.version,
            "description": pkg.description,
            "license": pkg.license,
            "framework": self.detect_framework(pkg),
            "node_engine": self.get_node_engine_requirement(pkg),
            "scripts": self.get_scripts(pkg),
            "dependency_count": len(pkg.dependencies),
            "dev_dependency_count": len(pkg.dev_dependencies),
        }
        return json.dumps(report, indent=2)
