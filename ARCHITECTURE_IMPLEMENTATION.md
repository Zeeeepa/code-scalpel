"""
# Code Scalpel Architecture Refactoring - Phase 1-3 Implementation Summary

## Objective
Transform Code Scalpel from a loosely coupled set of tools into a unified,
modular architecture with clear abstractions, self-correction capabilities,
and standardized documentation.

## Architectural Vision

### The Three-Layer Flow
```
Input (Raw LLM Request)
  ↓
Normalizer (@normalize_input decorator)
  ↓
Validation Engine (Self-Correction)
  ↓
Language Router (Parser Strategy)
  ↓
Core Logic (lib_scalpel)
  ↓
Response Formatter (Profile-Based Filtering)
  ↓
Output (MCP ToolResponseEnvelope)
```

## Completed Components

### Phase 1: The Kernel (Core Abstractions)

#### 1.1 SourceContext & ProjectContext Models
**File:** `mcp/models/context.py`

**What it solves:**
- Unifies dual-input handling (code vs file_path)
- Removes boilerplate from individual tools
- Provides AST caching to prevent double-parsing
- Enables file change detection via content hashing

**Key classes:**
```python
SourceContext:
  - content: str (source code)
  - origin: str (file path or "memory")
  - language: Language (PYTHON, JAVASCRIPT, TYPESCRIPT, GO, RUST, JAVA, TERRAFORM, YAML, JSON, UNKNOWN)
  - ast_cache: Optional[Any] (parsed AST, excluded from serialization)
  - file_hash: str (SHA256 for change detection)
  - file_size_bytes: int (auto-computed)

ProjectContext:
  - root_path: str (project root directory)
  - max_files: int (tier-dependent limit)
  - max_depth: int (traversal depth limit)
  - include_patterns: list[str] (file glob patterns to include)
  - exclude_patterns: list[str] (directories to skip)
  - scanned_files: list[str] (incremental tracking)

FileMetadata:
  - path, language, size_bytes, line_count, hash, last_modified
```

**Benefits:**
- Single source of truth for code context
- Type-safe with Pydantic validation
- Immutable (freeze=True for safety)
- Serialization-safe (ast_cache excluded)

---

#### 1.2 ToolDefinition & Registry
**File:** `mcp/models/tool_definition.py`

**What it solves:**
- Standardizes how tool capabilities are documented
- Separates "system prompt" (LLM) from "user docs" (humans)
- Enables dynamic example injection based on context
- Makes capabilities tier-aware and discoverable

**Key classes:**
```python
ToolDefinition:
  - tool_id: str (canonical name: "analyze_code")
  - name: str (human-readable: "Code Analyzer")
  - system_prompt: str (minimal, ~100-200 tokens for LLM)
  - documentation: str (verbose, ~1000+ tokens for humans)
  - args_schema: dict (Pydantic/JSON Schema)
  - capabilities: dict[Tier, CapabilitySpec] (tier-specific features)
  - examples: dict[str, str] (lazy-loaded, optional)
  - category: str ("analysis", "extraction", "security", etc)

CapabilitySpec:
  - tier: Tier (community, pro, enterprise)
  - limits: dict[str, Any] (max_files: 100, max_depth: 2)
  - features: list[str] (enabled features)
  - description: str (what's available)

ToolDefinitionRegistry:
  - Centralized registration point
  - Methods: register(), get(), list_all(), list_by_category()
  - Thread-safe singleton pattern
```

**Benefits:**
- Clear separation between marketing (docs) and implementation (schema)
- Examples can be injected dynamically without bloating system prompt
- Tier logic is declarative, not scattered across tool code
- Easy to generate MCP ToolSchema automatically

**Example Usage:**
```python
analyze_code_def = ToolDefinition(
    tool_id="analyze_code",
    name="Code Analyzer",
    system_prompt="Analyze Python/JS code structure (functions, classes, imports).",
    documentation="[Full docs with parameters, returns, examples]",
    args_schema={
        "properties": {
            "code": {"type": "string", "description": "Source code"},
            "file_path": {"type": "string", "description": "Path to file"},
            ...
        },
        "required": ["code", "file_path"]  # Actually should be "at least one"
    },
    capabilities={
        Tier.COMMUNITY: CapabilitySpec(
            tier=Tier.COMMUNITY,
            limits={"max_file_size_mb": 1},
            features=["basic_ast", "functions", "classes"]
        ),
        Tier.PRO: CapabilitySpec(
            tier=Tier.PRO,
            limits={"max_file_size_mb": 10},
            features=["basic_ast", "complexity", "metrics"]
        ),
    }
)

ToolDefinitionRegistry.register(analyze_code_def)
```

---

#### 1.3 Validation Engine (Self-Correction Layer)
**File:** `mcp/validators.py`

**What it solves:**
- Pre-execution validation to catch typos early (fail fast)
- Fuzzy matching using difflib for smart suggestions
- Prevents expensive analysis on invalid inputs
- Enables agents to self-correct from "Did you mean?" hints

**Key classes:**
```python
SymbolExtractor (Shallow Scanner):
  - extract_python_symbols(content) → {imports, functions, classes, attributes}
  - extract_javascript_symbols(content) → same structure
  - Uses AST where possible, regex as fallback
  - Fast, doesn't require full parsing

SemanticValidator:
  - validate_symbol_exists(context, symbol_name, type="any")
    Raises: ValidationError with suggestions if symbol not found
  - validate_import_exists(context, import_name)
    "Did you mean: pandas?" if typo detected
  - Symbol caching by file hash (expensive ops cached)

StructuralValidator:
  - validate_python_syntax(context) → raises on SyntaxError
  - validate_file_size(context, max_bytes) → tier-aware limits

ValidationError:
  - error: str (message)
  - suggestions: list[str] (fuzzy matches for correction)
```

**Benefits:**
- Catch agent hallucinations before expensive analysis
- Provide actionable suggestions ("Did you mean...")
- Reduce token waste on invalid requests
- Enable self-correction without human intervention

**Example:**
```python
validator = get_symbol_validator()

try:
    validator.validate_symbol_exists(source_context, "process_dta", "function")
except ValidationError as e:
    # e.message: "Symbol 'process_dta' not found..."
    # e.suggestions: ["process_data"]
    # Agent sees this and retries with correct name
```

---

### Phase 2: Input & Language Processing

#### 2.1 @normalize_input Decorator
**File:** `mcp/normalizers.py`

**What it solves:**
- Removes boilerplate from every tool (if code is None and file_path is None...)
- Centralizes file I/O, validation, and error handling
- Auto-detects language and creates SourceContext
- Applies tier-based file size limits
- Supports both async and sync functions

**Key components:**
```python
@normalize_input(tool_id="analyze_code")
async def my_tool(source_context: SourceContext, ...other params):
    # source_context is guaranteed valid and complete
    pass

# Decorator handles:
# 1. XOR validation: exactly one of code or file_path
# 2. File existence check
# 3. Tier-based size limit check
# 4. File reading with encoding error handling
# 5. Language auto-detection
# 6. SourceContext creation
# 7. Passes context as first arg to function
```

**Helper functions:**
```python
validate_file_exists(path) → abs_path
read_file_content(path, encoding="utf-8") → str
check_file_size_limit(path, max_bytes) → None (raises on excess)
InputNormalizationError (ValueError subclass)
```

**Benefits:**
- Single decorator eliminates 30+ lines of boilerplate per tool
- Consistent error messages across all tools
- Unified file validation and reading
- Language detection integrated into tool input flow

---

#### 2.2 LanguageRouter (Multi-Language Support)
**File:** `mcp/routers.py`

**What it solves:**
- Unified language detection across multiple strategies
- Graceful degradation for unsupported languages
- Clear separation of parser tiers (AST vs regex vs text)
- Confidence scoring for detection results

**Key classes:**
```python
LanguageDetectionResult:
  - language: Language (detected language)
  - confidence: float (0.0-1.0)
  - detected_by: str ("extension", "shebang", "content", "fallback")

LanguageRouter:
  # Tier 1: Full AST parsing
  TIER_1_LANGUAGES = {
      PYTHON: ["py", "pyw"],
      JAVASCRIPT: ["js"],
      TYPESCRIPT: ["ts", "tsx"]
  }
  
  # Tier 2: Regex/text analysis
  TIER_2_LANGUAGES = {
      GO: ["go"],
      RUST: ["rs"],
      JAVA: ["java"],
      TERRAFORM: ["tf"],
      YAML: ["yaml"],
      JSON: ["json"]
  }
  
  @classmethod
  detect(content, file_path=None, language_override=None) → LanguageDetectionResult
  
  @classmethod
  get_parser_tier(language) → 1|2|3
  
  @classmethod
  can_do_ast_analysis(language) → bool
  
  @classmethod
  get_analysis_mode(language) → "ast"|"regex"|"text"
```

**Detection strategies (in order):**
1. Explicit override (if provided)
2. File extension (.py → Python)
3. Shebang (#! python)
4. Content patterns (import, def, function, etc)
5. Fallback to UNKNOWN

**Graceful degradation:**
- Tier 1: Native AST or tree-sitter parsing
- Tier 2: Regex-based function/class extraction
- Tier 3: Raw text, no structural analysis

**Benefits:**
- Language-agnostic tools (one tool, many languages)
- Confidence scores help agents decide trust level
- Clear tier expectations prevent surprises
- No hard failures on unknown languages

---

### Phase 3: Output Formatting

#### 3.1 ResponseFormatter (Profile-Based Filtering)
**File:** `mcp/response_formatter.py`

**What it solves:**
- Centralizes token-budget control
- Enables per-call profile overrides
- Connects response_config.json to runtime behavior
- Removes token-heavy optional fields based on profile

**Key classes:**
```python
ResponseProfile:
  - name: str ("minimal", "standard", "verbose", "debug")
  - include_envelope_fields: set[str] (tier, tool_version, error, etc)
  - exclude_data_fields: set[str] (raw_ast, intermediate_results, etc)
  - preserve_structure: bool (keep nested objects or flatten)

PROFILE_MINIMAL:
  # Envelope fields: none
  # Excluded data: raw_ast, intermediate_results, timing, metadata, duration_ms
  # ~50-100 tokens

PROFILE_STANDARD:
  # Envelope fields: error, upgrade_hints
  # Excluded data: raw_ast, intermediate_results, timing
  # ~100-500 tokens (default)

PROFILE_VERBOSE:
  # Envelope fields: tier, tool_version, error, upgrade_hints, duration_ms
  # Excluded data: raw_ast, intermediate_results
  # ~500-2000 tokens

PROFILE_DEBUG:
  # Envelope fields: all (tier, tool_version, tool_id, request_id, etc)
  # Excluded data: none (everything included)
  # unlimited tokens

ResponseFormatter:
  @staticmethod
  get_profile(profile_name: Optional[str]) → ResponseProfile
  
  @staticmethod
  filter_data(data: Any, profile: ResponseProfile) → filtered
  
  @staticmethod
  resolve_profile_cascading(tool_argument_profile=None) → ResponseProfile
  # Precedence: argument → config → 'standard'
  
  @staticmethod
  list_profiles() → ["minimal", "standard", "verbose", "debug"]
```

**Benefits:**
- Dynamic token budget control without changing code
- Users can override globally (config) or per-call (argument)
- Recursive filtering preserves nested structure
- Easy to add new profiles without touching tools

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Tool Function                        │
│  async def analyze_code(code=None, file_path=None, ...)     │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────▼──────────────┐
         │  @normalize_input        │
         │  Decorator               │
         │  (Removes boilerplate)   │
         └───────────┬──────────────┘
                     │
      ┌──────────────▼──────────────┐
      │  Input Normalization        │
      │  - XOR validation           │
      │  - File I/O                 │
      │  - Size limits              │
      │  Creates SourceContext      │
      └──────────────┬──────────────┘
                     │
        ┌────────────▼────────────┐
        │  Language Router         │
        │  Auto-detect language    │
        │  Graceful degradation    │
        │  Tier 1/2/3 routing      │
        └────────────┬────────────┘
                     │
          ┌──────────▼──────────┐
          │  Validation Engine  │
          │  (Self-Correction)  │
          │  - Shallow scan     │
          │  - Fuzzy matching   │
          │  - "Did you mean?"  │
          └──────────┬──────────┘
                     │
       ┌─────────────▼─────────────┐
       │  Core Logic (lib_scalpel) │
       │  AST parsing              │
       │  Analysis/extraction      │
       │  Returns typed data       │
       └─────────────┬─────────────┘
                     │
        ┌────────────▼────────────┐
        │  ResponseFormatter      │
        │  - Profile resolution   │
        │  - Data filtering       │
        │  - Structure preserved  │
        │  - Token budget control │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────────┐
        │  ToolResponseEnvelope       │
        │  (MCP contract wrapper)     │
        │  - Tier metadata            │
        │  - Error/upgrade_hints      │
        │  - Filtered data            │
        └────────────┬────────────────┘
                     │
              ┌──────▼──────┐
              │  JSON-RPC   │
              │  Response   │
              └─────────────┘
```

---

## Integration Points

### How lib_scalpel Fits In

**Current State (Phase 3 complete):**
- Tools call lib_scalpel functions directly (existing pattern)
- ResponseFormatter filters lib_scalpel outputs based on profile
- SourceContext provides parsed code + metadata to lib_scalpel

**Future (Phase 4-5, TBD):**
- Refactor tools to "thin wrappers" calling lib_scalpel.{analyze,extract,etc}
- lib_scalpel becomes the single source of logic
- Tools become pure I/O controllers

### How response_config.json Fits In

```json
{
  "global": {
    "profile": "standard",  // default profile
    "exclude_empty_arrays": true,
    "exclude_null_values": true
  },
  "tool_overrides": {
    "analyze_code": {
      "profile": "verbose",  // override for this tool
      "exclude_fields": ["raw_ast"]
    }
  }
}
```

**Resolution order:**
1. Tool invocation: `profile="verbose"` (highest priority)
2. Tool config: `tool_overrides.analyze_code.profile`
3. Global config: `global.profile`
4. Default: `"standard"`

---

## Implementation Files Created

| File | Purpose | Classes/Functions |
|------|---------|-------------------|
| `mcp/models/context.py` | Context models | SourceContext, ProjectContext, FileMetadata, Language |
| `mcp/models/tool_definition.py` | Tool metadata | ToolDefinition, CapabilitySpec, ToolDefinitionRegistry, Tier |
| `mcp/validators.py` | Validation engine | SymbolExtractor, SemanticValidator, StructuralValidator, ValidationError |
| `mcp/routers.py` | Language detection | LanguageRouter, LanguageDetectionResult |
| `mcp/normalizers.py` | Input decorator | @normalize_input, InputNormalizationError, validate_file_exists, etc |
| `mcp/response_formatter.py` | Output filtering | ResponseFormatter, ResponseProfile, PROFILE_* constants |

---

## Next Steps (Waves 1-3)

### Wave 1: High-Traffic Tool Refactoring
**Goal:** Prove the pattern works on frequently-used tools

1. **analyze_code refactoring:**
   - Generate "golden master" test output (current implementation)
   - Create ToolDefinition for analyze_code
   - Add @normalize_input decorator
   - Run tests: new output == golden output
   - Add validation layer

2. **extract_code refactoring:**
   - Same pattern as analyze_code
   - Ensure dual-input (code or file_path) works
   - Test with Python and JavaScript

### Wave 2: Project-Level Tools
**Goal:** Apply ProjectContext to multi-file tools

1. **get_project_map** → uses ProjectContext
2. **validate_paths** → uses ProjectContext for scoping

### Wave 3: Specialized Tools
**Goal:** Validate patterns work for complex tools

1. **security_scan** → validation + language routing
2. **oracle generation** → ResponseFormatter + lib_scalpel integration

---

## Key Design Decisions

### 1. Immutable SourceContext
- Pydantic with frozen=False (for flexibility during tests)
- AST cached but not serialized (exclude=True)
- Hash-based change detection

### 2. Unified Input Pattern
- Exactly one of: code OR file_path (never both, never neither)
- Decorator enforces at runtime
- Clear error messages guide users

### 3. Pre-Execution Validation
- Runs BEFORE expensive analysis (fail fast)
- Uses shallow scanning (regex + light AST)
- Fuzzy matching prevents hallucinations

### 4. Graceful Language Degradation
- Tier 1: Full AST (Python, JS/TS)
- Tier 2: Regex parsing (Go, Rust, Java, Terraform, YAML, JSON)
- Tier 3: Raw text (unknown languages)
- No hard failures; tools adapt to available tiers

### 5. Profile Cascading
- Runtime override (tool argument)
- Config override (response_config.json)
- Default to 'standard'
- Enables fine-grained token control

---

## Testing Strategy

### Unit Tests (per-component)
```python
# test_context.py
def test_source_context_hash_computation()
def test_source_context_change_detection()
def test_project_context_file_tracking()

# test_validators.py
def test_symbol_extraction_python()
def test_fuzzy_matching_suggestions()
def test_validation_error_handling()

# test_routers.py
def test_language_detection_by_extension()
def test_language_detection_by_content()
def test_parser_tier_assignment()

# test_normalizers.py
def test_normalize_input_code_branch()
def test_normalize_input_file_branch()
def test_size_limit_enforcement()

# test_response_formatter.py
def test_profile_resolution()
def test_data_filtering()
def test_field_exclusion()
```

### Integration Tests (end-to-end)
```python
# Golden Master Testing (Wave 1)
def test_analyze_code_refactored_equals_original():
    # Run current analyze_code on fixture.py
    original = current_analyze_code(fixture_content)
    
    # Run refactored analyze_code
    new = refactored_analyze_code(code=fixture_content)
    
    # Assert outputs match (structure, not tokens)
    assert normalize(original) == normalize(new)
```

---

## Success Criteria

### Phase 1-3 (Completed)
✅ SourceContext models created and validated  
✅ ToolDefinition system with 3-tier docs created  
✅ Validation engine with fuzzy matching created  
✅ @normalize_input decorator handles dual inputs  
✅ LanguageRouter supports graceful degradation  
✅ ResponseFormatter with cascading profiles created  

### Wave 1 (In Progress)
⏳ analyze_code refactored with decorator + validation  
⏳ extract_code refactored with dual-input support  
⏳ Golden master tests prove parity  

### Wave 2 (Planned)
⏳ ProjectContext applied to multi-file tools  
⏳ get_project_map refactored  
⏳ validate_paths refactored  

### Wave 3 (Planned)
⏳ security_scan integration  
⏳ oracle tools integration  
⏳ All tools using unified patterns  

---

## Metrics & Observability

### Token Efficiency
- Track tokens/response for each profile
- Minimal: ~50-100 tokens (data only)
- Standard: ~100-500 tokens (+ error/hints)
- Verbose: ~500-2000 tokens (+ envelope)
- Debug: unlimited

### Language Coverage
- Tier 1: 3 languages (Python, JS/TS)
- Tier 2: 6 languages (Go, Rust, Java, Terraform, YAML, JSON)
- Tier 3: All others (graceful fallback)

### Validation Hit Rate
- Track: validation errors caught/total requests
- Self-correction rate: agent retries after "Did you mean?"
- Goal: >80% catch rate for common typos

### Response Time
- Track: parse time (before validation)
- Track: validation time (shallow scan)
- Track: analysis time (core logic)
- Track: formatting time (filtering)

---

## Glossary

| Term | Definition |
|------|-----------|
| SourceContext | Unified representation of a single source file |
| ProjectContext | Unified representation of a project directory |
| ToolDefinition | Metadata about a tool (docs, schema, capabilities) |
| LanguageRouter | Routes code to appropriate parser based on language |
| @normalize_input | Decorator that creates SourceContext from code or file |
| ValidationEngine | Pre-execution validation with fuzzy matching |
| ResponseFormatter | Filters output based on profile (token budget control) |
| ResponseProfile | Configuration for output detail levels |
| Golden Master | Reference output for regression testing |
| Graceful Degradation | Tier system: AST → regex → text |
| Cascading | Precedence: argument → config → default |

---

## References

- **Strategic Document:** Master Plan (this document)
- **Config Schema:** `.code-scalpel/response_config.schema.json`
- **Config Instance:** `.code-scalpel/response_config.json`
- **MCP Contract:** `mcp/contract.py`
- **Licensing:** `licensing/features.py`
"""
