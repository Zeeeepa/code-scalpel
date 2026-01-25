"""Discover available MCP JSON-RPC methods via stdio JSON-RPC discovery.

This script writes a JSON-RPC discovery request to stdout and reads responses from stdin.
It is intended to be run as part of the harness where a server process is connected via stdio.
"""

import json
import sys


def send_request(method, params=None, id_val=1):
    req = {"jsonrpc": "2.0", "id": id_val, "method": method}
    if params is not None:
        req["params"] = params
    print(json.dumps(req))
    sys.stdout.flush()


def main():
    # Try common discovery methods in order
    methods = [
        "rpc.listMethods",
        "rpc.discover",
        "system.listMethods",
        "mcp.list_tools",
    ]
    # Send a request and read one JSON line response
    for i, m in enumerate(methods, start=1):
        send_request(m, id_val=i)
        line = sys.stdin.readline()
        if not line:
            continue
        try:
            resp = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "result" in resp:
            print(json.dumps({"discovered_method": m, "result": resp["result"]}))
            return 0
    # Fallback: print guidance to use docs/roadmap
    print(
        json.dumps(
            {
                "discovered_method": None,
                "message": "No discovery response; fallback to docs/roadmap",
            }
        )
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
