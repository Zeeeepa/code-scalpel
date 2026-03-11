#!/usr/bin/env python3
"""
Gradle Java Parser - Build tool and dependency management integration.

[20260303_FEATURE] Full implementation replacing NotImplementedError stubs.

Reference: https://gradle.org/
Command: gradle dependencies --configuration compileClasspath
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# e.g. implementation 'com.example:lib:1.0'
# [20260303_BUGFIX] Exclude newlines from character classes to prevent cross-line matching.
_DEP_RE = re.compile(
    r"(?P<config>\w+)\s+['\"](?P<group>[^:\n'\"]+):(?P<name>[^:\n'\"]+):(?P<version>[^'\"\n]+)['\"]"
)
# Gradle build output: error line
_BUILD_ERROR_RE = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+):(?P<col>\d+):\s+(?P<type>error|warning):\s+(?P<msg>.+)$",
    re.IGNORECASE,
)


@dataclass
class GradleDependency:
    """Gradle dependency entry."""

    group: str
    name: str
    version: str
    configuration: str = "implementation"


@dataclass
class GradleCompileError:
    """A compile error from Gradle build output."""

    file_path: str
    line: int
    column: int
    message: str
    error_type: str = "error"


class GradleParser:
    """Parser for Gradle build configuration and dependency graphs.

    [20260303_FEATURE] Full implementation with parse_gradle_file,
    get_dependencies, parse_build_output, extract_compile_errors, generate_report.
    """

    def __init__(self, build_path: Optional[Path] = None) -> None:
        """Initialize Gradle parser."""
        self.build_path = Path(build_path) if build_path else None
        self._gradle_data: Optional[Dict[str, Any]] = None

    def parse_gradle_file(self, path: Optional[Path] = None) -> Dict[str, Any]:
        """Parse a ``build.gradle`` or ``build.gradle.kts`` file using regex.

        [20260303_FEATURE] Extracts dependencies via pattern matching.
        """
        target = Path(path) if path else self.build_path
        if target is None:
            return {}
        try:
            content = target.read_text(encoding="utf-8")
        except OSError:
            return {}
        deps = self.get_dependencies(content=content)
        self._gradle_data = {
            "file": str(target),
            "dependencies": deps,
            "raw": content,
        }
        return self._gradle_data

    def get_dependencies(
        self,
        content: Optional[str] = None,
    ) -> List[GradleDependency]:
        """Extract dependencies from Gradle build file content."""
        if content is None:
            if self._gradle_data is not None:
                content = self._gradle_data.get("raw", "")
            elif self.build_path:
                try:
                    content = self.build_path.read_text(encoding="utf-8")
                except OSError:
                    return []
            else:
                return []
        deps: List[GradleDependency] = []
        for m in _DEP_RE.finditer(content):
            deps.append(
                GradleDependency(
                    group=m.group("group"),
                    name=m.group("name"),
                    version=m.group("version"),
                    configuration=m.group("config"),
                )
            )
        return deps

    def parse_build_output(self, text: str) -> List[Dict[str, Any]]:
        """Parse Gradle build output into structured records."""
        results: List[Dict[str, Any]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            upper = line.upper()
            if "BUILD SUCCESSFUL" in upper:
                results.append({"level": "SUCCESS", "message": line})
            elif "BUILD FAILED" in upper:
                results.append({"level": "FAILED", "message": line})
            elif upper.startswith("ERROR:") or upper.startswith("> TASK"):
                results.append({"level": "ERROR", "message": line})
            elif upper.startswith("W:") or "> Configure" in upper:
                results.append({"level": "WARNING", "message": line})
            else:
                results.append({"level": "INFO", "message": line})
        return results

    def extract_compile_errors(self, text: str = "") -> List[GradleCompileError]:
        """Extract compile errors from Gradle build output."""
        errors: List[GradleCompileError] = []
        for line in text.splitlines():
            m = _BUILD_ERROR_RE.match(line.strip())
            if m:
                try:
                    ln, col = int(m.group("line")), int(m.group("col"))
                except ValueError:
                    ln, col = 0, 0
                errors.append(
                    GradleCompileError(
                        file_path=m.group("file").strip(),
                        line=ln,
                        column=col,
                        message=m.group("msg").strip(),
                        error_type=m.group("type").upper(),
                    )
                )
        return errors

    def generate_report(
        self,
        dependencies: Optional[List[GradleDependency]] = None,
        errors: Optional[List[GradleCompileError]] = None,
        format: str = "json",
    ) -> str:
        """Return a JSON or text report."""
        deps = dependencies if dependencies is not None else self.get_dependencies()
        errs = errors or []
        if format == "json":
            return json.dumps(
                {
                    "tool": "gradle",
                    "dependencies": len(deps),
                    "compile_errors": len(errs),
                    "dependency_list": [
                        {
                            "group": d.group,
                            "name": d.name,
                            "version": d.version,
                            "configuration": d.configuration,
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
        lines = [f"Gradle: {len(deps)} dependencies, {len(errs)} compile errors"]
        for d in deps:
            lines.append(f"  {d.group}:{d.name}:{d.version} [{d.configuration}]")
        return "\n".join(lines)

    def parse(self) -> Dict[str, Any]:
        """Backward-compat: parse the build file set in constructor."""
        return self.parse_gradle_file(self.build_path) if self.build_path else {}
