# Code Scalpel v1.0.0 - Initial Release

**Release Date:** January 19, 2026  
**Status:** General Availability (GA)

---

## 🎉 Welcome to Code Scalpel v1.0.0

Code Scalpel is an **MCP (Model Context Protocol) server toolkit** designed for AI agents and developers to perform **surgical code operations** on real codebases with precision and safety.

This is the **first production release**, featuring 22 mature MCP tools for code analysis, security scanning, and automated transformations.

---

## ✨ Core Features

### 1. Code Analysis & Structure
- **`analyze_code`** - Parse and extract code structure (Python, JavaScript, TypeScript, Java)
- **`get_symbol_references`** - Find all usages of a symbol across the project
- **`get_cross_file_dependencies`** - Trace import chains and cross-file dependencies
- **`get_call_graph`** - Generate call graphs and trace execution flow
- **`get_project_map`** - Comprehensive project structure overview
- **`get_file_context`** - Quick file assessment without reading full content
- **`get_graph_neighborhood`** - Extract k-hop neighborhood subgraph

### 2. Code Extraction & Modification
- **`extract_code`** - Surgical extraction of functions/classes by name (not line guessing)
- **`update_symbol`** - Safe replacement of symbols with backup verification
- **`simulate_refactor`** - Verify behavior preservation before applying changes

### 3. Security Analysis
- **`security_scan`** - Taint-based vulnerability detection (SQL injection, XSS, command injection, etc.)
- **`unified_sink_detect`** - Polyglot sink detection across Python, Java, JavaScript, TypeScript
- **`cross_file_security_scan`** - Track taint flow across file boundaries
- **`scan_dependencies`** - Vulnerable dependency detection (CVE scanning via OSV)

### 4. Testing & Validation
- **`generate_unit_tests`** - Auto-generate test cases from symbolic execution paths
- **`symbolic_execute`** - Explore execution paths and find edge cases
- **`validate_paths`** - Verify path accessibility for Docker deployments

### 5. Infrastructure & Governance
- **`crawl_project`** - Project-wide analysis (Python focus)
- **`verify_policy_integrity`** - Cryptographic verification of governance policies

---

## 🏗️ Architecture

### Transport Protocols
- **stdio** (recommended) - Minimal overhead, works in all environments
- **streamable-http/SSE** - WebSocket alternative for certain integrations

### Language Support
- **Primary:** Python (full AST, symbolic execution, parsing)
- **Secondary:** Java, JavaScript, TypeScript (AST analysis, sinks/sources)
- **Detection:** 10+ languages for lightweight analysis

### Tiered Access Control
- **Community** - Free tier, core tools
- **Pro** - Extended analysis, higher complexity limits
- **Enterprise** - Full feature set, compliance reporting, custom governance

---

## 📦 Installation

### PyPI
```bash
pip install codescalpel
```

### Quick Start with MCP
```bash
# Start the MCP server (stdio transport)
code-scalpel mcp --stdio

# Or HTTP (port 8080)
code-scalpel mcp --http --port 8080
```

### Claude Desktop Integration
```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "code-scalpel",
      "args": ["mcp", "--stdio"]
    }
  }
}
```

---

## 🚀 Typical Workflows

### Security Audit
```bash
# 1. Scan for vulnerabilities
security_scan(code="...")

# 2. Check dependencies for CVEs
scan_dependencies(dependencies=[...])

# 3. Cross-file taint tracking
cross_file_security_scan(entry_point="app.py")
```

### Refactoring
```bash
# 1. Extract the code to refactor
code = extract_code(file_path="src/utils.py", target_name="process_data")

# 2. Modify it locally
new_code = "def process_data(x): return x * 2"

# 3. Verify behavior is preserved
simulate_refactor(original=code, modified=new_code)

# 4. Apply the change
update_symbol(file_path="src/utils.py", new_code=new_code)
```

### Test Generation
```bash
# 1. Analyze code paths
paths = symbolic_execute(code="def divide(a, b): return a / b")

# 2. Generate tests
tests = generate_unit_tests(code="...", symbolic_paths=paths)
```

---

## 🔐 Security

### Taint Analysis
Code Scalpel uses **data flow analysis** to detect vulnerabilities:
- SQL Injection (CWE-89)
- XSS (CWE-79)
- Command Injection (CWE-78)
- Path Traversal (CWE-22)
- NoSQL Injection (CWE-943)
- LDAP Injection (CWE-90)
- XPath Injection (CWE-643)
- Email Injection (CWE-98)
- Regex DoS (CWE-1333)
- Format String (CWE-134)
- Unsafe Reflection (CWE-470)
- Expression Language Injection (CWE-917)
- GraphQL Injection (CWE-1336)
- CORS Misconfiguration
- JWT Attacks
- HTML Injection

### Governance & Compliance
- **Policy Engine** - Enforce coding standards via YAML policies
- **License Scanning** - Detect license compliance issues
- **SBOM Generation** - Software Bill of Materials (CycloneDX)
- **Audit Trail** - Complete governance audit logs

---

## 📊 Test Coverage

- **4,000+ tests** across all modules
- **95%+ code coverage** (statement + branch)
- **CI/CD validated** on Python 3.10-3.13
- **Security audited** (Bandit SAST, pip-audit CVE scan)

---

## 📚 Documentation

### User Guides
- [MCP Integration Guide](../agent_integration.md) - Integrate with Claude, Cursor, etc.
- [Quick Reference](../QUICK_REFERENCE_DOCS.md) - Tool quick lookup
- [Examples](../../examples/) - Runnable code examples

### Architecture
- [System Design](../architecture/) - Component overview
- [Parser Documentation](../parsers/) - Language-specific parsing
- [Policy Engine](../compliance/) - Governance and compliance

### Deployment
- [Docker Setup](../../DOCKER_QUICK_START.md) - Container deployment
- [Kubernetes Guide](../deployment/) - Kubernetes deployment

---

## 🛠️ Local Release Pipeline

Code Scalpel includes a **local CI pipeline** that matches GitHub Actions:

```bash
# Full pipeline with validation
python local_pipeline/pipeline.py --validate-release

# Dry-run publish (before going live)
python local_pipeline/pipeline.py --validate-release --publish --publish-dry-run

# Full release (with PyPI publish + git tag)
python local_pipeline/pipeline.py --validate-release --publish
```

See [LOCAL_PIPELINE_ENHANCEMENTS.md](../../LOCAL_PIPELINE_ENHANCEMENTS.md) for details.

---

## 🔄 Release Candidate Path

This v1.0.0 release is the result of:
- **20+ pre-releases** (v3.0.0 - v3.3.1) with community feedback
- **Comprehensive refactoring** to MCP server model
- **22 production-ready tools** with stable APIs
- **Full test coverage** and security audit

**API Stability:** ✅ All MCP tool signatures are frozen and backward-compatible.

---

## ⚠️ Known Limitations

### v1.0.0 Scope
- Python symbolic execution limited to simple types (Int, Bool, String, Float)
- Complex object types (List, Dict) not yet supported in symbolic execution
- Java/JavaScript analysis is lighter-weight than Python (AST-only, no symbolic execution)

### Planned for Future Releases
- Symbolic execution for complex types (List, Dict, Objects)
- Full Java/JavaScript symbolic execution
- Rust, Go, C++ analysis
- IDE plugins (VS Code, JetBrains)

---

## 🤝 Contributing

Code Scalpel is open source. Contributions welcome!

**Repository:** https://github.com/3D-Tech-Solutions/code-scalpel

**Contributing Guide:** See `CONTRIBUTING.md` in the repository

---

## 📋 Compatibility Matrix

| Component | Status | Tested On |
|-----------|--------|-----------|
| Python | ✅ Stable | 3.10, 3.11, 3.12, 3.13 |
| MCP Protocol | ✅ Stable | v1.0 |
| stdio Transport | ✅ Stable | All platforms |
| HTTP Transport | ✅ Stable | All platforms |
| Claude Integration | ✅ Stable | Claude 3.x |
| Cursor Integration | ✅ Stable | Latest |
| GitHub Actions | ✅ Stable | Latest runner |
| Docker | ✅ Stable | 20.10+ |

---

## 📞 Support

### Issue Reporting
Report bugs: https://github.com/3D-Tech-Solutions/code-scalpel/issues

### Security
Found a vulnerability? Email: `security@3d-tech-solutions.com`

### Documentation
- [Full Documentation Index](../INDEX.md)
- [Comprehensive Guide](../COMPREHENSIVE_GUIDE.md)
- [FAQ](../BEGINNER_FAQ.md)

---

## 📄 License

Code Scalpel is licensed under the **MIT License** - see [LICENSE](../../LICENSE) for details.

**License Types Supported:**
- MIT (Code Scalpel itself)
- Apache 2.0 (compatible)
- GPL v3 (code analysis compatible)
- LGPL (compatible)
- BSD (compatible)

---

## 🎯 Next Steps

### For Users
1. Install: `pip install codescalpel`
2. Integrate with your AI agent (Claude, Cursor, etc.)
3. Run security audits on your code
4. Use for refactoring and testing

### For Contributors
1. Clone: `git clone https://github.com/3D-Tech-Solutions/code-scalpel.git`
2. Install dev deps: `pip install -e '.[dev]'`
3. Run tests: `pytest tests/`
4. Submit PR to main

---

## 🎉 Thank You

Code Scalpel v1.0.0 represents months of development, testing, and refinement. Thank you to:
- Community users who provided feedback during pre-releases
- Open source projects we depend on
- Everyone who contributed to making this possible

**Let's build better code together!** 🚀

---

**Latest Update:** January 19, 2026  
**Version:** 1.0.0 (Stable)  
**Status:** General Availability
