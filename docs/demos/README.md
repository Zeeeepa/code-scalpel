# Code Scalpel MCP Tools: Demo Scripts

This directory contains comprehensive demo scripts for recording marketing and onboarding videos showcasing Code Scalpel's MCP tools.

## 📁 Directory Structure

```
docs/demos/
├── README.md                           # This file
├── index.md                            # Main landing page with demo matrix
├── PHASE_2_REQUIREMENTS.md             # Asset preparation checklist
├── vibe-coder/                         # Casual user demos (4 demos)
│   ├── 01-cheaper-extract.md
│   ├── 02-accurate-sanitizers.md
│   ├── 03-safer-refactor.md
│   └── 04-governable-audit.md
├── developer/                          # Professional developer demos (4 demos)
│   ├── 01-accurate-cross-file.md
│   ├── 02-cheaper-surgical.md
│   ├── 03-safer-symbolic.md
│   └── 04-governable-policies.md
├── tech-leader/                        # Technical leadership demos (4 demos)
│   ├── 01-governable-compliance.md
│   ├── 02-accurate-supply-chain.md
│   ├── 03-safer-perfect-guard.md
│   └── 04-cheaper-monorepo.md
└── by-category/                        # Technical deep-dive demos (6 demos)
    ├── 01-static-analysis.md           # AST parsing, crawl, complexity metrics
    ├── 02-ast-analysis.md              # How ASTs work, extract_code mechanics
    ├── 03-pdg-call-graphs.md           # Call graphs, cross-file deps, neighborhoods
    ├── 04-symbolic-execution-z3.md     # Z3 solver, path exploration, test generation
    ├── 05-taint-analysis-security.md   # Taint tracking, sink detection, OWASP
    └── 06-polyglot-analysis.md         # 7-language support overview
```

## 🎯 Purpose

These demos serve multiple purposes:

1. **Marketing Assets**: Screen recordings for YouTube, social media
2. **Documentation Examples**: Embedded in docs website
3. **User Onboarding**: Step-by-step tutorials for new users
4. **Sales Enablement**: Show prospects the Four Pillars in action

## 📊 Demo Matrix

### By Persona (Marketing / Onboarding)

| Persona | Pillar | Demo | Tier | Duration |
|---------|--------|------|------|----------|
| Vibe Coder | Cheaper AI | 15k Tokens → 200 | Community | 5 min |
| Vibe Coder | Accurate AI | Detect Fake Sanitizers | Community | 7 min |
| Vibe Coder | Safer AI | Auto-Validate Refactors | Pro | 8 min |
| Vibe Coder | Governable AI | Audit What Changed | Pro | 6 min |
| Developer | Accurate AI | Cross-File Bug Detective | Pro | 12 min |
| Developer | Cheaper AI | Surgical Code Edits | Pro | 10 min |
| Developer | Safer AI | Symbolic Execution | Pro | 15 min |
| Developer | Governable AI | Custom Policies | Enterprise | 12 min |
| Tech Leader | Governable AI | SOC2/HIPAA Compliance | Enterprise | 10 min |
| Tech Leader | Accurate AI | Typosquat Detection | Enterprise | 8 min |
| Tech Leader | Safer AI | Block Risky Commits | Enterprise | 12 min |
| Tech Leader | Cheaper AI | Monorepo Incremental | Enterprise | 10 min |

**Subtotal**: 12 demos, 115 minutes

### By Technical Category (Deep Dives / Education)

| # | Category | Key Tools | Tier | Duration |
|---|----------|-----------|------|----------|
| 1 | Static Analysis | `analyze_code`, `crawl_project`, `get_file_context` | Community → Pro | 10 min |
| 2 | AST Analysis | `analyze_code`, `extract_code` | Community | 8 min |
| 3 | PDGs and Call Graphs | `get_call_graph`, `get_cross_file_dependencies` | Pro | 12 min |
| 4 | Symbolic Execution + Z3 | `symbolic_execute`, `generate_unit_tests` | Pro | 14 min |
| 5 | Taint Analysis + Security | `security_scan`, `unified_sink_detect` | Community → Enterprise | 12 min |
| 6 | 7-Language Polyglot | `analyze_code`, `extract_code`, `security_scan` | Community → Pro | 10 min |

**Subtotal**: 6 demos, 66 minutes

**Grand Total**: 18 demos, 181 minutes, covering all personas, pillars, and technical categories

## 🔄 Four Pillars

Each demo showcases one of Code Scalpel's Four Pillars:

### 1. 💰 Cheaper AI (Context Reduction)
- Extract only what you need (75x token reduction)
- Surgical edits (30x cheaper than full rewrites)
- Incremental indexing (1200x faster updates)

### 2. 🎯 Accurate AI (Graph Facts)
- AST + PDG analysis (no hallucinations)
- Cross-file bug detection (sees what context windows miss)
- Supply chain security (typosquat detection)

### 3. 🛡️ Safer AI (Parse-Before-Write)
- Simulate refactors before applying
- Symbolic execution (find all edge cases)
- Pre-merge security gates (block risky commits)

### 4. 📋 Governable AI (Audit Trails)
- Full audit logs with rollback
- Custom policy enforcement
- Compliance automation (SOC2, HIPAA, PCI-DSS, GDPR)

## 👥 Three Personas

### 🎨 Vibe Coder
- **Profile**: Casual user, quick wins, visual learner
- **Values**: Simplicity, immediate impact, fast results
- **Demos**: 4 (2 Community, 2 Pro)
- **Duration**: 26 minutes total

### 👨‍💻 Developer
- **Profile**: Professional engineer, accuracy-focused
- **Values**: Precision, efficiency, technical depth
- **Demos**: 4 (3 Pro, 1 Enterprise)
- **Duration**: 49 minutes total

### 👔 Technical Leader
- **Profile**: Governance-focused, compliance-driven
- **Values**: Audit trails, team safety, organizational standards, ROI
- **Demos**: 4 (all Enterprise)
- **Duration**: 40 minutes total

## 📖 Using the Demo Scripts

Each demo script contains:

1. **Metadata**: Persona, pillar, tier, duration
2. **Scenario**: Context and problem statement
3. **Tools Used**: Specific MCP tools demonstrated
4. **Recording Script**: Step-by-step instructions with timestamps
5. **Expected Outputs**: What the tool should produce
6. **Key Talking Points**: Narration suggestions
7. **Before/After Comparisons**: Visual evidence of improvement

### Example Usage

To record Demo "15k Tokens → 200":

1. Open [vibe-coder/01-cheaper-extract.md](vibe-coder/01-cheaper-extract.md)
2. Follow Phase 2 requirements to prepare fixtures
3. Set up recording environment (OBS, terminal, IDE)
4. Execute steps 1-6 with timestamps
5. Record narration for each step
6. Edit and add visual overlays

## 🛠️ Implementation Timeline

### Phase 1: Script Finalization ✅ COMPLETE
- Created all 12 demo markdown files
- Each includes step-by-step recording instructions
- Mapped to Ninja Warrior test fixtures

### Phase 2: Asset Preparation (Week 1) 🔄 IN PROGRESS
- See [PHASE_2_REQUIREMENTS.md](PHASE_2_REQUIREMENTS.md)
- Prepare test fixtures
- Configure recording equipment
- Create visual assets (diagrams, tables, overlays)

### Phase 3: Recording (Weeks 2-3)
- Record Developer demos first (highest impact)
- Then Vibe Coder and Tech Leader demos
- 2-3 demos per week

### Phase 4: Distribution (Week 4)
- Edit and add chapters
- Upload to YouTube
- Embed in docs website
- Launch social media campaign

## 📋 Phase 2 Requirements Summary

Before recording, complete these tasks:

### Test Environment
- [ ] Demo workspace created
- [ ] Tier configurations set up (Community, Pro, Enterprise)
- [ ] MCP server connected to Claude Desktop
- [ ] All MCP tools verified working

### Fixtures Prepared
- [ ] Large file (2000 lines) for extraction demo
- [ ] Fake sanitizer code for accuracy demo
- [ ] Refactor scenario (4 files) for safety demo
- [ ] Type evaporation (backend + frontend)
- [ ] Hidden bug for symbolic execution
- [ ] Typosquat requirements.txt
- [ ] Policy violation examples
- [ ] Large repo for monorepo demo

### Recording Equipment
- [ ] OBS Studio configured (1920×1080, 30fps)
- [ ] Blue Yeti microphone set up
- [ ] iTerm2/Terminal with 18pt font
- [ ] VS Code with readable theme
- [ ] Quiet recording environment

### Visual Assets
- [ ] 8 comparison tables (PNG)
- [ ] 5 Mermaid diagrams (PNG)
- [ ] 10 on-screen overlays (PNG)
- [ ] 6 thumbnail templates (PNG)

**Full details**: See [PHASE_2_REQUIREMENTS.md](PHASE_2_REQUIREMENTS.md)

## 🎬 Recording Standards

### Video Quality
- Resolution: 1920×1080
- Frame rate: 30fps
- Codec: H.264
- Bitrate: 6000 Kbps

### Audio Quality
- Sample rate: 48kHz
- Bit depth: 24-bit
- No background noise
- Clear narration

### Screen Readability
- Terminal font: 18pt minimum
- IDE font: 16pt minimum
- High contrast theme
- No dead air (max 2s pauses)

### Editing
- Add chapters every 2-3 minutes
- Speed up slow operations to 1.5x
- Include captions
- Call to action in last 30 seconds

## 📊 Success Metrics

### Per-Demo KPIs
- **Engagement**: 1000+ views/month, >70% watch time
- **Conversion**: >15% click-through, >5% trial signups
- **Retention**: >30% returning viewers

### Portfolio KPIs
- ✅ All 4 pillars represented per persona
- ✅ Balanced tier coverage (4 Community, 5 Pro, 3 Enterprise)
- ✅ 15+ unique MCP tools demonstrated
- ✅ Leverages Ninja Warrior test fixtures

## 🔗 Related Resources

- **MCP Tools Documentation**: [Coming soon]
- **Tier Comparison**: [.code-scalpel/limits.toml](../../.code-scalpel/limits.toml)
- **Feature Matrix**: [.code-scalpel/features.toml](../../.code-scalpel/features.toml)
- **Test Fixtures**: [tests/mcp_tool_verification/](../../tests/mcp_tool_verification/)

## 🚀 Quick Start

1. **Choose a demo**: Browse [index.md](index.md)
2. **Prepare environment**: Follow [PHASE_2_REQUIREMENTS.md](PHASE_2_REQUIREMENTS.md)
3. **Record**: Execute demo script step-by-step
4. **Edit**: Add chapters, overlays, captions
5. **Distribute**: Upload to YouTube, embed in docs

## ⚠️ Important Notes

- **Internal Only**: These demo scripts are for internal preparation and not for public distribution
- **Fixtures Required**: All demos require test fixtures from Ninja Warrior suite
- **Tier Licenses**: Enterprise demos require valid Enterprise license JWT
- **Brand Guidelines**: Follow Code Scalpel brand guidelines for visual assets

## 🤝 Contributing

Found an issue or have suggestions?

1. Review the demo script
2. Identify the issue (incorrect command, wrong output, timing off)
3. Update the markdown file
4. Test the updated script
5. Submit changes for review

## 📝 Version History

- **v1.0** (2026-02-08): Initial release
  - 12 demo scripts created
  - Phase 2 requirements documented
  - Ready for asset preparation

---

**Status**: Phase 1 Complete ✅ | Phase 2 In Progress 🔄

**Next Action**: Complete Phase 2 requirements checklist

**Owner**: [Assign team member]

**Questions?** Contact the Code Scalpel team.
