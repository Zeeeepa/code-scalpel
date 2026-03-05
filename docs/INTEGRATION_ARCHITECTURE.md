# Code Scalpel + Codegen Integration Architecture

## Executive Summary

This document defines the architecture for integrating Codegen's graph-sitter-based file editing capabilities into Code Scalpel's MCP server framework. The integration enables seamless codebase file edits while preserving Code Scalpel's tier system and maintaining backward compatibility.

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Client (Claude, etc.)                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │ MCP Protocol
┌────────────────────────────────▼────────────────────────────────┐
│                   Code Scalpel MCP Server                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Session Manager                              │   │
│  │  - Codebase instance lifecycle                            │   │
│  │  - Parse tree caching (LRU)                               │   │
│  │  - Transaction state management                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Tool Adapter Layer                           │   │
│  │  - Codegen tool → MCP tool wrapping                       │   │
│  │  - Tier-based access control                              │   │
│  │  - Parameter validation                                   │   │
│  │  - Error translation                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Integrated Tools                             │   │
│  │  File Ops  │ Symbol Ops │ Analysis │ Git │ Search        │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────┐
│                      Codegen Core                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Codebase Class                               │   │
│  │  - graph-sitter parsing                                   │   │
│  │  - Symbol resolution                                      │   │
│  │  - Dependency tracking                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Transaction Manager                          │   │
│  │  - ACID guarantees                                        │   │
│  │  - Checkpoint/rollback                                    │   │
│  │  - Undo/redo                                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Indexing System                              │   │
│  │  - Code index (symbols)                                   │   │
│  │  - File index (metadata)                                  │   │
│  │  - Symbol index (references)                              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Key Components

### 2.1 Session Manager

**Purpose**: Manage Codebase instances per MCP session with caching and resource management.

**Responsibilities**:
- Create/destroy Codebase instances
- Cache parsed trees (LRU with TTL)
- Manage transaction state
- Handle session timeouts
- Resource cleanup

**Implementation**:
```python
class CodebaseSessionManager:
    def __init__(self, max_sessions=100, cache_size=1000, session_ttl=3600):
        self._sessions: Dict[str, SessionContext] = {}
        self._parse_cache = LRUCache(maxsize=cache_size)
        self._metrics = MetricsCollector()
        
    async def get_or_create_session(self, session_id: str, workspace_path: Path) -> Codebase:
        """Get existing session or create new one"""
        
    async def cleanup_session(self, session_id: str):
        """Clean up session resources"""
        
    def get_cached_tree(self, file_path: Path) -> Optional[Tree]:
        """Get cached parse tree"""
```

### 2.2 Tool Adapter Base Class

**Purpose**: Wrap Codegen LangChain tools as MCP tools with tier control.

**Responsibilities**:
- Convert LangChain tool interface to MCP
- Enforce tier-based access control
- Validate parameters
- Translate errors
- Log invocations

**Implementation**:
```python
class CodegenToolAdapter(BaseTool):
    def __init__(self, codegen_tool: BaseTool, tier: Tier, requires_transaction: bool = False):
        self.codegen_tool = codegen_tool
        self.tier = tier
        self.requires_transaction = requires_transaction
        
    async def execute(self, session_id: str, **kwargs) -> ToolResult:
        # 1. Check tier access
        # 2. Get session
        # 3. Wrap in transaction if needed
        # 4. Execute codegen tool
        # 5. Translate result
```

### 2.3 Integrated Tools

#### File Operations (Phase 2)
| Tool | Tier | Transaction | Source |
|------|------|-------------|--------|
| view_file | Community | No | ViewFileTool |
| create_file | Community | Optional | CreateFileTool |
| edit_file | Pro | Mandatory | EditFileTool |
| delete_file | Pro | Mandatory | DeleteFileTool |
| rename_file | Pro | Mandatory | RenameFileTool |
| replacement_edit | Pro | Optional | ReplacementEditTool |
| global_replacement_edit | Enterprise | Mandatory | GlobalReplacementEditTool |

#### Symbol Operations (Phase 3)
| Tool | Tier | Transaction | Source |
|------|------|-------------|--------|
| find_symbol | Community | No | symbol_index.py |
| get_symbol_references | Pro | No | symbol_index.py |
| reveal_symbol | Community | No | RevealSymbolTool |
| move_symbol | Enterprise | Mandatory | MoveSymbolTool |
| semantic_edit | Enterprise | Mandatory | SemanticEditTool |

#### Analysis Tools (Phase 4)
| Tool | Tier | Transaction | Source |
|------|------|-------------|--------|
| get_codebase_summary | Community | No | codebase_analysis.py |
| get_function_summary | Community | No | codebase_analysis.py |
| get_class_summary | Community | No | codebase_analysis.py |
| get_symbol_summary | Pro | No | codebase_analysis.py |

#### Search Tools (Phase 4)
| Tool | Tier | Transaction | Source |
|------|------|-------------|--------|
| list_directory | Community | No | ListDirectoryTool |
| search_files_by_name | Community | No | SearchFilesByNameTool |
| ripgrep_search | Pro | No | RipGrepTool |
| semantic_search | Enterprise | No | SemanticSearchTool |

#### Git Operations (Phase 4)
| Tool | Tier | Transaction | Source |
|------|------|-------------|--------|
| commit_changes | Pro | No | Codebase.commit() |
| create_pull_request | Enterprise | No | Codebase.create_pr() |
| push_changes | Enterprise | No | Codebase.git_push() |
| get_diff | Community | No | Codebase.get_diff() |

## 3. Data Flow

### 3.1 Tool Invocation Flow

```
1. MCP Client sends tool request
   ↓
2. MCP Server receives request
   ↓
3. Tool Adapter validates tier access
   ↓
4. Session Manager provides Codebase instance
   ↓
5. Transaction Manager creates checkpoint (if needed)
   ↓
6. Codegen tool executes operation
   ↓
7. Result validated and formatted
   ↓
8. Transaction committed/rolled back
   ↓
9. Response sent to MCP Client
```

### 3.2 Transaction Flow

```
BEGIN TRANSACTION
  ↓
CREATE CHECKPOINT
  ↓
EXECUTE OPERATION(S)
  ↓
VALIDATE RESULT
  ├─ Success → COMMIT
  └─ Failure → ROLLBACK TO CHECKPOINT
```

## 4. State Management

### 4.1 Session State

Each MCP session maintains:
- **Codebase instance**: Parsed trees, indexes, symbol tables
- **Transaction state**: Active transaction, checkpoints, pending operations
- **Cache state**: Recently accessed files, parse trees
- **Metrics**: Operation counts, latencies, errors

### 4.2 Cache Strategy

**Parse Tree Cache**:
- LRU eviction with configurable size (default: 1000 trees)
- TTL-based expiration (default: 1 hour)
- Invalidation on file modification
- Shared across sessions for same workspace

**Index Cache**:
- Symbol index cached per workspace
- Incremental updates on file changes
- Rebuild on major changes (>10% of files)

## 5. Error Handling

### 5.1 Error Categories

1. **Tier Access Errors**: User lacks required tier
2. **Validation Errors**: Invalid parameters
3. **Parse Errors**: Syntax errors in code
4. **Transaction Errors**: Rollback failures
5. **Resource Errors**: Out of memory, disk space
6. **Network Errors**: Git operations, API calls

### 5.2 Error Translation

Codegen exceptions → MCP error responses:
```python
try:
    result = codegen_tool.execute(**params)
except ParseError as e:
    return MCPError(code="PARSE_ERROR", message=str(e), details={...})
except TransactionError as e:
    return MCPError(code="TRANSACTION_ERROR", message=str(e), details={...})
```

## 6. Performance Optimization

### 6.1 Lazy Loading

- Language grammars loaded on first use
- Parse trees created on demand
- Indexes built incrementally

### 6.2 Caching

- Parse trees cached with LRU eviction
- Symbol indexes cached per workspace
- File metadata cached

### 6.3 Streaming

- Large file operations stream results
- Progress callbacks for long operations
- Chunked responses for large outputs

## 7. Security Considerations

### 7.1 Tier Enforcement

- All tools check tier before execution
- Tier checks cannot be bypassed
- Audit log for tier violations

### 7.2 Resource Limits

- Max file size: 10MB (configurable)
- Max parse tree cache: 1GB
- Max concurrent sessions: 100
- Operation timeout: 5 minutes

### 7.3 Sandboxing

- File operations restricted to workspace
- No access to system files
- Git operations require authentication

## 8. Monitoring & Observability

### 8.1 Metrics

- Tool invocation counts
- Operation latencies (p50, p95, p99)
- Cache hit rates
- Transaction success/failure rates
- Memory usage per session

### 8.2 Logging

- Structured logs with correlation IDs
- Log levels: DEBUG, INFO, WARN, ERROR
- Sensitive data redaction

### 8.3 Tracing

- Distributed tracing with OpenTelemetry
- Trace tool invocations end-to-end
- Span annotations for key operations

## 9. Testing Strategy

### 9.1 Unit Tests

- Test each tool adapter individually
- Mock Codegen tools
- Test tier enforcement
- Test error handling

### 9.2 Integration Tests

- Test full MCP → Codegen flow
- Test transaction rollback
- Test concurrent sessions
- Test cache behavior

### 9.3 Performance Tests

- Benchmark tool latencies
- Stress test with 100+ concurrent sessions
- Memory leak detection
- Large codebase tests (10k+ files)

## 10. Deployment

### 10.1 Dependencies

**Codegen Core Package**:
```toml
[dependencies]
codegen-core = "^1.0.0"  # Extracted from Codegen
tree-sitter = "^0.20.0"
tree-sitter-python = "^0.20.0"
tree-sitter-typescript = "^0.20.0"
```

### 10.2 Configuration

```yaml
session:
  max_sessions: 100
  session_ttl: 3600
  cache_size: 1000
  
performance:
  lazy_loading: true
  streaming: true
  max_file_size: 10485760  # 10MB
  
observability:
  metrics_enabled: true
  tracing_enabled: true
  log_level: INFO
```

## 11. Migration Path

### 11.1 Phase 1: Foundation (Week 1-2)
- Extract codegen-core package
- Implement session manager
- Create tool adapter base class

### 11.2 Phase 2: Core Tools (Week 3-4)
- Integrate file operation tools
- Add transaction support
- Comprehensive testing

### 11.3 Phase 3: Advanced Tools (Week 5-6)
- Integrate symbol operations
- Add indexing system
- Performance optimization

### 11.4 Phase 4: Production (Week 7-8)
- Full test coverage
- Documentation
- Deployment automation

## 12. Success Metrics

- **Performance**: <100ms latency for cached operations
- **Reliability**: >99.9% transaction success rate
- **Scalability**: Support 100+ concurrent sessions
- **Compatibility**: 100% backward compatibility with existing Code Scalpel tools
- **Coverage**: >80% test coverage

## 13. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Performance degradation | High | Medium | Establish baselines, continuous benchmarking |
| Memory leaks | High | Medium | Regular profiling, automated leak detection |
| API breaking changes | Medium | High | Semantic versioning, deprecation warnings |
| Integration complexity | High | High | Incremental approach, extensive testing |
| Scope creep | Medium | High | Strict phase boundaries, regular reviews |

## 14. Appendix

### 14.1 Codegen API Surface

**Core Classes**:
- `Codebase`: Main entry point (40KB, 100+ methods)
- `TransactionManager`: ACID transactions
- `Symbol`, `Function`, `Class`: AST node wrappers

**Key Modules**:
- `tree_sitter_parser.py`: graph-sitter integration
- `codebase_context.py`: Codebase class
- `transaction_manager.py`: Transaction system
- `codebase_analysis.py`: Analysis functions

**Tool Count**: 30+ LangChain tools

### 14.2 Code Scalpel API Surface

**MCP Tools**: 23 specialized tools
**Tier System**: Community, Pro, Enterprise
**Protocol**: MCP (Model Context Protocol)

### 14.3 Integration Points

1. **Parsing**: Use Codegen's graph-sitter
2. **File I/O**: Use Codegen's I/O abstractions
3. **Transactions**: Use Codegen's transaction manager
4. **Indexing**: Use Codegen's indexing system
5. **Analysis**: Use Codegen's analysis functions

---

**Document Version**: 1.0
**Last Updated**: 2025-02-14
**Authors**: Codegen Integration Team

