
import os

file_path = "src/code_scalpel/mcp/server.py"

with open(file_path, "r") as f:
    lines = f.readlines()

# Find the line with semantic_summary = None
for i, line in enumerate(lines):
    if "semantic_summary = None" in line:
        print(f"Found target at {i+1}: {repr(line)}")
        
        # Check if lines = code.splitlines() is already there
        prev_lines = lines[i-5:i]
        if any("lines = code.splitlines()" in l for l in prev_lines):
            print("lines = code.splitlines() already exists.")
            break
            
        # Insert lines = code.splitlines() before the comment block
        # The comment block starts a few lines above
        insert_idx = i
        while insert_idx > 0 and "# [20251229_FEATURE] Pro: Semantic Summarization" not in lines[insert_idx]:
            insert_idx -= 1
            
        if insert_idx > 0:
            print(f"Found comment at {insert_idx+1}: {repr(lines[insert_idx])}")
            # Insert before the comment
            indent = " " * 8
            new_line = indent + "lines = code.splitlines()\n"
            lines.insert(insert_idx, new_line)
            print(f"Inserted '{new_line.strip()}' at line {insert_idx+1}")
            
            with open(file_path, "w") as f:
                f.writelines(lines)
            print("File updated.")
            break
        else:
            print("Could not find comment block start.")
