# Code Scalpel – Pre-Release Pipeline & License-Aware Capability Testing

**Document Version:** 1.0  
**Date:** January 27, 2026  
**Status:** Approved for Implementation  
**Audience:** Development Team, DevOps, QA, Product Managers  
**Last Updated:** January 27, 2026

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [Purpose & Goals](#purpose--goals)
3. [Current State Analysis](#current-state-analysis)
4. [Proposed Architecture](#proposed-architecture)
5. [Core Principles](#core-principles)
6. [Capability Model](#capability-model)
7. [License Architecture](#license-architecture)
8. [Test Matrix & Coverage](#test-matrix--coverage)
9. [CI/CD Pipeline Specification](#cicd-pipeline-specification)
10. [Enforcement Rules & Blockers](#enforcement-rules--blockers)
11. [Design Patterns & Best Practices](#design-patterns--best-practices)
12. [Implementation Roadmap](#implementation-roadmap)
13. [Success Criteria & Metrics](#success-criteria--metrics)
14. [FAQ & Troubleshooting](#faq--troubleshooting)
15. [Appendices](#appendices)

---

## EXECUTIVE SUMMARY

### What We're Building

A comprehensive pre-release validation system that ensures Code Scalpel's license-aware capabilities are:

- ✅ **Correctly enforced** across all 22 tools
- ✅ **Consistent** across all 3 tiers (FREE, PRO, ENTERPRISE)
- ✅ **Validated** across all 3 transports (stdio, HTTP, Docker)
- ✅ **Tested** with 300+ test cases
- ✅ **Automated** in CI/CD before every release

### Why This Matters

1. **Pricing Integrity**: Prevent accidental free access to paid features
2. **Client Stability**: Guarantee tools never disappear on upgrade
3. **Tier Correctness**: Validate pricing logic is executable code
4. **License Validation**: Ensure licenses properly control access
5. **Regression Prevention**: Catch tier enforcement issues before release

### Key Decisions

| Decision | Selection | Rationale |
|----------|-----------|-----------|
| **Test Scope** | Full Coverage (300+ tests) | Comprehensive guarantee; ~10-15 min acceptable |
| **Capability Files** | Hybrid (auto-gen + approval) | Always in sync; manual approval ensures pricing clarity |
| **License Secrets** | Production-ready | Ready to use immediately from GitHub secrets |
| **Pipeline Stages** | 8 stages | Syntax → Unit → Build → Tiers → Snapshots → Release |
| **Transport Coverage** | All 3 (stdio/HTTP/Docker) | Ensures consistency across deployment methods |

### Expected Outcomes

After implementation, every release will have:
- **Zero tier enforcement regressions**
- **100% test pass rate across all tiers**
- **Auditable pricing enforcement**
- **Stable tool contracts** (no schema changes)
- **Capability snapshots** as golden files for review

---

## PURPOSE & GOALS

### Why Do We Need This?

Code Scalpel has evolved from a simple analysis tool to a **commercial product with three tiers** and **22 MCP tools**. Current state:

- ✅ License validation exists (JWT-based, offline)
- ✅ Tier system exists (FREE/PRO/ENTERPRISE)
- ✅ Tool registry exists (22 tools mapped to tiers)
- ❌ **No automated capability validation**
- ❌ **No cross-transport tier verification**
- ❌ **No capability regression detection**
- ❌ **No CI/CD enforcement of tier limits**

**Risk**: Accidental releases could expose paid features at free tier, break client contracts, or silently degrade capabilities.

### Goals (What Success Looks Like)

| Goal | How We Measure | Target |
|------|----------------|--------|
| **Tier Enforcement** | All 22 tools × 3 tiers tested | 100% pass rate |
| **Transport Consistency** | Tests on stdio/HTTP/Docker | All pass |
| **Capability Accuracy** | Golden file snapshots | 0 diffs (or approved) |
| **License Validation** | Secret injection tests | All licenses work |
| **Client Stability** | Schema comparison tests | 0 breaking changes |
| **Release Safety** | Pre-merge CI gates | All blockers pass |

### Team Impact

**For Development:**
- Clear patterns for adding tier-aware features
- Automated verification of tier limits
- Safe refactoring with comprehensive tests

**For DevOps:**
- Reproducible deployment testing
- Confidence in tier enforcement
- Automated release validation

**For Product:**
- Executable pricing logic
- Auditable feature gating
- Safe tier changes without risk

**For Support:**
- Clear tier documentation
- Reproducible tier issues
- Evidence of correct behavior

---

## CURRENT STATE ANALYSIS

### What Already Exists (Don't Rebuild)

**Licensing System** (`src/code_scalpel/licensing/`)
- ✅ JWT validation (RS256/HS256)
- ✅ Tier detection (COMMUNITY/PRO/ENTERPRISE)
- ✅ License loading from env/files
- ✅ Offline validation, 24-hour grace period
- ✅ Strict failure mode (expired = COMMUNITY)

**Tool Registry** (`src/code_scalpel/tiers/`)
- ✅ 22 tools mapped to tiers
- ✅ Tool availability checks
- ✅ Feature registry (24 features)
- ✅ `@requires_tier` decorator
- ✅ `UpgradeRequiredError` exception

**MCP Server** (`src/code_scalpel/mcp/`)
- ✅ FastMCP with decorator-based tools
- ✅ `ToolResponseEnvelope` standard response
- ✅ Tier-aware error codes
- ✅ Tool registration system (21 tools + 1 oracle)

**CLI** (`src/code_scalpel/cli.py`)
- ✅ License install command
- ✅ MCP server startup with --license-file flag
- ✅ Tier override support
- ✅ Help/version commands

**Test Infrastructure** (`tests/`)
- ✅ Tier fixtures (community/pro/enterprise)
- ✅ License activation helpers
- ✅ 26 tier-specific test files
- ✅ Cache clearing utilities

### What's Missing (What We're Adding)

| Gap | Current State | New Implementation |
|-----|---------------|-------------------|
| **Capability Introspection** | Tools have limits, no query interface | `get_capabilities()` MCP method + CLI command |
| **Capability Schema** | Limits in TOML, not in JSON | Standardized JSON capability schema |
| **Golden Files** | No regression testing | `/capabilities/free.json` etc. with CI comparison |
| **Cross-Transport Tests** | Limited to stdio | Full matrix: stdio + HTTP + Docker per tier |
| **Transport Adapter** | Tests per transport | Unified `CodeScalpelAdapter` interface |
| **CI Tier Validation** | Generic CI checks | 8-stage pipeline with tier-specific gates |
| **Capability Diffs** | No visibility on changes | Auto-generated diffs for review |
| **Enforcement Rules** | Manual verification | Automated blocker violation detection |

---

## PROPOSED ARCHITECTURE

### High-Level Design

```
┌────────────────────────────────────────────────────────────────┐
│              Code Scalpel Execution Environment                │
│  (CLI / MCP Server / Docker Container)                         │
└────────────────────────────────────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────────┐
│                  License Loading & Validation                  │
│  Source: Env / File / Default                                  │
│  Method: JWT validation (offline, RS256)                       │
│  Result: Tier (COMMUNITY / PRO / ENTERPRISE)                   │
└────────────────────────────────────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────────┐
│              Capability Resolution (New!)                      │
│  Input: Tier, Tool ID                                          │
│  Sources: limits.toml + env overrides                          │
│  Output: Capability envelope (limits/features)                 │
└────────────────────────────────────────────────────────────────┘
                             ↓
        ┌────────────────────────────────────────┐
        │   All 22 Tools (Always Registered)     │
        │   ├─ 9 COMMUNITY (always available)    │
        │   ├─ 5 PRO (available if licensed)     │
        │   ├─ 5 ENTERPRISE (enterprise only)    │
        │   └─ 1 ORACLE (emerging)               │
        └────────────────────────────────────────┘
                             ↓
        ┌────────────────────────────────────────┐
        │   Response Envelope (with Capability)  │
        │   ├─ Success/Error result              │
        │   ├─ Tier information                  │
        │   ├─ Available capabilities            │
        │   └─ Metadata (version, date, etc.)    │
        └────────────────────────────────────────┘
                             ↓
        ┌────────────────────────────────────────┐
        │      Transport Layer (Unchanged)       │
        │   ├─ stdio (JSON-RPC)                  │
        │   ├─ HTTP (REST-like)                  │
        │   └─ Docker (stdio over container)     │
        └────────────────────────────────────────┘
```

### Key Design Principles

1. **Stable Tool Surface**: All 22 tools always registered, schema never changes
2. **Dynamic Capabilities**: Limits and features vary by tier, not tool availability
3. **Introspectable**: Capabilities queryable via `get_capabilities()`
4. **Testable**: Capability limits are executable code, not just documentation
5. **Auditable**: All tier decisions traceable to license tier
6. **No Client Surprise**: Agents never encounter unexpected unavailable tools

---

## CORE PRINCIPLES

### Principle 1: Stable Tool Surface (Non-Negotiable)

**What This Means:**
- All 22 tools **always registered** in tool list (no hiding)
- Tool schemas **never change** by tier
- Tool names/parameters **immutable** per tier
- Tools show "requires upgrade" message, not "not found"

**Why It Matters:**
- LLM agents don't hallucinate unavailable tools
- Clients don't break on version upgrade
- Tool contracts are permanent

**How We Enforce It:**
```python
def test_tool_count_constant_across_tiers():
    """Assert all 22 tools present in every tier."""
    for tier in ["free", "pro", "enterprise"]:
        tools = get_mcp_tools(tier)
        assert len(tools) == 22, f"Expected 22 tools, got {len(tools)} at {tier}"

def test_tool_schema_constant_across_tiers():
    """Assert tool schema doesn't change by tier."""
    for tool_id in ALL_TOOLS:
        schema_free = get_tool_schema(tool_id, "free")
        schema_pro = get_tool_schema(tool_id, "pro")
        schema_ent = get_tool_schema(tool_id, "enterprise")
        assert schema_free == schema_pro == schema_ent
```

### Principle 2: Dynamic Capability Envelope

**What This Means:**
- Every execution has runtime capability vector
- Capabilities computed from license tier
- Capabilities queryable via MCP and CLI
- Capabilities immutable during execution

**Example Capability Envelope:**
```json
{
  "tier": "pro",
  "effective_at": "2026-01-27T00:00:00Z",
  "valid_until": "2027-01-27T00:00:00Z",
  "tools": {
    "analyze_code": {
      "available": true,
      "max_files": 5000,
      "max_depth": 15,
      "analysis_modes": ["basic", "deep"]
    },
    "unified_sink_detect": {
      "available": false,
      "requires_tier": "enterprise",
      "upgrade_url": "https://code-scalpel.ai/pricing"
    }
  }
}
```

### Principle 3: No Hardcoded Tier Logic

**Forbidden Pattern:**
```python
# ❌ BAD - Tier logic scattered in tool code
def analyze_code(files):
    if get_current_tier() == "pro":
        max_files = 5000
    else:
        max_files = 1000
    return analyze(files[:max_files])
```

**Required Pattern:**
```python
# ✅ GOOD - Centralized capability lookup
@mcp.tool()
async def analyze_code(files: list[str]) -> AnalysisResult:
    caps = get_tool_capabilities("analyze_code")  # Lookup, not hardcode
    max_files = caps["capabilities"]["max_files"]
    return analyze(files[:max_files])
```

**Why?**
- Tier limits in one place (limits.toml)
- Testable and reviewable
- Pricing changes don't touch tool code
- Overrideable in CI for testing

---

## CAPABILITY MODEL

### 3.1 What Is a "Capability"?

A capability is a **feature or limit** available to a tool at a specific tier:

```json
{
  "tool_id": "analyze_code",
  "tier": "pro",
  "capabilities": {
    "max_files": 5000,           // Numeric limit
    "max_depth": 15,             // Numeric limit
    "analysis_modes": ["basic", "deep"],  // Feature list
    "pdg_generation": true,      // Boolean feature
    "symbolic_execution": false  // Feature not available at this tier
  }
}
```

### 3.2 Capability Sources (Precedence)

```
Environment Override (CI only)
         ↓
     License Tier
         ↓
    Hardcoded Defaults (limits.toml)
```

| Source | Priority | Example | When Used |
|--------|----------|---------|-----------|
| **Environment** | 1 (Highest) | `CODE_SCALPEL_CAPABILITY_OVERRIDES=test.json` | CI testing, local debugging |
| **License Tier** | 2 | JWT claims["tier"] = "pro" | Production, normal operation |
| **Defaults** | 3 (Lowest) | limits.toml [pro] section | Fallback when license unavailable |

### 3.3 Master Capability Files

Located in `/capabilities/` directory:

```
/capabilities/
  ├── free.json           # Full envelope for COMMUNITY tier
  ├── pro.json            # Full envelope for PRO tier
  ├── enterprise.json     # Full envelope for ENTERPRISE tier
  ├── schema.json         # JSON schema for validation
  └── README.md           # How to update/maintain
```

**Example: capabilities/pro.json**
```json
{
  "tier": "pro",
  "generated_at": "2026-01-27T12:00:00Z",
  "tools": {
    "analyze_code": {
      "available": true,
      "capabilities": {
        "max_files": 5000,
        "max_depth": 15,
        "analysis_modes": ["basic", "deep", "comprehensive"]
      }
    },
    "cross_file_security_scan": {
      "available": true,
      "capabilities": {
        "max_files": 2000,
        "semantic_mode": true,
        "cross_file": true
      }
    },
    "unified_sink_detect": {
      "available": false,
      "requires_tier": "enterprise",
      "upgrade_url": "https://code-scalpel.ai/pricing"
    }
  }
}
```

### 3.4 Capability Resolver (Single Source of Truth)

```python
# File: src/code_scalpel/capabilities/resolver.py

def get_tool_capabilities(tool_id: str, tier: str = None) -> dict:
    """
    Get current capabilities for a tool at given tier.
    
    This is the ONLY place tier limits are read from. All tools
    must use this function, not hardcoded values.
    
    Returns:
    {
        "available": True/False,
        "capabilities": { "max_files": 5000, ... },
        "metadata": { "tier": "pro", "expires": "2027-01-27", ... }
    }
    """
    if tier is None:
        tier = get_current_tier()
    
    # 1. Check availability
    if not is_tool_available(tool_id, tier):
        return {
            "available": False,
            "requires_tier": get_minimum_tier_for_tool(tool_id),
            "upgrade_url": "https://code-scalpel.ai/pricing"
        }
    
    # 2. Load from limits.toml
    config = load_limits_config()
    capabilities = config[tool_id][tier]
    
    # 3. Apply environment overrides (CI testing)
    if env_overrides := load_capability_overrides():
        capabilities.update(env_overrides.get(tool_id, {}))
    
    return {
        "available": True,
        "capabilities": capabilities,
        "metadata": {
            "tier": tier,
            "effective_at": get_license_issue_date(),
            "valid_until": get_license_expiry_date()
        }
    }
```

---

## LICENSE ARCHITECTURE

### 4.1 Current License Implementation

**Already Implemented (Don't Change):**
- ✅ JWT validation (RS256 production, HS256 testing)
- ✅ Three-tier system: COMMUNITY (0) → PRO (1) → ENTERPRISE (2)
- ✅ Offline validation (no network call required)
- ✅ 24-hour grace period for mid-session expiry
- ✅ Strict failure mode: expired licenses → COMMUNITY

**Key Files:**
- `src/code_scalpel/licensing/jwt_validator.py` - JWT validation
- `src/code_scalpel/licensing/tier_detector.py` - Tier detection
- `src/code_scalpel/licensing/__init__.py` - Public exports

### 4.2 License Injection for CI Testing

**GitHub Secrets Setup:**
```yaml
# Repository Settings → Secrets and Variables → Actions

CODESCALPEL_LICENSE_PRO:
  - Valid JWT token with tier="pro"
  - Non-expired
  - Full feature set

CODESCALPEL_LICENSE_ENTERPRISE:
  - Valid JWT token with tier="enterprise"
  - Non-expired
  - Full feature set

# Rotation: Renew 30 days before expiry
```

**CI Environment Setup:**
```yaml
# .github/workflows/ci-tier-validation.yml

env:
  GITHUB_CODESCALPEL_LICENSE_PRO: ${{ secrets.CODESCALPEL_LICENSE_PRO }}
  GITHUB_CODESCALPEL_LICENSE_ENTERPRISE: ${{ secrets.CODESCALPEL_LICENSE_ENTERPRISE }}
```

**Test Fixture for License Setup:**
```python
# tests/conftest.py

@pytest.fixture(scope="session")
def setup_licenses():
    """Inject license tokens from GitHub secrets."""
    
    # FREE: Uses COMMUNITY default (no license needed)
    os.environ.pop("CODE_SCALPEL_LICENSE", None)
    
    # PRO: From GitHub secret
    pro_license = os.environ.get("GITHUB_CODESCALPEL_LICENSE_PRO")
    if not pro_license:
        pytest.skip("PRO license not available in secrets")
    
    # ENTERPRISE: From GitHub secret
    ent_license = os.environ.get("GITHUB_CODESCALPEL_LICENSE_ENTERPRISE")
    if not ent_license:
        pytest.skip("ENTERPRISE license not available in secrets")
    
    yield {
        "free": None,
        "pro": pro_license,
        "enterprise": ent_license
    }
```

### 4.3 License Validation in CI

CI must verify that:
1. ✅ Secrets are properly injected
2. ✅ Licenses are valid (not expired)
3. ✅ Licenses grant correct tier
4. ✅ Tier detection works correctly
5. ✅ License-based capabilities are applied

---

## TEST MATRIX & COVERAGE

### 5.1 Three-Dimensional Test Matrix

```
Dimension 1: Transport (3)
├── stdio (subprocess, most common)
├── HTTP (remote server)
└── Docker (isolated container)

Dimension 2: Surface (2)
├── CLI (command line interface)
└── MCP (model context protocol)

Dimension 3: Tier (3)
├── free (COMMUNITY, no license)
├── pro (PRO, valid JWT)
└── enterprise (ENTERPRISE, full features)

Total Base Combinations: 3 × 2 × 3 = 18
```

### 5.2 Full Coverage Test Plan (~300 Tests)

**Phase 1: Tier Enforcement (132 tests)**
- Tool Availability: 22 tools × 3 tiers = 66 tests
- Capability Limits: 22 tools × 3 tiers = 66 tests

**Phase 2: Transport Validation (30 tests)**
- Stdio: 10 tests (list tools, get capabilities, sample calls)
- HTTP: 10 tests (startup, TLS, request format, error handling)
- Docker: 10 tests (build, startup, tools available, license propagation)

**Phase 3: Capability Snapshots (9 tests)**
- Golden File Comparison: 3 tiers × 1 comparison = 3 tests
- Diff Generation: 3 tiers × 1 on-mismatch = 3 tests
- Approval Workflow: 1 test (regenerate after approval)

**Phase 4: License Validation (10 tests)**
- Valid Licenses: 2 tiers (pro, enterprise) = 2 tests
- Expired License: 1 test
- Invalid License: 1 test
- Secret Injection: 2 tests
- Grace Period: 1 test
- License Propagation: 3 tests (stdio, HTTP, Docker)

**Phase 5: Feature Gating (90 tests)**
- Feature Availability: 24 features × 3 tiers = 72 tests
- Feature Interactions: 10 tests
- Deprecation: 8 tests

**Phase 6: Edge Cases (30 tests)**
- License Expiry During Execution: 3 tests
- Missing License File: 3 tests
- Corrupted License: 3 tests
- Clock Skew: 3 tests
- Multiple Licenses: 3 tests
- Tier Override: 6 tests
- Large Input Clamping: 6 tests

**Total: ~300 tests**
**Expected Runtime: 12-15 minutes**

### 5.3 Test Harness Structure

```
/tests/
  ├── conftest.py                          # Global fixtures, license setup
  ├── tier_setup.py                        # Tier activation helpers
  │
  ├── transports/
  │   ├── adapter.py                       # Unified adapter interface
  │   ├── stdio_adapter.py                 # Subprocess implementation
  │   ├── http_adapter.py                  # HTTP client implementation
  │   └── docker_adapter.py                # Container implementation
  │
  ├── capabilities/
  │   ├── test_capability_schema.py        # Validate schema structure
  │   ├── test_capability_snapshot.py      # Compare against golden files
  │   ├── test_capability_generation.py    # Test auto-generation
  │   └── fixtures/ (free.json, pro.json, enterprise.json)
  │
  ├── tier_enforcement/
  │   ├── test_tool_availability.py        # 22 tools × 3 tiers
  │   ├── test_tool_limits.py              # Limit enforcement per tool
  │   ├── test_upgrade_paths.py            # UpgradeRequired errors
  │   └── test_feature_gating.py           # 24 features × 3 tiers
  │
  ├── licenses/
  │   ├── test_license_validation.py       # JWT validation
  │   ├── test_secret_injection.py         # GitHub secret tests
  │   └── fixtures/ (valid/invalid/expired tokens)
  │
  └── integration/
      ├── test_end_to_end.py               # Full workflows per tier
      └── test_regression.py               # Known issues/edge cases
```

### 5.4 Unified Transport Adapter

```python
# tests/transports/adapter.py

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ToolCall:
    tool_name: str
    arguments: dict
    expected_tier: str = "community"

@dataclass
class ToolResponse:
    success: bool
    output: Any = None
    error: str = None
    tier_used: str = None

class CodeScalpelAdapter(ABC):
    """Unified interface for all transports."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection."""
        pass
    
    @abstractmethod
    async def list_tools(self) -> list[dict]:
        """Get all 22 tools (always)."""
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> dict:
        """Get capability envelope for current tier."""
        pass
    
    @abstractmethod
    async def call_tool(self, call: ToolCall) -> ToolResponse:
        """Execute a tool."""
        pass
    
    @abstractmethod
    async def is_ready(self) -> bool:
        """Check if server ready."""
        pass

# Concrete implementations
class StdioAdapter(CodeScalpelAdapter): ...  # ~100 lines
class HTTPAdapter(CodeScalpelAdapter): ...   # ~150 lines
class DockerAdapter(CodeScalpelAdapter): ...  # ~200 lines
```

### 5.5 Example: Unified Matrix Test

```python
# tests/tier_enforcement/test_tool_availability.py

@pytest.mark.parametrize("transport", ["stdio", "http", "docker"])
@pytest.mark.parametrize("tier", ["free", "pro", "enterprise"])
@pytest.mark.parametrize("tool_id", ALL_22_TOOLS)
async def test_tool_availability(adapter_factory, transport, tier, tool_id):
    """
    Assert tool availability matches tier requirements.
    
    PASS CONDITIONS:
    - COMMUNITY tools: visible in all tiers
    - PRO tools: hidden in free, visible in pro+
    - ENTERPRISE tools: visible only in enterprise
    """
    adapter = adapter_factory(transport, tier)
    await adapter.connect()
    
    tools = await adapter.list_tools()
    tool_names = [t["name"] for t in tools]
    
    # Get requirement
    requirement = TOOL_REQUIREMENTS[tool_id]
    should_be_visible = tier_supports(tier, requirement)
    
    # Assert
    is_visible = tool_id in tool_names
    assert is_visible == should_be_visible, (
        f"Tool {tool_id} should be "
        f"{'visible' if should_be_visible else 'hidden'} "
        f"at {tier} tier on {transport}"
    )
    
    await adapter.disconnect()
```

---

## CI/CD PIPELINE SPECIFICATION

### 6.1 Eight-Stage Pipeline Overview

```
Stage 1: Syntax & Format (2 min)
         ↓
Stage 2: Unit Tests (3 min)
         ↓
Stage 3: Build Package (2 min)
         ↓
Stage 4: FREE Tier Tests (4 min)
         ↓
Stage 5: PRO Tier Tests (5 min)
         ↓
Stage 6: ENTERPRISE Tier Tests (5 min)
         ↓
Stage 7: Capability Snapshots (2 min)
         ↓
Stage 8: Release/Publish (varies)
```

### 6.2 Stage Specifications

**Stage 1: Syntax & Format Checks (2 min)**

```yaml
- Run Black format check
- Run Ruff linter
- Run Pyright type checker
- Run Security audit (pip-audit)
```

Blockers: ❌ Format failure, ❌ Type error, ❌ Security issue

**Stage 2: Unit Tests (3 min)**

```yaml
- Core library tests (no tier dependencies)
- Licensing logic tests
- Capability resolver tests
- Tool registry tests
```

Blockers: ❌ Test failure

**Stage 3: Build Package (2 min)**

```yaml
- Build wheel distribution
- Build source distribution
- Verify entry points present
- Test local installation
- Verify both commands work (codescalpel + code-scalpel)
```

Blockers: ❌ Build failure, ❌ Entry point missing

**Stage 4: FREE Tier Tests (4 min)**

Prerequisites: Installed from Stage 3 build

```yaml
Matrix: stdio × HTTP × Docker
For each transport:
  - List tools (expect 9 COMMUNITY only)
  - Get capabilities (no PRO/ENTERPRISE features)
  - Call analyze_code with 5000 files (expect clamped to 1000)
  - Attempt cross_file_scan (expect UpgradeRequired error)
```

Blockers: ❌ Tool count wrong, ❌ Limits not enforced

**Stage 5: PRO Tier Tests (5 min)**

Prerequisites: Inject PRO license from GitHub secret

```yaml
Matrix: stdio × HTTP × Docker
For each transport:
  - List tools (expect 14: 9 COMMUNITY + 5 PRO)
  - Get capabilities (PRO features available, ENTERPRISE hidden)
  - Call cross_file_scan (expect success at PRO limit)
  - Attempt unified_sink_detect (expect UpgradeRequired error)
```

Blockers: ❌ License not injected, ❌ Tool count wrong, ❌ Limits not enforced

**Stage 6: ENTERPRISE Tier Tests (5 min)**

Prerequisites: Inject ENTERPRISE license from GitHub secret

```yaml
Matrix: stdio × HTTP × Docker
For each transport:
  - List tools (expect all 22)
  - Get capabilities (all features available)
  - Call all tools at ENTERPRISE limits (expect success)
  - Verify no UpgradeRequired errors
```

Blockers: ❌ License not injected, ❌ Tool count wrong, ❌ Feature unavailable

**Stage 7: Capability Snapshots (2 min)**

Prerequisites: Test environment ready

```yaml
For each tier (free, pro, enterprise):
  - Generate current capabilities
  - Compare against golden file (capabilities/{tier}.json)
  - If different:
    - Generate diff (for PR review)
    - FAIL with helpful message
    - Suggest approval process
```

Blockers: ❌ Capability mismatch (unless approved & regenerated)

**Stage 8: Release/Publish (varies)**

Prerequisites: All stages pass, on version tag

```yaml
- Publish to PyPI (Trusted Publisher)
- Create GitHub Release
- Publish VS Code Extension
```

Blockers: ❌ Authentication failure, ❌ Integrity check failure

### 6.3 GitHub Actions Workflow Template

```yaml
# .github/workflows/ci-tier-validation.yml

name: CI - Tier-Aware Capability Testing

on:
  pull_request:
    paths:
      - 'src/**'
      - 'tests/**'
      - 'pyproject.toml'
      - '.github/workflows/ci-tier-validation.yml'
  push:
    branches: [main]
    tags: ['v[0-9]+.[0-9]+.[0-9]+']

env:
  GITHUB_CODESCALPEL_LICENSE_PRO: ${{ secrets.CODESCALPEL_LICENSE_PRO }}
  GITHUB_CODESCALPEL_LICENSE_ENTERPRISE: ${{ secrets.CODESCALPEL_LICENSE_ENTERPRISE }}

jobs:
  # Stage 1
  syntax:
    name: Stage 1 - Syntax & Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - run: pip install black ruff pyright pip-audit
      - run: black --check .
      - run: ruff check .
      - run: pyright
      - run: pip-audit

  # Stage 2
  unit-tests:
    name: Stage 2 - Unit Tests
    runs-on: ubuntu-latest
    needs: syntax
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit -v

  # Stage 3
  build:
    name: Stage 3 - Build Package
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - run: pip install build
      - run: python -m build
      - uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/

  # Stage 4
  free-tier:
    name: Stage 4 - FREE Tier Tests
    runs-on: ubuntu-latest
    needs: build
    strategy:
      matrix: { transport: [stdio, http, docker] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - uses: actions/download-artifact@v3
        with: { name: dist }
      - run: pip install -e ".[dev]" dist/*.whl
      - run: |
          pytest tests/tier_enforcement/test_tool_availability.py \
            -k "free and transport_${{ matrix.transport }}" -v

  # Stage 5 (PRO)
  pro-tier:
    name: Stage 5 - PRO Tier Tests
    runs-on: ubuntu-latest
    needs: build
    strategy:
      matrix: { transport: [stdio, http, docker] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - uses: actions/download-artifact@v3
        with: { name: dist }
      - run: pip install -e ".[dev]" dist/*.whl
      - run: |
          pytest tests/tier_enforcement/test_tool_availability.py \
            -k "pro and transport_${{ matrix.transport }}" -v

  # Stage 6 (ENTERPRISE)
  enterprise-tier:
    name: Stage 6 - ENTERPRISE Tier Tests
    runs-on: ubuntu-latest
    needs: build
    strategy:
      matrix: { transport: [stdio, http, docker] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - uses: actions/download-artifact@v3
        with: { name: dist }
      - run: pip install -e ".[dev]" dist/*.whl
      - run: |
          pytest tests/tier_enforcement/test_tool_availability.py \
            -k "enterprise and transport_${{ matrix.transport }}" -v

  # Stage 7
  snapshots:
    name: Stage 7 - Capability Snapshots
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - uses: actions/download-artifact@v3
        with: { name: dist }
      - run: pip install -e ".[dev]" dist/*.whl
      - run: pytest tests/capabilities/test_capability_snapshot.py -v
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: capability-diffs
          path: artifacts/capability-diff-*.json

  # Stage 8
  release:
    name: Stage 8 - Release/Publish
    runs-on: ubuntu-latest
    needs: [free-tier, pro-tier, enterprise-tier, snapshots]
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.10' }
      - uses: actions/download-artifact@v3
        with: { name: dist }
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

---

## ENFORCEMENT RULES & BLOCKERS

### 7.1 Blocker Violations (CI Must Fail)

These violations **automatically block PR merge**:

| Violation | Detection | Why Blocker | Example |
|-----------|-----------|------------|---------|
| **Tool count changes** | `len(tools) != 22` | Breaks client code | Expected 22, got 21 |
| **Tool schema changes** | Schema comparison | Tool interface instability | Input param type changed |
| **Capability mismatch** | Golden file diff | Unintended pricing change | max_files changed without approval |
| **Tier limit ignored** | Tool accepts wrong input | Paid feature exposed free | FREE tier can call PRO limit |
| **License not injected** | Secret validation fails | Tier detection broken | License secret empty |
| **MCP tool lies** | Capability vs actual | Contract violation | Says available but errors |
| **Response format broken** | Contract validation | Breaks agents/clients | Missing required field |
| **Missing test** | Coverage check | Regression risk | New tier limit, no test |

### 7.2 Warning Violations (CI Warns, Doesn't Block)

These violations **warn but don't block merge**:

| Warning | Detection | Recommendation |
|---------|-----------|-----------------|
| **Feature improved** | Generated > golden | Verify docs updated |
| **Deprecated feature used** | Deprecation scanner | Schedule removal |
| **License expiring soon** | Date check | Renew within 30 days |
| **Test slow** | Execution time > 10s | Consider optimization |

### 7.3 Enforcement Implementation

```python
# tests/enforcement/test_blockers.py

class TestBlockerEnforcement:
    """Enforce non-negotiable rules before release."""
    
    def test_tool_count_must_be_22(self):
        """BLOCKER: Must have exactly 22 tools."""
        tools = get_mcp_tools()
        assert len(tools) == 22, (
            f"Expected 22 tools, got {len(tools)}. "
            "This is a BLOCKER - all 22 tools must always be registered."
        )
    
    def test_tool_schema_immutable(self):
        """BLOCKER: Tool schema cannot change."""
        for tool_id in get_available_tools():
            current = get_tool_schema(tool_id)
            golden = load_golden_schema(tool_id)
            assert current == golden, (
                f"Tool '{tool_id}' schema changed. "
                "This is a BLOCKER - schemas are client contracts."
            )
    
    def test_capability_snapshot_match(self):
        """BLOCKER: Capabilities must match golden unless approved."""
        for tier in ["free", "pro", "enterprise"]:
            generated = generate_capabilities(tier)
            golden = load_golden_capabilities(tier)
            
            if generated != golden:
                diff = json_diff.diff(golden, generated)
                # Check for explicit approval
                if not is_approved("regenerate-capabilities"):
                    pytest.fail(
                        f"Capability mismatch for {tier}. "
                        f"This is a BLOCKER - must be intentional. "
                        f"Approve PR with 'regenerate-capabilities' label to proceed.\n"
                        f"Diff:\n{json.dumps(diff, indent=2)}"
                    )
    
    def test_tier_limits_enforced(self):
        """BLOCKER: Tier limits must actually be enforced."""
        for tier in ["free", "pro", "enterprise"]:
            with tier_context(tier):
                caps = get_capabilities()
                max_files = caps["tools"]["analyze_code"]["capabilities"]["max_files"]
                
                # Actually call the tool with max input
                result = analyze_code(["file"] * max_files * 2)
                
                # Verify clamping
                assert len(result.analyzed) == max_files, (
                    f"Tier {tier} has max_files={max_files} "
                    f"but tool accepted {len(result.analyzed)} files. "
                    f"This is a BLOCKER - limits must be enforced."
                )
    
    def test_license_secrets_injected(self):
        """BLOCKER: License secrets must be available."""
        pro_license = os.environ.get("GITHUB_CODESCALPEL_LICENSE_PRO")
        ent_license = os.environ.get("GITHUB_CODESCALPEL_LICENSE_ENTERPRISE")
        
        assert pro_license, (
            "PRO license secret not found. "
            "This is a BLOCKER - check GitHub secrets setup."
        )
        assert ent_license, (
            "ENTERPRISE license secret not found. "
            "This is a BLOCKER - check GitHub secrets setup."
        )
```

---

## DESIGN PATTERNS & BEST PRACTICES

### 8.1 Forbidden Patterns (❌ Don't Do This)

```python
# ❌ Pattern 1: Tier logic scattered in tool code
@mcp.tool()
def analyze_code(files):
    if get_current_tier() == "pro":
        max_files = 5000
    elif get_current_tier() == "enterprise":
        max_files = 50000
    else:
        max_files = 1000
    return analyze(files[:max_files])

# ❌ Pattern 2: Hiding tools per tier
@mcp.tool()
def cross_file_scan():
    if get_current_tier() == "free":
        raise ToolNotAvailable("Upgrade to PRO")
    return scan_cross_file()

# ❌ Pattern 3: Client-side tier filtering
async def get_available_tools(tier):
    all_tools = [...]
    if tier == "pro":
        return [t for t in all_tools if t.available_at_tier <= "pro"]

# ❌ Pattern 4: Magic numbers
if file_count > 5000:  # Where does 5000 come from?
    files = files[:5000]
```

### 8.2 Required Patterns (✅ Do This)

```python
# ✅ Pattern 1: Tools read capabilities dynamically
from code_scalpel.capabilities import get_tool_capabilities

@mcp.tool()
async def analyze_code(files: list[str]) -> AnalysisResult:
    """Analyze code up to tier limit."""
    caps = get_tool_capabilities("analyze_code")  # LOOKUP, not hardcode
    max_files = caps["capabilities"]["max_files"]
    max_depth = caps["capabilities"]["max_depth"]
    
    files = files[:max_files]  # Apply limit
    return analyze(files, depth_limit=max_depth)

# ✅ Pattern 2: Capabilities queryable
@mcp.tool()
async def get_capabilities() -> CapabilityEnvelope:
    """Return what this execution can do."""
    return make_capability_envelope(get_current_tier())

# ✅ Pattern 3: Limits in configuration, not code
# File: src/code_scalpel/capabilities/limits.toml

[analyze_code.free]
max_files = 1000
max_depth = 5

[analyze_code.pro]
max_files = 5000
max_depth = 15

[analyze_code.enterprise]
max_files = 50000
max_depth = 30

# ✅ Pattern 4: Tests assert business rules
def test_analyze_code_free_limit():
    """FREE tier should limit to 1000 files."""
    with tier_context("free"):
        result = analyze_code(["file"] * 5000)
        assert len(result.analyzed) == 1000

def test_analyze_code_pro_limit():
    """PRO tier should limit to 5000 files."""
    with tier_context("pro"):
        result = analyze_code(["file"] * 10000)
        assert len(result.analyzed) == 5000
```

### 8.3 Tier-Aware Tool Development Checklist

When adding a new tier-gated feature:

- [ ] Add capability entry to `/src/code_scalpel/capabilities/limits.toml`
- [ ] Add tool to tier registry if new
- [ ] Update tool to use `get_tool_capabilities()` instead of hardcoding limits
- [ ] Add test for each tier (free/pro/enterprise)
- [ ] Verify tool appears in all tier's tool lists
- [ ] Verify capability envelope includes new limits
- [ ] Verify `get_capabilities()` MCP method returns correct limits
- [ ] Run full test matrix to verify no regressions

---

## IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Week 1) - Jan 27-31

**Objective:** Build capability model and resolver

- [ ] Create `/capabilities/` directory structure
- [ ] Implement `get_tool_capabilities()` resolver function
- [ ] Create capability schema (JSON Schema)
- [ ] Add `get_capabilities()` MCP method
- [ ] Generate initial golden capability files
- [ ] Add GitHub secrets for PRO and ENTERPRISE licenses
- [ ] Write capability resolver tests

**Deliverables:**
- Capability resolver working
- Golden files for all tiers
- Licenses injected into CI

### Phase 2: Test Infrastructure (Week 2) - Feb 3-7

**Objective:** Build unified test harness and tier tests

- [ ] Implement `CodeScalpelAdapter` base class
- [ ] Implement `StdioAdapter` (subprocess)
- [ ] Implement `HTTPAdapter` (HTTP client)
- [ ] Implement `DockerAdapter` (container runner)
- [ ] Write tool availability tests (22 tools × 3 tiers)
- [ ] Write capability limit tests
- [ ] Write feature gating tests (24 features × 3 tiers)

**Deliverables:**
- Unified transport adapter pattern
- 150+ tests for tier enforcement
- All tests passing locally

### Phase 3: CI Integration (Week 3) - Feb 10-14

**Objective:** Build 8-stage GitHub Actions pipeline

- [ ] Create `.github/workflows/ci-tier-validation.yml`
- [ ] Implement Stage 1 (syntax checks)
- [ ] Implement Stage 2 (unit tests)
- [ ] Implement Stage 3 (build)
- [ ] Implement Stages 4-6 (tier tests with matrix)
- [ ] Implement Stage 7 (snapshot comparison)
- [ ] Implement Stage 8 (release)
- [ ] Add blocker violation detection
- [ ] Test on real PR

**Deliverables:**
- 8-stage CI pipeline running
- All blockers working
- Warnings functional

### Phase 4: Documentation & Training (Week 4) - Feb 17-21

**Objective:** Document patterns and train team

- [ ] Write tier-aware tool development guide
- [ ] Create examples for each tier
- [ ] Document how to update capability files
- [ ] Document approval workflow for capability changes
- [ ] Train team on forbidden/required patterns
- [ ] Create troubleshooting guide

**Deliverables:**
- Complete documentation
- Team trained
- Ready for production use

---

## SUCCESS CRITERIA & METRICS

### 6.1 Success Criteria (Definition of Done)

✅ **Implementation Complete When:**

1. **Capability Model**
   - [ ] `get_tool_capabilities()` function works
   - [ ] Capability schema documented
   - [ ] Golden files exist for all tiers
   - [ ] All tools read capabilities dynamically

2. **Test Coverage**
   - [ ] 300+ tests passing
   - [ ] All 22 tools × 3 tiers tested
   - [ ] All 3 transports tested
   - [ ] All blockers functional

3. **CI/CD**
   - [ ] 8-stage pipeline running
   - [ ] Blockers prevent merge on violation
   - [ ] Warnings don't block
   - [ ] Release stage automated

4. **Documentation**
   - [ ] Architecture documented
   - [ ] Design patterns documented
   - [ ] Development guide complete
   - [ ] Team trained

### 6.2 Key Metrics to Track

After implementation, measure monthly:

| Metric | Target | Purpose |
|--------|--------|---------|
| **Tool schema stability** | 0 breaking changes | Ensures client stability |
| **Tier limit correctness** | 100% tests pass | Validates pricing enforcement |
| **Capability accuracy** | 100% snapshot match | Ensures marketing alignment |
| **License validation** | 100% secret success | Validates tier detection |
| **CI execution time** | <15 min per PR | Maintains velocity |
| **Test coverage** | ≥95% tools per tier | Ensures completeness |
| **False positive rate** | <2% | Reduces alert fatigue |
| **Release confidence** | 100% of releases pass validation | No post-release issues |

---

## FAQ & TROUBLESHOOTING

### Q1: Why do we need a new capability model when we already have limits.toml?

**A:** limits.toml is internal and not queryable by agents. The capability model:
- Makes limits **discoverable** via `get_capabilities()` MCP method
- Enables **dynamic testing** of limits in CI
- Creates **golden files** for regression testing
- Provides **audit trail** of pricing changes
- Makes pricing **testable code**, not documentation

### Q2: What if we accidentally change a tier limit?

**A:** The capability snapshot test will fail:
1. Test generates current capabilities
2. Compares against golden file
3. Fails if different (unless approved)
4. Shows diff for review
5. Requires explicit approval to merge
6. Regenerates golden file after approval

This gives product/engineering time to review pricing changes.

### Q3: How do we handle license renewal in CI?

**A:** Update GitHub secrets before expiry:
1. Generate new license tokens
2. Update `CODESCALPEL_LICENSE_PRO` secret
3. Update `CODESCALPEL_LICENSE_ENTERPRISE` secret
4. Next CI run uses new licenses
5. Old licenses still work for 24 hours (grace period)

Set calendar reminder 30 days before expiry.

### Q4: What if a tool has tier-specific features (not just limits)?

**A:** Capabilities handle both:

```json
{
  "analyze_code": {
    "available": true,
    "capabilities": {
      "max_files": 5000,           // Numeric limit
      "analysis_modes": ["basic", "deep"],  // Feature list
      "pdg_generation": true,      // Boolean feature
      "symbolic_execution": false  // Feature disabled at this tier
    }
  }
}
```

Tools check capabilities for both limits and feature availability.

### Q5: How do we add a new tier-gated tool?

**A:** 

1. Add to tool registry with tier requirement
2. Add capability entry to limits.toml
3. Implement tool with `get_tool_capabilities()` lookup
4. Add to all test matrices
5. Add tests for each tier
6. Golden files auto-generate from new limits
7. PR requires approval to merge (snapshot diff)

### Q6: Can clients/agents break the tier system?

**A:**

No, because:
- All 22 tools always registered (tool list immutable)
- Tier enforcement in server code (not client code)
- Limits applied before response sent
- Invalid tiers fall back to COMMUNITY
- Tests validate behavior before release

### Q7: What if CI tests pass but production fails?

**A:** This should not happen because:
- CI uses same code as production
- CI uses same licenses (real, not mocked)
- CI tests all 3 transports
- CI validates license injection
- Snapshot tests catch silent regressions

If production failure occurs:
1. Check license validity (not expired)
2. Check license injected correctly
3. Run CI test for that tier locally
4. If test passes locally, issue is environmental

---

## APPENDICES

### Appendix A: Tool Distribution by Tier

```
COMMUNITY (9 tools - always available)
├── 1. analyze_code
├── 2. get_file_context
├── 3. crawl_project
├── 4. get_project_map
├── 5. scan_dependencies
├── 6. get_graph_neighborhood
├── 7. get_call_graph
├── 8. get_cross_file_dependencies
└── 9. get_symbol_references

PRO (5 tools - requires license)
├── 1. cross_file_security_scan
├── 2. type_evaporation_scan
├── 3. extract_code
├── 4. update_symbol
└── 5. rename_symbol

ENTERPRISE (5 tools - enterprise only)
├── 1. unified_sink_detect
├── 2. code_policy_check
├── 3. simulate_refactor
├── 4. symbolic_execute
└── 5. generate_unit_tests

ORACLE (1 tool - emerging)
└── 1. oracle_tool

TOTAL: 22 tools
```

### Appendix B: Example Capability Files

**capabilities/free.json (excerpt)**
```json
{
  "tier": "free",
  "generated_at": "2026-01-27T12:00:00Z",
  "tools": {
    "analyze_code": {
      "available": true,
      "capabilities": {
        "max_files": 1000,
        "max_depth": 5,
        "analysis_modes": ["basic"]
      }
    },
    "cross_file_security_scan": {
      "available": false,
      "requires_tier": "pro",
      "upgrade_url": "https://code-scalpel.ai/pricing"
    }
  }
}
```

**capabilities/pro.json (excerpt)**
```json
{
  "tier": "pro",
  "generated_at": "2026-01-27T12:00:00Z",
  "tools": {
    "analyze_code": {
      "available": true,
      "capabilities": {
        "max_files": 5000,
        "max_depth": 15,
        "analysis_modes": ["basic", "deep", "comprehensive"]
      }
    },
    "cross_file_security_scan": {
      "available": true,
      "capabilities": {
        "max_files": 2000,
        "semantic_mode": true,
        "cross_file": true
      }
    }
  }
}
```

### Appendix C: Glossary

| Term | Definition |
|------|-----------|
| **Tier** | Subscription level (COMMUNITY, PRO, ENTERPRISE) |
| **Capability** | A feature or limit available at a tier |
| **Capability Envelope** | JSON response with tier and all capabilities |
| **Limit** | Numeric constraint (e.g., max_files) per tool per tier |
| **Golden File** | Committed reference capability file for regression testing |
| **Blocker** | Test failure that prevents PR merge |
| **Transport** | Communication method (stdio, HTTP, Docker) |
| **Adapter** | Transport-specific test implementation |
| **Feature Gate** | Code path enabled/disabled by capability |
| **Contract** | MCP tool interface (immutable) |

### Appendix D: Reference Links

- **License Validation:** `src/code_scalpel/licensing/jwt_validator.py`
- **Tool Registry:** `src/code_scalpel/tiers/tool_registry.py`
- **Feature Registry:** `src/code_scalpel/tiers/feature_registry.py`
- **MCP Server:** `src/code_scalpel/mcp/protocol.py`
- **CLI:** `src/code_scalpel/cli.py`
- **Limits Config:** `.code-scalpel/limits.toml`
- **Exploration Report:** `CODEBASE_EXPLORATION_REPORT.md`

---

## SIGN-OFF & APPROVAL

| Role | Name | Approved | Date | Notes |
|------|------|----------|------|-------|
| Architecture Lead | | ☐ | | |
| Engineering Lead | | ☐ | | |
| Product Manager | | ☐ | | |
| DevOps Lead | | ☐ | | |
| QA Lead | | ☐ | | |

---

## DOCUMENT HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-27 | OpenCode Agent | Initial comprehensive specification |

---

**END OF DOCUMENT**

**Next Steps:**
1. Team review and approval (1-2 days)
2. Phase 1 implementation (1 week)
3. Phase 2 implementation (1 week)
4. Phase 3 implementation (1 week)
5. Phase 4 documentation (1 week)
6. Production deployment (TBD)

**Contact for Questions:** Development Team Lead
