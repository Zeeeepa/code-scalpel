# Graph Engine Module

**Purpose:** Code dependency graph construction and analysis

## Overview

This module provides graph-based code analysis for:
- Cross-file dependency tracking
- Call graph construction
- Confidence-based edge weighting
- HTTP endpoint detection and mapping
- Node ID generation and resolution

## Key Components

### graph.py (16,409 LOC)
Core graph construction and analysis:
- `CodeGraph` - Unified dependency graph structure
- `GraphNode` - Represents functions, classes, modules
- `GraphEdge` - Represents dependencies with confidence scores
- Graph traversal algorithms (BFS, DFS, k-hop neighborhood)
- Import resolution and cross-file tracking

**Key Features:**
- Multi-language support (Python, Java, TypeScript, JavaScript)
- Confidence decay for deep dependencies
- Circular import detection
- Subgraph extraction for focused analysis

### confidence.py (9,175 LOC)
Confidence scoring for graph edges:
- `ConfidenceCalculator` - Computes edge confidence
- Depth-based confidence decay (exponential falloff)
- Type inference confidence
- Import resolution confidence
- Default: 0.9^depth decay factor

**Formula:** `C_effective = 1.0 × 0.9^depth`

### http_detector.py (13,316 LOC)
HTTP endpoint detection and tracking:
- Detects Flask/FastAPI/Django routes
- Maps endpoints to handler functions
- Tracks request parameter flow
- Correlates frontend fetch() calls with backend routes

**Key Features:**
- Detects `@app.route`, `@app.get`, `@router.post`, etc.
- Extracts path parameters (`/users/<id>`)
- Identifies request sources (`request.json`, `request.args`)

### node_id.py (6,431 LOC)
Canonical node ID generation:
- `NodeIdGenerator` - Creates unique node identifiers
- Format: `language::module::type::name`
- Example: `python::services::function::process_order`
- Ensures consistent IDs across analysis runs

## Usage

```python
from code_scalpel.graph_engine import CodeGraph, ConfidenceCalculator

# Build graph from project
graph = CodeGraph(project_root="/path/to/project")
graph.build()

# Get k-hop neighborhood
subgraph = graph.get_neighborhood(
    center_node="python::services::function::process_order",
    k=2,
    min_confidence=0.5
)

# Calculate confidence
calc = ConfidenceCalculator()
confidence = calc.calculate_edge_confidence(
    source_node=node1,
    target_node=node2,
    depth=3
)
```

## Integration

Used by:
- `mcp/server.py` - MCP tools: `get_call_graph`, `get_graph_neighborhood`, `get_cross_file_dependencies`
- `symbolic_execution_tools/cross_file_taint.py` - Cross-file taint tracking
- `policy_engine/` - Dependency-based policy enforcement

## v3.0.5 Status

- Graph construction: Stable, 95%+ coverage
- Confidence scoring: Stable
- HTTP detection: Stable
- Supports Python, Java, TypeScript, JavaScript
