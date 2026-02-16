"""
Codegen Symbols Adapter

Direct imports from Codegen SDK core symbol classes - no reimplementation.
Provides fundamental building blocks for semantic code manipulation.

These are the CORE classes that enable:
- Symbol-aware operations (functions, classes, variables)
- Dependency tracking and usage analysis
- Type-aware transformations
- Advanced refactoring operations
"""

from codegen.sdk.core.symbol import Symbol as _Symbol
from codegen.sdk.core.function import Function as _Function
from codegen.sdk.core.class_definition import Class as _Class
from codegen.sdk.core.assignment import Assignment as _Assignment
from codegen.sdk.core.export import Export as _Export
from codegen.sdk.core.type_alias import TypeAlias as _TypeAlias
from codegen.sdk.core.interface import Interface as _Interface
from codegen.sdk.core.symbol_group import SymbolGroup as _SymbolGroup
from codegen.sdk.core.directory import Directory as _Directory
from codegen.sdk.core.file import File as _File, SourceFile as _SourceFile
from codegen.sdk.core.external_module import ExternalModule as _ExternalModule
from codegen.sdk.core.codeowner import CodeOwner as _CodeOwner
from codegen.sdk.core.import_resolution import (
    Import as _Import,
    ImportResolution as _ImportResolution,
    WildcardImport as _WildcardImport,
    ExternalImportResolver as _ExternalImportResolver
)

# Re-export with tier unification
# All symbol classes are now Community tier accessible

# Base Symbol Class
Symbol = _Symbol
"""
Base symbol class - Community tier (unified from Pro)

Represents any named entity in code (function, class, variable, etc.)
Tracks usages, dependencies, and provides semantic operations.
"""

# Function Symbol
Function = _Function
"""
Function symbol class - Community tier

Represents function definitions with:
- Parameters and return types
- Docstrings and decorators
- Call sites and dependencies
- Semantic operations (rename, move, delete)
"""

# Class Symbol
Class = _Class
"""
Class symbol class - Community tier

Represents class definitions with:
- Methods and attributes
- Inheritance relationships
- Decorators and type parameters
- Semantic operations (refactor, extract)
"""

# Assignment Symbol
Assignment = _Assignment
"""
Assignment symbol class - Community tier

Represents variable assignments with:
- Type information
- Value tracking
- Usage analysis
"""

# Export Symbol
Export = _Export
"""
Export symbol class - Community tier

Represents export statements with:
- Export type (named, default, wildcard)
- Exported symbols
- Re-export tracking
"""

# Type Alias
TypeAlias = _TypeAlias
"""
Type alias symbol class - Community tier

Represents type alias definitions with:
- Type parameters
- Type constraints
- Usage tracking
"""

# Interface
Interface = _Interface
"""
Interface symbol class - Community tier

Represents interface definitions (TypeScript) with:
- Method signatures
- Property definitions
- Inheritance relationships
"""

# Symbol Group
SymbolGroup = _SymbolGroup
"""
Symbol group class - Community tier

Represents collections of related symbols with:
- Batch operations
- Group-level analysis
- Collective transformations
"""

# Directory
Directory = _Directory
"""
Directory class - Community tier

Represents filesystem directories with:
- File listing
- Recursive operations
- Directory-level analysis
"""

# File Classes
File = _File
"""
File class - Community tier

Represents any file in the codebase with:
- File metadata
- Content operations
- Path operations
"""

SourceFile = _SourceFile
"""
Source file class - Community tier

Represents parseable source code files with:
- AST access
- Symbol extraction
- Semantic operations
"""

# External Module
ExternalModule = _ExternalModule
"""
External module class - Community tier

Represents external dependencies with:
- Package information
- Version tracking
- Import analysis
"""

# Code Owner
CodeOwner = _CodeOwner
"""
Code owner class - Community tier

Represents code ownership information with:
- Owner identification
- Ownership rules
- Responsibility tracking
"""

# Import Resolution
Import = _Import
"""
Import class - Community tier

Represents import statements with:
- Import resolution
- Dependency tracking
- Import optimization
"""

ImportResolution = _ImportResolution
"""
Import resolution class - Community tier

Handles import resolution logic with:
- Module resolution
- Path resolution
- Circular import detection
"""

WildcardImport = _WildcardImport
"""
Wildcard import class - Community tier

Represents wildcard imports (import *) with:
- Symbol expansion
- Namespace pollution detection
- Refactoring suggestions
"""

ExternalImportResolver = _ExternalImportResolver
"""
External import resolver class - Community tier

Resolves imports to external packages with:
- Package resolution
- Version compatibility
- Dependency analysis
"""

__all__ = [
    # Base
    'Symbol',
    
    # Symbols
    'Function',
    'Class',
    'Assignment',
    'Export',
    'TypeAlias',
    'Interface',
    'SymbolGroup',
    
    # Files & Directories
    'Directory',
    'File',
    'SourceFile',
    
    # External
    'ExternalModule',
    'CodeOwner',
    
    # Imports
    'Import',
    'ImportResolution',
    'WildcardImport',
    'ExternalImportResolver',
]

