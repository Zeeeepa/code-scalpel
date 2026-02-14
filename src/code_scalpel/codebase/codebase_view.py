"""Minimal Codebase interface for analysis functions.

This module provides a simplified view of a codebase that analysis functions
actually need, without the heavy dependencies of the full Codegen Codebase class.
"""

from pathlib import Path
from typing import Protocol, List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SimpleFile:
    """Simplified file representation."""
    path: Path
    content: str
    language: str


@dataclass
class SimpleSymbol:
    """Simplified symbol representation."""
    name: str
    type: str  # 'class', 'function', 'variable', etc.
    file_path: Path
    line_number: int


@dataclass
class SimpleClass:
    """Simplified class representation."""
    name: str
    file_path: Path
    methods: List[str]
    attributes: List[str]


@dataclass
class SimpleFunction:
    """Simplified function representation."""
    name: str
    file_path: Path
    parameters: List[str]
    return_type: Optional[str]


@dataclass
class SimpleImport:
    """Simplified import representation."""
    module: str
    names: List[str]
    file_path: Path


class CodebaseView(Protocol):
    """Minimal interface that analysis functions need.
    
    This protocol defines only the essential methods required by the
    migrated analysis functions, avoiding dependencies on git, visualization,
    and complex configuration.
    """
    
    @property
    def root_path(self) -> Path:
        """Root directory of the codebase."""
        ...
    
    @property
    def language(self) -> str:
        """Primary programming language of the codebase."""
        ...
    
    @property
    def files(self) -> List[SimpleFile]:
        """All files in the codebase."""
        ...
    
    @property
    def symbols(self) -> List[SimpleSymbol]:
        """All symbols (classes, functions, variables) in the codebase."""
        ...
    
    @property
    def classes(self) -> List[SimpleClass]:
        """All classes in the codebase."""
        ...
    
    @property
    def functions(self) -> List[SimpleFunction]:
        """All functions in the codebase."""
        ...
    
    @property
    def imports(self) -> List[SimpleImport]:
        """All imports in the codebase."""
        ...
    
    def get_file(self, path: Path) -> Optional[SimpleFile]:
        """Get a specific file by path."""
        ...


class SimpleCodebaseView:
    """Concrete implementation of CodebaseView using simple data structures.
    
    This implementation can be populated from various sources:
    - Direct file system scanning
    - Existing Code Scalpel analysis results
    - Codegen Codebase (if available)
    - MCP tool inputs
    """
    
    def __init__(
        self,
        root_path: Path,
        language: str = "python",
        files: Optional[List[SimpleFile]] = None,
        symbols: Optional[List[SimpleSymbol]] = None,
        classes: Optional[List[SimpleClass]] = None,
        functions: Optional[List[SimpleFunction]] = None,
        imports: Optional[List[SimpleImport]] = None,
    ):
        self._root_path = root_path
        self._language = language
        self._files = files or []
        self._symbols = symbols or []
        self._classes = classes or []
        self._functions = functions or []
        self._imports = imports or []
    
    @property
    def root_path(self) -> Path:
        return self._root_path
    
    @property
    def language(self) -> str:
        return self._language
    
    @property
    def files(self) -> List[SimpleFile]:
        return self._files
    
    @property
    def symbols(self) -> List[SimpleSymbol]:
        return self._symbols
    
    @property
    def classes(self) -> List[SimpleClass]:
        return self._classes
    
    @property
    def functions(self) -> List[SimpleFunction]:
        return self._functions
    
    @property
    def imports(self) -> List[SimpleImport]:
        return self._imports
    
    def get_file(self, path: Path) -> Optional[SimpleFile]:
        """Get a specific file by path."""
        for file in self._files:
            if file.path == path:
                return file
        return None
    
    @classmethod
    def from_directory(cls, root_path: Path, language: str = "python") -> "SimpleCodebaseView":
        """Create a CodebaseView by scanning a directory.
        
        This is a basic implementation that can be enhanced with proper
        AST parsing using Code Scalpel's existing tools.
        """
        files = []
        
        # Scan for Python files (can be extended for other languages)
        if language == "python":
            for py_file in root_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    files.append(SimpleFile(
                        path=py_file,
                        content=content,
                        language=language
                    ))
                except Exception:
                    pass  # Skip files that can't be read
        
        return cls(
            root_path=root_path,
            language=language,
            files=files,
        )

