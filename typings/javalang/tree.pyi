# Type stubs for javalang library
# This file provides type hints for the javalang library which lacks native stubs
from typing import Any, Iterator, Optional, Tuple, List

class Node:
    position: Optional[Tuple[int, int]]
    parent: Optional["Node"]
    def __init__(self) -> None: ...

class CompilationUnit(Node):
    package: Any
    imports: List[Any]
    types: List[Any]
    def filter(self, node_type: type) -> Iterator[Tuple[Tuple[Any, ...], Any]]: ...

class Identifier(Node):
    value: str

class ClassDeclaration(Node):
    name: str
    modifiers: Optional[List[str]]
    extends: Optional[Any]
    implements: Optional[List[Any]]
    body: Optional[List[Any]]
    fields: Optional[List["FieldDeclaration"]]
    methods: Optional[List["MethodDeclaration"]]
    constructors: Optional[List["ConstructorDeclaration"]]

class InterfaceDeclaration(Node):
    name: str
    modifiers: Optional[List[str]]
    extends: Optional[List[Any]]
    body: Optional[List[Any]]

class MethodDeclaration(Node):
    name: str
    modifiers: Optional[List[str]]
    return_type: Optional[Any]
    parameters: Optional[List["FormalParameter"]]
    body: Optional[List[Any]]
    throws: Optional[List[Any]]

class FieldDeclaration(Node):
    modifiers: Optional[List[str]]
    type: Any
    declarators: List["VariableDeclarator"]

class VariableDeclarator(Node):
    name: str
    initializer: Optional[Any]

class FormalParameter(Node):
    name: str
    type: Any
    modifiers: Optional[List[str]]

class ConstructorDeclaration(Node):
    name: str
    modifiers: Optional[List[str]]
    parameters: Optional[List["FormalParameter"]]
    body: Optional[List[Any]]

class IfStatement(Node):
    condition: Any
    then_statement: Any
    else_statement: Optional[Any]

class ForStatement(Node):
    control: Any
    body: Any

class WhileStatement(Node):
    condition: Any
    body: Any

class DoStatement(Node):
    condition: Any
    body: Any

class SwitchStatement(Node):
    expression: Any
    cases: List[Any]

class TryStatement(Node):
    block: Optional[List[Any]]
    catches: Optional[List["CatchClause"]]
    finally_block: Optional[List[Any]]
    resources: Optional[List[Any]]

class CatchClause(Node):
    parameter: Any
    block: Optional[List[Any]]

class ReturnStatement(Node):
    expression: Optional[Any]

class BreakStatement(Node):
    label: Optional[str]

class ContinueStatement(Node):
    label: Optional[str]

class ThrowStatement(Node):
    expression: Any

class SynchronizedStatement(Node):
    lock: Any
    block: Optional[List[Any]]

class BinaryOperation(Node):
    operator: str
    operandl: Any
    operandr: Any

class TernaryExpression(Node):
    condition: Any
    if_true: Any
    if_false: Any

class Assignment(Node):
    expressionl: Any
    value: Any
    type: str

class MemberReference(Node):
    member: str
    qualifier: Optional[str]

class MethodInvocation(Node):
    member: str
    qualifier: Optional[str]
    arguments: Optional[List[Any]]

class ClassCreator(Node):
    type: Any
    arguments: Optional[List[Any]]

class ArraySelector(Node):
    index: Any

class Literal(Node):
    value: Any

class LambdaExpression(Node):
    parameters: Optional[List[Any]]
    body: Any

class MethodReference(Node):
    expression: Any
    method: Any

class StatementExpression(Node):
    expression: Any

class Statement(Node): ...
