#!/usr/bin/env python3
"""
Fix imports from code_scalpel.security.analyzers to use specific modules.

[20251225_BUGFIX] Fix imports after backward compat stub removal.
"""

import re
from pathlib import Path

# Mapping of symbols to their actual modules
SYMBOL_TO_MODULE = {
    # From taint_tracker.py
    "TaintSource": "taint_tracker",
    "SecuritySink": "taint_tracker",
    "SINK_PATTERNS": "taint_tracker",
    "SANITIZER_REGISTRY": "taint_tracker",
    "load_sanitizers_from_config": "taint_tracker",
    "register_sanitizer": "taint_tracker",
    "TaintedValue": "taint_tracker",
    "Vulnerability": "taint_tracker",
    "SSR_SINK_PATTERNS": "taint_tracker",
    "SSR_FRAMEWORK_IMPORTS": "taint_tracker",
    
    # From security_analyzer.py
    "find_sql_injections": "security_analyzer",
    "find_xss": "security_analyzer",
    "find_command_injections": "security_analyzer",
    "find_path_traversals": "security_analyzer",
    
    # From cross_file_taint.py
    "CrossFileTaintResult": "cross_file_taint",
    "CrossFileTaintFlow": "cross_file_taint",
    "CrossFileVulnerability": "cross_file_taint",
    "CrossFileSink": "cross_file_taint",
    "FunctionTaintInfo": "cross_file_taint",
    "SinkInfo": "cross_file_taint",
    "CallInfo": "cross_file_taint",
    "DANGEROUS_SINKS": "cross_file_taint",
    "TAINT_SOURCES": "cross_file_taint",
}

# Symbols that ARE in __all__ (can stay at package level)
PACKAGE_LEVEL_SYMBOLS = {
    "SecurityAnalyzer",
    "SecurityAnalysisResult",
    "TaintTracker",
    "TaintLevel",
    "TaintInfo",
    "UnifiedSinkDetector",
    "DetectedSink",
    "CrossFileTaintTracker",
}


def fix_file(file_path: Path) -> bool:
    """Fix imports in a single file. Returns True if modified."""
    content = file_path.read_text()
    original = content
    
    # Find all imports from code_scalpel.security.analyzers
    # Pattern handles both single-line and multi-line imports
    # Use a more precise pattern that captures everything including closing paren
    pattern = r'from\s+code_scalpel\.security\.analyzers\s+import\s+(\([^)]+\)|[^\n]+)'
    
    def replace_import(match):
        imports_str = match.group(1)
        
        # Remove parentheses if present
        if imports_str.startswith('(') and imports_str.endswith(')'):
            imports_str = imports_str[1:-1]
        
        # Split by comma and clean up
        symbols = [s.strip() for s in imports_str.split(',') if s.strip()]
        
        # Group symbols by module
        by_module = {}
        package_level = []
        
        for symbol in symbols:
            # Remove comments and whitespace
            symbol = symbol.split('#')[0].strip()
            if not symbol:
                continue
                
            if symbol in PACKAGE_LEVEL_SYMBOLS:
                package_level.append(symbol)
            elif symbol in SYMBOL_TO_MODULE:
                module = SYMBOL_TO_MODULE[symbol]
                if module not in by_module:
                    by_module[module] = []
                by_module[module].append(symbol)
            else:
                # Unknown symbol - keep at package level and let it fail for debugging
                package_level.append(symbol)
        
        # Build replacement imports
        imports = []
        
        # Package-level imports
        if package_level:
            if len(package_level) == 1:
                imports.append(f"from code_scalpel.security.analyzers import {package_level[0]}")
            else:
                formatted = ", ".join(package_level)
                imports.append(f"from code_scalpel.security.analyzers import ({formatted})")
        
        # Module-specific imports
        for module, symbols_list in sorted(by_module.items()):
            module_path = f"code_scalpel.security.analyzers.{module}"
            if len(symbols_list) == 1:
                imports.append(f"from {module_path} import {symbols_list[0]}")
            else:
                formatted = ", ".join(sorted(symbols_list))
                imports.append(f"from {module_path} import ({formatted})")
        
        return "\n".join(imports)
    
    # Replace all matches
    content = re.sub(pattern, replace_import, content, flags=re.MULTILINE)
    
    if content != original:
        file_path.write_text(content)
        return True
    return False


def main():
    """Fix all test files."""
    tests_dir = Path("tests")
    modified = []
    
    for test_file in sorted(tests_dir.glob("test_*.py")):
        try:
            if fix_file(test_file):
                modified.append(test_file)
                print(f"✓ Fixed {test_file.name}")
        except Exception as e:
            print(f"✗ Error in {test_file.name}: {e}")
    
    print(f"\n{len(modified)} files modified")


if __name__ == "__main__":
    main()
