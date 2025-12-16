# Getting Started with Code Scalpel

Welcome to Code Scalpel v2.2.0 "Nexus"! This guide covers installation, configuration, and your first analysis.

## What is Code Scalpel?

Code Scalpel is an **MCP server toolkit** for AI agents (Claude, GitHub Copilot, Cursor) to perform surgical code operations. Instead of stuffing entire files into context, Code Scalpel extracts *exactly* what's needed—saving 99% of tokens while improving accuracy.

**Key Capabilities:**
- **17 MCP Tools** for AI agents via Model Context Protocol
- **4 Languages** - Python, TypeScript, JavaScript, Java (all full support)
- **Security Analysis** - 17+ vulnerability types including SQLi, NoSQL, DOM XSS
- **Symbolic Execution** - Z3-powered path exploration and test generation
- **Cross-File Analysis** - Import resolution and taint tracking across modules
- **Unified Graph Engine** - Cross-language dependency tracking with confidence scoring

---

## Installation

### Option 1: pip (Standard)

```bash
pip install code-scalpel
```

### Option 2: uv (Recommended for MCP)

[uv](https://docs.astral.sh/uv/) is the fastest Python package manager and works seamlessly with MCP:

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run code-scalpel without installing
uvx code-scalpel --help

# Or install globally
uv tool install code-scalpel
```

### Option 3: From Source (Development)

```bash
git clone https://github.com/tescolopio/code-scalpel.git
cd code-scalpel
pip install -e ".[dev]"
```

### Option 4: Docker

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/tescolopio/code-scalpel:2.2.0

# Or build locally
docker build -t code-scalpel .
```

### Optional Dependencies

```bash
# For Autogen integration
pip install code-scalpel[autogen]

# For CrewAI integration  
pip install code-scalpel[crewai]

# For all AI integrations
pip install code-scalpel[all]

# For development (tests, linting)
pip install code-scalpel[dev]
```

---

## Server Configuration by Transport Type

Code Scalpel supports three transport methods:

| Transport | Protocol | Best For |
|-----------|----------|----------|
| **stdio** | Standard I/O | Local AI assistants (Claude Desktop, VS Code, Cursor) |
| **HTTP** | REST/SSE | Remote access, team servers, web integrations |
| **Docker** | HTTP (containerized) | CI/CD, isolated environments, production |

---

### stdio Transport (Local AI Assistants)

The stdio transport communicates via standard input/output streams. This is the **default and recommended** method for local AI assistants.

#### VS Code / GitHub Copilot

1. Create `.vscode/mcp.json` in your project root:

```json
{
  "servers": {
    "code-scalpel": {
      "type": "stdio",
      "command": "uvx",
      "args": ["code-scalpel", "mcp", "--root", "${workspaceFolder}"]
    }
  }
}
```

2. In VS Code: `Ctrl+Shift+P` → "MCP: List Servers"
3. Click "Start" next to code-scalpel
4. Use in Copilot Chat with agent mode (`@workspace`)

**Alternative with pip install:**
```json
{
  "servers": {
    "code-scalpel": {
      "type": "stdio", 
      "command": "python",
      "args": ["-m", "code_scalpel.mcp", "--root", "${workspaceFolder}"]
    }
  }
}
```

#### Claude Desktop

1. Find your config file:
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux:** `~/.config/Claude/claude_desktop_config.json`

2. Add the server configuration:

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp", "--root", "/path/to/your/project"]
    }
  }
}
```

**Windows paths:**
```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp", "--root", "C:\\Users\\you\\Projects\\myapp"]
    }
  }
}
```

3. Restart Claude Desktop
4. Look for the hammer icon indicating tools are available

#### Cursor IDE

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx", 
      "args": ["code-scalpel", "mcp", "--root", "/path/to/project"]
    }
  }
}
```

---

### HTTP Transport (Remote/Team Access)

The HTTP transport runs a web server that accepts MCP requests. Use this for:
- Team-shared analysis servers
- Remote access from web applications
- Integration with custom tools

#### Start HTTP Server

```bash
# Basic HTTP server (localhost only)
code-scalpel mcp --http --port 8593

# Allow LAN access for team use
code-scalpel mcp --http --port 8593 --allow-lan

# With specific project root
code-scalpel mcp --http --port 8593 --root /path/to/project
```

#### Health Check Endpoint

Code Scalpel v2.0.0 includes a health endpoint on port 8594:

```bash
curl http://localhost:8594/health
```

Response:
```json
{
  "status": "healthy",
  "version": "2.0.0", 
  "tools": 18,
  "uptime_seconds": 3600
}
```

#### Connect from VS Code (HTTP)

```json
{
  "servers": {
    "code-scalpel-remote": {
      "type": "http",
      "url": "http://your-server:8593/mcp"
    }
  }
}
```

#### Connect from Claude Desktop (HTTP)

Claude Desktop doesn't natively support HTTP transport. Use a proxy like [mcp-proxy](https://github.com/anthropics/mcp-proxy) or run locally with stdio.

---

### Docker Deployment

Docker provides isolation and reproducibility for CI/CD and production environments.

#### Quick Start

```bash
# Run with project volume mounted
docker run -d \
  --name code-scalpel \
  -p 8593:8593 \
  -p 8594:8594 \
  -v /path/to/project:/project \
  ghcr.io/tescolopio/code-scalpel:2.0.0

# Verify health
curl http://localhost:8594/health

# View logs
docker logs code-scalpel
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  code-scalpel:
    image: ghcr.io/tescolopio/code-scalpel:2.0.0
    ports:
      - "8593:8593"  # MCP server
      - "8594:8594"  # Health endpoint
    volumes:
      - ./:/project:ro  # Mount project read-only
    environment:
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8594/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

Start with:
```bash
docker-compose up -d
```

#### CI/CD Integration (GitHub Actions)

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    services:
      code-scalpel:
        image: ghcr.io/tescolopio/code-scalpel:2.0.0
        ports:
          - 8593:8593
    steps:
      - uses: actions/checkout@v4
      - name: Wait for server
        run: |
          for i in {1..30}; do
            curl -s http://localhost:8594/health && break
            sleep 1
          done
      - name: Run security scan
        run: |
          curl -X POST http://localhost:8593/mcp \
            -H "Content-Type: application/json" \
            -d '{"method": "tools/call", "params": {"name": "security_scan", "arguments": {"file_path": "src/"}}}'
```

---

## CLI Reference

Code Scalpel provides a command-line interface for standalone analysis:

```bash
# Show help
code-scalpel --help

# Analyze code structure
code-scalpel analyze app.py
code-scalpel analyze src/ --json

# Security scan
code-scalpel scan app.py
code-scalpel scan --code "cursor.execute(user_input)"

# Start MCP server (stdio - default)
code-scalpel mcp

# Start MCP server (HTTP)
code-scalpel mcp --http --port 8593

# With project root
code-scalpel mcp --root /path/to/project

# Version info
code-scalpel version
```

---

## Your First Analysis

### Using Python API

```python
from code_scalpel import CodeAnalyzer

analyzer = CodeAnalyzer()

code = """
def calculate_tax(amount, rate=0.1):
    if amount < 0:
        raise ValueError("Amount cannot be negative")
    return amount * rate

def unused_helper():
    pass  # This function is never called

total = calculate_tax(100)
print(total)
"""

result = analyzer.analyze(code)

# View metrics
print(f"Functions: {result.metrics.num_functions}")
print(f"Lines: {result.metrics.lines_of_code}")
print(f"Complexity: {result.metrics.cyclomatic_complexity}")

# Check for dead code
for item in result.dead_code:
    print(f"Dead code: {item.name} - {item.reason}")

# View suggestions
for suggestion in result.refactor_suggestions:
    print(f"Suggestion: {suggestion.description}")
```

### Using CLI

```bash
# Analyze a file
code-scalpel analyze myfile.py

# Output as JSON (for CI/CD)
code-scalpel analyze src/ --json > analysis.json

# Security scan with taint tracking
code-scalpel scan app.py
```

### Using MCP Tools (via AI Assistant)

Once connected to Claude or Copilot, ask:

> "Analyze the security of my Flask app"

The AI will use the `security_scan` tool to detect vulnerabilities:

```
Security Analysis Results:
- SQL Injection (CWE-89) at line 45
  Taint path: request.args['id'] → user_id → query → cursor.execute()
- Hardcoded Secret (AWS Key) at line 12
  Pattern: AKIA... detected in config.py
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CODE_SCALPEL_ROOT` | `.` | Default project root for analysis |
| `CODE_SCALPEL_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `CODE_SCALPEL_CACHE_DIR` | `~/.cache/code-scalpel` | Cache directory for analysis results |
| `CODE_SCALPEL_Z3_TIMEOUT` | `5` | Symbolic execution timeout (seconds) |

---

## Troubleshooting

### Server Won't Start

**Symptom:** `command not found: code-scalpel`

**Solution:** Ensure code-scalpel is installed and in PATH:
```bash
pip install code-scalpel
# Or with uv
uvx code-scalpel --help
```

### VS Code Can't Find Server

**Symptom:** MCP server shows as "Not Started" in VS Code

**Solutions:**
1. Check `.vscode/mcp.json` syntax (valid JSON)
2. Verify `uvx` or `python` is in PATH
3. Try absolute path: `"command": "/usr/local/bin/uvx"`
4. Check Output → MCP for error messages

### Claude Desktop Not Showing Tools

**Symptom:** No hammer icon in Claude Desktop

**Solutions:**
1. Restart Claude Desktop completely
2. Check config file location (varies by OS)
3. Validate JSON syntax: `cat config.json | python -m json.tool`
4. Check Claude logs: Help → Show Logs

### Docker Health Check Failing

**Symptom:** Container exits or health check fails

**Solutions:**
```bash
# Check container logs
docker logs code-scalpel

# Verify port mapping
docker ps

# Test health manually
curl -v http://localhost:8594/health
```

### Analysis Timeout

**Symptom:** Analysis hangs on large files

**Solutions:**
1. Increase Z3 timeout: `CODE_SCALPEL_Z3_TIMEOUT=30`
2. Use `AnalysisLevel.BASIC` for faster results
3. Analyze specific files instead of entire directories

---

## Next Steps

- [API Reference](api_reference.md) - Complete API documentation
- [Agent Integration Guide](agent_integration.md) - Deep dive into AI framework integrations
- [MCP Tools Reference](mcp_tools.md) - All 18 tools explained
- [Security Analysis Guide](security_analysis.md) - Vulnerability detection details
- [Examples](examples.md) - Code samples and use cases

---

## Getting Help

- **GitHub Issues:** [Report bugs](https://github.com/tescolopio/code-scalpel/issues)
- **GitHub Discussions:** [Ask questions](https://github.com/tescolopio/code-scalpel/discussions)
- **Release Notes:** [v2.0.0 Changes](release_notes/RELEASE_NOTES_v2.0.0.md)

---

## License

Code Scalpel is released under the MIT License. See [LICENSE](../LICENSE) for details.

"Code Scalpel" is a trademark of 3D Tech Solutions LLC.
