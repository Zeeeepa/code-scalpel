from __future__ import annotations

import ast
import logging
import tokenize
from functools import lru_cache
from io import StringIO
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class ASTBuilder:
    """
    Advanced AST builder with preprocessing and validation capabilities.
    """

    def __init__(self):
        self.preprocessing_hooks: list[Callable[[str], str]] = []
        self.validation_hooks: list[Callable[[ast.AST], None]] = []
        self.ast_cache: dict[str, ast.AST] = {}
        # ====================================================================
        # TIER 1: COMMUNITY (Free - High Priority)
        # ====================================================================
        # [20251224_TIER1_TODO] FEATURE: Comment preservation in preprocessing
        #   Purpose: Maintain code documentation during AST parsing
        #   Steps:
        #     1. Enhance _remove_comments to preserve docstrings
        #     2. Track comment locations with line numbers
        #     3. Reattach comments to AST nodes
        #     4. Add 20+ tests for comment preservation

        # [20251224_TIER1_TODO] FEATURE: Better syntax error recovery
        #   Purpose: Provide actionable error messages
        #   Steps:
        #     1. Suggest fixes for common syntax errors
        #     2. Recover and continue parsing
        #     3. Collect all errors in one pass
        #     4. Add 25+ tests for error recovery

        # [20251224_TIER1_TODO] TEST: Edge cases
        #   - Incomplete code, mixed line endings
        #   - Very large files, deeply nested structures

        # ====================================================================
        # TIER 2: PRO (Commercial - Medium Priority)
        # ====================================================================
        # [20251224_TIER2_TODO] FEATURE: Add incremental parsing for large codebases
        #   Purpose: Improve performance for multi-file projects
        #   Steps:
        #     1. Parse only modified files
        #     2. Reuse AST from unchanged files
        #     3. Track file modification times
        #     4. Implement dependency-aware incremental parsing
        #     5. Add 30+ tests for incremental parsing

        # [20251224_TIER2_TODO] FEATURE: Support caching with TTL and invalidation
        #   Purpose: Enable efficient cache management
        #   Steps:
        #     1. Implement TTL (time-to-live) for cache entries
        #     2. Support cache invalidation by dependency
        #     3. Track cache key dependencies
        #     4. Add cache warming strategies
        #     5. Add 25+ tests for cache expiration

        # [20251224_TIER2_TODO] ENHANCEMENT: Add preprocessing for type stubs
        #   Purpose: Support .pyi stub files for type checking
        #   Steps:
        #     1. Handle .pyi file parsing
        #     2. Extract type signatures from stubs
        #     3. Merge type information with source
        #     4. Support typing_extensions compatibility
        #     5. Add 20+ tests for stub handling

        # ====================================================================
        # TIER 3: ENTERPRISE (Commercial - Lower Priority)
        # ====================================================================
        # [20251224_TIER3_TODO] ENHANCEMENT: Support parallel AST building
        #   Purpose: Leverage multi-core processors
        #   Steps:
        #     1. Implement thread-pool based parsing
        #     2. Handle thread-safe cache access
        #     3. Support process-based parsing for isolation
        #     4. Add performance benchmarks
        #     5. Add 30+ tests for parallel parsing

        # [20251224_TIER3_TODO] FEATURE: Custom preprocessing pipeline
        #   Purpose: Allow extensible code transformations
        #   Steps:
        #     1. Support pipeline configuration
        #     2. Enable preprocessing hook ordering
        #     3. Add conditional preprocessing
        #     4. Support reversible preprocessing
        #     5. Add 25+ tests for preprocessing pipeline

        # [20251224_TIER3_TODO] FEATURE: AST validation with custom rules
        #   Purpose: Enforce code standards
        #   Steps:
        #     1. Support custom validation rule registration
        #     2. Generate detailed validation reports
        #     3. Suggest fixes for validation failures
        #     4. Support configurable rule sets
        #     5. Add 35+ tests for validation rules

    def build_ast(
        self, code: str, preprocess: bool = True, validate: bool = True
    ) -> Optional[ast.AST]:
        """
        Build an AST from Python code with optional preprocessing and validation.

        Args:
            code (str): The Python code to parse.
            preprocess (bool): Whether to apply preprocessing hooks.
            validate (bool): Whether to apply validation hooks.

        Returns:
            Optional[ast.AST]: The parsed AST, or None if an error occurred.
        """
        if code in self.ast_cache:
            return self.ast_cache[code]

        try:
            if preprocess:
                code = self._preprocess_code(code)

            tree = ast.parse(code)

            if validate:
                self._validate_ast(tree)

            self.ast_cache[code] = tree
            return tree
        except SyntaxError as e:
            self._handle_syntax_error(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error building AST: {str(e)}")
            return None

    @lru_cache(maxsize=100)
    def build_ast_from_file(
        self, filepath: str, preprocess: bool = True, validate: bool = True
    ) -> Optional[ast.AST]:
        """
        Build an AST from a Python source file with caching.

        Args:
            filepath (str): The path to the Python source file.
            preprocess (bool): Whether to apply preprocessing hooks.
            validate (bool): Whether to apply validation hooks.

        Returns:
            Optional[ast.AST]: The parsed AST, or None if an error occurred.
        """
        try:
            with tokenize.open(filepath) as file:
                code = file.read()
                return self.build_ast(code, preprocess, validate)
        except FileNotFoundError:
            logger.error(f"Error: File not found: {filepath}")
            return None
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
            return None

    def add_preprocessing_hook(self, hook: Callable[[str], str]) -> None:
        """Add a preprocessing hook to modify code before parsing."""
        self.preprocessing_hooks.append(hook)

    def remove_preprocessing_hook(self, hook: Callable[[str], str]) -> None:
        """Remove a preprocessing hook."""
        self.preprocessing_hooks.remove(hook)

    def add_validation_hook(self, hook: Callable[[ast.AST], None]) -> None:
        """Add a validation hook to check the AST after parsing."""
        self.validation_hooks.append(hook)

    def remove_validation_hook(self, hook: Callable[[ast.AST], None]) -> None:
        """Remove a validation hook."""
        self.validation_hooks.remove(hook)

    def _preprocess_code(self, code: str) -> str:
        """Apply all preprocessing hooks to the code."""
        processed_code = code

        # Remove comments
        processed_code = self._remove_comments(processed_code)

        # Apply custom preprocessing hooks
        for hook in self.preprocessing_hooks:
            processed_code = hook(processed_code)

        return processed_code

    def _validate_ast(self, tree: ast.AST) -> None:
        """Apply all validation hooks to the AST."""
        for hook in self.validation_hooks:
            hook(tree)

    @staticmethod
    def _remove_comments(code: str) -> str:
        """Remove comments while preserving line numbers."""
        result = []
        prev_toktype = tokenize.INDENT
        first_line = True

        tokens = tokenize.generate_tokens(StringIO(code).readline)

        for toktype, ttext, (_slineno, _scol), (_elineno, _ecol), _ltext in tokens:
            if toktype == tokenize.COMMENT:
                continue
            elif toktype == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
                    result.append(" ")
                result.append(ttext)
            elif toktype == tokenize.NEWLINE or toktype == tokenize.INDENT:
                result.append(ttext)
            elif toktype == tokenize.DEDENT:
                pass
            else:
                if not first_line and prev_toktype != tokenize.INDENT:
                    result.append(" ")
                result.append(ttext)
            prev_toktype = toktype
            first_line = False

        return "".join(result)

    def _handle_syntax_error(self, error: SyntaxError) -> None:
        """Handle syntax errors with detailed information."""
        logger.error(f"Syntax Error at line {error.lineno}, column {error.offset}:")
        if error.text:
            logger.error(f"  {error.text.strip()}")
            if error.offset:
                logger.error("  " + " " * (error.offset - 1) + "^")
        logger.error(f"Error message: {str(error)}")

    def clear_cache(self) -> None:
        """Clear the AST cache."""
        self.ast_cache.clear()
