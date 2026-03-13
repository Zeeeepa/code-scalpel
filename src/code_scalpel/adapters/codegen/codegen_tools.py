"""
Codegen Tools Adapter

Direct imports from Codegen SDK - no reimplementation.
All tools with tier unification applied (Community tier).
"""

from codegen.extensions.tools import (
    commit as _commit,
    create_file as _create_file,
    create_pr as _create_pr,
    create_pr_comment as _create_pr_comment,
    create_pr_review_comment as _create_pr_review_comment,
    delete_file as _delete_file,
    edit_file as _edit_file,
    move_symbol as _move_symbol,
    perform_reflection as _perform_reflection,
    rename_file as _rename_file,
    replacement_edit as _replacement_edit,
    replacement_edit_global as _replacement_edit_global,
    reveal_symbol as _reveal_symbol,
    run_codemod as _run_codemod,
    search as _search,
    search_files_by_name as _search_files_by_name,
    semantic_edit as _semantic_edit,
    semantic_search as _semantic_search,
    view_file as _view_file,
    view_pr as _view_pr
)

# Re-export with tier unification
# All tools are now Community tier accessible

def commit(*args, **kwargs):
    """Git commit - Community tier"""
    return _commit(*args, **kwargs)


def create_file(*args, **kwargs):
    """Create file - Community tier"""
    return _create_file(*args, **kwargs)


def create_pr(*args, **kwargs):
    """Create PR - Community tier"""
    return _create_pr(*args, **kwargs)


def create_pr_comment(*args, **kwargs):
    """Create PR comment - Community tier"""
    return _create_pr_comment(*args, **kwargs)


def create_pr_review_comment(*args, **kwargs):
    """Create PR review comment - Community tier"""
    return _create_pr_review_comment(*args, **kwargs)


def delete_file(*args, **kwargs):
    """Delete file - Community tier (unified from Pro)"""
    return _delete_file(*args, **kwargs)


def edit_file(*args, **kwargs):
    """Edit file - Community tier (unified from Pro)"""
    return _edit_file(*args, **kwargs)


def move_symbol(*args, **kwargs):
    """Move symbol - Community tier (unified from Enterprise)"""
    return _move_symbol(*args, **kwargs)


def perform_reflection(*args, **kwargs):
    """Perform reflection - Community tier"""
    return _perform_reflection(*args, **kwargs)


def rename_file(*args, **kwargs):
    """Rename file - Community tier (unified from Pro)"""
    return _rename_file(*args, **kwargs)


def replacement_edit(*args, **kwargs):
    """Replacement edit - Community tier (unified from Pro)"""
    return _replacement_edit(*args, **kwargs)


def replacement_edit_global(*args, **kwargs):
    """Global replacement edit - Community tier (unified from Enterprise)"""
    return _replacement_edit_global(*args, **kwargs)


def reveal_symbol(*args, **kwargs):
    """Reveal symbol - Community tier"""
    return _reveal_symbol(*args, **kwargs)


def run_codemod(*args, **kwargs):
    """Run codemod - Community tier"""
    return _run_codemod(*args, **kwargs)


def search(*args, **kwargs):
    """Search - Community tier"""
    return _search(*args, **kwargs)


def search_files_by_name(*args, **kwargs):
    """Search files by name - Community tier"""
    return _search_files_by_name(*args, **kwargs)


def semantic_edit(*args, **kwargs):
    """Semantic edit - Community tier"""
    return _semantic_edit(*args, **kwargs)


def semantic_search(*args, **kwargs):
    """Semantic search - Community tier (unified from Enterprise)"""
    return _semantic_search(*args, **kwargs)


def view_file(*args, **kwargs):
    """View file - Community tier"""
    return _view_file(*args, **kwargs)


def view_pr(*args, **kwargs):
    """View PR - Community tier"""
    return _view_pr(*args, **kwargs)

