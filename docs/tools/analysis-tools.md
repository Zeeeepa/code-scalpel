# Analysis Tools

Code analysis and metrics tools for understanding code structure and complexity.

**Tools in this category:**
- `analyze_code` - Comprehensive code analysis with complexity metrics and AST parsing

---

## analyze_code

Comprehensive code analysis with metrics, AST parsing, and code quality analysis.

### Overview

`analyze_code` provides deep code analysis:
- AST parsing with function/class inventory
- Complexity metrics (cyclomatic, cognitive)
- Code smell detection (Pro+)
- Dead code detection (Pro+)
- Duplicate code detection (Pro+)
- Architecture pattern analysis (Enterprise)
- Technical debt scoring (Enterprise)

**Use cases:**
- Understand code structure and organization
- Identify complex functions for refactoring
- Detect code smells and anti-patterns
- Find duplicate code
- Score technical debt
- Analyze API surface

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `code` | string | No | ✓ | ✓ | ✓ | Source code to analyze |
| `file_path` | string | No | ✓ | ✓ | ✓ | Path to file to analyze |
| `language` | string | No | ✓ | ✓ | ✓ | Programming language |

#### Tier-Specific Constraints

**Community:**
- Max file size: 1 MB
- Basic AST analysis
- Complexity metrics only

**Pro:**
- Max file size: 10 MB
- Code smell detection
- Dead code detection
- Framework detection
- Decorator analysis
- Halstead metrics
- Cognitive complexity

**Enterprise:**
- Max file size: 100 MB
- All Pro features + advanced analysis
- Architecture patterns
- Technical debt scoring
- API surface analysis
- Priority ordering
- Complexity trends

### Output Specification

```json
{
  "tier": "community|pro|enterprise",
  "tool_id": "analyze_code",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "language": "python",
    "file_size_kb": 45,
    "line_count": 250,
    "functions": [
      {
        "name": "calculate_sum",
        "lines": "10-25",
        "complexity": 3,
        "returns": "int",
        "docstring": "Calculate sum of items"
      }
    ],
    "classes": [
      {
        "name": "Calculator",
        "lines": "30-100",
        "methods": 5,
        "complexity": 2
      }
    ],
    "imports": ["os", "sys"],
    "metrics": {
      "cyclomatic_complexity": 8,
      "cognitive_complexity": 12,
      "maintainability_index": 85,
      "lines_of_code": 240
    },
    "code_smells": [],
    "dead_code_candidates": []
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Max file size** | 1 MB | 10 MB | 100 MB |
| **AST parsing** | ✓ | ✓ | ✓ |
| **Complexity metrics** | ✓ | ✓ | ✓ |
| **Code smells** | ✗ | ✓ | ✓ |
| **Dead code detection** | ✗ | ✓ | ✓ |
| **Duplicate detection** | ✗ | ✓ | ✓ |
| **Framework detection** | ✗ | ✓ | ✓ |
| **Architecture patterns** | ✗ | ✗ | ✓ |
| **Technical debt** | ✗ | ✗ | ✓ |

### Performance Considerations

- **Community**: 100-400ms (1 MB max)
- **Pro**: 200-1000ms (10 MB max)
- **Enterprise**: 500-3000ms (100 MB, with patterns)

---

## Response Envelope

```json
{
  "tier": "community|pro|enterprise|null",
  "tool_version": "1.x.x",
  "tool_id": "analyze_code",
  "request_id": "uuid-v4",
  "capabilities": ["envelope-v1"],
  "duration_ms": 1234,
  "error": null,
  "warnings": [],
  "upgrade_hints": [],
  "data": { /* tool-specific */ }
}
```

See `README.md` for complete specification.

## Related Tools

- **`crawl_project`** (context-tools.md) - Find files to analyze
- **`get_call_graph`** (graph-tools.md) - Visualize function relationships
