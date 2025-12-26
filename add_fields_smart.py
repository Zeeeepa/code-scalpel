
import os

file_path = "src/code_scalpel/mcp/server.py"
target_class = "class FileContextResult(BaseModel):"
target_field = '    error: str | None = Field(default=None, description="Error message if failed")'
insertion = """
    # [20251229_FEATURE] v3.3.0 - Pro/Enterprise fields
    semantic_summary: Optional[str] = Field(default=None, description="AI-generated semantic summary (Pro)")
    related_imports: List[str] = Field(default_factory=list, description="Related imports from other files (Pro)")
    pii_redacted: bool = Field(default=False, description="Whether PII was redacted (Enterprise)")
    access_controlled: bool = Field(default=False, description="Whether access control was applied (Enterprise)")
"""

with open(file_path, "r") as f:
    lines = f.readlines()

new_lines = []
in_target_class = False
inserted = False

for line in lines:
    new_lines.append(line)
    
    if target_class in line:
        in_target_class = True
        
    if in_target_class and target_field.strip() in line.strip():
        if not inserted:
            new_lines.append(insertion)
            inserted = True
            in_target_class = False # Stop looking after insertion
            print("Inserted fields into FileContextResult.")

if inserted:
    with open(file_path, "w") as f:
        f.writelines(new_lines)
else:
    print("Target not found or already inserted.")
