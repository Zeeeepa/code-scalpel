# Code Scalpel Website (Static)

This is a zero-build static marketing website scaffold.

## Local preview

From the repo root:

```bash
cd website
python3 -m http.server 5173
```

Then open:

- http://localhost:5173/

## Configure purchase links

Edit:

- `website/assets/config.js`

Set:
- `proPurchaseUrl` (Stripe Payment Link, Paddle checkout URL, Lemon Squeezy, etc.)
- `enterpriseContactUrl` (mailto or CRM form)
- `demoBookingUrl` (Calendly, HubSpot, etc.)

Optional (pricing display):
- `proPricePerSeatMonthly`, `proPricePerSeatAnnual`, `proBillingNote`
- `enterpriseBillingNote`

## Deploy

Because this site is static, you can deploy it to:
- GitHub Pages
- Netlify
- Cloudflare Pages
- Any static host

If deploying under a subpath (e.g., `/code-scalpel/`), you may need to adjust the absolute `/assets/...` links to relative paths.
