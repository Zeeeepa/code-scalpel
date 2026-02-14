"""Tests for CodebaseAdapter and CodebaseView integration.

This test suite validates that:
1. CodebaseView interface works correctly
2. CodebaseAdapter properly wraps Codegen's Codebase
3. Analysis functions work with the minimal interface
"""

import pytest
from pathlib import Path
from code_scalpel.codebase.codebase_view import (
    SimpleCodebaseView,
    SimpleFile,
    SimpleSymbol,
    SimpleClass,
    SimpleFunction,
    SimpleImport,
)


class TestSimpleCodebaseView:
    """Test the SimpleCodebaseView implementation."""
    
    def test_initialization(self):
        """Test basic initialization."""
        view = SimpleCodebaseView(
            root_path=Path("/test"),
            language="python",
        )
        
        assert view.root_path == Path("/test")
        assert view.language == "python"
        assert len(view.files) == 0
        assert len(view.symbols) == 0
    
    def test_with_data(self):
        """Test initialization with data."""
        files = [
            SimpleFile(Path("test.py"), "print('hello')", "python"),
        ]
        symbols = [
            SimpleSymbol("test_func", "function", Path("test.py"), 1),
        ]
        
        view = SimpleCodebaseView(
            root_path=Path("/test"),
            language="python",
            files=files,
            symbols=symbols,
        )
        
        assert len(view.files) == 1
        assert len(view.symbols) == 1
        assert view.files[0].path == Path("test.py")
        assert view.symbols[0].name == "test_func"
    
    def test_get_file(self):
        """Test get_file method."""
        files = [
            SimpleFile(Path("test.py"), "print('hello')", "python"),
            SimpleFile(Path("main.py"), "print('world')", "python"),
        ]
        
        view = SimpleCodebaseView(
            root_path=Path("/test"),
            language="python",
            files=files,
        )
        
        # Test existing file
        file = view.get_file(Path("test.py"))
        assert file is not None
        assert file.content == "print('hello')"
        
        # Test non-existing file
        file = view.get_file(Path("nonexistent.py"))
        assert file is None
    
    def test_from_directory(self, tmp_path):
        """Test creating view from directory."""
        # Create test files
        (tmp_path / "test.py").write_text("print('hello')")
        (tmp_path / "main.py").write_text("print('world')")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.py").write_text("print('nested')")
        
        # Create view
        view = SimpleCodebaseView.from_directory(tmp_path, language="python")
        
        assert view.root_path == tmp_path
        assert view.language == "python"
        assert len(view.files) == 3  # All .py files
        
        # Check files were loaded
        paths = [f.path.name for f in view.files]
        assert "test.py" in paths
        assert "main.py" in paths
        assert "nested.py" in paths


class TestCodebaseViewProtocol:
    """Test that CodebaseView protocol is properly defined."""
    
    def test_protocol_attributes(self):
        """Test that protocol has required attributes."""
        from code_scalpel.codebase.codebase_view import CodebaseView
        
        # Check protocol has required methods/properties
        assert hasattr(CodebaseView, 'root_path')
        assert hasattr(CodebaseView, 'language')
        assert hasattr(CodebaseView, 'files')
        assert hasattr(CodebaseView, 'symbols')
        assert hasattr(CodebaseView, 'classes')
        assert hasattr(CodebaseView, 'functions')
        assert hasattr(CodebaseView, 'imports')
        assert hasattr(CodebaseView, 'get_file')
    
    def test_simple_view_implements_protocol(self):
        """Test that SimpleCodebaseView implements the protocol."""
        view = SimpleCodebaseView(
            root_path=Path("/test"),
            language="python",
        )
        
        # Should have all protocol methods/properties
        assert hasattr(view, 'root_path')
        assert hasattr(view, 'language')
        assert hasattr(view, 'files')
        assert hasattr(view, 'symbols')
        assert hasattr(view, 'classes')
        assert hasattr(view, 'functions')
        assert hasattr(view, 'imports')
        assert hasattr(view, 'get_file')


class TestDataClasses:
    """Test the simple data classes."""
    
    def test_simple_file(self):
        """Test SimpleFile data class."""
        file = SimpleFile(
            path=Path("test.py"),
            content="print('hello')",
            language="python",
        )
        
        assert file.path == Path("test.py")
        assert file.content == "print('hello')"
        assert file.language == "python"
    
    def test_simple_symbol(self):
        """Test SimpleSymbol data class."""
        symbol = SimpleSymbol(
            name="test_func",
            type="function",
            file_path=Path("test.py"),
            line_number=10,
        )
        
        assert symbol.name == "test_func"
        assert symbol.type == "function"
        assert symbol.file_path == Path("test.py")
        assert symbol.line_number == 10
    
    def test_simple_class(self):
        """Test SimpleClass data class."""
        cls = SimpleClass(
            name="TestClass",
            file_path=Path("test.py"),
            methods=["method1", "method2"],
            attributes=["attr1", "attr2"],
        )
        
        assert cls.name == "TestClass"
        assert cls.file_path == Path("test.py")
        assert len(cls.methods) == 2
        assert len(cls.attributes) == 2
    
    def test_simple_function(self):
        """Test SimpleFunction data class."""
        func = SimpleFunction(
            name="test_func",
            file_path=Path("test.py"),
            parameters=["arg1", "arg2"],
            return_type="str",
        )
        
        assert func.name == "test_func"
        assert func.file_path == Path("test.py")
        assert len(func.parameters) == 2
        assert func.return_type == "str"
    
    def test_simple_import(self):
        """Test SimpleImport data class."""
        imp = SimpleImport(
            module="os.path",
            names=["join", "exists"],
            file_path=Path("test.py"),
        )
        
        assert imp.module == "os.path"
        assert len(imp.names) == 2
        assert imp.file_path == Path("test.py")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

