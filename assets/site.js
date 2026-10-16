// Shared behaviour for all pages. Each block only runs if its markup exists.

// ---- UI strings for the page language (<html lang="…">) ----
const I18N = {
  en: { dark: "dark mode", light: "light mode", pubs: "publications", open: "Open photo: ", keys: "← → · esc",
        flags: { Article: "Article", Dissertation: "Dissertation" } },
  de: { dark: "Dunkelmodus", light: "Hellmodus", pubs: "Publikationen", open: "Foto öffnen: ", keys: "← → · Esc",
        flags: { Article: "Artikel", Dissertation: "Dissertation" } },
};
const UI = I18N[document.documentElement.lang] || I18N.en;

// ---- theme toggle: light by default, dark only when chosen ----
(() => {
  const html = document.documentElement;
  const btn = document.getElementById("theme");
  if (!btn) return;
  const label = btn.querySelector("span");
  // the button names the mode it switches *to*
  const sync = () => { label.textContent = html.dataset.theme === "dark" ? UI.light : UI.dark; };
  sync();
  addEventListener("pageshow", sync);
  btn.addEventListener("click", () => {
    const t = html.dataset.theme === "dark" ? "light" : "dark";
    html.dataset.theme = t;
    try { localStorage.setItem("theme", t); } catch (_) {}
    sync();
  });
})();

// ---- publications: grouped by year, filter by tag ----
(() => {
  const root = document.getElementById("pubs");
  if (!root || !window.PUBS) return;
  const limit = Number(root.dataset.limit) || Infinity;   // About page shows only the latest few
  const pubs = PUBS.slice(0, limit);
  const years = [...new Set(pubs.map(p => p.year))].sort((a, b) => b - a);
  const esc = s => s.replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const me = s => esc(s).replace("L. Netz", "<b>L. Netz</b>");
  const links = p => {
    const out = [];
    if (p.pdf) out.push(`<a href="${esc(p.pdf)}" target="_blank" rel="noopener">pdf ↗</a>`);
    if (p.doi) out.push(`<a href="https://doi.org/${esc(p.doi)}" target="_blank" rel="noopener">doi ↗</a>`);
    if (p.url) out.push(`<a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.urlLabel || "link")} ↗</a>`);
    out.push(`<a href="https://scholar.google.com/scholar?q=${encodeURIComponent('"' + p.title + '"')}" target="_blank" rel="noopener">scholar ↗</a>`);
    return out.join("");
  };

  root.innerHTML = years.map(y => `
    <div class="year">
      <div class="y mono">${y}</div>
      <ol class="pubs">${pubs.filter(p => p.year === y).map(p => `
        <li data-tags="${p.tags.join(" ")}">
          <span class="key mono">${p.key}</span>
          <div>
            <div class="t">${esc(p.title)}${p.flag ? `<span class="flag mono">${UI.flags[p.flag] || p.flag}</span>` : ""}</div>
            <div class="a">${me(p.authors)}</div>
            <div class="v mono">${esc(p.venue)}</div>
            <div class="plinks mono">${links(p)}</div>
          </div>
        </li>`).join("")}
      </ol>
    </div>`).join("");

  const count = document.getElementById("pub-count");
  if (count) count.textContent = `${PUBS.length} ${UI.pubs}`;

  document.querySelectorAll(".filters button").forEach(btn => {
    const f = btn.dataset.f;
    const n = f === "all" ? PUBS.length : PUBS.filter(p => p.tags.includes(f)).length;
    btn.insertAdjacentHTML("beforeend", `<span class="n">${n}</span>`);
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filters button").forEach(b => b.setAttribute("aria-pressed", b === btn));
      root.querySelectorAll("li").forEach(li => li.hidden = f !== "all" && !li.dataset.tags.split(" ").includes(f));
      root.querySelectorAll(".year").forEach(y => y.classList.toggle("empty", !y.querySelector("li:not([hidden])")));
    });
  });
})();

// ---- photo lightbox ----
(() => {
  const lb = document.getElementById("lightbox");
  if (!lb) return;
  const img = lb.querySelector("img"), cap = lb.querySelector(".cap");
  const figs = [...document.querySelectorAll(".photos figure")];
  let i = -1, opener = null;

  const show = n => {
    i = (n + figs.length) % figs.length;
    const fig = figs[i], src = fig.querySelector("img");
    img.src = src.src;
    img.alt = src.alt;
    const text = [...fig.querySelectorAll("figcaption span")].map(s => s.textContent).filter(Boolean).join("  ·  ");
    cap.innerHTML = `<span>${i + 1} / ${figs.length}</span><span></span><span>${UI.keys}</span>`;
    cap.children[1].textContent = text;
  };
  const open = n => { opener = document.activeElement; show(n); lb.classList.add("open"); lb.focus(); };
  const close = () => { lb.classList.remove("open"); if (opener) opener.focus(); };

  lb.tabIndex = -1;
  figs.forEach((fig, n) => {
    fig.tabIndex = 0;                                   // photos are reachable by keyboard
    fig.setAttribute("role", "button");
    fig.setAttribute("aria-label", UI.open + fig.querySelector("img").alt);
    fig.addEventListener("click", () => open(n));
    fig.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(n); } });
  });
  lb.addEventListener("click", close);
  addEventListener("keydown", e => {
    if (!lb.classList.contains("open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowRight") show(i + 1);
    if (e.key === "ArrowLeft") show(i - 1);
  });
})();
