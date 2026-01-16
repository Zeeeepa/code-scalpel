import re
import sys
from pathlib import Path

server_path = Path("src/code_scalpel/mcp/server.py")
if not server_path.exists():
    print("server.py not found")
    sys.exit(1)

content = server_path.read_text(encoding="utf-8")

functions_to_remove = {
    "_crawl_project_discovery",
    "_crawl_project_sync",
    "crawl_project",
    "_get_file_context_sync",
    "get_file_context",
    "_get_symbol_references_sync",
    "get_symbol_references",
    "_get_cached_ast",
    "_cache_ast",
    "_parse_file_cached",
}

lines = content.splitlines()
new_lines = []
skip = False
ast_cache_removed = False

def is_top_level_start(line):
    # Detect start of new top-level block
    if re.match(r"^(async )?def ", line): return True
    if line.startswith("class "): return True
    if line.startswith("@"): return True
    if re.match(r"^[A-Z][A-Z0-9_]*(\s*:\s*.*)?\s*=", line): return True
    if line.startswith("if TYPE_CHECKING:"): return True
    return False

i = 0
while i < len(lines):
    line = lines[i]
    
    if not skip:
        # Check for _AST_CACHE global
        if line.startswith("_AST_CACHE:") or line.startswith("_AST_CACHE ="):
            print(f"Removing _AST_CACHE at line {i+1}")
            i += 1
            continue

        # Check for start of function to remove
        match = re.match(r"^(async )?def (\w+)\(", line)
        if match:
            func_name = match.group(2)
            if func_name in functions_to_remove:
                print(f"Removing {func_name} at line {i+1}")
                skip = True
                i += 1
                continue
        
        # Also check for decorators on functions to remove
        # This is harder because decorator comes before def.
        # But commonly our functions might have @tracker or similar.
        # If we are NOT skipping, and we see @, we need to peek ahead to see if it decorates a target function.
        if line.startswith("@"):
            # Peek ahead
            j = i + 1
            found_def = False
            target_func = None
            while j < len(lines) and j < i + 10: # Look ahead a bit
                peek = lines[j]
                match_def = re.match(r"^(async )?def (\w+)\(", peek)
                if match_def:
                    target_func = match_def.group(2)
                    found_def = True
                    break
                if not peek.startswith("@") and peek.strip():
                    break # Not a decorator stack
                j += 1
            
            if found_def and target_func in functions_to_remove:
                print(f"Removing decorator for {target_func} at line {i+1}")
                skip = True # Start skipping from the decorator
                i += 1
                continue

        new_lines.append(line)
        i += 1
    else:
        # We are skipping. Stop if we hit a new top level block
        if line.strip() and is_top_level_start(line):
            skip = False
            # Reprocess this line
            continue
        
        i += 1

# Prepare imports
imports = [
    "from code_scalpel.mcp.helpers.context_helpers import (",
    "    crawl_project,",
    "    get_file_context,",
    "    get_symbol_references,",
    "    _crawl_project_discovery,",
    "    _crawl_project_sync,",
    "    _get_file_context_sync,",
    "    _get_symbol_references_sync,",
    ")",
]

# Check if we need to alias parse_file_cached
joined_content = "\n".join(new_lines)
if "_parse_file_cached(" in joined_content:
    imports.append("from code_scalpel.mcp.helpers.ast_helpers import parse_file_cached as _parse_file_cached")

# Finds insertion point (after existing imports)
insert_pos = 0
last_import_idx = 0
for idx, line in enumerate(new_lines):
    if line.startswith("import ") or line.startswith("from "):
        last_import_idx = idx

# Insert after last import
if last_import_idx > 0:
    insert_pos = last_import_idx + 1
else:
    insert_pos = 0

new_lines[insert_pos:insert_pos] = imports

server_path.write_text("\n".join(new_lines), encoding="utf-8")
print("Done.")
