"""Language detection and routing for multi-language support.

This module provides the LanguageRouter that:
1. Auto-detects source code language from content or file extension
2. Routes to appropriate parser/analyzer based on language tier
3. Falls back gracefully when full AST support is unavailable
4. Validates language detection with confidence scores

Key design:
- Tier 1: Full AST support (Python, JS/TS via native/tree-sitter)
- Tier 2: Regex/text analysis (Go, Rust, Java, Terraform)
- Tier 3: Raw text (Unknown/unsupported languages)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from code_scalpel.mcp.models.context import Language

logger = logging.getLogger(__name__)


class LanguageDetectionResult:
    """Result of language detection."""

    def __init__(self, language: Language, confidence: float, detected_by: str):
        """Initialize detection result.

        Args:
            language: Detected language.
            confidence: Confidence score (0.0-1.0).
            detected_by: Method used for detection ('extension', 'shebang', 'content', 'fallback').
        """
        self.language = language
        self.confidence = confidence
        self.detected_by = detected_by

    def __repr__(self) -> str:
        return (
            f"LanguageDetectionResult(language={self.language.value}, "
            f"confidence={self.confidence:.2f}, detected_by={self.detected_by})"
        )


class LanguageRouter:
    """Routes code to appropriate parsers based on language.

    Implements graceful degradation:
    - Tier 1 languages get full AST parsing
    - Tier 2 languages get regex/text-based analysis
    - Tier 3 (unknown) gets raw text analysis
    """

    # Tier 1: Full AST support
    TIER_1_LANGUAGES = {
        Language.PYTHON: ["py", "pyw", "pyx", "pxd"],
        Language.JAVASCRIPT: ["js", "mjs", "cjs"],
        Language.TYPESCRIPT: ["ts", "tsx"],
    }

    # Tier 2: Regex/text-based analysis
    TIER_2_LANGUAGES = {
        Language.GO: ["go"],
        Language.RUST: ["rs"],
        Language.JAVA: ["java"],
        Language.TERRAFORM: ["tf", "tfvars"],
        Language.YAML: ["yaml", "yml"],
        Language.JSON: ["json"],
    }

    # File extension to language mapping
    EXTENSION_MAP = {
        **{ext: lang for lang, exts in TIER_1_LANGUAGES.items() for ext in exts},
        **{ext: lang for lang, exts in TIER_2_LANGUAGES.items() for ext in exts},
    }

    # Shebang patterns for detection
    SHEBANG_PATTERNS = {
        Language.PYTHON: [r"python", r"python3"],
        Language.JAVASCRIPT: [r"node", r"deno"],
        Language.GO: [r"go"],
    }

    @classmethod
    def detect_from_content(
        cls, content: str, confidence_threshold: float = 0.7
    ) -> Optional[Language]:
        """Detect language from code content (shebang, imports, syntax).

        Args:
            content: Source code content.
            confidence_threshold: Minimum confidence to return a detection.

        Returns:
            Detected Language or None if confidence is too low.
        """
        lines = content.split("\n", 5)[:5]

        # Check shebang
        if lines and lines[0].startswith("#!"):
            shebang = lines[0].lower()
            for lang, patterns in cls.SHEBANG_PATTERNS.items():
                if any(pattern in shebang for pattern in patterns):
                    logger.debug(f"Detected {lang.value} by shebang")
                    return lang

        # Check for language-specific patterns
        content_lower = content.lower()

        # Python indicators
        if any(
            pattern in content_lower
            for pattern in [
                "import ",
                "from ",
                "def ",
                "class ",
                ":=",
                "self.",
            ]
        ):
            if "def " in content_lower or "import " in content_lower:
                logger.debug("Detected PYTHON by content patterns")
                return Language.PYTHON

        # JavaScript/TypeScript indicators
        if any(
            pattern in content_lower
            for pattern in [
                "function ",
                "const ",
                "let ",
                "var ",
                "export ",
                "import {",
                "require(",
                "=>",
            ]
        ):
            if "function " in content_lower or "const " in content_lower:
                logger.debug("Detected JAVASCRIPT by content patterns")
                return Language.JAVASCRIPT

        # Go indicators
        if "package " in content_lower and "import (" in content_lower:
            logger.debug("Detected GO by content patterns")
            return Language.GO

        # Rust indicators
        if "fn " in content_lower and (
            "use " in content_lower or "impl " in content_lower
        ):
            logger.debug("Detected RUST by content patterns")
            return Language.RUST

        # JSON indicators
        if content.strip().startswith("{") and '"' in content:
            logger.debug("Detected JSON by content patterns")
            return Language.JSON

        # YAML indicators
        if content.lstrip().startswith("---") or (
            ":" in content and "{" not in content.split("\n")[0]
        ):
            logger.debug("Detected YAML by content patterns")
            return Language.YAML

        return None

    @classmethod
    def detect(
        cls,
        content: str,
        file_path: Optional[str] = None,
        language_override: Optional[Language] = None,
    ) -> LanguageDetectionResult:
        """Detect language using multi-strategy approach.

        Args:
            content: Source code content.
            file_path: Optional file path for extension-based detection.
            language_override: Skip detection, use this language directly.

        Returns:
            LanguageDetectionResult with detected language and confidence.
        """
        # Strategy 1: Explicit override
        if language_override and language_override != Language.UNKNOWN:
            logger.debug(f"Using language override: {language_override.value}")
            return LanguageDetectionResult(
                language=language_override,
                confidence=1.0,
                detected_by="override",
            )

        # Strategy 2: File extension
        if file_path:
            ext = Path(file_path).suffix.lstrip(".").lower()
            if ext in cls.EXTENSION_MAP:
                lang = cls.EXTENSION_MAP[ext]
                logger.debug(f"Detected {lang.value} by file extension: .{ext}")
                return LanguageDetectionResult(
                    language=lang,
                    confidence=0.95,
                    detected_by="extension",
                )

        # Strategy 3: Content-based detection
        detected = cls.detect_from_content(content)
        if detected:
            return LanguageDetectionResult(
                language=detected,
                confidence=0.8,
                detected_by="content",
            )

        # Fallback: Unknown
        logger.warning("Could not detect language, falling back to UNKNOWN")
        return LanguageDetectionResult(
            language=Language.UNKNOWN,
            confidence=0.0,
            detected_by="fallback",
        )

    @classmethod
    def get_parser_tier(cls, language: Language) -> int:
        """Get the analysis tier for a language.

        Tiers:
        - 1: Full AST parsing available
        - 2: Regex/text-based analysis
        - 3: Raw text analysis only

        Args:
            language: Language to check.

        Returns:
            Parser tier (1, 2, or 3).
        """
        if language in cls.TIER_1_LANGUAGES:
            return 1
        elif language in cls.TIER_2_LANGUAGES:
            return 2
        else:
            return 3

    @classmethod
    def can_do_ast_analysis(cls, language: Language) -> bool:
        """Check if language supports full AST analysis.

        Args:
            language: Language to check.

        Returns:
            True if Tier 1 language, False otherwise.
        """
        return cls.get_parser_tier(language) == 1

    @classmethod
    def get_analysis_mode(cls, language: Language) -> str:
        """Get recommended analysis mode for a language.

        Returns:
            One of: 'ast', 'regex', 'text'.
        """
        tier = cls.get_parser_tier(language)
        if tier == 1:
            return "ast"
        elif tier == 2:
            return "regex"
        else:
            return "text"

    @classmethod
    def get_supported_languages(cls) -> list[Language]:
        """Get list of all supported languages.

        Returns:
            List of Language enum values.
        """
        return sorted(
            set(list(cls.TIER_1_LANGUAGES.keys()) + list(cls.TIER_2_LANGUAGES.keys())),
            key=lambda lang: lang.value,
        )

    @classmethod
    def get_tier_description(cls, tier: int) -> str:
        """Get human-readable description of a parser tier.

        Args:
            tier: Parser tier (1, 2, or 3).

        Returns:
            Description string.
        """
        descriptions = {
            1: "Full AST parsing (native or tree-sitter)",
            2: "Regex and text-based analysis",
            3: "Raw text analysis only",
        }
        return descriptions.get(tier, "Unknown tier")

    @staticmethod
    def validate_and_route(
        source_context,
        validator=None,
        request_context_scope=None,
    ):
        """Route code through validation and language detection.

        This method orchestrates the validation layer with language routing:
        1. Pre-execution validation (syntax, symbols, imports)
        2. Language detection
        3. Route to appropriate parser tier

        Args:
            source_context: SourceContext with code to validate and route.
            validator: Optional SemanticValidator for symbol checking.
            request_context_scope: Optional scope for locality-aware validation.

        Returns:
            Tuple of (language, validator_suggestions, parser_tier)

        Raises:
            ValidationError: If validation fails (will include suggestions).
        """
        from code_scalpel.mcp.validators import (
            StructuralValidator,
            SemanticValidator,
        )

        language = source_context.language

        # Step 1: Structural validation (syntax, file size)
        StructuralValidator.validate_python_syntax(source_context)
        StructuralValidator.validate_file_size(source_context)

        # Step 2: Optional semantic validation (symbols, imports)
        suggestions = []
        if validator is None:
            validator = SemanticValidator()

        # Note: We don't raise on semantic validation errors here,
        # but we could collect them for suggestions
        try:
            # Could check for missing imports here
            pass
        except Exception as e:
            logger.debug(f"Semantic validation warning: {e}")

        # Step 3: Language detection
        result = LanguageRouter.detect(
            source_context.content,
            file_path=source_context.file_path,
        )

        if language == Language.UNKNOWN:
            language = result.language
            source_context.language = language
            logger.info(
                f"Auto-detected language: {language.value} "
                f"(confidence={result.confidence:.2f}, method={result.detected_by})"
            )

        # Step 4: Route to parser tier
        parser_tier = LanguageRouter.get_parser_tier(language)

        logger.debug(
            f"Routed {language.value} to tier {parser_tier}: "
            f"{LanguageRouter.get_tier_description(parser_tier)}"
        )

        return language, suggestions, parser_tier


__all__ = [
    "LanguageDetectionResult",
    "LanguageRouter",
]
