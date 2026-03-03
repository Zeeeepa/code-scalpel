# Adding Kotlin Language Support

**Difficulty**: Medium — JVM language with a clean tree-sitter grammar. Kotlin's main challenges are its primary constructor syntax (parameters declared on the class line), extension functions (receiver type is part of the function signature), companion objects, and `when` expressions. The IR mapping strategy is well-established from the Java normalizer and can serve as the closest reference.

**Estimated integration points**: 12 files (same as every language — see [Adding-A-Language.md](Adding-A-Language.md) for the master checklist).

---

## Package

```bash
pip install tree-sitter-kotlin
python -c "import tree_sitter_kotlin; print('OK')"
```

Add to `pyproject.toml`:

```toml
"tree-sitter-kotlin>=0.3.0",  # [FEATURE] Kotlin language support
```

Add to all three locations: `dependencies`, `[all]`, and `[polyglot]` extras.

---

## Language Enum + Extension Map

```python
# Language enum (both extractor files)
KOTLIN = "kotlin"

# Extension map
".kt":  Language.KOTLIN,
".kts": Language.KOTLIN,   # Kotlin script files
```

---

## Content-Based Detection Heuristics

Place the Kotlin block **before** the Java check (both share `fun` and class-like structures, but Kotlin keywords are distinctive):

```python
# Kotlin indicators — check before Java; "fun " and "val/var" are unambiguous
if any(kw in code for kw in ["fun ", "val ", "data class ", "object ", "companion object"]):
    return Language.KOTLIN
```

**Ordering**: C# → Go → Kotlin → Java → C++ → C → JavaScript → Python.

`"fun "` is safe because Java uses `void`/return-type declarations and not `fun`. Watch for false positives in comment strings, but these are rare in practice.

---

## Key AST Node Mappings

| tree-sitter-kotlin node | IR node | Notes |
|------------------------|---------|-------|
| `source_file` | `IRModule` | Root |
| `import_list` / `import_header` | `IRImport` | Strip `import ` prefix; alias from `import_alias` child |
| `package_header` | (record on module `_metadata["package"]`) | |
| `function_declaration` | `IRFunctionDef` | Regular `fun foo()` |
| `function_declaration` with `receiver_type` | `IRFunctionDef` | Extension function; store receiver in `_metadata["receiver"]` |
| `class_declaration` with `DATA_MODIFIER` | `IRClassDef` | `data class Foo(val x: Int)` |
| `class_declaration` with `ABSTRACT_MODIFIER` | `IRClassDef` | Abstract class |
| `class_declaration` | `IRClassDef` | Regular class |
| `object_declaration` | `IRClassDef` | Kotlin singleton object; `_metadata["kind"] = "object"` |
| `companion_object` | `IRClassDef` | Companion object inside a class; `_metadata["kind"] = "companion_object"` |
| `interface_declaration` | `IRClassDef` | `_metadata["kind"] = "interface"` |
| `property_declaration` with `val`/`var` | `IRAssign` | Top-level or class-level property |
| `local_variable_declaration` | `IRAssign` | Local `val`/`var` inside a function |
| `assignment` | `IRAssign` | Regular assignment |
| `return_statement` | `IRReturn` | |
| `if_expression` | `IRIf` | Note: Kotlin `if` is an expression, not a statement |
| `when_expression` | `IRIf` | Map to `IRIf` chain; store `_metadata["kind"] = "when"` |
| `for_statement` | `IRFor` | `for (x in collection)` |
| `while_statement` | `IRFor` | Map to `IRFor`; `_metadata["kind"] = "while"` |
| `do_while_statement` | `IRFor` | Map to `IRFor`; `_metadata["kind"] = "do_while"` |
| `call_expression` | `IRCall` | |
| `lambda_literal` | `IRFunctionDef` | `{ x -> x + 1 }`; `_metadata["kind"] = "lambda"` |
| `anonymous_function` | `IRFunctionDef` | `fun(x: Int): Int { ... }` |

---

## Kotlin-Specific Implementation Notes

### Primary constructor on the class header

Kotlin allows parameters directly on the class declaration line:

```kotlin
class Point(val x: Double, val y: Double)
```

The `primary_constructor` is a child of `class_declaration`. Extract it and add `IRParameter` nodes to the class's metadata, **not** as a method body. Do not create an `IRFunctionDef` for the primary constructor — it is part of the class definition.

```
class_declaration
  ├── type_identifier  ("Point")
  ├── primary_constructor
  │   └── class_parameter  (x: Double)
  │   └── class_parameter  (y: Double)
  └── class_body
```

Store these in `ir_class._metadata["primary_constructor_params"]` as a list of `(name, type_str)` tuples.

### Extension functions

Extension functions declare a receiver type before the function name:

```kotlin
fun String.shout(): String = this.uppercase() + "!"
```

The tree-sitter node is a regular `function_declaration` but has a `receiver_type` field. Map it to `IRFunctionDef` and store:

```python
fn._metadata["receiver"] = self._text_of(node.child_by_field_name("receiver_type"))
fn._metadata["kind"] = "extension"
```

### Companion objects

```kotlin
class Foo {
    companion object {
        fun create(): Foo = Foo()
    }
}
```

`companion_object` is a child of `class_body`. Map the companion object itself to `IRClassDef(name="Companion", _metadata={"kind": "companion_object"})` and add methods inside it as `IRFunctionDef` nodes in its body.

### `when` expressions

`when` is Kotlin's pattern-matching construct. Map it to an `IRIf` chain with `_metadata["kind"] = "when"`. Each `when_entry` maps to an `IRIf` condition branch.

### `init` blocks

```kotlin
class Foo {
    init { println("initialized") }
}
```

Map `anonymous_initializer` to `IRFunctionDef(name="<init>", _metadata={"kind": "init_block"})`.

### `object` declarations (singletons)

```kotlin
object Registry {
    val entries = mutableListOf<String>()
}
```

Map `object_declaration` to `IRClassDef` with `_metadata["kind"] = "object"`. This is a singleton — there will only ever be one instance.

---

## Block Structure

Kotlin uses `class_body` (for classes) and `function_body` (for functions):

```
function_declaration
  ├── simple_identifier  ("greet")
  ├── function_value_parameters
  └── function_body
        └── block
              └── statements
```

The `function_body` can be either a `block` (with `{...}`) or an `expression_body` (with `= expr`). Handle both:

```python
body_node = node.child_by_field_name("body")
if body_node:
    if body_node.type == "block":
        stmts = self._visit_block(body_node)
    elif body_node.type == "function_body":
        # expression body: fun foo() = expr
        stmts = [self._visit_expr(body_node.named_children[0])]
```

---

## `_parse_kotlin()` Method

```python
def _parse_kotlin(self) -> None:
    """Parse Kotlin code using tree-sitter-kotlin. [FEATURE]"""
    from code_scalpel.ir.normalizers.kotlin_normalizer import KotlinNormalizer

    normalizer = KotlinNormalizer()
    self._ir_module = normalizer.normalize(self.code)
```

---

## limits.toml

Add `"kotlin"` to the `languages` arrays in all three tier sections of `analyze_code` and `unified_sink_detect`.

---

## Tests to Write

### `tests/languages/test_kotlin_parser.py`

Cover all of the following scenarios with separate test methods:

1. **Extension detection** — `.kt` and `.kts` map to `Language.KOTLIN`
2. **Content detection** — `"fun "` heuristic identifies Kotlin
3. **Regular function extraction** — `fun greet(name: String): String`
4. **Class extraction** — `class Point(val x: Double, val y: Double)`
5. **Data class extraction** — `data class User(val id: Int, val name: String)`
6. **Interface extraction** — `interface Printable { fun print() }`
7. **Object declaration (singleton)** — `object Registry { ... }`
8. **Companion object** — extracted as nested `IRClassDef`
9. **Extension function** — receiver stored in `_metadata["receiver"]`
10. **Import extraction** — single and aliased imports
11. **Property declaration (val/var)** — maps to `IRAssign`
12. **Lambda in function body** — captured as nested `IRFunctionDef`
13. **Missing symbol** — returns graceful failure, not exception

### `tests/languages/test_polyglot_support.py`

- Add `"kotlin"` to `TestAnalyzeCodeLanguageSupport` parametrize
- Add `"kotlin"` to `TestUnifiedSinkDetectLanguageSupport` parametrize
- Add matrix rows for Kotlin in `TestToolLanguageMatrix`
- Add `.kt` to `TestLanguageDetection.test_file_extension_detection`

---

## Verification Commands

```bash
pip install tree-sitter-kotlin

# 1. Normalizer smoke test
python -c "
from code_scalpel.ir.normalizers.kotlin_normalizer import KotlinNormalizer
from code_scalpel.ir.nodes import IRFunctionDef, IRClassDef
n = KotlinNormalizer()
code = '''
data class Point(val x: Double, val y: Double)
fun distance(p: Point): Double = p.x + p.y
'''
m = n.normalize(code)
funcs = [x.name for x in m.body if isinstance(x, IRFunctionDef)]
classes = [x.name for x in m.body if isinstance(x, IRClassDef)]
print('Functions:', funcs)
print('Classes:', classes)
"

# 2. PolyglotExtractor end-to-end
python -c "
from code_scalpel.code_parsers.extractor import PolyglotExtractor, Language
code = 'fun hello(): String { return \"hi\" }\nfun world() { println(\"world\") }'
e = PolyglotExtractor(code, language=Language.KOTLIN)
r = e.extract('function', 'hello')
print('OK' if r.success else r.error)
"

# 3. Run test suite
pytest tests/languages/test_kotlin_parser.py -v
pytest tests/languages/ -v --tb=short
```

---

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Kotlin detected as Java | `"fun "` check not placed before Java check | Move Kotlin heuristic before Java in `detect_language()` |
| Primary constructor params missing | `primary_constructor` not traversed | Visit `class_declaration.primary_constructor` children |
| Extension functions not found | `receiver_type` makes the signature look different | Check for `receiver_type` field on `function_declaration` |
| Companion object methods missing | `companion_object` body not visited | Recurse into `companion_object.class_body` |
| `when` expression crashes | Not mapped to an IR node | Map `when_expression` → `IRIf` with `_metadata["kind"] = "when"` |
| `.kts` files not detected | Extension map only has `.kt` | Add both `.kt` and `.kts` to `EXTENSION_MAP` |

---

## Phase 2 — Static Analysis Tool Parsers

The `kotlin_parsers/` directory is pre-scaffolded with Phase 1 framework (data classes, method stubs). All 8 tool parsers must be fully implemented before Kotlin is considered complete.

### Tools to implement

| File | Tool | Output format | Type |
|------|------|--------------|------|
| `kotlin_parsers_Detekt.py` | Detekt | XML / SARIF / JSON (`--report xml:...`) | Free — execute + parse |
| `kotlin_parsers_ktlint.py` | ktlint | JSON (`ktlint --reporter=json`) | Free — execute + parse |
| `kotlin_parsers_diktat.py` | diktat | SARIF / XML | Free — execute + parse |
| `kotlin_parsers_gradle.py` | Gradle build | `build.gradle.kts` + build output | Config parsing |
| `kotlin_parsers_compose.py` | Compose Lint | SARIF (Android Lint format) | Free — execute + parse |
| `kotlin_parsers_Konsist.py` | Konsist | JUnit XML (test-based) | Test output parsing |
| `kotlin_parsers_test.py` | Test utilities | — | Helper utilities |

### Priority order

1. **ktlint** — most widely used Kotlin linter; JSON output is trivial to parse
2. **Detekt** — de-facto standard for Kotlin static analysis; rich rule set with severity levels
3. **diktat** — Kotlin coding standard linter (Kotlin Foundation-endorsed)
4. **Compose Lint** — critical for Android Kotlin projects (uses Android Lint SARIF)
5. **Gradle** — parse `build.gradle.kts` for dependencies and configuration
6. **Konsist** — architecture validation; parse JUnit XML output from tests

### ktlint implementation notes

ktlint JSON output format:
```json
[{"file":"src/main.kt","errors":[
  {"line":12,"column":5,"message":"Unexpected blank line(s)","rule":"no-blank-line-before-rbrace"}
]}]
```

```python
def execute_ktlint(self, paths: list[Path], config=None) -> list[KtlintViolation]:
    if shutil.which("ktlint") is None:
        return []
    cmd = ["ktlint", "--reporter=json"] + [str(p) for p in paths]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return self.parse_json_output(result.stdout)

def parse_json_output(self, output: str) -> list[KtlintViolation]:
    import json
    files = json.loads(output or "[]")
    violations = []
    for file_entry in files:
        for error in file_entry.get("errors", []):
            violations.append(KtlintViolation(
                file_path=file_entry["file"],
                line_number=error["line"],
                column=error["column"],
                message=error["message"],
                rule=error["rule"],
                severity="warning",
            ))
    return violations
```

### Detekt implementation notes

Detekt XML output format:
```xml
<checkstyle>
  <file name="src/main.kt">
    <error line="12" column="5" severity="warning" message="..." source="detekt.ComplexMethod"/>
  </file>
</checkstyle>
```

Use `xml.etree.ElementTree` to parse. Map `source` attribute to `DetektRuleCategory` enum.

### KotlinParserRegistry

```python
class KotlinParserRegistry:
    def __init__(self):
        from . import kotlin_parsers_ktlint, kotlin_parsers_Detekt, kotlin_parsers_diktat
        self._parsers = {
            "ktlint":  kotlin_parsers_ktlint.KtlintParser,
            "detekt":  kotlin_parsers_Detekt.DetektParser,
            "diktat":  kotlin_parsers_diktat.DiktatParser,
            "compose": kotlin_parsers_compose.ComposeLintParser,
            "gradle":  kotlin_parsers_gradle.GradleParser,
            "konsist": kotlin_parsers_Konsist.KonsistParser,
        }
    # ... standard get_parser() and analyze() methods
```

### Tests (`tests/languages/test_kotlin_tool_parsers.py`)

Write fixture-based tests (do not require tools installed):
- `test_ktlint_parse_json_output()` — parse sample JSON string
- `test_detekt_parse_xml_output()` — parse sample Checkstyle XML
- `test_detekt_categorize_by_rule()` — group by `DetektRuleCategory`
- `test_registry_get_parser_ktlint()` — factory test
- `test_graceful_degradation_no_ktlint()` — `shutil.which` returns None → returns `[]`
