#!/usr/bin/env python3
"""
Maven Java Parser - Build tool and dependency management integration.

[20260303_FEATURE] Full implementation replacing NotImplementedError stubs.

Reference: https://maven.apache.org/
Command: mvn dependency:tree -DoutputFile=dependencies.txt
         mvn compile / mvn test
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

_POM_NS = "http://maven.apache.org/POM/4.0.0"


@dataclass
class MavenDependency:
    """Maven dependency entry."""

    group_id: str
    artifact_id: str
    version: str
    scope: str = "compile"


@dataclass
class MavenPlugin:
    """Maven plugin entry."""

    group_id: str
    artifact_id: str
    version: str = ""


@dataclass
class CompileError:
    """A compile error extracted from Maven build output."""

    file_path: str
    line: int
    column: int
    message: str
    error_type: str = "ERROR"


_COMPILE_ERROR_RE = re.compile(
    r"\[(?P<type>ERROR|WARNING)\]\s+(?P<file>[^\[]+)\[(?P<line>\d+),(?P<col>\d+)\]\s+(?P<msg>.+)"
)


def _strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


class MavenParser:
    """Parser for Maven POM files and build output.

    [20260303_FEATURE] Full implementation with parse_pom_xml, get_dependencies,
    get_plugins, parse_build_output, extract_compile_errors, generate_report.
    """

    def __init__(self, pom_path: Optional[Path] = None) -> None:
        """Initialize Maven parser."""
        self.pom_path = Path(pom_path) if pom_path else None
        self._pom_data: Optional[Dict[str, Any]] = None

    def parse_pom_xml(self, path: Optional[Path] = None) -> Dict[str, Any]:
        """Parse a Maven ``pom.xml`` file and return structured data."""
        target = Path(path) if path else self.pom_path
        if target is None:
            return {}
        try:
            tree = ET.parse(str(target))
        except (ET.ParseError, OSError):
            return {}
        root = tree.getroot()

        def _text(elem: Optional[ET.Element]) -> str:
            return elem.text.strip() if elem is not None and elem.text else ""

        def _find(parent: ET.Element, tag: str) -> Optional[ET.Element]:
            result = parent.find(f"{{{_POM_NS}}}{tag}")
            return result if result is not None else parent.find(tag)

        def _findall(parent: ET.Element, path_str: str) -> List[ET.Element]:
            parts = path_str.split("/")
            ns_path = "/".join(f"{{{_POM_NS}}}{p}" for p in parts)
            result = parent.findall(ns_path)
            return result if result else parent.findall(path_str)

        deps: List[MavenDependency] = []
        for dep in _findall(root, "dependencies/dependency"):
            deps.append(
                MavenDependency(
                    group_id=_text(_find(dep, "groupId")),
                    artifact_id=_text(_find(dep, "artifactId")),
                    version=_text(_find(dep, "version")),
                    scope=_text(_find(dep, "scope")) or "compile",
                )
            )

        plugins: List[MavenPlugin] = []
        for plugin in _findall(root, "build/plugins/plugin"):
            plugins.append(
                MavenPlugin(
                    group_id=_text(_find(plugin, "groupId")),
                    artifact_id=_text(_find(plugin, "artifactId")),
                    version=_text(_find(plugin, "version")),
                )
            )

        props: Dict[str, str] = {}
        props_elem = _find(root, "properties")
        if props_elem is not None:
            for child in props_elem:
                props[_strip_ns(child.tag)] = (child.text or "").strip()

        self._pom_data = {
            "group_id": _text(_find(root, "groupId")),
            "artifact_id": _text(_find(root, "artifactId")),
            "version": _text(_find(root, "version")),
            "dependencies": deps,
            "plugins": plugins,
            "properties": props,
        }
        return self._pom_data

    def get_dependencies(self) -> List[MavenDependency]:
        """Return dependencies from the last ``parse_pom_xml`` call."""
        if self._pom_data is None:
            return []
        return list(self._pom_data.get("dependencies", []))

    def get_plugins(self) -> List[MavenPlugin]:
        """Return plugins from the last ``parse_pom_xml`` call."""
        if self._pom_data is None:
            return []
        return list(self._pom_data.get("plugins", []))

    def parse_build_output(self, text: str) -> List[Dict[str, Any]]:
        """Parse Maven build stdout/stderr into structured level+message records."""
        results: List[Dict[str, Any]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            for prefix, level in (
                ("[ERROR]", "ERROR"),
                ("[WARNING]", "WARNING"),
                ("[INFO]", "INFO"),
            ):
                if line.startswith(prefix):
                    results.append(
                        {"level": level, "message": line[len(prefix) :].strip()}
                    )
                    break
        return results

    def extract_compile_errors(self, text: str = "") -> List[CompileError]:
        """Extract compile errors from Maven build output."""
        errors: List[CompileError] = []
        for line in text.splitlines():
            m = _COMPILE_ERROR_RE.match(line.strip())
            if m:
                try:
                    ln, col = int(m.group("line")), int(m.group("col"))
                except ValueError:
                    ln, col = 0, 0
                errors.append(
                    CompileError(
                        file_path=m.group("file").strip(),
                        line=ln,
                        column=col,
                        message=m.group("msg").strip(),
                        error_type=m.group("type"),
                    )
                )
        return errors

    def generate_report(
        self,
        dependencies: Optional[List[MavenDependency]] = None,
        errors: Optional[List[CompileError]] = None,
        format: str = "json",
    ) -> str:
        """Return a JSON or text report."""
        deps = dependencies if dependencies is not None else self.get_dependencies()
        errs = errors or []
        if format == "json":
            return json.dumps(
                {
                    "tool": "maven",
                    "dependencies": len(deps),
                    "compile_errors": len(errs),
                    "dependency_list": [
                        {
                            "group": d.group_id,
                            "artifact": d.artifact_id,
                            "version": d.version,
                            "scope": d.scope,
                        }
                        for d in deps
                    ],
                    "errors": [
                        {
                            "file": e.file_path,
                            "line": e.line,
                            "column": e.column,
                            "type": e.error_type,
                            "message": e.message,
                        }
                        for e in errs
                    ],
                },
                indent=2,
            )
        lines = [f"Maven: {len(deps)} dependencies, {len(errs)} compile errors"]
        for d in deps:
            lines.append(f"  {d.group_id}:{d.artifact_id}:{d.version} [{d.scope}]")
        return "\n".join(lines)

    def parse(self) -> Dict[str, Any]:
        """Backward-compat: parse the POM file set in constructor."""
        return self.parse_pom_xml(self.pom_path) if self.pom_path else {}
