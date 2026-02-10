"""
CLI Entry point for codescalpel-agents package.

[20260125_FEATURE] Phase 3: Separate CLI commands for independent packages
- codescalpel-agents serve: Run agents service with MCP support
"""

import sys


def serve():
    """Serve the agents package via MCP.

    This command starts the agents service using the Code Scalpel MCP server
    from the parent code_scalpel package. Agents are available when the core
    package is installed.

    [20260125_FEATURE] This provides a convenient entry point for the agents
    package without requiring users to know about the core code-scalpel package.
    """
    try:
        from code_scalpel.mcp.server import run_server
    except ImportError:
        print(
            "Error: code-scalpel package is required for agents service",
            file=sys.stderr,
        )
        print(
            "Install with: pip install codescalpel or pip install codescalpel-agents[core]",
            file=sys.stderr,
        )
        return 1

    # Run the MCP server with agents available
    # This uses the same infrastructure as the main code-scalpel CLI
    return run_server(transport="stdio")


def main():
    """Main entry point for codescalpel-agents CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="codescalpel-agents",
        description="Code Scalpel Agents - AI Agent toolkit for code analysis",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Serve agents via MCP")
    serve_parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )
    serve_parser.add_argument(
        "--http",
        action="store_true",
        help="Use HTTP transport (alias for --transport sse)",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for HTTP transport (default: 8080)",
    )
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for HTTP (default: 127.0.0.1)",
    )

    # Parse arguments
    if len(sys.argv) == 1:
        # Default to 'serve' if no command given
        args = argparse.Namespace(command="serve", transport="stdio", http=False)
    else:
        args = parser.parse_args()

    if args.command == "serve" or args.command is None:
        try:
            from code_scalpel.mcp.server import run_server

            transport = args.transport if hasattr(args, "transport") else "stdio"
            if hasattr(args, "http") and args.http:
                transport = "sse"

            host = args.host if hasattr(args, "host") else "127.0.0.1"
            port = args.port if hasattr(args, "port") else 8080

            print(
                f"Starting codescalpel-agents MCP server ({transport} transport)",
                file=sys.stderr,
            )
            return run_server(transport=transport, host=host, port=port)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
