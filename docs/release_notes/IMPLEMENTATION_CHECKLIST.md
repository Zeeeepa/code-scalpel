# Feature Extraction & Package Separation - Implementation Checklist

**Status**: 🟢 READY FOR IMPLEMENTATION
**Created**: January 8, 2026
**Purpose**: Step-by-step checklist for executing the feature extraction plan

---

## Pre-Implementation Tasks (Verification)

### ✅ Documentation Complete
- [x] FEATURE_EXTRACTION_PLAN.md (1,399 lines) - Complete extraction strategy
- [x] LICENSING_SYSTEM_GUIDE.md (500+ lines) - How licensing works
- [x] PUBLIC_REPO_PREPARATION.md - Updated with correct architecture
- [x] All 22 tool roadmaps analyzed for tier features

### ✅ Licensing System Understood
- [x] JWT validation (RS256 signatures)
- [x] Tier detection (5-point priority)
- [x] License file locations (5 paths)
- [x] Two-stage validation (offline + online + grace period)
- [x] Feature gating (FeatureRegistry + tier hierarchy)
- [x] Plugin interfaces (FeaturePlugin base class)

### ✅ Test Licenses Available
- [x] Pro license: `tests/licenses/code_scalpel_license_pro_20260101_190345.jwt`
- [x] Enterprise license: `tests/licenses/code_scalpel_license_enterprise_20260101_190754.jwt`
- [x] Broken licenses for validation testing

### ✅ Current Architecture Analyzed
- [x] All 22 tools reviewed for tier features
- [x] Shared utilities identified
- [x] Dependencies mapped (PyJWT, cryptography, Z3, etc.)
- [x] Interface contracts defined

---

## Phase 1: Plugin System Implementation

**Timeline**: Week 1 (Jan 13-17)
**Owner**: Backend Lead
**Dependency**: None (foundational)

### 1.1 Create Plugin Interfaces

**File**: `src/code_scalpel/plugins/__init__.py`

- [ ] Create abstract `FeaturePlugin` base class
  - [ ] `register_features() -> List[Feature]` method
  - [ ] `register_tools() -> List[MCPTool]` method
  - [ ] `validate_license(license: JWTLicenseData) -> bool` method
  
- [ ] Create `PluginMetadata` dataclass
  - [ ] name: str
  - [ ] version: str
  - [ ] requires_tier: str
  - [ ] description: str
  - [ ] entry_point: str

**Test Coverage**:
- [ ] Test abstract class instantiation fails
- [ ] Test concrete implementation works
- [ ] Test license validation called during loading

### 1.2 Create Plugin Registry

**File**: `src/code_scalpel/plugins/registry.py`

- [ ] Create `PluginRegistry` class
  - [ ] `register_plugin(plugin: FeaturePlugin) -> None`
  - [ ] `get_registered_plugins() -> List[FeaturePlugin]`
  - [ ] `validate_all_plugins(tier: str) -> bool`
  - [ ] `get_tools_for_tier(tier: str) -> List[MCPTool]`
  
- [ ] Implement plugin discovery
  - [ ] `discover_plugins() -> List[FeaturePlugin]` - pkg_resources entry points
  - [ ] `discover_from_paths(paths: List[str]) -> List[FeaturePlugin]` - filesystem search
  - [ ] Error handling for missing plugins (graceful degradation)

**Test Coverage**:
- [ ] Test plugin registration
- [ ] Test plugin discovery
- [ ] Test plugin validation
- [ ] Test graceful degradation with missing plugins

### 1.3 Create Plugin Loader

**File**: `src/code_scalpel/plugins/loader.py`

- [ ] Create `PluginLoader` class
  - [ ] `load_plugins(tier: str, license: JWTLicenseData) -> List[FeaturePlugin]`
  - [ ] `load_from_entry_points() -> List[FeaturePlugin]`
  - [ ] Error handling and logging
  - [ ] Skip plugins if tier doesn't support them

- [ ] Implement safety checks
  - [ ] Verify plugin doesn't depend on missing Community modules
  - [ ] Check for circular dependencies between plugins
  - [ ] Validate plugin metadata matches setup.py entry_points

**Test Coverage**:
- [ ] Test load with no plugins installed
- [ ] Test load with Pro plugin only
- [ ] Test load with Pro + Enterprise plugins
- [ ] Test tier-based plugin filtering
- [ ] Test error handling for incompatible plugins

### 1.4 Update MCP Server Initialization

**File**: `src/code_scalpel/mcp/server.py`

- [ ] Modify `initialize_server()` async function
  ```python
  async def initialize_server():
      # Get license and tier
      tier = get_current_tier()
      license_data = validate_license()
      
      # Load base tools
      tools = list(COMMUNITY_TOOLS)
      registry = FeatureRegistry()
      
      # Load plugins
      if tier in ("pro", "enterprise"):
          loader = PluginLoader()
          plugins = loader.load_plugins(tier, license_data)
          for plugin in plugins:
              tools.extend(plugin.register_tools())
              registry.register_features(plugin.register_features())
      
      return MCPServer(tools, registry)
  ```

- [ ] Update tool registration
  - [ ] Tools have `requires_tier` metadata
  - [ ] Tools dispatch based on tier
  - [ ] Graceful fallback if plugin missing

**Test Coverage**:
- [ ] Test server starts with Community tier only
- [ ] Test server loads Pro plugin if available + tier=pro
- [ ] Test server loads Enterprise plugins if available + tier=enterprise
- [ ] Test server works without plugins installed
- [ ] Test license validation happens before plugin load

### 1.5 Integration Tests

**Directory**: `tests/integration/`

- [ ] `test_plugin_loading.py`
  - [ ] Test loading no plugins
  - [ ] Test loading Pro plugin only
  - [ ] Test loading Pro + Enterprise plugins
  - [ ] Test error handling

- [ ] `test_license_validation.py`
  - [ ] Test with valid Pro license
  - [ ] Test with valid Enterprise license
  - [ ] Test with expired license (grace period)
  - [ ] Test with no license (Community)

- [ ] `test_feature_gating.py`
  - [ ] Test feature available at each tier
  - [ ] Test feature unavailable below tier
  - [ ] Test registry reflects loaded plugins

- [ ] `test_graceful_degradation.py`
  - [ ] Test server works if Pro plugin missing
  - [ ] Test upgrade prompts shown for unavailable features
  - [ ] Test Community features always available

### 1.6 Documentation

- [ ] Write plugin development guide (`docs/PLUGIN_DEVELOPMENT.md`)
  - [ ] How to create a plugin
  - [ ] How to register features
  - [ ] How to implement tool overrides
  - [ ] Entry point configuration example
  
- [ ] Update main README
  - [ ] Link to plugin development guide
  - [ ] Explain tier system + plugins
  
- [ ] Update architecture docs
  - [ ] Plugin system architecture
  - [ ] Plugin loading sequence
  - [ ] Feature gating mechanism

**Acceptance Criteria**: 
- [ ] All tests passing (100+ new tests)
- [ ] Plugin system fully documented
- [ ] Server initializes with/without plugins
- [ ] Feature registry reflects tier + plugins

---

## Phase 2: Extract Community Code

**Timeline**: Week 2 (Jan 20-24)
**Owner**: Code Architecture Team
**Dependency**: Phase 1 complete

### 2.1 Mark Code with Tier Comments

**All tool files** in `src/code_scalpel/mcp/tools/`:

- [ ] `analyze_code.py`
  - [ ] Mark all COMMUNITY tier code with `# [COMMUNITY TIER]`
  - [ ] Mark all PRO tier code with `# [PRO TIER]`
  - [ ] Mark all ENTERPRISE tier code with `# [ENTERPRISE TIER]`

- [ ] Repeat for all 22 tools
  - [ ] `code_policy_check.py`
  - [ ] `crawl_project.py`
  - [ ] ... (all 22)

**For each tool**:
- [ ] Functions/classes have clear tier labels
- [ ] All conditional logic tagged (if tier == "pro": ...)
- [ ] Dependencies marked (this func used only in Pro)

**Verification**:
- [ ] All 22 tools have tier comments
- [ ] No functions without tier marking
- [ ] Comments are consistent across all files

### 2.2 Remove Pro/Enterprise Code from Community

**For each of 22 tools**:

- [ ] Keep COMMUNITY tier implementation
- [ ] Delete PRO tier code
- [ ] Delete ENTERPRISE tier code
- [ ] Replace with upgrade prompts

**Example refactoring**:
```python
# BEFORE (v3.3.0)
def analyze(code: str, tier: str = "community") -> AnalysisResult:
    result = AnalysisResult()
    
    # Community: Basic analysis
    result.complexity = calculate_complexity(code)
    
    # Pro: Code smells
    if tier in ("pro", "enterprise"):
        result.smells = detect_smells(code)
    
    # Enterprise: Custom rules
    if tier == "enterprise":
        result.custom = apply_custom_rules(code)
    
    return result

# AFTER (Community only)
def analyze(code: str) -> AnalysisResult:
    result = AnalysisResult()
    
    # Community: Basic analysis only
    result.complexity = calculate_complexity(code)
    
    # Placeholder for Pro features
    result.smells = None  # Available in Pro tier
    result.custom = None  # Available in Enterprise tier
    
    return result
```

- [ ] Keep basic functionality
- [ ] Remove advanced options/parameters
- [ ] Keep interface stable (add optional params with defaults)
- [ ] Update docstrings

**Verification**:
- [ ] All 22 tools have Community-only code
- [ ] No Pro/Enterprise code remains
- [ ] No conditional tier checks remain
- [ ] All tests for Community features still pass

### 2.3 Refactor for Plugin Compatibility

**Update tool implementations**:

- [ ] Replace `tier` parameter with registry checks
  ```python
  # BEFORE
  def analyze(code, tier="community"):
      if tier == "pro":
          return advanced_analysis()
  
  # AFTER
  def analyze(code):
      registry = FeatureRegistry()
      if registry.is_enabled("advanced_analysis"):
          # Advanced analysis available
          # This will be true if Pro plugin loaded
          return advanced_analysis()
      else:
          return basic_analysis()
  ```

- [ ] Create plugin hooks (for Pro/Enterprise to override)
  ```python
  # Make functions overrideable by plugins
  def _analyze_impl(code):
      """Core implementation (can be overridden by Pro plugin)."""
      return basic_analysis(code)
  ```

- [ ] Use feature registry for conditional logic
  ```python
  from code_scalpel.tiers import FeatureRegistry
  
  registry = FeatureRegistry()
  
  # Check if feature available
  if registry.is_enabled("advanced_analysis"):
      result.update(advanced_analysis())
  ```

**Verification**:
- [ ] All 22 tools use feature registry
- [ ] No hardcoded tier checks remain
- [ ] Plugin can override behavior
- [ ] Community features work without plugins

### 2.4 Run Full Test Suite

- [ ] Unit tests for all 22 tools
  - [ ] Community tier: 4,700+ tests pass
  - [ ] No failures
  - [ ] Coverage maintained ≥90%

- [ ] Integration tests
  - [ ] Plugin loading tests pass
  - [ ] License validation tests pass
  - [ ] Graceful degradation tests pass

- [ ] Manual testing
  - [ ] Run without plugins: Works
  - [ ] Run with Pro plugin: Works
  - [ ] Run with Pro + Enterprise: Works
  - [ ] Community features available at all tiers
  - [ ] Pro features gated to Pro+
  - [ ] Enterprise features gated to Enterprise

**Acceptance Criteria**:
- [ ] All tests passing (5,000+ tests)
- [ ] Coverage ≥ 90%
- [ ] Community package functional
- [ ] No Pro/Enterprise code visible
- [ ] Ready for Pro plugin extraction

---

## Phase 3: Create Pro Plugin Package

**Timeline**: Week 3 (Jan 27-31)
**Owner**: Pro Features Team
**Dependency**: Phase 2 complete

### 3.1 Initialize Pro Package Repository

- [ ] Create `code-scalpel-pro` private repository
- [ ] Copy structure from code-scalpel
  ```
  code-scalpel-pro/
  ├── setup.py
  ├── src/code_scalpel_pro/
  │   ├── __init__.py
  │   └── mcp/tools/
  │       ├── analyze_code_pro.py
  │       ├── security_scan_pro.py
  │       └── ... (Pro overrides for each tool)
  └── tests/
      └── test_pro_features.py
  ```

- [ ] Create setup.py
  ```python
  setuptools.setup(
      name="code-scalpel-pro",
      version="3.4.0",
      install_requires=["code-scalpel>=3.4.0"],
      entry_points={
          "code_scalpel.plugins": [
              "pro = code_scalpel_pro:ProFeaturePlugin"
          ]
      }
  )
  ```

- [ ] Create LICENSE (Commercial)

### 3.2 Extract Pro Implementations

**For each of 22 tools** (prioritize high-value first):

1. **analyze_code_pro.py**
   - [ ] Copy code smell detection logic
   - [ ] Add advanced metrics
   - [ ] Depend on Community `analyze_code` for base

2. **security_scan_pro.py**
   - [ ] Copy NoSQL/LDAP/CSRF/SSRF sinks
   - [ ] Add confidence scoring
   - [ ] Extend Community security_scan

3. **Repeat for all 22 tools**
   - [ ] Extract Pro-marked code from each
   - [ ] Create override implementations
   - [ ] Test Pro features independently

**For each Pro tool implementation**:
- [ ] Function signature matches Community (or extends with optional params)
- [ ] Calls Community version as base
- [ ] Adds Pro-specific features
- [ ] Well documented

### 3.3 Implement Pro Plugin Interface

**File**: `src/code_scalpel_pro/__init__.py`

```python
from code_scalpel.plugins import FeaturePlugin
from code_scalpel.licensing import JWTLicenseData

class ProFeaturePlugin(FeaturePlugin):
    """Code Scalpel Pro tier features plugin."""
    
    def register_features(self) -> List[Feature]:
        """Return all Pro features."""
        return [
            Feature("advanced_analysis", "pro", ...),
            Feature("advanced_security", "pro", ...),
            # ... all Pro features
        ]
    
    def register_tools(self) -> List[MCPTool]:
        """Return Pro tool implementations."""
        return [
            # Tool overrides with Pro features
        ]
    
    def validate_license(self, license: JWTLicenseData) -> bool:
        """Check if license supports Pro."""
        return license.tier in ("pro", "enterprise")
```

### 3.4 Create Pro Tests

**Directory**: `tests/`

- [ ] `test_pro_features.py`
  - [ ] Test each Pro feature is available
  - [ ] Test Pro features enhance Community base
  - [ ] Test Pro-specific parameters work
  - [ ] Test 500+ Pro tests passing

- [ ] `test_pro_license_validation.py`
  - [ ] Test Pro plugin loads with Pro license
  - [ ] Test Pro plugin loads with Enterprise license
  - [ ] Test Pro plugin doesn't load without license
  - [ ] Test graceful fallback to Community

- [ ] Integration with Community
  - [ ] Test Pro plugin depends on Community correctly
  - [ ] Test no duplicate implementations
  - [ ] Test feature registry updated after plugin load

### 3.5 Documentation

- [ ] Create README.md (Pro features overview)
- [ ] Create INSTALLATION.md (how to install with Pro license)
- [ ] Create API_REFERENCE.md (Pro tool enhancements)
- [ ] Update CHANGELOG.md (Pro tier features)

**Acceptance Criteria**:
- [ ] Pro plugin tests passing (500+)
- [ ] All Pro features implemented
- [ ] Plugin loads correctly with Pro license
- [ ] Plugin gracefully skips with Community tier
- [ ] Pro package can install alongside Community

---

## Phase 4: Create Enterprise Plugin Package

**Timeline**: Week 4 (Feb 3-7)
**Owner**: Enterprise Features Team
**Dependency**: Phase 3 complete (Pro plugin must work first)

### 4.1 Initialize Enterprise Package Repository

- [ ] Create `code-scalpel-enterprise` private repository
- [ ] Copy structure
  ```
  code-scalpel-enterprise/
  ├── setup.py
  ├── src/code_scalpel_enterprise/
  │   ├── __init__.py
  │   └── mcp/tools/
  │       ├── analyze_code_enterprise.py
  │       └── ... (Enterprise overrides)
  └── tests/
  ```

- [ ] Create setup.py
  ```python
  setuptools.setup(
      name="code-scalpel-enterprise",
      version="3.4.0",
      install_requires=["code-scalpel-pro>=3.4.0"],  # Depends on Pro!
      entry_points={
          "code_scalpel.plugins": [
              "enterprise = code_scalpel_enterprise:EnterpriseFeaturePlugin"
          ]
      }
  )
  ```

### 4.2 Extract Enterprise Implementations

**For each of 22 tools**:

1. Copy Enterprise-marked code
2. Create overrides that extend Pro version (not Community)
3. Add Enterprise-specific features

**Key difference from Pro**: Enterprise implementations should extend Pro (if available), not Community directly.

### 4.3 Implement Enterprise Plugin Interface

**File**: `src/code_scalpel_enterprise/__init__.py`

```python
class EnterpriseFeaturePlugin(FeaturePlugin):
    def register_features(self) -> List[Feature]:
        return [
            Feature("formal_verification", "enterprise", ...),
            # ... all Enterprise features
        ]
    
    def register_tools(self) -> List[MCPTool]:
        # Return tool implementations extending Pro
        return [
            analyze_code_enterprise,  # Extends Pro, which extends Community
            # ...
        ]
    
    def validate_license(self, license: JWTLicenseData) -> bool:
        return license.tier == "enterprise"
```

### 4.4 Create Enterprise Tests

- [ ] Test Enterprise features work
- [ ] Test Enterprise extends Pro features
- [ ] Test 500+ Enterprise tests passing
- [ ] Test plugin loading with Enterprise license
- [ ] Test hierarchical loading (Community → Pro → Enterprise)

### 4.5 Documentation

- [ ] Create README.md (Enterprise features)
- [ ] Create INSTALLATION.md (Enterprise setup)
- [ ] Create API_REFERENCE.md (Enterprise APIs)
- [ ] Create SLA.md (Service level agreements)

**Acceptance Criteria**:
- [ ] Enterprise plugin tests passing (500+)
- [ ] All Enterprise features implemented
- [ ] Plugin loads correctly with Enterprise license
- [ ] Hierarchical loading works (Pro + Enterprise)
- [ ] Enterprise package can install alongside Community + Pro

---

## Phase 5: Public Release Preparation

**Timeline**: Week 5 (Feb 10-14)
**Owner**: Release Manager + Marketing
**Dependency**: Phase 4 complete

### 5.1 Final Testing

- [ ] Community + no plugins: All tests pass
- [ ] Community + Pro plugin: All tests pass
- [ ] Community + Pro + Enterprise: All tests pass
- [ ] Test all 22 tools at each tier
- [ ] Integration tests: 100+ tests passing
- [ ] Coverage: ≥90% on Community package

### 5.2 Publish Community Package

**Preparation**:
- [ ] Update version to 3.4.0
- [ ] Update CHANGELOG.md
- [ ] Update README.md (public-facing)
- [ ] Create CONTRIBUTING.md
- [ ] Verify no Pro/Enterprise code in source

**Release to public PyPI**:
- [ ] Build: `python -m build`
- [ ] Upload: `twine upload dist/*`
- [ ] Verify on PyPI.org
- [ ] Test installation: `pip install code-scalpel`

### 5.3 Publish Pro & Enterprise Packages

**For each (Pro first, then Enterprise)**:

- [ ] Create private PyPI or GitHub Packages repository
- [ ] Upload Pro package to private PyPI
- [ ] Upload Enterprise package to private PyPI
- [ ] Create access tokens for customers
- [ ] Document private installation process

### 5.4 GitHub Repository Setup

**Public Repository (code-scalpel)**:
- [ ] Make repo public
- [ ] Update README for public audience
- [ ] Add MIT LICENSE
- [ ] Add CONTRIBUTING.md
- [ ] Create GitHub Discussions
- [ ] Setup GitHub Issues template
- [ ] Add GitHub Actions for CI/CD

**Private Repositories**:
- [ ] Create code-scalpel-pro private repo
- [ ] Create code-scalpel-enterprise private repo
- [ ] Setup access controls (private org)
- [ ] Configure CI/CD

### 5.5 Announcement

- [ ] Blog post: "Code Scalpel is now open source"
- [ ] GitHub Discussions launch announcement
- [ ] Tweet/LinkedIn announcement
- [ ] Update ProductHunt with Pro/Enterprise info
- [ ] Email to existing beta users

**Acceptance Criteria**:
- [ ] Community package on public PyPI
- [ ] No Pro/Enterprise code in public repo
- [ ] License validation prevents feature access
- [ ] Installation documentation complete
- [ ] Upgrade path (Community → Pro → Enterprise) clear

---

## Rollback Plan (If Needed)

At any point, if issues arise:

1. **Revert code changes**: `git revert` to restore v3.3.0 codebase
2. **Remove public package**: Contact PyPI maintainers
3. **Notify customers**: Explain issue, provide timeline
4. **Fix and re-release**: Address root cause, test thoroughly

---

## Success Metrics

| Milestone | Target | Success Criteria |
|-----------|--------|------------------|
| **Phase 1** | Plugin system | 100+ tests passing, 0 blocking bugs |
| **Phase 2** | Extract Community | 4,700+ tests passing, ≥90% coverage |
| **Phase 3** | Pro plugin | 500+ tests passing, all Pro features work |
| **Phase 4** | Enterprise plugin | 500+ tests passing, all Enterprise features work |
| **Phase 5** | Public release | Community on PyPI, 100+ GitHub stars week 1 |

---

## Timeline Summary

```
Week 1 (Jan 13-17): Plugin System
  Mon-Tue: Design & interfaces
  Wed-Thu: Registry & loader
  Fri: Integration tests

Week 2 (Jan 20-24): Extract Community
  Mon-Tue: Mark code with tier comments
  Wed: Remove Pro/Enterprise code
  Thu: Refactor for plugins
  Fri: Full test suite

Week 3 (Jan 27-31): Pro Plugin
  Mon-Tue: Initialize repo, setup.py
  Wed-Thu: Extract Pro implementations
  Fri: Pro tests, documentation

Week 4 (Feb 3-7): Enterprise Plugin
  Mon-Tue: Initialize repo, setup.py
  Wed-Thu: Extract Enterprise implementations
  Fri: Enterprise tests, documentation

Week 5 (Feb 10-14): Public Release
  Mon-Tue: Final testing across all tiers
  Wed: Publish Community to PyPI
  Thu-Fri: Setup GitHub repos, announcement

Total: 5 weeks (35 business days)
```

---

## Notes

**Key Success Factors**:
1. Strong test coverage ensures safety during extraction
2. Feature registry integration prevents duplicate code
3. Plugin system is non-invasive (Community works without plugins)
4. Graceful degradation ensures Community users aren't affected
5. Clear interface contracts between packages prevent breakage

**Risk Mitigation**:
- Small incremental commits with tests
- Each phase can be rolled back independently
- Community package tested extensively before Pro
- Pro tested before Enterprise
- Customer communication planned in advance

**Next Steps**:
1. Review this checklist with team
2. Assign ownership for each phase
3. Create detailed JIRA/GitHub issues
4. Begin Phase 1 implementation (Week 1)
5. Execute Week 1 launch plan (Jan 6-12 - already underway)
