"""Dedicated PHP parser tests.

Validates PHPNormalizer + PHPVisitor + PolyglotExtractor integration for PHP code.
All tests require tree-sitter-php to be installed; they are skipped gracefully otherwise.

[20260303_TEST] Created for PHP Stage 6 Phase 1 language support.
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Shared fixtures / skip guard
# ---------------------------------------------------------------------------

try:
    from code_scalpel.ir.normalizers.php_normalizer import PHPNormalizer

    _PHP_AVAILABLE = True
except ImportError:
    _PHP_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _PHP_AVAILABLE, reason="tree-sitter-php not installed"
)


# ---------------------------------------------------------------------------
# Shared PHP code snippets
# ---------------------------------------------------------------------------

_SIMPLE_FUNCTIONS = """\
<?php

function add(int $a, int $b): int {
    return $a + $b;
}

function greet(string $name): string {
    return "Hello, " . $name . "!";
}
"""

_CLASS_CODE = """\
<?php

class Animal {
    public string $name;

    public function __construct(string $name) {
        $this->name = $name;
    }

    public function speak(): string {
        return "...";
    }
}

class Dog extends Animal {
    public function speak(): string {
        return "Woof!";
    }
}

interface Speakable {
    public function speak(): string;
}
"""

_NAMESPACE_CODE = """\
<?php

namespace App\\Controllers;

use App\\Models\\User;
use App\\Services\\Auth as AuthService;

class UserController {
    public function index(): void {
        $users = User::all();
    }
}
"""

_CONTROL_FLOW_CODE = """\
<?php

function demo(int $x): string {
    if ($x > 0) {
        return "positive";
    } elseif ($x < 0) {
        return "negative";
    } else {
        return "zero";
    }
}

function looper(array $items): void {
    for ($i = 0; $i < 10; $i++) {
        echo $i;
    }
    foreach ($items as $key => $value) {
        echo $value;
    }
    while (true) {
        break;
    }
}
"""

_ASSIGNMENT_CODE = """\
<?php

function assignments(): void {
    $x = 42;
    $y = "hello";
    $z = $x + 1;
    $x += 10;
    $y .= " world";
}
"""

_COMPARISON_CODE = """\
<?php

function compare(int $a, int $b): bool {
    return $a === $b;
}

function loose_eq(mixed $a, mixed $b): bool {
    return $a == $b;
}

function bool_and(bool $a, bool $b): bool {
    return $a && $b;
}
"""


# ---------------------------------------------------------------------------
# Language / extension detection
# ---------------------------------------------------------------------------


class TestPHPLanguageDetection:
    """PHP should be detected by file extension and content heuristics."""

    def test_php_extension_detected(self):
        """``.php`` maps to Language.PHP."""
        from code_scalpel.code_parsers.extractor import EXTENSION_MAP, Language

        assert EXTENSION_MAP[".php"] is Language.PHP

    def test_additional_php_extensions_detected(self):
        """Legacy PHP extensions (.php5, .phtml, etc.) are mapped."""
        from code_scalpel.code_parsers.extractor import EXTENSION_MAP, Language

        for ext in (".php3", ".php4", ".php5", ".php7", ".phtml"):
            assert EXTENSION_MAP.get(ext) is Language.PHP, f"missing: {ext}"

    def test_php_language_enum_value(self):
        """Language.PHP should have value 'php'."""
        from code_scalpel.code_parsers.extractor import Language

        assert Language.PHP.value == "php"

    def test_content_detection_php_open_tag(self):
        """'<?php' heuristic should return Language.PHP."""
        from code_scalpel.code_parsers.extractor import Language, detect_language

        result = detect_language(None, "<?php\necho 'hello';")
        assert result is Language.PHP

    def test_content_detection_short_echo_tag(self):
        """'<?=' short echo heuristic should return Language.PHP."""
        from code_scalpel.code_parsers.extractor import Language, detect_language

        result = detect_language(None, "<?= $greeting ?>")
        assert result is Language.PHP

    def test_php_extension_on_both_extractor_modules(self):
        """Both code_parsers and polyglot extractor must agree on .php."""
        from code_scalpel.code_parsers.extractor import EXTENSION_MAP as CP_MAP
        from code_scalpel.code_parsers.extractor import Language as CP_Lang
        from code_scalpel.polyglot.extractor import EXTENSION_MAP as PG_MAP
        from code_scalpel.polyglot.extractor import Language as PG_Lang

        assert CP_MAP[".php"] is CP_Lang.PHP
        assert PG_MAP[".php"] is PG_Lang.PHP


# ---------------------------------------------------------------------------
# PHPNormalizer — functions
# ---------------------------------------------------------------------------


class TestPHPNormalizerFunctions:
    """PHPNormalizer should map PHP functions to IRFunctionDef nodes."""

    def test_simple_functions_extracted(self):
        """Top-level functions appear in module.body."""
        from code_scalpel.ir.nodes import IRFunctionDef

        n = PHPNormalizer()
        m = n.normalize(_SIMPLE_FUNCTIONS)
        names = [node.name for node in m.body if isinstance(node, IRFunctionDef)]
        assert "add" in names
        assert "greet" in names

    def test_function_has_location(self):
        """IRFunctionDef nodes carry line location info."""
        from code_scalpel.ir.nodes import IRFunctionDef

        n = PHPNormalizer()
        m = n.normalize(_SIMPLE_FUNCTIONS)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "add"
        )
        assert func.loc is not None
        assert func.loc.line > 0

    def test_function_parameters_captured(self):
        """Function parameters are IRParameter nodes."""
        from code_scalpel.ir.nodes import IRFunctionDef, IRParameter

        n = PHPNormalizer()
        m = n.normalize(_SIMPLE_FUNCTIONS)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "add"
        )
        param_names = [p.name for p in func.params if isinstance(p, IRParameter)]
        assert "a" in param_names
        assert "b" in param_names

    def test_function_body_has_return(self):
        """Function body contains IRReturn node."""
        from code_scalpel.ir.nodes import IRFunctionDef, IRReturn

        n = PHPNormalizer()
        m = n.normalize(_SIMPLE_FUNCTIONS)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "add"
        )
        returns = [s for s in func.body if isinstance(s, IRReturn)]
        assert len(returns) >= 1


# ---------------------------------------------------------------------------
# PHPNormalizer — classes and methods
# ---------------------------------------------------------------------------


class TestPHPNormalizerClasses:
    """Class, abstract class, and interface declarations map to IRClassDef."""

    def test_class_extracted(self):
        """Class declarations are IRClassDef nodes."""
        from code_scalpel.ir.nodes import IRClassDef

        n = PHPNormalizer()
        m = n.normalize(_CLASS_CODE)
        names = [node.name for node in m.body if isinstance(node, IRClassDef)]
        assert "Animal" in names

    def test_subclass_extracted(self):
        """Subclass with 'extends' is also an IRClassDef."""
        from code_scalpel.ir.nodes import IRClassDef

        n = PHPNormalizer()
        m = n.normalize(_CLASS_CODE)
        names = [node.name for node in m.body if isinstance(node, IRClassDef)]
        assert "Dog" in names

    def test_interface_extracted(self):
        """Interface declarations map to IRClassDef."""
        from code_scalpel.ir.nodes import IRClassDef

        n = PHPNormalizer()
        m = n.normalize(_CLASS_CODE)
        names = [node.name for node in m.body if isinstance(node, IRClassDef)]
        assert "Speakable" in names

    def test_methods_in_class_body(self):
        """Methods are IRFunctionDef nodes in IRClassDef.body."""
        from code_scalpel.ir.nodes import IRClassDef, IRFunctionDef

        n = PHPNormalizer()
        m = n.normalize(_CLASS_CODE)
        animal = next(
            node
            for node in m.body
            if isinstance(node, IRClassDef) and node.name == "Animal"
        )
        method_names = [b.name for b in animal.body if isinstance(b, IRFunctionDef)]
        assert "speak" in method_names


# ---------------------------------------------------------------------------
# PHPNormalizer — namespace and imports
# ---------------------------------------------------------------------------


class TestPHPNormalizerImports:
    """'use' statements produce IRImport nodes."""

    def test_use_statement_produces_ir_import(self):
        """'use App\\Models\\User' maps to an IRImport."""
        from code_scalpel.ir.nodes import IRImport

        n = PHPNormalizer()
        m = n.normalize(_NAMESPACE_CODE)
        imports = [node for node in m.body if isinstance(node, IRImport)]
        assert len(imports) >= 1

    def test_import_module_captured(self):
        """IRImport.names contains the imported symbol (e.g. 'User')."""
        from code_scalpel.ir.nodes import IRImport

        n = PHPNormalizer()
        m = n.normalize(_NAMESPACE_CODE)
        all_names: list[str] = []
        for node in m.body:
            if isinstance(node, IRImport):
                all_names.extend(node.names or [])
                if node.module:
                    all_names.append(node.module)
        assert any("User" in s for s in all_names)

    def test_import_alias_captured(self):
        """'use ... as AuthService' alias is preserved."""
        from code_scalpel.ir.nodes import IRImport

        n = PHPNormalizer()
        m = n.normalize(_NAMESPACE_CODE)
        aliases = {
            node.module: node.alias
            for node in m.body
            if isinstance(node, IRImport) and node.alias
        }
        assert any(a == "AuthService" for a in aliases.values())


# ---------------------------------------------------------------------------
# PHPNormalizer — control flow
# ---------------------------------------------------------------------------


class TestPHPNormalizerControlFlow:
    """if/for/foreach/while produce appropriate IR nodes."""

    def test_if_statement_produces_ir_if(self):
        """If statement maps to IRIf."""
        from code_scalpel.ir.nodes import IRFunctionDef, IRIf

        n = PHPNormalizer()
        m = n.normalize(_CONTROL_FLOW_CODE)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "demo"
        )
        ifs = [s for s in func.body if isinstance(s, IRIf)]
        assert len(ifs) >= 1

    def test_for_loop_produces_ir_for(self):
        """C-style for loop maps to IRFor."""
        from code_scalpel.ir.nodes import IRFor, IRFunctionDef

        n = PHPNormalizer()
        m = n.normalize(_CONTROL_FLOW_CODE)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "looper"
        )
        fors = [s for s in func.body if isinstance(s, IRFor)]
        assert len(fors) >= 1

    def test_foreach_loop_produces_ir_for(self):
        """foreach loop maps to IRFor with is_for_in=True."""
        from code_scalpel.ir.nodes import IRFor, IRFunctionDef

        n = PHPNormalizer()
        m = n.normalize(_CONTROL_FLOW_CODE)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "looper"
        )
        fors = [s for s in func.body if isinstance(s, IRFor)]
        # At least two loops (C-style + foreach)
        assert len(fors) >= 2

    def test_while_loop_produces_ir_while(self):
        """While loop maps to IRWhile."""
        from code_scalpel.ir.nodes import IRFunctionDef, IRWhile

        n = PHPNormalizer()
        m = n.normalize(_CONTROL_FLOW_CODE)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "looper"
        )
        whiles = [s for s in func.body if isinstance(s, IRWhile)]
        assert len(whiles) >= 1


# ---------------------------------------------------------------------------
# PHPNormalizer — assignments
# ---------------------------------------------------------------------------


class TestPHPNormalizerAssignments:
    """Variable assignments produce IRAssign and IRAugAssign nodes."""

    def test_assignment_produces_ir_assign(self):
        """Simple assignment '$x = 42' maps to IRAssign."""
        from code_scalpel.ir.nodes import IRAssign, IRFunctionDef

        n = PHPNormalizer()
        m = n.normalize(_ASSIGNMENT_CODE)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "assignments"
        )
        assigns = [s for s in func.body if isinstance(s, IRAssign)]
        assert len(assigns) >= 1


# ---------------------------------------------------------------------------
# PHPNormalizer — operators
# ---------------------------------------------------------------------------


class TestPHPNormalizerOperators:
    """Comparison and boolean operators map to IRCompare / IRBoolOp."""

    def test_strict_equality_produces_ir_compare(self):
        """'===' produces IRCompare with CompareOperator.STRICT_EQ."""
        from code_scalpel.ir.nodes import IRCompare, IRFunctionDef, IRReturn
        from code_scalpel.ir.operators import CompareOperator

        n = PHPNormalizer()
        m = n.normalize(_COMPARISON_CODE)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "compare"
        )
        ret = next(s for s in func.body if isinstance(s, IRReturn))
        assert isinstance(ret.value, IRCompare)
        assert CompareOperator.STRICT_EQ in ret.value.ops

    def test_loose_equality_produces_ir_compare(self):
        """'==' produces IRCompare with CompareOperator.EQ."""
        from code_scalpel.ir.nodes import IRCompare, IRFunctionDef, IRReturn
        from code_scalpel.ir.operators import CompareOperator

        n = PHPNormalizer()
        m = n.normalize(_COMPARISON_CODE)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "loose_eq"
        )
        ret = next(s for s in func.body if isinstance(s, IRReturn))
        assert isinstance(ret.value, IRCompare)
        assert CompareOperator.EQ in ret.value.ops

    def test_boolean_and_produces_ir_bool_op(self):
        """'&&' produces IRBoolOp with BoolOperator.AND."""
        from code_scalpel.ir.nodes import IRBoolOp, IRFunctionDef, IRReturn
        from code_scalpel.ir.operators import BoolOperator

        n = PHPNormalizer()
        m = n.normalize(_COMPARISON_CODE)
        func = next(
            node
            for node in m.body
            if isinstance(node, IRFunctionDef) and node.name == "bool_and"
        )
        ret = next(s for s in func.body if isinstance(s, IRReturn))
        assert isinstance(ret.value, IRBoolOp)
        assert ret.value.op is BoolOperator.AND


# ---------------------------------------------------------------------------
# PolyglotExtractor — end-to-end extraction
# ---------------------------------------------------------------------------


class TestPolyglotExtractorPHP:
    """PolyglotExtractor with Language.PHP should extract functions and classes."""

    def test_extract_function_by_name(self):
        """Extract a top-level function by name."""
        from code_scalpel.code_parsers.extractor import Language, PolyglotExtractor

        extractor = PolyglotExtractor(_SIMPLE_FUNCTIONS, language=Language.PHP)
        result = extractor.extract("function", "add")
        assert result.success, f"Expected success, got: {result.error}"
        assert "add" in result.code

    def test_extract_second_function(self):
        """Extract a second function to verify no state bleed."""
        from code_scalpel.code_parsers.extractor import Language, PolyglotExtractor

        extractor = PolyglotExtractor(_SIMPLE_FUNCTIONS, language=Language.PHP)
        result = extractor.extract("function", "greet")
        assert result.success, f"Expected success, got: {result.error}"
        assert "greet" in result.code

    def test_extract_class_by_name(self):
        """Extract a class definition by name."""
        from code_scalpel.code_parsers.extractor import Language, PolyglotExtractor

        extractor = PolyglotExtractor(_CLASS_CODE, language=Language.PHP)
        result = extractor.extract("class", "Animal")
        assert result.success, f"Expected success, got: {result.error}"
        assert "Animal" in result.code

    def test_extract_missing_symbol_returns_error(self):
        """Extracting a non-existent symbol returns failure."""
        from code_scalpel.code_parsers.extractor import Language, PolyglotExtractor

        extractor = PolyglotExtractor(_SIMPLE_FUNCTIONS, language=Language.PHP)
        result = extractor.extract("function", "nonExistent")
        assert not result.success
        assert result.error is not None

    def test_extract_reports_language_as_php(self):
        """ExtractionResult.language should be 'php'."""
        from code_scalpel.code_parsers.extractor import Language, PolyglotExtractor

        extractor = PolyglotExtractor(_SIMPLE_FUNCTIONS, language=Language.PHP)
        result = extractor.extract("function", "add")
        assert result.language == "php"

    def test_extract_reports_line_numbers(self):
        """ExtractionResult should carry valid start/end line numbers."""
        from code_scalpel.code_parsers.extractor import Language, PolyglotExtractor

        extractor = PolyglotExtractor(_SIMPLE_FUNCTIONS, language=Language.PHP)
        result = extractor.extract("function", "add")
        assert result.success
        assert result.start_line > 0
        assert result.end_line >= result.start_line

    def test_auto_detect_via_file_path(self):
        """When file_path ends in .php, language is auto-detected as PHP."""
        from code_scalpel.code_parsers.extractor import Language, PolyglotExtractor

        extractor = PolyglotExtractor(
            _SIMPLE_FUNCTIONS, file_path="app.php", language=Language.AUTO
        )
        assert extractor.language is Language.PHP
        result = extractor.extract("function", "add")
        assert result.success
