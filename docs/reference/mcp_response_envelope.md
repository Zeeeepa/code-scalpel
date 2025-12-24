# MCP Response Envelope (V1.0 Contract)

This document defines the universal response envelope for all Code Scalpel MCP tools.

Source of truth for this requirement: `docs/guides/production_release_v1.0.md`.

## Goals

- Every tool returns a consistent, machine-parseable top-level shape.
- Clients can reliably correlate requests (`request_id`) and determine tier/tool metadata.
- Errors are standardized via `error_code` (see `docs/reference/error_codes.md`).

## Envelope Schema (All Tools)

All MCP tools MUST return a JSON object with the following fields:

- `tier` (string): one of `community`, `pro`, `enterprise`
- `tool_version` (string): semantic version of the tool implementation
- `tool_id` (string): canonical MCP tool id (e.g., `security_scan`)
- `request_id` (string): correlation id (caller-provided or server-generated)
- `capabilities` (array[string]): describes what this invocation supports
- `duration_ms` (number): end-to-end runtime in milliseconds
  - Required for Pro/Enterprise
  - Recommended for Community
- `error` (object|null): standardized error model (see below)
- `upgrade_hints` (array[object]): upgrade hints when a feature is unavailable at this tier
- `data` (any|null): tool-specific payload (the tool’s existing response model)

## Error Model

When `error` is not null, it MUST include:

- `error` (string): human-readable message
- `error_code` (string): machine-parseable error code
- `error_details` (object|null): optional structured details safe for clients

Notes:
- Error responses MUST NOT include code contents.
- Tools may still include tool-specific failure details inside `data`, but the standardized `error` is the primary contract.

## Upgrade Hints

When a requested feature is not available in the current tier, include one or more entries in `upgrade_hints`:

- `feature` (string)
- `tier` (string)
- `reason` (string)

## Examples

### Successful response

```json
{
  "tier": "pro",
  "tool_version": "3.2.8",
  "tool_id": "security_scan",
  "request_id": "8b3e5f6c0a2f4ed4a3fb9e0b2f8f8d3a",
  "capabilities": ["envelope-v1"],
  "duration_ms": 27,
  "error": null,
  "upgrade_hints": [],
  "data": {"success": true, "risk_level": "high", "findings": []}
}
```

### Error response

```json
{
  "tier": "community",
  "tool_version": "3.2.8",
  "tool_id": "extract_code",
  "request_id": "0a46e6c2b6df4e938e8d16ffb567a9b2",
  "capabilities": ["envelope-v1"],
  "duration_ms": 3,
  "error": {
    "error": "File not found: /missing.py.",
    "error_code": "not_found",
    "error_details": null
  },
  "upgrade_hints": [],
  "data": {"success": false, "error": "File not found: /missing.py."}
}
```
