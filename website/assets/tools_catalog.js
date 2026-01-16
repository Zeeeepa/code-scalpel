// [20260114_FEATURE] Render per-tool catalog from deep-dive docs (pre-generated JSON).

(() => {
  const qs = (sel, root = document) => root.querySelector(sel);
  const qsa = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const normalize = (s) => String(s || "").toLowerCase();

  const tierAllows = (toolTierAvailability, wanted) => {
    if (!wanted || wanted === "all") return true;
    const tier = normalize(toolTierAvailability);
    if (wanted === "enterprise") return tier.includes("enterprise");
    if (wanted === "pro") return tier.includes("pro") || tier.includes("enterprise");
    if (wanted === "community") return tier.includes("all") || tier.includes("comm");
    return true;
  };

  const esc = (s) => {
    const div = document.createElement("div");
    div.textContent = String(s ?? "");
    return div.innerHTML;
  };

  const renderTool = (tool, idx) => {
    const panelId = `tool-panel-${idx}-${tool.name}`.replace(/[^a-zA-Z0-9_-]/g, "-");

    const caps = (tool.keyCapabilities || []).map((c) => `<li>${esc(c)}</li>`).join("");
    const benefits = (tool.keyBenefits || []).map((b) => `<li>${esc(b)}</li>`).join("");
    const when = (tool.whenToUse || []).map((w) => `<li>${esc(w)}</li>`).join("");
    const notOk = (tool.notSuitableFor || []).map((n) => `<li>${esc(n)}</li>`).join("");

    const signature = tool.signature
      ? `<div class="code-block" style="margin-top:10px;"><pre><code>${esc(tool.signature)}</code></pre></div>`
      : "";

    const metaBits = [
      tool.status ? `<span class="small" style="padding:4px 8px; border:1px solid rgba(255,255,255,.12); border-radius:999px;">${esc(tool.status)}</span>` : "",
      tool.tierAvailability ? `<span class="small" style="padding:4px 8px; border:1px solid rgba(255,255,255,.12); border-radius:999px;">${esc(tool.tierAvailability)}</span>` : "",
      tool.toolVersion ? `<span class="small" style="padding:4px 8px; border:1px solid rgba(255,255,255,.12); border-radius:999px;">Tool ${esc(tool.toolVersion)}</span>` : "",
    ].filter(Boolean);

    return `
      <div class="card" data-accordion style="margin-top:14px;">
        <div class="card-inner">
          <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; justify-content:space-between;">
            <div style="display:flex; gap:10px; align-items:baseline; flex-wrap:wrap;">
              <h3 style="margin:0;">${esc(tool.name)}</h3>
              ${metaBits.length ? `<div style="display:flex; gap:8px; flex-wrap:wrap;">${metaBits.join("")}</div>` : ""}
            </div>
            <button class="btn" style="justify-content:space-between;" data-accordion-trigger aria-expanded="false" aria-controls="${panelId}">Details</button>
          </div>

          ${tool.purpose ? `<p class="small" style="margin:10px 0 0; max-width: 920px;">${esc(tool.purpose)}</p>` : ""}

          <div id="${panelId}" hidden style="margin-top:12px;">
            <div class="grid2" style="gap:14px;">
              <div>
                ${tool.keyCapabilities?.length ? `<h4 style="margin:0 0 8px;">Key capabilities</h4><ul style="margin:0; padding-left:18px; color: var(--text-secondary); line-height: 1.7;">${caps}</ul>` : ""}
                ${tool.keyBenefits?.length ? `<h4 style="margin:14px 0 8px;">Key benefits</h4><ul style="margin:0; padding-left:18px; color: var(--text-secondary); line-height: 1.7;">${benefits}</ul>` : ""}
              </div>
              <div>
                ${tool.whenToUse?.length ? `<h4 style="margin:0 0 8px;">When to use</h4><ul style="margin:0; padding-left:18px; color: var(--text-secondary); line-height: 1.7;">${when}</ul>` : ""}
                ${tool.notSuitableFor?.length ? `<h4 style="margin:14px 0 8px;">Not suitable for</h4><ul style="margin:0; padding-left:18px; color: var(--text-secondary); line-height: 1.7;">${notOk}</ul>` : ""}
              </div>
            </div>

            ${signature ? `<h4 style="margin:16px 0 8px;">Signature</h4>${signature}` : ""}

            <div style="margin-top:12px; display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
              ${tool.deepDiveUrl ? `<a class="btn btn-ghost" href="${esc(tool.deepDiveUrl)}" target="_blank" rel="noreferrer">Deep dive doc</a>` : ""}
              ${tool.deepDiveFile ? `<span class="small" style="opacity:.85;">Source: docs/tools/deep_dive/${esc(tool.deepDiveFile)}</span>` : ""}
            </div>
          </div>
        </div>
      </div>
    `;
  };

  const main = async () => {
    const mount = qs("#toolCatalog");
    if (!mount) return;

    const search = qs("#toolSearch");
    const tierSel = qs("#tierFilter");

    let data;
    try {
      const res = await fetch("/assets/tool_catalog.json", { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      data = await res.json();
    } catch (e) {
      mount.innerHTML = `<div class="card"><div class="card-inner"><p class="small" style="margin:0;">Failed to load tool catalog. (${esc(e)})</p></div></div>`;
      return;
    }

    const tools = Array.isArray(data?.tools) ? data.tools : [];

    const apply = () => {
      const q = normalize(search?.value);
      const wantedTier = normalize(tierSel?.value || "all");

      const filtered = tools.filter((t) => {
        if (!tierAllows(t.tierAvailability, wantedTier)) return false;
        if (!q) return true;
        const hay = [t.name, t.purpose, ...(t.keyCapabilities || [])].map(normalize).join("\n");
        return hay.includes(q);
      });

      mount.innerHTML = filtered.map(renderTool).join("");

      // Re-bind accordion triggers for newly injected DOM.
      qsa("[data-accordion]", mount).forEach((acc) => {
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

      const countEl = qs("#toolCount");
      if (countEl) countEl.textContent = String(filtered.length);
    };

    if (search) search.addEventListener("input", apply);
    if (tierSel) tierSel.addEventListener("change", apply);

    apply();
  };

  main();
})();
