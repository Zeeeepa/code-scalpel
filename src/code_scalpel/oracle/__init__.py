"""Oracle: Deterministic code generation constraints for LLMs.

[20260126_FEATURE] Phase 1 - write_perfect_code tool

This module provides the Oracle system that generates constraint specifications
to bind LLMs to the reality of your codebase, preventing hallucinations and
enabling first-try correct code generation.

Core Components:
- symbol_extractor: Extract function/class signatures
- constraint_analyzer: Analyze graph and architectural rules
- spec_generator: Generate Markdown constraint specs
- models: Pydantic schemas for specs and rules

Public API:
- generate_constraint_spec(file_path, instruction) -> str
"""

from __future__ import annotations

__all__ = [
    "generate_constraint_spec",
]
