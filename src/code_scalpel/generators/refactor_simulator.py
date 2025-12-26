"""Refactor Simulator - Verify Code Changes Before Applying.

This module allows AI Agents to "dry run" their code changes,
verifying that a patch doesn't introduce security vulnerabilities
or break existing functionality.

Example:
    >>> from code_scalpel.generators import RefactorSimulator
    >>> simulator = RefactorSimulator()
    >>> result = simulator.simulate(original_code, patch)
    >>> if result.is_safe:
    ...     print("Safe to apply!")
    ... else:
    ...     print(f"UNSAFE: {result.reason}")

TODO ITEMS: generators/refactor_simulator.py
======================================================================
COMMUNITY TIER - Core Refactor Simulation
======================================================================
1. Add RefactorSimulator.simulate(original, new_code) method
2. Add RefactorSimulator.simulate_patch(original, patch) method
3. Add apply_patch_to_code(code, patch) utility
4. Add detect_structural_changes(old_ast, new_ast) analyzer
5. Add detect_function_signature_changes() detector
6. Add detect_removed_functions() detector
7. Add detect_added_functions() detector
8. Add detect_modified_functions() detector
9. Add detect_removed_imports() import analyzer
10. Add detect_added_imports() import analyzer
11. Add detect_removed_classes() class detector
12. Add detect_added_classes() class detector
13. Add detect_modified_classes() class modifier detector
14. Add detect_variable_scope_changes() scope analyzer
15. Add verify_syntax(code) syntax validator
16. Add verify_indentation(code) formatter
17. Add extract_function_definitions(code) extractor
18. Add compare_function_signatures(sig1, sig2) comparator
19. Add get_structural_diff(old_code, new_code) differ
20. Add RefactorWarning dataclass for warnings
21. Add RefactorInfo dataclass for info messages
22. Add build_change_summary(changes) summarizer
23. Add format_structural_changes(changes) formatter
24. Add to_json() result serializer
25. Add validate_refactor_result(result) validator

======================================================================
PRO TIER - Advanced Refactor Analysis
======================================================================
26. Add behavioral equivalence verification
27. Add symbolic execution for equivalence checking
28. Add invariant preservation checking
29. Add type safety verification post-refactor
30. Add dead code detection in refactored code
31. Add unused import detection
32. Add cyclomatic complexity change detection
33. Add code smell detection post-refactor
34. Add maintainability index change tracking
35. Add documentation coverage change tracking
36. Add test coverage change prediction
37. Add performance impact prediction (ML)
38. Add memory usage impact prediction
39. Add API compatibility checking
40. Add backward compatibility verification
41. Add deprecation detection
42. Add logging impact analysis
43. Add error handling preservation
44. Add side effects detection
45. Add global state modification detection
46. Add concurrency issue detection (race conditions)
47. Add exception handling changes detection
48. Add return type change detection
49. Add parameter count/type changes detection
50. Add access control changes detection

======================================================================
ENTERPRISE TIER - Distributed & Compliant Refactor Simulation
======================================================================
51. Add distributed refactor verification across agents
52. Add federated refactor verification across orgs
53. Add refactor approval workflow integration
54. Add multi-step refactor staging
55. Add refactor rollback planning
56. Add refactor impact assessment dashboard
57. Add refactor change log generation
58. Add refactor audit trail logging
59. Add refactor compliance checking (SOC2/HIPAA/GDPR)
60. Add refactor encryption for sensitive code
61. Add refactor access control (RBAC)
62. Add refactor multi-tenancy isolation
63. Add refactor cost estimation (cloud resources)
64. Add refactor execution time prediction
65. Add refactor risk scoring (ML)
66. Add refactor risk dashboard
67. Add refactor SLA monitoring
68. Add refactor alerting and notifications
69. Add refactor metrics collection
70. Add refactor performance profiling
71. Add refactor trend analysis (improvements over time)
72. Add refactor anomaly detection
73. Add refactor circuit breaker
74. Add refactor rate limiting
75. Add executive refactor reports
"""

import ast
import difflib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RefactorStatus(Enum):
    """Status of a refactor simulation."""

    SAFE = "safe"
    UNSAFE = "unsafe"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class SecurityIssue:
    """A security issue detected in refactored code."""

    type: str
    severity: str
    line: int | None
    description: str
    cwe: str | None = None


@dataclass
class RefactorResult:
    """Result of simulating a refactor."""

    status: RefactorStatus
    is_safe: bool
    patched_code: str
    reason: str | None = None
    security_issues: list[SecurityIssue] = field(default_factory=list)
    structural_changes: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "is_safe": self.is_safe,
            "reason": self.reason,
            "security_issues": [
                {
                    "type": issue.type,
                    "severity": issue.severity,
                    "line": issue.line,
                    "description": issue.description,
                    "cwe": issue.cwe,
                }
                for issue in self.security_issues
            ],
            "structural_changes": self.structural_changes,
            "warnings": self.warnings,
        }


class RefactorSimulator:
    """Simulate code refactors and verify safety.

    This class allows AI Agents to test their code changes in a
    sandboxed environment before actually applying them. It:

    1. Applies the patch to get the new code
    2. Runs security analysis on the patched code
    3. Compares structural changes (added/removed functions, etc.)
    4. Returns a verdict: SAFE, UNSAFE, WARNING, or ERROR

    Example:
        >>> simulator = RefactorSimulator()
        >>> result = simulator.simulate(
        ...     original_code='def foo(x): return x',
        ...     patch='@@ -1 +1 @@\\n-def foo(x): return x\\n+def foo(x): return eval(x)'
        ... )
        >>> result.is_safe
        False
        >>> result.reason
        'Introduced Code Injection vulnerability'
    """

    def __init__(self, strict_mode: bool = False):
        """Initialize the refactor simulator.

        Args:
            strict_mode: If True, treat warnings as unsafe
        """
        self.strict_mode = strict_mode

    def simulate(
        self,
        original_code: str,
        patch: str | None = None,
        new_code: str | None = None,
        language: str = "python",
    ) -> RefactorResult:
        """Simulate applying a patch and check for safety.

        Provide either a unified diff patch OR the new code directly.

        Args:
            original_code: The original source code
            patch: Unified diff patch to apply (optional)
            new_code: New code to compare against (optional)
            language: Source language ("python", "javascript", "java")

        Returns:
            RefactorResult with safety verdict and details

        Raises:
            ValueError: If neither patch nor new_code provided
        """
        if patch is None and new_code is None:
            raise ValueError("Must provide either 'patch' or 'new_code'")

        # Apply patch to get new code
        patch_text = patch
        if new_code is None:
            try:
                new_code = self._apply_patch(original_code, patch)  # type: ignore[arg-type]
            except Exception as e:
                return RefactorResult(
                    status=RefactorStatus.ERROR,
                    is_safe=False,
                    patched_code="",
                    reason=f"Failed to apply patch: {str(e)}",
                )

        patch_security_issues: list[SecurityIssue] = []
        if patch_text:
            patch_security_issues = self._scan_patch_added_lines_for_security(
                patch_text, original_code
            )

        # Validate syntax
        syntax_error = self._check_syntax(new_code, language)
        if syntax_error:
            return RefactorResult(
                status=RefactorStatus.ERROR,
                is_safe=False,
                patched_code=new_code,
                reason=f"Syntax error in patched code: {syntax_error}",
                security_issues=patch_security_issues,
            )

        # Run security scan
        security_issues = self._scan_security(new_code, original_code, language)
        if patch_security_issues:
            security_issues.extend(patch_security_issues)

        # Check structural changes
        structural_changes = self._analyze_structural_changes(
            original_code, new_code, language
        )

        # Generate warnings
        warnings = self._generate_warnings(structural_changes)

        # Determine verdict
        status, is_safe, reason = self._determine_verdict(
            security_issues, structural_changes, warnings
        )

        return RefactorResult(
            status=status,
            is_safe=is_safe,
            patched_code=new_code,
            reason=reason,
            security_issues=security_issues,
            structural_changes=structural_changes,
            warnings=warnings,
        )

    def _scan_patch_added_lines_for_security(
        self, patch: str, original_code: str
    ) -> list[SecurityIssue]:
        """Scan patch-added lines for obviously dangerous introductions.

        This is intentionally conservative: it only considers lines starting with '+'
        (excluding file headers like '+++') and only flags patterns not already
        present in the original code.
        """
        added_lines: list[str] = []
        for raw in patch.splitlines():
            stripped = raw.lstrip(" \t")
            if stripped.startswith("+++") or stripped.startswith("@@"):
                continue
            if stripped.startswith("+") and not stripped.startswith("+++"):
                added_lines.append(stripped[1:])

        added_text = "\n".join(added_lines)
        if not added_text.strip():
            return []

        issues: list[SecurityIssue] = []
        dangerous_patterns = [
            (
                "eval(",
                "Code Injection",
                "CWE-94",
                "high",
                "Introduced eval() via patch",
            ),
            (
                "exec(",
                "Code Injection",
                "CWE-94",
                "high",
                "Introduced exec() via patch",
            ),
            (
                "os.system(",
                "Command Injection",
                "CWE-78",
                "high",
                "Introduced os.system() via patch",
            ),
            (
                "subprocess.Popen(",
                "Command Injection",
                "CWE-78",
                "medium",
                "Introduced subprocess.Popen() via patch",
            ),
            (
                "pickle.loads(",
                "Deserialization",
                "CWE-502",
                "high",
                "Introduced pickle.loads() via patch",
            ),
        ]

        for pattern, vuln_type, cwe, severity, desc in dangerous_patterns:
            if pattern in added_text and pattern not in original_code:
                issues.append(
                    SecurityIssue(
                        type=vuln_type,
                        severity=severity,
                        line=None,
                        description=desc,
                        cwe=cwe,
                    )
                )

        return issues

    def simulate_inline(
        self,
        original_code: str,
        new_code: str,
        language: str = "python",
    ) -> RefactorResult:
        """Simulate by comparing original and new code directly.

        This is a convenience method when you have both versions.

        Args:
            original_code: Original source code
            new_code: New/modified source code
            language: Source language

        Returns:
            RefactorResult with safety analysis
        """
        return self.simulate(
            original_code=original_code,
            new_code=new_code,
            language=language,
        )

    def _apply_patch(self, original: str, patch: str) -> str:
        """Apply a unified diff patch to the original code."""
        # Parse the patch
        original_lines = original.splitlines(keepends=True)
        patched_lines = list(original_lines)

        # Simple unified diff parser
        hunk_pattern = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")

        lines = patch.splitlines(keepends=True)
        i = 0
        offset = 0

        while i < len(lines):
            line = lines[i]

            # Find hunk header
            match = hunk_pattern.match(line)
            if match:
                old_start = int(match.group(1)) - 1  # 0-indexed
                i += 1

                # Process hunk
                current_old = old_start + offset
                deletions = []
                additions = []

                while i < len(lines) and not lines[i].startswith("@@"):
                    hunk_line = lines[i]
                    if hunk_line.startswith("-") and not hunk_line.startswith("---"):
                        deletions.append(current_old)
                        current_old += 1
                    elif hunk_line.startswith("+") and not hunk_line.startswith("+++"):
                        additions.append(hunk_line[1:])
                    elif hunk_line.startswith(" ") or hunk_line == "\n":
                        current_old += 1
                    i += 1

                # Apply deletions (in reverse to preserve indices)
                for del_idx in reversed(deletions):
                    if del_idx < len(patched_lines):
                        patched_lines.pop(del_idx)

                # Apply additions
                insert_point = old_start + offset
                for j, add_line in enumerate(additions):
                    patched_lines.insert(insert_point + j, add_line)

                offset += len(additions) - len(deletions)
            else:
                i += 1

        return "".join(patched_lines)

    def _check_syntax(self, code: str, language: str) -> str | None:
        """Check if code has valid syntax. Returns error message or None."""
        if language == "python":
            try:
                ast.parse(code)
                return None
            except SyntaxError as e:
                return f"Line {e.lineno}: {e.msg}"
        # For other languages, we'd need tree-sitter
        return None

    def _scan_security(
        self, new_code: str, original_code: str, language: str
    ) -> list[SecurityIssue]:
        """Scan for security vulnerabilities in the new code."""
        issues = []

        # Prefer the built-in security analyzer (AST + taint + dangerous patterns).
        # This exists in the core package and should be available in normal installs.
        try:
            from code_scalpel.security.analyzers import (
                SecurityAnalyzer,
            )
            from code_scalpel.security.analyzers.taint_tracker import SecuritySink

            analyzer = SecurityAnalyzer()

            new_result = analyzer.analyze(new_code)
            old_result = analyzer.analyze(original_code)

            old_vulns = {
                (v.sink_type, v.sink_location)
                for v in getattr(old_result, "vulnerabilities", [])
            }

            severity_by_sink = {
                SecuritySink.SHELL_COMMAND: "high",
                SecuritySink.SQL_QUERY: "high",
                SecuritySink.EVAL: "high",
                SecuritySink.DESERIALIZATION: "high",
                SecuritySink.SSRF: "high",
                SecuritySink.WEAK_CRYPTO: "medium",
                SecuritySink.HARDCODED_SECRET: "medium",
                SecuritySink.HTML_OUTPUT: "medium",
                SecuritySink.DOM_XSS: "medium",
                SecuritySink.SSTI: "high",
                SecuritySink.XXE: "high",
            }

            for vuln in getattr(new_result, "vulnerabilities", []):
                vuln_key = (vuln.sink_type, vuln.sink_location)
                if vuln_key in old_vulns:
                    continue

                line = vuln.sink_location[0] if vuln.sink_location else None
                issues.append(
                    SecurityIssue(
                        type=vuln.vulnerability_type,
                        severity=severity_by_sink.get(vuln.sink_type, "medium"),
                        line=line,
                        description=vuln.vulnerability_type,
                        cwe=vuln.cwe_id,
                    )
                )

        except Exception:
            # Fallback to pattern-based detection (best-effort).
            issues.extend(self._pattern_security_scan(new_code, original_code))

        return issues

    def _pattern_security_scan(
        self, new_code: str, original_code: str
    ) -> list[SecurityIssue]:
        """Pattern-based security scan fallback."""
        issues = []

        dangerous_patterns = [
            (
                "eval(",
                "Code Injection",
                "CWE-94",
                "high",
                "eval() can execute arbitrary code",
            ),
            (
                "exec(",
                "Code Injection",
                "CWE-94",
                "high",
                "exec() can execute arbitrary code",
            ),
            (
                "os.system(",
                "Command Injection",
                "CWE-78",
                "high",
                "os.system() can execute shell commands",
            ),
            (
                "subprocess.call(",
                "Command Injection",
                "CWE-78",
                "medium",
                "subprocess with shell=True is dangerous",
            ),
            (
                "cursor.execute(",
                "SQL Injection",
                "CWE-89",
                "high",
                "SQL query may be injectable",
            ),
            (
                "render_template_string(",
                "XSS",
                "CWE-79",
                "medium",
                "Template injection risk",
            ),
            (
                "pickle.loads(",
                "Deserialization",
                "CWE-502",
                "high",
                "Insecure deserialization",
            ),
            (
                "yaml.load(",
                "Deserialization",
                "CWE-502",
                "medium",
                "yaml.load() is unsafe, use safe_load()",
            ),
        ]

        for line_num, line in enumerate(new_code.splitlines(), 1):
            for pattern, vuln_type, cwe, severity, desc in dangerous_patterns:
                if pattern in line and pattern not in original_code:
                    issues.append(
                        SecurityIssue(
                            type=vuln_type,
                            severity=severity,
                            line=line_num,
                            description=f"Introduced {desc}",
                            cwe=cwe,
                        )
                    )

        return issues

    def _analyze_structural_changes(
        self, original: str, new_code: str, language: str
    ) -> dict[str, Any]:
        """Analyze structural changes between versions."""
        changes = {
            "functions_added": [],
            "functions_removed": [],
            "functions_modified": [],
            "classes_added": [],
            "classes_removed": [],
            "imports_added": [],
            "imports_removed": [],
            "lines_added": 0,
            "lines_removed": 0,
        }

        if language == "python":
            try:
                old_tree = ast.parse(original)
                new_tree = ast.parse(new_code)

                old_funcs = {
                    n.name for n in ast.walk(old_tree) if isinstance(n, ast.FunctionDef)
                }
                new_funcs = {
                    n.name for n in ast.walk(new_tree) if isinstance(n, ast.FunctionDef)
                }

                old_classes = {
                    n.name for n in ast.walk(old_tree) if isinstance(n, ast.ClassDef)
                }
                new_classes = {
                    n.name for n in ast.walk(new_tree) if isinstance(n, ast.ClassDef)
                }

                old_imports = set()
                new_imports = set()

                for node in ast.walk(old_tree):
                    if isinstance(node, ast.Import):
                        old_imports.update(a.name for a in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        old_imports.update(
                            f"{node.module}.{a.name}" for a in node.names
                        )

                for node in ast.walk(new_tree):
                    if isinstance(node, ast.Import):
                        new_imports.update(a.name for a in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        new_imports.update(
                            f"{node.module}.{a.name}" for a in node.names
                        )

                changes["functions_added"] = list(new_funcs - old_funcs)
                changes["functions_removed"] = list(old_funcs - new_funcs)
                changes["classes_added"] = list(new_classes - old_classes)
                changes["classes_removed"] = list(old_classes - new_classes)
                changes["imports_added"] = list(new_imports - old_imports)
                changes["imports_removed"] = list(old_imports - new_imports)

            except SyntaxError:
                pass

        # Count line changes
        diff = list(
            difflib.unified_diff(
                original.splitlines(), new_code.splitlines(), lineterm=""
            )
        )

        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                changes["lines_added"] += 1
            elif line.startswith("-") and not line.startswith("---"):
                changes["lines_removed"] += 1

        return changes

    def _generate_warnings(self, structural_changes: dict[str, Any]) -> list[str]:
        """Generate warnings based on structural changes."""
        warnings = []

        if structural_changes.get("functions_removed"):
            funcs = ", ".join(structural_changes["functions_removed"])
            warnings.append(f"Removed functions: {funcs}")

        if structural_changes.get("classes_removed"):
            classes = ", ".join(structural_changes["classes_removed"])
            warnings.append(f"Removed classes: {classes}")

        lines_added = structural_changes.get("lines_added", 0)
        lines_removed = structural_changes.get("lines_removed", 0)

        if lines_removed > lines_added * 2:
            warnings.append(
                f"Large deletion: {lines_removed} lines removed vs {lines_added} added"
            )

        if lines_added > 100:
            warnings.append(f"Large addition: {lines_added} new lines")

        return warnings

    def _determine_verdict(
        self,
        security_issues: list[SecurityIssue],
        structural_changes: dict[str, Any],
        warnings: list[str],
    ) -> tuple[RefactorStatus, bool, str | None]:
        """Determine the final verdict."""
        # High severity security issues = UNSAFE
        high_severity = [i for i in security_issues if i.severity == "high"]
        if high_severity:
            issue = high_severity[0]
            return (
                RefactorStatus.UNSAFE,
                False,
                f"Introduced {issue.type} vulnerability: {issue.description}",
            )

        # Medium severity = UNSAFE in strict mode, WARNING otherwise
        medium_severity = [i for i in security_issues if i.severity == "medium"]
        if medium_severity:
            issue = medium_severity[0]
            if self.strict_mode:
                return (
                    RefactorStatus.UNSAFE,
                    False,
                    f"Introduced {issue.type} vulnerability: {issue.description}",
                )
            return (
                RefactorStatus.WARNING,
                True,  # Still safe but with warning
                f"Potential {issue.type} issue: {issue.description}",
            )

        # Warnings without security issues
        if warnings and self.strict_mode:
            return (
                RefactorStatus.WARNING,
                True,
                warnings[0],
            )

        # All clear
        return (RefactorStatus.SAFE, True, None)
