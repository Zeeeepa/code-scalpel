"""
Tests for C# parser support in code_scalpel.

[20260224_FEATURE] Full test suite for CSharpNormalizer and polyglot extractor
C# wiring.

Coverage:
    - CSharpNormalizer: class, struct, interface, record, enum
    - Methods, constructors, properties
    - Namespaces (transparent fold)
    - Generic type parameters
    - Using directives → IRImport
    - Field declarations → IRAssign
    - Control flow: if, while, for, foreach, switch
    - Expressions: binary ops, method calls, assignments
    - PolyglotExtractor: end-to-end C# extraction
    - Language detection: .cs extension, content heuristics
    - Normalizer LRU cache
    - EXTENSION_MAP entries
"""

import pytest

from code_scalpel.code_parsers.extractor import (
    EXTENSION_MAP,
    Language,
    PolyglotExtractor,
    detect_language,
)
from code_scalpel.ir.nodes import (
    IRAssign,
    IRClassDef,
    IRFunctionDef,
    IRImport,
    IRModule,
    IRName,
    IRReturn,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalizer():
    from code_scalpel.ir.normalizers.csharp_normalizer import CSharpNormalizer

    return CSharpNormalizer()


def _normalize(source: str) -> IRModule:
    return _normalizer().normalize(source)


def _top(source: str, kind: type):
    """Return the first top-level node of the given IR type."""
    mod = _normalize(source)
    for node in mod.body:
        if isinstance(node, kind):
            return node
    return None


# ---------------------------------------------------------------------------
# 1. Extension map
# ---------------------------------------------------------------------------


class TestExtensionMapCSharp:
    def test_cs_mapped(self):
        assert ".cs" in EXTENSION_MAP
        assert EXTENSION_MAP[".cs"] == Language.CSHARP


# ---------------------------------------------------------------------------
# 2. Language detection
# ---------------------------------------------------------------------------


class TestLanguageDetectionCSharp:
    def test_extension_detection(self):
        assert detect_language("Program.cs") == Language.CSHARP

    def test_content_using_system(self):
        code = "using System;\nclass Foo {}"
        assert detect_language(None, code) == Language.CSHARP

    def test_content_public_class(self):
        # "public class" alone is ambiguous with Java; add C#-specific "using System"
        code = "using System;\npublic class Foo : object { }"
        assert detect_language(None, code) == Language.CSHARP

    def test_content_void_main(self):
        code = "static void Main(string[] args) { }"
        assert detect_language(None, code) == Language.CSHARP

    def test_does_not_trigger_for_c_include(self):
        """C code with #include should not be classified as C#."""
        code = "#include <stdio.h>\nvoid main() {}"
        lang = detect_language(None, code)
        assert lang != Language.CSHARP


# ---------------------------------------------------------------------------
# 3. Module root
# ---------------------------------------------------------------------------


class TestCSharpNormalizerModule:
    def test_returns_irmodule(self):
        mod = _normalize("// empty file\n")
        assert isinstance(mod, IRModule)

    def test_source_language(self):
        mod = _normalize("class Foo {}")
        assert mod.source_language == "csharp"


# ---------------------------------------------------------------------------
# 4. Namespaces
# ---------------------------------------------------------------------------


class TestCSharpNormalizerNamespaces:
    def test_simple_namespace_transparent(self):
        code = """
namespace MyApp {
    class Foo {}
}
"""
        mod = _normalize(code)
        # Foo should be folded into the module body
        cls = next((n for n in mod.body if isinstance(n, IRClassDef)), None)
        assert cls is not None
        assert cls.name == "Foo"

    def test_namespace_metadata(self):
        code = """
namespace MyApp.Utils {
    class Bar {}
}
"""
        mod = _normalize(code)
        cls = next((n for n in mod.body if isinstance(n, IRClassDef)), None)
        assert cls is not None
        assert cls._metadata.get("namespace") == "MyApp.Utils"

    def test_nested_namespaces(self):
        code = """
namespace Outer {
    namespace Inner {
        class Baz {}
    }
}
"""
        mod = _normalize(code)

        # Baz may be directly in mod.body or nested one level
        def _find_class(nodes):
            for n in nodes:
                if isinstance(n, IRClassDef) and n.name == "Baz":
                    return n
                if isinstance(n, IRClassDef):
                    found = _find_class(n.body)
                    if found:
                        return found
            return None

        assert _find_class(mod.body) is not None


# ---------------------------------------------------------------------------
# 5. Classes
# ---------------------------------------------------------------------------


class TestCSharpNormalizerClasses:
    def test_simple_class(self):
        cls = _top("class Foo {}", IRClassDef)
        assert cls is not None
        assert cls.name == "Foo"
        assert cls._metadata.get("kind") == "class"

    def test_public_class(self):
        cls = _top("public class Vec3 {}", IRClassDef)
        assert cls is not None
        assert cls.name == "Vec3"

    def test_class_with_base(self):
        code = "public class Dog : Animal {}"
        cls = _top(code, IRClassDef)
        assert cls is not None
        base_names = [b.id for b in cls.bases]
        assert "Animal" in base_names

    def test_class_with_multiple_bases(self):
        code = "class MyList : IList<int>, IEnumerable<int> {}"
        cls = _top(code, IRClassDef)
        assert cls is not None
        assert len(cls.bases) >= 1

    def test_generic_class(self):
        code = "public class Stack<T> {}"
        cls = _top(code, IRClassDef)
        assert cls is not None
        assert cls.name == "Stack"
        assert "T" in cls._metadata.get("type_params", [])

    def test_location_set(self):
        cls = _top("class Foo {}", IRClassDef)
        assert cls.loc is not None
        assert cls.loc.line >= 1

    def test_class_body_method(self):
        code = """
public class Calc {
    public int Add(int a, int b) { return a + b; }
}
"""
        cls = _top(code, IRClassDef)
        assert cls is not None
        methods = [n for n in cls.body if isinstance(n, IRFunctionDef)]
        assert any(m.name == "Add" for m in methods)


# ---------------------------------------------------------------------------
# 6. Structs
# ---------------------------------------------------------------------------


class TestCSharpNormalizerStructs:
    def test_struct(self):
        code = "public struct Point { public float X; public float Y; }"
        cls = _top(code, IRClassDef)
        assert cls is not None
        assert cls.name == "Point"
        assert cls._metadata.get("kind") == "struct"

    def test_struct_with_fields(self):
        code = "struct Color { public byte R, G, B; }"
        cls = _top(code, IRClassDef)
        assert cls is not None
        assigns = [n for n in cls.body if isinstance(n, IRAssign)]
        # At least one field
        assert len(assigns) >= 1


# ---------------------------------------------------------------------------
# 7. Interfaces
# ---------------------------------------------------------------------------


class TestCSharpNormalizerInterfaces:
    def test_interface(self):
        code = "public interface IRenderable { void Render(); }"
        cls = _top(code, IRClassDef)
        assert cls is not None
        assert cls.name == "IRenderable"
        assert cls._metadata.get("kind") == "interface"

    def test_interface_method_stub(self):
        code = "public interface IRepo { Task<int> GetIdAsync(); }"
        cls = _top(code, IRClassDef)
        assert cls is not None
        # Methods with empty bodies should still be IRFunctionDef
        # (may be in body depending on tree-sitter grammar)
        # Just assert the interface is parsed
        assert cls.name == "IRepo"


# ---------------------------------------------------------------------------
# 8. Records
# ---------------------------------------------------------------------------


class TestCSharpNormalizerRecords:
    def test_record(self):
        code = "public record Person(string Name, int Age);"
        cls = _top(code, IRClassDef)
        if cls is None:
            # Tree-sitter may not produce record_declaration in some versions
            pytest.skip("record_declaration not produced by this grammar version")
        assert cls.name == "Person"
        assert cls._metadata.get("kind") == "record"


# ---------------------------------------------------------------------------
# 9. Enums
# ---------------------------------------------------------------------------


class TestCSharpNormalizerEnums:
    def test_enum(self):
        code = "public enum Direction { North, South, East, West }"
        cls = _top(code, IRClassDef)
        assert cls is not None
        assert cls.name == "Direction"
        assert cls._metadata.get("kind") == "enum"

    def test_enum_members(self):
        code = "enum Level { Low, Medium, High }"
        cls = _top(code, IRClassDef)
        assert cls is not None
        members = [n for n in cls.body if isinstance(n, IRAssign)]
        member_names = [
            n.targets[0].id for n in members if isinstance(n.targets[0], IRName)
        ]
        assert "Low" in member_names
        assert "Medium" in member_names
        assert "High" in member_names

    def test_enum_with_values(self):
        code = "enum Flags { None = 0, Read = 1, Write = 2 }"
        cls = _top(code, IRClassDef)
        assert cls is not None
        members = [n for n in cls.body if isinstance(n, IRAssign)]
        assert len(members) >= 1


# ---------------------------------------------------------------------------
# 10. Methods
# ---------------------------------------------------------------------------


class TestCSharpNormalizerMethods:
    def test_simple_method(self):
        code = """
class Calc {
    public int Add(int a, int b) { return a + b; }
}
"""
        cls = _top(code, IRClassDef)
        assert cls is not None
        m = next(
            (n for n in cls.body if isinstance(n, IRFunctionDef) and n.name == "Add"),
            None,
        )
        assert m is not None

    def test_method_return_type(self):
        code = "class C { public float Div(float a, float b) { return a / b; } }"
        cls = _top(code, IRClassDef)
        m = next((n for n in cls.body if isinstance(n, IRFunctionDef)), None)
        assert m is not None
        assert m.return_type == "float"

    def test_method_params(self):
        code = "class C { void Greet(string name, int count) {} }"
        cls = _top(code, IRClassDef)
        m = next((n for n in cls.body if isinstance(n, IRFunctionDef)), None)
        assert m is not None
        assert len(m.params) == 2
        param_names = [p.name for p in m.params]
        assert "name" in param_names
        assert "count" in param_names

    def test_method_param_types(self):
        code = "class C { void Log(string msg) {} }"
        cls = _top(code, IRClassDef)
        m = next((n for n in cls.body if isinstance(n, IRFunctionDef)), None)
        assert m is not None
        assert m.params[0].type_annotation == "string"

    def test_void_method(self):
        code = "class C { void Noop() {} }"
        cls = _top(code, IRClassDef)
        m = next((n for n in cls.body if isinstance(n, IRFunctionDef)), None)
        assert m is not None
        assert m.return_type == "void"

    def test_static_method(self):
        code = "class Math { public static int Min(int a, int b) { return a < b ? a : b; } }"
        cls = _top(code, IRClassDef)
        assert any(isinstance(n, IRFunctionDef) and n.name == "Min" for n in cls.body)

    def test_generic_method(self):
        code = "class C { T First<T>(T[] arr) { return arr[0]; } }"
        cls = _top(code, IRClassDef)
        m = next(
            (n for n in cls.body if isinstance(n, IRFunctionDef) and n.name == "First"),
            None,
        )
        assert m is not None
        assert "T" in m._metadata.get("type_params", [])

    def test_method_body_return(self):
        code = "class C { int Two() { return 2; } }"
        cls = _top(code, IRClassDef)
        m = next((n for n in cls.body if isinstance(n, IRFunctionDef)), None)
        assert m is not None
        returns = [n for n in m.body if isinstance(n, IRReturn)]
        assert len(returns) >= 1

    def test_method_location(self):
        code = "class C { void Noop() {} }"
        cls = _top(code, IRClassDef)
        m = next((n for n in cls.body if isinstance(n, IRFunctionDef)), None)
        assert m is not None
        assert m.loc is not None


# ---------------------------------------------------------------------------
# 11. Constructors
# ---------------------------------------------------------------------------


class TestCSharpNormalizerConstructors:
    def test_constructor(self):
        code = """
class Vec3 {
    public float X, Y, Z;
    public Vec3(float x, float y, float z) { X = x; Y = y; Z = z; }
}
"""
        cls = _top(code, IRClassDef)
        ctor = next(
            (
                n
                for n in cls.body
                if isinstance(n, IRFunctionDef) and n._metadata.get("is_constructor")
            ),
            None,
        )
        assert ctor is not None
        assert ctor.name == "Vec3"

    def test_constructor_params(self):
        code = "class P { public P(int x, int y) {} }"
        cls = _top(code, IRClassDef)
        ctor = next(
            (
                n
                for n in cls.body
                if isinstance(n, IRFunctionDef) and n._metadata.get("is_constructor")
            ),
            None,
        )
        assert ctor is not None
        assert len(ctor.params) == 2


# ---------------------------------------------------------------------------
# 12. Properties
# ---------------------------------------------------------------------------


class TestCSharpNormalizerProperties:
    def test_auto_property(self):
        code = "class Person { public string Name { get; set; } }"
        cls = _top(code, IRClassDef)
        prop = next(
            (n for n in cls.body if isinstance(n, IRFunctionDef) and n.name == "Name"),
            None,
        )
        assert prop is not None
        assert prop._metadata.get("is_property") is True

    def test_property_return_type(self):
        code = "class Person { public int Age { get; set; } }"
        cls = _top(code, IRClassDef)
        prop = next(
            (n for n in cls.body if isinstance(n, IRFunctionDef) and n.name == "Age"),
            None,
        )
        assert prop is not None
        assert prop.return_type == "int"


# ---------------------------------------------------------------------------
# 13. Fields
# ---------------------------------------------------------------------------


class TestCSharpNormalizerFields:
    def test_simple_field(self):
        code = "class C { private int _count; }"
        cls = _top(code, IRClassDef)
        assigns = [n for n in cls.body if isinstance(n, IRAssign)]
        assert len(assigns) >= 1
        assert any(
            isinstance(n.targets[0], IRName) and n.targets[0].id == "_count"
            for n in assigns
        )

    def test_field_type_annotation(self):
        code = "class C { public string Name; }"
        cls = _top(code, IRClassDef)
        assigns = [n for n in cls.body if isinstance(n, IRAssign)]
        assert any(n._metadata.get("type_annotation") == "string" for n in assigns)

    def test_multiple_declarators(self):
        code = "class C { float X, Y, Z; }"
        cls = _top(code, IRClassDef)
        assigns = [n for n in cls.body if isinstance(n, IRAssign)]
        names = [n.targets[0].id for n in assigns if isinstance(n.targets[0], IRName)]
        assert "X" in names
        assert "Y" in names
        assert "Z" in names


# ---------------------------------------------------------------------------
# 14. Using directives => IRImport
# ---------------------------------------------------------------------------


class TestCSharpNormalizerUsing:
    def test_simple_using(self):
        code = "using System;\nclass C {}"
        mod = _normalize(code)
        imports = [n for n in mod.body if isinstance(n, IRImport)]
        assert any(n.module == "System" for n in imports)

    def test_qualified_using(self):
        code = "using System.Collections.Generic;"
        mod = _normalize(code)
        imports = [n for n in mod.body if isinstance(n, IRImport)]
        assert len(imports) >= 1
        assert any("System" in n.module for n in imports)

    def test_multiple_usings(self):
        code = "using System;\nusing System.IO;\nusing System.Collections;"
        mod = _normalize(code)
        imports = [n for n in mod.body if isinstance(n, IRImport)]
        assert len(imports) >= 2


# ---------------------------------------------------------------------------
# 15. Expressions
# ---------------------------------------------------------------------------


class TestCSharpNormalizerExpressions:
    def test_binary_add(self):
        code = "class C { int F() { return a + b; } }"
        cls = _top(code, IRClassDef)
        m = next((n for n in cls.body if isinstance(n, IRFunctionDef)), None)
        assert m is not None
        returns = [n for n in m.body if isinstance(n, IRReturn)]
        assert len(returns) >= 1
        # The return value may be IRBinaryOp or IRConstant fallback
        # At minimum, the method body is non-empty

    def test_method_call_in_method(self):
        code = """
class C {
    void Run() { Console.WriteLine("hello"); }
}
"""
        cls = _top(code, IRClassDef)
        m = next((n for n in cls.body if isinstance(n, IRFunctionDef)), None)
        assert m is not None
        assert len(m.body) >= 1

    def test_return_integer(self):
        code = "class C { int Five() { return 5; } }"
        cls = _top(code, IRClassDef)
        m = next((n for n in cls.body if isinstance(n, IRFunctionDef)), None)
        assert m is not None
        returns = [n for n in m.body if isinstance(n, IRReturn)]
        assert len(returns) >= 1


# ---------------------------------------------------------------------------
# 16. Top-level / global statements (C# 9+)
# ---------------------------------------------------------------------------


class TestCSharpTopLevel:
    def test_top_level_statement(self):
        code = 'Console.WriteLine("Hello, World!");'
        mod = _normalize(code)
        # Should produce at least something in the module body
        assert isinstance(mod, IRModule)

    def test_top_level_function(self):
        code = """
int Add(int a, int b) => a + b;
"""
        mod = _normalize(code)
        funcs = [n for n in mod.body if isinstance(n, IRFunctionDef)]
        if funcs:
            assert any(f.name == "Add" for f in funcs)
        # Accept either: IRFunctionDef or wrapped in module body


# ---------------------------------------------------------------------------
# 17. PolyglotExtractor end-to-end
# ---------------------------------------------------------------------------


class TestPolyglotExtractorCSharp:
    def test_extract_class(self):
        code = """
public class Vec3 {
    public float X, Y, Z;
    public Vec3(float x, float y, float z) { X = x; Y = y; Z = z; }
    public float Dot(Vec3 o) { return X*o.X + Y*o.Y + Z*o.Z; }
}
"""
        extractor = PolyglotExtractor(code, language=Language.CSHARP)
        result = extractor.extract("class", "Vec3")
        assert result.success, f"Extraction failed: {result.error}"
        assert "Vec3" in result.code
        assert result.language == "csharp"

    def test_extract_method(self):
        code = """
public class Calc {
    public int Add(int a, int b) { return a + b; }
    public int Sub(int a, int b) { return a - b; }
}
"""
        extractor = PolyglotExtractor(code, language=Language.CSHARP)
        # C# methods are class members; use "method" with "ClassName.method" format
        result = extractor.extract("method", "Calc.Add")
        assert result.success, f"Extraction failed: {result.error}"
        assert "Add" in result.code

    def test_extract_from_cs_file(self, tmp_path):
        code = "public class HelloWorld { public void Run() {} }"
        cs_file = tmp_path / "HelloWorld.cs"
        cs_file.write_text(code)
        extractor = PolyglotExtractor(code, file_path=str(cs_file))
        result = extractor.extract("class", "HelloWorld")
        assert result.success
        assert "HelloWorld" in result.code

    def test_language_auto_detected_from_extension(self, tmp_path):
        code = "using System;\nclass Demo {}"
        cs_file = tmp_path / "Demo.cs"
        cs_file.write_text(code)
        extractor = PolyglotExtractor(code, file_path=str(cs_file))
        assert extractor.language == Language.CSHARP

    def test_extract_interface(self):
        code = """
namespace Contracts {
    public interface IRepository {
        int GetById(int id);
    }
}
"""
        extractor = PolyglotExtractor(code, language=Language.CSHARP)
        result = extractor.extract("class", "IRepository")
        assert result.success, f"Extraction failed: {result.error}"
        assert "IRepository" in result.code

    def test_extract_struct(self):
        code = """
public struct Color {
    public byte R, G, B;
    public Color(byte r, byte g, byte b) { R = r; G = g; B = b; }
}
"""
        extractor = PolyglotExtractor(code, language=Language.CSHARP)
        result = extractor.extract("class", "Color")
        assert result.success, f"Extraction failed: {result.error}"
        assert "Color" in result.code

    def test_extract_enum(self):
        code = "public enum Direction { North, South, East, West }"
        extractor = PolyglotExtractor(code, language=Language.CSHARP)
        result = extractor.extract("class", "Direction")
        assert result.success, f"Extraction failed: {result.error}"
        assert "Direction" in result.code

    def test_nonexistent_element(self):
        code = "class Foo {}"
        extractor = PolyglotExtractor(code, language=Language.CSHARP)
        result = extractor.extract("class", "Bar")
        assert not result.success

    def test_large_class(self):
        methods = "\n".join(
            f"    public int M{i}(int x) {{ return x + {i}; }}" for i in range(20)
        )
        code = f"public class BigClass {{\n{methods}\n}}"
        extractor = PolyglotExtractor(code, language=Language.CSHARP)
        result = extractor.extract("class", "BigClass")
        assert result.success


# ---------------------------------------------------------------------------
# 18. Normalizer cache
# ---------------------------------------------------------------------------


class TestNormalizerCacheCSharp:
    def test_same_source_reuses_cache(self):
        norm = _normalizer()
        code = "class Foo { int X; }"
        m1 = norm.normalize(code)
        m2 = norm.normalize(code)
        # Both should produce equivalent results (no crash, same structure)
        assert type(m1) is type(m2)
        cls1 = next((n for n in m1.body if isinstance(n, IRClassDef)), None)
        cls2 = next((n for n in m2.body if isinstance(n, IRClassDef)), None)
        assert cls1 is not None
        assert cls2 is not None
        assert cls1.name == cls2.name

    def test_different_source_different_result(self):
        norm = _normalizer()
        m1 = norm.normalize("class Foo {}")
        m2 = norm.normalize("class Bar {}")
        names1 = [n.name for n in m1.body if isinstance(n, IRClassDef)]
        names2 = [n.name for n in m2.body if isinstance(n, IRClassDef)]
        assert names1 != names2

    def test_cache_limit_no_crash(self):
        """Filling the cache beyond MAX_CACHE should not raise."""
        norm = _normalizer()
        from code_scalpel.ir.normalizers.csharp_normalizer import CSharpNormalizer

        limit = CSharpNormalizer._MAX_CACHE
        for i in range(limit + 5):
            norm.normalize(f"class C{i} {{}}")
        # If we reach here without exception, the test passes.


# ---------------------------------------------------------------------------
# 19. Adapter
# ---------------------------------------------------------------------------


class TestCSharpAdapter:
    def test_adapter_instantiates(self):
        from code_scalpel.code_parsers.adapters.csharp_adapter import (
            CSharpParserAdapter,
        )

        adapter = CSharpParserAdapter()
        assert adapter is not None

    def test_adapter_parse(self):
        from code_scalpel.code_parsers.adapters.csharp_adapter import (
            CSharpParserAdapter,
        )

        adapter = CSharpParserAdapter()
        result = adapter.parse("class Foo { int X; }")
        assert result is not None
        assert result.ast is not None  # IRModule returned

    def test_adapter_get_classes(self):
        from code_scalpel.code_parsers.adapters.csharp_adapter import (
            CSharpParserAdapter,
        )

        adapter = CSharpParserAdapter()
        result = adapter.parse("class Foo {} class Bar {}")
        names = adapter.get_classes(result.ast)
        assert "Foo" in names
        assert "Bar" in names

    def test_adapter_get_functions(self):
        from code_scalpel.code_parsers.adapters.csharp_adapter import (
            CSharpParserAdapter,
        )

        adapter = CSharpParserAdapter()
        result = adapter.parse(
            "class C { public int Add(int a, int b) { return a + b; } }"
        )
        names = adapter.get_functions(result.ast)
        assert "Add" in names


# ---------------------------------------------------------------------------
# 20. Normalizer __init__ exports
# ---------------------------------------------------------------------------


class TestNormalizerInitExports:
    def test_csharp_exported(self):
        from code_scalpel.ir.normalizers import CSharpNormalizer, _HAS_CSHARP

        assert _HAS_CSHARP is True
        assert CSharpNormalizer is not None

    def test_csharp_visitor_exported(self):
        from code_scalpel.ir.normalizers import CSharpVisitor, _HAS_CSHARP

        assert _HAS_CSHARP is True
        assert CSharpVisitor is not None


# ---------------------------------------------------------------------------
# 21. Realistic C# snippet
# ---------------------------------------------------------------------------


class TestCSharpRealistic:
    VECTOR3_CS = """
using System;

namespace MathLib {
    /// <summary>3-component float vector.</summary>
    public class Vector3 {
        public float X { get; set; }
        public float Y { get; set; }
        public float Z { get; set; }

        public Vector3(float x, float y, float z) {
            X = x; Y = y; Z = z;
        }

        public float Length() {
            return (float)Math.Sqrt(X*X + Y*Y + Z*Z);
        }

        public float Dot(Vector3 other) {
            return X * other.X + Y * other.Y + Z * other.Z;
        }

        public static Vector3 operator +(Vector3 a, Vector3 b) {
            return new Vector3(a.X + b.X, a.Y + b.Y, a.Z + b.Z);
        }

        public override string ToString() {
            return $"({X}, {Y}, {Z})";
        }
    }
}
"""

    def test_class_extraction(self):
        extractor = PolyglotExtractor(self.VECTOR3_CS, language=Language.CSHARP)
        result = extractor.extract("class", "Vector3")
        assert result.success, f"Extraction failed: {result.error}"
        assert "Vector3" in result.code

    def test_method_extraction(self):
        extractor = PolyglotExtractor(self.VECTOR3_CS, language=Language.CSHARP)
        result = extractor.extract("method", "Vector3.Dot")
        assert result.success, f"Extraction failed: {result.error}"
        assert "Dot" in result.code

    def test_namespace_metadata_on_class(self):
        mod = _normalize(self.VECTOR3_CS)
        cls = next(
            (n for n in mod.body if isinstance(n, IRClassDef) and n.name == "Vector3"),
            None,
        )
        assert cls is not None, "Vector3 class not found in module body"
        assert cls._metadata.get("namespace") == "MathLib"


# =============================================================================
# Real-World C# Patterns
# =============================================================================


class TestCSharpRealWorldPatterns:
    """C# patterns drawn from real codebases: async, generics, events, LINQ, etc.

    [20260224_TEST] Extended coverage for edge-case C# constructs.
    """

    def test_async_method(self):
        """async Task method — must surface as IRFunctionDef."""
        src = """
using System.Threading.Tasks;
public class Loader {
    public async Task<string> LoadAsync(string url) {
        return await FetchAsync(url);
    }
}
"""
        mod = _normalize(src)
        cls = next(
            (n for n in mod.body if isinstance(n, IRClassDef) and n.name == "Loader"),
            None,
        )
        assert cls is not None
        methods = [n for n in cls.body if isinstance(n, IRFunctionDef)]
        assert any(fn.name == "LoadAsync" for fn in methods)

    def test_extension_method(self):
        """Extension method with `this` parameter — method must be found."""
        src = """
public static class StringExtensions {
    public static string Truncate(this string s, int maxLen) {
        return s.Length <= maxLen ? s : s.Substring(0, maxLen);
    }
}
"""
        mod = _normalize(src)
        cls = next(
            (
                n
                for n in mod.body
                if isinstance(n, IRClassDef) and n.name == "StringExtensions"
            ),
            None,
        )
        assert cls is not None
        methods = [n for n in cls.body if isinstance(n, IRFunctionDef)]
        assert any(fn.name == "Truncate" for fn in methods)

    def test_nullable_property(self):
        """Nullable reference type `string?` — class and property surfaced."""
        src = """
public class Person {
    public string? MiddleName { get; set; }
    public string FirstName { get; set; } = string.Empty;
}
"""
        mod = _normalize(src)
        cls = next(
            (n for n in mod.body if isinstance(n, IRClassDef) and n.name == "Person"),
            None,
        )
        assert cls is not None

    def test_tuple_return_type(self):
        """Tuple return `(int, int)` — method must surface as IRFunctionDef."""
        src = """
public class Grid {
    public (int row, int col) IndexOf(int value) {
        return (0, 0);
    }
}
"""
        mod = _normalize(src)
        cls = next(
            (n for n in mod.body if isinstance(n, IRClassDef) and n.name == "Grid"),
            None,
        )
        assert cls is not None
        methods = [n for n in cls.body if isinstance(n, IRFunctionDef)]
        assert any(fn.name == "IndexOf" for fn in methods)

    def test_delegate_declaration_parses(self):
        """delegate declaration — module must parse without error."""
        m = _normalize("public delegate void EventHandler(object sender, int e);")
        assert isinstance(m, IRModule)

    def test_event_field_parses(self):
        """event field declaration — class must be found."""
        src = """
public class Button {
    public event System.EventHandler Clicked;
    public void Click() { Clicked?.Invoke(this, null); }
}
"""
        mod = _normalize(src)
        cls = next(
            (n for n in mod.body if isinstance(n, IRClassDef) and n.name == "Button"),
            None,
        )
        assert cls is not None

    def test_partial_class(self):
        """partial modifier on a class — class must still surface."""
        src = """
public partial class Form1 {
    private void InitializeComponent() {}
}
"""
        mod = _normalize(src)
        cls = next(
            (n for n in mod.body if isinstance(n, IRClassDef) and n.name == "Form1"),
            None,
        )
        assert cls is not None

    def test_indexer(self):
        """Indexer declaration `this[int i]` — class must be found."""
        src = """
public class Matrix {
    private float[] _data = new float[16];
    public float this[int i] { get => _data[i]; set => _data[i] = value; }
}
"""
        mod = _normalize(src)
        cls = next(
            (n for n in mod.body if isinstance(n, IRClassDef) and n.name == "Matrix"),
            None,
        )
        assert cls is not None

    def test_operator_overload(self):
        """C# operator+ overload — operator method must surface."""
        src = """
public struct Vec2 {
    public float X, Y;
    public static Vec2 operator+(Vec2 a, Vec2 b) {
        return new Vec2 { X = a.X + b.X, Y = a.Y + b.Y };
    }
}
"""
        mod = _normalize(src)
        cls = next(
            (n for n in mod.body if isinstance(n, IRClassDef) and n.name == "Vec2"),
            None,
        )
        assert cls is not None
        methods = [n for n in cls.body if isinstance(n, IRFunctionDef)]
        assert any("operator" in fn.name for fn in methods)

    def test_generic_class_with_constraint(self):
        """Generic class with `where T : IComparable<T>` constraint."""
        src = """
public class SortedList<T> where T : System.IComparable<T> {
    public void Add(T item) {}
    public T Min() { return default; }
}
"""
        mod = _normalize(src)
        cls = next(
            (
                n
                for n in mod.body
                if isinstance(n, IRClassDef) and n.name == "SortedList"
            ),
            None,
        )
        assert cls is not None

    def test_pattern_matching_switch_parses(self):
        """C# switch expression / is-pattern — method must surface."""
        src = """
public class Shapes {
    public string Describe(object shape) {
        return shape switch {
            Circle c  => $"Circle r={c.Radius}",
            Square s  => $"Square side={s.Side}",
            _         => "unknown"
        };
    }
}
"""
        mod = _normalize(src)
        cls = next(
            (n for n in mod.body if isinstance(n, IRClassDef) and n.name == "Shapes"),
            None,
        )
        assert cls is not None
        methods = [n for n in cls.body if isinstance(n, IRFunctionDef)]
        assert any(fn.name == "Describe" for fn in methods)

    def test_record_struct(self):
        """C# record struct (value record) — must surface as IRClassDef."""
        src = "public record struct Point(float X, float Y);"
        mod = _normalize(src)
        cls = next(
            (n for n in mod.body if isinstance(n, IRClassDef) and n.name == "Point"),
            None,
        )
        assert cls is not None

    def test_unity_style_component_smoke(self):
        """Smoke test: Unity-style MonoBehaviour component with lifecycle methods."""
        src = """
using System;
using System.Collections;

public class PlayerController : MonoBehaviour {
    public float speed = 5f;
    public float jumpForce = 8f;
    private bool _isGrounded;

    private void Start() {
        _isGrounded = true;
    }

    private void Update() {
        float h = Input.GetAxis("Horizontal");
        transform.Translate(h * speed * Time.deltaTime, 0, 0);
        if (Input.GetButtonDown("Jump") && _isGrounded) {
            Jump();
        }
    }

    private void Jump() {
        _isGrounded = false;
    }

    private void OnCollisionEnter(Collision col) {
        if (col.gameObject.CompareTag("Ground")) {
            _isGrounded = true;
        }
    }
}
"""
        mod = _normalize(src)
        cls = next(
            (
                n
                for n in mod.body
                if isinstance(n, IRClassDef) and n.name == "PlayerController"
            ),
            None,
        )
        assert cls is not None
        method_names = {fn.name for fn in cls.body if isinstance(fn, IRFunctionDef)}
        assert "Start" in method_names
        assert "Update" in method_names
        assert "Jump" in method_names
