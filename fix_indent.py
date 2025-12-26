
import os

file_path = "src/code_scalpel/mcp/server.py"

with open(file_path, "r") as f:
    lines = f.readlines()

# Find the line with pii_redacted = False
for i, line in enumerate(lines):
    if "pii_redacted = False" in line:
        print(f"Found error line at {i+1}: {repr(line)}")
        # Check previous line
        prev_line = lines[i-1]
        while not prev_line.strip(): # Skip empty lines
            prev_line = lines[lines.index(prev_line)-1]
            
        print(f"Previous line: {repr(prev_line)}")
        
        # Calculate indentation
        prev_indent = len(prev_line) - len(prev_line.lstrip())
        curr_indent = len(line) - len(line.lstrip())
        
        print(f"Previous indent: {prev_indent}")
        print(f"Current indent: {curr_indent}")
        
        if curr_indent != prev_indent:
            print("Indentation mismatch! Fixing...")
            # Fix indentation for the whole block
            # The block starts at i and goes until... next blank line or dedent?
            # I inserted a block, so I know what it looks like.
            
            # The block is:
            # pii_redacted = False
            # if "pii_redaction" in caps_set:
            #     import re
            #     # Simple email redaction for demo
            #     original_code = code
            #     code = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', code)
            #     if code != original_code:
            #         pii_redacted = True
            
            # I need to re-indent these lines to match prev_indent
            
            indent_str = " " * prev_indent
            
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
