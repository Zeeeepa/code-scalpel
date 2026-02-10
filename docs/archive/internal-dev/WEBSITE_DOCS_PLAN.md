# Code Scalpel Website Documentation Plan
# [20260203_DOCS] Comprehensive documentation strategy for codescalpel.dev

## Executive Summary

This document outlines the complete plan for creating user-facing documentation for the Code Scalpel website (codescalpel.dev). The documentation will serve users of all skill levels, from beginners to enterprise architects, covering all 22+ MCP tools, configuration options, and integration patterns.

**Target Platform:** MkDocs Material  
**Repository Location:** `website/` (git-ignored, deployed separately)  
**Target URL:** https://codescalpel.dev

---

## 1. Documentation Assessment Summary

### 1.1 Current Documentation Inventory

| Location | Files | Purpose |
|----------|-------|---------|
| `docs/` | 85+ files | Developer documentation |
| `docs/tools/deep_dive/` | 24 files | Tool deep dives |
| `docs/reference/` | 8 files | API specifications |
| `docs/guides/` | 14 files | Integration guides |
| `docs/getting_started/` | 4 files | Onboarding content |
| `.code-scalpel/` | 10+ files | Configuration reference |
| Root level | 5 files | Project overview |
| `examples/` | 15+ files | Code examples |

### 1.2 Content Quality Assessment

| Audience | Current Quality | Notes |
|----------|-----------------|-------|
| **Beginners** | ⭐⭐⭐⭐☆ | Good guides exist (BEGINNER_GUIDE.md, FAQ) |
| **Developers** | ⭐⭐⭐⭐⭐ | Excellent reference docs |
| **DevOps** | ⭐⭐⭐⭐☆ | CI/CD docs good, Docker needs expansion |
| **Enterprise** | ⭐⭐⭐☆☆ | Governance docs scattered |
| **Security** | ⭐⭐⭐☆☆ | Tool docs good, needs unified guide |

### 1.3 Identified Gaps

1. **No website landing page** - Need compelling homepage
2. **Missing step-by-step tutorials** - "How to do X" guides
3. **Scattered troubleshooting** - Needs centralization
4. **No interactive content** - Add Jupyter notebooks
5. **Enterprise guide fragmented** - Needs consolidation
6. **Security workflow missing** - Unified security guide needed

---

## 2. Technology Stack

### 2.1 Chosen Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Static Site Generator** | MkDocs Material | Best-in-class for technical docs |
| **Theme** | Material for MkDocs | Dark mode, search, code blocks |
| **Interactive Content** | Jupyter Notebooks | Hands-on learning via mkdocs-jupyter |
| **Diagrams** | Mermaid | Native MkDocs support |
| **Deployment** | codescalpel.dev | Custom domain |
| **Versioning** | mike | Multi-version docs |

### 2.2 MkDocs Plugins

```yaml
plugins:
  - search                          # Full-text search
  - tags                            # Content tagging
  - glightbox                       # Image lightbox
  - mkdocs-jupyter                  # Notebook rendering
  - git-revision-date-localized    # Last updated dates
  - minify                          # Production optimization
```

### 2.3 Directory Structure

```
website/
├── mkdocs.yml                 # Main configuration
├── docs/
│   ├── index.md               # Homepage
│   ├── getting-started/       # Onboarding
│   ├── tools/                 # Tool reference
│   │   ├── category/          # By category
│   │   ├── tier/              # By tier
│   │   └── deep-dive/         # Detailed guides
│   ├── tutorials/             # Step-by-step
│   │   ├── beginner/
│   │   ├── intermediate/
│   │   ├── advanced/
│   │   └── notebooks/         # Jupyter notebooks
│   ├── configuration/         # Config files
│   ├── guides/                # Integration guides
│   ├── api/                   # API reference
│   ├── faq/                   # FAQ & troubleshooting
│   ├── releases/              # Release notes
│   └── contributing/          # Contribution guide
├── overrides/                 # Theme customizations
├── includes/                  # Reusable snippets
└── assets/                    # Images, logos
```

---

## 3. Content Strategy

### 3.1 User Journey Mapping

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER JOURNEY MAP                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DISCOVER          LEARN            ADOPT           MASTER       │
│  ────────          ─────            ─────           ──────       │
│                                                                  │
│  Homepage    →   Quick Start   →   Tutorials   →   Deep Dives   │
│  Why Code        Installation      First Scan      Custom        │
│  Scalpel?        (5 min)           AI Integration  Policies      │
│                                                                  │
│  ↓                ↓                 ↓               ↓            │
│                                                                  │
│  Tool            Getting           CI/CD           Enterprise    │
│  Overview        Started           Setup           Governance    │
│                  Notebook                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Content by User Level

#### Beginner Content (New Users)
- Homepage with value proposition
- 5-minute quick start
- IDE installation guides (Claude, VSCode, Cursor)
- "Your First Analysis" tutorial
- Understanding tool responses
- Interactive getting-started notebook
- FAQ for common questions

#### Intermediate Content (Daily Users)
- AI agent integration (LangChain, CrewAI, AutoGen)
- CI/CD pipeline setup
- Multi-language project support
- Tool category guides
- Configuration basics
- Security scanning workflow
- Interactive security analysis notebook

#### Advanced Content (Power Users & Enterprise)
- Enterprise governance setup
- Custom policy rules (OPA)
- Symbolic execution deep dive
- Architecture boundaries
- Change budget management
- Compliance & audit trails
- Multi-team deployment
- Interactive code extraction notebook

---

## 4. Tool Documentation Strategy

### 4.1 Tool Categories

| Category | Tools | User Need |
|----------|-------|-----------|
| **Analysis** | `analyze_code` | Understand code structure |
| **Extraction** | `extract_code`, `update_symbol`, `rename_symbol` | Modify code safely |
| **Context** | `crawl_project`, `get_file_context`, `get_symbol_references` | Navigate codebases |
| **Security** | `security_scan`, `unified_sink_detect`, `cross_file_security_scan`, `scan_dependencies`, `type_evaporation_scan` | Find vulnerabilities |
| **Graph** | `get_call_graph`, `get_graph_neighborhood`, `get_project_map`, `get_cross_file_dependencies` | Understand dependencies |
| **Symbolic** | `symbolic_execute`, `generate_unit_tests`, `simulate_refactor` | Verify changes |
| **Policy** | `validate_paths`, `verify_policy_integrity`, `code_policy_check` | Enforce governance |

### 4.2 Tool Documentation Template

Each tool page will follow this structure:

```markdown
# tool_name

> One-line description of what this tool does and why AI agents use it.

## Quick Reference

| Property | Value |
|----------|-------|
| **Category** | Security / Extraction / etc. |
| **Tier** | Community / Pro / Enterprise |
| **Languages** | Python, JavaScript, TypeScript, Java |
| **Token Cost** | ~50-200 tokens |

## What This Tool Does

[2-3 paragraph explanation in plain English]

## When AI Agents Use This Tool

[List of scenarios when an AI assistant would invoke this tool]

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ... | ... | ... | ... |

## Response Format

[Annotated JSON response example]

## Examples

### Basic Usage
[Simple example]

### Advanced Usage  
[Complex example with all parameters]

## Common Patterns

[How this tool is typically combined with other tools]

## Troubleshooting

[Common errors and solutions]

## Tier Differences

| Feature | Community | Pro | Enterprise |
|---------|-----------|-----|------------|
| ... | ... | ... | ... |
```

### 4.3 Tool Documentation Mapping

Source existing content from:

| Website Page | Source Content |
|--------------|----------------|
| `tools/deep-dive/analyze-code.md` | `docs/tools/deep_dive/ANALYZE_CODE_DEEP_DIVE.md` |
| `tools/deep-dive/extract-code.md` | `docs/tools/deep_dive/EXTRACT_CODE_DEEP_DIVE.md` |
| `tools/deep-dive/security-scan.md` | `docs/tools/deep_dive/SECURITY_SCAN_DEEP_DIVE.md` |
| ... | ... (all 22+ tools) |
| `tools/category/security.md` | `docs/tools/05_security_tools.md` |
| `tools/tier/community.md` | `docs/reference/mcp_tools_by_tier.md` |

---

## 5. Configuration Documentation Strategy

### 5.1 Configuration Files Inventory

| File | Purpose | Priority |
|------|---------|----------|
| `limits.toml` | Tier-based capability limits | HIGH |
| `config.json` | Core server settings | HIGH |
| `governance.yaml` | Policy rules | HIGH |
| `budget.yaml` | Change operation limits | MEDIUM |
| `response_config.json` | Response verbosity | MEDIUM |
| `architecture.toml` | Dependency boundaries | MEDIUM |
| `policy.yaml` | OPA policy rules | ADVANCED |

### 5.2 Configuration Documentation Template

```markdown
# filename.ext

> One-line description of this file's purpose.

## Overview

[What this file controls and when you'd modify it]

## File Location

```
.code-scalpel/filename.ext
```

## Complete Reference

[Full annotated example with all options]

## Common Configurations

### Solo Developer
[Minimal config]

### Small Team (5-20 developers)
[Standard config]

### Enterprise (20+ developers)
[Full governance config]

## Validation

[How to verify the config is working]

## Related Files

[Links to related config files]
```

---

## 6. Tutorial Content Plan

### 6.1 Beginner Tutorials

| Tutorial | Description | Prerequisites |
|----------|-------------|---------------|
| **Your First Security Scan** | Run security_scan on a Python file | Installation complete |
| **Extracting Code Without Hallucination** | Use extract_code to get exact functions | Basic IDE setup |
| **Understanding Tool Responses** | Parse JSON responses from MCP tools | First tool usage |

### 6.2 Intermediate Tutorials

| Tutorial | Description | Prerequisites |
|----------|-------------|---------------|
| **AI Agent Integration** | Connect Code Scalpel to LangChain/CrewAI | Basic tutorials |
| **CI/CD Pipeline Setup** | Add security scanning to GitHub Actions | Git/CI knowledge |
| **Multi-Language Projects** | Analyze Python + TypeScript together | Multiple languages |

### 6.3 Advanced Tutorials

| Tutorial | Description | Prerequisites |
|----------|-------------|---------------|
| **Enterprise Governance Setup** | Configure full governance stack | Intermediate |
| **Custom Policy Rules** | Write OPA policies for compliance | Policy basics |
| **Symbolic Execution Deep Dive** | Use Z3 for path exploration | Symbolic concepts |

### 6.4 Interactive Notebooks

| Notebook | Content | Learning Outcome |
|----------|---------|------------------|
| **getting-started.ipynb** | Install, configure, first analysis | Can use basic tools |
| **security-analysis.ipynb** | Full vulnerability scanning workflow | Can run security audits |
| **code-extraction.ipynb** | Extract, modify, update code | Can safely modify code |

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1)
- [x] Create `website/` directory structure
- [x] Set up `mkdocs.yml` configuration
- [x] Add `website/` to `.gitignore`
- [ ] Create homepage (`docs/index.md`)
- [ ] Create getting started section
- [ ] Create installation guides

### Phase 2: Tool Reference (Week 2)
- [ ] Create tool category pages (7 categories)
- [ ] Create tool tier pages (3 tiers)
- [ ] Migrate all 22+ deep dive docs
- [ ] Create tool index page

### Phase 3: Tutorials (Week 3)
- [ ] Create 3 beginner tutorials
- [ ] Create 3 intermediate tutorials  
- [ ] Create 3 advanced tutorials
- [ ] Create 3 interactive notebooks

### Phase 4: Configuration & Guides (Week 4)
- [ ] Document all config files (7 files)
- [ ] Create governance profile guides
- [ ] Create AI integration guides
- [ ] Create DevOps guides
- [ ] Create security guides

### Phase 5: Polish (Week 5)
- [ ] Create FAQ section
- [ ] Create troubleshooting hub
- [ ] Create API reference
- [ ] Create contributing guide
- [ ] Add release notes
- [ ] Review and proofread all content

---

## 8. Content Migration Map

### 8.1 Direct Migration (Copy & Adapt)

| Source | Destination | Adaptation Needed |
|--------|-------------|-------------------|
| `docs/BEGINNER_GUIDE.md` | `getting-started/index.md` | Simplify, add visuals |
| `docs/BEGINNER_FAQ.md` | `faq/general.md` | Reorganize by topic |
| `docs/INSTALLING_FOR_CLAUDE.md` | `getting-started/installation/claude-desktop.md` | Add screenshots |
| `docs/SETUP_CHECKLIST.md` | `getting-started/quick-start.md` | Convert to steps |
| `docs/tools/deep_dive/*.md` | `tools/deep-dive/*.md` | Add examples |
| `docs/guides/ai_agent_integration.md` | `guides/ai-integration/index.md` | Split by framework |
| `.code-scalpel/README.md` | `configuration/overview.md` | Simplify |
| `docs/release_notes/*.md` | `releases/*.md` | Direct copy |

### 8.2 New Content (Write Fresh)

| Page | Why New |
|------|---------|
| Homepage | Need marketing-friendly intro |
| Tutorials | Step-by-step format doesn't exist |
| Notebooks | Interactive format is new |
| Tool category overviews | Need user-friendly summaries |
| Troubleshooting hub | Currently scattered |
| Enterprise guide | Needs consolidation |

---

## 9. Quality Standards

### 9.1 Writing Style

- **Tone:** Professional but approachable
- **Voice:** Second person ("You can...", "Your code...")
- **Length:** Concise paragraphs (3-5 sentences max)
- **Examples:** Every concept needs a code example
- **Visuals:** Use diagrams, screenshots, and Mermaid charts

### 9.2 Technical Accuracy

- All code examples must be tested
- Tool parameters must match current API
- Version numbers must be accurate
- Links must be validated

### 9.3 Accessibility

- Alt text on all images
- Proper heading hierarchy
- Code blocks with language hints
- Color contrast compliance

---

## 10. Maintenance Plan

### 10.1 Update Triggers

| Event | Documentation Update |
|-------|---------------------|
| New tool added | Tool reference + tutorial |
| Tool parameter change | Deep dive + API reference |
| New version release | Release notes + changelog |
| Config file change | Configuration section |
| Bug fix | FAQ/troubleshooting if relevant |

### 10.2 Review Schedule

- **Weekly:** Check for broken links
- **Per Release:** Update version numbers
- **Quarterly:** Full content audit
- **Annually:** Major restructure review

---

## 11. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to first analysis | < 10 minutes | User surveys |
| Documentation coverage | 100% of tools | Audit |
| Search success rate | > 80% | Analytics |
| Page load time | < 2 seconds | Lighthouse |
| Mobile usability | 100% score | Lighthouse |

---

## Appendix A: File Listing

### A.1 Files to Create

```
website/docs/
├── index.md
├── getting-started/
│   ├── index.md
│   ├── quick-start.md
│   ├── first-analysis.md
│   ├── tiers.md
│   └── installation/
│       ├── index.md
│       ├── claude-desktop.md
│       ├── vscode.md
│       ├── cursor.md
│       ├── docker.md
│       └── pip.md
├── tools/
│   ├── index.md
│   ├── category/
│   │   ├── analysis.md
│   │   ├── extraction.md
│   │   ├── context.md
│   │   ├── security.md
│   │   ├── graph.md
│   │   ├── symbolic.md
│   │   └── policy.md
│   ├── tier/
│   │   ├── community.md
│   │   ├── pro.md
│   │   └── enterprise.md
│   └── deep-dive/
│       ├── index.md
│       └── [22+ tool pages]
├── tutorials/
│   ├── index.md
│   ├── beginner/
│   │   ├── index.md
│   │   ├── first-security-scan.md
│   │   ├── extracting-code.md
│   │   └── understanding-responses.md
│   ├── intermediate/
│   │   ├── index.md
│   │   ├── ai-agent-integration.md
│   │   ├── ci-cd-setup.md
│   │   └── multi-language.md
│   ├── advanced/
│   │   ├── index.md
│   │   ├── enterprise-governance.md
│   │   ├── custom-policies.md
│   │   └── symbolic-execution.md
│   └── notebooks/
│       ├── index.md
│       ├── getting-started.ipynb
│       ├── security-analysis.ipynb
│       └── code-extraction.ipynb
├── configuration/
│   ├── index.md
│   ├── overview.md
│   ├── files/
│   │   ├── index.md
│   │   ├── limits-toml.md
│   │   ├── config-json.md
│   │   ├── governance-yaml.md
│   │   ├── budget-yaml.md
│   │   ├── response-config-json.md
│   │   ├── architecture-toml.md
│   │   └── policy-yaml.md
│   ├── profiles/
│   │   ├── index.md
│   │   ├── permissive.md
│   │   ├── minimal.md
│   │   ├── default.md
│   │   └── restrictive.md
│   └── licensing/
│       ├── index.md
│       ├── comparison.md
│       └── activation.md
├── guides/
│   ├── index.md
│   ├── ai-integration/
│   │   ├── index.md
│   │   ├── claude.md
│   │   ├── copilot.md
│   │   ├── cursor.md
│   │   ├── langchain.md
│   │   ├── langgraph.md
│   │   ├── crewai.md
│   │   └── autogen.md
│   ├── devops/
│   │   ├── index.md
│   │   ├── github-actions.md
│   │   ├── gitlab-ci.md
│   │   ├── jenkins.md
│   │   └── docker.md
│   ├── security/
│   │   ├── index.md
│   │   ├── best-practices.md
│   │   ├── scanning-workflow.md
│   │   └── compliance.md
│   └── enterprise/
│       ├── index.md
│       ├── architecture.md
│       ├── multi-team.md
│       └── audit.md
├── api/
│   ├── index.md
│   ├── mcp-protocol.md
│   ├── tool-responses.md
│   ├── error-codes.md
│   └── oracle-middleware.md
├── faq/
│   ├── index.md
│   ├── general.md
│   ├── installation.md
│   ├── tools.md
│   ├── configuration.md
│   └── troubleshooting.md
├── releases/
│   ├── index.md
│   ├── v1.3.0.md
│   ├── v1.2.0.md
│   ├── v1.1.0.md
│   ├── v1.0.0.md
│   └── changelog.md
└── contributing/
    ├── index.md
    ├── setup.md
    ├── code-style.md
    ├── testing.md
    └── documentation.md
```

**Total Files to Create:** ~120 markdown files + 3 notebooks

---

## Appendix B: Dependencies

### B.1 Python Packages (for MkDocs)

```txt
mkdocs>=1.5.0
mkdocs-material>=9.5.0
mkdocs-material-extensions>=1.3.0
mkdocs-jupyter>=0.24.0
mkdocs-git-revision-date-localized-plugin>=1.2.0
mkdocs-minify-plugin>=0.7.0
mkdocs-glightbox>=0.3.0
mike>=2.0.0
```

### B.2 Build Commands

```bash
# Install dependencies
pip install -r website/requirements.txt

# Local development
cd website && mkdocs serve

# Build for production
cd website && mkdocs build

# Deploy with versioning
cd website && mike deploy --push --update-aliases 1.3.0 latest
```

---

*Document created: February 3, 2026*  
*Last updated: February 3, 2026*  
*Status: Implementation in progress*
