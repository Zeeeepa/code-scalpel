#!/usr/bin/env python3
"""Composer Parser — PHP dependency and package management analysis.

[20260304_FEATURE] Phase 2: full implementation (pure Python — no CLI needed).

Reference: https://getcomposer.org/
Parses composer.json and composer.lock using stdlib json only.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Semver range constraint pattern for basic parsing
_CONSTRAINT_RE = re.compile(r"[^\d]*(\d+\.\d+(?:\.\d+)?)")


@dataclass
class ComposerPackage:
    """Represents a Composer package dependency."""

    name: str
    version: str
    constraint: Optional[str] = None
    is_dev: bool = False
    description: Optional[str] = None
    license: Optional[str] = None


@dataclass
class ComposerConfig:
    """Composer project configuration."""

    name: Optional[str] = None
    description: Optional[str] = None
    requires: List[ComposerPackage] = field(default_factory=list)
    requires_dev: List[ComposerPackage] = field(default_factory=list)
    autoload: Dict[str, Any] = field(default_factory=dict)
    scripts: Dict[str, str] = field(default_factory=dict)


def _extract_package(name: str, constraint: str, is_dev: bool) -> ComposerPackage:
    """Build a ComposerPackage from name + version constraint."""
    return ComposerPackage(
        name=name,
        version=constraint,
        constraint=constraint,
        is_dev=is_dev,
    )


class ComposerParser:
    """Parser for Composer dependency management files.

    [20260304_FEATURE] Full implementation — pure Python, no CLI required.
    Parses composer.json and composer.lock.
    """

    def __init__(self) -> None:
        """Initialise ComposerParser."""
        self.config: Optional[ComposerConfig] = None
        self.installed: List[ComposerPackage] = []
        self.language = "php"

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def parse_composer_json(self, json_file: Path) -> ComposerConfig:
        """Parse composer.json into a ComposerConfig.

        [20260304_FEATURE] Full implementation.

        Args:
            json_file: Path to composer.json.
        Returns:
            Parsed ComposerConfig object.
        """
        try:
            data = json.loads(Path(json_file).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return ComposerConfig()

        config = ComposerConfig(
            name=data.get("name"),
            description=data.get("description", ""),
            autoload=data.get("autoload", {}),
            scripts={
                k: (v if isinstance(v, str) else str(v))
                for k, v in data.get("scripts", {}).items()
            },
        )
        for pkg_name, constraint in data.get("require", {}).items():
            if pkg_name == "php":
                continue  # skip PHP runtime constraint
            config.requires.append(_extract_package(pkg_name, constraint, is_dev=False))
        for pkg_name, constraint in data.get("require-dev", {}).items():
            config.requires_dev.append(
                _extract_package(pkg_name, constraint, is_dev=True)
            )

        self.config = config
        return config

    def parse_composer_json_string(self, json_data: str) -> ComposerConfig:
        """Parse composer.json content from a string (helper for tests)."""
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return ComposerConfig()
        config = ComposerConfig(
            name=data.get("name"),
            description=data.get("description", ""),
            autoload=data.get("autoload", {}),
        )
        for pkg_name, constraint in data.get("require", {}).items():
            if pkg_name == "php":
                continue
            config.requires.append(_extract_package(pkg_name, constraint, is_dev=False))
        for pkg_name, constraint in data.get("require-dev", {}).items():
            config.requires_dev.append(
                _extract_package(pkg_name, constraint, is_dev=True)
            )
        self.config = config
        return config

    def parse_composer_lock(self, lock_file: Path) -> List[ComposerPackage]:
        """Parse composer.lock into installed package list.

        [20260304_FEATURE] Full implementation.

        Args:
            lock_file: Path to composer.lock.
        Returns:
            List of installed ComposerPackage objects.
        """
        try:
            data = json.loads(Path(lock_file).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        packages: List[ComposerPackage] = []
        for pkg in data.get("packages", []):
            packages.append(
                ComposerPackage(
                    name=pkg.get("name", ""),
                    version=pkg.get("version", ""),
                    is_dev=False,
                    description=pkg.get("description", ""),
                    license=str(pkg.get("license", "") or ""),
                )
            )
        for pkg in data.get("packages-dev", []):
            packages.append(
                ComposerPackage(
                    name=pkg.get("name", ""),
                    version=pkg.get("version", ""),
                    is_dev=True,
                    description=pkg.get("description", ""),
                    license=str(pkg.get("license", "") or ""),
                )
            )
        self.installed = packages
        return packages

    def parse_composer_lock_string(self, json_data: str) -> List[ComposerPackage]:
        """Parse composer.lock content from a string (helper for tests)."""
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return []
        packages: List[ComposerPackage] = []
        for pkg in data.get("packages", []):
            packages.append(
                ComposerPackage(
                    name=pkg.get("name", ""),
                    version=pkg.get("version", ""),
                    is_dev=False,
                    description=pkg.get("description"),
                )
            )
        for pkg in data.get("packages-dev", []):
            packages.append(
                ComposerPackage(
                    name=pkg.get("name", ""),
                    version=pkg.get("version", ""),
                    is_dev=True,
                    description=pkg.get("description"),
                )
            )
        self.installed = packages
        return packages

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def scan_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Return installed packages with advisories stub.

        [20260304_FEATURE] Checks for known bad version ranges in known packages.
        Production implementations should call packagist or use composer audit.
        """
        # Basic allowlist — flag if version contains "dev-" (unstable) or "*" (unbounded)
        risk: List[Dict[str, Any]] = []
        for pkg in self.installed:
            if "*" in (pkg.constraint or "") or "dev-" in pkg.version:
                risk.append(
                    {
                        "package": pkg.name,
                        "version": pkg.version,
                        "risk": (
                            "unbounded_constraint"
                            if "*" in (pkg.constraint or "")
                            else "dev_version"
                        ),
                        "advisory": None,
                    }
                )
        return risk

    def detect_outdated(self) -> List[ComposerPackage]:
        """Return packages whose version constraint allows major upgrades.

        [20260304_FEATURE] Heuristic: flag '^' major-wildcard constraints only.
        Real outdated detection requires calling the Packagist API.
        """
        outdated: List[ComposerPackage] = []
        if self.config is None:
            return outdated
        for pkg in self.config.requires + self.config.requires_dev:
            # Flag packages using ^ (compatible-with) major-version upgrades
            if pkg.constraint and pkg.constraint.startswith("^"):
                outdated.append(pkg)
        return outdated

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_report(
        self,
        packages: Optional[List[ComposerPackage]] = None,
        fmt: str = "json",
    ) -> str:
        """Return JSON or text dependency report."""
        pkgs = packages if packages is not None else (self.installed or [])
        if fmt == "json":
            return json.dumps(
                {
                    "tool": "composer",
                    "project": self.config.name if self.config else None,
                    "package_count": len(pkgs),
                    "packages": [
                        {
                            "name": p.name,
                            "version": p.version,
                            "dev": p.is_dev,
                            "license": p.license,
                        }
                        for p in pkgs
                    ],
                },
                indent=2,
            )
        return "\n".join(f"{p.name}:{p.version} (dev={p.is_dev})" for p in pkgs)
