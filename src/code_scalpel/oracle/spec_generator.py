"""Constraint spec generator for LLM code generation.

[20260126_FEATURE] Generate Markdown constraint specifications.

Combines symbol tables, graph constraints, and architectural rules
into a single Markdown document for LLM consumption.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from code_scalpel.oracle.models import (
    GraphConstraints,
    MarkdownSpec,
    SymbolTable,
    TopologyRule,
)
from code_scalpel.oracle.symbol_extractor import SymbolExtractor
from code_scalpel.oracle.constraint_analyzer import ConstraintAnalyzer

logger = logging.getLogger(__name__)


class SpecGenerator:
    """Generates constraint specifications in Markdown format."""

    def __init__(self):
        """Initialize the generator."""
        self.symbol_extractor = SymbolExtractor()
        self.constraint_analyzer = ConstraintAnalyzer()

    def generate_constraint_spec(
        self,
        file_path: str,
        instruction: str,
        graph: Any = None,
        governance_config: Optional[Dict[str, Any]] = None,
        tier: str = "community",
        max_graph_depth: Optional[int] = None,
        max_context_lines: Optional[int] = None,
    ) -> MarkdownSpec:
        """Generate a constraint specification for a file.

        Args:
            file_path: Target file path
            instruction: What needs to be implemented
            graph: UniversalGraph instance (optional)
            governance_config: Governance config (optional)
            tier: Current tier ("community", "pro", "enterprise")
            max_graph_depth: Max depth for graph analysis
            max_context_lines: Max lines of code context

        Returns:
            MarkdownSpec with Markdown constraint specification

        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file has syntax errors
        """
        # Apply tier-based limits
        if max_graph_depth is None:
            max_graph_depth = self._get_tier_graph_depth(tier)
        if max_context_lines is None:
            max_context_lines = self._get_tier_context_lines(tier)

        # Extract symbol table
        try:
            symbol_table = self.symbol_extractor.extract_from_file(file_path)
        except (FileNotFoundError, SyntaxError):
            raise

        # Analyze constraints
        graph_constraints = self.constraint_analyzer.analyze_file(
            file_path,
            graph=graph,
            governance_config=governance_config,
            max_depth=max_graph_depth,
        )

        # Build topology rules
        topology_rules = []
        if governance_config and tier in ("pro", "enterprise"):
            self.constraint_analyzer.load_governance_rules(governance_config)
            topology_rules = list(self.constraint_analyzer.topology_rules.values())

        # Generate Markdown
        markdown = self._generate_markdown(
            file_path=file_path,
            instruction=instruction,
            symbol_table=symbol_table,
            graph_constraints=graph_constraints,
            topology_rules=topology_rules,
            tier=tier,
            max_context_lines=max_context_lines,
        )

        return MarkdownSpec(
            file_path=file_path,
            instruction=instruction,
            markdown=markdown,
            tier=tier,
            generated_at=datetime.utcnow().isoformat() + "Z",
        )

    def _generate_markdown(
        self,
        file_path: str,
        instruction: str,
        symbol_table: SymbolTable,
        graph_constraints: GraphConstraints,
        topology_rules: List[TopologyRule],
        tier: str,
        max_context_lines: int,
    ) -> str:
        """Generate Markdown constraint specification.

        Args:
            file_path: Target file
            instruction: Implementation instruction
            symbol_table: Extracted symbols
            graph_constraints: Graph analysis
            topology_rules: Architectural rules
            tier: Current tier
            max_context_lines: Max context lines

        Returns:
            Markdown specification string
        """
        lines = []

        # Header
        lines.append(f"# Code Generation Constraints for {file_path}\n")
        lines.append(f"*Generated: {datetime.utcnow().isoformat()}Z*\n")
        lines.append(f"*Tier: {tier.upper()}*\n")

        # Instruction
        lines.append("## Instruction\n")
        lines.append(f"{instruction}\n")

        # Available Symbols
        lines.append("## Available Symbols\n")

        if symbol_table.functions:
            lines.append("### Functions\n")
            for func in symbol_table.functions:
                lines.append(f"- `{func.signature}` (line {func.line})")
                if func.docstring:
                    lines.append(f"\n  {func.docstring.split(chr(10))[0]}")
                lines.append("\n")

        if symbol_table.classes:
            lines.append("### Classes\n")
            for cls in symbol_table.classes:
                bases = f"({', '.join(cls.bases)})" if cls.bases else ""
                lines.append(f"- `{cls.name}{bases}` (line {cls.line})\n")
                if cls.docstring:
                    lines.append(f"  {cls.docstring.split(chr(10))[0]}\n")
                if cls.methods:
                    lines.append("  Methods:\n")
                    for method in cls.methods[:5]:  # Limit to 5 methods
                        lines.append(f"    - `{method.signature}`\n")
                    if len(cls.methods) > 5:
                        lines.append(f"    - ... and {len(cls.methods) - 5} more\n")

        if symbol_table.imports:
            lines.append("### Imports\n")
            for imp in symbol_table.imports:
                if imp.symbols:
                    symbols_str = ", ".join(imp.symbols)
                    lines.append(f"- `{imp.module}`: {symbols_str}\n")
                else:
                    lines.append(f"- `{imp.module}`\n")

        # Graph Constraints
        if graph_constraints.callers or graph_constraints.callees:
            lines.append("## Graph Constraints\n")

            if graph_constraints.callers:
                lines.append("### Callers (Who imports/uses this file)\n")
                for caller in graph_constraints.callers[:10]:  # Limit to 10
                    lines.append(f"- `{caller}`\n")
                if len(graph_constraints.callers) > 10:
                    lines.append(
                        f"- ... and {len(graph_constraints.callers) - 10} more\n"
                    )

            if graph_constraints.callees:
                lines.append("### Dependencies (What this file imports/calls)\n")
                for callee in graph_constraints.callees[:10]:  # Limit to 10
                    lines.append(f"- `{callee}`\n")
                if len(graph_constraints.callees) > 10:
                    lines.append(
                        f"- ... and {len(graph_constraints.callees) - 10} more\n"
                    )

            if graph_constraints.circular_dependencies:
                lines.append("### ⚠️ Circular Dependencies Detected\n")
                for dep in graph_constraints.circular_dependencies[:5]:
                    lines.append(f"- `{dep}`\n")

        # Architectural Rules
        if topology_rules:
            lines.append("## Architectural Rules\n")
            for rule in topology_rules:
                status = "✓ Can" if rule.action == "ALLOW" else "✗ Cannot"
                lines.append(f"- {status} {rule.description}\n")

        # Code Context
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_lines = f.readlines()

            if source_lines:
                lines.append("## Code Context\n")
                lines.append("\n```python\n")
                # Show first N lines
                context_lines = source_lines[:max_context_lines]
                lines.extend(context_lines)
                if len(source_lines) > max_context_lines:
                    lines.append(
                        f"\n# ... ({len(source_lines) - max_context_lines} more lines)\n"
                    )
                lines.append("```\n")

        except Exception as e:
            logger.warning(f"Could not read code context from {file_path}: {e}")

        # Implementation Notes
        lines.append("## Implementation Notes\n")
        lines.append("1. Follow the existing code style and patterns in this file\n")
        lines.append("2. Respect all architectural rules defined above\n")
        lines.append("3. Ensure all symbols exist as documented\n")
        lines.append("4. Test imports and dependencies resolve correctly\n")
        lines.append("5. Maintain backward compatibility with callers\n")

        return "".join(lines)

    @staticmethod
    def _get_tier_graph_depth(tier: str) -> int:
        """Get max graph depth for tier.

        Args:
            tier: Tier name

        Returns:
            Max graph depth
        """
        depths = {
            "community": 2,
            "pro": 5,
            "enterprise": 999,
        }
        return depths.get(tier, 2)

    @staticmethod
    def _get_tier_context_lines(tier: str) -> int:
        """Get max context lines for tier.

        Args:
            tier: Tier name

        Returns:
            Max context lines
        """
        lines = {
            "community": 100,
            "pro": 200,
            "enterprise": 999,
        }
        return lines.get(tier, 100)
