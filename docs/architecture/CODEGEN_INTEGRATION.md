# Codegen Integration Architecture

**Status:** In Progress  
**Created:** 2026-02-14  
**Last Updated:** 2026-02-14

## Executive Summary

This document outlines the architecture for integrating Codegen's code manipulation capabilities into Code Scalpel's MCP-based analysis platform, creating a unified code editing and analysis module.

## Goals

1. **Consolidate** Codegen and Code Scalpel into a single cohesive module
2. **Preserve** all existing Code Scalpel functionality (22 MCP tools)
3. **Extend** with Codegen's manipulation, AI, and indexing capabilities
4. **Maintain** backward compatibility for existing users
5. **Use** graph-sitter as the integration bridge

## Architecture Overview

### Current State

**Code Scalpel:**
- MCP (Model Context Protocol) server
- 22 analysis tools (extraction, security, symbolic, graph, policy)
- Tree-sitter based AST parsing
- 3-tier system (Community, Pro, Enterprise)
- Focus: Read-heavy analysis operations

**Codegen:**
- SDK with Codebase abstraction
- Graph-sitter based code manipulation
- Langchain tool integrations
- AI helper layer
- Focus: Write-heavy manipulation operations

### Target State

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified Code Module                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Analysis   │  │ Manipulation │  │  AI Enhanced │      │
│  │   (Scalpel)  │  │  (Codegen)   │  │  Operations  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                  ┌─────────▼─────────┐                       │
│                  │  Protocol Layer   │                       │
│                  │  MCP + Langchain  │                       │
│                  └─────────┬─────────┘                       │
│                            │                                 │
│         ┌──────────────────┴──────────────────┐             │
│         │                                      │             │
│  ┌──────▼───────┐                    ┌────────▼────────┐    │
│  │   Codebase   │                    │     Indexes     │    │
│  │  Abstraction │◄───────────────────┤ Code/File/Symbol│    │
│  └──────┬───────┘                    └────────┬────────┘    │
│         │                                      │             │
│         └──────────────────┬──────────────────┘             │
│                            │                                 │
│                  ┌─────────▼─────────┐                       │
│                  │  Graph-Sitter     │                       │
│                  │  Foundation       │                       │
│                  └───────────────────┘                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Integration Strategy

### Approach: Adapter Pattern with Strangler Fig

We'll use a **hybrid approach** combining:

1. **Adapter Pattern**: Wrap Codegen functionality as MCP tools
2. **Strangler Fig**: Gradually migrate features while maintaining both systems
3. **Facade**: Unified API surface for consumers
4. **Event System**: Lightweight pub/sub for cross-module communication

### Key Principles

1. **Non-Destructive**: Preserve all existing Code Scalpel functionality
2. **Incremental**: Add features one at a time with validation
3. **Tier-Aware**: Extend tier system to new features
4. **Performance-First**: No degradation of existing analysis speed
5. **Test-Driven**: Leverage existing tests, validate at each step

## Module Structure

```
src/code_scalpel/
├── core/                    # Existing analysis tools (PRESERVED)
│   ├── extraction/
│   ├── security/
│   ├── symbolic/
│   ├── graph/
│   └── policy/
│
├── graph_sitter/           # NEW: Unified graph-sitter foundation
│   ├── __init__.py
│   ├── parser.py           # Language-agnostic parsing
│   ├── graph.py            # Graph operations
│   ├── traversal.py        # AST traversal utilities
│   └── resolution.py       # Symbol resolution
│
├── codebase/               # NEW: Core abstraction from Codegen
│   ├── __init__.py
│   ├── codebase.py         # Main Codebase class
│   ├── types.py            # TFunction, TClass, TImport, etc.
│   ├── analysis.py         # get_codebase_summary, etc.
│   └── git_ops.py          # Git operations
│
├── indexes/                # NEW: Fast lookup indexes
│   ├── __init__.py
│   ├── code_index.py       # Full-text code search
│   ├── file_index.py       # File metadata index
│   └── symbol_index.py     # Symbol name/location index
│
├── manipulation/           # NEW: Code transformation tools
│   ├── __init__.py
│   ├── move_symbol.py      # Symbol movement between files
│   ├── refactor.py         # Refactoring operations
│   └── codemod.py          # Codemod runner
│
├── ai/                     # NEW: AI-enhanced operations
│   ├── __init__.py
│   ├── ai_helper.py        # AI client and utilities
│   ├── semantic_search.py  # Embedding-based search
│   └── generation.py       # Code generation helpers
│
├── visualization/          # NEW: Graph visualization
│   ├── __init__.py
│   └── graph_viz.py        # Graphviz integration
│
├── protocols/              # NEW: Protocol adapters
│   ├── __init__.py
│   ├── mcp_adapter.py      # Langchain → MCP adapter
│   └── tool_registry.py    # Dynamic tool registration
│
└── mcp/                    # Existing MCP server (EXTENDED)
    ├── server.py           # Extended with new tools
    ├── protocol.py         # MCP protocol implementation
    └── tools/              # All tools (existing + new)
        ├── analyze.py      # EXISTING
        ├── extraction.py   # EXISTING
        ├── security.py     # EXISTING
        ├── symbolic.py     # EXISTING
        ├── graph.py        # EXISTING
        ├── policy.py       # EXISTING
        ├── codebase_analysis.py  # NEW
        ├── manipulation.py       # NEW
        ├── semantic_search.py    # NEW
        ├── visualization.py      # NEW
        ├── ai_tools.py          # NEW
        └── training_data.py     # NEW
```

## Data Flow

### Analysis Operation (Existing)
```
User Request → MCP Server → Analysis Tool → Tree-Sitter → AST → Result
```

### Manipulation Operation (New)
```
User Request → MCP Server → Manipulation Tool → Codebase → Graph-Sitter → 
  → Symbol Resolution → File Update → Git Commit → Result
```

### AI-Enhanced Operation (New)
```
User Request → MCP Server → AI Tool → Codebase → Index Lookup → 
  → AI Client → LLM API → Result Generation → Result
```

## API Topology

### Codegen APIs to Integrate

**Core Codebase Operations:**
- `Codebase.from_repo(url)` - Load repository
- `Codebase.from_string(code)` - Parse code string
- `Codebase.files` - List all files
- `Codebase.symbols` - Get all symbols
- `Codebase.classes` - Get all classes
- `Codebase.functions` - Get all functions
- `Codebase.get_symbol(name)` - Find symbol by name
- `Codebase.create_file(path, content)` - Create new file
- `Codebase.commit(message)` - Git commit
- `Codebase.create_pr(title, body)` - Create pull request

**Analysis Functions:**
- `get_codebase_summary(codebase)` - High-level overview
- `get_file_summary(file)` - File-level analysis
- `get_class_summary(cls)` - Class structure
- `get_function_summary(func)` - Function details

**AI Operations:**
- `codebase.ai.generate_code(prompt)` - AI code generation
- `codebase.ai.explain_code(code)` - Code explanation
- `codebase.set_ai_key(key)` - Configure AI provider

**Index Operations:**
- `CodeIndex.search(query)` - Full-text search
- `FileIndex.find(pattern)` - File name search
- `SymbolIndex.lookup(name)` - Symbol lookup

**Manipulation:**
- `move_symbol_to_file(symbol, target_file)` - Move symbol
- `rename_symbol(old_name, new_name)` - Rename with updates
- `run_codemod(codemod_func)` - Execute codemod

### MCP Tool Mapping

| Codegen API | MCP Tool Name | Tier | Priority |
|-------------|---------------|------|----------|
| `get_codebase_summary` | `analyze_codebase` | Community | High |
| `get_function_summary` | `analyze_function` | Community | High |
| `move_symbol_to_file` | `move_symbol` | Pro | High |
| `CodeIndex.search` | `search_code` | Community | High |
| `codebase.ai.generate_code` | `generate_code` | Enterprise | Medium |
| `run_codemod` | `run_codemod` | Pro | Medium |
| `visualize_graph` | `visualize_dependencies` | Pro | Low |

## Tier System Extension

### Community Tier (Free)
- All existing analysis tools
- Basic codebase summary
- File and symbol search
- Single-file operations

### Pro Tier
- All Community features
- Cross-file symbol movement
- Advanced refactoring
- Codemod execution
- Visualization
- Limited AI operations (100 requests/month)

### Enterprise Tier
- All Pro features
- Unlimited AI operations
- Function mining for training data
- Custom codemods
- Organization-wide operations
- Advanced analytics

## Performance Considerations

### Caching Strategy

**Cache Layers:**
1. **AST Cache**: Parsed ASTs keyed by file hash
2. **Index Cache**: Symbol/file indexes with incremental updates
3. **Analysis Cache**: Expensive analysis results (complexity, dependencies)
4. **AI Cache**: LLM responses for common queries

**Cache Invalidation:**
- File change → Invalidate AST + dependent analyses
- Git commit → Invalidate all caches for changed files
- Manual refresh → Clear all caches

### Resource Limits

| Operation | Community | Pro | Enterprise |
|-----------|-----------|-----|-----------|
| Max file size | 1 MB | 10 MB | 100 MB |
| Max files analyzed | 100 | 1,000 | Unlimited |
| Concurrent operations | 1 | 5 | 20 |
| Cache size | 100 MB | 1 GB | 10 GB |
| AI requests/month | 0 | 100 | Unlimited |

## Security Considerations

### Input Validation
- Sanitize all file paths (prevent directory traversal)
- Validate code before execution (no eval of untrusted code)
- Rate limit API calls
- Validate AI prompts (no prompt injection)

### Secret Management
- Store API keys in secure vault (not in code)
- Rotate keys regularly
- Audit all key usage
- Encrypt keys at rest

### Sandboxing
- Execute codemods in isolated environment
- Limit file system access
- Timeout long-running operations
- Monitor resource usage

## Migration Path

### Phase 1: Foundation (Weeks 1-2)
- Set up graph-sitter foundation
- Port Codebase abstraction
- Create basic indexes
- Add first MCP tool wrappers

### Phase 2: Core Features (Weeks 3-4)
- Add analysis functions
- Implement symbol movement
- Add search capabilities
- Create visualization tools

### Phase 3: Advanced Features (Weeks 5-6)
- Integrate AI layer
- Add codemod runner
- Implement training data generation
- Add GitHub/Linear integrations

### Phase 4: Polish & Release (Week 7)
- Performance optimization
- Documentation
- Migration guides
- Release v2.0

## Testing Strategy

### Validation Approach
1. **Existing Tests**: Run all existing Code Scalpel tests (must pass)
2. **Integration Tests**: Test new features with existing tools
3. **Performance Tests**: Benchmark against baseline
4. **Compatibility Tests**: Verify API compatibility

### Test Coverage
- Unit tests for each new module
- Integration tests for cross-module operations
- End-to-end tests for complete workflows
- Performance regression tests

## Rollback Plan

### If Integration Fails
1. **Feature Flags**: Disable new features via environment variable
2. **Branch Strategy**: Keep main branch stable, integrate on feature branch
3. **Versioning**: Tag stable versions before major changes
4. **Documentation**: Clear rollback procedures

## Success Metrics

### Technical Metrics
- ✅ All 22 existing tools still functional
- ✅ No performance degradation (< 5% latency increase)
- ✅ 90%+ test coverage for new code
- ✅ Zero breaking changes to existing APIs

### Feature Metrics
- ✅ 15+ new MCP tools added
- ✅ AI integration functional
- ✅ Symbol movement working across files
- ✅ Visualization generating valid graphs

### User Metrics
- ✅ Backward compatible for existing users
- ✅ Clear migration documentation
- ✅ Positive user feedback
- ✅ Adoption of new features

## Open Questions

1. **Graph-sitter version compatibility**: Are Codegen and Code Scalpel using compatible versions?
2. **Dependency conflicts**: Will merging dependencies cause issues?
3. **AI provider support**: Which LLM providers to support (OpenAI, Anthropic, local)?
4. **Index persistence**: SQLite, Redis, or in-memory?
5. **Visualization format**: SVG, PNG, or interactive HTML?

## References

- [Code Scalpel Documentation](../README.md)
- [Codegen SDK Documentation](https://github.com/Zeeeepa/codegen)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Graph-Sitter Documentation](https://tree-sitter.github.io/tree-sitter/)

## Changelog

- **2026-02-14**: Initial architecture document created

