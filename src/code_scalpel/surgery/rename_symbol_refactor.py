"""rename_symbol V1.0 helpers.

This module implements conservative, token-preserving reference/import renames for
Python projects.

Design goals:
- Preserve formatting: edits are applied via tokenize.untokenize.
- Be conservative: only rewrite references when we can infer linkage via imports.
- Avoid strings/comments: tokenizer edits NAME tokens only.

Tier intent (enforced by caller):
- Community: definition-only (no cross-file changes)
- Pro: cross-file reference/import renames with bounded limits
- Enterprise: same as Pro, but no tier limits
"""

from __future__ import annotations

import ast
import io
import os
import shutil
import tempfile
import tokenize
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

_SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
}


@dataclass(frozen=True)
class RenameEdits:
    # Mapping from token (line, col) start position to (old, new)
    token_replacements: dict[tuple[int, int], tuple[str, str]]


@dataclass
class CrossFileRenameResult:
    success: bool
    changed_files: list[str]
    backup_paths: dict[str, str | None]
    warnings: list[str]
    error: str | None = None


def iter_python_files(
    project_root: Path, *, max_files: int | None = None
) -> Iterable[Path]:
    """Yield Python files under project_root, skipping common virtualenv/build dirs."""
    count = 0
    for root, dirnames, filenames in os.walk(project_root):
        # Mutate dirnames in-place to prune walk
        dirnames[:] = [
            d for d in dirnames if d not in _SKIP_DIR_NAMES and not d.startswith(".")
        ]

        for name in filenames:
            if not name.endswith(".py"):
                continue
            path = Path(root) / name
            yield path
            count += 1
            if max_files is not None and count >= max_files:
                return


def module_name_for_file(project_root: Path, file_path: Path) -> str | None:
    """Best-effort module name for a .py file relative to project_root."""
    try:
        rel = file_path.resolve().relative_to(project_root.resolve())
    except Exception:
        return None

    if rel.suffix != ".py":
        return None

    parts = list(rel.parts)
    if not parts:
        return None

    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]  # strip .py

    # Filter empty parts
    parts = [p for p in parts if p]
    if not parts:
        return None
    return ".".join(parts)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text_atomic(path: Path, new_text: str, *, create_backup: bool) -> str | None:
    backup_path: str | None = None
    if create_backup:
        backup_path = f"{path}.bak"
        shutil.copy2(path, backup_path)

    dir_path = str(path.parent)
    with tempfile.NamedTemporaryFile(
        mode="w", dir=dir_path, delete=False, suffix=".tmp", encoding="utf-8"
    ) as f:
        f.write(new_text)
        tmp_path = f.name

    os.replace(tmp_path, path)
    return backup_path


def _tokenize(code: str) -> list[tokenize.TokenInfo]:
    return list(tokenize.generate_tokens(io.StringIO(code).readline))


def _apply_token_replacements(
    tokens: list[tokenize.TokenInfo],
    replacements: dict[tuple[int, int], tuple[str, str]],
) -> str:
    new_tokens: list[tokenize.TokenInfo] = []
    for tok in tokens:
        repl = replacements.get(tok.start)
        if repl and tok.type == tokenize.NAME and tok.string == repl[0]:
            tok = tokenize.TokenInfo(tok.type, repl[1], tok.start, tok.end, tok.line)
        new_tokens.append(tok)
    return tokenize.untokenize(new_tokens)


def _collect_import_context(
    tree: ast.AST,
    *,
    target_module: str,
    old_short: str,
    target_type: str,
    target_name: str,
) -> tuple[
    # from-import info: (local_name, should_rename_local_uses, has_asname)
    list[tuple[str, bool, bool]],
    # module alias names for `import target_module as alias`
    list[str],
    # local class names imported for method renames (OldClass or alias)
    list[str],
]:
    from_imports: list[tuple[str, bool, bool]] = []
    module_aliases: list[str] = []
    imported_class_locals: list[str] = []

    method_class: str | None = None
    method_old: str | None = None
    if target_type == "method":
        if "." in target_name:
            method_class, method_old = target_name.split(".", 1)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module != target_module:
                continue
            for alias in node.names:
                local = alias.asname or alias.name

                if target_type in {"function", "class"} and alias.name == old_short:
                    # If imported without alias, local uses should be renamed.
                    from_imports.append(
                        (local, alias.asname is None, alias.asname is not None)
                    )

                if (
                    target_type == "method"
                    and method_class
                    and alias.name == method_class
                ):
                    imported_class_locals.append(local)

        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name != target_module:
                    continue
                module_aliases.append(alias.asname or alias.name.split(".")[-1])

    return from_imports, module_aliases, imported_class_locals


def _collect_reference_edits(
    code: str,
    *,
    target_module: str,
    target_type: str,
    target_name: str,
    new_name: str,
) -> RenameEdits:
    """Collect token edits for a single file.

    Conservative rules:
    - Only rename local `Name(old)` when the file has `from target_module import old`.
    - Only rename `module_alias.old` when the file has `import target_module [as module_alias]`.
    - Method rename only rewrites `ClassName.old_method` and `module_alias.ClassName.old_method` patterns.

    Import statement rewriting is also applied when the module matches.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return RenameEdits(token_replacements={})

    token_replacements: dict[tuple[int, int], tuple[str, str]] = {}
    tokens = _tokenize(code)

    if target_type == "method":
        if "." not in target_name:
            return RenameEdits(token_replacements={})
        class_name, old_short = target_name.split(".", 1)
        new_short = new_name
    else:
        old_short = target_name
        new_short = new_name
        class_name = None

    from_imports, module_aliases, imported_class_locals = _collect_import_context(
        tree,
        target_module=target_module,
        old_short=old_short,
        target_type=target_type,
        target_name=target_name,
    )

    # 1) Rewrite import-from statements: from target_module import old_short [...]
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module != target_module:
            continue

        start_line = getattr(node, "lineno", None)
        end_line = getattr(node, "end_lineno", start_line)
        if not start_line:
            continue

        # Build set of import names we want to rewrite in this statement.
        desired: dict[str, str] = {}
        if target_type in {"function", "class"}:
            for alias in node.names:
                if alias.name == old_short:
                    desired[alias.name] = new_short
        elif target_type == "method" and class_name:
            # Method renames require importing the class name.
            for alias in node.names:
                if alias.name == class_name:
                    # No import rename needed for method-only rename.
                    desired = {}

        if not desired:
            continue

        in_stmt = False
        for tok in tokens:
            if tok.start[0] < start_line or (end_line and tok.start[0] > end_line):
                continue
            if tok.type != tokenize.NAME:
                continue
            if tok.string == "from":
                in_stmt = True
                continue
            if not in_stmt:
                continue
            # Only after keyword 'import' should we rewrite imported symbol names.
            # We'll detect this by requiring we've seen 'import' on the statement.

        seen_import_kw = False
        for tok in tokens:
            if tok.start[0] < start_line or (end_line and tok.start[0] > end_line):
                continue
            if tok.type != tokenize.NAME:
                continue
            if tok.string == "import":
                seen_import_kw = True
                continue
            if not seen_import_kw:
                continue
            replacement = desired.get(tok.string)
            if replacement:
                token_replacements[tok.start] = (tok.string, replacement)

    # 2) Rewrite local Name usages when imported directly.
    if target_type in {"function", "class"}:
        rename_local_names = {
            local
            for (local, should_rename, _has_as) in from_imports
            if should_rename and local == old_short
        }
        if rename_local_names:
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id == old_short:
                    # Only rewrite Name tokens at the Name's position.
                    if hasattr(node, "lineno") and hasattr(node, "col_offset"):
                        token_replacements[(node.lineno, node.col_offset)] = (
                            old_short,
                            new_short,
                        )

    # 3) Rewrite module_alias.old_short attribute usages.
    if target_type in {"function", "class"}:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute):
                continue
            if node.attr != old_short:
                continue
            if isinstance(node.value, ast.Name) and node.value.id in module_aliases:
                if hasattr(node, "end_lineno") and hasattr(node, "end_col_offset"):
                    if node.end_lineno is not None and node.end_col_offset is not None:
                        start = (node.end_lineno, node.end_col_offset - len(old_short))
                        token_replacements[start] = (old_short, new_short)

    # 4) Method rename patterns: ClassName.old_method and module_alias.ClassName.old_method
    if target_type == "method" and class_name:
        old_method = old_short
        new_method = new_short

        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute):
                continue
            if node.attr != old_method:
                continue

            # Pattern A: ImportedClass.old_method
            if (
                isinstance(node.value, ast.Name)
                and node.value.id in imported_class_locals
            ):
                if (
                    hasattr(node, "end_lineno")
                    and hasattr(node, "end_col_offset")
                    and node.end_lineno is not None
                    and node.end_col_offset is not None
                ):
                    start = (node.end_lineno, node.end_col_offset - len(old_method))
                    token_replacements[start] = (old_method, new_method)
                    continue

            # Pattern B: module_alias.ClassName.old_method
            if isinstance(node.value, ast.Attribute) and node.value.attr in {
                class_name
            }:
                inner = node.value
                if (
                    isinstance(inner.value, ast.Name)
                    and inner.value.id in module_aliases
                ):
                    if (
                        hasattr(node, "end_lineno")
                        and hasattr(node, "end_col_offset")
                        and node.end_lineno is not None
                        and node.end_col_offset is not None
                    ):
                        start = (node.end_lineno, node.end_col_offset - len(old_method))
                        token_replacements[start] = (old_method, new_method)

    return RenameEdits(token_replacements=token_replacements)


def rename_references_across_project(
    *,
    project_root: Path,
    target_file: Path,
    target_type: str,
    target_name: str,
    new_name: str,
    create_backup: bool,
    max_files_searched: int | None,
    max_files_updated: int | None,
) -> CrossFileRenameResult:
    """Rename references/imports across a project for Pro/Enterprise tiers."""
    warnings: list[str] = []

    target_module = module_name_for_file(project_root, target_file)
    if not target_module:
        return CrossFileRenameResult(
            success=False,
            changed_files=[],
            backup_paths={},
            warnings=warnings,
            error="Could not determine target module name for cross-file rename.",
        )

    changed_files: list[str] = []
    backup_paths: dict[str, str | None] = {}

    searched = 0
    updated = 0

    for py_file in iter_python_files(project_root, max_files=max_files_searched):
        searched += 1
        if py_file.resolve() == target_file.resolve():
            continue

        try:
            code = _read_text(py_file)
        except Exception:
            continue

        edits = _collect_reference_edits(
            code,
            target_module=target_module,
            target_type=target_type,
            target_name=target_name,
            new_name=new_name,
        )

        if not edits.token_replacements:
            continue

        new_code = _apply_token_replacements(_tokenize(code), edits.token_replacements)
        if new_code == code:
            continue

        if max_files_updated is not None and updated >= max_files_updated:
            warnings.append(
                f"Reached max_files_updated={max_files_updated}; additional reference updates were skipped."
            )
            break

        try:
            backup_path = _write_text_atomic(
                py_file, new_code, create_backup=create_backup
            )
            changed_files.append(str(py_file))
            backup_paths[str(py_file)] = backup_path
            updated += 1
        except Exception as e:
            warnings.append(f"Failed to update {py_file}: {e}")

    if max_files_searched is not None and searched >= max_files_searched:
        warnings.append(f"Search truncated at max_files_searched={max_files_searched}.")

    return CrossFileRenameResult(
        success=True,
        changed_files=changed_files,
        backup_paths=backup_paths,
        warnings=warnings,
        error=None,
    )
