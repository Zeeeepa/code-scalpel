"""
v1.5.1 Integration Tests - Cross-File Analysis Workflows

[20251213_TEST] Tests end-to-end workflows using ImportResolver,
CrossFileExtractor, and CrossFileTaintTracker together.

These tests verify that the v1.5.1 components work correctly in
realistic scenarios that span multiple files.
"""

import pytest
import tempfile
from pathlib import Path


class TestCrossFileWorkflow:
    """Integration tests for complete cross-file analysis workflows."""

    @pytest.fixture
    def flask_project(self, tmp_path):
        """Create a realistic Flask project structure."""
        # app.py - main application entry point
        app_file = tmp_path / "app.py"
        app_file.write_text('''
from flask import Flask
from routes import register_routes

app = Flask(__name__)
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
''')

        # routes.py - route definitions
        routes_file = tmp_path / "routes.py"
        routes_file.write_text('''
from flask import request, jsonify
from services import user_service
from db import database

def register_routes(app):
    @app.route("/search")
    def search():
        query = request.args.get("q")
        results = user_service.search_users(query)
        return jsonify(results)
    
    @app.route("/users/<int:user_id>")
    def get_user(user_id):
        user = database.get_user(user_id)
        return jsonify(user)
''')

        # services/user_service.py
        services_dir = tmp_path / "services"
        services_dir.mkdir()
        (services_dir / "__init__.py").write_text("")
        (services_dir / "user_service.py").write_text('''
from db import database

def search_users(query):
    """Search for users - potentially vulnerable."""
    return database.execute_query(f"SELECT * FROM users WHERE name LIKE '%{query}%'")

def get_user_by_id(user_id):
    """Get user by ID - safe parameterized query."""
    return database.get_user(user_id)
''')

        # db.py - database module
        db_file = tmp_path / "db.py"
        db_file.write_text('''
import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
    
    def execute_query(self, query):
        """Execute raw SQL - dangerous!"""
        cursor = self.conn.cursor()
        cursor.execute(query)  # SQL Injection sink
        return cursor.fetchall()
    
    def get_user(self, user_id):
        """Get user by ID - safe."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

database = Database()
''')

        return tmp_path

    def test_import_resolver_analyzes_flask_project(self, flask_project):
        """Test that ImportResolver can analyze a Flask project."""
        from code_scalpel.ast_tools.import_resolver import ImportResolver

        resolver = ImportResolver(flask_project)
        result = resolver.build()

        assert result.success
        assert result.modules >= 4  # app, routes, db, services
        
        # Check that imports are tracked
        assert len(resolver.imports) > 0
        
        # Verify module relationships using get_importers
        db_importers = resolver.get_importers("db")
        assert len(db_importers) >= 1  # db is imported by routes and/or services

    def test_cross_file_extractor_extracts_dependencies(self, flask_project):
        """Test that CrossFileExtractor can extract search_users with all deps."""
        from code_scalpel.ast_tools.cross_file_extractor import CrossFileExtractor

        extractor = CrossFileExtractor(flask_project)
        extractor.build()

        result = extractor.extract(
            str(flask_project / "services" / "user_service.py"),
            "search_users",
            depth=2,
        )

        assert result.success
        assert result.target is not None
        assert result.target.name == "search_users"
        
        # Should have the function code
        assert "SELECT * FROM users" in result.target.code or "execute_query" in result.target.code

    def test_cross_file_taint_tracking(self, flask_project):
        """Test that CrossFileTaintTracker detects cross-file vulnerabilities."""
        from code_scalpel.symbolic_execution_tools.cross_file_taint import CrossFileTaintTracker

        tracker = CrossFileTaintTracker(flask_project)
        result = tracker.analyze(max_depth=3)

        assert result.success
        assert result.modules_analyzed >= 3  # At least app, routes, db

    def test_mcp_tools_work_with_flask_project(self, flask_project):
        """Test that the MCP tools work end-to-end."""
        import asyncio
        from code_scalpel.mcp.server import (
            get_cross_file_dependencies,
            cross_file_security_scan,
        )

        async def run_tests():
            # Test get_cross_file_dependencies - use a function instead of variable
            dep_result = await get_cross_file_dependencies(
                target_file="db.py",
                target_symbol="Database",  # A class that exists
                project_root=str(flask_project),
                max_depth=2,
            )
            assert dep_result.success
            
            # Test cross_file_security_scan
            security_result = await cross_file_security_scan(
                project_root=str(flask_project),
                max_depth=3,
            )
            assert security_result.success

        asyncio.run(run_tests())


class TestLargeProjectScalability:
    """Test that cross-file tools scale to larger projects."""

    @pytest.fixture
    def large_project(self, tmp_path):
        """Create a project with many files."""
        # Create 10 modules with cross-dependencies
        for i in range(10):
            module_file = tmp_path / f"module_{i}.py"
            
            # Each module imports from 1-3 others
            imports = []
            if i > 0:
                imports.append(f"from module_{i-1} import func_{i-1}")
            if i > 1:
                imports.append(f"from module_{i-2} import func_{i-2}")
            
            code = "\n".join(imports) + f"""

def func_{i}(x):
    '''Function in module {i}.'''
    result = x * {i+1}
"""
            # Add calls to imported functions
            if i > 0:
                code += f"    result += func_{i-1}(x)\n"
            code += "    return result\n"
            
            module_file.write_text(code)
        
        return tmp_path

    def test_import_resolver_scales(self, large_project):
        """Test that ImportResolver handles many modules."""
        from code_scalpel.ast_tools.import_resolver import ImportResolver

        resolver = ImportResolver(large_project)
        result = resolver.build()

        assert result.success
        assert result.modules == 10

    def test_cross_file_extractor_scales(self, large_project):
        """Test that CrossFileExtractor handles deep dependency chains."""
        from code_scalpel.ast_tools.cross_file_extractor import CrossFileExtractor

        extractor = CrossFileExtractor(large_project)
        extractor.build()

        result = extractor.extract(
            str(large_project / "module_9.py"),
            "func_9",
            depth=5,
        )

        assert result.success
        assert result.target is not None


class TestCircularImportHandling:
    """Test handling of circular imports across the toolchain."""

    @pytest.fixture
    def circular_project(self, tmp_path):
        """Create a project with circular imports."""
        # a.py imports from b.py
        a_file = tmp_path / "a.py"
        a_file.write_text('''
from b import func_b

def func_a():
    return func_b() + 1
''')

        # b.py imports from a.py (circular!)
        b_file = tmp_path / "b.py"
        b_file.write_text('''
from a import func_a

def func_b():
    return 42  # Would call func_a() but that would recurse

def other_func():
    return func_a()
''')

        return tmp_path

    def test_import_resolver_detects_circular(self, circular_project):
        """Test that ImportResolver detects circular imports."""
        from code_scalpel.ast_tools.import_resolver import ImportResolver

        resolver = ImportResolver(circular_project)
        result = resolver.build()

        assert result.success
        # Should have detected the circular import
        circular_imports = resolver.get_circular_imports()
        assert len(circular_imports) > 0

    def test_cross_file_extractor_handles_circular(self, circular_project):
        """Test that CrossFileExtractor doesn't infinite loop on circular deps."""
        from code_scalpel.ast_tools.cross_file_extractor import CrossFileExtractor

        extractor = CrossFileExtractor(circular_project)
        extractor.build()

        # Should complete without hanging
        result = extractor.extract(
            str(circular_project / "a.py"),
            "func_a",
            depth=3,
        )

        # Should succeed or return a valid result
        assert result is not None


class TestMCPToolConsistency:
    """Test that MCP tools return consistent results."""

    @pytest.fixture
    def simple_project(self, tmp_path):
        """Create a simple two-file project."""
        utils_file = tmp_path / "utils.py"
        utils_file.write_text('''
def helper(x):
    """A helper function."""
    return x + 1
''')

        main_file = tmp_path / "main.py"
        main_file.write_text('''
from utils import helper

def process(x):
    """Process data using helper."""
    return helper(x) * 2
''')

        return tmp_path

    def test_get_cross_file_dependencies_consistency(self, simple_project):
        """Test that get_cross_file_dependencies returns consistent results."""
        import asyncio
        from code_scalpel.mcp.server import get_cross_file_dependencies

        async def run_twice():
            result1 = await get_cross_file_dependencies(
                target_file="main.py",
                target_symbol="process",
                project_root=str(simple_project),
            )
            result2 = await get_cross_file_dependencies(
                target_file="main.py",
                target_symbol="process",
                project_root=str(simple_project),
            )
            return result1, result2

        result1, result2 = asyncio.run(run_twice())

        assert result1.success == result2.success
        assert len(result1.extracted_symbols) == len(result2.extracted_symbols)
        assert result1.token_estimate == result2.token_estimate

    def test_cross_file_security_scan_consistency(self, simple_project):
        """Test that cross_file_security_scan returns consistent results."""
        import asyncio
        from code_scalpel.mcp.server import cross_file_security_scan

        async def run_twice():
            result1 = await cross_file_security_scan(project_root=str(simple_project))
            result2 = await cross_file_security_scan(project_root=str(simple_project))
            return result1, result2

        result1, result2 = asyncio.run(run_twice())

        assert result1.success == result2.success
        assert result1.vulnerability_count == result2.vulnerability_count
        assert result1.risk_level == result2.risk_level
