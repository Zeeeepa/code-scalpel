"""
C Normalizer - Converts C CST (tree-sitter-c) to Unified IR.

[20260224_FEATURE] C language support for surgical extraction and analysis.

Key Mappings:
    translation_unit      -> IRModule
    function_definition   -> IRFunctionDef
    struct_specifier      -> IRClassDef (structs are the closest C concept to a class)
    type_definition       -> IRClassDef (typedef struct Point {...} Point;)
    preproc_include       -> IRImport
    preproc_def           -> IRAssign  (constants)
    return_statement      -> IRReturn
    if_statement          -> IRIf
    while_statement       -> IRWhile
    for_statement         -> IRFor
    switch_statement      -> IRSwitch
    call_expression       -> IRCall
    binary_expression     -> IRBinaryOp
    identifier            -> IRName
    number_literal / ...  -> IRConstant

Tree-sitter field names used:
    function_definition:   type, declarator, body
    function_declarator:   declarator (name / pointer_declarator), parameters
    parameter_declaration: type, declarator
    struct_specifier:      name, body  (body = field_declaration_list)
    type_definition:       type (struct_specifier), declarator (type_identifier)
    if_statement:          condition, consequence, alternative
    while_statement:       condition, body
    for_statement:         initializer, condition, update, body
    call_expression:       function, arguments
    binary_expression:     left, operator, right
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, cast

import tree_sitter_c
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
# Operator mapping  (arithmetic + bitwise only — these exist in BinaryOperator)
# Comparison / logical ops fall back to IRConstant(value=text)
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

# ---------------------------------------------------------------------------
# Visitor
# ---------------------------------------------------------------------------


class CVisitor(TreeSitterVisitor):
    """Visitor that converts tree-sitter C CST nodes to Unified IR."""

    @property
    def language(self) -> str:
        return "c"

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

    def _visit_body(self, node: Any) -> List[IRNode]:
        """Visit all named children of a block node and collect IR nodes."""
        results: List[IRNode] = []
        for child in node.children:
            if not child.is_named:
                continue
            res = self.visit(child)
            if res is None:
                continue
            if isinstance(res, list):
                results.extend(res)
            else:
                results.append(cast(IRNode, res))
        return results

    def _unwrap_declarator_name(self, node: Any) -> str:
        """
        Recursively unwrap pointer/array/function declarators to get the base name.

        C declarator forms:
            identifier                      -> name directly
            pointer_declarator > declarator -> recurse into declarator
            array_declarator   > declarator -> recurse into declarator
            function_declarator > declarator -> recurse into declarator
        """
        if node is None:
            return "unknown"
        if node.type == "identifier":
            return self._get_text(node)
        # pointer_declarator / array_declarator / function_declarator
        inner = node.child_by_field_name("declarator")
        if inner:
            return self._unwrap_declarator_name(inner)
        # fallback – just grab the first identifier child
        for child in node.children:
            if child.type == "identifier":
                return self._get_text(child)
        return self._get_text(node)

    def _type_text(self, node: Any) -> Optional[str]:
        """Extract a human-readable type string from a type node."""
        if node is None:
            return None
        return self._get_text(node).strip()

    # ------------------------------------------------------------------
    # Root
    # ------------------------------------------------------------------

    def visit_translation_unit(self, node: Any) -> IRModule:
        """Root node of a C file."""
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
        return IRModule(body=body, source_language=self.language)

    # ------------------------------------------------------------------
    # Preprocessor
    # ------------------------------------------------------------------

    def visit_preproc_include(self, node: Any) -> IRImport:
        """
        #include <stdio.h>
        #include "myfile.h"

        [20260224_FEATURE] Maps to IRImport for cross-reference tracking.
        """
        path_node = None
        for child in node.children:
            if child.type in ("system_lib_string", "string_literal"):
                path_node = child
                break
        raw = self._get_text(path_node) if path_node else self._get_text(node)
        # Strip < > or " "
        module = raw.strip("<>\"' ")
        return IRImport(
            module=module,
            names=[],
            is_star=True,  # C includes bring everything in scope
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_preproc_def(self, node: Any) -> IRAssign:
        """
        #define MAX_SIZE 1024
        #define PI 3.14159

        [20260224_FEATURE] Macro constants become IRAssign for analysis.
        """
        name_node = None
        value_node = None
        for child in node.children:
            if child.type == "identifier":
                name_node = child
            elif child.type == "preproc_arg":
                value_node = child
        name = self._get_text(name_node) if name_node else "UNKNOWN"
        value_text = self._get_text(value_node).strip() if value_node else ""
        # Try to parse value as a number
        try:
            value: Any = int(value_text, 0)
        except (ValueError, TypeError):
            try:
                value = float(value_text)
            except (ValueError, TypeError):
                value = value_text
        return IRAssign(
            targets=[IRName(id=name, loc=self._get_location(name_node))],
            value=IRConstant(value=value),
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_preproc_ifdef(self, node: Any) -> Optional[List[IRNode]]:
        """#ifdef / #ifndef — skip guard blocks, visit inner declarations."""
        return self._visit_body(node)

    visit_preproc_if = visit_preproc_ifdef
    visit_preproc_elif = visit_preproc_ifdef
    visit_preproc_else = visit_preproc_ifdef

    def visit_preproc_function_def(self, node: Any) -> Optional[IRNode]:
        """Function-like macros — skip, too complex to model faithfully."""
        return None

    # ------------------------------------------------------------------
    # Functions
    # ------------------------------------------------------------------

    def visit_function_definition(self, node: Any) -> IRFunctionDef:
        """
        int add(int a, int b) { return a + b; }
        void update(float *pos, float dt) { ... }

        [20260224_FEATURE] Full function definition → IRFunctionDef.
        """
        type_node = node.child_by_field_name("type")
        decl_node = node.child_by_field_name("declarator")
        body_node = node.child_by_field_name("body")

        # Extract name and params from the declarator chain
        name = "unknown"
        params: List[IRParameter] = []

        if decl_node:
            # Walk through pointer declarators to find function_declarator
            fn_decl = decl_node
            while fn_decl and fn_decl.type not in ("function_declarator",):
                inner = fn_decl.child_by_field_name("declarator")
                if inner:
                    fn_decl = inner
                else:
                    break

            if fn_decl and fn_decl.type == "function_declarator":
                name_node = fn_decl.child_by_field_name("declarator")
                name = (
                    self._unwrap_declarator_name(name_node) if name_node else "unknown"
                )
                params_node = fn_decl.child_by_field_name("parameters")
                if params_node:
                    params = self._parse_parameters(params_node)
            else:
                name = self._unwrap_declarator_name(decl_node)

        return_type = self._type_text(type_node)

        # Body
        body_stmts: List[IRNode] = []
        if body_node:
            body_stmts = self._visit_body(body_node)

        return IRFunctionDef(
            name=name,
            params=params,
            body=body_stmts,
            return_type=return_type,
            source_language=self.language,
            loc=self._get_location(node),
        )

    def _parse_parameters(self, params_node: Any) -> List[IRParameter]:
        """Parse a parameter_list into a list of IRParameter."""
        params: List[IRParameter] = []
        for child in params_node.children:
            if child.type == "parameter_declaration":
                p = self._visit_parameter_declaration(child)
                if p:
                    params.append(p)
            elif child.type == "variadic_parameter":
                # [20260224_FEATURE] varargs (...)
                params.append(IRParameter(name="...", type_annotation=None))
        return params

    def _visit_parameter_declaration(self, node: Any) -> Optional[IRParameter]:
        """Parse a single parameter_declaration node."""
        type_node = node.child_by_field_name("type")
        decl_node = node.child_by_field_name("declarator")
        name = self._unwrap_declarator_name(decl_node) if decl_node else ""
        type_ann = self._type_text(type_node)
        return IRParameter(name=name, type_annotation=type_ann)

    # ------------------------------------------------------------------
    # Structs / Unions / Typedefs
    # ------------------------------------------------------------------

    def visit_struct_specifier(self, node: Any) -> Optional[IRClassDef]:
        """
        struct Point { int x; int y; };

        [20260224_FEATURE] Structs map to IRClassDef — conceptually the
        closest IR construct for a named aggregate type.
        """
        name_node = node.child_by_field_name("name")
        if name_node is None:
            # Anonymous struct inside typedef — handled by visit_type_definition
            return None
        name = self._get_text(name_node)
        body = self._parse_field_list(node.child_by_field_name("body"))
        return IRClassDef(
            name=name,
            bases=[],
            body=body,
            source_language=self.language,
            loc=self._get_location(node),
        )

    def visit_union_specifier(self, node: Any) -> Optional[IRClassDef]:
        """union Value { int i; float f; };  — treated like a struct."""
        name_node = node.child_by_field_name("name")
        if name_node is None:
            return None
        name = self._get_text(name_node)
        body = self._parse_field_list(node.child_by_field_name("body"))
        cls = IRClassDef(
            name=name,
            bases=[],
            body=body,
            source_language=self.language,
            loc=self._get_location(node),
        )
        cls._metadata["kind"] = "union"
        return cls

    def visit_enum_specifier(self, node: Any) -> Optional[IRClassDef]:
        """enum Color { RED, GREEN, BLUE }; — treated as a named group of constants."""
        name_node = node.child_by_field_name("name")
        if name_node is None:
            return None
        name = self._get_text(name_node)
        body_node = node.child_by_field_name("body")
        body: List[IRNode] = []
        if body_node:
            for child in body_node.children:
                if child.type == "enumerator":
                    enum_name_node = child.child_by_field_name("name")
                    enum_val_node = child.child_by_field_name("value")
                    ename = self._get_text(enum_name_node) if enum_name_node else ""
                    if enum_val_node:
                        val_text = self._get_text(enum_val_node).strip()
                        try:
                            val: Any = int(val_text, 0)
                        except ValueError:
                            val = val_text
                        body.append(
                            IRAssign(
                                targets=[IRName(id=ename)],
                                value=IRConstant(value=val),
                                loc=self._get_location(child),
                                source_language=self.language,
                            )
                        )
                    else:
                        body.append(IRName(id=ename, loc=self._get_location(child)))
        cls = IRClassDef(
            name=name,
            bases=[],
            body=body,
            source_language=self.language,
            loc=self._get_location(node),
        )
        cls._metadata["kind"] = "enum"
        return cls

    def visit_type_definition(self, node: Any) -> Optional[IRClassDef]:
        """
        typedef struct { int x; int y; } Point;
        typedef int MyInt;

        [20260224_FEATURE] typedef struct → IRClassDef with typedef name.
        """
        # Find the struct/union/enum specifier
        spec_node = None
        name_node = None
        for child in node.children:
            if child.type in ("struct_specifier", "union_specifier", "enum_specifier"):
                spec_node = child
            elif child.type == "type_identifier":
                name_node = child  # typedef alias name

        if spec_node is None or name_node is None:
            return None  # Simple typedef like `typedef int MyInt`

        typedef_name = self._get_text(name_node)
        # Parse the body of the struct/union/enum
        body = self._parse_field_list(spec_node.child_by_field_name("body"))
        # The original struct name (if any)
        orig_name_node = spec_node.child_by_field_name("name")
        cls = IRClassDef(
            name=typedef_name,
            bases=[],
            body=body,
            source_language=self.language,
            loc=self._get_location(node),
        )
        if orig_name_node:
            cls._metadata["struct_name"] = self._get_text(orig_name_node)
        cls._metadata["kind"] = spec_node.type.replace("_specifier", "")
        return cls

    def _parse_field_list(self, body_node: Any) -> List[IRNode]:
        """Parse a field_declaration_list into IRAssign stubs for each field."""
        if body_node is None:
            return []
        result: List[IRNode] = []
        for child in body_node.children:
            if child.type == "field_declaration":
                type_node = child.child_by_field_name("type")
                type_ann = self._type_text(type_node)
                for dec in child.children_by_field_name("declarator"):
                    fname = self._unwrap_declarator_name(dec)
                    fld = IRAssign(
                        targets=[IRName(id=fname)],
                        value=IRConstant(value=None),
                        loc=self._get_location(dec),
                        source_language=self.language,
                    )
                    if type_ann:
                        fld._metadata["type_annotation"] = type_ann
                    result.append(fld)
        return result

    # ------------------------------------------------------------------
    # Declarations (variable declarations at file/block scope)
    # ------------------------------------------------------------------

    def visit_declaration(self, node: Any) -> Optional[List[IRAssign]]:
        """
        int x = 5;
        float vertices[3] = {0.0f, 1.0f, 2.0f};

        [20260224_FEATURE] Variable declarations become IRAssign.
        """
        type_node = node.child_by_field_name("type")
        type_ann = self._type_text(type_node)
        results: List[IRAssign] = []
        for dec in node.children_by_field_name("declarator"):
            # init_declarator has fields declarator + value
            if dec.type == "init_declarator":
                name_node = dec.child_by_field_name("declarator")
                val_node = dec.child_by_field_name("value")
                name = self._unwrap_declarator_name(name_node) if name_node else "?"
                val_ir = self.visit(val_node) if val_node else IRConstant(value=None)
                a = IRAssign(
                    targets=[IRName(id=name)],
                    value=cast(Any, val_ir) if val_ir else IRConstant(value=None),
                    loc=self._get_location(dec),
                    source_language=self.language,
                )
                if type_ann:
                    a._metadata["type_annotation"] = type_ann
                results.append(a)
            else:
                name = self._unwrap_declarator_name(dec)
                a = IRAssign(
                    targets=[IRName(id=name)],
                    value=IRConstant(value=None),
                    loc=self._get_location(dec),
                    source_language=self.language,
                )
                if type_ann:
                    a._metadata["type_annotation"] = type_ann
                results.append(a)
        return results if results else None

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def visit_compound_statement(self, node: Any) -> List[IRNode]:
        """{ ... } — Just a list of inner statements."""
        return self._visit_body(node)

    def visit_return_statement(self, node: Any) -> IRReturn:
        """return expr;"""
        # The expression is the first named child (after the 'return' keyword)
        value: Optional[IRExpr] = None
        for child in node.children:
            if child.is_named and child.type != "return":
                res = self.visit(child)
                if res and not isinstance(res, list):
                    value = cast(IRExpr, res)
                break
        return IRReturn(
            value=value, loc=self._get_location(node), source_language=self.language
        )

    def visit_if_statement(self, node: Any) -> IRIf:
        """if (cond) { ... } else { ... }"""
        cond_node = node.child_by_field_name("condition")
        cons_node = node.child_by_field_name("consequence")
        alt_node = node.child_by_field_name("alternative")

        cond = cast(Any, self.visit(cond_node)) if cond_node else IRConstant(value=True)
        cons = self._as_body(cons_node)
        alt = self._as_body(alt_node) if alt_node else []

        return IRIf(
            test=cond,
            body=cons,
            orelse=alt,
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_while_statement(self, node: Any) -> IRWhile:
        """while (cond) { body }"""
        cond_node = node.child_by_field_name("condition")
        body_node = node.child_by_field_name("body")
        cond = cast(Any, self.visit(cond_node)) if cond_node else IRConstant(value=True)
        body = self._as_body(body_node)
        return IRWhile(
            test=cond,
            body=body,
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_do_statement(self, node: Any) -> IRWhile:
        """do { body } while (cond);"""
        cond_node = node.child_by_field_name("condition")
        body_node = node.child_by_field_name("body")
        cond = cast(Any, self.visit(cond_node)) if cond_node else IRConstant(value=True)
        body = self._as_body(body_node)
        wh = IRWhile(
            test=cond,
            body=body,
            loc=self._get_location(node),
            source_language=self.language,
        )
        wh._metadata["do_while"] = True
        return wh

    def visit_for_statement(self, node: Any) -> IRFor:
        """for (init; cond; update) { body }"""
        init_node = node.child_by_field_name("initializer")
        cond_node = node.child_by_field_name("condition")
        upd_node = node.child_by_field_name("update")
        body_node = node.child_by_field_name("body")

        init = cast(Any, self.visit(init_node)) if init_node else None
        cond = cast(Any, self.visit(cond_node)) if cond_node else IRConstant(value=True)
        upd = cast(Any, self.visit(upd_node)) if upd_node else None
        body = self._as_body(body_node)

        for_node = IRFor(
            target=init,
            iter=cond,
            body=body,
            loc=self._get_location(node),
            source_language=self.language,
        )
        if upd is not None:
            for_node._metadata["update"] = upd
        return for_node

    def visit_switch_statement(self, node: Any) -> IRSwitch:
        """switch (val) { case X: ...; break; default: ...; }"""
        cond_node = node.child_by_field_name("condition")
        body_node = node.child_by_field_name("body")
        subject = (
            cast(Any, self.visit(cond_node)) if cond_node else IRConstant(value=None)
        )
        cases: List[Any] = []
        defaults: List[Any] = []
        if body_node:
            current_stmts: List[Any] = []
            current_val: Any = None
            for child in body_node.children:
                if child.type == "case_statement":
                    val_node = child.child_by_field_name("value")
                    current_val = cast(Any, self.visit(val_node)) if val_node else None
                    current_stmts = self._visit_body(child)
                    cases.append((current_val, current_stmts))
                elif child.type == "default_statement":
                    defaults = self._visit_body(child)
        all_cases = cases + ([(None, defaults)] if defaults else [])
        return IRSwitch(
            discriminant=subject,
            cases=all_cases,
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_break_statement(self, node: Any) -> IRBreak:
        return IRBreak(loc=self._get_location(node), source_language=self.language)

    def visit_continue_statement(self, node: Any) -> IRContinue:
        return IRContinue(loc=self._get_location(node), source_language=self.language)

    def visit_expression_statement(self, node: Any) -> Optional[IRExprStmt]:
        """expr;"""
        for child in node.children:
            if child.is_named:
                res = self.visit(child)
                if res and not isinstance(res, list):
                    return IRExprStmt(
                        value=cast(Any, res),
                        loc=self._get_location(node),
                        source_language=self.language,
                    )
        return None

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def visit_call_expression(self, node: Any) -> IRCall:
        """func(args...)"""
        func_node = node.child_by_field_name("function")
        args_node = node.child_by_field_name("arguments")
        func = cast(Any, self.visit(func_node)) if func_node else IRName(id="unknown")
        args: List[Any] = []
        if args_node:
            for child in args_node.children:
                if child.is_named:
                    res = self.visit(child)
                    if res and not isinstance(res, list):
                        args.append(cast(Any, res))
        return IRCall(
            func=cast(Any, func),
            args=args,
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_binary_expression(self, node: Any) -> IRNode:
        """a + b, x == y, etc."""
        left_node = node.child_by_field_name("left")
        right_node = node.child_by_field_name("right")
        op_node = node.child_by_field_name("operator")
        op_str = self._get_text(op_node) if op_node else "+"
        op = _BINOP_MAP.get(op_str)
        if op is None:
            # Comparison / logical operators — return a raw IRConstant with source text
            # so the node is not lost but we don’t require extra IR nodes here.
            return IRConstant(value=self._get_text(node), loc=self._get_location(node))
        left = cast(Any, self.visit(left_node)) if left_node else IRConstant(value=0)
        right = cast(Any, self.visit(right_node)) if right_node else IRConstant(value=0)
        return IRBinaryOp(
            left=left,
            op=op,
            right=right,
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_unary_expression(self, node: Any) -> Optional[IRNode]:
        """!x, -x, ++x, *ptr, &var — descend into operand."""
        for child in node.children:
            if child.is_named:
                return cast(Any, self.visit(child))
        return None

    def visit_assignment_expression(self, node: Any) -> IRAssign:
        """x = expr, x += expr, etc."""
        left_node = node.child_by_field_name("left")
        right_node = node.child_by_field_name("right")
        name = self._get_text(left_node) if left_node else "?"
        val = self.visit(right_node) if right_node else IRConstant(value=None)
        return IRAssign(
            targets=[IRName(id=name)],
            value=cast(Any, val) if val else IRConstant(value=None),
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_parenthesized_expression(self, node: Any) -> Optional[IRNode]:
        """( expr ) — unwrap."""
        for child in node.children:
            if child.is_named:
                return cast(Any, self.visit(child))
        return None

    def visit_cast_expression(self, node: Any) -> Optional[IRNode]:
        """(Type)expr — skip the cast, return the inner value."""
        val_node = node.child_by_field_name("value")
        return cast(Any, self.visit(val_node)) if val_node else None

    def visit_sizeof_expression(self, node: Any) -> IRCall:
        """sizeof(T) or sizeof expr — treated as a function call."""
        return IRCall(
            func=IRName(id="sizeof"),
            args=[],
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_subscript_expression(self, node: Any) -> IRName:
        """arr[i] — return a name for the array."""
        arr_node = node.child_by_field_name("argument")
        name = self._get_text(arr_node) if arr_node else "arr"
        return IRName(
            id=name, loc=self._get_location(node), source_language=self.language
        )

    def visit_field_expression(self, node: Any) -> IRName:
        """obj.field or obj->field — return dotted name."""
        arg_node = node.child_by_field_name("argument")
        field_node = node.child_by_field_name("field")
        base = self._get_text(arg_node) if arg_node else ""
        field = self._get_text(field_node) if field_node else ""
        return IRName(
            id=f"{base}.{field}",
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_conditional_expression(self, node: Any) -> Optional[IRNode]:
        """cond ? a : b — return a rough If node."""
        cond_node = node.child_by_field_name("condition")
        cond = cast(Any, self.visit(cond_node)) if cond_node else IRConstant(value=True)
        cons_node = node.child_by_field_name("consequence")
        alt_node = node.child_by_field_name("alternative")
        return IRIf(
            test=cond,
            body=[cast(Any, self.visit(cons_node))] if cons_node else [],
            orelse=[cast(Any, self.visit(alt_node))] if alt_node else [],
            loc=self._get_location(node),
            source_language=self.language,
        )

    # ------------------------------------------------------------------
    # Literals / leaves
    # ------------------------------------------------------------------

    def visit_identifier(self, node: Any) -> IRName:
        return IRName(
            id=self._get_text(node),
            loc=self._get_location(node),
            source_language=self.language,
        )

    def visit_number_literal(self, node: Any) -> IRConstant:
        text = self._get_text(node).rstrip("uUlLfF")
        try:
            v: Any = int(text, 0)
        except ValueError:
            try:
                v = float(text)
            except ValueError:
                v = text
        return IRConstant(value=v, loc=self._get_location(node))

    def visit_string_literal(self, node: Any) -> IRConstant:
        return IRConstant(value=self._get_text(node), loc=self._get_location(node))

    def visit_char_literal(self, node: Any) -> IRConstant:
        return IRConstant(value=self._get_text(node), loc=self._get_location(node))

    def visit_true(self, node: Any) -> IRConstant:
        return IRConstant(value=True, loc=self._get_location(node))

    def visit_false(self, node: Any) -> IRConstant:
        return IRConstant(value=False, loc=self._get_location(node))

    def visit_null(self, node: Any) -> IRConstant:
        return IRConstant(value=None, loc=self._get_location(node))

    # null is a preproc_def for NULL in C, so also handle NULL as identifier
    def visit_null_literal(self, node: Any) -> IRConstant:
        return IRConstant(value=None, loc=self._get_location(node))

    # Concatenated string
    def visit_concatenated_string(self, node: Any) -> IRConstant:
        parts = []
        for child in node.children:
            if child.type == "string_literal":
                parts.append(self._get_text(child))
        return IRConstant(value=" ".join(parts), loc=self._get_location(node))

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _as_body(self, node: Any) -> List[IRNode]:
        """Turn a statement or compound_statement into a flat list of IRNodes."""
        if node is None:
            return []
        if node.type == "compound_statement":
            return self._visit_body(node)
        res = self.visit(node)
        if res is None:
            return []
        if isinstance(res, list):
            return res
        return [cast(IRNode, res)]


# ---------------------------------------------------------------------------
# Normalizer
# ---------------------------------------------------------------------------


class CNormalizer(BaseNormalizer):
    """
    Normalizes C source code to Unified IR using tree-sitter-c.

    [20260224_FEATURE] C language support for:
    - Function extraction (extract_code)
    - Struct/union/enum extraction as IRClassDef
    - #include tracking via IRImport
    - #define constants via IRAssign
    - Control flow: if/while/for/switch
    - Expression analysis: binary ops, calls, assignments

    Supported file extensions: .c, .h
    """

    @property
    def language(self) -> str:
        return "c"

    _MAX_CACHE: int = 16
    _tree_cache: Dict[int, Any] = {}

    def __init__(self) -> None:
        self._ts_language = Language(tree_sitter_c.language())
        self._parser = Parser()
        self._parser.language = self._ts_language
        self._visitor: Optional[CVisitor] = None

    def normalize(self, source: str, filename: str = "<string>") -> IRModule:
        """Parse C source and return a Unified IRModule."""
        tree = self._parse_cached(source)
        self._visitor = CVisitor(source)
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
