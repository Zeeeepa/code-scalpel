# Graph Tools

Call graph, dependency graph, and cross-file analysis tools for understanding code relationships and data flow.

**Tools in this category:**
- `get_call_graph` - Generate call graphs showing function relationships
- `get_graph_neighborhood` - Explore k-hop neighborhoods in the code graph
- `get_project_map` - Generate comprehensive project structure map
- `get_cross_file_dependencies` - Map cross-file dependencies and imports
- `cross_file_security_scan` - Perform cross-file taint and security analysis

---

## get_call_graph

Generate call graphs showing function call relationships and analyze caller/callee hierarchies.

### Overview

`get_call_graph` analyzes function call relationships:
- Static call graph generation
- Caller and callee analysis
- Mermaid diagram generation
- Circular import detection
- Entry point detection (Community+)
- Polymorphism resolution (Pro+)
- Hot path identification (Enterprise)

**Use cases:**
- Understand function call hierarchies
- Detect circular dependencies
- Find entry points and hotspots
- Generate call flow diagrams
- Analyze code structure

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `symbol` | string | Yes | ✓ | ✓ | ✓ | Function name to graph |
| `file_path` | string | Yes | ✓ | ✓ | ✓ | Starting file |
| `direction` | string | No | ✓ | ✓ | ✓ | `callers` or `callees` |
| `max_depth` | integer | No | ✓ | ✓ | ✓ | Graph depth |

#### Tier-Specific Constraints

**Community:**
- Max depth: 3
- Max nodes: 50
- Basic call graph only
- No polymorphism resolution

**Pro:**
- Max depth: 50
- Max nodes: 500
- Advanced resolution
- Polymorphism handling
- Dynamic dispatch analysis

**Enterprise:**
- Max depth: Unlimited
- Max nodes: Unlimited
- Hot path identification
- Dead code detection
- Runtime trace overlay

### Output Specification

```json
{
  "tier": "community|pro|enterprise",
  "tool_id": "get_call_graph",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "root_symbol": "main",
    "direction": "callees",
    "depth": 3,
    "nodes": 12,
    "graph": {
      "nodes": [
        {"id": "main", "type": "function"}
      ],
      "edges": [
        {"from": "main", "to": "process", "label": "calls"}
      ]
    },
    "mermaid_diagram": "graph TD\n  main --> process\n  process --> analyze",
    "circular_imports": []
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Max depth** | 3 | 50 | Unlimited |
| **Max nodes** | 50 | 500 | Unlimited |
| **Polymorphism resolution** | ✗ | ✓ | ✓ |
| **Dynamic dispatch** | ✗ | ✓ | ✓ |
| **Hot path identification** | ✗ | ✗ | ✓ |
| **Runtime trace overlay** | ✗ | ✗ | ✓ |

---

## get_graph_neighborhood

Explore k-hop neighborhoods in the code dependency graph.

### Overview

`get_graph_neighborhood` discovers related code:
- Basic and advanced neighborhood traversal
- Semantic neighbor detection (Pro+)
- Logical relationship detection (Pro+)
- Custom traversal rules (Enterprise)
- Weighted path analysis (Enterprise)
- Graph query language (Enterprise)

**Use cases:**
- Find related functions and classes
- Discover semantic neighbors
- Explore code relationships
- Build neighborhood maps
- Analyze coupling and cohesion

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `symbol` | string | Yes | ✓ | ✓ | ✓ | Starting symbol |
| `k` | integer | No | ✓ (1) | ✓ | ✓ | Hop distance |
| `direction` | string | No | ✓ | ✓ | ✓ | `forward`, `backward`, `both` |

#### Tier-Specific Constraints

**Community:**
- Max k: 1 (immediate neighbors only)
- Max nodes: 20

**Pro:**
- Max k: 5
- Max nodes: 100
- Semantic neighbors
- Logical relationships

**Enterprise:**
- Max k: Unlimited
- Max nodes: Unlimited
- Custom traversal
- Graph queries

### Output Specification

```json
{
  "tier": "community|pro|enterprise",
  "tool_id": "get_graph_neighborhood",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "center_symbol": "process_data",
    "k": 2,
    "neighbors": [
      {
        "symbol": "validate_input",
        "distance": 1,
        "type": "function",
        "relationship": "called_by"
      }
    ]
  }
}
```

### Performance Considerations

- **Community**: 100-300ms (k=1, 20 nodes max)
- **Pro**: 200-1000ms (k=5, 100 nodes max)
- **Enterprise**: 500-3000ms (unlimited k)

---

## get_project_map

Generate comprehensive project structure and dependency maps.

### Overview

`get_project_map` creates high-level project visualizations showing overall structure and major components. (See `crawl_project` for detailed file-level analysis.)

---

## get_cross_file_dependencies

Map cross-file dependencies and import relationships.

### Overview

`get_cross_file_dependencies` analyzes import and dependency relationships across files:
- Direct import mapping
- Circular import detection
- Transitive dependency mapping (Pro+)
- Deep coupling analysis (Pro+)
- Architectural firewall (Enterprise)
- Layer constraint enforcement (Enterprise)

**Use cases:**
- Understand cross-file dependencies
- Detect circular imports
- Map dependency chains
- Analyze coupling
- Enforce architectural boundaries

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `file_path` | string | Yes | ✓ | ✓ | ✓ | Starting file |
| `direction` | string | No | ✓ | ✓ | ✓ | `imports` or `imported_by` |
| `include_external` | boolean | No | ✓ | ✓ | ✓ | Include external packages |

#### Tier-Specific Constraints

**Community:**
- Max depth: 1 (direct dependencies only)
- Max files: 50
- No transitive mapping

**Pro:**
- Max depth: 5
- Max files: 500
- Transitive dependencies
- Deep coupling analysis

**Enterprise:**
- Max depth: Unlimited
- Max files: Unlimited
- Architectural rules
- Layer constraints

### Output Specification

```json
{
  "tier": "community|pro|enterprise",
  "tool_id": "get_cross_file_dependencies",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "root_file": "/src/api.py",
    "direction": "imports",
    "dependencies": [
      {
        "file": "/src/utils.py",
        "depth": 1,
        "type": "module_import",
        "symbols": ["calculate_sum", "format_date"]
      }
    ],
    "circular_imports": [],
    "coupling_score": 0.45
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Max depth** | 1 | 5 | Unlimited |
| **Max files** | 50 | 500 | Unlimited |
| **Transitive** | ✗ | ✓ | ✓ |
| **Deep coupling** | ✗ | ✓ | ✓ |
| **Architectural rules** | ✗ | ✗ | ✓ |
| **Layer enforcement** | ✗ | ✗ | ✓ |

---

## cross_file_security_scan

Perform cross-file taint analysis and security scanning.

### Overview

`cross_file_security_scan` traces security-relevant data flows across files:
- Source-to-sink tracing
- Basic and advanced taint tracking
- Framework-aware analysis (Pro+)
- Global taint flow (Enterprise)
- Custom taint rules (Enterprise)

**Use cases:**
- Detect security vulnerabilities across files
- Trace data flow from sources to sinks
- Find injection vulnerabilities
- Analyze framework-specific patterns
- Custom security analysis

### Input Specification

#### Parameters

| Parameter | Type | Required | Community | Pro | Enterprise | Notes |
|-----------|------|----------|-----------|-----|-----------|-------|
| `root_path` | string | Yes | ✓ | ✓ | ✓ | Project root for scanning |
| `sources` | array[string] | No | ✓ | ✓ | ✓ | Data sources to track |
| `sinks` | array[string] | No | ✓ | ✓ | ✓ | Security-critical operations |
| `max_depth` | integer | No | ✓ | ✓ | ✓ | Max analysis depth |

#### Tier-Specific Constraints

**Community:**
- Max modules: 10
- Max depth: 3
- Basic taint tracking only
- Single-module focus

**Pro:**
- Max modules: 100
- Max depth: 10
- Advanced taint tracking
- Framework awareness
- DI resolution

**Enterprise:**
- Max modules: Unlimited
- Max depth: Unlimited
- Global taint flow
- Custom taint rules
- Microservice tracing

### Output Specification

```json
{
  "tier": "community|pro|enterprise",
  "tool_id": "cross_file_security_scan",
  "duration_ms": 1234,
  "data": {
    "success": true,
    "vulnerabilities": [
      {
        "vulnerability_id": "sql-001",
        "type": "sql_injection",
        "source": {
          "file": "/src/api.py",
          "line": 42,
          "symbol": "user_id"
        },
        "sink": {
          "file": "/src/db.py",
          "line": 100,
          "symbol": "execute"
        },
        "path_length": 3,
        "severity": "high"
      }
    ],
    "modules_scanned": 8,
    "taint_paths": 3
  }
}
```

### Tier Comparison Matrix

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|-----------|
| **Max modules** | 10 | 100 | Unlimited |
| **Max depth** | 3 | 10 | Unlimited |
| **Framework aware** | ✗ | ✓ | ✓ |
| **DI resolution** | ✗ | ✓ | ✓ |
| **Global taint** | ✗ | ✗ | ✓ |
| **Custom rules** | ✗ | ✗ | ✓ |

### Error Handling

- `invalid_argument` - Invalid parameters
- `invalid_path` - Path not found
- `timeout` - Scan timeout
- `resource_exhausted` - Exceeded limits (Community: 10 modules, depth 3)
- `internal_error` - Scan error

### Example Requests & Responses

#### Example 1: SQL Injection Tracing (Community)

**Request:**
```json
{
  "root_path": "/src",
  "sources": ["request.args", "request.form"],
  "sinks": ["db.execute"],
  "max_depth": 3
}
```

**Response:**
```json
{
  "tier": "community",
  "tool_id": "cross_file_security_scan",
  "duration_ms": 890,
  "data": {
    "success": true,
    "vulnerabilities": [
      {
        "vulnerability_id": "sql-001",
        "type": "sql_injection",
        "source": {
          "file": "/src/api.py",
          "line": 42,
          "symbol": "request.args.get('id')"
        },
        "sink": {
          "file": "/src/db.py",
          "line": 100,
          "symbol": "db.execute(query)"
        },
        "path": [
          "/src/api.py:42 (source)",
          "/src/handlers.py:15 (process)",
          "/src/db.py:100 (sink)"
        ],
        "severity": "high"
      }
    ],
    "modules_scanned": 5,
    "taint_paths": 1
  }
}
```

### Performance Considerations

- **Community**: 500-2000ms (10 modules max)
- **Pro**: 1000-5000ms (100 modules max)
- **Enterprise**: 2000-10000ms (unlimited scope)

### Upgrade Paths

**Community → Pro:**
- Increase module limit (10 → 100)
- Increase depth (3 → 10)
- Framework-aware analysis
- DI resolution

**Pro → Enterprise:**
- Unlimited scope
- Global taint flow across all modules
- Custom taint rules
- Microservice boundary crossing
- API to database tracing

---

## Response Envelope Specification

All tools in this category return responses wrapped in a standard envelope:

```json
{
  "tier": "community|pro|enterprise|null",
  "tool_version": "1.x.x",
  "tool_id": "get_call_graph|get_graph_neighborhood|get_project_map|get_cross_file_dependencies|cross_file_security_scan",
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

- **`extract_code`** (extraction-tools.md) - Extract code discovered in graphs
- **`security_scan`** (security-tools.md) - Detailed vulnerability scanning
- **`analyze_code`** (analysis-tools.md) - Analyze code metrics
- **`crawl_project`** (context-tools.md) - Project structure exploration
