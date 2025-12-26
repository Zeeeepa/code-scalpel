
import os

file_path = "src/code_scalpel/mcp/server.py"

with open(file_path, "r") as f:
    lines = f.readlines()

# Find the success return block
# It starts with `return FileContextResult(` and has `total_imports=total_imports,` as the last field before closing parenthesis.

start_idx = -1
end_idx = -1

for i in range(len(lines)):
    if "return FileContextResult(" in lines[i]:
        # Check context to ensure it's the right one
        # It should be preceded by `imports_truncated = total_imports > 20`
        if i > 0 and "imports_truncated = total_imports > 20" in lines[i-2]: # Check line i-2 or i-3 depending on empty lines
             start_idx = i
             break
        if i > 0 and "imports_truncated = total_imports > 20" in lines[i-3]:
             start_idx = i
             break

if start_idx != -1:
    # Find end of block
    for i in range(start_idx, len(lines)):
        if ")" in lines[i] and lines[i].strip() == ")":
            end_idx = i
            break

if start_idx != -1 and end_idx != -1:
    print(f"Found block at {start_idx+1}-{end_idx+1}")
    
    # Construct new block
    new_block = [
        "            return FileContextResult(\n",
        "                success=True,\n",
        "                file_path=str(path),\n",
        "                language=\"python\",\n",
        "                line_count=len(lines),\n",
        "                functions=functions,\n",
        "                classes=classes,\n",
        "                imports=imports[:20],\n",
        "                exports=exports,\n",
        "                complexity_score=complexity,\n",
        "                has_security_issues=has_security_issues,\n",
        "                summary=summary,\n",
        "                imports_truncated=imports_truncated,\n",
        "                total_imports=total_imports,\n",
        "                semantic_summary=semantic_summary,\n",
        "                related_imports=related_imports,\n",
        "                pii_redacted=pii_redacted,\n",
        "                access_controlled=access_controlled,\n",
        "            )\n"
    ]
    
    # Replace lines
    lines[start_idx:end_idx+1] = new_block
    
    with open(file_path, "w") as f:
        f.writelines(lines)
    print("Updated python return block.")
else:
    print("Could not find python return block.")
