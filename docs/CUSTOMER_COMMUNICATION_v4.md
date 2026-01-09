# Customer Communication Template - v4.0.0 Split

Use this template to notify existing Pro/Enterprise customers about the v4.0.0 split into Community, Pro, and Enterprise packages.

## Audience
- No current Pro/Enterprise customers (pre-launch, silent phase)
- Prospects: pending Pro trials and Enterprise pilots when activated

## Purpose
- Explain the repo/package split and what stays open-source
- Describe how Pro/Enterprise artifacts will be delivered and authenticated
- Provide action items and support contacts

## Key Changes (TL;DR)
- Community stays MIT open-source in the new `code-scalpel` package
- Pro/Enterprise move to private packages with the same MCP API
- JWT licensing flow remains; download endpoints change (see below)

## Rollout Timeline
- v3.3.0: Final monolith release (2026-01-15)
- v4.0.0: Split release (2026-02-01)
- Grace period: 90 days (2026-02-01 → 2026-04-30) - monolith support window
- EOL monolith: 2026-05-01

## Download Path Changes
- Community: PyPI `code-scalpel` (public, no auth needed)
- Pro: Private index `https://dist.code-scalpel.io/pro/` (JWT bearer token required)
- Enterprise: Private index `https://dist.code-scalpel.io/enterprise/` (JWT bearer token required)
- Artifacts: Wheel files + pinned requirements.txt for reproducible builds
- Auth: JWT bearer token configured in `pip` via `.netrc` or `PIP_INDEX_URL` env var

## What Customers Need To Do
- Update install commands to new private index URLs
- Ensure JWT token/config is available in CI/CD and local dev
- Validate MCP client config continues to point to the Pro/Enterprise server entrypoints
- Review firewall/allowlist requirements for new artifact host

## Licensing and Compliance
- License remains MIT for Community; commercial terms apply for Pro/Enterprise
- No change to existing contract terms; new license keys issued for v4.0.0
- Audit/usage logging remains enabled for Pro/Enterprise per contract

## Support and Contacts
- Pro support: support@code-scalpel.io (48h SLA, support@code-scalpel.io)
- Enterprise support: enterprise@code-scalpel.io (dedicated contact, 24/5 SLA)
- Escalations: escalations@code-scalpel.io
- Support portal: https://support.code-scalpel.io

## Upgrade FAQ (fill before send)
- **Q: Will my existing license key work?**
  A: Yes, for 90 days (grace period through 2026-04-30). New v4.0.0 keys are issued at no cost for active Pro/Enterprise customers.

- **Q: Is there a cost to upgrade?**
  A: No. Community remains free; Pro/Enterprise upgrade is included in your contract with no additional fees.

- **Q: Are MCP tool APIs breaking?**
  A: No. All 22 tool names and signatures remain stable. Tier-gated fields are additive (Pro/Enterprise get new capability fields only).

- **Q: Do I need to reconfigure my IDE/clients?**
  A: Update package source URLs in pip/poetry config to point to the new private indexes. MCP server endpoints unchanged; tools work identically.

- **Q: How long is the monolith (v3.3.0) supported?**
  A: 90 days from v4.0.0 release (until 2026-04-30). After that, only v4.0.0+ receives updates and security patches.

- **Q: Where are release notes and migration guide?**
  A: Full migration guide at https://docs.code-scalpel.io/v4-migration; release notes on GitHub releases page.

- **Q: What if I have issues during migration?**
  A: Enterprise support is available 24/5 (enterprise@code-scalpel.io); Pro customers can email support@code-scalpel.io (48h SLA). Dedicated support window during grace period.

## Communications Plan
- **Internal Dry-Run:** Before public send, internal team reviews template for accuracy and dates
- **Customer Email:** Send 1 week before v4.0.0 GA (around 2026-01-25) to Pro/Enterprise customers and beta signups
- **Public Blog Post:** Announcement and migration guide published at https://code-scalpel.io/blog on v4.0.0 release day
- **In-Product Notice:** If applicable, add banner in Pro/Enterprise UI alerting to new download URLs
- **Timeline:** Email → Blog → Docs → In-product (all by 2026-02-01 GA)
