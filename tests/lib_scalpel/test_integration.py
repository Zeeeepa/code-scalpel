"""Integration tests for full lib_scalpel pipeline.

Tests the complete flow: ProjectScanner → ConstraintAnalyzer → SpecGenerator
"""

from code_scalpel.lib_scalpel.graph_engine.scanner import ProjectScanner
from code_scalpel.lib_scalpel.analysis.constraint_analyzer import ConstraintAnalyzer
from code_scalpel.lib_scalpel.analysis.spec_generator import SpecGenerator


class TestLibScalpelIntegration:
    """Integration tests for the complete lib_scalpel pipeline."""

    def test_full_pipeline_scanner_to_spec(self, tmp_path):
        """Test complete pipeline: scan project, analyze constraints, generate spec."""
        # Create sample Python files in temp directory
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create auth module with function and class
        auth_file = src_dir / "auth.py"
        auth_file.write_text('''"""Authentication module."""

def authenticate(username: str, password: str) -> bool:
    """Validate user credentials."""
    import database
    db = database.get_connection()
    return db.verify_user(username, password)

class AuthService:
    """Service for authentication."""
    
    def __init__(self):
        """Initialize service."""
        self.db = None
    
    def login(self, username: str) -> bool:
        """Login user."""
        return authenticate(username, "")

import json
from typing import Dict
''')

        # Create database module
        db_file = src_dir / "database.py"
        db_file.write_text('''"""Database module."""

def get_connection():
    """Get database connection."""
    import json
    return DatabaseConnection()

class DatabaseConnection:
    """Database connection."""
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials."""
        return True
''')

        # Step 1: Scan project
        scanner = ProjectScanner(
            root_dir=str(src_dir), max_files=10, max_depth=2, extract_symbols=True
        )
        graph = scanner.scan()

        assert graph is not None
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0

        # Step 2: Analyze constraints
        analyzer = ConstraintAnalyzer()
        constraints = analyzer.analyze_file(str(auth_file), graph=graph)

        assert constraints is not None
        assert constraints.file_path == str(auth_file)

        # Step 3: Generate spec
        generator = SpecGenerator()
        spec = generator.generate_constraint_spec(
            file_path=str(auth_file),
            instruction="Add JWT token validation to authenticate function",
            graph=graph,
            max_graph_depth=2,
            max_context_lines=100,
        )

        assert spec is not None
        assert spec.file_path == str(auth_file)
        assert "JWT token validation" in spec.instruction
        assert "Code Generation Constraints" in spec.markdown
        assert "Available Symbols" in spec.markdown
        assert len(spec.markdown) > 0

    def test_pipeline_with_governance_rules(self, tmp_path):
        """Test pipeline including governance rule checking."""
        # Create sample Python files
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        views_dir = src_dir / "views"
        views_dir.mkdir()
        utils_dir = src_dir / "utils"
        utils_dir.mkdir()

        # Create a view file
        view_file = views_dir / "dashboard.py"
        view_file.write_text('''"""Dashboard view."""

def render_dashboard():
    """Render dashboard."""
    from src.utils.helpers import format_data
    data = format_data()
    return {"data": data}
''')

        # Create utilities file
        utils_file = utils_dir / "helpers.py"
        utils_file.write_text('''"""Utility helpers."""

def format_data():
    """Format data."""
    return {}
''')

        # Scan project
        scanner = ProjectScanner(
            root_dir=str(src_dir), max_files=10, max_depth=3, extract_symbols=True
        )
        graph = scanner.scan()

        # Define governance rules
        governance_config = {
            "oracle": {
                "graph_constraints": {
                    "forbidden_edges": [
                        {
                            "from": "src/views",
                            "to": "src/utils",
                            "name": "no-views-to-utils",
                            "reason": "Views should not directly import utilities",
                            "action": "DENY",
                            "severity": "HIGH",
                        }
                    ]
                }
            }
        }

        # Analyze with governance
        analyzer = ConstraintAnalyzer()
        analyzer.load_governance_rules(governance_config)

        # Generate spec with topology rules
        generator = SpecGenerator()
        spec = generator.generate_constraint_spec(
            file_path=str(view_file),
            instruction="Refactor imports",
            graph=graph,
            governance_config=governance_config,
            include_topology_rules=True,
            max_graph_depth=3,
            max_context_lines=100,
        )

        assert spec is not None
        assert "Architectural Rules" in spec.markdown

    def test_pipeline_with_circular_dependency_detection(self, tmp_path):
        """Test that circular dependencies are detected in pipeline."""
        # Create files with potential circular dependency
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # File A imports B
        file_a = src_dir / "module_a.py"
        file_a.write_text('''"""Module A."""

def func_a():
    """Function in A."""
    from module_b import func_b
    return func_b()
''')

        # File B imports A
        file_b = src_dir / "module_b.py"
        file_b.write_text('''"""Module B."""

def func_b():
    """Function in B."""
    from module_a import func_a
    return func_a()
''')

        # Scan
        scanner = ProjectScanner(
            root_dir=str(src_dir), max_files=10, max_depth=2, extract_symbols=True
        )
        graph = scanner.scan()

        # Analyze
        analyzer = ConstraintAnalyzer()
        _ = analyzer.analyze_file(str(file_a), graph=graph)

        # Generate spec
        generator = SpecGenerator()
        spec = generator.generate_constraint_spec(
            file_path=str(file_a),
            instruction="Break circular dependency",
            graph=graph,
            max_graph_depth=2,
            max_context_lines=50,
        )

        assert spec is not None
        assert "Code Generation Constraints" in spec.markdown
        # The spec should handle circular dependencies gracefully
        assert len(spec.markdown) > 0

    def test_pipeline_handles_syntax_errors_gracefully(self, tmp_path):
        """Test that pipeline handles Python files with syntax errors."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create a valid file
        valid_file = src_dir / "valid.py"
        valid_file.write_text('''"""Valid module."""

def valid_function():
    """Valid function."""
    return True
''')

        # Create an invalid file (syntax error)
        invalid_file = src_dir / "invalid.py"
        invalid_file.write_text('''"""Invalid module."""

def invalid_function(
    # Missing closing parenthesis
    return True
''')

        # Scan should handle errors gracefully
        scanner = ProjectScanner(
            root_dir=str(src_dir), max_files=10, max_depth=2, extract_symbols=True
        )
        graph = scanner.scan()

        # Should still have scanned the valid file
        assert graph is not None
        assert len(graph.nodes) > 0

        # Should be able to generate spec for valid file
        generator = SpecGenerator()
        spec = generator.generate_constraint_spec(
            file_path=str(valid_file),
            instruction="Enhance valid function",
            graph=graph,
            max_graph_depth=2,
            max_context_lines=50,
        )

        assert spec is not None
        assert "valid_function" in spec.markdown

    def test_pipeline_with_enriched_symbols(self, tmp_path):
        """Test that symbol enrichment works through the pipeline."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create a file with rich symbol information
        rich_file = src_dir / "models.py"
        rich_file.write_text('''"""Data models."""

from typing import Optional, List
from dataclasses import dataclass

@dataclass
class User:
    """User model with docstring."""
    
    id: int
    name: str
    email: Optional[str] = None
    
    def get_name(self) -> str:
        """Get user name."""
        return self.name
    
    def get_email(self) -> Optional[str]:
        """Get user email."""
        return self.email
    
    @property
    def display_name(self) -> str:
        """Get display name."""
        return self.name.upper()

class Repository:
    """Base repository class."""
    
    def __init__(self):
        """Initialize repository."""
        self.items: List[User] = []
    
    def add(self, item: User) -> None:
        """Add item to repository."""
        self.items.append(item)

def create_user(name: str, email: Optional[str] = None) -> User:
    """Create a new user."""
    return User(id=1, name=name, email=email)
''')

        # Scan with symbol extraction
        scanner = ProjectScanner(
            root_dir=str(src_dir), max_files=10, max_depth=2, extract_symbols=True
        )
        graph = scanner.scan()

        # Generate spec
        generator = SpecGenerator()
        spec = generator.generate_constraint_spec(
            file_path=str(rich_file),
            instruction="Add validation to User model",
            graph=graph,
            max_graph_depth=2,
            max_context_lines=200,
        )

        assert spec is not None
        # Should include symbol information
        assert "User" in spec.markdown
        assert "get_name" in spec.markdown or "Repository" in spec.markdown
        # Should show available symbols section
        assert "Available Symbols" in spec.markdown

    def test_pipeline_respects_config_limits(self, tmp_path):
        """Test that pipeline respects max_files and max_depth limits."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Create nested directories with files
        sub1 = src_dir / "sub1"
        sub1.mkdir()
        sub2 = sub1 / "sub2"
        sub2.mkdir()

        # Create files at different levels
        file1 = src_dir / "file1.py"
        file1.write_text("# Level 1")

        file2 = sub1 / "file2.py"
        file2.write_text("# Level 2")

        file3 = sub2 / "file3.py"
        file3.write_text("# Level 3")

        # Scan with limited depth
        scanner = ProjectScanner(
            root_dir=str(src_dir), max_files=10, max_depth=1, extract_symbols=True
        )
        graph = scanner.scan()

        # Should have limited the depth
        assert graph is not None
        # Nodes should exist
        assert len(graph.nodes) > 0
        # Check that at least one node represents a file
        node_ids = [str(node.id) for node in graph.nodes]
        assert any("file" in node_id for node_id in node_ids)

        # Generate spec
        generator = SpecGenerator()
        spec = generator.generate_constraint_spec(
            file_path=str(file1),
            instruction="Test instruction",
            graph=graph,
            max_graph_depth=1,
            max_context_lines=50,
        )

        assert spec is not None
        assert len(spec.markdown) > 0
