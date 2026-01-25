"""Simple test runner for MCP stdio JSON-RPC server.

This runner will spawn the server (optional), run discovery, and execute a small smoke test
against a few tools generated from docs/roadmap. It writes logs under testing/logs/ and updates
testing/TRACKING.md (manual updates only in this version).
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
LOGDIR = ROOT / "testing" / "logs"
LOGDIR.mkdir(parents=True, exist_ok=True)
SPECDIR = ROOT / "test-harness" / "specs"


def update_tracking(tool_name: str, result: str, reason: str, logpath: str):
    tracking = ROOT / "testing" / "TRACKING.md"
    now = datetime.utcnow().isoformat() + "Z"
    # Append a short line to TRACKING.md (simple approach)
    with tracking.open("a", encoding="utf-8") as f:
        f.write(
            f"| {tool_name} | tool | yes | {now} | {result} | {reason} | - | {logpath} |\n"
        )


def spawn_server():
    # Use the project's CLI to start MCP server in stdio mode; keep it connected via pipes
    # We'll run: python -m code_scalpel.mcp.server --transport stdio
    cmd = [sys.executable, "-m", "code_scalpel.mcp.server", "--transport", "stdio"]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
    )
    return proc


def send_jsonrpc(proc, method, params=None, id_val=1):
    req = {"jsonrpc": "2.0", "id": id_val, "method": method}
    if params is not None:
        req["params"] = params
    line = json.dumps(req)
    proc.stdin.write(line + "\n")
    proc.stdin.flush()
    return line


def read_response(proc, timeout=5.0):
    # Read one line of stdout with timeout
    start = time.time()
    while True:
        if proc.stdout.readable():
            line = proc.stdout.readline()
            if line:
                return line.strip()
        if time.time() - start > timeout:
            return None
        time.sleep(0.05)


def smoke_tests(proc):
    # Load specs and construct minimal requests for each
    tests = []
    for spec in sorted(SPECDIR.glob("*.json")):
        try:
            s = json.loads(spec.read_text(encoding="utf-8"))
            tests.append((s.get("tool"), s))
        except Exception:
            continue
    results = []
    for i, (method, params) in enumerate(tests, start=1):
        # For auto-generated specs we don't have concrete params; use empty or overview
        arguments = None
        if isinstance(params, dict) and params.get("overview"):
            arguments = {}
        req_line = send_jsonrpc(
            proc, "tools/call", {"name": method, "arguments": arguments}, id_val=i
        )
        resp_line = read_response(proc, timeout=15.0)
        entry = {"method": method, "req": req_line, "resp": resp_line}
        results.append(entry)
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        logfile = LOGDIR / f"{method}-{timestamp}.log"
        logfile.write_text(json.dumps(entry, indent=2), encoding="utf-8")
        # Update tracking
        update_tracking(method, "unknown", "smoke-run", str(logfile))
    return results


def main():
    print("Starting harness; spawning MCP stdio server...")
    proc = spawn_server()
    # Allow server to initialize briefly
    time.sleep(1.0)
    # run discovery
    send_jsonrpc(proc, "rpc.listMethods", id_val=1)
    resp = read_response(proc, timeout=3.0)
    print("Discovery response:", resp)
    results = smoke_tests(proc)
    print("Smoke test results:")
    for r in results:
        print(r["method"], "->", r["resp"])
    # capture stderr
    try:
        stderr = proc.stderr.read()
        if stderr:
            (LOGDIR / "server-stderr.log").write_text(stderr)
    except Exception:
        pass
    proc.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
