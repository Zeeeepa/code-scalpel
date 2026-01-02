# get_symbol_references Tool Roadmap

**Tool Name:** `get_symbol_references`  
**Tool Version:** v1.0  
**Code Scalpel Version:** v3.3.1  
**Current Status:** Stable  
**Primary Module:** `src/code_scalpel/mcp/server.py`  
**Tier Availability:** All tiers (Community, Pro, Enterprise)

---

## Configuration Files

| File | Purpose |
|------|---------|
| `src/code_scalpel/licensing/features.py` | Tier capability definitions |
| `.code-scalpel/limits.toml` | Numeric limits (max_files_searched, max_references) |
| `.code-scalpel/response_config.json` | Output filtering |
| `CODEOWNERS` | Ownership attribution (Enterprise) |

---

## Overview

The `get_symbol_references` tool finds all references to a symbol (function, class, variable) across the project for safe refactoring and impact analysis.

**Why AI Agents Need This:**
- **Safe refactoring:** Know all call sites before changing signatures
- **Impact analysis:** Understand blast radius of changes
- **No hallucination:** Real references from AST parsing, not guessed
- **Risk-aware changes:** Enterprise risk scoring prevents blind modifications
- **Team coordination:** CODEOWNERS integration identifies stakeholders

---

## Research Queries for Future Development

### Foundational Research
| Topic | Query | Purpose |
|-------|-------|---------|
| Name Resolution | "identifier resolution algorithms programming languages" | Improve accuracy |
| Scope Analysis | "lexical scoping static analysis implementation" | Better shadowing detection |
| Incremental Parsing | "incremental symbol table construction IDE" | Real-time updates |
| Cross-Language | "cross-language reference finding polyglot projects" | Multi-lang support |

### Language-Specific Research
| Topic | Query | Purpose |
|-------|-------|---------|
| Python Imports | "python import resolution dynamic vs static" | Better import handling |
| JavaScript | "javascript hoisting symbol resolution challenges" | Improve JS accuracy |
| TypeScript | "typescript declaration merging reference finding" | TS module support |
| Dynamic Languages | "dynamic typing static reference analysis approaches" | Ruby/Python/JS |

### Advanced Techniques
| Topic | Query | Purpose |
|-------|-------|---------|
| Type-Aware | "type-directed reference finding static analysis" | Precision improvement |
| ML Enhancement | "machine learning identifier resolution code" | AI-assisted finding |
| Change Impact | "change impact analysis prediction models software" | Better risk scoring |
| Ownership | "code ownership prediction machine learning" | Auto-owner detection |

---

## Current Capabilities (v1.0)

### Community Tier (World-Class Base Features)
- ✅ Find definition location (`definition_location`)
- ✅ Find all usage references (`ast_based_find_usages`)
- ✅ Exact reference matching (`exact_reference_matching`)
- ✅ Comment/string exclusion (`comment_string_exclusion`)
- ✅ Line number, column, and context snippet
- ✅ Test file detection
- ✅ Supports Python (.py files)

**Capability Keys:** `ast_based_find_usages`, `exact_reference_matching`, `comment_string_exclusion`, `definition_location`

**Limits (from limits.toml):**
- `max_files_searched: 10`
- `max_references: 50`

### Pro Tier (Reference Intelligence)
- ✅ All Community features (unlimited)
- ✅ **Project-wide search** (`project_wide_search`)
- ✅ **Reference categorization** (`usage_categorization`)
  - definition, import, call, read, write, method_call
  - instance_method_call, class_method_call, static_method_call
  - decorator, type_annotation, first_assignment, reassignment
- ✅ **Read/write classification** (`read_write_classification`)
- ✅ **Import classification** (`import_classification`)
- ✅ **Scope filtering** (`scope_filtering`) - limit to path prefix
- ✅ **Test file filtering** (`test_file_filtering`) - include/exclude tests
- ✅ Category counts in response

**Capability Keys:** All Community + `project_wide_search`, `usage_categorization`, `read_write_classification`, `import_classification`, `scope_filtering`, `test_file_filtering`

**Limits:** Unlimited (no caps on files or references)

### Enterprise Tier (Impact & Ownership)
- ✅ All Pro features
- ✅ **Impact analysis** (`impact_analysis`)
  - `risk_score`: Weighted 0-100 score
  - `risk_factors`: List of contributing factors
  - `blast_radius`: Number of unique files affected
  - `test_coverage_ratio`: Ratio of references in test files
  - `complexity_hotspots`: High-complexity files with references
  - `impact_mermaid`: Mermaid diagram of reference distribution
- ✅ **CODEOWNERS integration** (`codeowners_integration`)
  - `owners`: Per-reference owner attribution
  - `owner_counts`: Counts by owner
  - `codeowners_coverage`: Ratio of owned references
- ✅ **Change risk assessment** (`change_risk_assessment`)
  - `change_risk`: "low" | "medium" | "high"

**Capability Keys:** All Pro + `impact_analysis`, `codeowners_integration`, `ownership_attribution`, `change_risk_assessment`

**Limits:** Unlimited

---

## Return Model: SymbolReferencesResult

```python
class SymbolReferencesResult(BaseModel):
    # Core fields (All Tiers)
    success: bool                           # Whether search succeeded
    symbol_name: str                        # Name of the searched symbol
    definition_file: str | None             # File where symbol is defined
    definition_line: int | None             # Line where symbol is defined
    references: list[SymbolReference]       # References found (may be truncated)
    total_references: int                   # Total before truncation
    files_scanned: int                      # Number of files scanned
    total_files: int                        # Total candidate files
    files_truncated: bool                   # Whether file scan was truncated
    file_truncation_warning: str | None     # Warning if truncated
    references_truncated: bool              # Whether references were truncated
    truncation_warning: str | None          # Warning if truncated
    
    # Pro Tier
    category_counts: dict[str, int] | None  # Counts by reference category
    
    # Enterprise Tier
    owner_counts: dict[str, int] | None     # Counts by CODEOWNERS owner
    change_risk: str | None                 # "low" | "medium" | "high"
    risk_score: int | None                  # 0-100 weighted score
    risk_factors: list[str] | None          # Contributing factors
    blast_radius: int | None                # Unique files affected
    test_coverage_ratio: float | None       # References in test files
    complexity_hotspots: list[str] | None   # High-complexity files
    impact_mermaid: str | None              # Mermaid diagram
    codeowners_coverage: float | None       # Ratio of owned references
```

### SymbolReference Model

```python
class SymbolReference(BaseModel):
    file: str                               # File path
    line: int                               # Line number
    column: int                             # Column number
    context: str                            # Code snippet
    is_definition: bool                     # Whether this is the definition
    reference_type: str | None              # Category (Pro+)
    is_test_file: bool                      # Whether in test file
    owners: list[str] | None                # CODEOWNERS (Enterprise)
```

---

## Usage Examples

### Community Tier
```python
result = await get_symbol_references("process_order")
# Returns: definition_file, definition_line, references (max 50),
#          files_scanned (max 10), truncation info
```

### Pro Tier
```python
result = await get_symbol_references(
    "process_order",
    scope_prefix="src/services/",  # Only search in this path
    include_tests=False             # Exclude test files
)
# Additional: category_counts populated
# e.g., {"call": 15, "import": 3, "read": 7, "definition": 1}
```

### Enterprise Tier
```python
result = await get_symbol_references("process_order")
# Additional:
# - risk_score: 45
# - risk_factors: ["Multiple files affected (12 files)", "Moderate test coverage (28.5%)"]
# - blast_radius: 12
# - change_risk: "medium"
# - owner_counts: {"@backend-team": 8, "@api-team": 4}
# - impact_mermaid: "graph TD\n    SYMBOL[\"process_order\"]\n    ..."
```

---

## Response Configuration

Output verbosity is controlled by `.code-scalpel/response_config.json`:

```json
{
  "get_symbol_references": {
    "profile": "minimal",
    "exclude_fields": ["search_metadata", "file_scan_order"]
  }
}
```

**Limits Configuration:** Numerical limits are defined in `.code-scalpel/limits.toml`:

```toml
[community.get_symbol_references]
max_files_searched = 10
max_references = 50

[pro.get_symbol_references]
# Unlimited - omit keys

[enterprise.get_symbol_references]
# Unlimited - omit keys
```

---

## MCP Request/Response Examples

### MCP Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "mcp_code-scalpel_get_symbol_references",
    "arguments": {
      "symbol_name": "process_order",
      "project_root": "/home/user/my-project"
    }
  },
  "id": 1
}
```

### Community Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "symbol_name": "process_order",
    "definition_file": "services/order.py",
    "definition_line": 45,
    "references": [
      {
        "file": "services/order.py",
        "line": 45,
        "column": 4,
        "context": "def process_order(order_data: dict) -> Order:",
        "is_definition": true,
        "reference_type": null,
        "is_test_file": false,
        "owners": null
      },
      {
        "file": "handlers/api.py",
        "line": 78,
        "column": 12,
        "context": "    result = process_order(validated_data)",
        "is_definition": false,
        "reference_type": null,
        "is_test_file": false,
        "owners": null
      },
      {
        "file": "tests/test_order.py",
        "line": 23,
        "column": 8,
        "context": "        process_order(mock_data)",
        "is_definition": false,
        "reference_type": null,
        "is_test_file": true,
        "owners": null
      }
    ],
    "total_references": 35,
    "files_scanned": 10,
    "total_files": 125,
    "files_truncated": true,
    "file_truncation_warning": "Community tier: scanned 10/125 files (upgrade to Pro for full search)",
    "references_truncated": false,
    "truncation_warning": null,
    "category_counts": null,
    "owner_counts": null,
    "change_risk": null,
    "risk_score": null,
    "risk_factors": null,
    "blast_radius": null,
    "test_coverage_ratio": null,
    "complexity_hotspots": null,
    "impact_mermaid": null,
    "codeowners_coverage": null
  },
  "id": 1
}
```

### Pro Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "symbol_name": "process_order",
    "definition_file": "services/order.py",
    "definition_line": 45,
    "references": [
      {
        "file": "services/order.py",
        "line": 45,
        "column": 4,
        "context": "def process_order(order_data: dict) -> Order:",
        "is_definition": true,
        "reference_type": "definition",
        "is_test_file": false,
        "owners": null
      },
      {
        "file": "services/__init__.py",
        "line": 5,
        "column": 0,
        "context": "from .order import process_order",
        "is_definition": false,
        "reference_type": "import",
        "is_test_file": false,
        "owners": null
      },
      {
        "file": "handlers/api.py",
        "line": 78,
        "column": 12,
        "context": "    result = process_order(validated_data)",
        "is_definition": false,
        "reference_type": "call",
        "is_test_file": false,
        "owners": null
      }
    ],
    "total_references": 35,
    "files_scanned": 125,
    "total_files": 125,
    "files_truncated": false,
    "file_truncation_warning": null,
    "references_truncated": false,
    "truncation_warning": null,
    "category_counts": {
      "definition": 1,
      "import": 8,
      "call": 18,
      "read": 3,
      "type_annotation": 5
    },
    "owner_counts": null,
    "change_risk": null,
    "risk_score": null,
    "risk_factors": null,
    "blast_radius": null,
    "test_coverage_ratio": null,
    "complexity_hotspots": null,
    "impact_mermaid": null,
    "codeowners_coverage": null
  },
  "id": 1
}
```

### Enterprise Tier Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "symbol_name": "process_order",
    "definition_file": "services/order.py",
    "definition_line": 45,
    "references": [
      {
        "file": "services/order.py",
        "line": 45,
        "column": 4,
        "context": "def process_order(order_data: dict) -> Order:",
        "is_definition": true,
        "reference_type": "definition",
        "is_test_file": false,
        "owners": ["@backend-team", "@alice"]
      },
      {
        "file": "handlers/api.py",
        "line": 78,
        "column": 12,
        "context": "    result = process_order(validated_data)",
        "is_definition": false,
        "reference_type": "call",
        "is_test_file": false,
        "owners": ["@api-team"]
      }
    ],
    "total_references": 35,
    "files_scanned": 125,
    "total_files": 125,
    "files_truncated": false,
    "file_truncation_warning": null,
    "references_truncated": false,
    "truncation_warning": null,
    "category_counts": {
      "definition": 1,
      "import": 8,
      "call": 18,
      "read": 3,
      "type_annotation": 5
    },
    "owner_counts": {
      "@backend-team": 15,
      "@api-team": 12,
      "@test-team": 8
    },
    "change_risk": "medium",
    "risk_score": 45,
    "risk_factors": [
      "Multiple files affected (12 files)",
      "Moderate test coverage (28.5%)",
      "High-complexity callers detected"
    ],
    "blast_radius": 12,
    "test_coverage_ratio": 0.285,
    "complexity_hotspots": [
      "handlers/api.py",
      "services/order.py"
    ],
    "impact_mermaid": "graph TD\n    subgraph Impact\n        SYMBOL[\"process_order\"]\n        F1[\"handlers/api.py (3 refs)\"]\n        F2[\"services/order.py (2 refs)\"]\n        F3[\"tests/ (10 refs)\"]\n        SYMBOL --> F1\n        SYMBOL --> F2\n        SYMBOL --> F3\n    end",
    "codeowners_coverage": 0.92
  },
  "id": 1
}
```

---

## Roadmap

### v1.1 (Q1 2026): Enhanced Detection

#### Community Tier
- [x] ~~Test file detection~~ (Done in v1.0)
- [ ] Better error messages for ambiguous symbols
- [ ] Shadowed variable detection
- [ ] JavaScript/TypeScript support

#### Pro Tier
- [x] ~~Decorator tracking~~ (Done in v1.0)
- [x] ~~Type annotation tracking~~ (Done in v1.0)
- [ ] Dynamic reference detection (getattr, etc.)
- [ ] Reflection-based reference tracking

#### Enterprise Tier
- [ ] Cross-repository references
- [ ] Historical reference tracking
- [ ] Batch reference queries

### v1.2 (Q2 2026): Language Expansion

#### All Tiers
- [ ] JavaScript/TypeScript full support
- [ ] Java reference finding
- [ ] Go reference finding

#### Pro Tier
- [ ] Confidence scoring per reference
- [ ] C/C++ reference finding
- [ ] Rust reference finding

#### Enterprise Tier
- [ ] Multi-language reference graphs
- [ ] Cross-language FFI tracking

### v1.3 (Q3 2026): Performance Optimization

#### All Tiers
- [x] ~~AST caching~~ (Done in v1.0)
- [ ] Faster reference search (<1s for 10K files)
- [ ] Incremental reference indexing

#### Pro Tier
- [ ] Parallel reference search
- [ ] Delta reference updates

#### Enterprise Tier
- [ ] Distributed reference indexing
- [ ] Real-time reference monitoring

### v1.4 (Q4 2026): Advanced Features

#### Pro Tier
- [ ] Reference visualization
- [ ] Refactoring impact preview
- [ ] Automated rename suggestions

#### Enterprise Tier
- [ ] Reference-based compliance checking
- [ ] Automated deprecation warnings
- [ ] Reference policy enforcement

---

## Integration Points

### Related Tools
| Tool | Relationship |
|------|--------------|
| `rename_symbol` | Uses references for safe renames |
| `update_symbol` | Impact analysis before updates |
| `get_call_graph` | Complementary: calls vs. all references |
| `simulate_refactor` | Reference count in risk scoring |

### Export Formats
| Format | Status | Use Case |
|--------|--------|----------|
| **JSON** | ✅ v1.0 | Programmatic analysis |
| **Mermaid** | ✅ v1.0 (Enterprise) | Impact visualization |
| **CSV** | 🔄 v1.2 | Spreadsheet analysis |
| **SARIF** | 🔄 v1.3 | IDE integration |

---

## Competitive Analysis

| Tool | Strengths | Weaknesses | Our Differentiation |
|------|-----------|------------|---------------------|
| **IDE Find References** | Fast, integrated | Single-file focus | Project-wide + ownership |
| **LSP Servers** | Standard protocol | Language-specific | Multi-language unified API |
| **CodeQL** | Powerful queries | Complex setup | Zero-config, tier-based |
| **grep/ripgrep** | Fast, simple | Text-only, false positives | AST-based precision |
| **Sourcegraph** | Enterprise-grade | Self-hosted complexity | MCP-native, simpler |

---

## Known Issues & Limitations

### Current Limitations
- **Dynamic symbols:** Cannot find runtime-only references
- **String-based:** References in strings not detected
- **External usage:** Cannot track usage in external packages

### Planned Fixes
- v1.1: Partial dynamic reference inference
- v1.2: String literal analysis (opt-in)
- v1.3: External package scanning (Enterprise)

---

## Success Metrics

### Performance Targets
- **Search time:** <2s for 10K files
- **Accuracy:** >98% correct references
- **False positive rate:** <2%

### Adoption Metrics
- **Usage:** 100K+ reference searches per month by Q4 2026
- **Use case:** Pre-refactoring validation

---

## Dependencies

### Internal Dependencies
- `ast_tools/call_graph.py` - Call graph analysis
- `analysis/project_crawler.py` - Project scanning
- `cache/unified_cache.py` - Caching

### External Dependencies
- None

---

## Breaking Changes

None planned for v1.x series.

---

**Last Updated:** December 30, 2025  
**Next Review:** March 31, 2026
