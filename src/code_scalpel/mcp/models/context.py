"""Unified context models for tool inputs.

This module provides the core context objects that normalize tool inputs
and serve as the single source of truth for file and project information.

Key classes:
- SourceContext: Represents a single source file with AST caching
- ProjectContext: Represents a project directory for multi-file analysis
- BaseContext: Abstract base for all context types
"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Language(str, Enum):
    """Supported programming languages with tier-1 AST support."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    TERRAFORM = "terraform"
    YAML = "yaml"
    JSON = "json"
    UNKNOWN = "unknown"


class BaseContext(BaseModel):
    """Abstract base context for all analysis operations."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    """Timestamp when this context was created."""

    class Config:
        arbitrary_types_allowed = True


class SourceContext(BaseContext):
    """Unified representation of a single source file with provenance.

    This is the core normalization object that tools receive after
    the @normalize_input decorator processes raw inputs.

    Key features:
    - Accepts either code string or file path, but not both (enforced via validator)
    - Caches the parsed AST to prevent double-parsing
    - Stores language metadata (detected or specified)
    - Computes deterministic hash for change tracking
    - Normalizes line endings to \n for consistent hashing
    - Tracks provenance (file path or in-memory origin)
    """

    content: str = Field(..., description="Normalized source code (\\r\\n → \\n)")

    file_path: Optional[str] = Field(
        default=None,
        description="Absolute file path, or None if in-memory code",
    )

    is_memory: bool = Field(
        default=False,
        description="True if content is in-memory (not from a file)",
    )

    language: Language = Field(
        Language.UNKNOWN,
        description="Programming language of the source. Auto-detected if UNKNOWN.",
    )

    metadata: dict = Field(
        default_factory=dict,
        description="Audit traces, git hashes, provenance information",
    )

    ast_cache: Optional[Any] = Field(
        default=None,
        description="Cached AST object (Any type to support multiple AST formats). "
        "Set by validator during preprocessing.",
        exclude=True,  # Don't serialize AST to avoid circular refs
    )

    content_hash: str = Field(
        default="",
        description="SHA256 hash of normalized content. Computed deterministically for change detection.",
    )

    file_size_bytes: int = Field(
        default=0, description="Size of source content in bytes (after UTF-8 encoding)."
    )

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        """Ensure content is not empty."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v

    @field_validator("file_size_bytes", mode="before")
    @classmethod
    def compute_file_size(cls, v: int, info) -> int:
        """Auto-compute file size from content if not provided."""
        if v == 0 and "content" in info.data:
            return len(info.data["content"].encode("utf-8"))
        return v

    @model_validator(mode="after")
    def validate_memory_constraint(self) -> SourceContext:
        """Enforce: if file_path is None, is_memory must be True (and vice versa).

        This ensures exactly one of (file_path, is_memory) is set.
        """
        if self.file_path is None and not self.is_memory:
            raise ValueError("If file_path is None, is_memory must be True")
        if self.file_path is not None and self.is_memory:
            raise ValueError("Cannot have both file_path and is_memory=True")
        return self

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization: normalize line endings and compute hash.

        Called by Pydantic v2 after model validation.
        """
        # 1. Normalize line endings (\\r\\n -> \\n)
        if "\r\n" in self.content:
            self.content = self.content.replace("\r\n", "\n")

        # 2. Compute deterministic hash
        if not self.content_hash:
            self.content_hash = self.compute_hash()

        # 3. Ensure file_size_bytes is accurate
        if self.file_size_bytes == 0:
            self.file_size_bytes = len(self.content.encode("utf-8"))

    def compute_hash(self) -> str:
        """Compute SHA256 hash of normalized content for change detection.

        Returns:
            Hex-encoded SHA256 hash of the content.
        """
        hash_obj = hashlib.sha256(self.content.encode("utf-8"))
        return hash_obj.hexdigest()

    def has_content_changed(self, previous_hash: str) -> bool:
        """Check if content has changed since a previous hash.

        Args:
            previous_hash: SHA256 hash from a previous parse.

        Returns:
            True if content has changed, False otherwise.
        """
        return self.compute_hash() != previous_hash

    def get_origin_description(self) -> str:
        """Get human-readable description of content origin.

        Returns:
            Either the file path or "memory" string.
        """
        return self.file_path if self.file_path else "memory"


class ProjectContext(BaseContext):
    """Unified representation of a project directory.

    Used by tools that operate on multiple files (crawl, map, graph).

    Key features:
    - Specifies root directory to scan
    - Applies tier-aware limits (max files, max depth)
    - Optionally filters to specific file patterns
    - Tracks which files have been scanned
    """

    root_path: str = Field(
        ..., description="Root directory path (absolute or relative to cwd)"
    )

    max_files: int = Field(
        default=100,
        description="Maximum number of files to scan (tier-dependent, overridable)",
    )

    max_depth: int = Field(
        default=5,
        description="Maximum directory depth to traverse (tier-dependent, overridable)",
    )

    include_patterns: list[str] = Field(
        default_factory=lambda: ["*.py", "*.js", "*.ts", "*.go", "*.rs"],
        description="Glob patterns for files to include (default: common source files)",
    )

    exclude_patterns: list[str] = Field(
        default_factory=lambda: [
            ".git",
            ".venv",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            "build",
            "dist",
        ],
        description="Directory patterns to exclude",
    )

    scanned_files: list[str] = Field(
        default_factory=list,
        description="List of files already scanned in this session (for incremental analysis)",
    )

    @field_validator("root_path")
    @classmethod
    def validate_root_exists(cls, v: str) -> str:
        """Ensure root directory exists (at validation time)."""
        if not os.path.isdir(v):
            raise ValueError(f"Project root does not exist: {v}")
        return v

    def add_scanned_file(self, file_path: str) -> None:
        """Track a file that has been scanned.

        Args:
            file_path: Absolute or relative path to scanned file.
        """
        if file_path not in self.scanned_files:
            self.scanned_files.append(file_path)

    def get_remaining_files(self, total_files: int) -> int:
        """Calculate how many more files can be scanned given the limit.

        Args:
            total_files: Total number of files discovered so far.

        Returns:
            Number of files remaining before hitting max_files limit.
        """
        return max(0, self.max_files - total_files)


class FileMetadata(BaseModel):
    """Metadata about a file (lightweight, no content)."""

    path: str = Field(..., description="Absolute or relative file path")
    language: Language = Field(
        default=Language.UNKNOWN, description="Detected language"
    )
    size_bytes: int = Field(default=0, description="File size in bytes")
    line_count: int = Field(default=0, description="Number of lines")
    hash: Optional[str] = Field(default=None, description="SHA256 hash of content")
    last_modified: Optional[datetime] = Field(
        default=None, description="Last modified time"
    )


__all__ = [
    "Language",
    "BaseContext",
    "SourceContext",
    "ProjectContext",
    "FileMetadata",
]
