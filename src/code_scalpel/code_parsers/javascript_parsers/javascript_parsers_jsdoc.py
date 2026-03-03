#!/usr/bin/env python3
# [20260303_FEATURE] Complete implementation of JSDoc parser (was stub)
"""
JSDoc JavaScript Parser - JSDoc comment analysis and coverage.

Reference: https://jsdoc.app/
Command: jsdoc -X (outputs JSON)

Provides pure-Python JSDoc extraction via regex and optional jsdoc -X output
parsing.  No external tool installation required for the regex-based methods.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

# Regex: capture the doc-block body AND the following exported symbol name.
# Flags: re.DOTALL so `.` matches newlines inside the comment.
_JSDOC_RE = re.compile(
    r"/\*\*(.*?)\*/\s*(?:export\s+)?(?:async\s+)?(?:function|const|class)\s+(\w+)",
    re.DOTALL,
)

# Simplified regex for undocumented exports / functions (no preceding /** */)
_EXPORT_RE = re.compile(
    r"(?:^|\n)(?:export\s+)?(?:async\s+)?(?:function|const|class)\s+(\w+)"
)
_TAG_RE = re.compile(r"@(\w+)(?:\s+\{([^}]*)\})?(?:\s+(\S+))?(?:\s+(.+))?", re.MULTILINE)


@dataclass
class JsDocComment:
    """Parsed JSDoc comment block."""

    # [20260303_FEATURE] Dataclass matching Stage 4b specification
    description: str
    tags: list[dict] = field(default_factory=list)
    file_path: str = ""
    line: int = 0


class JsDocParser:
    """Pure-Python JSDoc comment extractor and coverage analyser.

    All regex-based methods work without any external tools.
    ``parse_jsdoc_json`` parses output from ``jsdoc -X`` if available.
    """

    # [20260303_FEATURE] Complete parser implementation

    def __init__(self) -> None:
        """Initialise JsDocParser."""
        pass

    # ------------------------------------------------------------------
    # Pure-Python / regex methods
    # ------------------------------------------------------------------

    def extract_jsdoc_comments(self, code: str) -> list[JsDocComment]:
        """Extract JSDoc comment blocks from *code* using regex.

        Finds ``/** ... */`` blocks immediately preceding a function, const,
        or class declaration (including ``export`` / ``async`` prefixes).

        Args:
            code: JavaScript or TypeScript source code as a string.

        Returns:
            List of JsDocComment objects in order of appearance.
        """
        results: list[JsDocComment] = []
        for match in _JSDOC_RE.finditer(code):
            raw_body = match.group(1)
            # Strip leading « * » from each line (standard JSDoc formatting)
            lines = [ln.strip().lstrip("*").strip() for ln in raw_body.splitlines()]
            # First non-empty, non-tag line is the description
            description_lines: list[str] = []
            tags: list[dict] = []
            for line in lines:
                if line.startswith("@"):
                    break
                if line:
                    description_lines.append(line)
            description = " ".join(description_lines)

            # Parse @tags from the raw body
            for tag_match in _TAG_RE.finditer(raw_body):
                tag_name = tag_match.group(1)
                type_str = (tag_match.group(2) or "").strip()
                name_str = (tag_match.group(3) or "").strip()
                desc_str = (tag_match.group(4) or "").strip()
                entry: dict[str, str] = {"tag": tag_name}
                if type_str:
                    entry["type"] = type_str
                if name_str:
                    entry["name"] = name_str
                if desc_str:
                    entry["description"] = desc_str
                tags.append(entry)

            # Approximate line number by counting newlines before match start
            line_number = code[: match.start()].count("\n") + 1
            results.append(JsDocComment(description=description, tags=tags, line=line_number))
        return results

    def parse_jsdoc_json(self, output: str) -> list[JsDocComment]:
        """Parse ``jsdoc -X`` JSON output.

        ``jsdoc -X`` emits a JSON array where each element has at least:
        ``comment``, ``meta.filename``, and ``meta.lineno``.

        Args:
            output: Raw JSON string produced by ``jsdoc -X``.

        Returns:
            List of JsDocComment objects.
        """
        try:
            items: list[dict[str, Any]] = json.loads(output)
        except (json.JSONDecodeError, TypeError):
            return []

        results: list[JsDocComment] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            raw_comment: str = item.get("comment", "")
            meta: dict[str, Any] = item.get("meta", {})
            file_path = str(meta.get("filename", ""))
            line = int(meta.get("lineno", 0) or 0)

            # Strip /** and */ delimiters then extract description + tags
            inner = raw_comment.strip()
            if inner.startswith("/**"):
                inner = inner[3:]
            if inner.endswith("*/"):
                inner = inner[:-2]

            lines = [ln.strip().lstrip("*").strip() for ln in inner.splitlines()]
            description_lines: list[str] = []
            tags: list[dict] = []
            in_desc = True
            for line_text in lines:
                if line_text.startswith("@"):
                    in_desc = False
                if in_desc:
                    if line_text:
                        description_lines.append(line_text)
                else:
                    tag_m = _TAG_RE.match(line_text)
                    if tag_m:
                        entry: dict[str, str] = {"tag": tag_m.group(1)}
                        if tag_m.group(2):
                            entry["type"] = tag_m.group(2).strip()
                        if tag_m.group(3):
                            entry["name"] = tag_m.group(3).strip()
                        if tag_m.group(4):
                            entry["description"] = tag_m.group(4).strip()
                        tags.append(entry)

            results.append(
                JsDocComment(
                    description=" ".join(description_lines),
                    tags=tags,
                    file_path=file_path,
                    line=line,
                )
            )
        return results

    def get_documentation_coverage(self, code: str) -> dict[str, Any]:
        """Compute JSDoc coverage for *code*.

        Counts all top-level function/const/class declarations and how many
        are preceded by a JSDoc block.

        Args:
            code: JavaScript or TypeScript source code.

        Returns:
            Dict with ``total_functions``, ``documented``, and
            ``coverage_pct`` (0.0 – 100.0).
        """
        all_symbols = set(_EXPORT_RE.findall(code))
        documented_symbols = set()
        for match in _JSDOC_RE.finditer(code):
            documented_symbols.add(match.group(2))

        total = len(all_symbols)
        documented = len(documented_symbols & all_symbols)
        coverage_pct = (documented / total * 100.0) if total else 0.0
        return {
            "total_functions": total,
            "documented": documented,
            "coverage_pct": round(coverage_pct, 2),
        }

    def list_undocumented_exports(self, code: str) -> list[str]:
        """Return export/function names that lack JSDoc documentation.

        Args:
            code: JavaScript or TypeScript source code.

        Returns:
            List of symbol names without a preceding JSDoc block.
        """
        all_symbols = set(_EXPORT_RE.findall(code))
        documented_symbols = {match.group(2) for match in _JSDOC_RE.finditer(code)}
        return sorted(all_symbols - documented_symbols)

    def generate_report(self, data: Any, format: str = "json") -> str:
        """Generate a structured JSDoc report.

        Args:
            data: A list of JsDocComment objects, or a coverage dict, or any
                  other serialisable value.
            format: Output format (currently only "json" is supported).

        Returns:
            JSON string with tool name and provided data.
        """
        if isinstance(data, list):
            serialised: Any = [
                {
                    "description": c.description,
                    "tags": c.tags,
                    "file_path": c.file_path,
                    "line": c.line,
                }
                for c in data
                if isinstance(c, JsDocComment)
            ]
        else:
            serialised = data
        report = {"tool": "jsdoc", "data": serialised}
        return json.dumps(report, indent=2)
