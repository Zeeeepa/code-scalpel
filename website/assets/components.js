export function layout({ title, description, active, content }) {
  const safeTitle = title ? `${title} — Code Scalpel` : "Code Scalpel";
  const safeDesc = description ?? "Governed AI code operations: analyze, extract, validate, and safely patch code with policy and auditability.";

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <meta name="description" content="${escapeHtml(safeDesc)}" />
  <title>${escapeHtml(safeTitle)}</title>
  <link rel="stylesheet" href="/assets/styles.css" />
</head>
<body>
  <header class="nav">
    <div class="container nav-inner">
      <a class="brand" href="/">
        <span class="logo" aria-hidden="true"></span>
        <span>Code Scalpel</span>
      </a>

      <nav class="nav-links" aria-label="Primary">
        <a ${active === "tools" ? 'style="color: var(--text)"' : ''} href="/pages/tools.html">Tools</a>
        <a ${active === "pricing" ? 'style="color: var(--text)"' : ''} href="/pages/pricing.html">Pricing</a>
        <a href="/pages/security.html">Security</a>
      </nav>

      <div style="display:flex; gap:10px; align-items:center;">
        <a class="btn ghost" data-link="demo-book" href="https://example.com/book/demo">Book a demo</a>
        <a class="btn primary" data-link="pro-buy" href="https://example.com/buy/pro">Buy Pro</a>
        <button class="btn mobile-only" data-menu-button aria-expanded="false" aria-controls="mobile-menu">Menu</button>
      </div>
    </div>
    <div class="container mobile-menu" id="mobile-menu" data-mobile-menu data-open="false">
      <a href="/pages/tools.html">Tools</a>
      <a href="/pages/pricing.html">Pricing</a>
      <a href="/pages/security.html">Security</a>
      <a data-link="enterprise-contact" href="mailto:sales@codescalpel.dev?subject=Code%20Scalpel%20Enterprise%20Inquiry">Contact sales</a>
    </div>
  </header>

  ${content}

  <footer class="footer">
    <div class="container">
      <div style="display:flex; gap:14px; flex-wrap:wrap; align-items:center; justify-content:space-between;">
        <div>© ${new Date().getFullYear()} Code Scalpel</div>
        <div style="display:flex; gap:14px; flex-wrap:wrap;">
          <a class="small" href="/pages/pricing.html">Pricing</a>
          <a class="small" href="/pages/security.html">Security</a>
          <a class="small" data-link="enterprise-contact" href="mailto:sales@codescalpel.dev?subject=Code%20Scalpel%20Enterprise%20Inquiry">Contact</a>
        </div>
      </div>
      <div class="small" style="margin-top:10px;">Links are placeholders until you set <code>website/assets/config.js</code>.</div>
    </div>
  </footer>

  <script src="/assets/config.js"></script>
  <script src="/assets/site.js"></script>
</body>
</html>`;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
