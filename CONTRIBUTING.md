# Contributing to Code Scalpel

Thank you for your interest in contributing to Code Scalpel! This document provides guidelines and information for contributors.

---

## Project Overview

**Code Scalpel** is a production-ready AI code analysis toolkit with Model Context Protocol (MCP) support for AI coding assistants.

**What Code Scalpel is:**
- Python library installable via pip
- MCP (Model Context Protocol) server for AI coding assistants
- Integration layer for AI frameworks (Autogen, CrewAI, LangChain)
- Code analysis engine (AST, PDG, Symbolic Execution, Governance)

**Target Users:**
- AI Coding Assistants (Cursor, Cline, Claude Desktop)
- AI Agent Frameworks (Autogen, CrewAI, LangChain)
- DevOps/CI/CD Pipelines
- Developers building AI-powered code analysis tools

---

## Quick Start

### 1. Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/tescolopio/code-scalpel.git
cd code-scalpel

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Initialize configuration
code-scalpel init
```

### 2. Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=code_scalpel --cov-report=html

# Run specific test file
pytest tests/test_ast_tools.py -v
```

### 3. Check Code Quality

```bash
# Lint with ruff
ruff check src/

# Format code
ruff format src/

# Type checking
mypy src/code_scalpel/
```

---

## Development Workflow

### 1. Create an Issue

Before starting work, create or find an issue:
- Check existing issues for duplicates
- Use issue templates (.github/ISSUE_TEMPLATE/)
- Add appropriate labels (bug, feature, documentation)
- Link to relevant projects/milestones

### 2. Create a Branch

```bash
# Feature branch
git checkout -b feature/your-feature-name

# Bug fix branch
git checkout -b fix/bug-description

# Documentation branch
git checkout -b docs/documentation-update
```

### 3. Make Changes

- Follow existing code style (PEP 8)
- Add tests for new functionality (aim for ≥90% coverage)
- Update documentation as needed
- Keep commits focused and atomic

### 4. Run Quality Checks

```bash
# Run all checks
./scripts/check_quality.sh

# Or manually:
pytest tests/
ruff check src/
mypy src/code_scalpel/
```

### 5. Commit Changes

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add symbolic execution for loops
fix: correct PDG edge direction
docs: update policy engine guide
test: add coverage for governance system
chore: update dependencies
refactor: simplify AST visitor pattern
perf: optimize cache lookup
```

### 6. Submit Pull Request

- Reference related issues (#123)
- Describe changes clearly
- Include test results
- Request review from maintainers

---

## Code Structure

```
code-scalpel/
├── src/code_scalpel/           # Main package
│   ├── ast_tools/              # AST parsing and analysis
│   ├── pdg_tools/              # Program dependence graphs
│   ├── symbolic_execution/     # Path exploration, constraint solving
│   ├── policy_engine/          # OPA/Rego policy enforcement
│   ├── policy/                 # Change budgets, blast radius control
│   ├── governance/             # Unified governance orchestration
│   ├── integrations/           # AI framework connectors
│   └── mcp_server/             # Model Context Protocol server
├── tests/                      # Test suite (4367+ tests)
├── docs/                       # Documentation
├── examples/                   # Usage examples
└── .code-scalpel/              # Runtime configuration
```

---

## Testing Guidelines

### Test Organization

- `tests/test_*.py` - Unit tests for corresponding modules
- `tests/integration/` - Integration tests
- `tests/fixtures/` - Test data and fixtures

### Writing Tests

```python
import pytest
from code_scalpel.ast_tools import PythonParser

def test_parse_simple_function():
    """Test parsing a simple Python function."""
    code = "def foo(): return 42"
    parser = PythonParser()
    ast = parser.parse(code)
    assert ast is not None
    assert ast.body[0].name == "foo"

@pytest.mark.slow
def test_large_codebase():
    """Test parsing large codebases (marked as slow)."""
    # ... test code
```

### Coverage Requirements

- Minimum coverage: **90%** (statement + branch)
- Current coverage: **94.86%**
- Tests must pass before merging

---

## Documentation Guidelines

### Code Documentation

- Docstrings for all public classes, methods, and functions
- Use Google-style docstrings:

```python
def analyze_code(code: str, language: str = "python") -> dict:
    """Analyze source code and return metrics.
    
    Args:
        code: Source code string to analyze
        language: Programming language (default: python)
        
    Returns:
        Dictionary with analysis results including:
        - ast: Abstract syntax tree
        - metrics: Code metrics
        - issues: Detected issues
        
    Raises:
        ParseError: If code cannot be parsed
        
    Example:
        >>> result = analyze_code("def foo(): pass")
        >>> print(result['metrics']['functions'])
        1
    """
```

### User Documentation

- Module READMEs in module directories
- Guides in `docs/` directory
- Examples in `examples/` directory
- Keep `docs/INDEX.md` updated

---

## Architecture Decisions

We use Architecture Decision Records (ADRs) for significant decisions:

- Location: `docs/adr/`
- Format: `ADR-XXX-title.md`
- See existing ADRs for examples

When to create an ADR:
- Major architectural changes
- Technology selection
- Security model decisions
- API design choices

---

## Governance & Security

### Policy Engine

Code Scalpel includes enterprise governance:
- **Policy Engine** - OPA/Rego declarative policies
- **Change Budgets** - Quantitative limits on modifications
- **Semantic Analysis** - Security vulnerability detection
- **Compliance Reporting** - Audit trails and metrics

See [Policy Engine README](src/code_scalpel/policy_engine/README.md) for details.

### Development Governance

When contributing, follow development policies in `.code-scalpel/dev-governance.yaml`:
- Place READMEs in module directories
- Respect module boundaries
- Add tests for new features
- Never commit secrets
- Update backlog on task completion

### Security

- **NO SECRETS** in code or commits
- Use environment variables for credentials
- Follow OWASP Top 10 guidelines
- Report security issues privately (see SECURITY.md)

---

## Release Process

### Version Numbers

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Update documentation
5. Create release notes in `docs/release_notes/`
6. Tag release: `git tag v3.x.x`
7. Build and publish to PyPI

---

## Community

### Code of Conduct

Be respectful, inclusive, and collaborative. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

### Communication Channels

- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - Questions, ideas, general discussion
- **Pull Requests** - Code review and collaboration

### Getting Help

- Check [docs/INDEX.md](docs/INDEX.md) for documentation
- Search existing issues
- Ask in GitHub Discussions
- Tag maintainers in PRs for review

---

## Areas Needing Contribution

### High Priority

- [ ] Additional language parsers (Java, C++, Rust)
- [ ] Performance optimization for large codebases
- [ ] Integration tests for MCP server
- [ ] Documentation and tutorials
- [ ] Security vulnerability patterns

### Medium Priority

- [ ] GitHub Actions workflow improvements
- [ ] Docker deployment enhancements
- [ ] CLI tool improvements
- [ ] Additional compliance frameworks (GDPR, HIPAA)

### Good First Issues

Look for issues labeled `good-first-issue`:
- Documentation improvements
- Test coverage expansion
- Example code and demos
- Bug fixes with reproduction steps

---

## Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` (if created)
- Release notes
- Git commit history

Thank you for helping make Code Scalpel better! 🎉

---

**Resources:**
- [Documentation Index](docs/INDEX.md)
- [Getting Started Guide](docs/getting_started.md)
- [Policy Engine Guide](src/code_scalpel/policy_engine/README.md)
- [Development Roadmap](DEVELOPMENT_ROADMAP.md)

**Last Updated:** December 21, 2025
