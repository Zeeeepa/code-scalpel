
import os

file_path = "src/code_scalpel/mcp/server.py"

with open(file_path, "r") as f:
    lines = f.readlines()

# Find the line with pii_redacted = False
for i, line in enumerate(lines):
    if "pii_redacted = False" in line:
        print(f"Found error line at {i+1}: {repr(line)}")
        
        # Find previous non-empty line
        prev_idx = i - 1
        while prev_idx >= 0 and not lines[prev_idx].strip():
            prev_idx -= 1
            
        if prev_idx < 0:
            print("Could not find previous line.")
            break
            
        prev_line = lines[prev_idx]
        print(f"Previous line ({prev_idx+1}): {repr(prev_line)}")
        
        # Calculate indentation
        prev_indent = len(prev_line) - len(prev_line.lstrip())
        curr_indent = len(line) - len(line.lstrip())
        
        print(f"Previous indent: {prev_indent}")
        print(f"Current indent: {curr_indent}")
        
        if curr_indent != prev_indent:
            print("Indentation mismatch! Fixing...")
            
            indent_str = " " * prev_indent
            
            # Fix PII block (8 lines)
            lines[i] = indent_str + "pii_redacted = False\n"
            lines[i+1] = indent_str + 'if "pii_redaction" in caps_set:\n'
            lines[i+2] = indent_str + "    import re\n"
            lines[i+3] = indent_str + "    # Simple email redaction for demo\n"
            lines[i+4] = indent_str + "    original_code = code\n"
            lines[i+5] = indent_str + "    code = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', code)\n"
            lines[i+6] = indent_str + "    if code != original_code:\n"
            lines[i+7] = indent_str + "        pii_redacted = True\n"
            
            with open(file_path, "w") as f:
                f.writelines(lines)
            print("Fixed indentation.")
            break
