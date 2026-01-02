#!/usr/bin/env python3
"""
ktlint Parser - Kotlin linter and formatter integration.

ktlint is an anti-bikeshedding Kotlin linter with built-in formatter.
It enforces the official Kotlin coding conventions and Android Kotlin Style Guide.

ktlint provides:
- Zero-configuration Kotlin linting
- Built-in code formatter
- Custom rule set support
- EditorConfig integration
- Baseline support

TODO: HIGH PRIORITY - Core Implementation
==========================================
[20251221_TODO] Implement JSON report parsing (ktlint --reporter=json)
[20251221_TODO] Implement plain text output parsing
[20251221_TODO] Implement SARIF report parsing
[20251221_TODO] Add violation extraction with rule IDs
[20251221_TODO] Add source location extraction (file, line, column)
[20251221_TODO] Add error message and detail extraction

TODO: HIGH PRIORITY - Execution
================================
[20251221_TODO] Add ktlint CLI execution via subprocess
[20251221_TODO] Add Gradle task execution support (ktlintCheck, ktlintFormat)
[20251221_TODO] Add format mode execution (--format flag)
[20251221_TODO] Add stdin support for code snippets
[20251221_TODO] Add incremental checking support

TODO: HIGH PRIORITY - Configuration
====================================
[20251221_TODO] Implement .editorconfig parsing for ktlint rules
[20251221_TODO] Add custom ruleset configuration
[20251221_TODO] Add disabled_rules parsing
[20251221_TODO] Add ktlint_* editorconfig property extraction
[20251221_TODO] Add baseline file parsing (.ktlint-baseline.xml)

TODO: MEDIUM PRIORITY - Standard Rules
=======================================
[20251221_TODO] Parse indentation rules (indent_size, indent_style)
[20251221_TODO] Parse import rules (no-wildcard-imports, no-unused-imports)
[20251221_TODO] Parse spacing rules (no-consecutive-blank-lines, no-trailing-spaces)
[20251221_TODO] Parse naming rules (package-name, class-naming)
[20251221_TODO] Parse wrapping rules (argument-list-wrapping, parameter-list-wrapping)
[20251221_TODO] Parse comment rules (comment-spacing)
[20251221_TODO] Parse string rules (no-multi-spaces, string-template)

TODO: MEDIUM PRIORITY - Experimental Rules
===========================================
[20251221_TODO] Track experimental rule status
[20251221_TODO] Add opt-in experimental rule support
[20251221_TODO] Parse function-signature rule
[20251221_TODO] Parse type-parameter-list-spacing rule
[20251221_TODO] Parse annotation rules

TODO: MEDIUM PRIORITY - Formatter
==================================
[20251221_TODO] Add format diff generation (before/after)
[20251221_TODO] Add dry-run format checking
[20251221_TODO] Track auto-fixable violations
[20251221_TODO] Generate format statistics

TODO: LOW PRIORITY - Advanced Features
=======================================
[20251221_TODO] Add custom rule loading (.kt ruleset files)
[20251221_TODO] Add rule documentation URL extraction
[20251221_TODO] Add Git pre-commit hook generation
[20251221_TODO] Add CI/CD integration helpers
[20251221_TODO] Add comparison with Detekt formatting rules
[20251221_TODO] Add migration helpers from other formatters
"""

import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class KtlintSeverity(Enum):
    """ktlint violation severity levels."""

    ERROR = "error"
    WARNING = "warning"


class KtlintRuleSet(Enum):
    """ktlint rule set categories."""

    STANDARD = "standard"
    EXPERIMENTAL = "experimental"
    CUSTOM = "custom"


@dataclass
class KtlintViolation:
    """Represents a single ktlint violation."""

    rule_id: str
    rule_set: str
    message: str
    severity: KtlintSeverity
    file_path: str
    line: int
    column: int
    can_be_auto_corrected: bool = False
    detail: Optional[str] = None

    @property
    def location(self) -> str:
        """Get formatted location string."""
        return f"{self.file_path}:{self.line}:{self.column}"

    @property
    def full_rule_id(self) -> str:
        """Get full rule ID including rule set."""
        return f"{self.rule_set}:{self.rule_id}"

    def get_docs_url(self) -> str:
        """Get documentation URL for the rule."""
        # ktlint standard rules documentation
        if self.rule_set == "standard":
            return f"https://pinterest.github.io/ktlint/latest/rules/standard/#{self.rule_id}"
        elif self.rule_set == "experimental":
            return f"https://pinterest.github.io/ktlint/latest/rules/experimental/#{self.rule_id}"
        return "https://pinterest.github.io/ktlint/latest/rules/"


@dataclass
class KtlintConfig:
    """ktlint configuration from .editorconfig."""

    # Indentation
    indent_size: int = 4
    indent_style: str = "space"  # "space" or "tab"

    # Max line length
    max_line_length: int = -1  # -1 means no limit

    # Disabled rules
    disabled_rules: list[str] = field(default_factory=list)

    # Experimental rules opt-in
    experimental_rules: bool = False

    # Android style
    android_style: bool = False

    # Code style
    code_style: str = "official"  # "official" or "android"

    # Additional ktlint-specific settings
    ktlint_settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class KtlintReport:
    """Complete ktlint analysis report."""

    violations: list[KtlintViolation] = field(default_factory=list)
    config: Optional[KtlintConfig] = None
    files_checked: int = 0
    execution_time_ms: Optional[float] = None
    ktlint_version: Optional[str] = None

    @property
    def error_count(self) -> int:
        """Count of errors."""
        return sum(1 for v in self.violations if v.severity == KtlintSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of warnings."""
        return sum(1 for v in self.violations if v.severity == KtlintSeverity.WARNING)

    @property
    def fixable_count(self) -> int:
        """Count of auto-fixable violations."""
        return sum(1 for v in self.violations if v.can_be_auto_corrected)

    @property
    def total_count(self) -> int:
        """Total violation count."""
        return len(self.violations)

    def by_rule(self) -> dict[str, list[KtlintViolation]]:
        """Group violations by rule ID."""
        result: dict[str, list[KtlintViolation]] = {}
        for violation in self.violations:
            key = violation.full_rule_id
            if key not in result:
                result[key] = []
            result[key].append(violation)
        return result

    def by_file(self) -> dict[str, list[KtlintViolation]]:
        """Group violations by file."""
        result: dict[str, list[KtlintViolation]] = {}
        for violation in self.violations:
            if violation.file_path not in result:
                result[violation.file_path] = []
            result[violation.file_path].append(violation)
        return result


class KtlintParser:
    """
    Parser for ktlint linter output.

    ktlint is a Kotlin linter and formatter. This parser can:
    - Parse ktlint JSON/text output
    - Execute ktlint via CLI
    - Parse .editorconfig for ktlint settings
    - Run formatter and generate diffs

    Example usage:
        parser = KtlintParser()

        # Parse existing report
        report = parser.parse_json_report('ktlint-report.json')

        # Run ktlint on files
        report = parser.check_file('src/main/kotlin/App.kt')

        # Format a file
        formatted = parser.format_file('src/main/kotlin/App.kt')

    TODO: Implement all parsing methods
    TODO: Add ktlint CLI execution
    TODO: Add EditorConfig parsing
    """

    def __init__(self, ktlint_path: Optional[str] = None):
        """
        Initialize ktlint parser.

        :param ktlint_path: Path to ktlint executable or jar.
        """
        self._ktlint_path = ktlint_path or self._find_ktlint()

    def _find_ktlint(self) -> Optional[str]:
        """Find ktlint executable."""
        # Check for ktlint in PATH
        ktlint = shutil.which("ktlint")
        if ktlint:
            return ktlint

        # Check for local installation
        local = Path("ktlint")
        if local.exists():
            return str(local)

        # Check for Gradle wrapper
        if Path("gradlew").exists():
            return "./gradlew"

        return None

    def parse_json_report(self, json_path: str) -> KtlintReport:
        """
        Parse ktlint JSON report.

        :param json_path: Path to ktlint JSON report.
        :return: KtlintReport with violations.

        TODO: Implement JSON parsing
        """
        raise NotImplementedError("JSON report parsing not yet implemented")

    def parse_json_output(self, json_output: str) -> KtlintReport:
        """
        Parse ktlint JSON output string.

        :param json_output: ktlint JSON output.
        :return: KtlintReport with violations.

        TODO: Implement JSON output parsing
        """
        raise NotImplementedError("JSON output parsing not yet implemented")

    def parse_text_output(self, text: str) -> KtlintReport:
        """
        Parse ktlint plain text output.

        :param text: ktlint plain text output.
        :return: KtlintReport with violations.

        TODO: Implement text parsing
        """
        raise NotImplementedError("Text output parsing not yet implemented")

    def parse_editorconfig(self, config_path: str = ".editorconfig") -> KtlintConfig:
        """
        Parse .editorconfig for ktlint settings.

        :param config_path: Path to .editorconfig.
        :return: KtlintConfig object.

        TODO: Implement EditorConfig parsing
        """
        raise NotImplementedError("EditorConfig parsing not yet implemented")

    def check_file(
        self,
        file_path: str,
        config_path: Optional[str] = None,
    ) -> KtlintReport:
        """
        Run ktlint on a single file.

        :param file_path: Path to Kotlin file.
        :param config_path: Optional path to .editorconfig.
        :return: KtlintReport with violations.

        TODO: Implement file checking
        """
        raise NotImplementedError("File checking not yet implemented")

    def check_code(
        self,
        code: str,
        filename: str = "input.kt",
    ) -> KtlintReport:
        """
        Run ktlint on code string via stdin.

        :param code: Kotlin source code.
        :param filename: Virtual filename for reporting.
        :return: KtlintReport with violations.

        TODO: Implement code checking via stdin
        """
        raise NotImplementedError("Code checking not yet implemented")

    def check_directory(
        self,
        directory: str,
        patterns: Optional[list[str]] = None,
    ) -> KtlintReport:
        """
        Run ktlint on a directory.

        :param directory: Path to directory.
        :param patterns: Optional glob patterns to include.
        :return: KtlintReport with violations.

        TODO: Implement directory checking
        """
        raise NotImplementedError("Directory checking not yet implemented")

    def format_file(
        self,
        file_path: str,
        dry_run: bool = False,
    ) -> tuple[str, bool]:
        """
        Format a Kotlin file.

        :param file_path: Path to Kotlin file.
        :param dry_run: If True, don't write changes.
        :return: Tuple of (formatted_code, was_modified).

        TODO: Implement file formatting
        """
        raise NotImplementedError("File formatting not yet implemented")

    def format_code(self, code: str) -> tuple[str, bool]:
        """
        Format Kotlin code string.

        :param code: Kotlin source code.
        :return: Tuple of (formatted_code, was_modified).

        TODO: Implement code formatting
        """
        raise NotImplementedError("Code formatting not yet implemented")

    def get_fixable_violations(self, report: KtlintReport) -> list[KtlintViolation]:
        """Get violations that can be auto-fixed."""
        return [v for v in report.violations if v.can_be_auto_corrected]

    def generate_baseline(
        self,
        directory: str,
        output_path: str = ".ktlint-baseline.xml",
    ) -> str:
        """
        Generate a baseline file for existing violations.

        :param directory: Directory to analyze.
        :param output_path: Output path for baseline file.
        :return: Path to generated baseline file.

        TODO: Implement baseline generation
        """
        raise NotImplementedError("Baseline generation not yet implemented")
