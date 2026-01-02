#!/usr/bin/env python3
"""
Java Parsers Module - Comprehensive Java code analysis.

This module provides multiple Java parsing and analysis tools:

Core Parsers (AST-based):
- JavaParser (tree-sitter): Fast native parsing with detailed extraction
- JavaParser (javalang): Pure Python parsing

Static Analysis Tools:
- CheckstyleParser: Code style enforcement
- PMDParser: Common programming flaws
- SpotBugsParser: Bug pattern detection (FindBugs successor)
- ErrorProneParser: Google's compile-time analyzer
- InferParser: Facebook's null/resource leak detector

Security Analysis:
- FindSecBugsParser: Security vulnerability detection

Architecture & Metrics:
- JArchitectParser: Architecture and quality metrics
- SonarQubeParser: Quality platform integration

# [20251221_FEATURE] Phase 2 Enhancement TODOs - Prioritized by Impact

# High Priority (Core Infrastructure)
# [20251221_TODO] Add unified JavaAnalyzer that aggregates results from all parsers
# [20251221_TODO] Create unified issue severity mapping across all tools (BLOCKER/CRITICAL/MAJOR/MINOR)
# [20251221_TODO] Add result caching to avoid redundant analysis (file hash-based)
# [20251221_TODO] Implement async parallel execution for multi-tool analysis

# Medium Priority (New Tools & Features)
# [20251221_TODO] Add OWASP Dependency-Check parser for CVE/vulnerability scanning
# [20251221_TODO] Add Semgrep parser for custom pattern matching rules
# [20251221_TODO] Add JaCoCo parser for code coverage analysis
# [20251221_TODO] Add Pitest parser for mutation testing results
# [20251221_TODO] Add JavaDoc coverage analyzer
# [20251221_TODO] Add Gradle/Maven plugin output parsers for build tool integration

# Low Priority (Enhancements & Optimization)
# [20251221_TODO] Add incremental analysis support (only re-parse changed files)
# [20251221_TODO] Implement cross-parser conflict resolution (same issue detected by multiple tools)
# [20251221_TODO] Add result comparison/trending (track issues over multiple runs)
# [20251221_TODO] Implement performance profiling for each parser
# [20251221_TODO] Add custom rule support for PMD/SpotBugs
# [20251221_TODO] Support Java 21+ features (pattern matching, virtual threads)
"""

from .java_parser_treesitter import (JavaAnnotation, JavaClass, JavaEnum,
                                     JavaEnumConstant, JavaField,
                                     JavaInterface, JavaMethod, JavaModule,
                                     JavaModuleDirective, JavaParameter)
from .java_parser_treesitter import JavaParser as TreeSitterJavaParser
from .java_parser_treesitter import (JavaParseResult, JavaRecord,
                                     JavaRecordComponent,
                                     JavaStaticInitializer)
from .java_parsers_Checkstyle import CheckstyleParser, CheckstyleViolation
from .java_parsers_ErrorProne import ErrorProneIssue, ErrorProneParser
from .java_parsers_FindSecBugs import FindSecBugsParser, SecurityBug
from .java_parsers_Infer import InferIssue, InferParser
from .java_parsers_JArchitect import (DependencyIssue, JArchitectParser,
                                      JArchitectReport, QualityMetric)
from .java_parsers_javalang import (CodeMetrics, DesignPatternMatch,
                                    HalsteadMetrics)
from .java_parsers_javalang import JavaParser as JavalangParser
from .java_parsers_javalang import (MethodCallInfo, MethodMetrics,
                                    SecurityIssue, ThreadSafetyInfo,
                                    TryCatchPattern, TypeHierarchy)
from .java_parsers_PMD import PMDParser, PMDViolation
from .java_parsers_SonarQube import SonarIssue, SonarMetrics, SonarQubeParser
from .java_parsers_SpotBugs import SpotBug, SpotBugsParser

__all__ = [
    # Core parsers
    "TreeSitterJavaParser",
    "JavalangParser",
    # Tree-sitter dataclasses
    "JavaParseResult",
    "JavaClass",
    "JavaMethod",
    "JavaField",
    "JavaParameter",
    "JavaAnnotation",
    "JavaEnum",
    "JavaEnumConstant",
    "JavaInterface",
    # Java 14+ Records
    "JavaRecord",
    "JavaRecordComponent",
    # Java 9+ Modules
    "JavaModule",
    "JavaModuleDirective",
    # Static initializers
    "JavaStaticInitializer",
    # Javalang dataclasses
    "MethodCallInfo",
    "MethodMetrics",
    "HalsteadMetrics",
    "TypeHierarchy",
    "DesignPatternMatch",
    "TryCatchPattern",
    "ThreadSafetyInfo",
    "SecurityIssue",
    "CodeMetrics",
    # Static analysis
    "CheckstyleParser",
    "CheckstyleViolation",
    "PMDParser",
    "PMDViolation",
    "SpotBugsParser",
    "SpotBug",
    "ErrorProneParser",
    "ErrorProneIssue",
    "InferParser",
    "InferIssue",
    # Security
    "FindSecBugsParser",
    "SecurityBug",
    # Architecture
    "JArchitectParser",
    "JArchitectReport",
    "QualityMetric",
    "DependencyIssue",
    # Quality platform
    "SonarQubeParser",
    "SonarIssue",
    "SonarMetrics",
]
