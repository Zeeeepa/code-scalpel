"""
Code Scalpel CLI - Command-line interface for code analysis.

Usage:
    code-scalpel analyze <file>           Analyze a Python file
    code-scalpel analyze --code "..."     Analyze code string
    code-scalpel scan <file>              Security vulnerability scan
    code-scalpel mcp                      Start MCP server (for AI clients)
    code-scalpel server [--port PORT]     Start REST API server (legacy)
    code-scalpel version                  Show version

TODO: CLI Enhancement Roadmap
=============================

Phase 1 - Multi-Language Analysis via code_parsers:
- TODO: Integrate code_parsers.ParserFactory for unified language handling
- TODO: Replace manual extension_map with ParserFactory.detect_language()
- TODO: Add --parser flag to select specific parser backend (ast, ruff, mypy)
- TODO: Support all languages in code_parsers (Go, C#, Ruby, Swift, PHP, Kotlin)
- TODO: Add analyze subcommand for TypeScript with full type checking
- TODO: Use code_parsers.ParseResult for consistent error/warning format

Phase 2 - New CLI Commands:
- TODO: Add 'extract' command for surgical extraction (code-scalpel extract func main.py::calculate)
- TODO: Add 'patch' command for surgical patching (code-scalpel patch func main.py::calculate new_code.py)
- TODO: Add 'diff' command to show symbol-level diffs between versions
- TODO: Add 'refactor' command for automated refactoring operations
- TODO: Add 'crawl' command to analyze entire project structure
- TODO: Add 'symbols' command to list all extractable symbols in a file

Phase 3 - Output Formats & Reporting:
- TODO: Add --format markdown for documentation generation
- TODO: Add --format sarif for GitHub code scanning integration
- TODO: Add --format csv for spreadsheet analysis
- TODO: Add --quiet mode for CI/CD pipelines (exit codes only)
- TODO: Add --verbose mode with detailed progress output
- TODO: Support streaming JSON output for large projects

Phase 4 - Configuration & Profiles:
- TODO: Add --profile flag to load predefined configurations (strict, lenient, security)
- TODO: Support .code-scalpel/cli.yaml for persistent CLI defaults
- TODO: Add --ignore flag to skip specific files/patterns
- TODO: Add --include flag for explicit file selection
- TODO: Support reading file lists from stdin (find . -name '*.py' | code-scalpel analyze -)

Phase 5 - Watch Mode & Incremental Analysis:
- TODO: Add --watch flag for continuous file monitoring
- TODO: Implement incremental analysis (only re-analyze changed files)
- TODO: Add --cache flag to persist analysis results between runs
- TODO: Support LSP-style diagnostics output for editor integration

Phase 6 - Batch & Parallel Processing:
- TODO: Add --parallel flag for multi-core analysis
- TODO: Add --batch flag to process multiple files from a manifest
- TODO: Implement progress bars for long-running operations
- TODO: Add --timeout flag to limit analysis time per file

Phase 7 - Integration Commands:
- TODO: Add 'mcp tools' command to list available MCP tools
- TODO: Add 'mcp test' command to verify MCP server functionality
- TODO: Add 'config show' command to display current configuration
- TODO: Add 'config validate' command to check configuration files
"""

import argparse
import json
import sys
from pathlib import Path


def analyze_file(
    filepath: str, output_format: str = "text", language: str | None = None
) -> int:
    """Analyze a file and print results."""

    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    # [20251219_BUGFIX] v3.0.4 - Extended language detection for TS/JSX/TSX
    if language is None:
        ext = path.suffix.lower()
        extension_map = {
            ".py": "python",
            ".pyw": "python",
            ".js": "javascript",
            ".mjs": "javascript",
            ".cjs": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".mts": "typescript",
            ".cts": "typescript",
            ".java": "java",
        }
        if ext in extension_map:
            language = extension_map[ext]
        else:
            print(
                f"Warning: Unknown extension {path.suffix}, defaulting to Python",
                file=sys.stderr,
            )
            language = "python"

    try:
        code = path.read_text(encoding="utf-8")
        # [20251219_BUGFIX] v3.0.4 - Strip UTF-8 BOM if present
        if code.startswith("\ufeff"):
            code = code[1:]
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    return analyze_code(code, output_format, filepath, language)


def _analyze_javascript(code: str, output_format: str, source: str) -> int:
    """Analyze JavaScript code using SymbolicAnalyzer."""
    from .symbolic_execution_tools import SymbolicAnalyzer

    analyzer = SymbolicAnalyzer()
    try:
        result = analyzer.analyze(code, language="javascript")
    except Exception as e:
        print(f"Error analyzing JavaScript code: {e}", file=sys.stderr)
        return 1

    if output_format == "json":
        output = {
            "source": source,
            "language": "javascript",
            "success": True,
            "paths": [
                {
                    "id": p.path_id,
                    "status": p.status.value,
                    "model": p.model,
                }
                for p in result.paths
            ],
            "feasible_count": result.feasible_count,
            "infeasible_count": result.infeasible_count,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nCode Scalpel Analysis (JavaScript): {source}")
        print("=" * 60)
        print(f"Feasible paths: {result.feasible_count}")
        print(f"Infeasible paths: {result.infeasible_count}")
        print("-" * 60)
        for p in result.get_feasible_paths():
            print(f"Path {p.path_id}: {p.status.value}")
            if p.model:
                print(f"  Model: {p.model}")

    return 0


def _analyze_java(code: str, output_format: str, source: str) -> int:
    """Analyze Java code using SymbolicAnalyzer."""
    from .symbolic_execution_tools import SymbolicAnalyzer

    analyzer = SymbolicAnalyzer()
    try:
        result = analyzer.analyze(code, language="java")
    except Exception as e:
        print(f"Error analyzing Java code: {e}", file=sys.stderr)
        return 1

    if output_format == "json":
        output = {
            "source": source,
            "language": "java",
            "success": True,
            "paths": [
                {
                    "id": p.path_id,
                    "status": p.status.value,
                    "model": p.model,
                }
                for p in result.paths
            ],
            "feasible_count": result.feasible_count,
            "infeasible_count": result.infeasible_count,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nCode Scalpel Analysis (Java): {source}")
        print("=" * 60)
        print(f"Feasible paths: {result.feasible_count}")
        print(f"Infeasible paths: {result.infeasible_count}")
        print("-" * 60)
        for p in result.get_feasible_paths():
            print(f"Path {p.path_id}: {p.status.value}")
            if p.model:
                print(f"  Model: {p.model}")

    return 0


def analyze_code(
    code: str,
    output_format: str = "text",
    source: str = "<string>",
    language: str = "python",
) -> int:
    """Analyze code string and print results."""
    if language == "javascript":
        return _analyze_javascript(code, output_format, source)
    if language == "java":
        return _analyze_java(code, output_format, source)

    from .code_analyzer import AnalysisLevel, CodeAnalyzer

    analyzer = CodeAnalyzer(level=AnalysisLevel.STANDARD)

    try:
        result = analyzer.analyze(code)
    except Exception as e:
        print(f"Error analyzing code: {e}", file=sys.stderr)
        return 1

    if output_format == "json":
        output = {
            "source": source,
            "success": not result.errors,
            "metrics": {
                "lines_of_code": result.metrics.lines_of_code,
                "num_functions": result.metrics.num_functions,
                "num_classes": result.metrics.num_classes,
                "cyclomatic_complexity": result.metrics.cyclomatic_complexity,
                "analysis_time_seconds": result.metrics.analysis_time_seconds,
            },
            "dead_code": [
                {
                    "name": dc.name,
                    "type": dc.code_type,
                    "line_start": dc.line_start,
                    "line_end": dc.line_end,
                    "reason": dc.reason,
                }
                for dc in result.dead_code
            ],
            "security_issues": result.security_issues,
            "suggestions": [
                {
                    "type": s.refactor_type,
                    "description": s.description,
                    "priority": s.priority,
                }
                for s in result.refactor_suggestions
            ],
            "errors": result.errors,
        }
        print(json.dumps(output, indent=2))
    else:
        # Text format
        print(f"\nCode Scalpel Analysis: {source}")
        print("=" * 60)

        print("\nMetrics:")
        print(f"   Lines of code: {result.metrics.lines_of_code}")
        print(f"   Functions: {result.metrics.num_functions}")
        print(f"   Classes: {result.metrics.num_classes}")
        print(f"   Cyclomatic complexity: {result.metrics.cyclomatic_complexity}")
        print(f"   Analysis time: {result.metrics.analysis_time_seconds:.3f}s")

        if result.dead_code:
            print(f"\nDead Code Detected ({len(result.dead_code)} items):")
            for dc in result.dead_code:
                print(
                    f"   - {dc.code_type} '{dc.name}' (lines {dc.line_start}-{dc.line_end})"
                )
                print(f"     Reason: {dc.reason}")

        if result.security_issues:
            print(f"\n[WARNING] Security Issues ({len(result.security_issues)}):")
            for issue in result.security_issues:
                print(
                    f"   - {issue.get('type', 'Unknown')}: {issue.get('description', 'No description')}"
                )

        if result.refactor_suggestions:
            print(f"\nSuggestions ({len(result.refactor_suggestions)}):")
            for s in result.refactor_suggestions[:5]:  # Show top 5
                print(f"   - [{s.refactor_type}] {s.description}")

        if result.errors:
            print("\n[ERROR] Errors:")
            for err in result.errors:
                print(f"   - {err}")

        print()

    return 0 if not result.errors else 1


def scan_security(filepath: str, output_format: str = "text") -> int:
    """Scan a file for security vulnerabilities using taint analysis."""
    from .symbolic_execution_tools import analyze_security

    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    try:
        code = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    try:
        result = analyze_security(code)
    except Exception as e:
        print(f"Error during security analysis: {e}", file=sys.stderr)
        return 1

    if output_format == "json":
        output = {
            "source": str(filepath),
            "has_vulnerabilities": result.has_vulnerabilities,
            "vulnerability_count": result.vulnerability_count,
            "vulnerabilities": [
                {
                    "type": v.vulnerability_type,
                    "cwe": v.cwe_id,
                    "source": v.taint_source.name,
                    "sink": v.sink_type.name,
                    "line": v.sink_location[0] if v.sink_location else None,
                    "taint_path": v.taint_path,
                }
                for v in result.vulnerabilities
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nCode Scalpel Security Scan: {filepath}")
        print("=" * 60)

        if not result.has_vulnerabilities:
            print("\n[OK] No vulnerabilities detected.")
        else:
            print(
                f"\n[WARNING] Found {result.vulnerability_count} vulnerability(ies):\n"
            )
            for i, v in enumerate(result.vulnerabilities, 1):
                print(f"  {i}. {v.vulnerability_type} ({v.cwe_id})")
                print(f"     Source: {v.taint_source.name}")
                print(f"     Sink: {v.sink_type.name}")
                if v.sink_location:
                    print(f"     Line: {v.sink_location[0]}")
                print(f"     Taint Path: {' -> '.join(v.taint_path)}")
                print()

        print(result.summary())

    return 0 if not result.has_vulnerabilities else 2


def scan_code_security(code: str, output_format: str = "text") -> int:
    """Scan code string for security vulnerabilities."""
    from .symbolic_execution_tools import analyze_security

    try:
        result = analyze_security(code)
    except Exception as e:
        print(f"Error during security analysis: {e}", file=sys.stderr)
        return 1

    if output_format == "json":
        output = {
            "source": "<string>",
            "has_vulnerabilities": result.has_vulnerabilities,
            "vulnerability_count": result.vulnerability_count,
            "vulnerabilities": [
                {
                    "type": v.vulnerability_type,
                    "cwe": v.cwe_id,
                    "source": v.taint_source.name,
                    "sink": v.sink_type.name,
                    "line": v.sink_location[0] if v.sink_location else None,
                    "taint_path": v.taint_path,
                }
                for v in result.vulnerabilities
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print("\nCode Scalpel Security Scan: <string>")
        print("=" * 60)

        if not result.has_vulnerabilities:
            print("\n[OK] No vulnerabilities detected.")
        else:
            print(
                f"\n[WARNING] Found {result.vulnerability_count} vulnerability(ies):\n"
            )
            for i, v in enumerate(result.vulnerabilities, 1):
                print(f"  {i}. {v.vulnerability_type} ({v.cwe_id})")
                print(f"     Source: {v.taint_source.name}")
                print(f"     Sink: {v.sink_type.name}")
                if v.sink_location:
                    print(f"     Line: {v.sink_location[0]}")
                print(f"     Taint Path: {' -> '.join(v.taint_path)}")
                print()

        print(result.summary())

    return 0 if not result.has_vulnerabilities else 2


def init_configuration(target_dir: str = ".", force: bool = False) -> int:
    """Initialize .code-scalpel configuration directory.

    [20251219_FEATURE] v3.0.2 - Auto-initialize configuration for first-time users.
    Creates .code-scalpel/ with config.json, policy.yaml, budget.yaml, README.md, .gitignore.
    """
    from .config import init_config_dir

    print("Code Scalpel Configuration Initialization")
    print("=" * 60)

    result = init_config_dir(target_dir)

    if not result["success"]:
        if "already exists" in result["message"]:
            if force:
                print("\n[WARNING] Directory exists, but --force specified.")
                print(f"   Path: {result['path']}")
                print("\n[SKIP] Use manual deletion if you need to reinitialize.")
                return 1
            else:
                print("\n[OK] Configuration directory already exists.")
                print(f"   Path: {result['path']}")
                print("\nUse --force to attempt reinitialization.")
                return 0
        else:
            print(f"\n[ERROR] {result['message']}")
            return 1

    print("\n[SUCCESS] Configuration directory created:")
    print(f"   Path: {result['path']}")
    print(f"\nCreated {len(result['files_created'])} files:")
    for filename in result["files_created"]:
        print(f"   - {filename}")

    print("\nNext steps:")
    print("   1. Review policy.yaml to configure security rules")
    print("   2. Review budget.yaml to set change limits")
    print("   3. Read README.md for configuration guidance")
    print("   4. Add .code-scalpel/ to version control (optional)")

    return 0


def start_server(host: str = "127.0.0.1", port: int = 5000) -> int:
    """Start the REST API server (legacy, for non-MCP clients).

    [20251223_SECURITY] Default binding is localhost-only.
    Use --host 0.0.0.0 to allow LAN access on trusted networks.
    """
    from .integrations.rest_api_server import run_server

    print(f"Starting Code Scalpel REST API Server on {host}:{port}")
    print(f"   Health check: http://{host}:{port}/health")
    print(f"   Analyze endpoint: POST http://{host}:{port}/analyze")
    print(f"   Refactor endpoint: POST http://{host}:{port}/refactor")
    print(f"   Security endpoint: POST http://{host}:{port}/security")
    print(
        "\nNote: For MCP-compliant clients (Claude Desktop, Cursor), use 'code-scalpel mcp' instead."
    )
    print("Press Ctrl+C to stop the server.\n")

    try:
        run_server(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        print("\nServer stopped.")

    return 0


def start_mcp_server(
    transport: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 8080,
    allow_lan: bool = False,
    root_path: str | None = None,
    tier: str | None = None,
    ssl_certfile: str | None = None,
    ssl_keyfile: str | None = None,
) -> int:
    """Start the MCP-compliant server (for AI clients like Claude Desktop, Cursor)."""
    from .mcp.server import run_server

    # [20251215_FEATURE] Determine protocol based on SSL config
    use_https = ssl_certfile and ssl_keyfile
    protocol = "https" if use_https else "http"

    if transport == "stdio":
        print("Starting Code Scalpel MCP Server (stdio transport)")
        print("   This server communicates via stdin/stdout.")
        print("   Add to your Claude Desktop config or use with MCP Inspector.")
        print("\nPress Ctrl+C to stop.\n")
    else:
        print(
            f"Starting Code Scalpel MCP Server ({protocol.upper()} transport) on {host}:{port}"
        )
        endpoint_path = "/mcp" if transport == "streamable-http" else "/sse"
        print(f"   MCP endpoint: {protocol}://{host}:{port}{endpoint_path}")
        if use_https:
            print("   SSL/TLS: ENABLED")
        if allow_lan:
            print("   LAN access: ENABLED (host validation disabled)")
            print("   WARNING: Only use on trusted networks!")
        print("\nPress Ctrl+C to stop.\n")

    # [20251216_BUGFIX] Avoid passing SSL kwargs when not configured to maintain compatibility with minimal run_server signatures
    server_kwargs = {
        "transport": transport,
        "host": host,
        "port": port,
        "allow_lan": allow_lan,
        "root_path": root_path,
        "tier": tier,
    }
    if use_https:
        server_kwargs.update(
            {
                "ssl_certfile": ssl_certfile,
                "ssl_keyfile": ssl_keyfile,
            }
        )

    try:
        run_server(**server_kwargs)
    except KeyboardInterrupt:
        print("\nMCP Server stopped.")

    return 0


def main() -> int:
    """Main CLI entry point."""
    from . import __version__

    parser = argparse.ArgumentParser(
        prog="code-scalpel",
        description="AI Agent toolkit for code analysis using ASTs, PDGs, and Symbolic Execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  code-scalpel analyze myfile.py              Analyze a Python file
  code-scalpel analyze --code "def f(): pass" Analyze code string
  code-scalpel analyze myfile.py --json       Output as JSON
  code-scalpel scan myfile.py                 Security vulnerability scan
  code-scalpel scan myfile.py --json          Security scan with JSON output
  code-scalpel mcp                            Start MCP server (stdio, for Claude Desktop)
  code-scalpel mcp --http --port 8080         Start MCP server (HTTP transport)
  code-scalpel mcp --http --allow-lan         Start MCP server with LAN access
  code-scalpel mcp --http --ssl-cert cert.pem --ssl-key key.pem  HTTPS for production/Claude
  code-scalpel server --port 5000             Start REST API server (legacy)
  code-scalpel version                        Show version info

For production deployments with Claude API, use HTTPS:
  code-scalpel mcp --http --ssl-cert /path/to/cert.pem --ssl-key /path/to/key.pem

For more information, visit: https://github.com/tescolopio/code-scalpel
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze code")
    analyze_parser.add_argument("file", nargs="?", help="File to analyze")
    analyze_parser.add_argument("--code", "-c", help="Code string to analyze")
    analyze_parser.add_argument(
        "--json", "-j", action="store_true", help="Output as JSON"
    )
    analyze_parser.add_argument(
        "--language",
        "-l",
        choices=["python", "javascript", "java"],
        help="Source language (default: auto-detect or python)",
    )

    # Scan command (Security Analysis)
    scan_parser = subparsers.add_parser(
        "scan", help="Scan for security vulnerabilities (SQLi, XSS, etc.)"
    )
    scan_parser.add_argument("file", nargs="?", help="Python file to scan")
    scan_parser.add_argument("--code", "-c", help="Code string to scan")
    scan_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    # Init command (Configuration Setup) - [20251219_FEATURE] v3.0.2
    init_parser = subparsers.add_parser(
        "init", help="Initialize .code-scalpel configuration directory"
    )
    init_parser.add_argument(
        "--dir",
        "-d",
        default=".",
        help="Target directory (default: current directory)",
    )
    init_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force initialization even if directory exists",
    )

    # Server command (REST API - legacy)
    server_parser = subparsers.add_parser(
        "server", help="Start REST API server (legacy)"
    )
    server_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    server_parser.add_argument(
        "--port", "-p", type=int, default=5000, help="Port to bind to (default: 5000)"
    )

    # MCP command (Model Context Protocol - recommended)
    mcp_parser = subparsers.add_parser(
        "mcp", help="Start MCP server (for Claude Desktop, Cursor)"
    )
    mcp_parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    mcp_parser.add_argument(
        "--http",
        action="store_true",
        help="Use HTTP transport (alias for --transport sse)",
    )
    mcp_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for HTTP (default: 127.0.0.1)",
    )
    mcp_parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8080,
        help="Port for HTTP transport (default: 8080)",
    )
    mcp_parser.add_argument(
        "--allow-lan",
        action="store_true",
        help="Allow LAN connections (disables host validation, use on trusted networks only)",
    )
    mcp_parser.add_argument(
        "--root",
        default=None,
        help="Project root directory for context resources (default: current directory)",
    )
    mcp_parser.add_argument(
        "--tier",
        choices=["community", "pro", "enterprise"],
        default=None,
        help="Tool tier (default: enterprise or CODE_SCALPEL_TIER/SCALPEL_TIER)",
    )
    # [20251215_FEATURE] SSL/TLS support for HTTPS - required for Claude API and production
    mcp_parser.add_argument(
        "--ssl-cert",
        default=None,
        help="Path to SSL certificate file for HTTPS (required for Claude API)",
    )
    mcp_parser.add_argument(
        "--ssl-key",
        default=None,
        help="Path to SSL private key file for HTTPS (required for Claude API)",
    )

    # Version command
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args()

    if args.command == "analyze":
        output_format = "json" if args.json else "text"
        if args.code:
            return analyze_code(
                args.code, output_format, language=args.language or "python"
            )
        elif args.file:
            return analyze_file(args.file, output_format, language=args.language)
        else:
            analyze_parser.print_help()
            return 1

    elif args.command == "scan":
        output_format = "json" if args.json else "text"
        if args.code:
            return scan_code_security(args.code, output_format)
        elif args.file:
            return scan_security(args.file, output_format)
        else:
            scan_parser.print_help()
            return 1

    elif args.command == "init":  # [20251219_FEATURE] v3.0.2
        return init_configuration(args.dir, args.force)

    elif args.command == "server":
        return start_server(args.host, args.port)

    elif args.command == "mcp":
        transport = args.transport
        if args.http:
            transport = "sse"

        allow_lan = getattr(args, "allow_lan", False)
        root_path = getattr(args, "root", None)
        tier = getattr(args, "tier", None)
        ssl_certfile = getattr(args, "ssl_cert", None)
        ssl_keyfile = getattr(args, "ssl_key", None)

        # [20251216_BUGFIX] Only override host if allow_lan and host is default
        if allow_lan and args.host == "127.0.0.1":
            # LAN access is intentional when --allow-lan is used.
            args.host = "0.0.0.0"  # nosec B104

        # Build kwargs for server startup
        start_kwargs = {
            "transport": transport,
            "host": args.host,
            "port": args.port,
            "allow_lan": allow_lan,
            "root_path": root_path,
            "tier": tier,
        }
        if ssl_certfile and ssl_keyfile:
            start_kwargs.update(
                {
                    "ssl_certfile": ssl_certfile,
                    "ssl_keyfile": ssl_keyfile,
                }
            )

        return start_mcp_server(**start_kwargs)

    elif args.command == "version":
        print(f"Code Scalpel v{__version__}")
        print(f"Python {sys.version}")
        return 0

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
