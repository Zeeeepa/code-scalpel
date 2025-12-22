#!/usr/bin/env python3
"""
JavaScript Parsers Module - Comprehensive JavaScript/TypeScript code analysis.

This module provides multiple JavaScript parsing and analysis tools:

Parsers:
    JavaScriptParser (esprima)  - Pure Python AST parsing with detailed extraction
    TreeSitterJSParser          - Fast native incremental parsing
    TypeScriptParser            - TypeScript type extraction and analysis
    FlowParser                  - Facebook Flow type checking integration
    BabelParser                 - Modern ECMAScript feature detection

Linting & Style:
    ESLintParser                - Pluggable linting with directive parsing
    JSHintParser                - Error detection and code quality
    StandardJSParser            - Zero-config JavaScript style guide
    PrettierFormatter           - Code formatting verification

Code Quality:
    CodeQualityAnalyzer         - Comprehensive code smell detection

Features:
    Core Analysis:
        - Cognitive & cyclomatic complexity calculation
        - Halstead complexity metrics (vocabulary, volume, difficulty, effort)
        - Function call graph building
        - Import/export dependency tracking
        - CommonJS vs ES6 module detection
        - Maintainability index calculation

    Security Analysis:
        - XSS vulnerability detection (innerHTML, document.write, eval)
        - Hardcoded secrets detection (API keys, passwords)
        - eval/Function constructor detection
        - setTimeout/setInterval string argument detection

    Code Quality Checks:
        - Callback hell / deep nesting detection
        - Magic number/string detection
        - Long function detection (configurable threshold)
        - Too many parameters detection
        - Duplicate code block detection
        - Empty catch block detection
        - Console.log/debugger statement detection
        - TODO/FIXME/HACK comment extraction
        - Nested ternary detection
        - Complex boolean condition detection
        - Promise anti-pattern detection

    Framework Detection:
        - React (components, hooks, JSX)
        - Vue (Options API, Composition API)
        - Angular (components, services, decorators)
        - Express.js / Next.js / NestJS
        - jQuery, Redux, Lodash

    ESLint Integration:
        - Rule documentation URL generation
        - Inline directive parsing (eslint-disable/enable)
        - Suppression report generation

Phase 2 Enhancement TODOs (Module Level):

High Priority:
[20251221_TODO] Implement JavaScriptAnalyzer aggregation interface (multi-parser orchestration)
[20251221_TODO] Add severity/confidence mapping across all tools
[20251221_TODO] Implement parser result caching with content-hash keys
[20251221_TODO] Add async execution support for parallel analysis

Medium Priority:
[20251221_TODO] Implement Webpack/bundle analyzer integration
[20251221_TODO] Add JSDoc coverage analysis tool
[20251221_TODO] Create test pattern detection parser
[20251221_TODO] Implement package.json analyzer (dependencies, scripts)
[20251221_TODO] Add npm audit integration for vulnerability scanning
[20251221_TODO] Create Webpack bundler analyzer parser

Low Priority:
[20251221_TODO] Implement closure and scope chain analysis
[20251221_TODO] Add incremental analysis across all parsers
[20251221_TODO] Implement trending and historical analysis
[20251221_TODO] Add custom rule plugin system
[20251221_TODO] Support configuration conflict resolution

Future Enhancements:
    - Closure and scope chain analysis
    - Prototype pollution detection
    - SQL/command injection detection
    - JSDoc coverage analysis
    - Test file pattern detection
    - Webpack/bundle analysis
    - Unified JavaScriptAnalyzer aggregator
"""

from .javascript_parsers_esprima import (
    JavaScriptParser,
    # Dataclasses for analysis
    FunctionInfo,
    FunctionCallInfo,
    HalsteadMetrics,
    ScopeInfo,
    SecurityIssue,
    SecuritySeverity,
    DesignPatternType,
    DesignPatternMatch,
    ImportInfo,
    ExportInfo,
    CodeMetrics,
)
from .javascript_parsers_eslint import (
    ESLintParser,
    ESLintViolation,
    ESLintFileResult,
    ESLintConfig,
    ESLintSeverity,
)
from .javascript_parsers_jshint import (
    JSHintParser,
    JSHintError,
    JSHintFileResult,
    JSHintConfig,
    JSHintSeverity,
)
from .javascript_parsers_prettier import (
    PrettierFormatter,
    PrettierConfig,
    FormatDiff,
    FormatResult,
    PrettierParser as PrettierParserType,
    EndOfLine,
    QuoteType,
    TrailingComma,
    ProseWrap,
    HTMLWhitespaceSensitivity,
)
from .javascript_parsers_standard import (
    StandardJSParser,
    StandardViolation,
    StandardFileResult,
    StandardConfig,
    StandardSeverity,
)
from .javascript_parsers_treesitter import (
    TreeSitterJSParser,
    TreeSitterNode,
    TreeSitterParseResult,
    JSLanguageVariant,
    JSSymbol,
    JSXComponent,
    ImportStatement,
    ExportStatement,
    SyntaxError as TreeSitterSyntaxError,
)
from .javascript_parsers_typescript import (
    TypeScriptParser,
    TypeScriptAnalysis,
    TypeKind,
    TypeAnnotation,
    TypeParameter,
    InterfaceDeclaration,
    TypeAliasDeclaration,
    PropertySignature,
    MethodSignature,
    IndexSignature,
    ParameterDeclaration,
    EnumDeclaration,
    EnumMember,
    DecoratorUsage,
    DecoratorKind,
    NamespaceDeclaration,
    TypeGuard,
)
from .javascript_parsers_babel import (
    BabelParser,
    BabelAnalysis,
    BabelConfig,
    BabelPlugin,
    BabelPreset,
    ECMAScriptVersion,
    ProposalStage,
    SyntaxFeature,
    TransformationResult,
    JSXElement,
    ModernJSSyntax,
)
from .javascript_parsers_flow import (
    FlowParser,
    FlowAnalysis,
    FlowConfig,
    FlowError,
    FlowCoverage,
    FlowSeverity,
    FlowTypeKind,
    FlowTypeAnnotation,
    FlowTypeParameter,
    FlowTypeAlias,
    FlowInterface,
    Variance,
)
from .javascript_parsers_code_quality import (
    CodeQualityAnalyzer,
    CodeQualityResult,
    CodeSmell,
    CodeSmellType,
    CodeSmellSeverity,
    TodoComment,
    DuplicateCodeBlock,
    FrameworkDetection,
    FrameworkType,
    ModuleAnalysis,
    ModuleType,
)
from .javascript_parsers_eslint import (
    ESLintDirective,
    ESLintDirectiveType,
)

__all__ = [
    # Core parser (esprima)
    "JavaScriptParser",
    # Core analysis dataclasses
    "FunctionInfo",
    "FunctionCallInfo",
    "HalsteadMetrics",
    "ScopeInfo",
    "SecurityIssue",
    "SecuritySeverity",
    "DesignPatternType",
    "DesignPatternMatch",
    "ImportInfo",
    "ExportInfo",
    "CodeMetrics",
    # ESLint
    "ESLintParser",
    "ESLintViolation",
    "ESLintFileResult",
    "ESLintConfig",
    "ESLintSeverity",
    "ESLintDirective",
    "ESLintDirectiveType",
    # JSHint
    "JSHintParser",
    "JSHintError",
    "JSHintFileResult",
    "JSHintConfig",
    "JSHintSeverity",
    # Prettier
    "PrettierFormatter",
    "PrettierConfig",
    "FormatDiff",
    "FormatResult",
    "PrettierParserType",
    "EndOfLine",
    "QuoteType",
    "TrailingComma",
    "ProseWrap",
    "HTMLWhitespaceSensitivity",
    # StandardJS
    "StandardJSParser",
    "StandardViolation",
    "StandardFileResult",
    "StandardConfig",
    "StandardSeverity",
    # Tree-sitter
    "TreeSitterJSParser",
    "TreeSitterNode",
    "TreeSitterParseResult",
    "JSLanguageVariant",
    "JSSymbol",
    "JSXComponent",
    "ImportStatement",
    "ExportStatement",
    "TreeSitterSyntaxError",
    # TypeScript
    "TypeScriptParser",
    "TypeScriptAnalysis",
    "TypeKind",
    "TypeAnnotation",
    "TypeParameter",
    "InterfaceDeclaration",
    "TypeAliasDeclaration",
    "PropertySignature",
    "MethodSignature",
    "IndexSignature",
    "ParameterDeclaration",
    "EnumDeclaration",
    "EnumMember",
    "DecoratorUsage",
    "DecoratorKind",
    "NamespaceDeclaration",
    "TypeGuard",
    # Babel
    "BabelParser",
    "BabelAnalysis",
    "BabelConfig",
    "BabelPlugin",
    "BabelPreset",
    "ECMAScriptVersion",
    "ProposalStage",
    "SyntaxFeature",
    "TransformationResult",
    "JSXElement",
    "ModernJSSyntax",
    # Flow
    "FlowParser",
    "FlowAnalysis",
    "FlowConfig",
    "FlowError",
    "FlowCoverage",
    "FlowSeverity",
    "FlowTypeKind",
    "FlowTypeAnnotation",
    "FlowTypeParameter",
    "FlowTypeAlias",
    "FlowInterface",
    "Variance",
    # Code Quality
    "CodeQualityAnalyzer",
    "CodeQualityResult",
    "CodeSmell",
    "CodeSmellType",
    "CodeSmellSeverity",
    "TodoComment",
    "DuplicateCodeBlock",
    "FrameworkDetection",
    "FrameworkType",
    "ModuleAnalysis",
    "ModuleType",
]
