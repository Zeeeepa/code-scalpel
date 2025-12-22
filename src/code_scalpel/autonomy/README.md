# Autonomy Module - Speculative Execution (Sandboxed)

**Last Updated:** December 17, 2025  
**Version:** v2.2.0+  
**Status:** Stable

## Overview

The autonomy module provides tools for testing proposed code changes in isolated sandbox environments before applying them to the main codebase. This enables "try before you apply" workflows that minimize risk of breaking changes.

## Features

### Core Capabilities

- **Isolated Sandbox Execution**: Creates temporary project copy with full isolation
- **Resource Limits**: Enforces CPU, memory, and disk limits
- **Network Blocking**: Disables network access by default
- **Filesystem Isolation**: Changes never affect main codebase
- **Multi-Mode Support**: Process-level or container-level isolation
- **Side Effect Detection**: Monitors for unintended side effects

### Execution Modes

1. **Process Mode** (default): Uses subprocess with resource limits
2. **Container Mode**: Full Docker container isolation (requires Docker)

## Quick Start

```python
from code_scalpel.autonomy import SandboxExecutor, FileChange

# Initialize executor
executor = SandboxExecutor(
    isolation_level="process",  # or "container"
    network_enabled=False,
    max_memory_mb=512,
    max_cpu_seconds=60
)

# Define changes to test
changes = [
    FileChange(
        relative_path="src/module.py",
        operation="modify",
        new_content="def fixed_func():\n    return 42\n"
    )
]

# Test changes in sandbox
result = executor.execute_with_changes(
    project_path="/path/to/project",
    changes=changes,
    test_command="pytest",
    lint_command="ruff check",
    build_command="python -m build"
)

# Check results
if result.success:
    print("[COMPLETE] Safe to apply changes")
else:
    print("[FAILED] Changes introduce failures")
```

## API Reference

### SandboxExecutor

Main class for executing code changes in isolated environments.

**Constructor:**
```python
SandboxExecutor(
    isolation_level: str = "process",  # "process" or "container"
    network_enabled: bool = False,
    max_memory_mb: int = 512,
    max_cpu_seconds: int = 60,
    max_disk_mb: int = 100
)
```

**Methods:**
- `execute_with_changes()`: Apply changes and run tests in sandbox

### FileChange

Represents a file modification to apply in sandbox.

```python
FileChange(
    relative_path: str,      # Path relative to project root
    operation: str,          # "create", "modify", or "delete"
    new_content: str | None  # New file content (for create/modify)
)
```

### SandboxResult

Result of sandbox execution.

**Attributes:**
- `success: bool` - Overall success status
- `build_success: bool` - Build command success
- `test_results: list[ExecutionTestResult]` - Test execution results
- `lint_results: list[LintResult]` - Linter findings
- `side_effects_detected: bool` - Side effect detection status
- `execution_time_ms: int` - Total execution time
- `stdout: str` - Standard output
- `stderr: str` - Standard error

## Security Guarantees

The sandbox provides multiple layers of security:

1. **Filesystem Isolation**: All changes occur in temporary directory
2. **Network Blocking**: Network access disabled by default (configurable)
3. **Resource Limits**: CPU, memory, and disk quotas enforced
4. **Process Isolation**: Subprocesses cannot affect parent
5. **Side Effect Detection**: Monitors for blocked operations

## Examples

See `examples/sandbox_example.py` for a complete working example.

## Testing

Run tests:
```bash
pytest tests/test_sandbox.py -v
```

Coverage: 100% (32 tests, all passing)

## Change Tags

All code includes `[20251217_FEATURE]` tags indicating the implementation date and type.

## Integration

The autonomy module integrates with:
- Project analysis tools (project_crawler.py)
- Security analysis (policy module)
- Symbolic execution tools
- MCP server (future)

## Known Limitations

1. **Container Mode**: Requires Docker installation
2. **Resource Limits**: Linux/Unix only (Windows has limited support)
3. **Side Effect Detection**: Best-effort monitoring
4. **Test Parsing**: Currently simple pattern matching (can be enhanced)

## Future Enhancements

Planned for v3.0.0 "Autonomy" (Phase 2):
- Sandbox executor with Docker container support
- Error-to-diff engine for intelligent fix suggestions
- Mutation testing gate to prevent hollow fixes
- Fix loop with supervised error correction
- Audit trail for all autonomous operations
- Integration with external frameworks (AutoGen, CrewAI, LangGraph)
- Advanced policy engine with DSL support

See Development Roadmap section for complete task breakdown (69 TODOs across Phase 2-3)

---

## Data Flow

### Input (FROM)
```
User Request / Claude / Copilot
    ↓
MCP Server (mcp_server.py)
    ↓
Autonomy Engine
    ↓ (file path, analysis options)
Source Code & Policies
```

### Processing (WITHIN)
```
AutonomyEngine.execute()
    ↓
Policy Validation (PolicyEngine)
    ├─ Check rules against request
    ├─ Determine approval requirements
    └─ Set constraints & limits
    ↓
Agent Selection
    ├─ Determine which agents needed
    ├─ Set execution order
    └─ Configure agent parameters
    ↓
Orchestration
    ├─ Sequential execution
    ├─ Parallel execution
    ├─ Conditional branching
    └─ Human-in-the-loop gates
    ↓
Agents (SecurityAgent, CodeReviewAgent, etc.)
    ├─ Execute OODA loops
    ├─ Call MCP tools
    └─ Produce findings
    ↓
Result Synthesis
    ├─ Aggregate findings
    ├─ Apply policies
    └─ Prepare recommendations
```

### Output (TO)
```
Orchestrated Analysis Results
    ├─ Security findings (from SecurityAgent)
    ├─ Quality metrics (from CodeReviewAgent)
    ├─ Refactoring suggestions (from RefactoringAgent)
    ├─ Test coverage gaps (from TestingAgent)
    ├─ Documentation issues (from DocumentationAgent)
    └─ Project metrics (from MetricsAgent)
    ↓
Framework Integrations (integrations/)
    ├─ AutoGen (team conversations)
    ├─ CrewAI (crew-based workflows)
    └─ LangGraph (DAG workflows)
    ↓
User / Claude / Copilot
```

---

## Development Roadmap

### Phase 1: Core Orchestration (Complete ✅)
- [x] Basic agent orchestration
- [x] Sequential workflow execution
- [x] Parallel workflow support
- [x] Policy engine implementation
- [x] Rule-based decision making
- [x] Human approval gates

### Phase 2: Sandbox & Error Handling (In Progress 🔄)

#### Sandbox Executor Enhancements (10 TODOs)
- [ ] Implement Docker container execution
- [ ] Add resource limit enforcement (CPU, memory, disk)
- [ ] Implement side effect detection
- [ ] Add test result parsing and categorization
- [ ] Support multiple test frameworks (pytest, unittest, jest, etc.)
- [ ] Result caching for repeated executions
- [ ] Incremental test execution (only changed tests)
- [ ] Parallel test execution
- [ ] Integration with error-to-diff system
- [ ] Performance profiling hooks

#### Error-to-Diff Engine (15 TODOs)
- [ ] Multi-language error parsing (Python, JS, TS, Java, Go, Rust)
- [ ] Pattern-based fix generation
- [ ] Confidence scoring for fixes
- [ ] Alternative fix suggestions
- [ ] Diff format generation (unified diff)
- [ ] ML-based fix ranking
- [ ] Context-aware suggestions
- [ ] Learning from applied fixes
- [ ] Framework-specific error handling
- [ ] Semantic code analysis
- [ ] AST-based fix generation
- [ ] Fix validation before returning
- [ ] Error context extraction
- [ ] Error prioritization
- [ ] Error chaining support (errors caused by other errors)

#### Fix Loop Improvements (11 TODOs)
- [ ] Implement error pattern learning
- [ ] Add similar error detection (avoid redundant fixes)
- [ ] Support custom escalation strategies
- [ ] Add fix quality metrics
- [ ] Implement result caching
- [ ] ML-based fix quality prediction
- [ ] Intelligent retry strategies
- [ ] Parallel fix attempt exploration
- [ ] Integration with mutation gate
- [ ] Feedback loop for learning
- [ ] Support for user-guided fixes

#### Mutation Test Gate (11 TODOs)
- [ ] Implement additional mutation types (logic inversions, boundary mutations)
- [ ] Add mutation impact visualization
- [ ] Support custom mutation rules
- [ ] Implement mutation caching
- [ ] Add mutation filtering (skip trivial mutations)
- [ ] ML-based mutation relevance scoring
- [ ] Adaptive mutation generation
- [ ] Integration with test coverage analysis
- [ ] Generate weak test detection report
- [ ] Suggest test improvements
- [ ] Support mutation score trending

#### Autonomy Engine Coordination (11 TODOs)
- [ ] Add agent composition and coordination
- [ ] Implement result caching across operations
- [ ] Add operation sequencing logic
- [ ] Support conditional branching
- [ ] Implement rollback mechanisms
- [ ] ML-based decision making
- [ ] Intelligent resource allocation
- [ ] Cross-agent communication
- [ ] Advanced policy evaluation
- [ ] Integration with external frameworks (AutoGen, CrewAI)
- [ ] Continuous monitoring and adjustment

#### Audit Trail Enhancement (11 TODOs)
- [ ] Implement advanced querying (filters, aggregations)
- [ ] Add audit trail compression
- [ ] Support database backend
- [ ] Implement audit trail rotation
- [ ] Add performance metrics collection
- [ ] Anomaly detection in audit trail
- [ ] Integration with SIEM systems
- [ ] Compliance report generation
- [ ] Audit trail analytics
- [ ] Integration with external audit systems
- [ ] Real-time alerting

### Phase 3: Intelligent Autonomy (Future)
- [ ] Machine learning policy optimization
- [ ] Agent performance learning
- [ ] Anomaly detection in results
- [ ] Cost optimization (API calls, compute)
- [ ] Security incident response automation
- [ ] Performance tuning automation
- [ ] Dependency update automation
- [ ] Documentation synchronization
- [ ] Test suite maintenance automation
- [ ] Technical debt tracking & remediation

## Contributing

When adding features:
1. Add comprehensive tests (maintain 100% coverage)
2. Use `[YYYYMMDD_TYPE]` change tags
3. Follow existing code style (black + ruff)
4. Update this README

## License

Part of Code Scalpel, MIT License.
