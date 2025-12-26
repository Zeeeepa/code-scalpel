
import os

file_path = "src/code_scalpel/mcp/server.py"

with open(file_path, "r") as f:
    content = f.read()

old_code = """    # [20251229_FEATURE] v3.3.0 - Detect tier and get capabilities
    tier = get_current_tier()
    capabilities = get_tool_capabilities("get_file_context", tier)"""

new_code = """    # [20251229_FEATURE] v3.3.0 - Detect tier and get capabilities
    from code_scalpel.licensing import get_tool_capabilities
    tier = _get_current_tier()
    capabilities = get_tool_capabilities("get_file_context", tier)"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, "w") as f:
        f.write(content)
    print("Fixed get_file_context.")
else:
    print("Could not find code block.")
    # Debug: print what is there
    idx = content.find("# [20251229_FEATURE] v3.3.0 - Detect tier and get capabilities")
    if idx != -1:
        print("Found comment:")
        print(repr(content[idx:idx+200]))
