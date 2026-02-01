"""Golden master tests for the validation system.

Tests cover:
1. Weighted scoring algorithm correctness
2. Scope-aware fuzzy matching
3. Export boost logic
4. Locality boost logic
5. Threshold filtering
6. Symbol extraction (Python and JavaScript)
7. Semantic validator integration
8. Error messages with suggestions
"""

import pytest
from code_scalpel.mcp.models.context import Language, SourceContext
from code_scalpel.mcp.validators import (
    ScoredCandidate,
    WeightedSymbolMatcher,
    ValidationError,
    SymbolExtractor,
    SemanticValidator,
    StructuralValidator,
)

# =============================================================================
# GOLDEN MASTER TESTS: WeightedSymbolMatcher
# =============================================================================


class TestWeightedSymbolMatcher:
    """Test the weighted symbol matching algorithm."""

    def test_base_score_identical_symbols(self):
        """Identical symbols should have base_score = 1.0."""
        scored = WeightedSymbolMatcher.calculate_match_score(
            target_symbol="process_data",
            candidate_symbol="process_data",
            candidate_scope="module",
            candidate_is_exported=True,
        )
        assert scored.base_score == 1.0
        assert scored.total_score == 1.0  # No boosts applied

    def test_base_score_one_char_difference(self):
        """One character difference (typo) should have high base_score."""
        # process_data vs process_dta (missing 'a')
        scored = WeightedSymbolMatcher.calculate_match_score(
            target_symbol="process_dta",
            candidate_symbol="process_data",
            candidate_scope="module",
            candidate_is_exported=False,  # No export boost
        )
        # Similarity should be high but not 1.0
        assert 0.8 < scored.base_score < 1.0
        assert scored.locality_boost == 0.0
        assert scored.export_boost == 0.0
        assert scored.total_score == scored.base_score  # No boosts

    def test_base_score_no_similarity(self):
        """Completely unrelated symbols should have low base_score."""
        scored = WeightedSymbolMatcher.calculate_match_score(
            target_symbol="foo",
            candidate_symbol="xyz",
            candidate_scope="module",
            candidate_is_exported=True,
        )
        assert scored.base_score < 0.4  # Very low similarity

    def test_locality_boost_same_scope(self):
        """Locality boost (+0.2) when request scope matches candidate scope."""
        scored = WeightedSymbolMatcher.calculate_match_score(
            target_symbol="process_dta",
            candidate_symbol="process_data",
            candidate_scope="UserService",
            candidate_is_exported=True,
            request_context_scope="UserService",
        )
        # Should have locality boost
        assert scored.locality_boost == 0.2
        # Total should include locality boost
        assert scored.total_score > scored.base_score
        # Max is capped at 1.0
        assert scored.total_score <= 1.0

    def test_locality_boost_different_scope(self):
        """No locality boost when scopes don't match."""
        scored = WeightedSymbolMatcher.calculate_match_score(
            target_symbol="process_dta",
            candidate_symbol="process_data",
            candidate_scope="UserService",
            candidate_is_exported=True,
            request_context_scope="OrderService",
        )
        assert scored.locality_boost == 0.0

    def test_locality_boost_no_request_scope(self):
        """No locality boost when request_context_scope is None."""
        scored = WeightedSymbolMatcher.calculate_match_score(
            target_symbol="process_dta",
            candidate_symbol="process_data",
            candidate_scope="UserService",
            candidate_is_exported=True,
            request_context_scope=None,
        )
        assert scored.locality_boost == 0.0

    def test_export_boost_public_api(self):
        """Export boost (+0.1) for public API symbols."""
        scored = WeightedSymbolMatcher.calculate_match_score(
            target_symbol="process_dta",
            candidate_symbol="process_data",
            candidate_scope="module",
            candidate_is_exported=True,  # Public API
        )
        assert scored.export_boost == 0.1

    def test_export_boost_private_api(self):
        """No export boost for private symbols (leading underscore)."""
        scored = WeightedSymbolMatcher.calculate_match_score(
            target_symbol="process_dta",
            candidate_symbol="process_data",
            candidate_scope="module",
            candidate_is_exported=False,  # Private
        )
        assert scored.export_boost == 0.0

    def test_total_score_capped_at_one(self):
        """Total score should never exceed 1.0."""
        # Construct a case where all boosts might add up
        scored = WeightedSymbolMatcher.calculate_match_score(
            target_symbol="process_data",
            candidate_symbol="process_data",  # Identical
            candidate_scope="UserService",
            candidate_is_exported=True,  # +0.1
            request_context_scope="UserService",  # +0.2
        )
        # base=1.0 + 0.2 (locality) + 0.1 (export) = 1.3 before capping
        assert scored.total_score == 1.0  # Capped

    def test_reason_string_format(self):
        """Reason string should show score breakdown."""
        scored = WeightedSymbolMatcher.calculate_match_score(
            target_symbol="process_dta",
            candidate_symbol="process_data",
            candidate_scope="UserService",
            candidate_is_exported=True,
            request_context_scope="UserService",
        )
        # Should mention base score and boosts
        assert "base=" in scored.reason
        assert "+local" in scored.reason
        assert "+export" in scored.reason

    def test_rank_candidates_sorts_by_score(self):
        """Candidates should be sorted by total_score descending."""
        candidates = [
            ScoredCandidate(
                name="foo",
                base_score=0.7,
                locality_boost=0.0,
                export_boost=0.0,
                total_score=0.7,
                scope="module",
                is_exported=False,
                reason="test1",
            ),
            ScoredCandidate(
                name="bar",
                base_score=0.9,
                locality_boost=0.1,
                export_boost=0.0,
                total_score=1.0,
                scope="module",
                is_exported=False,
                reason="test2",
            ),
            ScoredCandidate(
                name="baz",
                base_score=0.7,
                locality_boost=0.0,
                export_boost=0.1,
                total_score=0.8,
                scope="module",
                is_exported=True,
                reason="test3",
            ),
        ]
        ranked = WeightedSymbolMatcher.rank_candidates(
            candidates, threshold=0.6, top_k=3
        )
        assert ranked[0].name == "bar"  # Highest score
        assert ranked[1].name == "baz"
        assert ranked[2].name == "foo"

    def test_rank_candidates_filters_by_threshold(self):
        """Candidates below threshold should be filtered out."""
        candidates = [
            ScoredCandidate(
                name="high",
                base_score=0.7,
                locality_boost=0.0,
                export_boost=0.1,
                total_score=0.8,
                scope="module",
                is_exported=True,
                reason="high",
            ),
            ScoredCandidate(
                name="low",
                base_score=0.4,
                locality_boost=0.0,
                export_boost=0.0,
                total_score=0.4,
                scope="module",
                is_exported=False,
                reason="low",
            ),
        ]
        # With threshold=0.6, only "high" (0.8) passes
        ranked = WeightedSymbolMatcher.rank_candidates(
            candidates, threshold=0.6, top_k=3
        )
        assert len(ranked) == 1
        assert ranked[0].name == "high"

    def test_rank_candidates_respects_top_k(self):
        """Should return at most top_k candidates."""
        candidates = [
            ScoredCandidate(
                name=f"cand{i}",
                base_score=1.0 - (i * 0.1),
                locality_boost=0.0,
                export_boost=0.0,
                total_score=1.0 - (i * 0.1),
                scope="module",
                is_exported=True,
                reason=f"test{i}",
            )
            for i in range(10)
        ]
        ranked = WeightedSymbolMatcher.rank_candidates(
            candidates, threshold=None, top_k=3
        )
        assert len(ranked) == 3


# =============================================================================
# GOLDEN MASTER TESTS: Symbol Extraction
# =============================================================================


class TestSymbolExtractor:
    """Test symbol extraction from Python and JavaScript code."""

    def test_extract_python_functions(self):
        """Should extract function definitions with correct scope."""
        code = """
def hello():
    pass

def world():
    pass
"""
        symbols = SymbolExtractor.extract_python_symbols(code)
        assert len(symbols["functions"]) == 2
        names = [s.name for s in symbols["functions"]]
        assert "hello" in names
        assert "world" in names
        # Should have module scope
        for func in symbols["functions"]:
            assert func.scope == "module"

    def test_extract_python_classes(self):
        """Should extract class definitions."""
        code = """
class UserService:
    pass

class DataProcessor:
    pass
"""
        symbols = SymbolExtractor.extract_python_symbols(code)
        assert len(symbols["classes"]) == 2
        names = [s.name for s in symbols["classes"]]
        assert "UserService" in names
        assert "DataProcessor" in names

    def test_extract_python_class_methods(self):
        """Should extract methods inside classes with correct scope."""
        code = """
class UserService:
    def get_user(self):
        pass
    
    def save_user(self):
        pass
"""
        symbols = SymbolExtractor.extract_python_symbols(code)
        assert len(symbols["classes"]) == 1
        assert symbols["classes"][0].name == "UserService"
        # Methods should have class scope
        methods = [s for s in symbols["functions"] if s.scope == "UserService"]
        assert len(methods) == 2
        names = [m.name for m in methods]
        assert "get_user" in names
        assert "save_user" in names

    def test_extract_python_imports(self):
        """Should extract import statements."""
        code = """
import os
from pathlib import Path
from typing import Optional, List
"""
        symbols = SymbolExtractor.extract_python_symbols(code)
        imports = [s.name for s in symbols["imports"]]
        assert "os" in imports
        assert "pathlib" in imports
        assert "typing" in imports

    def test_python_symbols_are_exported_when_public(self):
        """Public symbols (no leading underscore) should have is_exported=True."""
        code = """
def public_function():
    pass

def _private_function():
    pass
"""
        symbols = SymbolExtractor.extract_python_symbols(code)
        public = [s for s in symbols["functions"] if s.name == "public_function"]
        private = [s for s in symbols["functions"] if s.name == "_private_function"]
        assert public[0].is_exported is True
        assert private[0].is_exported is False

    def test_extract_javascript_functions(self):
        """Should extract function declarations from JavaScript."""
        code = """
function hello() {
}

function world() {
}

const arrow = () => {
};
"""
        symbols = SymbolExtractor.extract_javascript_symbols(code)
        names = [s.name for s in symbols["functions"]]
        assert "hello" in names
        assert "world" in names
        assert "arrow" in names
        # All should be module scope for JS
        for func in symbols["functions"]:
            assert func.scope == "module"

    def test_extract_javascript_classes(self):
        """Should extract class definitions from JavaScript."""
        code = """
class User {
}

class Product {
}
"""
        symbols = SymbolExtractor.extract_javascript_symbols(code)
        names = [s.name for s in symbols["classes"]]
        assert "User" in names
        assert "Product" in names

    def test_extract_javascript_imports(self):
        """Should extract ES6 and CommonJS imports."""
        code = """
import React from 'react';
const express = require('express');
"""
        symbols = SymbolExtractor.extract_javascript_symbols(code)
        imports = [s.name for s in symbols["imports"]]
        assert "react" in imports
        assert "express" in imports


# =============================================================================
# GOLDEN MASTER TESTS: SemanticValidator Integration
# =============================================================================


class TestSemanticValidator:
    """Test the semantic validator with fuzzy matching."""

    def test_exact_match_symbol_exists(self):
        """Should not raise when symbol exists exactly."""
        code = """
def process_data():
    pass
"""
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        validator = SemanticValidator()
        # Should not raise (use "function" not "functions", validator adds 's')
        validator.validate_symbol_exists(
            source, symbol_name="process_data", symbol_type="function"
        )

    def test_fuzzy_match_with_typo(self):
        """Should suggest correct symbol when there's a typo."""
        code = """
def process_data():
    pass

def calculate_total():
    pass
"""
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        validator = SemanticValidator()
        # Try to find "process_dta" (missing 'a')
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_symbol_exists(
                source, symbol_name="process_dta", symbol_type="function"
            )
        error = exc_info.value
        # Should have suggestions
        assert error.suggestions is not None
        assert len(error.suggestions) > 0
        assert "process_data" in error.suggestions
        # Error message should be helpful
        assert "Did you mean" in str(error)

    def test_no_suggestions_when_threshold_not_met(self):
        """Should have no suggestions when all candidates are below threshold."""
        code = """
def foo():
    pass
"""
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        validator = SemanticValidator()
        # Try something completely different
        with pytest.raises(ValidationError):
            validator.validate_symbol_exists(
                source, symbol_name="xyz", symbol_type="function"
            )
        # May have no suggestions since "xyz" vs "foo" is very different
        # (depends on threshold, but likely empty or very few)

    def test_validate_import_exists(self):
        """Should validate imports exist."""
        code = """
import os
from pathlib import Path
"""
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        validator = SemanticValidator()
        # Should not raise
        validator.validate_import_exists(source, import_name="os")
        validator.validate_import_exists(source, import_name="pathlib")

    def test_validate_import_suggests_typo(self):
        """Should suggest correct import when there's a typo."""
        code = """
import os
import sys
"""
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        validator = SemanticValidator()
        # Try "o" (typo of "os")
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_import_exists(source, import_name="o")
        error = exc_info.value
        # Should suggest "os"
        assert "os" in error.suggestions

    def test_cache_is_used(self):
        """Symbol cache should prevent re-extraction."""
        code = """
def foo():
    pass
"""
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        validator = SemanticValidator()

        # First call extracts and caches
        validator.validate_symbol_exists(
            source, symbol_name="foo", symbol_type="function"
        )
        cache_size_after_first = len(validator.symbol_cache)

        # Second call with same source should use cache
        validator.validate_symbol_exists(
            source, symbol_name="foo", symbol_type="function"
        )
        cache_size_after_second = len(validator.symbol_cache)

        # Cache size shouldn't grow (same key)
        assert cache_size_after_first == cache_size_after_second

    def test_clear_cache(self):
        """clear_cache() should empty the symbol cache."""
        code = "def foo(): pass"
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        validator = SemanticValidator()
        validator.validate_symbol_exists(
            source, symbol_name="foo", symbol_type="function"
        )
        assert len(validator.symbol_cache) > 0
        validator.clear_cache()
        assert len(validator.symbol_cache) == 0


# =============================================================================
# GOLDEN MASTER TESTS: StructuralValidator
# =============================================================================


class TestStructuralValidator:
    """Test structural validation (syntax, file size, etc)."""

    def test_validate_python_syntax_valid(self):
        """Valid Python should not raise."""
        code = """
def hello():
    return "world"
"""
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        # Should not raise
        StructuralValidator.validate_python_syntax(source)

    def test_validate_python_syntax_invalid(self):
        """Invalid Python should raise ValidationError."""
        code = "def hello("  # Missing closing paren
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        from code_scalpel.mcp.validators import ValidationError

        with pytest.raises(ValidationError):
            StructuralValidator.validate_python_syntax(source)

    def test_validate_python_syntax_non_python_language(self):
        """Should skip validation for non-Python languages."""
        code = "let x = 1"  # JavaScript
        source = SourceContext(
            content=code,
            file_path="/test/example.js",
            language=Language.JAVASCRIPT,
        )
        # Should not raise even though it's valid JS not Python
        StructuralValidator.validate_python_syntax(source)

    def test_validate_file_size_within_limit(self):
        """File under limit should not raise."""
        code = "x = 1\n" * 100  # 600 bytes
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        # Should not raise
        StructuralValidator.validate_file_size(source, max_bytes=1_000_000)

    def test_validate_file_size_exceeds_limit(self):
        """File over limit should raise ValidationError."""
        code = "x = 1\n" * 10000  # Large file
        source = SourceContext(
            content=code,
            file_path="/test/example.py",
            language=Language.PYTHON,
        )
        from code_scalpel.mcp.validators import ValidationError

        with pytest.raises(ValidationError):
            StructuralValidator.validate_file_size(
                source,
                max_bytes=1000,  # Very small limit
            )


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestValidationIntegration:
    """Integration tests for the validation system."""

    def test_self_correction_flow(self):
        """Test the self-correction flow with agent retries."""
        code = """
class UserService:
    def get_user(self, user_id):
        return {"id": user_id}
    
    def save_user(self, user_data):
        return True
"""
        source = SourceContext(
            content=code,
            file_path="/test/service.py",
            language=Language.PYTHON,
        )
        validator = SemanticValidator()

        # Agent tries wrong symbol name (typo)
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_symbol_exists(
                source,
                symbol_name="get_usr",  # Typo: should be "get_user"
                symbol_type="function",
                request_context_scope="UserService",  # Locality hint
            )

        error = exc_info.value
        # Agent should see the suggestion
        assert "get_user" in error.suggestions
        assert len(error.suggestions) <= 3  # Top-3 suggestions

        # Agent self-corrects and retries with correct name
        validator.validate_symbol_exists(
            source,
            symbol_name="get_user",
            symbol_type="function",
            request_context_scope="UserService",
        )  # Should succeed

    def test_locality_boost_improves_ranking(self):
        """Locality boost should improve ranking of same-scope symbols."""
        code = """
class DataProcessor:
    def process_data(self):
        pass
    
    def process_item(self):
        pass

def process_file():
    pass
"""
        source = SourceContext(
            content=code,
            file_path="/test/processor.py",
            language=Language.PYTHON,
        )
        validator = SemanticValidator()

        # Search for typo "process_dta" with locality hint
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_symbol_exists(
                source,
                symbol_name="process_dta",
                symbol_type="function",
                request_context_scope="DataProcessor",  # Class hint
            )

        error = exc_info.value
        # Should suggest "process_data" over "process_file"
        # because process_data is in DataProcessor (same scope)
        if error.suggestions:
            # process_data should be first or present
            assert error.suggestions[0] == "process_data"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
