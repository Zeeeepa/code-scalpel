# Code Scalpel + Codegen Consolidation - 20-Step Implementation Plan

## Overview

This document outlines the complete 20-step plan to unify community/pro/enterprise features by consolidating Codegen's advanced capabilities into Code Scalpel's MCP framework, making all tiers accessible by default.

## Status Legend
- ✅ Complete
- 🔄 In Progress
- 📋 Planned
- ⏸️ Blocked

---

## Phase 1: Foundation (Steps 1-4) ✅ COMPLETE

### Step 1: Integration Architecture ✅
**Status**: Complete  
**Deliverables**:
- `docs/INTEGRATION_ARCHITECTURE.md` (440 lines)
- Complete system design with 14 sections
- Tool integration matrix (24 tools)
- Data flow diagrams
- Performance targets

### Step 2: API Discovery ✅
**Status**: Complete  
**Deliverables**:
- `tools/api_topology_discovery.py` (500+ lines)
- Analyzed 562 Python files in Codegen
- Dependency and call graphs
- Public API identification

### Step 3: Codegen Bridge ✅
**Status**: Complete  
**Deliverables**:
- `src/code_scalpel/core/codegen_bridge.py`
- Lightweight facade over Codegen
- Auto-discovery of installation
- Tier enum (Community/Pro/Enterprise)

### Step 4: Session Manager ✅
**Status**: Complete  
**Deliverables**:
- `src/code_scalpel/session/codebase_manager.py`
- LRU cache for parsed trees
- Thread-safe session management
- 16 passing tests

---

## Phase 2: Core File Operations (Steps 5-11) 🔄

### Step 5: View File Tool 📋
**Tier**: Community  
**Transaction**: No  
**Implementation**:
```python
class ViewFileTool(CodegenToolAdapter):
    def _execute_impl(self, session, file_path):
        return session.codebase.read_file(file_path)
```

### Step 6: Create File Tool 📋
**Tier**: Community  
**Transaction**: Optional  
**Implementation**:
- Integrate with Codegen's file creation
- Support templates and boilerplate

### Step 7: Edit File Tool 📋
**Tier**: Pro → Community (unified)  
**Transaction**: Mandatory  
**Implementation**:
- AST-aware editing
- Preserve formatting
- Transaction support

### Step 8: Delete File Tool 📋
**Tier**: Pro → Community (unified)  
**Transaction**: Mandatory  
**Implementation**:
- Safe deletion with rollback
- Dependency checking

### Step 9: Rename File Tool 📋
**Tier**: Pro → Community (unified)  
**Transaction**: Mandatory  
**Implementation**:
- Update all imports automatically
- Cross-file reference updates

### Step 10: Replacement Edit Tool 📋
**Tier**: Pro → Community (unified)  
**Transaction**: Optional  
**Implementation**:
- String-based replacements
- Regex support

### Step 11: Global Replacement Edit Tool 📋
**Tier**: Enterprise → Community (unified)  
**Transaction**: Mandatory  
**Implementation**:
- Multi-file replacements
- Scope control (directory, project)

---

## Phase 3: Symbol Operations (Steps 12-15) 📋

### Step 12: Find Symbol Tool 📋
**Tier**: Community  
**Transaction**: No  
**Implementation**:
- Symbol resolution via graph-sitter
- Cross-file symbol lookup

### Step 13: Get Symbol References Tool 📋
**Tier**: Pro → Community (unified)  
**Transaction**: No  
**Implementation**:
- Find all usages
- Call graph integration

### Step 14: Reveal Symbol Tool 📋
**Tier**: Community  
**Transaction**: No  
**Implementation**:
- Navigate to definition
- Show symbol context

### Step 15: Move Symbol Tool 📋
**Tier**: Enterprise → Community (unified)  
**Transaction**: Mandatory  
**Implementation**:
- Move classes/functions between files
- Update all references

---

## Phase 4: Enhanced Integration (Steps 16-18) 📋

### Step 16: Analysis Tools 📋
**Tools**:
- `get_codebase_summary` (Community)
- `get_function_summary` (Community)
- `get_class_summary` (Community)
- `get_symbol_summary` (Pro → Community)

**Implementation**:
- Integrate Codegen's analysis engine
- Generate summaries with AI

### Step 17: Search Tools 📋
**Tools**:
- `list_directory` (Community)
- `search_files_by_name` (Community)
- `ripgrep_search` (Pro → Community)
- `semantic_search` (Enterprise → Community)

**Implementation**:
- Integrate existing search infrastructure
- Add semantic search via embeddings

### Step 18: Git Operations 📋
**Tools**:
- `get_diff` (Community)
- `commit_changes` (Pro → Community)
- `create_pull_request` (Enterprise → Community)
- `push_changes` (Enterprise → Community)

**Implementation**:
- Wrap Codegen's Git integration
- Transaction-aware commits

---

## Phase 5: Testing & Validation (Steps 19-20) 📋

### Step 19: Integration Testing 📋
**Deliverables**:
- End-to-end test suite
- Performance benchmarks
- Regression tests
- Load testing (100+ concurrent sessions)

**Targets**:
- <100ms latency (cached operations)
- >99.9% transaction success rate
- 100+ concurrent sessions supported

### Step 20: Documentation & Release 📋
**Deliverables**:
- User documentation
- API reference
- Migration guide
- Example workflows
- Release notes

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Latency** | <100ms (cached) | TBD |
| **Reliability** | >99.9% success | TBD |
| **Scalability** | 100+ sessions | TBD |
| **Test Coverage** | >80% | 100% (Phase 1) |
| **Tier Unification** | All features accessible | 0% → 100% |

---

## Architecture Decisions

### Key Principles
1. **Tier Unification**: All features accessible by default
2. **Backward Compatibility**: Existing tier system preserved for business continuity
3. **Performance First**: Lazy loading and caching built-in from day one
4. **Production Ready**: Observability, error handling, resource limits

### Technology Stack
- **Parsing**: graph-sitter (from Codegen)
- **Caching**: LRU cache with TTL
- **Transactions**: ACID via Codegen's TransactionManager
- **Protocol**: MCP (Model Context Protocol)
- **Testing**: pytest with 80%+ coverage target

---

## Timeline Estimate

| Phase | Steps | Estimated Time | Status |
|-------|-------|----------------|--------|
| Phase 1 | 1-4 | 2 weeks | ✅ Complete |
| Phase 2 | 5-11 | 3 weeks | 📋 Planned |
| Phase 3 | 12-15 | 2 weeks | 📋 Planned |
| Phase 4 | 16-18 | 2 weeks | 📋 Planned |
| Phase 5 | 19-20 | 1 week | 📋 Planned |
| **Total** | **20** | **10 weeks** | **20% Complete** |

---

## Risk Mitigation

### Identified Risks
1. **Codegen Dependency**: Tight coupling to Codegen internals
   - **Mitigation**: Bridge pattern with facade layer
   
2. **Performance Degradation**: Additional abstraction layers
   - **Mitigation**: Aggressive caching, lazy loading, benchmarking
   
3. **Breaking Changes**: Codegen API changes
   - **Mitigation**: Version pinning, comprehensive tests
   
4. **State Management**: MCP stateless vs Codebase stateful
   - **Mitigation**: Session-scoped instances with cleanup

---

## Next Steps

1. **Immediate**: Begin Phase 2 implementation (Steps 5-11)
2. **Week 1**: Complete core file operations
3. **Week 2**: Validate with integration tests
4. **Week 3**: Begin Phase 3 (symbol operations)

---

## References

- [Integration Architecture](./INTEGRATION_ARCHITECTURE.md)
- [API Topology Discovery](../tools/api_topology_discovery.py)
- [Phase 1 Tests](../tests/test_phase1_foundation.py)
- [Codegen Repository](https://github.com/codegen-sh/codegen)

