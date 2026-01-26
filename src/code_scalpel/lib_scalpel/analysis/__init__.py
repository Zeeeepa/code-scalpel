"""Analysis - The Lawyer.

Constraint analysis and Markdown spec generation.
"""

from .constraint_analyzer import ConstraintAnalyzer
from .spec_generator import SpecGenerator

__all__ = ["ConstraintAnalyzer", "SpecGenerator"]


# Helper function for pure spec generation
def generate_markdown_spec(graph, constraints, file_path, instruction):
    """Generate Markdown spec from graph and constraints."""
    gen = SpecGenerator()
    spec = gen.generate_constraint_spec(
        file_path=file_path,
        instruction=instruction,
        graph=graph,
        governance_config=None,
    )
    return spec.markdown
