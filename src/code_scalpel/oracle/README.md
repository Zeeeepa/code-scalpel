# Oracle: Deterministic Code Generation Constraints

## Overview

The Oracle module generates "Constraint Specifications" that bind Large Language Models (LLMs) to the reality of your codebase. Instead of probabilistic guessing, the Oracle provides deterministic, graph-constrained context that enables LLMs to write code that compiles and integrates correctly on the first try.

## Architecture

### Core Components

**1. Symbol Extractor** (`symbol_extractor.py`)
- Extracts function/class signatures from ASTs
- Resolves type hints and annotations
- Generates strict symbol tables preventing hallucinations

**2. Constraint Analyzer** (`constraint_analyzer.py`)
- Analyzes dependency graphs (from `UniversalGraph`)
- Queries call graphs for inbound/outbound relationships
- Applies architectural rules from governance policies
- Identifies "forbidden edges" violations

**3. Spec Generator** (`spec_generator.py`)
- Combines symbols + constraints + context into Markdown
- Formats for optimal LLM consumption
- Caches results (5-minute TTL) for performance

**4. Data Models** (`models/`)
- Pydantic models for constraint specs
- Topology rules and enforcement policies

### Integration Points

- **Graph Engine:** Uses `UniversalGraph` for dependency analysis
- **Call Graph:** Leverages `CallGraph` for function relationships
- **Parsers:** Reuses existing Python/TypeScript/JavaScript parsers
- **Cache:** Uses unified caching system with LRU eviction
- **Governance:** Reads architectural rules from `.code-scalpel/governance.yaml`
- **Tiers:** Enforces limits via existing tier system

## Usage

### MCP Tool: `write_perfect_code`

```python
result = await client.call_tool(
    "write_perfect_code",
    arguments={
        "file_path": "src/auth.py",
        "instruction": "Add JWT validation using the 'jose' library"
    }
)
# Returns Markdown constraint specification
```

### Output Format

The constraint spec includes:

1. **Instruction** - What needs to be implemented
2. **Strict Symbol Table** - Available functions, classes, types
3. **Graph Constraints** - Callers, dependencies, forbidden edges
4. **Architectural Rules** - Layer boundaries, design patterns
5. **Code Context** - Relevant code slice
6. **Implementation Notes** - Best practices, patterns

### Example Constraint Spec

```markdown
# Code Generation Constraints for src/auth.py

## Instruction
Add JWT validation using the 'jose' library

## Available Symbols

### Functions
- `validate_token(token: str) -> User` (line 45)
  - Validates JWT token and returns User model

### External Libraries
- `jose.jwt`: jwt.decode(), jwt.encode()

## Graph Constraints

### Callers
- `middleware.py::validate_request` - imports this module

### Architectural Rules
- ✓ Can import from "models" layer
- ✗ CANNOT import from "database" layer

## Code Context
```python
def validate_token(token: str) -> User:
    # Add JWT validation here
    pass
```
```

## Configuration

Oracle behavior is configured in `.code-scalpel/governance.yaml`:

```yaml
oracle:
  symbol_extraction:
    include_type_hints: true
    include_decorators: true
    max_signature_depth: 3
  
  graph_constraints:
    max_depth: 5  # Community: 2, Pro: 5, Enterprise: unlimited
    
  context_window:
    max_lines: 200  # Community: 100, Pro: 200, Enterprise: unlimited
```

## Tier Gating

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|------------|
| Symbol table | Basic (own file) | Full + imports | Full + external |
| Graph depth | 1 level | 5 levels | Unlimited |
| Governance rules | None | Active | Active + audit |
| Caching | 5 min | 5 min | 5 min |
| Max specs/day | 100 | Unlimited | Unlimited |

## Performance

- Symbol extraction: <100ms
- Graph analysis: <200ms
- Spec generation: <200ms
- **Total (with caching): <500ms**

Results cached for 5 minutes to reduce repeated computation.

## Testing

Run Oracle tests:

```bash
pytest tests/tools/oracle/ -v
```

Run with coverage:

```bash
pytest tests/tools/oracle/ --cov=src/code_scalpel/oracle --cov-report=html
```

## Best Practices

### When to Use write_perfect_code

✅ **Good use cases:**
- Implementing new features with complex dependencies
- Refactoring code that touches multiple layers
- Integrating third-party libraries
- Following architectural patterns

❌ **Not ideal for:**
- Simple one-liners or trivial changes
- Exploratory/experimental code
- When you know exactly what to write

### Optimization Tips

1. **Be specific with instructions**
   - ❌ "Add validation"
   - ✅ "Add JWT validation that returns User object or raises AuthError"

2. **Target specific files**
   - Larger files = longer constraint specs
   - Consider breaking into smaller functions

3. **Leverage caching**
   - Same file + instruction within 5 minutes = instant
   - Spec is reusable across team

## Roadmap

- **Phase 1 (Current):** `write_perfect_code` tool
- **Phase 2:** `enforce_topology` for architectural linting
- **Phase 3:** `predict_regression_risk` for git-based risk analysis
- **Phase 4:** `semantic_resolve_conflict` and `generate_live_docs`

## Troubleshooting

### Spec generation is slow

Check if caching is enabled:
```bash
# View cache stats
python -c "from code_scalpel.cache.unified_cache import cache; print(cache.stats())"
```

### Missing symbols in constraint spec

- Verify file is valid Python/TypeScript/JavaScript
- Check that imports are resolvable (analyzer needs to find dependencies)
- Pro tip: Run `analyze_code` tool first to validate structure

### Tier limits being enforced too strictly

- Check `limits.toml` for your tier's constraints
- Set `CODE_SCALPEL_TIER=enterprise` for development/testing
- Review governance rules in `.code-scalpel/governance.yaml`

## Contributing

When adding new Oracle features:

1. Add test fixtures in `tests/tools/oracle/fixtures/`
2. Write tests first (TDD)
3. Update this README with new capabilities
4. Ensure coverage ≥95%
5. Add tier gating if appropriate
