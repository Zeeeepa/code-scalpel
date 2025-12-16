# Quick Reference: Document Organization

**Last Updated:** December 15, 2025

## 📍 Where to Find What

### 🏠 Root Directory (Essential Documents)
Only governance and quick-start materials belong here.

| Document | Purpose | For Whom |
|----------|---------|----------|
| `README.md` | Project overview, installation, quick start | Everyone |
| `SECURITY.md` | Security policies and reporting | Security team, users |
| `DEVELOPMENT_ROADMAP.md` | Future features, milestones, strategy | Project leads, contributors |
| `DOCKER_QUICK_START.md` | Quick Docker deployment guide | DevOps, developers |
| `RELEASE_v*.*.*.SUMMARY.md` | Release status and summaries | Stakeholders, users |
| `LICENSE` | Legal terms (MIT) | Legal team, users |

### 📚 docs/ Subdirectories (Detailed Documentation)

| Directory | Contents | Example |
|-----------|----------|---------|
| `docs/deployment/` | Deployment procedures, checklists, troubleshooting | DOCKER_DEPLOYMENT_CHECKLIST.md |
| `docs/release_notes/` | Comprehensive version release documentation | RELEASE_NOTES_v1.5.0.md |
| `docs/architecture/` | System design, module descriptions, data flows | Architecture diagrams, PDG design |
| `docs/guides/` | How-to guides and tutorials | Getting started guides |
| `docs/modules/` | API reference and module internals | Per-module documentation |
| `docs/compliance/` | Regulatory, security, audit documentation | Compliance reports, checklists |
| `docs/ci_cd/` | CI/CD pipeline configuration | Pipeline docs, GitHub Actions config |
| `docs/internal/` | Internal team documentation | Design discussions, decisions |
| `docs/research/` | Research findings and benchmarks | Performance studies, analysis |

### 🏆 release_artifacts/ (Evidence & Validation)

```
release_artifacts/v{VERSION}/
├── v{VERSION}_mcp_tools_evidence.json      Tool inventory
├── v{VERSION}_test_evidence.json           Test results  
├── v{VERSION}_performance_evidence.json    Benchmarks
├── v{VERSION}_security_evidence.json       Security scan
└── v{VERSION}_deployment_evidence.json     Deployment validation
```

### 💡 examples/ (Executable Code)
- `examples/claude_example.py` - Claude API integration
- `examples/autogen_example.py` - AutoGen framework
- `examples/langchain_example.py` - LangChain integration
- `examples/crewai_example.py` - CrewAI framework
- `examples/security_analysis_example.py` - Security scanning
- `examples/symbolic_execution_example.py` - Symbolic execution

## 🔍 Common Scenarios

### "I'm new, where do I start?"
1. Read [README.md](README.md) - Overview and installation
2. See [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - Get running quickly
3. Check [docs/getting_started.md](docs/getting_started.md) - Detailed getting started
4. Explore [docs/](docs/) - Topic-specific guides

### "I need to deploy this to Docker"
1. Quick overview: [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)
2. Full checklist: [docs/deployment/DOCKER_DEPLOYMENT_CHECKLIST.md](docs/deployment/DOCKER_DEPLOYMENT_CHECKLIST.md)
3. Troubleshoot: [docs/deployment/DOCKER_CONNECTION_TROUBLESHOOTING.md](docs/deployment/DOCKER_CONNECTION_TROUBLESHOOTING.md)
4. Volumes: [docs/deployment/docker_volume_mounting.md](docs/deployment/docker_volume_mounting.md)

### "I need to understand the architecture"
1. Design overview: [docs/architecture/](docs/architecture/)
2. Module details: [docs/modules/](docs/modules/)
3. API reference: Each module's documentation
4. Research findings: [docs/research/](docs/research/)

### "What changed in version 1.5.0?"
1. Summary: [RELEASE_v1.5.0_SUMMARY.md](RELEASE_v1.5.0_SUMMARY.md) (root)
2. Details: [docs/release_notes/RELEASE_NOTES_v1.5.0.md](docs/release_notes/RELEASE_NOTES_v1.5.0.md)
3. Evidence: [release_artifacts/v1.5.0/](release_artifacts/v1.5.0/)
4. Migration: See release notes for upgrade guide

### "I need to add documentation"
1. Classify: Is it governance (root), feature guide (docs/), or something else?
2. Choose location: Use table above to find appropriate directory
3. Follow naming: `TOPIC_DESCRIPTION.md` or `DOCUMENT_v{VERSION}.md`
4. Update index: Add to [docs/INDEX.md](docs/INDEX.md)
5. Reference guide: [DOCUMENT_ORGANIZATION.md](DOCUMENT_ORGANIZATION.md)

## 📊 Document Statistics

| Category | Location | Count | Purpose |
|----------|----------|-------|---------|
| Root (Governance) | / | 10 | Project status, quick-start |
| Release Notes | docs/release_notes/ | 11+ | Version documentation |
| Architecture | docs/architecture/ | Multiple | System design |
| Guides | docs/guides/ | Multiple | How-to documentation |
| Deployment | docs/deployment/ | 7 | Deployment procedures |
| Examples | examples/ | 7+ | Runnable code |
| Release Artifacts | release_artifacts/v*/ | 30+ | Evidence files |

## 🎯 Key Principles

1. **Root = Governance** - Only project status and essential info
2. **docs/ = Features** - Organized by topic and functionality
3. **release_artifacts/ = Evidence** - Test results, metrics, validation
4. **examples/ = Code** - Runnable, tested integrations

## 🔗 Important Links

- [DOCUMENT_ORGANIZATION.md](DOCUMENT_ORGANIZATION.md) - Complete reference guide
- [docs/INDEX.md](docs/INDEX.md) - Master table of contents
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Copilot guidelines
- [CONTRIBUTING_TO_MCP_REGISTRY.md](docs/CONTRIBUTING_TO_MCP_REGISTRY.md) - Contribution guide

## ✅ Quick Checklist for New Documents

When adding documentation:

- [ ] Decided on location (root vs docs/ vs release_artifacts/ vs examples/)
- [ ] Followed naming convention (TOPIC_DESCRIPTION.md)
- [ ] Added change tag ([20251215_DOCS])
- [ ] Updated [docs/INDEX.md](docs/INDEX.md) 
- [ ] Tested all relative links
- [ ] Verified code examples work
- [ ] Reviewed for style consistency
- [ ] Got appropriate review/approval

## 🚀 Quick Commands

```bash
# List root documentation
ls -1 *.md

# List deployment documentation
ls -1 docs/deployment/

# Find a specific document
find docs/ -name "*deployment*"

# Search for a topic
grep -r "topic" docs/

# Validate markdown links
grep -r "\[.*\](.*\.md)" docs/
```

---

**Status:** Current ✓  
**Last Review:** December 15, 2025  
**Organization Standard:** [DOCUMENT_ORGANIZATION.md](DOCUMENT_ORGANIZATION.md)
