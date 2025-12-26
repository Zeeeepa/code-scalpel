
import os

file_path = "src/code_scalpel/mcp/server.py"

with open(file_path, "r") as f:
    lines = f.readlines()

# Find the line with semantic_summary = None
for i, line in enumerate(lines):
    if "semantic_summary = None" in line:
        print(f"Found error line at {i+1}: {repr(line)}")
        
        # Find code = path.read_text
        ref_idx = i - 1
        while ref_idx >= 0 and "code = path.read_text" not in lines[ref_idx]:
            ref_idx -= 1
            
        if ref_idx < 0:
            print("Could not find reference line.")
            break
            
        ref_line = lines[ref_idx]
        print(f"Reference line ({ref_idx+1}): {repr(ref_line)}")
        
        # Calculate indentation
        ref_indent = len(ref_line) - len(ref_line.lstrip())
        curr_indent = len(line) - len(line.lstrip())
        
        print(f"Reference indent: {ref_indent}")
        print(f"Current indent: {curr_indent}")
        
        if curr_indent != ref_indent:
            print("Indentation mismatch! Fixing...")
            
            indent_str = " " * ref_indent
            
            # Fix Semantic Summary block (approx 15 lines)
            # I need to be careful to fix the whole block
            # The block ends before `detected_lang = ...`
            
            # Find end of block
            end_idx = i
            while end_idx < len(lines) and "detected_lang =" not in lines[end_idx]:
                end_idx += 1
            
            print(f"Fixing lines {i+1} to {end_idx}")
            
            for j in range(i, end_idx):
                if lines[j].strip(): # Only fix non-empty lines
                    # Calculate relative indent
                    current_line_indent = len(lines[j]) - len(lines[j].lstrip())
                    relative_indent = current_line_indent - curr_indent
                    
                    lines[j] = indent_str + (" " * relative_indent) + lines[j].lstrip()
            
            with open(file_path, "w") as f:
                f.writelines(lines)
            print("Fixed indentation.")
            break
