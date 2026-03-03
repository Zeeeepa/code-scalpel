#!/usr/bin/env python3
# [20260303_FEATURE] Complete implementation of webpack config parser (was stub)
"""
Webpack JavaScript Parser - Static analysis of webpack configuration files.

Reference: https://webpack.js.org/configuration/

All analysis is performed via regex heuristics on the config file text.
No webpack installation or execution is required.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ----- Regex patterns for heuristic config extraction -----

# entry: './src/index.js'  or  entry: "src/index"
_ENTRY_STRING_RE = re.compile(r"entry\s*:\s*['\"]([^'\"]+)['\"]")
# entry: { main: './src/main.js', app: './src/app.js' }
_ENTRY_OBJECT_RE = re.compile(
    r"entry\s*:\s*\{([^}]+)\}", re.DOTALL
)
_ENTRY_OBJECT_VALUE_RE = re.compile(r":\s*['\"]([^'\"]+)['\"]")

# resolve.alias: { '@': path.resolve(..., 'src') }
_ALIAS_BLOCK_RE = re.compile(r"alias\s*:\s*\{([^}]+)\}", re.DOTALL)
_ALIAS_KV_RE = re.compile(r"['\"]?([\w@/.-]+)['\"]?\s*:\s*[^,\n}]+")

# rules: [{ test: /\.jsx?$/, use: 'babel-loader' }]
_RULE_USE_RE = re.compile(
    r"use\s*:\s*(?:['\"]([^'\"]+)['\"]|\[([^\]]+)\]|\{[^}]*loader\s*:\s*['\"]([^'\"]+)['\"])"
)
_RULE_LOADER_RE = re.compile(r"loader\s*:\s*['\"]([^'\"]+)['\"]")

# output.path
_OUTPUT_PATH_RE = re.compile(
    r"output\s*:\s*\{[^}]*path\s*:[^,}]+['\"]([^'\"]+)['\"][^}]*\}",
    re.DOTALL,
)

# mode: 'production' | 'development'
_MODE_RE = re.compile(r"mode\s*:\s*['\"]([^'\"]+)['\"]")

# Known optimisation / utility plugin names
_KNOWN_PLUGINS = [
    "TerserPlugin",
    "MiniCssExtractPlugin",
    "HtmlWebpackPlugin",
    "DefinePlugin",
    "HotModuleReplacementPlugin",
    "CopyWebpackPlugin",
    "CleanWebpackPlugin",
    "BundleAnalyzerPlugin",
    "CompressionPlugin",
    "DllPlugin",
    "DllReferencePlugin",
    "ProvidePlugin",
    "EnvironmentPlugin",
    "SourceMapDevToolPlugin",
    "SplitChunksPlugin",
    "ModuleFederationPlugin",
]


@dataclass
class WebpackConfig:
    """Extracted information from a webpack configuration file."""

    # [20260303_FEATURE] Dataclass matching Stage 4b specification
    entry_points: list[str] = field(default_factory=list)
    aliases: dict = field(default_factory=dict)
    loaders: list[str] = field(default_factory=list)
    plugins: list[str] = field(default_factory=list)
    output_path: str = ""
    mode: str = "production"


class WebpackConfigParser:
    """Heuristic static analyser for webpack.config.js / webpack.config.ts.

    All methods parse the raw text of the config file with regex; no Node.js
    or webpack installation is required.
    """

    # [20260303_FEATURE] Complete parser implementation

    def __init__(self) -> None:
        """Initialise WebpackConfigParser."""
        pass

    def parse_webpack_config(self, path: str | Path) -> WebpackConfig:
        """Read *path* and extract webpack configuration via heuristics.

        Args:
            path: Path to ``webpack.config.js`` or ``webpack.config.ts``.

        Returns:
            WebpackConfig dataclass populated with extracted values.

        Raises:
            FileNotFoundError: If *path* does not exist.
        """
        config_text = Path(path).read_text(encoding="utf-8")
        return WebpackConfig(
            entry_points=self.extract_entry_points(config_text),
            aliases=self.extract_aliases(config_text),
            loaders=self.extract_loaders(config_text),
            plugins=self.detect_optimization_plugins(config_text),
            output_path=self._extract_output_path(config_text),
            mode=self._extract_mode(config_text),
        )

    # ------------------------------------------------------------------
    # Sub-extractors
    # ------------------------------------------------------------------

    def extract_entry_points(self, config_text: str) -> list[str]:
        """Extract webpack entry point paths from *config_text*.

        Handles both string (``entry: './src/index.js'``) and
        object (``entry: { main: './src/main.js' }``) forms.

        Args:
            config_text: Raw text of the webpack config file.

        Returns:
            List of entry point path strings (de-duplicated, preserving order).
        """
        entries: list[str] = []
        seen: set[str] = set()

        # String form first
        for m in _ENTRY_STRING_RE.finditer(config_text):
            val = m.group(1)
            if val not in seen:
                seen.add(val)
                entries.append(val)

        # Object form
        obj_match = _ENTRY_OBJECT_RE.search(config_text)
        if obj_match:
            block = obj_match.group(1)
            for vm in _ENTRY_OBJECT_VALUE_RE.finditer(block):
                val = vm.group(1)
                if val not in seen:
                    seen.add(val)
                    entries.append(val)

        return entries

    def extract_aliases(self, config_text: str) -> dict[str, str]:
        """Extract ``resolve.alias`` entries from *config_text*.

        Args:
            config_text: Raw text of the webpack config file.

        Returns:
            Dict mapping alias key to its (raw) value string.
        """
        alias_match = _ALIAS_BLOCK_RE.search(config_text)
        if not alias_match:
            return {}
        block = alias_match.group(1)
        aliases: dict[str, str] = {}
        for kvm in _ALIAS_KV_RE.finditer(block):
            key = kvm.group(1).strip(" '\"")
            # Extract the first quoted value on the RHS if present
            raw = kvm.group(0)
            val_match = re.search(r":\s*.*?['\"]([^'\"]+)['\"]$", raw)
            if val_match:
                aliases[key] = val_match.group(1)
            else:
                aliases[key] = raw.split(":", 1)[-1].strip()
        return aliases

    def extract_loaders(self, config_text: str) -> list[str]:
        """Extract loader names from ``module.rules`` in *config_text*.

        Args:
            config_text: Raw text of the webpack config file.

        Returns:
            Sorted, de-duplicated list of loader name strings.
        """
        loaders: set[str] = set()
        # use: 'babel-loader' or use: ['style-loader', 'css-loader']
        for m in _RULE_USE_RE.finditer(config_text):
            single = m.group(1)
            multi = m.group(2)
            loader_in_obj = m.group(3)
            if single:
                loaders.add(single)
            if multi:
                for item in re.findall(r"['\"]([^'\"]+)['\"]" ,multi):
                    loaders.add(item)
            if loader_in_obj:
                loaders.add(loader_in_obj)
        # loader: 'file-loader' (inside rule objects)
        for m in _RULE_LOADER_RE.finditer(config_text):
            loaders.add(m.group(1))
        return sorted(loaders)

    def detect_optimization_plugins(self, config_text: str) -> list[str]:
        """Detect known optimisation/utility plugins mentioned in *config_text*.

        Args:
            config_text: Raw text of the webpack config file.

        Returns:
            List of recognised plugin names that appear in the config.
        """
        found: list[str] = []
        for plugin in _KNOWN_PLUGINS:
            if plugin in config_text:
                found.append(plugin)
        return found

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_output_path(self, config_text: str) -> str:
        m = _OUTPUT_PATH_RE.search(config_text)
        return m.group(1) if m else ""

    def _extract_mode(self, config_text: str) -> str:
        m = _MODE_RE.search(config_text)
        return m.group(1) if m else "production"

    def generate_report(self, config: WebpackConfig, format: str = "json") -> str:
        """Generate a structured webpack config report.

        Args:
            config: A WebpackConfig instance.
            format: Output format (currently only "json" is supported).

        Returns:
            JSON string with tool name and extracted config information.
        """
        report: dict[str, Any] = {
            "tool": "webpack",
            "mode": config.mode,
            "output_path": config.output_path,
            "entry_points": config.entry_points,
            "aliases": config.aliases,
            "loaders": config.loaders,
            "plugins": config.plugins,
        }
        return json.dumps(report, indent=2)


# Convenience alias so the module is self-consistent with Stage 4b naming
WebpackParser = WebpackConfigParser
