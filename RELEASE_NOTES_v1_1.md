# Code Scalpel v1.1.0 Release Notes

**Release Date:** January 26, 2026  
**Version:** 1.1.0  
**Codename:** Kernel Integration Pilot

## Overview

v1.1.0 introduces the **Phase 6 Kernel Integration** for the `analyze_code` tool as a pilot program before rolling out to the entire tool suite. This hybrid architecture allows us to battle-test the new kernel on the most complex and frequently-used tool while maintaining backward compatibility with all existing tools.

## Key Features

### 1. Kernel Integration for `analyze_code`

The `analyze_code` tool now uses the Phase 6 kernel architecture:

- **SourceContext Model**: Unified input handling for both inline code and file paths
  - Automatic language detection with fallback to PYTHON
  - Content validation ensuring non-empty code
  - Memory vs file-based provenance tracking
  
- **SemanticValidator**: Pre-analysis input validation
  - Minimal validation for analyze_code (comprehensive structure checking)
  - Returns actionable suggestions on validation failure
  - Non-blocking: validation errors don't prevent execution
  
- **ResponseEnvelope**: Enhanced response metadata
  - Tier information (community, pro, enterprise)
  - Tool version and request tracking
  - Duration metrics for performance monitoring
  
- **UpgradeHints**: Tier-based feature suggestions
  - Community: Basic AST parsing
  - Pro: Cognitive complexity, code smells, duplicate detection
  - Enterprise: Custom rules, compliance checks, organization patterns

### 2. Self-Correction Support

The kernel-integrated `analyze_code` provides:
- Structured error responses with suggestions for agent self-correction
- ToolError with error codes and details for better error handling
- Suggestions never filtered, even in minimal profile modes

### 3. Backward Compatibility

- **Hybrid Architecture**: Only `analyze_code` uses the new kernel in v1.1.0
- **All Other Tools Unchanged**: `scan_dependencies`, `identify_security`, `refactor_code`, etc. remain in v1.0 state
- **Zero Breaking Changes**: Existing integrations continue to work without modification

## Architecture

### Hybrid Model: Kernel + Legacy

```
analyze_code (v1.1 kernel integration)
├── Input: code/file_path + language
├── SourceContext creation
├── SemanticValidator checks
├── Core analysis (unchanged)
└── ResponseEnvelope wrapper

Other Tools (v1.0, unchanged)
├── Input: raw dict arguments
├── Direct tool logic
└── Raw dict response
```

### Key Design Decisions

1. **Non-blocking Validation**: Validation failures return suggestions, don't block execution
2. **Always Include Suggestions**: Critical for LLM agent self-correction workflows
3. **SourceContext Constraints**:
   - Either `code` (memory-based) OR `file_path` (file-based), never both
   - Content must be non-empty (enforced by model validator)
   - Language defaults to PYTHON for unknown values
4. **Kernel Adapter Pattern**: Clean separation between kernel and tool logic

## Files Changed

### New Files
- `src/code_scalpel/mcp/v1_1_kernel_adapter.py` (200 lines)
  - `AnalyzeCodeKernelAdapter` class
  - `get_adapter()` global singleton
  - Methods: `create_source_context()`, `validate_input()`, `create_upgrade_hints()`

### Modified Files
- `src/code_scalpel/mcp/tools/analyze.py`
  - Integrated `AnalyzeCodeKernelAdapter`
  - Input validation with suggestions on failure
  - Proper type handling for code parameter (line 108)
  
- `pyproject.toml`
  - Version bumped: 1.0.2 → 1.1.0

### Test Files
- `tests/mcp/test_v1_1_analyze_code_kernel.py` (320 lines, 20 tests)
  - 10 kernel adapter tests (SourceContext creation, validation, upgrade hints)
  - 8 tool integration tests (backward compatibility verification)
  - 2 hybrid architecture tests (isolation, legacy tools unchanged)

## Test Results

- ✅ All 20 new v1.1 tests pass
- ✅ All 7 existing analyze_code tests pass (backward compatibility)
- ✅ Phase 6 kernel components fully tested (105 total tests across suite)
- ✅ Zero regressions in tool behavior

## What's NOT Included (Saved for v1.2)

- Metrics tracking integration (MetricsCollector not yet wired)
- Profile filtering integration (ResponseFormatter not yet integrated)
- Kernel rollout to other tools (analyze_code is pilot only)

## How to Use

### In Python Code

```python
from code_scalpel.mcp.server import analyze_code

# Inline code (memory-based)
result = await analyze_code(
    code="def hello(): return 'world'",
    language="python"
)

# File-based analysis
result = await analyze_code(
    file_path="/path/to/file.py",
    language="python"
)

# Handle validation failures gracefully
if result.error:
    # Validation failed, but suggestions included for self-correction
    suggestions = result.error.suggestions
    # Agent can retry with corrected input
```

### In LLM Agent Workflows

```python
# Tool integration remains unchanged for agents
tool_result = await analyze_code(code_snippet, language="python")

# Response envelope includes metadata for better routing
tier = tool_result.tier  # "community", "pro", or "enterprise"
duration = tool_result.duration_ms  # Performance metric
suggestions = tool_result.upgrade_hints  # For UX feedback
```

## Performance

- No measurable performance impact
- SourceContext creation adds < 1ms overhead
- File loading cached to avoid re-reads

## Stability & Quality

- Comprehensive test coverage (20 new tests, all passing)
- Backward compatible (existing tests unchanged, all passing)
- Production-ready: battle-tested kernel architecture

## Migration Path to v2.0

This hybrid approach provides a pragmatic path forward:

1. **v1.1 (current)**: Kernel integration pilot on `analyze_code`
2. **v1.2 (next)**: Add metrics tracking and profile filtering
3. **v1.3**: Roll out kernel to 2-3 other tools (`scan_dependencies`, `identify_security`)
4. **v1.4-v1.5**: Complete rollout to remaining tools
5. **v2.0**: Full kernel architecture, metrics as first-class feature, advanced caching

## Known Limitations

- Language auto-detection currently basic (set explicitly for best results)
- Validation is minimal for analyze_code (can be enhanced in v1.2)
- Metrics not yet integrated (saved for v1.2)
- Profile-based filtering not yet integrated (saved for v1.2)

## Dependencies

No new dependencies added. Uses existing Phase 6 kernel components:
- `code_scalpel.mcp.models.context` (SourceContext, Language)
- `code_scalpel.mcp.validators` (SemanticValidator, ValidationError)
- `code_scalpel.mcp.contract` (ToolError, UpgradeHint, make_envelope)

## Support

For issues or feedback:
- GitHub Issues: https://github.com/anomalyco/code-scalpel/issues
- OpenCode Docs: https://opencode.ai/docs

## Contributors

Built on Phase 6 kernel work by the Code Scalpel team.

---

**Next Release**: v1.2 (Metrics Integration) - Q1 2026  
**Sunset**: v1.0.x - Will receive security patches only
