
filename = "src/code_scalpel/mcp/server.py"
with open(filename) as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "class FileContextResult" in line:
        print(f"Found at line {i+1}: {line.strip()}")
    if "def get_file_context" in line:
        print(f"Found at line {i+1}: {line.strip()}")
