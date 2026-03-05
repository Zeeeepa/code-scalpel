"""
Codegen Document Functions Adapter

Example use case adapter showing how to use Codegen SDK for automated documentation.
Based on codegen/codegen-examples/examples/document_functions/run.py

This demonstrates:
- Using Codebase.from_repo() to load a repository
- Navigating symbol dependencies and usages
- Using codebase.ai() for AI-powered documentation generation
- Incremental commits for safe progress tracking
"""

from codegen.sdk.core.codebase import Codebase as _Codebase
from codegen.sdk.core.external_module import ExternalModule as _ExternalModule
from codegen.sdk.core.import_resolution import Import as _Import
from codegen.sdk.core.symbol import Symbol as _Symbol

# Re-export core classes
Codebase = _Codebase
ExternalModule = _ExternalModule
Import = _Import
Symbol = _Symbol


def hop_through_imports(imp):
    """
    Finds the root symbol for an import - Community tier
    
    Recursively follows import chains to find the actual symbol being imported.
    
    Args:
        imp: Import object to resolve
        
    Returns:
        Symbol or ExternalModule at the end of the import chain
    """
    if isinstance(imp.imported_symbol, _Import):
        return hop_through_imports(imp.imported_symbol)
    return imp.imported_symbol


def get_extended_context(symbol, degree):
    """
    Recursively collect dependencies and usages - Community tier
    
    Collects all symbols that the given symbol depends on or is used by,
    up to the specified degree of separation.
    
    Args:
        symbol: The symbol to collect context for
        degree: How many levels deep to collect dependencies and usages
        
    Returns:
        A tuple of (dependencies, usages) where each is a set of related Symbol objects
    """
    dependencies = set()
    usages = set()
    
    if degree > 0:
        # Collect direct dependencies
        for dep in symbol.dependencies:
            # Hop through imports to find the root symbol
            if isinstance(dep, _Import):
                dep = hop_through_imports(dep)
            
            if isinstance(dep, _Symbol) and dep not in dependencies:
                dependencies.add(dep)
                dep_deps, dep_usages = get_extended_context(dep, degree - 1)
                dependencies.update(dep_deps)
                usages.update(dep_usages)
        
        # Collect usages in the current symbol
        for usage in symbol.usages:
            usage_symbol = usage.usage_symbol
            # Hop through imports for usage symbols too
            if isinstance(usage_symbol, _Import):
                usage_symbol = hop_through_imports(usage_symbol)
            
            if isinstance(usage_symbol, _Symbol) and usage_symbol not in usages:
                usages.add(usage_symbol)
                usage_deps, usage_usages = get_extended_context(usage_symbol, degree - 1)
                dependencies.update(usage_deps)
                usages.update(usage_usages)
    
    return dependencies, usages


def document_functions(codebase, n_degree=2, skip_patterns=None):
    """
    Automatically generate docstrings for functions - Community tier
    
    Uses AI to generate comprehensive docstrings based on function context,
    including dependencies and usages.
    
    Args:
        codebase: Codegen Codebase instance
        n_degree: How many levels of dependencies/usages to include in context (default: 2)
        skip_patterns: List of patterns to skip (e.g., ["test", "tutorial"])
        
    Returns:
        Dictionary with statistics about processed functions
    """
    if skip_patterns is None:
        skip_patterns = ["test", "tutorial"]
    
    # Filter out test and tutorial functions
    functions = [
        f for f in codebase.functions 
        if not any(pattern in f.name.lower() for pattern in skip_patterns)
        and not any(pattern in f.filepath.lower() for pattern in skip_patterns)
    ]
    
    # Track progress
    total_functions = len(functions)
    processed = 0
    generated = 0
    skipped = 0
    failed = 0
    
    print(f"Found {total_functions} functions to process (excluding {', '.join(skip_patterns)})")
    
    for function in functions:
        processed += 1
        
        # Skip if already has docstring
        if function.docstring:
            print(f"[{processed}/{total_functions}] Skipping {function.name} - already has docstring")
            skipped += 1
            continue
        
        print(f"[{processed}/{total_functions}] Generating docstring for {function.name} at {function.filepath}")
        
        # Collect context using N-degree dependencies and usages
        dependencies, usages = get_extended_context(function, n_degree)
        
        # Generate a docstring using the AI with the context
        docstring = codebase.ai(
            """
            Generate a docstring for this function using the provided context.
            The context includes:
            - dependencies: other symbols this function depends on
            - usages: other symbols that use this function
            """,
            target=function,
            context={"dependencies": list(dependencies), "usages": list(usages)},
        )
        
        # Set the generated docstring for the function
        if docstring:
            function.set_docstring(docstring)
            print("  ✓ Generated docstring")
            generated += 1
        else:
            print("  ✗ Failed to generate docstring")
            failed += 1
        
        # Commit after each function for incremental progress
        codebase.commit()
    
    stats = {
        "total": total_functions,
        "processed": processed,
        "generated": generated,
        "skipped": skipped,
        "failed": failed,
    }
    
    print(f"\nCompleted processing {total_functions} functions")
    print(f"  Generated: {generated}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed: {failed}")
    
    return stats


__all__ = [
    'Codebase',
    'ExternalModule',
    'Import',
    'Symbol',
    'hop_through_imports',
    'get_extended_context',
    'document_functions',
]

