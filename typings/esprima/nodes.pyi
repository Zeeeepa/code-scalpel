"""Type stubs for esprima.nodes - AST node definitions."""

from typing import Dict, List, Optional, Union

class SourceLocation:
    """Source location information."""

    start: Position
    end: Position
    source: Optional[str]

class Position:
    """Position in source code."""

    line: int
    column: int

class Node:
    """Base class for all AST nodes."""

    type: str
    loc: Optional[SourceLocation]
    range: Optional[List[int]]
    parent: Optional["Node"]

    def __init__(self) -> None: ...

class Program(Node):
    """Root node of the AST."""

    body: List[Union["Statement", "ModuleDeclaration"]]
    sourceType: str  # "script" or "module"

class Statement(Node):
    """Base class for statements."""

    pass

class Expression(Node):
    """Base class for expressions."""

    pass

class Pattern(Node):
    """Base class for patterns (destructuring)."""

    pass

class Declaration(Statement):
    """Base class for declarations."""

    pass

class ModuleDeclaration(Node):
    """Base class for module declarations."""

    pass

# Statements
class ExpressionStatement(Statement):
    expression: Expression

class BlockStatement(Statement):
    body: List[Statement]

class EmptyStatement(Statement):
    pass

class DebuggerStatement(Statement):
    pass

class WithStatement(Statement):
    object: Expression
    body: Statement

class ReturnStatement(Statement):
    argument: Optional[Expression]

class LabeledStatement(Statement):
    label: "Identifier"
    body: Statement

class BreakStatement(Statement):
    label: Optional["Identifier"]

class ContinueStatement(Statement):
    label: Optional["Identifier"]

class IfStatement(Statement):
    test: Expression
    consequent: Statement
    alternate: Optional[Statement]

class SwitchStatement(Statement):
    discriminant: Expression
    cases: List["SwitchCase"]

class SwitchCase(Node):
    test: Optional[Expression]
    consequent: List[Statement]

class ThrowStatement(Statement):
    argument: Expression

class TryStatement(Statement):
    block: BlockStatement
    handler: Optional["CatchClause"]
    finalizer: Optional[BlockStatement]

class CatchClause(Node):
    param: Optional[Pattern]
    body: BlockStatement

class WhileStatement(Statement):
    test: Expression
    body: Statement

class DoWhileStatement(Statement):
    body: Statement
    test: Expression

class ForStatement(Statement):
    init: Optional[Union["VariableDeclaration", Expression]]
    test: Optional[Expression]
    update: Optional[Expression]
    body: Statement

class ForInStatement(Statement):
    left: Union["VariableDeclaration", Pattern]
    right: Expression
    body: Statement

class ForOfStatement(Statement):
    left: Union["VariableDeclaration", Pattern]
    right: Expression
    body: Statement
    await_: bool

# Declarations
class FunctionDeclaration(Declaration):
    id: Optional["Identifier"]
    params: List[Pattern]
    body: BlockStatement
    generator: bool
    async_: bool
    expression: bool

class VariableDeclaration(Declaration):
    declarations: List["VariableDeclarator"]
    kind: str  # "var", "let", "const"

class VariableDeclarator(Node):
    id: Pattern
    init: Optional[Expression]

class ClassDeclaration(Declaration):
    id: Optional["Identifier"]
    superClass: Optional[Expression]
    body: "ClassBody"

class ClassBody(Node):
    body: List["MethodDefinition"]

class MethodDefinition(Node):
    key: Expression
    value: "FunctionExpression"
    kind: str  # "constructor", "method", "get", "set"
    computed: bool
    static: bool

# Expressions
class Identifier(Expression, Pattern):
    name: str

class Literal(Expression):
    value: Union[str, bool, int, float, None]
    raw: str
    regex: Optional[Dict[str, str]]

class ThisExpression(Expression):
    pass

class ArrayExpression(Expression):
    elements: List[Optional[Expression]]

class ObjectExpression(Expression):
    properties: List["Property"]

class Property(Node):
    key: Expression
    value: Expression
    kind: str  # "init", "get", "set"
    method: bool
    shorthand: bool
    computed: bool

class FunctionExpression(Expression):
    id: Optional[Identifier]
    params: List[Pattern]
    body: BlockStatement
    generator: bool
    async_: bool
    expression: bool

class ArrowFunctionExpression(Expression):
    id: Optional[Identifier]
    params: List[Pattern]
    body: Union[BlockStatement, Expression]
    generator: bool
    async_: bool
    expression: bool

class ClassExpression(Expression):
    id: Optional[Identifier]
    superClass: Optional[Expression]
    body: ClassBody

class TaggedTemplateExpression(Expression):
    tag: Expression
    quasi: "TemplateLiteral"

class TemplateLiteral(Expression):
    quasis: List["TemplateElement"]
    expressions: List[Expression]

class TemplateElement(Node):
    value: Dict[str, str]
    tail: bool

class MemberExpression(Expression, Pattern):
    object: Expression
    property: Expression
    computed: bool
    optional: bool

class Super(Node):
    pass

class MetaProperty(Expression):
    meta: Identifier
    property: Identifier

class CallExpression(Expression):
    callee: Union[Expression, Super]
    arguments: List[Expression]
    optional: bool

class NewExpression(Expression):
    callee: Expression
    arguments: List[Expression]

class SpreadElement(Node):
    argument: Expression

class UpdateExpression(Expression):
    operator: str  # "++" or "--"
    argument: Expression
    prefix: bool

class AwaitExpression(Expression):
    argument: Expression

class UnaryExpression(Expression):
    operator: str
    prefix: bool
    argument: Expression

class BinaryExpression(Expression):
    operator: str
    left: Expression
    right: Expression

class LogicalExpression(Expression):
    operator: str  # "||", "&&", "??"
    left: Expression
    right: Expression

class ConditionalExpression(Expression):
    test: Expression
    consequent: Expression
    alternate: Expression

class YieldExpression(Expression):
    argument: Optional[Expression]
    delegate: bool

class AssignmentExpression(Expression):
    operator: str
    left: Pattern
    right: Expression

class SequenceExpression(Expression):
    expressions: List[Expression]

class AssignmentPattern(Pattern):
    left: Pattern
    right: Expression

class ArrayPattern(Pattern):
    elements: List[Optional[Pattern]]

class ObjectPattern(Pattern):
    properties: List["AssignmentProperty"]

class AssignmentProperty(Node):
    key: Expression
    value: Pattern
    computed: bool
    shorthand: bool

class RestElement(Pattern):
    argument: Pattern

# Module declarations
class ImportDeclaration(ModuleDeclaration):
    specifiers: List[
        Union["ImportSpecifier", "ImportDefaultSpecifier", "ImportNamespaceSpecifier"]
    ]
    source: Literal

class ImportSpecifier(Node):
    imported: Identifier
    local: Identifier

class ImportDefaultSpecifier(Node):
    local: Identifier

class ImportNamespaceSpecifier(Node):
    local: Identifier

class ExportAllDeclaration(ModuleDeclaration):
    source: Literal
    exported: Optional[Identifier]

class ExportDefaultDeclaration(ModuleDeclaration):
    declaration: Union[Declaration, Expression]

class ExportNamedDeclaration(ModuleDeclaration):
    declaration: Optional[Declaration]
    specifiers: List["ExportSpecifier"]
    source: Optional[Literal]

class ExportSpecifier(Node):
    exported: Identifier
    local: Identifier
