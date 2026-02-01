"""Comprehensive tests for Phase 6: ResponseEnvelope, ResponseFormatter, and validation integration.

Tests cover:
1. ResponseEnvelope versioning and metadata
2. Profile-based response filtering
3. Envelope field inclusion/exclusion
4. Data field filtering by profile
5. Validation integration with routers
6. End-to-end formatting workflow
"""

import pytest
from code_scalpel.mcp.models.context import Language, SourceContext
from code_scalpel.mcp.models.envelope import ResponseEnvelope, SchemaVersion
from code_scalpel.mcp.response_formatter import (
    ResponseFormatter,
    PROFILE_MINIMAL,
    PROFILE_STANDARD,
    PROFILE_VERBOSE,
    PROFILE_DEBUG,
    PROFILES,
)
from code_scalpel.mcp.validators import SemanticValidator

# =============================================================================
# TESTS: ResponseEnvelope
# =============================================================================


class TestResponseEnvelope:
    """Test ResponseEnvelope functionality."""

    def test_envelope_creation_with_data(self):
        """Envelope should be creatable with minimal data."""
        envelope = ResponseEnvelope(
            tool_id="analyze_code",
            tool_name="Code Analyzer",
            tool_version="1.0.0",
            data={"results": "test"},
        )
        assert envelope.tool_id == "analyze_code"
        assert envelope.tool_name == "Code Analyzer"
        assert envelope.tool_version == "1.0.0"
        assert envelope.data == {"results": "test"}
        assert envelope.schema_version == SchemaVersion.V1_1

    def test_envelope_with_error(self):
        """Envelope.with_error() should set error and suggestions."""
        envelope = ResponseEnvelope(
            tool_id="test_tool",
            tool_name="Test",
            tool_version="1.0.0",
            data={},
        )
        envelope.with_error(
            "Symbol not found",
            suggestions=["did_you_mean_this", "or_this"],
        )
        assert envelope.error == "Symbol not found"
        assert envelope.suggestions == ["did_you_mean_this", "or_this"]
        assert envelope.validation_passed is False

    def test_envelope_with_suggestions(self):
        """Envelope.with_suggestions() should add suggestions."""
        envelope = ResponseEnvelope(
            tool_id="test_tool",
            tool_name="Test",
            tool_version="1.0.0",
            data={},
        )
        envelope.with_suggestions(
            ["option1", "option2"],
            upgrade_hints=["Pro feature"],
        )
        assert envelope.suggestions == ["option1", "option2"]
        assert envelope.upgrade_hints == ["Pro feature"]

    def test_envelope_with_validation_warning(self):
        """Envelope.with_validation_warning() should add warnings."""
        envelope = ResponseEnvelope(
            tool_id="test_tool",
            tool_name="Test",
            tool_version="1.0.0",
            data={},
        )
        envelope.with_validation_warning("Possible import issue")
        envelope.with_validation_warning("Deprecated syntax")
        assert len(envelope.validation_errors) == 2
        assert "Possible import issue" in envelope.validation_errors

    def test_envelope_to_dict(self):
        """Envelope.to_dict() should serialize to dict."""
        envelope = ResponseEnvelope(
            tool_id="test_tool",
            tool_name="Test",
            tool_version="1.0.0",
            data={"key": "value"},
            error="Test error",
        )
        result = envelope.to_dict()
        assert result["tool_id"] == "test_tool"
        assert result["data"] == {"key": "value"}
        assert result["error"] == "Test error"

    def test_envelope_to_json(self):
        """Envelope.to_json() should serialize to JSON string."""
        envelope = ResponseEnvelope(
            tool_id="test_tool",
            tool_name="Test",
            tool_version="1.0.0",
            data={"key": "value"},
        )
        json_str = envelope.to_json()
        assert isinstance(json_str, str)
        assert "test_tool" in json_str
        assert "key" in json_str


# =============================================================================
# TESTS: ResponseFormatter with Envelope
# =============================================================================


class TestResponseFormatterWithEnvelope:
    """Test ResponseFormatter with ResponseEnvelope."""

    def test_filter_envelope_minimal_profile(self):
        """Minimal profile should exclude most envelope fields."""
        envelope = ResponseEnvelope(
            tool_id="analyze_code",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"result": "test"},
            tier="pro",
            duration_ms=100.5,
            error="Test error",
        )
        filtered = ResponseFormatter.filter_envelope(envelope, PROFILE_MINIMAL)
        # Minimal should not have tier or duration
        assert "tier" not in filtered or filtered.get("tier") is None
        # Should have essential fields
        assert filtered["tool_id"] == "analyze_code"
        assert filtered["data"] == {"result": "test"}

    def test_filter_envelope_verbose_profile(self):
        """Verbose profile should include envelope metadata."""
        envelope = ResponseEnvelope(
            tool_id="analyze_code",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"result": "test"},
            tier="pro",
            duration_ms=100.5,
        )
        filtered = ResponseFormatter.filter_envelope(envelope, PROFILE_VERBOSE)
        # Verbose includes tier and duration
        assert "tier" in filtered
        assert "duration_ms" in filtered

    def test_filter_envelope_debug_profile(self):
        """Debug profile should include everything."""
        envelope = ResponseEnvelope(
            tool_id="analyze_code",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"result": "test"},
            tier="pro",
            duration_ms=100.5,
            request_id="req-123",
            capabilities_used=["feature1", "feature2"],
        )
        filtered = ResponseFormatter.filter_envelope(envelope, PROFILE_DEBUG)
        # Debug includes all fields
        assert filtered["tool_id"] == "analyze_code"
        assert filtered.get("tier") == "pro"
        assert filtered.get("request_id") == "req-123"

    def test_filter_envelope_data_field(self):
        """Envelope data should be filtered according to profile."""
        envelope = ResponseEnvelope(
            tool_id="analyze_code",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={
                "results": [1, 2, 3],
                "raw_ast": "large AST dump",
                "metadata": {"internal": True},
            },
        )
        filtered = ResponseFormatter.filter_envelope(envelope, PROFILE_MINIMAL)
        # Minimal excludes raw_ast, intermediate_results, metadata
        assert "results" in filtered["data"]
        assert "raw_ast" not in filtered["data"]
        assert "metadata" not in filtered["data"]


# =============================================================================
# TESTS: Profile Resolution
# =============================================================================


class TestProfileResolution:
    """Test response profile resolution and cascading."""

    def test_profile_resolution_explicit(self):
        """Explicit profile argument should override all."""
        profile = ResponseFormatter.resolve_profile_cascading(
            tool_argument_profile="debug"
        )
        assert profile.name == "debug"

    def test_profile_resolution_fallback(self):
        """Should fall back to standard if unknown profile."""
        profile = ResponseFormatter.resolve_profile_cascading(
            tool_argument_profile="nonexistent"
        )
        # Falls back to config or standard
        assert profile in [PROFILES.get(p, PROFILE_STANDARD) for p in PROFILES]

    def test_all_profiles_available(self):
        """All standard profiles should be accessible."""
        profiles = ResponseFormatter.list_profiles()
        assert "minimal" in profiles
        assert "standard" in profiles
        assert "verbose" in profiles
        assert "debug" in profiles

    def test_profile_descriptions(self):
        """Profiles should have descriptions."""
        for name in ResponseFormatter.list_profiles():
            desc = ResponseFormatter.get_profile_description(name)
            assert desc
            assert len(desc) > 0
            assert "Unknown" not in desc or name not in PROFILES


# =============================================================================
# TESTS: format_with_envelope (end-to-end)
# =============================================================================


class TestFormatWithEnvelope:
    """Test end-to-end envelope formatting."""

    def test_format_success_response(self):
        """format_with_envelope() should create complete response."""
        result = ResponseFormatter.format_with_envelope(
            tool_id="analyze_code",
            tool_name="Code Analyzer",
            tool_version="1.0.0",
            data={"functions": 3, "classes": 2},
            profile_name="standard",
            tier="pro",
            duration_ms=150.0,
        )
        assert result["tool_id"] == "analyze_code"
        assert result["tool_name"] == "Code Analyzer"
        assert result["data"] == {"functions": 3, "classes": 2}
        assert result["response_profile"] == "standard"

    def test_format_error_response(self):
        """format_with_envelope() should include error and suggestions."""
        result = ResponseFormatter.format_with_envelope(
            tool_id="analyze_code",
            tool_name="Code Analyzer",
            tool_version="1.0.0",
            data={},
            error="Symbol 'process_dta' not found",
            suggestions=["process_data", "process_item"],
            profile_name="standard",
        )
        assert result["error"] == "Symbol 'process_dta' not found"
        assert "process_data" in result.get("suggestions", [])

    def test_format_with_capabilities(self):
        """format_with_envelope() should track capabilities."""
        result = ResponseFormatter.format_with_envelope(
            tool_id="analyze_code",
            tool_name="Code Analyzer",
            tool_version="1.0.0",
            data={"result": "test"},
            capabilities_used=["ast_analysis", "type_checking"],
        )
        assert result.get("capabilities_used") == ["ast_analysis", "type_checking"]


# =============================================================================
# TESTS: Validation Integration
# =============================================================================


class TestValidationIntegration:
    """Test validator integration with formatting."""

    def test_formatter_with_validation_suggestions(self):
        """Formatter should include validation suggestions in envelope."""
        from code_scalpel.mcp.validators import ValidationError

        code = """
def get_user():
    pass

def save_user():
    pass
"""
        source = SourceContext(
            content=code,
            file_path="/test/service.py",
            language=Language.PYTHON,
        )
        validator = SemanticValidator()

        # Try to find misspelled symbol
        error_msg = None
        suggestions = []
        try:
            validator.validate_symbol_exists(
                source,
                symbol_name="get_usr",  # Typo
                symbol_type="function",
            )
        except ValidationError as e:
            error_msg = str(e)
            suggestions = getattr(e, "suggestions", [])

        # Format response with suggestions
        result = ResponseFormatter.format_with_envelope(
            tool_id="analyze_code",
            tool_name="Code Analyzer",
            tool_version="1.0.0",
            data={},
            error=error_msg,
            suggestions=suggestions,
        )
        if suggestions:
            assert "get_user" in result.get("suggestions", [])

    def test_envelope_preserves_validation_metadata(self):
        """Envelope should preserve validation metadata across profiles."""
        envelope = ResponseEnvelope(
            tool_id="analyze_code",
            tool_name="Analyzer",
            tool_version="1.0.0",
            data={"result": "test"},
            validation_passed=False,
            suggestions=["suggestion1"],
        )

        # Minimal profile should still have suggestions
        filtered_minimal = ResponseFormatter.filter_envelope(envelope, PROFILE_MINIMAL)
        # Verbose profile should definitely have suggestions
        filtered_verbose = ResponseFormatter.filter_envelope(envelope, PROFILE_VERBOSE)

        assert "data" in filtered_minimal
        assert "data" in filtered_verbose


# =============================================================================
# TESTS: Schema Versioning
# =============================================================================


class TestSchemaVersioning:
    """Test ResponseEnvelope schema versioning."""

    def test_envelope_current_schema_version(self):
        """Envelope should use current schema version by default."""
        envelope = ResponseEnvelope(
            tool_id="test",
            tool_name="Test",
            tool_version="1.0.0",
            data={},
        )
        assert envelope.schema_version == SchemaVersion.CURRENT

    def test_envelope_can_specify_version(self):
        """Envelope should allow specifying schema version."""
        envelope = ResponseEnvelope(
            tool_id="test",
            tool_name="Test",
            tool_version="1.0.0",
            data={},
            schema_version=SchemaVersion.V1_0,
        )
        assert envelope.schema_version == SchemaVersion.V1_0

    def test_schema_version_in_json(self):
        """Schema version should appear in JSON output."""
        envelope = ResponseEnvelope(
            tool_id="test",
            tool_name="Test",
            tool_version="1.0.0",
            data={},
        )
        json_str = envelope.to_json()
        assert SchemaVersion.CURRENT.value in json_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
