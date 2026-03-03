# Adding Swift Language Support

**Difficulty**: Medium-High — Swift's grammar shares many concepts with Kotlin (both are modern, statically-typed languages with classes, structs, protocols, and closures), but has several unique constructs: extensions (methods added to existing types from outside), property observers (`willSet`/`didSet`), computed properties, `guard` statements, `defer` blocks, and multiple initializer forms (`init`, `convenience init`, `required init`). Like Rust, methods live inside `extension` declarations that are separate from type definitions.

**Estimated integration points**: 12 files (see [Adding-A-Language.md](Adding-A-Language.md) for the master checklist).

---

## Package

```bash
pip install tree-sitter-swift
python -c "import tree_sitter_swift; print('OK')"
```

Add to `pyproject.toml`:

```toml
"tree-sitter-swift>=0.6.0",  # [FEATURE] Swift language support
```

Add to all three locations: `dependencies`, `[all]`, and `[polyglot]` extras.

---

## Language Enum + Extension Map

```python
# Language enum (both extractor files)
SWIFT = "swift"

# Extension map
".swift": Language.SWIFT,
```

---

## Content-Based Detection Heuristics

Place the Swift block **after** C# and **before** Java (Swift shares some Java-like structure but `var`/`let` + `func` combination is decisive):

```python
# Swift indicators — "func " + "var/let" without C-style types is unambiguous
if any(kw in code for kw in [
    "func ", "var ", "let ", "guard ", "import Foundation", "import UIKit",
    "protocol ", "override func", "@objc",
]):
    # Disambiguate from JS/TS: Swift doesn't have "=>" fat arrow, "const", or "=>"
    if "=>" not in code and "const " not in code:
        return Language.SWIFT
```

**Ordering**: C# → Swift → Go → Kotlin → Java → C++ → Rust → C → JavaScript → Python.

The `"=>"` exclusion distinguishes Swift from TypeScript/JavaScript. `"import Foundation"` and `"import UIKit"` are unambiguous Swift signals.

---

## Key AST Node Mappings

| tree-sitter-swift node | IR node | Notes |
|-----------------------|---------|-------|
| `source_file` | `IRModule` | Root |
| `import_declaration` | `IRImport` | `import Foundation` → `IRImport(module="Foundation")` |
| `function_declaration` | `IRFunctionDef` | `func greet(name: String) -> String` |
| `init_declaration` | `IRFunctionDef` | `init(x: Int)` → `IRFunctionDef(name="init")` |
| `deinit_declaration` | `IRFunctionDef` | `deinit { ... }` → `IRFunctionDef(name="deinit")` |
| `subscript_declaration` | `IRFunctionDef` | `subscript(index: Int) -> Element` → `_metadata["kind"] = "subscript"` |
| `class_declaration` | `IRClassDef` | `class Animal: NSObject` → `_metadata["kind"] = "class"` |
| `struct_declaration` | `IRClassDef` | `struct Point { var x: Double }` → `_metadata["kind"] = "struct"` |
| `enum_declaration` | `IRClassDef` | `enum Direction { case north, south }` → `_metadata["kind"] = "enum"` |
| `protocol_declaration` | `IRClassDef` | `protocol Drawable { func draw() }` → `_metadata["kind"] = "protocol"` |
| `extension_declaration` | (visit body; methods stored with `_metadata["extension_of"]`) | `extension Array { func second() -> Element? }` |
| `variable_declaration` with `var` | `IRAssign` | Top-level or stored property |
| `variable_declaration` with `let` | `IRAssign` | Constant |
| `assignment` | `IRAssign` | |
| `return_statement` | `IRReturn` | |
| `if_statement` | `IRIf` | |
| `if_let_statement` | `IRIf` | `if let x = optional { ... }` → `_metadata["kind"] = "if_let"` |
| `guard_statement` | `IRIf` | `guard let x = y else { return }` → `_metadata["kind"] = "guard"` |
| `switch_statement` | `IRIf` | Each `case` → branch; `_metadata["kind"] = "switch"` |
| `for_statement` | `IRFor` | `for item in collection` |
| `while_statement` | `IRFor` | |
| `repeat_while_statement` | `IRFor` | `_metadata["kind"] = "repeat_while"` |
| `defer_statement` | `IRFor` | `defer { ... }` — executed at scope exit; `_metadata["kind"] = "defer"` |
| `call_expression` | `IRCall` | |
| `closure_expression` | `IRFunctionDef` | `{ (x: Int) -> Int in x + 1 }` → `_metadata["kind"] = "closure"` |
| `computed_property` | `IRFunctionDef` | `var area: Double { get { ... } set { ... } }` → two `IRFunctionDef` nodes for `get` and `set` |

---

## Swift-Specific Implementation Notes

### Extensions — the central challenge

Swift extensions add methods and computed properties to *existing types*, defined separately from the original type:

```swift
struct Point {
    var x: Double
    var y: Double
}

extension Point {
    func distance(to other: Point) -> Double {
        let dx = x - other.x
        let dy = y - other.y
        return (dx * dx + dy * dy).squareRoot()
    }
}
```

The `extension_declaration` has a `type_identifier` indicating the extended type. For each `function_declaration` (or `init_declaration`) inside the extension body, emit `IRFunctionDef` at module level with:

```python
fn._metadata["extension_of"] = "Point"
fn._metadata["kind"] = "extension_method"
```

This mirrors Go's method and Rust's impl approach — methods are at module level with a metadata pointer back to their type.

### Protocol conformance in extensions

Extensions frequently declare conformance:

```swift
extension Point: CustomStringConvertible {
    var description: String { "(\(x), \(y))" }
}
```

The `extension_declaration` has both `type_identifier` (the extended type) and `type_inheritance_clause` (the conformed protocol). Store both:

```python
fn._metadata["extension_of"] = "Point"
fn._metadata["conforms_to"] = "CustomStringConvertible"
```

### Multiple initializer forms

Swift has several init variants:

```swift
init(x: Int, y: Int) { ... }               // designated
convenience init(origin: Bool) { ... }      // delegating
required init(coder: NSCoder) { ... }       // required
init?(data: Data) { ... }                   // failable (returns Optional)
```

All map to `IRFunctionDef(name="init")`. Store the variant in `_metadata`:
- `_metadata["init_kind"] = "designated"` / `"convenience"` / `"required"` / `"failable"`

For failable inits (`init?`), also set `_metadata["failable"] = True`.

### Computed properties

```swift
var area: Double {
    get { width * height }
    set { width = newValue / height }
}
```

`computed_property` has `getter` and/or `setter` children. Map the property as two `IRFunctionDef` nodes:
- `IRFunctionDef(name="<property>_get", _metadata={"kind": "getter", "property": "area"})`
- `IRFunctionDef(name="<property>_set", _metadata={"kind": "setter", "property": "area"})`

Or, for simpler read-only properties (`var x: Int { return 42 }`), emit a single `IRFunctionDef` with `_metadata["kind"] = "computed_property"`.

### Property observers

```swift
var score: Int = 0 {
    willSet { print("Will set to \(newValue)") }
    didSet  { print("Was \(oldValue)") }
}
```

Map `willSet_clause` and `didSet_clause` to `IRFunctionDef` with `_metadata["kind"] = "willSet"` / `"didSet"`.

### `guard` statements

```swift
guard let user = session.user else {
    throw AuthError.notLoggedIn
}
```

Map `guard_statement` to `IRIf` with `_metadata["kind"] = "guard"`. The `else` body is always present (required by Swift) and contains the early-exit logic.

### Argument labels

Swift functions have external and internal parameter names:

```swift
func move(from start: Point, to end: Point) -> Path
```

`from` and `to` are external labels (used at the call site), while `start` and `end` are internal names. When building `IRParameter`, store the internal name as `IRParameter.name` and the external label in `_metadata["label"]`.

### `@` attributes

Swift uses attributes for many purposes:

```swift
@objc func bridgedMethod() { }
@available(iOS 14, *)
@discardableResult
```

Store the list of attribute strings in `fn._metadata["attributes"]`. Do not try to interpret them — just preserve them for analysis tools.

---

## Block Structure

Swift function bodies use `code_block` nodes:

```
function_declaration
  ├── simple_identifier         ("greet")
  ├── function_value_parameters
  │   └── parameter             (name: String)
  ├── type_annotation           (-> String)
  └── function_body
        └── code_block
              └── statements
```

Iterate `code_block.named_children` (or `statements.named_children` if a `statements` wrapper node is present — check your tree-sitter-swift version).

For class/struct bodies:

```
class_declaration
  ├── type_identifier           ("Animal")
  ├── type_inheritance_clause   (: NSObject)
  └── class_body
        ├── variable_declaration
        └── function_declaration
```

Iterate `class_body.named_children` for member declarations.

---

## `_parse_swift()` Method

```python
def _parse_swift(self) -> None:
    """Parse Swift code using tree-sitter-swift. [FEATURE]"""
    from code_scalpel.ir.normalizers.swift_normalizer import SwiftNormalizer

    normalizer = SwiftNormalizer()
    self._ir_module = normalizer.normalize(self.code)
```

---

## limits.toml

Add `"swift"` to the `languages` arrays in all three tier sections of `analyze_code` and `unified_sink_detect`.

---

## Tests to Write

### `tests/languages/test_swift_parser.py`

Cover all of the following scenarios:

1. **Extension detection** — `.swift` maps to `Language.SWIFT`
2. **Content detection** — `"func "` + absence of `"=>"` identifies Swift
3. **Function extraction** — `func greet(name: String) -> String`
4. **Class extraction** — `class Animal: NSObject`
5. **Struct extraction** — `struct Point { var x: Double; var y: Double }` → `_metadata["kind"] = "struct"`
6. **Protocol extraction** — `protocol Drawable { func draw() }` → `_metadata["kind"] = "protocol"`
7. **Enum extraction** — `enum Direction { case north, south }` → `_metadata["kind"] = "enum"`
8. **Extension method extraction** — method from `extension Point` with `_metadata["extension_of"] = "Point"`
9. **Init extraction** — `init(x: Int, y: Int)` → `IRFunctionDef(name="init")`
10. **Failable init** — `init?(data: Data)` → `_metadata["failable"] = True`
11. **Import extraction** — `import Foundation` → `IRImport(module="Foundation")`
12. **Property declaration** — `var name: String` → `IRAssign`
13. **Computed property** — `var area: Double { ... }` → `IRFunctionDef` with getter/setter metadata
14. **Closure expression** — `{ (x: Int) in x + 1 }` → `IRFunctionDef` with `_metadata["kind"] = "closure"`
15. **Guard statement** — `guard let x = y else { return }` → `IRIf` with `_metadata["kind"] = "guard"`
16. **Missing symbol** — returns graceful failure, not exception
17. **Both extractor modules agree** on `.swift` → `Language.SWIFT`

### `tests/languages/test_polyglot_support.py`

- Add `"swift"` to `TestAnalyzeCodeLanguageSupport` parametrize
- Add `"swift"` to `TestUnifiedSinkDetectLanguageSupport` parametrize
- Add matrix rows for Swift
- Add `.swift` to `TestLanguageDetection.test_file_extension_detection`

---

## Verification Commands

```bash
pip install tree-sitter-swift

# 1. Normalizer smoke test
python -c "
from code_scalpel.ir.normalizers.swift_normalizer import SwiftNormalizer
from code_scalpel.ir.nodes import IRFunctionDef, IRClassDef
n = SwiftNormalizer()
code = '''
import Foundation

struct Point {
    var x: Double
    var y: Double
}

extension Point {
    func distance(to other: Point) -> Double {
        let dx = x - other.x
        let dy = y - other.y
        return (dx * dx + dy * dy).squareRoot()
    }
}

func greet(name: String) -> String {
    return \"Hello, \" + name
}
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
code = 'func hello() -> String { return \"hi\" }\nfunc world() { print(\"world\") }'
e = PolyglotExtractor(code, language=Language.SWIFT)
r = e.extract('function', 'hello')
print('OK' if r.success else r.error)
"

# 3. Run test suite
pytest tests/languages/test_swift_parser.py -v
pytest tests/languages/ -v --tb=short
```

---

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Swift detected as TypeScript | Both use `var`, `let`, and `func` / `function` | Add `"=>" not in code` exclusion to Swift heuristic; TypeScript heavily uses arrow functions |
| Extension methods not found | `extension_declaration` body not visited | Add `visit_extension_declaration()` and emit functions at module level with `_metadata["extension_of"]` |
| Multiple inits conflict | All map to `IRFunctionDef(name="init")` | Expected — differentiate via `_metadata["init_kind"]` and `_metadata["failable"]` |
| Computed properties crash | `computed_property` node structure varies by version | Probe actual node type with the tree-sitter playground before writing the visitor |
| Argument labels not captured | External parameter label treated as part of identifier | Check for `external_parameter_name` field on `parameter` node |
| `@` attributes cause unknown node type | Attribute nodes precede the declaration | Skip attribute nodes gracefully; collect attribute strings into `_metadata["attributes"]` |
| Protocol default implementations missing | Protocol body methods are `function_declaration` without a body | Emit `IRFunctionDef` for both required (no body) and default (with body) protocol methods |
| `guard` crashes because it requires `else` | `else_clause` is mandatory in Swift `guard` | Always visit `guard_statement.else_body` — it is never absent |

---

## Version Note

The `tree-sitter-swift` Python binding has had less maintenance activity than the other grammars. Before starting, verify the currently published version on PyPI handles your target Swift syntax (Swift 5.9+). If the binding lags behind the language spec, note it in the implementation file header and pin to the tested version in `pyproject.toml`.

---

## Phase 2 — Static Analysis Tool Parsers

The `swift_parsers/` directory is pre-scaffolded with Phase 1 framework. All 4 tool parsers must be fully implemented before Swift is considered complete.

### Tools to implement

| File | Tool | Output format | Type |
|------|------|--------------|------|
| `swift_parsers_SwiftLint.py` | SwiftLint | JSON (`swiftlint lint --reporter json`) | Free — execute + parse |
| `swift_parsers_swiftformat.py` | SwiftFormat | text diff | Free — execute + parse |
| `swift_parsers_sourcekitten.py` | SourceKitten | JSON (`sourcekitten doc ...`) | Free — execute + parse |
| `swift_parsers_Tailor.py` | Tailor | JSON / XML | Free — execute + parse |

### Priority order

1. **SwiftLint** — universal Swift linter; JSON output; CWE-mappable rule violations
2. **SwiftFormat** — formatting; check-only mode returns diff
3. **SourceKitten** — documentation extraction and IDE-level semantic info
4. **Tailor** — additional style enforcement

### SwiftLint implementation notes

SwiftLint JSON output format:
```json
[{"character":5,"file":"/path/to/File.swift","line":12,"reason":"Trailing whitespace.",
  "rule_id":"trailing_whitespace","severity":"Warning","type":"Trailing Whitespace"}]
```

```python
def execute_swiftlint(self, paths: list[Path], config=None) -> list[SwiftLintViolation]:
    if shutil.which("swiftlint") is None:
        return []
    cmd = ["swiftlint", "lint", "--reporter", "json"] + [str(p) for p in paths]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return self.parse_json_output(result.stdout)

def parse_json_output(self, output: str) -> list[SwiftLintViolation]:
    import json
    items = json.loads(output or "[]")
    return [SwiftLintViolation(
        file_path=item["file"],
        line_number=item["line"],
        column=item.get("character", 0),
        rule_id=item["rule_id"],
        message=item["reason"],
        severity=item["severity"],
    ) for item in items]
```

### Platform note

SwiftLint and SwiftFormat are macOS-primary tools. Implement graceful degradation on Linux (check `sys.platform` and `shutil.which`). SourceKitten requires Xcode command-line tools (`xcode-select`) — document this requirement clearly and return `[]` if unavailable.

### SwiftParserRegistry

```python
class SwiftParserRegistry:
    def __init__(self):
        self._parsers = {
            "swiftlint":   SwiftLintParser,
            "swiftformat": SwiftFormatParser,
            "sourcekitten": SourceKittenParser,
            "tailor":       TailorParser,
        }
```

### Tests (`tests/languages/test_swift_tool_parsers.py`)

- `test_swiftlint_parse_json_output()` — fixture JSON
- `test_swiftlint_graceful_on_linux()` — skip if `swiftlint` not available
- `test_swiftformat_parse_diff_output()` — fixture diff text
- `test_registry_get_parser_swiftlint()` — factory test
- `test_graceful_degradation_no_swiftlint()` — returns `[]` when not installed
