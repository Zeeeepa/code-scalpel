# Intermediate Representation (IR) Module

**Purpose:** Language-agnostic code representation and normalization

## Overview

This module provides a unified intermediate representation (IR) for multiple programming languages, enabling polyglot analysis and transformation.

## Architecture

```
Source Code (Python/Java/JS/TS)
    ↓
Tree-sitter Parse
    ↓
Language-Specific Normalizer
    ↓
Unified IR (nodes.py)
    ↓
Semantic Analysis (semantics.py)
    ↓
Analysis Tools (PDG, Security, Symbolic Execution)
```

## Key Components

### nodes.py (20,775 LOC)
Unified IR node definitions:
- `IRNode` - Base class for all IR nodes
- `FunctionNode` - Function/method definitions
- `ClassNode` - Class/interface definitions
- `VariableNode` - Variable declarations
- `ExpressionNode` - Expressions (binary ops, calls, etc.)
- `StatementNode` - Statements (if, while, return, etc.)
- `TypeNode` - Type annotations

**Key Features:**
- Language-agnostic representation
- Preserves source location information
- Maintains parent-child relationships
- Supports annotations and metadata

### operators.py (3,255 LOC)
Operator definitions and semantics:
- `BinaryOp` - Binary operators (+, -, *, /, ==, !=, etc.)
- `UnaryOp` - Unary operators (-, !, ~, etc.)
- `LogicalOp` - Logical operators (and, or, not)
- `ComparisonOp` - Comparison operators (<, >, <=, >=, ==, !=)

### semantics.py (27,175 LOC)
Semantic analysis on IR:
- `SemanticAnalyzer` - Performs semantic checks
- Type inference
- Name resolution
- Scope analysis
- Dead code detection
- Constant folding

**Key Features:**
- Cross-language type inference
- Control flow analysis on IR
- Data flow analysis on IR
- Detects semantic errors (undefined variables, type mismatches)

## Normalizers

The `normalizers/` subdirectory contains language-specific normalizers that convert language ASTs to unified IR.

### python_normalizer.py (37,869 LOC)
Python AST → IR normalization:
- Handles Python-specific constructs (list comprehensions, decorators, with statements)
- Maps Python types to IR types
- Preserves Python semantics in IR

### java_normalizer.py (38,736 LOC)
Java AST → IR normalization:
- Handles Java-specific constructs (interfaces, generics, annotations)
- Maps Java types to IR types
- Preserves Java semantics (static vs instance, access modifiers)

### javascript_normalizer.py (61,362 LOC)
JavaScript/JSX AST → IR normalization:
- Handles JS-specific constructs (arrow functions, destructuring, async/await)
- JSX/React component normalization
- Prototype chain representation

### typescript_normalizer.py (13,939 LOC)
TypeScript AST → IR normalization:
- Handles TypeScript-specific constructs (interfaces, enums, generics)
- Type annotation preservation
- Extends JavaScript normalizer

### base.py (3,125 LOC)
Base normalizer interface:
- `Normalizer` - Abstract base class for all normalizers
- Common normalization utilities
- Visitor pattern implementation

### tree_sitter_visitor.py (13,122 LOC)
Tree-sitter AST traversal:
- `TreeSitterVisitor` - Generic visitor for tree-sitter ASTs
- Node type dispatching
- Recursive traversal with context

## Usage

```python
from code_scalpel.ir import IRNode, FunctionNode
from code_scalpel.ir.normalizers import PythonNormalizer, JavaNormalizer

# Normalize Python code
python_normalizer = PythonNormalizer()
python_ir = python_normalizer.normalize(python_ast)

# Normalize Java code
java_normalizer = JavaNormalizer()
java_ir = java_normalizer.normalize(java_ast)

# Both produce same IR structure
assert isinstance(python_ir, FunctionNode)
assert isinstance(java_ir, FunctionNode)

# Perform semantic analysis
from code_scalpel.ir.semantics import SemanticAnalyzer
analyzer = SemanticAnalyzer()
errors = analyzer.analyze(python_ir)
```

## Integration

Used by:
- `polyglot/` - Multi-language parsing
- `pdg_tools/` - PDG construction from IR
- `symbolic_execution_tools/` - Symbolic execution on IR
- `security/` - Security analysis on IR

## Benefits of IR

1. **Unified Analysis:** Write analysis once, run on multiple languages
2. **Simplified Tools:** PDG/symbolic execution don't need language-specific logic
3. **Cross-Language Analysis:** Analyze Python calling Java, JS calling TypeScript
4. **Maintenance:** Language changes don't affect analysis tools

## v3.0.5 Status

- IR structure: Stable, 100% coverage
- Python normalizer: Stable, 100% coverage
- Java normalizer: Stable, 95% coverage
- JavaScript normalizer: Stable, 90% coverage
- TypeScript normalizer: Stable, 90% coverage
- Semantic analysis: Beta, 85% coverage
