"""
C++ Normalizer - Converts C++ CST (tree-sitter-cpp) to Unified IR.

[20260224_FEATURE] C++ language support for surgical extraction and analysis.

Extends the C normalizer with C++-specific constructs:
    class_specifier       -> IRClassDef  (class/struct with access specifiers)
    namespace_definition  -> IRModule    (yields body into parent scope)
    template_declaration  -> unwrap inner function/class definition
    using_declaration     -> IRImport
    access_specifier      -> skip (public:, private:, protected:)
    destructor_name       -> handled inside function_definition
    operator_name         -> handled inside function_declarator

3D-relevant patterns supported:
    class Vec3 { ... };          -> IRClassDef("Vec3")
    Vec3::dot(const Vec3& o)     -> IRFunctionDef("Vec3.dot")  [qualified name]
    template<T> T lerp(T,T,float) -> IRFunctionDef("lerp")
    namespace geom { ... }       -> body folded into parent module
    using std::vector;           -> IRImport

Tree-sitter grammar notes for tree-sitter-cpp:
    class_specifier:  name=type_identifier, body=field_declaration_list
    namespace_definition: name=namespace_identifier, body=declaration_list
    template_declaration: body=function_definition|class_specifier
    using_declaration: "using" ... ";"
    access_specifier: "public"|"private"|"protected"

"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, cast

import tree_sitter_cpp
from tree_sitter import Language, Parser

from ..nodes import (
    IRAssign,
    IRClassDef,
    IRConstant,
    IRExpr,
    IRFunctionDef,
    IRImport,
    IRModule,
    IRName,
    IRNode,
    IRParameter,
)
from .base import BaseNormalizer
from .c_normalizer import CVisitor

# ---------------------------------------------------------------------------
# C++ Visitor  (extends CVisitor)
# ---------------------------------------------------------------------------


class CppVisitor(CVisitor):
    """
    Visitor for C++ CST nodes.

    Inherits all C handling from CVisitor and overrides/adds C++-specific
    node handlers.

    [20260224_FEATURE] C++ visitor for 3D-project extraction.
    """

    @property
    def language(self) -> str:
        return "cpp"

    # ------------------------------------------------------------------
    # Root  (same structure as C's translation_unit, just re-use it)
    # ------------------------------------------------------------------

    # translation_unit is inherited from CVisitor — no override needed

    # ------------------------------------------------------------------
    # Classes and Structs
    # ------------------------------------------------------------------

    def visit_class_specifier(self, node: Any) -> Optional[IRClassDef]:
        """
        class Vec3 { public: float x, y, z; float dot(const Vec3&) const; };

        [20260224_FEATURE] C++ classes → IRClassDef.
        Access specifiers (public:/private:/protected:) are skipped.
        Method declarations inside the class body become IRFunctionDef stubs.
        """
        name_node = node.child_by_field_name("name")
        name = self._get_text(name_node) if name_node else "Anonymous"

        body_node = node.child_by_field_name("body")
        body = self._parse_class_body(body_node) if body_node else []

        # Collect base classes
        bases = self._collect_base_classes(node)

        return IRClassDef(
            name=name,
            bases=bases,
            body=body,
            source_language=self.language,
            loc=self._get_location(node),
        )

    # C++ struct is also a class_specifier in tree-sitter-cpp;
    # but struct_specifier is emitted separately for C-style structs.
    # Keep C's visit_struct_specifier for plain structs.

    def _parse_class_body(self, body_node: Any) -> List[IRNode]:
        """
        Parse the body of a C++ class/struct.

        Handles: field_declaration, function_definition (inline methods),
        declaration (method stubs), access_specifier (skipped).

        [20260224_BUGFIX] Nested class/struct declarations (wrapped as
        field_declaration in tree-sitter-cpp) are now unfolded into the
        containing body so they appear as IRClassDef children.
        """
        result: List[IRNode] = []
        for child in body_node.children:
            if not child.is_named:
                continue
            if child.type == "access_specifier":
                continue  # public: / private: — skip
            # Unwrap nested type declarations (class/struct/enum inside a class)
            if child.type == "field_declaration":
                nested = self._extract_nested_type(child)
                if nested is not None:
                    result.append(nested)
                    continue
            res = self.visit(child)
            if res is None:
                continue
            if isinstance(res, list):
                result.extend(res)
            else:
                result.append(cast(IRNode, res))
        return result

    def _extract_nested_type(self, field_decl: Any) -> Optional[IRClassDef]:
        """Return an IRClassDef if field_decl wraps a nested type declaration.

        In tree-sitter-cpp a nested 'class Node { };' inside a class body
        is represented as::

            field_declaration
                class_specifier   ← the nested class
                ";"

        [20260224_BUGFIX] Unfold nested types from field_declaration wrappers.
        """
        for child in field_decl.children:
            if child.type in ("class_specifier", "struct_specifier", "enum_specifier"):
                result = self.visit(child)
                if isinstance(result, IRClassDef):
                    return result
        return None

    def _collect_base_classes(self, node: Any) -> List[IRExpr]:
        """Extract base classes from a class_specifier.

        [20260224_BUGFIX] In tree-sitter-cpp the base_class_clause is a direct
        child of class_specifier (not behind a named field "bases").  Iterate
        children directly.
        """
        bases: List[IRExpr] = []
        for child in node.children:
            if child.type != "base_class_clause":
                continue
            # base_class_clause children: ':'  access_specifier?  type_identifier
            for inner in child.children:
                if inner.type in ("type_identifier", "identifier"):
                    bases.append(IRName(id=self._get_text(inner)))
        return bases

    # ------------------------------------------------------------------
    # Namespaces
    # ------------------------------------------------------------------

    def visit_namespace_definition(self, node: Any) -> Optional[List[IRNode]]:
        """
        namespace geom { ... }

        [20260224_FEATURE] Namespaces are transparent — we fold their
        declarations into the parent scope. Namespace name is stored in
        _metadata of each child for traceability.
        """
        name_node = node.child_by_field_name("name")
        ns_name = self._get_text(name_node) if name_node else "<anon>"

        body_node = node.child_by_field_name("body")
        if body_node is None:
            return None

        children = self._visit_body(body_node)
        # Tag each child with its namespace for downstream tooling
        for child in children:
            if not isinstance(child, list):
                child._metadata.setdefault("namespace", ns_name)
        return children

    # Inline/anonymous namespaces
    def visit_anonymous_namespace(self, node: Any) -> Optional[List[IRNode]]:
        return self._visit_body(node)

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------

    def visit_template_declaration(
        self, node: Any
    ) -> Union[List[IRNode], IRNode, None]:
        """
        template<typename T>
        T lerp(T a, T b, float t) { return a + (b - a) * t; }

        template<typename T>
        class AABB { ... };

        [20260224_FEATURE] Templates unwrap the inner declaration and store
        template parameters in _metadata. This means template functions and
        classes are visible to extract_code by their base name.
        """
        # Collect template parameter names
        params_node = node.child_by_field_name("parameters")
        tparam_names: List[str] = []
        if params_node:
            for child in params_node.children:
                if child.type == "type_parameter_declaration":
                    # [20260224_BUGFIX] tree-sitter-cpp exposes no "name" field;
                    # the name is the last named child (type_identifier).
                    p_name = None
                    for sub in reversed(child.children):
                        if sub.type in ("type_identifier", "identifier"):
                            p_name = sub
                            break
                    if p_name:
                        tparam_names.append(self._get_text(p_name))

        # The templated entity is in the last named child
        inner_node = None
        for child in reversed(node.children):
            if child.is_named and child.type not in (
                "template_parameter_list",
                "template",
            ):
                inner_node = child
                break

        if inner_node is None:
            return None

        result = self.visit(inner_node)
        if result is None:
            return None

        # Tag with template params
        nodes = result if isinstance(result, list) else [result]
        for n in nodes:
            if not isinstance(n, list):
                n._metadata["template_params"] = tparam_names
        return result

    # ------------------------------------------------------------------
    # Using declarations
    # ------------------------------------------------------------------

    def visit_using_declaration(self, node: Any) -> IRImport:
        """
        using std::vector;
        using namespace std;

        [20260224_FEATURE] using declarations become IRImport.
        """
        text = self._get_text(node).strip().rstrip(";")
        # "using namespace std" or "using std::vector"
        text = text.replace("using namespace ", "").replace("using ", "").strip()
        module_parts = text.rsplit("::", 1)
        if len(module_parts) == 2:
            module, name = module_parts
            names = [name]
        else:
            module = text
            names = []
        return IRImport(
            module=module,
            names=names,
            is_star=False,
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_namespace_alias_definition(self, node: Any) -> IRImport:
        """namespace fs = std::filesystem; — treat as an alias import."""
        text = self._get_text(node).strip().rstrip(";")
        return IRImport(
            module=text,
            names=[],
            loc=self._get_location(node),
            source_language=self.language,
        )

    # ------------------------------------------------------------------
    # Qualified function definitions  (Vec3::dot(...) { ... })
    # ------------------------------------------------------------------

    def visit_function_definition(self, node: Any) -> IRFunctionDef:
        """
        Extends C function handling for:
        - Qualified names: Vec3::dot(const Vec3&)
        - Const methods:   float length() const { ... }
        - Destructors:     ~Mesh() { ... }

        [20260224_FEATURE] C++ qualified method definitions.
        """
        # Re-use C base implementation
        fn = super().visit_function_definition(node)

        # Post-process: check if declarator has a qualified_identifier
        decl_node = node.child_by_field_name("declarator")
        if decl_node:
            qualified = self._extract_qualified_name(decl_node)
            if qualified and "::" in qualified:
                fn.name = qualified.replace("::", ".")
                fn._metadata["qualified_name"] = qualified
        return fn

    def _extract_qualified_name(self, node: Any) -> Optional[str]:
        """Walk a declarator tree to find a qualified_identifier."""
        if node is None:
            return None
        if node.type == "qualified_identifier":
            return self._get_text(node)
        # Recurse into function_declarator / pointer_declarator
        inner = node.child_by_field_name("declarator")
        if inner:
            return self._extract_qualified_name(inner)
        return None

    # ------------------------------------------------------------------
    # C++ method declarations inside class body (stubs)
    # ------------------------------------------------------------------

    def visit_field_declaration(self, node: Any) -> Optional[Any]:
        """
        Handle field_declaration nodes inside C++ class bodies.

        [20260224_BUGFIX] In tree-sitter-cpp, member declarations inside a
        class body are emitted as field_declaration, not declaration.
        A field_declaration that carries a function_declarator is a method
        prototype and becomes an IRFunctionDef stub; plain field declarations
        become IRAssign nodes (field initializers).
        """
        type_node = node.child_by_field_name("type")
        # Collect all declarator children
        for child in node.children:
            if not child.is_named:
                continue
            if child.type == "function_declarator":
                return self._parse_method_stub(type_node, child, node)
            elif child.type in ("pointer_declarator", "reference_declarator"):
                inner = child.child_by_field_name("declarator")
                if inner and inner.type == "function_declarator":
                    return self._parse_method_stub(type_node, inner, node)
        # Plain field — treat like a C declaration (field name = IRAssign)
        return super().visit_declaration(node)

    def visit_declaration(self, node: Any) -> Optional[Any]:
        """
        Extend C declaration handling for C++ method stubs inside classes.

        A declaration with a function_declarator is a method prototype:
            int area() const;
            Vec3(float x, float y);   (constructor prototype)

        These become IRFunctionDef stubs with empty bodies.
        """
        # Detect if this is a function prototype
        type_node = node.child_by_field_name("type")
        for child in node.children_by_field_name("declarator"):
            if child.type == "function_declarator":
                return self._parse_method_stub(type_node, child, node)
            elif child.type in ("pointer_declarator", "reference_declarator"):
                inner = child.child_by_field_name("declarator")
                if inner and inner.type == "function_declarator":
                    return self._parse_method_stub(type_node, inner, node)

        # Otherwise fall back to C's variable declaration handling
        return super().visit_declaration(node)

    def _parse_method_stub(
        self, type_node: Any, fn_decl: Any, full_node: Any
    ) -> IRFunctionDef:
        """Create an IRFunctionDef stub from a method prototype declaration."""
        name_node = fn_decl.child_by_field_name("declarator")
        name = self._unwrap_declarator_name(name_node) if name_node else "unknown"
        params: List[IRParameter] = []
        params_node = fn_decl.child_by_field_name("parameters")
        if params_node:
            params = self._parse_parameters(params_node)
        return_type = self._type_text(type_node)
        stub = IRFunctionDef(
            name=name,
            params=params,
            body=[],  # No body — this is a declaration
            return_type=return_type,
            source_language=self.language,
            loc=self._get_location(full_node),
        )
        stub._metadata["is_declaration"] = True
        return stub

    # ------------------------------------------------------------------
    # Operator overloads
    # ------------------------------------------------------------------

    def visit_operator_cast(self, node: Any) -> Optional[IRFunctionDef]:
        """operator float() — skip, too complex."""
        return None

    # ------------------------------------------------------------------
    # Exception handling (C++ try/catch)
    # ------------------------------------------------------------------

    def visit_try_statement(self, node: Any) -> Optional[IRNode]:
        """try { ... } catch (...) { ... } — visit body, skip catch details."""
        body_node = node.child_by_field_name("body")
        if body_node:
            stmts = self._visit_body(body_node)
            if stmts:
                return stmts[0] if len(stmts) == 1 else None
        return None

    # ------------------------------------------------------------------
    # Lambda expressions
    # ------------------------------------------------------------------

    def visit_lambda_expression(self, node: Any) -> IRFunctionDef:
        """
        [](float x) { return x * 2; }  — inline anonymous function.

        [20260224_FEATURE] Lambdas become anonymous IRFunctionDef.
        """
        params_node = node.child_by_field_name("parameters")
        body_node = node.child_by_field_name("body")
        params: List[IRParameter] = []
        if params_node:
            params = self._parse_parameters(params_node)
        body = self._as_body(body_node) if body_node else []
        fn = IRFunctionDef(
            name="<lambda>",
            params=params,
            body=body,
            source_language=self.language,
            loc=self._get_location(node),
        )
        fn._metadata["is_lambda"] = True
        return fn

    # ------------------------------------------------------------------
    # Initializer lists (common in 3D code: Vec3{1,0,0})
    # ------------------------------------------------------------------

    def visit_initializer_list(self, node: Any) -> IRConstant:
        """Vec3{1.0f, 0.0f, 0.0f} — return a constant placeholder."""
        return IRConstant(value=self._get_text(node), loc=self._get_location(node))

    # ------------------------------------------------------------------
    # Scoped identifiers (std::vector, glm::vec3, ...)
    # ------------------------------------------------------------------

    def visit_scoped_identifier(self, node: Any) -> IRName:
        """std::vector, glm::vec3 — preserve as a dotted name."""
        return IRName(
            id=self._get_text(node).replace("::", "."),
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_scoped_namespace_identifier(self, node: Any) -> IRName:
        return IRName(
            id=self._get_text(node).replace("::", "."),
            loc=self._get_location(node),
            source_language=self.language,
        )

    # ------------------------------------------------------------------
    # Type aliases
    # ------------------------------------------------------------------

    def visit_alias_declaration(self, node: Any) -> IRAssign:
        """using Vertex = std::array<float, 3>;"""
        text = self._get_text(node).strip().rstrip(";")
        name_node = node.child_by_field_name("name")
        name = self._get_text(name_node) if name_node else "?"
        return IRAssign(
            targets=[IRName(id=name)],
            value=IRConstant(value=text),
            loc=self._get_location(node),
            source_language=self.language,
        )

    # ------------------------------------------------------------------
    # New / Delete
    # ------------------------------------------------------------------

    def visit_new_expression(self, node: Any) -> IRName:
        """new Vec3(0,0,0) — return name of allocated type."""
        type_node = node.child_by_field_name("type")
        type_text = self._get_text(type_node) if type_node else "unknown"
        return IRName(id=f"new {type_text}", loc=self._get_location(node))

    def visit_delete_expression(self, node: Any) -> IRName:
        """delete ptr — return name."""
        return IRName(id="delete", loc=self._get_location(node))


# ---------------------------------------------------------------------------
# C++ Normalizer
# ---------------------------------------------------------------------------


class CppNormalizer(BaseNormalizer):
    """
    Normalizes C++ source code to Unified IR using tree-sitter-cpp.

    [20260224_FEATURE] C++ language support for:
    - Class extraction (extract_code) — classes, structs, templates
    - Function/method extraction including qualified names (Vec3::dot)
    - namespace transparency (body folded into parent scope)
    - template_declaration unwrapping
    - using declarations as IRImport
    - Lambda expressions as anonymous IRFunctionDef
    - All C constructs inherited from CNormalizer (via CppVisitor < CVisitor)

    3D-specific patterns handled:
        class Vec3 / struct Vertex / template<T> class AABB
        void Mesh::render(const Camera& cam) { ... }
        namespace glm { ... }
        using glm::vec3;

    Supported file extensions: .cpp, .cc, .cxx, .c++, .hpp, .hxx, .hh, .h++
    """

    @property
    def language(self) -> str:
        return "cpp"

    _MAX_CACHE: int = 16
    _tree_cache: Dict[int, Any] = {}

    def __init__(self) -> None:
        self._ts_language = Language(tree_sitter_cpp.language())
        self._parser = Parser()
        self._parser.language = self._ts_language
        self._visitor: Optional[CppVisitor] = None

    def normalize(self, source: str, filename: str = "<string>") -> IRModule:
        """Parse C++ source and return a Unified IRModule."""
        tree = self._parse_cached(source)
        self._visitor = CppVisitor(source)
        result = self._visitor.visit(tree.root_node)
        return cast(IRModule, result)

    def _parse_cached(self, source: str) -> Any:
        key = hash(source)
        cached = self._tree_cache.get(key)
        if cached is not None:
            return cached
        tree = self._parser.parse(bytes(source, "utf-8"))
        if len(self._tree_cache) >= self._MAX_CACHE:
            self._tree_cache.pop(next(iter(self._tree_cache)))
        self._tree_cache[key] = tree
        return tree

    def normalize_node(self, node: Any) -> Any:
        if self._visitor is None:
            raise RuntimeError("normalize() must be called before normalize_node()")
        return self._visitor.visit(node)
