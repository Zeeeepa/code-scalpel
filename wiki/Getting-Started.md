# Getting Started

This guide walks you through your first Code Scalpel operations, from basic extraction to security scanning.

## Your First Tool Call

Once installed and configured (see [Installation](Installation)), your AI assistant can use Code Scalpel tools directly.

### Example 1: Extract a Function

Instead of reading an entire file, surgically extract just what you need:

**AI Assistant Command:**
```
Extract the calculate_tax function from utils.py
```

**Code Scalpel does:**
```python
extract_code(
    file_path="/project/utils.py",
    target_type="function",
    target_name="calculate_tax"
)
```

**Result:**
- Returns only the function definition
- Includes necessary imports
- 99% token reduction compared to reading the full file

### Example 2: Analyze Code Structure

Understand a file's architecture before modifying it:

**AI Assistant Command:**
```
What functions and classes are in payment.py?
```

**Code Scalpel does:**
```python
analyze_code(code=file_contents)
```

**Returns:**
```json
{
  "functions": ["process_payment", "validate_card", "refund"],
  "classes": ["PaymentProcessor", "PaymentError"],
  "imports": ["stripe", "decimal.Decimal"],
  "complexity_score": 8,
  "lines_of_code": 245
}
```

### Example 3: Security Scan

Detect vulnerabilities using taint analysis:

**AI Assistant Command:**
```
Check this code for SQL injection vulnerabilities
```

**Code Scalpel does:**
```python
security_scan(
    code=suspicious_code,
    entry_points=["handle_request"]
)
```

**Returns:**
- Vulnerabilities found with CWE codes
- Taint flow from user input to dangerous sinks
- Line numbers and severity levels

## Common Workflows

### Workflow 1: Safe Refactoring

Before changing code, verify it's safe:

```python
# 1. Extract the current function
current = extract_code(file_path="app.py", target_name="process_order")

# 2. Simulate your changes
result = simulate_refactor(
    original_code=current,
    new_code=improved_version
)

# 3. Check if safe
if result.is_safe:
    # 4. Apply the change
    update_symbol(
        file_path="app.py",
        target_name="process_order",
        new_code=improved_version
    )
```

### Workflow 2: Find All Usages

Before modifying a function, find everywhere it's called:

```python
# 1. Find all references
refs = get_symbol_references(symbol_name="calculate_tax")

# Returns:
# - Definition location
# - All call sites across the project
# - Usage context for each reference

# 2. Update all references safely
rename_symbol(
    file_path="utils.py",
    old_name="calculate_tax",
    new_name="compute_tax_amount"
)
# Automatically updates all call sites!
```

### Workflow 3: Generate Tests

Create comprehensive tests automatically:

```python
# 1. Extract the function to test
func = extract_code(file_path="logic.py", target_name="validate_input")

# 2. Explore all execution paths
paths = symbolic_execute(code=func, max_paths=10)

# 3. Generate tests covering all paths
tests = generate_unit_tests(
    code=func,
    framework="pytest",
    max_paths=10
)

# Returns pytest test code ready to use!
```

### Workflow 4: Cross-File Dependency Analysis

Understand how modules interact:

```python
# 1. Get project structure
project_map = get_project_map(root_path="/project")

# 2. Analyze specific file dependencies
deps = get_cross_file_dependencies(
    file_path="/project/services/order.py"
)

# Returns:
# - Direct imports
# - Transitive dependencies
# - Dependency graph
```

## Understanding Tool Results

### Success Response

Most tools return structured data:

```json
{
  "status": "success",
  "result": {
    "code": "def calculate_tax(amount): ...",
    "imports": ["from decimal import Decimal"],
    "metadata": {
      "line_start": 42,
      "line_end": 58
    }
  }
}
```

### Error Handling

When something goes wrong:

```json
{
  "status": "error",
  "error_type": "SymbolNotFound",
  "message": "Function 'calculate_taxes' not found. Did you mean 'calculate_tax'?",
  "suggestions": ["calculate_tax", "compute_tax"]
}
```

## Token Efficiency

Code Scalpel dramatically reduces token usage:

| Operation | Traditional | Code Scalpel | Savings |
|-----------|-------------|--------------|---------|
| Extract function | Read 10K LOC file | Extract 50 LOC | **99%** |
| Find usages | Grep entire codebase | Symbol references | **95%** |
| Security scan | Manual review | Taint analysis | **90%** |

**Example:**
- Reading a 10,000-line file: ~10,000 tokens
- Extracting one function: ~50 tokens
- **Savings: 9,950 tokens (99%)**

## Language Support

### Python (Full Support)

All features available:
- AST parsing ✅
- PDG analysis ✅
- Taint analysis ✅
- Symbolic execution ✅
- Test generation ✅

### JavaScript/TypeScript

Core features:
- AST parsing ✅
- Function extraction ✅
- Call graphs ✅
- Type evaporation scan ✅
- Basic security scanning ⚠️

### Java, Go, Rust, Ruby, PHP

Limited support:
- AST parsing ✅
- Code extraction ✅
- Structure analysis ✅

## Interactive Examples

### Example: E-commerce Refactor

**Scenario:** Refactor payment processing to handle multiple currencies.

```python
# Step 1: Understand current implementation
context = get_file_context(file_path="payment.py")
print(context.functions)  # ['process_payment', 'validate_card']

# Step 2: Extract the payment function
current = extract_code(
    file_path="payment.py",
    target_name="process_payment"
)

# Step 3: Find all places it's called
refs = get_symbol_references(symbol_name="process_payment")
print(f"Used in {len(refs.references)} places")

# Step 4: Check for security issues
security = security_scan(code=current)
if security.vulnerabilities:
    print("Warning: Fix security issues first!")

# Step 5: Simulate the refactor
new_code = """
def process_payment(amount, currency='USD'):
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported currency: {currency}")
    # ... enhanced logic
"""

safe = simulate_refactor(original_code=current, new_code=new_code)
if safe.is_safe:
    # Step 6: Apply the change
    update_symbol(
        file_path="payment.py",
        target_name="process_payment",
        new_code=new_code
    )
```

## Best Practices

### 1. Always Extract Before Analyzing

Don't read entire files unnecessarily:

❌ **Inefficient:**
```python
# Reads entire 5000-line file
full_file = read_file("services.py")
# Parse to find one function
```

✅ **Efficient:**
```python
# Extracts just 50 lines
function = extract_code(file_path="services.py", target_name="process")
```

### 2. Verify Before Modifying

Use `simulate_refactor` before `update_symbol`:

```python
# Always check safety first
result = simulate_refactor(original, new_code)
if result.is_safe and not result.security_issues:
    update_symbol(...)
```

### 3. Find All References Before Renaming

```python
# Check impact before renaming
refs = get_symbol_references("old_function")
print(f"Will update {len(refs.references)} locations")
# Then rename
rename_symbol(...)
```

### 4. Use Security Scanning Early

Catch vulnerabilities before they reach production:

```python
# Scan as you write
scan_result = security_scan(new_code)
if scan_result.vulnerabilities:
    # Fix issues before committing
```

## Next Steps

- **[MCP Tools Reference](MCP-Tools-Reference)** - Complete documentation of all 22 tools
- **[Configuration](Configuration)** - Environment variables and settings
- **[Examples](Examples)** - More complex use cases and patterns
- **[Security](Security)** - Policy enforcement and integrity verification

## Troubleshooting

### "Symbol not found"

```python
# Use get_file_context first to see what's available
context = get_file_context(file_path="myfile.py")
print(context.functions)  # See actual function names
```

### "Token limit exceeded"

Code Scalpel tools are designed to minimize tokens, but:
- Use `extract_code` instead of reading full files
- Use `get_file_context` for quick overviews
- Use `max_depth` parameters to limit recursion

### "Unsupported language"

Check [Language Support](#language-support) above. For unsupported languages:
- Basic extraction may still work via tree-sitter
- Advanced features (symbolic execution, PDG) are Python-only

---

**Ready for advanced features?** → [MCP Tools Reference](MCP-Tools-Reference)
