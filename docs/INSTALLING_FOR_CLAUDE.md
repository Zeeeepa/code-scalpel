# Installing Code Scalpel for Claude

Code Scalpel is an AI-powered code analysis tool available for Claude Desktop, VSCode, and Cursor IDEs. This guide walks you through installation and integration.

---

## Quick Start

The fastest way to use Code Scalpel with Claude:

```bash
uvx codescalpel mcp
```

This installs and configures Code Scalpel for immediate use with Claude Desktop.

---

## Installation Methods

### Method 1: UVX (Recommended for Claude Desktop)

UVX automatically manages the Python environment and dependencies.

```bash
# One-time setup
uvx codescalpel mcp
```

**Benefits**:
- No Python installation required
- Automatic dependency management
- Clean isolation from system Python
- Easiest integration with Claude Desktop

**Requirements**:
- macOS 11+, Linux, or Windows (with WSL2)
- Internet connection for first run

---

### Method 2: PyPI (pip)

For manual installation with pip:

```bash
# Install from PyPI
pip install codescalpel

# Start the MCP server
code-scalpel mcp
```

**Requirements**:
- Python 3.10 or later
- pip package manager
- Existing Python environment

**Optional**: Install with all features
```bash
pip install "code-scalpel[agents,web,polyglot]"
```

---

### Method 3: From Source

For development or latest features:

```bash
# Clone the repository
git clone https://github.com/anthropics/code-scalpel.git
cd code-scalpel

# Install in development mode
pip install -e .

# Start the MCP server
python -m code_scalpel.mcp.protocol
```

---

## Claude Desktop Integration

### Step 1: Access Claude Configuration

Locate your Claude configuration file:

**macOS**:
```bash
~/.config/Claude/claude_desktop_config.json
```

**Linux**:
```bash
~/.config/Claude/claude_desktop_config.json
```

**Windows**:
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

### Step 2: Add Code Scalpel to Configuration

Add Code Scalpel to the `mcpServers` section:

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp"]
    }
  }
}
```

**Alternative** (if using local installation):
```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "python",
      "args": ["-m", "code_scalpel.mcp.protocol"]
    }
  }
}
```

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop to activate Code Scalpel.

### Step 4: Verify Installation

In Claude Desktop, try this prompt:

```
Please analyze this Python code for me:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

Claude should respond with Code Scalpel tool availability and analysis results.

---

## VSCode / Cursor Integration

### Step 1: Install Code Scalpel

```bash
pip install codescalpel
```

Or use UVX:
```bash
uvx codescalpel mcp
```

### Step 2: Install Claude Extension

In VSCode or Cursor, install the [Claude Extension](https://marketplace.visualstudio.com/items?itemName=Anthropic.claude-vsx).

### Step 3: Configure MCP Server

Open VSCode settings and add Code Scalpel to MCP servers:

**VSCode Settings** (`settings.json`):
```json
{
  "claude.mcp.servers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp"]
    }
  }
}
```

**Cursor Settings** (similar configuration via Cursor Settings UI)

### Step 4: Reload VSCode/Cursor

Reload the IDE to activate Code Scalpel integration.

### Step 5: Use in Chat

Open the Claude chat panel and ask for code analysis:

```
Analyze this file for security issues: src/app.py
```

---

## Docker Integration (Advanced)

For containerized environments:

```dockerfile
FROM python:3.11-slim

RUN pip install codescalpel

EXPOSE 8080

CMD ["code-scalpel", "mcp"]
```

Build and run:
```bash
docker build -t code-scalpel .
docker run -p 8080:8080 code-scalpel
```

Configure Claude to connect:
```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "curl",
      "args": ["http://localhost:8080"]
    }
  }
}
```

---

## Troubleshooting

### Issue: "command not found: uvx"

**Solution**: Install UVX first
```bash
pip install uvx
```

Or use standard Python:
```bash
python -m code_scalpel.mcp.protocol
```

---

### Issue: "No module named code_scalpel"

**Solution**: Install the package
```bash
pip install codescalpel
```

Verify installation:
```bash
python -c "import code_scalpel; print(code_scalpel.__version__)"
```

---

### Issue: Claude doesn't see Code Scalpel

**Solution**:
1. Verify configuration file syntax (JSON is strict)
2. Restart Claude Desktop completely
3. Check error logs:
   - **macOS**: `~/Library/Logs/Claude/`
   - **Linux**: `~/.local/share/Claude/logs/`

---

### Issue: "Connection refused" or timeout

**Solution**:
1. Verify the MCP server is running:
   ```bash
   python -m code_scalpel.mcp.protocol --port 8080
   ```
2. Check if port 8080 is available
3. Try a different port in configuration

---

### Issue: Memory or performance problems

**Solution**: Code Scalpel respects tier-based limits:

- **Community**: 100 files, depth=3, 1 MB file size
- **Pro**: unlimited files, depth=50, 10 MB file size
- **Enterprise**: unlimited, 100 MB file size

Contact support to upgrade tier if hitting limits.

---

### Issue: "Permission denied" on macOS/Linux

**Solution**: Make the script executable
```bash
chmod +x ~/.local/bin/code-scalpel
```

Or use Python directly:
```bash
python -m code_scalpel.mcp.protocol
```

---

## Configuration Options

### Environment Variables

Control Code Scalpel behavior via environment variables:

```bash
# Set default tier
export CODE_SCALPEL_TIER=pro

# Enable debug logging
export CODE_SCALPEL_DEBUG=1

# Set custom limits
export CODE_SCALPEL_MAX_FILES=500

# Start the server
uvx codescalpel mcp
```

### Configuration File

Create `~/.code-scalpel/config.toml`:

```toml
[governance]
tier = "pro"
enable_caching = true
cache_ttl_seconds = 3600

[limits]
max_file_size_mb = 10
max_depth = 50
timeout_seconds = 120

[features]
enable_polyglot = true
enable_symbolic_execution = true
```

---

## Advanced: Multiple MCP Servers

If you have multiple MCP servers configured:

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "uvx",
      "args": ["code-scalpel", "mcp"]
    },
    "other-server": {
      "command": "uvx",
      "args": ["other-server", "start"]
    }
  }
}
```

Claude will automatically detect and use all available tools.

---

## Verification Checklist

After installation, verify everything works:

- [ ] Installation command completed without errors
- [ ] `python -c "import code_scalpel; print(code_scalpel.__version__)"` shows v1.0.1+
- [ ] Configuration file is valid JSON
- [ ] Claude Desktop/VSCode recognizes Code Scalpel tool
- [ ] Can analyze code samples through Claude
- [ ] Results include complexity metrics and recommendations

---

## Next Steps

Once installed, you can:

1. **Analyze Code**: Ask Claude to analyze Python, JavaScript, TypeScript, or Java code
2. **Find Issues**: Request security analysis and bug detection
3. **Extract Symbols**: Get precise extraction of functions, classes, and methods
4. **Refactor Safely**: Simulate refactorings and validate changes
5. **Generate Tests**: Create unit tests from code analysis

Example prompts:
```
"Find security vulnerabilities in src/auth.py"
"Generate unit tests for the login function"
"Refactor this code to use async/await"
"Extract the payment processing logic and explain it"
```

---

## Support & Documentation

- **GitHub**: https://github.com/anthropics/code-scalpel
- **Issues**: https://github.com/anthropics/code-scalpel/issues
- **README**: https://github.com/anthropics/code-scalpel#readme
- **Main Docs**: [docs/](../README.md)

---

## FAQ

**Q: Is Code Scalpel free?**
A: Yes! Community tier is always free. Pro and Enterprise tiers available for advanced features.

**Q: Does Code Scalpel send my code to the internet?**
A: No. Code Scalpel runs locally on your machine and analyzes code offline (except for optional cloud features in Enterprise tier).

**Q: Which languages are supported?**
A: Python (full support), JavaScript/TypeScript/Java (basic support), with polyglot mode for extended language coverage.

**Q: Can I use Code Scalpel offline?**
A: Yes, fully offline with local installation. UVX requires internet for first-time setup only.

**Q: How do I upgrade my tier?**
A: Configure via environment variables or config file. Enterprise users should contact support.

**Q: Is there a CLI tool?**
A: Yes! Use `codescalpel` command:
```bash
code-scalpel analyze /path/to/code.py
code-scalpel extract MyClass /path/to/file.py
```

---

**Version**: v1.0.1
**Last Updated**: 2025-01-25
