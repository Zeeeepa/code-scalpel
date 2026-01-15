#!/usr/bin/env python3
# TODO [FEATURE/HIGH] Add unified JavaAnalyzer that aggregates results from all parsers
# TODO [FEATURE/HIGH] Create unified issue severity mapping across all tools (BLOCKER/CRITICAL/MAJOR/MINOR)
# TODO [FEATURE/HIGH] Add result caching to avoid redundant analysis (file hash-based)
# TODO [FEATURE/HIGH] Implement async parallel execution for multi-tool analysis

# TODO [FEATURE/MEDIUM] Add OWASP Dependency-Check parser for CVE/vulnerability scanning
# TODO [FEATURE/MEDIUM] Add Semgrep parser for custom pattern matching rules
# TODO [FEATURE/MEDIUM] Add JaCoCo parser for code coverage analysis
# TODO [FEATURE/MEDIUM] Add Pitest parser for mutation testing results
# TODO [FEATURE/MEDIUM] Add JavaDoc coverage analyzer
# TODO [FEATURE/MEDIUM] Add Gradle/Maven plugin output parsers for build tool integration

# TODO [FEATURE/LOW] Add incremental analysis support (only re-parse changed files)
# TODO [FEATURE/LOW] Implement cross-parser conflict resolution (same issue detected by multiple tools)
# TODO [FEATURE/LOW] Add result comparison/trending (track issues over multiple runs)
# TODO [FEATURE/LOW] Implement performance profiling for each parser
# TODO [FEATURE/LOW] Add custom rule support for PMD/SpotBugs
# TODO [FEATURE/LOW] Support Java 21+ features (pattern matching, virtual threads)

from .java_parser_treesitter import (
    JavaAnnotation,
    JavaClass,
    JavaEnum,
    JavaEnumConstant,
    JavaField,
    JavaInterface,
    JavaMethod,
    JavaModule,
    JavaModuleDirective,
    JavaParameter,
)
from .java_parser_treesitter import JavaParser as TreeSitterJavaParser
from .java_parser_treesitter import (
    JavaParseResult,
    JavaRecord,
    JavaRecordComponent,
    JavaStaticInitializer,
)
from .java_parsers_Checkstyle import CheckstyleParser, CheckstyleViolation
from .java_parsers_ErrorProne import ErrorProneIssue, ErrorProneParser
from .java_parsers_FindSecBugs import FindSecBugsParser, SecurityBug
from .java_parsers_Infer import InferIssue, InferParser
from .java_parsers_JArchitect import (
    DependencyIssue,
    JArchitectParser,
    JArchitectReport,
    QualityMetric,
)
from .java_parsers_javalang import (
    CodeMetrics,
    DesignPatternMatch,
    HalsteadMetrics,
)
from .java_parsers_javalang import JavaParser as JavalangParser
from .java_parsers_javalang import (
    MethodCallInfo,
    MethodMetrics,
    SecurityIssue,
    ThreadSafetyInfo,
    TryCatchPattern,
    TypeHierarchy,
)
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
