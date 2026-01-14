// Configure purchase + contact links here.
// Replace placeholders with Stripe Payment Links, Paddle, Lemon Squeezy, etc.

window.CODE_SCALPEL_SITE_CONFIG = {
  proPurchaseUrl: "https://example.com/buy/pro",
  enterpriseContactUrl: "mailto:sales@codescalpel.dev?subject=Code%20Scalpel%20Enterprise%20Inquiry",
  demoBookingUrl: "https://example.com/book/demo",

  // Licensing & pricing display
  // Pricing is per-seat. Use strings so you can include currency symbols.
  currencySymbol: "$",
  proPricePerSeatMonthly: "59",
  proPricePerSeatAnnual: "49",
  proBillingNote: "per seat / month, billed annually",
  enterpriseBillingNote: "per seat, annual contract (volume discounts)",
};
