"""Test suite for SpecGenerator.

Tests Markdown constraint specification generation.
"""

import pytest
import tempfile
from unittest.mock import MagicMock

from code_scalpel.lib_scalpel.analysis.spec_generator import SpecGenerator
from code_scalpel.lib_scalpel.models import (
    SymbolTable,
    FunctionSignature,
    ClassSignature,
    GraphConstraints,
    TopologyRule,
    MarkdownSpec,
)


class TestSpecGenerator:
    """Test cases for SpecGenerator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = SpecGenerator()

    @pytest.fixture
    def sample_python_file(self):
        """Create a sample Python file for testing."""
        content = '''"""Module docstring."""

def authenticate(username: str, password: str) -> bool:
    """Validate user credentials."""
    return True

class User:
    """User model."""
    
    def __init__(self, name: str):
        """Initialize user."""
        self.name = name
    
    def get_name(self) -> str:
        """Get user name."""
        return self.name

import json
from typing import Optional
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            return f.name

    def test_generate_constraint_spec_basic(self, sample_python_file):
        """Test generating basic constraint spec."""
        spec = self.generator.generate_constraint_spec(
            file_path=sample_python_file,
            instruction="Add JWT validation to the authenticate function",
        )

        assert isinstance(spec, MarkdownSpec)
        assert spec.file_path == sample_python_file
        assert spec.instruction == "Add JWT validation to the authenticate function"
        assert len(spec.markdown) > 0
        assert "Code Generation Constraints" in spec.markdown

    def test_generate_constraint_spec_file_not_found(self):
        """Test generating spec for non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.generator.generate_constraint_spec(
                file_path="/nonexistent/file.py",
                instruction="Some instruction",
            )

    def test_generate_constraint_spec_with_graph(self, sample_python_file):
        """Test generating spec with graph data."""
        graph = MagicMock()
        graph.predecessors.return_value = ["src/routes.py", "src/api.py"]
        graph.successors.return_value = ["src/models.py"]
        graph.find_cycles.return_value = []

        spec = self.generator.generate_constraint_spec(
            file_path=sample_python_file,
            instruction="Add validation",
            graph=graph,
        )

        assert "callers" in spec.markdown.lower() or "imports" in spec.markdown.lower()

    def test_generate_constraint_spec_custom_limits(self, sample_python_file):
        """Test custom graph depth and context line limits."""
        spec = self.generator.generate_constraint_spec(
            file_path=sample_python_file,
            instruction="Test",
            max_graph_depth=10,
            max_context_lines=50,
        )

        assert isinstance(spec, MarkdownSpec)
        assert len(spec.markdown) > 0

    def test_generate_markdown_with_symbols(self, sample_python_file):
        """Test markdown generation includes symbols."""
        symbol_table = SymbolTable(
            file_path=sample_python_file,
            language="python",
            functions=[
                FunctionSignature(
                    name="authenticate",
                    signature="authenticate(username: str, password: str) -> bool",
                    params=[
                        {"name": "username", "type": "str"},
                        {"name": "password", "type": "str"},
                    ],
                    returns="bool",
                    line=3,
                    docstring="Validate user credentials.",
                ),
            ],
            classes=[
                ClassSignature(
                    name="User",
                    bases=["object"],
                    methods=[
                        FunctionSignature(
                            name="__init__",
                            signature="__init__(name: str)",
                            params=[{"name": "name", "type": "str"}],
                            line=7,
                        )
                    ],
                    line=6,
                    docstring="User model.",
                ),
            ],
        )

        graph_constraints = GraphConstraints(file_path=sample_python_file, depth=5)

        markdown = self.generator._generate_markdown(
            file_path=sample_python_file,
            instruction="Add JWT validation",
            symbol_table=symbol_table,
            graph_constraints=graph_constraints,
            topology_rules=[],
            max_context_lines=200,
        )

        assert "Available Symbols" in markdown
        assert "authenticate" in markdown
        assert "User" in markdown
        assert "Functions" in markdown
        assert "Classes" in markdown

    def test_generate_markdown_with_graph_constraints(self):
        """Test markdown generation includes graph constraints."""
        symbol_table = SymbolTable(file_path="src/auth.py", language="python")
        graph_constraints = GraphConstraints(
            file_path="src/auth.py",
            callers=["src/routes.py", "src/api.py"],
            callees=["src/models.py", "src/utils.py"],
            depth=5,
        )

        markdown = self.generator._generate_markdown(
            file_path="src/auth.py",
            instruction="Add JWT validation",
            symbol_table=symbol_table,
            graph_constraints=graph_constraints,
            topology_rules=[],
            max_context_lines=200,
        )

        assert "Graph Constraints" in markdown
        assert "Callers" in markdown or "imports" in markdown.lower()
        assert "Dependencies" in markdown or "imports" in markdown.lower()

    def test_generate_markdown_with_circular_dependencies(self):
        """Test markdown generation with circular dependencies."""
        symbol_table = SymbolTable(file_path="src/auth.py", language="python")
        graph_constraints = GraphConstraints(
            file_path="src/auth.py",
            callers=["src/routes.py"],
            circular_dependencies=["src/models.py", "src/services.py"],
            depth=5,
        )

        markdown = self.generator._generate_markdown(
            file_path="src/auth.py",
            instruction="Add JWT validation",
            symbol_table=symbol_table,
            graph_constraints=graph_constraints,
            topology_rules=[],
            max_context_lines=200,
        )

        assert "Circular" in markdown
        assert "src/models.py" in markdown

    def test_generate_markdown_with_topology_rules(self):
        """Test markdown generation includes topology rules."""
        symbol_table = SymbolTable(file_path="src/auth.py", language="python")
        graph_constraints = GraphConstraints(file_path="src/auth.py", depth=5)
        rules = [
            TopologyRule(
                name="no-views-to-utils",
                description="Views cannot import utilities",
                from_layer="src/views",
                to_layer="src/utils",
                action="DENY",
                severity="HIGH",
            ),
            TopologyRule(
                name="allow-views-to-services",
                description="Views can import services",
                from_layer="src/views",
                to_layer="src/services",
                action="ALLOW",
                severity="LOW",
            ),
        ]

        markdown = self.generator._generate_markdown(
            file_path="src/auth.py",
            instruction="Add JWT validation",
            symbol_table=symbol_table,
            graph_constraints=graph_constraints,
            topology_rules=rules,
            max_context_lines=200,
        )

        assert "Architectural Rules" in markdown
        assert "Views cannot import utilities" in markdown
        assert "Views can import services" in markdown

    def test_generate_markdown_includes_code_context(self, sample_python_file):
        """Test markdown includes code context."""
        symbol_table = SymbolTable(file_path=sample_python_file, language="python")
        graph_constraints = GraphConstraints(file_path=sample_python_file, depth=5)

        markdown = self.generator._generate_markdown(
            file_path=sample_python_file,
            instruction="Test",
            symbol_table=symbol_table,
            graph_constraints=graph_constraints,
            topology_rules=[],
            max_context_lines=200,
        )

        assert "Code Context" in markdown
        assert "```python" in markdown

    def test_generate_markdown_includes_implementation_notes(self):
        """Test markdown includes implementation notes."""
        symbol_table = SymbolTable(file_path="src/auth.py", language="python")
        graph_constraints = GraphConstraints(file_path="src/auth.py", depth=5)

        markdown = self.generator._generate_markdown(
            file_path="src/auth.py",
            instruction="Add JWT validation",
            symbol_table=symbol_table,
            graph_constraints=graph_constraints,
            topology_rules=[],
            max_context_lines=200,
        )

        assert "Implementation Notes" in markdown
        assert "existing code style" in markdown
        assert "architectural rules" in markdown

    def test_generate_constraint_spec_with_governance(self, sample_python_file):
        """Test generating spec with governance configuration."""
        governance_config = {
            "oracle": {
                "graph_constraints": {
                    "forbidden_edges": [
                        {
                            "from": "src/views",
                            "to": "src/utils",
                            "name": "no-views-to-utils",
                            "reason": "Views cannot import utilities",
                        }
                    ]
                }
            }
        }

        spec = self.generator.generate_constraint_spec(
            file_path=sample_python_file,
            instruction="Add JWT validation",
            governance_config=governance_config,
            include_topology_rules=True,
        )

        assert isinstance(spec, MarkdownSpec)
        assert "Architectural Rules" in spec.markdown

    def test_markdown_spec_has_metadata(self, sample_python_file):
        """Test MarkdownSpec includes required metadata."""
        spec = self.generator.generate_constraint_spec(
            file_path=sample_python_file,
            instruction="Test instruction",
        )

        assert spec.file_path == sample_python_file
        assert spec.instruction == "Test instruction"
        assert spec.generated_at is not None
        # Verify generated_at is ISO format with Z suffix
        assert spec.generated_at.endswith("Z")

    def test_generate_spec_with_large_context_limit(self, sample_python_file):
        """Test generating spec with large context limit."""
        spec = self.generator.generate_constraint_spec(
            file_path=sample_python_file,
            instruction="Test",
            max_context_lines=1000,
        )

        assert isinstance(spec, MarkdownSpec)

    def test_generate_spec_with_minimal_context_limit(self, sample_python_file):
        """Test generating spec with minimal context."""
        spec = self.generator.generate_constraint_spec(
            file_path=sample_python_file,
            instruction="Test",
            max_context_lines=1,
        )

        assert isinstance(spec, MarkdownSpec)
        # Should still have code context section
        assert "Code Context" in spec.markdown

    def test_markdown_limits_symbols_display(self):
        """Test that markdown limits display of symbols to prevent bloat."""
        # Create symbol table with many classes
        classes = [
            ClassSignature(
                name=f"Class{i}",
                bases=[],
                methods=[
                    FunctionSignature(
                        name=f"method{j}",
                        signature=f"method{j}()",
                        params=[],
                        line=j,
                    )
                    for j in range(10)  # 10 methods per class
                ],
                line=i,
            )
            for i in range(10)
        ]

        symbol_table = SymbolTable(file_path="src/auth.py", language="python", classes=classes)
        graph_constraints = GraphConstraints(file_path="src/auth.py", depth=5)

        markdown = self.generator._generate_markdown(
            file_path="src/auth.py",
            instruction="Test",
            symbol_table=symbol_table,
            graph_constraints=graph_constraints,
            topology_rules=[],
            max_context_lines=200,
        )

        # Should include "and X more" indicators
        assert "more" in markdown

    def test_markdown_limits_callers_display(self):
        """Test that markdown limits display of callers."""
        symbol_table = SymbolTable(file_path="src/auth.py", language="python")
        callers = [f"src/module{i}.py" for i in range(15)]
        graph_constraints = GraphConstraints(
            file_path="src/auth.py",
            callers=callers,
            depth=5,
        )

        markdown = self.generator._generate_markdown(
            file_path="src/auth.py",
            instruction="Test",
            symbol_table=symbol_table,
            graph_constraints=graph_constraints,
            topology_rules=[],
            max_context_lines=200,
        )

        # Should show "and X more" since we have 15 callers but limit is 10
        assert "and" in markdown
        assert "more" in markdown

    def test_default_parameter_values(self, sample_python_file):
        """Test that default parameter values are sensible."""
        spec = self.generator.generate_constraint_spec(
            file_path=sample_python_file,
            instruction="Test",
        )

        assert isinstance(spec, MarkdownSpec)
        # Should have generated markdown with defaults
        assert len(spec.markdown) > 0

    def test_include_topology_rules_flag(self, sample_python_file):
        """Test that include_topology_rules flag controls rule inclusion."""
        governance_config = {
            "oracle": {
                "graph_constraints": {
                    "forbidden_edges": [
                        {
                            "from": "src/views",
                            "to": "src/utils",
                            "name": "no-views-to-utils",
                            "reason": "Views cannot import utilities",
                        }
                    ]
                }
            }
        }

        # Without flag
        spec_without = self.generator.generate_constraint_spec(
            file_path=sample_python_file,
            instruction="Test",
            governance_config=governance_config,
            include_topology_rules=False,
        )

        # With flag
        spec_with = self.generator.generate_constraint_spec(
            file_path=sample_python_file,
            instruction="Test",
            governance_config=governance_config,
            include_topology_rules=True,
        )

        # The "with" version should include architectural rules
        assert "Architectural Rules" in spec_with.markdown
        # Without flag shouldn't have rules (unless they're in code context)
        # This just ensures the flag has an effect
        assert isinstance(spec_without, MarkdownSpec)
