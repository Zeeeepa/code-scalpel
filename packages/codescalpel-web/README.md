# Code Scalpel Web

REST API and web framework integrations for Code Scalpel MCP server.

## Installation

```bash
pip install codescalpel-web
```

## Quick Start

```bash
# Run the REST API server
codescalpel-web --host 0.0.0.0 --port 8000
```

## Features

- **Flask REST API**: HTTP/HTTPS interface to all Code Scalpel tools
- **MCP Bridge**: Bridges Code Scalpel MCP protocol to REST
- **Framework Support**: Works with Flask, and can be extended for other frameworks

## Requires

- `codescalpel>=1.0.2` (core analysis engine)
- `flask>=2.0.0` for REST API server

## License

MIT
