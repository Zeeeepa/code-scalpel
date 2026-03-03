# Demo: "AST Analysis: Seeing Code as Structure, Not Text"

**Category**: Abstract Syntax Trees (ASTs)
**Pillar**: Accurate AI + Cheaper AI
**Tier**: Community
**Duration**: 8 minutes
**Fixture**: Any source file (use `src/code_scalpel/mcp/tools/extraction.py`)

## What Is This Demo About?

An **Abstract Syntax Tree (AST)** is the structured, hierarchical representation of source code — the first transformation that every compiler, linter, and code analysis tool performs. When Code Scalpel builds an AST, it strips away formatting noise (whitespace, comments, variable names) and reveals the **grammatical structure** of the code.

This demo explains ASTs visually, shows how `analyze_code` and `extract_code` use AST parsing to extract precise information, and demonstrates why AST-based extraction is **radically more reliable** than regex or LLM-based extraction.

## Tools Used

- `analyze_code` (Community) — Parses to AST, returns structured metadata
- `extract_code` (Community) — Surgically extracts a named symbol using AST
- `get_file_context` (Community) — Lightweight AST summary

## Scenario

You need to extract the exact signature of a function — its name, parameters, type annotations, return type, and docstring. You could ask an LLM "what are the parameters?", but it might hallucinate or miss a default value. Or you could use AST-based extraction: deterministic, exact, token-efficient.

## Recording Script

### Step 1: What Is an AST? (0:00-2:00)

- Show raw Python code:
  ```python
  def calculate_tax(amount: float, rate: float = 0.2) -> float:
      """Calculate sales tax."""
      if amount < 0:
          raise ValueError("Amount must be non-negative")
      return amount * rate
  ```
- Show what an AST looks like (simplified):
  ```
  FunctionDef
  ├── name: "calculate_tax"
  ├── args:
  │   ├── arg: amount (annotation: float)
  │   └── arg: rate   (annotation: float, default: 0.2)
  ├── returns: float
  ├── body:
  │   ├── Expr (docstring: "Calculate sales tax.")
  │   ├── If (test: amount < 0)
  │   │   └── Raise ValueError
  │   └── Return (amount * rate)
  └── decorator_list: []
  ```
- On-screen: "The AST is the grammar of your code. Formatting stripped. Logic exposed."

### Step 2: AST vs Regex vs LLM (2:00-3:30)

Show three approaches to extracting function signature:

**Regex approach**:
```regex
def\s+(\w+)\(([^)]*)\)\s*(?:->\s*(\w+))?
```
- Problems: breaks on multiline args, misses type annotations with generics, fragile

**LLM approach**:
- Prompt: "What are the parameters of calculate_tax?"
- Cost: ~2,000 tokens to include file context
- Risk: May hallucinate or misread

**Code Scalpel AST approach**:
- `extract_code(target_type="function", target_name="calculate_tax", file_path="...")`
- Cost: ~150 tokens
- Accuracy: 100% (deterministic parse)
- On-screen: "AST is immune to hallucination. 13x cheaper than LLM context."

### Step 3: `extract_code` in Action (3:30-5:30)

- Prompt: "Extract the calculate_tax function with full metadata"
- Tool call: `extract_code(file_path="utils/tax.py", target_type="function", target_name="calculate_tax")`
- Output:
  ```json
  {
    "name": "calculate_tax",
    "type": "function",
    "line_start": 1,
    "line_end": 6,
    "parameters": [
      {"name": "amount", "annotation": "float", "default": null},
      {"name": "rate", "annotation": "float", "default": 0.2}
    ],
    "return_annotation": "float",
    "docstring": "Calculate sales tax.",
    "body": "...",
    "token_estimate": 142
  }
  ```
- On-screen: "Extracted. Not hallucinated. 142 tokens instead of 2,000."

### Step 4: Class AST Extraction (5:30-6:30)

- Extract a class:
  ```python
  extract_code(
    file_path="src/mcp/server.py",
    target_type="class",
    target_name="MCPServer"
  )
  ```
- Output shows: class name, base classes, all methods with signatures, class attributes, docstrings
- Highlight: `include_context=True` option fetches cross-file imports too

### Step 5: Multi-Language AST (6:30-7:30)

- Show the **same** `extract_code` tool on a TypeScript React component:
  ```typescript
  // Button.tsx
  export function Button({ label, onClick }: ButtonProps) {
    return <button onClick={onClick}>{label}</button>
  }
  ```
- Output:
  ```json
  {
    "name": "Button",
    "component_type": "functional",
    "props": {"label": "string", "onClick": "() => void"},
    "is_server_component": false,
    "jsx_elements": ["button"]
  }
  ```
- On-screen: "Python, TypeScript, Java, C, C++, C# — one tool, one API."

### Step 6: The Token Math (7:30-8:00)

- Show the economics:
  ```
  Read 500-line file: 15,000 tokens
  extract_code result: 200-400 tokens
  Savings per call: 14,600 tokens
  At $15/M tokens (GPT-4o): $0.219 saved per call
  At 100 calls/day: $21.90/day = $657/month saved
  ```
- On-screen: "AST-powered extraction. Not just accurate. Economically decisive."

## Expected Outputs

```json
// analyze_code output
{
  "language": "python",
  "functions": [
    {
      "name": "calculate_tax",
      "args": ["amount: float", "rate: float = 0.2"],
      "returns": "float",
      "lines": [1, 6],
      "complexity": 2
    }
  ],
  "classes": [],
  "imports": []
}
```

## Key Talking Points

- "ASTs are how every compiler sees code — we bring that power to AI agents"
- "Regex is fragile; LLMs hallucinate; AST is deterministic and exact"
- "extract_code gives you the minimum viable context: just the symbol you need"
- "Token efficiency isn't just about cost — it's about context window preservation"
- "Community tier handles single-file AST analysis with full metadata"

## Technical Depth: AST Node Types

### Python AST Node Hierarchy (simplified)
```
Module
├── FunctionDef / AsyncFunctionDef
│   ├── arguments (args, vararg, kwarg, defaults)
│   ├── body (statements)
│   └── decorator_list
├── ClassDef
│   ├── bases (parent classes)
│   ├── keywords (metaclass=...)
│   └── body (methods, attributes)
└── Import / ImportFrom
```

### Why "Abstract"?
The AST is "abstract" because it omits:
- Whitespace and formatting
- Semicolons and parentheses (captured in structure instead)
- Comments (except docstrings)

What remains is pure **semantic content**: the meaning of the code, not its presentation.

### Supported AST Node Types per Language

| Language | Functions | Classes | Generics | Async | JSX |
|----------|-----------|---------|----------|-------|-----|
| Python | ✓ | ✓ | N/A | ✓ | N/A |
| JavaScript | ✓ | ✓ | N/A | ✓ | ✓ |
| TypeScript | ✓ | ✓ | ✓ | ✓ | ✓ |
| Java | ✓ | ✓ | ✓ | N/A | N/A |
| C | ✓ | N/A | N/A | N/A | N/A |
| C++ | ✓ | ✓ | ✓ | N/A | N/A |
| C# | ✓ | ✓ | ✓ | ✓ | N/A |
