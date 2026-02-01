"""
Tests for Project Awareness Engine (ProjectWalker and ProjectContext).

Tests cover:
- File discovery and filtering
- Directory classification
- File importance scoring
- Language detection
- Cache functionality
- Performance and scaling
"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from code_scalpel.analysis.project_walker import (
    ALL_SUPPORTED_EXTENSIONS,
    CSHARP_EXTENSIONS,
    CPP_EXTENSIONS,
    GO_EXTENSIONS,
    JAVA_EXTENSIONS,
    JAVASCRIPT_EXTENSIONS,
    PYTHON_EXTENSIONS,
    RUBY_EXTENSIONS,
    RUST_EXTENSIONS,
    TYPESCRIPT_EXTENSIONS,
    FileInfo,
    ProjectWalker,
)
from code_scalpel.analysis.project_context import (
    ProjectContext,
)


@pytest.fixture
def temp_project() -> Generator[Path, None, None]:
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create source structure
        src = root / "src"
        src.mkdir()
        (src / "main.py").write_text("def hello(): pass\n")
        (src / "utils.py").write_text("def util(): pass\n")

        # Create test structure
        tests = root / "tests"
        tests.mkdir()
        (tests / "test_main.py").write_text("def test_hello(): pass\n")

        # Create excluded directories
        (root / "node_modules").mkdir()
        (root / "node_modules" / "package.json").write_text("{}")

        (root / ".venv").mkdir()
        (root / ".venv" / "pyvenv.cfg").write_text("")

        # Create config files
        (root / "setup.py").write_text("from setuptools import setup\n")
        (root / "requirements.txt").write_text("pytest>=7.0\n")
        (root / ".gitignore").write_text("*.pyc\n__pycache__/\n")

        # Create multi-language files
        js_dir = root / "frontend"
        js_dir.mkdir()
        (js_dir / "app.js").write_text("console.log('hello');\n")
        (js_dir / "app.ts").write_text("const x: string = 'hello';\n")

        java_dir = root / "backend"
        java_dir.mkdir()
        (java_dir / "Main.java").write_text("public class Main {}\n")

        yield root


class TestProjectWalker:
    """Tests for ProjectWalker file discovery."""

    def test_walker_init_invalid_path(self):
        """Test that ProjectWalker raises on invalid path."""
        with pytest.raises(ValueError):
            ProjectWalker("/nonexistent/path")

    def test_walker_init_file_path(self, temp_project):
        """Test that ProjectWalker raises on file path."""
        file_path = temp_project / "src" / "main.py"
        with pytest.raises(ValueError):
            ProjectWalker(file_path)

    def test_walker_basic_discovery(self, temp_project):
        """Test basic file discovery."""
        walker = ProjectWalker(temp_project)
        files = list(walker.get_files())

        assert len(files) > 0
        # Should find Python, JS, TS, Java files
        assert any(f.language == "python" for f in files)
        assert any(f.language == "javascript" for f in files)
        assert any(f.language == "typescript" for f in files)
        assert any(f.language == "java" for f in files)

    def test_walker_exclude_dirs(self, temp_project):
        """Test that excluded directories are skipped."""
        walker = ProjectWalker(temp_project)
        files = list(walker.get_files())

        # Should not find files in excluded directories
        paths = [f.rel_path for f in files]
        assert not any("node_modules" in p for p in paths)
        assert not any(".venv" in p for p in paths)

    def test_walker_custom_exclude_dirs(self, temp_project):
        """Test custom exclusion patterns."""
        custom_exclude = frozenset({"tests"})
        walker = ProjectWalker(temp_project, exclude_dirs=custom_exclude)
        files = list(walker.get_files())

        paths = [f.rel_path for f in files]
        assert not any("test" in p for p in paths)
        assert any("src" in p for p in paths)

    def test_walker_max_depth(self, temp_project):
        """Test max_depth limiting."""
        # Create deeper structure
        deep = temp_project / "a" / "b" / "c" / "d"
        deep.mkdir(parents=True)
        (deep / "deep.py").write_text("pass")

        walker = ProjectWalker(temp_project, max_depth=2)
        files = list(walker.get_files())

        # Should not find deeply nested file
        paths = [f.rel_path for f in files]
        assert not any("a/b/c/d" in p for p in paths)

    def test_walker_max_files(self, temp_project):
        """Test max_files limiting."""
        walker = ProjectWalker(temp_project, max_files=5)
        files = list(walker.get_files())

        assert len(files) <= 5

    def test_walker_python_files_only(self, temp_project):
        """Test filtering for Python files only."""
        walker = ProjectWalker(temp_project)
        py_files = list(walker.get_python_files())

        assert len(py_files) > 0
        assert all(f.language == "python" for f in py_files)

    def test_walker_code_files_only(self, temp_project):
        """Test filtering for code files only."""
        walker = ProjectWalker(temp_project)
        code_files = list(walker.get_code_files())

        # All code files should have supported language
        assert all(f.language != "unknown" for f in code_files)

    def test_walker_language_specific(self, temp_project):
        """Test filtering by specific language."""
        walker = ProjectWalker(temp_project)

        js_files = list(walker.get_files_by_language("javascript"))
        assert all(f.language == "javascript" for f in js_files)
        assert len(js_files) > 0

        py_files = list(walker.get_files_by_language("python"))
        assert all(f.language == "python" for f in py_files)
        assert len(py_files) > 0

    def test_walker_file_info_properties(self, temp_project):
        """Test FileInfo properties."""
        walker = ProjectWalker(temp_project)
        files = list(walker.get_python_files())

        assert len(files) > 0
        file_info = files[0]

        assert isinstance(file_info.path, str)
        assert isinstance(file_info.rel_path, str)
        assert file_info.size > 0
        assert file_info.extension == ".py"
        assert file_info.language == "python"
        assert file_info.is_code_file()
        assert file_info.name.endswith(".py")

    def test_walker_project_map(self, temp_project):
        """Test creating a complete project map."""
        walker = ProjectWalker(temp_project)
        project_map = walker.create_project_map()

        assert project_map.total_files > 0
        assert project_map.total_dirs > 0
        assert project_map.total_size > 0
        assert len(project_map.files) > 0
        assert len(project_map.directories) > 0
        assert len(project_map.language_breakdown) > 0

        # Check language breakdown
        assert "python" in project_map.language_breakdown
        assert "javascript" in project_map.language_breakdown

    def test_walker_directories(self, temp_project):
        """Test directory discovery."""
        walker = ProjectWalker(temp_project)
        dirs = list(walker.get_directories())

        assert len(dirs) > 0
        assert any("src" in d.rel_path for d in dirs)
        assert any("tests" in d.rel_path for d in dirs)

    def test_walker_symlink_detection(self, temp_project):
        """Test symlink detection and cycle prevention."""
        # Create a symlink
        link_path = temp_project / "link_to_src"
        try:
            link_path.symlink_to(temp_project / "src")
        except (OSError, NotImplementedError):
            # Symlinks might not be supported on all systems
            pytest.skip("Symlinks not supported")

        # Without following symlinks
        walker = ProjectWalker(temp_project, follow_symlinks=False)
        files = list(walker.get_files())
        # Should not follow into symlink
        assert len(files) > 0

        # With following (should detect cycles)
        walker = ProjectWalker(temp_project, follow_symlinks=True)
        # Should handle cycles gracefully
        walker.create_project_map()


class TestDirectoryClassification:
    """Tests for directory type classification."""

    def test_detect_source_directory(self):
        """Test classification of source directory."""
        context = ProjectContext("/tmp")
        dir_type = context._detect_directory_type("src/main")

        assert dir_type.is_source

    def test_detect_test_directory(self):
        """Test classification of test directory."""
        context = ProjectContext("/tmp")
        dir_type = context._detect_directory_type("tests")

        assert dir_type.is_test
        assert dir_type.primary_type == "test"

    def test_detect_build_directory(self):
        """Test classification of build directory."""
        context = ProjectContext("/tmp")
        dir_type = context._detect_directory_type("build")

        assert dir_type.is_build

    def test_detect_docs_directory(self):
        """Test classification of docs directory."""
        context = ProjectContext("/tmp")
        dir_type = context._detect_directory_type("docs")

        assert dir_type.is_docs

    def test_detect_vendor_directory(self):
        """Test classification of vendor directory."""
        context = ProjectContext("/tmp")
        dir_type = context._detect_directory_type("node_modules/package")

        assert dir_type.is_vendor

    def test_detect_config_directory(self):
        """Test classification of config directory."""
        context = ProjectContext("/tmp")
        dir_type = context._detect_directory_type(".github")

        assert dir_type.is_config


class TestFileImportanceScoring:
    """Tests for file importance scoring."""

    def test_score_root_file_higher(self):
        """Test that root-level files get higher scores."""
        context = ProjectContext("/tmp")

        # Root file
        root_file = FileInfo(
            path="/tmp/config.json",
            rel_path="config.json",
            size=100,
            extension=".json",
            language="unknown",
            depth=0,
        )

        # Nested file
        nested_file = FileInfo(
            path="/tmp/a/b/c/data.json",
            rel_path="a/b/c/data.json",
            size=100,
            extension=".json",
            language="unknown",
            depth=3,
        )

        root_score = context._score_file_importance(root_file)
        nested_score = context._score_file_importance(nested_file)

        assert root_score > nested_score

    def test_score_code_files_higher(self):
        """Test that code files get higher scores."""
        context = ProjectContext("/tmp")

        code_file = FileInfo(
            path="/tmp/main.py",
            rel_path="main.py",
            size=1000,
            extension=".py",
            language="python",
            depth=0,
        )

        data_file = FileInfo(
            path="/tmp/data.json",
            rel_path="data.json",
            size=1000,
            extension=".json",
            language="unknown",
            depth=0,
        )

        code_score = context._score_file_importance(code_file)
        data_score = context._score_file_importance(data_file)

        assert code_score > data_score

    def test_score_config_files_important(self):
        """Test that config files are important."""
        context = ProjectContext("/tmp")

        config_file = FileInfo(
            path="/tmp/setup.py",
            rel_path="setup.py",
            size=500,
            extension=".py",
            language="python",
            depth=0,
        )

        regular_file = FileInfo(
            path="/tmp/utils.py",
            rel_path="utils.py",
            size=500,
            extension=".py",
            language="python",
            depth=0,
        )

        config_score = context._score_file_importance(config_file)
        regular_score = context._score_file_importance(regular_file)

        assert config_score > regular_score

    def test_score_large_files_penalized(self):
        """Test that very large files are penalized."""
        context = ProjectContext("/tmp")

        small_file = FileInfo(
            path="/tmp/small.py",
            rel_path="small.py",
            size=1000,
            extension=".py",
            language="python",
            depth=0,
        )

        large_file = FileInfo(
            path="/tmp/large.py",
            rel_path="large.py",
            size=50_000_000,  # 50MB
            extension=".py",
            language="python",
            depth=0,
        )

        small_score = context._score_file_importance(small_file)
        large_score = context._score_file_importance(large_file)

        assert small_score > large_score


class TestProjectContext:
    """Tests for ProjectContext functionality."""

    def test_context_load_or_create(self, temp_project):
        """Test loading or creating a project context."""
        with ProjectContext(temp_project) as context:
            walker = ProjectWalker(temp_project)
            project_map = context.load_or_create(walker)

            assert project_map.total_files > 0
            assert context.is_cache_fresh()

    def test_context_directory_classification(self, temp_project):
        """Test directory type classification in context."""
        with ProjectContext(temp_project) as context:
            walker = ProjectWalker(temp_project)
            context.load_or_create(walker)

            project_map = context.get_project_map()
            assert project_map is not None
            # Check that directories are classified
            for dir_info in project_map.directories:
                dir_type = context.get_directory_type(dir_info.path)
                assert dir_type is not None

    def test_context_file_importance_scores(self, temp_project):
        """Test that files have importance scores."""
        with ProjectContext(temp_project) as context:
            walker = ProjectWalker(temp_project)
            context.load_or_create(walker)

            project_map = context.get_project_map()
            assert project_map is not None
            for file_info in project_map.files:
                score = context.get_file_importance(file_info.path)
                assert 0.0 <= score <= 1.0

    def test_context_important_files(self, temp_project):
        """Test filtering for important files."""
        with ProjectContext(temp_project) as context:
            walker = ProjectWalker(temp_project)
            context.load_or_create(walker)

            important_files = context.get_important_files(min_score=0.7)
            assert len(important_files) > 0
            assert all(
                context.get_file_importance(f.path) >= 0.7 for f in important_files
            )

    def test_context_directories_by_type(self, temp_project):
        """Test filtering directories by type."""
        with ProjectContext(temp_project) as context:
            walker = ProjectWalker(temp_project)
            context.load_or_create(walker)

            test_dirs = context.get_directories_by_type("test")
            # Should find test directories
            assert any("tests" in d.rel_path for d in test_dirs)

    def test_context_clear_cache(self, temp_project):
        """Test cache clearing."""
        with ProjectContext(temp_project) as context:
            walker = ProjectWalker(temp_project)
            context.load_or_create(walker)
            assert context.is_cache_fresh()

            context.clear_cache()
            assert not context.is_cache_fresh()


class TestLanguageDetection:
    """Tests for language detection."""

    def test_python_detection(self):
        """Test Python file detection."""
        walker = ProjectWalker("/tmp")

        for ext in PYTHON_EXTENSIONS:
            file_info = FileInfo(
                path=f"/tmp/file{ext}",
                rel_path=f"file{ext}",
                size=100,
                extension=ext,
                language=walker._get_language(ext),
                depth=0,
            )
            assert file_info.language == "python"

    def test_javascript_detection(self):
        """Test JavaScript file detection."""
        walker = ProjectWalker("/tmp")

        for ext in JAVASCRIPT_EXTENSIONS:
            lang = walker._get_language(ext)
            assert lang == "javascript"

    def test_typescript_detection(self):
        """Test TypeScript file detection."""
        walker = ProjectWalker("/tmp")

        for ext in TYPESCRIPT_EXTENSIONS:
            lang = walker._get_language(ext)
            assert lang == "typescript"

    def test_java_detection(self):
        """Test Java file detection."""
        walker = ProjectWalker("/tmp")

        for ext in JAVA_EXTENSIONS:
            lang = walker._get_language(ext)
            assert lang == "java"

    def test_cpp_detection(self):
        """Test C++ file detection."""
        walker = ProjectWalker("/tmp")

        for ext in CPP_EXTENSIONS:
            lang = walker._get_language(ext)
            assert lang == "cpp"

    def test_all_supported_languages(self):
        """Test that all supported extensions are detected."""
        walker = ProjectWalker("/tmp")

        for ext in ALL_SUPPORTED_EXTENSIONS:
            lang = walker._get_language(ext)
            assert lang != "unknown"


class TestExtensionsAndLanguages:
    """Tests for language extension constants."""

    def test_no_extension_overlap(self):
        """Test that language extensions don't overlap."""
        all_extensions = [
            PYTHON_EXTENSIONS,
            JAVASCRIPT_EXTENSIONS,
            TYPESCRIPT_EXTENSIONS,
            JAVA_EXTENSIONS,
            CPP_EXTENSIONS,
            CSHARP_EXTENSIONS,
            RUBY_EXTENSIONS,
            GO_EXTENSIONS,
            RUST_EXTENSIONS,
        ]

        checked = set()
        for ext_set in all_extensions:
            overlap = checked & ext_set
            assert not overlap, f"Extension overlap: {overlap}"
            checked |= ext_set

    def test_all_extensions_in_supported(self):
        """Test that all language extensions are in ALL_SUPPORTED_EXTENSIONS."""
        assert PYTHON_EXTENSIONS.issubset(ALL_SUPPORTED_EXTENSIONS)
        assert JAVASCRIPT_EXTENSIONS.issubset(ALL_SUPPORTED_EXTENSIONS)
        assert JAVA_EXTENSIONS.issubset(ALL_SUPPORTED_EXTENSIONS)


@pytest.mark.performance
class TestPerformance:
    """Performance tests for Project Awareness Engine."""

    def test_walker_performance_on_large_structure(self, temp_project):
        """Test walker performance on moderately large structure."""
        # Create 100 files
        for i in range(10):
            subdir = temp_project / f"subdir_{i}"
            subdir.mkdir(exist_ok=True)
            for j in range(10):
                (subdir / f"file_{j}.py").write_text("pass\n")

        walker = ProjectWalker(temp_project)
        import time

        start = time.time()
        files = list(walker.get_files())
        elapsed = time.time() - start

        assert len(files) >= 100
        assert elapsed < 5.0  # Should be reasonably fast


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
