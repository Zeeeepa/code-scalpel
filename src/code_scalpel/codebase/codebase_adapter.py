"""Adapter to wrap Codegen's Codebase class with CodebaseView interface.

This adapter provides a bridge between Codegen's heavyweight Codebase class
and our minimal CodebaseView interface, handling complex dependencies internally.
"""

from pathlib import Path
from typing import List, Optional, TYPE_CHECKING
import logging

from code_scalpel.codebase.codebase_view import (
    CodebaseView,
    SimpleFile,
    SimpleSymbol,
    SimpleClass,
    SimpleFunction,
    SimpleImport,
)

if TYPE_CHECKING:
    from code_scalpel.core.codebase import Codebase

logger = logging.getLogger(__name__)


class CodebaseAdapter:
    """Adapter that wraps Codegen's Codebase to implement CodebaseView.

    This adapter:
    - Implements the minimal CodebaseView interface
    - Handles complex Codegen dependencies internally
    - Provides lazy loading for expensive operations
    - Gracefully degrades when features are unavailable

    Usage:
        from code_scalpel.core.codebase import Codebase

        # Create Codegen codebase (if available)
        codegen_codebase = Codebase(...)

        # Wrap it with adapter
        view = CodebaseAdapter(codegen_codebase)

        # Use through minimal interface
        files = view.files
        symbols = view.symbols
    """

    def __init__(self, codebase: "Codebase"):
        """Initialize adapter with a Codegen Codebase instance.

        Args:
            codebase: Codegen Codebase instance to wrap
        """
        self._codebase = codebase
        self._files_cache: Optional[List[SimpleFile]] = None
        self._symbols_cache: Optional[List[SimpleSymbol]] = None
        self._classes_cache: Optional[List[SimpleClass]] = None
        self._functions_cache: Optional[List[SimpleFunction]] = None
        self._imports_cache: Optional[List[SimpleImport]] = None

    @property
    def root_path(self) -> Path:
        """Root directory of the codebase."""
        try:
            return Path(self._codebase.root_path)
        except Exception as e:
            logger.warning(f"Failed to get root_path: {e}")
            return Path.cwd()

    @property
    def language(self) -> str:
        """Primary programming language of the codebase."""
        try:
            lang = self._codebase.language
            return str(lang) if lang else "python"
        except Exception as e:
            logger.warning(f"Failed to get language: {e}")
            return "python"

    @property
    def files(self) -> List[SimpleFile]:
        """All files in the codebase."""
        if self._files_cache is not None:
            return self._files_cache

        try:
            files = []
            for file in self._codebase.files:
                try:
                    files.append(
                        SimpleFile(
                            path=Path(file.path),
                            content=file.content or "",
                            language=(
                                str(file.language)
                                if hasattr(file, "language")
                                else self.language
                            ),
                        )
                    )
                except Exception as e:
                    logger.debug(f"Failed to convert file {file}: {e}")
                    continue

            self._files_cache = files
            return files
        except Exception as e:
            logger.error(f"Failed to get files: {e}")
            return []

    @property
    def symbols(self) -> List[SimpleSymbol]:
        """All symbols (classes, functions, variables) in the codebase."""
        if self._symbols_cache is not None:
            return self._symbols_cache

        try:
            symbols = []
            for symbol in self._codebase.symbols:
                try:
                    symbols.append(
                        SimpleSymbol(
                            name=symbol.name,
                            type=(
                                str(symbol.type)
                                if hasattr(symbol, "type")
                                else "unknown"
                            ),
                            file_path=(
                                Path(symbol.file_path)
                                if hasattr(symbol, "file_path")
                                else Path()
                            ),
                            line_number=(
                                symbol.line_number
                                if hasattr(symbol, "line_number")
                                else 0
                            ),
                        )
                    )
                except Exception as e:
                    logger.debug(f"Failed to convert symbol {symbol}: {e}")
                    continue

            self._symbols_cache = symbols
            return symbols
        except Exception as e:
            logger.error(f"Failed to get symbols: {e}")
            return []

    @property
    def classes(self) -> List[SimpleClass]:
        """All classes in the codebase."""
        if self._classes_cache is not None:
            return self._classes_cache

        try:
            classes = []
            for cls in self._codebase.classes:
                try:
                    methods = []
                    attributes = []

                    if hasattr(cls, "methods"):
                        methods = [m.name for m in cls.methods if hasattr(m, "name")]

                    if hasattr(cls, "attributes"):
                        attributes = [
                            a.name for a in cls.attributes if hasattr(a, "name")
                        ]

                    classes.append(
                        SimpleClass(
                            name=cls.name,
                            file_path=(
                                Path(cls.file_path)
                                if hasattr(cls, "file_path")
                                else Path()
                            ),
                            methods=methods,
                            attributes=attributes,
                        )
                    )
                except Exception as e:
                    logger.debug(f"Failed to convert class {cls}: {e}")
                    continue

            self._classes_cache = classes
            return classes
        except Exception as e:
            logger.error(f"Failed to get classes: {e}")
            return []

    @property
    def functions(self) -> List[SimpleFunction]:
        """All functions in the codebase."""
        if self._functions_cache is not None:
            return self._functions_cache

        try:
            functions = []
            for func in self._codebase.functions:
                try:
                    parameters = []
                    return_type = None

                    if hasattr(func, "parameters"):
                        parameters = [
                            p.name for p in func.parameters if hasattr(p, "name")
                        ]

                    if hasattr(func, "return_type"):
                        return_type = str(func.return_type)

                    functions.append(
                        SimpleFunction(
                            name=func.name,
                            file_path=(
                                Path(func.file_path)
                                if hasattr(func, "file_path")
                                else Path()
                            ),
                            parameters=parameters,
                            return_type=return_type,
                        )
                    )
                except Exception as e:
                    logger.debug(f"Failed to convert function {func}: {e}")
                    continue

            self._functions_cache = functions
            return functions
        except Exception as e:
            logger.error(f"Failed to get functions: {e}")
            return []

    @property
    def imports(self) -> List[SimpleImport]:
        """All imports in the codebase."""
        if self._imports_cache is not None:
            return self._imports_cache

        try:
            imports = []
            for imp in self._codebase.imports:
                try:
                    names = []
                    if hasattr(imp, "names"):
                        names = [n for n in imp.names if isinstance(n, str)]

                    imports.append(
                        SimpleImport(
                            module=imp.module if hasattr(imp, "module") else "",
                            names=names,
                            file_path=(
                                Path(imp.file_path)
                                if hasattr(imp, "file_path")
                                else Path()
                            ),
                        )
                    )
                except Exception as e:
                    logger.debug(f"Failed to convert import {imp}: {e}")
                    continue

            self._imports_cache = imports
            return imports
        except Exception as e:
            logger.error(f"Failed to get imports: {e}")
            return []

    def get_file(self, path: Path) -> Optional[SimpleFile]:
        """Get a specific file by path."""
        try:
            # Try to get from Codegen codebase
            file = self._codebase.get_file(str(path))
            if file:
                return SimpleFile(
                    path=Path(file.path),
                    content=file.content or "",
                    language=(
                        str(file.language)
                        if hasattr(file, "language")
                        else self.language
                    ),
                )
        except Exception as e:
            logger.debug(f"Failed to get file {path}: {e}")

        # Fallback: search in cached files
        for file in self.files:
            if file.path == path:
                return file

        return None

    def clear_cache(self):
        """Clear all cached data to force refresh."""
        self._files_cache = None
        self._symbols_cache = None
        self._classes_cache = None
        self._functions_cache = None
        self._imports_cache = None


def create_codebase_view(codebase: "Codebase") -> CodebaseView:
    """Factory function to create a CodebaseView from a Codegen Codebase.

    This is the recommended way to create a view from a Codegen codebase.

    Args:
        codebase: Codegen Codebase instance

    Returns:
        CodebaseView implementation (CodebaseAdapter)

    Example:
        from code_scalpel.core.codebase import Codebase
        from code_scalpel.codebase.codebase_adapter import create_codebase_view

        # Create Codegen codebase
        codebase = Codebase(...)

        # Get minimal view
        view = create_codebase_view(codebase)

        # Use through interface
        for file in view.files:
            print(file.path)
    """
    return CodebaseAdapter(codebase)
