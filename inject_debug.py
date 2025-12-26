
import os

file_path = "src/code_scalpel/mcp/server.py"
target_line = '    tier = get_current_tier()'
insertion = """    print(f"DEBUG: tier={tier}")
    capabilities = get_tool_capabilities("get_file_context", tier)
    print(f"DEBUG: capabilities={capabilities}")"""

with open(file_path, "r") as f:
    content = f.read()

if target_line in content:
    # Replace the lines to inject debug prints
    # Note: I need to match the exact lines
    old_code = """    tier = get_current_tier()
    capabilities = get_tool_capabilities("get_file_context", tier)"""
    
    new_code = """    tier = get_current_tier()
    print(f"DEBUG: tier={tier}")
    capabilities = get_tool_capabilities("get_file_context", tier)
    print(f"DEBUG: capabilities={capabilities}")"""
    
    new_content = content.replace(old_code, new_code)
    with open(file_path, "w") as f:
        f.write(new_content)
    print("Injected debug prints.")
else:
    print("Target line not found.")
