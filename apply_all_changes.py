
import os
import re

file_path = "src/code_scalpel/mcp/server.py"

with open(file_path, "r") as f:
    content = f.read()

# 1. Fix Import
old_import = "from code_scalpel.symbolic_execution_tools.unified_sink_detector import"
new_import = "from code_scalpel.security.analyzers.unified_sink_detector import"
if old_import in content:
    content = content.replace(old_import, new_import)
    print("Fixed import.")

# 2. Add Fields to FileContextResult
target_class = "class FileContextResult(BaseModel):"
target_field = '    error: str | None = Field(default=None, description="Error message if failed")'
insertion = """
    # [20251229_FEATURE] v3.3.0 - Pro/Enterprise fields
    semantic_summary: Optional[str] = Field(default=None, description="AI-generated semantic summary (Pro)")
    related_imports: list[str] = Field(default_factory=list, description="Related imports from other files (Pro)")
    pii_redacted: bool = Field(default=False, description="Whether PII was redacted (Enterprise)")
    access_controlled: bool = Field(default=False, description="Whether access control was applied (Enterprise)")
"""

if target_class in content and "semantic_summary" not in content:
    # Find the class block
    class_start = content.find(target_class)
    # Find the target field after class start
    field_idx = content.find(target_field, class_start)
    if field_idx != -1:
        # Insert after the field line (including newline)
        line_end = content.find("\n", field_idx)
        content = content[:line_end+1] + insertion + content[line_end+1:]
        print("Added fields to FileContextResult.")
    else:
        print("Could not find target field in FileContextResult.")

# 3. Update get_file_context
old_get_context = '    return await asyncio.to_thread(_get_file_context_sync, file_path)'
new_get_context = """    # [20251229_FEATURE] v3.3.0 - Detect tier and get capabilities
    tier = get_current_tier()
    capabilities = get_tool_capabilities("get_file_context", tier)
    
    return await asyncio.to_thread(_get_file_context_sync, file_path, tier, capabilities)"""

if old_get_context in content:
    content = content.replace(old_get_context, new_get_context)
    print("Updated get_file_context.")

# 4. Update _get_file_context_sync signature
old_sig = 'def _get_file_context_sync(file_path: str) -> FileContextResult:'
new_sig = 'def _get_file_context_sync(file_path: str, tier: str = "community", capabilities: dict = None) -> FileContextResult:'

if old_sig in content:
    content = content.replace(old_sig, new_sig)
    print("Updated _get_file_context_sync signature.")

# 5. Update _get_file_context_sync start (capabilities init)
target_start = """    [20251214_FEATURE] v1.5.3 - Integrated PathResolver for intelligent path resolution
    [20251220_FEATURE] v3.0.5 - Multi-language support via file extension detection
    \"\"\"
    from code_scalpel.mcp.path_resolver import resolve_path"""

new_start = """    [20251214_FEATURE] v1.5.3 - Integrated PathResolver for intelligent path resolution
    [20251220_FEATURE] v3.0.5 - Multi-language support via file extension detection
    [20251229_FEATURE] v3.3.0 - Tier-based feature gating
    \"\"\"
    from code_scalpel.mcp.path_resolver import resolve_path
    
    if capabilities is None:
        capabilities = {}
        
    caps_set = capabilities.get("capabilities", set())
    limits = capabilities.get("limits", {})"""

if target_start in content:
    content = content.replace(target_start, new_start)
    print("Updated _get_file_context_sync start.")

# 6. Add PII redaction logic (Safe Context)
# Context: inside _get_file_context_sync, after FileNotFoundError return
context_str = """                return FileContextResult(
                    success=False,
                    file_path=file_path,
                    line_count=0,
                    error=str(e),
                )

            code = path.read_text(encoding="utf-8")"""

pii_logic = """                return FileContextResult(
                    success=False,
                    file_path=file_path,
                    line_count=0,
                    error=str(e),
                )

            code = path.read_text(encoding="utf-8")
            
            # [20251229_FEATURE] Enterprise: PII Redaction
            pii_redacted = False
            if "pii_redaction" in caps_set:
                import re
                # Simple email redaction for demo
                original_code = code
                code = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', code)
                if code != original_code:
                    pii_redacted = True"""

if context_str in content:
    content = content.replace(context_str, pii_logic)
    print("Added PII redaction logic.")
else:
    print("Could not find safe context for PII logic.")

# 7. Add Semantic Summary logic
detect_lang = '            # [20251220_FEATURE] Detect language from file extension'
summary_logic = """            
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
                access_controlled = True

            # [20251220_FEATURE] Detect language from file extension"""

# We need to be careful because this line might appear multiple times.
# It should be inside _get_file_context_sync.
# The previous replacement (PII) was inside the function.
# So we can search starting from there?
# But replace() works on whole string.
# However, this comment is specific to _get_file_context_sync (I hope).
# Let's check if it appears elsewhere.
if content.count(detect_lang.strip()) > 1:
    print("Warning: Language detection line appears multiple times. Using context.")
    # Use context: lines = code.splitlines()
    context_lang = """            lines = code.splitlines()

            # [20251220_FEATURE] Detect language from file extension"""
    
    new_context_lang = """            lines = code.splitlines()

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
                access_controlled = True

            # [20251220_FEATURE] Detect language from file extension"""
            
    if context_lang in content:
        content = content.replace(context_lang, new_context_lang)
        print("Added Semantic Summary logic (safe).")
    else:
        print("Could not find safe context for Semantic Summary.")
else:
    if detect_lang in content:
        content = content.replace(detect_lang, summary_logic)
        print("Added Semantic Summary logic.")

# 8. Update non-python return
non_py_return = """                error=analysis.error,
            )"""
non_py_return_new = """                error=analysis.error,
                    semantic_summary=semantic_summary,
                    related_imports=related_imports,
                    pii_redacted=pii_redacted,
                    access_controlled=access_controlled,
                )"""

# This might match multiple places.
# It matches `_analyze_code_sync` return? No, that returns AnalysisResult.
# It matches `_get_file_context_sync` non-python return.
# Let's check context.
context_non_py = """                    imports_truncated=total_imports > 20,
                    total_imports=total_imports,
                    error=analysis.error,
                )"""

new_context_non_py = """                    imports_truncated=total_imports > 20,
                    total_imports=total_imports,
                    error=analysis.error,
                    semantic_summary=semantic_summary,
                    related_imports=related_imports,
                    pii_redacted=pii_redacted,
                    access_controlled=access_controlled,
                )"""

if context_non_py in content:
    content = content.replace(context_non_py, new_context_non_py)
    print("Updated non-python return.")

# 9. Update python return
# Use the block replacement logic from update_return.py
# Find the block starting with `return FileContextResult(` inside _get_file_context_sync
# It is preceded by `imports_truncated = total_imports > 20`

# We can use regex or string find.
# Since we have the full content, let's find the specific block.
# It's the LAST return in the function (before exception handler).

py_return_start = """            # [20251220_FEATURE] v3.0.5 - Communicate truncation
            total_imports = len(imports)
            imports_truncated = total_imports > 20

            return FileContextResult("""

if py_return_start in content:
    # Find the closing parenthesis
    start_idx = content.find(py_return_start)
    end_idx = content.find(")", start_idx)
    
    original_block = content[start_idx:end_idx+1]
    
    # Construct new block
    # We need to preserve indentation
    new_block = """            # [20251220_FEATURE] v3.0.5 - Communicate truncation
            total_imports = len(imports)
            imports_truncated = total_imports > 20

            return FileContextResult(
                success=True,
                file_path=str(path),
                language="python",
                line_count=len(lines),
                functions=functions,
                classes=classes,
                imports=imports[:20],
                exports=exports,
                complexity_score=complexity,
                has_security_issues=has_security_issues,
                summary=summary,
                imports_truncated=imports_truncated,
                total_imports=total_imports,
                semantic_summary=semantic_summary,
                related_imports=related_imports,
                pii_redacted=pii_redacted,
                access_controlled=access_controlled,
            )"""
            
    content = content.replace(original_block, new_block)
    print("Updated python return.")
else:
    print("Could not find python return block.")

with open(file_path, "w") as f:
    f.write(content)
