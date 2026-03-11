#!/usr/bin/env python3
"""Tests for PHP tool parsers — Phase 2 implementations.

[20260304_TEST] Comprehensive fixture-based tests for all 7 PHP parsers.
No external PHP tools need to be installed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Lazy import helpers (follow test_kotlin_tool_parsers.py pattern)
# ---------------------------------------------------------------------------


def _import_phpcs():
    from code_scalpel.code_parsers.php_parsers.php_parsers_PHPCS import (
        PHPCSParser,
        PHPCSViolation,
        PHPCSSeverity,
        PHPCSStandard,
        PHPCSConfig,
    )

    return PHPCSParser, PHPCSViolation, PHPCSSeverity, PHPCSStandard, PHPCSConfig


def _import_phpstan():
    from code_scalpel.code_parsers.php_parsers.php_parsers_PHPStan import (
        PHPStanParser,
        PHPStanError,
        PHPStanLevel,
        PHPStanErrorType,
        PHPStanConfig,
    )

    return PHPStanParser, PHPStanError, PHPStanLevel, PHPStanErrorType, PHPStanConfig


def _import_psalm():
    from code_scalpel.code_parsers.php_parsers.php_parsers_Psalm import (
        PsalmParser,
        PsalmError,
        PsalmSeverity,
        PsalmErrorType,
        PsalmConfig,
    )

    return PsalmParser, PsalmError, PsalmSeverity, PsalmErrorType, PsalmConfig


def _import_phpmd():
    from code_scalpel.code_parsers.php_parsers.php_parsers_phpmd import (
        PHPMDParser,
        PHPMDViolation,
        PHPMDPriority,
        PHPMDRuleType,
        PHPMDConfig,
    )

    return PHPMDParser, PHPMDViolation, PHPMDPriority, PHPMDRuleType, PHPMDConfig


def _import_ast():
    from code_scalpel.code_parsers.php_parsers.php_parsers_ast import (
        PHPParserAST,
        PHPClass,
        PHPFunction,
    )

    return PHPParserAST, PHPClass, PHPFunction


def _import_composer():
    from code_scalpel.code_parsers.php_parsers.php_parsers_composer import (
        ComposerParser,
        ComposerPackage,
        ComposerConfig,
    )

    return ComposerParser, ComposerPackage, ComposerConfig


def _import_exakat():
    from code_scalpel.code_parsers.php_parsers.php_parsers_exakat import (
        ExakatParser,
        ExakatIssue,
        ExakatCategory,
    )

    return ExakatParser, ExakatIssue, ExakatCategory


# ===========================================================================
# Module exports
# ===========================================================================


@pytest.mark.parametrize(
    "symbol,module_path",
    [
        ("PHPCSParser", "code_scalpel.code_parsers.php_parsers.php_parsers_PHPCS"),
        ("PHPCSViolation", "code_scalpel.code_parsers.php_parsers.php_parsers_PHPCS"),
        ("PHPStanParser", "code_scalpel.code_parsers.php_parsers.php_parsers_PHPStan"),
        ("PHPStanError", "code_scalpel.code_parsers.php_parsers.php_parsers_PHPStan"),
        ("PsalmParser", "code_scalpel.code_parsers.php_parsers.php_parsers_Psalm"),
        ("PsalmError", "code_scalpel.code_parsers.php_parsers.php_parsers_Psalm"),
        ("PHPMDParser", "code_scalpel.code_parsers.php_parsers.php_parsers_phpmd"),
        ("PHPMDViolation", "code_scalpel.code_parsers.php_parsers.php_parsers_phpmd"),
        ("PHPParserAST", "code_scalpel.code_parsers.php_parsers.php_parsers_ast"),
        ("PHPClass", "code_scalpel.code_parsers.php_parsers.php_parsers_ast"),
        (
            "ComposerParser",
            "code_scalpel.code_parsers.php_parsers.php_parsers_composer",
        ),
        (
            "ComposerPackage",
            "code_scalpel.code_parsers.php_parsers.php_parsers_composer",
        ),
        ("ExakatParser", "code_scalpel.code_parsers.php_parsers.php_parsers_exakat"),
        ("ExakatIssue", "code_scalpel.code_parsers.php_parsers.php_parsers_exakat"),
    ],
)
def test_module_exports(symbol: str, module_path: str) -> None:
    """All expected symbols should be importable from their modules."""
    import importlib

    mod = importlib.import_module(module_path)
    assert hasattr(mod, symbol), f"{symbol} not found in {module_path}"


def test_package_all_exports() -> None:
    """Package __all__ should expose all 7 parsers."""
    from code_scalpel.code_parsers.php_parsers import __all__  # type: ignore

    expected = {
        "PHPCSParser",
        "PHPStanParser",
        "PsalmParser",
        "PHPMDParser",
        "PHPParserAST",
        "ComposerParser",
        "ExakatParser",
    }
    assert expected.issubset(set(__all__))


# ===========================================================================
# PHPStan
# ===========================================================================


class TestPHPStanParser:
    """Tests for PHPStanParser (type checker, JSON output)."""

    def test_parse_empty_returns_empty(self) -> None:
        PHPStanParser, *_ = _import_phpstan()
        p = PHPStanParser()
        assert p.parse_json_report("") == []

    def test_parse_invalid_json_returns_empty(self) -> None:
        PHPStanParser, *_ = _import_phpstan()
        p = PHPStanParser()
        assert p.parse_json_report("not json") == []

    def test_parse_valid_json(self) -> None:
        PHPStanParser, PHPStanError, _, PHPStanErrorType, _ = _import_phpstan()
        payload = {
            "totals": {"errors": 1, "file_errors": 1},
            "files": {
                "src/Foo.php": {
                    "errors": 1,
                    "messages": [
                        {
                            "message": "Undefined variable: $x",
                            "line": 10,
                            "ignorable": True,
                        }
                    ],
                }
            },
            "errors": [],
        }
        p = PHPStanParser()
        errors = p.parse_json_report(json.dumps(payload))
        assert len(errors) == 1
        assert errors[0].file_path == "src/Foo.php"
        assert errors[0].line_number == 10
        assert "Undefined variable" in errors[0].message

    def test_error_type_inference_undefined(self) -> None:
        PHPStanParser, _, _, PHPStanErrorType, _ = _import_phpstan()
        from code_scalpel.code_parsers.php_parsers.php_parsers_PHPStan import (
            _infer_error_type,
        )

        assert (
            _infer_error_type("Undefined variable: $x")
            == PHPStanErrorType.UNDEFINED.value
        )

    def test_error_type_inference_type_error(self) -> None:
        from code_scalpel.code_parsers.php_parsers.php_parsers_PHPStan import (
            _infer_error_type,
        )

        _, _, _, PHPStanErrorType, _ = _import_phpstan()
        assert (
            _infer_error_type("Parameter does not accept type int")
            == PHPStanErrorType.TYPE_ERROR.value
        )

    def test_cwe_inferred_for_null(self) -> None:
        from code_scalpel.code_parsers.php_parsers.php_parsers_PHPStan import _infer_cwe

        cwe = _infer_cwe("Cannot access null offset")
        assert cwe == "CWE-476"

    def test_cwe_none_for_generic(self) -> None:
        from code_scalpel.code_parsers.php_parsers.php_parsers_PHPStan import _infer_cwe

        assert _infer_cwe("Method signature mismatch") is None

    def test_categorize_by_type(self) -> None:
        PHPStanParser, PHPStanError, _, PHPStanErrorType, _ = _import_phpstan()
        p = PHPStanParser()
        errors = [
            PHPStanError(message="a", error_type=PHPStanErrorType.TYPE_ERROR.value),
            PHPStanError(message="b", error_type=PHPStanErrorType.UNDEFINED.value),
            PHPStanError(message="c", error_type=PHPStanErrorType.TYPE_ERROR.value),
        ]
        grouped = p.categorize_by_type(errors)
        assert len(grouped[PHPStanErrorType.TYPE_ERROR.value]) == 2
        assert len(grouped[PHPStanErrorType.UNDEFINED.value]) == 1

    def test_generate_report_json(self) -> None:
        PHPStanParser, PHPStanError, _, PHPStanErrorType, _ = _import_phpstan()
        p = PHPStanParser()
        errors = [
            PHPStanError(
                message="Null offset",
                file_path="a.php",
                line_number=5,
                error_type=PHPStanErrorType.TYPE_ERROR.value,
            )
        ]
        report = p.generate_report(errors, fmt="json")
        data = json.loads(report)
        assert data["tool"] == "phpstan"
        assert data["total_errors"] == 1

    def test_generate_report_text(self) -> None:
        PHPStanParser, PHPStanError, _, _t, _ = _import_phpstan()
        p = PHPStanParser()
        errors = [PHPStanError(message="Oops", file_path="b.php", line_number=3)]
        report = p.generate_report(errors, fmt="text")
        assert "b.php" in report
        assert "Oops" in report

    def test_execute_phpstan_returns_empty_when_missing(self) -> None:
        """Should return [] gracefully when phpstan is not installed."""
        PHPStanParser, *_ = _import_phpstan()
        # If phpstan IS present this will actually run; we mock shutil.which
        import unittest.mock as mock

        with mock.patch(
            "code_scalpel.code_parsers.php_parsers.php_parsers_PHPStan.shutil.which",
            return_value=None,
        ):
            p = PHPStanParser()
            assert p.execute_phpstan() == []


# ===========================================================================
# PHPCS
# ===========================================================================


class TestPHPCSParser:
    """Tests for PHPCSParser (code sniffer, JSON/XML output)."""

    _PHPCS_JSON = json.dumps(
        {
            "totals": {"errors": 1, "warnings": 0, "fixable": 1},
            "files": {
                "src/Bar.php": {
                    "errors": 1,
                    "warnings": 0,
                    "messages": [
                        {
                            "message": "Space before opening brace",
                            "source": "PSR2.Classes.ClassDeclaration.OpenBraceNewLine",
                            "severity": 5,
                            "fixable": True,
                            "type": "ERROR",
                            "line": 12,
                            "column": 1,
                        }
                    ],
                }
            },
        }
    )

    def test_parse_empty_returns_empty(self) -> None:
        PHPCSParser, *_ = _import_phpcs()
        assert PHPCSParser().parse_json_report("") == []

    def test_parse_invalid_json_returns_empty(self) -> None:
        PHPCSParser, *_ = _import_phpcs()
        assert PHPCSParser().parse_json_report("garbage") == []

    def test_parse_valid_json(self) -> None:
        PHPCSParser, PHPCSViolation, PHPCSSeverity, _, _ = _import_phpcs()
        violations = PHPCSParser().parse_json_report(self._PHPCS_JSON)
        assert len(violations) == 1
        v = violations[0]
        assert v.file_path == "src/Bar.php"
        assert v.line_number == 12
        assert v.is_fixable is True
        assert v.severity == "error"

    def test_sniff_id_preserved(self) -> None:
        PHPCSParser, *_ = _import_phpcs()
        violations = PHPCSParser().parse_json_report(self._PHPCS_JSON)
        assert "PSR2" in violations[0].sniff_id

    def test_categorize_by_severity(self) -> None:
        PHPCSParser, PHPCSViolation, *_ = _import_phpcs()
        p = PHPCSParser()
        viols = [
            PHPCSViolation(sniff_id="a", message="x", severity="error"),
            PHPCSViolation(sniff_id="b", message="y", severity="warning"),
        ]
        grouped = p.categorize_by_severity(viols)
        assert "error" in grouped
        assert "warning" in grouped

    def test_generate_report_json(self) -> None:
        PHPCSParser, PHPCSViolation, *_ = _import_phpcs()
        p = PHPCSParser()
        viols = [
            PHPCSViolation(
                sniff_id="s",
                message="msg",
                file_path="f.php",
                line_number=1,
                severity="error",
            )
        ]
        data = json.loads(p.generate_report(viols, fmt="json"))
        assert data["tool"] == "phpcs"
        assert data["total"] == 1

    def test_generate_report_text(self) -> None:
        PHPCSParser, PHPCSViolation, *_ = _import_phpcs()
        p = PHPCSParser()
        viols = [
            PHPCSViolation(
                sniff_id="s",
                message="bad",
                file_path="f.php",
                line_number=2,
                severity="warning",
            )
        ]
        report = p.generate_report(viols, fmt="text")
        assert "f.php" in report
        assert "bad" in report

    def test_parse_xml_report(self, tmp_path: Path) -> None:
        xml_content = (
            '<?xml version="1.0" ?>\n'
            '<checkstyle version="phpcs-3.6">\n'
            ' <file name="src/Baz.php">\n'
            '  <error line="5" column="1" severity="error" message="Missing doc comment" source="Generic.Commenting.Todo" />\n'
            " </file>\n"
            "</checkstyle>"
        )
        xml_file = tmp_path / "report.xml"
        xml_file.write_text(xml_content)
        PHPCSParser, *_ = _import_phpcs()
        violations = PHPCSParser().parse_xml_report(xml_file)
        assert len(violations) == 1
        assert violations[0].file_path == "src/Baz.php"
        assert violations[0].line_number == 5

    def test_execute_phpcs_returns_empty_when_missing(self) -> None:
        PHPCSParser, *_ = _import_phpcs()
        import unittest.mock as mock

        with mock.patch(
            "code_scalpel.code_parsers.php_parsers.php_parsers_PHPCS.shutil.which",
            return_value=None,
        ):
            assert PHPCSParser().execute_phpcs() == []

    def test_language_attribute(self) -> None:
        PHPCSParser, *_ = _import_phpcs()
        assert PHPCSParser().language == "php"


# ===========================================================================
# Psalm
# ===========================================================================


class TestPsalmParser:
    """Tests for PsalmParser (type checker + taint analysis)."""

    _PSALM_JSON = json.dumps(
        [
            {
                "severity": "error",
                "line_from": 20,
                "column_from": 4,
                "type": "PossiblyNullReference",
                "message": "Cannot call method on possibly null value",
                "file_name": "src/Controller.php",
                "snippet": "$foo->bar()",
            },
            {
                "severity": "error",
                "line_from": 30,
                "column_from": 1,
                "type": "TaintedInput",
                "message": "Tainted input from SQL query",
                "file_name": "src/DB.php",
            },
        ]
    )

    def test_parse_empty_returns_empty(self) -> None:
        PsalmParser, *_ = _import_psalm()
        assert PsalmParser().parse_json_report("") == []

    def test_parse_valid_json(self) -> None:
        PsalmParser, PsalmError, *_ = _import_psalm()
        errors = PsalmParser().parse_json_report(self._PSALM_JSON)
        assert len(errors) == 2
        assert errors[0].file_path == "src/Controller.php"
        assert errors[0].line_number == 20
        assert errors[0].cwe_id == "CWE-476"

    def test_taint_detection(self) -> None:
        PsalmParser, _, _, PsalmErrorType, _ = _import_psalm()
        errors = PsalmParser().parse_json_report(self._PSALM_JSON)
        taint = [e for e in errors if e.error_type == PsalmErrorType.TAINT.value]
        assert len(taint) >= 1

    def test_analyze_taint_returns_list(self) -> None:
        PsalmParser, *_ = _import_psalm()
        p = PsalmParser()
        p.errors = p.parse_json_report(self._PSALM_JSON)
        taint = p.analyze_taint()
        assert isinstance(taint, list)
        assert all("cwe" in t for t in taint)

    def test_generate_report_json(self) -> None:
        PsalmParser, *_ = _import_psalm()
        p = PsalmParser()
        errors = p.parse_json_report(self._PSALM_JSON)
        data = json.loads(p.generate_report(errors, fmt="json"))
        assert data["tool"] == "psalm"
        assert data["total_errors"] == 2

    def test_execute_psalm_returns_empty_when_missing(self) -> None:
        PsalmParser, *_ = _import_psalm()
        import unittest.mock as mock

        with mock.patch(
            "code_scalpel.code_parsers.php_parsers.php_parsers_Psalm.shutil.which",
            return_value=None,
        ):
            assert PsalmParser().execute_psalm() == []

    def test_language_attribute(self) -> None:
        PsalmParser, *_ = _import_psalm()
        assert PsalmParser().language == "php"


# ===========================================================================
# PHPMD
# ===========================================================================


class TestPHPMDParser:
    """Tests for PHPMDParser (mess detector, XML/JSON output)."""

    _PHPMD_XML = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<pmd version="phpmd-2.15.0" xmlns="http://pmd.sf.net/ruleset/2.0.0">\n'
        '  <file name="src/Foo.php">\n'
        '    <violation beginline="14" endline="14" rule="CyclomaticComplexity"\n'
        '               ruleset="Code Size Rules" priority="2"\n'
        '               externalInfoUrl="https://phpmd.org/rules/">\n'
        "      The method foo has a Cyclomatic Complexity of 12.\n"
        "    </violation>\n"
        "  </file>\n"
        "</pmd>\n"
    )

    _PHPMD_JSON = json.dumps(
        {
            "files": [
                {
                    "file": "src/Bar.php",
                    "violations": [
                        {
                            "rule": "ExcessiveMethodLength",
                            "ruleSet": "Code Size Rules",
                            "priority": 3,
                            "beginLine": 40,
                            "description": "Method bar has 200 lines",
                        }
                    ],
                }
            ]
        }
    )

    def test_parse_xml_file(self, tmp_path: Path) -> None:
        xml_file = tmp_path / "phpmd.xml"
        xml_file.write_text(self._PHPMD_XML)
        PHPMDParser, *_ = _import_phpmd()
        violations = PHPMDParser().parse_xml_report(xml_file)
        assert len(violations) == 1
        v = violations[0]
        assert v.file_path == "src/Foo.php"
        assert v.line_number == 14
        assert v.rule == "CyclomaticComplexity"
        assert v.priority == 2
        assert v.cwe_id == "CWE-1121"

    def test_parse_json_report(self) -> None:
        PHPMDParser, *_ = _import_phpmd()
        violations = PHPMDParser().parse_json_report(self._PHPMD_JSON)
        assert len(violations) == 1
        assert violations[0].file_path == "src/Bar.php"
        assert violations[0].rule == "ExcessiveMethodLength"

    def test_parse_xml_string_auto(self) -> None:
        PHPMDParser, *_ = _import_phpmd()
        violations = PHPMDParser().parse_output(self._PHPMD_XML)
        assert len(violations) == 1

    def test_parse_empty_returns_empty(self) -> None:
        PHPMDParser, *_ = _import_phpmd()
        assert PHPMDParser().parse_json_report("") == []

    def test_generate_report_json(self) -> None:
        PHPMDParser, PHPMDViolation, *_ = _import_phpmd()
        p = PHPMDParser()
        viols = [
            PHPMDViolation(
                message="m",
                rule="CyclomaticComplexity",
                rule_set="Code Size Rules",
                file_path="f.php",
            )
        ]
        data = json.loads(p.generate_report(viols, fmt="json"))
        assert data["tool"] == "phpmd"
        assert data["total"] == 1

    def test_execute_phpmd_returns_empty_when_missing(self) -> None:
        PHPMDParser, *_ = _import_phpmd()
        import unittest.mock as mock

        with mock.patch(
            "code_scalpel.code_parsers.php_parsers.php_parsers_phpmd.shutil.which",
            return_value=None,
        ):
            assert PHPMDParser().execute_phpmd() == []

    def test_language_attribute(self) -> None:
        PHPMDParser, *_ = _import_phpmd()
        assert PHPMDParser().language == "php"


# ===========================================================================
# PHP AST parser
# ===========================================================================


class TestPHPParserAST:
    """Tests for PHPParserAST (no external CLI; uses PHPNormalizer internally)."""

    def test_instantiation(self) -> None:
        PHPParserAST, *_ = _import_ast()
        p = PHPParserAST()
        assert p.language == "php"
        assert p.classes == []
        assert p.functions == []

    def test_extract_classes_fallback_empty_when_no_normalizer(self) -> None:
        """When tree-sitter-php is absent, extract_classes returns []."""
        PHPParserAST, *_ = _import_ast()
        import unittest.mock as mock

        with mock.patch(__name__ + "._patch_normalizer_none"):
            pass  # no-op; real test is below where we mock _get_normalizer
        p = PHPParserAST()
        with mock.patch.object(p, "_get_normalizer", return_value=None):
            result = p.extract_classes("<?php class Foo {}")
            assert result == []

    def test_extract_functions_fallback_empty_when_no_normalizer(self) -> None:
        PHPParserAST, *_ = _import_ast()
        import unittest.mock as mock

        p = PHPParserAST()
        with mock.patch.object(p, "_get_normalizer", return_value=None):
            result = p.extract_functions("<?php function bar() {}")
            assert result == []

    def test_analyze_structure_with_real_normalizer(self):
        """If tree-sitter-php is available, parse basic class+function."""
        PHPParserAST, PHPClass, PHPFunction = _import_ast()
        p = PHPParserAST()
        if p._get_normalizer() is None:
            pytest.skip("tree-sitter-php not installed")
        php_code = "<?php\nclass MyClass {\n  public function hello() {}\n}\nfunction stand_alone() {}"
        summary = p.analyze_structure(php_code)
        assert "class_count" in summary
        assert "function_count" in summary

    def test_generate_report_json(self) -> None:
        PHPParserAST, PHPClass, PHPFunction = _import_ast()
        p = PHPParserAST()
        classes = [PHPClass(name="Foo", line_number=2, methods=["bar"])]
        funcs = [PHPFunction(name="baz", line_number=10)]
        data = json.loads(p.generate_report(classes, funcs, fmt="json"))
        assert data["tool"] == "php-ast"
        assert data["class_count"] == 1
        assert data["function_count"] == 1

    def test_generate_report_text(self) -> None:
        PHPParserAST, PHPClass, PHPFunction = _import_ast()
        p = PHPParserAST()
        classes = [PHPClass(name="Alpha", methods=["run"])]
        funcs = [PHPFunction(name="beta")]
        text = p.generate_report(classes, funcs, fmt="text")
        assert "Alpha" in text
        assert "beta" in text

    def test_build_call_graph_no_normalizer(self) -> None:
        PHPParserAST, *_ = _import_ast()
        import unittest.mock as mock

        p = PHPParserAST()
        with mock.patch.object(p, "_get_normalizer", return_value=None):
            graph = p.build_call_graph("<?php function a() { b(); }")
            assert graph == {}


# ---------------------------------------------------------------------------
# dummy function to avoid NameError in test_extract_classes_fallback
# ---------------------------------------------------------------------------
def _patch_normalizer_none():  # noqa: ANN201
    pass


# ===========================================================================
# Composer
# ===========================================================================


class TestComposerParser:
    """Tests for ComposerParser (pure Python, no CLI)."""

    _COMPOSER_JSON = json.dumps(
        {
            "name": "vendor/my-app",
            "description": "Test project",
            "require": {
                "php": ">=8.0",
                "symfony/console": "^6.0",
                "guzzlehttp/guzzle": "^7.4",
            },
            "require-dev": {
                "phpunit/phpunit": "^10.0",
            },
        }
    )

    _COMPOSER_LOCK = json.dumps(
        {
            "packages": [
                {
                    "name": "symfony/console",
                    "version": "6.3.0",
                    "description": "Symfony Console",
                },
                {
                    "name": "guzzlehttp/guzzle",
                    "version": "7.5.0",
                    "description": "HTTP client",
                },
            ],
            "packages-dev": [
                {
                    "name": "phpunit/phpunit",
                    "version": "10.1.0",
                    "description": "PHPUnit",
                },
            ],
        }
    )

    def test_parse_composer_json_string(self) -> None:
        ComposerParser, ComposerPackage, ComposerConfig = _import_composer()
        p = ComposerParser()
        config = p.parse_composer_json_string(self._COMPOSER_JSON)
        assert config.name == "vendor/my-app"
        assert len(config.requires) == 2  # php excluded
        assert len(config.requires_dev) == 1

    def test_require_names(self) -> None:
        ComposerParser, *_ = _import_composer()
        p = ComposerParser()
        config = p.parse_composer_json_string(self._COMPOSER_JSON)
        names = {pkg.name for pkg in config.requires}
        assert "symfony/console" in names
        assert "guzzlehttp/guzzle" in names

    def test_dev_flag(self) -> None:
        ComposerParser, *_ = _import_composer()
        p = ComposerParser()
        config = p.parse_composer_json_string(self._COMPOSER_JSON)
        assert all(not pkg.is_dev for pkg in config.requires)
        assert all(pkg.is_dev for pkg in config.requires_dev)

    def test_parse_composer_json_file(self, tmp_path: Path) -> None:
        cj = tmp_path / "composer.json"
        cj.write_text(self._COMPOSER_JSON)
        ComposerParser, *_ = _import_composer()
        p = ComposerParser()
        config = p.parse_composer_json(cj)
        assert config.name == "vendor/my-app"

    def test_parse_composer_lock_string(self) -> None:
        ComposerParser, ComposerPackage, _ = _import_composer()
        p = ComposerParser()
        packages = p.parse_composer_lock_string(self._COMPOSER_LOCK)
        assert len(packages) == 3
        prod = [pk for pk in packages if not pk.is_dev]
        dev = [pk for pk in packages if pk.is_dev]
        assert len(prod) == 2
        assert len(dev) == 1

    def test_parse_composer_lock_file(self, tmp_path: Path) -> None:
        lf = tmp_path / "composer.lock"
        lf.write_text(self._COMPOSER_LOCK)
        ComposerParser, *_ = _import_composer()
        p = ComposerParser()
        packages = p.parse_composer_lock(lf)
        assert len(packages) == 3

    def test_scan_vulnerabilities_dev_version(self) -> None:
        ComposerParser, ComposerPackage, _ = _import_composer()
        p = ComposerParser()
        lock = json.dumps(
            {
                "packages": [{"name": "evil/pkg", "version": "dev-main"}],
                "packages-dev": [],
            }
        )
        p.parse_composer_lock_string(lock)
        risks = p.scan_vulnerabilities()
        assert any(r["package"] == "evil/pkg" for r in risks)

    def test_detect_outdated_caret_constraints(self) -> None:
        ComposerParser, *_ = _import_composer()
        p = ComposerParser()
        p.parse_composer_json_string(self._COMPOSER_JSON)
        outdated = p.detect_outdated()
        # Both symfony/console (^6.0) and guzzle (^7.4) use ^
        assert len(outdated) >= 1

    def test_generate_report_json(self) -> None:
        ComposerParser, ComposerPackage, _ = _import_composer()
        p = ComposerParser()
        pkgs = [ComposerPackage(name="symfony/console", version="6.3.0")]
        data = json.loads(p.generate_report(pkgs, fmt="json"))
        assert data["tool"] == "composer"
        assert data["package_count"] == 1

    def test_parse_invalid_composer_json(self) -> None:
        ComposerParser, *_ = _import_composer()
        p = ComposerParser()
        config = p.parse_composer_json_string("not json")
        assert isinstance(config, _import_composer()[2])  # ComposerConfig

    def test_language_attribute(self) -> None:
        ComposerParser, *_ = _import_composer()
        assert ComposerParser().language == "php"


# ===========================================================================
# Exakat
# ===========================================================================


class TestExakatParser:
    """Tests for ExakatParser (enterprise tool; execute raises NotImplementedError)."""

    _EXAKAT_JSON = json.dumps(
        [
            {
                "analyzer": "Security/PHPInjection",
                "file": "src/Vuln.php",
                "line": 42,
                "code": "eval($user_input)",
                "severity": "critical",
            },
            {
                "analyzer": "Performance/NoEcho",
                "file": "src/View.php",
                "line": 10,
                "severity": "low",
            },
        ]
    )

    _EXAKAT_CSV = (
        "analyzer,file,namespace,class,function,line,code\n"
        "Security/XSS,src/X.php,,Ctrl,show,5,echo $_GET['q']\n"
        "Dead code/UnusedVariable,src/Y.php,,,,12,$tmp = 1\n"
    )

    def test_parse_json_report(self) -> None:
        ExakatParser, ExakatIssue, _ = _import_exakat()
        issues = ExakatParser().parse_json_report(self._EXAKAT_JSON)
        assert len(issues) == 2
        assert issues[0].category == "Security"
        assert issues[0].title == "PHPInjection"
        assert issues[0].file_path == "src/Vuln.php"
        assert issues[0].line_number == 42

    def test_json_cwe_inferred(self) -> None:
        ExakatParser, *_ = _import_exakat()
        issues = ExakatParser().parse_json_report(self._EXAKAT_JSON)
        security_issue = issues[0]
        assert security_issue.cwe_id is not None

    def test_parse_csv_string(self) -> None:
        ExakatParser, *_ = _import_exakat()
        p = ExakatParser()
        issues = p.parse_csv_string(self._EXAKAT_CSV)
        assert len(issues) == 2
        assert issues[0].category == "Security"
        assert issues[0].title == "XSS"
        assert issues[0].file_path == "src/X.php"
        assert issues[0].line_number == 5
        assert issues[0].cwe_id == "CWE-79"

    def test_parse_csv_file(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "report.csv"
        csv_file.write_text(self._EXAKAT_CSV)
        ExakatParser, *_ = _import_exakat()
        issues = ExakatParser().parse_csv_report(csv_file)
        assert len(issues) == 2

    def test_parse_empty_returns_empty(self) -> None:
        ExakatParser, *_ = _import_exakat()
        assert ExakatParser().parse_json_report("") == []

    def test_parse_output_auto_json(self) -> None:
        ExakatParser, *_ = _import_exakat()
        issues = ExakatParser().parse_output(self._EXAKAT_JSON)
        assert len(issues) == 2

    def test_execute_exakat_raises(self) -> None:
        ExakatParser, *_ = _import_exakat()
        with pytest.raises(NotImplementedError):
            ExakatParser().execute_exakat(Path("/tmp/project"))

    def test_generate_report_json(self) -> None:
        ExakatParser, ExakatIssue, _ = _import_exakat()
        issues = ExakatParser().parse_json_report(self._EXAKAT_JSON)
        data = json.loads(ExakatParser().generate_report(issues, fmt="json"))
        assert data["tool"] == "exakat"
        assert data["total"] == 2

    def test_generate_report_text(self) -> None:
        ExakatParser, ExakatIssue, _ = _import_exakat()
        issues = ExakatParser().parse_json_report(self._EXAKAT_JSON)
        text = ExakatParser().generate_report(issues, fmt="text")
        assert "Security" in text

    def test_categorize_by_category(self) -> None:
        ExakatParser, *_ = _import_exakat()
        p = ExakatParser()
        issues = p.parse_json_report(self._EXAKAT_JSON)
        cats = p.categorize_by_category(issues)
        assert "Security" in cats
        assert "Performance" in cats

    def test_language_attribute(self) -> None:
        ExakatParser, *_ = _import_exakat()
        assert ExakatParser().language == "php"
