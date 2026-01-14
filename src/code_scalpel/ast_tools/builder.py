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
        # TODO [COMMUNITY][FEATURE]: Comment preservation in preprocessing
        # TODO [COMMUNITY]: Enhance _remove_comments to preserve docstrings
        # TODO [COMMUNITY]: Track comment locations with line numbers
        # TODO [COMMUNITY]: Reattach comments to AST nodes
        # TODO [COMMUNITY]: Add 20+ tests for comment preservation

        # TODO [COMMUNITY][FEATURE]: Better syntax error recovery
        # TODO [COMMUNITY]: Suggest fixes for common syntax errors
        # TODO [COMMUNITY]: Recover and continue parsing
        # TODO [COMMUNITY]: Collect all errors in one pass
        # TODO [COMMUNITY]: Add 25+ tests for error recovery

        # TODO [COMMUNITY][TEST]: Edge cases
        # TODO [COMMUNITY]: Test incomplete code, mixed line endings
        # TODO [COMMUNITY]: Test very large files, deeply nested structures

        # ====================================================================
        # TIER 2: PRO (Commercial - Medium Priority)
        # ====================================================================
        # TODO [PRO][FEATURE]: Add incremental parsing for large codebases
        # TODO [PRO]: Parse only modified files
        # TODO [PRO]: Reuse AST from unchanged files
        # TODO [PRO]: Track file modification times
        # TODO [PRO]: Implement dependency-aware incremental parsing
        # TODO [PRO]: Add 30+ tests for incremental parsing

        # TODO [PRO][FEATURE]: Support caching with TTL and invalidation
        # TODO [PRO]: Implement TTL (time-to-live) for cache entries
        # TODO [PRO]: Support cache invalidation by dependency
        # TODO [PRO]: Track cache key dependencies
        # TODO [PRO]: Add cache warming strategies
        # TODO [PRO]: Add 25+ tests for cache expiration

        # TODO [PRO][ENHANCEMENT]: Add preprocessing for type stubs
        # TODO [PRO]: Handle .pyi file parsing
        # TODO [PRO]: Extract type signatures from stubs
        # TODO [PRO]: Merge type information with source
        # TODO [PRO]: Support typing_extensions compatibility
        # TODO [PRO]: Add 20+ tests for stub handling

        # ====================================================================
        # TIER 3: ENTERPRISE (Commercial - Lower Priority)
        # ====================================================================
        # TODO [ENTERPRISE][ENHANCEMENT]: Support parallel AST building
        # TODO [ENTERPRISE]: Implement thread-pool based parsing
        # TODO [ENTERPRISE]: Handle thread-safe cache access
        # TODO [ENTERPRISE]: Support process-based parsing for isolation
        # TODO [ENTERPRISE]: Add performance benchmarks
        # TODO [ENTERPRISE]: Add 30+ tests for parallel parsing

        # TODO [ENTERPRISE][FEATURE]: Custom preprocessing pipeline
        # TODO [ENTERPRISE]: Support pipeline configuration
        # TODO [ENTERPRISE]: Enable preprocessing hook ordering
        # TODO [ENTERPRISE]: Add conditional preprocessing
        # TODO [ENTERPRISE]: Support reversible preprocessing
        # TODO [ENTERPRISE]: Add 25+ tests for preprocessing pipeline

        # TODO [ENTERPRISE][FEATURE]: AST validation with custom rules
        # TODO [ENTERPRISE]: Support custom validation rule registration
        # TODO [ENTERPRISE]: Generate detailed validation reports
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
