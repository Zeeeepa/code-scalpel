"""
ProjectContext - Metadata storage and caching for large project analysis.

ProjectContext provides:
- In-memory caching of project structure
- Optional persistent cache (SQLite)
- Directory type detection (library, test, build, etc.)
- File importance scoring
- Fast lookups for large projects
- Change detection and invalidation
"""

import json
import sqlite3
import time
from dataclasses import dataclass
from hashlib import md5
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from .project_walker import ProjectWalker

from .project_walker import DirectoryInfo, FileInfo, ProjectMap


@dataclass
class CacheMetadata:
    """Metadata about a cached project map."""

    project_root: str
    created_at: float
    updated_at: float
    file_count: int
    dir_count: int
    total_size: int
    hash: str  # MD5 of the project structure
    language_breakdown: Dict[str, int]

    def is_fresh(self, max_age_seconds: int = 3600) -> bool:
        """Check if cache is fresh (less than max_age_seconds old)."""
        return (time.time() - self.updated_at) < max_age_seconds


@dataclass
class DirectoryType:
    """Classification of a directory."""

    is_library: bool = False  # Library/shared code
    is_test: bool = False  # Test directory
    is_build: bool = False  # Build artifacts
    is_config: bool = False  # Configuration
    is_docs: bool = False  # Documentation
    is_vendor: bool = False  # Third-party dependencies
    is_source: bool = False  # Main source code
    confidence: float = 0.0  # Confidence of classification (0.0-1.0)

    @property
    def primary_type(self) -> str:
        """Get the primary classification."""
        if self.is_vendor:
            return "vendor"
        if self.is_build:
            return "build"
        if self.is_test:
            return "test"
        if self.is_docs:
            return "docs"
        if self.is_config:
            return "config"
        if self.is_library:
            return "library"
        if self.is_source:
            return "source"
        return "unknown"


class ProjectContext:
    """
    Context manager for project analysis with caching and metadata.

    Features:
    - In-memory cache of discovered project structure
    - Directory type classification
    - File importance scoring
    - Optional persistent SQLite cache
    - Change detection via hashing
    """

    def __init__(
        self,
        root_path: str | Path,
        enable_disk_cache: bool = False,
        cache_dir: Optional[str | Path] = None,
    ):
        """
        Initialize ProjectContext.

        Args:
            root_path: Root directory of the project
            enable_disk_cache: Whether to use persistent SQLite cache
            cache_dir: Directory for cache files (default: .cache in root)
        """
        self.root_path = Path(root_path).resolve()
        self.enable_disk_cache = enable_disk_cache

        # Set up cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir).resolve()
        else:
            self.cache_dir = self.root_path / ".code-scalpel" / "cache"

        if enable_disk_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._init_cache_db()
        else:
            self._db_conn = None

        # In-memory caches
        self._project_map: Optional[ProjectMap] = None
        self._dir_types: Dict[str, DirectoryType] = {}
        self._file_scores: Dict[str, float] = {}
        self._cache_metadata: Optional[CacheMetadata] = None

    def _init_cache_db(self) -> None:
        """Initialize SQLite cache database."""
        db_path = self.cache_dir / "project_cache.db"
        self._db_conn = sqlite3.connect(str(db_path))
        cursor = self._db_conn.cursor()

        # Create tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                project_root TEXT PRIMARY KEY,
                created_at REAL,
                updated_at REAL,
                file_count INTEGER,
                dir_count INTEGER,
                total_size INTEGER,
                hash TEXT,
                language_breakdown TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                rel_path TEXT,
                size INTEGER,
                extension TEXT,
                language TEXT,
                is_symlink INTEGER,
                depth INTEGER,
                importance_score REAL,
                cached_at REAL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS directories (
                id INTEGER PRIMARY KEY,
                path TEXT UNIQUE,
                rel_path TEXT,
                is_symlink INTEGER,
                depth INTEGER,
                file_count INTEGER,
                dir_type TEXT,
                type_confidence REAL,
                cached_at REAL
            )
        """
        )

        self._db_conn.commit()

    def _detect_directory_type(self, rel_path: str) -> DirectoryType:
        """Detect the type of a directory based on its path and name."""
        path_lower = rel_path.lower()

        dir_type = DirectoryType()

        # Vendor/third-party
        if any(
            x in path_lower
            for x in ["node_modules", "vendor", "dependencies", "third-party"]
        ):
            dir_type.is_vendor = True
            dir_type.confidence = 0.95

        # Build artifacts
        elif any(x in path_lower for x in ["build", "dist", "bin", "out", "target"]):
            dir_type.is_build = True
            dir_type.confidence = 0.9

        # Tests
        elif any(x in path_lower for x in ["test", "tests", "spec", "specs"]):
            dir_type.is_test = True
            dir_type.confidence = 0.9

        # Documentation
        elif any(x in path_lower for x in ["doc", "docs", "documentation"]):
            dir_type.is_docs = True
            dir_type.confidence = 0.85

        # Configuration
        elif any(x in path_lower for x in [".config", ".github", ".gitlab", "config"]):
            dir_type.is_config = True
            dir_type.confidence = 0.85

        # Library (common patterns)
        elif any(x in path_lower for x in ["lib", "libs", "lib_scalpel"]):
            dir_type.is_library = True
            dir_type.confidence = 0.75

        # Source code (default positive indicator)
        else:
            dir_type.is_source = True
            dir_type.confidence = 0.5

        return dir_type

    def _score_file_importance(self, file_info: FileInfo) -> float:
        """
        Score a file's importance (0.0 = least important, 1.0 = most important).

        Factors:
        - Depth (root files more important)
        - Language (code more important than data)
        - Name patterns (config files important)
        - Size (very large files less important)
        """
        score = 0.5

        # Depth factor (prefer root files)
        if file_info.depth == 0:
            score += 0.2
        elif file_info.depth == 1:
            score += 0.1

        # Language importance
        if file_info.language != "unknown":
            score += 0.15

        # Configuration files
        name_lower = file_info.name.lower()
        if any(
            x in name_lower
            for x in [
                "config",
                "setup",
                "requirements",
                "package",
                "manifest",
                "makefile",
            ]
        ):
            score += 0.15

        # Entrypoint files
        if any(x in name_lower for x in ["main", "__main__", "init", "index"]):
            score += 0.1

        # Very large files are less important
        if file_info.size > 10_000_000:  # 10MB
            score -= 0.2

        return min(1.0, max(0.0, score))

    def load_or_create(
        self,
        walker: "ProjectWalker",  # type: ignore
    ) -> ProjectMap:
        """
        Load cached project map or create new one.

        Args:
            walker: ProjectWalker instance to use for discovery

        Returns:
            ProjectMap with all discovered files and directories
        """
        # Check disk cache first
        if self.enable_disk_cache:
            cached_map = self._load_from_disk()
            if cached_map is not None:
                self._project_map = cached_map
                return cached_map

        # Create new map from walker
        project_map = walker.create_project_map()
        self._project_map = project_map

        # Classify directories and score files
        for dir_info in project_map.directories:
            self._dir_types[dir_info.path] = self._detect_directory_type(
                dir_info.rel_path
            )

        for file_info in project_map.files:
            self._file_scores[file_info.path] = self._score_file_importance(file_info)

        # Create metadata
        self._cache_metadata = CacheMetadata(
            project_root=str(self.root_path),
            created_at=time.time(),
            updated_at=time.time(),
            file_count=project_map.total_files,
            dir_count=project_map.total_dirs,
            total_size=project_map.total_size,
            hash=self._hash_project(project_map),
            language_breakdown=project_map.language_breakdown,
        )

        # Cache to disk if enabled
        if self.enable_disk_cache and self._cache_metadata:
            self._save_to_disk(project_map)

        return project_map

    def _hash_project(self, project_map: ProjectMap) -> str:
        """Create a hash of the project structure for change detection."""
        hash_input = json.dumps(
            {
                "file_count": project_map.total_files,
                "dir_count": project_map.total_dirs,
                "languages": sorted(project_map.language_breakdown.items()),
            },
            sort_keys=True,
        )
        return md5(hash_input.encode(), usedforsecurity=False).hexdigest()

    def _save_to_disk(self, project_map: ProjectMap) -> None:
        """Save project map to SQLite cache."""
        if not self._db_conn or not self._cache_metadata:
            return

        cursor = self._db_conn.cursor()

        try:
            # Save metadata
            cursor.execute(
                """
                INSERT OR REPLACE INTO metadata
                (project_root, created_at, updated_at, file_count, dir_count, total_size, hash, language_breakdown)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self._cache_metadata.project_root,
                    self._cache_metadata.created_at,
                    self._cache_metadata.updated_at,
                    self._cache_metadata.file_count,
                    self._cache_metadata.dir_count,
                    self._cache_metadata.total_size,
                    self._cache_metadata.hash,
                    json.dumps(self._cache_metadata.language_breakdown),
                ),
            )

            # Save files
            current_time = time.time()
            for file_info in project_map.files:
                score = self._file_scores.get(file_info.path, 0.0)
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO files
                    (path, rel_path, size, extension, language, is_symlink, depth, importance_score, cached_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        file_info.path,
                        file_info.rel_path,
                        file_info.size,
                        file_info.extension,
                        file_info.language,
                        int(file_info.is_symlink),
                        file_info.depth,
                        score,
                        current_time,
                    ),
                )

            # Save directories
            for dir_info in project_map.directories:
                dir_type = self._dir_types.get(dir_info.path)
                type_str = dir_type.primary_type if dir_type else "unknown"
                confidence = dir_type.confidence if dir_type else 0.0

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO directories
                    (path, rel_path, is_symlink, depth, file_count, dir_type, type_confidence, cached_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        dir_info.path,
                        dir_info.rel_path,
                        int(dir_info.is_symlink),
                        dir_info.depth,
                        dir_info.file_count,
                        type_str,
                        confidence,
                        current_time,
                    ),
                )

            self._db_conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving to cache database: {e}")

    def _load_from_disk(self) -> Optional[ProjectMap]:
        """Load project map from SQLite cache if it exists and is fresh."""
        if not self._db_conn:
            return None

        cursor = self._db_conn.cursor()

        try:
            # Load metadata
            cursor.execute(
                "SELECT * FROM metadata WHERE project_root = ?", (str(self.root_path),)
            )
            row = cursor.fetchone()
            if not row:
                return None

            metadata = CacheMetadata(
                project_root=row[0],
                created_at=row[1],
                updated_at=row[2],
                file_count=row[3],
                dir_count=row[4],
                total_size=row[5],
                hash=row[6],
                language_breakdown=json.loads(row[7]),
            )

            # Check if cache is fresh
            if not metadata.is_fresh():
                return None

            self._cache_metadata = metadata

            # Load files
            # TODO: Reconstruct FileInfo objects from database
            # (Note: our schema doesn't track project_root in files)
            # For now, we'll skip loading from disk cache to keep it simple
            # In production, you'd want a proper foreign key setup
            return None

        except sqlite3.Error as e:
            print(f"Error loading from cache database: {e}")
            return None

    def get_project_map(self) -> Optional[ProjectMap]:
        """Get the cached project map (if loaded)."""
        return self._project_map

    def get_directory_type(self, dir_path: str) -> DirectoryType:
        """Get the classification of a directory."""
        return self._dir_types.get(dir_path, DirectoryType())

    def get_file_importance(self, file_path: str) -> float:
        """Get the importance score of a file."""
        return self._file_scores.get(file_path, 0.5)

    def get_important_files(self, min_score: float = 0.7) -> List[FileInfo]:
        """Get all files above a minimum importance threshold."""
        if not self._project_map:
            return []

        return [
            f
            for f in self._project_map.files
            if self._file_scores.get(f.path, 0.0) >= min_score
        ]

    def get_directories_by_type(self, dir_type: str) -> List[DirectoryInfo]:
        """Get all directories of a specific type."""
        if not self._project_map:
            return []

        results = []
        for dir_info in self._project_map.directories:
            classified = self._dir_types.get(dir_info.path)
            if classified and classified.primary_type == dir_type:
                results.append(dir_info)
        return results

    def is_cache_fresh(self) -> bool:
        """Check if in-memory cache is fresh."""
        return self._project_map is not None

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._project_map = None
        self._dir_types.clear()
        self._file_scores.clear()
        self._cache_metadata = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._db_conn:
            self._db_conn.close()


__all__ = [
    "ProjectContext",
    "CacheMetadata",
    "DirectoryType",
]
