# Demo: "Static Analysis Deep Dive: Instant Codebase Intelligence"

**Category**: Static Analysis
**Pillar**: Accurate AI + Cheaper AI
**Tier**: Community → Pro
**Duration**: 10 minutes
**Fixture**: Any mid-size codebase (use Ninja Warrior fixture or Code Scalpel itself)

## What Is This Demo About?

Static analysis means analyzing code **without running it** — examining its structure, patterns, and relationships by parsing the source text into structured representations. Code Scalpel's static analysis pipeline:

1. **Parses** source files into Abstract Syntax Trees (ASTs)
2. **Extracts** functions, classes, imports, and their metadata
3. **Indexes** structural relationships across the entire project
4. **Reports** complexity metrics, patterns, and anomalies

This demo shows how `analyze_code`, `crawl_project`, and `get_file_context` give you instant codebase intelligence without reading files line-by-line.

## Tools Used

- `get_file_context` (Community) — Structural overview of a single file
- `analyze_code` (Community) — Full AST parse + metadata extraction
- `crawl_project` (Pro) — Codebase-wide crawl with complexity metrics
- `get_project_map` (Pro) — Package hierarchy and architectural map

## Scenario

You've just joined a new team. You have a 50,000-line Python codebase. Your task: understand the architecture in under 2 minutes. Without static analysis, you'd spend hours clicking through files. With Code Scalpel, you get the full picture in seconds.

## Recording Script

### Step 1: The Problem — Unknown Territory (0:00-1:00)

- Show repo structure: many nested directories
- On-screen: "New developer. 50k lines. 0 context."
- Traditional approach: open files one-by-one, read for 2 hours
- Code Scalpel approach: surgical structural extraction

### Step 2: Single File Overview with `get_file_context` (1:00-3:00)

- Prompt: "Give me the structural overview of `src/code_scalpel/mcp/server.py`"
- Tool call: `get_file_context(file_path="src/code_scalpel/mcp/server.py")`
- Output (in ~2 seconds):
  ```
  File: src/code_scalpel/mcp/server.py
  Functions (8): create_server, register_tools, handle_analyze_code, handle_extract_code, ...
  Classes (2): MCPServer, ToolRegistry
  Imports (12): mcp, fastmcp, code_scalpel.tools...
  Complexity: MEDIUM (McCabe score: 14)
  ```
- On-screen: "23 lines of output instead of 800 lines of code. 35x reduction."

### Step 3: Deep Structural Parse with `analyze_code` (3:00-5:30)

- Prompt: "Analyze the full structure of this file — functions, classes, parameters, return types"
- Tool call: `analyze_code(file_path="src/code_scalpel/mcp/server.py")`
- Output includes:
  - Each function: name, line range, parameters with types, return type
  - Each class: name, base classes, methods, attributes
  - Import graph: what this file depends on
  - Docstrings extracted automatically
- On-screen: "No file reading needed. The server extracted this via AST."

### Step 4: Multi-Language Static Analysis (5:30-6:30)

- Show `analyze_code` works across languages:
  ```
  Python  → Full AST + PDG + type inference
  JS/JSX  → AST + call graph + component tree
  TS/TSX  → AST + type analysis + React component metadata
  Java    → AST + class hierarchy + interface contracts
  C/C++   → AST + struct/union/enum + macro expansion
  C#      → AST + generics + async/await patterns
  ```
- Run `analyze_code` on a TypeScript file to show identical output structure
- On-screen: "One tool. Seven languages. Same API."

### Step 5: Project-Wide Crawl with `crawl_project` (6:30-9:00)

- Prompt: "Crawl the entire codebase and report complexity hotspots"
- Tool call: `crawl_project(root_path="src/", complexity_threshold=10)`
- Output:
  ```
  Files scanned: 47
  Total functions: 312
  Average complexity: 4.2

  HIGH COMPLEXITY (threshold: 10):
  ├── src/code_scalpel/polyglot/extractor.py (complexity: 24) ⚠️
  ├── src/code_scalpel/oracle/__init__.py (complexity: 18) ⚠️
  └── src/code_scalpel/mcp/tools/graph.py (complexity: 15) ⚠️

  Security warnings:
  ├── src/code_scalpel/config/init_config.py: potential path traversal
  └── (0 SQL injection, 0 XSS)
  ```
- On-screen: "3 complexity hotspots. 47 files. 2 seconds."

### Step 6: Architectural Map with `get_project_map` (9:00-10:00)

- Prompt: "Show me the package hierarchy and identify architectural boundaries"
- Tool call: `get_project_map(project_root="src/", include_complexity=True)`
- Output: Package tree with module dependencies, entry points, circular import warnings
- On-screen: "Architecture understood in 10 minutes. Not 10 hours."

## Expected Outputs

```
# get_file_context output
{
  "file": "server.py",
  "functions": ["create_server", "register_tools", ...],
  "classes": ["MCPServer"],
  "complexity": {"score": 14, "level": "MEDIUM"},
  "imports": [...]
}

# crawl_project output
{
  "files_scanned": 47,
  "high_complexity_files": [...],
  "security_warnings": [...],
  "summary": "312 functions, 28 classes, avg complexity 4.2"
}
```

## Key Talking Points

- "Static analysis reads structure — not runtime behavior"
- "AST parsing is deterministic: same input → same output, every time"
- "Complexity metrics (McCabe score) identify refactoring candidates"
- "Zero code execution: your code never leaves your machine"
- "Community tier: single file analysis. Pro: project-wide crawl."

## Technical Depth: How Static Analysis Works

### Phase 1: Lexing
Raw source text → stream of tokens (keywords, identifiers, operators)

### Phase 2: Parsing
Token stream → Abstract Syntax Tree (hierarchical structure)

### Phase 3: Semantic Analysis
AST + symbol table → type information, scope resolution

### Phase 4: Metric Extraction
- **McCabe Complexity**: count of linearly independent paths through code
- **Halstead Metrics**: vocabulary, length, difficulty, effort
- **Coupling**: number of external dependencies

### Complexity Thresholds
| Score | Level | Action |
|-------|-------|--------|
| 1-5 | LOW | Maintainable, no action |
| 6-10 | MEDIUM | Monitor, add tests |
| 11-20 | HIGH | Refactor candidate |
| 21+ | VERY HIGH | Technical debt priority |

## Before/After Comparison

| Method | Time | Files Covered | Depth | Token Cost |
|--------|------|---------------|-------|------------|
| Manual reading | 4 hours | Partial | Deep | N/A |
| `cat` + LLM | 3 min | 1 file | Shallow | 15,000 tokens |
| `get_file_context` | 1 sec | 1 file | Structural | 200 tokens |
| `crawl_project` | 3 sec | All 47 files | Deep + metrics | 800 tokens |
