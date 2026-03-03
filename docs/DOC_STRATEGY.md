# Documentation Strategy

**Last Updated:** February 24, 2026
**Version:** Code Scalpel 2.0.0

---

## Build Pipeline

### How Docs Flow from Source to Website

```
Edit here (main repo):
  docs/website/docs/          ← public content source  ✏️ EDIT HERE
  docs/                       ← internal content only

Bridge (symlink, do not remove):
  website/docs/  →  docs/website/docs/

Build config (canonical — docs/website/mkdocs.yml symlinks here):
  website/mkdocs.yml

Running a build:
  bash scripts/build_docs.sh          # build only  → website/site/
  bash scripts/build_docs.sh --serve  # local preview at http://127.0.0.1:8000
  bash scripts/build_docs.sh --deploy # build + deploy to Hostinger

Deploy script:
  docs/website/deploy.sh              # rsync website/ to Hostinger
```

You **never need to leave the main repo** to update the public website. The entire workflow is:

1. Edit files under `docs/website/docs/` in the main repo
2. Run `bash scripts/build_docs.sh --serve` to preview locally
3. Run `bash scripts/build_docs.sh --deploy` to publish

### What Stays Private

Everything in `docs/` that is **not** under `docs/website/docs/` is internal and never built into the public website:

- `docs/architecture/` — design decisions
- `docs/testing/` — test reports and strategies
- `docs/marketing/` — sales collateral
- `docs/release_notes/` — internal release notes
- `docs/guides/ENTERPRISE_COMPLIANCE_*.md` — internal compliance guides
- This file (`DOC_STRATEGY.md`)

### Keeping the Config in Sync

`docs/website/mkdocs.yml` is a **symlink** to `website/mkdocs.yml`. There is exactly one config file. Editing either path edits the same file. Never replace the symlink with a copy.

To verify the symlink is intact:
```bash
readlink docs/website/mkdocs.yml
# Expected output: ../../website/mkdocs.yml
```

To rebuild the symlink if it is ever removed:
```bash
ln -sfn ../../website/mkdocs.yml docs/website/mkdocs.yml
```

### Release Checklist: Documentation

When releasing a new version, update these files in `docs/website/docs/`:

| File | Change |
|------|--------|
| `releases/v{VERSION}.md` | Create release notes page |
| `releases/index.md` | Update current release card + table row |
| `releases/changelog.md` | Add version entry |

Then update `website/mkdocs.yml`:
- Add the new version to the `Release Notes:` nav section
- Mark it `(Current)`, demote the previous current

Then run:
```bash
bash scripts/build_docs.sh --deploy
```

---

## Overview

Code Scalpel maintains three documentation systems. Each owns a distinct category of content and targets a different audience. This document defines content ownership, the update contract between systems, and rules for keeping them in sync.

---

## The Three Systems

| System | Location | Audience | Published? | Source of Truth For |
|--------|----------|----------|-----------|-------------------|
| **Internal docs** | `docs/` | Contributors, CI/CD | No | Architecture, release process, testing, compliance, marketing |
| **GitHub Wiki** | `wiki/` | Community, end-users | Yes (GitHub) | Installation, tool reference, troubleshooting, contributing |
| **Public website** | `docs/website/docs/` (symlinked to `website/docs/`) | Developers, buyers | Yes (code-scalpel.com) | Onboarding, guides, tutorials, landing pages |

---

## Ownership Rules

### `docs/` — Internal Documentation

**Owns:**
- Architecture and design decisions (`docs/architecture/`)
- Release process and pre-release pipeline (`RELEASE_PROCESS.md`, `RELEASING.md`)
- Testing strategy and verification reports (`docs/testing/`)
- Compliance documentation (`docs/guides/ENTERPRISE_COMPLIANCE_*.md`)
- Developer onboarding (`AGENTS.md`, `.github/copilot-instructions.md`)
- API and tool specifications (`docs/reference/DOCSTRING_SPECIFICATIONS.md`)
- Marketing and sales collateral (`docs/marketing/`)
- This strategy document

**Does not own:** User-facing installation instructions, end-user tutorials, public website copy.

**Update trigger:** Any code change, new tool, version bump, or process change.

---

### `wiki/` — GitHub Wiki

**Owns:**
- Installation instructions (`wiki/Installation.md`)
- End-user getting started guide (`wiki/Getting-Started.md`)
- MCP tools reference for end-users (`wiki/MCP-Tools-Reference.md`)
- Configuration reference (`wiki/Configuration.md`)
- Troubleshooting (`wiki/Troubleshooting.md`)
- Contributing guide (`wiki/Contributing.md`)
- Version changelog (`wiki/Changelog.md`)
- Architecture overview for users (`wiki/Architecture.md`)
- Security reporting (`wiki/Security.md`)

**Does not own:** Internal process docs, marketing copy, detailed API specifications (link to `docs/reference/` instead).

**Update trigger:** Any change that affects user-visible behavior, installation steps, tool count, supported languages, or version number.

---

### `docs/website/docs/` (Public Website)

**Owns:**
- Public landing page (`index.md`)
- Onboarding tutorials (`getting-started/`, `tutorials/`)
- Tool deep-dives written for web (`tools/deep-dive/`)
- Public API reference (`api-reference.md`)
- Pricing and tier guides (`guides/`)
- FAQ (`faq.md`)

**Does not own:** Internal release process, raw test reports, developer-only architecture details.

**Update trigger:** Any release, UX improvement, or change to the public-facing value proposition.

---

## Content Overlap Rules

Some topics appear in multiple systems. The rules below prevent contradictory content.

### Tool Count

**Single source of truth:** `pyproject.toml` version + `docs/reference/AUDIT_REPORT.md`

| System | What to write |
|--------|--------------|
| `docs/INDEX.md` | Current count from AUDIT_REPORT |
| `wiki/Home.md` | Match, update on every version bump |
| `wiki/MCP-Tools-Reference.md` | Full table, match count in heading |
| `wiki/Architecture.md` | ASCII diagram tool-layer label |
| `website/docs/index.md` | Match, update on every version bump |

### Supported Languages

**Single source of truth:** `src/code_scalpel/code_parsers/extractor.py` (`Language` enum)

Update all three systems when a new language parser ships.

**Current (v2.0.0):** Python, JavaScript, TypeScript, Java, C, C++, C#

### Version Numbers

**Single source of truth:** `pyproject.toml`

Must match in: `docs/INDEX.md`, `wiki/Home.md`, `wiki/Changelog.md`, `website/docs/changelog.md`, `CHANGELOG.md`, `README.md`, `AGENTS.md`, `.github/copilot-instructions.md`.

### Installation Instructions

**Single source of truth:** `wiki/Installation.md`

`docs/` may link to it. `website/docs/getting-started/` may have a simplified version but must stay in sync with the pip package name, Docker image name, and Python version requirement.

---

## Update Contract

When any of the following events happen, update ALL systems as described:

### Version Bump

| File to change | What to update |
|----------------|----------------|
| `pyproject.toml` | `version = "X.Y.Z"` |
| `docs/INDEX.md` | Header version + date |
| `wiki/Home.md` | Version in intro |
| `wiki/Changelog.md` | New version section |
| `wiki/MCP-Tools-Reference.md` | Tool count if changed |
| `wiki/Architecture.md` | Tool count if changed |
| `website/docs/changelog.md` | New version section |
| `README.md` | Version badge / footer |
| `AGENTS.md` | Footer version + date |
| `.github/copilot-instructions.md` | Project Context table |
| `CHANGELOG.md` | New entry |

### New MCP Tool Added

| File to change | What to update |
|----------------|----------------|
| `docs/reference/DOCSTRING_SPECIFICATIONS.md` | Add tool spec |
| `docs/reference/AUDIT_REPORT.md` | Add row |
| `docs/reference/mcp_tools_current.md` | Add entry |
| `wiki/Home.md` | Update tool count |
| `wiki/MCP-Tools-Reference.md` | Update count + add section |
| `wiki/Architecture.md` | Update tool-layer count |
| `website/docs/index.md` | Update count if featured |
| `.github/copilot-instructions.md` | Update tool list |
| `capabilities/*.json` (golden files) | Regenerate |

### New Language Supported

| File to change | What to update |
|----------------|----------------|
| `wiki/Installation.md` | Language prereqs if any |
| `wiki/MCP-Tools-Reference.md` | Add to language tables |
| `wiki/Architecture.md` | Add to AST Parsers section |
| `wiki/Getting-Started.md` | Example if applicable |
| `website/docs/index.md` | Update language list |
| `docs/INDEX.md` | Update polyglot section |
| `README.md` | Update language table |
| `capabilities/README.md` | Add language to array |
| `.github/copilot-instructions.md` | Update language list |

---

## Content That Must Never Be Duplicated

The following content exists in exactly one place. Other files must **link**, not copy:

| Content | Source of Truth | Others must link here |
|---------|-----------------|----------------------|
| Tool docstrings / specs | `docs/reference/DOCSTRING_SPECIFICATIONS.md` | Link from wiki and website |
| Tier limit values | `src/code_scalpel/capabilities/limits.toml` | Link from docs/wiki |
| Release notes | `docs/release_notes/RELEASE_NOTES_vX.Y.Z.md` | Link from wiki/Changelog and website |
| Pre-release checklist | `docs/RELEASE_PROCESS.md` | Link from AGENTS.md |
| Security policy | `SECURITY.md` | Link from wiki/Security and website |
| License | `LICENSE` | Reference only |

---

## Anti-Patterns to Avoid

- Writing installation instructions in `docs/` instead of `wiki/`
- Copying tool specs into the wiki instead of linking to `docs/reference/`  
- Updating a version number in one file without running the checklist above
- Putting marketing copy in `wiki/` or `docs/architecture/`
- Creating new root-level `.md` files in `docs/` for content that belongs in a subdirectory (see `docs/DOC_STRATEGY.md` Rule 4 in `.github/copilot-instructions.md`)

---

## Review Cadence

- **Per release:** Run the Version Bump checklist above
- **Per quarter:** Scan all three systems for stale version references with `grep -r "1\.[0-9]\." docs/ wiki/ website/docs/`
- **Per new tool or language:** Run the appropriate checklist section above

---

**Maintained by:** Developer Relations + Engineering
**Last Updated:** February 24, 2026
