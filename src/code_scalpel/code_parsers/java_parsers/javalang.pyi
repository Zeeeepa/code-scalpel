# Type stubs for javalang library
# This file provides type hints for the javalang library which lacks native stubs
from typing import Any, Iterator, Optional, Tuple

class ast:
    class Node:
        position: Optional[Tuple[int, int]]
        def __init__(self) -> None: ...

class tree:
    class CompilationUnit(ast.Node):
        package: Any
        imports: list[Any]
        types: list[Any]
        def filter(self, node_type: type) -> Iterator[Tuple[Tuple[Any, ...], Any]]: ...

    class Identifier(ast.Node):
        value: str

    class ClassDeclaration(ast.Node):
        name: str
        modifiers: Optional[list[str]]
        extends: Optional[Any]
        implements: Optional[list[Any]]
        body: Optional[list[Any]]
        fields: Optional[list[Any]]
        methods: Optional[list[Any]]
        constructors: Optional[list[Any]]

    class InterfaceDeclaration(ast.Node):
        name: str
        modifiers: Optional[list[str]]
        extends: Optional[list[Any]]
        body: Optional[list[Any]]

    class MethodDeclaration(ast.Node):
        name: str
        modifiers: Optional[list[str]]
        return_type: Optional[Any]
        parameters: Optional[list[Any]]
        body: Optional[list[Any]]
        throws: Optional[list[Any]]

    class FieldDeclaration(ast.Node):
        modifiers: Optional[list[str]]
        type: Any
        declarators: list[Any]

    class VariableDeclarator(ast.Node):
        name: str
        initializer: Optional[Any]

    class FormalParameter(ast.Node):
        name: str
        type: Any
        modifiers: Optional[list[str]]

    class ConstructorDeclaration(ast.Node):
        name: str
        modifiers: Optional[list[str]]
        parameters: Optional[list[Any]]
        body: Optional[list[Any]]

    class IfStatement(ast.Node):
        condition: Any
        then_statement: Any
        else_statement: Optional[Any]

    class ForStatement(ast.Node):
        control: Any
        body: Any

    class WhileStatement(ast.Node):
        condition: Any
        body: Any

    class DoStatement(ast.Node):
        condition: Any
        body: Any

    class SwitchStatement(ast.Node):
        expression: Any
        cases: list[Any]

    class TryStatement(ast.Node):
        block: Optional[list[Any]]
        catches: Optional[list[Any]]
        finally_block: Optional[list[Any]]
        resources: Optional[list[Any]]

    class CatchClause(ast.Node):
        parameter: Any
        block: Optional[list[Any]]

    class ReturnStatement(ast.Node):
        expression: Optional[Any]
        parent: Optional[ast.Node]

    class BreakStatement(ast.Node):
        label: Optional[str]

    class ContinueStatement(ast.Node):
        label: Optional[str]

    class ThrowStatement(ast.Node):
        expression: Any

    class SynchronizedStatement(ast.Node):
        lock: Any
        block: Optional[list[Any]]

    class BinaryOperation(ast.Node):
        operator: str
        operandl: Any
        operandr: Any

    class TernaryExpression(ast.Node):
        condition: Any
        if_true: Any
        if_false: Any

    class Assignment(ast.Node):
        expressionl: Any
        value: Any
        type: str

    class MemberReference(ast.Node):
        member: str
        qualifier: Optional[str]

    class MethodInvocation(ast.Node):
        member: str
        qualifier: Optional[str]
        arguments: Optional[list[Any]]

    class ClassCreator(ast.Node):
        type: Any
        arguments: Optional[list[Any]]

    class ArraySelector(ast.Node):
        index: Any

    class Literal(ast.Node):
        value: Any

    class LambdaExpression(ast.Node):
        parameters: Optional[list[Any]]
        body: Any

    class MethodReference(ast.Node):
        expression: Any
        method: Any

    class StatementExpression(ast.Node):
        expression: Any

    class Statement(ast.Node): ...

class parser:
    class JavaSyntaxError(Exception):
        position: Optional[Tuple[int, int]]
        description: str

class parse:
    @staticmethod
    def parse(code: str) -> tree.CompilationUnit: ...
