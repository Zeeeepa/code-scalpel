
import os

file_path = "src/code_scalpel/mcp/server.py"

with open(file_path, "r") as f:
    lines = f.readlines()

# Find the line with pii_redacted = False
for i, line in enumerate(lines):
    if "pii_redacted = False" in line:
        print(f"Found error line at {i+1}: {repr(line)}")
        
        # Find code = path.read_text
        # It should be a few lines above
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
            
            # Fix PII block (8 lines)
            # Also fix the comment line if it exists
            comment_idx = i - 1
            if "Enterprise: PII Redaction" in lines[comment_idx]:
                lines[comment_idx] = indent_str + "# [20251229_FEATURE] Enterprise: PII Redaction\n"
            
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
