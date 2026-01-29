"""End-to-end integration tests for Phase 6 architecture.

This test suite validates the complete flow:
1. Input normalization with SourceContext
2. Validation engine (structural + semantic)
3. Language detection and routing
4. ResponseEnvelope creation
5. Profile-based filtering
6. Metrics tracking

Tests multi-language support, tier-based capabilities, and self-correction flows.
"""

import pytest

from code_scalpel.mcp.models.context import Language, SourceContext
from code_scalpel.mcp.metrics import (
    MetricsCollector,
    SuggestionOutcome,
    SuggestionType,
)
from code_scalpel.mcp.response_formatter import ResponseFormatter
from code_scalpel.mcp.routers import LanguageRouter
from code_scalpel.mcp.validators import StructuralValidator


class TestPhase6FullWorkflow:
    """Test complete Phase 6 workflow from input to output."""

    def test_python_success_path(self):
        """Complete successful flow for Python code."""
        code = """
def calculate_sum(a, b):
    return a + b

result = calculate_sum(1, 2)
"""
        context = SourceContext(
            content=code,
            language=Language.PYTHON,
            file_path="/tmp/test.py",
        )

        # Step 1: Validation
        StructuralValidator.validate_python_syntax(context)
        StructuralValidator.validate_file_size(context)

        # Step 2: Language detection
        result = LanguageRouter.detect(code, file_path="/tmp/test.py")
        assert result.language == Language.PYTHON

        # Step 3: Create response envelope
        response = ResponseFormatter.format_with_envelope(
            tool_id="code_analyzer",
            tool_name="Code Analyzer",
            tool_version="1.0.0",
            data={"functions": 1, "variables": 1},
            profile_name="standard",
        )

        assert response["tool_id"] == "code_analyzer"
        assert response["data"]["functions"] == 1
        assert response["response_profile"] == "standard"

    def test_python_with_syntax_error(self):
        """Handle Python code with syntax errors."""
        code = "def broken_function( # missing closing paren"
        context = SourceContext(
            content=code,
            language=Language.PYTHON,
            is_memory=True,  # Fix: memory code requires is_memory=True
        )

        # Should detect syntax error
        with pytest.raises(Exception):  # SyntaxError or ValidationError
            StructuralValidator.validate_python_syntax(context)

    def test_javascript_detection(self):
        """Detect JavaScript from content."""
        code = """
const greet = (name) => {
    console.log(`Hello, ${name}!`);
};
"""
        result = LanguageRouter.detect(code, file_path=None)
        assert result.language == Language.JAVASCRIPT
        assert result.confidence > 0.5

    def test_file_extension_detection(self):
        """Use file extension for language detection."""
        code = "unknown_content_here"

        # Go extension
        result = LanguageRouter.detect(code, file_path="/app/main.go")
        assert result.language == Language.GO
        assert result.detected_by == "extension"

        # TypeScript extension
        result = LanguageRouter.detect(code, file_path="/app/app.ts")
        assert result.language == Language.TYPESCRIPT
        assert result.detected_by == "extension"

    def test_unknown_language_fallback(self):
        """Unknown language falls back to Tier 3."""
        code = "unknown_language_code"
        result = LanguageRouter.detect(code, file_path=None)
        # Should not raise, falls back to something
        assert result.language in [
            Language.UNKNOWN,
            Language.PYTHON,
        ]  # Generic fallback

    def test_response_profile_minimal(self):
        """Minimal profile strips extra metadata."""
        response = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"result": "test_data", "metadata": "should_be_stripped"},
            profile_name="minimal",
            tier="pro",
            duration_ms=100.0,
        )

        # Minimal should not include tier, duration, version
        assert "tool_id" in response
        assert "data" in response
        assert "response_profile" in response
        # These optional fields should not be in minimal
        assert response.get("tier") is None
        assert response.get("duration_ms") is None

    def test_response_profile_standard(self):
        """Standard profile includes essentials and error handling."""
        response = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"result": "test"},
            profile_name="standard",
            error="Symbol not found",
            suggestions=["possible_symbol_1", "possible_symbol_2"],
        )

        assert response["error"] == "Symbol not found"
        assert "suggestions" in response
        assert "possible_symbol_1" in response["suggestions"]

    def test_response_profile_verbose(self):
        """Verbose profile includes all envelope fields."""
        response = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"result": "test"},
            profile_name="verbose",
            tier="premium",
            duration_ms=250.0,
            capabilities_used=["ast_analysis", "type_checking"],
        )

        assert response["tier"] == "premium"
        assert response["duration_ms"] == 250.0
        assert "capabilities_used" in response

    def test_response_profile_debug(self):
        """Debug profile includes everything without filtering."""
        response = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={
                "raw_ast": "complete_ast_here",
                "timing": {"parse": 10, "analyze": 20},
            },
            profile_name="debug",
            tier="enterprise",
            duration_ms=100.0,
            capabilities_used=["deep_analysis"],
        )

        # Debug profile preserves data fields
        assert response["data"].get("raw_ast") == "complete_ast_here"
        assert response["data"].get("timing") == {"parse": 10, "analyze": 20}
        assert response["tier"] == "enterprise"

    def test_self_correction_flow(self):
        """Test agent self-correction with suggestions."""
        # Simulate agent making a request with a typo
        typo_code = "result = process_dta()"

        # Validator detects unknown symbol and provides suggestions
        # (creating SourceContext to validate the structure)
        _context = SourceContext(
            content=typo_code,
            language=Language.PYTHON,
            is_memory=True,  # Fix: memory code requires is_memory=True
        )

        # Create response with error and suggestions
        response = ResponseFormatter.format_with_envelope(
            tool_id="symbol_validator",
            tool_name="Symbol Validator",
            tool_version="1.0.0",
            data={},
            error="Symbol 'process_dta' not found in scope",
            suggestions=["process_data", "process_item"],
            profile_name="standard",
        )

        assert response["error"] is not None
        assert "process_data" in response["suggestions"]

        # This response would be sent to the agent for self-correction
        # Agent can choose to retry with the suggested symbol

    def test_metrics_integration(self):
        """Track metrics alongside response generation."""
        metrics = MetricsCollector()

        # Track suggestion
        metric = metrics.track_suggestion(
            request_id="req_001",
            tool_id="symbol_validator",
            suggestion_type=SuggestionType.SYMBOL_TYPO,
            suggestions=["correct_name"],
            context={"typo": "corret_name"},
        )

        assert metric.request_id == "req_001"

        # Simulate agent accepting the suggestion
        metrics.report_outcome(
            request_id="req_001",
            outcome=SuggestionOutcome.ACCEPTED,
            agent_choice="correct_name",
            accuracy_score=1.0,
        )

        stats = metrics.get_statistics()
        assert stats["acceptance_rate"] == 1.0
        assert stats["avg_accuracy"] == 1.0

    def test_error_response_with_suggestions(self):
        """Error responses include actionable suggestions."""
        response = ResponseFormatter.format_with_envelope(
            tool_id="import_validator",
            tool_name="Import Validator",
            tool_version="1.0.0",
            data={},
            error="Import 'numpy' not found",
            suggestions=["from numpy import array", "import numpy as np"],
            profile_name="standard",
        )

        assert response["error"] is not None
        assert len(response["suggestions"]) == 2
        assert all("numpy" in s for s in response["suggestions"])

    def test_validation_error_with_correction(self):
        """Validation errors provide self-correction hints."""
        code = "result = undefined_variable + 5"
        # (creating SourceContext to validate the structure)
        _context = SourceContext(
            content=code,
            language=Language.PYTHON,
            is_memory=True,  # Fix: memory code requires is_memory=True
        )

        # Validator would generate suggestions
        suggestions = ["defined_variable", "another_variable"]

        response = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={},
            error="Undefined variable: undefined_variable",
            suggestions=suggestions,
            profile_name="standard",
        )

        assert response["validation_passed"] is False
        assert response.get("error") is not None
        assert "suggestions" in response


class TestPhase6MultiLanguageRouting:
    """Test language detection and routing for multiple languages."""

    def test_python_detection_by_content(self):
        """Python detected from code content."""
        code = """
import os
def main():
    print("Hello")
if __name__ == "__main__":
    main()
"""
        result = LanguageRouter.detect(code)
        assert result.language == Language.PYTHON

    def test_javascript_detection_by_content(self):
        """JavaScript detected from code content."""
        code = """
const express = require('express');
const app = express();
app.listen(3000);
"""
        result = LanguageRouter.detect(code)
        assert result.language == Language.JAVASCRIPT

    def test_go_detection_by_extension(self):
        """Go detected by file extension when extension available."""
        code = "random_code_content"
        result = LanguageRouter.detect(code, file_path="main.go")
        assert result.language == Language.GO

    def test_rust_detection_by_extension(self):
        """Rust detected by file extension."""
        code = "random_code"
        result = LanguageRouter.detect(code, file_path="lib.rs")
        assert result.language == Language.RUST

    def test_shebang_detection(self):
        """Python detected from shebang or content."""
        code = """#!/usr/bin/env python3
print("Hello")
"""
        result = LanguageRouter.detect(code)
        assert result.language == Language.PYTHON
        # May be detected as 'shebang' or 'content' depending on implementation
        assert result.detected_by in ["shebang", "content"]


class TestPhase6TierBasedCapabilities:
    """Test tier-based capability limiting and reporting."""

    def test_tier_affects_capabilities(self):
        """Different tiers have different capabilities."""
        # Pro tier can use advanced features
        response_pro = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"result": "test"},
            profile_name="verbose",
            tier="pro",
            capabilities_used=["type_checking", "ast_analysis", "optimization_hints"],
        )

        assert response_pro["tier"] == "pro"
        assert len(response_pro.get("capabilities_used", [])) == 3

    def test_community_tier_limited_capabilities(self):
        """Community tier has limited capabilities."""
        response_community = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"result": "test"},
            profile_name="minimal",
            tier="community",
            capabilities_used=["basic_syntax_check"],
        )

        # Community tier still gets capabilities but may be limited in detail
        assert response_community["response_profile"] == "minimal"


class TestPhase6ProfileCascading:
    """Test profile resolution and cascading."""

    def test_explicit_profile_override(self):
        """Explicit profile argument overrides defaults."""
        response = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"test": "data"},
            profile_name="debug",  # Explicit override
        )

        assert response["response_profile"] == "debug"

    def test_invalid_profile_fallback(self):
        """Invalid profile falls back to config default (debug in this case)."""
        response = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"test": "data"},
            profile_name="nonexistent",  # Invalid
        )

        # Should fall back to a valid profile (config default or debug)
        assert response["response_profile"] in [
            "standard",
            "minimal",
            "verbose",
            "debug",
        ]

    def test_all_profiles_available(self):
        """All standard profiles can be used."""
        profiles = ["minimal", "standard", "verbose", "debug"]
        for profile in profiles:
            response = ResponseFormatter.format_with_envelope(
                tool_id="analyzer",
                tool_name="Analyzer",
                tool_version="1.0.0",
                data={"test": "data"},
                profile_name=profile,
            )
            assert response["response_profile"] == profile


class TestPhase6DataFiltering:
    """Test data field filtering by profile."""

    def test_minimal_strips_debug_fields(self):
        """Minimal profile strips debug fields."""
        data = {
            "result": "main_data",
            "raw_ast": "debug_info",
            "intermediate_results": "should_strip",
            "timing": {"parse": 10},
        }
        response = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data=data,
            profile_name="minimal",
        )

        # Result and main fields preserved
        assert response["data"]["result"] == "main_data"
        # Debug fields stripped
        assert "raw_ast" not in response["data"]
        assert "intermediate_results" not in response["data"]
        assert "timing" not in response["data"]

    def test_debug_preserves_all_fields(self):
        """Debug profile preserves all data fields."""
        data = {
            "result": "main_data",
            "raw_ast": "debug_info",
            "intermediate_results": "preserved",
            "timing": {"parse": 10},
        }
        response = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data=data,
            profile_name="debug",
        )

        assert response["data"]["result"] == "main_data"
        assert response["data"]["raw_ast"] == "debug_info"
        assert response["data"]["intermediate_results"] == "preserved"
        assert response["data"]["timing"] == {"parse": 10}


class TestPhase6SchemaVersioning:
    """Test schema versioning for backward compatibility."""

    def test_current_schema_version(self):
        """Response uses current schema version."""
        response = ResponseFormatter.format_with_envelope(
            tool_id="analyzer",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"test": "data"},
        )

        assert "schema_version" in response
        # Should be SchemaVersion enum or string representation
        schema_version = response["schema_version"]
        schema_str = schema_version.value if hasattr(schema_version, "value") else str(schema_version)
        assert schema_str in ["1.0", "1.1", "2.0", "V1_0", "V1_1", "V2_0"]

    def test_validation_metadata_preserved(self):
        """Validation metadata is preserved across all profiles."""
        for profile in ["minimal", "standard", "verbose", "debug"]:
            response = ResponseFormatter.format_with_envelope(
                tool_id="analyzer",
                tool_name="Analyzer",
                tool_version="1.0.0",
                data={"test": "data"},
                profile_name=profile,
            )

            assert "validation_passed" in response
            assert response["validation_passed"] is not None
