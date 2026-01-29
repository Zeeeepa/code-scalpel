"""
ProjectWalker - Smart file discovery engine for large codebases.

ProjectWalker provides intelligent directory traversal with:
- Symlink loop detection and cycle prevention
- Max depth and max files limiting
- Configurable exclusion patterns
- Optional .gitignore respect
- Fast iteration without context overhead
- File type filtering and classification

This module enables efficient project map generation and discovery
without the overhead of full AST analysis (which is handled by ProjectCrawler).
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator

# Default directories to exclude from walking
DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        # Version control
        ".git",
        ".hg",
        ".svn",
        # Virtual environments
        "venv",
        ".venv",
        "env",
        ".env",
        # Python caches
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        # JavaScript
        "node_modules",
        # Build artifacts
        "dist",
        "build",
        "egg-info",
        ".egg-info",
        # Test automation
        ".tox",
        ".nox",
        # Coverage reports
        "htmlcov",
        # Installed packages
        "site-packages",
    }
)

# Common file extensions by language
PYTHON_EXTENSIONS = frozenset({".py", ".pyx", ".pyi"})
JAVASCRIPT_EXTENSIONS = frozenset({".js", ".jsx", ".mjs"})
TYPESCRIPT_EXTENSIONS = frozenset({".ts", ".tsx"})
JAVA_EXTENSIONS = frozenset({".java"})
CPP_EXTENSIONS = frozenset({".cpp", ".cc", ".cxx", ".h", ".hpp"})
CSHARP_EXTENSIONS = frozenset({".cs"})
RUBY_EXTENSIONS = frozenset({".rb"})
GO_EXTENSIONS = frozenset({".go"})
RUST_EXTENSIONS = frozenset({".rs"})

# All supported extensions
ALL_SUPPORTED_EXTENSIONS = (
    PYTHON_EXTENSIONS
    | JAVASCRIPT_EXTENSIONS
    | TYPESCRIPT_EXTENSIONS
    | JAVA_EXTENSIONS
    | CPP_EXTENSIONS
    | CSHARP_EXTENSIONS
    | RUBY_EXTENSIONS
    | GO_EXTENSIONS
    | RUST_EXTENSIONS
)


@dataclass
class FileInfo:
    """Information about a discovered file."""

    path: str  # Absolute path
    rel_path: str  # Path relative to root
    size: int  # File size in bytes
    extension: str  # File extension (e.g., ".py")
    language: str  # Detected language (e.g., "python")
    is_symlink: bool = False  # Whether this is a symlink
    depth: int = 0  # Depth from root (0 = root level)

    @property
    def name(self) -> str:
        """Get the filename."""
        return Path(self.path).name

    def is_code_file(self) -> bool:
        """Check if this is a supported code file."""
        return self.extension.lower() in ALL_SUPPORTED_EXTENSIONS


@dataclass
class DirectoryInfo:
    """Information about a discovered directory."""

    path: str  # Absolute path
    rel_path: str  # Path relative to root
    is_symlink: bool = False  # Whether this is a symlink
    depth: int = 0  # Depth from root
    file_count: int = 0  # Number of files in this directory (non-recursive)

    @property
    def name(self) -> str:
        """Get the directory name."""
        return Path(self.path).name


@dataclass
class ProjectMap:
    """Complete map of a project's file structure."""

    root_path: str
    total_files: int = 0
    total_dirs: int = 0
    total_size: int = 0
    files: list[FileInfo] = field(default_factory=list)
    directories: list[DirectoryInfo] = field(default_factory=list)
    language_breakdown: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    cycles_detected: list[str] = field(default_factory=list)

    @property
    def code_files_count(self) -> int:
        """Count of supported code files."""
        return sum(1 for f in self.files if f.is_code_file())

    def get_files_by_language(self, language: str) -> list[FileInfo]:
        """Get all files for a specific language."""
        return [f for f in self.files if f.language == language]

    def get_files_by_extension(self, extension: str) -> list[FileInfo]:
        """Get all files with a specific extension."""
        ext_lower = extension.lower() if not extension.startswith(".") else extension.lower()
        return [f for f in self.files if f.extension.lower() == ext_lower]


class ProjectWalker:
    """
    Smart file discovery engine for large codebases.

    Features:
    - Fast directory traversal without full file analysis
    - Symlink cycle detection and prevention
    - Configurable depth and file limits
    - Optional .gitignore support
    - Language detection and file classification
    """

    def __init__(
        self,
        root_path: str | Path,
        exclude_dirs: frozenset[str] | None = None,
        max_depth: int | None = None,
        max_files: int | None = None,
        respect_gitignore: bool = False,
        follow_symlinks: bool = False,
    ):
        """
        Initialize ProjectWalker.

        Args:
            root_path: Root directory to walk
            exclude_dirs: Set of directory names to exclude (default: DEFAULT_EXCLUDE_DIRS)
            max_depth: Maximum directory depth to traverse (None = unlimited)
            max_files: Maximum number of files to discover (None = unlimited)
            respect_gitignore: Whether to respect .gitignore patterns
            follow_symlinks: Whether to follow symlinks (with cycle detection)

        Raises:
            ValueError: If root_path doesn't exist
        """
        self.root_path = Path(root_path).resolve()
        if not self.root_path.exists():
            raise ValueError(f"Root path does not exist: {root_path}")
        if not self.root_path.is_dir():
            raise ValueError(f"Root path is not a directory: {root_path}")

        self.exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
        self.max_depth = max_depth
        self.max_files = max_files
        self.respect_gitignore = respect_gitignore
        self.follow_symlinks = follow_symlinks

        # Track visited inodes to detect cycles (for symlinks)
        self._visited_inodes: set[int] = set()
        self._cycles_detected: list[str] = []

        # Gitignore patterns cache (if enabled)
        self._gitignore_patterns: dict[Path, list[str]] = {}

    def _get_language(self, extension: str) -> str:
        """Detect language from file extension."""
        ext_lower = extension.lower()
        if ext_lower in PYTHON_EXTENSIONS:
            return "python"
        elif ext_lower in JAVASCRIPT_EXTENSIONS:
            return "javascript"
        elif ext_lower in TYPESCRIPT_EXTENSIONS:
            return "typescript"
        elif ext_lower in JAVA_EXTENSIONS:
            return "java"
        elif ext_lower in CPP_EXTENSIONS:
            return "cpp"
        elif ext_lower in CSHARP_EXTENSIONS:
            return "csharp"
        elif ext_lower in RUBY_EXTENSIONS:
            return "ruby"
        elif ext_lower in GO_EXTENSIONS:
            return "go"
        elif ext_lower in RUST_EXTENSIONS:
            return "rust"
        else:
            return "unknown"

    def _load_gitignore(self, directory: Path) -> list[str]:
        """Load .gitignore patterns from a directory."""
        if directory in self._gitignore_patterns:
            return self._gitignore_patterns[directory]

        patterns = []
        gitignore_path = directory / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.rstrip("\n\r")
                        # Skip empty lines and comments
                        if not line or line.startswith("#"):
                            continue
                        patterns.append(line)
            except (OSError, UnicodeDecodeError):
                pass

        self._gitignore_patterns[directory] = patterns
        return patterns

    def _is_gitignored(self, rel_path: Path, is_dir: bool = False) -> bool:
        """Check if a path matches .gitignore patterns."""
        if not self.respect_gitignore:
            return False

        # Simple pattern matching - not full gitignore semantics
        path_str = str(rel_path).replace("\\", "/")
        patterns = self._load_gitignore(self.root_path)

        for pattern in patterns:
            # Remove trailing slash for consistency
            pattern = pattern.rstrip("/")

            # Directory-only pattern (ended with / in .gitignore)
            if is_dir and pattern.endswith("/"):
                pattern = pattern[:-1]

            # Simple fnmatch-like matching
            if "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(path_str, pattern):
                    return True
                if fnmatch.fnmatch(Path(path_str).name, pattern):
                    return True
            else:
                # Exact match
                if path_str == pattern or Path(path_str).name == pattern:
                    return True

        return False

    def _check_cycle(self, dir_path: Path) -> bool:
        """Check for symlink cycles using inode tracking."""
        if not self.follow_symlinks:
            return False

        try:
            stat_info = os.stat(dir_path)
            inode = stat_info.st_ino
            if inode in self._visited_inodes:
                cycle_str = f"Cycle detected at: {dir_path}"
                self._cycles_detected.append(cycle_str)
                return True
            self._visited_inodes.add(inode)
            return False
        except (OSError, AttributeError):
            # AttributeError on Windows where st_ino might not exist
            return False

    def walk(self) -> Generator[tuple[str, list[str], list[str]], None, None]:
        """
        Walk the directory tree like os.walk().

        Yields:
            (root, dirs, files) tuples
        """
        for root, dirs, files in os.walk(self.root_path, followlinks=self.follow_symlinks):
            root_path = Path(root).resolve()

            # Check for cycles
            if self.follow_symlinks and self._check_cycle(root_path):
                dirs[:] = []  # Don't descend into cyclic directory
                continue

            # Calculate depth
            try:
                rel_path = root_path.relative_to(self.root_path)
                depth = len(rel_path.parts)
            except ValueError:
                rel_path = Path(".")
                depth = 0

            # Check max depth
            if self.max_depth is not None and depth >= self.max_depth:
                dirs[:] = []
                yield root, dirs, files
                continue

            # Filter directories
            filtered_dirs = []
            for d in dirs:
                if d in self.exclude_dirs:
                    continue
                rel_child = rel_path / d
                if self._is_gitignored(rel_child, is_dir=True):
                    continue
                filtered_dirs.append(d)

            dirs[:] = filtered_dirs
            yield root, dirs, files

    def get_files(self) -> Generator[FileInfo, None, None]:
        """
        Discover all files (respecting filters).

        Yields:
            FileInfo for each discovered file
        """
        count = 0
        for root, dirs, files in self.walk():
            root_path = Path(root).resolve()
            try:
                rel_dir = root_path.relative_to(self.root_path)
                depth = len(rel_dir.parts)
            except ValueError:
                depth = 0

            for filename in files:
                if self.max_files is not None and count >= self.max_files:
                    return

                file_path = root_path / filename
                try:
                    rel_path = file_path.relative_to(self.root_path)
                except ValueError:
                    continue

                if self._is_gitignored(rel_path, is_dir=False):
                    continue

                try:
                    stat_info = file_path.stat()
                    extension = file_path.suffix
                    language = self._get_language(extension)
                    is_symlink = file_path.is_symlink()

                    file_info = FileInfo(
                        path=str(file_path),
                        rel_path=str(rel_path),
                        size=stat_info.st_size,
                        extension=extension,
                        language=language,
                        is_symlink=is_symlink,
                        depth=depth,
                    )
                    yield file_info
                    count += 1
                except (OSError, ValueError):
                    # Skip files we can't stat
                    continue

    def get_code_files(self) -> Generator[FileInfo, None, None]:
        """
        Discover only code files (supported languages).

        Yields:
            FileInfo for each supported code file
        """
        for file_info in self.get_files():
            if file_info.is_code_file():
                yield file_info

    def get_python_files(self) -> Generator[FileInfo, None, None]:
        """
        Discover only Python files.

        Yields:
            FileInfo for each Python file
        """
        for file_info in self.get_files():
            if file_info.language == "python":
                yield file_info

    def get_files_by_language(self, language: str) -> Generator[FileInfo, None, None]:
        """
        Discover files for a specific language.

        Args:
            language: Language name (e.g., "python", "javascript")

        Yields:
            FileInfo for each file in the language
        """
        for file_info in self.get_files():
            if file_info.language == language:
                yield file_info

    def get_directories(self) -> Generator[DirectoryInfo, None, None]:
        """
        Discover all directories (respecting filters).

        Yields:
            DirectoryInfo for each discovered directory
        """
        visited_dirs: set[int] = set()

        for root, dirs, files in self.walk():
            root_path = Path(root).resolve()

            try:
                rel_path = root_path.relative_to(self.root_path)
                depth = len(rel_path.parts)
            except ValueError:
                depth = 0

            # Yield root directory (only once)
            try:
                stat_info = root_path.stat()
                inode = getattr(stat_info, "st_ino", id(root))
                if inode not in visited_dirs:
                    visited_dirs.add(inode)
                    try:
                        rel_root = root_path.relative_to(self.root_path)
                    except ValueError:
                        rel_root = Path(".")

                    is_symlink = root_path.is_symlink()
                    dir_info = DirectoryInfo(
                        path=str(root_path),
                        rel_path=str(rel_root),
                        is_symlink=is_symlink,
                        depth=depth,
                        file_count=len(files),
                    )
                    yield dir_info
            except (OSError, ValueError):
                pass

    def create_project_map(self) -> ProjectMap:
        """
        Create a complete project map.

        Returns:
            ProjectMap with all discovered files and directories
        """
        project_map = ProjectMap(root_path=str(self.root_path))

        # Discover files
        language_counts: dict[str, int] = {}
        for file_info in self.get_files():
            project_map.files.append(file_info)
            project_map.total_files += 1
            project_map.total_size += file_info.size

            # Track language breakdown
            lang = file_info.language
            language_counts[lang] = language_counts.get(lang, 0) + 1

        project_map.language_breakdown = language_counts

        # Discover directories
        for dir_info in self.get_directories():
            project_map.directories.append(dir_info)
            project_map.total_dirs += 1

        # Track cycles
        project_map.cycles_detected = self._cycles_detected

        return project_map

    def estimate_context_tokens(self) -> int:
        """
        Estimate total tokens needed for all discovered files.

        Uses rough estimate of ~4 characters per token.

        Returns:
            Estimated token count
        """
        return self.create_project_map().total_size // 4


__all__ = [
    "ProjectWalker",
    "FileInfo",
    "DirectoryInfo",
    "ProjectMap",
    "DEFAULT_EXCLUDE_DIRS",
    "PYTHON_EXTENSIONS",
    "JAVASCRIPT_EXTENSIONS",
    "TYPESCRIPT_EXTENSIONS",
    "JAVA_EXTENSIONS",
    "CPP_EXTENSIONS",
    "CSHARP_EXTENSIONS",
    "RUBY_EXTENSIONS",
    "GO_EXTENSIONS",
    "RUST_EXTENSIONS",
    "ALL_SUPPORTED_EXTENSIONS",
]
