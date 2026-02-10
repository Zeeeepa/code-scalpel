# Parser Expansion Requirements

**Date**: 2026-02-06
**Status**: Investigation Complete
**Purpose**: Document current parser architecture and requirements for implementing 7 missing language parsers

---

## Executive Summary

Code Scalpel has a well-designed parser architecture with adapters for multiple languages. Currently, **4 languages are fully implemented** (Python, JavaScript, TypeScript, Java) and **7 languages are stubbed** (C++, C#, Go, Kotlin, PHP, Ruby, Swift).

All stub adapters have the same structure: they raise `NotImplementedError` with helpful TODO comments explaining what needs to be implemented.

---

## Current Parser Architecture

### Core Components

1. **interface.py** - Defines the IParser contract
   - Abstract methods: `parse()`, `get_functions()`, `get_classes()`
   - Language enum (expandable)
   - ParseResult dataclass

2. **factory.py** - ParserFactory for language detection and parser instantiation
   - Registers parsers by Language enum
   - Auto-registration system for available parsers
   - Extension-to-language mapping
   - `from_file()` convenience method

3. **base_parser.py** - BaseParser abstract class with shared utilities
   - Comment removal
   - Whitespace normalization
   - Complexity calculation
   - Preprocessing logic

4. **Adapters** - Language-specific IParser implementations
   - Located in `src/code_scalpel/code_parsers/adapters/`
   - Each adapter wraps a language-specific parser
   - Converts language-specific AST to unified interface

---

## Language Implementation Status

### ✅ Fully Implemented (4 languages)

| Language | Adapter | Backend | Status |
|----------|---------|---------|--------|
| **Python** | `PythonParser` | `ast` (stdlib) | ✅ Complete |
| **JavaScript** | `JavaScriptParserAdapter` | `esprima` | ✅ Complete |
| **TypeScript** | `TypeScriptParserAdapter` | `tree-sitter` or `esprima` | ✅ Complete |
| **Java** | `JavaParserAdapter` | `javalang` | ✅ Complete |

### ❌ Stubbed (7 languages)

| Language | Adapter File | Status | Suggested Backend |
|----------|-------------|--------|-------------------|
| **C++** | `cpp_adapter.py` | ❌ Stub | tree-sitter-cpp, libclang, or clang bindings |
| **C#** | `csharp_adapter.py` | ❌ Stub | tree-sitter-c-sharp or Roslyn |
| **Go** | `go_adapter.py` | ❌ Stub | tree-sitter-go or go/parser stdlib |
| **Kotlin** | `kotlin_adapter.py` | ❌ Stub | tree-sitter-kotlin |
| **PHP** | `php_adapter.py` | ❌ Stub | tree-sitter-php or php-parser |
| **Ruby** | `ruby_adapter.py` | ❌ Stub | tree-sitter-ruby or ripper (stdlib) |
| **Swift** | `swift_adapter.py` | ❌ Stub | tree-sitter-swift or lib-syntax |

---

## IParser Interface Contract

Every language adapter must implement these methods:

```python
class IParser(ABC):
    """Interface for language-specific parsers."""

    @abstractmethod
    def parse(self, code: str) -> ParseResult:
        """Parse source code into an AST.

        Returns:
            ParseResult with:
                - ast: Language-specific AST structure
                - errors: List of parsing errors (dicts with message, line, column)
                - warnings: List of warning strings
                - metrics: Dict with complexity and other metrics
                - language: Language enum value
        """
        pass

    @abstractmethod
    def get_functions(self, ast_tree: Any) -> List[str]:
        """Extract list of function/method names from AST."""
        pass

    @abstractmethod
    def get_classes(self, ast_tree: Any) -> List[str]:
        """Extract list of class/struct/type names from AST."""
        pass
```

---

## Example: Python Parser Implementation

**File**: `src/code_scalpel/code_parsers/python_parser.py`

```python
class PythonParser(IParser):
    """Python implementation of the parser interface."""

    def parse(self, code: str) -> ParseResult:
        errors = []
        metrics = {}
        try:
            tree = ast.parse(code)
            metrics["complexity"] = self._calculate_complexity(tree)
            return ParseResult(
                ast=tree,
                errors=[],
                warnings=[],
                metrics=metrics,
                language=Language.PYTHON,
            )
        except SyntaxError as e:
            errors.append({
                "type": "SyntaxError",
                "message": e.msg,
                "line": e.lineno,
                "column": e.offset,
                "text": e.text.strip() if e.text else None,
            })
            return ParseResult(
                ast=None,
                errors=errors,
                warnings=[],
                metrics={},
                language=Language.PYTHON,
            )

    def get_functions(self, ast_tree: Any) -> List[str]:
        if not isinstance(ast_tree, ast.AST):
            return []
        return [
            node.name
            for node in ast.walk(ast_tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

    def get_classes(self, ast_tree: Any) -> List[str]:
        if not isinstance(ast_tree, ast.AST):
            return []
        return [
            node.name
            for node in ast.walk(ast_tree)
            if isinstance(node, ast.ClassDef)
        ]

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
```

---

## Example: JavaScript Parser Implementation

**File**: `src/code_scalpel/code_parsers/adapters/javascript_adapter.py`

```python
class JavaScriptParserAdapter(IParser):
    """Adapter that wraps JavaScriptParser (esprima) to implement IParser interface."""

    def __init__(self):
        """Initialize the JavaScript parser adapter."""
        if not JAVASCRIPT_PARSER_AVAILABLE or EsprimaParser is None:
            raise ImportError(
                "JavaScriptParser not available. Install esprima: pip install esprima"
            )
        self._parser = EsprimaParser()
        self._last_ast = None
        self._last_functions = []
        self._last_classes = []

    def parse(self, code: str) -> ParseResult:
        """Parse JavaScript code into an AST."""
        try:
            # Use the underlying parser's internal parse method
            internal_result = self._parser._parse_javascript(code)

            # Cache the AST
            self._last_ast = internal_result.ast

            # Extract names from AST
            self._extract_names_from_ast(internal_result.ast)

            # Convert to IParser ParseResult format
            return ParseResult(
                ast=internal_result.ast,
                errors=self._convert_errors(internal_result.errors),
                warnings=getattr(internal_result, "warnings", []) or [],
                metrics=getattr(internal_result, "metrics", {}) or {},
                language=Language.JAVASCRIPT,
            )
        except Exception as e:
            return ParseResult(
                ast=None,
                errors=[{"message": str(e), "line": 0, "column": 0}],
                warnings=[],
                metrics={},
                language=Language.JAVASCRIPT,
            )

    def get_functions(self, ast_tree: Any) -> List[str]:
        """Get list of function names from the AST."""
        if ast_tree is None:
            return self._last_functions

        self._extract_names_from_ast(ast_tree)
        return self._last_functions

    def get_classes(self, ast_tree: Any) -> List[str]:
        """Get list of class names from the AST."""
        if ast_tree is None:
            return self._last_classes

        self._extract_names_from_ast(ast_tree)
        return self._last_classes
```

---

## Implementation Requirements per Language

### 1. C++ Parser (Priority: HIGH)

**File**: `src/code_scalpel/code_parsers/adapters/cpp_adapter.py` (currently stub)

**Recommended Backend**: tree-sitter-cpp (most mature)

**Requirements**:
- ✅ Parse C++11/14/17/20/23 syntax
- ✅ Handle templates and template specializations
- ✅ Extract functions, classes, structs, namespaces
- ✅ Support header files (.h, .hpp, .hxx)
- ✅ Handle complex preprocessor directives (#include, #define, #ifdef)

**Implementation Steps**:
1. Install py-tree-sitter and tree-sitter-cpp
2. Create CppParserAdapter that:
   - Initializes tree-sitter C++ language
   - Implements parse() with tree-sitter parsing
   - Implements get_functions() extracting function declarations/definitions
   - Implements get_classes() extracting class/struct/union declarations
3. Add Language.CPP to interface.py enum (if not present)
4. Register CppParserAdapter in factory.py
5. Add tests in tests/core/parsers/test_cpp_parser.py

**Complexity**: HIGH (C++ syntax complexity, templates, preprocessor)

---

### 2. C# Parser (Priority: HIGH)

**File**: `src/code_scalpel/code_parsers/adapters/csharp_adapter.py` (currently stub)

**Recommended Backend**: tree-sitter-c-sharp (good support)

**Requirements**:
- ✅ Parse C# 7.0+ syntax
- ✅ Handle LINQ expressions
- ✅ Extract classes, interfaces, structs, enums
- ✅ Support properties and events
- ✅ Handle async/await patterns

**Implementation Steps**:
1. Install py-tree-sitter and tree-sitter-c-sharp
2. Create CSharpParserAdapter following JavaScript adapter pattern
3. Add Language.CSHARP to interface.py enum
4. Register in factory.py
5. Add tests

**Complexity**: MEDIUM (LINQ can be tricky, but tree-sitter handles it)

---

### 3. Go Parser (Priority: HIGH)

**File**: `src/code_scalpel/code_parsers/adapters/go_adapter.py` (currently stub)

**Recommended Backend**: tree-sitter-go (excellent support)

**Alternative**: go/parser (requires cgo, more complex)

**Requirements**:
- ✅ Parse Go 1.18+ syntax (generics)
- ✅ Extract functions, methods, structs, interfaces
- ✅ Handle goroutines and channels
- ✅ Support package declarations

**Implementation Steps**:
1. Install py-tree-sitter and tree-sitter-go
2. Create GoParserAdapter
3. Map Go "funcs" to IParser functions
4. Map structs/interfaces to IParser classes
5. Add Language.GO to interface.py
6. Register in factory.py
7. Add tests

**Complexity**: LOW-MEDIUM (Go syntax is simple, tree-sitter support excellent)

---

### 4. Kotlin Parser (Priority: MEDIUM)

**File**: `src/code_scalpel/code_parsers/adapters/kotlin_adapter.py` (currently stub)

**Recommended Backend**: tree-sitter-kotlin

**Requirements**:
- ✅ Parse Kotlin 1.9+ syntax
- ✅ Handle data classes, sealed classes
- ✅ Extract functions, classes, objects, interfaces
- ✅ Support extension functions
- ✅ Handle coroutines

**Implementation Steps**:
1. Install py-tree-sitter and tree-sitter-kotlin
2. Create KotlinParserAdapter
3. Handle Kotlin's unique constructs (data classes, companion objects)
4. Add Language.KOTLIN to interface.py
5. Register in factory.py
6. Add tests

**Complexity**: MEDIUM (Kotlin has many language features)

---

### 5. PHP Parser (Priority: MEDIUM)

**File**: `src/code_scalpel/code_parsers/adapters/php_adapter.py` (currently stub)

**Recommended Backend**: tree-sitter-php (good support)

**Alternative**: php-parser (Python package)

**Requirements**:
- ✅ Parse PHP 7.4+ and PHP 8.x syntax
- ✅ Handle namespaces and traits
- ✅ Extract functions, classes, traits, interfaces
- ✅ Support closures and arrow functions

**Implementation Steps**:
1. Install py-tree-sitter and tree-sitter-php
2. Create PHPParserAdapter
3. Handle PHP's HTML embedding (parse PHP blocks)
4. Add Language.PHP to interface.py
5. Register in factory.py
6. Add tests

**Complexity**: MEDIUM (PHP's HTML embedding adds complexity)

---

### 6. Ruby Parser (Priority: MEDIUM)

**File**: `src/code_scalpel/code_parsers/adapters/ruby_adapter.py` (currently stub)

**Recommended Backend**: tree-sitter-ruby (good support)

**Alternative**: ripper (Ruby stdlib, requires Ruby installation)

**Requirements**:
- ✅ Parse Ruby 3.x syntax
- ✅ Extract methods, classes, modules
- ✅ Handle blocks and procs
- ✅ Support metaprogramming constructs

**Implementation Steps**:
1. Install py-tree-sitter and tree-sitter-ruby
2. Create RubyParserAdapter
3. Map Ruby methods to IParser functions
4. Map classes/modules to IParser classes
5. Add Language.RUBY to interface.py
6. Register in factory.py
7. Add tests

**Complexity**: MEDIUM (Ruby's metaprogramming features can be tricky)

---

### 7. Swift Parser (Priority: LOW)

**File**: `src/code_scalpel/code_parsers/adapters/swift_adapter.py` (currently stub)

**Recommended Backend**: tree-sitter-swift

**Requirements**:
- ✅ Parse Swift 5.x syntax
- ✅ Extract functions, classes, structs, protocols, extensions
- ✅ Handle optionals and generics
- ✅ Support SwiftUI syntax

**Implementation Steps**:
1. Install py-tree-sitter and tree-sitter-swift
2. Create SwiftParserAdapter
3. Handle Swift's protocol-oriented programming
4. Add Language.SWIFT to interface.py
5. Register in factory.py
6. Add tests

**Complexity**: MEDIUM-HIGH (Swift's modern features, SwiftUI syntax)

---

## Tool-Specific Parsers (Separate from AST Parsers)

**Important Note**: Each language directory (e.g., `cpp_parsers/`, `go_parsers/`) contains many tool-specific parsers:

- `cpp_parsers/cpp_parsers_Cppcheck.py` - Parses Cppcheck OUTPUT
- `go_parsers/go_parsers_golint.py` - Parses golint OUTPUT
- `java_parsers/java_parsers_Maven.py` - Parses Maven OUTPUT

These are **NOT** AST parsers. They parse the JSON/XML output of static analysis tools.

**Do not confuse these with the core language adapters.**

The core language adapters (in `adapters/`) parse the actual source code.

---

## Implementation Priority Ranking

Based on strategic value and ecosystem size:

1. **C++** (HIGH) - Huge ecosystem, enterprise demand
2. **Go** (HIGH) - Growing ecosystem, cloud-native focus
3. **C#** (HIGH) - Enterprise demand, .NET ecosystem
4. **PHP** (MEDIUM) - Large web ecosystem
5. **Kotlin** (MEDIUM) - Android development, JVM ecosystem
6. **Ruby** (MEDIUM) - Rails ecosystem, declining but stable
7. **Swift** (LOW) - iOS/macOS only, smaller market

---

## Shared Implementation Pattern

All 7 adapters should follow this pattern:

1. **Choose tree-sitter backend** (recommended for all)
   - Consistent API across languages
   - No external dependencies beyond Python
   - Well-maintained grammars

2. **Implement CLA_adapter.py**:
   ```python
   class CppParserAdapter(IParser):
       def __init__(self):
           # Initialize tree-sitter parser
           self._parser = self._init_treesitter()
           self._last_ast = None

       def parse(self, code: str) -> ParseResult:
           try:
               tree = self._parser.parse(bytes(code, "utf8"))
               return ParseResult(
                   ast=tree.root_node,
                   errors=[],
                   warnings=[],
                   metrics=self._calculate_metrics(tree),
                   language=Language.CPP,
               )
           except Exception as e:
               return ParseResult(
                   ast=None,
                   errors=[{"message": str(e), "line": 0, "column": 0}],
                   warnings=[],
                   metrics={},
                   language=Language.CPP,
               )

       def get_functions(self, ast_tree: Any) -> List[str]:
           # Query tree-sitter AST for function declarations
           query = self._language.query("""
               (function_definition
                   declarator: (function_declarator
                       declarator: (identifier) @func-name))
           """)
           matches = query.captures(ast_tree)
           return [node.text.decode("utf8") for node, _ in matches]

       def get_classes(self, ast_tree: Any) -> List[str]:
           # Query tree-sitter AST for class declarations
           query = self._language.query("""
               (class_specifier
                   name: (type_identifier) @class-name)
           """)
           matches = query.captures(ast_tree)
           return [node.text.decode("utf8") for node, _ in matches]
   ```

3. **Register in factory.py**:
   ```python
   def _register_available_parsers() -> None:
       try:
           from .adapters.cpp_adapter import CppParserAdapter
           ParserFactory.register_parser(Language.CPP, CppParserAdapter)
       except ImportError:
           pass
   ```

4. **Add tests**:
   - Create `tests/core/parsers/test_cpp_parser.py`
   - Test parsing valid code
   - Test handling syntax errors
   - Test function extraction
   - Test class extraction

---

## Dependency Installation

For tree-sitter-based implementations:

```bash
pip install py-tree-sitter
pip install tree-sitter-cpp
pip install tree-sitter-c-sharp
pip install tree-sitter-go
pip install tree-sitter-kotlin
pip install tree-sitter-php
pip install tree-sitter-ruby
pip install tree-sitter-swift
```

**Note**: These are PyPI packages that bundle the tree-sitter grammars.

---

## Testing Requirements

Each language parser needs:

1. **Unit tests** (`tests/core/parsers/test_{lang}_parser.py`):
   - Test parsing valid code samples
   - Test handling syntax errors
   - Test function extraction
   - Test class extraction
   - Test complexity metrics

2. **Integration tests**:
   - Test with real-world code samples
   - Test with Code Scalpel tools (analyze_code, extract_code)

3. **Test fixtures**:
   - Add sample files in `tests/fixtures/sample_projects/{lang}/`
   - Include edge cases (generics, templates, etc.)

---

## Estimated Effort

Per language (assuming tree-sitter backend):

- **Research & setup**: 2-4 hours
- **Adapter implementation**: 6-10 hours
- **Tree-sitter query development**: 4-8 hours
- **Testing**: 4-6 hours
- **Documentation**: 2-3 hours

**Total per language**: 18-31 hours

**Total for all 7 languages**: 126-217 hours (3.5-6 months for 1 developer at 40 hrs/week)

If parallelized (2 developers): 1.75-3 months

---

## Success Criteria

For each language, the adapter is considered complete when:

- ✅ `parse()` successfully parses valid source code
- ✅ `parse()` returns errors for invalid syntax
- ✅ `get_functions()` extracts function/method names
- ✅ `get_classes()` extracts class/struct/type names
- ✅ Complexity metrics are calculated
- ✅ Registered in ParserFactory
- ✅ All tests pass (90%+ coverage)
- ✅ Works with analyze_code MCP tool
- ✅ Works with extract_code MCP tool
- ✅ Documentation updated

---

## Next Steps

1. **Prioritize languages** - Start with C++, Go, C#
2. **Prototype one language** - Validate approach with C++ or Go
3. **Create implementation template** - Extract common code
4. **Parallelize implementation** - Each language can be done independently
5. **Incremental testing** - Test each language as it's completed
6. **Update documentation** - Document supported languages as they're added

---

## Related Files

### Core Files
- `src/code_scalpel/code_parsers/interface.py` - IParser contract
- `src/code_scalpel/code_parsers/factory.py` - Parser registration
- `src/code_scalpel/code_parsers/base_parser.py` - Shared utilities

### Implemented Adapters (Reference)
- `src/code_scalpel/code_parsers/python_parser.py`
- `src/code_scalpel/code_parsers/adapters/javascript_adapter.py`
- `src/code_scalpel/code_parsers/adapters/java_adapter.py`

### Stub Adapters (To Implement)
- `src/code_scalpel/code_parsers/adapters/cpp_adapter.py`
- `src/code_scalpel/code_parsers/adapters/csharp_adapter.py`
- `src/code_scalpel/code_parsers/adapters/go_adapter.py`
- `src/code_scalpel/code_parsers/adapters/kotlin_adapter.py`
- `src/code_scalpel/code_parsers/adapters/php_adapter.py`
- `src/code_scalpel/code_parsers/adapters/ruby_adapter.py`
- `src/code_scalpel/code_parsers/adapters/swift_adapter.py`

### Tests
- `tests/core/parsers/` - Parser test directory

---

## Conclusion

The Code Scalpel parser architecture is well-designed and extensible. Implementing the 7 missing languages is straightforward but time-consuming work. Using tree-sitter as a common backend will provide consistency and reduce complexity.

Priority should be given to C++, Go, and C# due to their large ecosystems and enterprise demand.
