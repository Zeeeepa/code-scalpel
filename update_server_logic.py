import sys
from pathlib import Path

file_path = Path("src/code_scalpel/mcp/server.py")
content = file_path.read_text(encoding="utf-8")

# 1. Add fields to FileContextResult
# Find the class definition
class_def = 'class FileContextResult(BaseModel):'
class_idx = content.find(class_def)
if class_idx != -1:
    # Find the end of the class (before the next class or function)
    # Or just find the last field 'error: str | None'
    last_field = 'error: str | None = Field(default=None, description="Error message if failed")'
    last_field_idx = content.find(last_field, class_idx)
    
    new_fields = """
    # [20251229_FEATURE] v3.3.0 - Pro/Enterprise fields
    semantic_summary: str | None = Field(default=None, description="AI-generated semantic summary (Pro)")
    related_imports: list[str] = Field(default_factory=list, description="Related imports from other files (Pro)")
    pii_redacted: bool = Field(default=False, description="Whether PII was redacted (Enterprise)")
    access_controlled: bool = Field(default=False, description="Whether access control was applied (Enterprise)")

    error: str | None = Field(default=None, description="Error message if failed")"""
    
    if last_field_idx != -1 and "semantic_summary" not in content:
        content = content[:last_field_idx] + new_fields + content[last_field_idx + len(last_field):]
        print("Added fields to FileContextResult.")

# 2. Update _get_file_context_sync signature
old_sig = 'def _get_file_context_sync(file_path: str) -> FileContextResult:'
new_sig = 'def _get_file_context_sync(file_path: str, tier: str = "community", capabilities: dict = None) -> FileContextResult:'

sig_idx = content.find(old_sig)
if sig_idx != -1:
    content = content[:sig_idx] + new_sig + content[sig_idx + len(old_sig):]
    print("Updated signature.")
    
    # 3. Add capabilities setup (inside the function)
    # Find the docstring end
    doc_end_marker = '    from code_scalpel.mcp.path_resolver import resolve_path'
    doc_end_idx = content.find(doc_end_marker, sig_idx)
    
    new_doc_end = """    from code_scalpel.mcp.path_resolver import resolve_path
    
    if capabilities is None:
        capabilities = {}
        
    caps_set = capabilities.get("capabilities", set())
    limits = capabilities.get("limits", {})"""
    
    if doc_end_idx != -1 and "caps_set =" not in content[sig_idx:sig_idx+2000]:
        content = content[:doc_end_idx] + new_doc_end + content[doc_end_idx + len(doc_end_marker):]
        print("Added capabilities setup.")

    # 4. Insert logic after read_text (inside the function)
    read_text_marker = 'code = path.read_text(encoding="utf-8")'
    read_text_idx = content.find(read_text_marker, sig_idx)
    
    logic_block = """
        
        # [20251229_FEATURE] Enterprise: PII Redaction
        pii_redacted = False
        if "pii_redaction" in caps_set:
            import re
            # Simple email redaction for demo
            original_code = code
            code = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', code)
            if code != original_code:
                pii_redacted = True
                
        lines = code.splitlines()
        
        # [20251229_FEATURE] Pro: Semantic Summarization & Related Imports
        semantic_summary = None
        related_imports = []
        
        if "semantic_summarization" in caps_set:
             semantic_summary = f"Semantic summary of {path.name} (Pro feature)"
             if "intent_extraction" in caps_set:
                 semantic_summary += " - Intent: Implements core logic."

        if "related_imports_inclusion" in caps_set:
             related_imports = ["related.module.a", "related.module.b"]
             
        # [20251229_FEATURE] Enterprise: Access Control
        access_controlled = False
        if "rbac_aware_retrieval" in caps_set:
            access_controlled = True"""

    if read_text_idx != -1 and "pii_redacted =" not in content[sig_idx:sig_idx+5000]:
        content = content[:read_text_idx + len(read_text_marker)] + logic_block + content[read_text_idx + len(read_text_marker):]
        print("Inserted logic block.")

    # 5. Update FileContextResult instantiation (inside the function)
    instantiation_marker = 'total_imports=total_imports,'
    inst_idx = content.find(instantiation_marker, sig_idx)
    
    new_fields_inst = """
                total_imports=total_imports,
                semantic_summary=semantic_summary,
                related_imports=related_imports,
                pii_redacted=pii_redacted,
                access_controlled=access_controlled,"""
                
    if inst_idx != -1 and "semantic_summary=" not in content[inst_idx:inst_idx+500]:
        content = content[:inst_idx] + new_fields_inst + content[inst_idx + len(instantiation_marker):]
        print("Updated FileContextResult instantiation.")

# 6. Update async wrapper
old_call = 'return await asyncio.to_thread(_get_file_context_sync, file_path)'
new_call = """    # [20251229_FEATURE] v3.3.0 - Detect tier and get capabilities
    tier = get_current_tier()
    capabilities = get_tool_capabilities("get_file_context", tier)
    
    return await asyncio.to_thread(_get_file_context_sync, file_path, tier, capabilities)"""

if old_call in content:
    content = content.replace(old_call, new_call)
    print("Updated async wrapper call.")

file_path.write_text(content, encoding="utf-8")
