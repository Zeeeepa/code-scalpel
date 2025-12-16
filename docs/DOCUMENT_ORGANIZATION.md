# Document Organization Guide

**Last Updated:** December 15, 2025

This guide describes the organization of all documentation in the Code Scalpel project. All contributors must follow these guidelines when creating, updating, or maintaining project documentation.

## Quick Reference: Document Locations

### Root Level (Governance & Status)
```
/README.md                                    - Project overview
/SECURITY.md                                  - Security policies
/DEVELOPMENT_ROADMAP.md                       - Feature roadmap
/LICENSE                                      - MIT License
/DOCKER_QUICK_START.md                        - Docker quick start guide
(All release & deployment docs: docs/ subdirectories)
```

### Comprehensive Documentation (docs/)
```
docs/INDEX.md                                 - Master TOC
docs/COMPREHENSIVE_GUIDE.md                   - End-to-end feature guide
docs/getting_started.md                       - Developer quick start
docs/CONTRIBUTING_TO_MCP_REGISTRY.md          - MCP registry guide
docs/release_gate_checklist.md                - Pre-release checklist
docs/agent_integration.md                     - AI agent integration
docs/examples.md                              - Code examples
docs/V1.5.1_TEAM_ONBOARDING.md                - Team onboarding

docs/architecture/                            - System design & architecture
docs/guides/                                  - How-to guides & tutorials
docs/modules/                                 - API reference & internals
docs/parsers/                                 - Parser documentation
docs/ci_cd/                                   - CI/CD configuration
docs/deployment/                              - Deployment procedures
docs/compliance/                              - Regulatory & audit docs
docs/release_notes/                           - Version release notes
docs/internal/                                - Internal team docs
docs/research/                                - Research & benchmarks
```

### Release Artifacts (release_artifacts/)
```
release_artifacts/v{VERSION}/
  ├── v{VERSION}_mcp_tools_evidence.json      - Tool inventory & specs
  ├── v{VERSION}_test_evidence.json           - Test results & coverage
  ├── v{VERSION}_performance_evidence.json    - Benchmarks & metrics
  ├── v{VERSION}_security_evidence.json       - Security scan results
  └── v{VERSION}_deployment_evidence.json     - Deployment validation
```

### Code Examples (examples/)
```
examples/claude_example.py                    - Claude integration
examples/autogen_example.py                   - AutoGen framework
examples/langchain_example.py                 - LangChain integration
examples/crewai_example.py                    - CrewAI framework
examples/security_analysis_example.py         - Security scanning
examples/symbolic_execution_example.py        - Symbolic execution
```

## Document Classification

### Root-Level Documents
**Purpose:** Accessibility and project visibility for all stakeholders

**When to use:**
- Project overview and status information
- Security policies and advisories
- Strategic roadmap and planning
- Critical deployment information
- Release summaries

**Who creates:**
- Project leads
- Release managers
- Security team

### docs/ Subdirectories
**Purpose:** Organized, topic-specific, discoverable documentation

**When to use:**
- Feature explanations and tutorials
- Architecture and design documentation
- API reference and module internals
- Getting started guides
- Integration procedures

**Who creates:**
- Technical writers
- Architects
- Feature implementers

### release_artifacts/v{VERSION}/
**Purpose:** Audit trail and verification records for releases

**When to use:**
- Documenting test results and coverage
- Recording tool inventory and specifications
- Capturing performance metrics
- Verifying security compliance
- Validating deployment procedures

**Who creates:**
- Release engineering team
- QA and testing teams
- Deployment engineers

### examples/
**Purpose:** Executable, runnable demonstrations

**When to use:**
- Showing integration patterns
- Demonstrating API usage
- Providing copy-paste ready code
- Illustrating best practices

**Who creates:**
- Developers
- Technical advocates
- Integration partners

## Naming Conventions

### Markdown Files
- **Topics:** `TOPIC_DESCRIPTION.md` (uppercase for root-level, mixed-case for subdirs)
  - Examples: `agent_integration.md`, `COMPREHENSIVE_GUIDE.md`
- **Versions:** `DOCUMENT_v{VERSION}.md`
  - Example: `RELEASE_NOTES_v1.5.0.md`
- **Summaries:** `DOCUMENT_SUMMARY.md`
  - Example: `DEPLOYMENT_FINAL_REPORT.md`

### JSON Evidence Files
- **Format:** `v{VERSION}_{TYPE}_evidence.json`
- **Types:** `mcp_tools`, `test`, `performance`, `security`, `deployment`
- **Examples:**
  - `v1.5.0_test_evidence.json`
  - `v1.5.0_security_evidence.json`

### Directories
- **Kebab-case:** `ci_cd`, `release_notes`, `release_artifacts`
- **Descriptive names:** Each directory has a clear, single purpose

## Cross-Referencing Rules

### Link Format
```markdown
# Same directory
[Link text](document.md)

# Different directory (relative)
[Link text](../other_dir/document.md)

# With section anchor
[Link text](../path/document.md#section-heading)

# Specific line (when necessary)
[file.md](file.md#L10)
```

### Best Practices
1. Use descriptive link text (not "click here")
2. Prefer relative paths (portable)
3. Update INDEX.md when adding new documents
4. Test all links before committing
5. Avoid deep nesting (max 3 levels)

## Document Lifecycle

### Active Documents
- Current version guides
- Latest release notes
- In-progress features
- Current best practices

**Status:** Maintained and regularly updated

### Archived Documents
- Previous release notes
- Historical documentation
- Superseded guides
- Old implementation details

**Status:** Kept for historical reference, not updated

### Deprecated Documents
- Outdated procedures
- Replaced features
- Legacy code documentation

**Template for deprecation:**
```markdown
> **DEPRECATED:** This documentation is outdated.
> See [new guide](new_guide.md) instead.
> Deprecated on: [DATE]
> Will be removed: [FUTURE DATE]
```

## Maintenance Procedures

### Adding New Documentation
1. **Classify the document** (root, docs/, examples, release_artifacts)
2. **Choose appropriate naming** per conventions above
3. **Write using style guidelines** (see below)
4. **Add cross-references** in related documents
5. **Update INDEX.md** with new document entry
6. **Test all links** before committing
7. **Tag the commit:** `[20251215_DOCS] Added new documentation`

### Updating Documentation
1. **Check for inconsistencies** with current codebase
2. **Update version numbers** if version-specific
3. **Test code examples** against current code
4. **Validate all links** after changes
5. **Update TOC** if headers changed
6. **Add change tag:** `[20251215_DOCS] Updated documentation`

### Archiving Documentation
1. Move to `docs/release_notes/` (for release docs)
2. Add "See also:" section pointing to replacement
3. No deletion—keep historical record
4. Update INDEX.md to mark as "Archived"

## Style Guidelines

### Header Hierarchy
```markdown
# Main Title (H1 - use once per document)

## Major Section (H2)

### Subsection (H3)

#### Details (H4 - use sparingly)
```

### Content Formatting
- **Bold:** `**Important term**` for emphasis
- **Code:** `` `symbol()` `` for inline code
- **Code blocks:** ` ```language ` for snippets
- **Lists:** Use `-` for unordered, `1.` for ordered
- **Tables:** Use markdown tables for comparisons

### Writing Style
- Professional, clinical tone
- No emojis or casual language
- Active voice preferred
- Clear, concise sentences
- Plain English without jargon (or explain it)

### Code Examples
- All examples must be tested
- Include language specification in code blocks
- Add explanatory comments
- Show complete, working code
- Provide context (imports, setup)

### Metadata
For substantial documents, include at top:
```markdown
# Document Title

**Status:** [Active|Archived|Deprecated]
**Last Updated:** YYYY-MM-DD
**Author:** [Name/Team]
**Version Applies To:** v1.5.0+

---
```

## Automation and Verification

### Link Validation
```bash
# Check all markdown links in docs/
grep -r "\[.*\](.*\.md)" docs/
```

### JSON Validation
```bash
# Validate evidence files
python -m json.tool release_artifacts/v*/\*.json
```

### Release Checklist
Before releasing, verify:
- [ ] All release notes are in `docs/release_notes/`
- [ ] Evidence files exist in `release_artifacts/v{VERSION}/`
- [ ] INDEX.md is updated with new documentation
- [ ] All links are valid and tested
- [ ] Code examples are tested
- [ ] Version numbers are consistent
- [ ] Breaking changes documented
- [ ] Migration guides provided

## Document Ownership

| Document Type | Owner | Review Required | Frequency |
|---|---|---|---|
| README.md | Project Lead | Yes | Per release |
| DEVELOPMENT_ROADMAP.md | Architect | Yes | Quarterly |
| docs/release_notes/ | Release Manager | Yes | Per release |
| docs/architecture/ | Architect | Yes | Per major change |
| docs/guides/ | Technical Writer | No | As needed |
| examples/ | Developer/Advocate | Yes | Per API change |
| release_artifacts/ | QA/Release Team | Yes | Per release |
| SECURITY.md | Security Team | Yes | Per incident |

## Enforcement

All pull requests touching documentation must:
1. Follow naming conventions
2. Update INDEX.md if adding documents
3. Include change tag (`[YYYYMMDD_DOCS]`)
4. Pass link validation
5. Have descriptive commit message
6. Be reviewed by document owner

Non-compliance will result in PR rejection.

## Questions or Issues?

Refer to:
- [docs/INDEX.md](docs/INDEX.md) - Master table of contents
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Copilot guidelines
- [CONTRIBUTING_TO_MCP_REGISTRY.md](docs/CONTRIBUTING_TO_MCP_REGISTRY.md) - Contribution guide
