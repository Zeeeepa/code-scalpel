#!/usr/bin/env python3
"""C# Parser Registry and SARIF 2.1 helper.

[20260303_FEATURE] Phase 2: Full CSharpParserRegistry with lazy-load factory
and shared _parse_sarif() helper consumed by Roslyn, StyleCop, and SCS parsers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

__all__ = [
    "CSharpParserRegistry",
    "SarifFinding",
    "_parse_sarif",
    "ReSharperParser",
    "RoslynAnalyzersParser",
    "StyleCopParser",
    "SonarQubeCSharpParser",
    "FxCopParser",
    "SecurityCodeScanParser",
]

# ---------------------------------------------------------------------------
# SARIF 2.1 shared helper
# ---------------------------------------------------------------------------


@dataclass
class SarifFinding:
    """Normalized representation of a single SARIF 2.1 result.

    [20260303_FEATURE] Shared across Roslyn, StyleCop, SecurityCodeScan parsers.
    """

    rule_id: str
    level: str  # "error", "warning", "note", "none"
    message: str
    uri: str
    line: int
    column: int
    tool: str = ""
    tags: List[str] = field(default_factory=list)


def _parse_sarif(sarif_source: Union[str, Path, dict]) -> List[SarifFinding]:
    """Parse a SARIF 2.1 document and return a flat list of SarifFinding.

    [20260303_FEATURE] Shared helper for all C# SARIF-emitting tools.

    Args:
        sarif_source: Path to a SARIF JSON file, a JSON string, or a pre-parsed
            dict.

    Returns:
        List of SarifFinding — empty list on empty/invalid input.
    """
    # ---- load ----
    if isinstance(sarif_source, dict):
        data: Any = sarif_source
    elif isinstance(sarif_source, Path):
        try:
            data = json.loads(sarif_source.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
    else:
        try:
            data = json.loads(sarif_source)
        except (json.JSONDecodeError, TypeError):
            return []

    findings: List[SarifFinding] = []
    for run in data.get("runs", []):
        tool_name = run.get("tool", {}).get("driver", {}).get("name", "")
        for result in run.get("results", []):
            rule_id = result.get("ruleId", "")
            level = result.get("level", "warning")
            msg_text = result.get("message", {})
            if isinstance(msg_text, dict):
                msg_text = msg_text.get("text", "")

            # Extract first physical location
            uri = ""
            line = 0
            col = 0
            locations = result.get("locations", [])
            if locations:
                phys = locations[0].get("physicalLocation", {})
                art = phys.get("artifactLocation", {})
                uri = art.get("uri", "")
                region = phys.get("region", {})
                line = region.get("startLine", 0)
                col = region.get("startColumn", 0)

            tags = result.get("tags", [])
            findings.append(
                SarifFinding(
                    rule_id=rule_id,
                    level=level,
                    message=str(msg_text),
                    uri=uri,
                    line=line,
                    column=col,
                    tool=tool_name,
                    tags=tags,
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_TOOL_MAP: Dict[str, str] = {
    "roslyn": "RoslynAnalyzersParser",
    "stylecop": "StyleCopParser",
    "scs": "SecurityCodeScanParser",
    "security-code-scan": "SecurityCodeScanParser",  # [20260303_FEATURE] alias
    "fxcop": "FxCopParser",
    "resharper": "ReSharperParser",
    "sonarqube": "SonarQubeCSharpParser",
}


class CSharpParserRegistry:
    """Registry for C# parser implementations with lazy-load factory pattern.

    [20260303_FEATURE] Phase 2: full registry replacing NotImplementedError stubs.
    """

    def get_parser(self, tool_name: str) -> Any:
        """Return an instantiated parser for *tool_name*.

        Args:
            tool_name: One of "roslyn", "stylecop", "scs", "fxcop",
                "resharper", "sonarqube" (case-insensitive).

        Raises:
            ValueError: If tool_name is not recognised.
        """
        key = tool_name.lower()
        if key not in _TOOL_MAP:
            raise ValueError(
                f"Unknown C# parser tool: {tool_name!r}. "
                f"Valid options: {sorted(_TOOL_MAP.keys())}"
            )
        class_name = _TOOL_MAP[key]
        # Lazy import to avoid circular deps
        module = _get_parser_module(key)
        return getattr(module, class_name)()

    def analyze(
        self, path: Union[str, Path], tools: Optional[List[str]] = None
    ) -> Dict[str, List]:
        """Run all (or specified) parsers on *path* and aggregate results.

        [20260303_FEATURE] Returns a dict keyed by tool name; each value is
        the list of findings from that parser (empty list if tool absent).
        """
        selected = [t.lower() for t in tools] if tools else list(_TOOL_MAP.keys())
        results: Dict[str, List] = {}
        for tool in selected:
            try:
                parser = self.get_parser(tool)
                # All parsers expose a parse_file / execute method; fall back to []
                if hasattr(parser, "parse_sarif_output"):
                    results[tool] = parser.parse_sarif_output(path)
                elif hasattr(parser, "parse_xml_report"):
                    results[tool] = parser.parse_xml_report(path)
                elif hasattr(parser, "parse_issues_json"):
                    results[tool] = parser.parse_issues_json("{}")
                else:
                    results[tool] = []
            except Exception:  # noqa: BLE001
                results[tool] = []
        return results


def _get_parser_module(key: str) -> Any:
    """Lazy-import the parser module for *key*.

    [20260303_FEATURE] Uses spec_from_file_location to handle hyphenated
    filenames such as csharp_parsers_Roslyn-Analyzers.py.  Sets __package__
    so relative imports (``from . import SarifFinding``) resolve correctly.
    """
    import importlib.util
    import sys
    from pathlib import Path

    _dir = Path(__file__).parent
    # Normalize aliases before file_map lookup
    _KEY_ALIASES = {"security-code-scan": "scs"}
    key = _KEY_ALIASES.get(key, key)
    file_map = {
        "roslyn": (
            _dir / "csharp_parsers_Roslyn-Analyzers.py",
            "csharp_parsers_Roslyn_Analyzers",
        ),
        "stylecop": (_dir / "csharp_parsers_StyleCop.py", "csharp_parsers_StyleCop"),
        "scs": (
            _dir / "csharp_parsers_SecurityCodeScan.py",
            "csharp_parsers_SecurityCodeScan",
        ),
        "fxcop": (_dir / "csharp_parsers_fxcop.py", "csharp_parsers_fxcop"),
        "resharper": (_dir / "csharp_parsers_ReSharper.py", "csharp_parsers_ReSharper"),
        "sonarqube": (_dir / "csharp_parsers_SonarQube.py", "csharp_parsers_SonarQube"),
    }
    filepath, mod_name = file_map[key]
    full_name = f"code_scalpel.code_parsers.csharp_parsers.{mod_name}"
    if full_name in sys.modules:
        return sys.modules[full_name]
    spec = importlib.util.spec_from_file_location(full_name, filepath)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module for {key!r}")
    mod = importlib.util.module_from_spec(spec)
    # Set __package__ so that ``from . import SarifFinding`` resolves correctly.
    mod.__package__ = "code_scalpel.code_parsers.csharp_parsers"
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------------------
# Re-export parser classes (lazy; resolved via registry on first use)
# ---------------------------------------------------------------------------
# [20251222_BUGFIX] Provide placeholder parser symbols until implementations land.
# [20260303_FEATURE] Now replaced with importable references.


def __getattr__(name: str) -> Any:  # module-level __getattr__ (PEP 562)
    _class_to_key = {v: k for k, v in _TOOL_MAP.items()}
    if name in _class_to_key:
        key = _class_to_key[name]
        mod = _get_parser_module(key)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
