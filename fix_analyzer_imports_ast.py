#!/usr/bin/env python3
"""
Properly fix security.analyzers imports by parsing AST.

[20251225_BUGFIX] Fix imports after backward compat stub removal using AST.
"""

import ast
from pathlib import Path
from typing import Set, List, Tuple

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
    "analyze_security": "security_analyzer",
    
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


class ImportFixer(ast.NodeTransformer):
    """Fix imports from security.analyzers."""
    
    def __init__(self):
        self.new_imports: List[Tuple[str, List[str]]] = []
        self.found_target_import = False
    
    def visit_ImportFrom(self, node):
        # Check if this is the target import
        if (node.module == "code_scalpel.security.analyzers" or 
            node.module == "code_scalpel.symbolic_execution_tools.security_analyzer" or
            node.module == "code_scalpel.symbolic_execution_tools.taint_tracker" or
            node.module == "code_scalpel.symbolic_execution_tools.cross_file_taint"):
            
            self.found_target_import = True
            
            # Group imported names by their target module
            by_module = {}
            package_level = []
            
            for alias in node.names:
                name = alias.name
                
                if name in PACKAGE_LEVEL_SYMBOLS:
                    package_level.append(name)
                elif name in SYMBOL_TO_MODULE:
                    target_module = SYMBOL_TO_MODULE[name]
                    if target_module not in by_module:
                        by_module[target_module] = []
                    by_module[target_module].append(name)
                else:
                    # Unknown - keep at package level
                    package_level.append(name)
            
            # Create new import nodes
            new_nodes = []
            
            # Package-level imports
            if package_level:
                new_node = ast.ImportFrom(
                    module="code_scalpel.security.analyzers",
                    names=[ast.alias(name=n, asname=None) for n in package_level],
                    level=0
                )
                new_nodes.append(new_node)
            
            # Module-specific imports
            for module, names in sorted(by_module.items()):
                new_node = ast.ImportFrom(
                    module=f"code_scalpel.security.analyzers.{module}",
                    names=[ast.alias(name=n, asname=None) for n in sorted(names)],
                    level=0
                )
                new_nodes.append(new_node)
            
            # Return first node, store rest
            if len(new_nodes) == 1:
                return new_nodes[0]
            elif len(new_nodes) > 1:
                # Store for later insertion
                self.new_imports = new_nodes[1:]
                return new_nodes[0]
            else:
                return None
        
        return node


def fix_file_ast(file_path: Path) -> bool:
    """Fix imports using AST. Returns True if modified."""
    try:
        content = file_path.read_text()
        tree = ast.parse(content)
        
        fixer = ImportFixer()
        new_tree = fixer.visit(tree)
        
        if fixer.found_target_import:
            # Generate new code
            new_code = ast.unparse(new_tree)
            if new_code != content:
                file_path.write_text(new_code)
                return True
        
        return False
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return False


def main():
    """Fix all test files."""
    tests_dir = Path("tests")
    error_files = [
        "test_coverage_final_17.py",
        "test_coverage_final_33.py",
        "test_coverage_final_95.py",
        "test_coverage_final_boost.py",
        "test_coverage_final_push.py",
        "test_coverage_last_push.py",
        "test_coverage_perfect.py",
        "test_coverage_push_95.py",
        "test_coverage_ultra_final.py",
        "test_deep_coverage_95.py",
        "test_final_95_push.py",
        "test_frontend_input_tracker.py",
        "test_graphql_schema_tracker.py",
        "test_grpc_contract_analyzer.py",
        "test_java_security_sinks.py",
        "test_kafka_taint_tracker.py",
        "test_new_vulnerabilities.py",
        "test_security_analysis.py",
        "test_v1_4_specifications.py",
        "test_vulnerability_scanner.py",
    ]
    
    modified = []
    
    for filename in sorted(error_files):
        test_file = tests_dir / filename
        if test_file.exists():
            try:
                if fix_file_ast(test_file):
                    modified.append(test_file)
                    print(f"✓ Fixed {filename}")
                else:
                    print(f"- No changes needed for {filename}")
            except Exception as e:
                print(f"✗ Error in {filename}: {e}")
    
    print(f"\n{len(modified)} files modified")


if __name__ == "__main__":
    main()
