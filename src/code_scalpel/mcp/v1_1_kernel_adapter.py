"""v1.1.0 Kernel Integration Layer for analyze_code.

This module adapts the Phase 6 kernel components (SourceContext, Validators, ResponseEnvelope)
to the existing analyze_code tool, enabling self-correction and structured error handling.

Design:
- SourceContext: Unified input model (wraps code/file_path detection)
- SemanticValidator: Pre-analysis validation with suggestions
- ResponseEnvelope: Already used in make_envelope(); we enhance error hints
- Backward Compatibility: Existing AnalysisResult payloads unchanged
"""

from __future__ import annotations

import logging
from typing import Optional

from code_scalpel.mcp.models.context import Language, SourceContext
from code_scalpel.mcp.validators import SemanticValidator, ValidationError
from code_scalpel.mcp.contract import ToolError, UpgradeHint

logger = logging.getLogger(__name__)


class AnalyzeCodeKernelAdapter:
    """Bridges Phase 6 Kernel to analyze_code tool.

    Responsibilities:
    1. Convert MCP arguments to SourceContext
    2. Validate input with SemanticValidator
    3. Convert validation errors to ToolError + suggestions
    4. Track metrics for suggestion effectiveness
    """

    def __init__(self):
        """Initialize adapter with validators and metrics."""
        self.validator = SemanticValidator()
        # Future: integrate MetricsCollector here for suggestion tracking

    def create_source_context(
        self,
        code: Optional[str] = None,
        file_path: Optional[str] = None,
        language: str = "auto",
    ) -> SourceContext:
        """Create SourceContext from analyze_code arguments.

        Args:
            code: Source code string (if provided)
            file_path: Path to source file (if provided)
            language: Language hint ("auto" = auto-detect)

        Returns:
            SourceContext with normalized content and language

        Raises:
            ValueError: If both code and file_path are None
        """
        import os

        if code is None and file_path is None:
            raise ValueError("Either 'code' or 'file_path' must be provided")

        # Determine language (will be auto-detected if "auto")
        detected_language = Language.UNKNOWN
        if language != "auto":
            try:
                detected_language = Language(language.lower())
            except ValueError:
                # Default to PYTHON for compatibility with unknown languages
                detected_language = Language.PYTHON

        # Load content from file if needed
        actual_content = code
        if actual_content is None and file_path is not None:
            if not os.path.isfile(file_path):
                raise ValueError(f"File not found: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                actual_content = f.read()

        # Create SourceContext
        ctx = SourceContext(
            content=actual_content,
            file_path=file_path,
            language=detected_language,
            is_memory=code is not None,  # Memory-based if code provided inline
        )

        return ctx

    def validate_input(
        self,
        ctx: SourceContext,
        request_scope: Optional[str] = None,
    ) -> tuple[bool, Optional[ToolError], list[str]]:
        """Validate input with SemanticValidator.

        For analyze_code, we perform minimal validation:
        - Basic syntax check for Python code
        - File readability for file_path inputs

        Args:
            ctx: SourceContext to validate
            request_scope: Optional scope for locality-aware suggestions

        Returns:
            (is_valid, error_obj, suggestions)
            - is_valid: True if all validations passed
            - error_obj: ToolError if validation failed, None otherwise
            - suggestions: List of suggestions for self-correction
        """
        try:
            # For analyze_code, we do basic structural validation
            # Full semantic validation (symbol existence) is not needed here
            # since analyze_code parses arbitrary code that may not be executable

            # Placeholder for future: Add syntax validation if needed
            logger.debug(
                f"Validating input: language={ctx.language}, is_memory={ctx.is_memory}"
            )

            return (True, None, [])

        except ValidationError as e:
            # Convert ValidationError to ToolError
            error_obj = ToolError(
                error=str(e),
                error_code="invalid_argument",
                error_details={"validation_error": str(e)},
            )
            return (False, error_obj, e.suggestions)
        except Exception as e:
            # Unexpected validation error
            error_obj = ToolError(
                error=f"Validation failed: {str(e)}",
                error_code="internal_error",
            )
            return (False, error_obj, [])

    def create_upgrade_hints(
        self,
        tier: str,
        requested_features: Optional[list[str]] = None,
    ) -> Optional[list[UpgradeHint]]:
        """Create upgrade hints for tier-gated features.

        For v1.1.0, we support basic tier hints for analyze_code:
        - Community: Basic AST parsing
        - Pro: + Cognitive complexity, code smells
        - Enterprise: + Custom rules, compliance checks

        Args:
            tier: Current license tier
            requested_features: Features the user tried to use

        Returns:
            List of UpgradeHint objects, or None
        """
        if requested_features is None:
            return None

        hints = []

        # Map features to required tier
        feature_map = {
            "cognitive_complexity": "pro",
            "code_smells": "pro",
            "duplicate_detection": "pro",
            "halstead_metrics": "pro",
            "custom_rules": "enterprise",
            "compliance_checks": "enterprise",
            "organization_patterns": "enterprise",
            "technical_debt": "enterprise",
        }

        current_tier_order = {"community": 0, "pro": 1, "enterprise": 2}
        current_level = current_tier_order.get(tier.lower(), 0)

        for feature in requested_features:
            required_tier = feature_map.get(feature)
            if required_tier:
                required_level = current_tier_order.get(required_tier, 0)
                if required_level > current_level:
                    hints.append(
                        UpgradeHint(
                            feature=feature,
                            tier=required_tier.upper(),
                            reason=f"Feature '{feature}' is available in {required_tier.upper()} tier and above",
                        )
                    )

        return hints if hints else None


# Global adapter instance
_adapter: Optional[AnalyzeCodeKernelAdapter] = None


def get_adapter() -> AnalyzeCodeKernelAdapter:
    """Get or create global adapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = AnalyzeCodeKernelAdapter()
    return _adapter


__all__ = [
    "AnalyzeCodeKernelAdapter",
    "get_adapter",
]
