import sys
from pathlib import Path

file_path = Path("src/code_scalpel/mcp/server.py")
content = file_path.read_text(encoding="utf-8")

target_marker = 'total_imports: int = Field(default=0, description="Total imports before truncation")'
insertion = """
    
    # [20251229_FEATURE] v3.3.0 - Pro/Enterprise fields
    semantic_summary: str | None = Field(default=None, description="AI-generated semantic summary (Pro)")
    related_imports: list[str] = Field(default_factory=list, description="Related imports from other files (Pro)")
    pii_redacted: bool = Field(default=False, description="Whether PII was redacted (Enterprise)")
    access_controlled: bool = Field(default=False, description="Whether access control was applied (Enterprise)")"""

if target_marker in content:
    if "semantic_summary: str | None" not in content:
        new_content = content.replace(target_marker, target_marker + insertion)
        file_path.write_text(new_content, encoding="utf-8")
        print("Successfully added fields.")
    else:
        print("Fields already exist.")
else:
    print("Target marker not found.")
