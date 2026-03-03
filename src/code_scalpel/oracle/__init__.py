"""Oracle: Deterministic code generation constraints for LLMs.

[20260126_FEATURE] Phase 1 - Oracle constraint spec pipeline
[20260224_REFACTOR] write_perfect_code demoted to internal pipeline function; not a public MCP tool

This module provides the Oracle system that generates constraint specifications
to bind LLMs to the reality of your codebase, preventing hallucinations and
enabling first-try correct code generation.

Core Components:
- symbol_extractor: Extract function/class signatures
- constraint_analyzer: Analyze graph and architectural rules
- spec_generator: Generate Markdown constraint specs
- models: Pydantic schemas for specs and rules

Public API:
- generate_constraint_spec(repo_root, file_path, instruction, tier, governance_config) -> str
"""

from __future__ import annotations

from code_scalpel.oracle.oracle_pipeline import (
    generate_constraint_spec_async,
    generate_constraint_spec_sync,
)

# Main entry point - use sync version as default
generate_constraint_spec = generate_constraint_spec_sync

__all__ = [
    "generate_constraint_spec",
    "generate_constraint_spec_async",
    "generate_constraint_spec_sync",
]
