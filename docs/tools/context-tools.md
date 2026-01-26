# Context Tools

Project understanding and context discovery tools for exploring code structure and symbol relationships.

**Tools in this category:**
- `crawl_project` - Crawl and analyze project structure with framework detection
- `get_file_context` - Get file overview with semantic analysis
- `get_symbol_references` - Find all references to a symbol with impact analysis

---

## crawl_project

Crawl and analyze project directory structure with framework-specific detection.

### Overview

`crawl_project` provides comprehensive project indexing:
- Full file tree analysis with language breakdown
- Framework-specific entry point detection (Django, Flask, Next.js)
- Dependency mapping and hotspot identification
- Monorepo support (Enterprise)
- Historical trend analysis (Enterprise)
- Distributed crawling (Enterprise)

**Use cases:**
- Understand project structure and entry points
- Identify hotspots and high-complexity areas
- Detect framework-specific patterns
- Map project dependencies and imports
- Support monorepo analysis

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `root_path` | string | No | ✓ | ✓ | ✓ | Project root directory |
| `exclude_dirs` | array[string] | No | ✓ | ✓ | ✓ | Directories to exclude |
| `complexity_threshold` | integer | No | ✓ | ✓ | ✓ | Min complexity for reporting |
| `include_report` | boolean | No | ✓ | ✓ | ✓ | Generate summary report |
| `pattern` | string | No | ✓ | ✓ | ✓ | File pattern to match |
| `include_related` | array[string] | No | ✓ | ✓ | ✓ | Include related files |

#### Tier-Specific Constraints

**Community:**
- Max files: 100
- Max depth: 10
- Basic file indexing
- Language breakdown only

**Pro:**
- Max files: Unlimited
- Smart Crawl with framework detection
- Dependency mapping
- Hotspot identification
- Generated code detection

**Enterprise:**
- All Pro features + advanced capabilities
- Distributed crawling
- Historical analysis
- Monorepo support (unlimited repos)
- Custom crawl rules
- 100k+ file support

### Output Specification

#### Response Structure

```json
{
  "tier": "community|pro|enterprise",
  "tool_version": "1.x.x",
  "tool_id": "crawl_project",
  "request_id": "uuid-v4",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "files_found": 150,
    "languages": {
      "python": 80,
      "javascript": 45,
      "json": 25
    },
    "framework_detected": "django",
    "entrypoints": [
      {"file": "manage.py", "type": "django_management"},
      {"file": "views.py", "type": "django_views"}
    ],
    "report": {
      "total_files": 150,
      "high_complexity_files": 3,
      "generated_files": 2
    }
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Max files** | 100 | Unlimited | Unlimited |
| **Max depth** | 10 | Unlimited | Unlimited |
| **File indexing** | ✓ | ✓ | ✓ |
| **Framework detection** | ✗ | ✓ | ✓ |
| **Dependency mapping** | ✗ | ✓ | ✓ |
| **Hotspot detection** | ✗ | ✓ | ✓ |
| **Distributed crawl** | ✗ | ✗ | ✓ |
| **Monorepo support** | ✗ | ✗ | ✓ |
| **Historical analysis** | ✗ | ✗ | ✓ |

---

## get_file_context

Get file overview and context without reading full content.

### Overview

`get_file_context` provides intelligent file summarization:
- AST-based outlining and code folding
- Raw source retrieval
- Semantic summarization (Pro+)
- Code quality metrics (Pro+)
- Intent extraction (Pro+)
- Smart context expansion (Pro+)

**Use cases:**
- Get quick file overview without full read
- Understand key functions and classes
- Check code quality metrics
- Extract semantic meaning
- Analyze related imports

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `file_path` | string | Yes | ✓ | ✓ | ✓ | Path to file to analyze |

#### Tier-Specific Constraints

**Community:**
- Max context lines: 500
- AST outlining only
- Function/class folding

**Pro:**
- Max context lines: 2,000
- Semantic summarization
- Code quality metrics
- Intent extraction
- Smart expansion

**Enterprise:**
- Max context lines: Unlimited
- All Pro features + advanced analysis

### Output Specification

```json
{
  "tier": "community|pro|enterprise",
  "tool_id": "get_file_context",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "file_path": "/src/utils.py",
    "language": "python",
    "line_count": 250,
    "outline": [
      {
        "type": "function",
        "name": "calculate_sum",
        "line": 10,
        "lines": "10-15",
        "docstring": "Calculate sum of items"
      }
    ],
    "imports": ["os", "sys"],
    "quality_metrics": {
      "maintainability_index": 85,
      "documentation_coverage": 90
    }
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **AST outlining** | ✓ | ✓ | ✓ |
| **Max lines** | 500 | 2,000 | Unlimited |
| **Semantic summary** | ✗ | ✓ | ✓ |
| **Quality metrics** | ✗ | ✓ | ✓ |
| **Code smell detection** | ✗ | ✓ | ✓ |

---

## get_symbol_references

Find all references to a symbol with categorization and impact analysis.

### Overview

`get_symbol_references` locates and analyzes symbol usage:
- AST-based exact matching
- Usage categorization (imports, reads, writes)
- Read/write classification (Pro+)
- Scope filtering (Pro+)
- Impact analysis (Enterprise)
- Ownership attribution (Enterprise)
- Risk assessment (Enterprise)

**Use cases:**
- Find all usages of a symbol before refactoring
- Understand impact of changing a function
- Categorize usage types (import vs. direct call)
- Perform impact analysis
- Assess refactoring risk

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `symbol_name` | string | Yes | ✓ | ✓ | ✓ | Symbol to find (function, class, variable) |
| `file_path` | string | No | ✓ | ✓ | ✓ | Starting file for search |
| `project_root` | string | No | ✓ | ✓ | ✓ | Project root for scoping |
| `exclude_tests` | boolean | No | ✓ | ✓ | ✓ | Exclude test files |

#### Tier-Specific Constraints

**Community:**
- Max files searched: 100
- Max references: 100
- Basic matching only
- No categorization

**Pro:**
- Max files searched: Unlimited
- Max references: Unlimited
- Usage categorization
- Read/write classification
- Scope filtering

**Enterprise:**
- All Pro features
- Impact analysis
- Ownership attribution
- Risk assessment

### Output Specification

```json
{
  "tier": "community|pro|enterprise",
  "tool_id": "get_symbol_references",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "symbol": "calculate_total",
    "references_found": 5,
    "definition": {
      "file": "/src/math.py",
      "line": 42
    },
    "references": [
      {
        "file": "/src/api.py",
        "line": 100,
        "type": "function_call",
        "category": "usage",
        "code": "result = calculate_total(items)"
      }
    ],
    "impact_analysis": {
      "high_risk_changes": 2,
      "affected_modules": ["api", "services"]
    }
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Max files** | 100 | Unlimited | Unlimited |
| **Max references** | 100 | Unlimited | Unlimited |
| **Usage categorization** | ✗ | ✓ | ✓ |
| **Read/write classification** | ✗ | ✓ | ✓ |
| **Scope filtering** | ✗ | ✓ | ✓ |
| **Impact analysis** | ✗ | ✗ | ✓ |
| **Ownership attribution** | ✗ | ✗ | ✓ |
| **Risk assessment** | ✗ | ✗ | ✓ |

### Error Handling

- `invalid_argument` - Invalid symbol or file
- `invalid_path` - Path not found
- `not_found` - Symbol not found
- `resource_exhausted` - Too many references (Community: max 100)
- `internal_error` - Search error

### Performance Considerations

- **Community**: 100-500ms (100 files max)
- **Pro**: 200-1500ms (unlimited files)
- **Enterprise**: 500-3000ms (with impact analysis)

---

## Response Envelope Specification

All tools in this category return responses wrapped in a standard envelope:

```json
{
  "tier": "community|pro|enterprise|null",
  "tool_version": "1.x.x",
  "tool_id": "crawl_project|get_file_context|get_symbol_references",
  "request_id": "uuid-v4",
  "capabilities": ["envelope-v1"],
  "duration_ms": 1234,
  "error": null,
  "warnings": [],
  "upgrade_hints": [],
  "data": { /* tool-specific */ }
}
```

See `README.md` for complete envelope specification.

## Related Tools

- **`extract_code`** (extraction-tools.md) - Extract symbols discovered by reference search
- **`analyze_code`** (analysis-tools.md) - Analyze files found by crawl_project
- **`get_call_graph`** (graph-tools.md) - Visualize relationships between discovered symbols
