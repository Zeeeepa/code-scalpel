"""
C# Normalizer - Converts C# CST (tree-sitter-c-sharp) to Unified IR.

[20260224_FEATURE] C# language support for surgical extraction and analysis.

Key Mappings:
    compilation_unit          -> IRModule
    namespace_declaration     -> transparent (fold into parent, tag with namespace)
    class_declaration         -> IRClassDef
    struct_declaration        -> IRClassDef  (kind='struct')
    interface_declaration     -> IRClassDef  (kind='interface')
    enum_declaration          -> IRClassDef  (kind='enum')
    method_declaration        -> IRFunctionDef
    constructor_declaration   -> IRFunctionDef (is_constructor=True)
    local_function_statement  -> IRFunctionDef (top-level / nested)
    using_directive           -> IRImport
    field_declaration         -> IRAssign
    return_statement          -> IRReturn
    binary_expression         -> IRBinaryOp  (arithmetic/bitwise) or IRConstant
    invocation_expression     -> IRCall
    identifier                -> IRName
    literal                   -> IRConstant

Tree-sitter field notes (C# grammar uses positional children, not field names):
    class_declaration:       modifier*, 'class', identifier, base_list?, declaration_list
    method_declaration:      modifier*, return_type, identifier, type_parameter_list?,
                             parameter_list, block
    constructor_declaration: modifier*, identifier, parameter_list, block
    parameter:               type identifier
    namespace_declaration:   'namespace', identifier/qualified_name, declaration_list
    using_directive:         'using', identifier/qualified_name, ';'
    field_declaration:       modifier*, variable_declaration ';'
    variable_declaration:    type variable_declarator+
    binary_expression:       left, operator, right
    invocation_expression:   expression, argument_list
    base_list:               ':', base_type+
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, cast

import tree_sitter_c_sharp
from tree_sitter import Language, Parser

from ..nodes import (
    IRAssign,
    IRBinaryOp,
    IRBreak,
    IRCall,
    IRClassDef,
    IRConstant,
    IRContinue,
    IRExpr,
    IRExprStmt,
    IRFor,
    IRFunctionDef,
    IRIf,
    IRImport,
    IRModule,
    IRName,
    IRNode,
    IRParameter,
    IRReturn,
    IRSwitch,
    IRWhile,
    SourceLocation,
)
from ..operators import BinaryOperator
from .base import BaseNormalizer
from .tree_sitter_visitor import TreeSitterVisitor

# ---------------------------------------------------------------------------
# Binary operator map (arithmetic + bitwise only; comparison/logical fall back)
# ---------------------------------------------------------------------------

_BINOP_MAP: Dict[str, BinaryOperator] = {
    "+": BinaryOperator.ADD,
    "-": BinaryOperator.SUB,
    "*": BinaryOperator.MUL,
    "/": BinaryOperator.DIV,
    "%": BinaryOperator.MOD,
    "&": BinaryOperator.BIT_AND,
    "|": BinaryOperator.BIT_OR,
    "^": BinaryOperator.BIT_XOR,
    "<<": BinaryOperator.LSHIFT,
    ">>": BinaryOperator.RSHIFT,
}

# Node types that represent a C# type expression
_TYPE_NODES = {
    "predefined_type",
    "identifier",
    "generic_name",
    "qualified_name",
    "nullable_type",
    "array_type",
    "pointer_type",
    "void_keyword",
    # [20260224_BUGFIX] Tuple return types like (int row, int col) weren't recognised
    "tuple_type",
}

# Modifier node types (access/other modifier keywords)
_MODIFIER_TYPES = {"modifier", "access_modifier"}


# ---------------------------------------------------------------------------
# Helper to extract the plain text of a qualified or simple name
# ---------------------------------------------------------------------------


def _name_text(node: Any, source: str) -> str:
    """Return dot-separated text of an identifier or qualified_name node."""
    return source[node.start_byte : node.end_byte]


# ---------------------------------------------------------------------------
# Visitor
# ---------------------------------------------------------------------------


class CSharpVisitor(TreeSitterVisitor):
    """Visitor that converts tree-sitter C# CST nodes to Unified IR."""

    @property
    def language(self) -> str:
        return "csharp"

    def __init__(self, source: str = ""):
        super().__init__()
        self.ctx.source = source

    # ------------------------------------------------------------------
    # Required abstract helpers
    # ------------------------------------------------------------------

    def _get_node_type(self, node: Any) -> str:
        return node.type

    def _get_text(self, node: Any) -> str:
        return self.ctx.source[node.start_byte : node.end_byte]

    def _get_location(self, node: Any) -> Optional[SourceLocation]:
        if node is None:
            return None
        return SourceLocation(
            line=node.start_point[0] + 1,
            column=node.start_point[1],
            end_line=node.end_point[0] + 1,
            end_column=node.end_point[1],
        )

    def _get_children(self, node: Any) -> List[Any]:
        return node.children

    def _get_named_children(self, node: Any) -> List[Any]:
        return [c for c in node.children if c.is_named]

    def _get_child_by_field(self, node: Any, field_name: str) -> Optional[Any]:
        return node.child_by_field_name(field_name)

    def _get_children_by_field(self, node: Any, field_name: str) -> List[Any]:
        return node.children_by_field_name(field_name)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _type_text(self, node: Optional[Any]) -> Optional[str]:
        """Return string form of a type node."""
        if node is None:
            return None
        return self._get_text(node)

    def _visit_body(self, node: Any) -> List[IRNode]:
        """Walk a declaration_list / block and collect IR nodes."""
        result: List[IRNode] = []
        for child in node.children:
            if not child.is_named:
                continue
            res = self.visit(child)
            if res is None:
                continue
            if isinstance(res, list):
                result.extend(res)
            else:
                result.append(cast(IRNode, res))
        return result

    def _parse_parameters(self, param_list_node: Any) -> List[IRParameter]:
        """Build a list of IRParameter from a parameter_list node."""
        params: List[IRParameter] = []
        for child in param_list_node.children:
            if child.type == "parameter":
                p = self._visit_parameter(child)
                if p:
                    params.append(p)
        return params

    def _visit_parameter(self, node: Any) -> Optional[IRParameter]:
        """
        Parse a single parameter node.

        C# parameter children: [type_annotation] [identifier]
        Named children are the type then the name.
        """
        named = [c for c in node.children if c.is_named]
        if not named:
            return None
        if len(named) == 1:
            # Just a name (minimal case)
            return IRParameter(name=self._get_text(named[0]))
        # First named child = type annotation, second = name
        type_ann = self._get_text(named[0])
        name = self._get_text(named[-1])
        return IRParameter(name=name, type_annotation=type_ann)

    def _parse_method_children(self, node: Any):
        """
        Walk method_declaration children to extract return type, name, params,
        type param names, and body.

        Returns (return_type_str, name_str, [IRParameter], [str], body_stmts)
        C# method_declaration has no named fields; we scan positional children:
          modifier*  return_type  identifier  type_parameter_list?
          parameter_list  block | ';'
        """
        seen_type = False
        return_type: Optional[str] = None
        name: Optional[str] = None
        params: List[IRParameter] = []
        tparams: List[str] = []
        body_stmts: List[IRNode] = []

        for child in node.children:
            t = child.type
            if not child.is_named:
                continue
            if t == "modifier":
                continue  # skip public, static, async, etc.
            if t in _TYPE_NODES and not seen_type:
                return_type = self._get_text(child)
                seen_type = True
                continue
            if t == "identifier" and name is None:
                name = self._get_text(child)
                continue
            if t == "type_parameter_list":
                for tp in child.children:
                    if tp.type == "type_parameter":
                        tpname = tp.child_by_field_name("name") or None
                        if tpname:
                            tparams.append(self._get_text(tpname))
                        else:
                            inner_ids = [
                                x for x in tp.children if x.type == "identifier"
                            ]
                            if inner_ids:
                                tparams.append(self._get_text(inner_ids[-1]))
                continue
            if t == "parameter_list":
                params = self._parse_parameters(child)
                continue
            if t in ("block", "arrow_expression_clause"):
                body_stmts = self._visit_body(child)
                continue

        return return_type, name, params, tparams, body_stmts

    def _collect_base_types(self, node: Any) -> List[IRExpr]:
        """Extract base types from a base_list node."""
        bases: List[IRExpr] = []
        for child in node.children:
            if child.type in ("identifier", "qualified_name", "generic_name"):
                bases.append(IRName(id=self._get_text(child)))
            elif child.type == "primary_constructor_base_type":
                for inner in child.children:
                    if inner.type in ("identifier", "qualified_name", "generic_name"):
                        bases.append(IRName(id=self._get_text(inner)))
                        break
        return bases

    def _find_base_list(self, node: Any) -> Optional[Any]:
        """Return the base_list child of a type declaration, or None."""
        for child in node.children:
            if child.type == "base_list":
                return child
        return None

    def _find_declaration_list(self, node: Any) -> Optional[Any]:
        """Return the declaration_list body of a type declaration, or None."""
        for child in node.children:
            if child.type == "declaration_list":
                return child
        return None

    def _find_identifier(self, node: Any) -> Optional[str]:
        """Return the text of the first direct identifier child."""
        fn = node.child_by_field_name("name")
        if fn:
            return self._get_text(fn)
        for child in node.children:
            if child.type == "identifier" and child.is_named:
                return self._get_text(child)
        return None

    # ------------------------------------------------------------------
    # Root
    # ------------------------------------------------------------------

    def visit_compilation_unit(self, node: Any) -> IRModule:
        """
        compilation_unit is the root of a C# file.

        [20260224_FEATURE] C# compilation unit → IRModule.
        """
        body: List[IRNode] = []
        for child in node.children:
            if not child.is_named:
                continue
            res = self.visit(child)
            if res is None:
                continue
            if isinstance(res, list):
                body.extend(res)
            else:
                body.append(cast(IRNode, res))
        return IRModule(
            body=body,
            source_language=self.language,
            loc=self._get_location(node),
        )

    # ------------------------------------------------------------------
    # Namespaces — transparent (fold children into parent scope)
    # ------------------------------------------------------------------

    def visit_namespace_declaration(self, node: Any) -> Optional[List[IRNode]]:
        """
        namespace MyApp { ... }
        namespace MyApp.Utils { ... }

        [20260224_FEATURE] Namespaces are transparent — fold declarations into
        the parent scope, tagging each node with the namespace name.
        """
        # Name can be identifier or qualified_name
        ns_name: str = "<anon>"
        for child in node.children:
            if child.type in ("identifier", "qualified_name") and child.is_named:
                ns_name = self._get_text(child)
                break

        decl_list = self._find_declaration_list(node)
        if decl_list is None:
            return None

        children = self._visit_body(decl_list)
        for child in children:
            child._metadata.setdefault("namespace", ns_name)
        return children

    # ------------------------------------------------------------------
    # Type declarations → IRClassDef
    # ------------------------------------------------------------------

    def _make_class_def(self, node: Any, kind: str = "class") -> Optional[IRClassDef]:
        """Shared factory for class/struct/interface → IRClassDef."""
        name = self._find_identifier(node)
        if not name:
            return None

        # Base types
        base_list_node = self._find_base_list(node)
        bases: List[IRExpr] = []
        if base_list_node is not None:
            bases = self._collect_base_types(base_list_node)

        # Body
        decl_list = self._find_declaration_list(node)
        body: List[IRNode] = self._visit_body(decl_list) if decl_list else []

        # Generic type parameters
        tparams: List[str] = []
        for child in node.children:
            if child.type == "type_parameter_list":
                for tp in child.children:
                    if tp.type == "type_parameter":
                        inner_ids = [x for x in tp.children if x.type == "identifier"]
                        if inner_ids:
                            tparams.append(self._get_text(inner_ids[-1]))

        cls = IRClassDef(
            name=name,
            bases=bases,
            body=body,
            source_language=self.language,
            loc=self._get_location(node),
        )
        cls._metadata["kind"] = kind
        if tparams:
            cls._metadata["type_params"] = tparams
        return cls

    def visit_class_declaration(self, node: Any) -> Optional[IRClassDef]:
        """public class Vec3 { ... }

        [20260224_FEATURE] C# class → IRClassDef.
        """
        return self._make_class_def(node, kind="class")

    def visit_struct_declaration(self, node: Any) -> Optional[IRClassDef]:
        """struct Color { ... }

        [20260224_FEATURE] C# struct → IRClassDef with kind='struct'.
        """
        return self._make_class_def(node, kind="struct")

    def visit_interface_declaration(self, node: Any) -> Optional[IRClassDef]:
        """interface IRenderable { ... }

        [20260224_FEATURE] C# interface → IRClassDef with kind='interface'.
        """
        return self._make_class_def(node, kind="interface")

    def visit_record_declaration(self, node: Any) -> Optional[IRClassDef]:
        """record Person(string Name, int Age);

        [20260224_FEATURE] C# record → IRClassDef with kind='record'.
        """
        return self._make_class_def(node, kind="record")

    def visit_enum_declaration(self, node: Any) -> Optional[IRClassDef]:
        """enum Axis { X, Y, Z }

        [20260224_FEATURE] C# enum → IRClassDef with kind='enum'.
        """
        name = self._find_identifier(node)
        if not name:
            return None

        # enum members → IRAssign nodes
        members: List[IRNode] = []
        for child in node.children:
            if child.type == "enum_member_declaration_list":
                for m in child.children:
                    if m.type == "enum_member_declaration":
                        mname_node = None
                        mval_node = None
                        for sub in m.children:
                            if sub.type == "identifier" and mname_node is None:
                                mname_node = sub
                            elif sub.is_named and mname_node:
                                mval_node = sub
                        if mname_node:
                            val = (
                                IRConstant(value=self._get_text(mval_node))
                                if mval_node
                                else IRConstant(value=None)
                            )
                            a = IRAssign(
                                targets=[IRName(id=self._get_text(mname_node))],
                                value=val,
                                source_language=self.language,
                            )
                            members.append(a)

        cls = IRClassDef(
            name=name,
            bases=[],
            body=members,
            source_language=self.language,
            loc=self._get_location(node),
        )
        cls._metadata["kind"] = "enum"
        return cls

    # ------------------------------------------------------------------
    # Methods and constructors
    # ------------------------------------------------------------------

    def visit_method_declaration(self, node: Any) -> Optional[IRFunctionDef]:
        """
        public float Dot(Vec3 o) { return X*o.X; }

        [20260224_FEATURE] C# method → IRFunctionDef.
        """
        return_type, name, params, tparams, body = self._parse_method_children(node)
        if not name:
            return None
        fn = IRFunctionDef(
            name=name,
            params=params,
            body=body,
            return_type=return_type,
            source_language=self.language,
            loc=self._get_location(node),
        )
        if tparams:
            fn._metadata["type_params"] = tparams
        return fn

    def visit_constructor_declaration(self, node: Any) -> Optional[IRFunctionDef]:
        """
        public Vec3(float x) { X = x; }

        [20260224_FEATURE] C# constructor → IRFunctionDef with is_constructor=True.
        """
        name: Optional[str] = None
        params: List[IRParameter] = []
        body: List[IRNode] = []

        for child in node.children:
            t = child.type
            if not child.is_named:
                continue
            if t == "modifier":
                continue
            if t == "identifier" and name is None:
                name = self._get_text(child)
            elif t == "parameter_list":
                params = self._parse_parameters(child)
            elif t == "block":
                body = self._visit_body(child)

        if not name:
            return None
        fn = IRFunctionDef(
            name=name,
            params=params,
            body=body,
            return_type=name,  # constructors "return" their own type
            source_language=self.language,
            loc=self._get_location(node),
        )
        fn._metadata["is_constructor"] = True
        return fn

    def visit_operator_declaration(self, node: Any) -> Optional[IRFunctionDef]:
        """
        public static Vec2 operator+(Vec2 a, Vec2 b) { ... }

        [20260224_BUGFIX] C# operator declarations now surface as IRFunctionDef
        with name 'operator<symbol>' (e.g. 'operator+', 'operator==').
        """
        children = node.children
        # Find the 'operator' keyword position; the symbol follows immediately
        op_symbol: Optional[str] = None
        op_index: Optional[int] = None
        for i, child in enumerate(children):
            if child.type == "operator":
                op_index = i
                if i + 1 < len(children):
                    op_symbol = self._get_text(children[i + 1]).strip()
                break
        if op_index is None or not op_symbol:
            return None

        # Named children before the 'operator' keyword → return type (skip modifiers)
        return_type: Optional[str] = None
        seen_type = False
        for child in children[:op_index]:
            t = child.type
            if not child.is_named:
                continue
            if t in ("modifier", "access_modifier"):
                continue
            if t in _TYPE_NODES and not seen_type:
                return_type = self._get_text(child)
                seen_type = True

        # Remaining named children → parameter_list and block
        params: List[IRParameter] = []
        body_stmts: List[IRNode] = []
        for child in children[op_index + 2 :]:
            if not child.is_named:
                continue
            t = child.type
            if t == "parameter_list":
                params = self._parse_parameters(child)
            elif t in ("block", "arrow_expression_clause"):
                body_stmts = self._visit_body(child)

        fn = IRFunctionDef(
            name=f"operator{op_symbol}",
            params=params,
            body=body_stmts,
            return_type=return_type,
            source_language=self.language,
            loc=self._get_location(node),
        )
        fn._metadata["is_operator"] = True
        return fn

    def visit_local_function_statement(self, node: Any) -> Optional[IRFunctionDef]:
        """
        Top-level function statements in a compilation_unit (C# 9+ top-level
        statements) or local functions inside methods.

        [20260224_FEATURE] C# local function / top-level statement→ IRFunctionDef.
        """
        return_type, name, params, tparams, body = self._parse_method_children(node)
        if not name:
            return None
        fn = IRFunctionDef(
            name=name,
            params=params,
            body=body,
            return_type=return_type,
            source_language=self.language,
            loc=self._get_location(node),
        )
        if tparams:
            fn._metadata["type_params"] = tparams
        return fn

    def visit_global_statement(self, node: Any) -> Optional[Any]:
        """
        Wrap top-level statements (C# 9+, e.g. Console.WriteLine("hi")).

        [20260224_FEATURE] Unwrap global_statement to its inner statement.
        """
        for child in node.children:
            if child.is_named:
                return self.visit(child)
        return None

    def visit_property_declaration(self, node: Any) -> Optional[IRFunctionDef]:
        """
        public float X { get; set; }

        [20260224_FEATURE] Properties become stub IRFunctionDef nodes
        tagged with is_property=True so they are discoverable by extract_code.
        """
        name: Optional[str] = None
        return_type: Optional[str] = None
        seen_type = False
        for child in node.children:
            t = child.type
            if not child.is_named:
                continue
            if t == "modifier":
                continue
            if t in _TYPE_NODES and not seen_type:
                return_type = self._get_text(child)
                seen_type = True
                continue
            if t == "identifier" and name is None:
                name = self._get_text(child)
                continue
        if not name:
            return None
        fn = IRFunctionDef(
            name=name,
            params=[],
            body=[],
            return_type=return_type,
            source_language=self.language,
            loc=self._get_location(node),
        )
        fn._metadata["is_property"] = True
        return fn

    # ------------------------------------------------------------------
    # Using directives → IRImport
    # ------------------------------------------------------------------

    def visit_using_directive(self, node: Any) -> Optional[IRImport]:
        """
        using System;
        using System.Collections.Generic;
        using static System.Math;
        using Alias = System.Collections.Generic.List<int>;

        [20260224_FEATURE] C# using directive → IRImport.
        """
        names: List[str] = []
        module: str = "unknown"

        for child in node.children:
            t = child.type
            if not child.is_named:
                continue
            if t in (
                "identifier",
                "qualified_name",
                "generic_name",
                "alias_qualified_name",
            ):
                module = self._get_text(child)
                # last segment becomes the names list
                parts = module.rsplit(".", 1)
                names = [parts[-1]]
            # 'using static Foo' — skip the 'static' modifier (already a named child)

        return IRImport(
            module=module,
            names=names,
            source_language=self.language,
            loc=self._get_location(node),
        )

    # ------------------------------------------------------------------
    # Field declarations → IRAssign
    # ------------------------------------------------------------------

    def visit_field_declaration(self, node: Any) -> Optional[Any]:
        """
        public float X, Y, Z;
        private int _count = 0;

        [20260224_FEATURE] Field declarations → IRAssign per declarator.
        """
        var_decl = None
        type_str: Optional[str] = None
        for child in node.children:
            if not child.is_named:
                continue
            if child.type == "variable_declaration":
                var_decl = child
                break

        if var_decl is None:
            return None

        results: List[IRNode] = []
        for child in var_decl.children:
            t = child.type
            if t in _TYPE_NODES and type_str is None:
                type_str = self._get_text(child)
            if t == "variable_declarator":
                # identifier, optional '=' + initializer
                vname_node = None
                vval_node = None
                eq_seen = False
                for sub in child.children:
                    if sub.type == "identifier" and vname_node is None:
                        vname_node = sub
                    elif sub.type == "=":
                        eq_seen = True
                    elif eq_seen and sub.is_named:
                        vval_node = sub
                if vname_node:
                    target = IRName(id=self._get_text(vname_node))
                    value = (
                        IRConstant(value=self._get_text(vval_node))
                        if vval_node
                        else IRConstant(value=None)
                    )
                    a = IRAssign(
                        targets=[target],
                        value=value,
                        source_language=self.language,
                        loc=self._get_location(child),
                    )
                    a._metadata["type_annotation"] = type_str
                    results.append(a)

        return results if len(results) > 1 else (results[0] if results else None)

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def visit_return_statement(self, node: Any) -> IRReturn:
        """return x * y;"""
        val_node = None
        for child in node.children:
            if child.is_named and child.type != "return":
                val_node = child
                break
        val = self.visit(val_node) if val_node else None
        return IRReturn(
            value=cast(Any, val) if val and not isinstance(val, list) else None,
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_if_statement(self, node: Any) -> IRIf:
        """if (cond) { ... } else { ... }"""
        cond_node = node.child_by_field_name("condition")
        cons_node = node.child_by_field_name("consequence")
        alt_node = node.child_by_field_name("alternative")

        cond = cast(Any, self.visit(cond_node)) if cond_node else IRConstant(value=True)
        cons = self._visit_body(cons_node) if cons_node else []
        orelse: List[IRNode] = []
        if alt_node:
            res = self.visit(alt_node)
            if isinstance(res, list):
                orelse = res
            elif res:
                orelse = [cast(IRNode, res)]

        return IRIf(
            # [20260224_BUGFIX] IRIf uses `test`, not `condition`
            test=cond,
            body=cons,
            orelse=orelse,
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_while_statement(self, node: Any) -> IRWhile:
        """while (condition) { ... }"""
        cond_node = node.child_by_field_name("condition")
        body_node = node.child_by_field_name("body")
        cond = cast(Any, self.visit(cond_node)) if cond_node else IRConstant(value=True)
        body = self._visit_body(body_node) if body_node else []
        return IRWhile(
            # [20260224_BUGFIX] IRWhile uses `test`, not `condition`
            test=cond,
            body=body,
            orelse=[],
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_for_statement(self, node: Any) -> IRFor:
        """for (init; cond; update) { ... }"""
        body_node = node.child_by_field_name("body")
        cond_node = node.child_by_field_name("condition")
        body = self._visit_body(body_node) if body_node else []
        cond = cast(Any, self.visit(cond_node)) if cond_node else IRConstant(value=True)
        fn = IRFor(
            target=IRName(id="__for__"),
            iter=cond,
            body=body,
            orelse=[],
            is_for_in=False,
            source_language=self.language,
            loc=self._get_location(node),
        )
        fn._metadata["for_kind"] = "for"
        return fn

    def visit_foreach_statement(self, node: Any) -> IRFor:
        """foreach (var item in collection) { ... }"""
        var_node = node.child_by_field_name("left")
        coll_node = node.child_by_field_name("right")
        body_node = node.child_by_field_name("body")

        target = cast(Any, self.visit(var_node)) if var_node else IRName(id="__item__")
        iter_val = (
            cast(Any, self.visit(coll_node)) if coll_node else IRConstant(value=None)
        )
        body = self._visit_body(body_node) if body_node else []
        return IRFor(
            target=target if not isinstance(target, list) else IRName(id="__item__"),
            iter=iter_val if not isinstance(iter_val, list) else IRConstant(value=None),
            body=body,
            orelse=[],
            is_for_in=True,
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_switch_statement(self, node: Any) -> IRSwitch:
        """switch (expr) { case X: ... default: ... }"""
        val_node = node.child_by_field_name("value")
        disc = cast(Any, self.visit(val_node)) if val_node else IRConstant(value=None)
        cases: List[Any] = []
        for child in node.children:
            if child.type == "switch_body":
                for section in child.children:
                    if section.type == "switch_section":
                        labels = []
                        stmts: List[IRNode] = []
                        for sub in section.children:
                            if sub.type in (
                                "case_switch_label",
                                "default_switch_label",
                            ):
                                expr = None
                                for lab_child in sub.children:
                                    if lab_child.is_named and lab_child.type not in (
                                        "case",
                                        "default",
                                        ":",
                                    ):
                                        r = self.visit(lab_child)
                                        if r and not isinstance(r, list):
                                            expr = r
                                labels.append(expr)
                            elif sub.is_named:
                                r = self.visit(sub)
                                if r:
                                    stmts.extend(
                                        r if isinstance(r, list) else [cast(IRNode, r)]
                                    )
                        for lbl in labels:
                            cases.append((lbl, stmts))
        return IRSwitch(
            discriminant=disc if not isinstance(disc, list) else IRConstant(value=None),
            cases=cases,
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_try_statement(self, node: Any) -> Any:
        """try { ... } catch (...) { ... } finally { ... }"""
        from ..nodes import IRTry

        body_node = node.child_by_field_name("body")
        body = self._visit_body(body_node) if body_node else []
        return IRTry(
            body=body,
            handlers=[],
            orelse=[],
            finalbody=[],
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_break_statement(self, node: Any) -> IRBreak:
        return IRBreak(source_language=self.language, loc=self._get_location(node))

    def visit_continue_statement(self, node: Any) -> IRContinue:
        return IRContinue(source_language=self.language, loc=self._get_location(node))

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def visit_binary_expression(self, node: Any) -> Any:
        """
        Arithmetic/bitwise → IRBinaryOp.
        Comparison/logical → IRConstant(value=text) fallback.
        """
        text = self._get_text(node)
        # Find the operator token
        op_str: Optional[str] = None
        for child in node.children:
            if not child.is_named:
                op_str = self._get_text(child).strip()
                break
        if op_str and op_str in _BINOP_MAP:
            left_node = node.child_by_field_name("left")
            right_node = node.child_by_field_name("right")
            left = (
                cast(Any, self.visit(left_node))
                if left_node
                else IRConstant(value=None)
            )
            right = (
                cast(Any, self.visit(right_node))
                if right_node
                else IRConstant(value=None)
            )
            if not isinstance(left, list) and not isinstance(right, list):
                return IRBinaryOp(
                    op=_BINOP_MAP[op_str],
                    left=left,
                    right=right,
                    source_language=self.language,
                    loc=self._get_location(node),
                )
        return IRConstant(
            value=text,
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_invocation_expression(self, node: Any) -> IRCall:
        """
        Foo.Bar(x, y)  or  Method(arg)
        """
        func_node = node.child_by_field_name("function")
        args_node = node.child_by_field_name("argument_list")

        func_name = self._get_text(func_node) if func_node else "unknown"
        func_ir = IRName(id=func_name)

        args: List[Any] = []
        if args_node:
            for child in args_node.children:
                if child.type == "argument" and child.is_named:
                    r = self.visit(child)
                    if r and not isinstance(r, list):
                        args.append(r)

        return IRCall(
            func=func_ir,
            args=args,
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_argument(self, node: Any) -> Optional[Any]:
        """argument → visit inner expression."""
        for child in node.children:
            if child.is_named:
                return self.visit(child)
        return None

    def visit_expression_statement(self, node: Any) -> Optional[Any]:
        """Wrap expression in IRExprStmt."""
        for child in node.children:
            if child.is_named:
                res = self.visit(child)
                if res and not isinstance(res, list):
                    return IRExprStmt(
                        value=cast(Any, res),
                        source_language=self.language,
                        loc=self._get_location(node),
                    )
        return None

    def visit_assignment_expression(self, node: Any) -> Optional[IRAssign]:
        """x = expr"""
        left_node = node.child_by_field_name("left")
        right_node = node.child_by_field_name("right")
        if not left_node or not right_node:
            return None
        lhs = cast(Any, self.visit(left_node))
        rhs = cast(Any, self.visit(right_node))
        if isinstance(lhs, list) or isinstance(rhs, list):
            return None
        target = (
            lhs if isinstance(lhs, IRName) else IRName(id=self._get_text(left_node))
        )
        return IRAssign(
            targets=[target],
            value=rhs if rhs else IRConstant(value=None),
            source_language=self.language,
            loc=self._get_location(node),
        )

    # ------------------------------------------------------------------
    # Atoms
    # ------------------------------------------------------------------

    def visit_identifier(self, node: Any) -> IRName:
        return IRName(
            id=self._get_text(node),
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_this_expression(self, node: Any) -> IRName:
        return IRName(
            id="this", source_language=self.language, loc=self._get_location(node)
        )

    def visit_integer_literal(self, node: Any) -> IRConstant:
        text = self._get_text(node)
        try:
            base = 16 if text.startswith(("0x", "0X")) else 10
            val: Any = int(text.rstrip("Uu Ll").replace("_", ""), base)
        except ValueError:
            val = text
        return IRConstant(
            value=val, source_language=self.language, loc=self._get_location(node)
        )

    def visit_real_literal(self, node: Any) -> IRConstant:
        text = self._get_text(node)
        try:
            val: Any = float(text.rstrip("fFdDmM").replace("_", ""))
        except ValueError:
            val = text
        return IRConstant(
            value=val, source_language=self.language, loc=self._get_location(node)
        )

    def visit_boolean_literal(self, node: Any) -> IRConstant:
        return IRConstant(
            value=self._get_text(node) == "true",
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_null_literal(self, node: Any) -> IRConstant:
        return IRConstant(
            value=None, source_language=self.language, loc=self._get_location(node)
        )

    def visit_string_literal(self, node: Any) -> IRConstant:
        return IRConstant(
            value=self._get_text(node),
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_character_literal(self, node: Any) -> IRConstant:
        return IRConstant(
            value=self._get_text(node),
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_member_access_expression(self, node: Any) -> IRName:
        """obj.Member → IRName(id='obj.Member')"""
        return IRName(
            id=self._get_text(node),
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_qualified_name(self, node: Any) -> IRName:
        """System.Collections.Generic → IRName"""
        return IRName(
            id=self._get_text(node),
            source_language=self.language,
            loc=self._get_location(node),
        )


# ---------------------------------------------------------------------------
# Normalizer wrapper
# ---------------------------------------------------------------------------


class CSharpNormalizer(BaseNormalizer):
    """
    Normalizes C# source code to Unified IR using tree-sitter-c-sharp.

    [20260224_FEATURE] C# language support for:
    - Class, struct, interface, record, enum extraction
    - Method, constructor, property extraction
    - Namespace transparency (fold into parent scope)
    - Generic type parameter tagging
    - Using directive → IRImport
    - Field declarations → IRAssign
    - Control flow: if/while/for/foreach/switch/try
    - Expressions: binary ops, method calls, assignments

    Supported file extensions: .cs
    """

    @property
    def language(self) -> str:
        return "csharp"

    _MAX_CACHE: int = 16
    _tree_cache: Dict[int, Any] = {}

    def __init__(self) -> None:
        self._ts_language = Language(tree_sitter_c_sharp.language())
        self._parser = Parser()
        self._parser.language = self._ts_language
        self._visitor: Optional[CSharpVisitor] = None

    def normalize(self, source: str, filename: str = "<string>") -> IRModule:
        """Parse C# source and return a Unified IRModule."""
        tree = self._parse_cached(source)
        self._visitor = CSharpVisitor(source)
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
