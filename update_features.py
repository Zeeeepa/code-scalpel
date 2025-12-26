
import os

file_path = "src/code_scalpel/licensing/features.py"

old_block = """    "get_file_context": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_context"},
            "limits": {
                "context_lines": 10,
            },
            "description": "Basic file context (±10 lines)",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_context",
                "extended_context"
            },
            "limits": {
                "context_lines": 50,
            },
            "description": "Extended context (±50 lines)",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_context",
                "extended_context",
                "semantic_context", "related_symbols"
            },
            "limits": {
                "context_lines": None,
            },
            "description": "Semantic context with related symbols",
        },
    },"""

new_block = """    "get_file_context": {
        "community": {
            "enabled": True,
            "capabilities": {"basic_context"},
            "limits": {
                "context_lines": 10,
            },
            "description": "Basic file context (±10 lines)",
        },
        "pro": {
            "enabled": True,
            "capabilities": {
                "basic_context",
                "extended_context",
                "semantic_summarization", "related_imports_inclusion"
            },
            "limits": {
                "context_lines": 50,
            },
            "description": "Extended context with semantic summary",
        },
        "enterprise": {
            "enabled": True,
            "capabilities": {
                "basic_context",
                "extended_context",
                "semantic_summarization", "related_imports_inclusion",
                "pii_redaction", "rbac_aware_retrieval"
            },
            "limits": {
                "context_lines": None,
            },
            "description": "Enterprise context with PII redaction and RBAC",
        },
    },"""

with open(file_path, "r") as f:
    content = f.read()

if old_block in content:
    new_content = content.replace(old_block, new_block)
    with open(file_path, "w") as f:
        f.write(new_content)
    print("Successfully updated features.py")
else:
    print("Could not find old block in features.py")
    # Debug: print surrounding lines
    idx = content.find('"get_file_context":')
    if idx != -1:
        print("Found start of block:")
        print(content[idx:idx+500])
    else:
        print("Could not find 'get_file_context' key")
