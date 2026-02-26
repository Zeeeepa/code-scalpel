# Release Notes — Code Scalpel v2.0.0

**Release Date:** February 24, 2026
**Version:** 2.0.0 (Major)
**Previous:** 1.5.0

---

## Executive Summary

Code Scalpel v2.0.0 delivers **full C, C++, and C# language support**, extending the polyglot
parser from four languages (Python, JavaScript, TypeScript, Java) to **seven**.  Any project
written in C, C++, or C# — game engines, Win32 applications, .NET services, embedded firmware,
systems software — can now use all Code Scalpel MCP tools (`extract_code`, `analyze_code`,
`get_call_graph`, `security_scan`, etc.) with the same surgical precision previously available
only for high-level languages.

The release also resolves four latent normalizer correctness bugs discovered by the new
real-world pattern test suite.

---

## New Features

### C Language Support

**Normalizer:** `CVisitor` + `CNormalizer` in `src/code_scalpel/ir/normalizers/c_normalizer.py`
**Parser:** `tree-sitter-c>=0.21.0`

Supported constructs:

| Construct | Notes |
|---|---|
| Function definitions | `int`, `void`, `float*`, variadic (`...`), `static`, `extern`, `const` |
| Function pointer typedefs | `typedef int (*Fn)(void*, int)` |
| Structs (named, typedef, anonymous) | Fields surfaced as `IRAssign` stubs |
| Unions | Including anonymous unions nested inside structs |
| Enums | Named and typedef forms with explicit values |
| Bitfields | `unsigned int dirty:1` |
| Preprocessor | `#include <...>`, `#include "..."`, `#define` (int, float, hex, string, functional) |
| Array parameters | `void fill(float arr[], int n)` |
| Multi-level pointers | `char **argv`, `float ***voxel` |
| Nested structs | BVH nodes, D3D math structs |

**Extensions recognized:** `.c`, `.h`

**End-to-end extraction example:**
```python
from code_scalpel.code_parsers.extractor import PolyglotExtractor, Language

ext = PolyglotExtractor.from_file("renderer.c")
result = ext.extract("function", "vec3_dot")
# result.success == True, result.code contains the function body
```

---

### C++ Language Support

**Normalizer:** `CppVisitor` + `CppNormalizer` (extends `CVisitor`) in `cpp_normalizer.py`
**Parser:** `tree-sitter-cpp>=0.21.0`

Supported constructs (in addition to all C constructs):

| Construct | Notes |
|---|---|
| Classes | Inline/out-of-line methods, access specifiers skipped |
| Inheritance | Single and multiple (`class C : public A, public B`) |
| Virtual / override / pure virtual | `= 0` abstract methods |
| Operator overloading | `operator+`, `operator==`, etc. surfaced as `IRFunctionDef` |
| Namespaces | Transparent fold; children tagged with `_metadata["namespace"]` |
| Anonymous namespaces | `namespace { ... }` |
| Templates | Class and function templates; `template_params` in `_metadata` |
| Variadic templates | `template<typename... Args>` |
| `enum class` | Scoped enums |
| `constexpr` / `inline` functions | Surfaced as normal `IRFunctionDef` |
| Move semantics | `T&&`, `noexcept` move constructors |
| `= delete` / `= default` | Special member declarations |
| Nested classes | Unfolded from `field_declaration` wrappers |
| Qualified method definitions | `Vec3::dot(...)` → name `"Vec3.dot"` |
| Lambda expressions | Outer function still extracted |
| Trailing return types | `auto dot() -> float` |

**Extensions recognized:** `.cpp`, `.cc`, `.cxx`, `.c++`, `.hpp`, `.hxx`, `.hh`, `.h++`, `.inl`

**Extraction example:**
```python
ext = PolyglotExtractor.from_file("vec3.hpp")
result = ext.extract("class", "Vec3")         # full class
result = ext.extract("function", "lerp")      # template function
```

---

### C# Language Support

**Normalizer:** `CSharpVisitor` + `CSharpNormalizer` in `csharp_normalizer.py`
**Parser:** `tree-sitter-c-sharp>=0.21.0`
**Adapter:** `CSharpAdapter` (full implementation, was `NotImplementedError` stub)

Supported constructs:

| Construct | Notes |
|---|---|
| Classes / structs / records / interfaces | Single and multiple inheritance |
| `record struct` | Value records |
| `partial` classes | Modifier preserved |
| Enums | Named values surfaced as `IRAssign` |
| Methods | `async`/`await`, extension methods (`this T`), tuple returns, generic with constraints |
| Operator overloads | `operator+`, `operator==` → `IRFunctionDef` named `"operator+"` |
| Properties | Auto-properties, full get/set |
| Constructors | Standard and primary constructors |
| Indexers | `this[int i]` |
| Fields | Including `const`, `readonly`, `static` |
| Events / delegates | Parsed without crash |
| Namespaces | Transparent fold; children tagged with `_metadata["namespace"]` |
| Using directives | → `IRImport` |
| Control flow | `if`, `while`, `for`, `foreach`, `switch`, `try` |
| Pattern-matching switch | `switch (x) { case Circle c => ... }` |
| Nullable types | `string?`, `int?` |
| Tuple return types | `(int row, int col) IndexOf(int value)` |
| Generics with constraints | `where T : IComparable<T>` |
| Top-level statements (C# 9+) | `global_statement` unwrapped |

**Extensions recognized:** `.cs`

**Extraction example:**
```python
ext = PolyglotExtractor.from_file("PlayerController.cs")
result = ext.extract("class", "PlayerController")
result = ext.extract("method", "PlayerController.Update")
```

---

## Bug Fixes

### `IRIf`/`IRWhile` wrong constructor keyword in C# normalizer
**Impact:** Any C# source file containing an `if` statement inside a method body raised
`TypeError: IRIf.__init__() got an unexpected keyword argument 'condition'`.
The IR dataclasses use `test=`, not `condition=`.  This made the Unity
`MonoBehaviour` smoke test (and any real-world C# class with branching) crash.

### Tuple return type dropped in `_parse_method_children`
**Impact:** Methods with tuple return types such as `(int row, int col) IndexOf(int value)`
had `IndexOf` treated as the return type and the method name was parsed as `None`, causing
the method to be silently discarded.  Root cause: `tuple_type` was absent from `_TYPE_NODES`.

### C# `operator_declaration` silently ignored
**Impact:** Operator overloads (`operator+`, `operator==`, `operator*`, etc.) in structs and
classes were never surfaced as `IRFunctionDef` nodes.  The visitor dispatch table had no entry
for `operator_declaration`.

### C++ nested class extraction broken
**Impact:** A class defined inside another class (e.g. `class SceneGraph { class Node {...}; }`)
was invisible to `extract_code` and did not appear in `IRClassDef.body`.  Root cause: in
`tree-sitter-cpp` a nested type declaration is wrapped as `field_declaration → class_specifier`.
The `_parse_class_body` loop dispatched `field_declaration` generically and the inner
`class_specifier` was never visited.  Fixed by adding `_extract_nested_type()` which unwraps
the pattern before falling through to the generic dispatcher.

---

## Test Suite

| Suite | Tests | Focus |
|---|---|---|
| `tests/languages/test_c_cpp_parsers.py` | 123 | C and C++ unit tests + real-world patterns |
| `tests/languages/test_csharp_parser.py` | 84 | C# unit tests + real-world patterns |
| `tests/languages/` total | 262 | All language tests |
| Full suite (`tests/`) | **7,575** | All tests |

All 7,575 tests pass.  Pre-existing coverage: 94.86% combined (96.28% stmt, 90.95% branch).

Real-world pattern classes added:

- `TestCRealWorldPatterns` — Win32 headers, function pointer callbacks, bitfields, anonymous unions
- `TestCppRealWorldPatterns` — full `Vec3` with operators, virtual hierarchies, RAII containers
- `TestCSharpRealWorldPatterns` — Unity `MonoBehaviour`, async services, extension methods, LINQ-ready patterns

---

## Migration Guide

No breaking changes.  All existing APIs remain identical.

**New optional dependency groups** (already present in `dependencies` since v1.5.0):
```
pip install "codescalpel[polyglot]"   # includes tree-sitter-c, tree-sitter-cpp, tree-sitter-c-sharp
```

**Language detection** is automatic from file extension.  Explicit override:
```python
PolyglotExtractor(source, language=Language.C)
PolyglotExtractor(source, language=Language.CPP)
PolyglotExtractor(source, language=Language.CSHARP)
```

---

## Supported Languages — v2.0.0

| Language | Extensions | Normalizer |
|---|---|---|
| Python | `.py` | `PythonNormalizer` |
| JavaScript | `.js`, `.mjs`, `.cjs` | `JavaScriptNormalizer` |
| TypeScript | `.ts`, `.tsx` | `TypeScriptNormalizer` |
| Java | `.java` | `JavaNormalizer` |
| **C** | `.c`, `.h` | `CNormalizer` *(new)* |
| **C++** | `.cpp`, `.cc`, `.cxx`, `.c++`, `.hpp`, `.hxx`, `.hh`, `.h++`, `.inl` | `CppNormalizer` *(new)* |
| **C#** | `.cs` | `CSharpNormalizer` *(new)* |

---

## Known Limitations

- C/C++ preprocessor macro bodies beyond simple integer, float, hex, and string literals are
  parsed without expansion (macros with expressions are stored as `IRAssign` with `None` value).
- C++ lambda capture lists are not extracted into IR; only the outer function containing the
  lambda is surfaced.
- C# LINQ query expression syntax (`from x in y select z`) is not parsed into dedicated IR nodes;
  the expression is treated as an opaque statement and the containing method is still surfaced.
- `unsafe` / `fixed` blocks in C# parse without crash but pointer arithmetic inside is not
  tracked in taint analysis.

---

*Code Scalpel v2.0.0 — February 24, 2026*
