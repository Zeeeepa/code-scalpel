# Oracle Integration Guide for Community and Pro Tier Tools

## Overview

This document describes how the Oracle validation system integrates with each MCP tool at the Community, Pro, and Enterprise tiers. Oracle activates on tool failures and provides confidence-scored guidance to help AI agents recover from errors and make better decisions.

Oracle uses fuzzy matching, constraint analysis, and project context to suggest corrections with confidence scores. All suggestions include a "did you mean?" format with alternatives.

## Community Tier Tool Integration

### 1. analyze_code
**Primary Failure Scenario**: File not found or invalid path
**Oracle Guidance**: Suggests closest matching file path using fuzzy string matching against the project file tree
**Example**:
```json
{
  "error": "File not found: src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "src/utils.py",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.py'?",
    "alternatives": ["src/utilities.py", "src/utils_test.py"]
  }
}
```

### 2. code_policy_check
**Primary Failure Scenario**: Invalid rule name or compliance standard
**Oracle Guidance**: Suggests closest matching rule names from available policy patterns
**Example**:
```json
{
  "error": "Unknown rule: pep9",
  "oracle_suggestion": {
    "suggestion": "pep8",
    "confidence": 0.89,
    "message": "Did you mean 'pep8'?",
    "alternatives": ["pycodestyle", "flake8"]
  }
}
```

### 3. crawl_project
**Primary Failure Scenario**: Invalid pattern or exclude path
**Oracle Guidance**: Suggests valid glob patterns based on project structure
**Example**:
```json
{
  "error": "Invalid pattern: *.java",
  "oracle_suggestion": {
    "suggestion": "**/*.java",
    "confidence": 0.95,
    "message": "Did you mean '**/*.java'?",
    "alternatives": ["*.java", "java/**/*.java"]
  }
}
```

### 4. cross_file_security_scan
**Primary Failure Scenario**: Invalid entry point or module path
**Oracle Guidance**: Suggests valid module paths from project analysis
**Example**:
```json
{
  "error": "Module not found: app.routs",
  "oracle_suggestion": {
    "suggestion": "app.routes",
    "confidence": 0.91,
    "message": "Did you mean 'app.routes'?",
    "alternatives": ["app.routing", "routes.py"]
  }
}
```

### 5. extract_code
**Primary Failure Scenario**: Symbol not found in file
**Oracle Guidance**: Suggests closest matching function/class names using AST analysis
**Example**:
```json
{
  "error": "Symbol not found: calculat_tax",
  "oracle_suggestion": {
    "suggestion": "calculate_tax",
    "confidence": 0.93,
    "message": "Did you mean 'calculate_tax'?",
    "alternatives": ["compute_tax", "tax_calculator"]
  }
}
```

### 6. generate_unit_tests
**Primary Failure Scenario**: Function not found or invalid framework
**Oracle Guidance**: Suggests valid function names and supported test frameworks (limited to pytest)
**Example**:
```json
{
  "error": "Function not found: test_calculatr",
  "oracle_suggestion": {
    "suggestion": "test_calculator",
    "confidence": 0.94,
    "message": "Did you mean 'test_calculator'? Supported frameworks: pytest",
    "alternatives": ["calculator_test", "test_calculate"]
  }
}
```

### 7. get_call_graph
**Primary Failure Scenario**: Invalid entry point function
**Oracle Guidance**: Suggests valid function names from project analysis
**Example**:
```json
{
  "error": "Entry point not found: man",
  "oracle_suggestion": {
    "suggestion": "main",
    "confidence": 0.86,
    "message": "Did you mean 'main'?",
    "alternatives": ["run_main", "__main__"]
  }
}
```

### 8. get_cross_file_dependencies
**Primary Failure Scenario**: Target file or symbol not found
**Oracle Guidance**: Suggests closest matching files and symbols across the project
**Example**:
```json
{
  "error": "Target not found: utils.calculatr",
  "oracle_suggestion": {
    "suggestion": "utils.calculator",
    "confidence": 0.92,
    "message": "Did you mean 'utils.calculator'?",
    "alternatives": ["utils.compute", "calculator.utils"]
  }
}
```

### 9. get_file_context
**Primary Failure Scenario**: File not found or invalid line range
**Oracle Guidance**: Suggests valid files and line ranges based on file analysis
**Example**:
```json
{
  "error": "File not found: src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "src/utils.py",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.py'?",
    "alternatives": ["src/utilities.py", "utils.py"]
  }
}
```

### 10. get_graph_neighborhood
**Primary Failure Scenario**: Invalid center node ID
**Oracle Guidance**: Suggests valid node IDs from call graph analysis
**Example**:
```json
{
  "error": "Node not found: python::utils::calculatr",
  "oracle_suggestion": {
    "suggestion": "python::utils::calculator",
    "confidence": 0.93,
    "message": "Did you mean 'python::utils::calculator'?",
    "alternatives": ["python::utils::compute", "python::calculator::utils"]
  }
}
```

### 11. get_project_map
**Primary Failure Scenario**: Invalid root path or filter pattern
**Oracle Guidance**: Suggests valid project paths and filter patterns
**Example**:
```json
{
  "error": "Invalid root path: /src",
  "oracle_suggestion": {
    "suggestion": "./src",
    "confidence": 0.88,
    "message": "Did you mean './src'?",
    "alternatives": ["src/", "/project/src"]
  }
}
```

### 12. get_symbol_references
**Primary Failure Scenario**: Symbol not found in project
**Oracle Guidance**: Suggests closest matching symbols across all files
**Example**:
```json
{
  "error": "Symbol not found: calculatTax",
  "oracle_suggestion": {
    "suggestion": "calculateTax",
    "confidence": 0.94,
    "message": "Did you mean 'calculateTax'?",
    "alternatives": ["computeTax", "taxCalculator"]
  }
}
```

### 13. rename_symbol
**Primary Failure Scenario**: Symbol not found (Community tier disabled)
**Oracle Guidance**: Explains tier limitation and suggests upgrade
**Example**:
```json
{
  "error": "rename_symbol not available in Community tier",
  "oracle_suggestion": {
    "suggestion": "upgrade_required",
    "confidence": 1.0,
    "message": "rename_symbol requires Pro tier or higher. Consider upgrading for cross-file symbol renaming.",
    "alternatives": ["Use update_symbol for single-file changes"]
  }
}
```

### 14. scan_dependencies
**Primary Failure Scenario**: Invalid package name or path
**Oracle Guidance**: Suggests valid dependency names from project analysis
**Example**:
```json
{
  "error": "Package not found: requsts",
  "oracle_suggestion": {
    "suggestion": "requests",
    "confidence": 0.93,
    "message": "Did you mean 'requests'?",
    "alternatives": ["urllib3", "httpx"]
  }
}
```

### 15. security_scan
**Primary Failure Scenario**: File not found or invalid language
**Oracle Guidance**: Suggests valid files and supported languages
**Example**:
```json
{
  "error": "File not found: src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "src/utils.py",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.py'?",
    "alternatives": ["src/utilities.py", "utils.py"]
  }
}
```

### 16. simulate_refactor
**Primary Failure Scenario**: Invalid code or file not found
**Oracle Guidance**: Suggests corrected code snippets or file paths
**Example**:
```json
{
  "error": "File not found: src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "src/utils.py",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.py'?",
    "alternatives": ["src/utilities.py", "utils.py"]
  }
}
```

### 17. symbolic_execute
**Primary Failure Scenario**: Invalid code or unsupported construct
**Oracle Guidance**: Suggests corrected code or explains limitations
**Example**:
```json
{
  "error": "Unsupported construct: complex data structures",
  "oracle_suggestion": {
    "suggestion": "use_supported_types",
    "confidence": 0.95,
    "message": "Community tier supports int, bool, string, float. Consider upgrading for list/dict support.",
    "alternatives": ["Simplify to primitive types", "Use Pro tier for advanced types"]
  }
}
```

### 18. type_evaporation_scan
**Primary Failure Scenario**: Invalid file paths or unsupported languages
**Oracle Guidance**: Suggests valid TypeScript/JavaScript files
**Example**:
```json
{
  "error": "File not found: src/utilz.ts",
  "oracle_suggestion": {
    "suggestion": "src/utils.ts",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.ts'?",
    "alternatives": ["src/utilities.ts", "utils.ts"]
  }
}
```

### 19. unified_sink_detect
**Primary Failure Scenario**: Invalid language or file not found
**Oracle Guidance**: Suggests supported languages and valid files
**Example**:
```json
{
  "error": "Unsupported language: ruby",
  "oracle_suggestion": {
    "suggestion": "python",
    "confidence": 0.80,
    "message": "Did you mean 'python'? Supported: python, javascript, typescript, java",
    "alternatives": ["javascript", "typescript", "java"]
  }
}
```

### 20. update_symbol
**Primary Failure Scenario**: Symbol not found or invalid code
**Oracle Guidance**: Suggests closest matching symbols and corrected code
**Example**:
```json
{
  "error": "Symbol not found: calculat_tax",
  "oracle_suggestion": {
    "suggestion": "calculate_tax",
    "confidence": 0.93,
    "message": "Did you mean 'calculate_tax'?",
    "alternatives": ["compute_tax", "tax_calculator"]
  }
}
```

### 21. validate_paths
**Primary Failure Scenario**: Invalid paths or permission issues
**Oracle Guidance**: Suggests corrected paths and explains access issues
**Example**:
```json
{
  "error": "Path not found: /src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "./src/utils.py",
    "confidence": 0.90,
    "message": "Did you mean './src/utils.py'? Use relative paths within project.",
    "alternatives": ["src/utils.py", "./utils.py"]
  }
}
```

### 22. verify_policy_integrity
**Primary Failure Scenario**: Invalid policy file or path
**Oracle Guidance**: Suggests valid policy file locations and formats
**Example**:
```json
{
  "error": "Policy file not found: .code-scalpel/policy.yam",
  "oracle_suggestion": {
    "suggestion": ".code-scalpel/policy.yaml",
    "confidence": 0.96,
    "message": "Did you mean '.code-scalpel/policy.yaml'?",
    "alternatives": [".code-scalpel/policies.yaml", "policy.yaml"]
  }
}
```

## Pro Tier Tool Integration

### 1. analyze_code
**Primary Failure Scenario**: File not found or invalid path
**Oracle Guidance**: Suggests closest matching file path with expanded language support
**Example**:
```json
{
  "error": "File not found: src/utilz.go",
  "oracle_suggestion": {
    "suggestion": "src/utils.",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.go'?",
    "alternatives": ["src/utilities.go", "utils.go"]
  }
}
```

### 2. code_policy_check
**Primary Failure Scenario**: Invalid rule name or custom rule syntax
**Oracle Guidance**: Suggests valid rule names and custom rule formats
**Example**:
```json
{
  "error": "Invalid custom rule syntax: no-sql",
  "oracle_suggestion": {
    "suggestion": "no_sql_injection",
    "confidence": 0.87,
    "message": "Did you mean 'no_sql_injection'?.",
    "alternatives": ["sql_injection_check", "security_sql"]
  }
}
```

### 3. crawl_project
**Primary Failure Scenario**: Invalid pattern or parsing error
**Oracle Guidance**: Suggests valid patterns with parsing hints
**Example**:
```json
{
  "error": "Parsing failed for pattern: *.java",
  "oracle_suggestion": {
    "suggestion": "**/*.java",
    "confidence": 0.95,
    "message": "Did you mean '**/*.java'?",
    "alternatives": ["java/**/*.java", "*.java"]
  }
}
```

### 4. cross_file_security_scan
**Primary Failure Scenario**: Invalid entry point or deep module path
**Oracle Guidance**: Suggests valid module paths with deeper analysis
**Example**:
```json
{
  "error": "Deep module path not found: app.controllers.auth.routs",
  "oracle_suggestion": {
    "suggestion": "app.controllers.auth.routes",
    "confidence": 0.91,
    "message": "Did you mean 'app.controllers.auth.routes'?",
    "alternatives": ["app.controllers.auth.routing", "routes.py"]
  }
}
```

### 5. extract_code
**Primary Failure Scenario**: Symbol not found or cross-file dependency issue
**Oracle Guidance**: Suggests symbols with cross-file dependency hints
**Example**:
```json
{
  "error": "Cross-file symbol not found: calculat_tax",
  "oracle_suggestion": {
    "suggestion": "calculate_tax",
    "confidence": 0.93,
    "message": "Did you mean 'calculate_tax'?",
    "alternatives": ["utils.calculate_tax", "tax_calculator"]
  }
}
```

### 6. generate_unit_tests
**Primary Failure Scenario**: Function not found or unsupported framework
**Oracle Guidance**: Suggests valid functions and multiple test frameworks
**Example**:
```json
{
  "error": "Unsupported framework: mocha",
  "oracle_suggestion": {
    "suggestion": "jest",
    "confidence": 0.88,
    "message": "Did you mean 'jest'?",
    "alternatives": ["pytest", "unittest"]
  }
}
```

### 7. get_call_graph
**Primary Failure Scenario**: Invalid entry point or deep call chain
**Oracle Guidance**: Suggests valid entry points with depth analysis
**Example**:
```json
{
  "error": "Deep call chain not found: app.main.process",
  "oracle_suggestion": {
    "suggestion": "app.main.run_process",
    "confidence": 0.89,
    "message": "Did you mean 'app.main.run_process'?",
    "alternatives": ["app.main.execute", "process_data"]
  }
}
```

### 8. get_cross_file_dependencies
**Primary Failure Scenario**: Target not found or deep dependency chain
**Oracle Guidance**: Suggests targets with dependency chain hints
**Example**:
```json
{
  "error": "Deep dependency not found: utils.calculatr",
  "oracle_suggestion": {
    "suggestion": "utils.calculator",
    "confidence": 0.92,
    "message": "Did you mean 'utils.calculator'?",
    "alternatives": ["utils.compute", "calculator.utils"]
  }
}
```

### 9. get_file_context
**Primary Failure Scenario**: File not found or line range beyond limits
**Oracle Guidance**: Suggests valid files with extended context limits
**Example**:
```json
{
  "error": "Line range 500-2000 exceeds limit",
  "oracle_suggestion": {
    "suggestion": "500-2000",
    "confidence": 0.95,
    "message": "Enterprise tier supports up to 2000 lines of context. Your range is valid.",
    "alternatives": ["500-1500", "1000-2000"]
  }
}
```

### 10. get_graph_neighborhood
**Primary Failure Scenario**: Invalid node ID or large neighborhood
**Oracle Guidance**: Suggests valid node IDs with neighborhood analysis
**Example**:
```json
{
  "error": "Large neighborhood for node: python::utils::calculatr",
  "oracle_suggestion": {
    "suggestion": "python::utils::calculator",
    "confidence": 0.93,
    "message": "Did you mean 'python::utils::calculator'? Pro tier supports up to 100 nodes in neighborhood.",
    "alternatives": ["python::utils::compute", "python::calculator::utils"]
  }
}
```

### 11. get_project_map
**Primary Failure Scenario**: Invalid path or large project scope
**Oracle Guidance**: Suggests valid paths with detailed mapping
**Example**:
```json
{
  "error": "Project too large for basic mapping",
  "oracle_suggestion": {
    "suggestion": "detailed",
    "confidence": 0.90,
    "message": "Pro tier supports detailed project mapping for up to 1000 files.",
    "alternatives": ["basic", "comprehensive"]
  }
}
```

### 12. get_symbol_references
**Primary Failure Scenario**: Symbol not found or many references
**Oracle Guidance**: Suggests symbols with reference count hints
**Example**:
```json
{
  "error": "Too many references for symbol: calculatTax",
  "oracle_suggestion": {
    "suggestion": "calculateTax",
    "confidence": 0.94,
    "message": "Did you mean 'calculateTax'? Pro tier supports up to 500 references.",
    "alternatives": ["computeTax", "taxCalculator"]
  }
}
```

### 13. rename_symbol
**Primary Failure Scenario**: Symbol not found or cross-file rename limits
**Oracle Guidance**: Suggests valid symbols with rename scope hints
**Example**:
```json
{
  "error": "Cross-file rename failed: calculat_tax",
  "oracle_suggestion": {
    "suggestion": "calculate_tax",
    "confidence": 0.93,
    "message": "Did you mean 'calculate_tax'? Pro tier supports renaming across up to 200 files.",
    "alternatives": ["compute_tax", "tax_calculator"]
  }
}
```

### 14. scan_dependencies
**Primary Failure Scenario**: Invalid package or large dependency tree
**Oracle Guidance**: Suggests valid packages with curation hints
**Example**:
```json
{
  "error": "Large dependency tree for package: requsts",
  "oracle_suggestion": {
    "suggestion": "requests",
    "confidence": 0.93,
    "message": "Did you mean 'requests'? Pro tier supports up to 500 dependencies.",
    "alternatives": ["urllib3", "httpx"]
  }
}
```

### 15. security_scan
**Primary Failure Scenario**: File not found or many findings
**Oracle Guidance**: Suggests valid files with severity filtering
**Example**:
```json
{
  "error": "Too many findings in file: src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "src/utils.py",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.py'? Pro tier supports up to 500 findings with all severity levels.",
    "alternatives": ["src/utilities.py", "utils.py"]
  }
}
```

### 16. simulate_refactor
**Primary Failure Scenario**: Invalid code or large file size
**Oracle Guidance**: Suggests corrected code with advanced analysis
**Example**:
```json
{
  "error": "File too large for basic analysis: src/large.py",
  "oracle_suggestion": {
    "suggestion": "src/large.py",
    "confidence": 0.95,
    "message": "Pro tier supports advanced refactoring analysis for files up to 10MB.",
    "alternatives": ["Split into smaller files", "Use basic analysis"]
  }
}
```

### 17. symbolic_execute
**Primary Failure Scenario**: Unsupported construct or complex execution
**Oracle Guidance**: Suggests corrected code with extended type support
**Example**:
```json
{
  "error": "Complex list operations not supported",
  "oracle_suggestion": {
    "suggestion": "use_list_support",
    "confidence": 0.95,
    "message": "Pro tier supports list and dict types. Your code should work.",
    "alternatives": ["Use primitive types", "Simplify operations"]
  }
}
```

### 18. type_evaporation_scan
**Primary Failure Scenario**: Invalid file or backend analysis needed
**Oracle Guidance**: Suggests valid files with full-stack analysis
**Example**:
```json
{
  "error": "Backend analysis needed for file: src/utilz.ts",
  "oracle_suggestion": {
    "suggestion": "src/utils.ts",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.ts'? Pro tier supports full-stack type evaporation analysis.",
    "alternatives": ["src/utilities.ts", "utils.ts"]
  }
}
```

### 19. unified_sink_detect
**Primary Failure Scenario**: Unsupported language or many sinks
**Oracle Guidance**: Suggests supported languages with extended detection
**Example**:
```json
{
  "error": "Unsupported language: ruby",
  "oracle_suggestion": {
    "suggestion": "go",
    "confidence": 0.82,
    "message": "Did you mean 'go'? Pro tier supports python, javascript, typescript, java, php, go.",
    "alternatives": ["python", "javascript", "java"]
  }
}
```

### 20. update_symbol
**Primary Failure Scenario**: Symbol not found or semantic validation failure
**Oracle Guidance**: Suggests symbols with semantic validation hints
**Example**:
```json
{
  "error": "Semantic validation failed: calculat_tax",
  "oracle_suggestion": {
    "suggestion": "calculate_tax",
    "confidence": 0.93,
    "message": "Did you mean 'calculate_tax'? Pro tier enables semantic validation.",
    "alternatives": ["compute_tax", "tax_calculator"]
  }
}
```

### 21. validate_paths
**Primary Failure Scenario**: Invalid paths or complex validation
**Oracle Guidance**: Suggests corrected paths with advanced validation
**Example**:
```json
{
  "error": "Complex path validation failed: /src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "./src/utils.py",
    "confidence": 0.90,
    "message": "Did you mean './src/utils.py'? Pro tier supports advanced path validation.",
    "alternatives": ["src/utils.py", "./utils.py"]
  }
}
```

### 22. verify_policy_integrity
**Primary Failure Scenario**: Invalid policy file or path
**Oracle Guidance**: Suggests valid policy file locations and formats
**Example**:
```json
{
  "error": "Policy file not found: .code-scalpel/policy.yam",
  "oracle_suggestion": {
    "suggestion": ".code-scalpel/policy.yaml",
    "confidence": 0.96,
    "message": "Did you mean '.code-scalpel/policy.yaml'?",
    "alternatives": [".code-scalpel/policies.yaml", "policy.yaml"]
  }
}
```

## Enterprise Tier Tool Integration

### 1. analyze_code
**Primary Failure Scenario**: File not found or invalid path
**Oracle Guidance**: Suggests closest matching file path with universal language support
**Example**:
```json
{
  "error": "File not found: src/utilz.rs",
  "oracle_suggestion": {
    "suggestion": "src/utils.rs",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.rs'? Enterprise tier supports all programming languages.",
    "alternatives": ["src/utilities.rs", "utils.rs"]
  }
}
```

### 2. code_policy_check
**Primary Failure Scenario**: Invalid rule or compliance framework
**Oracle Guidance**: Suggests valid rules with enterprise compliance and audit features
**Example**:
```json
{
  "error": "Invalid compliance framework: custom",
  "oracle_suggestion": {
    "suggestion": "GDPR",
    "confidence": 0.85,
    "message": "Did you mean 'GDPR'? Enterprise tier supports full compliance auditing with PDF reports.",
    "alternatives": ["SOC2", "ISO27001", "PCI-DSS"]
  }
}
```

### 3. crawl_project
**Primary Failure Scenario**: Invalid pattern or massive codebase
**Oracle Guidance**: Suggests valid patterns with unlimited parsing and complexity analysis
**Example**:
```json
{
  "error": "Pattern failed on massive codebase: *.java",
  "oracle_suggestion": {
    "suggestion": "**/*.java",
    "confidence": 0.95,
    "message": "Did you mean '**/*.java'? Enterprise tier supports unlimited files with full parsing.",
    "alternatives": ["java/**/*.java", "*.java"]
  }
}
```

### 4. cross_file_security_scan
**Primary Failure Scenario**: Invalid entry point or complex module structure
**Oracle Guidance**: Suggests valid modules with unlimited depth analysis
**Example**:
```json
{
  "error": "Complex module structure not found: enterprise.auth.security.routs",
  "oracle_suggestion": {
    "suggestion": "enterprise.auth.security.routes",
    "confidence": 0.91,
    "message": "Did you mean 'enterprise.auth.security.routes'? Enterprise tier supports unlimited module depth.",
    "alternatives": ["enterprise.auth.security.routing", "routes.py"]
  }
}
```

### 5. extract_code
**Primary Failure Scenario**: Symbol not found or complex dependency chains
**Oracle Guidance**: Suggests symbols with unlimited extraction and context
**Example**:
```json
{
  "error": "Complex symbol not found: enterprise.calculat_tax",
  "oracle_suggestion": {
    "suggestion": "enterprise.calculate_tax",
    "confidence": 0.93,
    "message": "Did you mean 'enterprise.calculate_tax'? Enterprise tier supports unlimited extraction size and context.",
    "alternatives": ["enterprise.utils.calculate_tax", "tax_calculator"]
  }
}
```

### 6. generate_unit_tests
**Primary Failure Scenario**: Function not found or unsupported framework
**Oracle Guidance**: Suggests valid functions with all test framework support
**Example**:
```json
{
  "error": "Unsupported framework: custom_test",
  "oracle_suggestion": {
    "suggestion": "vitest",
    "confidence": 0.88,
    "message": "Did you mean 'vitest'? Enterprise tier supports all test frameworks with unlimited test cases.",
    "alternatives": ["jest", "mocha", "pytest"]
  }
}
```

### 7. get_call_graph
**Primary Failure Scenario**: Invalid entry point or massive call chains
**Oracle Guidance**: Suggests valid entry points with unlimited graph analysis
**Example**:
```json
{
  "error": "Massive call chain not found: enterprise.main.process",
  "oracle_suggestion": {
    "suggestion": "enterprise.main.run_process",
    "confidence": 0.89,
    "message": "Did you mean 'enterprise.main.run_process'? Enterprise tier supports unlimited call graph depth and nodes.",
    "alternatives": ["enterprise.main.execute", "process_data"]
  }
}
```

### 8. get_cross_file_dependencies
**Primary Failure Scenario**: Target not found or infinite dependency chains
**Oracle Guidance**: Suggests targets with unlimited dependency analysis
**Example**:
```json
{
  "error": "Infinite dependency not found: enterprise.utils.calculatr",
  "oracle_suggestion": {
    "suggestion": "enterprise.utils.calculator",
    "confidence": 0.92,
    "message": "Did you mean 'enterprise.utils.calculator'? Enterprise tier supports unlimited dependency depth.",
    "alternatives": ["enterprise.utils.compute", "calculator.utils"]
  }
}
```

### 9. get_file_context
**Primary Failure Scenario**: File not found or massive line ranges
**Oracle Guidance**: Suggests valid files with unlimited context lines
**Example**:
```json
{
  "error": "Massive line range 1-100000 exceeds limit",
  "oracle_suggestion": {
    "suggestion": "1-100000",
    "confidence": 0.95,
    "message": "Enterprise tier supports unlimited context lines. Your range is valid.",
    "alternatives": ["1-50000", "50000-100000"]
  }
}
```

### 10. get_graph_neighborhood
**Primary Failure Scenario**: Invalid node ID or massive neighborhoods
**Oracle Guidance**: Suggests valid node IDs with unlimited neighborhood analysis
**Example**:
```json
{
  "error": "Massive neighborhood for node: enterprise::utils::calculatr",
  "oracle_suggestion": {
    "suggestion": "enterprise::utils::calculator",
    "confidence": 0.93,
    "message": "Did you mean 'enterprise::utils::calculator'? Enterprise tier supports unlimited neighborhood size.",
    "alternatives": ["enterprise::utils::compute", "enterprise::calculator::utils"]
  }
}
```

### 11. get_project_map
**Primary Failure Scenario**: Invalid path or enterprise-scale project
**Oracle Guidance**: Suggests valid paths with comprehensive enterprise mapping
**Example**:
```json
{
  "error": "Enterprise-scale project mapping failed",
  "oracle_suggestion": {
    "suggestion": "comprehensive",
    "confidence": 0.90,
    "message": "Enterprise tier supports comprehensive project mapping for unlimited files and 1000 modules.",
    "alternatives": ["detailed", "basic"]
  }
}
```

### 12. get_symbol_references
**Primary Failure Scenario**: Symbol not found or massive reference counts
**Oracle Guidance**: Suggests symbols with unlimited reference analysis
**Example**:
```json
{
  "error": "Massive references for symbol: calculatTax",
  "oracle_suggestion": {
    "suggestion": "calculateTax",
    "confidence": 0.94,
    "message": "Did you mean 'calculateTax'? Enterprise tier supports unlimited symbol references.",
    "alternatives": ["computeTax", "taxCalculator"]
  }
}
```

### 13. rename_symbol
**Primary Failure Scenario**: Symbol not found or enterprise-wide renames
**Oracle Guidance**: Suggests valid symbols with unlimited rename scope
**Example**:
```json
{
  "error": "Enterprise-wide rename failed: calculat_tax",
  "oracle_suggestion": {
    "suggestion": "calculate_tax",
    "confidence": 0.93,
    "message": "Did you mean 'calculate_tax'? Enterprise tier supports unlimited file renames.",
    "alternatives": ["compute_tax", "tax_calculator"]
  }
}
```

### 14. scan_dependencies
**Primary Failure Scenario**: Invalid package or massive dependency trees
**Oracle Guidance**: Suggests valid packages with enterprise curation
**Example**:
```json
{
  "error": "Massive dependency tree for package: requsts",
  "oracle_suggestion": {
    "suggestion": "requests",
    "confidence": 0.93,
    "message": "Did you mean 'requests'? Enterprise tier supports unlimited dependencies with curation.",
    "alternatives": ["urllib3", "httpx"]
  }
}
```

### 15. security_scan
**Primary Failure Scenario**: File not found or massive security findings
**Oracle Guidance**: Suggests valid files with unlimited security analysis
**Example**:
```json
{
  "error": "Massive findings in enterprise file: src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "src/utils.py",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.py'? Enterprise tier supports unlimited security findings with all severity levels.",
    "alternatives": ["src/utilities.py", "utils.py"]
  }
}
```

### 16. simulate_refactor
**Primary Failure Scenario**: Invalid code or massive file sizes
**Oracle Guidance**: Suggests corrected code with deep enterprise analysis
**Example**:
```json
{
  "error": "Massive file too large for analysis: src/enterprise.py",
  "oracle_suggestion": {
    "suggestion": "src/enterprise.py",
    "confidence": 0.95,
    "message": "Enterprise tier supports deep refactoring analysis for files up to 100MB.",
    "alternatives": ["Split into smaller modules", "Use basic analysis"]
  }
}
```

### 17. symbolic_execute
**Primary Failure Scenario**: Unsupported construct or complex enterprise logic
**Oracle Guidance**: Suggests corrected code with full type support
**Example**:
```json
{
  "error": "Complex enterprise logic not supported",
  "oracle_suggestion": {
    "suggestion": "use_full_type_support",
    "confidence": 0.95,
    "message": "Enterprise tier supports all constraint types and unlimited execution depth.",
    "alternatives": ["Use supported constructs", "Simplify logic"]
  }
}
```

### 18. type_evaporation_scan
**Primary Failure Scenario**: Invalid file or full-stack enterprise analysis
**Oracle Guidance**: Suggests valid files with comprehensive type analysis
**Example**:
```json
{
  "error": "Full-stack analysis needed for file: src/utilz.ts",
  "oracle_suggestion": {
    "suggestion": "src/utils.ts",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.ts'? Enterprise tier supports full-stack type evaporation analysis.",
    "alternatives": ["src/utilities.ts", "utils.ts"]
  }
}
```

### 19. unified_sink_detect
**Primary Failure Scenario**: Unsupported language or massive sink detection
**Oracle Guidance**: Suggests supported languages with unlimited detection
**Example**:
```json
{
  "error": "Unsupported language: erlang",
  "oracle_suggestion": {
    "suggestion": "elixir",
    "confidence": 0.82,
    "message": "Did you mean 'elixir'? Enterprise tier supports all languages with unlimited sink detection.",
    "alternatives": ["python", "javascript", "java"]
  }
}
```

### 20. update_symbol
**Primary Failure Scenario**: Symbol not found or full validation failure
**Oracle Guidance**: Suggests symbols with full enterprise validation
**Example**:
```json
{
  "error": "Full validation failed: calculat_tax",
  "oracle_suggestion": {
    "suggestion": "calculate_tax",
    "confidence": 0.93,
    "message": "Did you mean 'calculate_tax'? Enterprise tier enables full validation with unlimited updates.",
    "alternatives": ["compute_tax", "tax_calculator"]
  }
}
```

### 21. validate_paths
**Primary Failure Scenario**: Invalid paths or complex enterprise validation
**Oracle Guidance**: Suggests corrected paths with enterprise validation
**Example**:
```json
{
  "error": "Complex enterprise path validation failed: /enterprise/src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "./enterprise/src/utils.py",
    "confidence": 0.90,
    "message": "Did you mean './enterprise/src/utils.py'? Enterprise tier supports advanced path validation.",
    "alternatives": ["enterprise/src/utils.py", "./utils.py"]
  }
}
```

### 22. verify_policy_integrity
**Primary Failure Scenario**: Invalid policy or enterprise compliance conflicts
**Oracle Guidance**: Suggests valid policies with enterprise conflict resolution
**Example**:
```json
{
  "error": "Enterprise compliance conflict: .code-scalpel/policy.yam",
  "oracle_suggestion": {
    "suggestion": ".code-scalpel/policy.yaml",
    "confidence": 0.96,
    "message": "Did you mean '.code-scalpel/policy.yaml'? Enterprise tier enables conflict detection and audit trails.",
    "alternatives": [".code-scalpel/policies.yaml", "policy.yaml"]
  }
}
```

## Implementation Notes

- **Confidence Threshold**: Suggestions only provided when confidence > 0.6
- **Tier Awareness**: Responses highlight tier-specific advantages and unlimited capabilities
- **Multiple Alternatives**: Up to 3 alternative suggestions provided
- **Context Preservation**: Oracle maintains original error context while adding guidance
- **Non-Breaking**: Existing error responses unchanged; Oracle suggestions are additive

## Testing Oracle Integration

Each tool's Oracle integration should be tested with:
1. Valid inputs (no Oracle activation)
2. Invalid inputs triggering Oracle suggestions
3. Confidence scoring accuracy
4. Alternative suggestion quality
5. Tier-appropriate guidance

- **Confidence Threshold**: Suggestions only provided when confidence > 0.6
- **Tier Awareness**: Responses highlight Pro tier advantages over Community
- **Multiple Alternatives**: Up to 3 alternative suggestions provided
- **Context Preservation**: Oracle maintains original error context while adding guidance
- **Non-Breaking**: Existing error responses unchanged; Oracle suggestions are additive

## Testing Oracle Integration

Each tool's Oracle integration should be tested with:
1. Valid inputs (no Oracle activation)
2. Invalid inputs triggering Oracle suggestions
3. Confidence scoring accuracy
4. Alternative suggestion quality
5. Tier-appropriate guidance

### 1. analyze_code
**Primary Failure Scenario**: File not found or invalid path
**Oracle Guidance**: Suggests closest matching file path using fuzzy string matching against the project file tree
**Example**:
```json
{
  "error": "File not found: src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "src/utils.py",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.py'?",
    "alternatives": ["src/utilities.py", "src/utils_test.py"]
  }
}
```

### 2. code_policy_check
**Primary Failure Scenario**: Invalid rule name or compliance standard
**Oracle Guidance**: Suggests closest matching rule names from available policy patterns
**Example**:
```json
{
  "error": "Unknown rule: pep9",
  "oracle_suggestion": {
    "suggestion": "pep8",
    "confidence": 0.89,
    "message": "Did you mean 'pep8'?",
    "alternatives": ["pycodestyle", "flake8"]
  }
}
```

### 3. crawl_project
**Primary Failure Scenario**: Invalid pattern or exclude path
**Oracle Guidance**: Suggests valid glob patterns based on project structure
**Example**:
```json
{
  "error": "Invalid pattern: *.java",
  "oracle_suggestion": {
    "suggestion": "**/*.java",
    "confidence": 0.95,
    "message": "Did you mean '**/*.java'?",
    "alternatives": ["*.java", "java/**/*.java"]
  }
}
```

### 4. cross_file_security_scan
**Primary Failure Scenario**: Invalid entry point or module path
**Oracle Guidance**: Suggests valid module paths from project analysis
**Example**:
```json
{
  "error": "Module not found: app.routs",
  "oracle_suggestion": {
    "suggestion": "app.routes",
    "confidence": 0.91,
    "message": "Did you mean 'app.routes'?",
    "alternatives": ["app.routing", "routes.py"]
  }
}
```

### 5. extract_code
**Primary Failure Scenario**: Symbol not found in file
**Oracle Guidance**: Suggests closest matching function/class names using AST analysis
**Example**:
```json
{
  "error": "Symbol not found: calculat_tax",
  "oracle_suggestion": {
    "suggestion": "calculate_tax",
    "confidence": 0.93,
    "message": "Did you mean 'calculate_tax'?",
    "alternatives": ["compute_tax", "tax_calculator"]
  }
}
```

### 6. generate_unit_tests
**Primary Failure Scenario**: Function not found or invalid framework
**Oracle Guidance**: Suggests valid function names and supported test frameworks
**Example**:
```json
{
  "error": "Function not found: test_calculatr",
  "oracle_suggestion": {
    "suggestion": "test_calculator",
    "confidence": 0.94,
    "message": "Did you mean 'test_calculator'?",
    "alternatives": ["calculator_test", "test_calculate"]
  }
}
```

### 7. get_call_graph
**Primary Failure Scenario**: Invalid entry point function
**Oracle Guidance**: Suggests valid function names from project analysis
**Example**:
```json
{
  "error": "Entry point not found: man",
  "oracle_suggestion": {
    "suggestion": "main",
    "confidence": 0.86,
    "message": "Did you mean 'main'?",
    "alternatives": ["run_main", "__main__"]
  }
}
```

### 8. get_cross_file_dependencies
**Primary Failure Scenario**: Target file or symbol not found
**Oracle Guidance**: Suggests closest matching files and symbols across the project
**Example**:
```json
{
  "error": "Target not found: utils.calculatr",
  "oracle_suggestion": {
    "suggestion": "utils.calculator",
    "confidence": 0.92,
    "message": "Did you mean 'utils.calculator'?",
    "alternatives": ["utils.compute", "calculator.utils"]
  }
}
```

### 9. get_file_context
**Primary Failure Scenario**: File not found or invalid line range
**Oracle Guidance**: Suggests valid files and line ranges based on file analysis
**Example**:
```json
{
  "error": "File not found: src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "src/utils.py",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.py'?",
    "alternatives": ["src/utilities.py", "utils.py"]
  }
}
```

### 10. get_graph_neighborhood
**Primary Failure Scenario**: Invalid center node ID
**Oracle Guidance**: Suggests valid node IDs from call graph analysis
**Example**:
```json
{
  "error": "Node not found: python::utils::calculatr",
  "oracle_suggestion": {
    "suggestion": "python::utils::calculator",
    "confidence": 0.93,
    "message": "Did you mean 'python::utils::calculator'?",
    "alternatives": ["python::utils::compute", "python::calculator::utils"]
  }
}
```

### 11. get_project_map
**Primary Failure Scenario**: Invalid root path or filter pattern
**Oracle Guidance**: Suggests valid project paths and filter patterns
**Example**:
```json
{
  "error": "Invalid root path: /src",
  "oracle_suggestion": {
    "suggestion": "./src",
    "confidence": 0.88,
    "message": "Did you mean './src'?",
    "alternatives": ["src/", "/project/src"]
  }
}
```

### 12. get_symbol_references
**Primary Failure Scenario**: Symbol not found in project
**Oracle Guidance**: Suggests closest matching symbols across all files
**Example**:
```json
{
  "error": "Symbol not found: calculatTax",
  "oracle_suggestion": {
    "suggestion": "calculateTax",
    "confidence": 0.94,
    "message": "Did you mean 'calculateTax'?",
    "alternatives": ["computeTax", "taxCalculator"]
  }
}
```

### 13. rename_symbol
**Primary Failure Scenario**: Symbol not found (Community tier disabled)
**Oracle Guidance**: Explains tier limitation and suggests upgrade
**Example**:
```json
{
  "error": "rename_symbol not available in Community tier",
  "oracle_suggestion": {
    "suggestion": "upgrade_required",
    "confidence": 1.0,
    "message": "rename_symbol requires Pro tier or higher. Consider upgrading for cross-file symbol renaming.",
    "alternatives": ["Use update_symbol for single-file changes"]
  }
}
```

### 14. scan_dependencies
**Primary Failure Scenario**: Invalid package name or path
**Oracle Guidance**: Suggests valid dependency names from project analysis
**Example**:
```json
{
  "error": "Package not found: requsts",
  "oracle_suggestion": {
    "suggestion": "requests",
    "confidence": 0.93,
    "message": "Did you mean 'requests'?",
    "alternatives": ["urllib3", "httpx"]
  }
}
```

### 15. security_scan
**Primary Failure Scenario**: File not found or invalid language
**Oracle Guidance**: Suggests valid files and supported languages
**Example**:
```json
{
  "error": "File not found: src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "src/utils.py",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.py'?",
    "alternatives": ["src/utilities.py", "utils.py"]
  }
}
```

### 16. simulate_refactor
**Primary Failure Scenario**: Invalid code or file not found
**Oracle Guidance**: Suggests corrected code snippets or file paths
**Example**:
```json
{
  "error": "File not found: src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "src/utils.py",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.py'?",
    "alternatives": ["src/utilities.py", "utils.py"]
  }
}
```

### 17. symbolic_execute
**Primary Failure Scenario**: Invalid code or unsupported construct
**Oracle Guidance**: Suggests corrected code or explains limitations
**Example**:
```json
{
  "error": "Unsupported construct: complex data structures",
  "oracle_suggestion": {
    "suggestion": "use_supported_types",
    "confidence": 0.95,
    "message": "Community tier supports int, bool, string, float. Consider upgrading for list/dict support.",
    "alternatives": ["Simplify to primitive types", "Use Pro tier for advanced types"]
  }
}
```

### 18. type_evaporation_scan
**Primary Failure Scenario**: Invalid file paths or unsupported languages
**Oracle Guidance**: Suggests valid TypeScript/JavaScript files
**Example**:
```json
{
  "error": "File not found: src/utilz.ts",
  "oracle_suggestion": {
    "suggestion": "src/utils.ts",
    "confidence": 0.92,
    "message": "Did you mean 'src/utils.ts'?",
    "alternatives": ["src/utilities.ts", "utils.ts"]
  }
}
```

### 19. unified_sink_detect
**Primary Failure Scenario**: Invalid language or file not found
**Oracle Guidance**: Suggests supported languages and valid files
**Example**:
```json
{
  "error": "Unsupported language: ruby",
  "oracle_suggestion": {
    "suggestion": "python",
    "confidence": 0.80,
    "message": "Did you mean 'python'? Supported: python, javascript, typescript, java",
    "alternatives": ["javascript", "typescript", "java"]
  }
}
```

### 20. update_symbol
**Primary Failure Scenario**: Symbol not found or invalid code
**Oracle Guidance**: Suggests closest matching symbols and corrected code
**Example**:
```json
{
  "error": "Symbol not found: calculat_tax",
  "oracle_suggestion": {
    "suggestion": "calculate_tax",
    "confidence": 0.93,
    "message": "Did you mean 'calculate_tax'?",
    "alternatives": ["compute_tax", "tax_calculator"]
  }
}
```

### 21. validate_paths
**Primary Failure Scenario**: Invalid paths or permission issues
**Oracle Guidance**: Suggests corrected paths and explains access issues
**Example**:
```json
{
  "error": "Path not found: /src/utilz.py",
  "oracle_suggestion": {
    "suggestion": "./src/utils.py",
    "confidence": 0.90,
    "message": "Did you mean './src/utils.py'? Use relative paths within project.",
    "alternatives": ["src/utils.py", "./utils.py"]
  }
}
```

### 22. verify_policy_integrity
**Primary Failure Scenario**: Invalid policy file or path
**Oracle Guidance**: Suggests valid policy file locations and formats
**Example**:
```json
{
  "error": "Policy file not found: .code-scalpel/policy.yam",
  "oracle_suggestion": {
    "suggestion": ".code-scalpel/policy.yaml",
    "confidence": 0.96,
    "message": "Did you mean '.code-scalpel/policy.yaml'?",
    "alternatives": [".code-scalpel/policies.yaml", "policy.yaml"]
  }
}
```
