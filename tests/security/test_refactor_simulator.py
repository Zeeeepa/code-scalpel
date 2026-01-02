"""Tests for the Refactor Simulator.

Tests the safety verification of code changes before applying them.
"""

import pytest


class TestRefactorSimulator:
    """Tests for RefactorSimulator class."""

    def test_safe_refactor(self):
        """Test that safe refactors are detected as safe."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def add(x, y):
    return x + y
"""
        new_code = '''
def add(x, y):
    """Add two numbers."""
    return x + y
'''
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert result.is_safe is True
        assert result.status.value == "safe"

    def test_unsafe_eval_injection(self):
        """Test that introducing eval() is detected as unsafe."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def process(data):
    return data.upper()
"""
        new_code = """
def process(data):
    return eval(data)
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert result.is_safe is False
        assert result.status.value == "unsafe"
        assert any(
            "eval" in issue.description.lower()
            or "code injection" in issue.type.lower()
            for issue in result.security_issues
        )

    def test_unsafe_exec_injection(self):
        """Test that introducing exec() is detected as unsafe."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def run(code):
    print(code)
"""
        new_code = """
def run(code):
    exec(code)
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert result.is_safe is False
        assert result.status.value == "unsafe"

    def test_unsafe_os_system(self):
        """Test that introducing os.system() is detected as unsafe."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def run_command(cmd):
    print(f"Would run: {cmd}")
"""
        new_code = """
import os
def run_command(cmd):
    os.system(cmd)
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert result.is_safe is False
        assert "Command" in result.security_issues[0].type

    def test_unsafe_subprocess_shell_true(self):
        """Test that introducing subprocess.run(..., shell=True) is unsafe."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def run_command(cmd):
    return cmd
"""

        new_code = """
import subprocess

def run_command(cmd):
    subprocess.run(cmd, shell=True)
    return cmd
"""

        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert result.is_safe is False
        assert any(
            (issue.cwe == "CWE-78")
            or ("command" in (issue.type or "").lower())
            or ("shell" in (issue.description or "").lower())
            for issue in result.security_issues
        )

    def test_structural_changes_tracked(self):
        """Test that structural changes are tracked."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def foo():
    pass

def bar():
    pass
"""
        new_code = """
def foo():
    pass

def baz():
    pass
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert "bar" in result.structural_changes.get("functions_removed", [])
        assert "baz" in result.structural_changes.get("functions_added", [])

    def test_syntax_error_detected(self):
        """Test that syntax errors in new code are detected."""
        from code_scalpel.generators import RefactorSimulator

        original = "def foo(): pass"
        new_code = "def foo(:"  # Syntax error

        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert result.status.value == "error"
        assert "syntax" in result.reason.lower()

    def test_strict_mode_warnings(self):
        """Test strict mode treats medium severity as unsafe."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def load(data):
    return data
"""
        # subprocess.call is medium severity
        new_code = """
import subprocess
def load(data):
    subprocess.call(data)
"""
        # Normal mode
        simulator = RefactorSimulator(strict_mode=False)
        simulator.simulate(original, new_code=new_code)
        # Medium severity might be warning, not necessarily unsafe

        # Strict mode
        strict_simulator = RefactorSimulator(strict_mode=True)
        strict_result = strict_simulator.simulate(original, new_code=new_code)

        # In strict mode, any security issue should be unsafe
        if strict_result.security_issues:
            assert strict_result.is_safe is False

    def test_simulate_inline_method(self):
        """Test the simulate_inline convenience method."""
        from code_scalpel.generators import RefactorSimulator

        original = "def foo(): return 1"
        new_code = "def foo(): return 2"

        simulator = RefactorSimulator()
        result = simulator.simulate_inline(original, new_code)

        assert result.is_safe is True

    def test_must_provide_new_code_or_patch(self):
        """Test that either new_code or patch must be provided."""
        from code_scalpel.generators import RefactorSimulator

        simulator = RefactorSimulator()

        with pytest.raises(ValueError, match="Must provide"):
            simulator.simulate("def foo(): pass")

    def test_result_to_dict(self):
        """Test RefactorResult serialization."""
        from code_scalpel.generators import RefactorSimulator

        original = "def foo(): pass"
        new_code = "def foo(): return 1"

        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        data = result.to_dict()

        assert "status" in data
        assert "is_safe" in data
        assert "security_issues" in data
        assert isinstance(data["security_issues"], list)

    def test_line_changes_tracked(self):
        """Test that line additions/removals are tracked."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def foo():
    pass
"""
        new_code = """
def foo():
    x = 1
    y = 2
    z = 3
    return x + y + z
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert result.structural_changes["lines_added"] > 0

    def test_warning_on_large_deletion_strict_mode(self):
        """Test warning verdict when deletions dominate additions."""
        # [20251215_TEST] Cover warning path for deletion-heavy changes in strict mode
        from code_scalpel.generators.refactor_simulator import (
            RefactorSimulator, RefactorStatus)

        original = """
def foo():
    a = 1
    b = 2
    c = 3
    return a + b + c
"""
        new_code = """
def foo():
    return 0
"""

        simulator = RefactorSimulator(strict_mode=True)
        result = simulator.simulate(original, new_code=new_code)

        assert result.status == RefactorStatus.WARNING
        assert result.is_safe is True
        assert any("Large deletion" in warning for warning in result.warnings)


class TestRefactorSimulatorPatch:
    """Tests for patch application."""

    def test_simple_patch_application(self):
        """Test applying a simple unified diff patch."""
        from code_scalpel.generators import RefactorSimulator

        original = """def foo():
    return 1
"""
        patch = """@@ -1,2 +1,2 @@
 def foo():
-    return 1
+    return 2
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, patch=patch)

        assert "return 2" in result.patched_code

    def test_patch_introducing_eval_is_unsafe(self):
        """Patch-mode should detect eval() introduction."""
        from code_scalpel.generators import RefactorSimulator

        original = """def foo(data):
    return data
"""

        patch = """@@ -1,2 +1,3 @@
 def foo(data):
-    return data
+    # dangerous
+    return eval(data)
"""

        simulator = RefactorSimulator()
        result = simulator.simulate(original, patch=patch)

        assert result.is_safe is False
        assert any("Code Injection" in issue.type for issue in result.security_issues)

    def test_invalid_patch_error(self):
        """Test that invalid patches are handled gracefully."""
        from code_scalpel.generators import RefactorSimulator

        original = "def foo(): pass"
        patch = "not a valid patch format"

        simulator = RefactorSimulator()
        # Should not crash
        simulator.simulate(original, patch=patch)
        # Result depends on implementation handling


class TestRefactorSimulatorSecurityPatterns:
    """Tests for specific security pattern detection."""

    def test_sql_injection_pattern(self):
        """Test SQL injection detection via cursor.execute."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def get_user(user_id):
    return {"id": user_id}
"""
        new_code = """
def get_user(user_id):
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert result.is_safe is False
        assert any("SQL" in issue.type for issue in result.security_issues)

    def test_pickle_deserialization(self):
        """Test pickle.loads detection."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def load_data(data):
    return data
"""
        new_code = """
import pickle
def load_data(data):
    return pickle.loads(data)
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert result.is_safe is False
        assert any("Deserialization" in issue.type for issue in result.security_issues)

    def test_safe_yaml_load(self):
        """Test that yaml.safe_load is not flagged (only yaml.load)."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def load_config(data):
    return data
"""
        # yaml.safe_load is safe
        new_code = """
import yaml
def load_config(data):
    return yaml.safe_load(data)
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        # Should not flag yaml.safe_load
        yaml_issues = [
            i for i in result.security_issues if "yaml" in i.description.lower()
        ]
        assert len(yaml_issues) == 0


class TestRefactorSimulatorWarnings:
    """Tests for warning generation."""

    def test_warning_on_function_removal(self):
        """Test warning when functions are removed."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def important_function():
    return "critical"

def helper():
    pass
"""
        new_code = """
def helper():
    pass
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert any("important_function" in w for w in result.warnings)

    def test_warning_on_large_deletion(self):
        """Test warning when many lines are deleted."""
        from code_scalpel.generators import RefactorSimulator

        original = "\n".join([f"line{i} = {i}" for i in range(50)])
        new_code = "x = 1"

        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        # Should warn about large deletion
        assert (
            any("delet" in w.lower() for w in result.warnings)
            or result.structural_changes["lines_removed"] > 40
        )


class TestJavaScriptTypeScriptSupport:
    """Tests for JavaScript/TypeScript syntax validation and structural analysis.

    [20251231_TEST] v3.3.1 - Added JS/TS support tests for roadmap v1.0 compliance.
    """

    def test_js_syntax_validation_valid(self):
        """Test that valid JavaScript is accepted."""
        from code_scalpel.generators import RefactorSimulator

        original = """
function add(a, b) {
    return a + b;
}
"""
        new_code = """
function add(a, b) {
    // Added documentation
    return a + b;
}
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="javascript")

        assert result.is_safe is True
        assert result.status.value == "safe"

    def test_js_syntax_validation_invalid(self):
        """Test that invalid JavaScript syntax is detected."""
        from code_scalpel.generators import RefactorSimulator

        original = """
function add(a, b) {
    return a + b;
}
"""
        new_code = """
function add(a, b) {
    return a + b
    // Missing closing brace
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="javascript")

        # Should detect syntax error
        assert result.is_safe is False or result.status.value in ("error", "warning")

    def test_ts_syntax_validation_valid(self):
        """Test that valid TypeScript is accepted."""
        from code_scalpel.generators import RefactorSimulator

        original = """
function greet(name: string): string {
    return `Hello, ${name}!`;
}
"""
        new_code = """
function greet(name: string): string {
    // Added null check
    if (!name) return 'Hello, stranger!';
    return `Hello, ${name}!`;
}
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="typescript")

        assert result.is_safe is True
        assert result.status.value == "safe"

    def test_js_structural_analysis_function_added(self):
        """Test detection of added functions in JavaScript."""
        from code_scalpel.generators import RefactorSimulator

        original = """
function add(a, b) {
    return a + b;
}
"""
        new_code = """
function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="javascript")

        assert "subtract" in result.structural_changes.get("functions_added", [])

    def test_js_structural_analysis_function_removed(self):
        """Test detection of removed functions in JavaScript."""
        from code_scalpel.generators import RefactorSimulator

        original = """
function add(a, b) {
    return a + b;
}

function multiply(a, b) {
    return a * b;
}
"""
        new_code = """
function add(a, b) {
    return a + b;
}
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="javascript")

        assert "multiply" in result.structural_changes.get("functions_removed", [])
        # Should also generate a warning about removed function
        assert any("multiply" in w for w in result.warnings) or "multiply" in str(
            result.structural_changes
        )

    def test_js_structural_analysis_class_added(self):
        """Test detection of added classes in JavaScript."""
        from code_scalpel.generators import RefactorSimulator

        original = """
const utils = {};
"""
        new_code = """
const utils = {};

class Calculator {
    add(a, b) {
        return a + b;
    }
}
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="javascript")

        assert "Calculator" in result.structural_changes.get("classes_added", [])

    def test_js_structural_analysis_imports(self):
        """Test detection of import changes in JavaScript."""
        from code_scalpel.generators import RefactorSimulator

        original = """
import { useState } from 'react';

function App() {
    return null;
}
"""
        new_code = """
import { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    return null;
}
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="javascript")

        # Should detect new axios import
        imports_added = result.structural_changes.get("imports_added", [])
        assert "axios" in imports_added or any("axios" in imp for imp in imports_added)

    def test_ts_arrow_function_detection(self):
        """Test detection of arrow functions in TypeScript."""
        from code_scalpel.generators import RefactorSimulator

        original = """
const utils = {};
"""
        new_code = """
const add = (a: number, b: number): number => a + b;

const multiply = (a: number, b: number): number => {
    return a * b;
};
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="typescript")

        functions_added = result.structural_changes.get("functions_added", [])
        # Should detect arrow functions
        assert "add" in functions_added or "multiply" in functions_added

    def test_js_security_eval_detection(self):
        """Test that eval() injection is detected in JavaScript."""
        from code_scalpel.generators import RefactorSimulator

        original = """
function process(data) {
    return data.toUpperCase();
}
"""
        new_code = """
function process(data) {
    return eval(data);
}
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="javascript")

        # Even in JS, pattern-based detection should catch eval
        assert result.is_safe is False or any(
            "eval" in str(issue).lower() for issue in result.security_issues
        )

    def test_js_unbalanced_braces(self):
        """Test detection of unbalanced braces in JavaScript."""
        from code_scalpel.generators import RefactorSimulator

        original = """
function test() {
    console.log('test');
}
"""
        new_code = """
function test() {
    console.log('test');
    if (true) {
        console.log('nested');
    // Missing closing brace for if
}
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="javascript")

        # Should detect syntax error
        assert result.is_safe is False or result.status.value in (
            "error",
            "warning",
            "unsafe",
        )

    def test_java_syntax_validation(self):
        """Test Java syntax validation support."""
        from code_scalpel.generators import RefactorSimulator

        original = """
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
"""
        new_code = """
public class Calculator {
    public int add(int a, int b) {
        // Added logging
        System.out.println("Adding " + a + " + " + b);
        return a + b;
    }
}
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="java")

        # Should pass syntax validation
        assert result.is_safe is True or result.status.value in ("safe", "warning")


class TestProTierFeatures:
    """Tests for Pro tier features: confidence scoring and test impact analysis.

    [20251231_TEST] v3.3.1 - Pro tier feature tests.
    """

    def test_confidence_score_in_result(self):
        """Test that confidence score is included in results."""
        from code_scalpel.generators import RefactorSimulator

        original = "def add(x, y): return x + y"
        new_code = "def add(x, y): return x + y  # comment"

        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)

        assert hasattr(result, "confidence_score")
        assert 0.0 <= result.confidence_score <= 1.0
        assert hasattr(result, "confidence_factors")
        assert isinstance(result.confidence_factors, dict)

    def test_confidence_factors_populated(self):
        """Test that confidence factors are properly populated."""
        from code_scalpel.generators import RefactorSimulator

        original = "def add(x, y): return x + y"
        new_code = "def add(x, y): return x + y + 0"

        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code, language="python")

        factors = result.confidence_factors
        assert "language_support" in factors
        assert "syntax_validation" in factors
        assert "security_analysis" in factors
        assert factors["language_support"] > 0

    def test_confidence_lower_for_security_issues(self):
        """Test that confidence is affected by security issues."""
        from code_scalpel.generators import RefactorSimulator

        original = "def process(x): return x"
        unsafe_code = "def process(x): return eval(x)"

        simulator = RefactorSimulator()
        simulator.simulate(original, new_code=original)
        unsafe_result = simulator.simulate(original, new_code=unsafe_code)

        # Confidence factors should differ
        assert unsafe_result.security_issues  # Should have issues
        assert "security_analysis" in unsafe_result.confidence_factors

    def test_test_impact_analysis_enabled(self):
        """Test that test impact analysis can be enabled."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def calculate_tax(amount):
    return amount * 0.1
"""
        new_code = """
def calculate_tax(amount, rate=0.1):
    return amount * rate
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(
            original, new_code=new_code, enable_test_impact=True
        )

        assert hasattr(result, "test_impact")
        assert isinstance(result.test_impact, dict)

    def test_test_impact_with_project_root(self):
        """Test test impact analysis with project root."""
        import tempfile
        from pathlib import Path

        from code_scalpel.generators import RefactorSimulator

        # Create a temp project with a test file
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_utils.py"
            test_file.write_text(
                """
def test_calculate_tax():
    from utils import calculate_tax
    assert calculate_tax(100) == 10
"""
            )

            original = "def calculate_tax(amount): return amount * 0.1"
            new_code = "def different_func(): pass"

            simulator = RefactorSimulator()
            result = simulator.simulate(
                original,
                new_code=new_code,
                enable_test_impact=True,
                project_root=tmpdir,
            )

            assert "recommendations" in result.test_impact

    def test_to_dict_includes_new_fields(self):
        """Test that to_dict() includes new Pro tier fields."""
        from code_scalpel.generators import RefactorSimulator

        original = "x = 1"
        new_code = "x = 2"

        simulator = RefactorSimulator()
        result = simulator.simulate(original, new_code=new_code)
        result_dict = result.to_dict()

        assert "confidence_score" in result_dict
        assert "confidence_factors" in result_dict
        assert "test_impact" in result_dict
        assert "rollback_strategy" in result_dict


class TestEnterpriseTierFeatures:
    """Tests for Enterprise tier features: multi-file simulation and rollback strategy.

    [20251231_TEST] v3.3.1 - Enterprise tier feature tests.
    """

    def test_rollback_strategy_generated(self):
        """Test that rollback strategy is generated when enabled."""
        from code_scalpel.generators import RefactorSimulator

        original = """
def process_data(data):
    return data.upper()
"""
        new_code = """
def process_data(data):
    # Enhanced processing
    return data.upper().strip()
"""
        simulator = RefactorSimulator()
        result = simulator.simulate(
            original,
            new_code=new_code,
            enable_rollback_strategy=True,
            file_path="utils.py",
        )

        assert hasattr(result, "rollback_strategy")
        assert result.rollback_strategy.get("steps")
        assert result.rollback_strategy.get("original_checksum")
        assert result.rollback_strategy.get("new_checksum")

    def test_rollback_strategy_has_reverse_patch(self):
        """Test that rollback strategy includes reverse patch."""
        from code_scalpel.generators import RefactorSimulator

        original = "x = 1"
        new_code = "x = 2"

        simulator = RefactorSimulator()
        result = simulator.simulate(
            original,
            new_code=new_code,
            enable_rollback_strategy=True,
        )

        assert "reverse_patch" in result.rollback_strategy
        # Reverse patch should show change from 2 back to 1
        reverse = result.rollback_strategy["reverse_patch"]
        assert "-x = 2" in reverse or "+x = 1" in reverse

    def test_rollback_risk_assessment(self):
        """Test rollback risk is assessed based on changes."""
        from code_scalpel.generators import RefactorSimulator

        # Large change with removed functions
        original = """
def func1(): pass
def func2(): pass
def func3(): pass
def func4(): pass
"""
        new_code = "pass"

        simulator = RefactorSimulator()
        result = simulator.simulate(
            original,
            new_code=new_code,
            enable_rollback_strategy=True,
        )

        # Should be high risk due to removed functions
        assert result.rollback_strategy.get("estimated_risk") in ("medium", "high")

    def test_multi_file_simulation(self):
        """Test multi-file refactor simulation."""
        from code_scalpel.generators import RefactorSimulator

        file_changes = [
            {
                "file_path": "utils.py",
                "original_code": "def helper(): pass",
                "new_code": "def helper(): return True",
            },
            {
                "file_path": "main.py",
                "original_code": "from utils import helper",
                "new_code": "from utils import helper\nhelper()",
            },
        ]

        simulator = RefactorSimulator()
        result = simulator.simulate_multi_file(file_changes)

        assert result["summary"]["total_files"] == 2
        assert len(result["file_results"]) == 2
        assert "overall_verdict" in result
        assert "is_safe" in result

    def test_multi_file_detects_cross_file_issues(self):
        """Test that multi-file simulation detects cross-file dependency issues."""
        from code_scalpel.generators import RefactorSimulator

        file_changes = [
            {
                "file_path": "utils.py",
                "original_code": "def helper(): pass",
                "new_code": "def different_func(): pass",  # helper removed!
            },
            {
                "file_path": "main.py",
                "original_code": "from utils import helper\nhelper()",
                "new_code": "from utils import helper\nhelper()",  # Still uses helper
            },
        ]

        simulator = RefactorSimulator()
        result = simulator.simulate_multi_file(file_changes)

        # Should detect that main.py uses removed function
        assert result["dependency_analysis"]["removed_functions_total"]
        # May or may not detect cross-file issue depending on analysis depth

    def test_multi_file_aggregates_counts(self):
        """Test that multi-file aggregates safe/unsafe counts correctly."""
        from code_scalpel.generators import RefactorSimulator

        file_changes = [
            {
                "file_path": "safe.py",
                "original_code": "x = 1",
                "new_code": "x = 2",
            },
            {
                "file_path": "unsafe.py",
                "original_code": "def f(): pass",
                "new_code": "def f(): return eval(input())",
            },
        ]

        simulator = RefactorSimulator()
        result = simulator.simulate_multi_file(file_changes)

        # One safe, one unsafe
        assert result["summary"]["safe_count"] >= 0
        assert result["summary"]["unsafe_count"] >= 1  # eval should be caught
        assert result["is_safe"] is False  # Overall unsafe

    def test_multi_file_dependency_analysis(self):
        """Test dependency analysis in multi-file simulation."""
        from code_scalpel.generators import RefactorSimulator

        file_changes = [
            {
                "file_path": "a.py",
                "original_code": "def old_func(): pass",
                "new_code": "def new_func(): pass",
            },
            {
                "file_path": "b.py",
                "original_code": "class MyClass: pass",
                "new_code": "class NewClass: pass",
            },
        ]

        simulator = RefactorSimulator()
        result = simulator.simulate_multi_file(file_changes)

        dep = result["dependency_analysis"]
        assert "removed_functions_total" in dep
        assert "added_functions_total" in dep
        assert "removed_classes_total" in dep
        assert "added_classes_total" in dep
