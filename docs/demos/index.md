# Code Scalpel MCP Tools: Demo Scripts

Welcome to the Code Scalpel demo script collection! These comprehensive demos showcase our MCP tools organized by persona and demonstrating the **Four Pillars** of Code Scalpel.

## Four Pillars

1. **Governable AI**: Audit trails, policy enforcement, compliance reporting
2. **Accurate AI**: Graph-based facts (AST/PDG), no hallucinations, precision analysis
3. **Safer AI**: Parse-before-write, syntax-aware gatekeeper, validation
4. **Cheaper AI**: Context reduction (200 tokens vs 15k), efficient surgical operations

## Personas

### 🎨 Vibe Coder
Casual user seeking quick wins, visual demonstrations, and fast results. Values simplicity and immediate impact.

### 👨‍💻 Developer
Professional engineer focused on accuracy, efficiency, and technical depth. Values precision and comprehensive solutions.

### 👔 Technical Leader
Governance-focused, compliance-driven, concerned with team safety and organizational standards. Values audit trails and ROI.

---

## Demo Matrix

| Persona | Pillar | Demo Title | Tier | Duration |
|---------|--------|------------|------|----------|
| **Vibe Coder** | Cheaper AI | [15k Tokens → 200: Extract What You Need](vibe-coder/01-cheaper-extract.md) | Community | 5 min |
| Vibe Coder | Accurate AI | [Stop Hallucinating: Detect Fake Sanitizers](vibe-coder/02-accurate-sanitizers.md) | Community | 7 min |
| Vibe Coder | Safer AI | [No More Broken Commits: Auto-Validate Refactors](vibe-coder/03-safer-refactor.md) | Pro | 8 min |
| Vibe Coder | Governable AI | [Your AI Safety Net: Audit What Changed](vibe-coder/04-governable-audit.md) | Pro | 6 min |
| **Developer** | Accurate AI | [Graph Truth: Cross-File Bug Detective](developer/01-accurate-cross-file.md) | Pro | 12 min |
| Developer | Cheaper AI | [200x Context Efficiency: Surgical Code Edits](developer/02-cheaper-surgical.md) | Pro | 10 min |
| Developer | Safer AI | [Symbolic Execution: Find Hidden Edge Cases](developer/03-safer-symbolic.md) | Pro | 15 min |
| Developer | Governable AI | [Custom Policies: Enforce Team Standards](developer/04-governable-policies.md) | Enterprise | 12 min |
| **Tech Leader** | Governable AI | [SOC2/HIPAA Compliance Reports in 60 Seconds](tech-leader/01-governable-compliance.md) | Enterprise | 10 min |
| Tech Leader | Accurate AI | [Supply Chain Guardian: Typosquat Detection](tech-leader/02-accurate-supply-chain.md) | Enterprise | 8 min |
| Tech Leader | Safer AI | [The Perfect Guard: Block Risky Commits Pre-Merge](tech-leader/03-safer-perfect-guard.md) | Enterprise | 12 min |
| Tech Leader | Cheaper AI | [Monorepo Mastery: Incremental Crawl at Scale](tech-leader/04-cheaper-monorepo.md) | Enterprise | 10 min |

---

## Browse by Persona

### 🎨 Vibe Coder Demos

Quick wins and visual demonstrations perfect for getting started with Code Scalpel.

1. **[15k Tokens → 200: Extract What You Need](vibe-coder/01-cheaper-extract.md)** (5 min, Community)
   - **Pillar**: Cheaper AI
   - **Tools**: `extract_code`, `get_file_context`
   - **Highlight**: 75x cheaper token usage, context reduction in action

2. **[Stop Hallucinating: Detect Fake Sanitizers](vibe-coder/02-accurate-sanitizers.md)** (7 min, Community)
   - **Pillar**: Accurate AI
   - **Tools**: `security_scan`, `analyze_code`
   - **Highlight**: Graph-based analysis catches what LLMs miss

3. **[No More Broken Commits: Auto-Validate Refactors](vibe-coder/03-safer-refactor.md)** (8 min, Pro)
   - **Pillar**: Safer AI
   - **Tools**: `simulate_refactor`, `get_symbol_references`
   - **Highlight**: Catch broken references before committing

4. **[Your AI Safety Net: Audit What Changed](vibe-coder/04-governable-audit.md)** (6 min, Pro)
   - **Pillar**: Governable AI
   - **Tools**: `update_symbol`, audit trail
   - **Highlight**: Full transparency and rollback capability

### 👨‍💻 Developer Demos

Technical depth showcasing advanced features and cross-file analysis.

1. **[Graph Truth: Cross-File Bug Detective](developer/01-accurate-cross-file.md)** (12 min, Pro)
   - **Pillar**: Accurate AI
   - **Tools**: `type_evaporation_scan`, `get_cross_file_dependencies`
   - **Highlight**: Detect type mismatches across 247 files in 8 seconds

2. **[200x Context Efficiency: Surgical Code Edits](developer/02-cheaper-surgical.md)** (10 min, Pro)
   - **Pillar**: Cheaper AI
   - **Tools**: `update_symbol`, `get_file_context`
   - **Highlight**: 30x token reduction, 10x ROI

3. **[Symbolic Execution: Find Hidden Edge Cases](developer/03-safer-symbolic.md)** (15 min, Pro)
   - **Pillar**: Safer AI
   - **Tools**: `symbolic_execute`, `generate_unit_tests`
   - **Highlight**: Z3 solver explores all 47 execution paths

4. **[Custom Policies: Enforce Team Standards](developer/04-governable-policies.md)** (12 min, Enterprise)
   - **Pillar**: Governable AI
   - **Tools**: `code_policy_check`, `verify_policy_integrity`
   - **Highlight**: Encode tribal knowledge as enforceable rules

### 👔 Technical Leader Demos

Enterprise features focused on governance, compliance, and organizational scale.

1. **[SOC2/HIPAA Compliance Reports in 60 Seconds](tech-leader/01-governable-compliance.md)** (10 min, Enterprise)
   - **Pillar**: Governable AI
   - **Tools**: `code_policy_check` (compliance mode)
   - **Highlight**: Automated compliance for SOC2, HIPAA, PCI-DSS, GDPR

2. **[Supply Chain Guardian: Typosquat Detection](tech-leader/02-accurate-supply-chain.md)** (8 min, Enterprise)
   - **Pillar**: Accurate AI
   - **Tools**: `scan_dependencies`
   - **Highlight**: Detect typosquats and phantom packages

3. **[The Perfect Guard: Block Risky Commits Pre-Merge](tech-leader/03-safer-perfect-guard.md)** (12 min, Enterprise)
   - **Pillar**: Safer AI
   - **Tools**: `code_policy_check`, `security_scan`, `verify_policy_integrity`
   - **Highlight**: 2.7% block rate, 31 vulnerabilities prevented monthly

4. **[Monorepo Mastery: Incremental Crawl at Scale](tech-leader/04-cheaper-monorepo.md)** (10 min, Enterprise)
   - **Pillar**: Cheaper AI
   - **Tools**: `crawl_project` (incremental mode)
   - **Highlight**: 1200x faster updates, handles 127k files

---

## Browse by Pillar

### 💰 Cheaper AI (Context Reduction)

Demos showing how Code Scalpel reduces token usage by 10x-200x through surgical operations.

- [15k Tokens → 200: Extract What You Need](vibe-coder/01-cheaper-extract.md) (Vibe Coder, Community)
- [200x Context Efficiency: Surgical Code Edits](developer/02-cheaper-surgical.md) (Developer, Pro)
- [Monorepo Mastery: Incremental Crawl at Scale](tech-leader/04-cheaper-monorepo.md) (Tech Leader, Enterprise)

### 🎯 Accurate AI (Graph Facts)

Demos highlighting graph-based analysis that sees what context windows miss.

- [Stop Hallucinating: Detect Fake Sanitizers](vibe-coder/02-accurate-sanitizers.md) (Vibe Coder, Community)
- [Graph Truth: Cross-File Bug Detective](developer/01-accurate-cross-file.md) (Developer, Pro)
- [Supply Chain Guardian: Typosquat Detection](tech-leader/02-accurate-supply-chain.md) (Tech Leader, Enterprise)

### 🛡️ Safer AI (Parse-Before-Write)

Demos showcasing syntax-aware validation and formal verification.

- [No More Broken Commits: Auto-Validate Refactors](vibe-coder/03-safer-refactor.md) (Vibe Coder, Pro)
- [Symbolic Execution: Find Hidden Edge Cases](developer/03-safer-symbolic.md) (Developer, Pro)
- [The Perfect Guard: Block Risky Commits Pre-Merge](tech-leader/03-safer-perfect-guard.md) (Tech Leader, Enterprise)

### 📋 Governable AI (Audit Trails)

Demos focusing on compliance, policy enforcement, and organizational governance.

- [Your AI Safety Net: Audit What Changed](vibe-coder/04-governable-audit.md) (Vibe Coder, Pro)
- [Custom Policies: Enforce Team Standards](developer/04-governable-policies.md) (Developer, Enterprise)
- [SOC2/HIPAA Compliance Reports in 60 Seconds](tech-leader/01-governable-compliance.md) (Tech Leader, Enterprise)

---

## Browse by Tier

### 🆓 Community Tier (FREE)

Perfect for individual developers and small teams getting started.

- [15k Tokens → 200: Extract What You Need](vibe-coder/01-cheaper-extract.md) - Context reduction
- [Stop Hallucinating: Detect Fake Sanitizers](vibe-coder/02-accurate-sanitizers.md) - Security scanning

**Features**: Basic AST analysis, pattern matching, 5 test cases per query, 50-100 file limit

### 💎 Pro Tier ($49/month)

For professional developers requiring advanced analysis and cross-file capabilities.

- [No More Broken Commits: Auto-Validate Refactors](vibe-coder/03-safer-refactor.md)
- [Your AI Safety Net: Audit What Changed](vibe-coder/04-governable-audit.md)
- [Graph Truth: Cross-File Bug Detective](developer/01-accurate-cross-file.md)
- [200x Context Efficiency: Surgical Code Edits](developer/02-cheaper-surgical.md)
- [Symbolic Execution: Find Hidden Edge Cases](developer/03-safer-symbolic.md)

**Features**: Cross-file analysis, taint analysis, custom rules, 20 test cases, 500-1000 files, audit trails

### 🏢 Enterprise Tier (Custom Pricing)

For organizations requiring compliance, governance, and unlimited scale.

- [Custom Policies: Enforce Team Standards](developer/04-governable-policies.md)
- [SOC2/HIPAA Compliance Reports in 60 Seconds](tech-leader/01-governable-compliance.md)
- [Supply Chain Guardian: Typosquat Detection](tech-leader/02-accurate-supply-chain.md)
- [The Perfect Guard: Block Risky Commits Pre-Merge](tech-leader/03-safer-perfect-guard.md)
- [Monorepo Mastery: Incremental Crawl at Scale](tech-leader/04-cheaper-monorepo.md)

**Features**: Compliance frameworks (SOC2, HIPAA, GDPR, PCI-DSS), unlimited scale, distributed execution, cryptographic signatures, PDF reports

---

## Recording Guidelines

### Equipment
- **Screen Recording**: OBS Studio or Camtasia (1920×1080, 30fps)
- **Microphone**: Blue Yeti or equivalent (clear audio essential)
- **Terminal**: iTerm2 with large font (18pt+), high contrast theme
- **IDE**: VS Code with readable theme

### Visual Standards
- **On-screen Text**: Bold, 48pt minimum, high contrast
- **Code Snippets**: 16pt font, syntax highlighting
- **Diagrams**: Mermaid or draw.io, export as PNG
- **Overlays**: Branded lower-third for key stats

### Editing Workflow
1. Cut dead air (max 2s pauses)
2. Add chapters every 2-3 minutes
3. Speed up slow operations to 1.5x
4. Add captions (auto-generate with Descript or Rev.com)
5. Call to action in last 30 seconds

---

## Test Fixtures

All demos use fixtures from the **Ninja Warrior** test suite:

- `tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/01_the_full_stack_snap/` - Type evaporation
- `tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/02_the_surgeon_vs_the_butcher/` - Large file surgical editing
- `tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/03_the_typosquat_trap/` - Supply chain attack
- `tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/04_hidden_bug/` - Hidden edge case
- `tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/challenges/06_policy_prison/` - Policy violations
- `tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-structural/mcp_contract/ninja_warrior/test_ninja_anti_hallucination.py` - Fake sanitizer
- `tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/workflow-structural/mcp_contract/ninja_warrior/test_ninja_vibe_coding_adversarial.py` - Adversarial patterns

---

## Success Metrics

### Per-Demo KPIs
- **Engagement**: 1000+ views/month, >70% watch time
- **Conversion**: >15% click-through to docs, >5% trial signups
- **Retention**: >30% returning viewers

### Portfolio KPIs
- ✓ All 4 pillars represented per persona
- ✓ Balanced tier coverage (4 Community, 5 Pro, 3 Enterprise)
- ✓ 15+ unique MCP tools demonstrated
- ✓ Leverages existing Ninja Warrior test fixtures

---

## Getting Started

1. **Choose your persona**: Are you a Vibe Coder, Developer, or Technical Leader?
2. **Pick a pillar**: Which of the Four Pillars interests you most?
3. **Select a demo**: Browse by persona, pillar, or tier
4. **Follow the script**: Each demo includes step-by-step recording instructions
5. **Use the fixtures**: All demos reference existing test scenarios

---

## Additional Resources

- **MCP Tools Documentation**: [Link to full MCP tool reference]
- **Tier Comparison**: [Link to pricing page]
- **Ninja Warrior Test Suite**: `tests/mcp_tool_verification/mcp_inspector/code-scalpel-ninja-warrior/`
- **Configuration Files**:
  - `.code-scalpel/limits.toml` - Numeric limits per tier
  - `.code-scalpel/features.toml` - Capability arrays per tier

---

## Contributing

Found an issue or want to suggest improvements? Please open an issue or submit a pull request.

**Happy Demoing!** 🎬
