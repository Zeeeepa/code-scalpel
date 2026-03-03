#!/usr/bin/env python3
# [20260303_FEATURE] Complete implementation of test detection parser (was stub)
"""
Test Detection JavaScript Parser - Test framework and file discovery.

Reference: https://jestjs.io/docs/getting-started

No external tools required.  Framework detection works from package.json
devDependencies; file discovery uses pathlib glob patterns.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Mapping of devDependency name -> canonical framework name
_FRAMEWORK_DEPS: dict[str, str] = {
    "jest": "jest",
    "@jest/core": "jest",
    "ts-jest": "jest",
    "babel-jest": "jest",
    "mocha": "mocha",
    "vitest": "vitest",
    "jasmine": "jasmine",
    "jasmine-core": "jasmine",
    "ava": "ava",
    "tap": "tap",
    "tape": "tape",
    "qunit": "qunit",
    "cypress": "cypress",
    "@cypress/react": "cypress",
    "playwright": "playwright",
    "@playwright/test": "playwright",
    "karma": "karma",
    "karma-jasmine": "jasmine",
    "karma-mocha": "mocha",
}

# Glob patterns used when discovering test files
_TEST_PATTERNS: list[str] = [
    "**/*.test.js",
    "**/*.spec.js",
    "**/*.test.ts",
    "**/*.spec.ts",
    "**/*.test.mjs",
    "**/*.spec.mjs",
    "**/__tests__/**/*.js",
    "**/__tests__/**/*.ts",
]

# Directories blacklisted during file discovery
_IGNORE_DIRS: frozenset[str] = frozenset(
    {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "coverage"}
)


@dataclass
class TestDetectionResult:
    """Result of test framework detection and file discovery."""

    # [20260303_FEATURE] Dataclass matching Stage 4b specification
    framework: str = "unknown"
    test_files: list[str] = field(default_factory=list)
    config: dict = field(default_factory=dict)
    total_test_files: int = 0


class TestDetectionParser:
    """Detect JavaScript test frameworks and enumerate test files.

    All methods are pure (no subprocess calls).
    """

    # [20260303_FEATURE] Complete parser implementation

    def __init__(self) -> None:
        """Initialise TestDetectionParser."""
        pass

    def detect_test_framework(self, package_json: dict[str, Any]) -> str:
        """Identify the primary test framework from a parsed package.json.

        Checks ``devDependencies`` (and ``dependencies`` as fallback) against
        a known mapping of package names to framework names.

        Args:
            package_json: Parsed contents of a package.json file.

        Returns:
            Canonical framework name (e.g. ``"jest"``, ``"mocha"``) or
            ``"unknown"``.
        """
        dev_deps: dict[str, Any] = package_json.get("devDependencies") or {}
        deps: dict[str, Any] = package_json.get("dependencies") or {}
        all_deps = {**deps, **dev_deps}
        for dep_name in all_deps:
            canonical = _FRAMEWORK_DEPS.get(dep_name.lower())
            if canonical:
                return canonical
        # Also check scripts for clues (e.g. "test": "jest" )
        scripts: dict[str, str] = package_json.get("scripts") or {}
        test_script = scripts.get("test", "").lower()
        for keyword in ("jest", "mocha", "vitest", "jasmine", "ava", "tap", "karma"):
            if keyword in test_script:
                return keyword
        return "unknown"

    def find_test_files(self, project_root: str | Path) -> list[str]:
        """Discover test files under *project_root* using glob patterns.

        Skips ``node_modules``, ``.git``, and other common non-source
        directories.

        Args:
            project_root: Root directory of the JavaScript project.

        Returns:
            Sorted list of relative path strings (relative to *project_root*).
        """
        root = Path(project_root)
        found: set[str] = set()
        for pattern in _TEST_PATTERNS:
            for path in root.glob(pattern):
                # Discard paths that pass through ignored directories
                parts = path.relative_to(root).parts
                if any(p in _IGNORE_DIRS for p in parts):
                    continue
                found.add(path.relative_to(root).as_posix())
        return sorted(found)

    def get_test_config(self, package_json: dict[str, Any]) -> dict[str, Any]:
        """Extract test tool configuration embedded in package.json.

        Looks for top-level ``jest``, ``mocha``, ``vitest``, and ``ava``
        configuration sections.

        Args:
            package_json: Parsed contents of a package.json file.

        Returns:
            Dict mapping framework name to its configuration sub-dict
            (empty dict if none found).
        """
        config: dict[str, Any] = {}
        for key in ("jest", "mocha", "vitest", "ava", "tap", "karma"):
            if key in package_json:
                config[key] = package_json[key]
        return config

    def generate_report(
        self, findings: dict[str, Any], format: str = "json"
    ) -> str:
        """Generate a test detection report.

        Args:
            findings: A dict (or TestDetectionResult converted to dict) with
                      keys ``framework``, ``test_files``, ``config``, and
                      ``total_test_files``.
            format: Output format (currently only "json" is supported).

        Returns:
            JSON string with tool name and detection results.
        """
        if isinstance(findings, TestDetectionResult):
            data: dict[str, Any] = {
                "framework": findings.framework,
                "test_files": findings.test_files,
                "config": findings.config,
                "total_test_files": findings.total_test_files,
            }
        else:
            data = dict(findings)
        report = {"tool": "test-detection", **data}
        return json.dumps(report, indent=2)
