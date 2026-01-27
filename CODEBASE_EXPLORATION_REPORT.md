# Code Scalpel Codebase Exploration Report
## Comprehensive Overview of Licensing, Tiers, MCP Server, and Test Architecture

**Generated:** January 26, 2025
**Scope:** Licensing/tier implementation, MCP tool registration, CLI architecture, and test infrastructure

---

## EXECUTIVE SUMMARY

Code Scalpel implements a sophisticated three-tier licensing system (COMMUNITY/PRO/ENTERPRISE) with:
- **JWT-based cryptographic license validation** (v3.3.0+)
- **21 MCP tools** with tier-based capability gating
- **Declarative feature and tool registries** for runtime access control
- **Comprehensive test infrastructure** with tier-specific test matrices

The architecture separates concerns cleanly: licensing handles validation/tier detection, tiers module provides feature gates and decorators, and MCP tools consume tier information for capability limiting.

---

## 1. LICENSE/TIER IMPLEMENTATION

### 1.1 Licensing Architecture

**Location:** `/src/code_scalpel/licensing/`

**Core Files:**
- `__init__.py` - Module exports and tier enum
- `jwt_validator.py` - JWT signature verification (RS256/HS256)
- `tier_detector.py` - Tier detection from environment/config
- `license_manager.py` - Feature availability and tier management
- `config_loader.py` - TOML-based limits configuration
- `features.py` - Feature capabilities by tier

**Key Classes:**

```python
# Tier enum (3-level hierarchy)
class Tier(Enum):
    COMMUNITY = "community"      # Level 0: Always available, no license required
    PRO = "pro"                  # Level 1: Requires valid JWT
    ENTERPRISE = "enterprise"    # Level 2: Highest tier with org/seat features
```

**Tier Hierarchy for Comparison:**
```python
TIER_LEVELS = {
    "community": 0,    # Free/open-core
    "pro": 1,          # Paid tier with advanced features
    "enterprise": 2    # Full-featured with org management
}
# Tier comparison: enterprise >= pro >= community
```

### 1.2 License Validation Pipeline

**JWT-Based Validation (v3.3.0+):**

1. **Load License Token**
   - Source priority:
     1. Environment variable: `CODE_SCALPEL_LICENSE_PATH` (file path)
     2. Local project: `.code-scalpel/license.jwt`
     3. User config: `~/.config/code-scalpel/license.jwt`
     4. Legacy: `.scalpel-license`
     5. Default: COMMUNITY (no license required)

2. **Validate JWT Signature**
   - Algorithm: RS256 (RSA, production) or HS256 (HMAC, testing)
   - Public key embedded in distribution (RS256)
   - Secret key via environment variable (HS256)
   - File: `licensing/public_key/cs-prod-public-20260124.pem`

3. **Check Expiration**
   - **Strict posture:** Expired licenses NEVER grant paid tier
   - Grace period (7 days) for renewal messaging only
   - No network call required for offline validation

4. **Return Tier**
   - Valid JWT → claims["tier"] (pro/enterprise)
   - Invalid/expired → community (fail-closed)
   - Environment override: `CODE_SCALPEL_TIER` (for testing)

**JWT Claims Structure:**
```json
{
    "iss": "code-scalpel-licensing",
    "sub": "customer_id_12345",
    "tier": "pro" | "enterprise",
    "features": [...],
    "exp": 1735689600,
    "iat": 1704153600,
    "organization": "Acme Corp",
    "seats": 10
}
```

**File:** `/src/code_scalpel/licensing/jwt_validator.py` (90+ lines)
- Class `JWTLicenseValidator` - Main validator
- Class `JWTLicenseData` - Validation result dataclass
- Function `get_current_tier()` - Primary tier lookup
- Function `get_license_info()` - Detailed license information

### 1.3 Tier-Based Feature Mapping

**Feature Tiers (from license_manager.py):**

**COMMUNITY (9 tools):**
- analyze_code, extract_code, update_symbol
- crawl_project, get_file_context, get_symbol_references
- get_call_graph, get_project_map, validate_paths
- security_scan, unified_sink_detect
- generate_unit_tests

**PRO (5 additional tools):**
- symbolic_execute, simulate_refactor, scan_dependencies
- get_cross_file_dependencies, get_graph_neighborhood

**ENTERPRISE (5 additional tools):**
- cross_file_security_scan, verify_policy_integrity
- type_evaporation_scan, autonomous_repair, compliance_report

**Total: 21 MCP tools + 1 Oracle tool = 22 tools**

**Storage:** `/src/code_scalpel/licensing/license_manager.py` (lines 65-92)
```python
FEATURE_TIERS: Dict[str, str] = {
    # COMMUNITY features
    "analyze_code": "community",
    "extract_code": "community",
    # ... (9 community tools)
    
    # PRO features (require tier >= pro)
    "symbolic_execute": "pro",
    "simulate_refactor": "pro",
    # ... (5 pro tools)
    
    # ENTERPRISE features (require tier == enterprise)
    "cross_file_security_scan": "enterprise",
    # ... (5 enterprise tools)
}
```

### 1.4 Capability Envelopes (Limits by Tier)

**Configuration File:** `.code-scalpel/limits.toml`

**Structure:** Tool-specific limits apply at each tier
- Example: `get_cross_file_dependencies`
  - COMMUNITY: max_depth=2, max_files_searched=5
  - PRO: max_depth=5, max_files_searched=50
  - ENTERPRISE: max_depth=unlimited, max_files_searched=unlimited

**Access Pattern:**
```python
# File: /src/code_scalpel/licensing/features.py
capabilities = get_tool_capabilities(tool_id, tier)
# Returns: {"limits": {...}, "capabilities": [list of features]}
```

**Key Limits Enforced:**
- File search depth and breadth
- Reference result counts
- Path exploration limits (symbolic_execute)
- Concurrent operation limits
- Feature-specific capabilities (remediation hints, compliance mapping)

**File:** `/src/code_scalpel/licensing/config_loader.py`
- Function: `get_tool_limits(tool_id, tier)` - Load tier limits
- Function: `load_limits()` - Parse limits.toml
- Function: `merge_limits()` - Combine tier configurations
- Caching: Results cached in-memory with TTL

---

## 2. MCP TOOL REGISTRATION

### 2.1 Tool Registration System

**Architecture:** Decorator-based registration via FastMCP instance

**Shared MCP Instance:** `/src/code_scalpel/mcp/protocol.py`
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP()  # Global shared instance

# Exported for tools to import
from code_scalpel.mcp.protocol import mcp
```

**Tool Registration Pattern:**
```python
@mcp.tool()
async def analyze_code(code: str, language: str = None) -> AnalysisResult:
    """Tool docstring with MCP metadata."""
    # Implementation
    return result
```

**Tools Modules:** `/src/code_scalpel/mcp/tools/`
- `analyze.py` - analyze_code, code_policy_check
- `extraction.py` - extract_code, update_symbol, rename_symbol
- `context.py` - get_file_context, get_symbol_references, get_call_graph
- `graph.py` - get_project_map, get_graph_neighborhood, get_cross_file_dependencies, cross_file_security_scan
- `security.py` - security_scan, unified_sink_detect, scan_dependencies, type_evaporation_scan, verify_policy_integrity
- `symbolic.py` - symbolic_execute, generate_unit_tests, simulate_refactor
- `policy.py` - compliance_report, autonomy governance tools
- `oracle.py` - write_perfect_code (Pro feature - NEW)

**Total Registered Tools: 21 (+ 1 Oracle)**

### 2.2 Tool Schema and Metadata

**Tool Definition System:** `/src/code_scalpel/mcp/models/tool_definition.py`

**Classes:**

```python
@dataclass
class CapabilitySpec:
    """Per-tier capability specification."""
    tier: Tier                    # Which tier (community/pro/enterprise)
    limits: Dict[str, Any]        # Hard limits (max_files, max_depth, etc.)
    features: List[str]           # Enabled features
    description: str              # Tier-specific capability description

@dataclass
class ToolDefinition:
    """Unified tool metadata."""
    tool_id: str                  # Canonical ID (e.g., "analyze_code")
    name: str                      # Human-readable name
    system_prompt: str            # Concise prompt for LLM (100-200 tokens)
    documentation: str            # Full docs for humans (1000+ tokens)
    args_schema: Dict[str, Any]   # JSON schema for parameters
    capabilities: Dict[Tier, CapabilitySpec]  # Tier-specific capabilities
    examples: Optional[Dict[str, str]]  # Lazy-loaded examples
    category: str                 # Tool category (analysis, security, etc.)
    deprecated: bool
    min_version: str

class ToolDefinitionRegistry:
    """Singleton registry of all tool definitions."""
    _definitions: Dict[str, ToolDefinition] = {}
    
    @classmethod
    def register(cls, definition: ToolDefinition) -> None:
        """Register a tool definition."""
    
    @classmethod
    def get(cls, tool_id: str) -> Optional[ToolDefinition]:
        """Get tool definition by ID."""
    
    @classmethod
    def list_all(cls) -> List[ToolDefinition]:
        """List all registered definitions."""
```

**MCP Protocol Schema Generation:**
```python
def to_mcp_tool_schema(self) -> Dict[str, Any]:
    """Convert to MCP ToolSchema format."""
    return {
        "name": self.tool_id,
        "description": self.system_prompt,
        "inputSchema": {
            "type": "object",
            "properties": self.args_schema.get("properties", {}),
            "required": self.args_schema.get("required", [])
        }
    }
```

### 2.3 Tool Visibility and Availability

**Tool Registry (Runtime):** `/src/code_scalpel/tiers/tool_registry.py`

```python
@dataclass
class MCPTool:
    """Definition of an MCP tool."""
    name: str
    tier: str                    # "community", "pro", "enterprise"
    description: str
    handler: Optional[Callable] = None
    parameters: Dict[str, Any]   # Parameter schema
    category: str = "general"
    deprecated: bool = False
    beta: bool = False

# 21 tools defined in DEFAULT_TOOLS
DEFAULT_TOOLS: Dict[str, MCPTool] = {
    # COMMUNITY tools (9)
    "analyze_code": MCPTool(name="analyze_code", tier="community", ...),
    "extract_code": MCPTool(...),
    # ... etc
}

class ToolRegistry:
    """Central registry of MCP tools and tier requirements."""
    
    def is_tool_available(self, tool_name: str) -> bool:
        """Check if tool is available at current tier."""
        tool = self._tools.get(tool_name)
        current_tier_level = TIER_LEVELS.get(get_current_tier(), 0)
        required_level = TIER_LEVELS.get(tool.tier, 0)
        return current_tier_level >= required_level
    
    def get_available_tools(self) -> List[MCPTool]:
        """Get all tools available at current tier."""
    
    def get_tool_tier(self, tool_name: str) -> str:
        """Get minimum required tier for tool."""
```

**Usage from Tools:**
```python
from code_scalpel.tiers import is_tool_available, get_available_tools
from code_scalpel.licensing import get_current_tier

# In tool handler
if not is_tool_available("cross_file_security_scan"):
    raise UpgradeRequiredError(
        tool_id="cross_file_security_scan",
        feature="cross_file_security_scan",
        required_tier="enterprise"
    )
```

### 2.4 Tool Response Contract

**Universal Response Envelope:** `/src/code_scalpel/mcp/contract.py`

```python
class ErrorCode(Literal):
    # Machine-parseable error codes
    "invalid_argument"
    "invalid_path"
    "forbidden"
    "not_found"
    "timeout"
    "too_large"
    "resource_exhausted"
    "not_implemented"
    "upgrade_required"      # Tier-based restriction
    "dependency_unavailable"
    "internal_error"

class ToolError(BaseModel):
    error: str              # Human-readable message
    error_code: ErrorCode   # Machine-parseable code
    error_details: Dict[str, Any]  # Structured details

class ToolResponseEnvelope(BaseModel):
    tier: Optional[str]     # Current tier (community/pro/enterprise)
    tool_version: Optional[str]  # Semantic version
    tool_id: Optional[str]  # Canonical tool ID
    request_id: Optional[str]  # Correlation ID
    # ... response_data, error, metadata ...
```

**Tier Gating Pattern:**
```python
@mcp.tool()
async def cross_file_security_scan(directory: str) -> ToolResponseEnvelope:
    """Cross-module taint tracking (ENTERPRISE only)."""
    current_tier = get_current_tier()
    
    if current_tier != "enterprise":
        raise UpgradeRequiredError(
            tool_id="cross_file_security_scan",
            feature="cross_file_security_scan",
            required_tier="enterprise"
        )
    
    # Implementation
    result = scan_cross_files(directory)
    
    return make_envelope(
        tool_id="cross_file_security_scan",
        tier=current_tier,
        response=result,
        error=None
    )
```

---

## 3. CLI ARCHITECTURE

### 3.1 Entry Points

**Main CLI:** `/src/code_scalpel/cli.py`

**Commands:**
```
codescalpel analyze              - Analyze file/code
codescalpel mcp                  - Start MCP server (stdio transport)
codescalpel mcp --http --port X  - Start MCP server (HTTP transport)
codescalpel server               - Start REST API server (legacy)
codescalpel license install      - Install JWT license
```

**License Command Structure:**
```python
def _license_install(
    source_path: Path,
    dest_path: Optional[Path] = None,
    force: bool = False
) -> int:
    """[20251228_FEATURE] Implements `code-scalpel license install`."""
    
    # 1. Read JWT from source_path
    token = source_path.read_text().strip()
    
    # 2. Validate JWT signature
    validator = JWTLicenseValidator()
    data = validator.validate_token(token)
    if not data.is_valid:
        print(f"Error: {data.error_message}", file=sys.stderr)
        return 1
    
    # 3. Write to destination (default: ~/.config/code-scalpel/license.jwt)
    if dest_path is None:
        xdg_home = Path.home() / ".config"
        dest_path = xdg_home / "code-scalpel" / "license.jwt"
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(token + "\n")
    
    # 4. Report success with tier and expiration
    print(f"✓ Tier: {data.tier}")
    print(f"✓ Expires: {data.expiration_date}")
    
    return 0
```

**MCP Server Startup:**
```python
def start_mcp_server(
    host: str = "127.0.0.1",
    port: int = 5000,
    transport: str = "stdio",  # stdio or streamable-http
    use_https: bool = False,
    ssl_cert: Optional[str] = None,
    ssl_key: Optional[str] = None,
    allow_lan: bool = False,
    tier: Optional[str] = None,
    license_file: Optional[str] = None,
    **kwargs
) -> int:
    """Start the MCP-compliant server."""
    
    # 1. Handle explicit license file path
    if license_file:
        license_path = Path(license_file).expanduser()
        if not license_path.exists():
            print(f"Error: License file not found: {license_file}")
            return 1
        os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(license_path)
    
    # 2. Determine transport protocol
    protocol = "https" if use_https else "http"
    
    # 3. Validate tier argument (if provided)
    if tier and tier not in ("community", "pro", "enterprise"):
        print(f"Error: Invalid tier: {tier}")
        return 1
    
    # 4. Start server
    from code_scalpel.mcp.server import run_server
    run_server(
        host=host,
        port=port,
        transport=transport,
        tier=tier,
        **kwargs
    )
    
    return 0
```

### 3.2 CLI Arguments

**MCP Server Arguments:**
```
--http                 - Use HTTP transport instead of stdio
--port PORT           - Port for HTTP server (default: 5000)
--host HOST           - Host to bind to (default: 127.0.0.1)
--allow-lan          - Allow connections from LAN (not just localhost)
--ssl-cert CERT      - Path to SSL certificate (for HTTPS)
--ssl-key KEY        - Path to SSL key (for HTTPS)
--tier {community,pro,enterprise}  - Override detected tier
--license-file PATH  - Path to JWT license file
```

**License Command Arguments:**
```
license install LICENSE_FILE  - Install JWT license
  --dest PATH               - Destination path (default: ~/.config/code-scalpel/license.jwt)
  --force                   - Overwrite existing license
```

### 3.3 Tier Handling in CLI

**Tier Detection Flow:**
```
1. Check --tier argument (explicit override)
2. Check CODE_SCALPEL_TIER env var
3. Validate license file (--license-file or CODE_SCALPEL_LICENSE_PATH)
4. Fall back to COMMUNITY tier
```

**License Validation at Startup:**
```python
# In start_mcp_server()
from code_scalpel.licensing import JWTLicenseValidator
from code_scalpel.licensing.authorization import compute_effective_tier_for_startup

validator = JWTLicenseValidator()
license_data = validator.validate()

# Compute effective tier (min of licensed tier and requested tier)
effective_tier = compute_effective_tier_for_startup(
    licensed_tier=license_data.tier,
    requested_tier=tier,
    expiration_valid=license_data.is_valid
)
```

---

## 4. MCP SERVER IMPLEMENTATION

### 4.1 Server Architecture

**Main Server File:** `/src/code_scalpel/mcp/server.py`

**Global State:**
```python
CURRENT_TIER = "community"                # Runtime tier
PROJECT_ROOT: Path = Path.cwd()          # Working directory
_PROJECT_ROOT_HOLDER: List[Path] = [...]  # Mutable container for dynamic updates
ALLOWED_ROOTS: List[Path] = []            # Path boundaries for security

# License grace for long-lived server processes
_LAST_VALID_LICENSE_TIER: Optional[str] = None
_LAST_VALID_LICENSE_AT: Optional[float] = None
_MID_SESSION_EXPIRY_GRACE_SECONDS = 24 * 60 * 60  # 24-hour grace
```

**Initialization Flow:**
```python
async def main(
    transport: str = "stdio",
    port: int = 5000,
    host: str = "127.0.0.1",
    tier: Optional[str] = None,
    **kwargs
) -> int:
    """Initialize and run the MCP server."""
    
    # 1. Configure logging (stderr only for stdio transport)
    _configure_logging(transport)
    
    # 2. Validate tier and set CURRENT_TIER
    from code_scalpel.licensing.authorization import compute_effective_tier_for_startup
    CURRENT_TIER = compute_effective_tier_for_startup(tier)
    
    # 3. Set project root
    set_project_root(Path.cwd())
    
    # 4. Register all MCP tools
    # (implicit: @mcp.tool() decorators run on import)
    
    # 5. Start server
    await mcp.run(
        transport=transport,
        port=port,
        host=host,
        **kwargs
    )
```

### 4.2 License Validation in Server

**Tier Detection Function:** `/src/code_scalpel/mcp/protocol.py`

```python
def _get_current_tier() -> str:
    """Get current tier from license validation with env var override."""
    
    global _LAST_VALID_LICENSE_TIER, _LAST_VALID_LICENSE_AT
    
    # 1. Check environment override (testing/downgrade)
    requested = _requested_tier_from_env()
    
    # 2. Validate JWT license
    validator = JWTLicenseValidator()
    license_data = validator.validate()
    licensed = "community"
    
    if license_data.is_valid:
        licensed = _normalize_tier(license_data.tier)
        _LAST_VALID_LICENSE_TIER = licensed
        _LAST_VALID_LICENSE_AT = time_module.time()
    else:
        # Check for revocation (immediate downgrade)
        if "revoked" in (license_data.error_message or "").lower():
            licensed = "community"
        # Check for expiration with 24-hour grace
        elif "expired" in (license_data.error_message or "").lower():
            if _LAST_VALID_LICENSE_TIER and _LAST_VALID_LICENSE_AT:
                elapsed = time_module.time() - _LAST_VALID_LICENSE_AT
                if elapsed < _MID_SESSION_EXPIRY_GRACE_SECONDS:
                    licensed = _LAST_VALID_LICENSE_TIER
                else:
                    licensed = "community"
    
    # 3. Compute effective tier (min of licensed and requested)
    if requested:
        licensed_level = TIER_LEVELS.get(licensed, 0)
        requested_level = TIER_LEVELS.get(requested, 0)
        return licensed if licensed_level <= requested_level else requested
    
    return licensed

def set_current_tier(tier: str) -> None:
    """Set current tier (called by server initialization)."""
    global CURRENT_TIER
    CURRENT_TIER = tier
```

---

## 5. TEST INFRASTRUCTURE

### 5.1 Tier Testing Framework

**Test Configuration:** `/tests/tools/tiers/conftest.py`

**Fixtures:**

```python
@pytest.fixture
def community_tier():
    """Set up Community tier for testing."""
    activate_tier("community")
    yield {"tier": "community", "license_path": None, "is_mocked": False}
    clear_tier_caches()

@pytest.fixture
def pro_tier():
    """Set up Pro tier for testing (uses real license or env mock)."""
    license_path = activate_tier("pro", skip_if_missing=False)
    yield {"tier": "pro", "license_path": license_path, "is_mocked": license_path is None}
    clear_tier_caches()

@pytest.fixture
def enterprise_tier():
    """Set up Enterprise tier for testing."""
    license_path = activate_tier("enterprise", skip_if_missing=False)
    yield {"tier": "enterprise", "license_path": license_path, "is_mocked": license_path is None}
    clear_tier_caches()

@pytest.fixture
def tier_limits():
    """Load tier limits from limits.toml configuration."""
    # Provides mapping: tier -> tool -> limits dict
    # Supports all 22 Code Scalpel tools
    # Decouples tests from hardcoded limit values
```

**Tier Activation Helper:** `/tests/utils/tier_setup.py`

```python
def activate_tier(tier: str, skip_if_missing: bool = False) -> Optional[Path]:
    """Activate a tier via license file or environment variable."""
    
    # 1. Try to find valid license file
    license_path = _find_valid_license(tier)
    if license_path:
        os.environ["CODE_SCALPEL_LICENSE_PATH"] = str(license_path)
        return license_path
    
    # 2. Fallback: mock via environment variable
    if not skip_if_missing:
        os.environ["CODE_SCALPEL_TIER"] = tier
        os.environ["CODE_SCALPEL_DISABLE_LICENSE_DISCOVERY"] = "1"
        return None
    
    return None

def clear_tier_caches():
    """Clear tier detection and config caches between tests."""
    # Clear JWT validation cache
    jwt_validator._LICENSE_VALIDATION_CACHE = None
    # Clear config loader cache
    config_loader.clear_cache()
```

### 5.2 Test Patterns

**Tier-Gated Feature Test:**

```python
@pytest.mark.asyncio
async def test_cross_file_security_scan_community_denied(community_tier, monkeypatch):
    """Community tier cannot access cross_file_security_scan."""
    
    # 1. Ensure community tier is active
    assert community_tier["tier"] == "community"
    
    # 2. Mock the tool registry to reflect tier constraints
    monkeypatch.setattr(
        code_scalpel.tiers.tool_registry,
        "is_tool_available",
        lambda tool_name: tool_name != "cross_file_security_scan"
    )
    
    # 3. Call the tool - should fail
    with pytest.raises(UpgradeRequiredError) as exc_info:
        await cross_file_security_scan("/some/path")
    
    assert exc_info.value.required_tier == "enterprise"
    assert "upgrade" not in str(exc_info.value).lower()  # No marketing messages


@pytest.mark.asyncio
async def test_get_symbol_references_community_limits(community_tier, monkeypatch, tmp_path):
    """Community tier enforces max_files_searched and max_references limits."""
    
    # 1. Create test files
    for idx in range(10):
        (tmp_path / f"m{idx}.py").write_text("def target(): return 1\nx = target()")
    
    # 2. Mock tier detection
    monkeypatch.setattr(
        code_scalpel.licensing.tier_detector,
        "get_current_tier",
        lambda: "community"
    )
    
    # 3. Mock capability lookup to return community limits
    monkeypatch.setattr(
        code_scalpel.mcp.helpers.context_helpers,
        "get_tool_capabilities",
        lambda tool_id, tier: {
            "limits": {"max_files_searched": 2, "max_references": 3},
            "capabilities": []
        }
    )
    
    # 4. Call tool
    result = await get_symbol_references("target", str(tmp_path))
    
    # 5. Verify limits were applied
    assert result.success is True
    assert result.files_truncated is True
    assert result.files_scanned == 2          # Limited to 2
    assert len(result.references) == 3        # Limited to 3
    assert "upgrade" not in (result.truncation_warning or "").lower()
```

**Tool-Specific Tier Tests:**

Test files follow naming pattern:
```
tests/tools/tiers/test_<tool_name>_tiers.py
```

Examples:
- `test_analyze_code_tiers.py` - COMMUNITY tool
- `test_cross_file_security_scan_tiers.py` - ENTERPRISE tool
- `test_symbolic_execute_tiers.py` - PRO tool
- `test_tier_gating_smoke.py` - Core tier gating validation
- `test_tier_limits_applied.py` - Limit enforcement validation

### 5.3 License Test Files

**Location:** `/tests/licenses/` and `/.code-scalpel/archive/`

**Naming Convention:**
```
code_scalpel_license_<tier>_<timestamp>_<hash>.jwt
```

**Examples:**
- `code_scalpel_license_pro_20260101_190345.jwt`
- `code_scalpel_license_enterprise_20260101_190754.jwt`

**Test License Discovery:**
```python
def _find_valid_license(tier: str) -> Optional[Path]:
    """Find a valid license file for testing."""
    
    validator = JWTLicenseValidator()
    
    if tier == "pro":
        candidates = [
            PROJECT_ROOT / "tests/licenses/code_scalpel_license_pro_20260101_190345.jwt",
            # ... fallback paths
        ]
    
    for path in candidates:
        if path.exists():
            token = path.read_text().strip()
            result = validator.validate_token(token)
            if result.is_valid and result.tier == tier:
                return path
    
    return None
```

### 5.4 Test Organization

**Test Matrix:**
```
tests/
├── tools/
│   ├── tiers/                    # 26 tier-specific test files
│   │   ├── conftest.py          # Tier fixtures and setup
│   │   ├── test_analyze_code_tiers.py
│   │   ├── test_cross_file_security_scan_tiers.py
│   │   ├── test_tier_gating_smoke.py
│   │   └── ...
│   └── validate_paths/
│       ├── licensing/           # Tool-specific licensing tests
│       └── tiers/
│           └── test_tier_enforcement.py
├── licensing/                    # Core licensing tests
│   ├── test_jwt_validator.py
│   ├── test_jwt_integration.py
│   ├── test_runtime_behavior_server.py
│   ├── test_crl_fetch_consumer_integration.py
│   └── ...
├── licenses/                     # Test JWT tokens
│   └── code_scalpel_license_*.jwt
└── utils/
    └── tier_setup.py           # Tier activation helpers
```

**Test Patterns:**
1. **Smoke tests** (`test_tier_gating_smoke.py`) - Quick validation of tier enforcement
2. **Limit tests** (`test_tier_limits_applied.py`) - Verify capability limits
3. **Upgrade tests** - Ensure graceful degradation without marketing
4. **License fallback** (`test_generate_unit_tests_license_fallback.py`) - Test env-based tiers

---

## 6. FEATURE REGISTRY & CAPABILITY SYSTEM

### 6.1 Feature Registry

**File:** `/src/code_scalpel/tiers/feature_registry.py`

```python
@dataclass
class Feature:
    """Definition of a Code Scalpel feature."""
    name: str
    tier: str              # "community", "pro", "enterprise"
    description: str = ""
    category: str = "general"
    deprecated: bool = False
    beta: bool = False

# 24 features defined
DEFAULT_FEATURES: Dict[str, Feature] = {
    # COMMUNITY
    "analyze_code": Feature(name="analyze_code", tier="community", ...),
    # ...
    
    # PRO (NEW)
    "write_perfect_code": Feature(name="write_perfect_code", tier="pro", ...),
}

class FeatureRegistry:
    """Central registry of features and tier requirements."""
    
    def is_enabled(self, feature_name: str) -> bool:
        """Check if feature is available at current tier."""
    
    def get_available_features(self) -> List[Feature]:
        """Get all features available at current tier."""
    
    def get_tier(self, feature_name: str) -> str:
        """Get minimum required tier for feature."""
```

### 6.2 Capability System

**Tier Decorators:** `/src/code_scalpel/tiers/decorators.py`

```python
def requires_tier(
    tier: Union[str, Tier],
    feature_name: Optional[str] = None,
    graceful: bool = False,
    fallback: Any = None,
) -> Callable:
    """Decorator restricting function to specified tier or higher."""
    
    # Usage:
    @requires_tier("pro", feature_name="advanced_scan")
    async def advanced_feature():
        pass
    
    # Graceful degradation:
    @requires_tier("enterprise", graceful=True, fallback=None)
    def enterprise_only():
        pass

class TierRequirementError(Exception):
    """Raised when tier requirement not met."""
    def __init__(self, feature_name: str, required_tier: str, current_tier: str):
        self.feature_name = feature_name
        self.required_tier = required_tier
        self.current_tier = current_tier
```

---

## 7. KEY FILES AND LOCATIONS

### Core Licensing
| File | Purpose | Size |
|------|---------|------|
| `/src/code_scalpel/licensing/__init__.py` | Licensing module exports | 186 lines |
| `/src/code_scalpel/licensing/jwt_validator.py` | JWT signature verification | 80+ lines |
| `/src/code_scalpel/licensing/tier_detector.py` | Tier detection | ~200 lines |
| `/src/code_scalpel/licensing/license_manager.py` | Feature availability | 100+ lines |
| `/src/code_scalpel/licensing/features.py` | Feature capabilities by tier | ~300 lines |
| `/src/code_scalpel/licensing/config_loader.py` | TOML limits loading | ~150 lines |
| `/src/code_scalpel/licensing/authorization.py` | Tier authorization | ~50 lines |

### Tiers System
| File | Purpose | Size |
|------|---------|------|
| `/src/code_scalpel/tiers/__init__.py` | Tiers module exports, Tier enum | 108 lines |
| `/src/code_scalpel/tiers/tool_registry.py` | Tool tier mapping | 391 lines |
| `/src/code_scalpel/tiers/feature_registry.py` | Feature tier mapping | 319 lines |
| `/src/code_scalpel/tiers/decorators.py` | @requires_tier decorator | 185 lines |

### MCP Server
| File | Purpose | Size |
|------|---------|------|
| `/src/code_scalpel/mcp/server.py` | Main MCP server | 150+ lines shown |
| `/src/code_scalpel/mcp/protocol.py` | Shared MCP instance, tier logic | 100+ lines shown |
| `/src/code_scalpel/mcp/contract.py` | Response envelope, error codes | 100+ lines shown |
| `/src/code_scalpel/mcp/models/tool_definition.py` | Tool metadata | 231 lines |

### CLI
| File | Purpose | Size |
|------|---------|------|
| `/src/code_scalpel/cli.py` | Main CLI interface | 1000+ lines |
| Commands: `mcp`, `license install`, `server`, `analyze` | | |

### Configuration
| File | Purpose |
|------|---------|
| `.code-scalpel/limits.toml` | Tool limits by tier |
| `.code-scalpel/license/cs-prod-public-20260124.pem` | RS256 public key |
| `tests/licenses/*.jwt` | Test license files |

---

## 8. DESIGN PATTERNS

### 8.1 Tier-Aware Tool Pattern

```python
# In tool handler
from code_scalpel.licensing import get_current_tier, get_tool_capabilities
from code_scalpel.mcp.contract import UpgradeRequiredError, make_envelope

@mcp.tool()
async def some_tool(param: str) -> ToolResponseEnvelope:
    """Tool docstring."""
    
    # 1. Get current tier
    tier = get_current_tier()
    
    # 2. Check if feature available
    if tier != "enterprise":
        raise UpgradeRequiredError(
            tool_id="some_tool",
            feature="some_feature",
            required_tier="enterprise"
        )
    
    # 3. Get capabilities for this tier
    capabilities = get_tool_capabilities("some_tool", tier)
    limits = capabilities.get("limits", {})
    
    # 4. Apply limits
    result = compute_result(param, max_depth=limits.get("max_depth", 2))
    
    # 5. Return with envelope
    return make_envelope(tool_id="some_tool", response=result, tier=tier)
```

### 8.2 Graceful Degradation Pattern

```python
# Feature available at pro but with degradation at community
def get_symbol_references(symbol: str, path: str) -> Result:
    """Find symbol references with tier-dependent limits."""
    
    tier = get_current_tier()
    caps = get_tool_capabilities("get_symbol_references", tier)
    limits = caps.get("limits", {})
    
    # Community: 2 files, 3 references
    # Pro: 50 files, 100 references
    # Enterprise: unlimited
    max_files = limits.get("max_files_searched", 100)
    max_refs = limits.get("max_references", 100)
    
    refs = search_references(symbol, path)
    
    # Truncate if necessary
    files = list(set(r.file for r in refs))[:max_files]
    refs = refs[:max_refs]
    
    return Result(
        references=refs,
        files_truncated=(len(set(r.file for r in refs)) > max_files),
        references_truncated=(len(refs) > max_refs),
        # NO upgrade hints - users consult docs
    )
```

### 8.3 License Validation at Startup Pattern

```python
# In CLI or server initialization
from code_scalpel.licensing.authorization import compute_effective_tier_for_startup
from code_scalpel.licensing import JWTLicenseValidator

def initialize_server(explicit_tier=None, license_file=None):
    """Initialize server with tier validation."""
    
    # 1. Load license if explicit path provided
    if license_file:
        os.environ["CODE_SCALPEL_LICENSE_PATH"] = license_file
    
    # 2. Validate license
    validator = JWTLicenseValidator()
    license_data = validator.validate()
    licensed_tier = license_data.tier if license_data.is_valid else "community"
    
    # 3. Compute effective tier
    effective_tier = compute_effective_tier_for_startup(
        licensed_tier=licensed_tier,
        requested_tier=explicit_tier,
        expiration_valid=license_data.is_valid
    )
    
    # 4. Set runtime tier
    set_current_tier(effective_tier)
    
    # 5. Report to user
    print(f"✓ Running at {effective_tier.upper()} tier")
    if license_data.days_until_expiration:
        print(f"  License expires in {license_data.days_until_expiration} days")
```

---

## 9. SUMMARY TABLE

| Component | Purpose | Key Classes/Functions | Location |
|-----------|---------|----------------------|----------|
| **Licensing** | JWT validation, tier detection | `JWTLicenseValidator`, `get_current_tier()` | `licensing/` |
| **Tiers** | Feature gates, decorators | `@requires_tier`, `FeatureRegistry` | `tiers/` |
| **MCP Server** | Tool registration, deployment | `FastMCP`, `@mcp.tool()` | `mcp/server.py` |
| **Tool Registry** | Runtime tool availability | `ToolRegistry`, `is_tool_available()` | `tiers/tool_registry.py` |
| **Feature Registry** | Feature availability tracking | `FeatureRegistry`, `is_feature_enabled()` | `tiers/feature_registry.py` |
| **CLI** | Command-line interface | `start_mcp_server()`, `_license_install()` | `cli.py` |
| **Response Contract** | Universal tool response format | `ToolResponseEnvelope`, `ToolError` | `mcp/contract.py` |
| **Tool Metadata** | Tool definitions for MCP | `ToolDefinition`, `CapabilitySpec` | `mcp/models/tool_definition.py` |
| **Test Infrastructure** | Tier testing helpers | `activate_tier()`, `clear_tier_caches()` | `tests/utils/`, `tests/tools/tiers/` |
| **Limits Configuration** | Per-tool limits by tier | TOML parsing | `.code-scalpel/limits.toml` |

---

## 10. CURRENT PATTERNS & OBSERVATIONS

### Strengths
1. **Separation of Concerns:** Licensing validates, tiers gate, MCP serves
2. **Cryptographic Security:** RS256 JWT tokens prevent tampering
3. **Offline-First:** JWT validation requires no network call
4. **Extensible:** Tool/feature registries support dynamic additions
5. **Graceful Degradation:** Community users get functional tools with limits
6. **Test Coverage:** 26+ tier-specific tests + licensing tests

### Notable Design Decisions
1. **Strict Failure:** Expired licenses immediately downgrade to COMMUNITY
2. **Mid-Session Grace:** 24-hour tolerance for expiration during long-lived sessions
3. **No Upgrade Messaging in Tool Responses:** Upgrade hints in docs, not errors
4. **Limit-Based Gating:** Prefer limits over outright denial for COMMUNITY
5. **Environment Override:** `CODE_SCALPEL_TIER` allows testing/downgrade (with guard flags)

### Areas for Future Enhancement
1. **Remote License Verifier:** `CODE_SCALPEL_LICENSE_VERIFIER_URL` (beta)
2. **CRL (Certificate Revocation List):** Revocation checking via `crl_fetcher.py`
3. **Runtime Revalidation:** `runtime_revalidator.py` for long-lived processes
4. **Distributed Caching:** Redis support in cache module
5. **Custom Validators:** User-defined tier rules via authorization module

---

**END OF REPORT**
