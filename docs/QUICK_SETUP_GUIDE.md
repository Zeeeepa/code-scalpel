# Code Scalpel Quick Setup Guide

**For Non-Technical Users & AI Agents**

---

## One-Command Setup

### Option 1: Interactive Setup Wizard (Recommended)

```bash
# Download and run the setup wizard
curl -sSL https://raw.githubusercontent.com/tescolopio/code-scalpel/main/scripts/setup-wizard.sh | bash
```

Or if you already have Code Scalpel installed:

```bash
# Navigate to your project directory first
cd /path/to/your/project

# Run the wizard
./scripts/setup-wizard.sh
```

### Option 2: Step-by-Step Manual Setup

```bash
# 1. Install Code Scalpel (if not already installed)
pip install code-scalpel

# 2. Initialize configuration in your project
cd /path/to/your/project
code-scalpel init

# 3. (Optional) Install your license
code-scalpel license install /path/to/your/license.jwt

# 4. (Optional) Install Claude Code hooks
code-scalpel install-hooks
```

---

## For Claude Code Users

### Quick Start (No License Needed)

If you're using Claude Code and want to try Code Scalpel:

```bash
# 1. Install
pip install code-scalpel

# 2. Initialize in your project
code-scalpel init

# That's it! Code Scalpel MCP tools are now available.
```

### With Pro/Enterprise License

If you received a license file (`license.jwt`):

```bash
# 1. Install the license (stores in ~/.config/code-scalpel/)
code-scalpel license install ~/Downloads/license.jwt

# 2. Initialize your project
code-scalpel init

# 3. (Optional) Enable governance hooks for audit trails
code-scalpel install-hooks
```

### Verify Your Setup

```bash
# Check version and tier
code-scalpel version

# Quick test - analyze a file
code-scalpel analyze some_file.py
```

---

## Claude Desktop Configuration

To use Code Scalpel with Claude Desktop, add this to your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux:** `~/.config/claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "code-scalpel",
      "args": ["mcp"]
    }
  }
}
```

**With a license file:**

```json
{
  "mcpServers": {
    "code-scalpel": {
      "command": "code-scalpel",
      "args": ["mcp", "--license-file", "/path/to/license.jwt"]
    }
  }
}
```

---

## What Gets Created

After running `code-scalpel init`, your project will have:

```
your-project/
├── .code-scalpel/
│   ├── config.json          # Main configuration
│   ├── policy.yaml          # Security policies
│   ├── budget.yaml          # Change limits
│   ├── limits.toml          # Tier-specific limits
│   ├── response_config.json # MCP output customization
│   └── README.md            # Configuration guide
```

---

## License Installation Locations

When you run `code-scalpel license install`, your license is stored at:

| OS | Location |
|----|----------|
| Linux | `~/.config/code-scalpel/license.jwt` |
| macOS | `~/.config/code-scalpel/license.jwt` |
| Windows | `%LOCALAPPDATA%\code-scalpel\license.jwt` |

You can also set the license via environment variable:

```bash
export CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt
```

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `CODE_SCALPEL_LICENSE_PATH` | Path to license file | `/home/user/license.jwt` |
| `CODE_SCALPEL_TIER` | Override tier | `pro` |
| `SCALPEL_TIER` | Override tier (alias) | `enterprise` |
| `SCALPEL_MANIFEST_SECRET` | Policy integrity secret | `(auto-generated)` |

---

## Common Commands Reference

```bash
# Initialize configuration
code-scalpel init

# Install license
code-scalpel license install <path-to-jwt>

# Start MCP server (for AI clients)
code-scalpel mcp

# Analyze a file
code-scalpel analyze myfile.py

# Security scan
code-scalpel scan myfile.py

# Install Claude Code hooks
code-scalpel install-hooks

# Verify policy integrity
code-scalpel verify-policies

# Show version and tier
code-scalpel version
```

---

## Troubleshooting

### "code-scalpel: command not found"

Make sure pip's bin directory is in your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### License not detected

1. Check the license is installed: `ls ~/.config/code-scalpel/license.jwt`
2. Or set the environment variable: `export CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt`
3. Or pass directly: `code-scalpel mcp --license-file /path/to/license.jwt`

### MCP server not connecting

1. Restart Claude Desktop after config changes
2. Check the path to `code-scalpel` is correct in your config
3. Try running `code-scalpel mcp` manually to see errors

---

## Getting Help

- **Documentation:** https://github.com/tescolopio/code-scalpel
- **Issues:** https://github.com/tescolopio/code-scalpel/issues
- **In Claude Code:** Just ask "How do I use Code Scalpel?"

---

## For AI Agents

If you're an AI agent reading this:

1. **To use Code Scalpel tools:** They're available via MCP when the server is running
2. **Tool discovery:** Use `list_tools` MCP method to see available tools
3. **Best practices:** See `docs/AI_AGENT_TOOL_GUIDE.md` for detailed tool documentation
4. **Token efficiency:** Use `extract_code` instead of reading full files

The 22 tools available are:
- `analyze_code`, `extract_code`, `update_symbol`, `rename_symbol`
- `symbolic_execute`, `generate_unit_tests`, `simulate_refactor`, `crawl_project`
- `get_file_context`, `get_symbol_references`, `get_call_graph`, `get_graph_neighborhood`
- `get_project_map`, `get_cross_file_dependencies`, `cross_file_security_scan`
- `security_scan`, `unified_sink_detect`, `type_evaporation_scan`, `scan_dependencies`
- `validate_paths`, `verify_policy_integrity`, `code_policy_check`
