# Code Scalpel - Defensible Marketing Claims

**Document Status:** Pre-Launch Review
**Version:** 1.0
**Date:** January 2026
**Purpose:** Honest assessment of marketing claims for public launch

---

## Executive Summary

This document provides an honest assessment of Code Scalpel's marketing claims, categorizing them as:
- **STRONG** - Fully defensible, mathematically provable
- **CONDITIONAL** - True under specific conditions (must be qualified)
- **REFRAME** - Current claim is misleading; better positioning available

---

## Claim Assessment Matrix

### Pillar 1: CHEAPER - Token Efficiency

| Current Claim | Assessment | Recommendation |
|---------------|------------|----------------|
| "99% token reduction" | **STRONG** | Keep - Demonstrable in Four Pillars notebook (97.9% measured) |
| "Operate on million-line codebases with 4K token models" | **CONDITIONAL** | Qualify: "...for surgical operations on individual functions" |
| "~150-200 tokens saved per MCP response" | **STRONG** | Keep - Measured via configurable output filtering |

**Recommended Claim:**
> "Reduce LLM context window usage by 95-99% through surgical code extraction. Our PDG-based extraction sends only the relevant function and its dependencies—not the entire file."

**Proof Point:** Four Pillars Demo shows 49x reduction (2,280 tokens → 47 tokens)

---

### Pillar 2: SAFER - Syntax Validation

| Current Claim | Assessment | Recommendation |
|---------------|------------|----------------|
| "AST-validated modifications" | **STRONG** | Keep - Every edit is parsed before write |
| "Mathematically verify modifications preserve AST structure" | **STRONG** | Keep - Literal AST parsing with type checking |
| "Backup creation before every change" | **STRONG** | Keep - Implemented in update_symbol |
| "Syntax validation prevents syntax errors" | **STRONG** | Keep - Parse-before-write is real |

**Recommended Claim:**
> "Every code modification is parsed and validated BEFORE touching your filesystem. Invalid syntax is rejected, never written. Backups are created automatically."

**Proof Point:** Parse-before-write demo shows SyntaxError caught and blocked

---

### Pillar 3: ACCURATE - Determinism

| Current Claim | Assessment | Recommendation |
|---------------|------------|----------------|
| "Eliminate AI hallucinations" | **CONDITIONAL** | Qualify: "...for code structure queries" |
| "Deterministic through AST/PDG/Z3" | **STRONG** | Keep - These are mathematical, not probabilistic |
| "When Code Scalpel says X, it's a mathematical fact" | **STRONG** | Keep - For symbol resolution, line numbers, call graphs |
| "100% path coverage test generation" | **CONDITIONAL** | Qualify: "...within Z3 solver constraints and timeout" |

**Recommended Claim:**
> "Code Scalpel provides deterministic answers to code structure questions. When we say 'function X is at line 47 with 3 callers', it's mathematically proven from the AST and PDG—not an LLM inference that might be wrong."

**Proof Point:** AST parsing is O(n) deterministic algorithm, not ML inference

---

### Pillar 4: GOVERNABLE - Compliance ⚠️

| Current Claim | Assessment | Recommendation |
|---------------|------------|----------------|
| "Enterprise-ready compliance" | **CONDITIONAL** | **Major qualification needed** |
| "Invisible governance at the MCP boundary" | **REFRAME** | Misleading - AI can bypass MCP entirely |
| "Audit trails for compliance" | **CONDITIONAL** | Only logs MCP operations, not direct edits |
| "Policy enforcement" | **CONDITIONAL** | Only when AI chooses to use MCP |

**The Enforcement Gap:**

Current claim implies: "AI cannot make changes without governance"
Reality: "AI CAN bypass MCP and edit files directly via bash, native IDE tools, etc."

**Honest Assessment:**
- ✅ Code Scalpel provides excellent governance infrastructure
- ✅ Audit trails are cryptographically signed and tamper-resistant
- ✅ Policy engine (OPA/Rego) is production-grade
- ❌ Enforcement requires AI to USE the MCP server
- ❌ No mechanism to FORCE AI tools to route through MCP

**Recommended Claim:**
> "Code Scalpel provides governance infrastructure for AI-assisted development: immutable audit trails, cryptographic policy verification, and compliance mapping. Enforcement at the repository level requires integration with git hooks or CI/CD pipelines."

**Or (for enterprise):**
> "Code Scalpel enables governance-by-design: AI agents that use Code Scalpel automatically get audit trails, policy enforcement, and compliance evidence. For mandatory enforcement, integrate with your CI/CD pipeline to reject commits without Code Scalpel audit coverage."

---

## Revised Four Pillars Messaging

### Original vs Recommended

| Pillar | Original | Recommended |
|--------|----------|-------------|
| **CHEAPER** | "Reduce context window by 99%" | "95-99% token reduction via surgical extraction" ✅ |
| **SAFER** | "Surgical software development" | "Parse-before-write validation prevents syntax corruption" ✅ |
| **ACCURATE** | "Eliminate AI hallucinations" | "Deterministic code structure queries—mathematical facts, not inferences" ✅ |
| **GOVERNABLE** | "Enterprise-ready compliance" | "Governance infrastructure with audit trails—enforce via git hooks/CI" ⚠️ |

---

## Claims by Audience

### For Individual Developers (Community Tier)

**STRONG Claims:**
- "Stop wasting tokens on full file context"
- "Never commit syntactically invalid code again"
- "Get exact line numbers and call graphs, not LLM guesses"
- "Free tier with 22 tools"

**Avoid:**
- Governance/compliance claims (not relevant to individuals)
- "Enterprise-ready" language

### For Teams (Pro Tier)

**STRONG Claims:**
- "Audit trail of every AI-assisted code change"
- "Change budgets limit blast radius"
- "Sanitizer recognition reduces false positives"
- "Cross-file security scanning"

**Conditional Claims (qualify):**
- "Policy enforcement" → "...for changes made via Code Scalpel"

### For Enterprise (Enterprise Tier)

**STRONG Claims:**
- "Compliance mapping to OWASP, SOC2, PCI-DSS, HIPAA"
- "Cryptographic policy integrity verification (HMAC-SHA256)"
- "Custom security policies via OPA/Rego"
- "Immutable JSONL audit logs"

**Must Qualify:**
- "Enforcement requires integration with CI/CD or git hooks"
- "Audit trail covers MCP operations; direct file edits require filesystem monitoring"

**Recommended Enterprise Positioning:**
> "Code Scalpel provides the governance layer for AI-assisted development. Combined with git hooks that require audit coverage, you get mandatory compliance for all AI code changes."

---

## Competitive Claims

### vs GitHub Copilot

| Claim | Defensible? | Notes |
|-------|-------------|-------|
| "Copilot suggests, we verify" | **YES** | Complementary positioning |
| "Copilot hallucinates, we prove" | **YES** | AST is deterministic |
| "Copilot has no audit trail" | **YES** | True |
| "We're more accurate" | **QUALIFIED** | For structure queries, yes; for code generation, N/A |

### vs SonarQube

| Claim | Defensible? | Notes |
|-------|-------------|-------|
| "SonarQube is reactive, we're proactive" | **YES** | Pre-modification vs post-commit |
| "SonarQube has high false positives" | **QUALIFIED** | Depends on configuration |
| "We integrate with AI agents" | **YES** | MCP-native vs CI/CD only |

### vs Cursor/Claude Code

| Claim | Defensible? | Notes |
|-------|-------------|-------|
| "We add safety to AI modifications" | **YES** | Parse-before-write |
| "We provide audit trails" | **YES** | (when used via MCP) |
| "AI can't bypass our governance" | **NO** | This is the enforcement gap |

---

## The "Capability Gap" - Our TRUE Differentiator

**Reframe the value proposition from "enforcement" to "capability":**

Code Scalpel doesn't just add rules—it gives AI capabilities it literally cannot have otherwise:

### Things LLMs CANNOT Do (But Code Scalpel Can)

1. **Guarantee symbol location accuracy**
   - LLM: "The function is probably around line 45-50"
   - Code Scalpel: "The function is at line 47, character 0, ending at line 52" (AST-verified)

2. **Trace data flow across files**
   - LLM: "This input might reach the database query"
   - Code Scalpel: "user_input flows through sanitize() → validate() → query() with 3 taint paths" (PDG-verified)

3. **Generate provably-correct test inputs**
   - LLM: "Try testing with edge cases like 0, -1, null"
   - Code Scalpel: "Z3 proves these 5 inputs hit all 5 branches: [specific values]"

4. **Validate syntax before write**
   - LLM: Writes potentially broken code
   - Code Scalpel: Parses and rejects invalid syntax before touching disk

5. **Provide deterministic security findings**
   - LLM: "This looks like it might be SQL injection"
   - Code Scalpel: "CWE-89 SQL Injection: taint source at line 12, sink at line 18, no sanitizer in path"

**Recommended Headline:**
> "Code Scalpel gives AI agents capabilities they can't have alone: deterministic code understanding, mathematically-verified security analysis, and provable test generation."

---

## Summary: The Honest Pitch

### What Code Scalpel IS:
- A deterministic pre-processor for probabilistic AI models
- Infrastructure for governance-by-design (audit trails, policies, compliance mapping)
- A capability layer that enables AI to do things it literally cannot do otherwise
- Parse-before-write validation that prevents syntax corruption

### What Code Scalpel IS NOT:
- A mandatory enforcement layer that prevents AI from bypassing it
- A replacement for CI/CD security gates
- A silver bullet for AI governance (requires integration for enforcement)

### The Honest Enterprise Pitch:
> "Code Scalpel provides the governance infrastructure for AI-assisted development. When AI agents use our MCP tools, they automatically get audit trails, policy enforcement, and compliance evidence. For mandatory enforcement—ensuring AI CAN'T bypass governance—integrate our audit verification with your git hooks or CI/CD pipeline. We provide the infrastructure; you define the enforcement points."

---

## Action Items for Launch

1. **Update README** - Qualify governance claims with enforcement context
2. **Add git hook example** - Show how to enforce audit coverage
3. **Create CI/CD integration guide** - "Reject commits without Code Scalpel audit"
4. **Update Four Pillars Demo** - Add honest "Enforcement Gap" section
5. **Revise enterprise pitch deck** - Lead with capability, follow with governance infrastructure

---

## Appendix: Claim Verification Sources

| Claim | Verification Method | Location |
|-------|---------------------|----------|
| 99% token reduction | Four Pillars Demo measurement | `examples/Four_Pillars_Demo.ipynb` |
| Parse-before-write | AST validation in update_symbol | `src/code_scalpel/tools/update_symbol.py` |
| HMAC-SHA256 integrity | Policy manifest verification | `src/code_scalpel/policy_engine/` |
| Z3 test generation | Symbolic execution implementation | `src/code_scalpel/symbolic_execution/` |
| PDG taint analysis | Taint tracking implementation | `src/code_scalpel/pdg/` |
| 4,388 tests | Test suite | `tests/` |
| 94% coverage | Coverage report | `.coverage` |
