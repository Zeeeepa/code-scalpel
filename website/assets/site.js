(() => {
  const qs = (sel, root = document) => root.querySelector(sel);
  const qsa = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const config = (window.CODE_SCALPEL_SITE_CONFIG ?? {});

  const bindLink = (selector, url) => {
    if (!url) return;
    qsa(selector).forEach((el) => {
      el.setAttribute("href", url);
      el.dataset.bound = "true";
    });
  };

  bindLink("a[data-link='pro-buy']", config.proPurchaseUrl);
  bindLink("a[data-link='enterprise-contact']", config.enterpriseContactUrl);
  bindLink("a[data-link='demo-book']", config.demoBookingUrl);

  const bindText = (selector, value) => {
    if (value === undefined || value === null) return;
    qsa(selector).forEach((el) => {
      el.textContent = String(value);
      el.dataset.bound = "true";
    });
  };

  bindText("[data-field='currency']", config.currencySymbol);
  bindText("[data-field='pro-price-monthly']", config.proPricePerSeatMonthly);
  bindText("[data-field='pro-price-annual']", config.proPricePerSeatAnnual);
  bindText("[data-field='pro-billing-note']", config.proBillingNote);
  bindText("[data-field='enterprise-billing-note']", config.enterpriseBillingNote);

  // Mobile menu
  const menuBtn = qs("[data-menu-button]");
  const menu = qs("[data-mobile-menu]");
  if (menuBtn && menu) {
    menuBtn.addEventListener("click", () => {
      const open = menu.dataset.open === "true";
      menu.dataset.open = open ? "false" : "true";
      menuBtn.setAttribute("aria-expanded", open ? "false" : "true");
    });
  }

  // Simple accordion
  qsa("[data-accordion]").forEach((acc) => {
    qsa("button[data-accordion-trigger]", acc).forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("aria-controls");
        const panel = id ? qs(`#${id}`) : null;
        if (!panel) return;
        const expanded = btn.getAttribute("aria-expanded") === "true";
        btn.setAttribute("aria-expanded", expanded ? "false" : "true");
        panel.hidden = expanded;
      });
    });
  });
})();
