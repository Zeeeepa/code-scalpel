#!/usr/bin/env python3
"""Gradle build parser for Kotlin projects.

[20260303_FEATURE] Phase 2: full implementation replacing NotImplementedError stubs.
"""

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfigurationType(Enum):
    IMPLEMENTATION = "implementation"
    API = "api"
    COMPILE_ONLY = "compileOnly"
    RUNTIME_ONLY = "runtimeOnly"
    TEST_IMPLEMENTATION = "testImplementation"
    DEBUG_IMPLEMENTATION = "debugImplementation"
    RELEASE_IMPLEMENTATION = "releaseImplementation"


class PluginType(Enum):
    ANDROID_APPLICATION = "android-application"
    ANDROID_LIBRARY = "android-library"
    KOTLIN_ANDROID = "kotlin-android"
    KOTLIN_JVM = "kotlin-jvm"
    KOTLIN_MULTIPLATFORM = "kotlin-multiplatform"
    COMPOSE = "compose"
    DETEKT = "detekt"
    KTLINT = "ktlint"
    OTHER = "other"


@dataclass
class Dependency:
    group: str
    artifact: str
    version: Optional[str] = None
    configuration: str = "implementation"
    is_bom: bool = False

    def __str__(self) -> str:
        v = f":{self.version}" if self.version else ""
        return f'{self.configuration}("{self.group}:{self.artifact}{v}")'


@dataclass
class GradlePlugin:
    id: str
    version: Optional[str] = None
    plugin_type: str = PluginType.OTHER.value


@dataclass
class BuildConfiguration:
    source_file: Optional[Path] = None
    compile_sdk: Optional[int] = None
    min_sdk: Optional[int] = None
    target_sdk: Optional[int] = None
    kotlin_version: Optional[str] = None
    java_version: Optional[str] = None
    application_id: Optional[str] = None
    version_code: Optional[int] = None
    version_name: Optional[str] = None
    dependencies: List[Dependency] = field(default_factory=list)
    plugins: List[GradlePlugin] = field(default_factory=list)
    raw_content: str = ""


# Known vulnerable patterns {group:artifact: [bad_version_prefixes]}
_VULNERABLE_PATTERNS: Dict[str, List[str]] = {
    "log4j:log4j": ["1."],
    "org.apache.logging.log4j:log4j-core": ["2.0.", "2.1.", "2.2.", "2.3.", "2.4.",
                                              "2.5.", "2.6.", "2.7.", "2.8.", "2.9.",
                                              "2.10.", "2.11.", "2.12.", "2.13.", "2.14."],
}


class GradleBuildParser:
    """Parser for Gradle build files (build.gradle / build.gradle.kts)."""

    def __init__(self) -> None:
        self.build_config: Optional[BuildConfiguration] = None

    def parse_build_gradle_kts(self, build_file: Path) -> BuildConfiguration:
        config = BuildConfiguration(source_file=build_file)
        try:
            text = Path(build_file).read_text(encoding="utf-8")
        except OSError:
            return config
        config.raw_content = text
        for m in re.finditer(r'compileSdk\s*[=:]?\s*(\d+)', text):
            config.compile_sdk = int(m.group(1))
        for m in re.finditer(r'minSdk\s*[=:]?\s*(\d+)', text):
            config.min_sdk = int(m.group(1))
        for m in re.finditer(r'targetSdk\s*[=:]?\s*(\d+)', text):
            config.target_sdk = int(m.group(1))
        for m in re.finditer(r'kotlin[\s\S]*?(\d+\.\d+(?:\.\d+)?)', text):
            config.kotlin_version = m.group(1)
        for m in re.finditer(r'applicationId\s*=\s*[\x22\x27]([^\x22\x27]+)[\x22\x27]', text):
            config.application_id = m.group(1)
        for m in re.finditer(r'versionCode\s*[=]?\s*(\d+)', text):
            config.version_code = int(m.group(1))
        for m in re.finditer(r'versionName\s*=\s*[\x22\x27]([^\x22\x27]+)[\x22\x27]', text):
            config.version_name = m.group(1)
        config.dependencies = self.extract_dependencies(text)
        config.plugins = self.identify_plugins(text)
        self.build_config = config
        return config

    def extract_dependencies(self, text_or_config: Any = None) -> List[Dependency]:
        if text_or_config is None and self.build_config:
            text = self.build_config.raw_content
        elif isinstance(text_or_config, str):
            text = text_or_config
        elif isinstance(text_or_config, Path):
            text = text_or_config.read_text(encoding="utf-8")
        else:
            return []
        deps: List[Dependency] = []
        pattern = re.compile(
            r'(\w+)\s*\(\s*[\x22\x27]([\w.-]+):([\w.-]+)(?::([\w.+\-]+))?[\x22\x27]\s*\)'
        )
        for m in pattern.finditer(text):
            cfg, group, artifact, version = m.group(1), m.group(2), m.group(3), m.group(4)
            deps.append(Dependency(group=group, artifact=artifact,
                                   version=version, configuration=cfg))
        return deps

    def identify_plugins(self, text_or_config: Any = None) -> List[GradlePlugin]:
        if text_or_config is None and self.build_config:
            text = self.build_config.raw_content
        elif isinstance(text_or_config, str):
            text = text_or_config
        elif isinstance(text_or_config, Path):
            text = text_or_config.read_text(encoding="utf-8")
        else:
            return []
        plugins: List[GradlePlugin] = []
        _TYPE_MAP = {
            "com.android.application": PluginType.ANDROID_APPLICATION.value,
            "com.android.library": PluginType.ANDROID_LIBRARY.value,
            "org.jetbrains.kotlin.android": PluginType.KOTLIN_ANDROID.value,
            "org.jetbrains.kotlin.jvm": PluginType.KOTLIN_JVM.value,
            "org.jetbrains.kotlin.multiplatform": PluginType.KOTLIN_MULTIPLATFORM.value,
            "io.gitlab.arturbosch.detekt": PluginType.DETEKT.value,
            "org.jlleitschuh.gradle.ktlint": PluginType.KTLINT.value,
        }
        for m in re.finditer(r'id\s*\(\s*[\x22\x27]([^\x22\x27]+)[\x22\x27]\s*\)\s*version\s*[\x22\x27]([^\x22\x27]+)[\x22\x27]', text):
            pid, ver = m.group(1), m.group(2)
            ptype = _TYPE_MAP.get(pid, PluginType.OTHER.value)
            plugins.append(GradlePlugin(id=pid, version=ver, plugin_type=ptype))
        for m in re.finditer(r'id\s*\(\s*[\x22\x27]([^\x22\x27]+)[\x22\x27]\s*\)', text):
            pid = m.group(1)
            if not any(p.id == pid for p in plugins):
                plugins.append(GradlePlugin(id=pid, plugin_type=_TYPE_MAP.get(pid, PluginType.OTHER.value)))
        return plugins

    def parse_dependency_report(self, report_output: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for line in report_output.splitlines():
            m = re.search(r'[+\\]+---\s+([\w.-]+):([\w.-]+):([\w.+-]+)', line)
            if m:
                results.append({"group": m.group(1), "artifact": m.group(2), "version": m.group(3)})
        return results

    def analyze_build_performance(self, gradle_profiler_data: Dict[str, Any]) -> Dict[str, Any]:
        total = gradle_profiler_data.get("totalBuildTime", 0)
        tasks = gradle_profiler_data.get("tasks", {})
        sorted_tasks = sorted(tasks.items(), key=lambda x: x[1], reverse=True)
        return {
            "total_build_time": total,
            "task_count": len(tasks),
            "slowest_tasks": sorted_tasks[:5],
            "avg_task_time": (sum(tasks.values()) / len(tasks)) if tasks else 0,
        }

    def detect_dependency_vulnerabilities(self) -> List[Dict[str, Any]]:
        vulns: List[Dict[str, Any]] = []
        deps = self.build_config.dependencies if self.build_config else []
        for dep in deps:
            key = f"{dep.group}:{dep.artifact}"
            bad_prefixes = _VULNERABLE_PATTERNS.get(key, [])
            if dep.version and any(dep.version.startswith(p) for p in bad_prefixes):
                vulns.append({"dependency": str(dep), "group": dep.group,
                               "artifact": dep.artifact, "version": dep.version,
                               "severity": "high"})
        return vulns

    def generate_build_report(self, format: str = "json") -> str:
        if not self.build_config:
            return json.dumps({"error": "no config parsed"}) if format == "json" else "No config"
        bc = self.build_config
        vulns = self.detect_dependency_vulnerabilities()
        if format == "json":
            return json.dumps({
                "source": str(bc.source_file),
                "compile_sdk": bc.compile_sdk,
                "min_sdk": bc.min_sdk,
                "kotlin_version": bc.kotlin_version,
                "dependencies": len(bc.dependencies),
                "plugins": [p.id for p in bc.plugins],
                "vulnerabilities": vulns,
            }, indent=2)
        lines = ["Gradle Build Report",
                 f"  Compile SDK: {bc.compile_sdk}", f"  Min SDK: {bc.min_sdk}",
                 f"  Kotlin: {bc.kotlin_version}", f"  Deps: {len(bc.dependencies)}",
                 f"  Plugins: {[p.id for p in bc.plugins]}",
                 f"  Vulnerabilities: {len(vulns)}"]
        return "\n".join(lines)