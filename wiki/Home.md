# Code Scalpel Wiki

**Welcome to the Code Scalpel documentation!**

Code Scalpel is an MCP (Model Context Protocol) server that provides AI agents with surgical precision for code analysis, security scanning, and safe refactoring.

## 🚀 Quick Links

### Getting Started
- **[Installation](Installation)** - Setup and deployment options
- **[Getting Started](Getting-Started)** - Your first Code Scalpel operations
- **[Configuration](Configuration)** - Environment variables and settings

### Core Documentation
- **[MCP Tools Reference](MCP-Tools-Reference)** - Complete tool documentation (22 tools)
- **[Architecture](Architecture)** - Tier system, components, design decisions
- **[Security](Security)** - Policy checking and integrity verification

### Learning & Support
- **[Examples](Examples)** - Code examples and tutorials
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions
- **[Contributing](Contributing)** - Development setup and guidelines
- **[Changelog](Changelog)** - Version history and updates

## What is Code Scalpel?

Code Scalpel bridges **Generative AI** and **Reliable Software Engineering** by treating code as a **Graph** (AST + PDG) rather than text. It provides 22 specialized tools that enable AI agents to:

- 🔍 **Extract code surgically** - Get functions/classes by name without reading entire files
- 🛡️ **Detect vulnerabilities** - Taint-based security analysis across 12+ CWEs
- ✅ **Verify changes** - Simulate refactors before applying them
- 🧪 **Generate tests** - Auto-create unit tests using symbolic execution
- 🔄 **Refactor safely** - Rename symbols and update code with atomic operations

## Key Capabilities

### 1. Surgical Extraction (99% Token Reduction)
```python
# Instead of reading entire files
extract_code(file_path="services.py", target_type="function", target_name="process_payment")
```

### 2. Taint-Based Security Analysis
```python
# Detect SQL injection, XSS, command injection, etc.
security_scan(code=source_code, entry_points=["handle_request"])
```

### 3. Symbolic Execution & Test Generation
```python
# Explore all execution paths and generate tests
generate_unit_tests(code=function_code, max_paths=10)
```

### 4. Safe Refactoring
```python
# Verify changes before applying
simulate_refactor(original_code=old_code, new_code=new_code)
update_symbol(file_path="app.py", target_name="old_func", new_code=new_func)
```

## Tier System

Code Scalpel offers three tiers:

| Tier | License | Use Case |
|------|---------|----------|
| **Community** | MIT (Free) | Personal projects, learning, open source |
| **Pro** | Commercial | Professional development, unlimited findings |
| **Enterprise** | Commercial | Teams, compliance reporting, audit trails |

**All 22 tools are available in the Community tier!** Higher tiers provide enhanced limits and enterprise features.

## Supported Languages

- **Python** - Full support (AST + PDG + symbolic execution)
- **JavaScript/TypeScript** - AST analysis, call graphs, extraction
- **Java** - AST parsing and analysis
- **Go, Rust, Ruby, PHP** - AST parsing via tree-sitter

## MCP Transports

Code Scalpel works with all major AI coding assistants:

- ✅ **VS Code** (stdio)
- ✅ **GitHub Copilot** (stdio)
- ✅ **Claude Desktop** (stdio)
- ✅ **Cursor** (stdio)
- ✅ **HTTP/SSE** - Remote deployments
- ✅ **Docker** - Containerized environments

## Community & Support

- **GitHub Repository**: [3D-Tech-Solutions/code-scalpel](https://github.com/3D-Tech-Solutions/code-scalpel)
- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Community Q&A and announcements
- **Security**: See [Security Policy](Security) for vulnerability reporting

---

**Ready to get started?** → [Installation Guide](Installation)
