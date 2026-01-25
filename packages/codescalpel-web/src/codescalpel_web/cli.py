"""
CLI Entry point for codescalpel-web package.

[20260125_FEATURE] Phase 3: Separate CLI commands for independent packages
- codescalpel-web serve: Run REST API server with MCP support
"""

import sys


def serve():
    """Serve the REST API server.

    This command starts the REST API server for Code Scalpel,
    providing a traditional REST API interface for analysis tools.

    [20260125_FEATURE] This provides a convenient entry point for the web
    package without requiring users to know about the core code-scalpel package.
    """
    try:
        from codescalpel_web.server import run_server
    except ImportError:
        print(
            "Error: codescalpel-web package is required or not properly installed",
            file=sys.stderr,
        )
        print(
            "Install with: pip install codescalpel-web",
            file=sys.stderr,
        )
        return 1

    # Run the REST API server
    return run_server(host="127.0.0.1", port=5000, debug=False)


def main():
    """Main entry point for codescalpel-web CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="codescalpel-web",
        description="Code Scalpel Web - REST API server for code analysis",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Serve REST API")
    serve_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=5000,
        help="Port to bind to (default: 5000)",
    )
    serve_parser.add_argument(
        "--allow-lan",
        action="store_true",
        help="Allow LAN connections (disables host validation)",
    )
    serve_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (not for production)",
    )

    # Parse arguments
    if len(sys.argv) == 1:
        # Default to 'serve' if no command given
        args = argparse.Namespace(
            command="serve", host="127.0.0.1", port=5000, allow_lan=False, debug=False
        )
    else:
        args = parser.parse_args()

    if args.command == "serve" or args.command is None:
        try:
            from codescalpel_web.server import run_server

            host = args.host if hasattr(args, "host") else "127.0.0.1"
            port = args.port if hasattr(args, "port") else 5000
            allow_lan = args.allow_lan if hasattr(args, "allow_lan") else False
            debug = args.debug if hasattr(args, "debug") else False

            if allow_lan:
                host = "0.0.0.0"

            print(
                f"Starting codescalpel-web REST API server on {host}:{port}",
                file=sys.stderr,
            )
            if debug:
                print("Debug mode ENABLED (not for production)", file=sys.stderr)
            return run_server(host=host, port=port, debug=debug)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback

            traceback.print_exc(file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
