# License Discovery

This guide explains how the MCP server discovers license JWT files and what filename patterns are supported.

License discovery priority:

1. Explicit path via `CODE_SCALPEL_LICENSE_PATH` (can be a file or a directory).
2. Project license: `.code-scalpel/license/license.jwt`.
3. Project license file: `.code-scalpel/license.jwt`.
4. User config: `~/.config/code-scalpel/license.jwt`.
5. Legacy locations: `~/.code-scalpel/license.jwt`, `.scalpel-license`.

Supported filename patterns when scanning a directory:

- `code_scalpel_license*.jwt`
- `code-scalpel-license*.jwt`
- `license*.jwt`
- `*.license.jwt`
- `code_scalpel_*_beta_*.jwt` (beta builds)
- `code_scalpel_enterprise*.jwt`
- `code_scalpel_pro*.jwt`
- Any `*.jwt` in the configured directories will be considered as a candidate (newer files take precedence).

How to set `CODE_SCALPEL_LICENSE_PATH`:

- To point to a specific file:

```bash
export CODE_SCALPEL_LICENSE_PATH=/path/to/license.jwt
```

- To point to a directory (preferred for developer workflows where multiple license files may exist):

```bash
export CODE_SCALPEL_LICENSE_PATH=/path/to/.code-scalpel/license/
```

When the license file is found but validation fails, the server will log a clear error explaining the reason (invalid signature, expired token, revoked token, or mismatched issuer/audience). See the troubleshooting section below.

Troubleshooting:

- "Invalid signature": The license token was not signed with the expected public key. Use a license issued by the Code Scalpel distribution owner or update the public key via the `public_key/` mechanism.
- "Expired": The license is expired. Request a renewed license or use the last-known-valid tier within 24 hours.
- "Revoked": The license was revoked and cannot be used.

If you need help, please provide the token header/claims (not the signature) so support can verify `iss`, `aud`, and `kid` values.